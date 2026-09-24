#!/usr/bin/env python3
import urllib.error as _urlerr
import urllib.request as _req
import re as _re
import base64 as _b64
import base64
import struct
import math
import traceback
import json
from urllib.parse import quote
from rbxl_parser import parse_rbxl, save_rbxl, publish_place, export_rbxm, import_rbxm
from flask import Flask, request, jsonify, Response, send_from_directory
from pathlib import Path
import sys
import subprocess
import os
import io



# Кэш .whl рядом со скриптом — после первой (единственной) установки с
# сетью pip кладёт сюда скачанные колёса, и все последующие запуски на
# Termux (в т.ч. без интернета — самолёт, метро, нет сим-карты) ставят
# зависимости из ЭТОЙ папки через --no-index, а не заново из PyPI.
#
# RSW_VENDOR_DIR — та же логика, что у RSW_ICONS_DIR ниже: если app.py
# запущен из-под APK-обёртки (bridge_launcher.py подменяет __file__ на
# путь внутри hotpatch, который недоступен на запись), эта переменная
# указывает на настоящую писабельную папку (например filesDir/vendor).
# При обычном запуске (`python app.py` в Termux/на ПК) — путь рядом со
# скриптом, как и раньше.
VENDOR_DIR = Path(os.environ['RSW_VENDOR_DIR']) if os.environ.get('RSW_VENDOR_DIR') \
    else Path(__file__).parent / 'vendor'
_WHEELS_DIR = VENDOR_DIR / 'wheels'


def _ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
        return
    except ImportError:
        pass

    _WHEELS_DIR.mkdir(parents=True, exist_ok=True)
    has_cached = any(_WHEELS_DIR.glob(f'{pkg.replace("-", "_")}*'))

    if has_cached:
        print(f'[RbxStudio] Устанавливаю {pkg} из локального кэша (офлайн)...')
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', pkg,
                '--break-system-packages', '-q',
                '--no-index', '--find-links', str(_WHEELS_DIR),
            ])
            return
        except subprocess.CalledProcessError:
            print(f'[RbxStudio] Офлайн-кэш для {pkg} не подошёл, пробую сеть...')

    print(f'[RbxStudio] Устанавливаю {pkg} (и сохраняю .whl в кэш для офлайн-запусков)...')
    # Сначала скачиваем колесо в кэш, потом ставим из него — так кэш
    # пополняется независимо от того, есть у pip install свой кэш или нет.
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'download', pkg,
            '-d', str(_WHEELS_DIR), '-q',
        ])
    except subprocess.CalledProcessError:
        pass  # даже без скачивания .whl обычная установка ниже может сработать
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', pkg,
        '--break-system-packages', '-q',
        '--find-links', str(_WHEELS_DIR),
    ])


_ensure('flask')


sys.path.insert(0, str(Path(__file__).parent))

# На Android иконки (icons/, icons.txt) НИКОГДА не проходят через
# OTA-хотфикс (см. OtaUpdater.kt) — только через полную пересборку APK.
# Но bridge_launcher.py при наличии хотфикса подменяет __file__ этого
# модуля на путь внутри filesDir/hotpatch, где icons/ и icons.txt
# физически не существуют. Раньше это молча обнуляло CLASS_ICONS и
# гасило все иконки в Explorer/Properties. RSW_ICONS_DIR — явный путь к
# ПОСТОЯННОЙ (baked-in) папке приложения, который bridge_launcher.py
# прокидывает через переменную окружения именно на такой случай; если
# её нет (обычный запуск `python app.py` с ПК), используем прежнее
# поведение — путь рядом с этим файлом.
_ICONS_BASE = Path(os.environ['RSW_ICONS_DIR']) if os.environ.get('RSW_ICONS_DIR') \
    else Path(__file__).parent

ICONS_DIR = _ICONS_BASE / 'icons'
PORT = 47182  # нестандартный порт — 8080 часто занят другими приложениями/ADB

CLASS_ICONS = {}
_icon_b64 = {}


def _load_icons():
    global CLASS_ICONS
    for p in [_ICONS_BASE / 'icons.json',
              _ICONS_BASE / 'icons.txt']:
        if not p.exists():
            continue
        try:
            txt = p.read_text(encoding='utf-8')
            if p.suffix == '.json':
                CLASS_ICONS = json.loads(txt)
            else:
                ns = {}
                exec(txt, {'__builtins__': {}}, ns)
                CLASS_ICONS = ns.get('CLASS_ICONS', {})
            break
        except Exception:
            pass
    if ICONS_DIR.exists():
        for f in ICONS_DIR.iterdir():
            if f.suffix.lower() == '.png':
                try:
                    _icon_b64[f.name] = (
                        'data:image/png;base64,' +
                        base64.b64encode(f.read_bytes()).decode()
                    )
                except Exception:
                    pass


_load_icons()


def icon_src(cls):
    # 'Instance.png' в icons/ никогда не было — любой класс без записи в
    # CLASS_ICONS раньше молча оставался без иконки. 'Unknown.png' там
    # реально есть.
    fn = CLASS_ICONS.get(cls, 'Unknown.png')
    return _icon_b64.get(fn, '')


state = {
    'parsed':    None,
    'file_path': None,
    'static_cache': None,
}

HIDDEN = {
    'Debris', 'CookiesService', 'InsertService', 'GamePassService', 'VRService',
    'Selection', 'ContextActionService', 'Instance', 'LuaWebService',
    'FilteredSelection', 'LocalizationService', 'PhysicsService',
    'TouchInputService', 'AvatarSettings', 'GuidRegistryService',
    'ProcessInstancePhysicsService', 'HttpService', 'UGCAvatarService',
    'VirtualInputManager', 'VideoService', 'CollectionService',
    'VideoCaptureService', 'NonReplicatedCSGDictionaryService',
    'CSGDictionaryService', 'TweenService', 'PermissionsService',
}

PART_CLASSES = {
    'Part', 'WedgePart', 'CornerWedgePart', 'TrussPart',
    'SpawnLocation', 'Seat', 'VehicleSeat', 'SpherePart',
    # MeshPart раньше сюда не входил — такие объекты молча пропускались
    # в build_all_scene_objects (см. ниже) и вообще не попадали в сцену,
    # хотя парсер их видит и активно используется классом в
    # Lua-песочнице/диалоге "Добавить". Рендерим как обычный box (реальная
    # геометрия .mesh не разбирается — см. _extract_part_texture_id ниже
    # про текстуру).
    'MeshPart',
}

# Классы 2D-интерфейса (Roblox GUI) — рендерятся отдельным DOM-оверлеем
# поверх 3D-вьюпорта в Play (см. index.html, buildGuiOverlay/#gui-overlay),
# а не как объекты сцены three.js/cannon.js, как PART_CLASSES.
GUI_ROOT_CLASSES = {'ScreenGui', 'BillboardGui'}
GUI_CONTAINER_CLASSES = {'Frame', 'ScrollingFrame'}
GUI_LEAF_CLASSES = {
    'TextLabel', 'TextButton', 'TextBox', 'ImageLabel', 'ImageButton',
}
# UICorner/UIStroke не рисуются отдельным DOM-узлом — они модификаторы
# соседнего GUI-объекта (border-radius / обводка), см. index.html
# applyGuiDecorationToParent. Раньше их не было ни в одном из наборов
# классов вообще, поэтому /api/gui_tree их молча отбрасывал — фронтенд
# никогда не узнавал о TopLeftRadius/.../Thickness, лежащих в самом
# .rbxl, и все GUI-плашки в Play всегда рисовались с прямыми углами и
# без обводки, независимо от того, что реально настроено в файле.
GUI_DECORATION_CLASSES = {'UICorner', 'UIStroke'}
GUI_CLASSES = GUI_ROOT_CLASSES | GUI_CONTAINER_CLASSES | GUI_LEAF_CLASSES | GUI_DECORATION_CLASSES

# Свойства, которые реально нужны фронтенду для рисования GUI-оверлея —
# сознательно узкий список (как и SCRIPT_CLASSES выше по духу), чтобы не
# гонять по сети произвольные бинарные/редкие свойства ради одного div'а.
GUI_PROPS = (
    'Name', 'Position', 'Size', 'AnchorPoint', 'Visible', 'Enabled',
    'ZIndex', 'BackgroundColor3', 'BackgroundTransparency', 'BorderSizePixel',
    'BorderColor3', 'Text', 'TextColor3', 'TextTransparency', 'TextSize',
    'TextScaled', 'TextWrapped', 'TextXAlignment', 'TextYAlignment', 'Font',
    'Image', 'ScaleType', 'ClipsDescendants',
    # UICorner: некоторые файлы (в т.ч. этот) хранят независимый радиус
    # на каждый угол (более новый вариант UICorner в Roblox) вместо
    # одного общего CornerRadius — фронтенд понимает оба варианта.
    'CornerRadius', 'TopLeftRadius', 'TopRightRadius',
    'BottomLeftRadius', 'BottomRightRadius',
    # UIStroke
    'Color', 'Thickness', 'Transparency',
)

# Script/LocalScript исполняются в РАЗНЫХ средах в настоящем Roblox
# (сервер и клиент соответственно) — 'side' используется фронтендом
# (index.html, /api/scripts) только для того, чтобы пометить бейджем и в
# Output, откуда пришёл вывод; сам движок остаётся с одной общей Lua VM
# (нет настоящей сети клиент↔сервер), см. комментарий у api_scripts ниже.
SCRIPT_SIDE = {'Script': 'server', 'LocalScript': 'client', 'ModuleScript': 'shared'}


def safe_float(v, default=0.0):
    try:
        f = float(v)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except Exception:
        return default


def get_vec3(d, default=1.0):
    if not isinstance(d, dict):
        return default, default, default
    return (safe_float(d.get('x', default), default),
            safe_float(d.get('y', default), default),
            safe_float(d.get('z', default), default))


def get_color(c):
    if not isinstance(c, dict):
        return '#a0a0a0'
    r = min(255, int(safe_float(c.get('r', 0.6)) * 255))
    g = min(255, int(safe_float(c.get('g', 0.6)) * 255))
    b = min(255, int(safe_float(c.get('b', 0.6)) * 255))
    return f'#{r:02x}{g:02x}{b:02x}'


def get_part_color(props):
    """Цвет BasePart. В новых .rbxl (zstd, 2024+) цвет лежит в свойстве
    Color3uint8 (целые 0..255), а НЕ в Color3/Color (float 0..1) — раньше
    читались только последние, поэтому все Part из новых файлов были
    серыми (#a0a0a0): Head/Torso/руки/ноги R6 без цвета кожи и т.д."""
    c8 = props.get('Color3uint8')
    if isinstance(c8, dict) and 'r' in c8:
        r = max(0, min(255, int(safe_float(c8.get('r', 160), 160))))
        g = max(0, min(255, int(safe_float(c8.get('g', 160), 160))))
        b = max(0, min(255, int(safe_float(c8.get('b', 160), 160))))
        return f'#{r:02x}{g:02x}{b:02x}'
    col = props.get('Color') or props.get('Color3') or props.get('BrickColor')
    return get_color(col) if isinstance(col, dict) else '#a0a0a0'


# Enum.MeshType (SpecialMesh.MeshType): Head=0, Torso=1, Wedge=2, Sphere=3,
# Cylinder=4, FileMesh=5, Brick=6, Prism=7, Pyramid=8, ParallelRamp=9,
# RightAngleRamp=10, CornerWedge=11. Раньше 1 читался как цилиндр, а 6
# (Brick) как клин — числа были перепутаны.
MESHTYPE_TO_SHAPE = {
    0: 'head', 1: 'box', 2: 'wedge', 3: 'sphere', 4: 'cylinder',
    6: 'box', 7: 'wedge', 8: 'cone', 9: 'wedge', 10: 'wedge', 11: 'wedge',
}


def find_special_mesh(ref, children_by_parent, all_props, referent_to_class):
    """Свойства первого SpecialMesh-ребёнка части (или None). Раньше
    искали по номеру referent (ref+1 / ref+2) — это работало только пока
    меш лежал в файле сразу после детали."""
    for child in children_by_parent.get(ref, ()):
        if referent_to_class.get(child) == 'SpecialMesh':
            return all_props.get(child, {})
    return None


def get_pos(cf):
    if not isinstance(cf, dict):
        return 0.0, 0.0, 0.0
    pos = cf.get('position', {})
    if isinstance(pos, dict):
        return get_vec3(pos, 0.0)
    mat = cf.get('matrix')
    if isinstance(mat, (list, tuple)) and len(mat) >= 12:
        return (safe_float(mat[3]), safe_float(mat[7]), safe_float(mat[11]))
    return 0.0, 0.0, 0.0


def get_rot_matrix(cf):
    if not isinstance(cf, dict):
        return [1, 0, 0, 0, 1, 0, 0, 0, 1]
    mat = cf.get('matrix')
    if isinstance(mat, (list, tuple)) and len(mat) >= 9:
        return [safe_float(v) for v in mat[:9]]
    angles = cf.get('angles_deg')
    if angles:
        rx, ry, rz = [math.radians(a) for a in angles]
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        return [
            cy*cz, -cy*sz, sy,
            sx*sy*cz+cx*sz, -sx*sy*sz+cx*cz, -sx*cy,
            -cx*sy*cz+sx*sz, cx*sy*sz+sx*cz, cx*cy
        ]
    return [1, 0, 0, 0, 1, 0, 0, 0, 1]


