import librosa
import pyaudio
import numpy as np

# Configuration du flux audio
CHUNK_SIZE = 1024
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100

# Initialisation de PyAudio
p = pyaudio.PyAudio()

# Ouverture du flux audio
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

# Fonction de détection de tempo en temps réel
def detect_tempo(y, sr):
    # Calcul de l'enveloppe d'onset
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Détection de tempo
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    
    # Traitement des beats détectés
    print(f"Tempo: {tempo}")
    print(f"Beats: {beats}")

# Boucle de traitement audio en temps réel
while True:
    # Lecture d'un chunk audio
    audio_data = stream.read(CHUNK_SIZE)
    
    # Conversion des données audio en tableau NumPy
    audio_buffer = np.frombuffer(audio_data, dtype=np.float32)
    
    # Détection de tempo sur le chunk audio
    detect_tempo(audio_buffer, RATE)