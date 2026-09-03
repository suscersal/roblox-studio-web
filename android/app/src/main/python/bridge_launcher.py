"""
Вызывается из MainActivity.kt. Запускает Flask-приложение из app.py прямо
в этом процессе, на 127.0.0.1.

start_server() блокирует поток — Kotlin запускает её в отдельном Thread.
"""

import os
import sys


def start_server(port: int, data_dir: str = "", hotpatch_dir: str = ""):
    os.environ.setdefault("FLASK_DEBUG", "False")

    # ВАЖНО: этот модуль (bridge_launcher.py) сам НИКОГДА не проходит через
    # OTA-хотфикс — Kotlin-сторона качает только app.py/rbxl_parser.py/
    # index.html (см. OtaUpdater.kt), а bridge_launcher.py грузится
    # исключительно из того, что зашито в APK при сборке. Поэтому его
    # собственный __file__ в момент вызова этой функции — это всегда
    # ПОСТОЯННЫЙ (baked-in) путь внутри APK, и именно рядом с ним лежат
    # icons/ и icons.txt, никогда не подменяемые хотфиксом. Запоминаем
    # этот путь ДО того, как ниже подменим sys.path/cwd на hotpatch_dir.
    baked_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["RSW_ICONS_DIR"] = baked_dir

    # Если Kotlin-сторона скачала обновлённые app.py/index.html (см.
    # MainActivity.checkForOtaUpdate -> OtaUpdater), они лежат в
    # hotpatch_dir. Подсовываем эту папку В НАЧАЛО sys.path, чтобы
    # `import app` нашёл именно скачанную версию, а не ту, что зашита в APK
    # при сборке. icons.txt и icons/ в hotpatch_dir НЕ приезжают (см.
    # комментарий в OtaUpdater.kt) — раньше это молча гасило все иконки в
    # Explorer/Properties, т.к. app.py вычислял ICONS_DIR относительно
    # своего __file__ (который после этой подмены указывает в hotpatch_dir).
    # Явный RSW_ICONS_DIR выше чинит это — app.py теперь всегда берёт
    # иконки из baked_dir, даже когда сам код запущен из hotpatch_dir.
    if hotpatch_dir and os.path.isdir(hotpatch_dir):
        sys.path.insert(0, hotpatch_dir)
        here = hotpatch_dir
    else:
        here = baked_dir

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

    # Публикуем реальный порт для Kotlin-стороны: waitForServerThenLoad()
    # раньше был жёстко привязан к исходному PORT и никогда не узнавал,
    # что сервер фактически поднялся на port+1 (см. комментарий выше) —
    # из-за этого "через раз" ждал подключения не туда и молча падал по
    # таймауту, сколько бы попыток ни давали. Файл кладём в data_dir
    # (filesDir), он читается в MainActivity.waitForServerThenLoad().
    if data_dir:
        try:
            with open(os.path.join(data_dir, "server_port.txt"), "w") as f:
                f.write(str(actual_port))
        except OSError:
            pass

    rsw_app.flask_app.run(
        host="127.0.0.1",
        port=actual_port,
        debug=False,
        use_reloader=False,
        threaded=True,
    )
