import cv2


class WebCamera:
    def __init__(self, src=0):
        self.stream = None
        self.src_id = src
        self.properties = {cv2.CAP_PROP_FRAME_WIDTH: 1280,
                           cv2.CAP_PROP_FRAME_HEIGHT: 720,
                           cv2.CAP_PROP_FPS: 25}
        self.start()
        self._nodemap = DummyNodeMap()
        self._nodemap_tls = DummyNodeMap()

    def read(self, timeout):
        _, frame = self.stream.read()
        return frame

    def start(self):
        if self.stream is None:
            self.stream = cv2.VideoCapture(self.src_id)
            for key, val in self.properties.items():
                self.stream.set(key, val)

    def stop(self):
        self.stream.release()
        self.stream = None


class DummyNodeMap:
    def set(self, *args):
        pass

    def get(self, key):
        nmap = {'HeightMax': 1200,
                'WidthMax': 1920}
        return nmap[key]
