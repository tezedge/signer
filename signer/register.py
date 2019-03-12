import json
import logging

import falcon
from signer import trezor_handler


class Register(object):

    def on_post(self, req, resp):
        # call trezor - get the pkh for the given HDpath
        try:
            with open('signer/known_keys.json', 'r') as myfile:
                json_blob = myfile.read().replace('\n', '')
                logging.info('Parsed keys.json successfully as JSON')
                config = json.loads(json_blob)
            data = req.media
            pkh = trezor_handler.get_address(data)
            logging.info("Registering pkh")

            if pkh not in config.keys():
                # add pkh and HDpath pair into config
                config[pkh] = data
                with open('signer/known_keys.json', 'w') as myfile:
                    myfile.write(json.dumps(config))

            resp.content_type = 'application/json'
            resp.body = json.dumps({"pkh": pkh})
        except Exception as e:
            data = {'Error occurred in register': str(e)}
            logging.error('Exception thrown during request: {}'.format(str(e)))
            resp.content_type = 'application/json'
            resp.status = falcon.HTTP_500
            resp.body = json.dumps({"error": data})
