import pyaudio as pa
import numpy as np
import scipy.fft as fft
from pitch_utilities import hz_to_note, find_nearest_string

FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096
BIN_SIZE = RATE / CHUNK

# Parabolic interpolation helper funtion (vibe coded)
def get_interpolated_peak(fft_array, max_index, bin_resolution):
    if max_index == 0 or max_index >= len(fft_array) - 1:
        return max_index * bin_resolution
    
    alpha = fft_array[max_index - 1]
    beta = fft_array[max_index]
    gamma = fft_array[max_index + 1]

    denominator = alpha - 2 * beta + gamma
    if denominator == 0:
        return max_index * bin_resolution
    
    p = 0.5 * (alpha - gamma) / denominator
    interpolated_index = max_index + p

    return interpolated_index * bin_resolution
    
p = pa.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

freqs = fft.fftfreq(CHUNK, 1 / RATE)
freq_history = []

print("Go on, pluck a string, don't be afraid.")

try:
    while True:
        raw_input = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(raw_input, dtype=np.int16)

        windowed_data = audio_data * np.hanning(CHUNK)

        fft_result = np.abs(fft.fft(windowed_data))

        positive_fft = fft_result[:CHUNK // 2]
        positive_freqs = freqs[:CHUNK // 2]

        ignore_index = np.where(positive_freqs < 40)[0]
        cleaned_fft = positive_fft.copy()
        cleaned_fft[ignore_index] = 0

        max_index = np.argmax(cleaned_fft)

        if cleaned_fft[max_index] > 100000:
            detected_freq = get_interpolated_peak(cleaned_fft, max_index, BIN_SIZE)

            freq_history.append(detected_freq)
            if len(freq_history) > 3:
                freq_history.pop(0)

            smoothed_freq = sum(freq_history) / len(freq_history)

            note, target_freq, cents = hz_to_note(smoothed_freq)

            if abs(cents) < 5:
                status = "In Tune"
            elif cents < 0:
                status = f"Flat ({cents:.1f} cents)"
            else:
                status = f"Sharp (+{cents:.1f} cents)"

            print(f"Detected Frequency: {smoothed_freq:.2f} Hz; \nNote: {note:<4}; \nStatus: {status} \n>---------<")

except KeyboardInterrupt:
    print("\nStopping stream")

stream.stop_stream()
stream.close()
p.terminate()