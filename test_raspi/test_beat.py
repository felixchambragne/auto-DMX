import pyaudio
import smbus
import numpy as np

bus = smbus.SMBus(1)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

# Paramètres audio
RATE = 44100
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

# Création du stream PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

# Seuil de détection de beat
THRESHOLD = 5000

# Fonction à enclencher lors d'un beat
def on_beat():
    print("Beat détecté !")

# Analyse en continu des données audio
while True:
    # Lecture d'un échantillon audio
    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

    # Conversion des données audio en tableau NumPy
    samples = np.frombuffer(data, dtype=np.int16)

    # Calcul de l'énergie de signal instantanée
    energy = np.sum(np.square(samples))

    # Détection de beat si l'énergie de signal dépasse le seuil
    if energy > THRESHOLD:
        on_beat()

# Fermeture du stream PyAudio
stream.stop_stream()
stream.close()
p.terminate()
