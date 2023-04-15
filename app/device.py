import array
from ola.DMXConstants import (DMX_MAX_SLOT_VALUE, DMX_MIN_SLOT_VALUE, DMX_UNIVERSE_SIZE)
import constants as const

class Device():
    def __init__(self, address, channels, type) -> None:
        self.address = address
        self.channels = channels
        self.type = type

        #self.color = const.BLACK
        #self.intensity = DMX_MIN_SLOT_VALUE
        self.data = array.array('B', [DMX_MIN_SLOT_VALUE] * len(self.channels))

    def set_data(self, channels, values):
        if type(channels) is not list and type(channels) is not tuple:
            channels = [channels]
        if type(values) is not list and type(values) is not tuple:
            values = [values]
        for channel, value in zip(channels, values):
            self.data[channel-1] = value

    def set_color(self, color):
        channels = [self.channels["red"], self.channels["green"], self.channels["blue"]]
        self.set_data(channels, color)

    def set_intensity(self, value):
        self.set_data(self.channels["intensity"], value)

