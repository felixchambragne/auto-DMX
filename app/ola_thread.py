import threading
from dmx_controller import DmxController
from ola.ClientWrapper import ClientWrapper

class OlaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

        self.wrapper = ClientWrapper()
        self.dmx_controller = DmxController(app, self.wrapper)

    def run(self):

        self.wrapper.Run()
