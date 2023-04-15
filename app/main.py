from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
import json
import constants as const
from device import Device

class Controller:
    UNIVERSE = 1
    UPDATE_INTERVAL = 1000 #ms
    wrapper: ClientWrapper
    
    def __init__(self, wrapper) -> None:
        self.wrapper = wrapper
        self.client = self.wrapper.Client()
        self.wrapper.AddEvent(self.UPDATE_INTERVAL, self.update_dmx)
        self.device_groups = {}
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)
        self.get_devices()

    def get_devices(self):
        with open('devices.json', 'r') as file:
            data = json.load(file)
        for device_data in data["devices"]:
            self.device_groups[device_data["type"]] = []
            for i in range(device_data["count"]):
                address = device_data["start_address"] + len(device_data["channels"]) * i
                device = Device(self.set_data, address, device_data["channels"], device_data["type"])
                self.device_groups[device_data["type"]].append(device)

    def update_dmx(self):
        for device in self.device_groups["washbeam"]:
            device.set_color(const.WHITE)
            device.set_intensity(125)
        
        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)
        self.wrapper.AddEvent(self.UPDATE_INTERVAL, self.update_dmx)

    def set_data(self, address, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        
        print(channels)

        for channel, value in zip(channels, values):
            self.data[address + channel] = value
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            print('Success!')
            #print(self.data)            
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()

if __name__ == '__main__':
    wrapper = ClientWrapper()
    controller = Controller(wrapper)
    wrapper.Run()
