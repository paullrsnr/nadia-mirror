#!/bin/bash
set -e
echo "📦 Packaging macOS installer"

# Node / npm
# shellcheck disable=SC1091
source "$(dirname "$0")/../setup/nodeEnv.sh"

# Apple notarization
# shellcheck disable=SC1091
source "$(dirname "$0")/../setup/prePackageMacOs.sh"

cd desktop
npm install
mkdir -p ../backend/dist/win # create empty win folder to avoid errors
npm run pack:mac