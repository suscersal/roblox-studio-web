#!/usr/bin/env python3
import urllib.error as _urlerr
import urllib.parse as _urlparse
import urllib.request as _req
import re as _re
import base64 as _b64
import base64
import struct
import math
import traceback
import json
import time
from urllib.parse import quote
from rbxl_parser import parse_rbxl, save_rbxl, publish_place, export_rbxm, import_rbxm
from rbxl_parser import union_mesh_from_parsed as _union_mesh_solid, union_mesh_render_json
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
    # UnionOperation (CSG-юнион) раньше не входил сюда вообще — такие
    # объекты молча пропускались и не попадали в сцену. Их настоящая
    # геометрия лежит в сжатом бинарном блобе MeshData2 (SharedString),
    # который мы не декодируем, поэтому пока рисуем как box по Size — с
    # правильными CFrame/цветом/материалом (Size у юниона — это габарит
    # готового тела, так что box хотя бы совпадает с его bounding box).
    # NegateOperation НЕ добавляем: это "вычитаемая" деталь, в игре её
    # не видно.
    'UnionOperation',
}

# Классы 2D-интерфейса (Roblox GUI) — рендерятся отдельным DOM-оверлеем
# поверх 3D-вьюпорта в Play (см. index.html, buildGuiOverlay/#gui-overlay),
# а не как объекты сцены three.js/cannon.js, как PART_CLASSES.
GUI_ROOT_CLASSES = {'ScreenGui', 'BillboardGui', 'SurfaceGui'}
GUI_CONTAINER_CLASSES = {'Frame', 'ScrollingFrame', 'CanvasGroup'}   # CanvasGroup: контейнер с общей прозрачностью (GroupTransparency)
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
GUI_DECORATION_CLASSES = {'UICorner', 'UIStroke', 'UIScale', 'UIListLayout', 'UIGridLayout'}   # layout-ы: свойства раскладки нужны клиенту, DOM-узла у них нет   # UIScale: масштаб родителя (см. applyGuiElementStyle)
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
    # UIScale
    'Scale',
    # CanvasGroup
    'GroupTransparency',
    # SurfaceGui (интерфейс на грани детали)
    'Face', 'SizingMode', 'PixelsPerStud', 'CanvasSize', 'AlwaysOnTop', 'Brightness',
    # BillboardGui (интерфейс в мире, лицом к камере)
    'Adornee', 'StudsOffset', 'StudsOffsetWorldSpace', 'SizeOffset', 'ExtentsOffset', 'MaxDistance',
    # UIListLayout / UIGridLayout (раскладка потомков)
    'FillDirection', 'Padding', 'HorizontalAlignment', 'VerticalAlignment', 'SortOrder', 'StartCorner',
    'CellSize', 'CellPadding', 'FillDirectionMaxCells', 'LayoutOrder',
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



# --- Геометрия юниона из его ИСХОДНЫХ деталей --------------------------------------------------------------
# Новый формат юниона хранит меш в MeshData2 (сжатые потоки), а старый SolidMeshHolder пуст — тогда union_mesh_from_parsed
# возвращал None, и юнион рисовался сплошным боксом по Size (стол в fnf.rbxl). Но в ChildData/ChildData2 лежит вложенный
# rbxm с деталями, из которых юнион собран (ножки, столешница...), в ЛОКАЛЬНОЙ системе юниона. Строим меш из них:
# реальные операнды вместо сплошного бокса. Ограничения: вычитающие операнды (NegateOperation) пропускаются, а пересечения
# деталей не склеиваются — внутри остаются лишние грани (на вид не влияет, т.к. они внутри).
_UNION_CHILD_SHAPES_BOX = {None, 1}   # Part.Shape: 1 = Block (по умолчанию); остальные формы приближаем боксом операнда


def _box_triangles(pos, rot, half):
    """Бокс (центр pos, поворот rot 3x3 по строкам, половинные размеры half) -> (positions, normals, tri_index)."""
    positions, normals, index = [], [], []
    axes = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for ax in axes:
        k = next(i for i in range(3) if ax[i] != 0)
        sgn = ax[k]
        u, v = [i for i in range(3) if i != k]
        base = len(positions)
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            loc = [0.0, 0.0, 0.0]
            loc[k] = sgn * half[k]; loc[u] = su * half[u]; loc[v] = sv * half[v]
            positions.append([pos[i] + sum(rot[i * 3 + j] * loc[j] for j in range(3)) for i in range(3)])
        nrm = [sum(rot[i * 3 + j] * ax[j] for j in range(3)) for i in range(3)]
        normals.append(nrm)
        # порядок обхода зависит от знака и от чётности осей — берём так, чтобы нормаль треугольника совпала с нормалью грани
        a, b, c, d = base, base + 1, base + 2, base + 3
        e1 = [positions[b][i] - positions[a][i] for i in range(3)]
        e2 = [positions[c][i] - positions[a][i] for i in range(3)]
        cr = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
        if sum(cr[i] * nrm[i] for i in range(3)) < 0:
            b, d = d, b
        index.append((len(normals) - 1, [a, b, c, a, c, d]))
    return positions, normals, index


