from app_constants import colors
import threading
import time
from app_constants import STROB_VALUE

class Device():
    def __init__(self, set_data, address, channels, type) -> None:
        self.address = address
        self.channels = channels
        self.type = type
        self.set_data = set_data

        self.fade_thread = None

        self.current_color = "BLACK"
        self.current_intensity = 0

    def set_color(self, color_name):
        color = colors[color_name]
        channels = [self.channels["red"], self.channels["green"], self.channels["blue"]]
        self.set_data(self.address, channels, color)
        self.current_color = color

    def set_intensity(self, value, fade_time):
        if self.fade_thread and self.fade_thread.is_alive(): # If a fade is already in progress, interrupt it
            self.fade_interrupted = True
            self.fade_thread.join()
        
        if fade_time == 0: # No Fade
            self.set_data(self.address, self.channels["intensity"], value)
            self.current_intensity = value
        else: # Fade
            self.fade_interrupted = False
            self.fade_thread = threading.Thread(target=self.fade_intensity, args=(value, fade_time))
            self.fade_thread.start()
        
    def fade_intensity(self, target_value, fade_time):
        start_time = time.time()
        end_time = start_time + fade_time

        while time.time() < end_time:
            if self.fade_interrupted:
                return
            
            elapsed_time = time.time() - start_time
            progress = elapsed_time / fade_time
            new_value = self.current_intensity + (target_value - self.current_intensity) * progress

            new_value = max(0, min(255, int(new_value)))

            self.set_data(self.address, self.channels["intensity"], new_value) # Set the new intensity value
            self.current_intensity = new_value

            time.sleep(0.1)  # Adjust sleep time as needed

        self.set_data(self.address, self.channels["intensity"], target_value) # Ensure the target value is set at the end of the fade
        self.current_intensity = target_value
    
    def set_strob(self, strob):
        if strob == True:
            self.set_data(self.address, self.channels["strob"], STROB_VALUE)
        else:
            self.set_data(self.address, self.channels["strob"], 0)

    def set_position(self, position):
        channels = [self.channels["pan"], self.channels["tilt"]]
        self.set_data(self.address, channels, position)
    
