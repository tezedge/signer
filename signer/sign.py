import json
import logging
import struct
from signer import trezor_handler
import falcon
import os

from trezorlib import messages
from trezorlib.protobuf import dict_to_proto


class KeysResource(object):
    BLOCK_WATERMARK = 1
    ENDORSEMENT_WATERMARK = 2
    TRANSACTION_WATERMARK = 3
    FITNESS_PREFIX_SIZE = 4
    DELEGATION_TAG = 10
    REVEAL_TAG = 7
    PROPOSAL_TAG = 5
    BALLOT_TAG = 6
    OPERATION_TAG_INDEX = 33

    # Pad the deserialized data
    PADDING_2 = 2

    # Index of the first zarith number
    ZARITH_DELEGATION_INDEX = ZARITH_REVEAL_INDEX = 56
    ZARITH_REVEAL_WITH_DELEGATION_INDEX = 23

    # length without zarith -> we need to calculate and add later
    REVEAL_LENGTH = 89

    # needed for the presence_of_nonce_hash
    BLOCK_PRESENCE_OF_NONCE_WITHOUT_FITNESS_INDEX = 133

    PROPOSAL_LENGTH = 32

    def __init__(self, keys_config):
        # the only mimetype we return is json
        self.content_type = 'application/json'

        self.keys_config = keys_config

    def on_get(self, req, resp, pkh):
        logging.info("Retrieving public key for {}".format(pkh))
        try:
            if pkh in self.keys_config.keys():
                pk = trezor_handler.get_public_key(self.keys_config[pkh])

                resp.content_type = self.content_type
                resp.body = json.dumps({"public_key": "{}".format(pk)})
            else:
                resp.body = json.dumps({"kind": "generic", "error": "no keys for the source contract manager"})
                resp.status = falcon.HTTP_500
        except Exception as e:
            logging.error("Error in retrieving pk: \n", e)
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"Error": "Exception in retrieving pk"})

    def on_post(self, req, resp, pkh):
        signature = None
        try:
            resp.content_type = self.content_type

            logging.info("Signing received data for {}".format(pkh))

            # sign, if we have already registered the hdpath for the signer
            if pkh in self.keys_config.keys():
                # read and deserialize data
                data = json.loads(req.stream.read())
                msg_bytes = bytes.fromhex(data)
                proto_message = self.parse_message(msg_bytes)

                # determine if the message is a baking operation or a transaction like operation
                if self.is_endorsement(msg_bytes) or self.is_block(msg_bytes):
                    signature = trezor_handler.sign_baking(proto_message, self.keys_config[pkh])

                elif self.is_transaction_like(msg_bytes):
                    logging.info("Operation is transaction like")
                    signature = trezor_handler.sign_non_baking_op(proto_message, self.keys_config[pkh])

                else:
                    resp.status = falcon.HTTP_500
                    resp.body = json.dumps({"Error": "Message not supported"})

                resp.body = json.dumps({"signature": "{}".format(signature)})

            else:
                resp.body = json.dumps({"kind": "generic", "error": "no keys for the source contract manager"})
                resp.status = falcon.HTTP_500
        except Exception as e:
            logging.error("Error in signing: \n", e)
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"Error": e})

    def is_endorsement(self, msg_bytes):
        return msg_bytes[0] == self.ENDORSEMENT_WATERMARK

    def is_block(self, msg_bytes):
        return msg_bytes[0] == self.BLOCK_WATERMARK

    def is_transaction_like(self, msg_bytes):
        return msg_bytes[0] == self.TRANSACTION_WATERMARK

    def parse_message(self, msg_bytes):
        # Determine the operation type from the message
        operation_tag = msg_bytes[self.OPERATION_TAG_INDEX]
        operation = None

        # parse the message according the operation type
        if self.is_block(msg_bytes):
            operation = self.parse_block(msg_bytes)

        elif self.is_endorsement(msg_bytes):
            operation = self.parse_endorsement(msg_bytes)

        elif self.is_transaction_like(msg_bytes):
            if operation_tag == self.DELEGATION_TAG:
                operation = self.parse_delegation(msg_bytes)

            elif operation_tag == self.REVEAL_TAG:
                operation = self.parse_delegation_with_reveal(msg_bytes)

            elif operation_tag == self.PROPOSAL_TAG:
                operation = self.parse_proposal(msg_bytes)

            elif operation_tag == self.BALLOT_TAG:
                operation = self.parse_ballot(msg_bytes)

            return dict_to_proto(messages.TezosSignTx, operation)
        else:
            logging.warning("Message not supported!")
            return None

        return dict_to_proto(messages.TezosSignBakerOp, operation)

    def parse_endorsement(self, msg_bytes):
        endorsement_msg = None
        try:
            logging.info(msg_bytes)
            endorsement_format = 'B4s32sBB4s'
            fields = struct.unpack(endorsement_format, msg_bytes)

            # unpack the message
            (magic_byte,
             chain_id,
             branch,
             tag,
             slot,
             level) = fields

            logging.info(slot)

            # create a dictionary from the deserialized data
            # f"{int}:0{padding}x" -> convert the int into string of the required length
            endorsement_msg = {
                "chain_id": chain_id.hex(),
                "endorsement": {
                    "branch": branch.hex(),
                    "slot": slot,
                    "level": int.from_bytes(level, 'big'),
                }
            }
        except Exception as e:
            logging.error(e)
            logging.error("Error occured while parsing endorsement")

        return endorsement_msg

    def parse_block(self, msg_bytes):
        # the field fitness has a variable length, we need determine that first
        block_header_msg = None
        try:
            bytes_in_fitness = int.from_bytes(msg_bytes[83:87], 'big') - self.FITNESS_PREFIX_SIZE

            # check for the presence of the field seed_nonce_hash in advance so we prevent deserialization error
            if self._decode_bool(msg_bytes[self.BLOCK_PRESENCE_OF_NONCE_WITHOUT_FITNESS_INDEX + bytes_in_fitness]):
                logging.info("with nonce hash")

                # The seed nonce hash is always represented by the last 32 bytes
                seed_nonce_hash = msg_bytes[-32:]

                # Remove the seed nonce hash from the message and continue with deserialization
                msg_bytes = msg_bytes[:len(msg_bytes) - 32]

            # deserialize data
            block_format = 'B4s4sB32s8sB32s4s4s{}s32s2s8sB'.format(bytes_in_fitness)
            fields = struct.unpack(block_format, msg_bytes)

            (magic_byte,
             chain_id,
             level,
             proto,
             predecessor,
             timestamp,
             validation_pass,
             operations_hash,
             bytes_in_field_fitness,
             bytes_in_next_field,
             fitness,
             context,
             priority,
             proof_of_work_nonce,
             presence_of_field_seed_nonce_hash,
            ) = fields

            # create a dictionary from the deserialized data
            block_header_msg = {
                "chain_id": chain_id.hex(),
                "block_header": {
                    "level": int.from_bytes(level, 'big'),
                    "proto": proto,
                    "predecessor": predecessor.hex(),
                    "timestamp": int.from_bytes(timestamp, 'big'),
                    "validation_pass": validation_pass,
                    "operations_hash": operations_hash.hex(),
                    "bytes_in_field_fitness": int.from_bytes(bytes_in_field_fitness, 'big'),
                    "bytes_in_next_field": int.from_bytes(bytes_in_next_field, 'big'),
                    "fitness": fitness.hex(),
                    "context": context.hex(),
                    "priority": int.from_bytes(priority, 'big'),
                    "proof_of_work_nonce": proof_of_work_nonce.hex(),
                    "presence_of_field_seed_nonce_hash": self._decode_bool(presence_of_field_seed_nonce_hash),
                }
            }

            # if the seed_nonce_hash field is present add it to the dictionary
            if self._decode_bool(presence_of_field_seed_nonce_hash):
                block_header_msg['block_header']['seed_nonce_hash'] = seed_nonce_hash.hex()

        except Exception as e:
            logging.error("Error occurred while parsing block ", e)

        return block_header_msg

    def parse_delegation(self, msg_bytes):
        delegation_msg = None

        try:
            # first, decode the zarith numbers to get the exact length of the zarith numbers
            zarith_nums, checked_bytes = self._decode_zarith(msg_bytes, self.ZARITH_DELEGATION_INDEX)

            # deserialize data
            delegation_format = 'B32sBB21s{}sB21s'.format(checked_bytes)
            fields = struct.unpack(delegation_format, msg_bytes)

            (magic_byte,
             branch,
             operation_tag,
             source_tag,
             source_hash,
             zarith,
             presence_of_delegate,
             delegate
            ) = fields

            # create a dictionary
            delegation_msg = {
                "branch": branch.hex(),
                "delegation": {
                    "source": {
                        "tag": source_tag,
                        "hash": source_hash.hex(),
                    },
                    "fee": zarith_nums[0],
                    "counter": zarith_nums[1],
                    "gas_limit": zarith_nums[2],
                    "storage_limit": zarith_nums[3],
                    "delegate": delegate.hex(),
                },
            }
        except Exception as e:
            logging.error("Error occurred while parsing delegation")

        return delegation_msg

    def parse_delegation_with_reveal(self, msg_bytes):
        delegation_with_reveal_msg = None
        try:
            # parse the reveal part first
            zarith_nums, checked_bytes = self._decode_zarith(msg_bytes, self.ZARITH_REVEAL_INDEX)

            # slice the message into reveal and delegation bytes
            reveal_bytes = msg_bytes[:self.REVEAL_LENGTH + checked_bytes]
            delegation_bytes = msg_bytes[self.REVEAL_LENGTH + checked_bytes:]

            # add the calculated bytes length
            reveal_format = 'B32sBB21s{}s33s'.format(checked_bytes)

            # deserialize reveal part
            fields = struct.unpack(reveal_format, reveal_bytes)

            (magic_byte,
             branch,
             operation_tag,
             source_tag,
             source_hash,
             zarith,
             public_key
             ) = fields

            reveal_msg = {
                "source": {
                    "tag": source_tag,
                    "hash": source_hash.hex(),
                },
                "fee": zarith_nums[0],
                "counter": zarith_nums[1],
                "gas_limit": zarith_nums[2],
                "storage_limit": zarith_nums[3],
                "public_key": public_key.hex(),
            }

            # do the same for the delegation part
            zarith_nums, checked_bytes = self._decode_zarith(delegation_bytes, self.ZARITH_REVEAL_WITH_DELEGATION_INDEX)
            delegation_format = 'BB21s{}sB21s'.format(checked_bytes)

            # deserialize delegation part
            fields = struct.unpack(delegation_format, delegation_bytes)

            (operation_tag,
             source_tag,
             source_hash,
             zarith,
             presence_of_delegate,
             delegate
             ) = fields

            delegation_msg = {
                "source": {
                    "tag": source_tag,
                    "hash": source_hash.hex(),
                },
                "fee": zarith_nums[0],
                "counter": zarith_nums[1],
                "gas_limit": zarith_nums[2],
                "storage_limit": zarith_nums[3],
                "delegate": delegate.hex(),
            }

            # put everything together
            delegation_with_reveal_msg = {
                "branch": branch.hex(),
                "reveal": reveal_msg,
                "delegation": delegation_msg
            }

        except Exception as e:
            logging.error("Error occurred while parsing delegation with reveal")

        return delegation_with_reveal_msg

    # TODO: test needed
    def parse_proposal(self, msg_bytes):
        proposal_msg = None
        try:
            bytes_in_proposals_field = int.from_bytes(msg_bytes[59:63], 'big')
            print(bytes_in_proposals_field)

            proposal_format = 'B32sB21s4s4s{}s'.format(bytes_in_proposals_field)
            fields = struct.unpack(proposal_format, msg_bytes)

            # unpack the message
            (magic_byte,
             branch,
             operation_tag,
             source,
             period,
             bytes_in_next_field,
             proposals
             ) = fields

            proposal_list = list(
                [
                    proposals[i: i + 32]
                    for i in range(0, len(proposals), 32)
                ]
            )
            proposal_list2 = [prop.hex() for prop in proposal_list]

            # create a dictionary from the deserialized data
            proposal_msg = {
                "branch": branch.hex(),
                "proposal": {
                    "source": source.hex(),
                    "period": int.from_bytes(period, 'big'),
                    "proposals": proposal_list2,
                },
            }
        except Exception as e:
            logging.error("Error occured while parsing proposal", e)

        return proposal_msg

    # TODO: test needed
    def parse_ballot(self, msg_bytes):
        ballot_msg = None

        try:
            ballot_format = 'B32sB21s4s32sB'
            fields = struct.unpack(ballot_format, msg_bytes)

            (magic_byte,
             branch,
             operation_tag,
             source,
             period,
             proposal,
             ballot
            ) = fields

        # create dictionary
            ballot_msg = {
                "branch": branch.hex(),
                "ballot": {
                    "source": source.hex(),
                    "period": int.from_bytes(period, 'big'),
                    "proposal": proposal.hex(),
                    "ballot": ballot
                },
            }

        except Exception as e:
            logging.error("Error occurred while parsing ballot", e)

        return ballot_msg

    def parse_tx(self, msg_bytes):
        tx_message = None

    @staticmethod
    def _decode_bool(num):
        if num == 255:
            return True
        else:
            return False

    @staticmethod
    def _decode_zarith(raw_bytes, start):
        num_list = []
        res_list = []
        counter = 0

        for i in range(4):
            next_b = 1
            while next_b:
                num = raw_bytes[start + counter] & ~(1 << 7)
                num_list.append(num)
                next_b = raw_bytes[start + counter] >> 7
                counter += 1
            res = num_list.pop()
            while num_list:
                res = res << 7 | num_list.pop()

            res_list.append(res)

        return res_list, counter
