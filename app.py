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


def _ensure(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except ImportError:
        print(f'[RbxStudio] Устанавливаю {pkg}...')
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', pkg,
            '--break-system-packages', '-q'
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


def make_scene_objects(cx=None, cy=None, cz=None, r=None, limit=None):
    parsed = state['parsed']
    if not parsed:
        return [], 0
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

    if cx is not None and cy is not None and cz is not None:
        def d2(o):
            return (o['px'] - cx) ** 2 + (o['py'] - cy) ** 2 + (o['pz'] - cz) ** 2
        if r is not None:
            objs = [o for o in objs if d2(o) <= r * r]
        objs.sort(key=d2)

    total = len(objs)
    if limit is not None:
        objs = objs[:limit]
    return objs, total


flask_app = Flask(__name__)


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


@flask_app.route('/api/scene')
def api_scene():
    cx = request.args.get('cx', type=float)
    cy = request.args.get('cy', type=float)
    cz = request.args.get('cz', type=float)
    r = request.args.get('r', type=float)
    limit = request.args.get('limit', type=int)
    objs, total = make_scene_objects(cx, cy, cz, r, limit)
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
    return jsonify({'ok': True, 'ref': new_ref})


@flask_app.route('/api/instance/<int:ref>', methods=['DELETE'])
def api_delete(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    for d in ('referent_to_class', 'parent_map', 'props'):
        parsed[d].pop(ref, None)
    parsed['_modified'] = True
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
