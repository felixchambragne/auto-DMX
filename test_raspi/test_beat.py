import smbus
import numpy as np
import scipy.signal as signal

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

while True:
    # Collecte des données
    for i in range(data.shape[0]):
        value = read_pcf8591()
        data[i] = value  # Ajout de l'échantillon au tableau de données

    # Prétraitement des données
    data = preprocess_data(data)

    # Détection des battements
    fft_data = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(data)) * sampling_rate
    powers = np.abs(fft_data) ** 2
    threshold = np.mean(powers) + np.std(powers)
    indices = np.where(powers > threshold)[0]
    freq = freqs[indices][np.argmax(powers[indices])]
    if abs(freq - prev_freq) > beat_threshold * prev_freq:
        beat_callback()
    prev_freq = freq


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
