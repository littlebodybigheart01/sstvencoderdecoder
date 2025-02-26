# app.py

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps
from pysstv.color import Robot36, MartinM1, MartinM2, ScottieS1, ScottieS2, ScottieDX
import numpy as np
import sounddevice as sd
import threading
import traceback
import wave
from decode import SSTVDecoder  # Asigură-te că decode.py este în același director
from common import log_message  # Asigură-te că common.py este în același director

# Global variables
selected_image = None
sstv_signal = None  # Store the generated SSTV signal globally
mode_var = None  # Tkinter StringVar for selected mode
is_playing = False  # Flag to indicate if playback is ongoing
play_button = None  # Reference to the play/stop button
message_label = None  # Label to display messages
status_label = None  # Label to display status messages
image_canvas = None  # Reference to the image canvas
decoded_image_canvas = None  # Canvas for decoded image
detected_mode_label = None  # Label for detected mode
icon_photo = None  # Reference to the upload icon image
remove_icon_photo = None  # Reference to the remove icon image
language = 'English'  # Default language
lang_var = None  # Tkinter StringVar for language selection
decoded_image_reference = None  # Reference to the decoded image
current_mode = 'main'  # 'main', 'encode', 'decode'

# Widgets to update on language change
widgets_to_update = {}

# Texts for English and Romanian
texts = {
    'English': {
        'title': "SSTV Encoder and Decoder",
        'choose_action': "Choose an action:",
        'encode_sstv': "Encode SSTV",
        'decode_sstv': "Decode SSTV",
        'exit': "Exit",
        'sstv_encoder': "SSTV Encoder",
        'sstv_decoder': "SSTV Decoder",
        'image_success': "Image Successfully Uploaded!",
        'press_upload': "Press here to upload an image!",
        'select_mode': "Select SSTV Mode:",
        'select_sstv_mode': "Select SSTV Mode:",
        'generate_play': "Generate and Play SSTV",
        'stop': "Stop",
        'playing': "Playing...",
        'download_signal': "Download SSTV Signal",
        'load_sstv_audio': "Load SSTV Audio File",
        'back': "Back",
        'version_info': "SSTV Encoder and Decoder\nVersion: 1.0.0",
        'version': "Version",
        'file': "File",
        'help': "Help",
        'language_menu': "Language",
        'english_label': "English",
        'romanian_label': "Română",
        'no_playback': "No playback to stop.",
        'info': "Info",
        'save_signal': "Save SSTV Signal",
        'wav_files': "WAV files",
        'signal_saved': "SSTV signal saved as '{}'",
        'success': "Success",
        'error': "Error",
        'failed_generate_play': "Failed to generate and play SSTV signal: {}",
        'failed_generate_save': "Failed to generate and save SSTV signal: {}",
        'failed_decode_sstv': "Failed to decode SSTV signal: {}",
        'image_files': "Image files",
        'image_load_error': "Failed to load image: {}",
        'please_select_image': "Please select an image first!",
        'unsupported_mode': "Unsupported mode: {}",
        'please_wait': "Please wait...",
        'decode_success': "✅ Decoding completed successfully!",
        'detected_mode_none': "Detected Mode: None",
        'detected_mode_unknown': "Detected Mode: Unknown",
        'save_decoded_image': "Save Decoded Image",
        'decoded_image_saved': "Decoded image saved as '{}'",
        'failed_save_image': "Failed to save decoded image: {}",
        'no_decoded_image': "No decoded image to save.",
    },
    'Romanian': {
        'title': "SSTV Encoder and Decoder",
        'choose_action': "Alege o acțiune:",
        'encode_sstv': "Codifică SSTV",
        'decode_sstv': "Decodifică SSTV",
        'exit': "Ieșire",
        'sstv_encoder': "Codificator SSTV",
        'sstv_decoder': "Decodificator SSTV",
        'image_success': "Imagine încărcată cu succes!",
        'press_upload': "Apasă aici pentru a încărca o imagine!",
        'select_mode': "Selectează modul SSTV:",
        'select_sstv_mode': "Selectează modul SSTV:",
        'generate_play': "Generează și Redă SSTV",
        'stop': "Oprește",
        'playing': "Redare...",
        'download_signal': "Descarcă Semnal SSTV",
        'load_sstv_audio': "Încarcă Fișier Audio SSTV",
        'back': "Înapoi",
        'version_info': "SSTV Encoder and Decoder\nVersiune: 1.0.0",
        'version': "Versiune",
        'file': "Fișier",
        'help': "Ajutor",
        'language_menu': "Limba",
        'english_label': "English",
        'romanian_label': "Română",
        'no_playback': "Nu există redare de oprit.",
        'info': "Informație",
        'save_signal': "Salvează Semnalul SSTV",
        'wav_files': "Fișiere WAV",
        'signal_saved': "Semnalul SSTV a fost salvat ca '{}'",
        'success': "Succes",
        'error': "Eroare",
        'failed_generate_play': "Eroare la generarea și redarea semnalului SSTV: {}",
        'failed_generate_save': "Eroare la generarea și salvarea semnalului SSTV: {}",
        'failed_decode_sstv': "Eroare la decodificarea semnalului SSTV: {}",
        'image_files': "Fișiere imagine",
        'image_load_error': "Eroare la încărcarea imaginii: {}",
        'please_select_image': "Vă rugăm să selectați mai întâi o imagine!",
        'unsupported_mode': "Mod nesuportat: {}",
        'please_wait': "Vă rugăm să așteptați...",
        'decode_success': "✅ Decodare completă cu succes!",
        'detected_mode_none': "Mod Detectat: Nedefinit",
        'detected_mode_unknown': "Mod Detectat: Necunoscut",
        'save_decoded_image': "Salvează Imaginea Decodată",
        'decoded_image_saved': "Imaginea decodată a fost salvată ca '{}'",
        'failed_save_image': "Eroare la salvarea imaginii decodate: {}",
        'no_decoded_image': "Nicio imagine decodată de salvat.",
    }
}

