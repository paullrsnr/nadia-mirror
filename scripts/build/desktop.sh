#!/bin/bash
set -e

echo "💻 Building desktop (Electron app)"

cd desktop
npm install
npm run build