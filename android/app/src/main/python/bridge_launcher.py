"""
Вызывается из MainActivity.kt. Запускает Flask-приложение из app.py прямо
в этом процессе, на 127.0.0.1.

start_server() блокирует поток — Kotlin запускает её в отдельном Thread.
"""

import os
import sys


def start_server(port: int, data_dir: str = "", hotpatch_dir: str = ""):
    os.environ.setdefault("FLASK_DEBUG", "False")

    # Если Kotlin-сторона скачала обновлённые app.py/index.html/icons.txt/
    # icons/ (см. MainActivity.checkForOtaUpdate -> OtaUpdater), они лежат в
    # hotpatch_dir. Подсовываем эту папку В НАЧАЛО sys.path, чтобы
    # `import app` нашёл именно скачанную версию, а не ту, что зашита в APK
    # при сборке. app.py сам вычисляет ICONS_DIR относительно своего
    # __file__, поэтому вместе с app.py подхватятся и icons/ из той же
    # папки — пересборка APK для этого не нужна.
    if hotpatch_dir and os.path.isdir(hotpatch_dir):
        sys.path.insert(0, hotpatch_dir)
        here = hotpatch_dir
    else:
        here = os.path.dirname(os.path.abspath(__file__))

    # app.py открывает index.html/icons.txt по ОТНОСИТЕЛЬНОМУ пути
    # (open("index.html", ...)) — это работало локально только потому,
    # что вы запускали `python app.py` из той же папки. Chaquopy стартует
    # процесс с другим текущим каталогом, поэтому переключаемся в папку,
    # где реально лежат app.py/index.html/icons.txt (обычная сборка) или в
    # hotpatch_dir (после OTA-обновления) — иначе open("index.html", ...)
    # найдёт старую версию файла из первой попавшейся папки на sys.path.
    os.chdir(here)

    # data_dir — приватная папка приложения (filesDir), куда Kotlin-сторона
    # копирует .rbxl-файлы, выбранные пользователем через системный пикер
    # (см. MainActivity.importRbxlFile). Прокидываем как переменную
    # окружения — app.py может ориентироваться на неё для /api/browse,
    # если вы решите ограничить обзор файлов только этой папкой, а не
    # Path.home() (на Android 10+ произвольный обзор ФС всё равно не
    # сработает из-за scoped storage).
    if data_dir:
        os.environ["RSW_DATA_DIR"] = data_dir

    # app.py содержит `_ensure('flask')` и подобные проверки — они
    # безвредны при импорте, т.к. flask уже установлен через chaquopy pip.
    import app as rsw_app  # это ваш существующий app.py

    # Подстраховка от SystemExit(1) из werkzeug при "Address already in
    # use": пробуем запрошенный порт, а если занят — перебираем следующие
    # 20. Реальный порт нигде дополнительно не публикуется — Kotlin-сторона
    # всё равно ждёт именно исходный PORT в waitForServerThenLoad(), так
    # что это чисто аварийный fallback для случая внешнего конфликта (не
    # спасёт от повторного вызова start_server в этом же процессе — тот
    # случай уже прикрыт флагом serverStarted в MainActivity.kt).
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

    rsw_app.flask_app.run(
        host="127.0.0.1",
        port=actual_port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