def serialize_prop(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    try:
        json.dumps(v)
        return v
    except Exception:
        return str(v)


CHUNK_SIZE = 48.0   # студов — целевой размер стороны одного фрагмента
CHUNK_MAX_GRID = 16  # ограничение и по X, и по Z из соображений пользователя
# Порог, ниже которого объект не режем — нет смысла плодить фрагменты
# для условного забора 60x2x2.
CHUNK_MIN_DIM = 64.0


def _rot_axis_world(rot, col):
    # rot — построчная 3x3 матрица (см. get_rot_matrix); мировое направление
    # локальной оси col — это СТОЛБЕЦ col матрицы (умножение R * e_col).
    return (rot[col], rot[3 + col], rot[6 + col])


def chunk_box_object(o):
    """Режет один box-объект на сетку под-фрагментов по двум наибольшим
    измерениям (третье — обычно толщина — не трогаем). Каждый фрагмент —
    самостоятельный объект с честным центром и размером, чтобы дистанция
    до игрока считалась по кускам, а не по гигантскому исходнику."""
    dims = [('sx', o['sx']), ('sy', o['sy']), ('sz', o['sz'])]
    # индексы измерений от большего к меньшему
    order = sorted(range(3), key=lambda i: -dims[i][1])
    big_a, big_b, keep = order[0], order[1], order[2]
    dim_names = ['sx', 'sy', 'sz']

    size_a = dims[big_a][1]
    size_b = dims[big_b][1]
    if max(size_a, size_b) < CHUNK_MIN_DIM:
        return [o]

    grid_a = max(1, min(CHUNK_MAX_GRID, math.ceil(size_a / CHUNK_SIZE)))
    grid_b = max(1, min(CHUNK_MAX_GRID, math.ceil(size_b / CHUNK_SIZE)))
    if grid_a == 1 and grid_b == 1:
        return [o]

    cell_a = size_a / grid_a
    cell_b = size_b / grid_b

    axis_a = _rot_axis_world(o['rot'], big_a)
    axis_b = _rot_axis_world(o['rot'], big_b)

    out = []
    for i in range(grid_a):
        # смещение центра фрагмента i вдоль локальной оси big_a от центра
        # исходного объекта (в студах, в локальных координатах)
        off_a = -size_a * 0.5 + cell_a * (i + 0.5)
        for j in range(grid_b):
            off_b = -size_b * 0.5 + cell_b * (j + 0.5)
            wx = o['px'] + axis_a[0] * off_a + axis_b[0] * off_b
            wy = o['py'] + axis_a[1] * off_a + axis_b[1] * off_b
            wz = o['pz'] + axis_a[2] * off_a + axis_b[2] * off_b

            new_sizes = {dim_names[big_a]: cell_a,
                         dim_names[big_b]: cell_b,
                         dim_names[keep]: dims[keep][1]}

            chunk = dict(o)
            chunk.update(new_sizes)
            chunk['px'], chunk['py'], chunk['pz'] = wx, wy, wz
            # синтетический, но уникальный ref — реальный ref детали
            # закодирован в старших разрядах, коллизий с настоящими
            # referent-ами (обычно < 10^6) быть не должно
            chunk['ref'] = o['ref'] * 100000 + i * CHUNK_MAX_GRID + j
            chunk['source_ref'] = o['ref']
            out.append(chunk)
    return out


def chunk_large_objects(objs):
    out = []
    for o in objs:
        # meshId — реальная кастомная геометрия (см. _extract_real_mesh_id),
        # а не настоящий bounding-box: chunk_box_object режет объект на
        # суб-боксы буквально по его Size, что для реального меша (форма
        # почти никогда не совпадает с прямоугольником) раздробило бы
        # видимую модель на набор неверных кубов вместо неё самой.
        if o.get('shape') == 'box' and not o.get('meshId'):
            out.extend(chunk_box_object(o))
        else:
            out.append(o)
    return out



# Счётчик версий сцены: правки в редакторе (добавление/удаление/смена
# свойств объекта) мутируют state['parsed'] НА МЕСТЕ, не пересоздавая сам
# словарь — значит id(parsed) не меняется, и кэши ниже (build_all_scene_
# objects/get_chunk_index), завязанные только на id(parsed), продолжали бы
# молча отдавать данные до правки.
# Каждая точка мутации (см. api_edit_prop/api_add_instance/api_delete)
# зовёт bump_scene_version() — кэши ключуются на (id(parsed), version), так
# что любая правка честно инвалидирует их все разом.
_scene_version = {'v': 0}


def bump_scene_version():
    _scene_version['v'] += 1


# ---- Chunk-based стриминг (как в Minecraft / Unreal World Partition) ----
#
# Все предыдущие итерации (один луч → веер лучей → лучи с радиусом →
# лучи неограниченной длины) пытались решить "что подгрузить" через
# направление взгляда камеры. Это НЕ то, как это принято делать —
# ни один крупный движок с open-world стримингом не завязывает загрузку
# геометрии на направление камеры, только на РАССТОЯНИЕ от игрока: мир
# один раз (при открытии карты) режется на равномерную 2D-сетку ячеек
# по осям X/Z (высота Y внутри ячейки не ограничивается — верхушка
# высокой башни остаётся в той же ячейке, что и её основание), а на
# каждый тик просто берутся все ячейки в радиусе loadRadius от игрока.
# Ни рейкаста, ни направления камеры — только позиция.
CHUNK_CELL_SIZE = 100.0  # студов на сторону ячейки

_chunk_index_cache = {'parsed_id': None, 'index': None}


def get_chunk_index():
    parsed = state.get('parsed')
    if not parsed:
        return {}
    pid = (id(parsed), _scene_version['v'])
    if _chunk_index_cache['parsed_id'] != pid:
        # Крупные объекты дробим (chunk_large_objects, уже есть для
        # .rbxl экспорта) ПЕРЕД раскладкой по ячейкам — иначе стена в
        # 300 студов длиной попадёт только в одну ячейку по своему
        # центру и не найдётся, когда игрок стоит в соседней, хотя
        # физически стена прямо перед ним.
        objs = chunk_large_objects(build_all_scene_objects())
        index = {}
        for o in objs:
            # Полуразмер по X/Z (без учёта поворота — консервативная
            # оценка чуть больше настоящей OBB, зато дешёвая и без
            # риска пропустить ячейку, которую объект реально задевает).
            half_x = math.sqrt(o['sx'] ** 2 + o['sz'] ** 2) * 0.5
            min_cx = int(math.floor((o['px'] - half_x) / CHUNK_CELL_SIZE))
            max_cx = int(math.floor((o['px'] + half_x) / CHUNK_CELL_SIZE))
            min_cz = int(math.floor((o['pz'] - half_x) / CHUNK_CELL_SIZE))
            max_cz = int(math.floor((o['pz'] + half_x) / CHUNK_CELL_SIZE))
            for ccx in range(min_cx, max_cx + 1):
                for ccz in range(min_cz, max_cz + 1):
                    index.setdefault((ccx, ccz), []).append(o)
        _chunk_index_cache.update(parsed_id=pid, index=index)
    return _chunk_index_cache['index']


def gather_objects_in_radius(cx, cy, cz, radius):
    # Круговой (в плане X/Z) отбор объектов вокруг игрока — сетка ячеек
    # используется только как быстрый способ НЕ перебирать все объекты
    # карты (кандидаты берутся из квадрата ячеек, задевающих окружность
    # радиуса radius), фильтрация "входит ли в радиус" — по честной
    # euclidean-дистанции.
    index = get_chunk_index()
    if not index:
        return []
    min_cx = int(math.floor((cx - radius) / CHUNK_CELL_SIZE))
    max_cx = int(math.floor((cx + radius) / CHUNK_CELL_SIZE))
    min_cz = int(math.floor((cz - radius) / CHUNK_CELL_SIZE))
    max_cz = int(math.floor((cz + radius) / CHUNK_CELL_SIZE))
    seen_refs = set()
    result = []
    for ccx in range(min_cx, max_cx + 1):
        for ccz in range(min_cz, max_cz + 1):
            for o in index.get((ccx, ccz), ()):
                if o['ref'] in seen_refs:
                    continue  # объект мог попасть в несколько соседних ячеек
                seen_refs.add(o['ref'])
                d = math.sqrt((o['px'] - cx) ** 2 + (o['py'] - cy) ** 2 + (o['pz'] - cz) ** 2)
                if d <= radius:
                    result.append((d, o))

    # Сортируем НЕ по чистой дистанции, а с поправкой на размер объекта.
    # Без этого, когда общий бюджет (limit/streamCap в api_scene) меньше,
    # чем всего объектов в радиусе, топ забивают ближние мелкие детали
    # (трава, мусор, декор в упор у игрока) — а структурно важная дальняя
    # стена или пол, которые реально нужны для обзора, просто не попадают
    # в отсечку. Крупные объекты получают скидку к своей "эффективной"
    # дистанции (логарифм — чтобы один гигантский terrain-кусок не забил
    # собой весь бюджет монопольно, но обычная стена/пол ощутимо выигрывает
    # у россыпи мелочи на той же дистанции).
    def sort_key(pair):
        d, o = pair
        bounding_radius = math.sqrt(o['sx'] ** 2 + o['sy'] ** 2 + o['sz'] ** 2) * 0.5
        return max(0.0, d - bounding_radius) / (1.0 + math.log1p(bounding_radius))

    result.sort(key=sort_key)
    return result


_scene_build_cache = {'parsed_id': None, 'objs': None}


def _rbxassetid_num(value):
    """'rbxassetid://123' -> '123'. Отсеивает rbxasset://textures/... —
    это встроенные в студию файлы, у них нет числового id и их всё равно
    нельзя утянуть с /api/asset-proxy (см. там же про assetdelivery)."""
    if not value:
        return None
    s = str(value)
    if 'rbxassetid://' not in s:
        return None
    m = _re.search(r'\d+', s)
    return m.group() if m else None


def _asset_url_num(value):
    """Числовой id из 'http://www.roblox.com/asset/?id=123' или 'rbxassetid://123'
    (ShirtTemplate/PantsTemplate хранятся в первом виде)."""
    if not value:
        return None
    s = str(value)
    if 'rbxasset://' in s and 'rbxassetid://' not in s:
        return None
    m = _re.search(r'\d+', s)
    return m.group() if m else None


# Части R6-персонажа, на которые ложится одежда (Shirt/Pants из соседних
# детей той же Model): shirt — торс и руки, pants — торс и ноги
# (в шаблоне 585x559 руки/ноги лежат в одних и тех же прямоугольниках,
# поэтому рубашку на ноги и штаны на руки класть нельзя).
R6_CLOTH_LIMBS = {
    'Torso': ('shirt', 'pants'),
    'Left Arm': ('shirt',), 'Right Arm': ('shirt',),
    'Left Leg': ('pants',), 'Right Leg': ('pants',),
}


def _extract_part_texture_id(ref, cls, props, children_by_parent, all_props, referent_to_class):
    """Ищем ЛЮБОЙ реальный (rbxassetid://) источник картинки для части:
    1) TextureID/Texture прямо на MeshPart,
    2) Texture дочернего Decal,
    3) TextureId дочернего SpecialMesh.
    Первое найденное побеждает — комбинировать несколько текстур на одном
    box-приближении всё равно не получится, это не полноценный UV-меш.

    Возвращает (texture_id, face) — face берём ТОЛЬКО у Decal (его
    свойство Face — на какую грань накладывать, по умолчанию 'Front',
    как в самом Roblox) и только для него: раньше текстура клалась
    ОДНИМ материалом на всю BoxGeometry — то есть на ВСЕ 6 граней сразу
    (дефолтный UV each-face-0..1 у Three.js), а не на одну, как в
    реальном Roblox — отсюда и "плохо легли текстуры" (растянутая
    копия текстуры со всех сторон сразу). Для MeshPart.TextureID/
    SpecialMesh face не возвращаем — они на реальном меше оборачивают
    всю поверхность, а не одну грань, так что "на все грани" тут ближе
    к истине (это по-прежнему лишь box-приближение, не настоящий меш)."""
    if cls == 'MeshPart':
        tid = _rbxassetid_num(props.get('TextureID') or props.get('Texture'))
        if tid:
            return tid, None
    for child in children_by_parent.get(ref, ()):
        child_cls = referent_to_class.get(child)
        if child_cls == 'Decal':
            child_props = all_props.get(child, {})
            tid = _rbxassetid_num(child_props.get('Texture'))
            if tid:
                return tid, (child_props.get('Face') or 'Front')
        elif child_cls == 'SpecialMesh':
            tid = _rbxassetid_num(all_props.get(child, {}).get('TextureId'))
            if tid:
                return tid, None
    return None, None


def _extract_real_mesh_id(ref, cls, props, children_by_parent, all_props, referent_to_class):
    """MeshId для РЕАЛЬНОЙ геометрии — в отличие от shape-эвристики в
    build_all_scene_objects (которая лишь подбирает ближайший ИЗ ФИКСИРОВАННОГО
    НАБОРА примитивов: box/sphere/cylinder/cone/wedge), это отдельный
    кастомный меш, который раньше вообще не подгружался: MeshPart.MeshId
    и SpecialMesh.MeshId (при MeshType.FileMesh, число 5 — единственный
    тип, где MeshId указывает на реальную кастомную геометрию с сервера;
    Cylinder/Sphere/Wedge/Head и т.п. — это встроенные примитивы, у них
    MeshId либо пуст, либо игнорируется настоящим Roblox тоже, никакой
    реальной геометрии подгружать не нужно). Раньше эти MeshId нигде не
    читались для геометрии вообще — FileMesh-меши (BasePart с дочерним
    SpecialMesh, MeshType=5) и любые MeshPart рендерились ТОЛЬКО как
    bounding-box, отсюда и "меши не грузятся"/"кривая развёртка" — текстура
    клеилась на приближение вместо настоящей формы и её настоящих UV."""
    if cls == 'MeshPart':
        mid = _rbxassetid_num(props.get('MeshId') or props.get('MeshID'))
        if mid:
            return mid
    for child in children_by_parent.get(ref, ()):
        if referent_to_class.get(child) == 'SpecialMesh':
            cp = all_props.get(child, {})
            mt = cp.get('MeshType', 0)
            if isinstance(mt, str):
                mt = int(mt) if mt.isdigit() else 0
            if mt == 5:
                mid = _rbxassetid_num(cp.get('MeshId'))
                if mid:
                    return mid
    return None


def build_all_scene_objects():
    # Раньше этот разбор (CFrame/матрицы поворота, поиск SpecialMesh для
    # формы, цвет, Anchored/CanCollide) заново гонялся по ВСЕМ объектам
    # карты на КАЖДЫЙ вызов /api/scene — а стриминг дёргает его каждые
    # ~600мс. На картах в несколько тысяч частей (Castle Warfare) это и
    # была основная причина тормозов: сами raycast/сортировка по факту
    # быстрые, но каждый запрос сначала заново пересобирал ВЕСЬ список
    # объектов с нуля. Карта между открытиями не меняется — кэшируем
    # построенный список по id распарсенной карты, как и get_chunk_index.
    parsed = state.get('parsed')
    if not parsed:
        return []
    pid = (id(parsed), _scene_version['v'])
    if _scene_build_cache['parsed_id'] == pid:
        return _scene_build_cache['objs']

    # ref ребёнка -> ref родителя из parent_map — переворачиваем один раз
    # на всю сборку сцены, а не ищем детей линейным проходом на каждую
    # часть (на картах в тысячи объектов это была бы O(n^2) сборка).
    children_by_parent = {}
    for child_ref, parent_ref in parsed['parent_map'].items():
        children_by_parent.setdefault(parent_ref, []).append(child_ref)

    # MaterialService/MaterialVariant: (имя, BaseMaterial) -> карты. Деталь
    # ссылается на вариант по имени в MaterialVariantSerialized (так
    # перчатки gloveR/gloveL получают свой материал 'main').
    material_variants = {}
    for vref, vcls in parsed['referent_to_class'].items():
        if vcls != 'MaterialVariant':
            continue
        vp = parsed['props'].get(vref, {})
        material_variants[(vp.get('Name'), vp.get('BaseMaterial'))] = {
            'name': vp.get('Name'),
            'colorMap': _asset_url_num(vp.get('ColorMap')),
            'normalMap': _asset_url_num(vp.get('NormalMap')),
            'roughnessMap': _asset_url_num(vp.get('RoughnessMap')),
            'metalnessMap': _asset_url_num(vp.get('MetalnessMap')),
            'studsPerTile': safe_float(vp.get('StudsPerTile', 10.0), 10.0) or 10.0,
        }

    objs = []
    for ref, cls in parsed['referent_to_class'].items():
        if cls not in PART_CLASSES:
            continue
        props = parsed['props'].get(ref, {})
        if props.get('Visible') is False:
            continue

        # Получаем Position
        pos = props.get('Position', {})
        if isinstance(pos, dict):
            px = safe_float(pos.get('x', 0))
            py = safe_float(pos.get('y', 0))
            pz = safe_float(pos.get('z', 0))
        else:
            px = py = pz = 0

        # Получаем CFrame (если он есть, он может переопределить позицию)
        cf = props.get('CFrame', {})
        # Используем CFrame только если он реально содержит позицию или матрицу
        if isinstance(cf, dict) and ('position' in cf or 'matrix' in cf):
            cf_pos = get_pos(cf)
            # Если get_pos вернул не (0,0,0) — берём позицию из CFrame
            if cf_pos != (0.0, 0.0, 0.0):
                px, py, pz = cf_pos
        rot_matrix = get_rot_matrix(cf)

        # Size
        sz = props.get('Size', props.get('size', {}))
        if isinstance(sz, dict):
            sx = max(0.05, safe_float(sz.get('x', 1), 1))
            sy = max(0.05, safe_float(sz.get('y', 1), 1))
            sz_ = max(0.05, safe_float(sz.get('z', 1), 1))
        elif isinstance(sz, (list, tuple)) and len(sz) >= 3:
            sx = max(0.05, safe_float(sz[0], 1))
            sy = max(0.05, safe_float(sz[1], 1))
            sz_ = max(0.05, safe_float(sz[2], 1))
        else:
            sx = sy = sz_ = 1.0

        # Цвет (Color3uint8 из новых файлов, иначе Color3/Color/BrickColor)
        color = get_part_color(props)

        # Прозрачность: раньше не передавалась вообще, и невидимый
        # HumanoidRootPart (Transparency=1, размером с Torso) рисовался
        # сплошным серым блоком поверх персонажа.
        transp = safe_float(props.get('Transparency', 0.0), 0.0)
        opacity = max(0.0, min(1.0, 1.0 - transp))
        # Head, который заменяет аксессуар-голова (у Handle есть свой
        # FaceCenterAttachment, как у Baki_head): в Roblox Head скрывают, иначе
        # он закрывает меш аксессуара (так и было: «Head перекрывает текстуру»).
        if cls == 'Part' and props.get('Name') == 'Head':
            for sib in children_by_parent.get(parsed['parent_map'].get(ref), ()):
                if parsed['referent_to_class'].get(sib) != 'Accessory':
                    continue
                for handle in children_by_parent.get(sib, ()):
                    if parsed['referent_to_class'].get(handle) not in PART_CLASSES:
                        continue
                    if any(parsed['referent_to_class'].get(a) == 'Attachment'
                           and parsed['props'].get(a, {}).get('Name') == 'FaceCenterAttachment'
                           for a in children_by_parent.get(handle, ())):
                        opacity = 0.0

        # Форма: Part.Shape (0=Ball, 1=Block, 2=Cylinder — ось вдоль X),
        # класс SpherePart, либо дочерний SpecialMesh (Enum.MeshType).
        shape = 'sphere' if cls == 'SpherePart' else 'box'
        part_shape = props.get('shape', props.get('Shape'))
        if part_shape == 0:
            shape = 'sphere'
        elif part_shape == 2:
            shape = 'cylinderx'
        CONE_IDS = ['9756362', '1033714', '9887819', 'cone.mesh']
        mesh_scale = None
        mesh_offset = None
        sm = find_special_mesh(ref, children_by_parent, parsed['props'],
                               parsed['referent_to_class'])
        if sm is not None:
            mt = sm.get('MeshType', 0)
            if isinstance(mt, str):
                mt = int(mt) if mt.isdigit() else 0
            mid = str(sm.get('MeshId', ''))
            sc = sm.get('Scale') or {}
            msx = safe_float(sc.get('x', 1), 1) if isinstance(sc, dict) else 1.0
            msy = safe_float(sc.get('y', 1), 1) if isinstance(sc, dict) else 1.0
            msz = safe_float(sc.get('z', 1), 1) if isinstance(sc, dict) else 1.0
            of = sm.get('Offset') or {}
            mox = safe_float(of.get('x', 0), 0) if isinstance(of, dict) else 0.0
            moy = safe_float(of.get('y', 0), 0) if isinstance(of, dict) else 0.0
            moz = safe_float(of.get('z', 0), 0) if isinstance(of, dict) else 0.0
            if any(cid in mid for cid in CONE_IDS):
                shape = 'cone'
            elif mt == 5:
                # FileMesh: реальный размер = родной размер меша * Scale,
                # Size детали НЕ участвует — передаём Scale клиенту.
                mesh_scale = [msx, msy, msz]
            elif mt in MESHTYPE_TO_SHAPE:
                shape = MESHTYPE_TO_SHAPE[mt]
                if shape == 'head':
                    # Head-меш — скруглённый цилиндр; ширина = глубине
                    # (иначе у R6 Head 2x1x1 получилась бы 2.5 в ширину).
                    sx, sy, sz_ = sz_ * msx, sy * msy, sz_ * msz
                else:
                    sx, sy, sz_ = sx * msx, sy * msy, sz_ * msz
            if mox or moy or moz:
                mesh_offset = [mox, moy, moz]
        name = props.get('Name', cls)

        # Enum.Material и MaterialVariant детали
        material = props.get('Material')
        if not isinstance(material, int):
            material = 256
        mvar = None
        mv_name = props.get('MaterialVariantSerialized')
        if mv_name:
            mvar = material_variants.get((mv_name, material))

        # Одежда R6 (Shirt/Pants рядом с частью в той же Model)
        cloth = None
        kinds = R6_CLOTH_LIMBS.get(name) if cls == 'Part' else None
        if kinds:
            shirt_id = pants_id = None
            for sib in children_by_parent.get(parsed['parent_map'].get(ref), ()):
                sc_cls = parsed['referent_to_class'].get(sib)
                if sc_cls == 'Shirt' and 'shirt' in kinds:
                    shirt_id = _asset_url_num(parsed['props'].get(sib, {}).get('ShirtTemplate'))
                elif sc_cls == 'Pants' and 'pants' in kinds:
                    pants_id = _asset_url_num(parsed['props'].get(sib, {}).get('PantsTemplate'))
            if shirt_id or pants_id:
                cloth = {'limb': name, 'shirt': shirt_id, 'pants': pants_id}

        texture_id, texture_face = _extract_part_texture_id(
            ref, cls, props, children_by_parent, parsed['props'],
            parsed['referent_to_class'])
        real_mesh_id = _extract_real_mesh_id(
            ref, cls, props, children_by_parent, parsed['props'],
            parsed['referent_to_class'])

        anchored = props.get('Anchored', False)
        if isinstance(anchored, str):
            anchored = anchored.lower() in ('true', '1')
        cancollide = props.get('CanCollide', True)
        if isinstance(cancollide, str):
            cancollide = cancollide.lower() in ('true', '1')

        objs.append({
            'ref': ref, 'class': cls, 'name': name,
            'shape': shape,
            'px': px, 'py': py, 'pz': pz,
            'sx': sx, 'sy': sy, 'sz': sz_,
            'rot': rot_matrix, 'color': color, 'texture': texture_id,
            'textureFace': texture_face, 'meshId': real_mesh_id,
            'opacity': opacity,
            'meshScale': mesh_scale, 'meshOffset': mesh_offset, 'cloth': cloth,
            'material': material, 'mvar': mvar,
            'anchored': bool(anchored), 'cancollide': bool(cancollide),
        })

    _scene_build_cache.update(parsed_id=pid, objs=objs)
    return objs


def make_scene_objects(cx=None, cy=None, cz=None, r=None, limit=None, chunk=False, points=None):
    parsed = state['parsed']
    if not parsed:
        return [], 0
    objs = build_all_scene_objects()

    if chunk:
        objs = chunk_large_objects(objs)

    # Можно передать несколько точек (не только cx,cy,cz) — дистанция
    # объекта берётся как минимум до любой из них. Используется вторым,
    # points-based путём в api_scene (обычная загрузка сцены редактора);
    # основной Play-стриминг теперь идёт через chunk-based
    # gather_objects_in_radius выше и этот путь не задействует.
    query_points = list(points) if points else (
        [(cx, cy, cz)] if cx is not None and cy is not None and cz is not None else []
    )

    if query_points:
        def dist_to_nearest_point(o):
            # Расстояние до центра занижает приоритет больших объектов:
            # у длинной плиты пола центр может быть в сотне студов от
            # игрока, а край — прямо под ногами. Аппроксимируем нижней
            # оценкой расстояния до объекта — вычитаем полудиагональ
            # его габаритов (радиус описанной сферы) из расстояния до
            # центра. Оценка консервативная (может немного занижать
            # реальную дистанцию до OBB), но гарантированно не отбросит
            # объект, который на самом деле рядом.
            bounding_radius = math.sqrt(
                o['sx'] ** 2 + o['sy'] ** 2 + o['sz'] ** 2) * 0.5
            best = None
            for (qx, qy, qz) in query_points:
                center_d = math.sqrt(
                    (o['px'] - qx) ** 2 + (o['py'] - qy) ** 2 + (o['pz'] - qz) ** 2)
                d = max(0.0, center_d - bounding_radius)
                if best is None or d < best:
                    best = d
            return best

        if r is not None:
            objs = [o for o in objs if dist_to_nearest_point(o) <= r]
        objs.sort(key=dist_to_nearest_point)

    total = len(objs)
    if limit is not None:
        objs = objs[:limit]
    return objs, total


flask_app = Flask(__name__)

# Откуда качать, если файла ещё нет локально — тот же список, что в
# setup_termux.sh. Автозагрузка ниже делает сам setup_termux.sh не
# обязательным: сервер докачивает недостающее по требованию сам.
VENDOR_SOURCES = {
    # CodeMirror 5 (+ addon'ы для автодополнения) убраны — редактор скриптов
    # теперь на CodeMirror 6, единым бандлом (см. cm6-bundle.min.js ниже):
    # он же честно работает с мобильными клавиатурами, чего CM5 не умел.
    'three.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'MTLLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js',
    'OBJLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js',
    'cannon.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js',
    'fengari-web.js': 'https://cdn.jsdelivr.net/npm/fengari-web@0.1.4/dist/fengari-web.js',
    # cm6-bundle.min.js — НЕ публичная CDN-библиотека, а свой собственный
    # сборённый rollup'ом файл (см. entry.mjs/rollup.config.mjs в корне
    # репозитория — оттуда его можно пересобрать заново: `npm install
    # @codemirror/state @codemirror/view @codemirror/commands
    # @codemirror/language @codemirror/autocomplete @codemirror/legacy-modes
    # @codemirror/theme-one-dark @codemirror/search @lezer/highlight rollup
    # @rollup/plugin-node-resolve @rollup/plugin-terser && npx rollup -c`).
    # У такого файла нет готового публичного CDN — качаем его из СВОЕГО ЖЕ
    # репозитория на GitHub, тем же простым HTTP GET, что и все остальные
    # vendor-файлы здесь. Для этого сам файл должен быть закоммичен в репо
    # по пути vendor/cm6-bundle.min.js — если ссылка ниже не подходит
    # (например, репозиторий переименован/перенесён), поправьте URL.
    'cm6-bundle.min.js': 'https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/vendor/cm6-bundle.min.js',
}
    

def _download_vendor_file(fn):
    """Качает fn с CDN прямо в VENDOR_DIR. True — успех (файл на диске)."""
    url = VENDOR_SOURCES.get(fn)
    if not url:
        return False
    try:
        VENDOR_DIR.mkdir(parents=True, exist_ok=True)
        req = _req.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with _req.urlopen(req, timeout=15) as resp:
            data = resp.read()
        # Пишем во временный файл и переименовываем — если параллельный
        # запрос на тот же файл долетит одновременно, никто не увидит
        # частично записанный .js/.css.
        tmp = VENDOR_DIR / (fn + '.part')
        tmp.write_bytes(data)
        tmp.replace(VENDOR_DIR / fn)
        print(f'[RbxStudio] vendor: скачал {fn} ({len(data)} байт)')
        return True
    except (_urlerr.URLError, _urlerr.HTTPError, OSError, TimeoutError) as e:
        print(f'[RbxStudio] vendor: не смог скачать {fn}: {e}')
        return False


@flask_app.route('/vendor/<path:fn>')
def vendor_files(fn):
    # Локальные копии CodeMirror/Three.js/Cannon.js/fengari.
    # index.html грузит их относительным путём 'vendor/...'; если файла
    # ещё нет на диске (первый запуск, setup_termux.sh не запускали),
    # качаем его сюда же по требованию — дальше все запуски офлайн,
    # без сети вообще, потому что файл уже лежит в VENDOR_DIR.
    path = VENDOR_DIR / fn
    if not path.exists():
        if not _download_vendor_file(fn):
            return '', 404
    return send_from_directory(str(VENDOR_DIR), fn)


@flask_app.route('/icons/<path:fn>')
def serve_icon(fn):
    if ICONS_DIR.exists():
        return send_from_directory(str(ICONS_DIR), fn)
    return '', 404


@flask_app.route('/api/open', methods=['POST'])
def api_open():
    path = (request.json or {}).get('path', '')
    try:
        parsed = parse_rbxl(path)
        state['parsed'] = parsed
        state['file_path'] = path
        return jsonify({'ok': True, 'count': len(parsed['referent_to_class'])})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@flask_app.route('/api/open/upload', methods=['POST'])
def api_open_upload():
    """Открытие .rbxl/.rbxlx, выбранного через ОБЫЧНЫЙ системный файловый
    менеджер (<input type=file> на фронте, см. pickRbxlFileForOpen() в
    index.html) — используется везде, кроме Android-APK с SAF-мостом (там
    Kotlin уже кладёт файл в приватное хранилище приложения и передаёт
    сюда обычный /api/open реальный путь на диске).

    В отличие от /api/open, здесь путь на диске СЕРВЕРА для выбранного
    пользователем файла в принципе не существует — браузер отдаёт только
    БАЙТЫ (это касается и десктопа: сервер и вкладка браузера физически
    не обязаны быть одной машиной). Поэтому сохраняем во временный файл
    и парсим его как обычно."""
    import tempfile

    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'Файл не передан'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'ok': False, 'error': 'Имя файла пустое'}), 400

    suffix = Path(file.filename).suffix or '.rbxl'
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Не удалось сохранить файл: {e}'}), 500

    try:
        parsed = parse_rbxl(tmp_path)
        state['parsed'] = parsed
        # Реального пути на диске пользователя у нас нет (временный файл
        # сейчас будет удалён) — оставляем file_path пустым, чтобы Ctrl+S/
        # saveFile() сам открыл "Сохранить как" вместо тихой записи в
        # исчезнувший temp-файл.
        state['file_path'] = None
        return jsonify({
            'ok': True,
            'count': len(parsed['referent_to_class']),
            'name': file.filename,
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@flask_app.route('/api/new', methods=['POST'])
def api_new():
    """Создаёт пустую сцену в памяти сервера (без файла на диске) — набор
    стандартных сервисов Roblox верхнего уровня, как в новом плейсе.
    Нужно, чтобы фичи вроде импорта Instance (например, 3D-аватара)
    работали даже без предварительно открытого .rbxl — раньше PUT
    /api/instance молча отваливался с ok:false, если state['parsed']
    был None, и объект оставался только визуальным в вьюпорте, не
    попадая ни в Explorer, ни в сохраняемый файл. save_rbxl умеет
    полностью пересобрать бинарник даже без _raw_chunks/_raw_data
    (см. ветку "с нуля" в save_rbxl), так что Save/Save As после этого
    работает как обычно — путь просто нужно будет выбрать при сохранении."""
    services = [
        'Workspace', 'Lighting', 'ReplicatedStorage', 'ReplicatedFirst',
        'ServerScriptService', 'ServerStorage', 'StarterGui', 'StarterPack',
        'StarterPlayer', 'SoundService', 'Players', 'Teams', 'Chat',
        'TextChatService',
    ]
    referent_to_class = {}
    parent_map = {}
    props = {}
    for i, cls in enumerate(services, start=1):
        referent_to_class[i] = cls
        parent_map[i] = -1
        props[i] = {'Name': cls}

    state['parsed'] = {
        'referent_to_class': referent_to_class,
        'parent_map': parent_map,
        'props': props,
        'class_id_to_name': {},
        'class_id_to_referents': {},
        'skipped_prop_chunks': 0,
        'service_refs': set(referent_to_class),  # все верхнеуровневые — сервисы
        '_modified': True,
        # Намеренно НЕ добавляем '_raw_chunks'/'_raw_data' — их отсутствие
        # заставляет save_rbxl собирать бинарник с нуля из
        # referent_to_class/parent_map/props вместо попытки переиспользовать
        # чужие сырые чанки.
    }
    state['file_path'] = None
    return jsonify({'ok': True, 'count': len(referent_to_class)})


@flask_app.route('/api/all_instances')
def api_all_instances():
    # Плоский СЫРОЙ список ВСЕХ инстансов карты — ref/class/name/parent, без
    # фильтрации HIDDEN-классов, без ограничения глубины и без вложенной
    # структуры children (в отличие от /api/tree, который строит именно то,
    # что рисует Explorer, и намеренно урезан для этого).
    #
    # Lua-мосту (см. index.html, startLuaScripts) нужна ПОЛНАЯ картина
    # иерархии — script.Parent должен работать для любого скрипта, даже
    # если он вложен внутрь чего-то, что Explorer прячет. Раньше Lua брал
    # родителя из того же дерева, что и Explorer (/api/tree), и любой
    # скрипт под отфильтрованной веткой получал Parent=nil без единой
    # реальной причины на стороне самого скрипта.
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    r2c = parsed['referent_to_class']
    pm = parsed['parent_map']
    pr = parsed['props']
    children_by_parent = {}
    for ref, parent_ref in pm.items():
        children_by_parent.setdefault(parent_ref, []).append(ref)
    out = []
    for ref, cls in r2c.items():
        name = pr.get(ref, {}).get('Name', cls)
        item = {'ref': ref, 'cls': cls, 'name': name, 'parent': pm.get(ref, -1)}
        if cls == 'Sound':
            # SoundId/Volume/Looped — заданные ПРЯМО В ФАЙЛЕ (а не через
            # Instance.new(...).SoundId = ... из Lua) звуки. Раньше сюда
            # не долетали: Lua-мост видел только cls/name/parent, поэтому
            # реальный HTMLAudioElement (см. getOrCreateSoundEl в
            # index.html) никогда не получал src для звуков, уже лежащих
            # в карте при загрузке — audio.src оставался пустым, даже
            # если Sound:Play() честно вызывался.
            sp = pr.get(ref, {})
            item['soundId'] = sp.get('SoundId', '')
            item['volume'] = sp.get('Volume', 0.5)
            item['looped'] = sp.get('Looped', False)
            # PlaybackSpeed — то же самое "задано прямо в файле, ни один
            # скрипт этого не трогает" — что и Octave ниже: FNF-карты с
            # готовым "sped up"-вариантом трека (PlaybackSpeed=2.0 у
            # нескольких твоих Sound) звучали на обычной скорости, потому
            # что раньше сюда попадали только soundId/volume/looped.
            ps = sp.get('PlaybackSpeed', 1.0)
            if ps != 1.0:
                item['playbackSpeed'] = ps
            # PitchShiftSoundEffect — НАСТОЯЩИЙ Roblox-механизм питча (не
            # устаревшее скалярное Sound.Pitch): отдельный дочерний
            # инстанс с Octave (множитель скорости = 2^Octave). Раньше
            # нигде не читался вообще — FNF-карты с "sped up"/замедленными
            # вариантами трека (Octave задан ПРЯМО в файле, без единой
            # строчки скрипта) звучали на обычной скорости, потому что
            # эффект просто никак не подключался к реальному <audio>.
            for child_ref in children_by_parent.get(ref, ()):
                if r2c.get(child_ref) == 'PitchShiftSoundEffect':
                    cp = pr.get(child_ref, {})
                    if cp.get('Enabled', True):
                        item['pitchOctave'] = cp.get('Octave', 0.0)
                    break
        out.append(item)
    return jsonify({'ok': True, 'instances': out})


@flask_app.route('/api/scripts')
def api_scripts():
    # Отдаёт все Script/LocalScript с исходником — используется Lua-рантаймом
    # в Play (см. index.html, startLuaScripts/fengari) для запуска скриптов
    # одним запросом, а не по одному через /api/instance/<ref> на каждый.
    # ModuleScript тоже отдаём (поле 'runnable': False) — сами они НЕ
    # запускаются автоматически (как и в настоящем Roblox), но их исходник
    # нужен фронтенду заранее, чтобы require(moduleScriptInstance) мог
    # скомпилировать/выполнить их по требованию (см. __require_module в
    # index.html). Раньше ModuleScript сюда не входил вообще, и require()
    # был не реализован — использовался голый require() из стандартной
    # библиотеки Lua ("bad argument #1 to 'require' (string expected, got
    # table)", поскольку скрипты зовут require(instance), а не
    # require("имя_модуля")).
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    r2c = parsed['referent_to_class']
    pm = parsed['parent_map']
    pr = parsed['props']
    out = []
    for ref, cls in r2c.items():
        if cls not in ('Script', 'LocalScript', 'ModuleScript'):
            continue
        props = pr.get(ref, {})
        enabled = props.get('Enabled', True)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ('true', '1')
        if cls != 'ModuleScript' and not enabled:
            continue
        out.append({
            'ref': ref, 'cls': cls,
            'name': props.get('Name', cls),
            'source': props.get('Source', '') or '',
            'parent': pm.get(ref, -1),
            'runnable': cls in ('Script', 'LocalScript'),
            # 'server' для Script, 'client' для LocalScript — см.
            # SCRIPT_SIDE выше. Фронтенд использует это только для
            # отображения (бейдж в Output/Properties), не для настоящей
            # сетевой изоляции.
            'side': SCRIPT_SIDE.get(cls, 'server'),
        })
    return jsonify({'ok': True, 'scripts': out})


@flask_app.route('/api/gui_tree')
def api_gui_tree():
    # Плоский список всех GUI-инстансов (ScreenGui и его потомки —
    # Frame/TextLabel/TextButton/TextBox/ImageLabel/ImageButton) с узким
    # набором свойств (GUI_PROPS), которых достаточно, чтобы фронтенд
    # (buildGuiOverlay в index.html) собрал DOM-дерево оверлея поверх
    # 3D-вьюпорта в Play. По духу — то же самое, что /api/scripts делает
    # для Script/LocalScript: один запрос вместо N обращений к
    # /api/instance/<ref> на каждый GUI-объект.
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    r2c = parsed['referent_to_class']
    pm = parsed['parent_map']
    pr = parsed['props']

    out = []
    for ref, cls in r2c.items():
        if cls not in GUI_CLASSES:
            continue
        props = pr.get(ref, {})
        enabled = props.get('Enabled', True)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ('true', '1')
        item = {
            'ref': ref, 'cls': cls,
            'parent': pm.get(ref, -1),
            'enabled': enabled,
        }
        for pname in GUI_PROPS:
            if pname in props:
                item[pname] = props[pname]
        out.append(item)
    return jsonify({'ok': True, 'elements': out})


@flask_app.route('/api/tree')
def api_tree():
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'Файл не загружен'}), 400
    r2c = parsed['referent_to_class']
    pm = parsed['parent_map']
    pr = parsed['props']
    children_of = {}
    for child, parent in pm.items():
        children_of.setdefault(parent, []).append(child)

    def node(ref, depth=0, vis=None):
        if vis is None:
            vis = set()
        if ref in vis or depth > 60:
            return None
        vis.add(ref)
        cls = r2c.get(ref, '?')

        # Пропускаем скрытые классы
        if cls in HIDDEN:
            return None

        name = pr.get(ref, {}).get('Name', cls)

        # Собираем детей (рекурсивно)
        kids = []
        for c in sorted(children_of.get(ref, [])):
            # Создаём копию vis для каждой ветки
            child_node = node(c, depth + 1, vis.copy())
            if child_node:
                kids.append(child_node)

        return {
            'ref': ref,
            'cls': cls,
            'name': name,
            'icon': icon_src(cls),
            'children': kids
        }

    # Корневые элементы (parent = -1 или отсутствует в parent_map)
    roots = []
    # Находим все ref, у которых parent = -1 или parent отсутствует в r2c
    root_refs = set()
    for ref in r2c:
        parent = pm.get(ref, -1)
        if parent == -1 or parent not in r2c:
            root_refs.add(ref)

    # Также добавляем явно указанных детей -1
    for ref in children_of.get(-1, []):
        root_refs.add(ref)

    for ref in sorted(root_refs):
        cls = r2c.get(ref, '?')
        if cls not in HIDDEN:
            n = node(ref)
            if n:
                roots.append(n)

    return jsonify({'ok': True, 'tree': roots})


