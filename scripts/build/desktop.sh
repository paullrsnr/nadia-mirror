#!/bin/bash
set -e

echo "🧹 Cleaning npm cache"
npm cache clean --force

echo "💻 Building desktop (Electron app)"
cd desktop
npm install
npm run build