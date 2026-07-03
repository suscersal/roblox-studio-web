import sys
import json
import traceback
import math
from pathlib import Path
from nicegui import ui, app

sys.path.insert(0, str(Path(__file__).parent))
from rbxl_parser import parse_rbxl, build_tree, publish_place, save_rbxl as save_rbxl_binary

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    
ICONS_DIR = Path(__file__).parent / 'icons'

_icon_cache = {}
_icon_base64_cache = {}
_icons_preloaded = False

def preload_icons():
    global _icons_preloaded, CLASS_ICONS
    if _icons_preloaded:
        return
    logger.info('🔄 Предзагрузка иконок...')
    CLASS_ICONS = {}
    json_path = Path(__file__).parent / 'icons.json'
    txt_path  = Path(__file__).parent / 'icons.txt'
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                CLASS_ICONS = json.load(f)
            logger.info(f'✅ icons.json: {len(CLASS_ICONS)} иконок')
        except Exception as e:
            logger.error(f'❌ icons.json: {e}')
    elif txt_path.exists():
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            safe_vars = {}
            exec(content, {'__builtins__': {}}, safe_vars)
            CLASS_ICONS = safe_vars.get('CLASS_ICONS', {})
            logger.info(f'✅ icons.txt: {len(CLASS_ICONS)} иконок')
        except Exception as e:
            logger.error(f'❌ icons.txt: {e}')
    if ICONS_DIR.exists():
        import base64
        count = 0
        for f in ICONS_DIR.iterdir():
            if f.is_file() and f.suffix.lower() == '.png':
                try:
                    _icon_cache[f.name] = f'/icons/{f.name}'
                    with open(f, 'rb') as fh:
                        data = base64.b64encode(fh.read()).decode('utf-8')
                        _icon_base64_cache[f.name] = f'data:image/png;base64,{data}'
                    count += 1
                except Exception as e:
                    logger.error(f'Ошибка кэша {f.name}: {e}')
        logger.info(f'✅ Закэшировано {count} иконок')
    _icons_preloaded = True

preload_icons()

HIDDEN_CLASSES = {
    'Debris', 'CookiesService', 'InsertService', 'GamePassService',
    'VRService', 'Selection', 'ContextActionService', 'Instance',
    'LuaWebService', 'FilteredSelection', 'LocalizationService',
    'Teleport Service', 'PhysicsService', 'TouchInputService',
    'AvatarSettings', 'GuidRegistryService', 'ProcessInstancePhysicsService',
    'HttpService', 'UGCAvatarService', 'VirtualInputManager', 'VideoService',
    'CollectionService', 'VideoCaptureService', 'NonReplicatedCSGDictionaryService',
    'CSGDictionaryService', 'TweenService', 'PermissionsService',
}

FALLBACK_ICON = 'Instance.png'

def class_icon_src(cls):
    filename = CLASS_ICONS.get(cls, FALLBACK_ICON)
    if filename in _icon_base64_cache:
        return _icon_base64_cache[filename]
    if filename in _icon_cache:
        return _icon_cache[filename]
    return None

# ── CFrame конвертеры ────────────────────────────────────────────────────────

def extract_position_from_cframe(cf_value):
    """Извлечь позицию из любого формата CFrame"""
    if cf_value is None:
        return {'x': 0, 'y': 0, 'z': 0}
    
    # Если есть position
    if isinstance(cf_value, dict) and 'position' in cf_value:
        pos = cf_value['position']
        if isinstance(pos, dict) and 'x' in pos:
            return pos
    
    # Если есть matrix (column-major: позиция в индексах 3, 7, 11)
    if isinstance(cf_value, dict) and 'matrix' in cf_value:
        matrix = cf_value['matrix']
        if isinstance(matrix, (list, tuple)):
            if len(matrix) >= 12:
                return {
                    'x': float(matrix[3]),
                    'y': float(matrix[7]),
                    'z': float(matrix[11])
                }
            elif len(matrix) >= 9:
                # Только матрица 3x3, без позиции
                return {'x': 0, 'y': 0, 'z': 0}
    
    return {'x': 0, 'y': 0, 'z': 0}

def extract_rotation_from_cframe(cf_value):
    """Извлечь вращение из CFrame (в градусах)"""
    if cf_value is None:
        return {'x': 0, 'y': 0, 'z': 0}
    
    if isinstance(cf_value, dict):
        # Специальные углы
        if 'angles_deg' in cf_value:
            angles = cf_value['angles_deg']
            if isinstance(angles, (list, tuple)) and len(angles) >= 3:
                return {'x': float(angles[0]), 'y': float(angles[1]), 'z': float(angles[2])}
        
        # Матрица
        if 'matrix' in cf_value:
            matrix = cf_value['matrix']
            if isinstance(matrix, (list, tuple)) and len(matrix) >= 9:
                return matrix_to_euler_deg(matrix)
    
    return {'x': 0, 'y': 0, 'z': 0}

def matrix_to_euler_deg(matrix):
    """Конвертировать матрицу 3x3 в углы Эйлера (градусы)"""
    if len(matrix) < 9:
        return {'x': 0, 'y': 0, 'z': 0}
    
    # Извлекаем элементы (column-major)
    r00, r10, r20 = float(matrix[0]), float(matrix[1]), float(matrix[2])
    r01, r11, r21 = float(matrix[3]), float(matrix[4]), float(matrix[5])
    r02, r12, r22 = float(matrix[6]), float(matrix[7]), float(matrix[8])
    
    # Вычисляем углы Эйлера в радианах
    if abs(r02) < 0.99999:
        y_rad = math.asin(-r02)
        x_rad = math.atan2(r12, r22)
        z_rad = math.atan2(r01, r00)
    else:
        # Gimbal lock
        sign = -1 if r02 < 0 else 1
        y_rad = sign * math.pi / 2
        x_rad = math.atan2(-r10, r11)
        z_rad = 0
    
    return {
        'x': round(math.degrees(x_rad), 2),
        'y': round(math.degrees(y_rad), 2),
        'z': round(math.degrees(z_rad), 2)
    }

