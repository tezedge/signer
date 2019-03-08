import logging

import falcon
import mimetypes


class Register(object):

    def on_post(self, req, resp):
        # call trezor - get the pkh for the given HDpath

        logging.info("Registering pkh")
        # register the key
        pass


