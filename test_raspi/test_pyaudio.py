import pyaudio
import smbus

bus = smbus.SMBus(1)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

# Paramètres audio
RATE = 44100
CHANNELS = 2
FORMAT = pyaudio.paInt16

# Création du stream PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=False, input=True)

# Lecture et traitement en continu
while True:
    # Lecture d'une valeur depuis le microphone
    value = read_pcf8591()

    # Conversion de la valeur en format audio (int16)
    data = value.to_bytes(2, byteorder='little', signed=True)

    # Écriture de la valeur dans le tampon audio
    stream.write(data)

# Fermeture du stream PyAudio
stream.stop_stream()
stream.close()
p.terminate()
