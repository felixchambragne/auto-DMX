import array
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import constants as const

class Device():
    def __init__(self, address, channels) -> None:
        self.address = address
        self.data = None
        self.color = const.WHITE
        self.intensity = DMX_MIN_SLOT_VALUE
        
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * len(channels))

    def set_data(self, channels, values):
        for channel, value in zip(channels, values):
            self.data[channel] = value

"""class PixelBar(Device):
    def __init__(self, address) -> None:
        super().__init__(address)
        self.nb_channels = 7
        self.init_data(self.nb_channels)

    def set_color(self, color):
        self.set_data()"""

    
