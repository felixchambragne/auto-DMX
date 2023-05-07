import smbus
import numpy as np
import scipy.signal as signal
import time

sample_size = 128

bus = smbus.SMBus(1)
data = np.zeros(sample_size)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 1000

duration = 100 # seconds
start_time = time.time()

bass_max = 0
bass_beat = False
beat_count = 0

print("collecting data...")

def fft(self, data, trim_by=2, log_scale=False, div_by=100):
    left, right = np.split(np.abs(np.fft.fft(data)), 2)
    ys = np.add(left, right[::-1])
    if log_scale:
        ys = np.multiply(20, np.log10(ys))
    xs = np.arange(self.BUFFERSIZE/2, dtype=float)
    if trim_by:
        i = int((self.BUFFERSIZE/2) / trim_by)
        ys = ys[:i]
        xs = xs[:i] * self.RATE / self.BUFFERSIZE
    if div_by:
        ys = ys / float(div_by)
    return xs, ys

while time.time() - start_time < duration:
    for i in range(data.shape[0]):
        value = read_pcf8591()
        data[i] = value 
    
    xs, ys = fft(data)
    
    time.sleep(0.001)


