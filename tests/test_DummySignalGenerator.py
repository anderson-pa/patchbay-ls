import pytest

from hardware.dummy_instrument import DummySignalGenerator
from hardware.base_instruments import Channel


@pytest.fixture
def sig_gen():
    sg = DummySignalGenerator()
    return sg


@pytest.fixture
def sig_gen_channel(sig_gen):
    ch = sig_gen.get_channel(ch_id)
    return ch

valid_channels = [(0, 'carrier'), (0, 'am'), (1, 'carrier'), (1, 'am'), 'sync']
ch_id = valid_channels[0]
output_defaults = {'enabled': False, 'shape': 'sine', 'frequency': 1e3,
                   'amplitude': 0.1, 'offset': 0, 'phase': 0, 'master': None}
output_updates = {'enabled': True, 'shape': 'square', 'frequency': 2e4,
                  'amplitude': 0.5, 'offset': 0.25, 'phase': 15, 'master': 1}


def test_get_channel_valid(sig_gen):
    # No missing or additional channels. Channels have correct IDs.

    assert len(valid_channels) == len(sig_gen.channel_ids)

    for channel_id in valid_channels:
        ch = sig_gen.get_channel(channel_id)
        assert Channel is type(ch)


def test_get_channel_invalid(sig_gen):
    # Attempting to get a channel with invalid ID raises `KeyError`.
    with pytest.raises(KeyError):
        sig_gen.get_channel('DoesNotExist')


def test_get_set_valid_channel_attribute(sig_gen):
    """Valid channel attributes can be individually set and retrieved."""
    for name, val in output_defaults.items():
        assert val == sig_gen.get_channel_attribute(ch_id, name)

    for name, val in output_updates.items():
        sig_gen.set_channel_attribute(ch_id, name, val)
        assert val == sig_gen.get_channel_attribute(ch_id, name)


def test_get_set_invalid_channel_attributes(sig_gen):
    """Check errors for getting/setting channel attributes with invalid inputs.

    Raise `KeyError` if `channel_id` is not valid.
    Raise `AttributeError` if `name` is not valid.
    """
    with pytest.raises(KeyError):
        sig_gen.get_channel_attribute('BadChannelID', 'frequency')
    with pytest.raises(KeyError):
        sig_gen.set_channel_attribute('BadChannelID', 'frequency', 10)

    with pytest.raises(AttributeError):
        sig_gen.get_channel_attribute(ch_id, 'BadAttrName')
    with pytest.raises(AttributeError):
        sig_gen.set_channel_attribute(ch_id, 'BadAttrName', 44)


def test_configure_channel_valid_inputs(sig_gen):
    """Multiple channel attributes can be updated using `configure_channel`."""

    # Confirm the defaults
    for name, val in output_defaults.items():
        assert val == sig_gen.get_channel_attribute(ch_id, name)

    # Change a few attributes directly and confirm only those values change.
    new_amplitude = 1
    new_shape = 'noise'
    sig_gen.configure_channel(ch_id, amplitude=new_amplitude, shape=new_shape)
    for name, val in output_defaults.items():
        if name == 'amplitude':
            assert new_amplitude == sig_gen.get_channel_attribute(ch_id, name)
        elif name == 'shape':
            assert new_shape == sig_gen.get_channel_attribute(ch_id, name)
        else:
            assert val == sig_gen.get_channel_attribute(ch_id, name)

    # Change multiple attributes with an unpacked dictionary
    # Check that values don't clash with the previous update
    assert output_updates['amplitude'] != new_amplitude
    assert output_updates['shape'] != new_shape
    sig_gen.configure_channel(ch_id, **output_updates)
    for name, val in output_updates.items():
        assert val == sig_gen.get_channel_attribute(ch_id, name)


def test_configure_channel_invalid_inputs(sig_gen):
    """Check errors for `configure_channel` with invalid inputs.

    Raise `KeyError` if `channel_id` is not valid.
    Raise `AttributeError` if `name` is not valid.
    """
    with pytest.raises(KeyError):
        sig_gen.configure_channel('BadChannelID', frequency=2)

    with pytest.raises(AttributeError):
        sig_gen.configure_channel(ch_id, BadAttrName=3)


