# AGENTS.md

Guide for AI agents working in the **roblox-studio-web** repository: a web-based `.rbxl` editor (a Roblox Studio clone) built on Python/Flask, with a 3D viewport and an Android wrapper.

Language note: code comments, log messages and the README are mostly in Russian. Keep new comments and commit messages consistent with the surrounding code.

## Stack

- **Backend:** Python 3, Flask (the only pip dependency; `app.py` installs it automatically on first run).
- **Parser:** custom binary `.rbxl` parser (`rbxl_parser.py`), no third-party libraries.
- **Frontend:** a single `index.html` file (~9,700 lines of HTML + CSS + JS), no bundler, no npm.
- **Frontend libraries** live in `vendor/`: `three.min.js`, `cannon.min.js`, `cm6-bundle.min.js` (CodeMirror), `fengari-web.js` (Lua in the browser).
- **Android:** WebView + CPython via Chaquopy + the same Flask server bound to 127.0.0.1.

## Layout

```
app.py                     Flask backend: all /api/* endpoints, state, startup
rbxl_parser.py             parse_rbxl / save_rbxl / publish_place, type decoders and serializers
index.html                 entire UI: Explorer, Properties, 3D viewport, Play mode, Lua editor
icons.txt, icons/          CLASS_ICONS (Python dict) and class icon PNGs
vendor/                    frontend JS libraries (+ vendor/wheels: .whl cache for offline installs)
content/                   Roblox resources (fonts, avatars, textures, api_docs)
asset_cache/               cache of downloaded assets (asset-proxy)
roblox_avatar_download.py  3D avatar downloader
scripts/                   sync-android-python.sh, generate-ota-manifest.sh
android/                   Android project (Kotlin + Chaquopy), see android/README-ANDROID.md
.github/workflows/         build-and-release.yml (APK builds and hot-update releases)
Castle Warfare.rbxl,
Backup_rbxl_file/          sample maps, handy for testing the parser
```

## Running

```bash
python3 app.py                 # no file
python3 app.py place.rbxl      # open a file at startup
```

- The port is the constant `PORT = 47182` in `app.py`. The README mentions 8080, which is outdated; trust the code.
- **Run from the repository root:** `index.html` is read via the relative path `open("index.html")` when `app.py` is imported.
- The server listens on `0.0.0.0` with `threaded=True`. This is required: without it, long requests (e.g. `/api/roblox/avatar3d/fetch`) block the whole editor. Do not remove `threaded=True`.

## Architecture

### State
A global `state` dict in `app.py`: `parsed` (the `parse_rbxl` result), `file_path`, `static_cache`. One open project per process; no sessions and no authentication.

### `parsed` format
Keys the code relies on (do not break them): `referent_to_class`, `parent_map`, `props`, plus internal `_raw_chunks`, `_raw_data`, `_modified`.
`save_rbxl` makes a **byte-for-byte copy** of the original when `_modified` is not set, and a **full rebuild** (`build_rbx_binary`, the same writer that `export_rbxm` uses) when it is. Any endpoint that changes `props`, `parent_map` or `referent_to_class` must set `parsed['_modified'] = True`, otherwise the changes will not be saved.

### Parser (`rbxl_parser.py`)
- `parse_rbxl` also records `prop_types` (`(class, prop) → type_id` as found in the file), `shared_strings` (SSTR), `service_refs` and `skipped_props`. The writer uses the recorded type instead of guessing from the Python value (an enum or referent looks like a plain int). Parser-added helper keys (`Position`/`Rotation` of parts, `Color3`, `Transparency`, `_assets`, derived `Size`) are not real properties and must not be written; see `_writable_props`.
- A property array covers **all instances of a class**, and Studio omits properties whose value is the default, so instances that lack a property get its default from the embedded `_DEFAULTS_B64` table (from `rbx_reflection_database`, MIT; a property absent from the table defaults to 0/false/empty). Binary names differ from reflection names for a few properties (`_BINARY_TO_REFLECTION_NAME`).
- rbxm: `export_rbxm` (selected objects + descendants, no services, referents renumbered, references to objects outside the selection become nil) and `import_rbxm` (merges into `parsed` under a parent, remaps referent and SharedString properties). Binary only; XML (`.rbxmx`) is rejected.
- `TYPE_DECODERS` / `TYPE_SERIALIZERS` map `type_id → function`. Decoders are named `t_*`, serializers `s_*`. When adding a property type, add **both** functions and register them in **both** tables, otherwise saving will drop or corrupt the property.
- Low-level primitives: LZ4 decompression, interleaved arrays (u32/u64/float), the Roblox float format, delta-encoded referents, zigzag transforms (`transform_i32` / `untransform_i32`, etc.). Every read/write pair must be an exact inverse of each other.
- To verify any parser change: open → save → open again, and compare the results on `Castle Warfare.rbxl`. A self-roundtrip cannot catch a wrong header or wrong type ids (the parser and the writer would agree with each other), so also load the saved file with an independent reader such as `rbx_binary` from rbx-dom.

