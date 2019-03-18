import falcon
import logging, sys
import os
import json
from signer.staking import StopStaking, StartStaking
from signer.sign import KeysResource
from signer.configuration import Register, ResetDevice, ChangePin
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


with open('signer/known_keys.json', 'r', os.O_NONBLOCK) as myfile:
    json_blob = myfile.read().replace('\n', '')
    logging.info('Parsed keys.json successfully as JSON')
    keys_config = json.loads(json_blob)

# create application instance
api = application = falcon.API(middleware=[RequestLogger(), RequireJSON()])

# add routes to endpoints
api.add_route('/keys/{pkh}', KeysResource(keys_config))
api.add_route('/register', Register(keys_config))
api.add_route('/start_staking', StartStaking())
api.add_route('/stop_staking', StopStaking())
api.add_route('/reset_device', ResetDevice())
api.add_route('/change_pin', ChangePin())
api.add_route('/authorized_keys', Authorized())