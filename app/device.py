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
        channels = [self.channels["red"], self.channels["green"], self.channels["blue"]]
        self.set_data(self.address, channels, color)
        self.current_color = color

    def set_intensity(self, value, fade_duration):
        if fade_duration > 0:
            t = threading.Thread(target=self.fade_intensity, args=(value, fade_duration))
            t.start()
        else:
            self.current_intensity = value
            self.set_data(self.address, self.channels["intensity"], value)

    def fade_intensity(self, target_value, fade_duration):
        fade_steps = int(fade_duration // (DMX_UPDATE_INTERVAL / 1000))
        fade_step_value = (target_value - self.current_intensity) / fade_steps

        for step in range(fade_steps):
            fade_value = int(self.current_intensity + (fade_step_value * step))
            if fade_step_value >= 0:
                if fade_value > target_value:
                    fade_value = target_value
            else:
                if fade_value < target_value:
                    fade_value = target_value

            self.set_data(self.address, self.channels["intensity"], fade_value)
            time.sleep(DMX_UPDATE_INTERVAL / 1000)
            
        self.current_intensity = target_value
        self.set_data(self.address, self.channels["intensity"], target_value)
        
    """def set_intensity(self, value, fade_time):
        fade_thread = None
        if fade_thread and fade_thread.is_alive(): # If a fade is already in progress, interrupt it
            fade_interrupted = True
            fade_thread.join()
        
        if fade_time == 0: # No Fade
            self.set_data(self.address, self.channels["intensity"], value)
            self.set_current_intensity(value)
        else: # Fade
            fade_interrupted = False
            fade_thread = threading.Thread(target=self.start_fade, args=(value, self.channels["intensity"], fade_time, fade_interrupted, self.current_intensity, self.set_current_intensity))
            fade_thread.start()"""

    """def set_current_intensity(self, value):
        self.current_intensity = value
        
    def start_fade(self, target_value, channel, fade_time, fade_interrupted, current_value, set_current_value):
        start_time = time.time()
        end_time = start_time + fade_time

        while time.time() < end_time:
            if fade_interrupted:
                return
            
            elapsed_time = time.time() - start_time
            progress = elapsed_time / fade_time
            new_value = current_value + (target_value - current_value) * progress

            new_value = max(0, min(255, int(new_value)))

            self.set_data(self.address, channel, new_value) # Set the new intensity value
            set_current_value(new_value)

            time.sleep(0.01)  # Adjust sleep time as needed

        self.set_data(self.address, channel, target_value) # Ensure the target value is set at the end of the fade
        set_current_value(target_value)"""
    
    def set_strob(self, strob):
        if strob == True:
            self.set_data(self.address, self.channels["strob"], STROB_VALUE)
        else:
            self.set_data(self.address, self.channels["strob"], 0)

    def set_position(self, position):
        channels = [self.channels["pan"], self.channels["tilt"]]
        self.set_data(self.address, channels, position)
    