# Determine the resampling method based on Pillow version
try:
    resample_method = Image.LANCZOS
except AttributeError:
    resample_method = Image.ANTIALIAS  # For older versions of Pillow

def resource_path(relative_path):
    """
    Obține calea absolută către resurse, indiferent dacă aplicația este executabilă sau rulată din sursă.
    """
    try:
        # PyInstaller creează un director temporar și setează variabila _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def set_language(lang):
    """Set the language of the application."""
    global language, lang_var
    language = lang
    lang_var.set(lang)
    create_menu_bar()
    update_texts_in_current_window()

def create_menu_bar():
    """Create the menu bar based on the current language."""
    global menu_bar, file_menu, help_menu, language_menu, lang_var
    # Remove the existing menu bar
    window.config(menu='')
    # Create new menu bar
    menu_bar = tk.Menu(window)
    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label=texts[language]['exit'], command=window.quit)
    menu_bar.add_cascade(label=texts[language]['file'], menu=file_menu)
    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label=texts[language]['version'], command=show_version)
    menu_bar.add_cascade(label=texts[language]['help'], menu=help_menu)
    # Language menu
    language_menu = tk.Menu(menu_bar, tearoff=0)
    language_menu.add_radiobutton(label=texts[language]['english_label'], variable=lang_var, value='English', command=lambda: set_language('English'))
    language_menu.add_radiobutton(label=texts[language]['romanian_label'], variable=lang_var, value='Romanian', command=lambda: set_language('Romanian'))
    menu_bar.add_cascade(label=texts[language]['language_menu'], menu=language_menu)
    window.config(menu=menu_bar)
    # Update window title
    window.title(texts[language]['title'])

