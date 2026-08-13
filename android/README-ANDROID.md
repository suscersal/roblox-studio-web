# Roblox Studio Web — Android-обёртка

APK = WebView + встроенный CPython (Chaquopy) + ваш существующий Flask-сервер
(`app.py`), запущенный на 127.0.0.1 внутри приложения. Тот же принцип, что
и в maxclient, но проще: единственная pip-зависимость — `flask`.

## Куда положить файлы этого архива

Распакуйте содержимое **в корень репозитория `roblox-studio-web`**, чтобы
получилось:

```
roblox-studio-web/
├── app.py                 ← у вас уже есть
├── rbxl_parser.py         ← у вас уже есть
├── index.html              ← у вас уже есть
├── icons.txt / icons/      ← у вас уже есть
├── android/                 ← из этого архива
└── .github/workflows/
    └── build-and-release.yml   ← из этого архива
```

`app.py`, `rbxl_parser.py`, `index.html`, `icons.txt`, `icons/` в
`android/app/src/main/python` копировать вручную не нужно — это делает шаг
`Sync Python sources` в workflow при каждой сборке (см. workflow-файл).
Если хотите собирать локально в Android Studio — скопируйте их туда сами
один раз (или запустите тот же `cp`, что и в workflow).

## Локальная сборка (Android Studio)

1. Откройте папку `android/` как проект в Android Studio.
2. Дождитесь sync Gradle (подтянет плагин Chaquopy и Python 3.11).
3. Run ▸ на подключённом устройстве/эмуляторе (arm64).

Без переменных окружения `ANDROID_KEYSTORE_*` сборка подписывается обычным
debug-ключом — этого достаточно для локальной разработки.

## Сборка в GitHub Actions

Workflow триггерится на push в `main` (при изменениях в `android/`,
`app.py`, `rbxl_parser.py`, `index.html`, `icons.txt`) и вручную
(`workflow_dispatch`). Результат:

- APK доступен как **artifact** сборки (вкладка Actions → конкретный run);
- и как **GitHub Release** с версией `v1.<номер запуска>`.

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

## Известные ограничения текущего скелета

- `/api/browse` в `app.py` ходит по `Path.home()` / произвольным путям —
  на Android 10+ это не будет видеть внешние файлы из-за scoped storage.
  В `MainActivity.kt` уже есть рабочий SAF-пикер
  (`window.AndroidBridge.pickRbxlFile()` из JS), который копирует выбранный
  `.rbxl` в приватную папку приложения и зовёт
  `window.onAndroidFileImported(path)` — остаётся добавить кнопку и этот
  колбэк в `index.html`, чтобы дергать открытие файла по этому пути через
  ваш существующий API вместо `/api/browse`.
- Иконка приложения не включена в шаблон (чтобы не тащить бинарные PNG) —
  добавьте свои `mipmap-*/ic_launcher.png` и пропишите
  `android:icon="@mipmap/ic_launcher"` в `AndroidManifest.xml`.
- Сборка идёт только под `arm64-v8a` (макс. современных устройств) — чтобы
  добавить `armeabi-v7a`, уберите `ndk { abiFilters ... }` в
  `app/build.gradle` (сборка станет заметно дольше).
