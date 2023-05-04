import smbus
import numpy as np
import scipy.signal as signal
import time
import csv

bus = smbus.SMBus(1)
data = np.zeros(32)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)

framerate = 1000

duration = 100 # seconds
start_time = time.time()

values1 = []
values2 = []
timestamps = []
frequencies = []

sub_bass_max = 0.001
bass_max = 0.001
low_midrange_max = 0.001
sub_bass_beat = False
bass_beat = False
low_midrange_beat = False

print("collecting data...")

while time.time() - start_time < duration:
    for i in range(data.shape[0]):
        value = read_pcf8591()
        """timestamp = time.time() - start_time
        timestamps.append(timestamp)
        values1.append(value)"""
        data[i] = value  # Ajout de l'échantillon au tableau de données

    audio_fft = np.abs((np.fft.fft(data)[1:int(len(data)/2)])/len(data))
    freqs = framerate*np.arange(len(data)/2)/len(data)

    """sub_bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 60]
    bass_indices = [idx for idx,val in enumerate(freqs) if val >= 60 and val <= 250]
    low_midrange_indices = [idx for idx,val in enumerate(freqs) if val >= 250 and val <= 450]"""
    sub_bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 200]
    
    """sub_bass = np.max(audio_fft[sub_bass_indices])
    bass = np.max(audio_fft[bass_indices])
    low_midrange = np.max(audio_fft[low_midrange_indices])"""
    sub_bass = np.max(audio_fft[sub_bass_indices])

    """sub_bass_max = max(sub_bass_max, sub_bass)
    bass_max = max(bass_max, bass)
    low_midrange_max = max(low_midrange_max, low_midrange)"""
    sub_bass_max = max(sub_bass_max, sub_bass)

    """if sub_bass >= sub_bass_max*.8 and not sub_bass_beat:
        sub_bass_beat = True
        print("Sub Bass Beat")
    elif sub_bass < sub_bass_max*.5:
        sub_bass_beat = False

    if bass >= bass_max*.8 and not bass_beat:
        bass_beat = True
        print("Bass Beat")
    elif bass < bass_max*.5:
        bass_beat = False

    if low_midrange >= low_midrange_max*.8 and not low_midrange_beat:
        low_midrange_beat = True
        print("Low Midrange Beat")
    elif low_midrange < low_midrange_max*.5:
        low_midrange_beat = False"""

    if sub_bass >= sub_bass_max*.7 and not sub_bass_beat:
        sub_bass_beat = True
        print("Sub Bass Beat")
    elif sub_bass < sub_bass_max*.5:
        sub_bass_beat = False

    """for v in freqs:
        frequencies.append(v)
    for v in audio_fft:
        values2.append(v)"""
    
    time.sleep(0.001)

"""print("saving data...")
def save_data(filename, values, ref):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for i in range(len(values)):
            writer.writerow([ref[i], values[i]])

save_data('data1.csv', values1, timestamps)
save_data('data2.csv', values2, frequencies)"""