def test_channel_details_valid_inputs(sig_gen):
    """Multiple channel attributes can be retrieved using `channel_details`."""

    # Confirm the defaults
    for name, val in output_defaults.items():
        assert val == sig_gen.get_channel_attribute(ch_id, name)

    # Return all attributes if none are directly specified.
    assert output_defaults == sig_gen.channel_details(ch_id)

    # Return only specific attributes if specified.
    attr_names = ['enabled', 'shape', 'amplitude']
    filtered_defaults = {key: val for key, val in output_defaults.items()
                         if key in attr_names}
    assert filtered_defaults == sig_gen.channel_details(ch_id, attr_names)


def test_channel_details_invalid_inputs(sig_gen):
    """Check errors for `channel_details` with invalid inputs.

    Raise `KeyError` if `channel_id` is not valid.
    Raise `AttributeError` if any item in `attributes` is not a valid name.
    """
    with pytest.raises(KeyError):
        sig_gen.channel_details('BadChannelID')

    with pytest.raises(AttributeError):
        sig_gen.configure_channel(ch_id, attributes=['shape', 'BadAttrName'])


def test_channel__id(sig_gen_channel):
    """Confirm that the channel ID is reported correctly."""
    assert ch_id == sig_gen_channel.id


def test_channel__get_set_valid_attribute(sig_gen_channel):
    """Valid channel attributes can be set and retrieved as attributes."""
    for name, val in output_defaults.items():
        assert hasattr(sig_gen_channel, name)
        assert val == getattr(sig_gen_channel, name)

    for name, val in output_updates.items():
        setattr(sig_gen_channel, name, val)
        assert val == getattr(sig_gen_channel, name)

    sig_gen_channel.frequency = 2.5
    assert 2.5 == sig_gen_channel.frequency


def test_channel__get_set_invalid_attributes(sig_gen_channel):
    """Check errors for getting/setting channel attributes with invalid inputs.

    Raise `AttributeError` if `name` is not valid when reading.
    """
    with pytest.raises(AttributeError):
        val = sig_gen_channel.BadAttrName


def test_channel__configure_valid_inputs(sig_gen_channel):
    """Multiple channel attributes can be updated using `configure`."""

    # Confirm the defaults
    for name, val in output_defaults.items():
        assert val == getattr(sig_gen_channel, name)

    # Change a few attributes directly and confirm only those values change.
    new_amplitude = 1
    new_shape = 'noise'
    sig_gen_channel.configure(amplitude=new_amplitude, shape=new_shape)
    for name, val in output_defaults.items():
        if name == 'amplitude':
            assert new_amplitude == getattr(sig_gen_channel, name)
        elif name == 'shape':
            assert new_shape == getattr(sig_gen_channel, name)
        else:
            assert val == getattr(sig_gen_channel, name)

    # Change multiple attributes with an unpacked dictionary
    # Check that values don't clash with the previous update
    assert output_updates['amplitude'] != new_amplitude
    assert output_updates['shape'] != new_shape
    sig_gen_channel.configure(**output_updates)
    for name, val in output_updates.items():
        assert val == getattr(sig_gen_channel, name)


def test_channel__configure_invalid_inputs(sig_gen_channel):
    """Check errors for `configure` with invalid inputs.

    Raise `AttributeError` if `name` is not valid.
    """
    with pytest.raises(AttributeError):
        sig_gen_channel.configure(BadAttrName=3)


def test_channel__details_valid_inputs(sig_gen_channel):
    """Multiple channel attributes can be retrieved using `details`."""

    # Confirm the defaults
    for name, val in output_defaults.items():
        assert val == getattr(sig_gen_channel, name)

    # Return all attributes if none are directly specified.
    assert output_defaults == sig_gen_channel.details()

    # Return only specific attributes if specified.
    attr_names = ['enabled', 'shape', 'amplitude']
    filtered_defaults = {key: val for key, val in output_defaults.items()
                         if key in attr_names}
    assert filtered_defaults == sig_gen_channel.details(attr_names)


def test_channel__details_invalid_inputs(sig_gen_channel):
    """Check errors for `details` with invalid inputs.

    Raise `AttributeError` if any item in `attributes` is not a valid name.
    """
    with pytest.raises(AttributeError):
        sig_gen_channel.details(attributes=['shape', 'BadAttrName'])
