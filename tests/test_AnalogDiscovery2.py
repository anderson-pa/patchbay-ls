import pytest
import dwf

from hardware.signal_generator import AnalogDiscovery2SignalGenerator
from hardware.oscilloscope import AnalogDiscovery2Oscilloscope

if not dwf.DwfEnumeration():
    pytest.skip("skipping AnalogDiscovery2 tests, no device present",
                allow_module_level=True)

@pytest.fixture
def hdwf():
    """Get a handle for the device to test with."""
    device = dwf.DwfEnumeration()[0]
    hdwf = dwf.Dwf(device)
    yield hdwf
    hdwf.close()


def test_pass(hdwf):
    ado = AnalogDiscovery2Oscilloscope(hdwf)
    adsg = AnalogDiscovery2SignalGenerator(hdwf)

    # assert ado


def test_2(hdwf):
    ado = AnalogDiscovery2Oscilloscope(hdwf)
    adsg = AnalogDiscovery2SignalGenerator(hdwf)
    cho = ado.get_channel(0)
    chsg = adsg.get_channel((0, 'carrier'))

    assert not cho.enabled
    assert chsg.shape == 'dc'
    assert not chsg.enabled