import time

import pytest

from hardware.stepper import Stepper
from tests.test_AnalogDiscovery2 import hdwf


@pytest.fixture
def stepper(hdwf):
    return Stepper(hdwf, range(4, 8))


def test_step_both(stepper):
    stepper.set_divider(2)
    stepper.step(1)
    time.sleep(2)
    print('hello')
    stepper.step(4, True)
    time.sleep(2.2)


def test_step_forward(stepper):
    stepper.set_divider(50)
    stepper.step(128)
    time.sleep(2.8)

def test_step_single(stepper):
    stepper.set_divider(50)
    stepper.step(1)
    time.sleep(0.1)


def test_step_reverse(stepper):
    stepper.set_divider(50)
    stepper.step(128, reverse=True)
    time.sleep(2.8
               )