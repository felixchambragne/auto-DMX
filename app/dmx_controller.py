from ola.ClientWrapper import ClientWrapper
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import array
import sys
import json
import random
from device import Device
import numpy as np
from app_constants import DMX_UPDATE_INTERVAL, STROB_VALUE, colors
import threading
import time

class DmxController:
    UNIVERSE = 1
    wrapper: ClientWrapper
    
    def __init__(self, app, wrapper) -> None:
        self.app = app
        self.wrapper = wrapper
        self.client = self.wrapper.Client()
        self.device_groups = {}
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)
        self.get_devices()
        self.current_step_id = 0
        self.shape_speed = 0.1
        self.beat_count = 0
        self.update_current_step()
        self.update_dmx()

        self.manual_program_paused = True
        self.program_paused = False

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
        #self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * DMX_UNIVERSE_SIZE)
        pass
    
    def set_data(self, address, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        
        for channel, value in zip(channels, values):
            self.data[address + channel - 2] = value

    def update_dmx(self):
        self.wrapper.AddEvent(DMX_UPDATE_INTERVAL, self.update_dmx)
        if np.any(self.data): # If there is data to send
            self.client.SendDmx(self.UNIVERSE, self.data, self.dmx_sent_callback)

    def update_current_step(self):
        self.reset_data()
        print("---------NEW STEP----------")
        self.current_step_id = (self.current_step_id + 1) % len(self.app.selected_program["steps"])
        self.current_step = self.app.selected_program["steps"][self.current_step_id]
        self.get_shapes()
        
        t = threading.Thread(target=self.set_shapes, args=())
        t.start()

    def get_shapes(self):
        self.shapes = {}
        for device_type, devices in self.device_groups.items():
            device_step = self.current_step[device_type]
            for device in devices:
                shape = device_step.get("shape")
                if shape != None:
                    if shape.get("type") == "random":
                        function = self.random_position_shape
                        args = (shape.get("pan_limit"), shape.get("tilt_limit"))
                    elif shape.get("type") == "circle":
                        function = self.circle_position_shape
                        args = (devices.index(device), device.current_position)
                    elif shape.get("type") == "rect":
                        function = self.rect_position_shape

                        rect = []
                        pan_limit = shape.get("pan_limit")
                        tilt_limit = shape.get("tilt_limit")
                        for i in range(pan_limit[0], pan_limit[1] + 1, 5):
                            rect.append((i, tilt_limit[0]))
                        for i in range(tilt_limit[0], tilt_limit[1] + 1, 5):
                            rect.append((pan_limit[1], i))
                        for i in range(pan_limit[1], pan_limit[0] - 1, -5):
                            rect.append((i, tilt_limit[1]))
                        for i in range(tilt_limit[1], tilt_limit[0] - 1, -5):
                            rect.append((pan_limit[0], i))

                        args = (rect)
                    self.shapes[device] = (function, args)

    def set_shapes(self):
        i = 0
        while self.shapes != {}:
            for device, (function, args) in self.shapes.items():
                value = function(*args, i)
                device.set_position(value)
            i += 1
            time.sleep(self.shape_speed)

    def random_position_shape(self, pan_limit, tilt_limit):
        pan = random.randint(pan_limit[0], pan_limit[1])
        tilt = random.randint(tilt_limit[0], tilt_limit[1])
        return [int(pan), int(tilt)]


    def rect_position_shape(self, rect, i):
        pan = rect[i % len(rect)][0]
        tilt = rect[i % len(rect)][1]
        return [int(pan), int(tilt)]
    
    def on_beat(self):
        if not self.program_paused:
            self.beat_count += 1
            if self.beat_count == self.current_step.get("duration"):
                self.beat_count = 0
                self.update_current_step()
            self.run_animations()
            
            print("beat", self.beat_count)
        else:
            print("Program paused, beat ignored")

    def run_animations(self):
        for device_type, devices in self.device_groups.items(): # For each device type
            device_step = self.current_step[device_type]

            for device in devices: # For each device of this type
                for animation_type, animation in device_step.items(): # For each animation type
                    if animation.get("values") != None and animation_type != "shape":
                        if animation.get("type") == "static":
                            value = self.set_static(devices.index(device), animation.get("values"))
                        elif animation.get("type") == "linear":
                            value = self.linear_animation(devices.index(device), animation.get("values"))
                        elif animation.get("type") == "random":
                            value = self.random_animation(animation.get("values"))
                        elif animation.get("type") == "uniform":
                            value = self.uniform_animation(animation.get("values"))
                        """elif animation.get("type") == "shape" and animation_type == "position":
                            if animation.get("shape") == "random":
                                value = self.random_position_shape(animation.get("pan_limit"), animation.get("tilt_limit"))
                            elif animation.get("shape") == "circle":
                                value = self.circle_position_shape(animation.get("pan_limit"), animation.get("tilt_limit"))"""

                        if animation_type == "color":
                            device.set_color(color_name=value, fade_duration=animation.get("fade"))
                        elif animation_type == "intensity":
                            device.set_intensity(value, animation.get("fade"))
                        elif animation_type == "strob":
                            device.set_strob(value)
                        elif animation_type == "position" and animation.get("values") != "none":
                            device.set_position(value)
                        elif animation_type == "zoom":
                            device.set_zoom(value)

    def linear_animation(self, index, values):
        return values[(self.beat_count + index) % len(values)]

    def random_animation(self, values):
        return values[random.randint(0, len(values) - 1)]

    def uniform_animation(self, values):
        return values[self.beat_count % len(values)]
    
    def set_static(self, index, values):
        return values[index % len(values)]
    
    def on_new_program_selected(self):
        self.beat_count = 0
        self.update_current_step()

    def start_strob(self):
        print("DEBUT STROB")
        #self.previous_data = np.copy(self.data)
        self.program_paused = True
        for device_type, devices in self.device_groups.items(): # For each device type
            for device in devices: # For each device of this type
                device.set_color(color_name="WHITE", fade_duration=0)
                device.set_intensity(255, 0)
                device.set_strob(True)
    
    def stop_strob(self):
        print("FIN STROB")
        #self.data = np.copy(self.previous_data)
        self.program_paused = False
        for device_type, devices in self.device_groups.items(): # For each device type
            for device in devices: # For each device of this type
                device.set_color(color=device.previous_color, fade_duration=0)
                device.set_intensity(device.previous_intensity, 0)
                device.set_strob(device.previous_strob)

    def on_start_blank(self):
        print("AUTOMATIC PAUSE")
        if not self.manual_program_paused:
            #self.pause_program()
            pass

    def on_stop_blank(self):
        print("AUTOMATIC RESUME")
        if not self.manual_program_paused:
            #self.resume_program()
            pass
    
    def pause_program(self):
        self.program_paused = True
        for device_type, devices in self.device_groups.items(): # For each device type
            for device in devices: # For each device of this type
                device.set_intensity(0, 2)

    def resume_program(self):
        self.program_paused = False
        for device_type, devices in self.device_groups.items():
            for device in devices:
                device.set_intensity(device.previous_intensity, 2)
        
    def dmx_sent_callback(self, status):
        if status.Succeeded():
            #print('Success!')
            pass
            #print(self.data)            
        else:
            print('Error: %s' % status.message, file=sys.stderr)
            self.wrapper.Stop()