def update_texts_in_current_window():
    """Update the texts in the current window."""
    global widgets_to_update, selected_image, image_canvas, decoded_image_canvas, current_mode
    for widget_name, widget in widgets_to_update.items():
        if widget_name == 'main_label':
            widget.config(text=texts[language]['choose_action'])
        elif widget_name == 'encode_button':
            widget.config(text=texts[language]['encode_sstv'])
        elif widget_name == 'decode_button':
            widget.config(text=texts[language]['decode_sstv'])
        elif widget_name == 'exit_button':
            widget.config(text=texts[language]['exit'])
        elif widget_name == 'sstv_label':
            if current_mode == 'encode':
                widget.config(text=texts[language]['sstv_encoder'])
            elif current_mode == 'decode':
                widget.config(text=texts[language]['sstv_decoder'])
        elif widget_name == 'sstv_decoder_label':
            widget.config(text=texts[language]['sstv_decoder'])
        elif widget_name == 'status_label':
            # Update based on whether an image is loaded
            if selected_image:
                widget.config(text=texts[language]['image_success'], fg="green")
            else:
                widget.config(text='')
        elif widget_name == 'mode_label':
            widget.config(text=texts[language]['select_mode'])
        elif widget_name == 'sstv_mode_label':
            widget.config(text=texts[language]['select_sstv_mode'])
        elif widget_name == 'play_button':
            if is_playing:
                widget.config(text=texts[language]['stop'])
            else:
                widget.config(text=texts[language]['generate_play'])
        elif widget_name == 'download_button':
            widget.config(text=texts[language]['download_signal'])
        elif widget_name == 'load_button':
            widget.config(text=texts[language]['load_sstv_audio'])
        elif widget_name == 'back_button':
            widget.config(text=texts[language]['back'])
        elif widget_name == 'message_label':
            if is_playing:
                widget.config(text=texts[language]['playing'])
            else:
                widget.config(text='')
        elif widget_name == 'image_canvas':
            # Update the upload prompt text only if no image is loaded
            if not selected_image:
                image_canvas.delete('prompt_text')
                image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')
        elif widget_name == 'decoded_image_canvas':
            # Reset decoded image canvas
            if not decoded_image_canvas.find_all():
                pass  # No action needed
        elif widget_name == 'detected_mode_label':
            # Reset detected mode label
            current_text = detected_mode_label.cget("text")
            if not current_text.startswith("✅") and not (language == 'Romanian' and current_text.startswith("Mod Detectat")):
                widget.config(text=texts[language]['detected_mode_none'] if language == 'English' else texts[language]['detected_mode_none'])
        elif widget_name == 'delete_decoded_button':
            # Update delete button tooltip or text if necessary
            pass
        elif widget_name == 'save_decoded_button':
            widget.config(text=texts[language]['save_decoded_image'])
        # Removed 'terminal_output' as per previous modifications

    # Actualizează label-ul bifei verzi dacă limba se schimbă
    if hasattr(window, 'checkmark_label'):
        window.checkmark_label.config(text="✅" if language == 'English' else "✅")

def load_image(canvas):
    """Load, scale, and display the selected image."""
    global selected_image, status_label, language
    file_path = filedialog.askopenfilename(filetypes=[(texts[language]['image_files'], "*.jpg;*.png;*.bmp")])
    if file_path:
        try:
            # Open the image and convert to RGB
            image = Image.open(file_path).convert("RGB")
            # Save the original image globally
            selected_image = image

            # Create a preview image scaled to fit the canvas (for display purposes)
            preview_image = ImageOps.contain(image, (320, 240), method=resample_method)

            img_preview = ImageTk.PhotoImage(preview_image)

            # Clear the canvas and display the image
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=img_preview)
            canvas.image = img_preview  # Keep a reference to prevent garbage collection

            # Update the status label
            status_label.config(text=texts[language]['image_success'], fg="green")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(texts[language]['error'], texts[language]['image_load_error'].format(e))

