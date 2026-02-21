# app.py

import os
import sys
import threading
import traceback
import wave

import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps
from pysstv.color import Robot36, MartinM1, MartinM2, ScottieS1, ScottieS2, ScottieDX

try:
    from pysstv.color import Robot72
except ImportError:
    Robot72 = None

from decode import SSTVDecoder
from common import log_message


TEXTS = {
    "English": {
        "app_title": "SSTV Studio",
        "app_tagline": "Encode images into SSTV audio and decode signals back to images.",
        "action_choose": "Choose a direction",
        "card_encode_title": "Encode",
        "card_encode_desc": "Turn a picture into a clean SSTV audio signal.",
        "card_decode_title": "Decode",
        "card_decode_desc": "Recover an image from an SSTV audio file.",
        "button_encode": "Open Encoder",
        "button_decode": "Open Decoder",
        "header_encoder": "SSTV Encoder",
        "header_decoder": "SSTV Decoder",
        "upload_hint": "Click to upload an image",
        "upload_image": "Upload Image",
        "remove_image": "Remove Image",
        "mode_label": "SSTV Mode",
        "play_signal": "Generate & Play",
        "stop_playback": "Stop",
        "save_wav": "Save WAV",
        "load_audio": "Load SSTV Audio",
        "save_image": "Save Image",
        "clear_image": "Clear",
        "back": "Back",
        "status_ready": "Ready",
        "status_loaded": "Image loaded",
        "status_playing": "Playing…",
        "status_saved": "Saved",
        "status_decoding": "Decoding…",
        "status_decoded": "Decoded",
        "detected_mode_none": "Detected Mode: None",
        "detected_mode_unknown": "Detected Mode: Unknown",
        "signal_saved": "SSTV signal saved as '{}'",
        "no_sstv_signal": "No SSTV signal found.",
        "info_title": "About",
        "version_info": "SSTV Studio\nVersion: 2.0.0",
        "language_label": "Language",
        "error": "Error",
        "success": "Success",
        "info": "Info",
        "no_playback": "No playback to stop.",
        "image_files": "Image files",
        "wav_files": "WAV files",
        "please_select_image": "Please select an image first.",
        "unsupported_mode": "Unsupported mode: {}",
        "image_load_error": "Failed to load image: {}",
        "failed_generate_play": "Failed to generate and play SSTV signal: {}",
        "failed_generate_save": "Failed to generate and save SSTV signal: {}",
        "failed_decode_sstv": "Failed to decode SSTV signal: {}",
        "failed_save_image": "Failed to save image: {}",
        "no_decoded_image": "No decoded image to save.",
        "decoded_image_saved": "Decoded image saved as '{}'",
    },
    "Romanian": {
        "app_title": "SSTV Studio",
        "app_tagline": "Codifică imagini în audio SSTV și decodifică semnale înapoi în imagini.",
        "action_choose": "Alege o direcție",
        "card_encode_title": "Codificare",
        "card_encode_desc": "Transformă o imagine într-un semnal SSTV curat.",
        "card_decode_title": "Decodificare",
        "card_decode_desc": "Recuperează o imagine dintr-un fișier audio SSTV.",
        "button_encode": "Deschide Codificator",
        "button_decode": "Deschide Decodificator",
        "header_encoder": "Codificator SSTV",
        "header_decoder": "Decodificator SSTV",
        "upload_hint": "Apasă pentru a încărca o imagine",
        "upload_image": "Încarcă Imagine",
        "remove_image": "Șterge Imagine",
        "mode_label": "Mod SSTV",
        "play_signal": "Generează & Redă",
        "stop_playback": "Oprește",
        "save_wav": "Salvează WAV",
        "load_audio": "Încarcă Audio SSTV",
        "save_image": "Salvează Imaginea",
        "clear_image": "Curăță",
        "back": "Înapoi",
        "status_ready": "Gata",
        "status_loaded": "Imagine încărcată",
        "status_playing": "Redare…",
        "status_saved": "Salvat",
        "status_decoding": "Decodificare…",
        "status_decoded": "Decodat",
        "detected_mode_none": "Mod Detectat: Niciunul",
        "detected_mode_unknown": "Mod Detectat: Necunoscut",
        "signal_saved": "Semnal SSTV salvat ca '{}'",
        "no_sstv_signal": "Nu s-a găsit semnal SSTV.",
        "info_title": "Despre",
        "version_info": "SSTV Studio\nVersiune: 2.0.0",
        "language_label": "Limba",
        "error": "Eroare",
        "success": "Succes",
        "info": "Info",
        "no_playback": "Nu există redare de oprit.",
        "image_files": "Fișiere imagine",
        "wav_files": "Fișiere WAV",
        "please_select_image": "Te rog selectează mai întâi o imagine.",
        "unsupported_mode": "Mod nesuportat: {}",
        "image_load_error": "Eroare la încărcarea imaginii: {}",
        "failed_generate_play": "Eroare la generarea și redarea semnalului SSTV: {}",
        "failed_generate_save": "Eroare la generarea și salvarea semnalului SSTV: {}",
        "failed_decode_sstv": "Eroare la decodificarea semnalului SSTV: {}",
        "failed_save_image": "Eroare la salvarea imaginii: {}",
        "no_decoded_image": "Nu există imagine decodată de salvat.",
        "decoded_image_saved": "Imaginea decodată a fost salvată ca '{}'",
    },
}


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SSTVApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.language = "English"
        self.selected_image = None
        self.sstv_signal = None
        self.is_playing = False
        self.decoded_image_reference = None

        self.mode_var = tk.StringVar(value="Robot 36")
        self.lang_display_var = tk.StringVar(value="English")
        self.status_var = tk.StringVar(value="")
        self.wait_var = tk.StringVar(value="")
        self.detected_mode_var = tk.StringVar(value="")

        self._image_preview = None
        self._decoded_preview = None
        self._detected_mode_name = None
        self._detected_mode_unknown = False
        self._is_decoding = False

        self._text_widgets = []
        self._dynamic_updaters = []

        self._setup_window()
        self._setup_style()
        self._setup_background()
        self._setup_layout()
        self._set_language("English")

    def tr(self, key):
        return TEXTS[self.language].get(key, key)

    def _setup_window(self):
        self.title(TEXTS[self.language]["app_title"])
        self.geometry("980x680")
        self.minsize(860, 600)
        self.configure(bg="#f5f0e7")

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as exc:
                print(f"Error setting icon: {exc}")

    def _setup_style(self):
        self.colors = {
            "bg_start": "#f5f0e7",
            "bg_end": "#cfe8e1",
            "card": "#ffffff",
            "ink": "#1f2a30",
            "muted": "#5a6b74",
            "accent": "#e76f51",
            "accent_alt": "#2a9d8f",
            "border": "#dde3dc",
        }

        self.fonts = {
            "title": ("Bahnschrift SemiBold", 22),
            "subtitle": ("Bahnschrift", 11),
            "heading": ("Bahnschrift SemiBold", 14),
            "body": ("Bahnschrift", 11),
            "button": ("Bahnschrift SemiBold", 11),
        }

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=self.colors["card"])
        style.configure("Card.TFrame", background=self.colors["card"], relief="flat")
        style.configure("Header.TFrame", background=self.colors["card"])
        style.configure("Body.TFrame", background=self.colors["card"])
        style.configure(
            "Title.TLabel",
            background=self.colors["card"],
            foreground=self.colors["ink"],
            font=self.fonts["title"],
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=self.fonts["subtitle"],
        )
        style.configure(
            "Heading.TLabel",
            background=self.colors["card"],
            foreground=self.colors["ink"],
            font=self.fonts["heading"],
        )
        style.configure(
            "Body.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=self.fonts["body"],
        )
        style.configure(
            "Status.TLabel",
            background=self.colors["card"],
            foreground=self.colors["accent_alt"],
            font=self.fonts["body"],
        )
        style.configure(
            "Muted.TLabel",
            background=self.colors["card"],
            foreground=self.colors["muted"],
            font=self.fonts["body"],
        )

        style.configure(
            "Primary.TButton",
            font=self.fonts["button"],
            foreground="#ffffff",
            background=self.colors["accent"],
            padding=(14, 8),
            borderwidth=0,
        )
        style.map("Primary.TButton", background=[("active", "#de5e40")])

        style.configure(
            "Secondary.TButton",
            font=self.fonts["button"],
            foreground=self.colors["ink"],
            background="#f1f3f2",
            padding=(14, 8),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#e5e8e6")])

        style.configure(
            "Ghost.TButton",
            font=self.fonts["button"],
            foreground=self.colors["accent_alt"],
            background=self.colors["card"],
            padding=(10, 6),
            borderwidth=0,
        )
        style.map("Ghost.TButton", background=[("active", "#eef5f3")])

        style.configure(
            "Link.TButton",
            font=self.fonts["body"],
            foreground=self.colors["accent_alt"],
            background=self.colors["card"],
            padding=(6, 2),
            borderwidth=0,
        )

        style.configure("TCombobox", padding=(6, 4))

    def _setup_background(self):
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.bg_canvas.bind("<Configure>", self._draw_background)

    def _setup_layout(self):
        self.content = ttk.Frame(self.bg_canvas, style="App.TFrame")
        self.bg_window = self.bg_canvas.create_window(0, 0, window=self.content, anchor="nw")

        self.header = ttk.Frame(self.content, style="Header.TFrame")
        self.header.pack(fill="x", padx=32, pady=(28, 10))

        self.body = ttk.Frame(self.content, style="Body.TFrame")
        self.body.pack(fill="both", expand=True, padx=32, pady=(8, 24))

        self._build_header()
        self.show_main_view()

        self.bg_canvas.bind("<Configure>", self._position_content)

    def _position_content(self, event):
        width = max(760, event.width - 60)
        height = max(520, event.height - 60)
        width = min(width, 980)
        height = min(height, 680)
        self.bg_canvas.itemconfigure(self.bg_window, width=width, height=height)
        x = (event.width - width) / 2
        y = (event.height - height) / 2
        self.bg_canvas.coords(self.bg_window, x, y)

    def _draw_background(self, event):
        self.bg_canvas.delete("bg")
        self._draw_gradient(
            0,
            0,
            event.width,
            event.height,
            self.colors["bg_start"],
            self.colors["bg_end"],
        )

        width = event.width
        height = event.height
        self.bg_canvas.create_oval(
            width * 0.62,
            -height * 0.2,
            width * 1.15,
            height * 0.6,
            fill="#f2d8c9",
            outline="",
            tags="bg",
        )
        self.bg_canvas.create_oval(
            -width * 0.2,
            height * 0.35,
            width * 0.45,
            height * 1.1,
            fill="#d7efe8",
            outline="",
            tags="bg",
        )

    def _draw_gradient(self, x0, y0, x1, y1, color1, color2):
        steps = 120
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        for i in range(steps):
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y = y0 + int((y1 - y0) * ratio)
            self.bg_canvas.create_rectangle(x0, y, x1, y + 4, outline="", fill=color, tags="bg")

    @staticmethod
    def _hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _build_header(self):
        self.header.columnconfigure(0, weight=1)

        title_frame = ttk.Frame(self.header, style="Header.TFrame")
        title_frame.grid(row=0, column=0, sticky="w")

        self.title_label = ttk.Label(title_frame, style="Title.TLabel")
        self.title_label.pack(anchor="w")
        self._bind_text(self.title_label, "app_title")

        self.subtitle_label = ttk.Label(title_frame, style="Subtitle.TLabel")
        self.subtitle_label.pack(anchor="w")
        self._bind_text(self.subtitle_label, "app_tagline")

        control_frame = ttk.Frame(self.header, style="Header.TFrame")
        control_frame.grid(row=0, column=1, sticky="e")

        self.lang_label = ttk.Label(control_frame, style="Body.TLabel")
        self.lang_label.grid(row=0, column=0, padx=(0, 8))
        self._bind_text(self.lang_label, "language_label")

        self.lang_combo = ttk.Combobox(
            control_frame,
            textvariable=self.lang_display_var,
            values=["English", "Română"],
            state="readonly",
            width=10,
        )
        self.lang_combo.grid(row=0, column=1, padx=(0, 10))
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        self.about_button = ttk.Button(
            control_frame,
            style="Ghost.TButton",
            text="About",
            command=self._show_about,
        )
        self.about_button.grid(row=0, column=2)

    def _bind_text(self, widget, key):
        widget._text_key = key
        self._text_widgets.append(widget)
        widget.configure(text=self.tr(key))

    def _refresh_texts(self):
        for widget in self._text_widgets:
            key = getattr(widget, "_text_key", None)
            if key:
                widget.configure(text=self.tr(key))

        for updater in self._dynamic_updaters:
            updater()

        self.title(self.tr("app_title"))
        self.lang_combo.set("Română" if self.language == "Romanian" else "English")
        self.about_button.configure(text=self.tr("info_title"))
        if self._is_decoding:
            self.wait_var.set(self.tr("status_decoding"))

    def _show_about(self):
        messagebox.showinfo(self.tr("info_title"), self.tr("version_info"))

    def _on_language_change(self, _event=None):
        label = self.lang_display_var.get()
        self._set_language("Romanian" if label == "Română" else "English")

    def _set_language(self, lang):
        self.language = lang
        self._refresh_texts()

    def _clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()
        self._text_widgets = [w for w in self._text_widgets if w.winfo_exists()]
        self._dynamic_updaters = []

    def _stagger_show(self, widgets, delay=70):
        for index, widget in enumerate(widgets):
            widget.grid_remove()
            self.after(delay * index, widget.grid)

    def show_main_view(self):
        self._clear_body()

        self.status_var.set("")

        title = ttk.Label(self.body, style="Heading.TLabel")
        title.grid(row=0, column=0, sticky="w")
        self._bind_text(title, "action_choose")

        cards = ttk.Frame(self.body, style="Body.TFrame")
        cards.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        cards.columnconfigure(0, weight=1)
        cards.columnconfigure(1, weight=1)

        encode_card = self._make_card(
            cards,
            "card_encode_title",
            "card_encode_desc",
            "button_encode",
            self.show_encode_view,
        )
        encode_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        decode_card = self._make_card(
            cards,
            "card_decode_title",
            "card_decode_desc",
            "button_decode",
            self.show_decode_view,
        )
        decode_card.grid(row=0, column=1, sticky="nsew", padx=(14, 0))

        self.body.rowconfigure(1, weight=1)
        self._stagger_show([encode_card, decode_card])

    def _make_card(self, parent, title_key, desc_key, button_key, command):
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.columnconfigure(0, weight=1)

        title = ttk.Label(card, style="Heading.TLabel")
        title.grid(row=0, column=0, sticky="w")
        self._bind_text(title, title_key)

        desc = ttk.Label(card, style="Body.TLabel", wraplength=280, justify="left")
        desc.grid(row=1, column=0, sticky="w", pady=(6, 14))
        self._bind_text(desc, desc_key)

        button = ttk.Button(card, style="Primary.TButton", command=command)
        button.grid(row=2, column=0, sticky="w")
        self._bind_text(button, button_key)

        return card

    def show_encode_view(self):
        self._clear_body()

        header = ttk.Label(self.body, style="Heading.TLabel")
        header.grid(row=0, column=0, sticky="w")
        self._bind_text(header, "header_encoder")

        layout = ttk.Frame(self.body, style="Body.TFrame")
        layout.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        layout.columnconfigure(0, weight=1)
        layout.columnconfigure(1, weight=1)

        self.image_card = ttk.Frame(layout, style="Card.TFrame", padding=16)
        self.image_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.image_card.columnconfigure(0, weight=1)

        self.image_canvas = tk.Canvas(
            self.image_card,
            width=360,
            height=270,
            bg="#f1f3f2",
            highlightthickness=0,
        )
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        self.image_canvas.bind("<Button-1>", lambda _e: self.load_image())

        self._show_upload_prompt()

        controls = ttk.Frame(layout, style="Card.TFrame", padding=16)
        controls.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        controls.columnconfigure(0, weight=1)

        mode_label = ttk.Label(controls, style="Body.TLabel")
        mode_label.grid(row=0, column=0, sticky="w")
        self._bind_text(mode_label, "mode_label")

        mode_options = ["Robot 36"]
        if Robot72 is not None:
            mode_options.append("Robot 72")
        mode_options.extend(
            [
                "Martin M1",
                "Martin M2",
                "Scottie S1",
                "Scottie S2",
                "Scottie DX",
            ]
        )
        self.mode_combo = ttk.Combobox(controls, textvariable=self.mode_var, values=mode_options, state="readonly")
        self.mode_combo.grid(row=1, column=0, sticky="ew", pady=(6, 12))

        self.play_button = ttk.Button(controls, style="Primary.TButton", command=self.generate_and_play_sstv)
        self.play_button.grid(row=2, column=0, sticky="ew")

        self.save_wav_button = ttk.Button(controls, style="Secondary.TButton", command=self.download_sstv)
        self.save_wav_button.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self._bind_text(self.save_wav_button, "save_wav")

        self.remove_button = ttk.Button(controls, style="Ghost.TButton", command=self.remove_image)
        self.remove_button.grid(row=4, column=0, sticky="w", pady=(12, 0))
        self._bind_text(self.remove_button, "remove_image")

        self.back_button = ttk.Button(controls, style="Link.TButton", command=self.show_main_view)
        self.back_button.grid(row=5, column=0, sticky="w", pady=(18, 0))
        self._bind_text(self.back_button, "back")

        self.status_label = ttk.Label(
            controls,
            style="Status.TLabel",
            textvariable=self.status_var,
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.status_label.grid(row=6, column=0, sticky="ew", pady=(12, 0))

        self._dynamic_updaters.append(self._refresh_play_button)
        self._dynamic_updaters.append(self._refresh_status_label)
        self._dynamic_updaters.append(self._refresh_upload_prompt)
        self._refresh_play_button()
        self._refresh_status_label()

        self.body.rowconfigure(1, weight=1)

        self._stagger_show([self.image_card, controls])

    def show_decode_view(self):
        self._clear_body()

        header = ttk.Label(self.body, style="Heading.TLabel")
        header.grid(row=0, column=0, sticky="w")
        self._bind_text(header, "header_decoder")

        layout = ttk.Frame(self.body, style="Body.TFrame")
        layout.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        layout.columnconfigure(0, weight=1)
        layout.columnconfigure(1, weight=1)

        preview_card = ttk.Frame(layout, style="Card.TFrame", padding=16)
        preview_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        preview_card.columnconfigure(0, weight=1)

        self.decoded_canvas = tk.Canvas(
            preview_card,
            width=360,
            height=270,
            bg="#f1f3f2",
            highlightthickness=0,
        )
        self.decoded_canvas.grid(row=0, column=0, sticky="nsew")

        self._detected_mode_name = None
        self._detected_mode_unknown = False
        self._set_detected_mode_label()
        self.detected_label = ttk.Label(preview_card, style="Body.TLabel", textvariable=self.detected_mode_var)
        self.detected_label.grid(row=1, column=0, sticky="w", pady=(10, 0))

        controls = ttk.Frame(layout, style="Card.TFrame", padding=16)
        controls.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        controls.columnconfigure(0, weight=1)

        self.load_audio_button = ttk.Button(controls, style="Primary.TButton", command=self.load_sstv_audio)
        self.load_audio_button.grid(row=0, column=0, sticky="ew")
        self._bind_text(self.load_audio_button, "load_audio")

        self.save_image_button = ttk.Button(controls, style="Secondary.TButton", command=self.save_decoded_image)
        self.save_image_button.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        self._bind_text(self.save_image_button, "save_image")

        self.clear_image_button = ttk.Button(controls, style="Ghost.TButton", command=self.remove_decoded_image)
        self.clear_image_button.grid(row=2, column=0, sticky="w", pady=(12, 0))
        self._bind_text(self.clear_image_button, "clear_image")

        self.back_button = ttk.Button(controls, style="Link.TButton", command=self.show_main_view)
        self.back_button.grid(row=3, column=0, sticky="w", pady=(18, 0))
        self._bind_text(self.back_button, "back")

        self.wait_label = ttk.Label(controls, style="Status.TLabel", textvariable=self.wait_var)
        self.wait_label.grid(row=4, column=0, sticky="w", pady=(12, 0))

        self._dynamic_updaters.append(self._set_detected_mode_label)
        self.body.rowconfigure(1, weight=1)
        self._stagger_show([preview_card, controls])

    def _refresh_upload_prompt(self):
        if self.selected_image is None and hasattr(self, "image_canvas"):
            self._show_upload_prompt()

    def _set_detected_mode_label(self):
        if not hasattr(self, "detected_mode_var"):
            return
        if self.wait_var.get():
            return
        if self._detected_mode_unknown:
            text = self.tr("detected_mode_unknown")
        elif self._detected_mode_name:
            text = (
                f"Detected Mode: {self._detected_mode_name}"
                if self.language == "English"
                else f"Mod Detectat: {self._detected_mode_name}"
            )
        else:
            text = self.tr("detected_mode_none")
        self.detected_mode_var.set(text)

    def _show_upload_prompt(self):
        self.image_canvas.delete("all")
        canvas_width, canvas_height = self._get_canvas_size(self.image_canvas, 360, 270)
        upload_icon_path = resource_path("icon2.png")
        if os.path.exists(upload_icon_path):
            try:
                icon_image = Image.open(upload_icon_path)
                icon_image = icon_image.resize((64, 64), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self._image_preview = icon_photo
                self.image_canvas.create_image(
                    canvas_width // 2,
                    canvas_height // 2 - 24,
                    anchor="center",
                    image=icon_photo,
                )
            except Exception as exc:
                print(f"Error loading icon: {exc}")
        self.image_canvas.create_text(
            canvas_width // 2,
            canvas_height // 2 + 40,
            text=self.tr("upload_hint"),
            anchor="center",
            font=self.fonts["body"],
            fill=self.colors["muted"],
        )

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[(self.tr("image_files"), "*.jpg;*.png;*.bmp")])
        if not file_path:
            return

        try:
            image = Image.open(file_path).convert("RGB")
            self.selected_image = image

            preview_image = ImageOps.contain(image, (360, 270), method=Image.LANCZOS)
            img_preview = ImageTk.PhotoImage(preview_image)

            canvas_width, canvas_height = self._get_canvas_size(self.image_canvas, 360, 270)
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                anchor="center",
                image=img_preview,
            )
            self.image_canvas.image = img_preview
            self._image_preview = img_preview

            self.status_var.set(self.tr("status_loaded"))
        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror(self.tr("error"), self.tr("image_load_error").format(exc))

    def remove_image(self):
        self.selected_image = None
        self.status_var.set("")
        self._show_upload_prompt()

    def convert_image_for_sstv(self, mode):
        if not self.selected_image:
            raise ValueError(self.tr("please_select_image"))

        if mode in {"Robot 36", "Robot36", "Robot 72", "Robot72"}:
            width, height = 320, 240
        elif mode in {"Martin M1", "Martin M2", "Scottie S1", "Scottie S2", "Scottie DX"}:
            width, height = 320, 256
        else:
            raise ValueError(self.tr("unsupported_mode").format(mode))

        return self.selected_image.resize((width, height), Image.LANCZOS)

    def generate_sstv_signal(self):
        if not self.selected_image:
            raise ValueError(self.tr("please_select_image"))

        mode = self.mode_var.get()
        converted_image = self.convert_image_for_sstv(mode)

        if mode in {"Robot 36", "Robot36"}:
            sstv = Robot36(converted_image, samples_per_sec=44100, bits=16)
        elif mode in {"Robot 72", "Robot72"}:
            if Robot72 is None:
                raise ValueError(self.tr("unsupported_mode").format(mode))
            sstv = Robot72(converted_image, samples_per_sec=44100, bits=16)
        elif mode == "Martin M1":
            sstv = MartinM1(converted_image, samples_per_sec=44100, bits=16)
        elif mode == "Martin M2":
            sstv = MartinM2(converted_image, samples_per_sec=44100, bits=16)
        elif mode == "Scottie S1":
            sstv = ScottieS1(converted_image, samples_per_sec=44100, bits=16)
        elif mode == "Scottie S2":
            sstv = ScottieS2(converted_image, samples_per_sec=44100, bits=16)
        elif mode == "Scottie DX":
            sstv = ScottieDX(converted_image, samples_per_sec=44100, bits=16)
        else:
            raise ValueError(self.tr("unsupported_mode").format(mode))

        samples = np.fromiter(sstv.gen_samples(), dtype=np.int16)
        self.sstv_signal = samples
        return samples
    def generate_and_play_sstv(self):
        try:
            audio_signal = self.generate_sstv_signal()
            audio_signal_float = audio_signal.astype(np.float32)
            max_val = np.max(np.abs(audio_signal_float))
            if max_val != 0:
                audio_signal_float /= max_val

            sd.play(audio_signal_float, samplerate=44100)
            self.is_playing = True
            self._refresh_play_button()
            self.status_var.set(self.tr("status_playing"))

            threading.Thread(target=self._playback_finished, daemon=True).start()

        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror(self.tr("error"), self.tr("failed_generate_play").format(exc))

    def _playback_finished(self):
        sd.wait()
        self.is_playing = False
        self.after(0, self._refresh_play_button)
        self.after(0, self._refresh_status_label)

    def stop_playback(self):
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            self._refresh_play_button()
            self._refresh_status_label()
        else:
            messagebox.showinfo(self.tr("info"), self.tr("no_playback"))

    def _refresh_play_button(self):
        if not hasattr(self, "play_button"):
            return
        if self.is_playing:
            self.play_button.configure(text=self.tr("stop_playback"), command=self.stop_playback)
        else:
            self.play_button.configure(text=self.tr("play_signal"), command=self.generate_and_play_sstv)

    def _refresh_status_label(self):
        if not hasattr(self, "status_label"):
            return
        if self.is_playing:
            self.status_var.set(self.tr("status_playing"))
        elif self.selected_image:
            self.status_var.set(self.tr("status_loaded"))
        else:
            self.status_var.set(self.tr("status_ready"))

    def download_sstv(self):
        try:
            audio_signal = self.generate_sstv_signal()

            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[(self.tr("wav_files"), "*.wav")],
                title=self.tr("save_wav"),
            )
            if not file_path:
                return

            with wave.open(file_path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframes(audio_signal.tobytes())

            self.status_var.set(self.tr("status_saved"))
            messagebox.showinfo(self.tr("success"), self.tr("signal_saved").format(file_path))
        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror(self.tr("error"), self.tr("failed_generate_save").format(exc))

    def load_sstv_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[(self.tr("wav_files"), "*.wav")])
        if not file_path:
            return

        self.decoded_canvas.delete("all")
        self._detected_mode_name = None
        self._detected_mode_unknown = False
        self._is_decoding = True
        self.detected_mode_var.set(self.tr("status_decoding"))
        self.wait_var.set(self.tr("status_decoding"))

        def decode_thread():
            try:
                with SSTVDecoder(file_path, language=self.language) as decoder:
                    log_message(
                        "Starting SSTV decoding..." if self.language == "English" else "Încep decodarea SSTV..."
                    )
                    decoder.progress_callback = self._update_progress
                    decoded_image = decoder.decode()

                    if decoded_image:
                        if decoder.mode:
                            self.after(0, lambda: self._apply_detected_mode(decoder.mode.NAME))
                        else:
                            self.after(0, lambda: self._apply_detected_mode(None, unknown=True))
                        self.display_decoded_image(decoded_image)
                        self.after(0, lambda: self._set_wait_status(self.tr("status_decoded")))
                    else:
                        self.after(0, lambda: self._apply_detected_mode(None, unknown=True))
                        self.after(
                            0,
                            lambda: messagebox.showerror(
                                self.tr("error"),
                                self.tr("failed_decode_sstv").format(self.tr("no_sstv_signal")),
                            ),
                        )
            except Exception as exc:
                log_message(
                    f"Error occurred: {exc}" if self.language == "English" else f"Eroare apărută: {exc}"
                )
                traceback.print_exc()
                self.after(
                    0,
                    lambda: messagebox.showerror(self.tr("error"), self.tr("failed_decode_sstv").format(exc)),
                )
            finally:
                self._is_decoding = False
                self.after(0, self._clear_wait_status_if_busy)

        threading.Thread(target=decode_thread, daemon=True).start()

    def _apply_detected_mode(self, mode_name, unknown=False):
        self._detected_mode_name = mode_name
        self._detected_mode_unknown = unknown
        self._set_detected_mode_label()

    def _set_wait_status(self, message):
        self.wait_var.set(message)
        self.after(1500, self._clear_wait_status)

    def _clear_wait_status(self):
        self.wait_var.set("")

    def _clear_wait_status_if_busy(self):
        if self.wait_var.get() == self.tr("status_decoding"):
            self.wait_var.set("")

    def _update_progress(self, _progress, _complete, message=""):
        if message:
            self.after(0, lambda: self.detected_mode_var.set(message))

    def display_decoded_image(self, image):
        self.decoded_image_reference = image

        canvas_width, canvas_height = self._get_canvas_size(self.decoded_canvas, 360, 270)

        preview_image = ImageOps.contain(image, (canvas_width, canvas_height), method=Image.LANCZOS)
        img_preview = ImageTk.PhotoImage(preview_image)

        def gui_update():
            self.decoded_canvas.delete("all")
            self.decoded_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                anchor="center",
                image=img_preview,
            )
            self.decoded_canvas.image = img_preview
            self._decoded_preview = img_preview

        self.after(0, gui_update)

    def save_decoded_image(self):
        if self.decoded_image_reference is None:
            messagebox.showerror(self.tr("error"), self.tr("no_decoded_image"))
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("BMP files", "*.bmp")],
            title=self.tr("save_image"),
        )
        if not file_path:
            return

        try:
            self.decoded_image_reference.save(file_path)
            messagebox.showinfo(self.tr("success"), self.tr("decoded_image_saved").format(file_path))
        except Exception as exc:
            traceback.print_exc()
            messagebox.showerror(self.tr("error"), self.tr("failed_save_image").format(exc))

    def remove_decoded_image(self):
        if hasattr(self, "decoded_canvas"):
            self.decoded_canvas.delete("all")
        self._apply_detected_mode(None, unknown=False)
        self.decoded_image_reference = None

    @staticmethod
    def _get_canvas_size(canvas, min_width, min_height):
        canvas.update_idletasks()
        return max(canvas.winfo_width(), min_width), max(canvas.winfo_height(), min_height)


if __name__ == "__main__":
    app = SSTVApp()
    app.mainloop()
