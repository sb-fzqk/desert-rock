import customtkinter as ctk
from tuner_engine import TunerEngine
from tuner_view import TunerView
from metronome_engine import MetronomeEngine
from metronome_view import MetronomeView

# Main app window
class DesertRock(ctk.CTk):
    # Constructor
    def __init__(self):
        super().__init__()

        self.title("Desert Rock")
        self.geometry("350x450")
        self.minsize(350, 450)

        ctk.set_appearance_mode("Dark")

        # Engines
        self.tuner_engine = TunerEngine()
        self.metronome_engine = MetronomeEngine()

        self._build_ui()

        # Clean window closure
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(fill="x", padx=10, pady=5)

        self.view_selector = ctk.CTkSegmentedButton(self.nav_frame, values=["Tuner", "Metronome"], command=self._switch_view, font=ctk.CTkFont(size=12, weight="bold"))
        self.view_selector.set("Tuner")
        self.view_selector.pack(fill="x")

        self.container = ctk.CTkFrame(self, fg_color="#1f1f1f")
        self.container.pack(fill="both", expand=True, padx=10, pady=5)

        self.views = {
            "Tuner": TunerView(self.container, tuner_engine=self.tuner_engine),
            "Metronome": MetronomeView(self.container, metronome_engine=self.metronome_engine)
        }

        self._switch_view("Tuner")

    def _switch_view(self, selected_view):
        for view in self.views.values():
            view.pack_forget()

        if selected_view == "Metronome":
            self.tuner_engine.stop()
        elif selected_view == "Tuner":
            self.metronome_engine.stop()
            self.tuner_engine.start()

        self.views[selected_view].pack(fill="both", expand=True)

    def on_closing(self):
        self.tuner_engine.close()
        self.metronome_engine.close()
        self.destroy()

if __name__ == "__main__":
    app = DesertRock()
    app.mainloop()