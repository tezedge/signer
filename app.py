import falcon
import logging, sys
from signer.staking import StopStaking, StartStaking
from signer.sign import KeysResource
from signer.register import Register
from signer.authorized import Authorized
from signer.log_requests import RequestLogger

logging.basicConfig(stream=sys.stdout, format='%(asctime)s %(message)s', level=logging.DEBUG)

# create application instance
api = application = falcon.API(middleware=RequestLogger())

# add routes to endpoints
api.add_route('/keys/{pkh}', KeysResource())
api.add_route('/register', Register())
api.add_route('/start_staking', StartStaking())
api.add_route('/stop_staking', StopStaking())
api.add_route('/authorized_keys', Authorized())