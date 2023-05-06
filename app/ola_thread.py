import threading
from dmx_controller import DmxController
from ola.ClientWrapper import ClientWrapper

class OlaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

    def run(self):
        #wrapper = ClientWrapper()
        wrapper = None
        dmx_controller = DmxController(self.app, wrapper)
        #wrapper.Run()