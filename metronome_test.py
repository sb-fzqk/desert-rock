import time
from metronome_engine import MetronomeEngine


def on_beat(beat_num, is_higher):
    marker = "beep" if is_higher else "boop"
    print(f"[{beat_num}] {marker}")


if __name__ == "__main__":
    print("Testing Metronome Engine...")
    metronome = MetronomeEngine(bpm=120, bpme=4)

    metronome.register_observer(on_beat)

    print("\n120 BPM 4/4:")
    metronome.start()
    time.sleep(4)

    print("\n180 BPM 4/4:")
    metronome.set_bpm(180)
    time.sleep(4)

    print("\n180 BPM 3/4:")
    metronome.set_bpme(3)
    time.sleep(4)

    print("\n90 BPM 5/4:")
    metronome.set_bpm(90)
    metronome.set_bpme(5)
    time.sleep(8)

    print("\nStopping engine...")
    metronome.stop()