def euler_to_matrix(x_deg, y_deg, z_deg):
    """Конвертировать углы Эйлера в матрицу 3x3 (column-major)"""
    x_rad = math.radians(x_deg)
    y_rad = math.radians(y_deg)
    z_rad = math.radians(z_deg)
    
    cx, sx = math.cos(x_rad), math.sin(x_rad)
    cy, sy = math.cos(y_rad), math.sin(y_rad)
    cz, sz = math.cos(z_rad), math.sin(z_rad)
    
    # Row-major матрица
    r00 = cy * cz
    r01 = cz * sx * sy - cx * sz
    r02 = cx * cz * sy + sx * sz
    
    r10 = cy * sz
    r11 = cx * cz + sx * sy * sz
    r12 = -cz * sx + cx * sy * sz
    
    r20 = -sy
    r21 = cy * sx
    r22 = cx * cy
    
    # Column-major порядок
    return [r00, r10, r20, r01, r11, r21, r02, r12, r22]

# ── Состояние ─────────────────────────────────────────────────────────────────

state = {
    'parsed':       None,
    'selected_ref': None,
    'scene_objects': {},
    'file_path':    None,
    '_ui':          {},
    'expanded':     set(),
    'search_text':  '',
    'clipboard':    None,
    'modified':     False,
}

SCRIPT_CLASSES = ('Script', 'LocalScript', 'ModuleScript')
PART_CLASSES = (
    'Part', 'WedgePart', 'CornerWedgePart',
    'TrussPart', 'SpawnLocation', 'Seat', 'VehicleSeat', 'SpherePart',
)

def get_prop(ref, name, default=None):
    if state['parsed'] is None:
        return default
    return state['parsed']['props'].get(ref, {}).get(name, default)

def vec3(v, default=0):
    if isinstance(v, dict):
        return v.get('x', default), v.get('y', default), v.get('z', default)
    return default, default, default

def color3_to_hex(c):
    if not c:
        return '#a0a0a0'
    try:
        if isinstance(c, dict):
            r = int(float(c.get('r', 0.6)) * 255)
            g = int(float(c.get('g', 0.6)) * 255)
            b = int(float(c.get('b', 0.6)) * 255)
            return f'#{r:02x}{g:02x}{b:02x}'
        elif isinstance(c, (list, tuple)) and len(c) >= 3:
            r = int(float(c[0]) * 255)
            g = int(float(c[1]) * 255)
            b = int(float(c[2]) * 255)
            return f'#{r:02x}{g:02x}{b:02x}'
    except Exception:
        pass
    return '#a0a0a0'

def update_prop(ref, prop_name, value):
    if state['parsed'] is None:
        return
    if ref not in state['parsed']['referent_to_class']:
        return
    state['parsed']['props'].setdefault(ref, {})[prop_name] = value
    state['modified'] = True

def find_workspace_ref():
    if state['parsed'] is None:
        return -1
    for ref, cls in state['parsed']['referent_to_class'].items():
        if cls == 'Workspace':
            return ref
    return -1

def is_hidden_class(cls_name):
    return str(cls_name).strip().lower() in {str(c).strip().lower() for c in HIDDEN_CLASSES}

def filter_by_search(ref, ref_to_class, props):
    search = state.get('search_text', '').strip().lower()
    if not search:
        return True
    cls  = ref_to_class.get(ref, '?')
    name = props.get(ref, {}).get('Name', cls)
    return search in name.lower() or search in str(cls).lower()

# ── 3D сцена ──────────────────────────────────────────────────────────────────

def populate_scene():
    scene3d = state['_ui'].get('scene3d')
    if scene3d is None:
        return
    scene3d.clear()
    state['scene_objects'] = {}
    if state['parsed'] is None:
        return
    
    count = 0
    for ref, cls in state['parsed']['referent_to_class'].items():
        if cls not in PART_CLASSES:
            continue
        if not get_prop(ref, 'Visible', True):
            continue
        
        cf  = get_prop(ref, 'CFrame')
        sz  = get_prop(ref, 'Size')
        col = get_prop(ref, 'Color')
        
        # Извлекаем позицию из CFrame (поддерживает matrix и position)
        if cf:
            pos = extract_position_from_cframe(cf)
            rot = extract_rotation_from_cframe(cf)
            px, py, pz = pos['x'], pos['y'], pos['z']
        else:
            px, py, pz = 0, 0, 0
            rot = {'x': 0, 'y': 0, 'z': 0}
        
        if sz:
            sx, sy, sz_val = sz.get('x', 1), sz.get('y', 1), sz.get('z', 1)
        else:
            sx, sy, sz_val = 1, 1, 1
        
        with scene3d:
            if cls == 'SpherePart':
                obj = scene3d.sphere(max(sx, sy, sz_val) * 0.5)
            elif cls in ('WedgePart', 'CornerWedgePart'):
                obj = scene3d.box(sx, sy, sz_val)
            else:
                obj = scene3d.box(sx, sy, sz_val)
            
            obj.move(px, py, pz)
            
            # Применяем вращение если есть
            if any(v != 0 for v in rot.values()):
                try:
                    obj.rotate(rot['x'], rot['y'], rot['z'])
                except Exception:
                    pass
            
            obj.material(color3_to_hex(col))
            obj.with_name(str(ref))
        
        state['scene_objects'][ref] = obj
        count += 1
    
    logger.info(f'✅ Сцена: {count} объектов')

def highlight_selected(selected_ref):
    for ref, obj in state['scene_objects'].items():
        obj.material('#ff6600' if ref == selected_ref
                     else color3_to_hex(get_prop(ref, 'Color')))

# ── Explorer ──────────────────────────────────────────────────────────────────

def toggle_expand(ref):
    if ref in state['expanded']:
        state['expanded'].discard(ref)
    else:
        state['expanded'].add(ref)
    rebuild_explorer()

