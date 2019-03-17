import pytest
from trezorlib.client import TrezorClient
from trezorlib.transport import get_transport
from trezorlib.tools import parse_path
from trezorlib import tezos, ui, device
from trezorlib import messages as proto
from trezorlib.transport import TransportException
from trezorlib.exceptions import TrezorFailure


def test_trezor_connected():
    client = trezor_connect()

    assert isinstance(client, TrezorClient)


def test_trezor_pin():
    # make sure we connect to trezor
    client = trezor_connect()
    assert isinstance(client, TrezorClient)

    # check PIN protection
    features = client.call(proto.Initialize())
    assert features.pin_protection is True


def test_trezor_not_supported_in_baking_mode():
    # make sure we connect to trezor
    client = trezor_connect()
    assert isinstance(client, TrezorClient)

    # make sure we activate baking mode
    ret = tezos.control_baking(client, stake=True)
    assert isinstance(ret, proto.Success)

    # call a not supported message during baking mode
    with pytest.raises(TrezorFailure):
        ret = device.change_pin(client)
        assert isinstance(ret, proto.Failure)

    # make sure we deactivate baking mode
    ret = tezos.control_baking(client, stake=False)
    assert isinstance(ret, proto.Success)


def trezor_connect():
    try:
        return TrezorClient(get_transport(), ui=ui.ClickUI())
    except TransportException as e:
        return None
