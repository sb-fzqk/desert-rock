import numpy as np

STANDARD_GUITAR_TUNING = {
    "E2": 82.41,
    "A2": 110.00,
    "D3": 146.83, 
    "G3": 196.00,
    "B3": 246.94,
    "E4": 329.63
}

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def hz_to_note(freq: float):
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

def e_standard(freq: float):
    if freq <= 0:
        return None, 0.0, 0.0
    
    best_match = None
    smallest_diff = float("inf")

    for note, target in STANDARD_GUITAR_TUNING.items():
        diff = abs(freq - target)
        if diff < smallest_diff:
            smallest_diff = diff
            best_match = note

    target_freq = STANDARD_GUITAR_TUNING[best_match]
    cents = 1200 * np.log2(freq / target_freq)

    return best_match, target_freq, cents