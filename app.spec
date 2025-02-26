# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['c:\\Users\\fabi\\Desktop\\sstv_project'],  # Înlocuiește cu calea corectă
    binaries=[],
    datas=[
        ('icon2.png', '.'), 
        ('icon3.png', '.'), 
        ('icon.ico', '.')  # Asigură-te că icon.ico este inclus
    ],
    hiddenimports=['decode', 'command', 'common'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Elimină consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Corectat: trece un șir de caractere, nu o listă
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app'
)
