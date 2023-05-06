import threading
from dmx_controller import DmxController
from ola.ClientWrapper import ClientWrapper

class OlaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

        #wrapper = ClientWrapper()
        wrapper = None
        self.dmx_controller = DmxController(self.app, wrapper)

    def run(self):
        #wrapper.Run()
        pass