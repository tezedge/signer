import falcon
from signer.staking import StopStaking, StartStaking
from signer.sign import KeysResource
from signer.register import Register
from signer.authorized import Authorized

# create application instance
api = application = falcon.API()

# add routes to endpoints
api.add_route('/keys/{pkh}', KeysResource())
api.add_route('/register', Register())
api.add_route('/start_staking', StartStaking())
api.add_route('/stop_staking', StopStaking())
api.add_route('/authorized_keys', Authorized)