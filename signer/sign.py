import json
import logging


class KeysResource(object):

    def __init__(self):
        # the only mimetype we return is json
        self.content_type = 'application/json'

    def on_get(self, req, resp, pkh):
        logging.info("Retrieving public key for {}".format(pkh))

        resp.content_type = self.content_type
        resp.body = json.dumps({"pk": "pk for {}".format(pkh)})

    def on_post(self, req, resp, pkh):
        logging.info("Signing received data for {}".format(pkh))
        resp.content_type = self.content_type
        resp.body = json.dumps({"sig": "sig for {}".format(pkh)})

    def parse_endorsement(self, hexstring):
        pass

    def parse_block(self, hexstring):
        pass

    def parse_delegation(self, hexstring):
        pass

    def parse_delegation_with_reveal(self, hexstring):
        pass
