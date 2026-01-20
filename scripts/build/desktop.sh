#!/bin/bash
set -e

echo "💻 Building desktop (Electron app)"
cd desktop

echo "🧹 Cleaning npm cache"
npm cache clean --force

npm install
npm run build