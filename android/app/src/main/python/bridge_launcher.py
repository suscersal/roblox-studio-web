"""
Вызывается из MainActivity.kt. Запускает Flask-приложение из app.py прямо
в этом процессе, на 127.0.0.1.

start_server() блокирует поток — Kotlin запускает её в отдельном Thread.
"""

import os
import sys


def start_server(port: int, data_dir: str = ""):
    os.environ.setdefault("FLASK_DEBUG", "False")

    # app.py открывает index.html/icons.txt по ОТНОСИТЕЛЬНОМУ пути
    # (open("index.html", ...)) — это работало локально только потому,
    # что вы запускали `python app.py` из той же папки. Chaquopy стартует
    # процесс с другим текущим каталогом, поэтому переключаемся в папку,
    # где реально лежат app.py/index.html/icons.txt — она всегда та же,
    # что и у этого файла (bridge_launcher.py копируется туда же
    # в шаге "Sync Python sources" из workflow).
    here = os.path.dirname(os.path.abspath(__file__))
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

    rsw_app.flask_app.run(
        host="127.0.0.1",
        port=int(port),
        debug=False,
        use_reloader=False,
        threaded=True,
    )
