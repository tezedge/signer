import json


class Authorized(object):

    def on_get(self, req, resp):
        resp.content_type = 'application/json'
        resp.body = json.dumps({})