def _collect_union_child_boxes(parsed, ref, depth=0, out=None):
    """Рекурсивно собирает (pos, rot, half) операндов юниона ref в его локальной системе. None — данных нет."""
    import os as _os, tempfile as _tmp
    from rbxl_parser import parse_rbxl as _parse
    out = [] if out is None else out
    ss = parsed.get('shared_strings') or []
    props = parsed['props'].get(ref, {})
    idx = props.get('ChildData2')
    if not isinstance(idx, int):
        idx = props.get('ChildData')
    if not isinstance(idx, int) or not (0 <= idx < len(ss)) or not ss[idx][1] or depth > 4:
        return None
    cache = parsed.setdefault('_union_child_cache', {})
    child = cache.get(idx)
    if child is None:
        fd, path = _tmp.mkstemp(suffix='.rbxm')
        try:
            with _os.fdopen(fd, 'wb') as f:
                f.write(ss[idx][1])
            child = _parse(path)
        except Exception:
            child = False
        finally:
            try:
                _os.unlink(path)
            except OSError:
                pass
        cache[idx] = child
    if not child:
        return None
    r2c, cp = child['referent_to_class'], child['props']
    got = False
    for cref, cls in r2c.items():
        if cls not in ('Part', 'MeshPart', 'UnionOperation'):
            continue   # NegateOperation и прочее — не добавляем
        pr = cp.get(cref, {})
        sz = pr.get('Size') or pr.get('InitialSize')
        cf = pr.get('CFrame')
        if not isinstance(sz, dict) or not isinstance(cf, dict):
            continue
        try:
            pos, rot = get_pos(cf), [float(v) for v in get_rot_matrix(cf)]
        except Exception:
            continue
        if cls == 'UnionOperation':
            # вложенный юнион: пробуем его собственные операнды (в его локальной системе -> переносим в нашу)
            sub = _collect_union_child_boxes(child, cref, depth + 1, [])
            if sub:
                for spos, srot, shalf in sub:
                    wp = [pos[i] + sum(rot[i * 3 + j] * spos[j] for j in range(3)) for i in range(3)]
                    wr = [sum(rot[i * 3 + k] * srot[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]
                    out.append((wp, wr, shalf)); got = True
                continue
        out.append((pos, rot, (sz['x'] / 2, sz['y'] / 2, sz['z'] / 2)))
        got = True
    return out if got else None


def union_mesh_from_parsed(parsed, ref):
    """Меш юниона: сначала старый формат (SolidMeshHolder), иначе — собранный из исходных деталей (ChildData/ChildData2)."""
    m = _union_mesh_solid(parsed, ref)
    if m is not None:
        return m
    cache = parsed.setdefault('_union_children_mesh', {})
    if ref in cache:
        return cache[ref]
    boxes = _collect_union_child_boxes(parsed, ref)
    result = None
    if boxes:
        positions, normals, index, normal_index = [], [], [], []
        for pos, rot, half in boxes:
            pts, nrms, faces = _box_triangles(pos, rot, half)
            base = len(positions)
            nbase = len(normals)
            positions.extend(pts); normals.extend(nrms)
            for ni, tri in faces:
                for t in tri:
                    index.append(base + t)
                    normal_index.append(nbase + ni)
        result = {'positions': positions, 'normals': normals, 'index': index, 'normal_index': normal_index,
                  'triangles': len(index) // 3}
    cache[ref] = result
    return result

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
        # unionMesh — то же самое: у юниона своя геометрия (с вырезами),
        # суб-боксы по Size закрыли бы вырезы.
        if o.get('shape') == 'box' and not o.get('meshId') and not o.get('unionMesh'):
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
    # Два формата ссылки на ассет: 'rbxassetid://123' (новый) и 'http://www.roblox.com/asset/?id=123'
    # (старый; так записаны классические R15-руки/ноги 5487114xx и их текстуры). Раньше принимался только
    # первый — у деталей со вторым терялись и меш, и текстура, и они рисовались запасным кубом.
    m = _re.search(r'(?:rbxassetid://|[?&]id=)(\d+)', s, _re.I)
    return m.group(1) if m else None


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
        # SurfaceAppearance.ColorMap — в Roblox он имеет приоритет над
        # MeshPart.TextureID (у таких мешей TextureID обычно пустой — как
        # у акул, у которых из-за этого не было текстуры).
        for child in children_by_parent.get(ref, ()):
            if referent_to_class.get(child) == 'SurfaceAppearance':
                tid = _rbxassetid_num(all_props.get(child, {}).get('ColorMap'))
                if tid:
                    return tid, None
        tid = _rbxassetid_num(props.get('TextureID') or props.get('Texture'))
        if tid:
            return tid, None
    for child in children_by_parent.get(ref, ()):
        child_cls = referent_to_class.get(child)
        if child_cls == 'Decal':
            child_props = all_props.get(child, {})
            tid = _rbxassetid_num(child_props.get('Texture'))
            if tid:
                # Face — число NormalId; 0 (Right) ложно по `or`, поэтому явная проверка на None
                _f = child_props.get('Face')
                return tid, (_f if _f is not None and _f != '' else 'Front')
        elif child_cls == 'SpecialMesh':
            tid = _rbxassetid_num(all_props.get(child, {}).get('TextureId'))
            if tid:
                return tid, None
    return None, None


_NORMAL_ID_NAMES = ['Right', 'Top', 'Back', 'Left', 'Bottom', 'Front']


def _normal_id_name(face):
    """Enum.NormalId (число 0..5 или имя) -> имя грани; неизвестное -> Front."""
    if isinstance(face, bool):
        return 'Front'
    if isinstance(face, (int, float)) and 0 <= int(face) <= 5:
        return _NORMAL_ID_NAMES[int(face)]
    if isinstance(face, str):
        if face.strip().isdigit() and 0 <= int(face) <= 5:
            return _NORMAL_ID_NAMES[int(face)]
        if face in _NORMAL_ID_NAMES:
            return face
    return 'Front'


def _extract_decals(ref, children_by_parent, all_props, referent_to_class):
    """ВСЕ Decal детали: [{tex, face, op}] — по одной на грань (при нескольких на
    одной грани побеждает с бОльшим ZIndex, при равенстве — более поздняя).
    Раньше бралась только первая найденная, и постеры на других гранях пропадали."""
    by_face = {}
    for order, child in enumerate(children_by_parent.get(ref, ())):
        if referent_to_class.get(child) != 'Decal':
            continue
        dp = all_props.get(child, {})
        tid = _rbxassetid_num(dp.get('Texture'))
        if not tid:
            continue
        face = _normal_id_name(dp.get('Face') if dp.get('Face') is not None else 'Front')
        try:
            op = max(0.0, min(1.0, 1.0 - float(dp.get('Transparency') or 0)))
        except (TypeError, ValueError):
            op = 1.0
        try:
            z = int(dp.get('ZIndex') or 1)
        except (TypeError, ValueError):
            z = 1
        key = (z, order)
        if face not in by_face or key >= by_face[face][0]:
            by_face[face] = (key, {'tex': tid, 'face': face, 'op': op})
    return [v[1] for v in by_face.values()]


def _surface_alpha_mode(ref, cls, children_by_parent, all_props, referent_to_class):
    """AlphaMode у SurfaceAppearance, из чьего ColorMap взята текстура MeshPart:
    0 = Overlay (альфа — «насколько текстура перекрывает Color детали»), 1 = Transparency (альфа — прозрачность),
    2 = TintMask. None — текстура не из SurfaceAppearance (обычный TextureID: альфа = вырез)."""
    if cls != 'MeshPart':
        return None
    for child in children_by_parent.get(ref, ()):
        if referent_to_class.get(child) == 'SurfaceAppearance':
            cp = all_props.get(child, {})
            if not _rbxassetid_num(cp.get('ColorMap')):
                return None
            try:
                return int(cp.get('AlphaMode') or 0)
            except (TypeError, ValueError):
                return 0
    return None


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
        # Прозрачность самого Decal (0..1). Decal на невидимой детали (Transparency=1) — частый
        # приём для постеров/вывесок: деталь не видна, а картинка видна. Раньше текстура
        # красилась прозрачностью ДЕТАЛИ, и такие постеры пропадали.
        texture_opacity = None
        if texture_id and texture_face is not None and texture_face != '':
            for _ch in children_by_parent.get(ref, ()):
                if parsed['referent_to_class'].get(_ch) == 'Decal':
                    _dp = parsed['props'].get(_ch, {})
                    if _rbxassetid_num(_dp.get('Texture')) == texture_id:
                        try:
                            texture_opacity = max(0.0, min(1.0, 1.0 - float(_dp.get('Transparency') or 0)))
                        except (TypeError, ValueError):
                            texture_opacity = 1.0
                        break
        decals = _extract_decals(ref, children_by_parent, parsed['props'],
                                 parsed['referent_to_class']) or None
        alpha_mode = _surface_alpha_mode(ref, cls, children_by_parent, parsed['props'],
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

        # У юниона есть настоящий меш, если SolidMeshHolder декодируется.
        # Сам меш по сети не гоняем — клиент заберёт его по /api/union_mesh.
        union_mesh = (cls == 'UnionOperation'
                      and union_mesh_from_parsed(parsed, ref) is not None)

        # PivotOffset детали (смещение точки вращения для GetPivot/PivotTo —
        # например петля двери): [x, y, z, R00..R22]; None, если единичный.
        pivot_offset = None
        _po = props.get('PivotOffset')
        if isinstance(_po, dict):
            _pp = list(get_pos(_po))
            _pr = [float(v) for v in get_rot_matrix(_po)]
            if (any(abs(v) > 1e-6 for v in _pp)
                    or any(abs(x - y) > 1e-6 for x, y in zip(_pr, [1, 0, 0, 0, 1, 0, 0, 0, 1]))):
                pivot_offset = _pp + _pr

        # Деталь лежит в контейнере, которого нет в мире (ServerStorage/ReplicatedStorage — склад шаблонов): клиент не рисует её
        # и не даёт ей физику, но данные оставляет — по ним Clone() строит меш копии в Workspace.
        _root = ref
        _pm = parsed['parent_map']
        _r2c = parsed['referent_to_class']
        _g = 0
        while _pm.get(_root) in _r2c and _g < 500:
            _root = _pm[_root]
            _g += 1
        not_in_world = _r2c.get(_root) in ('ServerStorage', 'ReplicatedStorage', 'StarterPack')

        objs.append({
            'ref': ref, 'class': cls, 'name': name,
            'nw': bool(not_in_world),
            'shape': shape,
            'pivotOffset': pivot_offset,
            'px': px, 'py': py, 'pz': pz,
            'sx': sx, 'sy': sy, 'sz': sz_,
            'rot': rot_matrix, 'color': color, 'texture': texture_id,
            'textureFace': texture_face, 'textureOpacity': texture_opacity, 'decals': decals, 'alphaMode': alpha_mode,
            'meshId': real_mesh_id,
            'opacity': opacity,
            'meshScale': mesh_scale, 'meshOffset': mesh_offset, 'cloth': cloth,
            'material': material, 'mvar': mvar,
            'unionMesh': union_mesh,
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
    # Запасные зеркала: jsdelivr/cdnjs часто недоступны без VPN, а
    # github raw с копией из самого репозитория — обычно доступен.
    urls = [url]
    if (VENDOR_DIR / fn).suffix == '.js':
        urls.append('https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/vendor/' + fn)
    try:
        VENDOR_DIR.mkdir(parents=True, exist_ok=True)
        data = None
        last_err = None
        for u in urls:
            try:
                req = _req.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                with _req.urlopen(req, timeout=15) as resp:
                    data = resp.read()
                if data:
                    break
            except (_urlerr.URLError, _urlerr.HTTPError, OSError, TimeoutError) as e:
                last_err = e
        if not data:
            raise last_err or OSError('пустой ответ')
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


@flask_app.route('/api/class_icons')
def api_class_icons():
    """Иконки классов (data-URI) для диалога «Add»: ?classes=Part,Script,..."""
    names = [c for c in (request.args.get('classes') or '').split(',') if c][:200]
    return jsonify({'ok': True, 'icons': {c: icon_src(c) for c in names}})


@flask_app.route('/icons/<path:fn>')
def serve_icon(fn):
    if ICONS_DIR.exists():
        return send_from_directory(str(ICONS_DIR), fn)
    return '', 404


# ============ Недавние (стартовый экран) ============
# recent_files.json лежит в той же папке данных, что и roblox_auth.json
# (RSW_DATA_DIR на Android, иначе рядом с app.py). Два вида записей:
#   {'kind': 'file',   'path', 'name', 'opened'}  — локальный .rbxl/.rbxlx
#   {'kind': 'roblox', 'placeId', 'universeId', 'name', 'opened'} — место с Roblox
# Файлы, выбранные через <input type=file>, у сервера без пути на диске, поэтому
# их копия кладётся в recent_files/ (максимум RECENTS_MAX штук, старые чистятся).
RECENTS_MAX = 12
RECENTS_MAX_COPY = 100 * 1024 * 1024


def _recents_dir():
    return Path(os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent))


def _recents_copy_dir():
    return _recents_dir() / 'recent_files'


def _recents_load():
    try:
        d = json.loads((_recents_dir() / 'recent_files.json').read_text(encoding='utf-8'))
        return [e for e in d if isinstance(e, dict) and e.get('kind') in ('file', 'roblox')]
    except Exception:
        return []


def _recents_key(e):
    return ('file', os.path.normcase(str(e.get('path', '')))) if e.get('kind') == 'file' \
        else ('roblox', str(e.get('placeId', '')))


def _recents_save(items):
    """Записывает список и чистит копии загрузок, на которые больше нет ссылок."""
    d = _recents_dir()
    d.mkdir(parents=True, exist_ok=True)
    tmp = d / 'recent_files.json.tmp'
    tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')
    os.replace(tmp, d / 'recent_files.json')
    cd = _recents_copy_dir()
    if cd.is_dir():
        keep = {os.path.normcase(os.path.realpath(e['path'])) for e in items
                if e.get('kind') == 'file' and e.get('path')}
        for f in cd.iterdir():
            if f.is_file() and os.path.normcase(os.path.realpath(f)) not in keep:
                try:
                    f.unlink()
                except Exception:
                    pass


def _recents_add(entry):
    """Не должна ломать основной сценарий: любые ошибки глотаются."""
    try:
        import datetime
        entry['opened'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        items = [e for e in _recents_load() if _recents_key(e) != _recents_key(entry)]
        items.insert(0, entry)
        _recents_save(items[:RECENTS_MAX])
    except Exception:
        traceback.print_exc()


def _recents_add_file(path, name=None):
    p = Path(path)
    if not name:   # повторное открытие: сохраняем прежнее (исходное) имя записи
        key = ('file', os.path.normcase(str(p)))
        name = next((e.get('name') for e in _recents_load() if _recents_key(e) == key), None)
    _recents_add({'kind': 'file', 'path': str(p), 'name': name or p.name})


@flask_app.route('/api/recents/remove', methods=['POST'])
def api_recents_remove():
    """Убрать запись из «недавних» (пункт ⋮ на карточке). Сам файл не удаляется,
    кроме внутренней копии загрузки в recent_files/."""
    body = request.get_json(silent=True) or {}
    kind = body.get('kind')
    if kind not in ('file', 'roblox'):
        return jsonify({'ok': False, 'error': 'kind должен быть file или roblox'}), 400
    probe = {'kind': kind, 'path': body.get('path', ''), 'placeId': body.get('placeId', '')}
    key = _recents_key(probe)
    items = _recents_load()
    kept = [e for e in items if _recents_key(e) != key]
    try:
        _recents_save(kept)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    return jsonify({'ok': True, 'removed': len(items) - len(kept)})


@flask_app.route('/api/recents')
def api_recents():
    """Недавно открытые: локальные файлы (только существующие) и места с Roblox."""
    out = []
    for e in _recents_load():
        if e['kind'] == 'file' and not (e.get('path') and os.path.isfile(e['path'])):
            continue
        out.append(e)
    return jsonify({'ok': True, 'recents': out})


@flask_app.route('/api/open', methods=['POST'])
def api_open():
    body = request.json or {}
    path = body.get('path', '')
    shown = (body.get('name') or '').strip() or None   # настоящее имя файла (Android отдаёт копию imported_<цифры>.rbxl)
    try:
        parsed = parse_rbxl(path)
        state['parsed'] = parsed
        state['file_path'] = path
        _recents_add_file(path, name=shown)
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
        try:   # копия для списка «недавних» (у загрузки нет пути на диске)
            if os.path.getsize(tmp_path) <= RECENTS_MAX_COPY:
                import shutil
                safe = _re.sub(r'[^\w.\- ]', '_', Path(file.filename).name)[:120] or 'place.rbxl'
                cd = _recents_copy_dir()
                cd.mkdir(parents=True, exist_ok=True)
                dst = cd / safe
                shutil.copyfile(tmp_path, dst)
                _recents_add_file(dst, name=Path(file.filename).name)
        except Exception:
            traceback.print_exc()
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


def _rbx_get_place_bytes_cookie(place_id, version=None):
    """Как делает сама Studio: AssetDelivery с сессией аккаунта
    (.ROBLOSECURITY из входа). Работает для мест, которые аккаунт может
    редактировать (свои, группы, Team Create) и для копируемых (uncopylocked).
    Возвращает None, если входа нет."""
    if _roblox_cookie() is None:
        return None
    url = f'https://assetdelivery.roblox.com/v1/asset/?id={int(place_id)}'
    if version:
        url += f'&version={int(version)}'
    r = _req.Request(url, headers=_roblox_headers())
    with _req.urlopen(r, timeout=120) as resp:   # urllib сам идёт по редиректу на CDN
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_place_bytes_key(place_id, version=None):
    """Запасной путь: Open Cloud Asset Delivery с x-api-key (право
    legacy-asset:manage). Возвращает None, если ключ не задан."""
    api_key = _roblox_api_key()
    if not api_key:
        return None
    url = f'https://apis.roblox.com/asset-delivery-api/v1/assetId/{int(place_id)}'
    if version:
        url += f'/version/{int(version)}'
    meta_req = _req.Request(
        url, headers={'x-api-key': api_key, 'Accept': 'application/json',
                      'Accept-Encoding': 'identity'})
    with _req.urlopen(meta_req, timeout=30) as resp:
        meta = json.loads(_rbx_maybe_gunzip(resp.read()).decode('utf-8', 'replace'))
    location = meta.get('location')
    if not location:
        raise RuntimeError(f'Open Cloud ответил без location: {meta}')
    cdn_req = _req.Request(location, headers={'Accept-Encoding': 'gzip'})
    with _req.urlopen(cdn_req, timeout=120) as resp:
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_place_bytes(place_id, version=None):
    """Скачивает файл места. Порядок: вход в аккаунт (как в Studio) →
    Open Cloud-ключ. Возвращает (bytes, способ) или (None, None), если
    не настроено ни то ни другое; если настроено, но всё упало, бросает
    RuntimeError с причинами по каждому способу (+ .status от HTTPError)."""
    errors, status = [], None
    for name, fn in (('вход в аккаунт', _rbx_get_place_bytes_cookie),
                     ('Open Cloud-ключ', _rbx_get_place_bytes_key)):
        try:
            data = fn(place_id, version)
        except _urlerr.HTTPError as e:
            status = status or e.code
            errors.append(f'{name}: HTTP {e.code}')
            continue
        except Exception as e:
            errors.append(f'{name}: {e}')
            continue
        if data is not None:
            return data, name
    if not errors:
        return None, None
    err = RuntimeError('; '.join(errors))
    err.status = status
    raise err


@flask_app.route('/api/roblox/experiences')
def api_roblox_experiences():
    """Список Experiences аккаунта — как стартовый экран Studio (My Recent
    Experiences). develop.roblox.com/v1/user/universes (нужен вход в
    аккаунт; ключ Open Cloud для него не подходит) + иконки с
    thumbnails.roblox.com. Отдаём до 150 штук, свежие изменения сверху.
    ?archived=1 — раздел Archive (архивированные experiences)."""
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'needLogin': True,
                        'error': 'Нужен вход в аккаунт Roblox'}), 401
    archived = 'true' if request.args.get('archived') in ('1', 'true') else 'false'
    items, cursor = [], None
    try:
        for _ in range(3):
            url = ('https://develop.roblox.com/v1/user/universes'
                   f'?isArchived={archived}&limit=50&sortOrder=Desc')
            if cursor:
                url += '&cursor=' + _urlparse.quote(cursor)
            d = _rbx_get_json(url)
            rows = d.get('data', []) if isinstance(d, dict) else (d or [])
            for u in rows:
                if not (u.get('id') and u.get('rootPlaceId')):
                    continue
                items.append({
                    'universeId': u['id'], 'placeId': u['rootPlaceId'],
                    'name': u.get('name') or str(u['id']),
                    'private': (u.get('privacyType') or 'Private') != 'Public',
                    'updated': u.get('updated') or u.get('created') or '',
                    'owner': u.get('creatorName') or '',
                    'icon': None})
            cursor = d.get('nextPageCursor') if isinstance(d, dict) else None
            if not cursor:
                break
    except Exception as e:
        needs = 'HTTP 401' in str(e) or 'HTTP 403' in str(e)
        return jsonify({'ok': False, 'needLogin': needs, 'error': str(e)}), (401 if needs else 502)

    # иконки (необязательны: при ошибке остаются заглушки)
    try:
        for i in range(0, len(items), 50):
            chunk = items[i:i + 50]
            ids = ','.join(str(x['universeId']) for x in chunk)
            d = _rbx_get_json('https://thumbnails.roblox.com/v1/games/icons'
                              f'?universeIds={ids}&returnPolicy=PlaceHolder'
                              '&size=256x256&format=Png&isCircular=false')
            by_id = {r.get('targetId'): r for r in (d.get('data') or [])}
            for x in chunk:
                r = by_id.get(x['universeId'])
                if r and r.get('state') == 'Completed' and r.get('imageUrl'):
                    x['icon'] = r['imageUrl']
    except Exception:
        pass
    items.sort(key=lambda x: x['updated'], reverse=True)
    return jsonify({'ok': True, 'experiences': items})


# === Игры студии на стартовом экране ===
# Список берётся из STUDIO_GAMES_DEFAULT ниже; можно переопределить файлом studio_games.json (в папке данных
# приложения или рядом с app.py). groupId — id группы Roblox: её игры подтянутся автоматически (публичный API),
# games — закреплённые вручную ({"name": "druns", "placeId": 123, "universeId": 456}; universeId необязателен).
STUDIO_GAMES_DEFAULT = {
    'title': None,      # None — заголовок берётся из перевода интерфейса (st_studio); строка — показывается как есть
    'groupId': 0,
    'games': [],
}
# Список подгружается С СЕРВЕРА: JSON в репозитории (поменял файл, закоммитил — у всех обновилось без пересборки APK).
# RSW_STUDIO_URL — своя ссылка; "url" в локальном studio_games.json тоже переопределяет. Нет сети — последняя
# удачно загруженная копия (studio_games.cache.json в папке данных), потом то, что зашито выше.
STUDIO_GAMES_URL = os.environ.get('RSW_STUDIO_URL') or \
    'https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/studio_games.json'
_STUDIO_REMOTE = {'at': 0.0, 'cfg': None}


def _studio_remote_config(url):
    """Конфиг с сервера с кэшем на 5 минут и запасной копией на диске. Возвращает dict или None."""
    now = time.time()
    if _STUDIO_REMOTE['cfg'] is not None and now - _STUDIO_REMOTE['at'] < 300:
        return _STUDIO_REMOTE['cfg']
    cache_file = _recents_dir() / 'studio_games.cache.json'
    cfg = None
    try:
        r = _req.Request(url, headers={'User-Agent': 'RbxStudioWeb', 'Accept': 'application/json',
                                       'Cache-Control': 'no-cache'})
        with _req.urlopen(r, timeout=6) as resp:
            data = json.loads(_rbx_maybe_gunzip(resp.read()).decode('utf-8', 'replace'))
        if isinstance(data, dict):
            cfg = data
            try:
                cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            except Exception:
                pass
    except Exception:
        try:
            if cache_file.is_file():
                data = json.loads(cache_file.read_text(encoding='utf-8'))
                if isinstance(data, dict):
                    cfg = data
        except Exception:
            pass
    _STUDIO_REMOTE['at'] = now
    _STUDIO_REMOTE['cfg'] = cfg
    return cfg


def _studio_config():
    """Порядок (каждый следующий перекрывает предыдущий): зашитое в app.py → studio_games.json рядом с app.py (из репозитория)
    → список с сервера → ручной studio_games.json в папке данных приложения (если она задана отдельно, RSW_DATA_DIR)."""
    def read(f):
        try:
            if f.is_file():
                d = json.loads(f.read_text(encoding='utf-8'))
                return d if isinstance(d, dict) else {}
        except Exception:
            traceback.print_exc()
        return {}

    cfg = dict(STUDIO_GAMES_DEFAULT)
    baked = read(Path(__file__).parent / 'studio_games.json')
    override = {}
    if os.environ.get('RSW_DATA_DIR'):
        override = read(Path(os.environ['RSW_DATA_DIR']) / 'studio_games.json')
    cfg.update(baked)
    remote = _studio_remote_config(override.get('url') or baked.get('url') or STUDIO_GAMES_URL)
    if remote:
        cfg.update(remote)
    cfg.update(override)
    return cfg


@flask_app.route('/api/studio/games')
def api_studio_games():
    cfg = _studio_config()
    items, seen = [], set()

    def add(name, place_id, universe_id=None, updated='', owner=''):
        try:
            place_id = int(place_id)
        except Exception:
            return
        key = ('u', int(universe_id)) if universe_id else ('p', place_id)
        if key in seen:
            return
        seen.add(key)
        items.append({'name': str(name or place_id), 'placeId': place_id,
                      'universeId': int(universe_id) if universe_id else '',
                      'updated': updated or '', 'owner': owner or '', 'icon': None})

    for g in (cfg.get('games') or []):
        if isinstance(g, dict) and g.get('placeId'):
            add(g.get('name'), g.get('placeId'), g.get('universeId'))

    group_id = cfg.get('groupId') or 0
    group_err = None
    if group_id:
        try:
            url = (f'https://games.roblox.com/v2/groups/{int(group_id)}/games'
                   '?accessFilter=2&limit=50&sortOrder=Asc')
            d = _rbx_get_json(url)
            for u in (d.get('data') or []):
                root = (u.get('rootPlace') or {}).get('id')
                if u.get('id') and root:
                    add(u.get('name'), root, u.get('id'), u.get('updated') or u.get('created') or '',
                        (u.get('creator') or {}).get('name') or '')
        except Exception as e:
            group_err = str(e)

    # иконки (необязательны)
    try:
        with_u = [x for x in items if x['universeId']]
        for i in range(0, len(with_u), 50):
            chunk = with_u[i:i + 50]
            ids = ','.join(str(x['universeId']) for x in chunk)
            d = _rbx_get_json('https://thumbnails.roblox.com/v1/games/icons'
                              f'?universeIds={ids}&returnPolicy=PlaceHolder'
                              '&size=256x256&format=Png&isCircular=false')
            by_id = {r.get('targetId'): r for r in (d.get('data') or [])}
            for x in chunk:
                r = by_id.get(x['universeId'])
                if r and r.get('state') == 'Completed' and r.get('imageUrl'):
                    x['icon'] = r['imageUrl']
    except Exception:
        pass
    return jsonify({'ok': True, 'title': cfg.get('title') or None, 'games': items,
                    'configured': bool(group_id or cfg.get('games')), 'groupError': group_err})


_DOH_CACHE = {}


def _doh_resolve(host):
    """A-запись через DNS-over-HTTPS (обходит сломанный системный DNS)."""
    if host in _DOH_CACHE:
        return _DOH_CACHE[host]
    last = None
    for url in ('https://1.1.1.1/dns-query?name=%s&type=A' % host,
                'https://8.8.8.8/resolve?name=%s&type=A' % host,
                'https://dns.google/resolve?name=%s&type=A' % host):
        try:
            rq = _req.Request(url, headers={'Accept': 'application/dns-json'})
            with _req.urlopen(rq, timeout=8) as resp:
                d = json.loads(resp.read().decode('utf-8', 'replace'))
            ips = [a['data'] for a in d.get('Answer', []) if a.get('type') == 1]
            if ips:
                _DOH_CACHE[host] = ips
                return ips
            last = 'нет A-записей'
        except Exception as e:
            last = repr(e)
    raise RuntimeError('DoH не сработал: ' + str(last))


def _fetch_via_doh(pu, hdr):
    import socket as _sock, ssl as _ssl, http.client as _hc
    host = pu.hostname
    path = (pu.path or '/') + ('?' + pu.query if pu.query else '')
    err = None
    for ip in _doh_resolve(host):
        try:
            class _IPConn(_hc.HTTPSConnection):
                def connect(self_):
                    sk = _sock.create_connection((ip, 443), 15)
                    self_.sock = self_._context.wrap_socket(sk, server_hostname=host)
            conn = _IPConn(host, timeout=15, context=_ssl.create_default_context())
            h = dict(hdr)
            h['Host'] = host
            conn.request('GET', path, headers=h)
            r = conn.getresponse()
            data = r.read()
            if r.status != 200:
                raise RuntimeError('HTTP %d' % r.status)
            return r.getheader('Content-Type', 'image/png'), data
        except Exception as e:
            err = e
    raise RuntimeError(repr(err))


_THUMB_CACHE = {}
_THUMB_CACHE_MAX = 400


@flask_app.route('/api/roblox/thumb')
def api_roblox_thumb():
    """Прокси иконок experiences. WebView/браузер часто не может сам
    открыть tr.rbxcdn.com (блокировка, нет VPN у приложения), хотя сервер
    до Roblox достаёт — поэтому картинку отдаём с нашего же origin.
    Разрешены только https-хосты *.rbxcdn.com (защита от SSRF)."""
    u = request.args.get('u', '')
    try:
        pu = _urlparse.urlparse(u)
    except Exception:
        return Response('bad url', status=400)
    host = (pu.hostname or '').lower()
    if pu.scheme != 'https' or not (host == 'rbxcdn.com' or host.endswith('.rbxcdn.com')):
        return Response('host not allowed', status=400)
    hit = _THUMB_CACHE.get(u)
    if hit:
        ct, data = hit
    else:
        hdr = dict(ROBLOX_HEADERS_BASE)       # без куки: CDN она не нужна
        hdr['Referer'] = 'https://www.roblox.com/'
        hdr['Accept'] = 'image/avif,image/webp,image/png,image/*;q=0.8'
        hdr.pop('Accept-Encoding', None)      # отдаём картинку как есть, без gzip
        try:
            r = _req.Request(u, headers=hdr)
            with _req.urlopen(r, timeout=15) as resp:
                data = resp.read()
                ct = resp.headers.get('Content-Type', 'image/png')
        except Exception as e1:
            # Часто rbxcdn.com не резолвится системным DNS (gaierror) —
            # тогда резолвим сами через DNS-over-HTTPS и ходим по IP.
            try:
                ct, data = _fetch_via_doh(pu, hdr)
            except Exception as e2:
                print('[thumb] FAIL', u, '->', repr(e1), '| DoH:', repr(e2))
                return Response('thumb fetch failed: ' + repr(e1) + ' | DoH: ' + repr(e2), status=502)
        if len(_THUMB_CACHE) >= _THUMB_CACHE_MAX:
            _THUMB_CACHE.pop(next(iter(_THUMB_CACHE)))
        _THUMB_CACHE[u] = (ct, data)
    resp = Response(data, mimetype=ct)
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


@flask_app.route('/api/roblox/experience/places')
def api_roblox_experience_places():
    """Места внутри Experience (у многих одно — тогда клиент открывает его сразу)."""
    um = _re.search(r'\d+', request.args.get('universeId', ''))
    if not um:
        return jsonify({'ok': False, 'error': 'universeId должен быть числом'}), 400
    root = request.args.get('rootPlaceId', '')
    try:
        d = _rbx_get_json(f'https://develop.roblox.com/v1/universes/{um.group()}'
                          '/places?limit=100&sortOrder=Asc')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502
    rows = d.get('data', []) if isinstance(d, dict) else (d or [])
    places = [{'id': r.get('id'), 'name': r.get('name') or str(r.get('id')),
               'root': str(r.get('id')) == root} for r in rows if r.get('id')]
    return jsonify({'ok': True, 'places': places})


@flask_app.route('/api/open/place', methods=['POST'])
def api_open_place():
    """Скачать место с Roblox по Place ID и открыть его в редакторе.
    Тело: {place_id, version?}. Сначала используется вход в аккаунт
    (как в Studio), если его нет или он не сработал — Open Cloud-ключ.
    Результат открывается так же, как /api/open/upload; публикация
    обратно — обычный /api/publish."""
    import tempfile
    body = request.get_json(silent=True) or {}
    m = _re.search(r'\d+', str(body.get('place_id', '')))
    if not m:
        return jsonify({'ok': False, 'error': 'Нужен числовой Place ID'}), 400
    place_id = int(m.group())
    vm = _re.search(r'\d+', str(body.get('version', '') or ''))
    version = int(vm.group()) if vm else None

    try:
        data, via = _rbx_get_place_bytes(place_id, version)
    except Exception as e:
        hints = {
            401: 'вход не принят или истёк — войди в аккаунт заново',
            403: 'нет доступа к месту: нужен аккаунт с правом редактирования '
                 '(владелец, группа, Team Create) или копируемое место',
            404: 'место или версия не найдены',
        }
        st = getattr(e, 'status', None)
        msg = str(e) + ((' — ' + hints[st]) if st in hints else '')
        return jsonify({'ok': False, 'status': st, 'error': msg}), 502
    if data is None:
        return jsonify({'ok': False,
                        'error': 'Войди в аккаунт Roblox (кнопка Account) '
                                 'или сохрани Open Cloud API-ключ'}), 400

    # .rbxl — бинарный ('<roblox!'), .rbxlx — XML ('<roblox ' / '<?xml').
    # Всё остальное — не файл места (например, JSON с ошибкой): state не трогаем.
    if data[:8] == b'<roblox!':
        suffix = '.rbxl'
    elif data[:7] == b'<roblox' or data[:5] == b'<?xml':
        suffix = '.rbxlx'
    else:
        return jsonify({'ok': False,
                        'error': f'Ответ не похож на файл места ({len(data)} байт, '
                                 f'начало: {data[:40]!r})'}), 502
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parsed = parse_rbxl(tmp_path)
        state['parsed'] = parsed
        state['file_path'] = None   # как у upload: Ctrl+S откроет «Сохранить как»
        universe_id = None
        um = _re.search(r'\d+', str(body.get('universe_id', '') or ''))
        if um:
            universe_id = int(um.group())
        else:
            try:   # Place ID -> Universe ID (публичный эндпоинт), нужен для Publish
                d = _rbx_get_json(f'https://apis.roblox.com/universes/v1/places/{place_id}/universe')
                if isinstance(d, dict) and d.get('universeId'):
                    universe_id = int(d['universeId'])
            except Exception:
                pass
        _recents_add({'kind': 'roblox', 'placeId': place_id, 'universeId': universe_id,
                      'name': (str(body.get('name') or '').strip()[:100] or f'Place {place_id}')})
        return jsonify({'ok': True, 'count': len(parsed['referent_to_class']),
                        'place_id': place_id, 'universe_id': universe_id,
                        'bytes': len(data), 'via': via})
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Скачано {len(data)} байт, но не разобралось как .rbxl: {e}'}), 400
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# ============ Шаблон «Baseplate» для кнопки New ============
# Встроен в код (base64 от BASEPLATE.rbxl), а не лежит отдельным файлом: так он
# одинаково доступен на десктопе, в Android-APK и в OTA-обновлениях (там __file__
# указывает в другую папку, а sync-android-python.sh копирует только список файлов).
# Хочешь свой шаблон без правки кода — положи templates/Baseplate.rbxl рядом с app.py:
# если файл есть, берётся он.
_BASEPLATE_B64 = (
    "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"
    "BwAAAEVuYWJsZWQCAVBST1AdAAAAIgAAAAAAAAD2BAMAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AYAAAAFgAAAAAAAADw"
    "BwMAAAAJAAAASW50ZW5zaXR5BH8AAABQUk9QGAAAABYAAAAAAAAA8AcDAAAABAAAAE5hbWUBBQAAAEJsb29tUFJPUBMAAAARAAAA"
    "AAAAAPACAwAAAAQAAABTaXplBIOAAABQUk9QIAAAAB4AAAAAAAAA8A8DAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9Q"
    "EwAAABEAAAAAAAAA8AIDAAAABAAAAFRhZ3McAAAAAFBST1AYAAAAFgAAAAAAAADwBwMAAAAJAAAAVGhyZXNob2xkBIAAAABQUk9Q"
    "IwAAACEAAAAAAAAA8BIDAAAACAAAAFVuaXF1ZUlkHwAAA/IKzaP3L0NehuZWXFpQUk9QKgAAACgAAAAAAAAA8BkEAAAACwAAAEFk"
    "b3JuZWVOYW1lARAAAABIdW1hbm9pZFJvb3RQYXJ0UFJPUCIAAAAgAAAAAAAAAPARBAAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXpl"
    "AQAAAABQUk9QJwAAACUAAAAAAAAA8BYEAAAAEAAAAEJhY2tncm91bmRDb2xvcjMMfvX19n719fZ+9fX2UFJPUCkAAAAnAAAAAAAA"
    "APAYBAAAABYAAABCYWNrZ3JvdW5kVHJhbnNwYXJlbmN5BZqZmZmZmbk/UFJPUB0AAAAbAAAAAAAAAPAMBAAAAA4AAABCdWJibGVE"
    "dXJhdGlvbgSC4AAAUFJPUB0AAAAbAAAAAAAAAPAMBAAAAA4AAABCdWJibGVzU3BhY2luZwSBgAAAUFJPUB8AAAAdAAAAAAAAAPAO"
    "BAAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4EAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMC"
    "AFBST1ATAAAAEQAAAAAAAADwAgQAAAAHAAAARW5hYmxlZAIBUFJPUBEAAAARAAAAAAAAAEAEAAAABACQRm9udBIAAAAvUFJPUFcA"
    "AABtAAAAAAAAAP80BAAAAAgAAABGb250RmFjZSAqAAAAcmJ4YXNzZXQ6Ly9mb250cy9mYW1pbGllcy9CdWlsZGVyU2Fucy5qc29u"
    "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"
    "AAAAIAAAAAAAAADwEQcAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUCcAAAAlAAAAAAAAAPAWBwAAABAAAABCYWNr"
    "Z3JvdW5kQ29sb3IzDHuRkZJ7sbGye9HR0lBST1ApAAAAJwAAAAAAAADwGAcAAAAWAAAAQmFja2dyb3VuZFRyYW5zcGFyZW5jeQUA"
    "AAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDgcAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAOBwAA"
    "ABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QEQAAABEAAAAAAAAAQAcAAAAEAJBFbmFibGVkAgBQUk9QVQAAAGsAAAAAAAAA"
    "/zQHAAAACAAAAEZvbnRGYWNlICoAAAByYnhhc3NldDovL2ZvbnRzL2ZhbWlsaWVzL0J1aWxkZXJTYW5zLmpzb268AgAlMQABBygA"
    "kC1Cb2xkLm90ZlBST1AdAAAAIgAAAAAAAAD2BAcAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AsAAAAKgAAAAAAAADwGwcA"
    "AAAVAAAASG92ZXJCYWNrZ3JvdW5kQ29sb3IzDH319fZ99fX2ffX19lBST1ArAAAAKQAAAAAAAADwGgcAAAAEAAAATmFtZQEYAAAA"
    "Q2hhbm5lbFRhYnNDb25maWd1cmF0aW9uUFJPUCwAAAAqAAAAAAAAAPAbBwAAABUAAABTZWxlY3RlZFRhYlRleHRDb2xvcjMMfwAA"
    "AH8AAAB/AAAAUFJPUCAAAAAeAAAAAAAAAPAPBwAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAABUFJPUBMAAAARAAAAAAAAAPAC"
    "BwAAAAQAAABUYWdzHAAAAABQUk9QIQAAAB8AAAAAAAAA8BAHAAAACgAAAFRleHRDb2xvcjMMfl9fYH5fX2B+X19gUFJPUBsAAAAZ"
    "AAAAAAAAAPAKBwAAAAgAAABUZXh0U2l6ZRsAAAAAAAAAJFBST1AnAAAAJQAAAAAAAADwFgcAAAAQAAAAVGV4dFN0cm9rZUNvbG9y"
    "MwwAAAAAAAAAAAAAAABQUk9QKQAAACcAAAAAAAAA8BgHAAAAFgAAAFRleHRTdHJva2VUcmFuc3BhcmVuY3kFAAAAAAAA8D9QUk9Q"
    "IwAAACEAAAAAAAAA8BIHAAAACAAAAFVuaXF1ZUlkHwAAA/sKzaP3L0NehuZWXFpQUk9QIgAAACAAAAAAAAAA8BEIAAAAEwAAAEF0"
    "dHJpYnV0ZXNTZXJpYWxpemUBAAAAAFBST1AdAAAAGwAAAAAAAADwDAgAAAARAAAAQnViYmxlQ2hhdEVuYWJsZWQCAVBST1AfAAAA"
    "HQAAAAAAAADwDggAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAOCAAAABMAAABEZWZpbmVzQ2Fw"
    "YWJpbGl0aWVzAgBQUk9QHQAAACIAAAAAAAAA9gQIAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QGgAAABgAAAAAAAAA8AkI"
    "AAAADgAAAElzQXV0b01pZ3JhdGVkAgBQUk9QGwAAABkAAAAAAAAA8AoIAAAADwAAAExvYWREZWZhdWx0Q2hhdAIBUFJPUBcAAAAV"
    "AAAAAAAAAPAGCAAAAAQAAABOYW1lAQQAAABDaGF0UFJPUCAAAAAeAAAAAAAAAPAPCAAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAA"
    "AAABUFJPUBMAAAARAAAAAAAAAPACCAAAAAQAAABUYWdzHAAAAABQUk9QIgAAACEAAAAAAAAAQAgAAAAEAPAKVW5pcXVlSWQfAAAD"
    "fQrNo/cvQ16G5lZcWlBST1AiAAAAIAAAAAAAAADwEQkAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAA"
    "AAAAAPAOCQAAABMAAABBdXRvY29tcGxldGVFbmFibGVkAgFQUk9QJwAAACUAAAAAAAAA8BYJAAAAEAAAAEJhY2tncm91bmRDb2xv"
    "cjMMe5GRknuxsbJ70dHSUFJPUCkAAAAnAAAAAAAAAPAYCQAAABYAAABCYWNrZ3JvdW5kVHJhbnNwYXJlbmN5BZqZmZmZmck/UFJP"
    "UB8AAAAdAAAAAAAAAPAOCQAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4JAAAAEwAAAERlZmlu"
    "ZXNDYXBhYmlsaXRpZXMCAFBST1ATAAAAEQAAAAAAAADwAgkAAAAHAAAARW5hYmxlZAIBUFJPUFcAAABtAAAAAAAAAP80CQAAAAgA"
    "AABGb250RmFjZSAqAAAAcmJ4YXNzZXQ6Ly9mb250cy9mYW1pbGllcy9CdWlsZGVyU2Fucy5qc29u9AEAJzEAAQcoALAtTWVkaXVt"
    "Lm90ZlBST1AbAAAAIgAAAAAAAABACQAAAAQAtkhpc3RvcnlJZB8AAQBQAAAAAABQUk9QHgAAABwAAAAAAAAA8A0JAAAADwAAAEtl"
    "eWJvYXJkS2V5Q29kZRIAAAAvUFJPUCwAAAAqAAAAAAAAAPAbCQAAAAQAAABOYW1lARkAAABDaGF0SW5wdXRCYXJDb25maWd1cmF0"
    "aW9uUFJPUCgAAAAmAAAAAAAAAPAXCQAAABEAAABQbGFjZWhvbGRlckNvbG9yMwx+ZWVmfmVlZn5lZWZQUk9QIAAAAB4AAAAAAAAA"
    "8A8JAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIJAAAABAAAAFRhZ3McAAAAAFBST1AgAAAA"
    "HgAAAAAAAADwDwkAAAARAAAAVGFyZ2V0VGV4dENoYW5uZWwTAAAAAVBST1AhAAAAHwAAAAAAAADwEAkAAAAKAAAAVGV4dENvbG9y"
    "Mwx/AAAAfwAAAH8AAABQUk9QGwAAABkAAAAAAAAA8AoJAAAACAAAAFRleHRTaXplGwAAAAAAAAAkUFJPUCcAAAAlAAAAAAAAAPAW"
    "CQAAABAAAABUZXh0U3Ryb2tlQ29sb3IzDAAAAAAAAAAAAAAAAFBST1ApAAAAJwAAAAAAAADwGAkAAAAWAAAAVGV4dFN0cm9rZVRy"
    "YW5zcGFyZW5jeQUAAAAAAADgP1BST1AjAAAAIQAAAAAAAADwEgkAAAAIAAAAVW5pcXVlSWQfAAAD9QrNo/cvQ16G5lZcWlBST1Ai"
    "AAAAIAAAAAAAAADwEQoAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUCcAAAAlAAAAAAAAAPAWCgAAABAAAABCYWNr"
    "Z3JvdW5kQ29sb3IzDHuRkZJ7sbGye9HR0lBST1ApAAAAJwAAAAAAAADwGAoAAAAWAAAAQmFja2dyb3VuZFRyYW5zcGFyZW5jeQUz"
    "MzMzMzPTP1BST1AfAAAAHQAAAAAAAADwDgoAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAOCgAA"
    "ABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QEwAAABEAAAAAAAAA8AIKAAAABwAAAEVuYWJsZWQCAVBST1BXAAAAbQAAAAAA"
    "AAD/NAoAAAAIAAAARm9udEZhY2UgKgAAAHJieGFzc2V0Oi8vZm9udHMvZmFtaWxpZXMvQnVpbGRlclNhbnMuanNvbvQBACcxAAEH"
    "KACwLU1lZGl1bS5vdGZQUk9QGgAAABgAAAAAAAAA8AkKAAAACwAAAEhlaWdodFNjYWxlBH8AAABQUk9QHQAAACIAAAAAAAAA9gQK"
    "AAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QIgAAACAAAAAAAAAA8BEKAAAAEwAAAEhvcml6b250YWxBbGlnbm1lbnQSAAAA"
    "AVBST1AqAAAAKAAAAAAAAADwGQoAAAAEAAAATmFtZQEXAAAAQ2hhdFdpbmRvd0NvbmZpZ3VyYXRpb25QUk9QIAAAAB4AAAAAAAAA"
    "8A8KAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIKAAAABAAAAFRhZ3McAAAAAFBST1AlAAAA"
    "IwAAAAAAAADwFAoAAAAWAAAAVGV4dENoYW5uZWxEaXNwbGF5TW9kZRIAAAAAUFJPUCAAAAAfAAAAAAAAAEAKAAAABADwCFRleHRD"
    "b2xvcjMMfwAAAH8AAAB/AAAAUFJPUBsAAAAZAAAAAAAAAPAKCgAAAAgAAABUZXh0U2l6ZRsAAAAAAAAAJFBST1AnAAAAJQAAAAAA"
    "AADwFgoAAAAQAAAAVGV4dFN0cm9rZUNvbG9yMwwAAAAAAAAAAAAAAABQUk9QKQAAACcAAAAAAAAA8BgKAAAAFgAAAFRleHRTdHJv"
    "a2VUcmFuc3BhcmVuY3kFAAAAAAAA4D9QUk9QIwAAACEAAAAAAAAA8BIKAAAACAAAAFVuaXF1ZUlkHwAAA/QKzaP3L0NehuZWXFpQ"
    "Uk9QIAAAAB4AAAAAAAAA8A8KAAAAEQAAAFZlcnRpY2FsQWxpZ25tZW50EgAAAAFQUk9QGAAAABcAAAAAAAAAQAoAAAAEAPAAV2lk"
    "dGhTY2FsZQR/AAAAUFJPUCIAAAAgAAAAAAAAAPARCwAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAA"
    "AAAA8A4LAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDgsAAAATAAAARGVmaW5lc0NhcGFiaWxp"
    "dGllcwIAUFJPUB0AAAAiAAAAAAAAAPYECwAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUCQAAAAiAAAAAAAAAPATCwAAAAQA"
    "AABOYW1lAREAAABDb2xsZWN0aW9uU2VydmljZVBST1AgAAAAHgAAAAAAAADwDwsAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAA"
    "AVBST1ATAAAAEQAAAAAAAADwAgsAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASCwAAAAgAAABVbmlxdWVJZB8AAANo"
    "Cs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARDAAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHgAAAB0AAAAA"
    "AAAAQAwAAAAEAPAGQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAODAAAABMAAABEZWZpbmVzQ2FwYWJpbGl0"
    "aWVzAgBQUk9QHQAAACIAAAAAAAAA9gQMAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QJwAAACUAAAAAAAAA8BYMAAAABAAA"
    "AE5hbWUBFAAAAENvbnRleHRBY3Rpb25TZXJ2aWNlUFJPUCAAAAAeAAAAAAAAAPAPDAAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAA"
    "AAABUFJPUBMAAAARAAAAAAAAAPACDAAAAAQAAABUYWdzHAAAAABQUk9QIwAAACEAAAAAAAAA8BIMAAAACAAAAFVuaXF1ZUlkHwAA"
    "A6QKzaP3L0NehuZWXFpQUk9QIgAAACAAAAAAAAAA8BENAAAAEwAAAEF0dHJpYnV0ZXNTZXJpYWxpemUBAAAAAFBST1AfAAAAHQAA"
    "AAAAAADwDg0AAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAODQAAABMAAABEZWZpbmVzQ2FwYWJp"
    "bGl0aWVzAgBQUk9QHQAAACIAAAAAAAAA9gQNAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QIQAAAB8AAAAAAAAA8BANAAAA"
    "BAAAAE5hbWUBDgAAAENvb2tpZXNTZXJ2aWNlUFJPUB8AAAAeAAAAAAAAAEANAAAABADwB1NvdXJjZUFzc2V0SWQbAAAAAAAAAAFQ"
    "Uk9QEwAAABEAAAAAAAAA8AINAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEg0AAAAIAAAAVW5pcXVlSWQfAAADngrN"
    "o/cvQ16G5lZcWlBST1AiAAAAIAAAAAAAAADwEQ4AAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUBkAAAAYAAAAAAAA"
    "AEAOAAAABADwAUF1dG9tYXRpY1JldHJ5AgFQUk9QHwAAAB0AAAAAAAAA8A4OAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBS"
    "T1AfAAAAHQAAAAAAAADwDg4AAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEDgAAAAkAAABIaXN0"
    "b3J5SWQfAAEAUAAAAAAAUFJPUB4AAAAcAAAAAAAAAPANDgAAABIAAABMZWdhY3lOYW1pbmdTY2hlbWUCAFBST1AjAAAAIQAAAAAA"
    "AADwEg4AAAAEAAAATmFtZQEQAAAARGF0YVN0b3JlU2VydmljZVBST1AgAAAAHgAAAAAAAADwDw4AAAANAAAAU291cmNlQXNzZXRJ"
    "ZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAg4AAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASDgAAAAgAAABVbmlx"
    "dWVJZB8AAAPcCs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARDwAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9Q"
    "HwAAAB0AAAAAAAAA8A4PAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDg8AAAATAAAARGVmaW5l"
    "c0NhcGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEDwAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBcAAAAVAAAAAAAA"
    "APAGDwAAAAgAAABNYXhJdGVtcwMAAAfQUFJPUBkAAAAXAAAAAAAAAPAIDwAAAAQAAABOYW1lAQYAAABEZWJyaXNQUk9QIAAAAB4A"
    "AAAAAAAA8A8PAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIPAAAABAAAAFRhZ3McAAAAAFBS"
    "T1AjAAAAIQAAAAAAAADwEg8AAAAIAAAAVW5pcXVlSWQfAAADnQrNo/cvQ16G5lZcWlBST1AiAAAAIAAAAAAAAADwERAAAAATAAAA"
    "QXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUBgAAAAWAAAAAAAAAPAHEAAAAAwAAABBdXRvTG9jYWxpemUCAVBST1AfAAAAHQAA"
    "AAAAAADwDhAAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB0AAAAbAAAAAAAAAPAMEAAAAAYAAABDb2xvcjMMfwAAAH8A"
    "AAB/AAAAUFJPUB8AAAAdAAAAAAAAAPAOEAAAABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QJwAAACwAAAAAAAAA9g4QAAAA"
    "EwAAAEVtaXNzaXZlTWFza0NvbnRlbnQiAAEAUAAAAAAAUFJPUB4AAAAdAAAAAAAAAEAQAAAABADwBkVtaXNzaXZlU3RyZW5ndGgE"
    "fwAAAFBST1AjAAAAIQAAAAAAAADwEhAAAAAMAAAARW1pc3NpdmVUaW50DH8AAAB/AAAAfwAAAFBST1ATAAAAEQAAAAAAAADwAhAA"
    "AAAEAAAARmFjZRIAAAABUFJPUB0AAAAiAAAAAAAAAPYEEAAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBsAAAAZAAAAAAAA"
    "APAKEAAAAAwAAABNZXRhbG5lc3NNYXABAAAAAFBST1AYAAAAFgAAAAAAAADwBxAAAAAEAAAATmFtZQEFAAAARGVjYWxQUk9QGAAA"
    "ABYAAAAAAAAA8AcQAAAACQAAAE5vcm1hbE1hcAEAAAAAUFJPUBcAAAAVAAAAAAAAAPAGEAAAAAgAAABSb3RhdGlvbgQAAAAAUFJP"
    "UBsAAAAZAAAAAAAAAPAKEAAAAAwAAABSb3VnaG5lc3NNYXABAAAAAFBST1AgAAAAHgAAAAAAAADwDxAAAAANAAAAU291cmNlQXNz"
    "ZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAhAAAAAEAAAAVGFncxwAAAAAUFJPUDkAAAA5AAAAAAAAAPIREAAAAAcAAABU"
    "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"
    "ZWxlY3Rpb25CZWhhdmlvckRvd24SAAAAAFBST1AjAAAAIgAAAAAAAABAFQAAAAQA8AtTZWxlY3Rpb25CZWhhdmlvckxlZnQSAAAA"
    "AFBST1AlAAAAIwAAAAAAAADwFBUAAAAWAAAAU2VsZWN0aW9uQmVoYXZpb3JSaWdodBIAAAAAUFJPUCIAAAAgAAAAAAAAAPARFQAA"
    "ABMAAABTZWxlY3Rpb25CZWhhdmlvclVwEgAAAABQUk9QGgAAABgAAAAAAAAA8AkVAAAADgAAAFNlbGVjdGlvbkdyb3VwAgBQUk9Q"
    "IwAAACEAAAAAAAAA8BIVAAAAFAAAAFNlbGVjdGlvbkltYWdlT2JqZWN0EwAAAAFQUk9QHQAAABsAAAAAAAAA8AwVAAAADgAAAFNl"
    "bGVjdGlvbk9yZGVyAwAAAABQUk9QEwAAABEAAAAAAAAA8AIVAAAABAAAAFNpbmsSAAAAAFBST1AXAAAAHQAAAAAAAADmFQAAAAQA"
    "AABTaXplBwABAFDIAAAAyFBST1AdAAAAGwAAAAAAAADwDBUAAAAOAAAAU2l6ZUNvbnN0cmFpbnQSAAAAAFBST1AfAAAAJAAAAAAA"
    "AAD2BhUAAAALAAAAU2xpY2VDZW50ZXIYAAEAUAAAAAAAUFJPUBkAAAAXAAAAAAAAAPAIFQAAAAoAAABTbGljZVNjYWxlBH8AAABQ"
    "Uk9QIAAAAB4AAAAAAAAA8A8VAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIVAAAABAAAAFRh"
    "Z3McAAAAAFBST1AiAAAAIQAAAAAAAADwBhUAAAAIAAAAVGlsZVNpemUHfwAAAAQAgAAAAAAAAAAAUFJPUCMAAAAhAAAAAAAAAPAS"
    "FQAAAAgAAABVbmlxdWVJZB8AAAP4Cs2j9y9DXobmVlxaUFJPUBMAAAARAAAAAAAAAPACFQAAAAcAAABWaXNpYmxlAgFQUk9QFQAA"
    "ABMAAAAAAAAA8AQVAAAABgAAAFpJbmRleAMAAAACUFJPUCEAAAAfAAAAAAAAAPAQFgAAABUAAABBbGxvd0luc2VydEZyZWVNb2Rl"
    "bHMCAFBST1AiAAAAIAAAAAAAAADwERYAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOFgAA"
    "AAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4WAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBS"
    "T1AdAAAAIgAAAAAAAAD2BBYAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AgAAAAHgAAAAAAAADwDxYAAAAEAAAATmFtZQEN"
    "AAAASW5zZXJ0U2VydmljZVBST1AgAAAAHgAAAAAAAADwDxYAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAA"
    "AAAAAADwAhYAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASFgAAAAgAAABVbmlxdWVJZB8AAAObCs2j9y9DXobmVlxa"
    "UFJPUCcAAAAsAAAAAAAAAPYOFwAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQABAFAAAAAAAFBST1AhAAAANQAAAAAAAAD/BxcA"
    "AAAMAAAAQ2FwYWJpbGl0aWVzIQABAAdQAAAAAABQUk9QIgAAACAAAAAAAAAA8BEXAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMC"
    "AAAAAFBST1AeAAAAUgAAAAAAAAD/BBcAAAAJAAAASGlzdG9yeUlkHwABACdQAAAAAABQUk9QLQAAAGEAAAAAAAAA/xMXAAAABAAA"
    "AE5hbWUBEQAAAEZpbHRlcmVkU2VsZWN0aW9uFQAnUGN0aW9uUFJPUCIAAAA2AAAAAAAAAP8IFwAAAA0AAABTb3VyY2VBc3NldElk"
    "GwABAAdQAAEBAQFQUk9QFwAAAB0AAAAAAAAA5hcAAAAEAAAAVGFncxwAAQBQAAAAAABQUk9QUAAAAFEAAAAAAAAA8wMXAAAACAAA"
    "AFVuaXF1ZUlkHwABAPApBAQEBEJDREUKCgoKzc3NzaOjo6P39/f3Ly8vL0NDQ0NeXl5ehoaGhubm5uZWVlZWXFxcXFpaWlpQUk9Q"
    "HgAAABwAAAAAAAAA8A0YAAAABwAAAEFtYmllbnQMfRkZGn0ZGRp9GRkaUFJPUHEAAAB5AAAAAAAAAPNCGAAAABMAAABBdHRyaWJ1"
    "dGVzU2VyaWFsaXplAVkAAAACAAAAJgAAAFJCWF9MaWdodGluZ1RlY2hub2xvZ3lVbmlmaWVkTWlncmF0aW9uAwEgLACGT3JpZ2lu"
    "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"
    "ABAAAABDZXJhbWljVGlsZXNOYW1lAQwVAFBUaWxlc1BST1AlAAAAKwAAAAAAAAD3DBwAAAARAAAAQ2xheVJvb2ZUaWxlc05hbWUB"
    "DRYAUFRpbGVzUFJPUCMAAAAnAAAAAAAAAPUKHAAAAA8AAABDb2JibGVzdG9uZU5hbWUBCxQAUHN0b25lUFJPUCMAAAAhAAAAAAAA"
    "APASHAAAAAwAAABDb25jcmV0ZU5hbWUBCAAAAENvbmNyZXRlUFJPUCUAAAArAAAAAAAAAPcMHAAAABEAAABDb3Jyb2RlZE1ldGFs"
    "TmFtZQENFgBQTWV0YWxQUk9QIwAAACcAAAAAAAAA9QocAAAADwAAAENyYWNrZWRMYXZhTmFtZQELFABQZExhdmFQUk9QHwAAAB0A"
    "AAAAAAAA8A4cAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1AkAAAAKQAAAAAAAAD2CxwAAAAQAAAARGlhbW9uZFBsYXRl"
    "TmFtZQEMFQBQUGxhdGVQUk9QHwAAAB0AAAAAAAAA8A4cAAAACgAAAEZhYnJpY05hbWUBBgAAAEZhYnJpY1BST1AbAAAAGQAAAAAA"
    "AADwChwAAAAIAAAARm9pbE5hbWUBBAAAAEZvaWxQUk9QIQAAAB8AAAAAAAAA8BAcAAAACwAAAEdsYWNpZXJOYW1lAQcAAABHbGFj"
    "aWVyUFJPUCEAAAAfAAAAAAAAAPAQHAAAAAsAAABHcmFuaXRlTmFtZQEHAAAAR3Jhbml0ZVBST1AdAAAAGwAAAAAAAADwDBwAAAAJ"
    "AAAAR3Jhc3NOYW1lAQUAAABHcmFzc1BST1AfAAAAHQAAAAAAAADwDhwAAAAKAAAAR3JvdW5kTmFtZQEGAAAAR3JvdW5kUFJPUB0A"
    "AAAiAAAAAAAAAPYEHAAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBkAAAAXAAAAAAAAAPAIHAAAAAcAAABJY2VOYW1lAQMA"
    "AABJY2VQUk9QIgAAACUAAAAAAAAA9AkcAAAADgAAAExlYWZ5R3Jhc3NOYW1lAQoTAFBHcmFzc1BST1AhAAAAHwAAAAAAAADwEBwA"
    "AAALAAAATGVhdGhlck5hbWUBBwAAAExlYXRoZXJQUk9QIQAAACMAAAAAAAAA8wgcAAAADQAAAExpbWVzdG9uZU5hbWUBCRIAUHN0"
    "b25lUFJPUB8AAAAdAAAAAAAAAPAOHAAAAAoAAABNYXJibGVOYW1lAQYAAABNYXJibGVQUk9QHQAAABsAAAAAAAAA8AwcAAAACQAA"
    "AE1ldGFsTmFtZQEFAAAATWV0YWxQUk9QGQAAABcAAAAAAAAA8AgcAAAABwAAAE11ZE5hbWUBAwAAAE11ZFBST1AiAAAAIAAAAAAA"
    "AADwERwAAAAEAAAATmFtZQEPAAAATWF0ZXJpYWxTZXJ2aWNlUFJPUCMAAAAhAAAAAAAAAPASHAAAAAwAAABQYXZlbWVudE5hbWUB"
    "CAAAAFBhdmVtZW50UFJPUB8AAAAdAAAAAAAAAPAOHAAAAAoAAABQZWJibGVOYW1lAQYAAABQZWJibGVQUk9QIQAAAB8AAAAAAAAA"
    "8BAcAAAACwAAAFBsYXN0ZXJOYW1lAQcAAABQbGFzdGVyUFJPUCEAAAAfAAAAAAAAAPAQHAAAAAsAAABQbGFzdGljTmFtZQEHAAAA"
    "UGxhc3RpY1BST1AbAAAAGQAAAAAAAADwChwAAAAIAAAAUm9ja05hbWUBBAAAAFJvY2tQUk9QJAAAACkAAAAAAAAA9gscAAAAEAAA"
    "AFJvb2ZTaGluZ2xlc05hbWUBDBUAUG5nbGVzUFJPUB8AAAAdAAAAAAAAAPAOHAAAAAoAAABSdWJiZXJOYW1lAQYAAABSdWJiZXJQ"
    "Uk9QGwAAABkAAAAAAAAA8AocAAAACAAAAFNhbHROYW1lAQQAAABTYWx0UFJPUBsAAAAZAAAAAAAAAPAKHAAAAAgAAABTYW5kTmFt"
    "ZQEEAAAAU2FuZFBST1AhAAAAIwAAAAAAAADzCBwAAAANAAAAU2FuZHN0b25lTmFtZQEJEgBQc3RvbmVQUk9QHQAAABsAAAAAAAAA"
    "8AwcAAAACQAAAFNsYXRlTmFtZQEFAAAAU2xhdGVQUk9QJQAAACsAAAAAAAAA9wwcAAAAEQAAAFNtb290aFBsYXN0aWNOYW1lAQ0W"
    "AFBhc3RpY1BST1AbAAAAGQAAAAAAAADwChwAAAAIAAAAU25vd05hbWUBBAAAAFNub3dQUk9QIAAAAB4AAAAAAAAA8A8cAAAADQAA"
    "AFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIcAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADw"
    "EhwAAAAIAAAAVW5pcXVlSWQfAAADhQrNo/cvQ16G5lZcWlBST1AfAAAAHQAAAAAAAADwDhwAAAATAAAAVXNlMjAyMk1hdGVyaWFs"
    "c1htbAIBUFJPUBsAAAAZAAAAAAAAAPAKHAAAAAgAAABXb29kTmFtZQEEAAAAV29vZFBST1AiAAAAJQAAAAAAAAD0CRwAAAAOAAAA"
    "V29vZFBsYW5rc05hbWUBChMAUGxhbmtzUFJPUCIAAAAgAAAAAAAAAPARHQAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQ"
    "Uk9QHwAAAB0AAAAAAAAA8A4dAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDh0AAAATAAAARGVm"
    "aW5lc0NhcGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEHQAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUDMAAAAyAAAA"
    "AAAAAOAdAAAABAAAAE5hbWUBIQkA8BFvblJlcGxpY2F0ZWRDU0dEaWN0aW9uYXJ5U2VydmljZVBST1AgAAAAHgAAAAAAAADwDx0A"
    "AAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAh0AAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAA"
    "AAAAAPASHQAAAAgAAABVbmlxdWVJZB8AAAN2Cs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARHgAAABMAAABBdHRyaWJ1dGVz"
    "U2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA8A4eAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAA"
    "AADwDh4AAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEHgAAAAkAAABIaXN0b3J5SWQfAAEAUAAA"
    "AAAAUFJPUBgAAAAWAAAAAAAAAPAHHgAAAAwAAABJc0RlaHlkcmF0ZWQCAFBST1AbAAAAGQAAAAAAAADwCh4AAAAEAAAATmFtZQEI"
    "AAAAUGFja2FnZXNQUk9QIQAAAB8AAAAAAAAA8BAeAAAAEgAAAFNoZWxsUGFja2FnZXNDb3VudAMAAAAAUFJPUCQAAAAiAAAAAAAA"
    "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"
    "AAAAAAAA8BEiAAAAEwAAAEVtdWxhdGVkQ291bnRyeUNvZGUBAAAAAFBST1AhAAAAHwAAAAAAAADwECIAAAASAAAARW11bGF0ZWRH"
    "YW1lTG9jYWxlAQAAAABQUk9QHQAAACIAAAAAAAAA9gQiAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QKAAAACYAAAAAAAAA"
    "8BciAAAABAAAAE5hbWUBFQAAAFBsYXllckVtdWxhdG9yU2VydmljZVBST1AiAAAAIAAAAAAAAADwESIAAAAWAAAAUGxheWVyRW11"
    "bGF0aW9uRW5hYmxlZAIAUFJPUCUAAAAjAAAAAAAAAPAUIgAAABkAAABQc2V1ZG9sb2NhbGl6YXRpb25FbmFibGVkAgBQUk9QKwAA"
    "ACkAAAAAAAAA8BoiAAAAHAAAAFNlcmlhbGl6ZWRFbXVsYXRlZFBvbGljeUluZm8BAAAAAFBST1AgAAAAHgAAAAAAAADwDyIAAAAN"
    "AAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAiIAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAA"
    "APASIgAAABQAAABUZXh0RWxvbmdhdGlvbkZhY3RvcgMAAAAAUFJPUCMAAAAhAAAAAAAAAPASIgAAAAgAAABVbmlxdWVJZB8AAAOJ"
    "Cs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARIwAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QGgAAABgAAAAA"
    "AAAA8AkjAAAADgAAAEJhbm5pbmdFbmFibGVkAgFQUk9QHwAAAB0AAAAAAAAA8A4jAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAA"
    "AFBST1AeAAAAHAAAAAAAAADwDSMAAAASAAAAQ2hhcmFjdGVyQXV0b0xvYWRzAgFQUk9QHwAAAB0AAAAAAAAA8A4jAAAAEwAAAERl"
    "ZmluZXNDYXBhYmlsaXRpZXMCAFBST1AdAAAAIgAAAAAAAAD2BCMAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AhAAAAHwAA"
    "AAAAAADwECMAAAASAAAATWF4UGxheWVyc0ludGVybmFsAwAAADxQUk9QGgAAABgAAAAAAAAA8AkjAAAABAAAAE5hbWUBBwAAAFBs"
    "YXllcnNQUk9QJwAAACUAAAAAAAAA8BYjAAAAGAAAAFByZWZlcnJlZFBsYXllcnNJbnRlcm5hbAMAAAA8UFJPUBoAAAAYAAAAAAAA"
    "APAJIwAAAAsAAABSZXNwYXduVGltZQSAgAAAUFJPUCAAAAAeAAAAAAAAAPAPIwAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAAB"
    "UFJPUBMAAAARAAAAAAAAAPACIwAAAAQAAABUYWdzHAAAAABQUk9QIwAAACEAAAAAAAAA8BIjAAAACAAAAFVuaXF1ZUlkHwAAA38K"
    "zaP3L0NehuZWXFpQUk9QIQAAAB8AAAAAAAAA8BAjAAAAFQAAAFVzZVN0cmFmaW5nQW5pbWF0aW9ucwIAUFJPUCIAAAAgAAAAAAAA"
    "APARJAAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA8A4kAAAADAAAAENhcGFiaWxpdGllcyEA"
    "AAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDiQAAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEJAAA"
    "AAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUDAAAAAuAAAAAAAAAPAfJAAAAAQAAABOYW1lAR0AAABQcm9jZXNzSW5zdGFuY2VQ"
    "aHlzaWNzU2VydmljZVBST1AgAAAAHgAAAAAAAADwDyQAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAA"
    "AADwAiQAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASJAAAAAgAAABVbmlxdWVJZB8AAAO7Cs2j9y9DXobmVlxaUFJP"
    "UCIAAAAgAAAAAAAAAPARJQAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA8A4lAAAADAAAAENh"
    "cGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDiUAAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUBMAAAAR"
    "AAAAAAAAAPACJQAAAAcAAABFbmFibGVkAgFQUk9QHQAAACIAAAAAAAAA9gQlAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9Q"
    "IwAAACEAAAAAAAAA8BIlAAAAFAAAAE1heEluZGljYXRvcnNWaXNpYmxlAwAAACBQUk9QIAAAAB4AAAAAAAAA8A8lAAAAEQAAAE1h"
    "eFByb21wdHNWaXNpYmxlAwAAACBQUk9QKQAAACcAAAAAAAAA8BglAAAABAAAAE5hbWUBFgAAAFByb3hpbWl0eVByb21wdFNlcnZp"
    "Y2VQUk9QIAAAAB4AAAAAAAAA8A8lAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIlAAAABAAA"
    "AFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEiUAAAAIAAAAVW5pcXVlSWQfAAAD3wrNo/cvQ16G5lZcWlBST1AiAAAAIAAAAAAA"
    "AADwESYAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOJgAAAAwAAABDYXBhYmlsaXRpZXMh"
    "AAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4mAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1AdAAAAIgAAAAAAAAD2BCYA"
    "AAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AiAAAAIAAAAAAAAADwESYAAAAEAAAATmFtZQEPAAAAUmVwbGljYXRlZEZpcnN0"
    "UFJPUCAAAAAeAAAAAAAAAPAPJgAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAABUFJPUBMAAAARAAAAAAAAAPACJgAAAAQAAABU"
    "YWdzHAAAAABQUk9QIwAAACEAAAAAAAAA8BImAAAACAAAAFVuaXF1ZUlkHwAAA4IKzaP3L0NehuZWXFpQUk9QRAAAAEIAAAAAAAAA"
    "8DMnAAAAEwAAAEF0dHJpYnV0ZXNTZXJpYWxpemUBIgAAAAEAAAARAAAARW1pdHRlcjJEX1ZlcnNpb24GKVyPwvUo9D9QUk9QHwAA"
    "AB0AAAAAAAAA8A4nAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDicAAAATAAAARGVmaW5lc0Nh"
    "cGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEJwAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUCQAAAAiAAAAAAAAAPAT"
    "JwAAAAQAAABOYW1lAREAAABSZXBsaWNhdGVkU3RvcmFnZVBST1AgAAAAHgAAAAAAAADwDycAAAANAAAAU291cmNlQXNzZXRJZBsA"
    "AAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAicAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASJwAAAAgAAABVbmlxdWVJ"
    "ZB8AAAO8Cs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARKAAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAA"
    "AB0AAAAAAAAA8A4oAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDigAAAATAAAARGVmaW5lc0Nh"
    "cGFiaWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEKAAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBsAAAAZAAAAAAAAAPAK"
    "KAAAAAQAAABOYW1lAQgAAABJbnN0YW5jZVBST1AgAAAAHgAAAAAAAADwDygAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBS"
    "T1ATAAAAEQAAAAAAAADwAigAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASKAAAAAgAAABVbmlxdWVJZB8AAAOlCs2j"
    "9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARKQAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA"
    "8A4pAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDikAAAATAAAARGVmaW5lc0NhcGFiaWxpdGll"
    "cwIAUFJPUB0AAAAiAAAAAAAAAPYEKQAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBwAAAAaAAAAAAAAAPALKQAAAAQAAABO"
    "YW1lAQkAAABTZWxlY3Rpb25QUk9QIAAAAB4AAAAAAAAA8A8pAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEA"
    "AAAAAAAA8AIpAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEikAAAAIAAAAVW5pcXVlSWQfAAADnwrNo/cvQ16G5lZc"
    "WlBST1AiAAAAIAAAAAAAAADwESoAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOKgAAAAwA"
    "AABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4qAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1Ad"
    "AAAAIgAAAAAAAAD2BCoAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AnAAAAJQAAAAAAAADwFioAAAAEAAAATmFtZQEUAAAA"
    "U2VyaWFsaXphdGlvblNlcnZpY2VQUk9QIAAAAB4AAAAAAAAA8A8qAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAA"
    "ABEAAAAAAAAA8AIqAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEioAAAAIAAAAVW5pcXVlSWQfAAAEZQrNo/cvQ16G"
    "5lZcWlBST1AiAAAAIAAAAAAAAADwESsAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOKwAA"
    "AAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A4rAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBS"
    "T1AdAAAAIgAAAAAAAAD2BCsAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AdAAAAGwAAAAAAAADwDCsAAAARAAAATG9hZFN0"
    "cmluZ0VuYWJsZWQCAFBST1AmAAAAJAAAAAAAAADwFSsAAAAEAAAATmFtZQETAAAAU2VydmVyU2NyaXB0U2VydmljZVBST1AgAAAA"
    "HgAAAAAAAADwDysAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAisAAAAEAAAAVGFncxwAAAAA"
    "UFJPUCMAAAAhAAAAAAAAAPASKwAAAAgAAABVbmlxdWVJZB8AAAO9Cs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARLAAAABMA"
    "AABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA8A4sAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBS"
    "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"
    "AAAAUFJPUCMAAAAhAAAAAAAAAPASLgAAAAgAAABVbmlxdWVJZB8AAAPvCs2j9y9DXobmVlxaUFJPUCUAAAAjAAAAAAAAAPAULwAA"
    "ABkAAABBY291c3RpY1NpbXVsYXRpb25FbmFibGVkAgBQUk9QHAAAABoAAAAAAAAA8AsvAAAADQAAAEFtYmllbnRSZXZlcmISAAAA"
    "AFBST1AiAAAAIAAAAAAAAADwES8AAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUCAAAAAeAAAAAAAAAPAPLwAAABEA"
    "AABBdWRpb0FwaUJ5RGVmYXVsdBIAAAAAUFJPUB8AAAAdAAAAAAAAAPAOLwAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9Q"
    "JwAAACUAAAAAAAAA8BYvAAAAGAAAAENoYXJhY3RlclNvdW5kc1VzZU5ld0FwaRIAAAAAUFJPUCYAAAAkAAAAAAAAAPAVLwAAABcA"
    "AABEZWZhdWx0TGlzdGVuZXJMb2NhdGlvbhIAAAADUFJPUB8AAAAdAAAAAAAAAPAOLwAAABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVz"
    "AgBQUk9QHgAAABwAAAAAAAAA8A0vAAAAEgAAAERpZmZyYWN0aW9uRW5hYmxlZAIBUFJPUB0AAAAbAAAAAAAAAPAMLwAAAA4AAABE"
    "aXN0YW5jZUZhY3RvcgSAqj1wUFJPUBsAAAAZAAAAAAAAAPAKLwAAAAwAAABEb3BwbGVyU2NhbGUEfwAAAFBST1AdAAAAIgAAAAAA"
    "AAD2BC8AAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AoAAAAJgAAAAAAAADwFy8AAAAcAAAASXNOZXdFeHBGb3JBdWRpb0Fw"
    "aUJ5RGVmYXVsdAIAUFJPUCYAAAAkAAAAAAAAAPAVLwAAAA4AAABMaXN0ZW5lckNGcmFtZRACAAAAAAAAAAAAAAAAUFJPUB0AAAAb"
    "AAAAAAAAAPAMLwAAAA4AAABMaXN0ZW5lck9iamVjdBMAAAABUFJPUBsAAAAZAAAAAAAAAPAKLwAAAAwAAABMaXN0ZW5lclR5cGUS"
    "AAAAAFBST1AfAAAAHQAAAAAAAADwDi8AAAAEAAAATmFtZQEMAAAAU291bmRTZXJ2aWNlUFJPUBwAAAAaAAAAAAAAAPALLwAAABAA"
    "AABPY2NsdXNpb25FbmFibGVkAgFQUk9QIwAAACEAAAAAAAAA8BIvAAAAFwAAAFJlc3BlY3RGaWx0ZXJpbmdFbmFibGVkAgFQUk9Q"
    "GQAAABcAAAAAAAAA8AgvAAAADQAAAFJldmVyYkVuYWJsZWQCAVBST1AbAAAAGQAAAAAAAADwCi8AAAAMAAAAUm9sbG9mZlNjYWxl"
    "BH8AAABQUk9QIAAAAB4AAAAAAAAA8A8vAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AIvAAAA"
    "BAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEi8AAAAIAAAAVW5pcXVlSWQfAAADaQrNo/cvQ16G5lZcWlBST1AeAAAAHAAA"
    "AAAAAADwDS8AAAAPAAAAVm9sdW1ldHJpY0F1ZGlvEgAAAAFQUk9QIgAAACAAAAAAAAAA8BEwAAAAFgAAAEFsbG93VGVhbUNoYW5n"
    "ZU9uVG91Y2gCAFBST1AUAAAAEgAAAAAAAADwAzAAAAAIAAAAQW5jaG9yZWQCAVBST1AiAAAAIAAAAAAAAADwETAAAAATAAAAQXR0"
    "cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUBsAAAAZAAAAAAAAAPAKMAAAAA8AAABBdWRpb0NhbkNvbGxpZGUCAVBST1AZAAAAFwAA"
    "AAAAAADwCDAAAAAKAAAAQmFja1BhcmFtQQR+AAABUFJPUBkAAAAXAAAAAAAAAPAIMAAAAAoAAABCYWNrUGFyYW1CBH4AAABQUk9Q"
    "GgAAABgAAAAAAAAA8AkwAAAACwAAAEJhY2tTdXJmYWNlEgAAAABQUk9QHwAAAB0AAAAAAAAA8A4wAAAAEAAAAEJhY2tTdXJmYWNl"
    "SW5wdXQSAAAAAFBST1AbAAAAGQAAAAAAAADwCjAAAAAMAAAAQm90dG9tUGFyYW1BBH4AAAFQUk9QGwAAABkAAAAAAAAA8AowAAAA"
    "DAAAAEJvdHRvbVBhcmFtQgR+AAAAUFJPUBwAAAAaAAAAAAAAAPALMAAAAA0AAABCb3R0b21TdXJmYWNlEgAAAABQUk9QIQAAAB8A"
    "AAAAAAAA8BAwAAAAEgAAAEJvdHRvbVN1cmZhY2VJbnB1dBIAAAAAUFJPUB4AAAAcAAAAAAAAAPANMAAAAAYAAABDRnJhbWUQAgAA"
    "AAB+AAAAAAAAAFBST1AWAAAAFAAAAAAAAADwBTAAAAAKAAAAQ2FuQ29sbGlkZQIBUFJPUBQAAAASAAAAAAAAAPADMAAAAAgAAABD"
    "YW5RdWVyeQIBUFJPUBQAAAASAAAAAAAAAPADMAAAAAgAAABDYW5Ub3VjaAIBUFJPUB8AAAAdAAAAAAAAAPAOMAAAAAwAAABDYXBh"
    "YmlsaXRpZXMhAAAAAAAAAABQUk9QFgAAABQAAAAAAAAA8AUwAAAACgAAAENhc3RTaGFkb3cCAVBST1AkAAAAIgAAAAAAAADwEzAA"
    "AAAOAAAAQ29sbGlzaW9uR3JvdXABBwAAAERlZmF1bHRQUk9QHwAAAB0AAAAAAAAA8A4wAAAAEAAAAENvbGxpc2lvbkdyb3VwSWQD"
    "AAAAAFBST1AZAAAAFwAAAAAAAADwCDAAAAALAAAAQ29sb3IzdWludDgao6KlUFJPUCQAAAAiAAAAAAAAAPATMAAAABgAAABDdXN0"
    "b21QaHlzaWNhbFByb3BlcnRpZXMZAlBST1AfAAAAHQAAAAAAAADwDjAAAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUBcA"
    "AAAVAAAAAAAAAPAGMAAAAAgAAABEdXJhdGlvbgMAAAAAUFJPUB0AAAAbAAAAAAAAAPAMMAAAABEAAABFbmFibGVGbHVpZEZvcmNl"
    "cwIBUFJPUBMAAAARAAAAAAAAAPACMAAAAAcAAABFbmFibGVkAgFQUk9QGgAAABgAAAAAAAAA8AkwAAAACwAAAEZyb250UGFyYW1B"
    "BH4AAAFQUk9QGgAAABgAAAAAAAAA8AkwAAAACwAAAEZyb250UGFyYW1CBH4AAABQUk9QGwAAABkAAAAAAAAA8AowAAAADAAAAEZy"
    "b250U3VyZmFjZRIAAAAAUFJPUCAAAAAeAAAAAAAAAPAPMAAAABEAAABGcm9udFN1cmZhY2VJbnB1dBIAAAAAUFJPUB0AAAAiAAAA"
    "AAAAAPYEMAAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUBkAAAAXAAAAAAAAAPAIMAAAAAoAAABMZWZ0UGFyYW1BBH4AAAFQ"
    "Uk9QGQAAABcAAAAAAAAA8AgwAAAACgAAAExlZnRQYXJhbUIEfgAAAFBST1AaAAAAGAAAAAAAAADwCTAAAAALAAAATGVmdFN1cmZh"
    "Y2USAAAAAFBST1AfAAAAHQAAAAAAAADwDjAAAAAQAAAATGVmdFN1cmZhY2VJbnB1dBIAAAAAUFJPUBIAAAAQAAAAAAAAAPABMAAA"
    "AAYAAABMb2NrZWQCAFBST1AUAAAAEgAAAAAAAADwAzAAAAAIAAAATWFzc2xlc3MCAFBST1AXAAAAFQAAAAAAAADwBjAAAAAIAAAA"
    "TWF0ZXJpYWwSAAABAFBST1AmAAAAJgAAAAAAAADxCTAAAAAZAAAATWF0ZXJpYWxWYXJpYW50Uw0AkGl6ZWQBAAAAAFBST1AgAAAA"
    "HgAAAAAAAADwDzAAAAAEAAAATmFtZQENAAAAU3Bhd25Mb2NhdGlvblBST1ATAAAAEQAAAAAAAADwAjAAAAAHAAAATmV1dHJhbAIB"
    "UFJPUCMAAAAhAAAAAAAAAPASMAAAAAsAAABQaXZvdE9mZnNldBACAAAAAAAAAAAAAAAAUFJPUBoAAAAYAAAAAAAAAPAJMAAAAAsA"
    "AABSZWZsZWN0YW5jZQQAAAAAUFJPUBoAAAAYAAAAAAAAAPAJMAAAAAsAAABSaWdodFBhcmFtQQR+AAABUFJPUBoAAAAYAAAAAAAA"
    "APAJMAAAAAsAAABSaWdodFBhcmFtQgR+AAAAUFJPUBsAAAAZAAAAAAAAAPAKMAAAAAwAAABSaWdodFN1cmZhY2USAAAAAFBST1Ag"
    "AAAAHgAAAAAAAADwDzAAAAARAAAAUmlnaHRTdXJmYWNlSW5wdXQSAAAAAFBST1AbAAAAGQAAAAAAAADwCjAAAAAMAAAAUm9vdFBy"
    "aW9yaXR5AwAAAABQUk9QIgAAACAAAAAAAAAA8BEwAAAACwAAAFJvdFZlbG9jaXR5DgAAAAAAAAAAAAAAAFBST1AgAAAAHgAAAAAA"
    "AADwDzAAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAjAAAAAEAAAAVGFncxwAAAAAUFJPUBgA"
    "AAAWAAAAAAAAAPAHMAAAAAkAAABUZWFtQ29sb3ILAAAAwlBST1AYAAAAFgAAAAAAAADwBzAAAAAJAAAAVG9wUGFyYW1BBH4AAAFQ"
    "Uk9QGAAAABYAAAAAAAAA8AcwAAAACQAAAFRvcFBhcmFtQgR+AAAAUFJPUBkAAAAXAAAAAAAAAPAIMAAAAAoAAABUb3BTdXJmYWNl"
    "EgAAAABQUk9QHgAAABwAAAAAAAAA8A0wAAAADwAAAFRvcFN1cmZhY2VJbnB1dBIAAAAAUFJPUBsAAAAZAAAAAAAAAPAKMAAAAAwA"
    "AABUcmFuc3BhcmVuY3kEAAAAAFBST1AjAAAAIQAAAAAAAADwEjAAAAAIAAAAVW5pcXVlSWQfAAAD6QrNo/cvQ16G5lZcWlBST1Af"
    "AAAAHQAAAAAAAADwDjAAAAAIAAAAVmVsb2NpdHkOAAAAAAAAAAAAAAAAUFJPUBwAAAAaAAAAAAAAAPALMAAAAA0AAABmb3JtRmFj"
    "dG9yUmF3EgAAAAFQUk9QFAAAABIAAAAAAAAA8AMwAAAABQAAAHNoYXBlEgAAAAFQUk9QGwAAABkAAAAAAAAA8AowAAAABAAAAHNp"
    "emUOgoAAAH8AAACCgAAAUFJPUCIAAAAgAAAAAAAAAPARMQAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0A"
    "AAAAAAAA8A4xAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDjEAAAATAAAARGVmaW5lc0NhcGFi"
    "aWxpdGllcwIAUFJPUB0AAAAiAAAAAAAAAPYEMQAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUCoAAAAoAAAAAAAAAPAZMQAA"
    "AAQAAABOYW1lARcAAABTdGFydGVyQ2hhcmFjdGVyU2NyaXB0c1BST1AgAAAAHgAAAAAAAADwDzEAAAANAAAAU291cmNlQXNzZXRJ"
    "ZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAjEAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASMQAAAAgAAABVbmlx"
    "dWVJZB8AAAPtCs2j9y9DXobmVlxaUFJPUCIAAAAgAAAAAAAAAPARMgAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9Q"
    "HwAAAB0AAAAAAAAA8A4yAAAADAAAAENhcGFiaWxpdGllcyEAAAAAAAAAAFBST1AvAAAALQAAAAAAAADwHjIAAAAgAAAAQ2xpcHNE"
    "ZXNjZW5kYW50c1N1cHBvcnRzUm90YXRpb24SAAAAAFBST1AfAAAAHQAAAAAAAADwDjIAAAATAAAARGVmaW5lc0NhcGFiaWxpdGll"
    "cwIAUFJPUB0AAAAiAAAAAAAAAPYEMgAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUB0AAAAbAAAAAAAAAPAMMgAAAAQAAABO"
    "YW1lAQoAAABTdGFydGVyR3VpUFJPUCEAAAAfAAAAAAAAAPAQMgAAABUAAABSZXNldFBsYXllckd1aU9uU3Bhd24CAVBST1AdAAAA"
    "GwAAAAAAAADwDDIAAAAOAAAAUnRsVGV4dFN1cHBvcnQSAAAAAFBST1AgAAAAHgAAAAAAAADwDzIAAAARAAAAU2NyZWVuT3JpZW50"
    "YXRpb24SAAAABFBST1AeAAAAHAAAAAAAAADwDTIAAAASAAAAU2hvd0RldmVsb3BtZW50R3VpAgFQUk9QIAAAAB4AAAAAAAAA8A8y"
    "AAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QJgAAACQAAAAAAAAA8BUyAAAAFwAAAFN0dWRpb0RlZmF1bHRTdHlsZVNo"
    "ZWV0EwAAAAFQUk9QQAAAAD8AAAAAAAAAQDIAAAAEAPAoU3R1ZGlvSW5zZXJ0V2lkZ2V0TGF5ZXJDb2xsZWN0b3JBdXRvTGlua1N0"
    "eWxlU2hlZXQTAAAAAVBST1ATAAAAEQAAAAAAAADwAjIAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASMgAAAAgAAABV"
    "bmlxdWVJZB8AAAOQCs2j9y9DXobmVlxaUFJPUCAAAAAeAAAAAAAAAPAPMgAAABEAAABWaXJ0dWFsQ3Vyc29yTW9kZRIAAAAAUFJP"
    "UCIAAAAgAAAAAAAAAPARMwAAABMAAABBdHRyaWJ1dGVzU2VyaWFsaXplAQAAAABQUk9QHwAAAB0AAAAAAAAA8A4zAAAADAAAAENh"
    "cGFiaWxpdGllcyEAAAAAAAAAAFBST1AfAAAAHQAAAAAAAADwDjMAAAATAAAARGVmaW5lc0NhcGFiaWxpdGllcwIAUFJPUB0AAAAi"
    "AAAAAAAAAPYEMwAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUB4AAAAcAAAAAAAAAPANMwAAAAQAAABOYW1lAQsAAABTdGFy"
    "dGVyUGFja1BST1AgAAAAHgAAAAAAAADwDzMAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1ATAAAAEQAAAAAAAADwAjMA"
    "AAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASMwAAAAgAAABVbmlxdWVJZB8AAAOPCs2j9y9DXobmVlxaUFJPUCEAAAAf"
    "AAAAAAAAAPAQNAAAABUAAABBbGxvd0N1c3RvbUFuaW1hdGlvbnMCAVBST1AiAAAAIAAAAAAAAADwETQAAAATAAAAQXR0cmlidXRl"
    "c1NlcmlhbGl6ZQEAAAAAUFJPUBsAAAAZAAAAAAAAAPAKNAAAAA8AAABBdXRvSnVtcEVuYWJsZWQCAVBST1AzAAAAMQAAAAAAAADw"
    "IjQAAAAkAAAAQXZhdGFySm9pbnRVcGdyYWRlX1NlcmlhbGl6ZWRSb2xsb3V0EgAAAAJQUk9QJAAAACIAAAAAAAAA8BM0AAAAFQAA"
    "AENhbWVyYU1heFpvb21EaXN0YW5jZQSGAAAAUFJPUCQAAAAiAAAAAAAAAPATNAAAABUAAABDYW1lcmFNaW5ab29tRGlzdGFuY2UE"
    "fgAAAFBST1AZAAAAFwAAAAAAAADwCDQAAAAKAAAAQ2FtZXJhTW9kZRIAAAAAUFJPUB8AAAAdAAAAAAAAAPAONAAAAAwAAABDYXBh"
    "YmlsaXRpZXMhAAAAAAAAAABQUk9QJwAAACUAAAAAAAAA8BY0AAAAGwAAAENoYXJhY3RlckJyZWFrSm9pbnRzT25EZWF0aAIAUFJP"
    "UCIAAAAgAAAAAAAAAPARNAAAABMAAABDaGFyYWN0ZXJKdW1wSGVpZ2h0BIHMzMxQUk9QIQAAAB8AAAAAAAAA8BA0AAAAEgAAAENo"
    "YXJhY3Rlckp1bXBQb3dlcgSEkAAAUFJPUCUAAAAjAAAAAAAAAPAUNAAAABYAAABDaGFyYWN0ZXJNYXhTbG9wZUFuZ2xlBIVkAABQ"
    "Uk9QIQAAAB8AAAAAAAAA8BA0AAAAFQAAAENoYXJhY3RlclVzZUp1bXBQb3dlcgIAUFJPUCEAAAAfAAAAAAAAAPAQNAAAABIAAABD"
    "aGFyYWN0ZXJXYWxrU3BlZWQEgwAAAFBST1AYAAAAFgAAAAAAAADwBzQAAAAMAAAAQ2xhc3NpY0RlYXRoAgFQUk9QJQAAACMAAAAA"
    "AAAA8BQ0AAAAGQAAAENyZWF0ZURlZmF1bHRQbGF5ZXJNb2R1bGUCAVBST1AfAAAAHQAAAAAAAADwDjQAAAATAAAARGVmaW5lc0Nh"
    "cGFiaWxpdGllcwIAUFJPUCUAAAAjAAAAAAAAAPAUNAAAABYAAABEZXZDYW1lcmFPY2NsdXNpb25Nb2RlEgAAAABQUk9QLAAAACoA"
    "AAAAAAAA8Bs0AAAAHQAAAERldkNvbXB1dGVyQ2FtZXJhTW92ZW1lbnRNb2RlEgAAAABQUk9QJgAAACQAAAAAAAAA8BU0AAAAFwAA"
    "AERldkNvbXB1dGVyTW92ZW1lbnRNb2RlEgAAAABQUk9QKQAAACcAAAAAAAAA8Bg0AAAAGgAAAERldlRvdWNoQ2FtZXJhTW92ZW1l"
    "bnRNb2RlEgAAAABQUk9QIwAAACEAAAAAAAAA8BI0AAAAFAAAAERldlRvdWNoTW92ZW1lbnRNb2RlEgAAAABQUk9QIQAAAB8AAAAA"
    "AAAA8BA0AAAAEgAAAEVuYWJsZUR5bmFtaWNIZWFkcxIAAAAAUFJPUCEAAAAfAAAAAAAAAPAQNAAAABUAAABFbmFibGVNb3VzZUxv"
    "Y2tPcHRpb24CAVBST1AqAAAAKAAAAAAAAADwGTQAAAAXAAAAR2FtZVNldHRpbmdzQXNzZXRJREZhY2UbAAAAAAAAAABQUk9QKgAA"
    "ACgAAAAAAAAA8Bk0AAAAFwAAAEdhbWVTZXR0aW5nc0Fzc2V0SURIZWFkGwAAAAAAAAAAUFJPUC0AAAArAAAAAAAAAPAcNAAAABoA"
    "AABHYW1lU2V0dGluZ3NBc3NldElETGVmdEFybRsAAAAAAAAAAFBST1AtAAAAKwAAAAAAAADwHDQAAAAaAAAAR2FtZVNldHRpbmdz"
    "QXNzZXRJRExlZnRMZWcbAAAAAAAAAABQUk9QKwAAACkAAAAAAAAA8Bo0AAAAGAAAAEdhbWVTZXR0aW5nc0Fzc2V0SURQYW50cxsA"
    "AAAAAAAAAFBST1AuAAAALAAAAAAAAADwHTQAAAAbAAAAR2FtZVNldHRpbmdzQXNzZXRJRFJpZ2h0QXJtGwAAAAAAAAAAUFJPUC4A"
    "AAAsAAAAAAAAAPAdNAAAABsAAABHYW1lU2V0dGluZ3NBc3NldElEUmlnaHRMZWcbAAAAAAAAAABQUk9QKwAAACkAAAAAAAAA8Bo0"
    "AAAAGAAAAEdhbWVTZXR0aW5nc0Fzc2V0SURTaGlydBsAAAAAAAAAAFBST1AuAAAALAAAAAAAAADwHTQAAAAbAAAAR2FtZVNldHRp"
    "bmdzQXNzZXRJRFRlZVNoaXJ0GwAAAAAAAAAAUFJPUCsAAAApAAAAAAAAAPAaNAAAABgAAABHYW1lU2V0dGluZ3NBc3NldElEVG9y"
    "c28bAAAAAAAAAABQUk9QIQAAAB8AAAAAAAAA8BA0AAAAEgAAAEdhbWVTZXR0aW5nc0F2YXRhchIAAAABUFJPUCcAAAAlAAAAAAAA"
    "APAWNAAAABgAAABHYW1lU2V0dGluZ3NSMTVDb2xsaXNpb24SAAAAAFBST1AxAAAALwAAAAAAAADwIDQAAAAeAAAAR2FtZVNldHRp"
    "bmdzU2NhbGVSYW5nZUJvZHlUeXBlFwAAAAAAAIA/UFJPUC0AAAArAAAAAAAAAPAcNAAAABoAAABHYW1lU2V0dGluZ3NTY2FsZVJh"
    "bmdlSGVhZBczM3M/AACAP1BST1AvAAAALQAAAAAAAADwHjQAAAAcAAAAR2FtZVNldHRpbmdzU2NhbGVSYW5nZUhlaWdodBdmZmY/"
    "ZmaGP1BST1AzAAAAMQAAAAAAAADwIjQAAAAgAAAAR2FtZVNldHRpbmdzU2NhbGVSYW5nZVByb3BvcnRpb24XAAAAAAAAgD9QUk9Q"
    "LgAAACwAAAAAAAAA8B00AAAAGwAAAEdhbWVTZXR0aW5nc1NjYWxlUmFuZ2VXaWR0aBczMzM/AACAP1BST1AkAAAAIgAAAAAAAADw"
    "EzQAAAAVAAAASGVhbHRoRGlzcGxheURpc3RhbmNlBIWQAABQUk9QHQAAACIAAAAAAAAA9gQ0AAAACQAAAEhpc3RvcnlJZB8AAQBQ"
    "AAAAAABQUk9QIwAAACEAAAAAAAAA8BI0AAAAFwAAAExvYWRDaGFyYWN0ZXJBcHBlYXJhbmNlAgFQUk9QKwAAACkAAAAAAAAA8Bo0"
    "AAAAHAAAAExvYWRDaGFyYWN0ZXJMYXllcmVkQ2xvdGhpbmcSAAAAAFBST1AlAAAAIwAAAAAAAADwFDQAAAAWAAAATHVhQ2hhcmFj"
    "dGVyQ29udHJvbGxlchIAAAAAUFJPUCAAAAAeAAAAAAAAAPAPNAAAAAQAAABOYW1lAQ0AAABTdGFydGVyUGxheWVyUFJPUCIAAAAg"
    "AAAAAAAAAPARNAAAABMAAABOYW1lRGlzcGxheURpc3RhbmNlBIWQAABQUk9QHwAAAB0AAAAAAAAA8A40AAAAEAAAAFBsYWNlQXZh"
    "dGFyUnVsZXMTAAAAAVBST1AhAAAAHwAAAAAAAADwEDQAAAASAAAAUGxheWVyTW9kdWxlU3RhdHVzAwAAAABQUk9QIAAAAB4AAAAA"
    "AAAA8A80AAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AI0AAAABAAAAFRhZ3McAAAAAFBST1Aj"
    "AAAAIQAAAAAAAADwEjQAAAAIAAAAVW5pcXVlSWQfAAADjgrNo/cvQ16G5lZcWlBST1AdAAAAGwAAAAAAAADwDDQAAAARAAAAVXNl"
    "ckVtb3Rlc0VuYWJsZWQCAVBST1AiAAAAIAAAAAAAAADwETUAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAd"
    "AAAAAAAAAPAONQAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A41AAAAEwAAAERlZmluZXNDYXBh"
    "YmlsaXRpZXMCAFBST1AdAAAAIgAAAAAAAAD2BDUAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AnAAAAJQAAAAAAAADwFjUA"
    "AAAEAAAATmFtZQEUAAAAU3RhcnRlclBsYXllclNjcmlwdHNQUk9QIAAAAB4AAAAAAAAA8A81AAAADQAAAFNvdXJjZUFzc2V0SWQb"
    "AAAAAAAAAAFQUk9QEwAAABEAAAAAAAAA8AI1AAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEjUAAAAIAAAAVW5pcXVl"
    "SWQfAAAD7ArNo/cvQ16G5lZcWlBST1AiAAAAIAAAAAAAAADwETYAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8A"
    "AAAdAAAAAAAAAPAONgAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A42AAAAEwAAAERlZmluZXND"
    "YXBhYmlsaXRpZXMCAFBST1AdAAAAIgAAAAAAAAD2BDYAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AgAAAAHgAAAAAAAADw"
    "DzYAAAAEAAAATmFtZQENAAAASW5zZXJ0aW9uSGFzaFBST1AgAAAAHgAAAAAAAADwDzYAAAANAAAAU291cmNlQXNzZXRJZBsAAAAA"
    "AAAAAVBST1ATAAAAEQAAAAAAAADwAjYAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASNgAAAAgAAABVbmlxdWVJZB8A"
    "AAPuCs2j9y9DXobmVlxaUFJPUDoAAAA4AAAAAAAAAPApNgAAAAUAAABWYWx1ZQEmAAAAezRFOTNCMkI5LTM5MUYtNEJCNC04Njk4"
    "LThBOERFMDk4RDExM31QUk9QIgAAACAAAAAAAAAA8BE3AAAAEwAAAEF0dHJpYnV0ZXNTZXJpYWxpemUBAAAAAFBST1AfAAAAHQAA"
    "AAAAAADwDjcAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAONwAAABMAAABEZWZpbmVzQ2FwYWJp"
    "bGl0aWVzAgBQUk9QLQAAACsAAAAAAAAA8Bw3AAAAIQAAAEVuYWJsZVNjcmlwdENvbGxhYkJ5RGVmYXVsdE9uTG9hZAIAUFJPUB0A"
    "AAAiAAAAAAAAAPYENwAAAAkAAABIaXN0b3J5SWQfAAEAUAAAAAAAUFJPUB0AAAAbAAAAAAAAAPAMNwAAAAQAAABOYW1lAQoAAABT"
    "dHVkaW9EYXRhUFJPUCAAAAAeAAAAAAAAAPAPNwAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAABUFJPUBMAAAARAAAAAAAAAPAC"
    "NwAAAAQAAABUYWdzHAAAAABQUk9QIwAAACEAAAAAAAAA8BI3AAAACAAAAFVuaXF1ZUlkHwAAA4wKzaP3L0NehuZWXFpQUk9QIgAA"
    "ACAAAAAAAAAA8BE4AAAAEwAAAEF0dHJpYnV0ZXNTZXJpYWxpemUBAAAAAFBST1AfAAAAHQAAAAAAAADwDjgAAAAMAAAAQ2FwYWJp"
    "bGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAOOAAAABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QEwAAABEAAAAA"
    "AAAA8AI4AAAABwAAAEVuYWJsZWQCAVBST1AdAAAAIgAAAAAAAAD2BDgAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AYAAAA"
    "FgAAAAAAAADwBzgAAAAJAAAASW50ZW5zaXR5BHhHrhRQUk9QGgAAABgAAAAAAAAA8Ak4AAAABAAAAE5hbWUBBwAAAFN1blJheXNQ"
    "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"
    "dGVTZWNvbmRzTGFnBQAAAAAAAAAAUFJPUCAAAAAeAAAAAAAAAPAPPAAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAABUFJPUBMA"
    "AAARAAAAAAAAAPACPAAAAAQAAABUYWdzHAAAAABQUk9QJQAAACMAAAAAAAAA8BQ8AAAAGQAAAFRocm90dGxlUGh5c2ljc1RvUmVh"
    "bHRpbWUCAVBST1AaAAAAGAAAAAAAAADwCTwAAAAHAAAAVGltZW91dAUAAAAAAAAkQFBST1AjAAAAIQAAAAAAAADwEjwAAAAIAAAA"
    "VW5pcXVlSWQfAAAD4QrNo/cvQ16G5lZcWlBST1AiAAAAIAAAAAAAAADwET0AAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAA"
    "UFJPUB8AAAAdAAAAAAAAAPAOPQAAAAwAAABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QJAAAACIAAAAAAAAA8BM9AAAAGAAAAENo"
    "YXRUcmFuc2xhdGlvbkZUVVhTaG93bgIBUFJPUCgAAAAmAAAAAAAAAPAXPQAAABwAAABDaGF0VHJhbnNsYXRpb25Ub2dnbGVFbmFi"
    "bGVkAgBQUk9QGgAAABgAAAAAAAAA8Ak9AAAACwAAAENoYXRWZXJzaW9uEgAAAAFQUk9QIQAAAB8AAAAAAAAA8BA9AAAAFQAAAENy"
    "ZWF0ZURlZmF1bHRDb21tYW5kcwIBUFJPUCUAAAAjAAAAAAAAAPAUPQAAABkAAABDcmVhdGVEZWZhdWx0VGV4dENoYW5uZWxzAgFQ"
    "Uk9QHwAAAB0AAAAAAAAA8A49AAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1AkAAAAIgAAAAAAAADwEz0AAAAYAAAASGFz"
    "U2VlbkRlcHJlY2F0aW9uRGlhbG9nAgBQUk9QHQAAACIAAAAAAAAA9gQ9AAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QIAAA"
    "AB4AAAAAAAAA8A89AAAAFAAAAElzTGVnYWN5Q2hhdERpc2FibGVkAgFQUk9QIgAAACAAAAAAAAAA8BE9AAAABAAAAE5hbWUBDwAA"
    "AFRleHRDaGF0U2VydmljZVBST1AlAAAAIwAAAAAAAADwFD0AAAAWAAAAUGxhdGZvcm1JbnRlZ3JhdGVkQ2hhdBIAAAAAUFJPUCAA"
    "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"
    "Q2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAORwAAABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QHQAA"
    "ACIAAAAAAAAA9gRHAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QJgAAACQAAAAAAAAA8BVHAAAABAAAAE5hbWUBEwAAAFZp"
    "ZGVvQ2FwdHVyZVNlcnZpY2VQUk9QIAAAAB4AAAAAAAAA8A9HAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEA"
    "AAAAAAAA8AJHAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEkcAAAAIAAAAVW5pcXVlSWQfAAADdQrNo/cvQ16G5lZc"
    "WlBST1AiAAAAIAAAAAAAAADwEUgAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOSAAAAAwA"
    "AABDYXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QHwAAAB0AAAAAAAAA8A5IAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1Ad"
    "AAAAIgAAAAAAAAD2BEgAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AfAAAAHQAAAAAAAADwDkgAAAAEAAAATmFtZQEMAAAA"
    "VmlkZW9TZXJ2aWNlUFJPUCAAAAAeAAAAAAAAAPAPSAAAAA0AAABTb3VyY2VBc3NldElkGwAAAAAAAAABUFJPUBMAAAARAAAAAAAA"
    "APACSAAAAAQAAABUYWdzHAAAAABQUk9QIwAAACEAAAAAAAAA8BJIAAAACAAAAFVuaXF1ZUlkHwAABA8KzaP3L0NehuZWXFpQUk9Q"
    "IgAAACAAAAAAAAAA8BFJAAAAEwAAAEF0dHJpYnV0ZXNTZXJpYWxpemUBAAAAAFBST1AfAAAAHQAAAAAAAADwDkkAAAAMAAAAQ2Fw"
    "YWJpbGl0aWVzIQAAAAAAAAAAUFJPUB8AAAAdAAAAAAAAAPAOSQAAABMAAABEZWZpbmVzQ2FwYWJpbGl0aWVzAgBQUk9QHQAAACIA"
    "AAAAAAAA9gRJAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QJgAAACQAAAAAAAAA8BVJAAAABAAAAE5hbWUBEwAAAFZpcnR1"
    "YWxJbnB1dE1hbmFnZXJQUk9QIAAAAB4AAAAAAAAA8A9JAAAADQAAAFNvdXJjZUFzc2V0SWQbAAAAAAAAAAFQUk9QEwAAABEAAAAA"
    "AAAA8AJJAAAABAAAAFRhZ3McAAAAAFBST1AjAAAAIQAAAAAAAADwEkkAAAAIAAAAVW5pcXVlSWQfAAAD4wrNo/cvQ16G5lZcWlBS"
    "T1AiAAAAIAAAAAAAAADwEUoAAAATAAAAQXR0cmlidXRlc1NlcmlhbGl6ZQEAAAAAUFJPUB8AAAAdAAAAAAAAAPAOSgAAAAwAAABD"
    "YXBhYmlsaXRpZXMhAAAAAAAAAABQUk9QKQAAACcAAAAAAAAA8BhKAAAAGgAAAERlZmF1bHREaXN0YW5jZUF0dGVudWF0aW9uEgAA"
    "AABQUk9QHwAAAB0AAAAAAAAA8A5KAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1AeAAAAHAAAAAAAAADwDUoAAAASAAAA"
    "RW5hYmxlRGVmYXVsdFZvaWNlAgFQUk9QKAAAACYAAAAAAAAA8BdKAAAAGQAAAEVuYWJsZVZvaWNlVm9sdW1lQ29udHJvbHMSAAAA"
    "AFBST1AdAAAAIgAAAAAAAAD2BEoAAAAJAAAASGlzdG9yeUlkHwABAFAAAAAAAFBST1AjAAAAIQAAAAAAAADwEkoAAAAEAAAATmFt"
    "ZQEQAAAAVm9pY2VDaGF0U2VydmljZVBST1AgAAAAHgAAAAAAAADwD0oAAAANAAAAU291cmNlQXNzZXRJZBsAAAAAAAAAAVBST1AT"
    "AAAAEQAAAAAAAADwAkoAAAAEAAAAVGFncxwAAAAAUFJPUCMAAAAhAAAAAAAAAPASSgAAAAgAAABVbmlxdWVJZB8AAAPkCs2j9y9D"
    "XobmVlxaUFJPUBoAAAAYAAAAAAAAAPAJSgAAAAsAAABVc2VBdWRpb0FwaRIAAAACUFJPUBkAAAAXAAAAAAAAAPAISwAAAAoAAABB"
    "aXJEZW5zaXR5BHU6kqRQUk9QJQAAACMAAAAAAAAA8BRLAAAAFgAAAEFpclR1cmJ1bGVuY2VJbnRlbnNpdHkEAAAAAFBST1AgAAAA"
    "HgAAAAAAAADwD0sAAAAUAAAAQWxsb3dUaGlyZFBhcnR5U2FsZXMCAFBST1AiAAAAIAAAAAAAAADwEUsAAAATAAAAQXR0cmlidXRl"
    "c1NlcmlhbGl6ZQEAAAAAUFJPUBwAAAAaAAAAAAAAAPALSwAAAA0AAABBdXRob3JpdHlNb2RlEgAAAAFQUk9QGAAAABYAAAAAAAAA"
    "8AdLAAAADAAAAEF1dG9TaW11bGF0ZQIBUFJPUCQAAAAiAAAAAAAAAPATSwAAABUAAABBdmF0YXJVbmlmaWNhdGlvbk1vZGUSAAAA"
    "AFBST1AfAAAAHQAAAAAAAADwDksAAAAMAAAAQ2FwYWJpbGl0aWVzIQAAAAAAAAAAUFJPUCcAAAAlAAAAAAAAAPAWSwAAABgAAABD"
    "bGllbnRBbmltYXRvclRocm90dGxpbmcSAAAAAFBST1AxAAAALwAAAAAAAADwIEsAAAASAAAAQ29sbGlzaW9uR3JvdXBEYXRhARAA"
    "AAABAQAE/////wdEZWZhdWx0UFJPUBwAAAAaAAAAAAAAAPALSwAAAA0AAABDdXJyZW50Q2FtZXJhEwAAAAJQUk9QHwAAAB0AAAAA"
    "AAAA8A5LAAAAEwAAAERlZmluZXNDYXBhYmlsaXRpZXMCAFBST1AmAAAAJAAAAAAAAADwFUsAAAATAAAARGlzdHJpYnV0ZWRHYW1l"
    "VGltZQUAAAAAAAAAAFBST1AgAAAAHgAAAAAAAADwD0sAAAARAAAARW5hYmxlU0xJTUF2YXRhcnMSAAAAAFBST1AeAAAAHAAAAAAA"
    "AADwDUsAAAAPAAAARXhwYW5kZWRUZXJyYWluEgAAAABQUk9QHgAAABwAAAAAAAAA8A1LAAAAEgAAAEV4cGxpY2l0QXV0b0pvaW50"
    "cwIBUFJPUB0AAAAbAAAAAAAAAPAMSwAAABEAAABGYWxsSGVpZ2h0RW5hYmxlZAIBUFJPUCcAAAAlAAAAAAAAAPAWSwAAABgAAABG"
    "YWxsZW5QYXJ0c0Rlc3Ryb3lIZWlnaHQEh/QAAVBST1AaAAAAGAAAAAAAAADwCUsAAAALAAAARmx1aWRGb3JjZXMSAAAAAFBST1Ah"
    "AAAAHwAAAAAAAADwEEsAAAAKAAAAR2xvYmFsV2luZA4AAAAAAAAAAAAAAABQUk9QFgAAABQAAAAAAAAA8AVLAAAABwAAAEdyYXZp"
    "dHkEhohmZlBST1AnAAAAJQAAAAAAAADwFksAAAAQAAAAR3Jhdml0eURpcmVjdGlvbg4AAAAAfwAAAQAAAABQUk9QHQAAACIAAAAA"
    "AAAA9gRLAAAACQAAAEhpc3RvcnlJZB8AAQBQAAAAAABQUk9QKQAAACcAAAAAAAAA8BhLAAAAGgAAAElLQ29udHJvbENvbnN0cmFp"
    "bnRTdXBwb3J0EgAAAABQUk9QKgAAACgAAAAAAAAA8BlLAAAAGwAAAEltcHJvdmVkQW5pbWF0aW9uQ29uc3RyYWludBIAAAAAUFJP"
    "UCkAAAAnAAAAAAAAAPAYSwAAABoAAABJbXByb3ZlZFBoeXNpY3NSZXBsaWNhdGlvbhIAAAAAUFJPUDAAAAAuAAAAAAAAAPAfSwAA"
    "ACEAAABMYXllcmVkQ2xvdGhpbmdDYWNoZU9wdGltaXphdGlvbnMSAAAAAFBST1AcAAAAGgAAAAAAAADwC0sAAAANAAAATGV2ZWxP"
    "ZkRldGFpbBIAAAAAUFJPUCAAAAAeAAAAAAAAAPAPSwAAABEAAABMdWF1VHlwZUNoZWNrTW9kZRIAAAAAUFJPUCsAAAApAAAAAAAA"
    "APAaSwAAABwAAABNYXBUVlJlbW90ZVRvR2FtZXBhZEtleWNvZGVzEgAAAABQUk9QKgAAACgAAAAAAAAA8BlLAAAAGwAAAE1lc2hQ"
    "YXJ0SGVhZHNBbmRBY2Nlc3NvcmllcxIAAAAAUFJPUCsAAAApAAAAAAAAAPAaSwAAABwAAABNZXNoU3RyZWFtaW5nQW5kSW1wcm92"
    "ZWRMb2RzEgAAAABQUk9QJwAAACUAAAAAAAAA8BZLAAAADwAAAE1vZGVsTWVzaENGcmFtZRACAAAAAAAAAAAAAAAAUFJPUBwAAAAa"
    "AAAAAAAAAPALSwAAAA0AAABNb2RlbE1lc2hEYXRhHAAAAABQUk9QJAAAACIAAAAAAAAA8BNLAAAADQAAAE1vZGVsTWVzaFNpemUO"
    "AAAAAAAAAAAAAAAAUFJPUCUAAAAjAAAAAAAAAPAUSwAAABYAAABNb2RlbFN0cmVhbWluZ0JlaGF2aW9yEgAAAABQUk9QIQAAAB8A"
    "AAAAAAAA8BBLAAAAEgAAAE1vZGVsU3RyZWFtaW5nTW9kZRIAAAAAUFJPUBwAAAAaAAAAAAAAAPALSwAAAAQAAABOYW1lAQkAAABX"
    "b3Jrc3BhY2VQUk9QHwAAAB0AAAAAAAAA8A5LAAAAEwAAAE5lZWRzUGl2b3RNaWdyYXRpb24CAFBST1AoAAAAJgAAAAAAAADwF0sA"
    "AAAZAAAATmV4dEdlbmVyYXRpb25SZXBsaWNhdGlvbhIAAAAAUFJPUCsAAAApAAAAAAAAAPAaSwAAABwAAABQYXRoZmluZGluZ1Vz"
    "ZUltcHJvdmVkU2VhcmNoEgAAAABQUk9QJAAAACIAAAAAAAAA8BNLAAAAFQAAAFBoeXNpY3NTdGVwcGluZ01ldGhvZBIAAAAAUFJP"
    "UC0AAAArAAAAAAAAAPAcSwAAAB4AAABQbGF5ZXJDaGFyYWN0ZXJEZXN0cm95QmVoYXZpb3ISAAAAAlBST1AwAAAALgAAAAAAAADw"
    "H0sAAAAhAAAAUGxheWVyU2NyaXB0c1VzZUlucHV0QWN0aW9uU3lzdGVtEgAAAAJQUk9QJgAAACQAAAAAAAAA8BVLAAAAFwAAAFBy"
    "ZWRpY3RpdmVTdHJlYW1pbmdNb2RlEgAAAABQUk9QIgAAACAAAAAAAAAA8BFLAAAAEwAAAFByaW1hbFBoeXNpY3NTb2x2ZXISAAAA"
    "AFBST1AaAAAAGAAAAAAAAADwCUsAAAALAAAAUHJpbWFyeVBhcnQTAAAAAVBST1AnAAAAJQAAAAAAAADwFksAAAAYAAAAUmVqZWN0"
    "Q2hhcmFjdGVyRGVsZXRpb25zEgAAAABQUk9QKgAAACgAAAAAAAAA8BlLAAAAGwAAAFJlbmRlcmluZ0NhY2hlT3B0aW1pemF0aW9u"
    "cxIAAAAAUFJPUC4AAAAsAAAAAAAAAPAdSwAAAB8AAABSZXBsaWNhdGVJbnN0YW5jZURlc3Ryb3lTZXR0aW5nEgAAAABQUk9QGgAA"
    "ABgAAAAAAAAA8AlLAAAACwAAAFJldGFyZ2V0aW5nEgAAAABQUk9QJAAAACIAAAAAAAAA8BNLAAAAFQAAAFNhbmRib3hlZEluc3Rh"
    "bmNlTW9kZRIAAAAAUFJPUBoAAAAYAAAAAAAAAPAJSwAAAAsAAABTY2FsZUZhY3RvcgR/AAAAUFJPUB4AAAAcAAAAAAAAAPANSwAA"
    "AA8AAABTaWduYWxCZWhhdmlvcjISAAAAAlBST1AdAAAAGwAAAAAAAADwDEsAAAAOAAAAU2ltdWxhdGlvblJhdGUEfwAAAFBST1AX"
    "AAAAFQAAAAAAAADwBksAAAAIAAAAU2xpbUhhc2gcAAAAAFBST1AgAAAAHgAAAAAAAADwD0sAAAANAAAAU291cmNlQXNzZXRJZBsA"
    "AAAAAAAAAVBST1AgAAAAHgAAAAAAAADwD0sAAAARAAAAU3RyZWFtT3V0QmVoYXZpb3ISAAAAAlBST1AjAAAAIQAAAAAAAADwEksA"
    "AAAXAAAAU3RyZWFtaW5nQWRhcHRpdmVSYWRpdXMCAFBST1AcAAAAGgAAAAAAAADwC0sAAAAQAAAAU3RyZWFtaW5nRW5hYmxlZAIB"
    "UFJPUCUAAAAjAAAAAAAAAPAUSwAAABYAAABTdHJlYW1pbmdJbnRlZ3JpdHlNb2RlEgAAAANQUk9QIQAAAB8AAAAAAAAA8BBLAAAA"
    "EgAAAFN0cmVhbWluZ01pblJhZGl1cwMAAACAUFJPUCQAAAAiAAAAAAAAAPATSwAAABUAAABTdHJlYW1pbmdUYXJnZXRSYWRpdXMD"
    "AAAIAFBST1ATAAAAEQAAAAAAAADwAksAAAAEAAAAVGFncxwAAAAAUFJPUB0AAAAbAAAAAAAAAPAMSwAAABEAAABUZXJyYWluV2Vs"
    "ZHNGaXhlZAIBUFJPUCwAAAAqAAAAAAAAAPAbSwAAAB0AAABUb3VjaEV2ZW50c1VzZUNvbGxpc2lvbkdyb3VwcxIAAAAAUFJPUCUA"
    "AAAjAAAAAAAAAPAUSwAAABkAAABUb3VjaGVzVXNlQ29sbGlzaW9uR3JvdXBzAgBQUk9QIwAAACEAAAAAAAAA8BJLAAAACAAAAFVu"
    "aXF1ZUlkHwAAAAIKzaP3L0NehuZWXFpQUk9QIQAAAB8AAAAAAAAA8BBLAAAAEgAAAFVzZUZpeGVkU2ltdWxhdGlvbhIAAAAAUFJP"
    "UBsAAAAZAAAAAAAAAPAKSwAAAAwAAABVc2VJbnB1dFNpbmsSAAAAAFBST1AjAAAAIQAAAAAAAADwEksAAAAUAAAAVXNlTmV3THVh"
    "dVR5cGVTb2x2ZXISAAAAAlBST1AtAAAAKwAAAAAAAADwHEsAAAAeAAAAVmFsaWRhdGVFbmFibGVkUHJveGltaXR5UHJvbXB0EgAA"
    "AABQUk9QEwAAABEAAAAAAAAA8AJLAAAABAAAAFdpbmQEAAAAAFBST1AkAAAAIgAAAAAAAADwE0sAAAANAAAAV2luZERpcmVjdGlv"
    "bg4AAAAAAAAAAAAAAABQUk9QJAAAACcAAAAAAAAA9AtLAAAADgAAAFdvcmxkUGl2b3REYXRhHhACAAEAUAAAAAIBUFJOVG8AAAB9"
    "AgAAAAAAAD8ATwABANyVAgQBBAQBCQ4CAQCgBAIEAgICBwoPEgwAIAMGGQAgBAEUAAwCAAEUACgJDBcADz4B22cEAwAKCQH0APEA"
    "JgAGAAAABQAlAAAAPgA9GgAhTk0HAAsCABB6EAAQeQUAkAAAAAAAAAAAAEVORAAAAAAACQAAAAAAAAA8L3JvYmxveD4="
)


def _baseplate_bytes():
    ext = Path(__file__).parent / 'templates' / 'Baseplate.rbxl'
    if ext.is_file():
        return ext.read_bytes()
    return base64.b64decode(_BASEPLATE_B64)


def _load_baseplate_into_state():
    """Открывает шаблон Baseplate как свежую несохранённую сцену. Возвращает
    число объектов; при любой ошибке бросает исключение (api_new откатится на
    пустую сцену)."""
    import tempfile
    tmp_path = None
    try:
        data = _baseplate_bytes()
        # parse_rbxl на мусоре не падает, а отдаёт пустую сцену — проверяем сами
        if data[:8] != b'<roblox!':
            raise RuntimeError('шаблон Baseplate — не бинарный .rbxl')
        with tempfile.NamedTemporaryFile(suffix='.rbxl', delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parsed = parse_rbxl(tmp_path)
        if 'Workspace' not in parsed['referent_to_class'].values():
            raise RuntimeError('в шаблоне Baseplate нет Workspace')
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    state['parsed'] = parsed
    state['file_path'] = None   # Ctrl+S откроет «Сохранить как», шаблон не перезаписывается
    return len(parsed['referent_to_class'])


@flask_app.route('/api/new', methods=['POST'])
def api_new():
    """Новая сцена = шаблон Baseplate (см. _load_baseplate_into_state); если
    он по какой-то причине не загрузился — пустая сцена, как раньше:
    создаёт её в памяти сервера (без файла на диске) — набор
    стандартных сервисов Roblox верхнего уровня, как в новом плейсе.
    Нужно, чтобы фичи вроде импорта Instance (например, 3D-аватара)
    работали даже без предварительно открытого .rbxl — раньше PUT
    /api/instance молча отваливался с ok:false, если state['parsed']
    был None, и объект оставался только визуальным в вьюпорте, не
    попадая ни в Explorer, ни в сохраняемый файл. save_rbxl умеет
    полностью пересобрать бинарник даже без _raw_chunks/_raw_data
    (см. ветку "с нуля" в save_rbxl), так что Save/Save As после этого
    работает как обычно — путь просто нужно будет выбрать при сохранении."""
    want_empty = ((request.get_json(silent=True) or {}).get('template') == 'empty')
    if not want_empty:
        try:
            return jsonify({'ok': True, 'count': _load_baseplate_into_state(), 'template': 'Baseplate'})
        except Exception:
            traceback.print_exc()   # шаблон не загрузился — делаем пустую сцену, как раньше
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


_VALUE_CLASSES = ('StringValue', 'NumberValue', 'IntValue', 'BoolValue',
                  'Vector3Value', 'CFrameValue', 'Color3Value', 'ObjectValue')


_REF_PROP_CLASSES = ('RigidConstraint', 'WeldConstraint', 'Weld', 'ManualWeld', 'Motor6D', 'Motor', 'BallSocketConstraint',
                    'NoCollisionConstraint', 'AnimationConstraint', 'HingeConstraint', 'SpringConstraint')


def _attachment_cf(q):
    """Attachment.CFrame из свойств файла -> [x, y, z, R00..R22] (row-major, как CFrame:GetComponents())."""
    import math as _m
    cf = q.get('CFrame') if isinstance(q.get('CFrame'), dict) else {}
    pos = cf.get('position') if isinstance(cf.get('position'), dict) else (q.get('Position') if isinstance(q.get('Position'), dict) else {})
    x, y, z = (float(pos.get(k, 0.0)) for k in ('x', 'y', 'z'))
    m = cf.get('matrix')
    if isinstance(m, (list, tuple)) and len(m) == 9:
        rot = [float(v) for v in m]
    elif isinstance(cf.get('angles_deg'), (list, tuple)) and len(cf['angles_deg']) == 3:
        rx, ry, rz = (_m.radians(float(v)) for v in cf['angles_deg'])   # Orientation: порядок Y, X, Z
        cx, sx, cy, sy, cz, sz = _m.cos(rx), _m.sin(rx), _m.cos(ry), _m.sin(ry), _m.cos(rz), _m.sin(rz)
        rot = [cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx,
               cx * sz, cx * cz, -sx,
               -sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx]
    else:
        rot = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    return [x, y, z] + rot


def _value_for_client(cls, v):
    # Примитивы отдаём как есть; Vector3/CFrame/Color3/ObjectValue — в виде
    # {'k': вид, 'v': [...]}, фронтенд соберёт из них Lua-значения.
    if v is None:
        return None
    if cls in ('StringValue',):
        return str(v)
    if cls in ('NumberValue', 'IntValue'):
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    if cls == 'BoolValue':
        return bool(v)
    if cls == 'Vector3Value' and isinstance(v, dict) and 'x' in v:
        return {'k': 'v3', 'v': [v['x'], v['y'], v['z']]}
    if cls == 'CFrameValue' and isinstance(v, dict) and 'position' in v:
        m = v.get('matrix') or [1, 0, 0, 0, 1, 0, 0, 0, 1]
        p = v['position']
        return {'k': 'cf', 'v': [p['x'], p['y'], p['z']] + list(m)}
    if cls == 'Color3Value':
        if isinstance(v, dict) and all(c in v for c in ('r', 'g', 'b')):
            return {'k': 'c3', 'v': [v['r'], v['g'], v['b']]}
        return None
    if cls == 'ObjectValue':
        return {'k': 'ref', 'v': [v]} if isinstance(v, int) and v >= 0 else None
    return None


def _decode_attributes(data):
    """AttributesSerialize (бинарный формат атрибутов Roblox) -> {имя: значение} для string/bool/number.
    Остальные типы (Color3, Vector, UDim...) пропускаются, но читаются до конца, чтобы не сбить следующие атрибуты.
    Формат: u32 число атрибутов; для каждого: u32 длина имени, имя, u8 тип, значение (string: u32 длина + байты;
    bool: 1; int32: 4; float: 4; double: 8; UDim 8; UDim2 16; BrickColor 4; Color3/Vector3 12; Vector2 8).
    Сверено на реальных данных карты (30 инстансов, типы 0x02/0x03/0x06/0x0F/0x10, декодер доходит до конца)."""
    import struct
    out = {}
    try:
        n = struct.unpack_from('<I', data, 0)[0]
        o = 4
        for _ in range(n):
            ln = struct.unpack_from('<I', data, o)[0]; o += 4
            name = data[o:o + ln].decode('utf-8', 'replace'); o += ln
            t = data[o]; o += 1
            if t == 0x02:
                l2 = struct.unpack_from('<I', data, o)[0]; o += 4
                out[name] = data[o:o + l2].decode('utf-8', 'replace'); o += l2
            elif t == 0x03:
                out[name] = bool(data[o]); o += 1
            elif t == 0x04:
                out[name] = struct.unpack_from('<i', data, o)[0]; o += 4
            elif t == 0x05:
                out[name] = struct.unpack_from('<f', data, o)[0]; o += 4
            elif t == 0x06:
                out[name] = struct.unpack_from('<d', data, o)[0]; o += 8
            elif t == 0x09 or t == 0x10:
                o += 8
            elif t == 0x0A:
                o += 16
            elif t == 0x0E:
                o += 4
            elif t == 0x0F or t == 0x11:
                o += 12
            else:
                break    # неизвестный тип — размер неизвестен, дальше читать нельзя
    except Exception:
        pass
    return out


def _decode_tags(value, shared_strings):
    """Свойство Tags (CollectionService) хранится как SharedString: строка тегов через \0."""
    raw = None
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < len(shared_strings):
        raw = shared_strings[value][1]
    elif isinstance(value, (bytes, bytearray)):
        raw = value
    if not raw:
        return []
    return [t for t in bytes(raw).decode('utf-8', 'replace').split('\0') if t]


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
        # Атрибуты и теги объекта из файла (Tool: viewModel/damage/..., форсфилды: теги PinkForcefield и т.д.) —
        # раньше не читались вообще, поэтому GetAttribute/GetTagged по объектам карты всегда возвращали nil/пусто.
        _pp = pr.get(ref, {})
        _ab = _pp.get('AttributesSerialize')
        if isinstance(_ab, (bytes, bytearray)) and _ab:
            _attrs = _decode_attributes(bytes(_ab))
            if _attrs:
                item['attrs'] = _attrs
        # Свойства Tool из файла (TextureId — иконка в хотбаре, ToolTip, CanBeDropped, ...): без них tool.TextureId был пуст
        # и хотбар рисовал слоты без картинок.
        if cls == 'Tool':
            _tp = {}
            for _k in ('TextureId', 'ToolTip', 'CanBeDropped', 'RequiresHandle', 'Enabled', 'ManualActivationOnly'):
                _v = _pp.get(_k)
                if isinstance(_v, (str, bool)):
                    _tp[_k] = _v
            if _tp:
                item['gprops'] = _tp
        _tg = _decode_tags(_pp.get('Tags'), parsed.get('shared_strings') or [])
        if _tg:
            item['tags'] = _tg
        # Model.WorldPivotData (OptionalCFrame, мировой): без него Model.WorldPivot/GetPivot считались
        # по центру габаритов, а скрипты вроде ElevatorSpawner (ELEV1.WorldPivot) падали на nil.
        _wp = _pp.get('WorldPivotData')
        if isinstance(_wp, dict):
            _wx, _wy, _wz = get_pos(_wp)
            item['pivot'] = {'p': [_wx, _wy, _wz], 'r': get_rot_matrix(_wp)}
        # Model.PrimaryPart (ссылка на деталь): pivot модели = pivot этой детали. Без него скрипты вроде спавна комнат
        # (room.PrimaryPart = маркер двери; room:PivotTo(...)) ставили комнату не по маркеру, а по центру габаритов.
        if cls == 'Model':
            _ppr = _pp.get('PrimaryPart')
            if isinstance(_ppr, int) and not isinstance(_ppr, bool) and _ppr in r2c:
                item['refs'] = {'PrimaryPart': _ppr}
        if cls == 'Team':
            item['teamColor'] = _pp.get('TeamColor')
            item['autoAssignable'] = _pp.get('AutoAssignable', True)
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
        elif cls == 'Attachment':
            item['att'] = _attachment_cf(pr.get(ref, {}))
        elif cls in _REF_PROP_CLASSES:
            # Ссылки Part0/Part1/Attachment0/Attachment1 (сварки и констрейнты): скрипты находят по ним, что
            # к чему прикреплено (например, аксессуар к голове через RigidConstraint).
            qq = pr.get(ref, {})
            refs = {}
            for key in ('Part0', 'Part1', 'Attachment0', 'Attachment1'):
                if key in qq:
                    vv = qq.get(key)
                    refs[key] = vv if (isinstance(vv, int) and not isinstance(vv, bool) and vv in r2c) else -1
            if refs:
                item['refs'] = refs
        elif cls in _VALUE_CLASSES:
            # ValueBase.Value, лежащий В ФАЙЛЕ (IntValue/CFrameValue/...) — иначе
            # Lua видит nil, пока скрипт сам что-нибудь не запишет в .Value.
            val = _value_for_client(cls, pr.get(ref, {}).get('Value'))
            if val is not None:
                item['value'] = val
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
        # В .rbxl флаг отключённого скрипта хранится как Disabled (а не Enabled) — раньше он игнорировался,
        # и Script с Disabled=true всё равно запускался в Play.
        disabled = props.get('Disabled', False)
        if isinstance(disabled, str):
            disabled = disabled.lower() in ('true', '1')
        if cls != 'ModuleScript' and (not enabled or disabled):
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
            'side': ('client' if (cls == 'Script' and props.get('RunContext') == 2)
                     else SCRIPT_SIDE.get(cls, 'server')),
            # Script.RunContext: 0 = Legacy (сервер), 1 = Server, 2 = Client — Script с Client
            # исполняется на клиенте (там есть Players.LocalPlayer), а не на сервере
            'runContext': props.get('RunContext'),
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
                v = props[pname]
                # MaxDistance = inf (по умолчанию у BillboardGui) нельзя отдавать в JSON: Infinity невалиден,
                # fetch().json() падает и весь Play. Нет поля = без ограничения дистанции.
                if isinstance(v, float) and (v != v or v in (float('inf'), float('-inf'))):
                    continue
                item[pname] = v
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
    # Шаблоны (ServerStorage/ReplicatedStorage): клиент в Play их не рисует, но данные нужны Clone() — отдаём ВСЕ сразу,
    # без лимита по дистанции (иначе у дальних шаблонов комнат/врагов клоны остаются без меша).
    if request.args.get('nw') == '1':
        if not state['parsed']:
            return jsonify({'ok': True, 'objects': []})
        return jsonify({'ok': True, 'objects': [o for o in build_all_scene_objects() if o.get('nw')]})
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


@flask_app.route('/api/proximity_prompts')
def api_proximity_prompts():
    """Все ProximityPrompt на карте — сразу все и один раз (список обычно
    маленький, не привязан к потоковой загрузке по радиусу, а сам объект
    может понадобиться игроку ещё до того, как он попадёт в LOD-радиус
    камеры). Клиент сам меряет дистанцию до parentRef каждый кадр — здесь
    только статические данные из файла."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'nothing open'}), 400
    out = []
    for ref, cls in parsed['referent_to_class'].items():
        if cls != 'ProximityPrompt':
            continue
        props = parsed['props'].get(ref, {})
        parent_ref = parsed['parent_map'].get(ref, -1)
        parent_cls = parsed['referent_to_class'].get(parent_ref)
        if parent_cls not in PART_CLASSES and parent_cls != 'Model':
            continue  # подсказка не на детали/модели — дистанцию мерить не от чего
        enabled = props.get('Enabled', True)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ('true', '1')
        requires_los = props.get('RequiresLineOfSight', True)
        if isinstance(requires_los, str):
            requires_los = requires_los.lower() in ('true', '1')
        out.append({
            'ref': ref,
            'parentRef': parent_ref,
            'actionText': props.get('ActionText', 'Interact'),
            'objectText': props.get('ObjectText', ''),
            'keyCode': props.get('KeyboardKeyCode', 'E'),
            'holdDuration': safe_float(props.get('HoldDuration', 0.0), 0.0),
            'maxDistance': safe_float(props.get('MaxActivationDistance', 10.0), 10.0),
            'requiresLineOfSight': bool(requires_los),
            'enabled': bool(enabled),
            'style': props.get('Style', 'Default'),
        })
    return jsonify({'ok': True, 'prompts': out})


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
        neutral = props.get('Neutral', True)
        if isinstance(neutral, str):
            neutral = neutral.lower() in ('true', '1')
        candidates.append((bool(anchored), px, py + sy * 0.5, pz, props.get('TeamColor'), bool(neutral)))

    if not candidates:
        return jsonify({'ok': False, 'error': 'no SpawnLocation in scene'})

    # team=auto: как в Roblox, игрок при входе попадает в первую AutoAssignable-команду и появляется на SpawnLocation
    # СВОЕЙ команды (TeamColor совпал, Neutral=false); нет такого — на нейтральном. Раньше брался просто первый спавн,
    # и Pink-игрок оказывался в зелёной зоне, по ту сторону чужого форсфилда.
    if request.args.get('team') == 'auto':
        team_color = None
        for ref, cls in parsed['referent_to_class'].items():
            if cls == 'Team' and parsed['props'].get(ref, {}).get('AutoAssignable', True):
                team_color = parsed['props'].get(ref, {}).get('TeamColor')
                break
        if team_color is not None:
            exact = [c for c in candidates if c[4] == team_color and not c[5]]
            neutral_c = [c for c in candidates if c[5]]
            if exact:
                candidates = exact
            elif neutral_c:
                candidates = neutral_c

    candidates.sort(key=lambda c: not c[0])  # anchored=True первыми
    x, y, z = candidates[0][1], candidates[0][2], candidates[0][3]
    return jsonify({'ok': True, 'x': x, 'y': y, 'z': z, 'anchored': candidates[0][0]})


@flask_app.route('/api/instance/<int:ref>')
def api_get_instance(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    cls = parsed['referent_to_class'].get(ref, '?')
    props = {k: serialize_prop(v)
             for k, v in parsed['props'].get(ref, {}).items()}
    # Прослушивание звука прямо из Explorer (buildSoundPreviewRow) раньше
    # играло его "как есть", без PlaybackSpeed/PitchShiftSoundEffect —
    # звучало не так, как в реальной игре. Octave лежит не в самом Sound, а
    # в дочернем PitchShiftSoundEffect, поэтому ищем его отдельно, как и в
    # /api/all_instances.
    pitch_octave = None
    if cls == 'Sound':
        for child_ref, parent_ref in parsed['parent_map'].items():
            if parent_ref != ref:
                continue
            if parsed['referent_to_class'].get(child_ref) == 'PitchShiftSoundEffect':
                cp = parsed['props'].get(child_ref, {})
                if cp.get('Enabled', True):
                    pitch_octave = safe_float(cp.get('Octave', 0.0), 0.0)
                break
    return jsonify({
        'ok': True, 'ref': ref, 'cls': cls,
        'icon': icon_src(cls), 'props': props,
        'parent': parsed['parent_map'].get(ref, -1),
        'pitchOctave': pitch_octave,
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


def _m3_mul(a, b):
    """3x3 (по строкам, 9 чисел) * 3x3."""
    return [sum(a[i * 3 + k] * b[k * 3 + j] for k in range(3)) for i in range(3) for j in range(3)]


def _m3_vec(m, v):
    return [m[i * 3] * v[0] + m[i * 3 + 1] * v[1] + m[i * 3 + 2] * v[2] for i in range(3)]


_PARTICLE_PROPS = (
    'Enabled', 'Rate', 'Lifetime', 'Speed', 'SpreadAngle', 'Rotation', 'RotSpeed',
    'Size', 'Transparency', 'Color', 'Squash', 'Acceleration', 'Drag', 'Texture',
    'LightEmission', 'LightInfluence', 'Brightness', 'EmissionDirection', 'LockedToPart',
    'TimeScale', 'ZOffset', 'Shape', 'ShapeStyle', 'ShapeInOut', 'ShapePartial',
    'Orientation', 'VelocityInheritance', 'WindAffectsDrag',
)


@flask_app.route('/api/particles')
def api_particles():
    """Все ParticleEmitter сцены: где они стоят (мировая позиция/поворот
    эмиттера и относительная к детали) и их свойства. Рисует их клиент
    (script.js, блок «ЧАСТИЦЫ»). Родитель эмиттера — Attachment (точка) или
    сама деталь (тогда частицы появляются в объёме детали)."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': True, 'emitters': []})
    r2c, pmap, allp = parsed['referent_to_class'], parsed['parent_map'], parsed['props']
    out = []
    for ref, cls in r2c.items():
        if cls != 'ParticleEmitter':
            continue
        parent = pmap.get(ref, -1)
        pcls = r2c.get(parent)
        if pcls == 'Attachment':
            att_cf = allp.get(parent, {}).get('CFrame')
            part = pmap.get(parent, -1)
            on_part = False
        elif pcls in PART_CLASSES:
            att_cf, part, on_part = None, parent, True
        else:
            continue
        if r2c.get(part) not in PART_CLASSES:
            continue
        pp = allp.get(part, {})
        pcf = pp.get('CFrame', {})
        px, py, pz = get_pos(pcf)
        prot = get_rot_matrix(pcf)
        ax, ay, az = get_pos(att_cf) if att_cf else (0.0, 0.0, 0.0)
        arot = get_rot_matrix(att_cf) if att_cf else [1, 0, 0, 0, 1, 0, 0, 0, 1]
        wpos = [a + b for a, b in zip(_m3_vec(prot, [ax, ay, az]), [px, py, pz])]
        wrot = _m3_mul(prot, arot)
        sz = pp.get('Size', {})
        size = [safe_float(sz.get('x', 1), 1), safe_float(sz.get('y', 1), 1), safe_float(sz.get('z', 1), 1)] \
            if isinstance(sz, dict) else [1, 1, 1]
        props = allp.get(ref, {})
        out.append({
            'ref': ref, 'name': props.get('Name', 'ParticleEmitter'), 'part': part,
            'onPart': on_part, 'partSize': size,
            'att': {'p': [ax, ay, az], 'r': arot},
            'world': {'p': wpos, 'r': wrot},
            'p': {k: props[k] for k in _PARTICLE_PROPS if k in props},
        })
    return jsonify({'ok': True, 'emitters': out})


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


@flask_app.route('/api/reparent', methods=['POST'])
def api_reparent():
    """Перенос объектов в другого родителя (drag & drop в Explorer).
    Тело: {"refs": [..], "parent": ref}. Мировые координаты не меняются —
    как в Roblox, меняется только дерево."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': 'Файл не загружен'}), 400
    data = request.json or {}
    try:
        refs = [int(r) for r in (data.get('refs') or [])]
        parent = int(data.get('parent'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Некорректные refs/parent'}), 400
    r2c, pm = parsed['referent_to_class'], parsed['parent_map']
    if parent not in r2c:
        return jsonify({'ok': False, 'error': 'Родитель не найден'}), 400

    def ancestors(ref):
        seen, cur = set(), ref
        while cur in pm and cur not in seen:
            seen.add(cur)
            cur = pm[cur]
            if cur == -1 or cur not in r2c:
                break
            seen.add(cur)
        return seen

    parent_chain = ancestors(parent) | {parent}
    moved, skipped = [], []
    for ref in refs:
        if ref not in r2c or ref == parent:
            skipped.append(ref); continue
        # нельзя класть объект в самого себя или в своего потомка
        if ref in parent_chain:
            skipped.append(ref); continue
        # сервисы (корни без родителя) и Terrain/Camera не переносим
        if pm.get(ref, -1) in (-1, None) or pm.get(ref) not in r2c or r2c[ref] in ('Terrain', 'Camera'):
            skipped.append(ref); continue
        if pm.get(ref) == parent:
            skipped.append(ref); continue
        pm[ref] = parent
        moved.append(ref)
    if moved:
        parsed['_modified'] = True
        bump_scene_version()
    return jsonify({'ok': True, 'moved': moved, 'skipped': skipped})


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
            _recents_add_file(p)
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


@flask_app.route('/api/roblox/cookie', methods=['POST'])
def api_roblox_cookie_save():
    """Вход на десктопе (в Android входит WebView, см. RobloxLoginActivity).
    Тело: {cookie}: значение .ROBLOSECURITY (с префиксом или без). Кука
    проверяется запросом к Roblox и сохраняется в roblox_auth.json (0600);
    в ответ она НЕ возвращается. Только с локальной машины: кука даёт
    полный доступ к аккаунту, а сервер слушает 0.0.0.0."""
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return jsonify({'ok': False, 'error': 'Только с локального устройства'}), 403
    body = request.get_json(silent=True) or {}
    val = str(body.get('cookie') or '').strip().strip('"\'')
    if val.upper().startswith('.ROBLOSECURITY='):
        val = val.split('=', 1)[1].strip().strip('"\'')
    if len(val) < 100 or any(c in val for c in ' ;\r\n'):
        return jsonify({'ok': False, 'error': 'Не похоже на значение .ROBLOSECURITY'}), 400

    p = _roblox_auth_file()
    old = p.read_text(encoding='utf-8') if p.exists() else None
    try:
        p.write_text(json.dumps({'cookie': '.ROBLOSECURITY=' + val}), encoding='utf-8')
        try:
            os.chmod(p, 0o600)
        except Exception:
            pass
        d = _rbx_get_json('https://users.roblox.com/v1/users/authenticated')
        if not (isinstance(d, dict) and d.get('id')):
            raise RuntimeError('в ответе нет id')
    except Exception as e:
        # не прошла проверка — возвращаем прежнее состояние
        try:
            if old is None:
                p.unlink()
            else:
                p.write_text(old, encoding='utf-8')
        except Exception:
            pass
        return jsonify({'ok': False, 'error': f'Roblox не принял куку: {e}'}), 400
    return jsonify({'ok': True, 'name': d.get('name') or '', 'userId': d.get('id')})


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


# --- Сжатие дискового кэша -------------------------------------------------
# Файлы кэша бывают трёх видов (вид определяется по имени/сигнатуре, поэтому ничего
# не ломается, если в папке лежит смесь):
#   <имя>        — сырые байты (старый формат, до сжатия);
#   <имя>.zst    — zstd (если установлен пакет zstandard — он уже нужен для .rbxl);
#   <имя>.gz     — gzip (запасной вариант без zstandard).
# Чтение понимает все три, а ещё сырой файл, внутри которого лежит готовый
# zstd/gzip-поток (определяется по сигнатуре), так что уже сжатые кем-то кэши подхватываются.
# Запись сжимает только то, что реально ужимается: JPEG/MP3/OGG/WEBP уже сжаты, а
# сжатая копия оставляется лишь при выигрыше не меньше 10% — иначе лежит сырой файл.
# Старые несжатые файлы сжимает фоновая задача (cache_compact), один раз на файл.
import gzip as _cgzip
import threading as _cthreading
try:
    import zstandard as _czstd
except Exception:  # пакета нет (например, урезанная сборка) — работаем через gzip
    _czstd = None

_CACHE_ZSTD_MAGIC = b'\x28\xb5\x2f\xfd'
_CACHE_GZIP_MAGIC = b'\x1f\x8b'
_CACHE_CODEC_SUFFIXES = ('.zst', '.gz')
_CACHE_SKIP_COMPRESS_CT = {'image/jpeg', 'audio/mpeg', 'audio/ogg', 'image/webp', 'video/mp4'}
_CACHE_MIN_SIZE = 256        # меньше — смысла нет
_CACHE_MIN_GAIN = 0.90       # сжатая копия должна быть ≤ 90% оригинала
_CACHE_SKIP_INDEX = 'compact_skip.json'   # имена, которые уже пробовали и сжать не удалось (не пробуем каждый запуск)
_cache_compact_started = False
_cache_compact_lock = _cthreading.Lock()


def _cache_compress(raw):
    """-> (суффикс, байты): zstd, если есть, иначе gzip."""
    if _czstd is not None:
        return '.zst', _czstd.ZstdCompressor(level=6).compress(raw)
    return '.gz', _cgzip.compress(raw, 6, mtime=0)


def _cache_decode(data):
    """Распаковывает zstd/gzip-поток по сигнатуре. Исключение — если распаковать нельзя."""
    if data[:4] == _CACHE_ZSTD_MAGIC:
        if _czstd is None:
            raise RuntimeError('запись сжата zstd, а пакет zstandard не установлен')
        return _czstd.ZstdDecompressor().decompressobj().decompress(data)
    if data[:2] == _CACHE_GZIP_MAGIC:
        return _cgzip.decompress(data)
    raise ValueError('не сжатый поток')


def _cache_read_file(f):
    """Байты файла кэша с прозрачной распаковкой; None — прочитать/распаковать нельзя (= промах кэша)."""
    try:
        data = f.read_bytes()
    except OSError:
        return None
    coded = f.name.endswith(_CACHE_CODEC_SUFFIXES)
    if coded or data[:4] == _CACHE_ZSTD_MAGIC or data[:2] == _CACHE_GZIP_MAGIC:
        try:
            return _cache_decode(data)
        except Exception:
            # помеченный .zst/.gz, но битый/нераспаковываемый — промах; сырой файл, который лишь
            # похож на поток по первым байтам, отдаём как есть
            return None if coded else data
    return data


def _cache_find(base):
    """Файл кэша для <base> в любом виде (сжатый предпочтительнее — он новее после сжатия) или None."""
    for sfx in _CACHE_CODEC_SUFFIXES + ('',):
        f = base.with_name(base.name + sfx)
        if f.is_file():
            return f
    return None


def _cache_store(base, raw, content_type):
    """Атомарно пишет <base>[.zst|.gz]. Возвращает размер записанного файла или None при ошибке."""
    data, suffix = raw, ''
    if content_type not in _CACHE_SKIP_COMPRESS_CT and len(raw) >= _CACHE_MIN_SIZE:
        try:
            sfx, comp = _cache_compress(raw)
            if len(comp) <= len(raw) * _CACHE_MIN_GAIN:
                data, suffix = comp, sfx
        except Exception:
            pass  # сжать не вышло — пишем как есть
    target = base.with_name(base.name + suffix)
    tmp = target.with_name(target.name + '.tmp')
    try:
        tmp.write_bytes(data)
        os.replace(tmp, target)
        return len(data)
    except OSError:
        try:
            tmp.unlink()
        except OSError:
            pass
        return None


def _cache_name_ct(name):
    """'123__image_png.bin(.zst)' -> 'image/png'; для остальных файлов — application/octet-stream."""
    for sfx in _CACHE_CODEC_SUFFIXES:
        if name.endswith(sfx):
            name = name[:-len(sfx)]
    if name.endswith('.json'):
        return 'application/json'
    if '__' in name and name.endswith('.bin'):
        return name[:-4].split('__', 1)[1].replace('_', '/')
    return 'application/octet-stream'


def cache_stats():
    """Размеры кэша: сколько файлов/байт сырых и сжатых (и сколько они занимали бы без сжатия — для сжатых
    берём размер распакованного содержимого из заголовка zstd/gzip недёшево, поэтому показываем фактический)."""
    d = _asset_cache_dir()
    st = {'codec': 'zstd' if _czstd is not None else 'gzip', 'raw_files': 0, 'raw_bytes': 0,
          'compressed_files': 0, 'compressed_bytes': 0, 'total_bytes': 0}
    for f in d.iterdir():
        if not f.is_file() or f.name.endswith('.tmp') or f.name == _CACHE_SKIP_INDEX:
            continue
        n = f.stat().st_size
        if f.name.endswith(_CACHE_CODEC_SUFFIXES):
            st['compressed_files'] += 1
            st['compressed_bytes'] += n
        else:
            st['raw_files'] += 1
            st['raw_bytes'] += n
        st['total_bytes'] += n
    return st


def cache_compact():
    """Сжимает старые несжатые файлы кэша. Безопасно к параллельному чтению: сначала пишется сжатая копия
    (атомарно), потом удаляется сырой оригинал; дата изменения сохраняется (по ней считается TTL аватаров).
    -> {'compressed': N, 'saved_bytes': B, 'skipped': M}."""
    import json as _json
    d = _asset_cache_dir()
    idx_path = d / _CACHE_SKIP_INDEX
    try:
        skip = _json.loads(idx_path.read_text(encoding='utf-8'))
    except Exception:
        skip = {}
    done, saved, skipped, skip_changed = 0, 0, 0, False
    for f in list(d.iterdir()):
        name = f.name
        if (not f.is_file() or name == _CACHE_SKIP_INDEX or name.endswith('.tmp')
                or name.endswith(_CACHE_CODEC_SUFFIXES) or not (name.endswith('.bin') or name.endswith('.json'))):
            continue
        try:
            stt = f.stat()
            if skip.get(name) == stt.st_size or _cache_name_ct(name) in _CACHE_SKIP_COMPRESS_CT:
                skipped += 1
                continue
            raw = f.read_bytes()
            if raw[:4] == _CACHE_ZSTD_MAGIC or raw[:2] == _CACHE_GZIP_MAGIC:
                # «уже сжатый» файл под именем .bin — переименовываем под настоящий вид, ничего не пережимая
                target = f.with_name(name + ('.zst' if raw[:4] == _CACHE_ZSTD_MAGIC else '.gz'))
                os.replace(f, target)
                done += 1
                continue
            if len(raw) < _CACHE_MIN_SIZE:
                skip[name] = stt.st_size; skip_changed = True
                continue
            sfx, comp = _cache_compress(raw)
            if len(comp) > len(raw) * _CACHE_MIN_GAIN:
                skip[name] = stt.st_size; skip_changed = True   # не ужимается — не пробуем снова
                skipped += 1
                continue
            target = f.with_name(name + sfx)
            tmp = target.with_name(target.name + '.tmp')
            tmp.write_bytes(comp)
            os.utime(tmp, (stt.st_atime, stt.st_mtime))
            os.replace(tmp, target)
            f.unlink()
            done += 1
            saved += len(raw) - len(comp)
        except Exception:
            continue  # один проблемный файл не должен останавливать остальные
    if skip_changed:
        try:
            idx_path.write_text(_json.dumps(skip), encoding='utf-8')
        except OSError:
            pass
    return {'compressed': done, 'saved_bytes': saved, 'skipped': skipped}


def _start_cache_compaction_once():
    """Один раз за запуск: фоновая задача сжимает старые файлы кэша (отключается RSW_CACHE_COMPACT=0)."""
    global _cache_compact_started
    with _cache_compact_lock:
        if _cache_compact_started or os.environ.get('RSW_CACHE_COMPACT') == '0':
            return
        _cache_compact_started = True

    def _run():
        import time as _t
        _t.sleep(10)   # не мешаем старту приложения и первым запросам
        try:
            cache_compact()
        except Exception:
            pass
    _cthreading.Thread(target=_run, daemon=True, name='asset-cache-compact').start()


def _asset_cache_dir():
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    d = Path(data_dir) / 'asset_cache'
    d.mkdir(parents=True, exist_ok=True)
    _start_cache_compaction_once()
    return d


def _asset_cache_disk_get(asset_id):
    """Ищет ассет на диске — имя файла кодирует content-type, чтобы не
    городить отдельный файл-метаданные на каждый ассет. Сжатые записи
    (.zst/.gz) и сырые читаются одинаково."""
    try:
        for f in _asset_cache_dir().glob(f'{asset_id}__*'):
            if f.name.endswith('.tmp'):
                continue
            data = _cache_read_file(f)
            if data is None:
                continue
            return _cache_name_ct(f.name), data
    except Exception:
        pass
    return None


def _asset_cache_disk_put(asset_id, content_type, raw_bytes):
    try:
        d = _asset_cache_dir()
        if any(not f.name.endswith('.tmp') for f in d.glob(f'{asset_id}__*')):
            return  # уже есть (в любом виде)
        safe_ct = content_type.replace('/', '_')
        _cache_store(d / f'{asset_id}__{safe_ct}.bin', raw_bytes, content_type)
    except Exception:
        pass  # дисковый кэш — best-effort, не должен ронять сам запрос


@flask_app.route('/api/cache/stats')
def api_cache_stats():
    return jsonify({'ok': True, **cache_stats()})


@flask_app.route('/api/cache/compact', methods=['POST'])
def api_cache_compact():
    """Сжать старые файлы кэша сейчас (синхронно) и вернуть итог + новую статистику."""
    return jsonify({'ok': True, **cache_compact(), 'stats': cache_stats()})


@flask_app.route('/api/union_mesh')
def api_union_mesh():
    """Геометрия UnionOperation: {'position': [...], 'normal': [...], 'triangles': N}.
    Координаты локальные (относительно CFrame юниона). 404 — меша нет или
    формат не поддержан (клиент оставляет box)."""
    parsed = state.get('parsed')
    ref = request.args.get('ref', type=int)
    if not parsed or ref is None or parsed['referent_to_class'].get(ref) != 'UnionOperation':
        return jsonify({'ok': False, 'error': 'not a union'}), 404
    key = (id(parsed), ref, parsed['props'].get(ref, {}).get('SolidMeshHolder'))
    hit = _union_mesh_cache.get(key)
    if hit is None:
        m = union_mesh_from_parsed(parsed, ref)
        hit = union_mesh_render_json(m) if m else False
        if hit:
            # Меш хранится в InitialSize, а Size детали мог быть изменён (масштаб) — в Roblox
            # геометрия юниона растягивается на Size/InitialSize по каждой оси.
            _pp = parsed['props'].get(ref, {})
            _ini, _sz = _pp.get('InitialSize'), _pp.get('Size', _pp.get('size'))
            if isinstance(_ini, dict) and isinstance(_sz, dict):
                try:
                    k = [float(_sz[c]) / float(_ini[c]) if abs(float(_ini[c])) > 1e-6 else 1.0 for c in 'xyz']
                except (KeyError, TypeError, ValueError):
                    k = [1.0, 1.0, 1.0]
                if any(abs(v - 1.0) > 1e-3 for v in k):
                    pos, nrm = hit['position'], hit['normal']
                    hit = dict(hit)
                    hit['position'] = [pos[i] * k[i % 3] for i in range(len(pos))]
                    nn = []   # нормаль при неравномерном масштабе: делим на k и нормируем
                    for i in range(0, len(nrm), 3):
                        x, y, z = nrm[i] / k[0], nrm[i + 1] / k[1], nrm[i + 2] / k[2]
                        ln = (x * x + y * y + z * z) ** 0.5 or 1.0
                        nn.extend((x / ln, y / ln, z / ln))
                    hit['normal'] = nn
        if len(_union_mesh_cache) > 512:
            _union_mesh_cache.clear()
        _union_mesh_cache[key] = hit
    if not hit:
        return jsonify({'ok': False, 'error': 'no solid mesh'}), 404
    return jsonify(hit)


_union_mesh_cache = {}


def _asset_response(raw_bytes, content_type):
    """Ассеты по id иммутабельны (rbxassetid:// не меняет содержимое под
    тем же id) — раньше ответ уходил вообще без Cache-Control, и браузер
    честно перезапрашивал одну и ту же картинку/звук при каждой
    перерисовке GUI (например карточек песен в меню) заново через тот же
    локальный сервер, хотя байты гарантированно те же самые."""
    resp = Response(raw_bytes, mimetype=content_type)
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return resp


@flask_app.route('/api/asset-export', methods=['POST'])
def api_asset_export():
    """Кладёт ассет (меш/текстуру/звук) во временный файл в папке данных приложения — для Android-моста
    AndroidBridge.exportRbxlFile (системный диалог «Сохранить как», пользователь сам выбирает папку).
    Берёт байты тем же путём, что /api/asset-proxy (память -> диск -> сеть)."""
    body = request.get_json(silent=True) or {}
    data_dir = Path(os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)).resolve()
    ids = []
    for x in (body.get('ids') or []):
        mm = _re.search(r'\d+', str(x))
        if mm and mm.group() not in ids:
            ids.append(mm.group())
    if len(ids) > 1:
        # Несколько ассетов — один ZIP (удобно отдавать одним файлом). Недоступные пропускаем и перечисляем.
        import io as _io, zipfile as _zipfile, base64 as _b64
        buf = _io.BytesIO()
        got, missing = [], []
        with _zipfile.ZipFile(buf, 'w', _zipfile.ZIP_DEFLATED) as zf:
            for aid in ids[:60]:
                with flask_app.test_request_context('/api/asset-proxy?id=' + aid):
                    resp = api_asset_proxy()
                    ok = getattr(resp, 'status_code', 200) == 200
                    raw = resp.get_data() if ok else b''
                if not raw:
                    missing.append(aid)
                    continue
                ext = ('.mesh' if raw.startswith(b'version ') else '.png' if raw[:4] == b'\x89PNG' else
                       '.ogg' if raw[:4] == b'OggS' else '.jpg' if raw[:2] == b'\xff\xd8' else '.bin')
                zf.writestr('asset_%s%s' % (aid, ext), raw)
                got.append(aid)
        if not got:
            return jsonify({'ok': False, 'error': 'ни один ассет не получен: ' + ', '.join(missing)}), 502
        zname = 'assets_%d.zip' % len(got)
        zbytes = buf.getvalue()
        res = {'ok': True, 'name': zname, 'size': len(zbytes), 'got': got, 'missing': missing}
        if body.get('inline'):
            res['b64'] = _b64.b64encode(zbytes).decode('ascii')
        else:
            zout = (data_dir / ('export_' + zname)).resolve()
            if data_dir not in zout.parents:
                return jsonify({'ok': False, 'error': 'bad path'}), 400
            zout.write_bytes(zbytes)
            res['path'] = str(zout)
        return jsonify(res)
    mm = _re.search(r'\d+', str(ids[0] if ids else body.get('id', '')))
    if not mm:
        return jsonify({'ok': False, 'error': 'bad asset id'}), 400
    asset_id = mm.group()
    with flask_app.test_request_context('/api/asset-proxy?id=' + asset_id):
        resp = api_asset_proxy()
        status = getattr(resp, 'status_code', 200)
        raw = resp.get_data() if status == 200 else b''
        err_text = resp.get_data(as_text=True)[:300] if status != 200 else ''
    if status != 200 or not raw:
        return jsonify({'ok': False, 'error': 'HTTP %s %s' % (status, err_text)}), 502
    if raw.startswith(b'version '):
        ext = '.mesh'
    elif raw[:4] == b'\x89PNG':
        ext = '.png'
    elif raw[:4] == b'OggS':
        ext = '.ogg'
    elif raw[:2] == b'\xff\xd8':
        ext = '.jpg'
    else:
        ext = '.bin'
    name = 'asset_%s%s' % (asset_id, ext)
    out = (data_dir / ('export_' + name)).resolve()
    if data_dir not in out.parents:
        return jsonify({'ok': False, 'error': 'bad path'}), 400
    out.write_bytes(raw)
    return jsonify({'ok': True, 'path': str(out), 'name': name, 'size': len(raw)})


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


def _rgb01(c):
    """Color3 {'r','g','b'} (0..1) -> [r,g,b] или None."""
    if isinstance(c, dict) and all(k in c for k in ('r', 'g', 'b')):
        try:
            v = [float(c['r']), float(c['g']), float(c['b'])]
            if max(v) > 1.5:  # на случай 0..255
                v = [x / 255.0 for x in v]
            return [round(max(0.0, min(1.0, x)), 4) for x in v]
        except (TypeError, ValueError):
            return None
    return None


def _clock_hours(lp):
    """ClockTime (часы, float) или TimeOfDay 'HH:MM:SS' -> часы 0..24."""
    ct = lp.get('ClockTime')
    try:
        if ct is not None:
            return float(ct) % 24.0
    except (TypeError, ValueError):
        pass
    tod = lp.get('TimeOfDay')
    if isinstance(tod, str):
        try:
            parts = [float(x) for x in tod.split(':')]
            parts += [0.0] * (3 - len(parts))
            return (parts[0] + parts[1] / 60.0 + parts[2] / 3600.0) % 24.0
        except ValueError:
            pass
    return 14.0


MAX_MAP_LIGHTS = 400


@flask_app.route('/api/lighting')
def api_lighting():
    """Настройки Lighting/Atmosphere карты и список PointLight/SpotLight с
    позициями — клиент строит по ним свет и дешёвое свечение (одним Points)."""
    parsed = state.get('parsed')
    if not parsed:
        return jsonify({'ok': True, 'found': False})
    r2c, props, pmap = parsed['referent_to_class'], parsed['props'], parsed['parent_map']
    lref = next((r for r, c in r2c.items() if c == 'Lighting'), None)
    if lref is None:
        return jsonify({'ok': True, 'found': False})
    lp = props.get(lref, {})

    def num(v, d):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d

    lighting = {
        'clockTime': _clock_hours(lp),
        'brightness': num(lp.get('Brightness'), 2.0),
        'ambient': _rgb01(lp.get('Ambient')),
        'outdoorAmbient': _rgb01(lp.get('OutdoorAmbient')),
        'fogColor': _rgb01(lp.get('FogColor')),
        'fogStart': num(lp.get('FogStart'), 0.0),
        'fogEnd': num(lp.get('FogEnd'), 100000.0),
        'latitude': num(lp.get('GeographicLatitude'), 41.7),
        'exposure': num(lp.get('ExposureCompensation'), 0.0),
        'globalShadows': bool(lp.get('GlobalShadows', False)),
    }
    atmosphere = None
    for r, c in r2c.items():
        if c == 'Atmosphere' and pmap.get(r) == lref:
            ap = props.get(r, {})
            atmosphere = {'color': _rgb01(ap.get('Color')), 'density': num(ap.get('Density'), 0.0),
                          'haze': num(ap.get('Haze'), 0.0), 'offset': num(ap.get('Offset'), 0.0)}
            break

    lights = []
    for r, c in r2c.items():
        if c not in ('PointLight', 'SpotLight', 'SurfaceLight'):
            continue
        lpr = props.get(r, {})
        if lpr.get('Enabled') is False:
            continue
        # позиция — у ближайшего предка с CFrame (Part, либо Attachment внутри Part)
        anc, pos = pmap.get(r), None
        for _ in range(4):
            if anc is None or anc not in props:
                break
            cf = props[anc].get('CFrame')
            if isinstance(cf, dict):
                pos = get_pos(cf)
                break
            anc = pmap.get(anc)
        if pos is None:
            continue
        b = num(lpr.get('Brightness'), 1.0)
        if b <= 0:
            continue
        lights.append({'x': pos[0], 'y': pos[1], 'z': pos[2], 'b': b,
                       'range': num(lpr.get('Range'), 8.0),
                       'color': _rgb01(lpr.get('Color')) or [1.0, 1.0, 1.0]})
        if len(lights) >= MAX_MAP_LIGHTS:
            break
    # Скайбокс (шесть граней) и цветокоррекция — только то, что можно применить без пост-обработки
    sky = None
    cc = None
    for r, c in r2c.items():
        if c == 'Sky' and pmap.get(r) == lref and sky is None:
            sp = props.get(r, {})
            faces = {k: _rbxassetid_num(sp.get('Skybox' + k)) for k in ('Bk', 'Dn', 'Ft', 'Lf', 'Rt', 'Up')}
            if all(faces.values()):
                sky = faces
        elif c == 'ColorCorrectionEffect' and pmap.get(r) == lref and cc is None:
            cp = props.get(r, {})
            if cp.get('Enabled', True):
                cc = {'brightness': num(cp.get('Brightness'), 0.0), 'contrast': num(cp.get('Contrast'), 0.0),
                      'saturation': num(cp.get('Saturation'), 0.0),
                      'tint': _rgb01(cp.get('TintColor')) or [1.0, 1.0, 1.0]}
    return jsonify({'ok': True, 'found': True, 'lighting': lighting, 'atmosphere': atmosphere,
                    'lights': lights, 'sky': sky, 'colorCorrection': cc})


_children_cache = {'pid': None, 'map': None}


def _children_of(parsed):
    """parent_map перевёрнутый в ref -> [дети]; кэшируется на распарсенную карту."""
    pid = id(parsed)
    if _children_cache['pid'] != pid:
        m = {}
        for ch, pa in parsed['parent_map'].items():
            m.setdefault(pa, []).append(ch)
        _children_cache.update(pid=pid, map=m)
    return _children_cache['map']


def _cf12(cf):
    """CFrame -> [x, y, z, r00..r22] (матрица поворота по строкам)."""
    return [float(v) for v in get_pos(cf)] + [float(v) for v in get_rot_matrix(cf)]


@flask_app.route('/api/outfit_item/<int:ref>')
def api_outfit_item(ref):
    """Данные Accessory / BodyColors ИЗ ФАЙЛА для отрисовки на персонаже: скрипт карты
    клонирует их в Character (морф костюма), а клиент по ref оригинала рисует."""
    parsed = state.get('parsed')
    if not parsed:
        return jsonify({'ok': False, 'error': 'карта не открыта'})
    r2c, props = parsed['referent_to_class'], parsed['props']
    cls = r2c.get(ref)
    p = props.get(ref, {})
    kids = _children_of(parsed)
    if cls == 'BodyColors':
        keys = {'Head': 'HeadColor3', 'Torso': 'TorsoColor3', 'LeftArm': 'LeftArmColor3',
                'RightArm': 'RightArmColor3', 'LeftLeg': 'LeftLegColor3', 'RightLeg': 'RightLegColor3'}
        cols = {}
        for limb, pk in keys.items():
            c = _rgb01(p.get(pk))
            if c:
                cols[limb] = '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in c)
        return jsonify({'ok': True, 'cls': 'BodyColors', 'colors': cols})
    if cls != 'Accessory':
        return jsonify({'ok': False, 'error': 'не Accessory/BodyColors'})

    parts = [k for k in kids.get(ref, []) if r2c.get(k) in ('Part', 'MeshPart')]
    handle = next((k for k in parts if props.get(k, {}).get('Name') == 'Handle'), parts[0] if parts else None)
    if handle is None:
        return jsonify({'ok': False, 'error': 'у аксессуара нет Handle'})
    hp, hkids = props[handle], kids.get(handle, [])
    sz = hp.get('Size') if isinstance(hp.get('Size'), dict) else {}
    size = [safe_float(sz.get('x', 1), 1), safe_float(sz.get('y', 1), 1), safe_float(sz.get('z', 1), 1)]

    mesh = {'kind': 'box'}
    if r2c[handle] == 'MeshPart':
        mid = _rbxassetid_num(hp.get('MeshId'))
        if mid:
            mesh = {'kind': 'meshpart', 'meshId': mid,
                    'textureId': _rbxassetid_num(hp.get('TextureID') or hp.get('TextureId'))}
    else:
        for k in hkids:
            if r2c.get(k) == 'SpecialMesh':
                sp = props[k]
                mid = _rbxassetid_num(sp.get('MeshId'))
                if mid:
                    sc, of = sp.get('Scale') or {}, sp.get('Offset') or {}
                    mesh = {'kind': 'special', 'meshId': mid,
                            'textureId': _rbxassetid_num(sp.get('TextureId')),
                            'scale': [safe_float(sc.get('x', 1), 1), safe_float(sc.get('y', 1), 1), safe_float(sc.get('z', 1), 1)],
                            'offset': [safe_float(of.get('x', 0), 0), safe_float(of.get('y', 0), 0), safe_float(of.get('z', 0), 0)]}
                break

    weld = None
    for k in hkids:
        if r2c.get(k) in ('Weld', 'ManualWeld'):
            wp = props[k]
            p0 = wp.get('Part0')
            weld = {'part0': props.get(p0, {}).get('Name') if p0 in props else None,
                    'c0': _cf12(wp.get('C0')), 'c1': _cf12(wp.get('C1'))}
            break
    att = None
    for k in hkids:
        if r2c.get(k) == 'Attachment':
            ap = props[k]
            att = {'name': ap.get('Name'), 'cf': _cf12(ap.get('CFrame'))}
            break
    return jsonify({'ok': True, 'cls': 'Accessory', 'name': p.get('Name'), 'mesh': mesh, 'size': size,
                    'color': get_part_color(hp), 'weld': weld, 'attachment': att})


@flask_app.route('/api/roblox/me')
def api_roblox_me():
    """Ник/ID аккаунта, под которым выполнен вход (кука .ROBLOSECURITY).
    Нет куки или она протухла — loggedIn=False (клиент тогда рисует
    стандартного Roblox-«нуба» вместо аватара игрока)."""
    if _roblox_cookie() is None:
        return jsonify({'ok': True, 'loggedIn': False})
    try:
        d = _rbx_get_json('https://users.roblox.com/v1/users/authenticated')
        uid = d.get('id') if isinstance(d, dict) else None
        if not uid:
            raise RuntimeError('в ответе нет id')
        return jsonify({'ok': True, 'loggedIn': True, 'userId': uid,
                        'name': d.get('name') or '',
                        'displayName': d.get('displayName') or d.get('name') or ''})
    except Exception as e:
        # HTTP 401 и т.п. — кука недействительна: считаем, что входа нет
        return jsonify({'ok': True, 'loggedIn': False, 'error': str(e)})


PLAY_AVATAR_TTL = 24 * 3600  # сутки: аватар меняется редко, а генерация у Roblox небыстрая


def _play_avatar_cache_path(user_id):
    return _asset_cache_dir() / f'play_avatar_{user_id}.json'


@flask_app.route('/api/roblox/play-avatar')
def api_roblox_play_avatar():
    """3D-аватар для персонажа в Play (OBJ+MTL+текстуры одним JSON, без zip).
    1) userId без bundleUrl — отдаёт кэш с диска, если он свежий, иначе
       {ok, cached: false} (клиент тогда опрашивает /avatar3d/status и
       приходит сюда снова уже с bundleUrl);
    2) userId + bundleUrl — скачивает, кладёт в кэш и отдаёт."""
    import time as _time
    user_id = request.args.get('userId', '').strip()
    if not user_id.isdigit():
        return jsonify({'ok': False, 'error': 'userId должен быть числом'}), 400
    cp = _play_avatar_cache_path(user_id)
    try:
        cf = _cache_find(cp)
        if cf is not None and _time.time() - cf.stat().st_mtime < PLAY_AVATAR_TTL:
            cached_json = _cache_read_file(cf)
            if cached_json is not None:
                return Response(cached_json, mimetype='application/json')
    except OSError:
        pass
    bundle_url = request.args.get('bundleUrl', '').strip()
    if not bundle_url:
        return jsonify({'ok': True, 'cached': False})
    if not bundle_url.startswith('https://'):
        return jsonify({'ok': False, 'error': 'bundleUrl некорректен'}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': 'Сначала войдите в аккаунт Roblox.'}), 401
    try:
        import concurrent.futures as _cf
        bundle = _rbx_get_json(bundle_url)
        tex_hashes = bundle.get('textures', [])
        with _cf.ThreadPoolExecutor(max_workers=max(2, len(tex_hashes) + 2)) as pool:
            obj_f = pool.submit(_rbx_download_cdn, bundle['obj'])
            mtl_f = pool.submit(_rbx_download_cdn, bundle['mtl'])
            tex_f = [pool.submit(_rbx_download_cdn, h) for h in tex_hashes]
            obj_bytes, mtl_bytes = obj_f.result(), mtl_f.result()
            tex_files = [(_re.sub(r'[^a-zA-Z0-9._-]+', '_', h) + '.png', f.result())
                         for h, f in zip(tex_hashes, tex_f)]
        # как в /avatar3d/fetch: Roblox пишет в .mtl текстуры без расширения
        mtl_text = mtl_bytes.decode('utf-8', 'replace')
        for h in tex_hashes:
            mtl_text = _re.sub(r'(?<![\w.])' + _re.escape(h) + r'(?!\.\w)', h + '.png', mtl_text)
        payload = {
            'ok': True, 'cached': True,
            'obj_text': obj_bytes.decode('utf-8', 'replace'),
            'mtl_text': mtl_text,
            'textures': [{'name': n, 'data_url': 'data:image/png;base64,' +
                          _b64.b64encode(d).decode('ascii')} for n, d in tex_files],
        }
        try:
            for sfx in ('',) + _CACHE_CODEC_SUFFIXES:   # старую запись (в любом виде) заменяем новой
                try:
                    cp.with_name(cp.name + sfx).unlink()
                except OSError:
                    pass
            _cache_store(cp, json.dumps(payload).encode('utf-8'), 'application/json')
        except Exception:
            pass
        return jsonify(payload)
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


SERVER_BUILD = '2026-10-21 · no-swallow'   # должна совпадать с BUILD_LABEL в script.js и --css-build в style.css


@flask_app.route('/api/status')
def api_status():
    parsed = state['parsed']
    return jsonify({
        'ok': True,
        'build': SERVER_BUILD,
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


def _no_cache(resp):
    # index/style/script читаются с диска ОДИН раз при старте, а WebView/
    # браузер раньше мог держать старую копию script.js — после правки
    # старая версия продолжала работать. no-cache заставляет перепроверять.
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


def _asset_version():
    import hashlib
    h = hashlib.md5()
    for name in ('script.js', 'style.css'):
        try:
            with open(name, 'rb') as f:
                h.update(f.read())
        except OSError:
            pass
    return h.hexdigest()[:10]


@flask_app.route('/')
def index():
    # ?v=<хэш> в ссылках на script.js/style.css — WebView не может отдать
    # старую копию из кеша после замены файлов.
    v = _asset_version()
    html = HTML_TEMPLATE.replace('src="script.js"', 'src="script.js?v=%s"' % v) \
                        .replace('href="style.css"', 'href="style.css?v=%s"' % v)
    return _no_cache(Response(html, mimetype='text/html'))


@flask_app.route('/style.css')
def style_css():
    return _no_cache(Response(CSS_TEMPLATE, mimetype='text/css'))


@flask_app.route('/script.js')
def script_js():
    return _no_cache(Response(JS_TEMPLATE, mimetype='application/javascript'))


# ============ ИИ-АССИСТЕНТ ============
# Любой OpenAI-совместимый провайдер (OpenRouter, Groq, Mistral, Ollama,
# российские агрегаторы...): адрес, ключ и модель задаются в панели «🤖 AI».
# Ключ хранится только на сервере (в браузер не отдаётся), по умолчанию
# эндпоинты принимают запросы только с 127.0.0.1 — сервер слушает 0.0.0.0,
# и без этого любой в локальной сети мог бы тратить чужой ключ.
# RSW_ASSISTANT_ALLOW_REMOTE=1 снимает это ограничение.
try:
    with open("assistant.js", "r", encoding="utf-8") as file:
        ASSISTANT_JS = file.read()
except OSError:   # нет файла (старая сборка) — редактор работает без ассистента
    ASSISTANT_JS = "/* assistant.js не найден */"


def _assistant_cfg_path():
    p = os.environ.get('RSW_ASSISTANT_CONFIG')
    if p:
        return Path(p)
    try:
        return Path.home() / '.rsw_assistant.json'
    except Exception:
        return Path(__file__).parent / '.rsw_assistant.json'


def _assistant_load():
    cfg = {'base_url': 'https://openrouter.ai/api/v1', 'api_key': '', 'model': ''}
    try:
        with open(_assistant_cfg_path(), 'r', encoding='utf-8') as f:
            saved = json.load(f)
        for k in cfg:
            if isinstance(saved.get(k), str):
                cfg[k] = saved[k]
    except (OSError, ValueError):
        pass
    return cfg


def _assistant_save(cfg):
    path = _assistant_cfg_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _alang(ru, en):
    """Сообщение на языке интерфейса (заголовок X-Lang от assistant.js)."""
    return ru if (request.headers.get('X-Lang') or '').lower().startswith('ru') else en


def _assistant_guard():
    if os.environ.get('RSW_ASSISTANT_ALLOW_REMOTE') == '1':
        return None
    if request.remote_addr in ('127.0.0.1', '::1', '::ffff:127.0.0.1'):
        return None
    return jsonify({'ok': False, 'error': _alang('Ассистент доступен только с этого устройства', 'The assistant is only available from this device')}), 403


def _assistant_http(url, key, payload=None, timeout=120):
    headers = {'User-Agent': 'roblox-studio-web/1.0', 'Accept': 'application/json'}
    data = None
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode('utf-8')
    if key:
        headers['Authorization'] = 'Bearer ' + key
    return _req.urlopen(_req.Request(url, data=data, headers=headers), timeout=timeout)


def _assistant_error(e):
    if isinstance(e, _urlerr.HTTPError):
        try:
            body = e.read()[:500].decode('utf-8', 'replace')
        except Exception:
            body = ''
        return 'HTTP %d: %s' % (e.code, body)
    return str(e)


import re as _re_ai

_AI_ACT_BLOCK = _re_ai.compile(r"```[a-zA-Z0-9_+-]*[ \t]*\n\s*\[\s*\{\s*\"op\"[\s\S]*?```")
_AI_TEXT_ONLY = _re_ai.compile(
    r"только\s+текст|без\s+(действий|изменений|правок)|не\s+(создавай|меняй|удаляй|трогай)|"
    r"\b(почему|зачем|объясни|расскажи|как\s+работает|что\s+значит|why|explain|text\s+only|only\s+text)\b|\?\s*$", _re_ai.I)


def _ai_strip_done_actions(text):
    """Выполненные блоки действий из истории заменяем заглушкой: иначе бесплатные модели
    копируют их по шаблону и снова лезут в сцену на любой вопрос."""
    return _re_ai.sub(r'(?im)^\\s*(User|Response) Safety:\\s*\\w+\\s*$', '', _AI_ACT_BLOCK.sub('[блок действий уже выполнен]', text))


def _ai_text_only(text):
    return bool(_AI_TEXT_ONLY.search(text or ''))


_ASSISTANT_ACTIONS_RU = (
    "ТЫ МОЖЕШЬ САМ МЕНЯТЬ СЦЕНУ, в том числе создавать скрипты: редактор выполняет блок "
    "```rbx-actions с JSON-массивом действий (одним блоком в конце ответа). Не проси пользователя "
    "создавать объекты и скрипты вручную и не говори, что не можешь.\n"
    "Действия: {\"op\":\"create\",\"class\":C,\"name\":N,\"parent\":ref?,\"source\":\"код\"?,\"props\":{...}?}, "
    "{\"op\":\"set\",\"ref\":R,\"prop\":P,\"value\":V}, {\"op\":\"delete\",\"ref\":R}, {\"op\":\"move\",\"ref\":R,\"parent\":P} (перенос в другого родителя; P — ref или имя). "
    "Не удаляй и не пересоздавай объект ради переноса — используй move. parent можно задавать именем объекта, созданного выше в этом же блоке.\n"
    "class: Part, WedgePart, SpherePart, CornerWedgePart, SpawnLocation, Folder, Model, Script, LocalScript, ModuleScript. "
    "Свойства (props/set): Position, Rotation, Size ([x,y,z]), Color (\"#RRGGBB\"), Transparency, Reflectance (0..1), "
    "Anchored, CanCollide, CastShadow (bool), Name, Source (текст скрипта, только для скриптов).\n"
    "Скрипт: {\"op\":\"create\",\"class\":\"Script\",\"name\":\"Spin\",\"source\":\"-- Luau код\"}. "
   "Без parent Script/ModuleScript попадает в ServerScriptService, LocalScript в StarterPlayerScripts, \n"
"ПРАВИЛА РАЗМЕЩЕНИЯ СКРИПТОВ (обязательно):\n"
"1. Если скрипт управляет конкретным объектом из Workspace — вращает Part, двигает дверь, "
"обрабатывает клик по модели, — создавай Script как РЕБЁНКА этого объекта: "
"parent = ref самого объекта. В Luau используй local target = script.Parent.\n"
"2. Не создавай исполняемые Script или LocalScript в ServerStorage или ReplicatedStorage, "
"если пользователь явно не попросил именно туда (или там точно будет лучше). "
"Script в ServerStorage не выполняется; LocalScript в ReplicatedStorage тоже не выполняется.\n"
"3. Обычный серверный Script без явного parent создавай в ServerScriptService. "
"В его коде ищи целевой объект через Workspace:WaitForChild(\"ИмяОбъекта\") или другой путь.\n"
"4. LocalScript без явного parent создавай в StarterPlayer > StarterPlayerScripts. "
"Никогда не клади LocalScript в ServerScriptService или ServerStorage.\n"
"5. ModuleScript для кода, нужного и серверу, и клиенту, создавай в ReplicatedStorage. "
"ModuleScript только для сервера можно создать в ServerScriptService или ServerStorage.\n"
"6. Никогда не используй parent = -1 и не выдумывай ref. Если подходящий объект не найден "
"в контексте редактора, не указывай parent вовсе и объясни в ответе, куда скрипт будет помещён.\n"
"ПРИМЕР ПРАВИЛЬНОЙ ИЕРАРХИИ для вращающегося куба:\n"
"Workspace\n"
"└─ Part \"Cube\"   <- parent для Script = ref этого Part\n"
"   └─ Script \"Spin\"\n"
"Код Script:\n"
"local part = script.Parent\n"
"game:GetService(\"RunService\").Heartbeat:Connect(function(dt)\n"
"    part.CFrame *= CFrame.Angles(0, dt * 1, 0)\n"
"end)\n"
"НЕПРАВИЛЬНО: создавать Script \"Spin\" с parent = ref ServerStorage.\n"
"ПРАВИЛЬНО: создавать Script \"Spin\" с parent = ref Part \"Cube\" в Workspace.\n"
"остальное в Workspace. Чтобы поменять код существующего скрипта: op=set, prop=Source. "    
    "ref берись только из контекста редактора. В JSON переводы строк в source пиши как \\n и экранируй кавычки. "
    "Перед блоком коротко (1-2 фразы) скажи, что делаешь. Если пользователь просил вращающийся куб — "
    "создай Part и Script, который его вращает, оба в одном блоке."
)
_ASSISTANT_ACTIONS_EN = (
    "YOU CAN CHANGE THE SCENE YOURSELF, including creating scripts: the editor executes a "
    "```rbx-actions block with a JSON array of actions (one block at the end of the reply). Never ask the user "
    "to create objects or scripts by hand and never say you cannot.\n"
    "Actions: {\"op\":\"create\",\"class\":C,\"name\":N,\"parent\":ref?,\"source\":\"code\"?,\"props\":{...}?}, "
    "{\"op\":\"set\",\"ref\":R,\"prop\":P,\"value\":V}, {\"op\":\"delete\",\"ref\":R}, {\"op\":\"move\",\"ref\":R,\"parent\":P} (reparent; P is a ref or a name). "
    "Never delete and recreate an object just to move it — use move. parent may be the name of an object created earlier in the same block.\n"
    "class: Part, WedgePart, SpherePart, CornerWedgePart, SpawnLocation, Folder, Model, Script, LocalScript, ModuleScript. "
    "Properties (props/set): Position, Rotation, Size ([x,y,z]), Color (\"#RRGGBB\"), Transparency, Reflectance (0..1), "
    "Anchored, CanCollide, CastShadow (bool), Name, Source (script text, scripts only).\n"
    "Script: {\"op\":\"create\",\"class\":\"Script\",\"name\":\"Spin\",\"source\":\"-- Luau code\"}. "
    "Without parent, Script/ModuleScript goes to ServerScriptService, LocalScript to StarterPlayerScripts, "
    "SCRIPT PLACEMENT RULES (mandatory):"
    "1. If a script controls a specific Workspace object — spins a Part, moves a door, or handles "
    "a click on a model — create the Script as a CHILD of that object: parent = the object's ref. "
    "In Luau, use local target = script.Parent."
    "2. Do not create executable Script or LocalScript instances in ServerStorage or ReplicatedStorage "
    "unless the user explicitly requests that location. A Script in ServerStorage does not run; "
    "a LocalScript in ReplicatedStorage does not run either."
    "3. Create a normal server Script without an explicit parent in ServerScriptService. "
    "In its code, locate the target through Workspace:WaitForChild(\"ObjectName\") or another explicit path."
    "4. Create a LocalScript without an explicit parent in StarterPlayer > StarterPlayerScripts. "
    "Never place a LocalScript in ServerScriptService or ServerStorage."
    "5. Create a ModuleScript in ReplicatedStorage when both the server and client need its code. "
    "A server-only ModuleScript may be created in ServerScriptService or ServerStorage."
    "6. Never use parent = -1 and never invent a ref. If no suitable object exists in the editor context, "
    "omit parent and state in your reply where the script will be placed."
    "CORRECT HIERARCHY EXAMPLE for a spinning cube:"
    "Workspace"
    "└─ Part \"Cube\"   <- Script parent = this Part's ref"
    "   └─ Script \"Spin\""
    "Script code:"
    "local part = script.Parent"
    "game:GetService(\"RunService\").Heartbeat:Connect(function(dt)"
    "    part.CFrame *= CFrame.Angles(0, dt * 1, 0)"
    "end)"
    "WRONG: create Script \"Spin\" with parent = ServerStorage's ref."
    "RIGHT: create Script \"Spin\" with parent = the Workspace Part \"Cube\" ref."
    "everything else to Workspace. To change an existing script: op=set, prop=Source. "
    "Take refs only from the editor context. In JSON write newlines in source as \\n and escape quotes. "
    "Before the block say in 1-2 sentences what you do. For a spinning cube create a Part and a Script that "
    "spins it, both in one block."
)

_ASSISTANT_SYSTEM = {
    'ru': (
        "Ты ассистент, встроенный в веб-редактор Roblox Studio (клон на Flask). "
        "Помогаешь с Luau-скриптами, свойствами объектов и структурой игры. "
        "Отвечай на языке пользователя, кратко. "
        "Код оформляй в блоках и убедись, что он использует только реальный Roblox API."

        "ВАЖНО О ФОРМАТЕ ОТВЕТА:"
        "Ты — обычный ассистент редактора, а не модератор и не классификатор безопасности. "
        "Никогда не выводи служебные метки, оценки или служебные протоколы, включая:"
        "User Safety:, Response Safety:, Safety Categories:, safe, unsafe, "
        "policy violation, moderation result и подобные."
        "Не объясняй, безопасен ли запрос. Не добавляй служебные заголовки, внутренние рассуждения, "
        "статусы, префиксы или постфиксы, не относящиеся к ответу пользователю."
        "Отвечай сразу обычным текстом для пользователя: объяснением, кодом, списком действий "
        "или вопросом для уточнения."

        + _ASSISTANT_ACTIONS_RU
    ),
    'en': (
        "You are an assistant built into a web-based Roblox Studio editor (a Flask clone). "
        "You help with Luau scripts, object properties and game structure. "
        "Reply in the user's language, concisely. "
        "Put code in blocks and make sure it only uses the real Roblox API."

        "IMPORTANT OUTPUT FORMAT:"
        "You are a regular editor assistant, not a safety moderator or classifier. "
        "Never output service labels, ratings, or internal protocols, including:"
        "User Safety:, Response Safety:, Safety Categories:, safe, unsafe, "
        "policy violation, moderation result, or similar."
        "Do not explain whether a request is safe. Do not add service headings, internal reasoning, "
        "statuses, prefixes, or suffixes unrelated to the user-facing answer."
        "Start immediately with normal user-facing text: an explanation, code, action list, "
        "or clarifying question."

        + _ASSISTANT_ACTIONS_EN
    ),
}


@flask_app.route('/assistant.js')
def assistant_js():
    return _no_cache(Response(ASSISTANT_JS, mimetype='application/javascript'))


@flask_app.route('/api/assistant/config', methods=['GET', 'POST'])
def assistant_config():
    deny = _assistant_guard()
    if deny:
        return deny
    cfg = _assistant_load()
    if request.method == 'POST':
        d = request.get_json(silent=True) or {}
        if isinstance(d.get('base_url'), str) and d['base_url'].strip():
            cfg['base_url'] = d['base_url'].strip()
        if isinstance(d.get('model'), str):
            cfg['model'] = d['model'].strip()
        if d.get('clear_key'):
            cfg['api_key'] = ''
        elif isinstance(d.get('api_key'), str) and d['api_key'].strip():
            cfg['api_key'] = d['api_key'].strip()
        try:
            _assistant_save(cfg)
        except OSError as e:
            return jsonify({'ok': False, 'error': _alang('Не удалось сохранить настройки: %s', 'Could not save settings: %s') % e}), 500
    return jsonify({'ok': True, 'base_url': cfg['base_url'], 'model': cfg['model'],
                    'has_key': bool(cfg['api_key'])})


@flask_app.route('/api/assistant/models')
def assistant_models():
    deny = _assistant_guard()
    if deny:
        return deny
    cfg = _assistant_load()
    try:
        with _assistant_http(cfg['base_url'].rstrip('/') + '/models', cfg['api_key'], timeout=30) as resp:
            j = json.loads(resp.read().decode('utf-8', 'replace'))
    except Exception as e:
        return jsonify({'ok': False, 'error': _assistant_error(e)}), 502
    items = j.get('data') if isinstance(j, dict) else j
    ids = []
    for m in items or []:
        mid = m.get('id') if isinstance(m, dict) else None
        if isinstance(mid, str):
            ids.append(mid)
    return jsonify({'ok': True, 'models': ids[:500]})


@flask_app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    deny = _assistant_guard()
    if deny:
        return deny
    cfg = _assistant_load()
    if not cfg['model']:
        return jsonify({'ok': False, 'error': _alang('Не выбрана модель (⚙ в панели ассистента)', 'No model selected (⚙ in the assistant panel)')}), 400
        
    d = request.get_json(silent=True) or {}

    raw = d.get('messages') or []
    msgs = []
    for m in raw[-12:]:                      # 6 пар user/assistant вместо 20 сообщений
        if not (isinstance(m, dict) and m.get('role') in ('user', 'assistant')
                and isinstance(m.get('content'), str)):
            continue
        msgs.append({'role': m['role'], 'content': m['content']})
    if not msgs:
        return jsonify({'ok': False, 'error': _alang('Пустой запрос', 'Empty request')}), 400
    # старые assistant-сообщения режем до головы+хвоста (там был блок rbx-actions,
    # который уже выполнен — целиком он больше не нужен)
    for m in msgs:
        if m['role'] == 'assistant':
            m['content'] = _ai_strip_done_actions(m['content'])
    assist_idx = [i for i, m in enumerate(msgs) if m['role'] == 'assistant']
    keep_full = set(assist_idx[-2:])
    for i, m in enumerate(msgs):
        c = m['content']
        if m['role'] == 'user':
            m['content'] = c[:3000]
        elif i in keep_full:
            m['content'] = c[:4000]
        elif len(c) > 1000:
            m['content'] = c[:400] + '\n[…]\n' + c[-600:]
    system = _alang(_ASSISTANT_SYSTEM['ru'], _ASSISTANT_SYSTEM['en'])
    ctx = d.get('context')
    if isinstance(ctx, str) and ctx.strip():
        system += _alang('\n\nКонтекст редактора:\n', '\n\nEditor context:\n') + ctx[:5000]
    
    if msgs and msgs[-1]['role'] == 'user':
        if _ai_text_only(msgs[-1]['content']):
            msgs[-1]['content'] += _alang(
                "\n\n[Это вопрос или обсуждение: ответь ТОЛЬКО текстом, 2-5 предложений, "
                "БЕЗ блока rbx-actions и без JSON.]",
                "\n\n[This is a question or discussion: answer with TEXT ONLY, 2-5 sentences, "
                "NO rbx-actions block and no JSON.]")
        else:
            msgs[-1]['content'] += _alang(
                "\n\n[Если это просьба создать/изменить сцену: одной-двумя фразами скажи план (что и куда "
                "положишь), затем сразу выдай блок ```rbx-actions (ровно такая метка) с JSON-массивом. "
                "Script, который управляет объектом через script.Parent, клади ВНУТРЬ этого объекта (parent = его имя, объект создай выше в том же блоке); общий серверный Script без parent попадает в ServerScriptService. Для Part всегда указывай Size и Position. "
                "LocalScript — StarterPlayerScripts/StarterGui, ModuleScript — ReplicatedStorage. "
                "В props только Position, Rotation, Size, Color, Transparency, Reflectance, Anchored, "
                "CanCollide, CastShadow, Name. Если это вопрос или просьба «только текст» — "
                "отвечай текстом без блока.]",
                "\n\n[If this asks to create/change the scene: state the plan in 1-2 sentences (what goes "
                "where), then output the ```rbx-actions block (exactly that tag) with a JSON array. "
                "A Script that controls an object via script.Parent goes INSIDE that object (parent = its name, create the object earlier in the same block); a general server Script without parent goes to ServerScriptService. Always give a Part Size and Position. "
                "LocalScript — StarterPlayerScripts/StarterGui, ModuleScript — ReplicatedStorage. "
                "props only: Position, Rotation, Size, Color, Transparency, Reflectance, Anchored, "
                "CanCollide, CastShadow, Name. If it is a question or 'text only' — answer in text, no block.]")

    payload = {'model': cfg['model'], 'stream': True, 'temperature': 0.3,
           'messages': [{'role': 'system', 'content': system}] + msgs}
    try:
        resp = _assistant_http(cfg['base_url'].rstrip('/') + '/chat/completions', cfg['api_key'], payload)
    except Exception as e:
        return jsonify({'ok': False, 'error': _assistant_error(e)}), 502

    # сообщения готовим заранее: внутри генератора контекста запроса уже нет
    msg_prov = _alang('\n\n[Ошибка провайдера: %s]', '\n\n[Provider error: %s]')
    msg_stream = _alang('\n\n[Ошибка потока: %s]', '\n\n[Stream error: %s]')

    def gen():
        try:
            with resp:
                for raw in resp:
                    line = raw.decode('utf-8', 'replace').strip()
                    if not line.startswith('data:'):
                        continue
                    chunk = line[5:].strip()
                    if chunk == '[DONE]':
                        break
                    try:
                        j = json.loads(chunk)
                    except ValueError:
                        continue
                    if j.get('error'):
                        yield msg_prov % json.dumps(j['error'], ensure_ascii=False)[:300]
                        break
                    delta = ((j.get('choices') or [{}])[0].get('delta')) or {}
                    t = delta.get('content')
                    if t:
                        yield t
        except Exception as e:
            yield msg_stream % e

    return Response(gen(), mimetype='text/plain; charset=utf-8',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


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
