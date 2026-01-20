#!/bin/bash
set -e

echo "🔧 Setting up environment for packaging macOS app"

export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
node --version
npm --version

export APPLE_API_KEY_ID="385MGD36L7"
export APPLE_API_ISSUER="22737eef-efcb-4e85-bb6c-c958f5c44d75"
export APPLE_API_KEY_PATH="$HOME/.apple/385MGD36L7.p8"
export APPLE_API_KEY="$HOME/.apple/385MGD36L7.p8"