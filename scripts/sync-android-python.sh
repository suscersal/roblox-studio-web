#!/usr/bin/env bash
# Синхронизирует единственный "источник правды" (корневой app.py,
# rbxl_parser.py, index.html, icons.txt, icons/) в папку Chaquopy для
# Android-сборки.
#
# Запускать из корня репозитория:
#   bash scripts/sync-android-python.sh
#
# Используется как локально (перед открытием Android Studio / gradle),
# так и в GitHub Actions (шаг перед сборкой APK и перед публикацией
# hot-update релиза — см. .github/workflows/build-and-release.yml).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DEST="android/app/src/main/python"

echo "[sync] Копирую app.py, rbxl_parser.py, index.html, icons.txt -> $DEST/"
mkdir -p "$DEST"
cp app.py rbxl_parser.py index.html icons.txt "$DEST/"

echo "[sync] Копирую icons/ -> $DEST/icons/"
mkdir -p "$DEST/icons"
cp -r icons/. "$DEST/icons/"

echo "[sync] Готово."