def remove_image():
    """Remove the loaded image and reset the canvas."""
    global selected_image, status_label, image_canvas, icon_photo, language
    selected_image = None
    status_label.config(text="")
    image_canvas.delete("all")

    # Remove existing checkmark if present
    if hasattr(window, 'checkmark_label'):
        window.checkmark_label.destroy()
        del window.checkmark_label

    # Display the upload prompt and icon again
    upload_icon_path = resource_path('icon2.png')  # Use resource_path
    if os.path.exists(upload_icon_path):
        try:
            icon_image = Image.open(upload_icon_path)
            icon_image = icon_image.resize((64, 64), resample_method)
            icon_photo = ImageTk.PhotoImage(icon_image)
            image_canvas.create_image(128, 50, anchor="nw", image=icon_photo)
            image_canvas.icon_photo = icon_photo  # Keep a reference
            image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')
        except Exception as e:
            print(f"Error loading icon: {e}")
            image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')
    else:
        print(f"Upload icon file '{upload_icon_path}' not found.")
        image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')

def convert_image_for_sstv(mode):
    """Convert the loaded image to ensure compatibility with SSTV."""
    global selected_image, language
    if not selected_image:
        raise ValueError(texts[language]['please_select_image'])

    # Determine the required image size based on the mode
    if mode == "Robot36":
        width, height = 320, 240
    elif mode in ["Martin M1", "Martin M2", "Scottie S1", "Scottie S2", "Scottie DX"]:
        width, height = 320, 256
    else:
        # Default size or raise an error
        raise ValueError(texts[language]['unsupported_mode'].format(mode))

    # Resize the image to the required size
    converted_image = selected_image.resize((width, height), resample_method)

    return converted_image

def generate_sstv_signal():
    """Generate the SSTV audio signal."""
    global selected_image, sstv_signal, mode_var, language
    if not selected_image:
        raise ValueError(texts[language]['please_select_image'])

    try:
        # Get the selected mode
        mode = mode_var.get()

        # Convert image to the required format
        converted_image = convert_image_for_sstv(mode)

        # Select the appropriate SSTV class based on the mode
        if mode == "Robot36":
            sstv = Robot36(converted_image, samples_per_sec=44100, bits=16)
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
            raise ValueError(texts[language]['unsupported_mode'].format(mode))

        # Collect samples into a list and then convert to a NumPy array
        samples = list(sstv.gen_samples())
        audio_signal = np.array(samples, dtype=np.int16)

        # Store the generated SSTV signal globally
        sstv_signal = audio_signal

        return audio_signal
    except Exception as e:
        traceback.print_exc()
        raise e

def reset_play_button():
    """Reset the play button and clear message label."""
    global play_button, message_label, language, is_playing
    is_playing = False
    play_button.config(text=texts[language]['generate_play'], command=generate_and_play_sstv)
    message_label.config(text="")

def playback_finished():
    """Callback function to reset is_playing flag after playback ends."""
    global is_playing
    sd.wait()
    is_playing = False
    # Schedule GUI updates on the main thread
    window.after(0, reset_play_button)

def generate_and_play_sstv():
    """Generate and play SSTV audio using the selected protocol."""
    global sstv_signal, is_playing, play_button, message_label, language
    try:
        # Generate the SSTV signal
        audio_signal = generate_sstv_signal()

        # Convert int16 samples to float32 for playback
        audio_signal_float = audio_signal.astype(np.float32)

        # Normalize the audio signal to -1.0 to 1.0
        max_val = np.max(np.abs(audio_signal_float))
        if max_val != 0:
            audio_signal_float /= max_val

        # Play the generated audio (non-blocking)
        sd.play(audio_signal_float, samplerate=44100)
        is_playing = True

        # Change the play button to 'Stop'
        play_button.config(text=texts[language]['stop'], command=stop_playback)

        # Display 'Playing...' message
        message_label.config(text=texts[language]['playing'])

        # Start a thread to monitor playback and reset the button after playback finishes
        threading.Thread(target=playback_finished, daemon=True).start()

    except Exception as e:
        traceback.print_exc()
        messagebox.showerror(texts[language]['error'], texts[language]['failed_generate_play'].format(e))

def stop_playback():
    """Stop the audio playback."""
    global is_playing, language
    if is_playing:
        sd.stop()
        is_playing = False
        # Schedule GUI updates on the main thread
        window.after(0, reset_play_button)
    else:
        messagebox.showinfo(texts[language]['info'], texts[language]['no_playback'])

