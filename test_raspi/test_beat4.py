import threading
import smbus
import numpy as np
import scipy.signal as signal
import time

class BeatDetection():
    def __init__(self):
    
        self.sample_size = 128
        self.bus = smbus.SMBus(1)
        self.data = np.zeros(self.sample_size)
        self.framerate = 1000

        self.bass_max = 0
        self.bass_beat = False

        self.mid_max = 0
        self.mid_beat = False

        self.blank_duration_threshold = 20
        self.blank_count = 0
    
    def read_pcf8591(self):
        self.bus.write_byte(0x48, 0x40)
        return self.bus.read_byte(0x48)
    
    def detect_bass(self):
        bass_indices = [idx for idx, val in enumerate(self.freqs) if val >= 20 and val <= 90]

        bass = np.max(self.psd[bass_indices])
        self.bass_max = max(self.bass_max, bass) * 0.8
        
        # Vérifier si un pic se trouve dans les fréquences de basses
        bass_peaks = np.intersect1d(self.peaks, bass_indices)
        
        # Calculer la moyenne des amplitudes des pics dans les fréquences de basses
        if len(bass_peaks) > 0:
            bass_peak_amplitudes = self.psd[bass_peaks]
            average_amplitude = np.mean(bass_peak_amplitudes)
        else:
            average_amplitude = 0
        
        if average_amplitude >= self.bass_max * 0.8 and not self.bass_beat:
            self.bass_beat = True
            print("OOOOO bass", round(average_amplitude * 100, 2), "bass_max", round(self.bass_max * 100, 2), "             ", end='\r')
        elif average_amplitude < self.bass_max * 0.5:
            self.bass_beat = False
        self.bass_max *= 0.95
        

    def detect_mid(self):
        mid_indices = [idx for idx,val in enumerate(self.freqs) if val >= 120 and val <= 300]

        mid = np.max(self.psd[mid_indices])
        self.mid_max = max(self.mid_max, mid) * 0.8
        
        # Vérifier si un pic se trouve dans les fréquences moyennes
        mid_peaks = np.intersect1d(self.peaks, mid_indices)
        
        # Calculer la moyenne des amplitudes des pics dans les fréquences moyennes
        if len(mid_peaks) > 0:
            mid_peak_amplitudes = self.psd[mid_peaks]
            average_amplitude = np.mean(mid_peak_amplitudes)
        else:
            average_amplitude = 0
        
        if average_amplitude >= self.mid_max * 0.8 and not self.mid_beat and not self.bass_beat:
            self.mid_beat = True
            print("----- mid", round(average_amplitude * 100, 2), "mid_max", round(self.mid_max * 100, 2), "             ", end='\r')
        elif average_amplitude < self.mid_max * 0.5:
            self.mid_beat = False
        self.mid_max *= 0.95

    def detect_blank(self):
        if len(self.peaks) == 0 or (self.mid_max < 0.01 and self.bass_max < 0.01):
            self.blank_count += 1
        else:
            self.blank_count = 0

        if self.blank_count >= self.blank_duration_threshold and not self.bass_beat and not self.mid_beat:
            print("Long Blank detected - Silence or no beats to detect", end='\r')
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

            print("\n", end='\r')

            time.sleep(0.001)

if __name__ == "__main__":
    beat_detection =  BeatDetection()
    beat_detection.run()