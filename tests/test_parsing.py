import pytest
from signer.sign import KeysResource


def test_parse_endorsement():
    endorsement_dict = {
        "magic_byte": "02",
        "chain_id": "e3e15e60",
        "endorsement": {
            "branch": "53f552f0e22a364259848b1e13f124cbae330569f10777e9fa1b1cd8ea57dac0",
            "tag": 0,
            "level": 0x00055507,
         }
    }

    rs = KeysResource()

    parsed_endorsement = rs.parse_endorsement(bytes.fromhex("02e3e15e6053f552f0e22a364259848b1e13f124cbae330569f10777e9fa1b1cd8ea57dac00000055507"))

    assert parsed_endorsement == endorsement_dict


def test_parse_block_header():
    block_header_dict = {
        "magic_byte": "01",
        "chain_id": "3bb717ee",
        "block_header": {
            "level": 0x0002c685,
            "proto": 1,
            "predecessor": "aac40470fa66b3ca657f46dba10df233837e14c31e1193505e056ea2116cf5b5",
            "timestamp": 0x000000005c361155,
            "validation_pass": 4,
            "operations_hash": "cd38e4e70d5668a28b65dddb6fa82edf8f631553895735625cf0d183b7b05d6e",
            "bytes_in_field_fitness": 0x11,
            "bytes_in_next_field": 0x1,
            "fitness": "000000000800000000005a62a2",
            "context": "877920f3904dd8619b2fb66ebb323cc3b70a7f03e4baaf4a9f0a252cb0e501e0",
            "priority": 0,
            "proof_of_work_nonce": "3b3fb8058de0aca2",
            "presence_of_field_seed_nonce_hash": False,
        }
    }

    rs = KeysResource()

    parsed_block_header = rs.parse_block(bytes.fromhex("013bb717ee0002c68501aac40470fa66b3ca657f46dba10df233837e14c31e1193505e056ea2116cf5b5000000005c36115504cd38e4e70d5668a28b65dddb6fa82edf8f631553895735625cf0d183b7b05d6e0000001100000001000000000800000000005a62a2877920f3904dd8619b2fb66ebb323cc3b70a7f03e4baaf4a9f0a252cb0e501e000003b3fb8058de0aca200"))

    assert parsed_block_header == block_header_dict


def test_parse_delegetion_without_reveal():
    delegegation = {
        "branch": "9b8b8bc45d611a3ada20ad0f4b6f0bfd72ab395cc52213a57b14d1fb75b37fd0",
        "delegation": {
            "source": {
                "tag": 0,
                "hash": "00001e65c88ae6317cd62a638c8abd1e71c83c8475",
            },
            "fee": 0,
            "counter": 108927,
            "gas_limit": 200,
            "storage_limit": 0,
            "delegate": "0049a35041e4be130977d51419208ca1d487cfb2e7",
        },
    }

    rs = KeysResource()

    parsed = rs.parse_delegation(bytes.fromhex("039b8b8bc45d611a3ada20ad0f4b6f0bfd72ab395cc52213a57b14d1fb75b37fd00a0000001e65c88ae6317cd62a638c8abd1e71c83c847500ffd206c80100ff0049a35041e4be130977d51419208ca1d487cfb2e7"))
    assert parsed == delegegation


def test_parse_delegation_with_reveal():
    delegation = {
        "branch": "a4f206a45ff89c2f660d84b91b4c2b2cbd2c02b8bffba41dd364693cefbfd0fc",
        "reveal": {
            "source": {
                "tag": 0,
                "hash": "005f450441f41ee11eee78a31d1e1e55627c783bd6",
            },
            "fee": 1259,
            "counter": 908,
            "gas_limit": 10000,
            "storage_limit": 0,
            "public_key": "000612ffd3ad44a335c620f6e2f6ce7ffdea0ee1ea835a661b9f6f3c2376836b0a",
        },
        "delegation": {
            "source": {
                "tag": 0,
                "hash": "005f450441f41ee11eee78a31d1e1e55627c783bd6",
            },
            "fee": 1162,
            "counter": 909,
            "gas_limit": 10100,
            "storage_limit": 0,
            "delegate": "005f450441f41ee11eee78a31d1e1e55627c783bd6",
        },
    }

    rs = KeysResource()

    parsed = rs.parse_delegation_with_reveal(bytes.fromhex("03a4f206a45ff89c2f660d84b91b4c2b2cbd2c02b8bffba41dd364693cefbfd0fc0700005f450441f41ee11eee78a31d1e1e55627c783bd6eb098c07904e00000612ffd3ad44a335c620f6e2f6ce7ffdea0ee1ea835a661b9f6f3c2376836b0a0a00005f450441f41ee11eee78a31d1e1e55627c783bd68a098d07f44e00ff005f450441f41ee11eee78a31d1e1e55627c783bd6"))
    assert parsed == delegation
