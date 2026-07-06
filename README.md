Part of the code and the README were written by Claude Sonnet 4.6 (I’m not familiar with binary files, and I don’t have the time to write the README myself right now).

[![Скачать](https://img.shields.io/github/downloads/suscersal/roblox-studio-web/total?label=Downloads&style=for-the-badge)](https://github.com/suscersal/roblox-studio-web/releases)

# 🎮 Roblox Studio Web

**Аналог Roblox Studio** без тестов и плагинов, зато с 3D-просмотром.  
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
- 💻 Редактор Lua-скриптов
- ➕ CRUD объектов (30+ классов)
- ☁️ Публикация в Roblox Open Cloud API
- ⌨️ Горячие клавиши

### Установка и запуск

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
pip install -r requirements.txt
python main.py
```


Открыть: `http://localhost:8080`  
С файлом: `python main.py place.rbxl`

### Горячие клавиши

| Клавиши | Действие |
|---|---|
| Ctrl+O | Открыть файл |
| Ctrl+S | Сохранить |
| Ctrl+Shift+S | Сохранить как... |
| Ctrl+C / Ctrl+V | Копировать / Вставить |
| Ctrl+D | Дублировать |
| Delete | Удалить |
| F5 | Обновить 3D-сцену |

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
- 💻 Lua script editor
- ➕ CRUD objects (30+ classes)
- ☁️ Roblox Open Cloud API publishing
- ⌨️ Keyboard shortcuts

### Setup & Run

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
pip install -r requirements.txt
python main.py
```

Open: `http://localhost:8080`  
With file: `python main.py place.rbxl`

### Keyboard Shortcuts

| Keys | Action |
|---|---|
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as... |
| Ctrl+C / Ctrl+V | Copy / Paste |
| Ctrl+D | Duplicate |
| Delete | Delete |
| F5 | Refresh 3D viewport |

### Screenshots

![](https://github.com/suscersal/roblox-studio-web/blob/main/screenshots/1.PNG)

