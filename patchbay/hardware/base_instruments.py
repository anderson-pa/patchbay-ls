class Channel:
    """Channel is a source or sink associated with an instrument.

    Data can be sent to or received from a channel and configuration can be
    updated. Channel passes responsibility off to the instrument.
    """
    attributes = ()

    def __init__(self, instrument, channel_id, attributes):
        self._instrument = instrument
        self._id = channel_id
        self.attributes = attributes

    def __str__(self):
        return f'{self._instrument}:{self._id}'

    def __repr__(self):
        return f'{self._instrument}:{self._id}'

    def __getattr__(self, item):
        if item in self.attributes:
            return self._instrument.get_channel_attribute(self._id, item)
        else:
            super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self.attributes:
            self._instrument.set_channel_attribute(self._id, key, value)
        else:
            super().__setattr__(key, value)

    @property
    def id(self):
        """Return the ID for this channel."""
        return self._id

    def configure(self, **kwargs):
        """Change the configuration of this channel."""
        self._instrument.configure_channel(self._id, **kwargs)

    def details(self, attributes=None):
        """Read the configuration details of this channel"""
        return self._instrument.channel_details(self._id, attributes)


class Instrument:
    def __init__(self, channel_specs):
        # source and sinks are dictionaries of id and channel
        self._channel_specs = channel_specs

    @property
    def channel_ids(self):
        return list(self._channel_specs.keys())

    def get_channel(self, channel_id):
        return Channel(self, channel_id, self._channel_specs[channel_id])

    def get_channel_attribute(self, channel_id, name):
        if name not in self._channel_specs[channel_id]:
            raise AttributeError(f"Channel has no attribute '{name}'")

    def set_channel_attribute(self, channel_id, name, value):
        if name not in self._channel_specs[channel_id]:
            raise AttributeError(f"Channel has no attribute '{name}'")

    def configure_channel(self, channel_id, **kwargs):
        for key, val in kwargs.items():
            self.set_channel_attribute(channel_id, key, val)

    def channel_details(self, channel_id, attributes=None):
        if attributes is None:
            attributes = self._channel_specs[channel_id]
        return {attr: self.get_channel_attribute(channel_id, attr)
                for attr in attributes}


class GenericCamera(Instrument):
    cam_attrs = []

    def __init__(self):
        super().__init__(channel_specs={})

    def read(self, timeout):
        """Get the next image"""
        raise NotImplementedError

    def start(self):
        """Begin acquisition"""
        raise NotImplementedError

    def stop(self):
        """End acquisition"""
        raise NotImplementedError


class GenericSignalGenerator(Instrument):
    """Class for a generic signal generator.

    Signal generators have one or more standard outputs and typically one
    sync output.

    Output channels are counted from 0 and have three possible nodes:
    carrier, am, fm sync channels are 'sync' """
    ch_out_attrs = ['enabled', 'shape', 'frequency', 'amplitude', 'offset',
                    'phase', 'master']
    ch_sync_attrs = ['enabled']

    output_nodes = ('carrier', 'am', 'fm')
    shapes = ('sinusoid', 'square', 'triangle', 'ramp', 'noise', 'dc', 'user')

    def __init__(self, num_outputs, *, has_fm=True, has_am=True, has_sync=True):
        out_nodes = [node for node, include in zip(['carrier', 'fm', 'am'],
                                                   [True, has_fm, has_am])
                     if include]
        channel_specs = {(i, node): self.ch_out_attrs.copy()
                         for i in range(num_outputs) for node in out_nodes}
        if has_sync:
            channel_specs['sync'] = self.ch_sync_attrs

        super().__init__(channel_specs)

    # def sweep_to(self, channel, new_frequency, duration=1, steps=10):
    #     f0 = self.channel_details(channel)['frequency']
    #     df = (new_frequency - f0) / steps
    #     for i in range(steps):
    #         self.configure_channel(channel, frequency=f0 + (i + 1) * df)
    #         time.sleep(duration / (steps - 1))

    # def ramp_to(self, channel, new_amplitude, duration=1, steps=10):
    #     a0 = self.channel_details(channel)['amplitude']
    #     da = (new_amplitude - a0) / steps
    #     for i in range(steps):
    #         self.configure_channel(channel, amplitude=a0 + (i + 1) * da)
    #         time.sleep(duration / (steps - 1))
    # print(self.channel_details(channel)['amplitude'])


class GenericOscilloscope(Instrument):
    """Base class to represent an oscilloscope.

    """

    ch_in_attrs = ['enabled', 'scale', 'offset']

    def __init__(self, num_inputs):
        channel_specs = {i: self.ch_in_attrs.copy() for i in range(num_inputs)}
        super().__init__(channel_specs)

    def arm(self):
        """Arm the instrument."""
        raise NotImplementedError

    def stop(self):
        """Disarm the instrument."""
        raise NotImplementedError

    def reset(self):
        """Reset to default settings (i.e., auto-configure)."""
        raise NotImplementedError

    # def get_data(self):
    #     raise NotImplementedError
