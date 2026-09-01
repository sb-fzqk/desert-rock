import sys
from PyInstaller.utils.hooks import collect_data_files

datas = [('theme.json', '.')]
datas += collect_data_files('customtkinter')

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['sounddevice', 'numpy', 'customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assembles=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DesertRock',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DesertRock',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='DesertRock.app',
        icon=None,
        bundle_identifier='com.desertrock.tuner',
        info_plist={
            'NSMicrophoneUsageDescription': 'Desert Rock requires microphone access to detect pitch.',
        },
    )