def rebuild_explorer():
    container = state['_ui'].get('tree_container')
    if not container:
        return
    if state['parsed'] is None:
        return

    ref_to_class = state['parsed']['referent_to_class']
    parent_map   = state['parsed']['parent_map']
    props        = state['parsed']['props']

    children_of = {}
    for child, parent in parent_map.items():
        children_of.setdefault(parent, []).append(child)

    container.clear()

    with container:
        def on_search_change(e):
            val = e.args if isinstance(e.args, str) else (str(e.args) if e.args else '')
            state['search_text'] = val
            if val.strip():
                state['expanded'].update(ref_to_class.keys())
            rebuild_explorer()

        search_input = ui.input(
            placeholder='🔍 Поиск...',
            value=state.get('search_text', ''),
        ).props('dense outlined').classes('w-full text-sm bg-gray-700 text-white')
        search_input.on('update:model-value', on_search_change)

        with search_input.add_slot('append'):
            def clear_search():
                state['search_text'] = ''
                state['expanded'] = set(children_of.get(-1, []))
                rebuild_explorer()
            ui.button(icon='close', on_click=clear_search).props('flat dense')

        search_text  = state.get('search_text', '').strip()
        total_count  = sum(1 for cls in ref_to_class.values() if not is_hidden_class(cls))
        visible_count = sum(
            1 for ref, cls in ref_to_class.items()
            if not is_hidden_class(cls) and filter_by_search(ref, ref_to_class, props)
        )
        if search_text:
            ui.label(f'🔍 {visible_count} из {total_count}').classes(
                'text-xs text-yellow-400 px-2 py-1 bg-gray-900 w-full'
            )
        else:
            ui.label(f'📁 {total_count} объектов').classes(
                'text-xs text-gray-400 px-2 py-1 bg-gray-900 w-full'
            )
        ui.separator()

        root_nodes = [
            ref for ref in children_of.get(-1, [])
            if not is_hidden_class(ref_to_class.get(ref, '?'))
        ]

        def render_node(ref, depth=0, visited=None):
            if visited is None:
                visited = set()
            if ref in visited or depth > 50:
                return
            visited.add(ref)

            cls = ref_to_class.get(ref, '?')
            if is_hidden_class(cls):
                return
            if not filter_by_search(ref, ref_to_class, props):
                return

            name     = props.get(ref, {}).get('Name', cls)
            children = [c for c in children_of.get(ref, [])
                        if not is_hidden_class(ref_to_class.get(c, '?'))]
            selected = ref == state['selected_ref']
            expanded = ref in state['expanded']
            icon_src = class_icon_src(cls)
            search   = state.get('search_text', '').strip()

            with container:
                with ui.row().style(
                    f'padding-left:{depth * 14}px; min-height:22px; '
                    f'{"background-color:#1e3a5f;" if selected else ""}'
                ).classes('items-center gap-0 w-full cursor-pointer hover:bg-gray-700'):

                    if children:
                        arrow = ui.label('▼' if expanded else '▶').classes(
                            'text-gray-400 text-xs w-4 shrink-0 cursor-pointer'
                        )
                        arrow.on('click.stop', lambda _, r=ref: toggle_expand(r))
                    else:
                        ui.label('').classes('w-4 shrink-0')

                    if icon_src:
                        with ui.element('div').style(
                            'width:16px;height:16px;background:white;display:flex;'
                            'align-items:center;justify-content:center;border-radius:2px;margin:2px;'
                        ):
                            ui.image(icon_src).style('width:14px;height:14px;object-fit:contain;')
                    else:
                        ui.label('▪').classes('text-gray-400 text-xs w-4 shrink-0 text-center')

                    if search and search.lower() in name.lower():
                        idx = name.lower().index(search.lower())
                        with ui.row().classes('gap-0 flex-1 px-1 cursor-pointer') as hl_row:
                            if idx > 0:
                                ui.label(name[:idx]).classes('text-xs text-white')
                            ui.label(name[idx:idx+len(search)]).classes(
                                'text-xs text-yellow-300 font-bold'
                            )
                            if idx + len(search) < len(name):
                                ui.label(name[idx+len(search):]).classes('text-xs text-white')
                        hl_row.on('click', lambda _, r=ref: select_instance(r))
                    else:
                        lbl = ui.label(name).classes('text-xs text-white truncate flex-1 px-1')
                        lbl.on('click', lambda _, r=ref: select_instance(r))

            if expanded:
                for child_ref in sorted(children):
                    render_node(child_ref, depth + 1, visited.copy())

        for ref in sorted(root_nodes):
            render_node(ref)

# ── выбор / снятие выбора ─────────────────────────────────────────────────────

def deselect():
    state['selected_ref'] = None
    highlight_selected(None)
    rebuild_explorer()
    u = state['_ui']
    if 'props_container' not in u:
        return
    u['props_container'].clear()
    with u['props_container']:
        ui.label('← Выбери объект').classes('text-gray-500 text-sm')

def select_by_scene_name(name):
    try:
        select_instance(int(name))
    except (TypeError, ValueError):
        pass

def copy_object():
    ref = state['selected_ref']
    if ref is None or state['parsed'] is None:
        ui.notify('Объект не выбран', color='warning'); return
    props = state['parsed']['props'].get(ref, {})
    cls   = state['parsed']['referent_to_class'].get(ref, '?')
    state['clipboard'] = {'class': cls, 'props': props.copy(), 'name': props.get('Name', cls)}
    ui.notify(f'📋 Скопирован: {props.get("Name", cls)}', color='info')

def duplicate_object():
    ref = state['selected_ref']
    if ref is None or state['parsed'] is None:
        ui.notify('Объект не выбран', color='warning'); return
    cls    = state['parsed']['referent_to_class'].get(ref, '?')
    props  = state['parsed']['props'].get(ref, {})
    parent = state['parsed']['parent_map'].get(ref, -1)
    new_ref = max(state['parsed']['referent_to_class'].keys(), default=0) + 1
    state['parsed']['referent_to_class'][new_ref] = cls
    state['parsed']['parent_map'][new_ref]         = parent
    state['parsed']['props'][new_ref]              = props.copy()
    state['parsed']['props'][new_ref]['Name']      = f'{props.get("Name", cls)} (Copy)'
    state['modified'] = True
    rebuild_explorer(); populate_scene(); select_instance(new_ref)
    ui.notify(f'📌 Дублирован: {props.get("Name", cls)}', color='info')

