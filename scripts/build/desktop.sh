#!/usr/bin/env sh
set -e

echo "💻 Building desktop (Electron app)"

cd desktop

echo "🧹 Cleaning workspace"
rm -rf node_modules
npm cache clean --force

npm ci

npm run build

# requis par electron-builder
mkdir -p ../backend/dist/mac

npm run pack:win