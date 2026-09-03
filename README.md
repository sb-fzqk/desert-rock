# Desert Rock

**Desert Rock** is a real-time, cross-platform (Linux & macOS) guitar tuner and metronome built for speed, stability, and zero visual bloat. Developed with Python and CustomTkinter.

## Features

### Tuner

* Chromatic mode, plus fixed presets for E Standard and Drop D tunings.
* Real-time note, frequency, and cents-off-pitch display.
* Visual needle gauge with a hold-to-confirm "in tune" indicator.
* Pitch detection via a NumPy implementation of the YIN algorithm.

### Metronome

* Adjustable tempo, 20-400 BPM.
* Configurable beats per measure (1-12).
* Visual beat indicators with an accented downbeat.

## Installation

Prebuilt binaries for Linux and macOS are published on the [Releases page](https://github.com/sb-fzqk/desert-rock/releases) for every tagged version.

> **macOS note:** the app is not code-signed. On first launch, macOS Gatekeeper may warn that it is from an unidentified developer - go to "Privacy & Security" settings, scroll down to "Security" and click "Open Anyway" next to the Desert Rock warning. The app needs microphone access for the tuner - grant it when prompted.

## Running from Source

Requires Python 3.10+.

**Linux only:** install the PortAudio runtime and Tk bindings first, since these are not pulled in by pip:

```bash
sudo apt-get update && sudo apt-get install libportaudio2 python3-tk
```

**Then:**

```bash
git clone https://github.com/sb-fzqk/desert-rock.git
cd desert-rock
pip install -r requirements.txt
python app.py
```

## Building from Source

Binaries are built with [PyInstaller](https://pyinstaller.org) using the included spec file:

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller desert_rock.spec
```

The build output lands in 'dist/'. This is also what the 'build-and-release.yml' GitHub Actions workflow runs automatically for every 'v*' tag.

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `C` | Switch between Tuner and Metronome |
| `Space` | Open tuner preset menu (Tuner) / Play/Stop (Metronome) |
| `←` / `→` | Decrease / increase BPM by 1 (Metronome) |

## Tech Stack

* [CustomTkinter](https://customtkinter.tomschimansky.com/) - UI
* [sounddevice](https://python-sounddevice.readthedocs.io/en/0.5.3/) - Audio I/O
* [NumPy](https://numpy.org/) - Signal processing

## Acknowledgements

* Pitch detection uses a custom implementation of the YIN algorithm described in de Cheveigné, A. & Kawahara, H. (2002). *YIN, a fundamental frequency estimator for speech and music.* The Journal of the Acoustical Society of America, 111(4), 1917-1930.
* Architecture design, audio stream optimisation, audio synthesis, YIN implementation, and cross-platform fixes developed with assistance from large language models.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
