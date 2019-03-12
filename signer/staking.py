import json
import logging
from signer import trezor_handler

class StartStaking(object):

    def on_get(self, req, resp):
        logging.info("Starting staking")

        resp.content_type = 'application/json'
        resp.body = json.dumps({"Success": "Staking mode started"})

        # call trezor
        trezor_handler.start_staking()

class StopStaking(object):

    def on_get(self, req, resp):
        logging.info("Stopping staking")

        resp.content_type = 'application/json'
        resp.body = json.dumps({"Success": "Staking mode stopped"})

        # call trezor
        trezor_handler.stop_staking()
