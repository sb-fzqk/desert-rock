import customtkinter as ctk
import tkinter as tk
import time
from tuner_engine import TunerEngine

ctk.set_appearance_mode("Dark")

# Tuner gauge class (LLM assisted)
class NeedleGauge(tk.Canvas):
    def __init__(self, master, width=300, height=40, bg_color="#2b2b2b", line_color="#a0a0a0", needle_color="#909090", **kwargs):
        super().__init__(master, width=width, height=height, bg=bg_color, highlightthickness=0, bd=0, **kwargs)

        self.width = width
        self.height = height
        self.center_x = width // 2
        self.needle_color = needle_color

        # Needle track
        self.create_line(20, self.height // 2, width - 20, self.height // 2, fill="#404040", width=2)

        # Target line at the centre
        self.create_line(self.center_x, 5, self.center_x, self.height - 5, fill=line_color, width=3)

        # Moving needle
        self.needle = self.create_line(self.center_x, 5, self.center_x, self.height - 5, fill=self.needle_color, width=4)

    def set_cents(self, cents):
        clamped_cents = max(-50, min(50, cents))
        offset = (clamped_cents / 50.0) * (self.center_x - 30)
        new_x = self.center_x + offset

        self.coords(self.needle, new_x, 5, new_x, self.height - 5)

# GUI frame for the tuner. Observer to TunerEngine
class TunerView(ctk.CTkFrame):
    # Constructor
    def __init__(self, master, tuner_engine: TunerEngine, **kwargs):
        super().__init__(master, **kwargs)
        self.tuner = tuner_engine

        self._build_ui()
        self.tuner.register_observer(self.on_pitch_detected)

        self.default_fg = self.cget("fg_color")

        # Green in-tune indicator stuff
        self.in_tune_start_time = None
        self.is_green = False
        self.IN_TUNE_CENTS_THRESHOLD = 5.0
        self.HOLD_DURATION = 0.5

        # Silence timeout stuff
        self.silence_timer = None
        self.SILENCE_TIMEOUT_MS = 2000

        # Smoothing stuff
        self.current_note = None
        self.cents_history = []
        self.HISTORY_LENGTH = 5

    def _build_ui(self):
        # Header label
        self.title_label = ctk.CTkLabel(self, text="Guitar Tuner", font=ctk.CTkFont(size=12, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Note display
        self.note_label = ctk.CTkLabel(self, text="--", font=ctk.CTkFont(size=64, weight="bold"))
        self.note_label.pack(pady=10)

        # Cents / In tune label
        self.status_label = ctk.CTkLabel(self, text="Pluck a string", font=ctk.CTkFont(size=16))
        self.status_label.pack(pady=5)

        # Frequency label
        self.freq_label = ctk.CTkLabel(self, text="0.00 Hz", font=ctk.CTkFont(size=16))
        self.freq_label.pack(pady=5)

        # Visual tuning gauge
        self.gauge = NeedleGauge(self, width=300, height=40, bg_color="#1f1f1f", line_color="#808080", needle_color="#ffffff")
        self.gauge.pack(pady=(20, 30))

        # Tuning preset drop-down
        self.preset_selector = ctk.CTkOptionMenu(self, values=["Chromatic", "E Standard", "Drop D"], command=self._on_preset_change)
        self.preset_selector.pack(pady=(10, 10))

    # Change tuning preset when requested and reset UI
    def _on_preset_change(self, selected_preset):
        self.tuner.set_preset(selected_preset)
        
        self._reset_ui()

    # Observer callback. Runs on a background thread when TunerEngine gives a new pitch
    def on_pitch_detected(self, note, target_freq, cents, detected_freq):
        self.after(0, self._update_ui, note, target_freq, cents, detected_freq)

    def _update_ui(self, note, target_freq, cents, detected_freq):
        # Reset the silence countdown on every incoming sample
        if self.silence_timer is not None:
            self.after_cancel(self.silence_timer)
        self.silence_timer = self.after(self.SILENCE_TIMEOUT_MS, self._reset_ui)

        # Update the labels
        self.note_label.configure(text=note)
        self.freq_label.configure(text=f"{detected_freq:.2f} Hz (Target: {target_freq:.2f} Hz)")

        current_time = time.time()

        # If current note changes, update and clear the history from last note
        if note != self.current_note:
            self.current_note = note
            self.cents_history.clear()

        # Populate cents history for current note and generate averaged cents
        self.cents_history.append(cents)
        self.cents_history = self.cents_history[-self.HISTORY_LENGTH:]
        smoothed_cents = sum(self.cents_history) / len(self.cents_history)

        # Update the visual gauge, passing in the averaged cents
        self.gauge.set_cents(smoothed_cents)

        # Change text colour depending on the status
        if abs(smoothed_cents) <= self.IN_TUNE_CENTS_THRESHOLD:
            self.status_label.configure(text="In Tune", text_color="#2ed573")

            if self.in_tune_start_time is None:
                self.in_tune_start_time = current_time

            elif current_time - self.in_tune_start_time >= self.HOLD_DURATION:
                if not self.is_green:
                    self.is_green = True
                    self.configure(fg_color="#143d22")

        else:
            self._reset_green_fg()

            if smoothed_cents < 0:
                self.status_label.configure(text=f"Flat ({smoothed_cents:.1f} cents)", text_color="#ff4757")
            else:
                self.status_label.configure(text=f"Sharp (+{smoothed_cents:.1f} cents)", text_color="#ff4757")

    def _reset_ui(self):
        self.note_label.configure(text="--")
        self.status_label.configure(text="Pluck a string", text_color=("black", "white"))
        self.freq_label.configure(text="0.00 Hz")
        self.gauge.set_cents(0)

        self._reset_green_fg()

        self.silence_timer = None

        self.current_note = None
        self.cents_history.clear()

    def _reset_green_fg(self):
        self.in_tune_start_time = None

        if self.is_green:
            self.is_green = False
            self.configure(fg_color=self.default_fg)

# Main app window
class DesertRock(ctk.CTk):
    # Constructor
    def __init__(self):
        super().__init__()

        # Window parameneters
        self.title("Desert Rock")
        self.geometry("350x450")

        # Tuner stuff
        self.tuner_engine = TunerEngine()
        self.tuner_view = TunerView(self, self.tuner_engine)
        self.tuner_view.pack(fill="both", expand=True, padx=20, pady=20)
        self.tuner_engine.start()

        # Clean window closure
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Operations to do upon closing
    def on_closing(self):
        print("Closing...")
        self.tuner_engine.stop()
        self.destroy()

if __name__ == "__main__":
    app = DesertRock()
    app.mainloop()