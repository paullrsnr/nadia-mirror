# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

project_root = os.getcwd()

# Collect everything from api package
api_datas, api_binaries, api_hiddenimports = collect_all("api")

a = Analysis(
    ["api/__main__.py"],
    pathex=[project_root],  # 👈 rend "api" importable
    binaries=api_binaries,
    datas=api_datas,
    hiddenimports=api_hiddenimports + [
        "uvicorn",
        "fastapi",
        "api",
        "api.main"
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="nadia-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)