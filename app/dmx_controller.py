from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
import json
import random
from device import Device
from app_constants import DMX_UPDATE_INTERVAL

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
        self.update_dmx()

    def get_devices(self):
        with open('devices.json', 'r') as file:
            devices_data = json.load(file)["devices"]
        for device_data in devices_data:
            self.device_groups[device_data["type"]] = []
            for i in range(device_data["number"]):
                address = device_data["start_address"] + len(device_data["channels"]) * i
                device = Device(self.set_data, address, device_data["channels"], device_data["type"])
                self.device_groups[device_data["type"]].append(device)
    
    def reset_data(self):
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)
    
    def set_data(self, address, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        
        for channel, value in zip(channels, values):
            self.data[address + channel - 2] = value

    def update_dmx(self):
        self.wrapper.AddEvent(DMX_UPDATE_INTERVAL, self.update_dmx)
        self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)

    def update_current_step(self):
        self.reset_data()
        print("---------NEW STEP----------")
        self.current_step_id = (self.current_step_id + 1) % len(self.app.selected_program["steps"])
        self.current_step = self.app.selected_program["steps"][self.current_step_id]

    def on_beat(self):
        self.beat_count += 1

        if self.beat_count == self.current_step.get("duration"):
            self.beat_count = 0
            self.update_current_step()

        self.run_animations()

        print("beat", self.beat_count)

    def run_animations(self):
        for device_type, devices in self.device_groups.items(): # For each device type
            device_step = self.current_step[device_type]

            for device in devices: # For each device of this type
                for animation_type, animation in device_step.items(): # For each animation type
                    if animation.get("values") != None:
                        if animation.get("type") == "static":
                            value = self.set_static(devices.index(device), animation.get("values"))
                        elif animation.get("type") == "linear":
                            value = self.linear_animation(devices.index(device), animation.get("values"))
                        elif animation.get("type") == "random":
                            value = self.random_animation(animation.get("values"))

                        if animation_type == "color":
                            device.set_color(value, animation.get("fade"))
                        elif animation_type == "intensity":
                            device.set_intensity(value, animation.get("fade"))
                        elif animation_type == "strob":
                            device.set_strob(value)
                        elif animation_type == "position":
                            device.set_position(value)
    
    def linear_animation(self, index, values):
        return values[(self.beat_count + index) % len(values)]

    def random_animation(self, values):
        return values[random.randint(0, len(values) - 1)]
    
    def set_static(self, index, values):
        return values[index % len(values)]
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            #print('Success!')
            pass
            #print(self.data)            
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()