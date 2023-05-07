import smbus
import numpy as np
import scipy.signal as signal
import time

print("starting...")

sample_size = 128

bus = smbus.SMBus(1)
data = np.zeros(sample_size)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 1000

duration = 300 # seconds
start_time = time.time()

bass_max = 0
bass_beat = False
beat_count = 0

print("collecting data...")

while time.time() - start_time < duration:
    for i in range(data.shape[0]):
        value = read_pcf8591()
        data[i] = value 
    
    freqs, psd = signal.welch(data, framerate, nperseg=sample_size)
    peaks, _ = signal.find_peaks(psd, height=0.1*np.max(psd), distance=50)

    bass_indices = [idx for idx,val in enumerate(freqs) if val >= 40 and val <= 90]

    bass = np.max(psd[bass_indices])
    bass_max = max(bass_max, bass)*0.8

    if bass >= bass_max*0.8 and not bass_beat:
        bass_beat = True
        beat_count += 1
        print("bass", round(bass*100, 2), "bass_max", round(bass_max*100, 2), "Beat", beat_count, "             ", end='\r')
    elif bass < bass_max*0.5:
        bass_beat = False
    
    bass_max *= 0.95

    print("\n", end='\r')
    
    if bass_beat == True:
        print("BEAT", end='\r')
    else:
        print("     ", end='\r')
    time.sleep(0.001)
