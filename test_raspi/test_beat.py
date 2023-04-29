import smbus
import numpy as np
import scipy.fftpack as fft

bus = smbus.SMBus(1)

# Fréquence d'échantillonnage du signal audio
fs = 44100

# Nombre d'échantillons à analyser pour chaque FFT
chunk_size = 2048

# Seuil de puissance des basses fréquences pour la détection de beats
power_threshold = 0.1

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

while True:
    # Lecture d'un chunk de données audio depuis le PCF8591
    data = [read_pcf8591() for i in range(chunk_size)]

    # Conversion des données en un tableau NumPy de flottants normalisés entre -1 et 1
    data = np.array(data) / 128.0 - 1.0

    # Application d'une fenêtre de Hamming aux données pour réduire les effets de bord
    data *= np.hamming(len(data))

    # Calcul de la FFT des données
    fft_data = fft.fft(data)

    # Extraction de la puissance des basses fréquences (entre 20 Hz et 200 Hz)
    freqs = fft.fftfreq(len(data), 1.0 / fs)
    idx = np.logical_and(freqs >= 20, freqs <= 200)
    power = np.sum(np.abs(fft_data[idx]) ** 2)

    # Si la puissance des basses fréquences dépasse le seuil, on considère qu'il y a un beat
    if power > power_threshold:
        print("Beat detected!")
