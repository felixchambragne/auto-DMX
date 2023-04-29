import smbus
import struct
import librosa
import time

# Define the I2C bus and device addresses
DEVICE_ADDRESS = 0x48

# Initialize the I2C bus and device
bus = smbus.SMBus(1)

# Set up the audio data buffer and the sample rate
buffer_size = 1024
sample_rate = 22050
audio_buffer = []

# Continuously read audio data from the I2C device and detect beats
while True:
    # Read a block of audio data from the I2C device
    audio_data = []
    for i in range(buffer_size):
        # Read a signed 16-bit integer from the I2C device
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, i*2, 2)
        sample = struct.unpack(">h", bytes(data))[0]
        audio_data.append(sample)
    
    # Convert the audio data to a numpy array with the correct sample rate
    audio_data = librosa.util.fix_length(audio_data, sample_rate)
    audio_data = librosa.resample(audio_data, 44100, sample_rate)
    
    # Append the audio data to the audio buffer
    audio_buffer.extend(audio_data)
    
    # If the audio buffer is long enough, detect the beats
    if len(audio_buffer) >= sample_rate:
        # Slice the audio buffer to the correct length
        audio_slice = audio_buffer[:sample_rate]
        
        # Detect the beats in the audio slice
        tempo, beats = librosa.beat.beat_track(audio_slice, sr=sample_rate)
        
        # Print the tempo and the indices of the detected beats
        print("Tempo: {:.2f} BPM".format(tempo))
        print("Beat indices:", beats)
        
        # Remove the processed audio data from the audio buffer
        audio_buffer = audio_buffer[sample_rate:]
    
    # Wait for a short period of time to control the loop rate
    time.sleep(0.01)
