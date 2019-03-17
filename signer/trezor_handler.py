from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.tools import parse_path
from trezorlib import tezos, ui, device
from trezorlib.transport import TransportException

import logging


def get_public_key(path):
    logging.info('Getting public key from trezor')
    try:
        client = trezor_connect()
        address_n = parse_path(path)

        pk = tezos.get_public_key(client, address_n=address_n)

        client.close()
        return pk

    except Exception as e:
        logging.error("Error while getting public key ", e)


def get_address(path):
    try:
        client = trezor_connect()
        address_n = parse_path(path)

        pkh = tezos.get_address(client, address_n=address_n)

        client.close()

        return pkh
    except Exception as e:
        logging.error("Error while getting tezos address (pkh) ", e)


def trezor_connect():
    try:
        return TrezorClient(get_transport(), ui=ui.ClickUI())
    except TransportException as e:
        logging.error("Trezor device not found")


def sign_delegation(msg, address):
    signature = None
    try:
        client = trezor_connect()
        address_n = parse_path(address)
        logging.info("Signing . . .")
        signature = tezos.sign_tx(client, address_n, msg)
        logging.info("Generated signature: {}".format(signature.signature))
        client.close()
    except Exception as e:
        logging.error("Error in trezor signing", e)

    return signature.signature


def sign_baking(msg, address):
    signature = None
    try:
        client = trezor_connect()
        address_n = parse_path(address)
        signature = tezos.sign_baker_op(client, address_n, msg)
        client.close()
    except Exception as e:
        logging.error("Error in trezor signing", e)

    return signature.signature


# will be removed
def start_staking():
    logging.info("Staking about to start")
    client = trezor_connect()

    tezos.control_baking(client, stake=True)
    client.close()


# will be removed
def stop_staking():
    logging.info("Staking about to stop")
    client = trezor_connect()

    tezos.control_baking(client, stake=False)

    client.close()

# TODO: move to right place 
def reset_device():
    logging.info("Setup device and generate new seed.")
    client = trezor_connect()
    try:
        device.reset(client)
    except Exception as e:
        logging.error("Error device is initialized", e)

    client.close()


# TODO: move to right place
def change_pin():
    logging.info("Setup device and generate new seed.")
    client = trezor_connect()
    try:
        device.change_pin(client)
    except Exception as e:
        logging.error("Can not change pin", e)

    client.close()