import numpy as np
from abc import ABC, abstractmethod

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

TUNING_PRESETS = {
    "E Standard": {
        "E2": 82.41,
        "A2": 110.00,
        "D3": 146.83, 
        "G3": 196.00,
        "B3": 246.94,
        "E4": 329.63
    },
    "Drop D": {
        "D2": 73.42,
        "A2": 110.00,
        "D3": 146.83, 
        "G3": 196.00,
        "B3": 246.94,
        "E4": 329.63
    }
}

# Abstract base Strategy
class TuningStrategy(ABC):
    @abstractmethod
    def get_target(self, freq):
        pass

# Chromatic Strategy
class ChromaticTuning(TuningStrategy):
    name = "Chromatic"

    def get_target(self, freq):
        if freq <= 0:
            return None, 0.0, 0.0
    
        midi_num = 12 * np.log2(freq / 440.0) + 69
        nearest_midi = int(round(midi_num))

        note_name = NOTES[nearest_midi % 12]
        octave = (nearest_midi // 12) - 1
        full_note = f"{note_name}{octave}"

        target_freq = 440.0 * (2 ** ((nearest_midi - 69) / 12))

        cents = 1200 * np.log2(freq / target_freq)

        return full_note, target_freq, cents

# Base class for fixed guitar note presets
class FixedTuningStrategy(TuningStrategy):
    def __init__(self, target_notes):
        self.target_notes = target_notes

    def get_target(self, freq):
        if freq <= 0:
            return None, 0.0, 0.0

        best_match = min(self.target_notes.keys(), key=lambda note: abs(freq - self.target_notes[note]))

        target_freq = self.target_notes[best_match]
        cents = 1200 * np.log2(freq / target_freq)

        return best_match, target_freq, cents

class EStandardTuning(FixedTuningStrategy):
    def __init__(self):
        super().__init__(TUNING_PRESETS["E Standard"])
        self.name = "E Standard"

class DropDTuning(FixedTuningStrategy):
    def __init__(self):
        super().__init__(TUNING_PRESETS["Drop D"])
        self.name = "Drop D"

class TuningStrategyFactory:
    STRATEGIES = {
        "Chromatic": ChromaticTuning(),
        "E Standard": EStandardTuning(),
        "Drop D": DropDTuning()
    }

    @staticmethod
    def create_strategy(preset_name):
        strategy_class = TuningStrategyFactory.STRATEGIES.get(preset_name)
        if not strategy_class:
            raise ValueError(f"Unknown preset: {preset_name}")

        return strategy_class