@flask_app.route('/api/scene', methods=['GET', 'POST'])
def api_scene():
    # POST с телом {cx,cy,cz,load_radius,limit,chunk} — используется
    # Play-стримингом (см. index.html, refreshStreamedGeometry): просто
    # "все объекты в радиусе load_radius от игрока", без рейкаста и без
    # направления камеры (см. get_chunk_index/gather_objects_in_radius
    # выше — chunk-based подход, как в Minecraft/UE5 World Partition).
    # GET с query-параметрами остаётся как был для остальных вызовов
    # (обычная загрузка сцены редактора) и для pts= из более старых версий.
    body = request.get_json(silent=True) if request.method == 'POST' else None
    body = body or {}

    def num(name, cast=float):
        if name in body:
            try:
                return cast(body[name])
            except (TypeError, ValueError):
                return None
        return request.args.get(name, type=cast)

    cx = num('cx')
    cy = num('cy')
    cz = num('cz')
    r = num('r')
    limit = num('limit', int)
    if 'chunk' in body:
        chunk = bool(body['chunk'])
    else:
        chunk = request.args.get('chunk', type=int, default=0) == 1

    load_radius = num('load_radius')
    if load_radius is not None and cx is not None and cy is not None and cz is not None:
        # Chunk-based путь: быстрый отбор кандидатов через сетку ячеек
        # (gather_objects_in_radius), уже отсортированных по дистанции —
        # берём просто ближайшие limit.
        by_dist = gather_objects_in_radius(cx, cy, cz, load_radius)
        objs = [o for _, o in by_dist]
        total = len(objs)
        if chunk:
            objs = chunk_large_objects(objs)
            # chunk_large_objects дробит крупные объекты уже ПОСЛЕ отбора
            # по радиусу здесь (в отличие от get_chunk_index, где дробление
            # идёт до раскладки по ячейкам) — порядок по дистанции при этом
            # не портится: части одного большого объекта остаются рядом
            # друг с другом в списке.
        if limit is not None:
            objs = objs[:limit]
        return jsonify({'ok': True, 'objects': objs, 'total': total})

    # Старый points-based путь (используется остальными вызовами —
    # обычная загрузка сцены в редакторе, где рейкаст/радиус не нужны).
    points = []
    if cx is not None and cy is not None and cz is not None:
        points.append((cx, cy, cz))

    # pts=x,y,z;x,y,z;... — обратная совместимость.
    pts_raw = body.get('pts') if 'pts' in body else request.args.get('pts')
    if pts_raw:
        groups = pts_raw if isinstance(pts_raw, list) else pts_raw.split(';')
        for group in groups:
            parts = group.split(',') if isinstance(group, str) else group
            if len(parts) == 3:
                try:
                    points.append((float(parts[0]), float(parts[1]), float(parts[2])))
                except (ValueError, TypeError):
                    pass

    objs, total = make_scene_objects(cx, cy, cz, r, limit, chunk=chunk, points=points or None)
    return jsonify({'ok': True, 'objects': objs, 'total': total})


