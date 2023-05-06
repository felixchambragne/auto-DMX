from app_constants import colors

class Device():
    def __init__(self, set_data, address, channels, type) -> None:
        self.address = address
        self.channels = channels
        self.type = type
        self.set_data = set_data

    def set_color(self, color_name):
        color = colors[color_name]
        channels = [self.channels["red"], self.channels["green"], self.channels["blue"]]
        self.set_data(self.address, channels, color)

    def set_intensity(self, value):
        self.set_data(self.address, self.channels["intensity"], value)

