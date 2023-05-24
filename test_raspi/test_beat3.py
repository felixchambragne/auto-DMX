import threading
import smbus
import numpy as np
import scipy.signal as signal
import time
import keyboard

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

        self.beat_number = 0
    
    def read_pcf8591(self):
        self.bus.write_byte(0x48, 0x40)
        return self.bus.read_byte(0x48)
    
    def detect_bass(self):
        bass_indices = [idx for idx,val in enumerate(self.freqs) if val >= 20 and val <= 90]

        self.bass = np.max(self.psd[bass_indices])
        self.bass_max = max(self.bass_max, self.bass)*0.8
        if self.bass >= self.bass_max*0.8 and not self.bass_beat:
            self.bass_beat = True
            print("bass", round(self.bass*100, 2), "bass_max", round(self.bass_max*100, 2), "Beat", "             ", end='\r')
        elif self.bass < self.bass_max*0.5:
            self.bass_beat = False
        self.bass_max *= 0.95

        print("\n", end='\r')

        if self.bass_beat == True:
            print("BEAT", end='\r')
        else:
            print("     ", end='\r')

    def detect_mid(self):
        mid_indices = [idx for idx,val in enumerate(self.freqs) if val >= 90 and val <= 300]

        self.mid = np.max(self.psd[mid_indices])
        self.mid_max = max(self.mid_max, self.mid)*0.8
        if self.mid >= self.mid_max*0.8 and not self.mid_beat:
            self.mid_beat = True
            print("mid", round(self.mid*100, 2), "mid_max", round(self.mid_max*100, 2), "Beat", "             ", end='\r')
        elif self.mid < self.mid_max*0.5:
            self.mid_beat = False
        self.mid_max *= 0.95

        print("\n", end='\r')

        if self.mid_beat == True:
            print("BEAT", end='\r')
        else:
            print("     ", end='\r')

    def run(self):
        print("start")
        switch = False
        while True:
            for i in range(self.data.shape[0]):
                value = self.read_pcf8591()
                self.data[i] = value
            
            self.freqs, self.psd = signal.welch(self.data, self.framerate, nperseg=self.sample_size)
            peaks, _ = signal.find_peaks(self.psd, height=0.1*np.max(self.psd), distance=50)

            #if key is pressed, switch between bass and mid detection
            if keyboard.is_pressed('q'):
                print("**************SWITCH**************")
                switch = not switch
            
            if switch:
                self.detect_bass()
            else:
                self.detect_mid()


            
            time.sleep(0.001)

if __name__ == "__main__":
    beat_detection =  BeatDetection()
    beat_detection.run()