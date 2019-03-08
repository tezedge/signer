import logging


class RequestLogger(object):
    def process_request(self, req, resp):
        logging.debug("[REQUEST] method: {}".format(req.method))
        logging.debug("          url: {}".format(req.uri))
        logging.debug("          content-type: {}".format(req.content_type))
        logging.debug("          data:{}".format(req.stream.read(req.content_length or 0)))

    def process_response(self, req, resp, resource, req_succeeded):
        logging.debug("[RESPONSE] status: {}".format(resp.status))
        logging.debug("           content-type: {}".format(resp.content_type))
        logging.debug("           data:{}".format(resp.body))
