import random
import sys
from PyQt5 import QtCore, QtWidgets
from bpm import SignalGenerator, AudioAnalyzer

class BeatDetector:
    timer_period = int(round(1000 / (180 / 60) / 16))  # 180bpm / 16

    min_program_beats = 8
    max_program_beats = 8 * 4

    current_intensity = 0
    current_program = 0
    current_program_beats = 0
    change_program = False
    calm_programs = [
        2,  # Full Color Slow
        5,  # Retro
        8,  # Wipe Noise
    ]
    normal_programs = [
        1,  # Full Color Moving
        3,  # Fill Up Once
        6,  # Kitt
    ]
    intense_programs = [
        4,  # Fill Up Repeat
        7,  # Flash Noise
    ]

    def __init__(self) -> None:
        self.auto_prog = False

        # Wire up beat detector and signal generation
        self.audio_analyzer = AudioAnalyzer(self.input_recorder)
        signal_generator = SignalGenerator(self.audio_analyzer)

        # Wire up callbacks
        signal_generator.on_beat(self.on_beat)
        signal_generator.on_bar(self.on_bar)
        signal_generator.on_new_song(self.on_new_song)
        signal_generator.on_bpm_change(self.on_bpm_change)
        signal_generator.on_intensity_change(self.on_intensity_change)

        # Start beat detection
        self.timer = QtCore.QTimer()
        self.timer.start(self.timer_period)

        self.timer.timeout.connect(self.audio_analyzer.analyze_audio)
        self.input_recorder.start()

    def change_program_if_needed(self):
        if self.change_program and self.current_program_beats >= self.min_program_beats:
            new_program = self.choose_program_by_intensity()
            if new_program != self.current_program:
                print("Change program to {:d} for intensity {:d}".format(new_program, self.current_intensity))
                self.current_program = new_program
            self.current_program_beats = 1
            self.change_program = False

    def choose_program_by_intensity(self):
        if self.current_intensity == 1:
            program_list = self.intense_programs
        elif self.current_intensity == -1:
            program_list = self.calm_programs
        else:
            program_list = self.normal_programs
        return random.choice(program_list)

    def on_beat(self, beat_index):
        print("beat", beat_index)
        # Keep track how long current program is running
        if self.auto_prog:
            self.current_program_beats += 1
            if self.current_program_beats > self.max_program_beats:
                self.change_program = True

    def on_bar(self):
        print("NEW bar")
        self.change_program_if_needed()

    def on_new_song(self):
        print("next song")
        self.change_program = True

    def on_bpm_change(self, bpm):
        print("bpm changed", bpm)

    def on_intensity_change(self, intensity):
        self.current_intensity = intensity
        if self.auto_prog:
            self.change_program = True

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Start beat tracking
    beat_detector = BeatDetector()

    code = app.exec_()

    sys.exit(code)