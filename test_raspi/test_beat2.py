import smbus
import numpy as np
import scipy.signal as signal
import time
import csv

bus = smbus.SMBus(1)
data = np.zeros(1024)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 44100

duration = 10 # seconds
start_time = time.time()

values1 = []
values2 = []
timestamps = []
frequencies = []

while time.time() - start_time < duration:
    value = read_pcf8591()
    timestamp = time.time()
    timestamps.append(timestamp)

    audio_fft = np.abs((np.fft.fft(data)[0:int(len(data)/2)])/len(data))
    freqs = framerate*np.arange(len(data)/2)/len(data)
    print(audio_fft)

    values1.append(value)
    frequencies.append(freqs)
    values2.append(audio_fft)

    # Collecte des données
    """for i in range(data.shape[0]):
        value = read_pcf8591()
        timestamp = time.time()
        timestamps.append(timestamp)
        data[i] = value  # Ajout de l'échantillon au tableau de données

    for d in data:
        values1.append(d)

    audio_fft = np.abs((np.fft.fft(data)[0:int(len(data)/2)])/len(data))
    freqs = framerate*np.arange(len(data)/2)/len(data)

    for d in freqs:
        frequencies.append(d)
    for d in audio_fft:
        values2.append(d)"""

def save_data(filename, values, ref):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for i in range(len(values)):
            writer.writerow([ref[i], values[i]])

save_data('data1.csv', values1, timestamps)
save_data('data2.csv', values2, frequencies)