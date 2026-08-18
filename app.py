import customtkinter as ctk
from tuner_engine import TunerEngine
from tuner_view import TunerView

ctk.set_appearance_mode("Dark")

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