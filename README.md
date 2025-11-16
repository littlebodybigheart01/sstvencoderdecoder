[README.md](https://github.com/user-attachments/files/23570300/README.md)
# SSTV Encoder and Decoder


A user-friendly tool to explore the world of Slow-Scan Television (SSTV). This project provides a graphical application and a command-line interface to encode images into SSTV audio signals and decode them back into images.

Ever wanted to "hear" an image? With this tool, you can convert your favorite pictures into sound waves, and then reconstruct the image from the sound, simulating how images are transmitted over radio waves.

This project features both a GUI for easy operation and a CLI for scripting and automation, and it even supports both English and Romanian.

## Features

### Graphical User Interface (GUI)
The application provides a simple and intuitive interface for:
- **Encoding**:
    - Upload your images (JPEG, PNG, BMP).
    - Select from a variety of popular SSTV modes.
    - Generate and preview the SSTV audio signal in real-time.
    - Save the generated audio as a `.wav` file.
- **Decoding**:
    - Load a `.wav` audio file containing an SSTV signal.
    - The tool automatically detects the SSTV mode.
    - View the reconstructed image as it's being decoded.
    - Save the final image.

### Command-Line Interface (CLI)
For power users and automation, the CLI provides:
- **Decoding**:
    - Decode SSTV audio files directly from the terminal.
    - Specify output file paths.
    - Option to skip to a certain timestamp in the audio file.
- **Utilities**:
    - List all supported SSTV modes.
    - List supported audio and image formats.

## Supported SSTV Modes

The following SSTV modes are supported for both encoding and decoding:

- Robot 36
- Robot 72
- Martin M1
- Martin M2
- Scottie S1
- Scottie S2
- Scottie DX

## Installation

This project is written in Python 3. You'll need to have Python 3.8+ installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/littlebodybigheart01/sstvencoderdecoder
    cd sstv-encoder-decoder
    ```

2.  **Install the dependencies:**
    The project relies on a few external libraries. You can install them using pip:
    ```bash
    pip install numpy pillow pysstv sounddevice soundfile scipy
    ```

## Usage

You can either use the graphical interface or the command-line tool.

### GUI Application

To launch the GUI, run the `app.py` script:

```bash
python app.py
```

#### Encoding an Image:
1.  From the main window, click on **"Encode SSTV"**.
2.  Click on the image area to upload an image.
3.  Select your desired SSTV mode from the dropdown menu.
4.  Click **"Generate and Play SSTV"** to hear the signal, or **"Download SSTV Signal"** to save it as a `.wav` file.

#### Decoding an Audio File:
1.  From the main window, click on **"Decode SSTV"**.
2.  Click **"Load SSTV Audio File"** and select a `.wav` file.
3.  The application will automatically start decoding, and you will see the image appear on the screen.
4.  Once finished, you can save the decoded image.

You can try this out with the example files provided in the `test/` directory. For example, you can try decoding `test/sunet1.wav`.

### Command-Line (Decoder)

The `command.py` script allows you to decode SSTV audio files directly.

**Basic Usage:**

```bash
python command.py -d <path_to_audio_file> -o <output_image_name.png>
```

**Example:**
To decode the example sound file `sunet1.wav` from the `test` directory and save it as `decoded_image.png`:

```bash
python command.py -d test/sunet1.wav -o decoded_image.png
```

**CLI Options:**

| Flag                  | Description                                     |
| --------------------- | ----------------------------------------------- |
| `-d`, `--decode`      | Path to the SSTV audio file to decode.          |
| `-o`, `--output`      | Path to save the decoded image. (Default: `result.png`) |
| `-s`, `--skip`        | Time in seconds to skip before decoding.        |
| `--list-modes`        | List supported SSTV modes.                      |
| `--list-audio-formats`| List supported audio formats.                   |
| `--list-image-formats`| List supported image formats for saving.        |


## Implementation Details

- **GUI**: The GUI is built with Python's standard `tkinter` library.
- **Encoding**: Image encoding and SSTV signal generation are handled by the `pysstv` library.
- **Decoding**: The decoding logic is implemented in `decode.py`. It uses `numpy` and `scipy` to perform an FFT-based frequency analysis to reconstruct the image from the audio signal.
- **Audio I/O**: `sounddevice` is used for audio playback, and `soundfile` is used for reading audio files.
- **Image Processing**: The `Pillow` library is used for all image manipulation tasks.

## Installer

For a more convenient setup, an installer is available for the project.
This allows you to run the application without any external dependencies, including Python.
