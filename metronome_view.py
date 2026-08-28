import customtkinter as ctk
from metronome_engine import MetronomeEngine
import theme

class MetronomeView(ctk.CTkFrame):
    def __init__(self, master, metronome_engine, **kwargs):
        super().__init__(master, **kwargs)
        self.metronome = metronome_engine

        self.beat_indicators = []

        self._build_ui()
        self.metronome.register_observer(self._on_click)

    def _build_ui(self):
        self.bpm_label = ctk.CTkLabel(self, text=f"{self.metronome.bpm}", font=ctk.CTkFont(size=64, weight="bold"))
        self.bpm_label.pack(pady=(35, 10))

        self.slider_frame = ctk.CTkFrame(self)
        self.slider_frame.pack(pady=(0, 20))

        self.decrement_btn = ctk.CTkButton(self.slider_frame, text="-", width=20, height=20, command=lambda: self._adjust_bpm(-1))
        self.decrement_btn.pack(side="left", padx=5, pady=5)

        self.bpm_slider = ctk.CTkSlider(self.slider_frame, from_=20, to=400, number_of_steps=380, command=self._on_slider_change)
        self.bpm_slider.set(self.metronome.bpm)
        self.bpm_slider.pack(side="left", padx=10, expand=True)

        self.increment_btn = ctk.CTkButton(self.slider_frame, text="+", width=20, height=20, command=lambda: self._adjust_bpm(1))
        self.increment_btn.pack(side="right", padx=5, pady=5)

        self.beats_frame = ctk.CTkFrame(self, corner_radius=12)
        self.beats_frame.pack(pady=(15, 5), ipady=6)
        self._rebuild_beat_indicators()

        self.ts_frame = ctk.CTkFrame(self)
        self.ts_frame.pack(pady=(0, 10))

        self.ts_label = ctk.CTkLabel(self.ts_frame, text="Beats / Measure:", font=ctk.CTkFont(size=12))
        self.ts_label.pack(side="left", padx=5, pady=1)

        self.ts_selector = ctk.CTkOptionMenu(self.ts_frame, values=[str(i) for i in range(1, 13)], width=45, height=20, command=self._on_ts_change)
        self.ts_selector.set(str(self.metronome.ts))
        self.ts_selector.pack(side="right", padx=5)

        self.toggle_btn = ctk.CTkButton(self, text="Play", font=ctk.CTkFont(size=18, weight="bold"), height=45, width=160, command=self._toggle_playback)
        self.toggle_btn.pack(pady=25)

    def _rebuild_beat_indicators(self):
        for indicator in self.beat_indicators:
            indicator.destroy()
        self.beat_indicators.clear()

        for _ in range(self.metronome.ts):
            dot = ctk.CTkFrame(self.beats_frame, width=12, height=12, corner_radius=6, fg_color=theme.COLOR_DOT_BLANK)
            dot.pack(side="left", padx=6)
            self.beat_indicators.append(dot)

    # UI event handling
    def _adjust_bpm(self, change):
        new_bpm = self.metronome.bpm + change
        self.metronome.set_bpm(new_bpm)
        self.bpm_slider.set(self.metronome.bpm)
        self.bpm_label.configure(text=f"{self.metronome.bpm}")

    def _on_slider_change(self, value):
        self.metronome.set_bpm(int(value))
        self.bpm_label.configure(text=f"{self.metronome.bpm}")

    def _on_ts_change(self, value):
        self.metronome.set_ts(int(value))
        self._rebuild_beat_indicators()

    def _toggle_playback(self):
        if self.metronome.is_running:
            self.metronome.stop()
            self.toggle_btn.configure(text="Play")
            self._reset_indicators()
        else:
            self.metronome.start()
            self.toggle_btn.configure(text="Stop")

    def _reset_indicators(self):
        for dot in self.beat_indicators:
            dot.configure(fg_color=theme.COLOR_DOT_BLANK)

    # Observer thread sync
    def _on_click(self, beat_num, is_higher):
        self.after(0, self._flash_beat, beat_num - 1, is_higher)

    def _flash_beat(self, beat_index, is_higher):
        if not self.metronome.is_running or beat_index >= len(self.beat_indicators):
            return

        self._reset_indicators()
        dot_colour = theme.COLOR_DOT_DOWNBEAT if is_higher else theme.COLOR_DOT_NORMAL
        self.beat_indicators[beat_index].configure(fg_color=dot_colour)