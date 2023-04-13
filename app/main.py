from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys

#self.data[device.address:device.address+len(device.data)] = device.data

class Controller:
    UNIVERSE = 1
    UPDATE_INTERVAL = 25 #ms
    wrapper: ClientWrapper

    def __init__(self, wrapper) -> None:
        self.wrapper = wrapper
        self.client = self.wrapper.Client()
        self.wrapper.AddEvent(self.UPDATE_INTERVAL, self.update_dmx)
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)

    def update_dmx(self):
        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            print('Success!')
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()

    def run(self) -> None:
        pass

if __name__ == '__main__':
    wrapper = ClientWrapper()
    controller = Controller(wrapper)
    wrapper.Run()
    
