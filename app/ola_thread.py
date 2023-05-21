import threading
from dmx_controller import DmxController
from ola.ClientWrapper import ClientWrapper
import asyncio


class OlaThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

        self.wrapper = ClientWrapper()
        self.dmx_controller = DmxController(app, self.wrapper)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_forever()
        self.wrapper.Run()
