import json


class StartStaking(object):

    def on_get(self, req, resp):

        resp.content_type = 'application/json'
        resp.body = json.dumps({"Success": "Staking mode started"})

        # call trezor


class StopStaking(object):

    def on_get(self, req, resp):

        resp.content_type = 'application/json'
        resp.body = {"Success": "Staking mode stopped"}

        # call trezor
