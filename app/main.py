from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
import json
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

        self.current_step = 0
        self.selected_category = "electro"
        self.selected_program_id = 0
        self.update_selected_program()

        with open('programs.json', 'r') as file:
            self.programs_data = json.load(file)["programs"]

    def get_devices(self):
        with open('devices.json', 'r') as file:
            devices_data = json.load(file)["devices"]
        for device_data in devices_data:
            self.device_groups[device_data["type"]] = []
            for i in range(device_data["count"]):
                address = device_data["start_address"] + len(device_data["channels"]) * i
                device = Device(self.set_data, address, device_data["channels"], device_data["type"])
                self.device_groups[device_data["type"]].append(device)

    def update_selected_program(self):
        self.selected_program = self.programs_data[self.selected_category][self.selected_program_id]["steps"]

    def do_step(self, device_type):
        step = self.selected_program[device_type][self.current_step]

        for i in range(step["duration"]):
            for j, device in enumerate(self.device_groups[device_type]):
                color = step["color"][(j + i) % len(step["color"])]
                device.set_color(color)
                intensity = step["intensity"][(j + i) % len(step["intensity"])]
                device.set_intensity()
            self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)
        
    def update_dmx(self):
        for device_types in self.device_groups.keys():
            self.do_step(device_types)
        
        self.current_step = (self.current_step + 1) % len(self.selected_program[self.device_groups.keys()[0]])

        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)
        self.wrapper.AddEvent(self.UPDATE_INTERVAL, self.update_dmx)

    def set_data(self, address, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        
        for channel, value in zip(channels, values):
            self.data[address + channel - 2] = value
        
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
