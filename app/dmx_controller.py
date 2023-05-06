from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
import json
from device import Device

class DmxController:
    UNIVERSE = 1
    UPDATE_INTERVAL = 1000 #ms
    wrapper: ClientWrapper
    
    def __init__(self, app, wrapper) -> None:
        self.app = app
        self.wrapper = wrapper
        self.client = self.wrapper.Client()
        self.device_groups = {}
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)
        self.get_devices()
        self.current_step_id = 0
        self.update_current_step()
        self.update_dmx()

    def get_devices(self):
        with open('devices.json', 'r') as file:
            devices_data = json.load(file)["devices"]
        for device_data in devices_data:
            self.device_groups[device_data["type"]] = []
            for i in range(device_data["count"]):
                address = device_data["start_address"] + len(device_data["channels"]) * i
                device = Device(self.set_data, address, device_data["channels"], device_data["type"])
                self.device_groups[device_data["type"]].append(device)

    def update_current_step(self):
        self.current_step_id = (self.current_step_id + 1) % len(self.app.current_program["steps"])
        self.current_step = self.app.current_program["steps"][self.current_step_id]

    def on_beat(self):
        print("ok")

    def set_color_animation(self, device_step):
        color_animation = device_step["color"]
    
        
        """["WHITE", "BLUE", "BLUE", "BLUE"][]
        color = color_animation["values"][i % len(device_step["color"])]"""

    def do_step(self):
        for device_type in self.device_groups.keys():
            device_step = self.current_step[device_type]
            
            #self.set_color_animation(device_step)

            """for i in range(device_step["duration"]):
                for j, device in enumerate(self.device_groups[device_type]):
                    color = device_step["color"][(j + i) % len(device_step["color"])]
                    device.set_color(color)
                    intensity = device_step["intensity"][(j + i) % len(device_step["intensity"])]
                    device.set_intensity(intensity)
                self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)"""
        
    def update_dmx(self):
        """self.do_step()
        self.update_current_step()

        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)"""
        pass

    def set_data(self, address, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        
        for channel, value in zip(channels, values):
            self.data[address + channel - 2] = value
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            #print('Success!')
            pass
            #print(self.data)            
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()