def paste_object():
    if state['parsed'] is None:
        ui.notify('Файл не загружен', color='warning'); return
    if state['clipboard'] is None:
        ui.notify('Буфер обмена пуст', color='warning'); return
    parent  = state['selected_ref'] if state['selected_ref'] is not None else find_workspace_ref()
    new_ref = max(state['parsed']['referent_to_class'].keys(), default=0) + 1
    state['parsed']['referent_to_class'][new_ref] = state['clipboard']['class']
    state['parsed']['parent_map'][new_ref]         = parent if parent != -1 else -1
    state['parsed']['props'][new_ref]              = state['clipboard']['props'].copy()
    state['parsed']['props'][new_ref]['Name']      = f'{state["clipboard"]["name"]} (Pasted)'
    state['modified'] = True
    rebuild_explorer(); populate_scene(); select_instance(new_ref)
    ui.notify(f'📋 Вставлен: {state["clipboard"]["name"]}', color='info')

def render_cframe_editor(ref, cframe_raw, container):
    """Специальный редактор CFrame с позицией и вращением"""
    pos = extract_position_from_cframe(cframe_raw)
    rot = extract_rotation_from_cframe(cframe_raw)
    
    with container:
        with ui.expansion('📍 Позиция', value=True).classes('w-full mt-1'):
            with ui.row().classes('w-full gap-1'):
                def update_pos():
                    try:
                        new_pos = {
                            'x': float(pos_x.value),
                            'y': float(pos_y.value),
                            'z': float(pos_z.value)
                        }
                        if cframe_raw and isinstance(cframe_raw, dict):
                            if 'matrix' in cframe_raw and len(cframe_raw['matrix']) >= 12:
                                # Обновляем позицию в матрице (индексы 3,7,11)
                                new_matrix = list(cframe_raw['matrix'])
                                new_matrix[3] = new_pos['x']
                                new_matrix[7] = new_pos['y']
                                new_matrix[11] = new_pos['z']
                                update_prop(ref, 'CFrame', {'matrix': new_matrix})
                            elif 'position' in cframe_raw:
                                new_cf = dict(cframe_raw)
                                new_cf['position'] = new_pos
                                update_prop(ref, 'CFrame', new_cf)
                        populate_scene()
                    except (ValueError, TypeError):
                        pass
                
                pos_x = ui.number('X', value=pos['x'], on_change=update_pos, format='%.3f'
                                 ).classes('flex-1').props('dense')
                pos_y = ui.number('Y', value=pos['y'], on_change=update_pos, format='%.3f'
                                 ).classes('flex-1').props('dense')
                pos_z = ui.number('Z', value=pos['z'], on_change=update_pos, format='%.3f'
                                 ).classes('flex-1').props('dense')
        
        with ui.expansion('🔄 Вращение', value=False).classes('w-full'):
            with ui.row().classes('w-full gap-1'):
                def update_rot():
                    try:
                        new_rot = {
                            'x': float(rot_x.value),
                            'y': float(rot_y.value),
                            'z': float(rot_z.value)
                        }
                        if cframe_raw and isinstance(cframe_raw, dict):
                            if 'matrix' in cframe_raw:
                                # Конвертируем углы в матрицу
                                new_matrix = euler_to_matrix(new_rot['x'], new_rot['y'], new_rot['z'])
                                # Сохраняем позицию из старой матрицы
                                if len(cframe_raw.get('matrix', [])) >= 12:
                                    old_matrix = cframe_raw['matrix']
                                    new_matrix.extend([old_matrix[3], old_matrix[7], old_matrix[11]])
                                update_prop(ref, 'CFrame', {'matrix': new_matrix})
                            elif 'angles_deg' in cframe_raw:
                                new_cf = dict(cframe_raw)
                                new_cf['angles_deg'] = (new_rot['x'], new_rot['y'], new_rot['z'])
                                update_prop(ref, 'CFrame', new_cf)
                        populate_scene()
                    except (ValueError, TypeError):
                        pass
                
                rot_x = ui.number('X°', value=rot['x'], on_change=update_rot, format='%.1f'
                                 ).classes('flex-1').props('dense')
                rot_y = ui.number('Y°', value=rot['y'], on_change=update_rot, format='%.1f'
                                 ).classes('flex-1').props('dense')
                rot_z = ui.number('Z°', value=rot['z'], on_change=update_rot, format='%.1f'
                                 ).classes('flex-1').props('dense')
            
            # Кнопки быстрого поворота
            with ui.row().classes('w-full gap-1 mt-1'):
                for angle in [0, 45, 90, 180]:
                    def make_snap(a):
                        return lambda: snap_rotation(ref, cframe_raw, a)
                    ui.button(f'{angle}°', on_click=make_snap(angle)
                             ).props('dense').classes('text-xs flex-1')

def snap_rotation(ref, cframe_raw, step):
    """Привязать вращение к шагу"""
    if cframe_raw is None:
        return
    
    rot = extract_rotation_from_cframe(cframe_raw)
    
    def snap(val, step):
        return round(val / step) * step if step > 0 else 0
    
    new_rot = {
        'x': snap(rot['x'], step),
        'y': snap(rot['y'], step),
        'z': snap(rot['z'], step)
    }
    
    if isinstance(cframe_raw, dict):
        if 'matrix' in cframe_raw:
            new_matrix = euler_to_matrix(new_rot['x'], new_rot['y'], new_rot['z'])
            if len(cframe_raw.get('matrix', [])) >= 12:
                old_matrix = cframe_raw['matrix']
                new_matrix.extend([old_matrix[3], old_matrix[7], old_matrix[11]])
            update_prop(ref, 'CFrame', {'matrix': new_matrix})
        elif 'angles_deg' in cframe_raw:
            new_cf = dict(cframe_raw)
            new_cf['angles_deg'] = (new_rot['x'], new_rot['y'], new_rot['z'])
            update_prop(ref, 'CFrame', new_cf)
    
    populate_scene()

