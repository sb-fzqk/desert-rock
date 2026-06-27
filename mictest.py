import pyaudio as pa
import numpy as np

FORMAT = pa.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pa.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print("Recording...")

try:
    while True:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)

        audio_data = np.frombuffer(raw_data, dtype=np.int16)

        peak = np.abs(audio_data).max()

        bars = "-" * int(peak / 500)
        print(f"Volume peak: {peak:<5} {bars}")

except KeyboardInterrupt:
    print("\nStopping stream")

stream.stop_stream()
stream.close()
p.terminate()