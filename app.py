import customtkinter as ctk
import time
from tuner_engine import TunerEngine

ctk.set_appearance_mode("Dark")

# GUI frame for the tuner. Observer to TunerEngine
class TunerView(ctk.CTkFrame):
    # Constructor
    def __init__(self, master, tuner_engine: TunerEngine, **kwargs):
        super().__init__(master, **kwargs)
        self.tuner = tuner_engine

        self._build_ui()
        self.tuner.register_observer(self.on_pitch_detected)

        self.default_fg = self.cget("fg_color")

        self.in_tune_start_time = None
        self.is_green = False
        self.IN_TUNE_CENTS_THRESHOLD = 5.0
        self.HOLD_DURATION = 0.5

        self.silence_timer = None
        self.SILENCE_TIMEOUT_MS = 2000

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
        self.gauge = ctk.CTkProgressBar(self, width=300, height=14)
        self.gauge.set(0.5)
        self.gauge.pack(pady=(20, 30))

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

        # Update the visual gauge
        clamped_cents = max(-50, min(50, cents))
        gauge_position = 0.5 + (clamped_cents / 100.0)
        self.gauge.set(gauge_position)

        # Change text colour depending on the status
        if abs(cents) <= self.IN_TUNE_CENTS_THRESHOLD:
            self.status_label.configure(text="In Tune", text_color="#2ed573")

            if self.in_tune_start_time is None:
                self.in_tune_start_time = current_time

            elif current_time - self.in_tune_start_time >= self.HOLD_DURATION:
                if not self.is_green:
                    self.is_green = True
                    self.configure(fg_color="#143d22")

        else:
            self._reset_green_fg()

            if cents < 0:
                self.status_label.configure(text=f"Flat ({cents:.1f} cents)", text_color="#ff4757")
            else:
                self.status_label.configure(text=f"Sharp (+{cents:.1f} cents)", text_color="#ff4757")

    def _reset_ui(self):
        self.note_label.configure(text="--")
        self.status_label.configure(text="Pluck a string")
        self.freq_label.configure(text="0.00 Hz")
        self.gauge.set(0.5)

        self._reset_green_fg()

        self.silence_timer = None

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