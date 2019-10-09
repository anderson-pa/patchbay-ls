import dwf


class AnalogDiscovery2Servo:
    def __init__(self, hdwf, pin, cal=None, limits=None,
                 slope=1.1/120, t_mid=1.5,
                 theta_min=-80, theta_max=80):
        self.device = dwf.DwfDigitalOut(hdwf)
        self.pin = None
        self.set_pin(pin)

        self.theta_min = theta_min
        self.theta_max = theta_max
        self.t_mid = t_mid
        self.slope = slope

        self.cc = True

    def set_pin(self, pin):
        if self.pin:
            self.device.enableSet(self.pin, False)
        self.pin = pin
        self.device.idleSet(pin, dwf.DwfDigitalOutIdleLow)
        self.device.enableSet(pin, True)
        self.device.dividerSet(pin, 100)  # set clock to microseconds
        # self.device.counterInitSet(pin, False, 0)  # what is default?

    def set_position(self, angle):
        angle = max(angle, self.theta_min)
        angle = min(angle, self.theta_max)

        self.set_pulse_width(angle * self.slope + self.t_mid)

    @property
    def position(self):
        _, counts_high = self.device.counterGet(self.pin)
        position = (counts_high / 1000 - self.t_mid) / self.slope
        return position

    @position.setter
    def position(self, angle):
        self.set_position(angle)

    def set_cal_position(self, p=0):
        """Set to 1 or 2 ms pulse width"""
        if p not in [0, 1]:
            return
        self.set_pulse_width(1 + p)

    def set_pulse_width(self, t_pulse):
        # pulse width given in milliseconds
        c = int(1000 * t_pulse)
        self.device.counterSet(self.pin, 20000 - c, c)
        self.device.configure(1)