### API (`app.py`, `@flask_app.route` decorators)
Endpoint groups:
- Files: `/api/open`, `/api/open/upload`, `/api/new`, `/api/save`, `/api/save/download`, `/api/browse`, `/api/publish`, `/api/export/rbxm` (GET download / POST to path), `/api/import/rbxm` (by path), `/api/import/rbxm/upload`
- Tree and instances: `/api/tree`, `/api/all_instances`, `/api/scripts`, `/api/gui_tree`, `/api/scene`, `/api/spawn`, `/api/instance` (GET/POST/PUT/DELETE)
- Roblox: `/api/roblox/*` (userid, auth-status, logout, api-key, avatar3d/*), `/api/asset-proxy`
- Utility: `/api/status`, `/api/log`, `/api/log/list`, `/api/log/<name>`, `/vendor/<path>`, `/icons/<path>`, `/`

Responses are JSON of the form `{'ok': True/False, 'error': ...}`; errors are returned with an HTTP 4xx/5xx status and the message in `error`.

### Play-mode logs
Written to `logs/play_*.log` next to `app.py`. Only names matching `play_*.log` inside `LOG_DIR` are served; do not widen this to arbitrary paths.

## Environment variables

| Variable | Purpose |
|---|---|
| `RSW_VENDOR_DIR` | Writable folder for the `.whl` cache (on Android, where the path to `app.py` is read-only) |
| `RSW_ICONS_DIR` | Persistent folder with `icons/` and `icons.txt` (Android hot-patch) |
| `RSW_DATA_DIR` | App data folder; `roblox_auth.json` lives here |

Do not hardcode writable data paths via `Path(__file__).parent`: on Android `__file__` points into a read-only hotpatch directory. Use these variables, falling back to the current behavior.

## Android and hot updates (OTA)

- The **single source of truth** for `app.py`, `rbxl_parser.py`, `index.html`, `icons.txt` and `icons/` is the repository root. **Do not edit** the copies in `android/app/src/main/python/` by hand: they are produced by `bash scripts/sync-android-python.sh` (CI does this in the `Sync Python sources` step). The only file edited by hand in that folder is `bridge_launcher.py`.
- If a commit changes **only** those files, CI publishes a lightweight hot update (`hot-<N>`) instead of a full APK. Changing Kotlin, gradle or the manifest triggers a full build (`v1.<N>`).
- Consequently, `app.py` and `rbxl_parser.py` must keep working without changes to the Kotlin side: do not change signatures or environment variables that `bridge_launcher.py` relies on without a matching Android-side change.
- On Android, files are opened through SAF (`window.AndroidBridge.pickRbxlFile()` / `exportRbxlFile()`), not through `/api/browse`. Do not rely on `/api/browse` in Android flows.
- Details: `android/README-ANDROID.md`.

## Rules for making changes

1. **Minimal diffs.** The files are large (`index.html` ~9,700 lines, `app.py` ~2,300, `rbxl_parser.py` ~1,260). Edit surgically (`str_replace`); do not rewrite files wholesale or reformat code you did not change.
2. **No new dependencies.** There is intentionally no `requirements.txt`: the project must run on bare Python (including Termux and Android). Apart from Flask, use only the standard library. New JS libraries go into `vendor/` and are loaded locally, with no CDN (the app must work offline).
3. **Offline-first.** Do not add mandatory network requests to the startup or file-open path. Network features (Open Cloud, avatars, asset-proxy) must degrade gracefully without internet.
4. **Termux/Android compatibility.** Avoid platform-specific things (Windows paths, `os.startfile`, native extensions) and do not assume a GUI browser is available.
5. **Secrets.** The Roblox API key and `.ROBLOSECURITY` are sensitive. Do not log them, write them to `logs/`, return them in full to the client, or commit `roblox_auth.json`.
6. **Path safety.** Endpoints that accept paths (`/api/open`, `/api/save`, `/api/browse`) and file-serving routes (`/vendor/`, `/icons/`, `/api/log/<name>`) must use `send_from_directory` or name validation, not string concatenation of user input into a path.
7. **Icons.** `icons.txt` is executed via `exec` with empty `__builtins__`; keep it a plain Python dict, `CLASS_ICONS = {...}`, with no code.
8. **Do not touch `content/` or `asset_cache/`** without a clear reason: they are resources and cache, not source code.
9. **Do not commit junk:** `*.rej`, `*.patch`, `*.log`, `*.pyc`, keystore files (see `.gitignore`). The file `android/README-ANDROID.md.rej` in the repository is an accidental artifact and can be deleted.
10. **License:** GPL-3.0. Do not paste in code with an incompatible license.

## Verifying changes

The repository has no automated tests, so verify manually:

```bash
python3 -m py_compile app.py rbxl_parser.py roblox_avatar_download.py
python3 app.py "Castle Warfare.rbxl"     # should print a "loaded ... (N objects)" line
curl -s localhost:47182/api/status
curl -s localhost:47182/api/tree | head -c 500
```

For parser changes, also run a roundtrip:

```python
from rbxl_parser import parse_rbxl, save_rbxl
p = parse_rbxl('Castle Warfare.rbxl')
p['_modified'] = True                  # force a full rebuild
save_rbxl(p, '/tmp/out.rbxl')
q = parse_rbxl('/tmp/out.rbxl')
assert p['referent_to_class'] == q['referent_to_class']
assert p['parent_map'] == q['parent_map']
assert p['props'] == q['props']
```

For frontend changes, test in a browser: open a file, select an object, edit a property, save, press F5, try Play mode, and check the console for errors.

## Known quirks

- Play mode (cannon.js physics, first-person camera, Lua via fengari) is experimental; it is not fully Roblox-compatible.
- `HIDDEN` in `app.py` is the set of services/classes hidden from the Explorer; change it there, not in the JS.
- Publishing goes through Roblox Open Cloud (`publish_place`) and needs an API key with permissions for the target universe/place.
