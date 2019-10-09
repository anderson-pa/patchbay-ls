from hardware import base_instruments
from numpy.random import rand


class DummyCamera(base_instruments.Instrument):
    pass


class DummySignalGenerator(base_instruments.GenericSignalGenerator):
    def __init__(self):
        super().__init__(2, has_fm=False)

        defaults = {'enabled': False, 'shape': 'sine', 'frequency': 1e3,
                    'amplitude': 0.1, 'offset': 0, 'phase': 0, 'master': None}

        self._dummy_channels = {c: defaults.copy() for c in self.channel_ids}

    def __str__(self):
        return 'DummySignalGenerator'

    def get_channel_attribute(self, channel_id, name):
        super().get_channel_attribute(channel_id, name)
        return self._dummy_channels[channel_id][name]

    def set_channel_attribute(self, channel_id, name, value):
        super().set_channel_attribute(channel_id, name, value)
        self._dummy_channels[channel_id][name] = value

    def run(self):
        pass


class DummyOscilloscope(base_instruments.GenericOscilloscope):
    def __init__(self):
        super().__init__(2)

    def arm(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass

    def get_data(self):
        return {0: rand(4000),
                1: rand(4000)}
