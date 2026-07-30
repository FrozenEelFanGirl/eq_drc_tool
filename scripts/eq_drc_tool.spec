# -*- mode: python ; coding: utf-8 -*-
import os

_project_root = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(SPECPATH, 'run.py')],
    pathex=[_project_root],
    binaries=[],
    datas=[
        (os.path.join(_project_root, 'doc', 'ref', 'guildlines'), 'doc/ref/guildlines'),
        (os.path.join(_project_root, 'doc', 'ref', 'copyright'), 'doc/ref/copyright'),
    ],
    hiddenimports=['PySide6', 'pyqtgraph', 'numpy'],
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
    a.binaries,
    a.datas,
    [],
    name='eq_drc_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
