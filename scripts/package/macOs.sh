#!/bin/bash
set -e
echo "📦 Packaging macOS installer"

cd desktop
npm install
mkdir -p ../backend/dist/win # create empty win folder to avoid errors
npm run pack:mac