def select_instance(ref):
    if ref is None or state['parsed'] is None:
        return
    if isinstance(ref, str):
        try:
            ref = int(ref)
        except ValueError:
            return

    state['selected_ref'] = ref
    highlight_selected(ref)
    rebuild_explorer()

    cls      = state['parsed']['referent_to_class'].get(ref, '?')
    props    = state['parsed']['props'].get(ref, {})
    u        = state['_ui']
    icon_src = class_icon_src(cls)

    u['props_container'].clear()
    with u['props_container']:
        with ui.row().classes('items-center gap-2 mb-1'):
            if icon_src:
                with ui.element('div').style(
                    'width:48px;height:48px;background:white;display:flex;'
                    'align-items:center;justify-content:center;border-radius:4px;padding:2px;'
                ):
                    ui.image(icon_src).style('width:44px;height:44px;object-fit:contain;')
            ui.label(cls).classes('text-white font-bold text-sm')
            ui.label(f'ref {ref}').classes('text-gray-500 text-xs')
        ui.separator().classes('bg-gray-600 mb-1')

        # Отдельно обрабатываем CFrame
        if 'CFrame' in props:
            render_cframe_editor(ref, props['CFrame'], u['props_container'])
        
        # Остальные свойства
        for pname, pval in sorted(props.items()):
            if pname == 'Source' or pname == 'CFrame':
                continue
            
            with ui.row().classes('w-full gap-1 items-center min-h-[28px]'):
                ui.label(pname).classes('text-gray-400 text-xs w-36 shrink-0 truncate')

                if isinstance(pval, bool):
                    def make_bool_handler(prop_name):
                        def handler(e):
                            update_prop(ref, prop_name, e.value)
                        return handler
                    ui.checkbox(text='', value=pval,
                                on_change=make_bool_handler(pname)).props('dense')

                elif isinstance(pval, dict):
                    display = json.dumps(pval, ensure_ascii=False)
                    if len(display) > 60:
                        with ui.expansion(f'{display[:50]}...').classes('flex-1 bg-gray-700 text-xs'):
                            ui.code(display, language='json').classes('text-xs')
                    else:
                        def make_dict_handler(prop_name):
                            def handler(e):
                                try:
                                    val = json.loads(e.value)
                                    update_prop(ref, prop_name, val)
                                except json.JSONDecodeError:
                                    pass
                            return handler
                        ui.input(value=display,
                                 on_change=make_dict_handler(pname)
                                 ).classes('flex-1 text-xs bg-gray-700 text-white').props('dense')

                elif isinstance(pval, (list, tuple, bytes)):
                    ui.label(f'[{type(pval).__name__}: {len(pval)} эл.]').classes('text-xs text-gray-500 flex-1')

                elif pname in ('Color', 'Color3', 'BrickColor'):
                    try:
                        hex_c = color3_to_hex(pval) if isinstance(pval, dict) else str(pval)
                        ui.element('div').style(
                            f'width:20px;height:20px;background:{hex_c};'
                            'border:1px solid #555;border-radius:3px;'
                        )
                    except Exception:
                        pass
                    def make_str_handler(prop_name):
                        def handler(e):
                            update_prop(ref, prop_name, e.value)
                        return handler
                    ui.input(value=str(pval),
                             on_change=make_str_handler(pname)
                             ).classes('flex-1 text-xs bg-gray-700 text-white').props('dense')

                else:
                    def make_str_handler(prop_name):
                        def handler(e):
                            update_prop(ref, prop_name, e.value)
                        return handler
                    ui.input(value=str(pval),
                             on_change=make_str_handler(pname)
                             ).classes('flex-1 text-xs bg-gray-700 text-white').props('dense')

    if cls in SCRIPT_CLASSES:
        u['script_editor'].set_value(props.get('Source', ''))
        u['script_label'].set_text(f'{cls}: {props.get("Name","?")}')
        u['tabs'].set_value(u['tab_script'])
    else:
        u['tabs'].set_value(u['tab_props'])

# ── файлы ─────────────────────────────────────────────────────────────────────

