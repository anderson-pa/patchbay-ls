import pytest

from hardware.base_instruments import Instrument

test_specs = specs = {0: ['enabled'],
                      (1, 'carrier'): ['enabled', 'test', 'frequency'],
                      'sync': ['enabled', 'shape']}


@pytest.fixture
def inst():
    """Return an Instrument instance with channels defined by `test_specs`."""
    instrument = Instrument(test_specs)
    return instrument


def test_channel_ids(inst):
    """Number of channels found should match number passed in."""
    assert list(test_specs.keys()) == inst.channel_ids


def test_get_channel(inst):
    """Retrieve channels for valid IDs. Raise KeyError for invalid IDs."""
    for ch in test_specs.keys():
        inst.get_channel(ch)

    with pytest.raises(KeyError):
        inst.get_channel('BadChannelID')


def test_get_channel_attribute(inst):
    """Confirm that the attributes match the specs."""

    # Valid attributes return nothing for an Instrument instance
    for ch_id, attributes in test_specs.items():
        for attribute in attributes:
            inst.get_channel_attribute(ch_id, attribute)
        with pytest.raises(AttributeError):
            inst.get_channel_attribute(ch_id, 'BadAttributeName')

    with pytest.raises(KeyError):
        inst.get_channel_attribute('BadChannelID', 'frequency')

