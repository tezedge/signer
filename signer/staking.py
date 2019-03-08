import json
import logging

class StartStaking(object):

    def on_get(self, req, resp):
        logging.info("Starting staking")

        resp.content_type = 'application/json'
        resp.body = json.dumps({"Success": "Staking mode started"})

        # call trezor


class StopStaking(object):

    def on_get(self, req, resp):
        logging.info("Stopping staking")

        resp.content_type = 'application/json'
        resp.body = {"Success": "Staking mode stopped"}

        # call trezor