@flask_app.route('/api/spawn')
def api_spawn_point():
    # Отдельная ручка, не зависящая от того, какой кусок сцены сейчас
    # подгружен в редакторе — нужна, чтобы Play всегда находил точку
    # спавна, даже если она не попала в текущий LOD-радиус камеры.
    #
    # На карте может быть несколько SpawnLocation (командные спавны и
    # т.п.). Предпочитаем Anchored=true — незакреплённый спавн часто
    # висит в воздухе (декоративный/на движущейся платформе) и роняет
    # игрока в пустоту, если он выбран первым просто по порядку в файле.
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'nothing open'}), 400

    candidates = []
    for ref, cls in parsed['referent_to_class'].items():
        if cls != 'SpawnLocation':
            continue
        props = parsed['props'].get(ref, {})
        if props.get('Visible') is False:
            continue
        cf = props.get('CFrame', {})
        px, py, pz = get_pos(cf)
        sz = props.get('Size', props.get('size', {}))
        sy = safe_float(sz.get('y', 1), 1) if isinstance(sz, dict) else 1
        anchored = props.get('Anchored', False)
        if isinstance(anchored, str):
            anchored = anchored.lower() in ('true', '1')
        candidates.append((bool(anchored), px, py + sy * 0.5, pz))

    if not candidates:
        return jsonify({'ok': False, 'error': 'no SpawnLocation in scene'})

    candidates.sort(key=lambda c: not c[0])  # anchored=True первыми
    _, x, y, z = candidates[0]
    return jsonify({'ok': True, 'x': x, 'y': y, 'z': z, 'anchored': candidates[0][0]})


