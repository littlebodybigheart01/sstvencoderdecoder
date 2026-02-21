# SSTV Studio

## English

SSTV Studio is a small desktop app for encoding images into SSTV audio and decoding SSTV audio back into images. It includes a modern GUI, supports English and Romanian, and focuses on a clean, practical workflow.

### Features
- Encode images to SSTV audio and save as WAV.
- Decode SSTV audio files into images.
- Automatic mode detection during decode.
- Simple, modern interface with clear status feedback.

### Supported SSTV Modes
**Decode** (auto-detected):
- Robot 36
- Robot 72
- Martin M1
- Martin M2
- Scottie S1
- Scottie S2
- Scottie DX

**Encode**:
- Robot 36
- Martin M1
- Martin M2
- Scottie S1
- Scottie S2
- Scottie DX

Robot 72 encoding is available only if your installed `pysstv` version provides it.

### Requirements
- Python 3.8+
- Packages listed in `requirements.txt`

### Install
```bash
pip install -r requirements.txt
```

### Run
```bash
python app.py
```

### Build (EXE + Installer)
**One-file EXE (PyInstaller)**
```bash
python -m PyInstaller --noconsole --onefile --name SSTVStudio --icon icon.ico --add-data "icon.ico;." --add-data "icon2.png;." --add-data "icon3.png;." app.py
```
Output: `dist\SSTVStudio.exe`

**Installer (Inno Setup)**
1. Install Inno Setup 6.
2. Compile `SSTVStudio.iss` in Inno Setup Compiler.

Output: `dist\SSTVStudio-Setup.exe`

### Quick Use
**Encode**
1. Open Encoder.
2. Click the image area to load a picture.
3. Select the SSTV mode.
4. Generate and play, or save as WAV.

**Decode**
1. Open Decoder.
2. Load a WAV file with SSTV audio.
3. Save the decoded image when it appears.

### License
MIT

### Notes
If Robot 72 does not appear in the encoder list, update `pysstv` or use a build that includes Robot 72 encoding.

---

## Română

SSTV Studio este o aplicație desktop pentru codificarea imaginilor în audio SSTV și decodificarea fișierelor audio SSTV înapoi în imagini. Include o interfață modernă, suportă limbile română și engleză și pune accent pe un flux simplu și clar.

### Funcționalități
- Codificare imagine în audio SSTV și salvare ca WAV.
- Decodificare fișier audio SSTV în imagine.
- Detectare automată a modului la decodare.
- Interfață modernă și feedback clar în status.

### Moduri SSTV suportate
**Decodare** (detectate automat):
- Robot 36
- Robot 72
- Martin M1
- Martin M2
- Scottie S1
- Scottie S2
- Scottie DX

**Codificare**:
- Robot 36
- Martin M1
- Martin M2
- Scottie S1
- Scottie S2
- Scottie DX

Codificarea Robot 72 este disponibilă doar dacă versiunea instalată de `pysstv` o oferă.

### Cerințe
- Python 3.8+
- Pachetele din `requirements.txt`

### Instalare
```bash
pip install -r requirements.txt
```

### Rulare
```bash
python app.py
```

### Build (EXE + Installer)
**EXE one-file (PyInstaller)**
```bash
python -m PyInstaller --noconsole --onefile --name SSTVStudio --icon icon.ico --add-data "icon.ico;." --add-data "icon2.png;." --add-data "icon3.png;." app.py
```
Rezultat: `dist\SSTVStudio.exe`

**Installer (Inno Setup)**
1. Instalează Inno Setup 6.
2. Compilează `SSTVStudio.iss` în Inno Setup Compiler.

Rezultat: `dist\SSTVStudio-Setup.exe`

### Utilizare rapidă
**Codificare**
1. Deschide Codificatorul.
2. Apasă pe zona imaginii pentru încărcare.
3. Selectează modul SSTV.
4. Generează și redă, sau salvează ca WAV.

**Decodificare**
1. Deschide Decodificatorul.
2. Încarcă un fișier WAV cu semnal SSTV.
3. Salvează imaginea decodată când apare.

### Notă
Dacă Robot 72 nu apare în lista de codare, actualizează `pysstv` sau folosește o versiune care include codificarea Robot 72.
