import os
import esptool

# Get the path where the esptool package is installed
esptool_path = os.path.dirname(esptool.__file__)

# Define the full path to the 'targets' directory that esptool uses
esptool_targets_path = os.path.join(esptool_path, 'targets')


a = Analysis(
    ['../flasher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (esptool_targets_path, 'esptool/targets')
    ],
    # Ensure PySide6 modules and esptool are included
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'esptool'],
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
