import pytest
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np


from hardware.basler import BaslerAPI


def test_pass():
    bapi = BaslerAPI()
    cam = bapi.get_camera()

    cam.start()
    im = cam.read()
    plt.imshow(im)
    print(np.min(im))