@flask_app.route('/api/instance/<int:ref>')
def api_get_instance(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    cls = parsed['referent_to_class'].get(ref, '?')
    props = {k: serialize_prop(v)
             for k, v in parsed['props'].get(ref, {}).items()}
    return jsonify({
        'ok': True, 'ref': ref, 'cls': cls,
        'icon': icon_src(cls), 'props': props,
        'parent': parsed['parent_map'].get(ref, -1),
    })


def _rbx_post_json(url, data):
    """Отправляет POST-запрос с JSON-телом и возвращает распарсенный JSON."""
    req = _req.Request(url, data=data, headers=_roblox_headers())
    req.add_header('Content-Type', 'application/json')
    try:
        with _req.urlopen(req, timeout=20) as resp:
            raw = _rbx_maybe_gunzip(resp.read())
            raw_text = raw.decode('utf-8', 'replace')
        return json.loads(raw_text)
    except _urlerr.HTTPError as e:
        body = _rbx_maybe_gunzip(e.read()).decode('utf-8', 'replace')[:300]
        raise RuntimeError(f'HTTP {e.code} от Roblox: {body}')
    except Exception as e:
        raise RuntimeError(str(e))


@flask_app.route('/api/roblox/userid', methods=['GET'])
def api_roblox_userid():
    """Получить User ID по никнейму через официальный API Roblox.
    Требуется наличие .ROBLOSECURITY (авторизация)."""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'ok': False, 'error': 'Missing username'}), 400

    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': 'Сначала войдите в аккаунт Roblox.'}), 401

    try:
        # Используем официальный эндпоинт Roblox
        resp = _rbx_post_json(
            'https://users.roblox.com/v1/usernames/users',
            json.dumps({'usernames': [username], 'excludeBannedUsers': False}).encode(
                'utf-8')
        )
        # _rbx_get_json по умолчанию делает GET. Нам нужно POST.
        # Придётся немного изменить _rbx_get_json или написать отдельную функцию.
        # Давайте перепишем _rbx_get_json, чтобы поддерживать POST.
        # Или создадим новую функцию _rbx_post_json.
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502

    # Обработка ответа
    if isinstance(resp, dict) and resp.get('data') and len(resp['data']) > 0:
        user_data = resp['data'][0]
        return jsonify({
            'ok': True,
            'id': user_data['id'],
            'displayName': user_data.get('displayName', ''),
            'name': user_data.get('name', '')
        })
    else:
        return jsonify({'ok': False, 'error': 'Пользователь не найден'}), 404


