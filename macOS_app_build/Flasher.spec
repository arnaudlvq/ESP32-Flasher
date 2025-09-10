# -*- mode: python ; coding: utf-8 -*-

from shutil import which

# Find the esptool executable to bundle it
esptool_path = which('esptool')
if not esptool_path:
    raise Exception("esptool not found in PATH. Please install it.")

a = Analysis(
    ['../flasher.py'],
    pathex=[],
    # Bundle the esptool executable
    binaries=[(esptool_path, '.')],
    # Bundle assets like the icon, but not the 'bin' folder
    datas=[('assets', 'assets')],
    # Ensure PySide6 modules are included
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Flasher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Flasher',
)
app = BUNDLE(
    coll,
    name='Flasher.app',
    icon='assets/icon.icns',
    bundle_identifier=None,
)