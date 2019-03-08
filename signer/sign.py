import json


class KeysResource(object):

    def __init__(self):
        # the only mimetype we return is json
        self.content_type = 'application/json'

    def on_get(self, req, resp, pkh):
        resp.content_type = self.content_type

        resp.body = json.dumps({"pk": "pk for {}".format(pkh)})

    def on_post(self, req, resp, pkh):
        resp.content_type = self.content_type
        resp.body = json.dumps({"sig": "sig for {}".format(pkh)})
