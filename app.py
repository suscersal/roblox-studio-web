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
from rbxl_parser import parse_rbxl, save_rbxl, publish_place
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
}

# Классы 2D-интерфейса (Roblox GUI) — рендерятся отдельным DOM-оверлеем
# поверх 3D-вьюпорта в Play (см. index.html, buildGuiOverlay/#gui-overlay),
# а не как объекты сцены three.js/cannon.js, как PART_CLASSES.
GUI_ROOT_CLASSES = {'ScreenGui', 'BillboardGui'}
GUI_CONTAINER_CLASSES = {'Frame', 'ScrollingFrame'}
GUI_LEAF_CLASSES = {
    'TextLabel', 'TextButton', 'TextBox', 'ImageLabel', 'ImageButton',
}
GUI_CLASSES = GUI_ROOT_CLASSES | GUI_CONTAINER_CLASSES | GUI_LEAF_CLASSES

# Свойства, которые реально нужны фронтенду для рисования GUI-оверлея —
# сознательно узкий список (как и SCRIPT_CLASSES выше по духу), чтобы не
# гонять по сети произвольные бинарные/редкие свойства ради одного div'а.
GUI_PROPS = (
    'Name', 'Position', 'Size', 'AnchorPoint', 'Visible', 'Enabled',
    'ZIndex', 'BackgroundColor3', 'BackgroundTransparency', 'BorderSizePixel',
    'BorderColor3', 'Text', 'TextColor3', 'TextTransparency', 'TextSize',
    'TextScaled', 'TextWrapped', 'TextXAlignment', 'TextYAlignment', 'Font',
    'Image', 'ScaleType', 'ClipsDescendants',
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
        if o.get('shape') == 'box':
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

        # Получаем цвет
        col = props.get('Color') or props.get(
            'Color3') or props.get('BrickColor')
        color = get_color(col) if isinstance(col, dict) else '#a0a0a0'

        shape = 'sphere' if cls == 'SpherePart' else 'box'
        CONE_IDS = ['9756362', '1033714', '9887819', 'cone.mesh']
        for sm_ref in [ref + 1, ref + 2]:
            if parsed['referent_to_class'].get(sm_ref) != 'SpecialMesh':
                continue
            cp = parsed['props'].get(sm_ref, {})
            mt = cp.get('MeshType', 0)
            if isinstance(mt, str):
                mt = int(mt) if mt.isdigit() else 0
            mid = str(cp.get('MeshId', ''))
            if mt == 4 or mt == 3:
                shape = 'sphere'
            elif mt == 1:
                shape = 'cylinder'
            elif mt == 6:
                shape = 'wedge'
            elif any(cid in mid for cid in CONE_IDS):
                shape = 'cone'
            break
        name = props.get('Name', cls)

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
            'rot': rot_matrix, 'color': color,
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
    'codemirror.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css',
    'monokai.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/monokai.min.css',
    'codemirror.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js',
    'lua.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/lua/lua.min.js',
    'closebrackets.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/edit/closebrackets.min.js',
    'matchbrackets.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/edit/matchbrackets.min.js',
    'three.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'MTLLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js',
    'OBJLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js',
    'cannon.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js',
    'fengari-web.js': 'https://cdn.jsdelivr.net/npm/fengari-web@0.1.4/dist/fengari-web.js',
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
    out = []
    for ref, cls in r2c.items():
        name = pr.get(ref, {}).get('Name', cls)
        out.append({'ref': ref, 'cls': cls, 'name': name, 'parent': pm.get(ref, -1)})
    return jsonify({'ok': True, 'instances': out})


@flask_app.route('/api/scripts')
def api_scripts():
    # Отдаёт все Script/LocalScript с исходником — используется Lua-рантаймом
    # в Play (см. index.html, startLuaScripts/fengari) для запуска скриптов
    # одним запросом, а не по одному через /api/instance/<ref> на каждый.
    # ModuleScript сюда сознательно не входит — Roblox их не исполняет
    # автоматически, только через require() из другого скрипта, а require()
    # в этой версии не реализован.
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    r2c = parsed['referent_to_class']
    pm = parsed['parent_map']
    pr = parsed['props']
    out = []
    for ref, cls in r2c.items():
        if cls not in ('Script', 'LocalScript'):
            continue
        props = pr.get(ref, {})
        enabled = props.get('Enabled', True)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ('true', '1')
        if not enabled:
            continue
        out.append({
            'ref': ref, 'cls': cls,
            'name': props.get('Name', cls),
            'source': props.get('Source', '') or '',
            'parent': pm.get(ref, -1),
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


def _rbx_get_bytes(url):
    r = _req.Request(url, headers=_roblox_headers())
    with _req.urlopen(r, timeout=8) as resp:
        return _rbx_maybe_gunzip(resp.read())


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


@flask_app.route('/api/roblox/avatar3d/status')
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


# Чтение HTML шаблона
with open("index.html", "r", encoding="utf-8") as file:
    HTML_TEMPLATE = file.read()


@flask_app.route('/')
def index():
    return Response(HTML_TEMPLATE, mimetype='text/html')


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
