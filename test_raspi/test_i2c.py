import smbus

bus = smbus.SMBus(1)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

while True:
    value = read_pcf8591()
    print(value)
