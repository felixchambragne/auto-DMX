import smbus
import numpy as np
from scipy import signal

# set up I2C communication
I2C_ADDRESS = 0x48  # replace with your ADC's I2C address
bus = smbus.SMBus(1)  # replace with the correct I2C bus number

# define the ADC channels
CHANNEL_LEFT = 0  # replace with the correct channel number for the left channel
CHANNEL_RIGHT = 1  # replace with the correct channel number for the right channel

# set up the beat detection parameters
FRAME_SIZE = 2048  # number of samples per frame
HOP_SIZE = 1024  # number of samples between frames
BPM_RANGE = (60, 180)  # range of possible BPM values
ENERGY_THRESHOLD_RATIO = 1.5  # ratio of current energy to average energy threshold for beat detection

# calculate the frequency range for the bandpass filter
SAMPLING_RATE = 44100  # replace with your sampling rate
BANDPASS_FREQ_RANGE = [70, 150]  # replace with your desired frequency range
BANDPASS_ORDER = 3  # order of the filter
BANDPASS_COEFFS = signal.butter(BANDPASS_ORDER, [BANDPASS_FREQ_RANGE[0], BANDPASS_FREQ_RANGE[1]], btype='bandpass', fs=SAMPLING_RATE, output='sos')
#BANDPASS_COEFFS = librosa.filters.band_pass(SAMPLING_RATE, BANDPASS_FREQ_RANGE[0], BANDPASS_FREQ_RANGE[1], BANDPASS_ORDER)

# initialize the energy and beat variables
energy = np.zeros((FRAME_SIZE // 2 + 1,))
average_energy = 1e-9
beat = False

# read audio data from the module and detect beats
while True:
    # read the left channel data
    bus.write_byte(I2C_ADDRESS, 0x40 | (CHANNEL_LEFT << 4))
    data_l = bus.read_word_data(I2C_ADDRESS, 0x00)
    # read the right channel data
    bus.write_byte(I2C_ADDRESS, 0x40 | (CHANNEL_RIGHT << 4))
    data_r = bus.read_word_data(I2C_ADDRESS, 0x00)
    # convert to float and normalize
    data = np.array([data_l, data_r], dtype=np.float32)
    data = (data / 1024.0) - 1.0
    # apply the bandpass filter and calculate the energy
    data_filtered = np.abs(np.fft.rfft(data * BANDPASS_COEFFS, n=FRAME_SIZE))
    energy = 0.9 * energy + 0.1 * data_filtered ** 2
    average_energy = 0.99 * average_energy + 0.01 * np.mean(energy)
    # detect beat if the energy exceeds the threshold
    if np.mean(energy) > ENERGY_THRESHOLD_RATIO * average_energy:
        beat = True
        print("beat detected")
    else:
        beat = False
    
    # TODO: do something with the beat
