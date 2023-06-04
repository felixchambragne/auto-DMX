from app_constants import colors as colors_constants
import threading
import time
from app_constants import STROB_VALUE, DMX_UPDATE_INTERVAL

class Device():
    def __init__(self, set_data, address, channels, type) -> None:
        self.address = address
        self.channels = channels
        self.type = type
        self.set_data = set_data

        self.current_color = colors_constants["BLACK"]
        self.previous_color = self.current_color
        self.current_intensity = 0
        self.previous_intensity = self.current_intensity
        self.current_strob = False
        self.previous_strob = self.current_strob

    def set_color(self, color=None, color_name=None, fade_duration=0):
        self.previous_color = self.current_color

        if color is None and color_name is not None:
            color = colors_constants[color_name]

        channels = [self.channels.get("red"), self.channels.get("green"), self.channels.get("blue")]
        if fade_duration > 0:
            t = threading.Thread(target=self.fade_color, args=(channels, color, fade_duration))
            t.start()
        else:
            self.set_data(self.address, channels, color)
            self.current_color = color

    def fade_color(self, channels, target_color, fade_duration):
        fade_steps = int(fade_duration // (DMX_UPDATE_INTERVAL / 1000))
        fade_step_values = [(target - current) / fade_steps for current, target in zip(self.current_color, target_color)]

        for step in range(fade_steps):
            fade_color = tuple(int(current + (step_value * step)) for current, step_value in zip(self.current_color, fade_step_values))

            fade_color = tuple(max(0, min(255, value)) for value in fade_color)  # Correction des valeurs de couleur si nécessaire


            self.set_data(self.address, channels, fade_color)
            self.current_color = fade_color  # Update current_color
            time.sleep(DMX_UPDATE_INTERVAL / 1000)

        self.current_color = target_color
        self.set_data(self.address, channels, target_color)

    def set_intensity(self, value, fade_duration):
        self.previous_intensity = self.current_intensity
        if fade_duration > 0 and self.current_intensity != value:
            t = threading.Thread(target=self.fade_intensity, args=(value, fade_duration))
            t.start()
        else:
            self.current_intensity = value
            self.set_data(self.address, self.channels.get("intensity"), value)
    
    def fade_intensity(self, target_value, fade_duration):
        fade_steps = int(fade_duration // (DMX_UPDATE_INTERVAL / 1000))
        fade_step_value = (target_value - self.current_intensity) / fade_steps

        for step in range(fade_steps):
            fade_value = int(self.current_intensity + (fade_step_value * step))
            if fade_step_value >= 0:
                fade_value = min(fade_value, target_value)
            else:
                fade_value = max(fade_value, target_value)

            self.set_data(self.address, self.channels.get("intensity"), fade_value)
            self.current_intensity = fade_value  # Update current_intensity
            time.sleep(DMX_UPDATE_INTERVAL / 1000)

        self.current_intensity = target_value
        self.set_data(self.address, self.channels.get("intensity"), target_value)
    
    def set_strob(self, strob):
        self.previous_strob = self.current_strob
        if strob == True:
            self.set_data(self.address, self.channels.get("strob"), STROB_VALUE)
        else:
            self.set_data(self.address, self.channels.get("strob"), 0)
        self.current_strob = strob

    def set_position(self, position):
        channels = [self.channels.get("pan"), self.channels.get("tilt")]
        self.set_data(self.address, channels, position)

    def set_zoom(self, zoom):
        self.set_data(self.address, self.channels.get("zoom"), zoom)
    