def download_sstv():
    """Generate the SSTV signal and allow the user to download it."""
    global sstv_signal, language
    try:
        # Generate the SSTV signal
        audio_signal = generate_sstv_signal()

        # Open a file dialog to choose where to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".wav",
                                                 filetypes=[(texts[language]['wav_files'], "*.wav")],
                                                 title=texts[language]['save_signal'])
        if file_path:
            # Save the audio signal to a WAV file
            with wave.open(file_path, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 2 bytes for int16
                wav_file.setframerate(44100)
                wav_file.writeframes(audio_signal.tobytes())

            messagebox.showinfo(texts[language]['success'], texts[language]['signal_saved'].format(file_path))
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror(texts[language]['error'], texts[language]['failed_generate_save'].format(e))

def open_encode_window():
    """Open the encoding window."""
    global mode_var, play_button, message_label, status_label, image_canvas, icon_photo, remove_icon_photo, language, widgets_to_update, current_mode

    # Set current_mode
    current_mode = 'encode'

    # Clear widgets_to_update
    widgets_to_update.clear()

    for widget in window.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()

    # SSTV Encoder label
    sstv_label = tk.Label(window, text=texts[language]['sstv_encoder'], font=("Arial", 16))
    sstv_label.pack(pady=5)
    widgets_to_update['sstv_label'] = sstv_label

    # Frame to hold the image canvas and remove button
    image_frame = tk.Frame(window)
    image_frame.pack(pady=5, anchor="center")  # Center the image_frame

    # Image placeholder as a Canvas
    global image_canvas
    image_canvas = tk.Canvas(image_frame, width=320, height=240, bg="lightgray")
    image_canvas.pack(side="left", padx=10)
    image_canvas.bind("<Button-1>", lambda e: load_image(image_canvas))
    widgets_to_update['image_canvas'] = image_canvas

    # Remove Image button with icon, placed to the right of the image_canvas
    remove_icon_path = resource_path('icon3.png')  # Use resource_path
    if os.path.exists(remove_icon_path):
        try:
            remove_icon = Image.open(remove_icon_path)
            remove_icon = remove_icon.resize((32, 32), resample_method)
            remove_icon_photo = ImageTk.PhotoImage(remove_icon)
            remove_button = tk.Button(image_frame, command=remove_image, image=remove_icon_photo, width=40, height=40)
            remove_button.image = remove_icon_photo  # Keep a reference
        except Exception as e:
            print(f"Error loading remove icon: {e}")
            remove_button = tk.Button(image_frame, text="", command=remove_image, width=4, height=2)
    else:
        print(f"Remove icon file '{remove_icon_path}' not found.")
        remove_button = tk.Button(image_frame, text="", command=remove_image, width=4, height=2)
    remove_button.pack(side="left", padx=5)
    widgets_to_update['remove_button'] = remove_button

    # Display 'Press here to upload an image!' and icon
    if not selected_image:
        upload_icon_path = resource_path('icon2.png')  # Use resource_path
        if os.path.exists(upload_icon_path):
            try:
                icon_image = Image.open(upload_icon_path)
                icon_image = icon_image.resize((64, 64), resample_method)
                icon_photo = ImageTk.PhotoImage(icon_image)
                image_canvas.create_image(128, 50, anchor="nw", image=icon_photo)
                image_canvas.icon_photo = icon_photo  # Keep a reference
                image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')
            except Exception as e:
                print(f"Error loading icon: {e}")
                image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')
        else:
            print(f"Upload icon file '{upload_icon_path}' not found.")
            image_canvas.create_text(160, 130, text=texts[language]['press_upload'], anchor="center", font=("Arial", 12), tags='prompt_text')

    # Status label (above the image canvas)
    status_label = tk.Label(window, text="", fg="green", font=("Arial", 10))
    status_label.pack()
    widgets_to_update['status_label'] = status_label

    # Frame for buttons and options
    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    # Mode selection OptionMenu
    modes = ["Robot36", "Martin M1", "Martin M2", "Scottie S1", "Scottie S2", "Scottie DX"]  # "Robot72" eliminat
    mode_var = tk.StringVar(value="Robot36")  # Default mode

    mode_label = tk.Label(button_frame, text=texts[language]['select_mode'])
    mode_label.pack(pady=5)
    widgets_to_update['mode_label'] = mode_label

    mode_menu = tk.OptionMenu(button_frame, mode_var, *modes)
    mode_menu.pack(pady=5)

    # Generate and Play button
    play_button = tk.Button(button_frame, text=texts[language]['generate_play'], command=generate_and_play_sstv, width=25)
    play_button.pack(pady=5)
    widgets_to_update['play_button'] = play_button

    # Download button
    download_button = tk.Button(button_frame, text=texts[language]['download_signal'], command=download_sstv, width=25)
    download_button.pack(pady=5)
    widgets_to_update['download_button'] = download_button

    # Back button
    back_button = tk.Button(button_frame, text=texts[language]['back'], command=open_main_window, width=25)
    back_button.pack(pady=5)
    widgets_to_update['back_button'] = back_button

    # Message label (below buttons)
    message_label = tk.Label(window, text="", fg="blue", font=("Arial", 12))
    message_label.pack(pady=5)
    widgets_to_update['message_label'] = message_label

def open_decode_window():
    """Open the decoding window."""
    global language, widgets_to_update, decoded_image_canvas, current_mode
    global detected_mode_label

    # Set current_mode
    current_mode = 'decode'

    # Clear widgets_to_update
    widgets_to_update.clear()

    for widget in window.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()

    # SSTV Decoder label
    sstv_label = tk.Label(window, text=texts[language]['sstv_decoder'], font=("Arial", 16))
    sstv_label.pack(pady=5)
    widgets_to_update['sstv_label'] = sstv_label

    # Frame for buttons and options
    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    # Button to load and decode SSTV audio
    load_button = tk.Button(button_frame, text=texts[language]['load_sstv_audio'], command=load_sstv_audio, width=25)
    load_button.pack(pady=5)
    widgets_to_update['load_button'] = load_button

    # Canvas to display the decoded image
    decoded_image_canvas = tk.Canvas(window, width=320, height=240, bg="lightgray")
    decoded_image_canvas.pack(pady=10)
    widgets_to_update['decoded_image_canvas'] = decoded_image_canvas

    # Label for detected SSTV mode
    detected_mode_label = tk.Label(window, text=texts[language]['detected_mode_none'], font=("Arial", 10))
    detected_mode_label.pack(pady=5)
    widgets_to_update['detected_mode_label'] = detected_mode_label

    # Save Decoded Image button
    save_decoded_button = tk.Button(button_frame, text=texts[language]['save_decoded_image'], command=save_decoded_image, width=25)
    save_decoded_button.pack(pady=5)
    widgets_to_update['save_decoded_button'] = save_decoded_button

    # Delete Decoded Image button with icon
    delete_icon_path = resource_path('icon3.png')  # Use resource_path
    if os.path.exists(delete_icon_path):
        try:
            delete_icon = Image.open(delete_icon_path)
            delete_icon = delete_icon.resize((32, 32), resample_method)
            delete_icon_photo = ImageTk.PhotoImage(delete_icon)
            delete_decoded_button = tk.Button(window, command=remove_decoded_image, image=delete_icon_photo, width=40, height=40)
            delete_decoded_button.image = delete_icon_photo  # Keep a reference
        except Exception as e:
            print(f"Error loading delete icon: {e}")
            delete_decoded_button = tk.Button(window, text="", command=remove_decoded_image, width=4, height=2)
    else:
        print(f"Delete icon file '{delete_icon_path}' not found.")
        delete_decoded_button = tk.Button(window, text="", command=remove_decoded_image, width=4, height=2)
    delete_decoded_button.pack(pady=5)
    widgets_to_update['delete_decoded_button'] = delete_decoded_button

    # Back button
    back_button = tk.Button(button_frame, text=texts[language]['back'], command=open_main_window, width=25)
    back_button.pack(pady=5)
    widgets_to_update['back_button'] = back_button

    # "Please wait..." label (hidden initially)
    global wait_label
    wait_label = tk.Label(window, text=texts[language]['please_wait'], fg="blue", font=("Arial", 12))
    wait_label.pack(pady=5)
    wait_label.pack_forget()  # Hide initially
    widgets_to_update['wait_label'] = wait_label

def update_progress(progress, complete, message=""):
    """
    Update the progress based on the decoding progress.
    """
    # Since the progress bar was removed, we can update only the message if necessary
    def gui_update():
        # Update the detected mode label if a message is provided
        if message:
            detected_mode_label.config(text=message)

    # Schedule the GUI update on the main thread
    window.after(0, gui_update)

def load_sstv_audio():
    """Load an SSTV audio file and decode it automatically using SSTVDecoder."""
    global language, decoded_image_canvas, detected_mode_label, wait_label

    # Remove existing checkmark if present
    if hasattr(window, 'checkmark_label'):
        window.checkmark_label.destroy()
        del window.checkmark_label

    # Select the audio file
    file_path = filedialog.askopenfilename(filetypes=[(texts[language]['wav_files'], "*.wav")])
    if file_path:
        # Reset UI elements
        decoded_image_canvas.delete("all")
        detected_mode_label.config(text=texts[language]['please_wait'] if language == 'English' else "Vă rugăm să așteptați...")
        wait_label.config(text=texts[language]['please_wait'] if language == 'English' else "Vă rugăm să așteptați...")
        wait_label.pack()  # Show the "Please wait..." label

        # Function for decoding in a separate thread
        def decode_thread():
            try:
                # Initialize the SSTV decoder with language
                with SSTVDecoder(file_path, language=language) as decoder:
                    log_message("Starting SSTV decoding..." if language == 'English' else "Încep decodarea SSTV...")

                    # Associate the progress callback
                    decoder.progress_callback = update_progress

                    # Decode the image
                    log_message("Decoding in progress..." if language == 'English' else "Decodificare în curs...")
                    decoded_image = decoder.decode()

                    if decoded_image:
                        log_message("Decoding completed successfully." if language == 'English' else "Decodare finalizată cu succes.")
                        # Update detected mode
                        if decoder.mode:
                            window.after(0, lambda: detected_mode_label.config(
                                text=f"Detected Mode: {decoder.mode.NAME}" if language == 'English' else f"Mod Detectat: {decoder.mode.NAME}"
                            ))
                        else:
                            window.after(0, lambda: detected_mode_label.config(
                                text=texts[language]['detected_mode_unknown']
                            ))
                        # Display the decoded image
                        display_decoded_image(decoded_image)
                        # Show green checkmark
                        show_checkmark()
                    else:
                        log_message("No SSTV signal found in the audio." if language == 'English' else "Niciun semnal SSTV găsit în audio.")
                        window.after(0, lambda: messagebox.showerror(
                            texts[language]['error'], 
                            texts[language]['failed_decode_sstv'].format("No SSTV signal found." if language == 'English' else "Niciun semnal SSTV găsit.")
                        ))
            except Exception as e:
                log_message(f"Error occurred: {e}" if language == 'English' else f"Eroare apărută: {e}")
                traceback.print_exc()
                window.after(0, lambda: messagebox.showerror(
                    texts[language]['error'], 
                    f"{texts[language]['failed_decode_sstv'].format(e)}"
                ))
            finally:
                # Hide the "Please wait..." label
                window.after(0, lambda: wait_label.pack_forget())

        # Start the decoding thread
        threading.Thread(target=decode_thread, daemon=True).start()

def display_decoded_image(image):
    """
    Display the decoded image on the canvas.
    """
    global decoded_image_canvas, decoded_image_reference

    # Determine the canvas size
    canvas_width = decoded_image_canvas.winfo_width()
    canvas_height = decoded_image_canvas.winfo_height()

    # Resize the image to fit the canvas
    preview_image = ImageOps.contain(image, (canvas_width, canvas_height), method=Image.LANCZOS)
    img_preview = ImageTk.PhotoImage(preview_image)

    # Store a reference to the image to prevent garbage collection
    decoded_image_reference = image  # Păstrează obiectul original pentru salvare

    # Function to update the GUI
    def gui_update():
        decoded_image_canvas.delete("all")
        decoded_image_canvas.create_image(0, 0, anchor="nw", image=img_preview)
        decoded_image_canvas.image = img_preview  # Keep a reference

    # Schedule the GUI update on the main thread
    window.after(0, gui_update)

def save_decoded_image():
    """Save the decoded image to a file."""
    global decoded_image_canvas, language, decoded_image_reference

    # Verifică dacă există o imagine decodată
    if decoded_image_reference is None:
        messagebox.showerror(texts[language]['error'], texts[language]['no_decoded_image'])
        return

    # Deschide un dialog de salvare
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("BMP files", "*.bmp")],
                                             title=texts[language]['save_decoded_image'])
    if file_path:
        try:
            # Salvează imaginea
            decoded_image_reference.save(file_path)
            messagebox.showinfo(texts[language]['success'], texts[language]['decoded_image_saved'].format(file_path))
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(texts[language]['error'], texts[language]['failed_save_image'].format(e))

