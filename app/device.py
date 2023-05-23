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
        self.current_intensity = 0

    def set_color(self, color_name, fade_duration):
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

        # Calculate fade step for each color channel
        fade_step_values = [(target - current) / fade_steps for target, current in zip(target_color, self.current_color)]

        for step in range(fade_steps):
            fade_color = tuple(int(current + (fade_step * step)) for current, fade_step in zip(self.current_color, fade_step_values))
            fade_color = tuple(min(max(channel, 0), 255) for channel in fade_color)  # Ensure color values are within valid range

            self.set_data(self.address, channels, fade_color)
            self.current_color = fade_color  # Update current_color
            time.sleep(DMX_UPDATE_INTERVAL / 1000)

        self.current_color = target_color
        self.set_data(self.address, channels, target_color)

    def set_intensity(self, value, fade_duration):
        if fade_duration > 0:
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
        if strob == True:
            self.set_data(self.address, self.channels.get("strob"), STROB_VALUE)
        else:
            self.set_data(self.address, self.channels.get("strob"), 0)

    def set_position(self, position):
        channels = [self.channels.get("pan"), self.channels.get("tilt")]
        self.set_data(self.address, channels, position)
    
