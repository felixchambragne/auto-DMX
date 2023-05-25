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

        self.bass_max = 0
        self.bass_beat = False
        self.beat_number = 0
    
    def read_pcf8591(self):
        self.bus.write_byte(0x48, 0x40)
        return self.bus.read_byte(0x48)
    
    def detect_bass(self):
        bass_indices = [idx for idx,val in enumerate(self.freqs) if val >= 20 and val <= 90]

        bass = np.max(self.psd[bass_indices])
        self.bass_max = max(self.bass_max, bass)*0.8
        if bass >= self.bass_max*0.8 and not self.bass_beat:
            self.bass_beat = True
            self.on_beat()
            print("OOOOO bass", round(bass*100, 2), "bass_max", round(self.bass_max*100, 2), "             ", end='\r')
        elif bass < self.bass_max*0.5:
            self.bass_beat = False
        self.bass_max *= 0.95

    def detect_mid(self):
        mid_indices = [idx for idx,val in enumerate(self.freqs) if val >= 120 and val <= 300]

        mid = np.max(self.psd[mid_indices])
        self.mid_max = max(self.mid_max, mid)*0.8
        if mid >= self.mid_max*0.8 and not self.mid_beat and not self.bass_beat:
            self.mid_beat = True
            #print("----- mid", round(mid*100, 2), "mid_max", round(self.mid_max*100, 2), "             ", end='\r')
        elif mid < self.mid_max*0.5:
            self.mid_beat = False
        self.mid_max *= 0.95

    def detect_blank(self):
        if len(self.peaks) == 0:
            self.blank_count += 1
        else:
            self.blank_count = 0

        if self.blank_count >= self.blank_duration_threshold and not self.bass_beat and not self.mid_beat:
            #print("Long Blank detected - Silence or no beats to detect", end='\r')
            self.blank_count = 0

    def run(self):
        while True:
            for i in range(self.data.shape[0]):
                value = self.read_pcf8591()
                self.data[i] = value
            
            self.freqs, self.psd = signal.welch(self.data, self.framerate, nperseg=self.sample_size)
            self.peaks, _ = signal.find_peaks(self.psd, height=0.1*np.max(self.psd), distance=50)

            self.detect_bass()
            self.detect_mid()
            self.detect_blank()

            #print("\n", end='\r')

            time.sleep(0.001)