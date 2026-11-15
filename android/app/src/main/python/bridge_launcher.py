"""
Called from MainActivity.kt. Starts the Flask app from app.py right
in this process, on 127.0.0.1.

start_server() blocks the thread — Kotlin runs it in a separate Thread.
"""

import os
import sys


def start_server(port: int, data_dir: str = "", hotpatch_dir: str = ""):
    os.environ.setdefault("FLASK_DEBUG", "False")

    # IMPORTANT: this module (bridge_launcher.py) itself NEVER goes through the
    # OTA hotfix — the Kotlin side downloads only
    # app.py/rbxl_parser.py/index.html/style.css/script.js (see OtaUpdater.kt), while bridge_launcher.py is loaded
    # exclusively from what is baked into the APK at build time. Therefore its
    # own __file__ at the moment this function is called is always the
    # PERMANENT (baked-in) path inside the APK, and right next to it lie
    # icons/ and icons.txt, which a hotfix never replaces. We remember
    # this path BEFORE below we swap sys.path/cwd for hotpatch_dir.
    baked_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["RSW_ICONS_DIR"] = baked_dir

    # If the Kotlin side has downloaded updated app.py/index.html/style.css/script.js (see
    # MainActivity.checkForOtaUpdate -> OtaUpdater), they lie in
    # hotpatch_dir. We put this folder AT THE START of sys.path so that
    # `import app` finds exactly the downloaded version, not the one baked into the APK
    # at build time. icons.txt and icons/ do NOT come to hotpatch_dir (see the
    # comment in OtaUpdater.kt) — this used to silently turn off all icons in
    # Explorer/Properties, since app.py computed ICONS_DIR relative to
    # its own __file__ (which after this swap points into hotpatch_dir).
    # The explicit RSW_ICONS_DIR above fixes this — app.py now always takes
    # icons from baked_dir, even when the code itself runs from hotpatch_dir.
    if hotpatch_dir and os.path.isdir(hotpatch_dir):
        sys.path.insert(0, hotpatch_dir)
        here = hotpatch_dir
    else:
        here = baked_dir

    # app.py opens index.html/icons.txt by a RELATIVE path
    # (open("index.html", ...)) — this worked locally only because
    # you ran `python app.py` from the same folder. Chaquopy starts the
    # process with a different current directory, so we switch to the folder
    # where app.py/index.html/style.css/script.js/icons.txt really lie (an ordinary build) or to
    # hotpatch_dir (after an OTA update) — otherwise open("index.html", ...)
    # would find an old version of the file from the first folder on sys.path.
    os.chdir(here)

    # data_dir — the app's private folder (filesDir), where the Kotlin side
    # copies the .rbxl files chosen by the user through the system picker
    # (see MainActivity.importRbxlFile). We pass it as an environment
    # variable — app.py can rely on it for /api/browse,
    # if you decide to limit file browsing to only this folder rather than
    # Path.home() (on Android 10+ arbitrary file system browsing won't work
    # anyway because of scoped storage).
    if data_dir:
        os.environ["RSW_DATA_DIR"] = data_dir

    # app.py contains `_ensure('flask')` and similar checks — they are
    # harmless on import, since flask is already installed via chaquopy pip.
    import app as rsw_app  # this is your existing app.py

    # A safety net against SystemExit(1) from werkzeug on "Address already in
    # use": we try the requested port, and if it is taken — we try the next
    # 20. The real port isn't published anywhere else — the Kotlin side
    # still waits for the original PORT in waitForServerThenLoad(), so
    # this is purely an emergency fallback for the case of an external conflict (it won't
    # save from a repeated start_server call in this same process — that
    # case is already covered by the serverStarted flag in MainActivity.kt).
    import socket as _socket

    def _port_free(p):
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", p))
            return True
        except OSError:
            return False
        finally:
            s.close()

    actual_port = int(port)
    if not _port_free(actual_port):
        for candidate in range(int(port) + 1, int(port) + 21):
            if _port_free(candidate):
                actual_port = candidate
                break

    # We publish the real port for the Kotlin side: waitForServerThenLoad()
    # used to be rigidly tied to the original PORT and never learned
    # that the server had actually come up on port+1 (see the comment above) —
    # because of this it «every other time» waited for a connection in the wrong place and silently failed
    # on timeout, however many attempts were given. We put the file in data_dir
    # (filesDir), it is read in MainActivity.waitForServerThenLoad().
    if data_dir:
        try:
            with open(os.path.join(data_dir, "server_port.txt"), "w") as f:
                f.write(str(actual_port))
        except OSError:
            pass

    rsw_app.flask_app.run(
        # 0.0.0.0, as in the desktop version: otherwise the room (collab) is unavailable to
        # other devices. Sensitive endpoints in app.py accept only loopback anyway,
        # and guest writes require X-Collab-Token.
        host="0.0.0.0",
        port=actual_port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
