import smbus
import numpy as np
import scipy.signal as signal

import time
import csv
import os

bus = smbus.SMBus(1)
data = np.zeros(1024)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

def preprocess_data(data):
    if np.var(data) == 0:
        return data
    
    # Normalisation
    data = (data - np.mean(data)) / np.std(data)

    # Filtre passe-bas pour éliminer les hautes fréquences
    b, a = signal.butter(4, 0.1)
    data = signal.filtfilt(b, a, data, axis=0)

    return data

def beat_callback():
    # Code à exécuter à chaque battement de la musique
    print("Beat detected!")
    
sampling_rate = 44100  # Fréquence d'échantillonnage en Hz
beat_threshold = 0.5  # Seuil de détection de battements
prev_freq = 0  # Fréquence dominante précédente

values1 = []
values2 = []
values3 = []
values4 = []
timestamps = []

duration = 10 # seconds
start_time = time.time()

while time.time() - start_time < duration:
    # Collecte des données
    for i in range(data.shape[0]):
        value = read_pcf8591()
        values1.append(value)
        data[i] = value  # Ajout de l'échantillon au tableau de données

    # Prétraitement des données
    data = preprocess_data(data)
    for d in data:
        values2.append(d)

    # Détection des battements
    fft_data = np.fft.fft(data)
    for d in fft_data:
        values3.append(d)
    freqs = np.fft.fftfreq(len(data)) * sampling_rate
    for d in freqs:
        values4.append(d)
    powers = np.abs(fft_data) ** 2
    threshold = np.mean(powers) + np.std(powers)
    indices = np.where(powers > threshold)[0]
    freq = freqs[indices][np.argmax(powers[indices])]
    if abs(freq - prev_freq) > beat_threshold * prev_freq:
        beat_callback()
    prev_freq = freq

    timestamp = time.time()
    timestamps.append(timestamp)

def save_data(filename, values):
    print(values, timestamps)
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for i in range(len(values)):
            writer.writerow([timestamps[i], values[i]])

save_data('data1.csv', values1)
"""save_data('data2.csv', values2)
save_data('data3.csv', values3)
save_data('data4.csv', values4)"""

"""def detect_beats(data, sampling_rate):
    # Transformation de Fourier
    print(data)
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data)) * sampling_rate
    powers = np.abs(fft_data) ** 2

    # Détection de battements
    threshold = np.mean(powers) + np.std(powers)
    indices = np.where(powers > threshold)[0]
    beats = freqs[indices]

    return beats



# Paramètres
sampling_rate = 44100  # Fréquence d'échantillonnage en Hz
beat_threshold = 0.5  # Seuil de détection de battements

while True:
    # Collecte des données
    for i in range(data.shape[0]):
        value = read_pcf8591()
        data[i] = value  # Ajout de l'échantillon au tableau de données

    # Prétraitement des données
    data = preprocess_data(data)

    # Détection des battements
    beats = detect_beats(data, sampling_rate)"""
