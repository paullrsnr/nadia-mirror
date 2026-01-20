#!/bin/bash
set -e

echo "Apple notarization setup for macOS packaging"
export APPLE_API_KEY_ID="${APPLE_API_KEY_ID}"
export APPLE_API_ISSUER="${APPLE_API_ISSUER}"
export APPLE_API_KEY_PATH="$HOME/.apple/${APPLE_API_KEY_ID}.p8"
export APPLE_API_KEY="$HOME/.apple/${APPLE_API_KEY_ID}.p8"