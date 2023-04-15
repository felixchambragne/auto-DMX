import array
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)

WHITE = (255, 255, 255)

class Device(object):
    def __init__(self, address) -> None:
        self.address = address
        self.data = None
        self.color = WHITE

    def init_data(self, nb_channels):
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * nb_channels)

    def set_data(self, channels, values):
        for channel, value in zip(channels, values):
            self.data[channel] = value

class PixelBar(Device):
    def __init__(self, address) -> None:
        super().__init__(address)
        self.nb_channels = 36
        self.init_data(self.nb_channels)

    def set_color(self, color):
        self.set_data([i for i in range(12, self.nb_channels)], color*self.nb_channels)

    
