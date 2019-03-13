import falcon
import logging, sys
import os
from signer.staking import StopStaking, StartStaking
from signer.sign import KeysResource
from signer.register import Register
from signer.authorized import Authorized
from signer.middleware import RequestLogger, RequireJSON

# set logging level from ENV variable
log_level = logging.INFO
try:
    if os.environ['LOGLEVEL'] == "DEBUG":
        log_level = logging.DEBUG
except KeyError:
    pass

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(message)s', level=log_level)

# create application instance
api = application = falcon.API(middleware=[RequestLogger()])

# add routes to endpoints
api.add_route('/keys/{pkh}', KeysResource())
api.add_route('/register', Register())
api.add_route('/start_staking', StartStaking())
api.add_route('/stop_staking', StopStaking())
api.add_route('/authorized_keys', Authorized())