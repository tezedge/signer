import logging
import falcon


class RequestLogger(object):
    def process_request(self, req, resp):
        logging.debug("[REQUEST] method: {}".format(req.method))
        logging.debug("          url: {}".format(req.uri))
        logging.debug("          content-type: {}".format(req.content_type))
        logging.debug("          data:{}".format(req.media))

    def process_response(self, req, resp, resource, req_succeeded):
        logging.debug("[RESPONSE] status: {}".format(resp.status))
        logging.debug("           content-type: {}".format(resp.content_type))
        logging.debug("           data:{}".format(resp.body))


class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.')
