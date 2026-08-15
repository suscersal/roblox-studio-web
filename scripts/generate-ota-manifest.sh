#!/usr/bin/env bash
# Готовит пакет для OTA-обновления: берёт "горячие" файлы (те, что не требуют
# пересборки APK — чистый Python и статика) из android/app/src/main/python
# (куда их уже разложил scripts/sync-android-python.sh), считает их sha256
# и складывает вместе с version.json в папку ota/ — она заливается как
# GitHub Release asset и скачивается приложением на устройстве.
#
# Использование:
#   bash scripts/generate-ota-manifest.sh <version>
#
# <version> — например "1.7" (то же значение, что ANDROID_VERSION_NAME в CI).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="${1:?Использование: generate-ota-manifest.sh <version>}"
SRC="android/app/src/main/python"
OUT_DIR="ota"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Список "горячих" файлов — тех, что грузятся Python/Flask как обычные
# файлы (не требуют компиляции и не влияют на нативный Kotlin/Java-код).
# Если добавляешь новый файл в корень репозитория, который должен
# обновляться без пересборки APK, — впиши его сюда тоже.
HOT_FILES=(app.py rbxl_parser.py index.html icons.txt)

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
        print(f"[ota] предупреждение: {path} не найден, пропускаю", file=sys.stderr)

# Всё содержимое icons/ (иконки классов) тоже считаем горячим.
icons_src = os.path.join(src, "icons")
if os.path.isdir(icons_src):
    for fname in sorted(os.listdir(icons_src)):
        fpath = os.path.join(icons_src, fname)
        if os.path.isfile(fpath):
            hash_and_copy(f"icons/{fname}", fpath)

with open(os.path.join(out_dir, "version.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"[ota] version.json готов: version={version}, файлов={len(manifest['files'])}")
PYEOF
