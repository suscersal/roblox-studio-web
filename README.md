Part of the code and the README were written by Claude Sonnet 4.6 (I’m not familiar with binary files, and I don’t have the time to write the README myself right now).

# 🎮 Roblox Studio Web

**Аналог Roblox Studio** без тестов и плагинов, зато с 3D-просмотром.  (Парсер `.rbxl` с веб-обёрткой на **NiceGUI**).

** A Roblox Studio clone (no tests/plugins, but with 3D viewport.(`.rbxl` parser with a NiceGUI web wrapper.) **

## 🇷🇺

### О проекте

Веб-редактор `.rbxl` файлов на Python. Открывает, показывает и редактирует Roblox-проекты в браузере.

**Ядро:** самописный бинарный парсер `.rbxl` с поддержкой:
- LZ4-декомпрессии чанков
- Interleaved-массивов (uint32, uint64, float)
- Roblox float формата
- Delta-кодирования referent'ов
- Всех основных типов свойств (CFrame, Vector3, Color3, UDim2, NumberSequence, Font и др.)

**Интерфейс:** NiceGUI (FastAPI + Vue) + CodeMirror для Lua.

### Возможности

- 📂 Открытие `.rbxl` (бинарный парсинг INST/PRNT/PROP чанков)
- 💾 Сохранение `.rbxl` (побайтовая копия или полная пересборка)
- 🌳 Explorer с иконками классов и поиском
- 🧊 3D-вьюпорт (Part, WedgePart, SpherePart, TrussPart, Seat и др.)
- 📝 Инспектор свойств + редактор CFrame (позиция, вращение, привязка)
- 💻 Редактор Lua-скриптов (CodeMirror, тема Dracula)
- ➕ CRUD объектов (30+ классов)
- ☁️ Публикация в Roblox Open Cloud API
- ⌨️ Горячие клавиши

### Установка и запуск

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
pip install nicegui
python main.py
```

Открыть: `http://localhost:8080`  
С файлом: `python main.py place.rbxl`

### Структура проекта

```
roblox-studio-web/
├── main.py           # Интерфейс (NiceGUI), логика редактора
├── rbxl_parser.py    # Бинарный парсер .rbxl
├── icons.json        # Сопоставление классов → иконки
├── icons/            # PNG-иконки классов
└── README.md
```

### Горячие клавиши

| Клавиши | Действие |
|---------|----------|
| Ctrl+O | Открыть файл |
| Ctrl+S | Сохранить |
| Ctrl+Shift+S | Сохранить как... |
| Ctrl+C / Ctrl+V | Копировать / Вставить |
| Ctrl+D | Дублировать |
| Delete | Удалить |
| F5 | Обновить 3D-сцену |


## EN

### About

A web-based `.rbxl` editor written in Python. Open, view, and edit Roblox projects in your browser.

**Core:** custom binary `.rbxl` parser with:
- LZ4 chunk decompression
- Interleaved arrays (uint32, uint64, float)
- Roblox float format
- Delta-encoded referents
- All major property types (CFrame, Vector3, Color3, UDim2, NumberSequence, Font, etc.)

**Frontend:** NiceGUI (FastAPI + Vue) + CodeMirror for Lua.

### Features

- 📂 Open `.rbxl` (binary INST/PRNT/PROP parsing)
- 💾 Save `.rbxl` (byte-exact copy or full rebuild)
- 🌳 Explorer with class icons and search
- 🧊 3D viewport (Part, WedgePart, SpherePart, TrussPart, Seat, etc.)
- 📝 Property inspector + CFrame editor (position, rotation, snap)
- 💻 Lua script editor (CodeMirror, Dracula theme)
- ➕ Object CRUD (30+ classes)
- ☁️ Publish to Roblox Open Cloud API
- ⌨️ Keyboard shortcuts

### Setup & Run

```
git clone https://github.com/suscersal/roblox-studio-web.git
cd roblox-studio-web
pip install nicegui
python main.py
```

Open: `http://localhost:8080`  
With file: `python main.py place.rbxl`

### Project Structure

```
roblox-studio-web/
├── main.py           # UI (NiceGUI), editor logic
├── rbxl_parser.py    # Binary .rbxl parser
├── icons.json        # Class → icon mapping
├── icons/            # PNG class icons
└── README.md
```

### Keyboard Shortcuts

| Keys | Action |
|------|--------|
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as... |
| Ctrl+C / Ctrl+V | Copy / Paste |
| Ctrl+D | Duplicate |
| Delete | Delete |
| F5 | Refresh 3D viewport |

```