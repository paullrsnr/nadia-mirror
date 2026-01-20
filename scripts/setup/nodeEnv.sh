#!/bin/bash
set -e

echo "🔧 Setting up Node.js environment"

export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
node --version
npm --version