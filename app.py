#!/usr/bin/env python3
"""
RbxStudio - мобильный редактор Roblox-мест
Запуск: python3 app.py [путь/к/файлу.rbxl]
Зависимости устанавливаются автоматически.
"""
from flask import Flask, request, jsonify, Response, send_from_directory
import base64
import struct
import math
import traceback
import json
import time
from pathlib import Path
import sys
import subprocess
import os
from rbxl_parser import parse_rbxl, save_rbxl, publish_place


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

ICONS_DIR = Path(__file__).parent / 'icons'
PORT = 8080

CLASS_ICONS = {}
_icon_b64 = {}


def _load_icons():
    global CLASS_ICONS
    for p in [Path(__file__).parent / 'icons.json',
              Path(__file__).parent / 'icons.txt']:
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
    fn = CLASS_ICONS.get(cls, 'Instance.png')
    return _icon_b64.get(fn, '')


state = {
    'parsed':    None,
    'file_path': None,
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


def serialize_prop(v):
    if isinstance(v, bytes):
        return v.decode('utf-8', 'replace')
    try:
        json.dumps(v)
        return v
    except Exception:
        return str(v)


# Кеш для объектов сцены
_scene_cache = {'timestamp': 0, 'objects': [],
                'hash': '', 'pos': (0, 0, 0), 'r': 0}


def make_scene_objects(viewport_center=None, viewport_radius=None):
    """
    viewport_center: (x, y, z) - центр камеры
    viewport_radius: float - радиус видимости (дальность камеры)
    """
    parsed = state['parsed']
    if not parsed:
        return []

    # Проверяем кеш (если данные не менялись и камера не двигалась)
    current_hash = str(len(parsed['referent_to_class'])) + \
        str(parsed.get('_mod_counter', 0))

    if viewport_center and viewport_radius:
        cx, cy, cz = viewport_center
        cache_cx, cache_cy, cache_cz = _scene_cache['pos']
        cache_r = _scene_cache['r']

        # Если камера сдвинулась меньше чем на 10% радиуса - используем кеш
        if (time.time() - _scene_cache['timestamp'] < 3.0 and
            _scene_cache['hash'] == current_hash and
            abs(cx - cache_cx) < viewport_radius * 0.1 and
            abs(cy - cache_cy) < viewport_radius * 0.1 and
            abs(cz - cache_cz) < viewport_radius * 0.1 and
                abs(viewport_radius - cache_r) < viewport_radius * 0.1):
            return _scene_cache['objects']

    objs = []
    r2c = parsed['referent_to_class']
    props_all = parsed['props']

    # Предвычисленные значения для быстрой фильтрации
    cx = cy = cz = 0
    radius_sq = float('inf')

    if viewport_center:
        cx, cy, cz = viewport_center
        radius_sq = (viewport_radius or 100) ** 2

    # Счётчики для статистики
    total_parts = 0
    skipped_invisible = 0
    skipped_distance = 0
    skipped_small = 0

    for ref, cls in r2c.items():
        # Только Part-классы
        if cls not in PART_CLASSES:
            continue

        total_parts += 1
        props = props_all.get(ref, {})

        # Пропускаем невидимые
        if props.get('Visible') is False:
            skipped_invisible += 1
            continue

        # Пропускаем полностью прозрачные
        transparency = props.get('Transparency', 0)
        if isinstance(transparency, (int, float)) and transparency > 0.95:
            skipped_invisible += 1
            continue

        # Получаем Position
        pos = props.get('Position', {})
        if isinstance(pos, dict):
            px = safe_float(pos.get('x', 0))
            py = safe_float(pos.get('y', 0))
            pz = safe_float(pos.get('z', 0))
        else:
            px = py = pz = 0

        dist_sq = 0

        # Фильтрация по расстоянию до камеры
        if viewport_center:
            dx = px - cx
            dy = py - cy
            dz = pz - cz
            dist_sq = dx*dx + dy*dy + dz*dz
            if dist_sq > radius_sq:
                skipped_distance += 1
                continue

        # Получаем Size
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

        max_dim = max(sx, sy, sz_)

        # Пропускаем мелкие объекты далеко от камеры
        if viewport_center and dist_sq > 10000 and max_dim < 0.5:
            skipped_small += 1
            continue

        # Получаем Rotation
        rot = props.get('Rotation', {})
        if isinstance(rot, dict):
            rx = math.radians(safe_float(rot.get('x', 0)))
            ry = math.radians(safe_float(rot.get('y', 0)))
            rz = math.radians(safe_float(rot.get('z', 0)))
        # else:
            # rx = ry = rz = 0

        # Создаем матрицу поворота
        if rx == 0 and ry == 0 and rz == 0:
            rot_matrix = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        else:
            cx_v, sx_v = math.cos(rx), math.sin(rx)
            cy_v, sy_v = math.cos(ry), math.sin(ry)
            cz_v, sz_v = math.cos(rz), math.sin(rz)
            rot_matrix = [
                cy_v*cz_v, -cy_v*sz_v, sy_v,
                sx_v*sy_v*cz_v+cx_v*sz_v, -sx_v*sy_v*sz_v+cx_v*cz_v, -sx_v*cy_v,
                -cx_v*sy_v*cz_v+sx_v*sz_v, cx_v*sy_v*sz_v+sx_v*cz_v, cx_v*cy_v
            ]

        # Получаем цвет
        col = props.get('Color') or props.get(
            'Color3') or props.get('BrickColor')
        color = get_color(col) if isinstance(col, dict) else '#a0a0a0'

        # Определяем форму
        shape = 'sphere' if cls == 'SpherePart' else 'box'

        # Проверяем SpecialMesh только для обычных Part
        if cls == 'Part':
            # Оптимизированный поиск SpecialMesh (только ближайшие ref)
            max_ref = max(r2c.keys()) if r2c else 0
            for child_ref in range(ref + 1, min(ref + 5, max_ref + 1)):
                if child_ref in r2c and r2c[child_ref] == 'SpecialMesh':
                    cp = props_all.get(child_ref, {})
                    mt = cp.get('MeshType', 0)
                    if isinstance(mt, str):
                        mt = int(mt) if mt.isdigit() else 0
                    mid = str(cp.get('MeshId', ''))

                    CONE_IDS = ['9756362', '1033714', '9887819', 'cone.mesh']

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

        objs.append({
            'ref': ref,
            'class': cls,
            'name': name,
            'shape': shape,
            'px': px, 'py': py, 'pz': pz,
            'sx': sx, 'sy': sy, 'sz': sz_,
            'rot': rot_matrix,
            'color': color,
            'distance_sq': dist_sq,
            'size': max_dim,
        })

    # Сортируем: ближние и крупные объекты первыми
    if viewport_center:
        objs.sort(key=lambda o: (o['distance_sq'] / 10000) - o['size'])

        # Ограничиваем количество объектов для производительности
        MAX_OBJECTS = 1500
        if len(objs) > MAX_OBJECTS:
            # Приоритет: ближние + крупные
            near_objects = [o for o in objs if o['distance_sq'] < 2500]
            far_big_objects = [
                o for o in objs if o['distance_sq'] >= 2500 and o['size'] > 2.0]

            # Если всё ещё много - берём ближайшие
            if len(near_objects) > MAX_OBJECTS:
                near_objects = near_objects[:MAX_OBJECTS]
                far_big_objects = []
            elif len(near_objects) + len(far_big_objects) > MAX_OBJECTS:
                far_big_objects = far_big_objects[:MAX_OBJECTS -
                                                  len(near_objects)]

            objs = near_objects + far_big_objects

    # Обновляем кеш
    _scene_cache['timestamp'] = time.time()
    _scene_cache['objects'] = objs
    _scene_cache['hash'] = current_hash
    _scene_cache['pos'] = (cx, cy, cz) if viewport_center else (0, 0, 0)
    _scene_cache['r'] = viewport_radius or 0
    parsed['_mod_counter'] = parsed.get('_mod_counter', 0)

    # Логируем статистику
    if total_parts > 100:
        print(f'[Scene] Всего частей: {total_parts}, '
              f'Пропущено: {skipped_invisible} невид, '
              f'{skipped_distance} далеко, '
              f'{skipped_small} мелких, '
              f'Отправлено: {len(objs)}')

    return objs


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
        state['parsed']['_mod_counter'] = 0
        # Сбрасываем кеш
        _scene_cache['hash'] = ''
        return jsonify({'ok': True, 'count': len(parsed['referent_to_class'])})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


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

        if cls in HIDDEN:
            return None

        name = pr.get(ref, {}).get('Name', cls)

        kids = []
        for c in sorted(children_of.get(ref, [])):
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

    roots = []
    root_refs = set()
    for ref in r2c:
        parent = pm.get(ref, -1)
        if parent == -1 or parent not in r2c:
            root_refs.add(ref)

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
    # Получаем позицию камеры из запроса
    try:
        cam_x = float(request.args.get('cx', 0))
        cam_y = float(request.args.get('cy', 0))
        cam_z = float(request.args.get('cz', 0))
        cam_r = float(request.args.get('r', 100))
    except (ValueError, TypeError):
        cam_x = cam_y = cam_z = 0
        cam_r = 100

    if cam_x == 0 and cam_y == 0 and cam_z == 0:
        objects = make_scene_objects()
    else:
        objects = make_scene_objects((cam_x, cam_y, cam_z), cam_r)

    # Удаляем служебные поля перед отправкой
    clean_objects = []
    for obj in objects:
        clean_obj = {k: v for k, v in obj.items(
        ) if k not in ('distance_sq', 'size')}
        clean_objects.append(clean_obj)

    return jsonify({
        'ok': True,
        'objects': clean_objects,
        'total': len(clean_objects),
        'cached': bool(cam_x or cam_y or cam_z)
    })


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


@flask_app.route('/api/instance/<int:ref>', methods=['POST'])
def api_set_prop(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    data = request.json or {}
    prop = data.get('prop')
    val = data.get('value')
    if prop is not None and ref in parsed['referent_to_class']:
        parsed['props'].setdefault(ref, {})[prop] = val
        parsed['_modified'] = True
        parsed['_mod_counter'] = parsed.get('_mod_counter', 0) + 1
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
    parsed['props'][new_ref] = {'Name': name}
    parsed['_modified'] = True
    parsed['_mod_counter'] = parsed.get('_mod_counter', 0) + 1
    return jsonify({'ok': True, 'ref': new_ref})


@flask_app.route('/api/instance/<int:ref>', methods=['DELETE'])
def api_delete(ref):
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    for d in ('referent_to_class', 'parent_map', 'props'):
        parsed[d].pop(ref, None)
    parsed['_modified'] = True
    parsed['_mod_counter'] = parsed.get('_mod_counter', 0) + 1
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
            parsed['_modified'] = False
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
            parsed['_modified'] = False
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
HTML_PATH = Path(__file__).parent / "index.html"
if HTML_PATH.exists():
    with open(HTML_PATH, "r", encoding="utf-8") as file:
        HTML_TEMPLATE = file.read()
else:
    HTML_TEMPLATE = "<h1>index.html не найден</h1>"


@flask_app.route('/')
def index():
    return Response(HTML_TEMPLATE, mimetype='text/html')


if __name__ == '__main__':
    import threading
    import webbrowser

    if len(sys.argv) > 1:
        p = sys.argv[1]
        if Path(p).exists():
            try:
                from rbxl_parser import parse_rbxl
                parsed = parse_rbxl(p)
                state['parsed'] = parsed
                state['file_path'] = p
                parsed['_mod_counter'] = 0
                print(
                    f'[RbxStudio] Загружен: {p} ({len(parsed["referent_to_class"])} объектов)')
            except Exception as e:
                print(f'[RbxStudio] Ошибка загрузки: {e}')

    url = f'http://127.0.0.1:{PORT}'
    print(f'[RbxStudio] Запуск: {url}')

    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    flask_app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
