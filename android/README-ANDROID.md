# Roblox Studio Web — Android-обёртка

APK = WebView + встроенный CPython (Chaquopy) + существующий Flask-сервер
(`app.py`), запущенный на 127.0.0.1 внутри приложения. Тот же принцип, что
и в maxclient: единственная pip-зависимость — `flask`, а изменения в
`app.py` / `rbxl_parser.py` / `index.html` / `icons.txt` / `icons/` могут
доезжать до установленного APK без переустановки — см. раздел
[Hot-обновления (OTA)](#hot-обновления-ota) ниже.

## Структура

```
roblox-studio-web/
├── app.py                 ← Flask-бэкенд (общий с десктоп-версией)
├── rbxl_parser.py         ← парсер .rbxl (общий с десктоп-версией)
├── index.html              ← фронтенд (общий с десктоп-версией)
├── icons.txt / icons/      ← иконки классов (общие с десктоп-версией)
├── scripts/
│   ├── sync-android-python.sh      ← копирует файлы выше в android/app/src/main/python
│   └── generate-ota-manifest.sh    ← собирает ota/version.json для hot-релиза
├── android/                 ← Android-проект (Chaquopy + Kotlin)
└── .github/workflows/
    └── build-and-release.yml   ← сборка APK и публикация hot-обновлений
```

`app.py`, `rbxl_parser.py`, `index.html`, `icons.txt`, `icons/` — это
единственный источник правды; копия в `android/app/src/main/python`
собирается автоматически шагом `Sync Python sources` в workflow (через
`scripts/sync-android-python.sh`) при каждой сборке. Если хотите собирать
локально в Android Studio — один раз запустите `bash
scripts/sync-android-python.sh` из корня репозитория.

## Локальная сборка (Android Studio)

1. Откройте папку `android/` как проект в Android Studio.
2. Дождитесь sync Gradle (подтянет плагин Chaquopy и Python 3.11).
3. Run ▸ на подключённом устройстве/эмуляторе (arm64).

Без переменных окружения `ANDROID_KEYSTORE_*` сборка подписывается обычным
debug-ключом — этого достаточно для локальной разработки.

## Сборка в GitHub Actions

Workflow триггерится на push в `main` (при изменениях в `android/`,
`app.py`, `rbxl_parser.py`, `index.html`, `icons.txt`, `icons/`,
`scripts/`) и вручную (`workflow_dispatch`). Сначала джоба `detect-changes`
смотрит на список изменённых файлов:

- Если поменялись **только** `app.py` / `rbxl_parser.py` / `index.html` /
  `icons.txt` / `icons/*` — полная сборка APK пропускается, вместо неё
  публикуется лёгкий **hot-update релиз** (см. ниже).
- Если поменялось что-то ещё (Kotlin, gradle, манифест, воркфлоу) —
  собирается полный APK:
  - доступен как **artifact** сборки (вкладка Actions → конкретный run);
  - и как **GitHub Release** с версией `v1.<номер запуска>`, описание
    которого GitHub собирает автоматически из коммитов/PR со времени
    прошлого релиза (`generate_release_notes: true`, как в maxclient).

## Hot-обновления (OTA)

Полная пересборка APK нужна не для каждого изменения — большая часть
логики (Flask-бэкенд, парсер, HTML/JS, иконки классов) грузится Chaquopy
как обычные файлы, без компиляции. Для них есть отдельный путь доставки,
без Google Play/переустановки:

1. CI (`publish-hot-update` job) считает sha256 каждого горячего файла
   через `scripts/generate-ota-manifest.sh` и публикует их вместе с
   `version.json` как **prerelease**-релиз с тегом `hot-<номер запуска>`.
2. При каждом запуске приложение (`OtaUpdater.kt`) смотрит последние
   релизы репозитория, сравнивает версию с сохранённой локально и
   докачивает изменившиеся файлы в `filesDir/hotpatch`.
3. `bridge_launcher.py` подставляет эту папку в начало `sys.path`, поэтому
   `import app` подхватывает скачанную версию вместо той, что была зашита
   в APK при сборке — без переустановки.
4. Если сервер уже успел стартовать в этом процессе со старым кодом,
   приложение просто перезапускает сам процесс, чтобы применить patch.

Полные релизы (`v1.N`) специально не публикуют `version.json` — иначе
`OtaUpdater` не мог бы отличить "просто новый APK" от "есть hot-patch".
Вместо этого он сравнивает `versionCode` установленного APK с сохранённым
и сам стирает устаревший hotpatch при полном обновлении (см. комментарии
в `OtaUpdater.kt`).

### Постоянная подпись (чтобы обновлять APK поверх старой версии)

Без этого шага каждая сборка на CI подписывается новым случайным
debug-ключом, и Android откажется ставить новую версию поверх старой без
удаления. Чтобы подписывать всегда одним ключом:

```bash
keytool -genkey -v -keystore release.keystore -alias rsw \
  -keyalg RSA -keysize 2048 -validity 10000
base64 -w0 release.keystore > release.keystore.base64
```

Добавьте в **Settings → Secrets and variables → Actions** репозитория:

| Secret                     | Значение                                |
| --------------------------- | ---------------------------------------- |
| `ANDROID_KEYSTORE_BASE64`   | содержимое `release.keystore.base64`     |
| `ANDROID_KEYSTORE_PASSWORD` | пароль хранилища, заданный в `keytool`   |
| `ANDROID_KEY_ALIAS`         | `rsw` (или другой alias, что указали)    |
| `ANDROID_KEY_PASSWORD`      | пароль ключа                             |

Без этих секретов workflow всё равно соберёт рабочий (debug-подписанный)
APK — просто без гарантии обновления поверх старой версии.

## Известные ограничения

- `/api/browse` в `app.py` ходит по `Path.home()` / произвольным путям —
  на Android 10+ это не видит внешние файлы из-за scoped storage.
  Открытие/сохранение файлов на Android идёт в обход этого эндпоинта —
  через системный пикер SAF (`window.AndroidBridge.pickRbxlFile()` /
  `exportRbxlFile()` в `index.html`, реализация в `MainActivity.kt`), а не
  через `/api/browse`.
- Иконка приложения не включена в шаблон (чтобы не тащить бинарные PNG) —
  добавьте свои `mipmap-*/ic_launcher.png` и пропишите
  `android:icon="@mipmap/ic_launcher"` в `AndroidManifest.xml`.
- Сборка идёт только под `arm64-v8a` (макс. современных устройств) — чтобы
  добавить `armeabi-v7a`, уберите `ndk { abiFilters ... }` в
  `app/build.gradle` (сборка станет заметно дольше).
