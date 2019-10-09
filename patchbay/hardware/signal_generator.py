from collections import namedtuple
from datetime import datetime

import dwf
import visa

from hardware.base_instruments import GenericSignalGenerator


class Agilent33120ASignalGenerator(GenericSignalGenerator):
    _map_command = {(0, 'carrier'): {'enabled': None,
                                     'shape': 'function:shape',
                                     'frequency': 'frequency',
                                     'amplitude': 'voltage',
                                     'offset': 'voltage:offset',
                                     'phase': None,
                                     'master': None},
                    'sync': {'enabled': 'output:sync'}}

    _map_shape = {'SIN': 'sinusoid', 'SQU': 'square', 'TRI': 'triangle',
                  'RAMP': 'ramp', 'NOIS': 'noise', 'DC': 'dc', 'USER': 'user'}

    def __init__(self, resource_name):
        super().__init__(1)
        resource_manager = visa.ResourceManager('@py')
        self.device = resource_manager.open_resource(resource_name)
        self.device.write('system:remote')
        self.errors = []

    def _preformat_channel_value(self, channel_id, attr_name, value):
        formatters = {'enabled': lambda x: x.lower() == 'on'}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def _postformat_channel_value(self, channel_id, attr_name, value):
        formatters = {'enabled': lambda x: True,
                      'shape': lambda x: self._map_shape[x],
                      'frequency': float,
                      'amplitude': float,
                      'offset': float,
                      'phase': lambda x: 0,
                      'master': lambda x: 0}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def get_channel_attribute(self, channel_id, name):
        super().get_channel_attribute(channel_id, name)
        scpi_command = self._map_command[channel_id][name]

        if scpi_command:
            response = self.device.query(scpi_command + '?').strip()
        else:
            response = None
        return self._postformat_channel_value(channel_id, name, response)

    def set_channel_attribute(self, channel_id, name, value):
        super().set_channel_attribute(channel_id, name, value)
        scpi_command = self._map_command[channel_id][name]

        if scpi_command:
            value = self._preformat_channel_value(channel_id, name, value)
            self.device.write(scpi_command + ' {}'.format(value))

    def get_errors(self):
        self.errors.extend([err for err in self._error_buffer()])
        return self.errors

    def clear_errors(self):
        self.errors = []

    def _next_error(self):
        ErrorMessage = namedtuple('ErrorMessage', 'timestamp, code, message')

        error_string = self.device.query('system:error?')
        code, message = error_string.strip().split(',')
        return ErrorMessage(datetime.now(), int(code), message.strip('"'))

    def _error_buffer(self):
        err = self._next_error()
        while err.code:
            yield err
            err = self._next_error()


class AnalogDiscovery2SignalGenerator(GenericSignalGenerator):
    _trigger_sources = dwf.DwfAnalogOut.TRIGSRC
    _states = dwf.DwfAnalogOut.STATE
    _modes = dwf.DwfAnalogOut.MODE
    _idles = dwf.DwfAnalogOut.IDLE

    _map_node_commands = {n: f'node{m.capitalize()}{{}}' for n, m in
                          {'enabled': 'enable',
                           'shape': 'function',
                           'frequency': 'frequency',
                           'amplitude': 'amplitude',
                           'offset': 'offset',
                           'phase': 'phase'}.items()}
    _map_channel_commands = {'master': 'master{}'}

    def __init__(self, device_handle=-1):
        super().__init__(2, has_sync=False)
        self.device = dwf.DwfAnalogOut(device_handle)
        self.device.autoConfigureSet(3)  # turn on dynamic settings

    def __str__(self):
        return 'AnalogDiscovery2SignalGenerator'

    def _preformat_channel_value(self, channel_id, attr_name, value):
        formatters = {'shape': lambda x: self._map_shape(x)}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def _postformat_channel_value(self, channel_id, attr_name, value):
        formatters = {'shape': lambda x: self._map_shape(x.name, reverse=True)}
        try:
            return formatters[attr_name](value)
        except KeyError:
            return value

    def get_channel_attribute(self, channel_id, name):
        super().get_channel_attribute(channel_id, name)

        channel_id = self._map_node(channel_id)
        if name in self._map_node_commands:
            handler_name = self._map_node_commands[name].format('Get')
            value = getattr(self.device, handler_name)(*channel_id)
        elif name in self._map_channel_commands:
            handler_name = self._map_channel_commands[name].format('Get')
            value = getattr(self.device, handler_name)(channel_id[0])
        else:
            value = None

        return self._postformat_channel_value(channel_id, name, value)

    def set_channel_attribute(self, channel_id, name, value):
        super().set_channel_attribute(channel_id, name, value)

        channel_id = self._map_node(channel_id)
        value = self._preformat_channel_value(channel_id, name, value)
        if name in self._map_node_commands:
            handler_name = self._map_node_commands[name].format('Set')
            getattr(self.device, handler_name)(*channel_id, value)

        elif name in self._map_channel_commands:
            handler_name = self._map_channel_commands[name].format('Set')
            getattr(self.device, handler_name)(channel_id[0], value)

    @staticmethod
    def _map_node(channel_id):
        return channel_id[0], dwf.DwfAnalogOut.NODE[channel_id[1].upper()]

    @staticmethod
    def _map_shape(shape, reverse=False):
        if not reverse:
            _map_shape = {'dc': 'DC', 'sinusoid': 'SINE', 'square': 'SQUARE',
                          'triangle': 'TRIANGLE', 'ramp': 'RAMP_UP',
                          'noise': 'NOISE', 'user': 'CUSTOM'}
            return dwf.DwfAnalogOut.FUNC[_map_shape[shape]]
        else:
            _map_shape = {'DC': 'dc', 'SINE': 'sinusoid', 'SQUARE': 'square',
                          'TRIANGLE': 'triangle', 'RAMP_UP': 'ramp',
                          'RAMP_DOWN': 'ramp', 'NOISE': 'noise',
                          'CUSTOM': 'user'}
            return _map_shape[shape]

    def run(self):
        masters = set()
        for c in range(self.device.channelCount()):
            masters.add(self.device.masterGet(c))

        for c in masters:
            if self.channel_details((c, 'carrier'), ['enabled']):
                self.device.configure(c, True)
