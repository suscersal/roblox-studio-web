Part of the code and the README were written by Claude Sonnet 4.6 (I’m not familiar with binary files, and I don’t have the time to write the README myself right now).

[![Download](https://img.shields.io/github/downloads/suscersal/roblox-studio-web/total?label=Downloads&style=for-the-badge)](https://github.com/suscersal/roblox-studio-web/releases)

# 🎮 Roblox Studio Web

**Аналог Roblox Studio** без тестов(полноценных) и плагинов, зато с 3D-просмотром.  
Парсер `.rbxl` с веб-обёрткой на **Flask**.

**A Roblox Studio clone** with a 3D viewport, built around a custom `.rbxl` parser and a Flask web wrapper.

## 🇷🇺

### О проекте

Веб-редактор `.rbxl` файлов на Python. Открывает, показывает и редактирует Roblox-проекты в браузере.

**Ядро:** самописный бинарный парсер `.rbxl` с поддержкой:
- LZ4-декомпрессии чанков
- Interleaved-массивов (uint32, uint64, float)
- Roblox float формата
- Delta-кодирования referent'ов
- Всех основных типов свойств (CFrame, Vector3, Color3, UDim2, NumberSequence, Font и др.)

**Интерфейс:** Flask + HTML/CSS/JavaScript.

### Возможности

- 📂 Открытие `.rbxl` (бинарный парсинг INST/PRNT/PROP чанков)
- 💾 Сохранение `.rbxl` (байтовая копия или полная пересборка)
- 🌳 Explorer с иконками классов и поиском
- 🧊 3D-вьюпорт (Part, WedgePart, SpherePart, TrussPart, Seat и др.)
- 📝 Инспектор свойств + редактор CFrame
- 💻 Редактор Lua-скриптов (CodeMirror с подсветкой Lua)
- ➕➖ Добавление/удаление объектов (33 класса на выбор)
- ▶️ Play-режим: простая физическая симуляция + камера от первого лица
  (управление WASD/джойстик на тач-устройствах) — экспериментально
- ☁️ Публикация в Roblox Open Cloud API
- ⌨️ Горячие клавиши
- 📱 Android-приложение (WebView + встроенный Python через Chaquopy,
  с фоновыми hot-обновлениями без переустановки APK) — см.
  [`android/README-ANDROID.md`](android/README-ANDROID.md)

### Установка и запуск

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
python3 app.py
```

Отдельно ставить зависимости не нужно — `app.py` сам поставит `flask`
через pip при первом запуске, если его ещё нет.

Открыть: `http://localhost:8080`  
С файлом: `python3 app.py place.rbxl`

### Горячие клавиши

| Клавиши | Действие |
|---|---|
| Ctrl+O | Открыть файл |
| Ctrl+S | Сохранить |
| Ctrl+Shift+S | Сохранить как... |
| Delete | Удалить выбранный объект |
| Escape | Закрыть окно / снять выделение |
| F5 | Обновить 3D-сцену |
| F | Навести камеру на выбранный объект |

## EN

### About

A web-based `.rbxl` editor written in Python. It opens, views, and edits Roblox projects in the browser.

**Core:** a custom binary `.rbxl` parser with support for:
- LZ4 chunk decompression
- Interleaved arrays (uint32, uint64, float)
- Roblox float format
- Delta-encoded referents
- Major property types (CFrame, Vector3, Color3, UDim2, NumberSequence, Font, etc.)

**Frontend:** Flask + HTML/CSS/JavaScript.

### Features

- 📂 Open `.rbxl` files with binary INST/PRNT/PROP parsing
- 💾 Save `.rbxl` files as a byte-exact copy or full rebuild
- 🌳 Explorer with class icons and search
- 🧊 3D viewport (Part, WedgePart, SpherePart, TrussPart, Seat, etc.)
- 📝 Property inspector + CFrame editor
- 💻 Lua script editor (CodeMirror with Lua syntax highlighting)
- ➕➖ Add/delete objects (33 selectable classes)
- ▶️ Play mode: basic physics simulation + first-person camera
  (WASD / on-screen joystick on touch devices) — experimental
- ☁️ Roblox Open Cloud API publishing
- ⌨️ Keyboard shortcuts
- 📱 Android app (WebView + embedded Python via Chaquopy, with
  background hot-updates that don't require reinstalling the APK) —
  see [`android/README-ANDROID.md`](android/README-ANDROID.md)

### Setup & Run

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
python3 app.py
```

No separate dependency install needed — `app.py` installs `flask` via
pip on first run if it isn't already present.

Open: `http://localhost:8080`  
With file: `python3 app.py place.rbxl`

### Keyboard Shortcuts

| Keys | Action |
|---|---|
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as... |
| Delete | Delete selected object |
| Escape | Close dialog / deselect |
| F5 | Refresh 3D viewport |
| F | Focus camera on selected object |

### Screenshots

![](https://github.com/suscersal/roblox-studio-web/blob/main/screenshots/1.png)
![](https://github.com/suscersal/roblox-studio-web/blob/main/screenshots/2.png)
![](https://github.com/suscersal/roblox-studio-web/blob/main/screenshots/3.png)

