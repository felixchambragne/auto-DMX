from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
from device import PixelBar

class Controller:
    UNIVERSE = 1
    UPDATE_INTERVAL = 25 #ms
    wrapper: ClientWrapper

    def __init__(self, wrapper) -> None:
        self.wrapper = wrapper
        self.client = self.wrapper.Client()
        self.wrapper.AddEvent(self.UPDATE_INTERVAL, self.update_dmx)
        self.devices = []
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)

    def update_dmx(self):
        print("update")
        for device in self.devices:
            device.update()
        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            print('Success!')
            print(self.data)
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()

    def run(self):
        pix = PixelBar(12)
        self.devices.append(pix)
        pix.set_color((255, 0, 125))

if __name__ == '__main__':
    wrapper = ClientWrapper()
    controller = Controller(wrapper)
    controller.run()
    wrapper.Run()
