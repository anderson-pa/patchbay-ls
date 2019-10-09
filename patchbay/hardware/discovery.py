from importlib.util import find_spec
from importlib import import_module


class Finder:
    def __init__(self, package_name):
        self.pkg = None
        self.pkg_name = package_name

    def is_available(self):
        return find_spec(self.pkg_name) is not None

    def import_pkg(self):
        self.pkg = import_module(self.pkg_name)

    @property
    def version(self):
        return self.pkg.__version__


class DigilentFinder(Finder):
    def __init__(self):
        super().__init__('dwf')

    @property
    def version(self):
        return self.pkg.FDwfGetVersion()

    def list_devices(self):
        devices = []
        for device in self.pkg.DwfEnumeration():
            devices.append((device.SN(), device.deviceName(),
                            device.isOpened()))
        return devices

    def get_device(self, device_id):
        for device in self.pkg.DwfEnumeration():
            if device.SN() == device_id:
                return device
        return None

    def status(self):
        analogio = self.pkg.DwfAnalogIO()
        analogio.status()
        usbVoltage = analogio.channelNodeStatus(2, 0)
        usbCurrent = analogio.channelNodeStatus(2, 1)
        deviceTemperature = analogio.channelNodeStatus(2, 2)
        auxVoltage = analogio.channelNodeStatus(3, 0)
        auxCurrent = analogio.channelNodeStatus(3, 1)
        print("Temperature: %.2fdegC" % deviceTemperature)
        print("USB:\t%.3fV\t%.3fA" % (usbVoltage, usbCurrent))
        print("AUX:\t%.3fV\t%.3fA" % (auxVoltage, auxCurrent))

    def close_device(self, device_id):
        device = self.get_device(device_id)

        if not device.isOpened():
            dwf_ai = self.pkg.DwfAnalogIn(device)
            channel = dwf_ai.channelCount()
            _, hzFreq = dwf_ai.frequencyInfo()
            print("\tAnalog input channels: " + str(channel))
            print("\tMax freq: " + str(hzFreq))
            dwf_ai.close()

    def close_all_devices(self):
        self.pkg.FDwfDeviceCloseAll()
