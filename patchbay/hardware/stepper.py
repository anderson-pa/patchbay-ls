import asyncio

import dwf


class AnalogDiscovery2Stepper:
    """Class to control a stepper motor from the AnalogDiscovery2.

    Sequentially enable pins for the stepper motor. Half steps"""
    _half_steps = [0b0001, 0b0101, 0b0100, 0b0110,
                   0b0010, 0b1010, 0b1000, 0b1001]
    _full_steps = _half_steps[::2]
    _full_steps_2 = _half_steps[1::2]

    def __init__(self, hdwf, pins, use_half_steps=False, step_time=0.002):
        self.device = dwf.DwfDigitalIO(hdwf)
        self.step_time = step_time

        self._pin_mask = None
        self._masked_steps = None
        self.set_pins(pins, use_half_steps)

        self.position = 0

    def set_pins(self, pins, use_half_steps=False):
        """Assign pins to use for the stepper motor.

        In general, this should be an iterable of four integers in the order
        that they should be driven to step forward (i.e., the pins associated
        with wires A A̅ B B̅  of the stepper motor).
        """
        # create a bit mask for the given pins
        self._pin_mask = sum(2 ** p for p in pins)

        # map the step patterns to the given pins
        step_pattern = self._half_steps if use_half_steps else self._full_steps
        self._masked_steps = [sum(2 ** pin * (pos >> i & 1)
                                  for i, pin in enumerate(pins))
                              for pos in step_pattern]

    @asyncio.coroutine
    def step_async(self, num_steps=1, step_time=None):
        direction = 1 if num_steps > 0 else -1
        if not step_time:
            step_time = self.step_time

        self.device.outputEnableSet(
            self.device.outputEnableGet() | self._pin_mask)
        for i in range(abs(num_steps)):
            self.device.outputSet(self.device.outputGet() & (~self._pin_mask)
                                  | self._masked_steps[
                                      (self.position + direction)
                                      % len(self._masked_steps)])
            self.position += direction
            yield from asyncio.sleep(step_time)

        self.device.outputEnableSet(
            self.device.outputEnableGet() & ~self._pin_mask)

    @asyncio.coroutine
    def go_to(self, position, step_time=None):
        yield from self.step_async(position - self.position,
                                   step_time=step_time)
