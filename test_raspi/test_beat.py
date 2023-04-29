import pyaudio
import numpy as np
from scipy.fftpack import fft
import smbus

# Variables de configuration
CHUNK = 1024
RATE = 44100
THRESHOLD = 12000
SILENCE_LIMIT = 10
DETECT_LENGTH = 50

# Initialisation de l'interface I2C
bus = smbus.SMBus(1)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

# Initialisation de PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Boucle de détection de beat
beat_detected = False
silence_count = 0
while True:
    # Lecture des échantillons audio
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.int16)

    # Calcul de la FFT
    fft_data = fft(audio_data)
    freqs = np.fft.fftfreq(len(fft_data))

    # Obtention de la puissance des fréquences basses
    low_freqs = np.where(freqs >= 0)[0][:len(freqs)//2]
    power = np.abs(fft_data[low_freqs])**2

    # Détection de beat
    if np.max(power) > THRESHOLD and not beat_detected:
        beat_detected = True
        silence_count = 0
    elif beat_detected:
        silence_count += 1
        if silence_count >= SILENCE_LIMIT:
            beat_detected = False