def build_rot_matrix_from_deg(rx_deg, ry_deg, rz_deg):
    """Строит 3x3-матрицу поворота (row-major, 9 элементов) из углов в
    градусах — той же конвенцией, что get_rot_matrix() и разложение в
    rbxl_parser.py (R = Rx(rx) * Ry(ry) * Rz(rz)), чтобы Rotation и CFrame
    оставались согласованы в обе стороны."""
    rx, ry, rz = math.radians(rx_deg), math.radians(
        ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    return [
        cy*cz, -cy*sz, sy,
        sx*sy*cz+cx*sz, -sx*sy*sz+cx*cz, -sx*cy,
        -cx*sy*cz+sx*sz, cx*sy*sz+sx*cz, cx*cy
    ]


@flask_app.route('/api/instance/<int:ref>', methods=['POST'])
def api_set_prop(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    data = request.json or {}
    prop = data.get('prop')
    val = data.get('value')
    if prop is not None and ref in parsed['referent_to_class']:
        props = parsed['props'].setdefault(ref, {})
        props[prop] = val
        parsed['_modified'] = True
        bump_scene_version()

        # CFrame в make_scene_objects имеет приоритет над Position/Rotation —
        # если объект уже содержит CFrame, правка этих полей визуально
        # ничего не меняла (сцена всё равно бралась из старого CFrame).
        # Синхронизируем оба случая.
        if prop == 'Position' and isinstance(val, dict):
            x = safe_float(val.get('x', 0))
            y = safe_float(val.get('y', 0))
            z = safe_float(val.get('z', 0))
            cf = props.get('CFrame')
            if isinstance(cf, dict) and isinstance(cf.get('matrix'), (list, tuple)) and len(cf['matrix']) >= 12:
                mat = list(cf['matrix'])
                mat[3], mat[7], mat[11] = x, y, z
                cf['matrix'] = mat
            elif isinstance(cf, dict) and 'position' in cf:
                cf['position'] = {'x': x, 'y': y, 'z': z}
            else:
                # CFrame отсутствовал — создаём с единичным поворотом
                props['CFrame'] = {
                    'matrix': [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z]
                }
        elif prop == 'Rotation' and isinstance(val, dict):
            rx = safe_float(val.get('x', 0))
            ry = safe_float(val.get('y', 0))
            rz = safe_float(val.get('z', 0))
            r00, r01, r02, r10, r11, r12, r20, r21, r22 = build_rot_matrix_from_deg(
                rx, ry, rz)
            cf = props.get('CFrame')
            if isinstance(cf, dict) and isinstance(cf.get('matrix'), (list, tuple)) and len(cf['matrix']) >= 12:
                mat = list(cf['matrix'])
                px, py, pz = mat[3], mat[7], mat[11]
            else:
                pos = props.get('Position', {})
                px = safe_float(pos.get('x', 0)) if isinstance(
                    pos, dict) else 0
                py = safe_float(pos.get('y', 0)) if isinstance(
                    pos, dict) else 0
                pz = safe_float(pos.get('z', 0)) if isinstance(
                    pos, dict) else 0
            props['CFrame'] = {
                'matrix': [r00, r01, r02, px, r10, r11, r12, py, r20, r21, r22, pz]
            }
    return jsonify({'ok': True})


@flask_app.route('/api/instance', methods=['PUT'])
def api_add():
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    data = request.json or {}
    cls = data.get('class', 'Part')
    name = data.get('name', 'New' + cls)
    parent = data.get('parent', -1)
    new_ref = max(parsed['referent_to_class'].keys(), default=0) + 1
    parsed['referent_to_class'][new_ref] = cls
    parsed['parent_map'][new_ref] = parent

    props = {'Name': name}
    if cls in PART_CLASSES:
        # Без начальных Position/Size/CFrame новый объект оказывается
        # в (0,0,0) с нулевым/дефолтным размером и накладывается на
        # другие части — визуально выглядит как "не появился".
        px, py, pz = data.get('px', 0), data.get('py', 5), data.get('pz', 0)
        sx, sy, sz = data.get('sx', 4), data.get('sy', 1), data.get('sz', 2)
        props['Position'] = {'x': safe_float(
            px), 'y': safe_float(py), 'z': safe_float(pz)}
        props['Rotation'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        props['Size'] = {'x': safe_float(sx, 4), 'y': safe_float(
            sy, 1), 'z': safe_float(sz, 2)}
        props['CFrame'] = {
            'matrix': [1, 0, 0, safe_float(px), 0, 1, 0, safe_float(py, 5), 0, 0, 1, safe_float(pz)]
        }
        props['Anchored'] = data.get('anchored', True)
        props['CanCollide'] = data.get('cancollide', True)
        props['Color'] = data.get('color', {'r': 0.63, 'g': 0.63, 'b': 0.63})

    parsed['props'][new_ref] = props
    parsed['_modified'] = True
    bump_scene_version()
    return jsonify({'ok': True, 'ref': new_ref})


@flask_app.route('/api/instance/<int:ref>', methods=['DELETE'])
def api_delete(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    for d in ('referent_to_class', 'parent_map', 'props'):
        parsed[d].pop(ref, None)
    parsed['_modified'] = True
    bump_scene_version()
    return jsonify({'ok': True})


@flask_app.route('/api/save', methods=['POST'])
def api_save():
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'Нет данных'}), 400
    data = request.json or {}
    path = data.get('path') or state['file_path']
    if not path:
        return jsonify({'ok': False, 'error': 'Нет пути'}), 400
    try:
        p = Path(path)
        ext = p.suffix.lower()
        if ext in ('.rbxl', '.rbxlx'):
            save_rbxl(parsed, str(p))
            state['file_path'] = str(p)
            return jsonify({'ok': True, 'path': str(p)})
        else:
            out = {}
            for ref, props in parsed['props'].items():
                out[str(ref)] = {k: serialize_prop(v)
                                 for k, v in props.items()}
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({
                    'referent_to_class': {str(k): v for k, v in parsed['referent_to_class'].items()},
                    'parent_map':        {str(k): v for k, v in parsed['parent_map'].items()},
                    'props':             out,
                }, f, indent=2, ensure_ascii=False)
            state['file_path'] = str(p)
            return jsonify({'ok': True, 'path': str(p)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/publish', methods=['POST'])
def api_publish():
    if not state['file_path']:
        return jsonify({'ok': False, 'error': 'Файл не загружен'}), 400
    data = request.json or {}
    try:
        status, text = publish_place(
            state['file_path'],
            data.get('universe_id', ''),
            data.get('place_id', ''),
            data.get('api_key', ''),
            data.get('version_type', 'Published'),
        )
        return jsonify({'ok': status == 200, 'status': status, 'text': text})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/save/download')
def api_save_download():
    """Сохранение "как" через обычную браузерную загрузку (нативный
    менеджер загрузок ОС/браузера) вместо самописного проводника по
    файловой системе СЕРВЕРА (см. /api/browse ниже) — тот путь вообще
    не имел смысла всякий раз, когда сервер и вкладка браузера физически
    не одна машина (в первую очередь — мобильный кейс). Пишем во
    временный файл на диске сервера (как уже делает Android-ветка
    сохранения через SAF), читаем байты в память и отдаём как
    attachment, временный файл сразу удаляем."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'Нет данных'}), 400

    name = os.path.basename(request.args.get('name') or 'place.rbxl') or 'place.rbxl'
    ext = Path(name).suffix.lower()
    if ext not in ('.rbxl', '.rbxlx'):
        name += '.rbxl'
        ext = '.rbxl'

    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    try:
        save_rbxl(parsed, tmp_path)
        with open(tmp_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return Response(
        data,
        mimetype='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename="{name}"'},
    )


def _rbxm_name(raw):
    name = os.path.basename(raw or '') or 'model.rbxm'
    if Path(name).suffix.lower() != '.rbxm':
        name += '.rbxm'
    return name


@flask_app.route('/api/export/rbxm', methods=['GET', 'POST'])
def api_export_rbxm():
    """Экспорт выбранных объектов (со всеми потомками) в бинарный .rbxm.

    GET  ?refs=1,2,3&name=model.rbxm — обычная браузерная загрузка (как
         /api/save/download: blob-URL в Android WebView не работают).
    POST {refs: [...], path: "..."} — запись файла на диск сервера; так
         Android кладёт файл в приватную папку перед экспортом через SAF."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'Нет данных'}), 400
    if request.method == 'POST':
        body = request.json or {}
        raw_refs = body.get('refs') or []
    else:
        raw_refs = [x for x in (request.args.get('refs') or '').split(',') if x.strip()]
    try:
        refs = [int(x) for x in raw_refs][:20000]
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Некорректный список объектов'}), 400
    try:
        data, count, warnings = export_rbxm(parsed, refs)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500

    if request.method == 'POST':
        path = (request.json or {}).get('path')
        if not path:
            return jsonify({'ok': False, 'error': 'Нет пути'}), 400
        try:
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500
        return jsonify({'ok': True, 'path': path, 'count': count, 'warnings': warnings})

    name = _rbxm_name(request.args.get('name'))
    return Response(
        data,
        mimetype='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename="{name}"',
            'X-Rbxm-Count': str(count),
            'X-Rbxm-Warnings': quote(json.dumps(warnings, ensure_ascii=False)),
        },
    )


def _finish_rbxm_import(path, parent):
    if not state['parsed']:
        api_new()   # нечего открывать — импортируем в новую пустую сцену
    try:
        roots, count, warnings = import_rbxm(state['parsed'], path, parent)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500
    bump_scene_version()
    return jsonify({'ok': True, 'count': count, 'roots': roots, 'warnings': warnings})


@flask_app.route('/api/import/rbxm', methods=['POST'])
def api_import_rbxm():
    """Импорт .rbxm по пути на диске сервера (Android: Kotlin уже скопировал
    выбранный через SAF файл в приватную папку приложения)."""
    data = request.json or {}
    path = data.get('path')
    if not path or not os.path.isfile(path):
        return jsonify({'ok': False, 'error': 'Файл не найден'}), 400
    parent = data.get('parent')
    return _finish_rbxm_import(path, int(parent) if parent is not None else None)


@flask_app.route('/api/import/rbxm/upload', methods=['POST'])
def api_import_rbxm_upload():
    """Импорт .rbxm, выбранного обычным <input type=file> (см. /api/open/upload)."""
    import tempfile
    if 'file' not in request.files or not request.files['file'].filename:
        return jsonify({'ok': False, 'error': 'Файл не передан'}), 400
    parent = request.form.get('parent')
    try:
        parent = int(parent) if parent not in (None, '', 'null') else None
    except ValueError:
        return jsonify({'ok': False, 'error': 'Некорректный родитель'}), 400
    try:
        with tempfile.NamedTemporaryFile(suffix='.rbxm', delete=False) as tmp:
            request.files['file'].save(tmp.name)
            tmp_path = tmp.name
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Не удалось сохранить файл: {e}'}), 500
    try:
        return _finish_rbxm_import(tmp_path, parent)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@flask_app.route('/api/browse')
def api_browse():
    path = request.args.get('path', str(Path.home()))
    try:
        p = Path(path)
        if not p.exists():
            p = Path.home()
        entries = []
        if p.parent != p:
            entries.append({'name': '..', 'path': str(
                p.parent), 'type': 'dir', 'size': 0})
        for item in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            try:
                is_dir = item.is_dir()
                ext = item.suffix.lower()
                entries.append({
                    'name': item.name,
                    'path': str(item),
                    'type': 'dir' if is_dir else ext.lstrip('.') or 'file',
                    'size': 0 if is_dir else item.stat().st_size,
                })
            except Exception:
                pass
        return jsonify({'ok': True, 'path': str(p), 'entries': entries})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


def _roblox_auth_file():
    """Путь к файлу с сохранённой .ROBLOSECURITY. На Android это
    RSW_DATA_DIR/roblox_auth.json (см. bridge_launcher.py и
    MainActivity.kt: RobloxLoginActivity пишет туда после логина). Вне
    Android (обычный запуск python app.py) используем локальную папку —
    так десктоп-версия тоже может подхватить куку, если её положить туда
    вручную."""
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    return Path(data_dir) / 'roblox_auth.json'


def _roblox_cookie():
    """Возвращает строку куки '.ROBLOSECURITY=...' или None, если логина
    ещё не было / файл повреждён."""
    p = _roblox_auth_file()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        cookie = data.get('cookie')
        return cookie if cookie else None
    except Exception:
        return None


ROBLOX_HEADERS_BASE = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/plain, */*',
    # КРИТИЧНО: без этого сервер может прислать тело в gzip, а urllib
    # НЕ распаковывает его автоматически (это делают только requests/
    # браузеры) — итог: JSON и даже сами файлы модели читались как сырые
    # сжатые байты и превращались в нечитаемую "бинарную кашу" вместо
    # текста/картинок. Проще всего попросить сервер вообще не сжимать.
    'Accept-Encoding': 'identity',
}


def _roblox_headers():
    headers = dict(ROBLOX_HEADERS_BASE)
    cookie = _roblox_cookie()
    if cookie:
        headers['Cookie'] = cookie
    return headers


@flask_app.route('/api/roblox/auth-status')
def api_roblox_auth_status():
    return jsonify({'ok': True, 'loggedIn': _roblox_cookie() is not None})


@flask_app.route('/api/roblox/logout', methods=['POST'])
def api_roblox_logout():
    p = _roblox_auth_file()
    try:
        if p.exists():
            p.unlink()
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/roblox/avatar3d/import-local-upload', methods=['POST'])
def api_roblox_avatar3d_import_local_upload():
    import zipfile
    import base64 as _b64

    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': 'Файл не передан'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'ok': False, 'error': 'Имя файла пустое'}), 400

    try:
        # Читаем содержимое загруженного файла в память
        zip_bytes = file.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            names = zf.namelist()
            obj_name = next(
                (n for n in names if n.lower().endswith('.obj')), None)
            mtl_name = next(
                (n for n in names if n.lower().endswith('.mtl')), None)
            if not obj_name or not mtl_name:
                return jsonify({'ok': False, 'error': 'В архиве нет .obj или .mtl — это точно экспорт аватара?'}), 400

            obj_text = zf.read(obj_name).decode('utf-8', 'replace')
            mtl_text = zf.read(mtl_name).decode('utf-8', 'replace')
            textures = []
            for n in names:
                if n.lower().endswith(('.png', '.jpg', '.jpeg')):
                    data = zf.read(n)
                    mime = 'image/png' if n.lower().endswith('.png') else 'image/jpeg'
                    textures.append({
                        'name': n.rsplit('/', 1)[-1],
                        'data_url': f'data:{mime};base64,' + _b64.b64encode(data).decode('ascii'),
                    })
        return jsonify({'ok': True, 'obj_text': obj_text, 'mtl_text': mtl_text, 'textures': textures})
    except zipfile.BadZipFile:
        return jsonify({'ok': False, 'error': 'Файл повреждён или это не .zip'}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


def _rbx_maybe_gunzip(raw: bytes) -> bytes:
    """Подстраховка: если какой-то узел всё же проигнорирует
    Accept-Encoding: identity и пришлёт gzip (сигнатура байтов 1f 8b),
    распаковываем сами — иначе на выходе будет нечитаемая бинарная каша
    вместо настоящего JSON/OBJ/PNG."""
    if len(raw) >= 2 and raw[0] == 0x1f and raw[1] == 0x8b:
        import gzip as _gzip
        return _gzip.decompress(raw)
    return raw


def _rbx_get_json(url):
    r = _req.Request(url, headers=_roblox_headers())
    try:
        with _req.urlopen(r, timeout=20) as resp:
            raw_bytes = _rbx_maybe_gunzip(resp.read())
            raw_text = raw_bytes.decode('utf-8', 'replace')
    except _urlerr.HTTPError as e:
        body = _rbx_maybe_gunzip(e.read()).decode('utf-8', 'replace')[:300]
        raise RuntimeError(f'HTTP {e.code} от Roblox: {body}')
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Не JSON — почти всегда значит, что вместо API-ответа пришла
        # HTML-страница (антибот-проверка Cloudflare/PerimeterX, редирект
        # на логин и т.п.). Показываем начало тела как есть — так сразу
        # видно, что это не наш баг, а блокировка со стороны Roblox.
        snippet = raw_text[:300].replace('\n', ' ')
        raise RuntimeError(
            f'Roblox вернул не-JSON ответ (похоже на антибот-страницу): {snippet}')


def _roblox_apikey_file():
    """Путь к файлу с сохранённым Open Cloud API-ключом — то же место и
    тот же принцип, что и _roblox_auth_file() для куки (см. рядом):
    RSW_DATA_DIR на Android, локальная папка иначе. Отдельный файл, а не
    внутри roblox_auth.json — ключ и кука это разные учётные данные с
    разным жизненным циклом (ключ не привязан к конкретному логину)."""
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    return Path(data_dir) / 'roblox_apikey.json'


def _roblox_api_key():
    """Open Cloud API-ключ — официальная замена сессионной куки для
    AssetDelivery. С 2 апреля 2025 Roblox закрыл анонимный доступ к
    assetdelivery.roblox.com (see devforum "New Asset Delivery API
    Endpoints for Community Tools") — без авторизации теперь 401 на
    ЛЮБОЙ запрос, а не только на приватные ассеты. Ключ создаётся в
    Creator Dashboard → Open Cloud → API Keys, с правом только на чтение
    ассетов.

    Порядок поиска: переменная окружения ROBLOX_API_KEY (для серверных
    деплоев, где ключ задаётся при запуске) — если не задана, читаем
    ключ, который пользователь ввёл сам через UI (/api/roblox/api-key,
    см. ниже) и который лежит в _roblox_apikey_file(). Ключ НЕ хранится
    в коде/репозитории ни в одном из вариантов."""
    env_key = os.environ.get('ROBLOX_API_KEY', '').strip()
    if env_key:
        return env_key
    p = _roblox_apikey_file()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        key = (data.get('api_key') or '').strip()
        return key or None
    except Exception:
        return None


@flask_app.route('/api/roblox/api-key', methods=['GET', 'POST', 'DELETE'])
def api_roblox_api_key():
    """Управление Open Cloud API-ключом из UI — пользователь вводит его
    сам (см. showRobloxApiKeyDialog в index.html), ключ сохраняется на
    диск локально (та же папка, что и roblox_auth.json) и никогда не
    уходит никуда, кроме прямых запросов к apis.roblox.com в
    _rbx_get_bytes_opencloud. GET отдаёт только факт наличия ключа и его
    последние 4 символа для опознания — сам ключ обратно не возвращаем."""
    p = _roblox_apikey_file()

    if request.method == 'GET':
        env_key = os.environ.get('ROBLOX_API_KEY', '').strip()
        if env_key:
            return jsonify({'ok': True, 'hasKey': True, 'source': 'env', 'last4': env_key[-4:]})
        key = _roblox_api_key()
        if not key:
            return jsonify({'ok': True, 'hasKey': False})
        return jsonify({'ok': True, 'hasKey': True, 'source': 'ui', 'last4': key[-4:]})

    if request.method == 'DELETE':
        try:
            if p.exists():
                p.unlink()
            return jsonify({'ok': True})
        except Exception as e:
            return jsonify({'ok': False, 'error': str(e)}), 500

    # POST — сохранить новый ключ
    body = request.get_json(silent=True) or {}
    key = (body.get('api_key') or '').strip()
    if not key:
        return jsonify({'ok': False, 'error': 'api_key пустой'}), 400
    try:
        p.write_text(json.dumps({'api_key': key}), encoding='utf-8')
        return jsonify({'ok': True, 'last4': key[-4:]})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/roblox/api-key/validate', methods=['POST'])
def api_roblox_api_key_validate():
    """Реальная проверка сохранённого ключа — раньше единственный способ
    узнать, что ключ битый/без нужного скоупа, был подождать, пока
    что-нибудь в игре не перестанет грузиться, и читать 502 из
    /api/asset-proxy постфактум. Дёргаем тот же metadata-запрос Open
    Cloud (без скачивания самого CDN-файла — незачем гонять байты ради
    проверки), тестовым ID из тела запроса, если он есть (обычно берём
    первый попавшийся реальный ассет прямо из сцены на фронте — так
    проверка идёт по тому, что реально понадобится в игре), иначе просто
    числом 1 (главное — отличить 401/403 по КЛЮЧУ от ошибки по
    конкретному ассету)."""
    api_key = _roblox_api_key()
    if not api_key:
        return jsonify({'ok': True, 'valid': False, 'reason': 'no_key'})

    body = request.get_json(silent=True) or {}
    m = _re.search(r'\d+', str(body.get('assetId', '')))
    test_id = m.group() if m else '1'

    meta_req = _req.Request(
        f'https://apis.roblox.com/asset-delivery-api/v1/assetId/{test_id}',
        headers={'x-api-key': api_key, 'Accept': 'application/json',
                 'Accept-Encoding': 'identity'})
    try:
        with _req.urlopen(meta_req, timeout=10) as resp:
            resp.read()
        return jsonify({'ok': True, 'valid': True})
    except _urlerr.HTTPError as e:
        if e.code in (401, 403):
            return jsonify({'ok': True, 'valid': False, 'reason': 'unauthorized',
                            'status': e.code})
        # Любая ДРУГАЯ ошибка (404 на конкретный тестовый ассет, 5xx у
        # Roblox и т.п.) НЕ значит, что ключ плохой — сам факт того, что
        # сервер ответил (а не отверг по x-api-key), уже означает, что
        # ключ авторизовался нормально.
        return jsonify({'ok': True, 'valid': True, 'note': f'HTTP {e.code} на тестовом ассете, но ключ авторизовался'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


def _rbx_get_bytes_opencloud(asset_id):
    """GET /asset-delivery-api/v1/assetId/{id} с x-api-key → JSON с
    полем location (временная подписанная CDN-ссылка, TTL несколько
    минут) → обычный GET по этой ссылке уже без заголовков авторизации.
    Возвращает None, если ключ не сконфигурирован (тогда вызывающий код
    падает обратно на анонимный путь ниже), и бросает исключение при
    реальной ошибке запроса — чтобы отличить "ключа просто нет" от
    "ключ есть, но не работает"."""
    api_key = _roblox_api_key()
    if not api_key:
        return None

    meta_req = _req.Request(
        f'https://apis.roblox.com/asset-delivery-api/v1/assetId/{asset_id}',
        headers={'x-api-key': api_key, 'Accept': 'application/json',
                 'Accept-Encoding': 'identity'})
    with _req.urlopen(meta_req, timeout=20) as resp:
        meta = json.loads(_rbx_maybe_gunzip(resp.read()).decode('utf-8', 'replace'))

    location = meta.get('location')
    if not location:
        raise RuntimeError(f'Open Cloud ответил без location: {meta}')

    # Сама CDN-ссылка уже подписана (signature+expiry в query, см.
    # archiveteam wiki про AWS CloudFront) — второй раз x-api-key слать
    # не нужно и не поможет, это просто обычный HTTPS GET.
    cdn_req = _req.Request(location, headers={'Accept-Encoding': 'gzip'})
    with _req.urlopen(cdn_req, timeout=20) as resp:
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_bytes(url):
    r = _req.Request(url, headers=_roblox_headers())
    with _req.urlopen(r, timeout=8) as resp:
        return _rbx_maybe_gunzip(resp.read())


# Кэш байтов ассетов — картинки/звуки в игре (SongIcon.Image, звуковые
# дорожки песен) грузились с этого эндпоинта заново КАЖДЫЙ раз, включая
# после перезапуска самого приложения: _ASSET_PROXY_CACHE был только
# in-memory и обнулялся при каждом старте процесса — то есть каждый
# новый запуск приложения снова честно ходил в сеть к Roblox за теми же
# самыми картинками/треками, которые уже качал минуту назад в прошлом
# запуске. Теперь под ним ещё и постоянный дисковый кэш (RSW_DATA_DIR/
# asset_cache — то же место, где уже лежит roblox_auth.json), переживающий
# перезапуск: in-memory кэш — для повторов В ПРЕДЕЛАХ одного запуска
# (без похода даже на диск), дисковый — для повторов МЕЖДУ запусками
# (без похода в сеть). Размер диска не ограничиваем намеренно — это же
# по сути локальная копия того, что и так уже сохранено в самом .rbxl
# как id ассетов, а не что-то растущее бесконтрольно с каждым новым
# файлом; при необходимости почистить — это просто папка, которую можно
# удалить руками.
_ASSET_PROXY_CACHE = {}
_ASSET_PROXY_CACHE_MAX = 64


def _asset_cache_dir():
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    d = Path(data_dir) / 'asset_cache'
    d.mkdir(parents=True, exist_ok=True)
    return d


def _asset_cache_disk_get(asset_id):
    """Ищет ассет на диске — имя файла кодирует content-type, чтобы не
    городить отдельный файл-метаданные на каждый ассет."""
    try:
        for f in _asset_cache_dir().glob(f'{asset_id}__*.bin'):
            ct = f.stem.split('__', 1)[1].replace('_', '/')
            return ct, f.read_bytes()
    except Exception:
        pass
    return None


def _asset_cache_disk_put(asset_id, content_type, raw_bytes):
    try:
        safe_ct = content_type.replace('/', '_')
        f = _asset_cache_dir() / f'{asset_id}__{safe_ct}.bin'
        if not f.exists():
            f.write_bytes(raw_bytes)
    except Exception:
        pass  # дисковый кэш — best-effort, не должен ронять сам запрос


def _asset_response(raw_bytes, content_type):
    """Ассеты по id иммутабельны (rbxassetid:// не меняет содержимое под
    тем же id) — раньше ответ уходил вообще без Cache-Control, и браузер
    честно перезапрашивал одну и ту же картинку/звук при каждой
    перерисовке GUI (например карточек песен в меню) заново через тот же
    локальный сервер, хотя байты гарантированно те же самые."""
    resp = Response(raw_bytes, mimetype=content_type)
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return resp


@flask_app.route('/api/asset-proxy')
def api_asset_proxy():
    """Прокси-загрузка ассета Roblox по id — превращает rbxassetid://N
    (то, что реально лежит в Image/SoundId у ImageLabel/Sound в файле) в
    настоящий скачиваемый URL для браузера. Нужен именно прокси, а не
    прямой fetch с клиента на assetdelivery.roblox.com/apis.roblox.com,
    из-за CORS — эти домены не шлют заголовки, разрешающие браузеру
    читать ответ с произвольного источника.

    Порядок попыток (обе ветки реально пробуются, а не "либо/либо"):
    1) Open Cloud (x-api-key, см. _rbx_get_bytes_opencloud) — официальный
       путь, если сконфигурирован ROBLOX_API_KEY.
    2) Кука/анонимный GET на /v1/asset/?id= (_roblox_headers сама решает,
       слать куку или нет — см. _roblox_cookie) — пробуется, если шаг 1
       не настроен ИЛИ настроен, но реально упал (сеть, невалидный ключ,
       ассет вне прав ключа и т.п.). С 2 апреля 2025 Roblox требует
       авторизацию на ЛЮБОЙ запрос к AssetDelivery, так что без ключа И
       без куки этот шаг тоже обычно вернёт 401 — тогда возвращаем
       ОБЕ ошибки, чтобы сразу было видно, что именно не сработало."""
    raw_id = request.args.get('id', '').strip()
    m = _re.search(r'\d+', raw_id)
    if not m:
        return Response('bad asset id', status=400)
    asset_id = m.group()

    cached = _ASSET_PROXY_CACHE.get(asset_id)
    if cached:
        content_type, raw_bytes = cached
        return _asset_response(raw_bytes, content_type)

    disk_cached = _asset_cache_disk_get(asset_id)
    if disk_cached:
        content_type, raw_bytes = disk_cached
        # Подтягиваем и в in-memory тоже — следующие запросы в ЭТОЙ сессии
        # не будут даже читать файл с диска.
        if len(_ASSET_PROXY_CACHE) >= _ASSET_PROXY_CACHE_MAX:
            _ASSET_PROXY_CACHE.pop(next(iter(_ASSET_PROXY_CACHE)))
        _ASSET_PROXY_CACHE[asset_id] = (content_type, raw_bytes)
        return _asset_response(raw_bytes, content_type)

    raw_bytes = None
    opencloud_error = None
    try:
        raw_bytes = _rbx_get_bytes_opencloud(asset_id)
    except Exception as e:
        opencloud_error = str(e)

    cookie_error = None
    if raw_bytes is None:
        try:
            raw_bytes = _rbx_get_bytes(
                f'https://assetdelivery.roblox.com/v1/asset/?id={asset_id}')
        except Exception as e:
            cookie_error = str(e)

    if raw_bytes is None:
        parts = []
        if opencloud_error:
            parts.append(f'Open Cloud: {opencloud_error}')
        if cookie_error:
            has_cookie = _roblox_cookie() is not None
            parts.append(
                f'{"кука" if has_cookie else "анонимно (нет куки)"}: {cookie_error}')
        return Response('asset fetch failed — ' + '; '.join(parts), status=502)

    # Ассет может оказаться не картинкой, а XML-обёрткой (Decal, Shirt, Pants,
    # Texture): внутри лежит id настоящего изображения. Идём по ссылке
    # (не глубже двух уровней) — иначе <img>/TextureLoader получал XML и не
    # мог его показать (текстуры одежды на теле не появлялись).
    for _ in range(2):
        head = raw_bytes[:400].lstrip()
        if not (head.startswith(b'<roblox') and not head.startswith(b'<roblox!')) and not head.startswith(b'<?xml'):
            break
        m_in = _re.search(
            rb'<Content name="(?:ShirtTemplate|PantsTemplate|Texture|Graphic|Image|ColorMap)">\s*<url>[^<]*?(\d+)</url>',
            raw_bytes)
        if not m_in or m_in.group(1).decode() == asset_id:
            break
        inner_id = m_in.group(1).decode()
        inner_bytes = None
        try:
            inner_bytes = _rbx_get_bytes_opencloud(inner_id)
        except Exception:
            try:
                inner_bytes = _rbx_get_bytes(
                    f'https://assetdelivery.roblox.com/v1/asset/?id={inner_id}')
            except Exception:
                inner_bytes = None
        if not inner_bytes:
            break
        raw_bytes = inner_bytes

    # Тип контента — по сигнатуре байтов (см. тот же приём в убранной
    # asset/fetch-фиче): Roblox отдаёт сырые байты картинки/звука без
    # заголовка, который тут можно было бы просто перенести как есть.
    if raw_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        content_type = 'image/png'
    elif raw_bytes[:3] == b'\xff\xd8\xff':
        content_type = 'image/jpeg'
    elif raw_bytes[:4] == b'OggS':
        content_type = 'audio/ogg'
    elif raw_bytes[:3] == b'ID3' or (raw_bytes[:1] == b'\xff' and len(raw_bytes) > 1 and (raw_bytes[1] & 0xe0) == 0xe0):
        # MP3 без ID3-тега начинается сразу с фрейма: 11-битное синхрослово
        # 0xFFE (первый байт FF, у второго байта старшие 3 бита тоже
        # единицы) — младшие биты второго байта кодируют версию MPEG/layer
        # и МЕНЯЮТСЯ от файла к файлу (0xFB — это только ОДИН конкретный
        # вариант). Раньше проверялся именно этот один вариант байт-в-байт,
        # так что любой трек с другой версией/битрейтом тихо улетал как
        # application/octet-stream — браузер такое играть отказывается
        # ("Failed to load because no supported source was found").
        content_type = 'audio/mpeg'
    elif raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
        # RIFF — общий контейнерный формат: WAV и WEBP ОБА начинаются с
        # "RIFF", различаются только по 4-байтовой метке форматa на
        # смещении 8 ("WAVE" против "WEBP"). Раньше сюда попадал только
        # WAV-случай, а Roblox реально отдаёт часть текстур именно в WEBP —
        # такая картинка уходила с типом audio/wav, и TextureLoader/<img>
        # закономерно не мог её декодировать ("Failed to load part texture").
        content_type = 'image/webp'
    elif raw_bytes[:4] == b'RIFF':
        content_type = 'audio/wav'
    else:
        content_type = 'application/octet-stream'

    if len(_ASSET_PROXY_CACHE) >= _ASSET_PROXY_CACHE_MAX:
        _ASSET_PROXY_CACHE.pop(next(iter(_ASSET_PROXY_CACHE)))
    _ASSET_PROXY_CACHE[asset_id] = (content_type, raw_bytes)
    _asset_cache_disk_put(asset_id, content_type, raw_bytes)

    return _asset_response(raw_bytes, content_type)


def _rbx_download_cdn(hash_value):
    """8 CDN-узлов Roblox равнозначны — здесь короткий таймаут на узел
    (8с), чтобы один зависший узел не превращал скачивание в минуты
    ожидания: суммарный худший случай — 8×8с=64с на один файл, что уже
    приемлемо, а на практике первый же живой узел отвечает почти сразу."""
    last_err = None
    for n in range(8):
        try:
            return _rbx_get_bytes(f'https://t{n}.rbxcdn.com/{hash_value}')
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or f'Не удалось скачать {hash_value}')


def api_roblox_avatar3d_status():
    """Один быстрый неблокирующий опрос состояния генерации у Roblox —
    вызывается клиентом периодически (см. doDownloadAvatar3d в index.html),
    а не ждётся одним долгим запросом. Roblox генерирует 3D-модель
    асинхронно и может занять от нескольких секунд до ~минуты — раньше мы
    ждали это одним запросом с фиксированным таймаутом, из-за чего при
    медленной генерации запрос обрывался с невнятной ошибкой."""
    user_id = request.args.get('userId', '').strip()
    if not user_id.isdigit():
        return jsonify({'ok': False, 'error': 'userId должен быть числом'}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': 'Сначала войдите в аккаунт Roblox.'}), 401
    try:
        resp = _rbx_get_json(
            f'https://thumbnails.roblox.com/v1/users/avatar-3d?userId={user_id}')

        if isinstance(resp, dict) and 'data' in resp and resp['data']:
            item = resp['data'][0]
        elif isinstance(resp, dict) and 'targetId' in resp and 'state' in resp:
            # Roblox иногда отдаёт этот эндпоинт без обёртки {"data":[...]}
            # — плоским объектом напрямую.
            item = resp
        elif isinstance(resp, dict) and resp.get('errors'):
            reason = resp['errors'][0].get('message', 'нет описания')
            return jsonify({
                'ok': False,
                'error': reason,
                'message': f'Roblox отклонил запрос: {reason}. Попробуйте выйти и войти в аккаунт заново.',
            }), 502
        else:
            # Незнакомый формат — показываем сырой ответ целиком, чтобы
            # можно было понять, что реально прислал Roblox (например,
            # HTML-страницу антибот-проверки вместо JSON).
            raw = json.dumps(resp, ensure_ascii=False)[:400]
            return jsonify({
                'ok': False,
                'error': 'unexpected_response_shape',
                'message': f'Roblox вернул формат ответа, который скрипт не понимает. Сырой ответ: {raw}',
            }), 502
        state_ = item.get('state')
        return jsonify({
            'ok': True,
            'state': state_,
            'ready': state_ == 'Completed',
            'bundleUrl': item.get('imageUrl') if state_ == 'Completed' else None,
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


@flask_app.route('/api/roblox/avatar3d/fetch')
def api_roblox_avatar3d_fetch():
    """Вызывается клиентом ТОЛЬКО после того, как /status вернул
    ready=true — сразу скачивает obj/mtl/текстуры по уже готовому
    bundleUrl (без повторного ожидания) и упаковывает их в ОДИН .zip,
    записанный на диск (а не base64 в JSON — see below).

    userId нужен для имени файла, savePath — папка, куда класть zip
    (на Android клиент передаёт window.AndroidBridge.getDataDir(),
    потому что писать напрямую в выбранное пользователем место сервер
    не может — нет доступа к SAF-Uri; см. androidSaveConfirm() в
    index.html, тот же паттерн, что уже используется для .rbxl).

    Раньше файлы отдавались как base64 внутри JSON, а на клиенте
    создавался <a download> с blob: URL — внутри Android WebView это
    НЕ настоящее скачивание, ссылка просто "кликалась в никуда" и
    пользователь не понимал, куда делись файлы."""
    import zipfile
    import tempfile as _tempfile

    bundle_url = request.args.get('bundleUrl', '').strip()
    user_id = request.args.get('userId', '').strip() or 'unknown'
    save_dir = request.args.get('savePath', '').strip()
    if not bundle_url.startswith('https://'):
        return jsonify({'ok': False, 'error': 'bundleUrl отсутствует или некорректен'}), 400
    if not save_dir:
        return jsonify({'ok': False, 'error': 'savePath отсутствует'}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': 'Сначала войдите в аккаунт Roblox.'}), 401
    try:
        bundle = _rbx_get_json(bundle_url)

        # obj, mtl и каждая текстура — независимые скачивания с разных
        # CDN-узлов; параллелим их вместо последовательного цикла, чтобы
        # весь процесс не растягивался на сумму времени всех файлов.
        import concurrent.futures as _cf

        tex_hashes = bundle.get('textures', [])
        with _cf.ThreadPoolExecutor(max_workers=max(2, len(tex_hashes) + 2)) as pool:
            obj_future = pool.submit(_rbx_download_cdn, bundle['obj'])
            mtl_future = pool.submit(_rbx_download_cdn, bundle['mtl'])
            tex_futures = [pool.submit(_rbx_download_cdn, h)
                           for h in tex_hashes]

            obj_bytes = obj_future.result()
            mtl_bytes = mtl_future.result()
            tex_files = []
            for tex_hash, fut in zip(tex_hashes, tex_futures):
                tex_files.append((
                    _re.sub(r'[^a-zA-Z0-9._-]+', '_', tex_hash) + '.png',
                    fut.result(),
                ))

        # БАГ-ФИКС: Roblox отдаёт .mtl со ссылками на текстуры БЕЗ
        # расширения (например "map_Kd 30DAY-abc123"), а сами файлы мы
        # сохраняем как "30DAY-abc123.png" — без этой правки Blender и
        # другие вьюеры не находят текстуры при импорте. Дописываем
        # ".png" к каждой ссылке, которая совпадает с одним из hash.
        mtl_text = mtl_bytes.decode('utf-8', 'replace')
        for tex_hash, _fname in zip(tex_hashes, [f[0] for f in tex_files]):
            mtl_text = _re.sub(
                r'(?<![\w.])' + _re.escape(tex_hash) + r'(?!\.\w)',
                tex_hash + '.png',
                mtl_text,
            )
        mtl_bytes = mtl_text.encode('utf-8')

        zip_name = f'roblox_avatar_{user_id}.zip'
        zip_path = str(Path(save_dir) / zip_name)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('avatar.obj', obj_bytes)
            zf.writestr('avatar.mtl', mtl_bytes)
            for name, data in tex_files:
                zf.writestr(name, data)
            meta = {'userId': user_id, 'camera': bundle.get(
                'camera'), 'aabb': bundle.get('aabb')}
            zf.writestr('meta.json', json.dumps(
                meta, ensure_ascii=False, indent=2))

        response = {
            'ok': True,
            'zipPath': zip_path,
            'zipName': zip_name,
            'fileCount': 3 + len(tex_files),
        }
        # Для импорта прямо в 3D-сцену редактора клиенту не нужен
        # повторный поход на диск/сеть — сразу отдаём текст OBJ/MTL и
        # текстуры как base64 (data URL). Это НЕ дублирует запись zip —
        # zip всё равно нужен для варианта "просто скачать себе на диск".
        if request.args.get('includeAssets') == '1':
            response['obj_text'] = obj_bytes.decode('utf-8', 'replace')
            response['mtl_text'] = mtl_text
            response['textures'] = [
                {'name': name, 'data_url': 'data:image/png;base64,' +
                    _b64.b64encode(data).decode('ascii')}
                for name, data in tex_files
            ]
        return jsonify(response)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


@flask_app.route('/api/status')
def api_status():
    parsed = state['parsed']
    return jsonify({
        'ok': True,
        'loaded': parsed is not None,
        'file': state['file_path'],
        'count': len(parsed['referent_to_class']) if parsed else 0,
    })


# Лог-файлы Lua Output — каждый запуск Play пишет в свой файл под logs/, а
# не только в браузерную панель Output (которая пропадает при закрытии
# вкладки/обновлении страницы). Одна запись на строку JSON — удобно и
# смотреть глазами (less/tail), и парсить скриптом при желании.
LOG_DIR = Path(__file__).resolve().parent / 'logs'
_log_state = {'file': None, 'session': None}


def _current_log_path():
    # Новый файл на каждую Play-сессию (см. 'session' в теле запроса —
    # фронтенд генерирует один id при старте Play и шлёт его с каждой
    # строкой лога этой сессии), не на каждую отдельную запись.
    return _log_state['file']


@flask_app.route('/api/log', methods=['POST'])
def api_log():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        data = request.get_json(force=True, silent=True) or {}
        session = data.get('session') or 'unknown'
        if _log_state['session'] != session:
            ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            _log_state['session'] = session
            _log_state['file'] = LOG_DIR / f'play_{ts}.log'
        line = {
            'time': data.get('time', ''),
            'level': data.get('level', 'print'),
            'source': data.get('source', ''),
            'text': data.get('text', ''),
        }
        with open(_current_log_path(), 'a', encoding='utf-8') as f:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')
        return jsonify({'ok': True})
    except Exception as e:
        # Логирование не должно ронять саму игру — если писать не
        # получилось (нет прав на диск и т.п.), просто молча отвечаем ok:false.
        return jsonify({'ok': False, 'error': str(e)}), 200


@flask_app.route('/api/log/list')
def api_log_list():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(LOG_DIR.glob('play_*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
        return jsonify({'ok': True, 'files': [f.name for f in files]})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/log/<path:name>')
def api_log_get(name):
    try:
        # Только файлы вида play_*.log из LOG_DIR — не отдаём произвольный
        # путь по запросу.
        safe = Path(name).name
        if not safe.startswith('play_') or not safe.endswith('.log'):
            return jsonify({'ok': False, 'error': 'bad name'}), 400
        return send_from_directory(LOG_DIR, safe, mimetype='text/plain')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404


# Чтение HTML/CSS/JS — раньше все три были одним файлом (index.html),
# из-за чего он разросся почти до 10000 строк в одном месте; теперь
# разложены на отдельные файлы рядом с app.py (index.html/style.css/
# script.js), index.html подключает их через <link>/<script src>.
with open("index.html", "r", encoding="utf-8") as file:
    HTML_TEMPLATE = file.read()
with open("style.css", "r", encoding="utf-8") as file:
    CSS_TEMPLATE = file.read()
with open("script.js", "r", encoding="utf-8") as file:
    JS_TEMPLATE = file.read()


@flask_app.route('/')
def index():
    return Response(HTML_TEMPLATE, mimetype='text/html')


@flask_app.route('/style.css')
def style_css():
    return Response(CSS_TEMPLATE, mimetype='text/css')


@flask_app.route('/script.js')
def script_js():
    return Response(JS_TEMPLATE, mimetype='application/javascript')


if __name__ == '__main__':
    import threading
    import webbrowser
    import time

    if len(sys.argv) > 1:
        p = sys.argv[1]
        if Path(p).exists():
            try:
                parsed = parse_rbxl(p)
                state['parsed'] = parsed
                state['file_path'] = p
                print(
                    f'[RbxStudio] Загружен: {p} ({len(parsed["referent_to_class"])} объектов)')
            except Exception as e:
                print(f'[RbxStudio] Ошибка загрузки: {e}')

    url = f'http://127.0.0.1:{PORT}'
    print(f'[RbxStudio] Запуск: {url}')

    def open_browser():
        time.sleep(2)
        # На Termux нет обычного GUI-браузера, который понимает
        # стандартный python webbrowser.open() — он там может найти
        # текстовый браузер (links/w3m/lynx) и открыть его ПРЯМО В
        # ТЕРМИНАЛЕ, что выглядит как "дамп" HTML вместо реального
        # запуска сервера. termux-open-url (из пакета Termux:API)
        # корректно передаёт ссылку системному Android-браузеру.
        try:
            subprocess.run(
                ['termux-open-url', url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        # Не на Termux (или Termux:API не установлен) — пробуем обычный
        # способ, но только если это НЕ похоже на текстовый браузер.
        if sys.platform != 'linux' or os.environ.get('TERMUX_VERSION'):
            return
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    # threaded=True обязателен: без него однопоточный dev-сервер Flask
    # блокирует ВООБЩЕ ВСЕ запросы (включая обычную работу редактора) на
    # всё время выполнения долгого /api/roblox/avatar3d/fetch — именно из-за
    # этого приложение выглядело "зависшим" целиком, а не только диалог
    # скачивания аватара.
    flask_app.run(host='0.0.0.0', port=PORT, debug=False,
                  use_reloader=False, threaded=True)