def file_browser_dialog(mode='open'):
    """mode: 'open' или 'save'"""
    import os

    start_dir = None
    
    if state['file_path']:
        try:
            p = Path(state['file_path']).parent
            if p.exists() and os.access(str(p), os.R_OK):
                start_dir = p
        except Exception:
            pass
    
    if start_dir is None:
        try:
            home = Path.home()
            if home.exists() and os.access(str(home), os.R_OK):
                start_dir = home
        except Exception:
            pass
    
    if start_dir is None:
        for fallback in [Path('C:/'), Path('D:/'), Path.cwd()]:
            try:
                if fallback.exists() and os.access(str(fallback), os.R_OK):
                    start_dir = fallback
                    break
            except Exception:
                pass
    
    if start_dir is None:
        start_dir = Path.cwd()
    
    current_dir = {'path': start_dir}
    selected_file = {'path': None}

    with ui.dialog().props('maximized') as dlg:
        with ui.card().classes('w-full h-full bg-gray-900 text-white p-0 gap-0'):
            with ui.row().classes('w-full items-center px-3 py-2 bg-gray-800 gap-2'):
                ui.label('📂 Выбор файла' if mode=='open' else '💾 Сохранить как').classes('font-bold')
                ui.space()
                ui.button(icon='close', on_click=dlg.close).props('flat dense').classes('text-gray-400')

            path_label = ui.label('').classes('text-xs text-gray-400 px-3 py-1 bg-gray-800 w-full')

            with ui.scroll_area().classes('flex-1 w-full'):
                file_list = ui.column().classes('w-full p-0 gap-0')

            with ui.column().classes('w-full bg-gray-800 p-3 gap-2'):
                with ui.row().classes('w-full items-center gap-2'):
                    ui.label('📄' if mode == 'open' else '💾').classes('text-sm shrink-0')
                    if mode == 'open':
                        file_path_input = ui.input(
                            placeholder='Выберите файл из списка...',
                            value=''
                        ).classes('flex-1 bg-gray-700 text-white').props('dense')
                    else:
                        # ИСПРАВЛЕНО: .json заменён на .rbxl
                        default_name = Path(state['file_path']).stem + '.rbxl' if state['file_path'] else 'Place1.rbxl'
                        file_path_input = ui.input(
                            placeholder='имя_файла.rbxl',
                            value=default_name
                        ).classes('flex-1 bg-gray-700 text-white').props('dense')
                
                with ui.row().classes('w-full gap-2'):
                    confirm_btn = ui.button(
                        'Открыть' if mode=='open' else 'Сохранить',
                        on_click=lambda: on_confirm()
                    ).classes('flex-1 bg-blue-600' if mode=='open' else 'flex-1 bg-green-600')
                    
                    ui.button('Отмена', on_click=dlg.close).classes('bg-gray-600')

        # ... остальной код render_dir и on_confirm без изменений ...

        def render_dir(path: Path):
            try:
                current_dir['path'] = path
                path_label.set_text(f'📁 {path}')
                file_list.clear()

                with file_list:
                    if path.parent != path:
                        with ui.row().classes(
                            'w-full items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-700'
                        ) as row:
                            ui.label('📁').classes('text-lg shrink-0')
                            ui.label('..  (назад)').classes('text-sm text-gray-300')
                        row.on('click', lambda _, p=path.parent: render_dir(p))

                    entries = []
                    try:
                        for entry in sorted(path.iterdir()):
                            try:
                                is_dir = entry.is_dir()
                                entries.append((is_dir, entry))
                            except (PermissionError, OSError):
                                pass
                    except (PermissionError, OSError):
                        ui.label('⛔ Нет доступа').classes('text-red-400 px-3 py-2')
                        return

                    for is_dir, entry in sorted(entries, key=lambda x: (not x[0], x[1].name.lower())):
                        if is_dir:
                            icon = '📁'
                            label_cls = 'text-sm text-yellow-200'
                            row_cls = 'w-full items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-700'
                        else:
                            ext = entry.suffix.lower()
                            if ext == '.rbxl':
                                icon = '🎮'
                            elif ext == '.rbxlx':
                                icon = '📄'
                            elif ext == '.json':
                                icon = '📋'
                            else:
                                icon = '📄'
                            label_cls = 'text-sm text-white'
                            if selected_file['path'] == entry:
                                row_cls = 'w-full items-center gap-2 px-3 py-2 cursor-pointer bg-blue-600 hover:bg-blue-500'
                            else:
                                row_cls = 'w-full items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-700'

                        with ui.row().classes(row_cls) as row:
                            ui.label(icon).classes('text-lg shrink-0')
                            ui.label(entry.name).classes(f'{label_cls} truncate flex-1')
                            if not is_dir:
                                try:
                                    size_kb = entry.stat().st_size // 1024
                                    ui.label(f'{size_kb} KB').classes('text-xs text-gray-500 shrink-0')
                                except (OSError, FileNotFoundError):
                                    ui.label('? KB').classes('text-xs text-gray-500 shrink-0')

                        if is_dir:
                            row.on('click', lambda _, p=entry: render_dir(p))
                        else:
                            if mode == 'open':
                                def on_file_click(_, p=entry):
                                    selected_file['path'] = p
                                    file_path_input.set_value(str(p))
                                    render_dir(current_dir['path'])
                                row.on('click', on_file_click)
                            else:
                                def on_file_click_save(_, p=entry):
                                    file_path_input.set_value(p.name)
                                row.on('click', on_file_click_save)
            except Exception as e:
                ui.notify(f'Ошибка при чтении директории: {e}', color='negative')

        def on_confirm():
            try:
                if mode == 'open':
                    file_path = file_path_input.value.strip()
                    if not file_path:
                        ui.notify('Выберите файл из списка', color='warning')
                        return
                    
                    if not Path(file_path).exists():
                        ui.notify('Файл не существует', color='warning')
                        return
                    
                    dlg.close()
                    load_rbxl(file_path)
                else:
                    name = file_path_input.value.strip()
                    if not name:
                        ui.notify('Введите имя файла', color='warning')
                        return
                    
                    if os.path.isabs(name) or '/' in name or '\\' in name:
                        full = Path(name)
                    else:
                        full = current_dir['path'] / name
                    
                    dlg.close()
                    save_rbxl(str(full))
            except Exception as e:
                ui.notify(f'Ошибка: {e}', color='negative')

        try:
            render_dir(current_dir['path'])
        except Exception as e:
            print(f'Ошибка при открытии директории {current_dir["path"]}: {e}')
            try:
                render_dir(Path('C:/'))
            except Exception:
                try:
                    render_dir(Path.cwd())
                except Exception:
                    ui.notify('Не удалось открыть файловый браузер', color='negative')
                    return

    dlg.open()

def select_file_dialog():
    file_browser_dialog(mode='open')

def save_file_dialog():
    if state['parsed'] is None:
        ui.notify('Файл не загружен', color='warning')
        return
    file_browser_dialog(mode='save')

def _props_to_json_safe(parsed):
    out = {}
    for ref, p in parsed['props'].items():
        out[str(ref)] = {
            k: v if not isinstance(v, bytes) else v.decode('utf-8', 'replace')
            for k, v in p.items()
        }
    return out

