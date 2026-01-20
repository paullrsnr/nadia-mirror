#!/bin/bash
set -e

echo "🐍 Building backend for macOS"

cd backend
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller nadia-backend.spec
mkdir -p dist/mac
mv dist/nadia-backend dist/mac/nadia-backend