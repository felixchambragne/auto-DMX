import smbus
import numpy as np
import scipy.signal as signal
import time
import csv

print("starting...")

bus = smbus.SMBus(1)
data = np.zeros(256)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 1000

duration = 100 # seconds
start_time = time.time()

bass_max = 0.001
bass_beat = False
beat_count = 0

segment_size = 256

# Number of previous segments used to calculate the threshold
n_past_segments = 10

# Threshold factor
threshold_factor = 1.5

# Initialize threshold
threshold = 0

print("collecting data...")

while time.time() - start_time < duration:
        # Read data
    for i in range(segment_size):
        value = read_pcf8591()
        data[i] = value
    
    # Compute energy of current segment
    energy = np.sum(data**2)

    # Update threshold
    if beat_detected:
        threshold = np.mean(energies[-n_past_segments:]) * threshold_factor
    
    # Compare energy with threshold
    if energy > threshold:
        if not beat_detected:
            beat_detected = True
            beat_count += 1
            print("Beat", beat_count, end='\r')
    else:
        beat_detected = False
    
    # Update energy buffer
    if 'energies' not in locals():
        energies = np.zeros(n_past_segments)
    energies[:-1] = energies[1:]
    energies[-1] = energy
    time.sleep(0.001)