def save_rbxl(file_path):
    if state['parsed'] is None:
        ui.notify('Нет данных', color='warning')
        return
    try:
        path = Path(file_path)
        
        # Всегда сохраняем как .rbxl
        if path.suffix.lower() not in ('.rbxl', '.rbxlx'):
            path = path.with_suffix('.rbxl')
        
        # Вызываем бинарное сохранение
        save_rbxl_binary(state['parsed'], str(path))
        
        state['file_path'] = str(path)
        state['modified'] = False
        
        ui.notify(f'💾 Сохранено: {path.name}', color='positive')
        logger.info(f'✅ Сохранено: {path}')
        
    except Exception as ex:
        logger.error(f'❌ Ошибка сохранения: {ex}')
        traceback.print_exc()
        ui.notify(f'❌ Ошибка сохранения: {ex}', color='negative')
        
        # Fallback: сохраняем в JSON если бинарное сохранение не удалось
        try:
            json_path = Path(file_path).with_suffix('.json')
            data = {
                'referent_to_class': {str(k): v for k, v in state['parsed']['referent_to_class'].items()},
                'parent_map': {str(k): v for k, v in state['parsed']['parent_map'].items()},
                'props': _props_to_json_safe(state['parsed']),
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            state['file_path'] = str(json_path)
            ui.notify(f'⚠️ Бинарное сохранение не удалось. Сохранено в JSON: {json_path.name}', color='warning')
        except Exception as ex2:
            ui.notify(f'❌ Ошибка: {ex2}', color='negative')


def quick_save():
    if state['parsed'] is None:
        ui.notify('Файл не загружен', color='warning')
        return
    
    if state['file_path']:
        # Всегда сохраняем как .rbxl
        path = Path(state['file_path'])
        if path.suffix.lower() != '.rbxl':
            path = path.with_suffix('.rbxl')
        save_rbxl(str(path))
    else:
        save_file_dialog()

def load_rbxl(path):
    logger.info(f'📂 ЗАГРУЗКА: {path}')
    try:
        parsed = parse_rbxl(path)
        state.update({'parsed': parsed, 'file_path': path,
                      'selected_ref': None, 'expanded': set(),
                      'modified': False})
        children_of = {}
        for child, parent in parsed['parent_map'].items():
            children_of.setdefault(parent, []).append(child)
        state['expanded'] = set(children_of.get(-1, []))
        rebuild_explorer()
        populate_scene()
        ui.notify(f'✅ {len(parsed["referent_to_class"])} объектов из {Path(path).name}',
                  color='positive')
    except Exception as ex:
        logger.error(f'❌ {ex}'); traceback.print_exc()
        ui.notify(f'❌ {ex}', color='negative')

def on_script_change(e):
    ref = state['selected_ref']
    if ref is None or state['parsed'] is None:
        return
    state['parsed']['props'].setdefault(ref, {})['Source'] = e.value
    state['modified'] = True

def save_script():
    ref = state['selected_ref']
    if ref is None:
        ui.notify('Скрипт не выбран', color='warning'); return
    src = state['parsed']['props'].get(ref, {}).get('Source', '')
    ui.notify(f'✅ {len(src)} симв. в памяти', color='positive')

# ── диалоги ───────────────────────────────────────────────────────────────────

def add_object_dialog():
    CLASSES = sorted([
        'Part','WedgePart','SpherePart','MeshPart','Model','Folder',
        'Script','LocalScript','ModuleScript','RemoteEvent','RemoteFunction',
        'BindableEvent','BindableFunction','ScreenGui','Frame','TextLabel',
        'TextButton','TextBox','ImageLabel','ImageButton','Sound',
        'ParticleEmitter','Fire','Smoke','PointLight','SpotLight',
        'SurfaceLight','NumberValue','StringValue','BoolValue',
        'IntValue','ObjectValue','Vector3Value','Animation','Tool','Camera',
    ])
    sel = state['selected_ref']
    default_parent = sel if sel is not None else find_workspace_ref()
    if default_parent is not None and default_parent != -1 and state['parsed']:
        p_cls  = state['parsed']['referent_to_class'].get(default_parent, '?')
        p_name = get_prop(default_parent, 'Name', str(default_parent))
    else:
        p_cls, p_name, default_parent = '?', 'DataModel', -1

    with ui.dialog() as dlg, ui.card().classes('bg-gray-800 text-white w-80'):
        ui.label('➕ Добавить объект').classes('font-bold text-lg mb-2')
        cls_select = ui.select(CLASSES, value='Part', label='Класс').classes('w-full')
        name_input = ui.input('Имя', value='NewPart').classes('w-full bg-gray-700 text-white')
        with ui.row().classes('items-center gap-1 mt-1'):
            src = class_icon_src(p_cls)
            if src:
                with ui.element('div').style('width:20px;height:20px;background:white;display:flex;align-items:center;justify-content:center;border-radius:2px;'):
                    ui.image(src).style('width:16px;height:16px;object-fit:contain;')
            ui.label(f'Родитель: {p_name}').classes('text-gray-400 text-xs')

        def do_add():
            if state['parsed'] is None:
                ui.notify('Нет файла', color='warning'); return
            new_ref = max(state['parsed']['referent_to_class'].keys(), default=0) + 1
            state['parsed']['referent_to_class'][new_ref] = cls_select.value
            state['parsed']['parent_map'][new_ref]        = default_parent
            state['parsed']['props'][new_ref]             = {'Name': name_input.value}
            state['expanded'].add(default_parent)
            state['modified'] = True
            rebuild_explorer(); populate_scene(); select_instance(new_ref)
            dlg.close()
            ui.notify(f'✅ {name_input.value}', color='positive')

        with ui.row().classes('mt-2 gap-2'):
            ui.button('Добавить', on_click=do_add).classes('bg-green-600')
            ui.button('Отмена', on_click=dlg.close).classes('bg-gray-600')
    dlg.open()

def delete_selected():
    ref = state['selected_ref']
    if ref is None or state['parsed'] is None:
        ui.notify('Не выбран', color='warning'); return
    name = get_prop(ref, 'Name', str(ref))
    for d in ('referent_to_class', 'parent_map', 'props'):
        state['parsed'][d].pop(ref, None)
    state['expanded'].discard(ref)
    state['selected_ref'] = None
    state['modified'] = True
    rebuild_explorer(); populate_scene()
    ui.notify(f'🗑 {name}', color='positive')

def publish_dialog():
    with ui.dialog() as dlg, ui.card().classes('bg-gray-800 text-white w-96'):
        ui.label('☁ Open Cloud').classes('font-bold text-lg mb-2')
        univ = ui.input('Universe ID').classes('w-full bg-gray-700 text-white')
        plc  = ui.input('Place ID').classes('w-full bg-gray-700 text-white')
        key  = ui.input('API Key', password=True).classes('w-full bg-gray-700 text-white')
        vt   = ui.select(['Published','Saved'], value='Published').classes('w-full')
        def do_pub():
            if not state['file_path']:
                ui.notify('Нет файла', color='warning'); return
            s, t = publish_place(state['file_path'], univ.value, plc.value, key.value, vt.value)
            dlg.close()
            ui.notify(f'HTTP {s}: {t[:200]}', color='positive' if s==200 else 'negative')
        with ui.row().classes('mt-2 gap-2'):
            ui.button('Опубликовать', on_click=do_pub).classes('bg-purple-600')
            ui.button('Отмена', on_click=dlg.close).classes('bg-gray-600')
    dlg.open()

# ── UI ────────────────────────────────────────────────────────────────────────

def handle_key(e):
    if e.modifiers.ctrl and e.key.name == 'o':    select_file_dialog()
    elif e.modifiers.ctrl and e.modifiers.shift and e.key.name == 's': save_file_dialog()
    elif e.modifiers.ctrl and e.key.name == 's':  quick_save()
    elif e.modifiers.ctrl and e.key.name == 'c':  copy_object()
    elif e.modifiers.ctrl and e.key.name == 'v':  paste_object()
    elif e.modifiers.ctrl and e.key.name == 'd':  duplicate_object()
    elif e.key.name == 'Delete':                   delete_selected()
    elif e.key.name == 'F5':                       populate_scene()

def build_ui():
    with ui.header().classes('bg-gray-900 text-white items-center gap-2 px-3 py-1 min-h-0'):
        ui.label('🎮 RbxStudio').classes('text-base font-bold mr-2')
        if state.get('modified'):
            ui.label('●').classes('text-yellow-400 text-xs')
        ui.button('📂', on_click=select_file_dialog).props('flat').classes('text-white')
        ui.button('💾', on_click=quick_save).props('flat').classes('text-white').tooltip('Сохранить (Ctrl+S)')
        ui.button('💾 Как...', on_click=save_file_dialog).props('flat').classes('text-white text-xs').tooltip('Сохранить как (Ctrl+Shift+S)')
        ui.button('➕', on_click=add_object_dialog).props('flat').classes('text-white')
        ui.button('🗑', on_click=delete_selected).props('flat').classes('text-red-400')
        ui.button('☁', on_click=publish_dialog).props('flat').classes('text-purple-400')
        ui.button('🔄', on_click=populate_scene).props('flat').classes('text-gray-300')

    with ui.splitter(value=18).classes('w-full').style('height:calc(100vh - 40px);min-height:0;') as sp1:

        with sp1.before:
            explorer_col = ui.column().classes('w-full h-full bg-gray-800 no-wrap overflow-hidden p-0 gap-0')
            with explorer_col:
                ui.label('Explorer').classes('text-white font-bold px-2 py-1 bg-gray-700 w-full text-sm shrink-0')
                with ui.scroll_area().classes('w-full flex-1'):
                    tree_container = ui.column().classes('w-full p-0')

        with sp1.after:
            with ui.splitter(value=72).classes('w-full h-full') as sp2:
                with sp2.before:
                    with ui.column().classes('w-full h-full bg-gray-950'):
                        ui.label('Viewport').classes('text-white font-bold px-2 py-1 bg-gray-700 w-full text-sm')
                        scene3d = ui.scene(
                            width=None, height=None, grid=True,
                            on_click=lambda e: (
                                select_by_scene_name(e.hits[0].object_name)
                                if e.hits and len(e.hits) > 0
                                else deselect()
                            ),
                        ).classes('w-full flex-1')
                        with scene3d:
                            scene3d.axes_helper()

                with sp2.after:
                    with ui.column().classes('w-full h-full bg-gray-800'):
                        with ui.tabs().classes('bg-gray-700 text-white w-full') as tabs:
                            tab_props  = ui.tab('Properties')
                            tab_script = ui.tab('Script')

                        with ui.tab_panels(tabs, value=tab_props).classes('flex-1 w-full bg-gray-800 overflow-hidden'):
                            with ui.tab_panel(tab_props):
                                with ui.scroll_area().classes('w-full h-full'):
                                    props_container = ui.column().classes('w-full gap-1 p-2')
                                    ui.label('← Выбери объект').classes('text-gray-500 text-sm')

                            with ui.tab_panel(tab_script):
                                script_label = ui.label('').classes('text-gray-400 text-xs px-2 py-1')
                                script_editor = ui.codemirror(
                                    '', language='lua', theme='dracula',
                                    on_change=on_script_change,
                                ).classes('w-full flex-1')
                                ui.button('💾 Сохранить скрипт', on_click=save_script).classes('bg-green-700 m-2')

    state['_ui'].update({
        'tree_container':  tree_container,
        'scene3d':         scene3d,
        'props_container': props_container,
        'script_editor':   script_editor,
        'script_label':    script_label,
        'tabs':            tabs,
        'tab_script':      tab_script,
        'tab_props':       tab_props,
    })
    ui.keyboard(on_key=handle_key)


app.add_static_files('/icons', str(ICONS_DIR))


@app.get('/api/select/{ref}')
def api_select(ref: int):
    select_instance(ref)
    return {'status': 'ok', 'ref': ref}


@ui.page('/')
def index():
    ui.dark_mode().enable()
    ui.query('body').style('margin:0;overflow:hidden;height:100vh;display:flex;flex-direction:column;background:#111827')
    ui.query('.nicegui-content').style('flex:1;display:flex;flex-direction:column;overflow:hidden;padding:0')
    build_ui()
    if len(sys.argv) > 1 and sys.argv[1].endswith(('.rbxl', '.rbxlx')):
        ui.timer(0.8, lambda: load_rbxl(sys.argv[1]), once=True)


if __name__ == '__main__':
    ui.run(
        title='RbxStudio Mobile',
        port=8080,
        host='0.0.0.0',
        dark=True,
        reload=False,
        favicon='🎮',
    )