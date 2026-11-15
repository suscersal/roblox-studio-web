#!/usr/bin/env bash
# Prepares a package for an OTA update: takes the "hot" files (those that don't require
# rebuilding the APK — pure Python and static files) from android/app/src/main/python
# (where scripts/sync-android-python.sh has already placed them), computes their sha256
# and puts them together with version.json into the ota/ folder — it is uploaded as a
# GitHub Release asset and downloaded by the app on the device.
#
# Usage:
#   bash scripts/generate-ota-manifest.sh <version>
#
# <version> — for example "1.7" (the same value as ANDROID_VERSION_NAME in CI).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="${1:?Usage: generate-ota-manifest.sh <version>}"
SRC="android/app/src/main/python"
OUT_DIR="ota"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# The list of "hot" files — those loaded by Python/Flask as ordinary
# files (they need no compilation and don't affect native Kotlin/Java code).
# icons.txt and icons/ are deliberately NOT included here: any icon change
# now always goes through a full APK build (see HOT_REGEX in
# build-and-release.yml) — uploading icons as OTA assets too easily
# runs into the GitHub Releases API limits, and the traffic for downloading each
# separate icon isn't worth it.
# If you add a new file to the repository root that should
# update without rebuilding the APK — add it here too.
# style.css/script.js — used to be part of index.html (a single file),
# after the split into separate files forgetting them here would mean that an
# OTA update reaches only the markup while CSS/JS stay old.
HOT_FILES=(app.py rbxl_parser.py index.html style.css script.js assistant.js collab.js cloud.js)

python3 - "$VERSION" "$SRC" "$OUT_DIR" "${HOT_FILES[@]}" <<'PYEOF'
import sys, os, json, hashlib, shutil

version, src, out_dir, *files = sys.argv[1:]

manifest = {"version": version, "files": {}}


def hash_and_copy(rel_name, abs_path):
    h = hashlib.sha256()
    with open(abs_path, "rb") as f:
        h.update(f.read())
    manifest["files"][rel_name] = h.hexdigest()
    dest = os.path.join(out_dir, rel_name)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(abs_path, dest)


for name in files:
    path = os.path.join(src, name)
    if os.path.isfile(path):
        hash_and_copy(name, path)
    else:
        print(f"[ota] warning: {path} not found, skipping", file=sys.stderr)

with open(os.path.join(out_dir, "version.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"[ota] version.json ready: version={version}, files={len(manifest['files'])}")
PYEOF