def remove_decoded_image():
    """Remove the decoded image and reset the canvas."""
    global decoded_image_canvas, detected_mode_label, language

    decoded_image_canvas.delete("all")
    detected_mode_label.config(text=texts[language]['detected_mode_none'] if language == 'English' else texts[language]['detected_mode_none'])

    # Remove existing checkmark if present
    if hasattr(window, 'checkmark_label'):
        window.checkmark_label.destroy()
        del window.checkmark_label

def show_checkmark():
    """Schedule the display of a green checkmark in the main thread."""
    def update_label():
        global checkmark_label
        if not hasattr(window, 'checkmark_label'):
            checkmark_label = tk.Label(window, text="✅", font=("Arial", 24), fg="green")
            checkmark_label.pack(pady=5)
            window.checkmark_label = checkmark_label
        else:
            window.checkmark_label.config(text="✅")

    window.after(0, update_label)

def open_main_window():
    """Open the main window."""
    global language, widgets_to_update, current_mode
    # Set current_mode
    current_mode = 'main'
    # Clear widgets_to_update
    widgets_to_update.clear()

    for widget in window.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()
    main_label = tk.Label(window, text=texts[language]['choose_action'], font=("Arial", 16))
    main_label.pack(pady=20)
    widgets_to_update['main_label'] = main_label

    encode_button = tk.Button(window, text=texts[language]['encode_sstv'], command=open_encode_window, width=20)
    encode_button.pack(pady=10)
    widgets_to_update['encode_button'] = encode_button

    # Add Decode SSTV button
    decode_button = tk.Button(window, text=texts[language]['decode_sstv'], command=open_decode_window, width=20)
    decode_button.pack(pady=10)
    widgets_to_update['decode_button'] = decode_button

    # Exit button
    exit_button = tk.Button(window, text=texts[language]['exit'], command=window.quit, width=20)
    exit_button.pack(pady=10)
    widgets_to_update['exit_button'] = exit_button

def show_version():
    """Show version information."""
    messagebox.showinfo(texts[language]['version'], texts[language]['version_info'])

# Main window setup
window = tk.Tk()
window.title(texts[language]['title'])
window.geometry("400x600")  # Adjusted size for better layout
window.resizable(False, False)

# Initialize the language variable
lang_var = tk.StringVar(value=language)

# Set the window icon
icon_path = resource_path('icon.ico')  # Use resource_path
if os.path.exists(icon_path):
    try:
        window.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error setting icon: {e}")
else:
    print(f"Icon file '{icon_path}' not found. Window will use the default icon.")

# Create the menu bar
create_menu_bar()

# Open the main window
open_main_window()
window.mainloop()
