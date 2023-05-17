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
        self.beat_count = 0
        self.update_current_step()

    def get_devices(self):
        with open('devices.json', 'r') as file:
            devices_data = json.load(file)["devices"]
        for device_data in devices_data:
            self.device_groups[device_data["type"]] = []
            for i in range(device_data["number"]):
                address = device_data["start_address"] + len(device_data["channels"]) * i
                device = Device(self.set_data, address, device_data["channels"], device_data["type"])
                self.device_groups[device_data["type"]].append(device)

    def update_current_step(self):
        print("---------NEW STEP----------")
        self.current_step_id = (self.current_step_id + 1) % len(self.app.selected_program["steps"])
        self.current_step = self.app.selected_program["steps"][self.current_step_id]

    def on_beat(self):
        self.beat_count += 1
        if self.beat_count == self.current_step["duration"]:
            self.update_current_step()
            self.beat_count = 0
        print("beat", self.beat_count)
        self.do_step()
        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)

    def do_step(self):
        for device_type, devices in self.device_groups.items():
            device_step = self.current_step[device_type]

            color_animation = device_step["color"]
            intensity_animation = device_step["intensity"]
            
            color_values = color_animation["values"]
            intensity_values = intensity_animation["values"]

            for index, device in enumerate(devices):
                color = color_values[(self.beat_count + index) % len(color_values)]
                intensity = intensity_values[(self.beat_count + index) % len(intensity_values)]

                device.set_color(color)
                device.set_intensity(intensity)
        
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