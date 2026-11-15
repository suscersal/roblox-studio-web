#!/usr/bin/env bash
# Synchronizes the single "source of truth" (the root app.py,
# rbxl_parser.py, index.html, style.css, script.js, icons.txt, icons/)
# into the Chaquopy folder for the Android build.
#
# Run from the repository root:
#   bash scripts/sync-android-python.sh
#
# Used both locally (before opening Android Studio / gradle)
# and in GitHub Actions (a step before building the APK and before publishing the
# hot-update release — see .github/workflows/build-and-release.yml).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DEST="android/app/src/main/python"

echo "[sync] Copying app.py, rbxl_parser.py, index.html, style.css, script.js, assistant.js, collab.js, cloud.js, icons.txt -> $DEST/"
mkdir -p "$DEST"
cp app.py rbxl_parser.py index.html style.css script.js assistant.js collab.js cloud.js icons.txt "$DEST/"

echo "[sync] Copying icons/ -> $DEST/icons/"
mkdir -p "$DEST/icons"
cp -r icons/. "$DEST/icons/"

echo "[sync] Done."
