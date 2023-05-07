import smbus
import numpy as np
import scipy.signal as signal
import time

sample_size = 128
bus = smbus.SMBus(1)
data = np.zeros(sample_size)

def read_pcf8591():
    bus.write_byte(0x48, 0x40)
    return bus.read_byte(0x48)




class AudioAnalyzer:
    min_bpm = 80
    max_bpm = 160
    bpm_history_length = 16  # beats
    freq_history_length = 24  # samples
    intensity_history_length = 128  # samples
    volume_history_length = 3*60  # seconds

    # Timing
    current_time: float
    prev_beat_time: float
    prev_volume_track_time: float

    # BPM
    current_bpm: int
    bpm_history: list

    # Intensity over time
    pause_count = 0
    max_volume = 1000  # Recent max volume
    current_intensity: int
    intensity_history: list
    y_max_history: list
    volume_long_history: list
    low_history: list
    bass_history: list
    low_midrange_history: list
    low_avg_time: -1

    def __init__(self):
        self.RATE = 44100
        self.BUFFERSIZE = 2**10
        self.current_intensity = 0
        self.reset_tracking()
        self.callback_beat_detected = lambda: None
        self.callback_new_song = lambda: None
        self.callback_pause = lambda: None
        self.callback_intensity_changed = lambda: None
        self.prev_volume_track_time = 0
        self.volume_long_history = []

    def reset_tracking(self):
        self.current_bpm = 0
        self.prev_beat_time = time.perf_counter()
        self.bpm_history = []
        self.y_max_history = []
        self.low_history = []
        self.bass_history = []
        self.low_midrange_history = []
        self.low_avg_time = -1
        self.change_intensity(0)
        self.intensity_history = []

    def analyze_audio(self):

        for i in range(data.shape[0]):
            value = read_pcf8591()
            data[i] = value 

        self.current_time = time.perf_counter()
        xs, ys = self.fft(data)
        intensity_samples = ys
        y_max = np.percentile(intensity_samples, 55)
        self.track_max_volume(y_max)

        y_avg = np.percentile(intensity_samples, 50)
        self.track_intensity(y_avg)

        if not self.track_low_volume(y_avg):
            # Calculate frequency average
            low_samples = [ys[i] for i in range(len(xs)) if xs[i] <= 1000]  # Overall low frequencies
            low = np.mean(low_samples)

            bass_samples = [ys[i] for i in range(len(xs)) if 60 <= xs[i] <= 130]  # Bass frequencies
            bass = np.mean(bass_samples)

            low_midrange_samples = [ys[i] for i in range(len(xs)) if 301 <= xs[i] <= 750]  # Low mid-range frequencies
            low_midrange = np.mean(low_midrange_samples)

            # Calculate recent low frequency average
            self.low_history.append(low)
            self.bass_history.append(bass)
            self.low_midrange_history.append(low_midrange)

            # recent_low_avg = numpy.mean(self.low_history)
            recent_bass_avg = np.mean(self.bass_history)
            recent_low_midrange_avg = np.mean(self.low_midrange_history)

            # Check if there is a beat
            if (y_avg > 1000  # Minimum intensity
                    and (
                            bass > recent_bass_avg * self.calculate_threshold(self.bass_history)
                            or low_midrange > recent_low_midrange_avg * self.calculate_threshold(self.low_midrange_history)
                    )
            ):
                # print(self.curr_time - self.prev_beat)
                time_since_last_beat = self.current_time - self.prev_beat_time
                if time_since_last_beat > 60 / self.max_bpm:
                    self.detect_beat(time_since_last_beat)
                    self.prev_beat_time = self.current_time

        # Detect pause in song when missing out more than 3 expected beats
        if self.current_bpm > 0 and self.current_time - self.prev_beat_time > 60 / self.current_bpm * 3.5:
            self.detect_pause()

        self.housekeeping()
    
    def fft(self, data, trim_by=2, log_scale=False, div_by=100):
        left, right = np.split(np.abs(np.fft.fft(data)), 2)
        ys = np.add(left, right[::-1])
        if log_scale:
            ys = np.multiply(20, np.log10(ys))
        xs = np.arange(self.BUFFERSIZE/2, dtype=float)
        if trim_by:
            i = int((self.BUFFERSIZE/2) / trim_by)
            ys = ys[:i]
            xs = xs[:i] * self.RATE / self.BUFFERSIZE
        if div_by:
            ys = ys / float(div_by)
        return xs, ys

    def track_max_volume(self, level):
        self.y_max_history.append(level)
        if self.current_time > self.prev_volume_track_time + 1:
            self.prev_volume_track_time = self.current_time
            self.volume_long_history.append(np.percentile(self.y_max_history, 95))
            if len(self.volume_long_history) > self.volume_history_length:
                self.volume_long_history = self.volume_long_history[1:]
            self.max_volume = np.percentile(self.volume_long_history, 95)

    def track_intensity(self, level):
        self.intensity_history.append(level / self.max_volume)
        if len(self.intensity_history) < self.intensity_history_length / 2:
            return

        avg = np.average(self.intensity_history)
        resistance_to_intense = +0.07
        resistance_to_calm = -0.07
        if self.current_intensity == 1:
            resistance_to_intense = -0.07
            resistance_to_calm = -0.07
        if self.current_intensity == -1:
            resistance_to_intense = +0.07
            resistance_to_calm = +0.07

        if avg > 0.60 + resistance_to_intense:  # Intense
            intensity = 1
        elif avg > 0.45 + resistance_to_calm:  # Normal
            intensity = 0
        else:  # Calm
            intensity = -1

        self.change_intensity(intensity)

    def change_intensity(self, intensity):
        if intensity != self.current_intensity:
            self.current_intensity = intensity
            self.detect_intensity_changed(self.current_intensity)

    def track_low_volume(self, y_avg):
        # Detect very low volume (to detect new track)
        if y_avg < self.max_volume * 0.05:
            if self.low_avg_time == -1:
                self.low_avg_time = self.current_time
        else:
            self.low_avg_time = -1

        # Reset tracking if intensity dropped significantly for multiple iterations
        if y_avg < 100:
            self.detect_new_song()
            return True

        if self.low_avg_time > 0 and (self.current_time - self.low_avg_time) * 1000 > 1000:
            self.detect_new_song()
            return True
        return False

    def housekeeping(self):
        # Shorten the cumulative list to account for changes in dynamics
        if len(self.low_history) > self.freq_history_length:
            self.low_history = self.low_history[1:]
        if len(self.bass_history) > self.freq_history_length:
            self.bass_history = self.bass_history[1:]
        if len(self.low_midrange_history) > self.freq_history_length:
            self.low_midrange_history = self.low_midrange_history[1:]
        if len(self.y_max_history) > self.freq_history_length:
            self.y_max_history = self.y_max_history[1:]
        if len(self.intensity_history) > self.intensity_history_length:
            self.intensity_history = self.intensity_history[1:]
        # Keep two 8-counts of BPMs so we can maybe catch tempo changes
        if len(self.bpm_history) > self.bpm_history_length:
            self.bpm_history = self.bpm_history[1:]

    def calculate_threshold(self, history):
        history_max = np.max(history)
        history_average = np.average(history)
        variance = np.average([np.power((i - history_average) / history_max, 2) for i in history])
        return np.max([-15 * variance + 1.55, 1.2])

    def detect_beat(self, time_since_last_beat):
        print("Detected: Beat")
        bpm_detected = 60 / time_since_last_beat
        if len(self.bpm_history) < 8:
            if bpm_detected > self.min_bpm:
                self.bpm_history.append(bpm_detected)
        else:
            if self.current_bpm == 0 or abs(self.current_bpm - bpm_detected) < 35:
                self.bpm_history.append(bpm_detected)
                # Recalculate with the new BPM value included
                self.current_bpm = self.calculate_bpm()

        self.callback_beat_detected(self.current_time, self.current_bpm)

    def calculate_bpm(self):
        self.reject_outliers(self.bpm_history)
        return np.mean(self.bpm_history)

    def reject_outliers(self, data, m=2.):
        data = np.array(data)
        return data[abs(data - np.mean(data)) < m * np.std(data)]

    def detect_new_song(self):
        #print("Detected: New song")
        self.reset_tracking()
        self.callback_new_song()

    def detect_pause(self):
        print("Detected: Pause")
        self.callback_pause()

    def detect_intensity_changed(self, intensity):
        print("New intensity: {:d}".format(intensity))
        self.callback_intensity_changed(intensity)

    def on_beat_detected(self, callback):
        self.callback_beat_detected = callback

    def on_new_song_detected(self, callback):
        self.callback_new_song = callback

    def on_pause(self, callback):
        self.callback_pause = callback

    def on_intensity_changed(self, callback):
        self.callback_intensity_changed = callback

class BeatDetector:
    timer_period = int(round(1000 / (180 / 60) / 16))  # 180bpm / 16

    min_program_beats = 8
    max_program_beats = 8 * 4

    current_intensity = 0
    current_program = 0
    current_program_beats = 0
    change_program = False

    def __init__(self) -> None:
        self.auto_prog = False

        # Wire up beat detector and signal generation
        self.audio_analyzer = AudioAnalyzer()

    def run(self):
        while True:
            self.audio_analyzer.analyze_audio()

    def on_beat(self, beat_index):
        print("beat", beat_index)
        # Keep track how long current program is running
        if self.auto_prog:
            self.current_program_beats += 1
            if self.current_program_beats > self.max_program_beats:
                self.change_program = True

    def on_bar(self):
        print("NEW bar")

    def on_new_song(self):
        print("next song")
        self.change_program = True

    def on_bpm_change(self, bpm):
        print("bpm changed", bpm)

    def on_intensity_change(self, intensity):
        self.current_intensity = intensity
        if self.auto_prog:
            self.change_program = True

beat_detector = BeatDetector()
beat_detector.run()