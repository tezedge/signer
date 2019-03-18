import json
import logging
import os

import falcon
from signer import trezor_handler


class Register(object):

    def __init__(self, keys_config):
        self.keys_config = keys_config

    def on_post(self, req, resp):
        # call trezor - get the pkh for the given HDpath
        try:
            data = req.media
            pkh = trezor_handler.get_address(data)
            logging.info("Registering pkh")

            if pkh not in self.keys_config.keys():
                # add pkh and HDpath pair into config
                self.keys_config[pkh] = data
                with open('signer/known_keys.json', 'w', os.O_NONBLOCK) as myfile:
                    myfile.write(json.dumps(self.keys_config))
            else:
                logging.info("Key {} already known".format(pkh))
            resp.content_type = 'application/json'
            resp.body = json.dumps({"pkh": pkh})
        except Exception as e:
            data = {'Error occurred in register': str(e)}
            logging.error('Exception thrown during request: {}'.format(str(e)))
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"error": data})


class ResetDevice(object):

    def on_get(self, req, resp):
        logging.info("Reset Device")
        resp.content_type = 'application/json'

        # call trezor
        try:
            trezor_handler.reset_device()
            resp.body = json.dumps({"Success": "Device initialized"})
        except Exception as e:
            resp.body = json.dumps({"Failed": "Device not initialized"})


class ChangePin(object):

    def on_get(self, req, resp):
        logging.info("Change Pin")
        resp.content_type = 'application/json'

        # call trezor
        try:
            trezor_handler.change_pin()
            resp.body = json.dumps({"Success": "Pin Changed"})
        except Exception as e:
            resp.body = json.dumps({"Failed": "Pin not changed"})
