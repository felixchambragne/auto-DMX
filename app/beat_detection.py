import threading
import smbus
import numpy as np
import scipy.signal as signal
import time

class BeatDetection(threading.Thread):
    def __init__(self, on_beat):
        threading.Thread.__init__(self)
        self.on_beat = on_beat

        self.sample_size = 128
        self.bus = smbus.SMBus(1)
        self.data = np.zeros(self.sample_size)
        self.framerate = 1000
        self.duration = 100 # seconds

        self.bass_max = 0
        self.bass_beat = False
        self.beat_number = 0
    
    def read_pcf8591(self):
        self.bus.write_byte(0x48, 0x40)
        return self.bus.read_byte(0x48)

    def run(self):
        while True:
            for i in range(self.data.shape[0]):
                value = self.read_pcf8591()
                self.data[i] = value
                print(value)
            
            freqs, psd = signal.welch(self.data, self.framerate, nperseg=self.sample_size)
            peaks, _ = signal.find_peaks(psd, height=0.1*np.max(psd), distance=50)

            bass_indices = [idx for idx,val in enumerate(freqs) if val >= 20 and val <= 90]

            self.bass = np.max(psd[bass_indices])
            self.bass_max = max(self.bass_max, self.bass)*0.8

            print(self.bass, self.bass_max)

            if self.bass >= self.bass_max*0.8 and not self.bass_beat:
                self.bass_beat = True
                self.on_beat()
            elif self.bass < self.bass_max*0.5:
                self.bass_beat = False
            self.bass_max *= 0.95
            
            time.sleep(0.001)