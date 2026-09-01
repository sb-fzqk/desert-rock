import os
import sys
import customtkinter as ctk
from tuner_engine import TunerEngine
from tuner_view import TunerView
from metronome_engine import MetronomeEngine
from metronome_view import MetronomeView

# Get an absolute path to resource (LLM-assisted)
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

ctk.set_default_color_theme(get_resource_path("theme.json"))
ctk.set_appearance_mode("Dark")

# Main app window
class DesertRock(ctk.CTk):
    # Constructor
    def __init__(self):
        super().__init__()

        self.title("Desert Rock")
        self.geometry("350x450")
        self.minsize(350, 450)

        # Engines
        self.tuner_engine = TunerEngine()
        self.metronome_engine = MetronomeEngine()

        self._build_ui()

        # Clean window closure
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.bind("<Key-c>", self._cycle_views)
        self.bind("<Key-C>", self._cycle_views)

    def _build_ui(self):
        self.nav_frame = ctk.CTkFrame(self)
        self.nav_frame.pack(fill="x", padx=10, pady=5)

        self.view_selector = ctk.CTkSegmentedButton(self.nav_frame, values=["Tuner", "Metronome"], command=self._switch_view, font=ctk.CTkFont(size=12, weight="bold"))
        self.view_selector.set("Tuner")
        self.view_selector.pack(fill="x")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=5)

        self.views = {
            "Tuner": TunerView(self.container, tuner_engine=self.tuner_engine),
            "Metronome": MetronomeView(self.container, metronome_engine=self.metronome_engine)
        }

        self._switch_view("Tuner")

    def _switch_view(self, selected_view):
        for view in self.views.values():
            view.pack_forget()
            if hasattr(view, "unbind_shortcuts"):
                view.unbind_shortcuts(self)

        if selected_view == "Metronome":
            self.tuner_engine.stop()
        elif selected_view == "Tuner":
            self.metronome_engine.stop()
            self.tuner_engine.start()

        current_view = self.views[selected_view]
        current_view.pack(fill="both", expand=True)

        if hasattr(current_view, "bind_shortcuts"):
            current_view.bind_shortcuts(self)

    def _cycle_views(self, event=None):
        current_view = self.view_selector.get()
        next_view = "Metronome" if current_view == "Tuner" else "Tuner"

        self.view_selector.set(next_view)
        self._switch_view(next_view)

    def on_closing(self):
        self.tuner_engine.close()
        self.metronome_engine.close()
        self.destroy()

if __name__ == "__main__":
    app = DesertRock()
    app.mainloop()