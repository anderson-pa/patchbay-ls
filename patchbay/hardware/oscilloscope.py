import dwf
import time

from hardware.base_instruments import GenericOscilloscope


class AnalogDiscovery2Oscilloscope(GenericOscilloscope):
    _acquisition_modes = dwf.DwfAnalogIn.ACQMODE
    _filters = dwf.DwfAnalogIn.FILTER
    _states = dwf.DwfAnalogIn.STATE
    _trigger_conditions = dwf.DwfAnalogIn.TRIGCOND
    _trigger_lengths = dwf.DwfAnalogIn.TRIGLEN
    _trigger_sources = dwf.DwfAnalogIn.TRIGSRC
    _trigger_types = dwf.DwfAnalogIn.TRIGTYPE

    _map_channel_commands = {n: f'channel{m.capitalize()}{{}}' for n, m in
                             {'enabled': 'enable',
                              'offset': 'offset',
                              'scale': 'range'}.items()}

    def __init__(self, device_handle=-1):
        self.device = dwf.DwfAnalogIn(device_handle)
        super().__init__(2)
        self.buffer_size = 4e3
        self.sampling_rate = 20e6

    def _preformat_channel_value(self, channel_id, attr_name, value):
        formatters = {}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def _postformat_channel_value(self, channel_id, attr_name, value):
        formatters = {}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def get_channel_attribute(self, channel_id, name):
        super().get_channel_attribute(channel_id, name)

        if name in self._map_channel_commands:
            handler_name = self._map_channel_commands[name].format('Get')
            value = getattr(self.device, handler_name)(channel_id)
        else:
            value = None

        return self._postformat_channel_value(channel_id, name, value)

    def set_channel_attribute(self, channel_id, name, value):
        super().set_channel_attribute(channel_id, name, value)

        value = self._preformat_channel_value(channel_id, name, value)
        if name in self._map_channel_commands:
            handler_name = self._map_channel_commands[name].format('Set')
            getattr(self.device, handler_name)(channel_id, value)

    def arm(self):
        self.device.configure(False, True)

    def stop(self):
        self.device.configure(False, False)

    def reset(self):
        arm = self.device.status(True) == self._states.DONE
        self.device.configure(True, arm)

    @property
    def buffer_size(self):
        return self.device.bufferSizeGet()

    @buffer_size.setter
    def buffer_size(self, buffer_size):
        self.device.bufferSizeSet(int(buffer_size))

    @property
    def sampling_rate(self):
        return self.device.frequencyGet()

    @sampling_rate.setter
    def sampling_rate(self, sampling_rate):
        self.device.frequencySet(sampling_rate)

    def get_data(self):
        while True:
            sts = self.device.status(True)
            if sts == self._states.DONE:
                break
            time.sleep(0.1)
        valid_samples = self.device.statusSamplesValid()

        data = {}
        for c in self.channel_ids:
            if self.channel_details(c)['enabled']:
                data[c] = self.device.statusData(c, valid_samples)
        return data
