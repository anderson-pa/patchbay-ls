from hardware.base_instruments import GenericCamera
from pypylon import pylon
import numpy as np


class BaslerAPI():
    def __init__(self):
        first_device = pylon.TlFactory.GetInstance().CreateFirstDevice()
        self.camera = pylon.InstantCamera(first_device)

    def list_cameras(self):
        pass

    def get_camera(self):
        return BaslerCamera(self.camera)


class BaslerCamera(GenericCamera):
    def __init__(self, device_handle):
        super().__init__()
        self.device_handle = device_handle

    def read(self, timeout=500):
        image_out = None
        if self.device_handle.IsGrabbing():
            grabResult = self.device_handle.RetrieveResult(timeout,
                                                           pylon.TimeoutHandling_ThrowException)

            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                # Access the image data.
                print("SizeX: ", grabResult.Width)
                print("SizeY: ", grabResult.Height)
                print("Min: ", np.min(grabResult.Array))
                image_out = grabResult.Array

            else:
                print("Error: ", grabResult.ErrorCode,
                      grabResult.ErrorDescription)
            grabResult.Release()
        return image_out

    def start(self):
        self.device_handle.StartGrabbingMax(5)


    def stop(self):
        self.device_handle.StopGrabbing()
