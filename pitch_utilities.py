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

# Dependency-free implementation of the YIN pitch estimation algorithm (de Cheveigne & Kawahara, 2002) (LLM-assisted)
class YinPitchDetector:
    def __init__(self, sample_rate, buffer_size, min_freq=40.0, max_freq=2000.0, threshold=0.15):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.threshold = threshold

        # Lag (tau) search range corresponding to the expected pitch range
        self.tau_min = max(2, int(sample_rate / max_freq))
        self.tau_max = min(buffer_size // 2, int(sample_rate / min_freq))

    # Returns frequency and confidence for a mono float buffer. 0.0 for both when no pitch could be estimated
    def detect(self, audio_buffer):
        diff = self._difference_function(audio_buffer)
        cmnd = self._cumulative_mean_normalised_difference(diff)

        tau = self._absolute_threshold(cmnd)
        if tau is None:
            return 0.0, 0.0

        refined_tau = self._parabolic_interpolation(cmnd, tau)
        if refined_tau <= 0:
            return 0.0, 0.0

        freq = self.sample_rate / refined_tau
        confidence = 1.0 - cmnd[tau]

        return float(freq), float(max(0.0, min(1.0, confidence)))

    # Squared-difference function over the lag search range
    def _difference_function(self, x):
        w = self.buffer_size
        diff = np.zeros(self.tau_max + 1)

        for tau in range(1, self.tau_max + 1):
            delta = x[:w - tau] - x[tau:w]
            diff[tau] = np.dot(delta, delta)

        return diff

    # Cumulative mean normalised difference function
    def _cumulative_mean_normalised_difference(self, diff):
        cmnd = np.ones_like(diff)
        running_sum = 0.0

        for tau in range(1, len(diff)):
            running_sum += diff[tau]
            cmnd[tau] = diff[tau] * tau / running_sum if running_sum > 0 else 1.0

        return cmnd

    # First tau under threshold, walked forward to its local minimum
    def _absolute_threshold(self, cmnd):
        for tau in range(self.tau_min, len(cmnd) - 1):
            if cmnd[tau] < self.threshold:
                while tau + 1 < len(cmnd) and cmnd[tau + 1] < cmnd[tau]:
                    tau += 1
                return tau

        return None

    # Parabolic interpolation around tau for a sub-sample estimate
    def _parabolic_interpolation(self, cmnd, tau):
        if tau <= 0 or tau >= len(cmnd) - 1:
            return float(tau)

        s0, s1, s2 = cmnd[tau - 1], cmnd[tau], cmnd[tau + 1]
        denom = 2 * s1 - s2 - s0

        if denom == 0:
            return float(tau)

        return tau + (s2 - s0) / (2 * denom)

# Abstract base Strategy
class TuningStrategy(ABC):
    @abstractmethod
    def get_target(self, freq):
        pass

    @staticmethod
    def _calculate_cents(freq, target_freq):
        if freq <= 0 or target_freq <= 0:
            return 0.0
        return float(1200 * np.log2(freq / target_freq))

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
        cents = self._calculate_cents(freq, target_freq)

        return full_note, float(target_freq), cents

# Base class for fixed guitar note presets
class FixedTuningStrategy(TuningStrategy):
    def __init__(self, target_notes):
        self.target_notes = target_notes

    def get_target(self, freq):
        if freq <= 0 or not self.target_notes:
            return None, 0.0, 0.0

        best_match = min(self.target_notes.keys(), key=lambda note: abs(freq - self.target_notes[note]))

        target_freq = self.target_notes[best_match]
        cents = self._calculate_cents(freq, target_freq)

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
        strategy = TuningStrategyFactory.STRATEGIES.get(preset_name)
        if not strategy:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        return strategy