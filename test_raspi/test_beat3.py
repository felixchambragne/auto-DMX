import smbus
import numpy as np
import scipy.signal as signal
import time
import csv

print("starting...")

sample_size = 256

bus = smbus.SMBus(1)
data = np.zeros(sample_size)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 1000

duration = 100 # seconds
start_time = time.time()

bass_max = 0.001
bass_beat = False
beat_count = 0

threshold = 0.1

print("collecting data...")

while time.time() - start_time < duration:
    for i in range(data.shape[0]):
        value = read_pcf8591()
        data[i] = value 
    
    freqs, psd = signal.welch(data, framerate, nperseg=sample_size)
    peaks, _ = signal.find_peaks(psd, height=threshold*np.max(psd), distance=50)

    bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 200]

    bass = np.max(psd[bass_indices])
    bass_max = max(bass_max, bass)

    if bass >= bass_max*.9 and not bass_beat:
        bass_beat = True
        beat_count += 1
    elif bass < bass_max*.4:
        bass_beat = False
    
    bass_max *= 0.99

    # Ajuster le seuil en fonction de la valeur maximale de la PSD
    if np.max(psd) > 1:
        threshold = 0.1/np.max(psd)
        print(threshold)

    if bass_beat:
        print("bass", round(bass*100, 2), "bass_max", round(bass_max*100, 2), "Beat", beat_count,  "          ", "BEAT", bass_beat, "               ", end='\r')
    else:
        print("bass", round(bass*100, 2), "bass_max", round(bass_max*100, 2), "Beat", beat_count,  "                                          ", end='\r')

    time.sleep(0.001)
