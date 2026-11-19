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
from rbxl_parser import parse_rbxl, save_rbxl, publish_place, export_rbxm, import_rbxm, scan_rbxm
from rbxl_parser import union_mesh_from_parsed as _union_mesh_solid, union_mesh_render_json
from flask import Flask, request, jsonify, Response, send_from_directory
from pathlib import Path
import sys
import subprocess
import os
import io



# The .whl cache next to the script — after the first (only) install with
# network access pip puts the downloaded wheels here, and all later launches on
# Termux (including without internet — a plane, the subway, no SIM card) install
# dependencies from THIS folder via --no-index, instead of from PyPI again.
#
# RSW_VENDOR_DIR — the same logic as RSW_ICONS_DIR below: if app.py
# is started under the APK wrapper (bridge_launcher.py replaces __file__ with
# a path inside hotpatch, which is not writable), this variable
# points to a real writable folder (for example filesDir/vendor).
# On an ordinary launch (`python app.py` in Termux/on a PC) — a path next to
# the script, as before.
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
        print(f'[RbxStudio] Installing {pkg} from the local cache (offline)...')
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', pkg,
                '--break-system-packages', '-q',
                '--no-index', '--find-links', str(_WHEELS_DIR),
            ])
            return
        except subprocess.CalledProcessError:
            print(f'[RbxStudio] The offline cache for {pkg} did not fit, trying the network...')

    print(f'[RbxStudio] Installing {pkg} (and saving the .whl to the cache for offline runs)...')
    # First we download the wheel into the cache, then install from it — this way the cache
    # is refilled regardless of whether pip install has its own cache.
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'download', pkg,
            '-d', str(_WHEELS_DIR), '-q',
        ])
    except subprocess.CalledProcessError:
        pass  # even without downloading the .whl the ordinary install below may work
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install', pkg,
        '--break-system-packages', '-q',
        '--find-links', str(_WHEELS_DIR),
    ])


_ensure('flask')


sys.path.insert(0, str(Path(__file__).parent))

# On Android the icons (icons/, icons.txt) NEVER go through the
# OTA hotfix (see OtaUpdater.kt) — only through a full APK rebuild.
# But when a hotfix is present, bridge_launcher.py replaces this module's __file__
# with a path inside filesDir/hotpatch, where icons/ and icons.txt
# physically don't exist. This used to silently zero out CLASS_ICONS and
# turn off all icons in Explorer/Properties. RSW_ICONS_DIR is an explicit path to the app's
# PERMANENT (baked-in) folder, which bridge_launcher.py
# passes through an environment variable precisely for this case; if
# it is absent (an ordinary `python app.py` launch from a PC), we use the previous
# behavior — a path next to this file.
_ICONS_BASE = Path(os.environ['RSW_ICONS_DIR']) if os.environ.get('RSW_ICONS_DIR') \
    else Path(__file__).parent

ICONS_DIR = _ICONS_BASE / 'icons'
PORT = 47182  # a non-standard port — 8080 is often taken by other apps/ADB

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
    # There never was an 'Instance.png' in icons/ — any class without an entry in
    # CLASS_ICONS used to silently stay without an icon. 'Unknown.png' is
    # really there.
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

# default sizes for new parts from the Add dialog (as in Roblox; the ladder is tall so there is something to climb)
_ADD_SIZE_DEFAULTS = {'Seat': (4, 1, 2), 'VehicleSeat': (4, 1, 2), 'TrussPart': (2, 10, 2), 'SpawnLocation': (6, 1, 6)}

PART_CLASSES = {
    'Part', 'WedgePart', 'CornerWedgePart', 'TrussPart',
    'SpawnLocation', 'Seat', 'VehicleSeat', 'SpherePart',
    # MeshPart used not to be included here — such objects were silently skipped
    # in build_all_scene_objects (see below) and didn't get into the scene at all,
    # although the parser sees them and the class is actively used in
    # the Lua sandbox/the "Add" dialog. We render it as an ordinary box (the real
    # .mesh geometry isn't parsed — see _extract_part_texture_id below
    # for the texture).
    'MeshPart',
    # UnionOperation (a CSG union) used not to be included here at all — such
    # objects were silently skipped and didn't get into the scene. Their real
    # geometry lies in the compressed binary blob MeshData2 (SharedString),
    # which we don't decode, so for now we draw a box by Size — with the
    # right CFrame/color/material (a union's Size is the dimension of the
    # finished body, so the box at least matches its bounding box).
    # We do NOT add NegateOperation: it is a "subtracted" part, it isn't
    # visible in the game.
    'UnionOperation',
}

# 2D interface classes (Roblox GUI) — rendered by a separate DOM overlay
# on top of the 3D viewport in Play (see index.html, buildGuiOverlay/#gui-overlay),
# and not as three.js/cannon.js scene objects, like PART_CLASSES.
GUI_ROOT_CLASSES = {'ScreenGui', 'BillboardGui', 'SurfaceGui'}
GUI_CONTAINER_CLASSES = {'Frame', 'ScrollingFrame', 'CanvasGroup'}   # CanvasGroup: a container with a shared transparency (GroupTransparency)
GUI_LEAF_CLASSES = {
    'TextLabel', 'TextButton', 'TextBox', 'ImageLabel', 'ImageButton',
}
# UICorner/UIStroke aren't drawn as a separate DOM node — they are modifiers
# of the neighboring GUI object (border-radius / outline), see index.html
# applyGuiDecorationToParent. They used not to be in any of the class
# sets at all, so /api/gui_tree silently dropped them — the frontend
# never learned about the TopLeftRadius/.../Thickness stored in the
# .rbxl itself, and all GUI plates in Play were always drawn with square corners and
# without an outline, regardless of what is really configured in the file.
GUI_DECORATION_CLASSES = {'UICorner', 'UIStroke', 'UIScale', 'UIListLayout', 'UIGridLayout'}   # layouts: the layout properties are needed by the client, they have no DOM node   # UIScale: the parent's scale (see applyGuiElementStyle)
GUI_CLASSES = GUI_ROOT_CLASSES | GUI_CONTAINER_CLASSES | GUI_LEAF_CLASSES | GUI_DECORATION_CLASSES

# The properties that the frontend really needs to draw the GUI overlay —
# a deliberately narrow list (like SCRIPT_CLASSES above in spirit), so as not to
# push arbitrary binary/rare properties over the network for the sake of one div.
GUI_PROPS = (
    'Name', 'Position', 'Size', 'AnchorPoint', 'Visible', 'Enabled',
    'ZIndex', 'BackgroundColor3', 'BackgroundTransparency', 'BorderSizePixel',
    'BorderColor3', 'Text', 'TextColor3', 'TextTransparency', 'TextSize',
    'TextScaled', 'TextWrapped', 'TextXAlignment', 'TextYAlignment', 'Font',
    'Image', 'ScaleType', 'ClipsDescendants',
    # UICorner: some files (this one included) store an independent radius
    # per corner (the newer UICorner variant in Roblox) instead of
    # one shared CornerRadius — the frontend understands both variants.
    'CornerRadius', 'TopLeftRadius', 'TopRightRadius',
    'BottomLeftRadius', 'BottomRightRadius',
    # UIStroke
    'Color', 'Thickness', 'Transparency',
    # UIScale
    'Scale',
    # CanvasGroup
    'GroupTransparency',
    # SurfaceGui (an interface on a part's face)
    'Face', 'SizingMode', 'PixelsPerStud', 'CanvasSize', 'AlwaysOnTop', 'Brightness',
    # BillboardGui (an interface in the world, facing the camera)
    'Adornee', 'StudsOffset', 'StudsOffsetWorldSpace', 'SizeOffset', 'ExtentsOffset', 'MaxDistance',
    # UIListLayout / UIGridLayout (layout of descendants)
    'FillDirection', 'Padding', 'HorizontalAlignment', 'VerticalAlignment', 'SortOrder', 'StartCorner',
    'CellSize', 'CellPadding', 'FillDirectionMaxCells', 'LayoutOrder',
)

# Script/LocalScript run in DIFFERENT environments in real Roblox
# (server and client respectively) — 'side' is used by the frontend
# (index.html, /api/scripts) only to mark with a badge and in
# Output where the output came from; the engine itself keeps one shared Lua VM
# (there is no real client↔server network), see the comment at api_scripts below.
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
    """BasePart color. In new .rbxl files (zstd, 2024+) the color lives in the
    Color3uint8 property (integers 0..255), NOT in Color3/Color (float 0..1) — previously
    only the latter were read, so all Parts from new files were
    gray (#a0a0a0): R6 Head/Torso/arms/legs without skin color, etc."""
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
# RightAngleRamp=10, CornerWedge=11. Previously 1 was read as a cylinder and 6
# (Brick) as a wedge — the numbers were mixed up.
MESHTYPE_TO_SHAPE = {
    0: 'head', 1: 'box', 2: 'wedge', 3: 'sphere', 4: 'cylinder',
    6: 'box', 7: 'wedge', 8: 'cone', 9: 'wedge', 10: 'wedge', 11: 'wedge',
}


def find_special_mesh(ref, children_by_parent, all_props, referent_to_class):
    """Properties of a part's first SpecialMesh child (or None). Previously we
    looked it up by referent number (ref+1 / ref+2) — that worked only while the
    mesh lay in the file right after the part."""
    for child in children_by_parent.get(ref, ()):
        c = referent_to_class.get(child)
        if c == 'SpecialMesh':
            return all_props.get(child, {})
        if c in _LEGACY_MESH_TYPE:
            # BlockMesh/CylinderMesh — old classes of the same kind (Scale/Offset), the type is baked into the class
            return dict(all_props.get(child, {}), MeshType=_LEGACY_MESH_TYPE[c])
    return None


_LEGACY_MESH_TYPE = {'BlockMesh': 6, 'CylinderMesh': 4}


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



# --- Union geometry from its SOURCE parts --------------------------------------------------------------
# The new union format stores the mesh in MeshData2 (compressed streams), and the old SolidMeshHolder is empty — then union_mesh_from_parsed
# returned None, and the union was drawn as a solid box by Size (the table in fnf.rbxl). But ChildData/ChildData2 hold a nested
# rbxm with the parts the union is made of (legs, tabletop...), in the union's LOCAL space. We build the mesh from them:
# real operands instead of a solid box. Limitations: subtracting operands (NegateOperation) are skipped, and the intersections of
# parts aren't merged — extra faces remain inside (it doesn't affect the look, since they are inside).
_UNION_CHILD_SHAPES_BOX = {None, 1}   # Part.Shape: 1 = Block (default); other shapes are approximated by the operand's box


def _box_triangles(pos, rot, half):
    """Box (center pos, rotation rot as 3x3 by rows, half sizes half) -> (positions, normals, tri_index)."""
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
        # the traversal order depends on the sign and the parity of the axes — we take it so that the triangle's normal matches the face normal
        a, b, c, d = base, base + 1, base + 2, base + 3
        e1 = [positions[b][i] - positions[a][i] for i in range(3)]
        e2 = [positions[c][i] - positions[a][i] for i in range(3)]
        cr = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
        if sum(cr[i] * nrm[i] for i in range(3)) < 0:
            b, d = d, b
        index.append((len(normals) - 1, [a, b, c, a, c, d]))
    return positions, normals, index


def _collect_union_child_boxes(parsed, ref, depth=0, out=None):
    """Recursively collects the (pos, rot, half) operands of union ref in its local space. None — no data."""
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
            continue   # NegateOperation and the rest — we don't add
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
            # a nested union: we try its own operands (in its local space -> transfer into ours)
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
    """Union mesh: first the old format (SolidMeshHolder), otherwise one assembled from the source parts (ChildData/ChildData2)."""
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


CHUNK_SIZE = 48.0   # studs — the target side size of one fragment
CHUNK_MAX_GRID = 16  # a limit on both X and Z for the user's sake
# A threshold below which we don't cut an object — there is no point spawning fragments
# for a conventional 60x2x2 fence.
CHUNK_MIN_DIM = 64.0


def _rot_axis_world(rot, col):
    # rot — a row-wise 3x3 matrix (see get_rot_matrix); the world direction
    # of the local axis col is COLUMN col of the matrix (the multiplication R * e_col).
    return (rot[col], rot[3 + col], rot[6 + col])


def chunk_box_object(o):
    """Cuts a single box object into a grid of sub-fragments along the two largest
    dimensions (the third — usually the thickness — is left alone). Each fragment is a
    standalone object with an honest center and size, so that the distance
    to the player is computed per piece, not for the giant original."""
    dims = [('sx', o['sx']), ('sy', o['sy']), ('sz', o['sz'])]
    # dimension indexes from larger to smaller
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
        # offset of fragment i's center along the local axis big_a from the center
        # of the original object (in studs, in local coordinates)
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
            # a synthetic but unique ref — the part's real ref is
            # encoded in the high bits, there must be no collisions with real
            # referents (usually < 10^6)
            chunk['ref'] = o['ref'] * 100000 + i * CHUNK_MAX_GRID + j
            chunk['source_ref'] = o['ref']
            out.append(chunk)
    return out


def chunk_large_objects(objs):
    out = []
    for o in objs:
        # meshId — real custom geometry (see _extract_real_mesh_id),
        # not a real bounding box: chunk_box_object cuts an object into
        # sub-boxes literally by its Size, which for a real mesh (the shape
        # almost never matches a rectangle) would break the
        # visible model into a set of wrong cubes instead of itself.
        # unionMesh — the same: a union has its own geometry (with cut-outs),
        # sub-boxes by Size would cover the cut-outs.
        if o.get('shape') == 'box' and not o.get('meshId') and not o.get('unionMesh'):
            out.extend(chunk_box_object(o))
        else:
            out.append(o)
    return out



# The scene version counter: edits in the editor (adding/deleting/changing
# an object's properties) mutate state['parsed'] IN PLACE, without recreating the
# dict itself — so id(parsed) doesn't change, and the caches below (build_all_scene_
# objects/get_chunk_index), keyed only by id(parsed), would keep
# silently serving data from before the edit.
# Every mutation point (see api_edit_prop/api_add_instance/api_delete)
# calls bump_scene_version() — caches are keyed on (id(parsed), version), so
# any edit honestly invalidates all of them at once.
_scene_version = {'v': 0}


def bump_scene_version():
    _scene_version['v'] += 1


# ---- Chunk-based streaming (like Minecraft / Unreal World Partition) ----
#
# All the previous iterations (one ray → a fan of rays → rays with a radius →
# rays of unlimited length) tried to solve "what to load" via
# the camera's view direction. That is NOT how it is usually done —
# no major open-world streaming engine ties geometry loading
# to the camera direction, only to the DISTANCE from the player: the world is
# cut once (when the map is opened) into a uniform 2D grid of cells
# along the X/Z axes (the Y height inside a cell isn't limited — the top of
# a tall tower stays in the same cell as its base), and on
# every tick we simply take all cells within loadRadius of the player.
# No raycasting, no camera direction — only position.
CHUNK_CELL_SIZE = 100.0  # studs per cell side

_chunk_index_cache = {'parsed_id': None, 'index': None}


def get_chunk_index():
    parsed = state.get('parsed')
    if not parsed:
        return {}
    pid = (id(parsed), _scene_version['v'])
    if _chunk_index_cache['parsed_id'] != pid:
        # We split large objects (chunk_large_objects, already present for the
        # .rbxl export) BEFORE laying them out into cells — otherwise a wall
        # 300 studs long lands in only one cell by its
        # center and won't be found when the player stands in a neighboring one, although
        # physically the wall is right in front of them.
        # Parts from ServerStorage/ReplicatedStorage/StarterPack (nw) don't exist in the world — they don't get into the scene;
        # their data for Clone() is served by a separate handler /api/scene?nw=1.
        objs = chunk_large_objects([o for o in build_all_scene_objects() if not o.get('nw')])
        index = {}
        for o in objs:
            # Half-size along X/Z (without accounting for rotation — a conservative
            # estimate slightly larger than the real OBB, but cheap and without
            # the risk of missing a cell the object really touches).
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
    # Circular (in the X/Z plan) selection of objects around the player — the cell grid
    # is used only as a fast way NOT to iterate over all objects
    # of the map (candidates are taken from the square of cells touching the circle of
    # radius radius), the "is it within the radius" filtering — by an honest
    # euclidean distance.
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
                    continue  # an object could fall into several neighboring cells
                seen_refs.add(o['ref'])
                d = math.sqrt((o['px'] - cx) ** 2 + (o['py'] - cy) ** 2 + (o['pz'] - cz) ** 2)
                if d <= radius:
                    result.append((d, o))

    # We sort NOT by pure distance, but with a correction for the object's size.
    # Without this, when the overall budget (limit/streamCap in api_scene) is smaller
    # than the total number of objects in the radius, the top gets filled by nearby small parts
    # (grass, trash, decor right next to the player) — while a structurally important distant
    # wall or floor, which are really needed for the view, simply don't make
    # the cut. Large objects get a discount on their "effective"
    # distance (a logarithm — so that one giant terrain piece doesn't eat
    # the whole budget monopolistically, but an ordinary wall/floor noticeably beats
    # a scatter of small stuff at the same distance).
    def sort_key(pair):
        d, o = pair
        bounding_radius = math.sqrt(o['sx'] ** 2 + o['sy'] ** 2 + o['sz'] ** 2) * 0.5
        return max(0.0, d - bounding_radius) / (1.0 + math.log1p(bounding_radius))

    result.sort(key=sort_key)
    return result


_scene_build_cache = {'parsed_id': None, 'objs': None}


def _rbxassetid_num(value):
    """'rbxassetid://123' -> '123'. Filters out rbxasset://textures/... —
    those are files built into Studio, they have no numeric id and can't be
    pulled via /api/asset-proxy anyway (see the assetdelivery notes there)."""
    if not value:
        return None
    s = str(value)
    # Two asset link formats: 'rbxassetid://123' (new) and 'http://www.roblox.com/asset/?id=123'
    # (old; the classic R15 arms/legs 5487114xx and their textures are written this way). Previously only the
    # first was accepted — parts with the second lost both the mesh and the texture, and were drawn as a fallback cube.
    m = _re.search(r'(?:rbxassetid://|[?&]id=)(\d+)', s, _re.I)
    return m.group(1) if m else None


def _asset_url_num(value):
    """The numeric id from 'http://www.roblox.com/asset/?id=123' or 'rbxassetid://123'
    (ShirtTemplate/PantsTemplate are stored in the former form)."""
    if not value:
        return None
    s = str(value)
    if 'rbxasset://' in s and 'rbxassetid://' not in s:
        return None
    m = _re.search(r'\d+', s)
    return m.group() if m else None


# The parts of an R6 character that clothing lies on (Shirt/Pants from sibling
# children of the same Model): shirt — torso and arms, pants — torso and legs
# (in the 585x559 template arms/legs lie in the same rectangles,
# so a shirt can't be put on the legs and pants on the arms).
R6_CLOTH_LIMBS = {
    'Torso': ('shirt', 'pants'),
    'Left Arm': ('shirt',), 'Right Arm': ('shirt',),
    'Left Leg': ('pants',), 'Right Leg': ('pants',),
}


def _extract_part_texture_id(ref, cls, props, children_by_parent, all_props, referent_to_class):
    """We look for ANY real (rbxassetid://) image source for a part:
    1) TextureID/Texture directly on the MeshPart,
    2) the Texture of a child Decal,
    3) the TextureId of a child SpecialMesh.
    The first one found wins — combining several textures on one
    box approximation won't work anyway, this is not a full UV mesh.
    
    Returns (texture_id, face) — face is taken ONLY from a Decal (its
    Face property — which face to apply it to, 'Front' by default,
    as in Roblox itself) and only for it: previously the texture was put as
    ONE material on the whole BoxGeometry — i.e. on ALL 6 faces at once
    (the default each-face-0..1 UV of Three.js), not on one, as in
    real Roblox — hence the "textures were laid out badly" (a stretched
    copy of the texture on all sides at once). For MeshPart.TextureID/
    SpecialMesh we don't return face — on a real mesh they wrap
    the whole surface, not one face, so "on all faces" is closer
    to the truth here (it is still only a box approximation, not a real mesh)."""
    if cls == 'MeshPart':
        # SurfaceAppearance.ColorMap — in Roblox it has priority over
        # MeshPart.TextureID (for such meshes TextureID is usually empty — as with
        # sharks, which for this reason had no texture).
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
                # Face — a NormalId number; 0 (Right) is falsy under `or`, hence the explicit check for None
                _f = child_props.get('Face')
                return tid, (_f if _f is not None and _f != '' else 'Front')
        elif child_cls == 'SpecialMesh':
            tid = _rbxassetid_num(all_props.get(child, {}).get('TextureId'))
            if tid:
                return tid, None
    return None, None


_NORMAL_ID_NAMES = ['Right', 'Top', 'Back', 'Left', 'Bottom', 'Front']


def _normal_id_name(face):
    """Enum.NormalId (a number 0..5 or a name) -> the face name; unknown -> Front."""
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
    """ALL Decals of a part: [{tex, face, op}] — one per face (when there are several on
    one face, the one with the larger ZIndex wins, on a tie — the later one).
    Previously only the first one found was taken, and posters on other faces disappeared."""
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
    """AlphaMode of the SurfaceAppearance whose ColorMap the MeshPart texture was taken from:
    0 = Overlay (alpha — «how much the texture covers the part's Color»), 1 = Transparency (alpha — transparency),
    2 = TintMask. None — the texture is not from a SurfaceAppearance (an ordinary TextureID: alpha = cutout)."""
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
    """MeshId for REAL geometry — unlike the shape heuristic in
    build_all_scene_objects (which merely picks the nearest of a FIXED
    SET of primitives: box/sphere/cylinder/cone/wedge), this is a separate
    custom mesh that previously wasn't loaded at all: MeshPart.MeshId
    and SpecialMesh.MeshId (with MeshType.FileMesh, the number 5 — the only
    type where MeshId points to real custom geometry from the server;
    Cylinder/Sphere/Wedge/Head etc. are built-in primitives, their
    MeshId is either empty or ignored by real Roblox too, so no
    real geometry needs to be loaded). Previously these MeshIds weren't
    read for geometry anywhere at all — FileMesh meshes (a BasePart with a child
    SpecialMesh, MeshType=5) and any MeshPart were rendered ONLY as a
    bounding box, hence "meshes don't load"/"crooked unwrap" — the texture
    was glued onto an approximation instead of the real shape and its real UVs."""
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
    # Previously this parsing (CFrame/rotation matrices, looking up a SpecialMesh for
    # the shape, color, Anchored/CanCollide) was run again over ALL map objects
    # on EVERY /api/scene call — and streaming calls it every
    # ~600 ms. On maps of several thousand parts (Castle Warfare) this
    # was the main cause of slowdowns: raycast/sorting themselves are in fact
    # fast, but every request first rebuilt the WHOLE object list
    # from scratch. The map doesn't change between openings — we cache the
    # built list by the id of the parsed map, like get_chunk_index.
    parsed = state.get('parsed')
    if not parsed:
        return []
    pid = (id(parsed), _scene_version['v'])
    if _scene_build_cache['parsed_id'] == pid:
        return _scene_build_cache['objs']

    # child ref -> parent ref from parent_map — we invert it once
    # for the whole scene build, instead of looking for children with a linear pass for every
    # part (on maps of thousands of objects that would be an O(n^2) build).
    children_by_parent = {}
    for child_ref, parent_ref in parsed['parent_map'].items():
        children_by_parent.setdefault(parent_ref, []).append(child_ref)

    # MaterialService/MaterialVariant: (name, BaseMaterial) -> maps. A part
    # refers to a variant by name in MaterialVariantSerialized (this is how the
    # gloveR/gloveL gloves get their own material 'main').
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

        # Get the Position
        pos = props.get('Position', {})
        if isinstance(pos, dict):
            px = safe_float(pos.get('x', 0))
            py = safe_float(pos.get('y', 0))
            pz = safe_float(pos.get('z', 0))
        else:
            px = py = pz = 0

        # Get the CFrame (if present, it can override the position)
        cf = props.get('CFrame', {})
        # We use the CFrame only if it really contains a position or a matrix
        if isinstance(cf, dict) and ('position' in cf or 'matrix' in cf):
            cf_pos = get_pos(cf)
            # If get_pos returned non-(0,0,0) — we take the position from the CFrame
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

        # Color (Color3uint8 from new files, otherwise Color3/Color/BrickColor)
        color = get_part_color(props)

        # Transparency: previously not passed at all, and an invisible
        # HumanoidRootPart (Transparency=1, the size of the Torso) was drawn as
        # a solid gray block over the character.
        transp = safe_float(props.get('Transparency', 0.0), 0.0)
        opacity = max(0.0, min(1.0, 1.0 - transp))
        # A Head that is replaced by an accessory head (the Handle has its own
        # FaceCenterAttachment, like Baki_head): in Roblox the Head is hidden, otherwise
        # it covers the accessory's mesh (this is how it was: «the Head overlaps the texture»).
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

        # Shape: Part.Shape (0=Ball, 1=Block, 2=Cylinder — axis along X),
        # class SpherePart, or a child SpecialMesh (Enum.MeshType).
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
                # FileMesh: the real size = the mesh's native size * Scale,
                # the part's Size does NOT take part — we pass Scale to the client.
                mesh_scale = [msx, msy, msz]
            elif mt in MESHTYPE_TO_SHAPE:
                shape = MESHTYPE_TO_SHAPE[mt]
                if shape == 'head':
                    # Head mesh — a rounded cylinder; the width = the depth
                    # (otherwise the R6 Head 2x1x1 would come out 2.5 wide).
                    sx, sy, sz_ = sz_ * msx, sy * msy, sz_ * msz
                else:
                    sx, sy, sz_ = sx * msx, sy * msy, sz_ * msz
            if mox or moy or moz:
                mesh_offset = [mox, moy, moz]
        name = props.get('Name', cls)

        # The part's Enum.Material and MaterialVariant
        material = props.get('Material')
        if not isinstance(material, int):
            material = 256
        mvar = None
        mv_name = props.get('MaterialVariantSerialized')
        if mv_name:
            mvar = material_variants.get((mv_name, material))

        # R6 clothing (Shirt/Pants next to the part in the same Model)
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
        # The Decal's own transparency (0..1). A Decal on an invisible part (Transparency=1) is a common
        # trick for posters/signs: the part isn't visible, but the picture is. Previously the texture
        # was tinted with the PART's transparency, and such posters disappeared.
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

        # A union has a real mesh if SolidMeshHolder decodes.
        # We don't send the mesh itself over the network — the client fetches it via /api/union_mesh.
        union_mesh = (cls == 'UnionOperation'
                      and union_mesh_from_parsed(parsed, ref) is not None)
        # Newer Studio saves a union WITHOUT embedded geometry (MeshData/MeshData2/ChildData are empty): only a link to its mesh
        # asset in Content («.../asset/?id=1999766009»). Such unions were drawn as a plain box (the TV's body, the screen frame…). The link
        # is fetched like a MeshPart's MeshId — the client fits the mesh into the union's Size.
        if cls == 'UnionOperation' and not union_mesh and not real_mesh_id:
            real_mesh_id = _rbxassetid_num(props.get('Content'))

        # The part's PivotOffset (an offset of the rotation point for GetPivot/PivotTo —
        # for example a door hinge): [x, y, z, R00..R22]; None if identity.
        pivot_offset = None
        _po = props.get('PivotOffset')
        if isinstance(_po, dict):
            _pp = list(get_pos(_po))
            _pr = [float(v) for v in get_rot_matrix(_po)]
            if (any(abs(v) > 1e-6 for v in _pp)
                    or any(abs(x - y) > 1e-6 for x, y in zip(_pr, [1, 0, 0, 0, 1, 0, 0, 0, 1]))):
                pivot_offset = _pp + _pr

        # The part lies in a container that doesn't exist in the world (ServerStorage/ReplicatedStorage — a template storage): the client doesn't draw it
        # and gives it no physics, but keeps the data — Clone() builds the copy's mesh in Workspace from it.
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
            'disabled': bool(props.get('Disabled')) if cls in ('Seat', 'VehicleSeat') else False,
            'trussStyle': (props.get('Style') if isinstance(props.get('Style'), int) and not isinstance(props.get('Style'), bool) else 0) if cls == 'TrussPart' else None,
        })

    _scene_build_cache.update(parsed_id=pid, objs=objs)
    return objs


def make_scene_objects(cx=None, cy=None, cz=None, r=None, limit=None, chunk=False, points=None):
    parsed = state['parsed']
    if not parsed:
        return [], 0
    # nw parts (ServerStorage/ReplicatedStorage/StarterPack) aren't drawn and aren't counted in limit/total
    objs = [o for o in build_all_scene_objects() if not o.get('nw')]

    if chunk:
        objs = chunk_large_objects(objs)

    # Several points can be passed (not only cx,cy,cz) — the object's distance
    # is taken as the minimum to any of them. Used by the second,
    # points-based path in api_scene (the editor's ordinary scene load);
    # the main Play streaming now goes through the chunk-based
    # gather_objects_in_radius above and doesn't use this path.
    query_points = list(points) if points else (
        [(cx, cy, cz)] if cx is not None and cy is not None and cz is not None else []
    )

    if query_points:
        def dist_to_nearest_point(o):
            # The distance to the center understates the priority of large objects:
            # a long floor slab can have its center a hundred studs from
            # the player, while its edge is right under the feet. We approximate with a lower
            # bound of the distance to the object — we subtract the half-diagonal of
            # its dimensions (the radius of the circumscribed sphere) from the distance to
            # the center. The estimate is conservative (it may slightly understate
            # the real distance to the OBB), but is guaranteed not to discard
            # an object that is actually nearby.
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

# ============ COLLABORATION (2+ people on one map) ============
# There is one server and it holds the single map state (state['parsed']); the second
# person opens the same address (http://<host-ip>:PORT) and enters the room code.
# All edits go through the same endpoints as before — each of them is wrapped in
# @_collab_track(...): under a shared lock the decorator takes a «before» snapshot, lets the
# edit through and writes an operation with the inverse action (undo) to the log — hence
# the «who changed what» history and rollback to a revision. The client (collab.js) long-polls
# /api/collab/poll every few seconds and re-reads the tree/scene.
# Off by default: until the host presses «Start» (/api/collab/start),
# the decorator writes nothing and the editor's behavior is as before. While the room
# is on, non-local write requests require the X-Collab-Token header.
import copy as _copy
import functools as _functools
import secrets as _secrets
import socket as _socket
import threading as _threading

COLLAB_MAX_OPS = 2000          # log length; old revisions drop out of the history
COLLAB_MAX_UNDO_BYTES = 65536  # We no longer snapshot a script's Source (such an edit isn't rolled back)
COLLAB_PEER_TTL = 15           # seconds without a poll — the person is considered gone

_collab = {
    'on': False, 'token': None, 'rev': 0, 'base': 0,
    'ops': [],      # {rev,t,by,byId,type,ref,name,cls,prop,n,undo,redo}
    'peers': {},    # id -> {name, seen, sel}
    'pv': 0,        # «presence» version: changes when someone joined/changed their selected object
}
# One lock for everything: a map edit + a log write are atomic (while api_add without
# a lock could hand the same ref to two simultaneous PUTs); the Condition on
# it wakes the long-polls.
_collab_cond = _threading.Condition(_threading.RLock())
_MISSING = object()


def _collab_is_local():
    return request.remote_addr in ('127.0.0.1', '::1', '::ffff:127.0.0.1')


def _collab_who():
    cid = (request.headers.get('X-Collab-Id') or '')[:40]
    # the name arrives in a header via encodeURIComponent (Cyrillic isn't allowed in headers)
    name = _urlparse.unquote(request.headers.get('X-Collab-Name') or '').strip()[:32]
    if not name:
        name = 'host' if _collab_is_local() else (request.remote_addr or '?')
    return cid, name


def _collab_push(typ, ref=None, name='', cls='', prop='', n=1, undo=None, redo=None,
                 who=None, remote=False):
    """Appends an operation to the log (call under _collab_cond). remote=True — the edit
    came through git from another author (who): we write it to our own log, but don't send it back."""
    c = _collab
    cid, me = _collab_who()
    if remote:
        cid, who = '', who or '?'
    else:
        who = me
    last = c['ops'][-1] if c['ops'] else None
    # consecutive edits of the SAME property by one person within 5 s — one entry
    # (an input field / script autosave): undo stays the very first old value
    if (typ == 'set' and not remote and last and last['type'] == 'set' and cid and last['byId'] == cid
            and last['ref'] == ref and last['prop'] == prop and time.time() - last['t'] < 5):
        c['rev'] += 1
        last.update(rev=c['rev'], t=time.time(), redo=redo)
        _cg_pending_add(last)
        _collab_cond.notify_all()
        return
    c['rev'] += 1
    op = {'rev': c['rev'], 't': time.time(), 'by': who, 'byId': cid,
          'type': typ, 'ref': ref, 'name': name, 'cls': cls,
          'prop': prop, 'n': n, 'undo': undo, 'redo': redo}
    c['ops'].append(op)
    if not remote:
        _cg_pending_add(op)
    if len(c['ops']) > COLLAB_MAX_OPS:
        drop = len(c['ops']) - COLLAB_MAX_OPS
        c['base'] = c['ops'][drop - 1]['rev']
        del c['ops'][:drop]
    _collab_cond.notify_all()


def _collab_reset(typ='reload'):
    """Another map was opened/created: the old map's history is meaningless."""
    c = _collab
    c['ops'] = []
    _collab_push(typ)
    c['base'] = c['rev']


# --- primitive actions that undo/redo are assembled from ---
# ('props', ref, {prop: value | _MISSING})  — restore property values
# ('put',   ref, cls, parent, props)           — create/restore an object
# ('rm',    ref)                               — delete an object
# ('parent', ref, parent)                      — change the parent

def _collab_apply(parsed, acts):
    for a in acts:
        k = a[0]
        if k == 'props':
            if a[1] not in parsed['referent_to_class']:
                continue
            p = parsed['props'].setdefault(a[1], {})
            for prop, val in a[2].items():
                if val is _MISSING:
                    p.pop(prop, None)
                else:
                    p[prop] = _copy.deepcopy(val)
        elif k == 'put':
            parsed['referent_to_class'][a[1]] = a[2]
            parsed['parent_map'][a[1]] = a[3]
            parsed['props'][a[1]] = _copy.deepcopy(a[4])
        elif k == 'rm':
            for d in ('referent_to_class', 'parent_map', 'props'):
                parsed[d].pop(a[1], None)
        elif k == 'parent':
            if a[1] in parsed['referent_to_class']:
                parsed['parent_map'][a[1]] = a[2]
    parsed['_modified'] = True
    bump_scene_version()


def _collab_obj(parsed, ref):
    """(class, name) of an object for the feed label."""
    cls = parsed['referent_to_class'].get(ref, '')
    return cls, str(parsed['props'].get(ref, {}).get('Name', ''))[:60]


def _collab_snapshot_props(parsed, ref, names):
    p = parsed['props'].get(ref, {})
    return {k: (_copy.deepcopy(p[k]) if k in p else _MISSING) for k in names}


def _collab_track(kind):
    """Decorator for editing endpoints. kind: set | add | del | move | reload | import."""
    def deco(fn):
        @_functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with _collab_cond:
                if not (_collab['on'] or _cg['on']):
                    return fn(*args, **kwargs)
                if kind == 'reload' and _collab['on'] and not _collab_is_local():
                    return jsonify({'ok': False, 'error': _alang('Карту открывает только хост', 'Only the host can open a map')}), 403
                parsed = state['parsed']
                body = request.get_json(silent=True) if request.is_json else None
                body = body if isinstance(body, dict) else {}
                pre = None
                try:
                    if parsed and kind == 'set' and body.get('prop') is not None:
                        ref, prop = kwargs.get('ref'), body.get('prop')
                        names = [prop] + (['CFrame'] if prop in ('Position', 'Rotation') else [])
                        pre = _collab_snapshot_props(parsed, ref, names)
                        big = prop == 'Source' and len(str(pre.get('Source'))) > COLLAB_MAX_UNDO_BYTES
                        pre = None if big else (ref, prop, pre)
                    elif parsed and kind == 'del':
                        ref = kwargs.get('ref')
                        if ref in parsed['referent_to_class']:
                            cls, nm = _collab_obj(parsed, ref)
                            pre = (ref, cls, nm, parsed['parent_map'].get(ref, -1),
                                   _copy.deepcopy(parsed['props'].get(ref, {})))
                    elif parsed and kind == 'move':
                        pm = parsed['parent_map']
                        pre = {r: pm.get(r, -1) for r in (body.get('refs') or [])
                               if isinstance(r, int)}
                except Exception:   # a snapshot must not break the edit itself
                    traceback.print_exc()
                    pre = None
                rv = fn(*args, **kwargs)
                try:
                    resp = flask_app.make_response(rv)
                    js = resp.get_json(silent=True) if resp.status_code == 200 else None
                    if not (isinstance(js, dict) and js.get('ok')):
                        return rv
                    parsed = state['parsed']
                    if kind in ('reload',):
                        if _cg['on']:
                            _cg_disable(_alang('Открыта другая карта — git отключён, подключите заново', 'Another map is open — git is disconnected, connect again'))
                        _collab_reset('reload')
                    elif kind == 'import':
                        _collab_push('import', n=int(js.get('count') or 0))
                    elif kind == 'add':
                        ref = js.get('ref')
                        cls, nm = _collab_obj(parsed, ref)
                        snap = (ref, cls, parsed['parent_map'].get(ref, -1),
                                _copy.deepcopy(parsed['props'].get(ref, {})))
                        _collab_push('add', ref, nm, cls,
                                     undo=[('rm', ref)], redo=[('put',) + snap])
                    elif kind == 'del' and pre:
                        ref, cls, nm, par, props = pre
                        _collab_push('del', ref, nm, cls,
                                     undo=[('put', ref, cls, par, props)], redo=[('rm', ref)])
                    elif kind == 'set' and pre:
                        ref, prop, old = pre
                        cls, nm = _collab_obj(parsed, ref)
                        new = _collab_snapshot_props(parsed, ref, list(old.keys()))
                        if ref not in parsed['referent_to_class'] or new == old:
                            return rv
                        _collab_push('set', ref, nm, cls, prop=prop or '',
                                     undo=[('props', ref, old)], redo=[('props', ref, new)])
                    elif kind == 'move' and pre:
                        moved = [r for r in (js.get('moved') or []) if r in pre]
                        if moved:
                            par = parsed['parent_map']
                            cls, nm = _collab_obj(parsed, moved[0])
                            _collab_push('move', moved[0], nm, cls, n=len(moved),
                                         undo=[('parent', r, pre[r]) for r in moved],
                                         redo=[('parent', r, par.get(r, -1)) for r in moved])
                except Exception:
                    traceback.print_exc()
                return rv
        return wrapper
    return deco


@flask_app.before_request
def _collab_gate():
    """While the room is on: writing and /api/collab/* — only locally or with a code."""
    c = _collab
    if not c['on'] or not request.path.startswith('/api/'):
        return None
    is_collab = request.path.startswith('/api/collab/')
    if request.method in ('GET', 'HEAD', 'OPTIONS') and not (
            is_collab and request.path != '/api/collab/status'):
        return None
    if _collab_is_local():
        return None
    tok = request.headers.get('X-Collab-Token') or ''
    if c['token'] and _secrets.compare_digest(tok, c['token']):
        return None
    return jsonify({'ok': False, 'error': _alang('Нужен код комнаты', 'A room code is required'), 'needToken': True}), 403


def _collab_public(op):
    return {k: op[k] for k in ('rev', 't', 'by', 'byId', 'type', 'ref', 'name', 'cls', 'prop', 'n')}


def _collab_peers():
    now = time.time()
    return [{'id': i, 'name': p['name'], 'sel': p['sel']}
            for i, p in _collab['peers'].items() if now - p['seen'] < COLLAB_PEER_TTL]


def _collab_touch():
    cid, who = _collab_who()
    if cid:
        sel = request.args.get('sel', type=int)
        old = _collab['peers'].get(cid)
        _collab['peers'][cid] = {'name': who, 'seen': time.time(), 'sel': sel}
        if old is None or old['sel'] != sel or old['name'] != who:
            _collab['pv'] += 1
            _collab_cond.notify_all()       # wake other people's polls — let them see it right away


def _collab_lan_urls():
    """ADDRESSES of THIS device on all networks. A guest needs the one from their network: at home it is
    usually 192.168.x.x, while 10.x is often a VPN/virtual adapter or a corporate network."""
    ips = set()
    # the default-route interface and one «probe» address from each private network:
    # no packet is sent — the OS just picks an interface (this is how virtual adapters are found too)
    for probe in ('8.8.8.8', '192.168.255.255', '172.16.255.255', '10.255.255.255'):
        try:
            s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
            s.connect((probe, 1))
            ips.add(s.getsockname()[0])
            s.close()
        except OSError:
            pass
    try:
        ips.update(i[4][0] for i in _socket.getaddrinfo(_socket.gethostname(), None, _socket.AF_INET))
    except OSError:
        pass
    ips = {ip for ip in ips if not ip.startswith(('127.', '169.254.', '0.'))}

    def rank(ip):
        if ip.startswith('192.168.'):
            return 0
        if _re.match(r'172\.(1[6-9]|2\d|3[01])\.', ip):
            return 1
        return 2 if ip.startswith('10.') else 3
    return ['http://%s:%d' % (ip, PORT) for ip in sorted(ips, key=lambda x: (rank(x), x))]


@flask_app.route('/api/collab/status')
def api_collab_status():
    c = _collab
    with _collab_cond:
        out = {'ok': True, 'on': c['on'], 'rev': c['rev'], 'base': c['base'],
               'peers': _collab_peers(), 'local': _collab_is_local()}
        if c['on'] and _collab_is_local():       # the code and addresses are seen only by the host
            out['token'] = c['token']
            out['urls'] = _collab_lan_urls()
        return jsonify(out)


@flask_app.route('/api/collab/start', methods=['POST'])
def api_collab_start():
    if not _collab_is_local():
        return jsonify({'ok': False, 'error': _alang('Комнату запускает только хост', 'Only the host can start the room')}), 403
    with _collab_cond:
        if not _collab['on']:
            _collab['on'] = True
            # without look-alike characters (0/O, 1/I) — the code is dictated by voice
            _collab['token'] = ''.join(_secrets.choice('ABCDEFGHJKMNPQRSTUVWXYZ23456789') for _ in range(6))
            _collab_reset('reload')
        _collab_cond.notify_all()
    return api_collab_status()


@flask_app.route('/api/collab/stop', methods=['POST'])
def api_collab_stop():
    if not _collab_is_local():
        return jsonify({'ok': False, 'error': _alang('Комнату закрывает только хост', 'Only the host can close the room')}), 403
    with _collab_cond:
        _collab.update({'on': False, 'token': None, 'ops': [], 'peers': {}})
        _collab['base'] = _collab['rev']
        _collab_cond.notify_all()
    return jsonify({'ok': True})


@flask_app.route('/api/collab/join', methods=['POST'])
def api_collab_join():
    with _collab_cond:
        if not _collab['on']:
            return jsonify({'ok': False, 'error': _alang('Комната не запущена', 'The room is not running')}), 404
        _collab_touch()
        return jsonify({'ok': True, 'rev': _collab['rev'], 'peers': _collab_peers()})


@flask_app.route('/api/collab/poll')
def api_collab_poll():
    """Long-poll: waits for a revision newer than since (up to wait seconds). If since is greater than
    the current revision (the server was restarted) — reset=True, the client re-reads everything."""
    since = request.args.get('since', 0, type=int)
    wait = min(max(request.args.get('wait', 15, type=float), 0), 25)
    deadline = time.time() + wait
    with _collab_cond:
        _collab_touch()
        pv0 = _collab['pv']
        while _collab['on'] and _collab['rev'] <= since and _collab['pv'] == pv0:
            left = deadline - time.time()
            if left <= 0:
                break
            _collab_cond.wait(min(left, 5))
            _collab_touch()
        c = _collab
        if not c['on']:
            return jsonify({'ok': True, 'on': False, 'rev': c['rev'], 'ops': [], 'peers': []})
        reset = since > c['rev'] or since < c['base']
        ops = [] if reset else [_collab_public(o) for o in c['ops'] if o['rev'] > since]
        return jsonify({'ok': True, 'on': True, 'rev': c['rev'], 'reset': reset,
                        'ops': ops, 'peers': _collab_peers()})


@flask_app.route('/api/collab/ping')
def api_collab_ping():
    """A light presence mark: the client calls it when the selected object changes."""
    with _collab_cond:
        if _collab['on']:
            _collab_touch()
    return jsonify({'ok': True})


@flask_app.route('/api/collab/history')
def api_collab_history():
    limit = min(request.args.get('limit', 100, type=int), COLLAB_MAX_OPS)
    with _collab_cond:
        ops = _collab['ops'][-limit:][::-1]       # newest on top
        return jsonify({'ok': True, 'rev': _collab['rev'], 'base': _collab['base'],
                        'ops': [dict(_collab_public(o), undoable=o['undo'] is not None) for o in ops]})


@flask_app.route('/api/collab/revert', methods=['POST'])
def api_collab_revert():
    """Rolls the map back to the state right AFTER revision `rev`: undoes all later
    operations from newest to oldest. History is not rewritten — the rollback itself becomes
    an operation (it can be rolled back too)."""
    body = request.get_json(silent=True) or {}
    try:
        target = int(body.get('rev'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': _alang('Нужен rev', 'rev is required')}), 400
    with _collab_cond:
        c, parsed = _collab, state['parsed']
        if not c['on'] or not parsed:
            return jsonify({'ok': False, 'error': _alang('Нет открытой комнаты/карты', 'No open room/map')}), 400
        if target < c['base'] or target > c['rev']:
            return jsonify({'ok': False, 'error': _alang('Эта ревизия уже выпала из истории', 'This revision has already dropped out of the history')}), 400
        later = [o for o in c['ops'] if o['rev'] > target]
        if not later:
            return jsonify({'ok': True, 'reverted': 0, 'rev': c['rev']})
        bad = [o['rev'] for o in later if o['undo'] is None]
        if bad:
            return jsonify({'ok': False, 'error': _alang('Не откатываются операции: %s', 'These operations cannot be reverted: %s') % bad[:5]}), 409
        undo_all = [a for o in reversed(later) for a in o['undo']]
        redo_all = [a for o in later for a in o['redo']]
        _collab_apply(parsed, undo_all)
        _collab_push('revert', n=len(later), prop=str(target), undo=redo_all, redo=undo_all)
        return jsonify({'ok': True, 'reverted': len(later), 'rev': c['rev']})


# ---------- fallback: edits through a git server ----------
# When there is no direct connection (different networks, Wi-Fi client isolation, closed
# ports), edits travel through any git repository. The repository holds base.rbxl
# (the original map) and ops/<author>.jsonl — the edit log of EACH author in their
# own file, so git never sees a merge conflict. «Synchronize»
# = append own new edits → fetch+rebase → apply others' → push.
# New objects of two people can get the same ref (api_add takes max+1),
# so in the file objects are named by canonical names: a number — an object of the original
# map, [author, ref] — one created later; everyone maps them to their own refs.
import json as _json
import re as _re
import shutil as _shutil
import subprocess as _subprocess

_CG_DIR = os.environ.get('RSW_COLLAB_GIT_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'collab-git')
_cg = {'on': False, 'sync': None, 'err': '', 'last': ''}


def _cg_path(*p):
    return os.path.join(_CG_DIR, *p)


def _cg_save():
    d = dict(_cg['sync'])
    d['mine'] = sorted(d['mine'])
    with open(_cg_path('.git', 'rsw-sync.json'), 'w', encoding='utf-8') as f:
        _json.dump(d, f, ensure_ascii=False)


def _cg_restore():
    """After the editor restarts we pick up the already connected repository."""
    try:
        with open(_cg_path('.git', 'rsw-sync.json'), encoding='utf-8') as f:
            d = _json.load(f)
        d['mine'] = set(d.get('mine', []))
        _cg['sync'], _cg['on'] = d, True
    except (OSError, ValueError):
        pass


def _cg_disable(why=''):
    _cg['on'], _cg['err'] = False, why
    try:
        os.remove(_cg_path('.git', 'rsw-sync.json'))
    except OSError:
        pass


def _cg_git(*args, cwd=None, timeout=90):
    try:
        p = _subprocess.run(['git'] + list(args), cwd=cwd or _CG_DIR, capture_output=True,
                            text=True, timeout=timeout,
                            env=dict(os.environ, GIT_TERMINAL_PROMPT='0', LC_ALL='C'))
    except FileNotFoundError:
        return 127, _alang('git не найден: установите git и перезапустите редактор', 'git not found: install git and restart the editor')
    except _subprocess.TimeoutExpired:
        return 124, _alang('git: нет ответа (сеть или запрос пароля). Настройте вход заранее: SSH-ключ или токен', 'git: no response (network or a password prompt). Set up sign-in beforehand: an SSH key or a token')
    return p.returncode, ((p.stdout or '') + (p.stderr or '')).strip()


# --- JSON representation of actions (tuples/«no property» don't live in JSON) ---
def _cg_enc(v):
    if v is _MISSING:
        return {'__m': 1}
    if isinstance(v, (bytes, bytearray)):          # binary properties (Terrain, attributes, etc.)
        return {'__b': _b64.b64encode(bytes(v)).decode('ascii')}
    if isinstance(v, tuple):
        return {'__t': [_cg_enc(x) for x in v]}
    if isinstance(v, list):
        return [_cg_enc(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _cg_enc(x) for k, x in v.items()}
    return v


def _cg_dec(v):
    if isinstance(v, dict):
        if '__m' in v:
            return _MISSING
        if '__b' in v:
            return _b64.b64decode(v['__b'])
        if '__t' in v:
            return tuple(_cg_dec(x) for x in v['__t'])
        return {k: _cg_dec(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_cg_dec(x) for x in v]
    return v


def _cg_acts_json(acts):
    out = []
    for a in acts:
        if a[0] == 'props':
            out.append(['props', a[1], {p: _cg_enc(v) for p, v in a[2].items()}])
        elif a[0] == 'put':
            out.append(['put', a[1], a[2], a[3], _cg_enc(a[4])])
        else:
            out.append(list(a))
    return out


def _cg_pending_add(op):
    """Each own edit is appended to disk immediately — it survives a restart before sending."""
    if not _cg['on'] or op['type'] not in ('set', 'add', 'del', 'move', 'revert', 'import'):
        return
    rec = {k: op[k] for k in ('t', 'type', 'name', 'cls', 'prop', 'n')}
    rec['acts'] = _cg_acts_json(op['redo']) if op.get('redo') else None
    try:
        with open(_cg_path('.git', 'rsw-pending.jsonl'), 'a', encoding='utf-8') as f:
            f.write(_json.dumps(rec, ensure_ascii=False) + '\n')
    except OSError:
        traceback.print_exc()


def _cg_pending_count():
    try:
        with open(_cg_path('.git', 'rsw-pending.jsonl'), encoding='utf-8') as f:
            return sum(1 for l in f if l.strip())
    except OSError:
        return 0


# --- refs: local <-> canonical ---
def _cg_cref(s, ref):
    if not isinstance(ref, int) or ref < 0:
        return ref
    if str(ref) in s['l2c']:
        return s['l2c'][str(ref)]
    if ref in s['mine']:
        return [s['slug'], ref]
    return ref


def _cg_lref(s, parsed, c, create=False):
    if isinstance(c, list):
        slug, r = c
        if slug == s['slug']:
            return r
        key = '%s:%s' % (slug, r)
        if key in s['c2l']:
            return s['c2l'][key]
        if create:
            new = max(parsed['referent_to_class'], default=0) + 1
            s['c2l'][key] = new
            s['l2c'][str(new)] = [slug, r]
            return new
        return None
    return c


def _cg_canon_act(s, a):
    k = a[0]
    if k == 'props':
        return ['props', _cg_cref(s, a[1]), a[2]]
    if k == 'put':
        return ['put', _cg_cref(s, a[1]), a[2], _cg_cref(s, a[3]), a[4]]
    if k == 'rm':
        return ['rm', _cg_cref(s, a[1])]
    return ['parent', _cg_cref(s, a[1]), _cg_cref(s, a[2])]


def _cg_local_act(s, parsed, a):
    """An action from a file -> an internal tuple with local refs (None — we don't have the object)."""
    k = a[0]
    if k == 'put':
        ref = _cg_lref(s, parsed, a[1], create=True)
        par = _cg_lref(s, parsed, a[3])
        return ('put', ref, a[2], -1 if par is None else par, _cg_dec(a[4]))
    ref = _cg_lref(s, parsed, a[1])
    if ref is None or ref not in parsed['referent_to_class']:
        return None
    if k == 'props':
        return ('props', ref, _cg_dec(a[2]))
    if k == 'rm':
        return ('rm', ref)
    par = _cg_lref(s, parsed, a[2])
    return ('parent', ref, -1 if par is None else par)


def _collab_inverse(parsed, a):
    """The inverse action for a single action — taken BEFORE it is applied."""
    k, ref = a[0], a[1]
    r2c = parsed['referent_to_class']
    if k == 'props':
        p = parsed['props'].get(ref, {})
        return [('props', ref, {n: (_copy.deepcopy(p[n]) if n in p else _MISSING) for n in a[2]})]
    if k in ('put', 'rm') and ref in r2c:
        return [('put', ref, r2c[ref], parsed['parent_map'].get(ref, -1),
                 _copy.deepcopy(parsed['props'].get(ref, {})))]
    if k == 'put':
        return [('rm', ref)]
    if k == 'parent':
        return [('parent', ref, parsed['parent_map'].get(ref, -1))]
    return []


def _cg_mask(u):
    """A token/password inside an https address (https://TOKEN@… or user:pass@…) is never given out."""
    return _re.sub(r'(https?://)[^/@\s]+@', r'\1***@', u or '')


def _cg_lww(s, a, t, who, local=False):
    """«Last one wins» for props/parent: for each (object, property) pair we remember
    (time, author) of the last applied edit. The (time, author) order is common to everyone,
    so with simultaneous edits everyone converges on one value. local=True — only
    remember our own edit. Returns the action (possibly without stale properties) or None."""
    if a[0] not in ('props', 'parent'):
        return a
    stamp, st, ref = s.setdefault('stamp', {}), (t, who), _json.dumps(a[1])
    if a[0] == 'parent':
        k = ref + '|@parent'
        if not local and tuple(stamp.get(k) or (0, '')) > st:
            return None
        stamp[k] = list(st)
        return a
    keep = {}
    for p, v in a[2].items():
        k = ref + '|' + p
        if not local and tuple(stamp.get(k) or (0, '')) > st:
            continue
        stamp[k] = list(st)
        keep[p] = v
    return ['props', a[1], keep] if keep else None


def _cg_export():
    """Own new edits -> ops/<me>.jsonl (with canonical refs). Returns how many were written."""
    s, pf = _cg['sync'], _cg_path('.git', 'rsw-pending.jsonl')
    if not os.path.exists(pf):
        return 0
    with open(pf, encoding='utf-8') as f:
        raw = [_json.loads(l) for l in f if l.strip()]
    out = _cg_path('ops', s['slug'] + '.jsonl')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        with open(out, encoding='utf-8') as f:
            seq = sum(1 for l in f if l.strip())
    except OSError:
        seq = 0
    with open(out, 'a', encoding='utf-8') as f:
        for o in raw:
            acts = o.get('acts')
            if o['type'] == 'add' and acts:
                s['mine'].add(acts[0][1])          # from now on the object is «mine»
            if acts is not None:
                acts = [_cg_canon_act(s, a) for a in acts]
                for a in acts:
                    _cg_lww(s, a, o['t'], s['slug'], local=True)
            f.write(_json.dumps({'seq': seq, 't': o['t'], 'by': s['name'], 'type': o['type'],
                                 'name': o['name'], 'cls': o['cls'], 'prop': o['prop'],
                                 'n': o['n'], 'acts': acts}, ensure_ascii=False) + '\n')
            seq += 1
    os.remove(pf)
    _cg_save()
    return len(raw)


def _cg_apply_remote():
    """Applies other people's edits from ops/*.jsonl that we haven't seen yet. -> (applied, skipped)."""
    s, parsed = _cg['sync'], state['parsed']
    ops_dir = _cg_path('ops')
    done = skipped = 0
    if not parsed or not os.path.isdir(ops_dir):
        return 0, 0
    batch, newcur = [], {}
    for fn in sorted(os.listdir(ops_dir)):
        slug = fn[:-6]
        if not fn.endswith('.jsonl') or slug == s['slug']:
            continue
        with open(os.path.join(ops_dir, fn), encoding='utf-8') as f:
            lines = [l for l in f.read().split('\n') if l.strip()]
        cur = s['cursor'].get(slug, 0)
        for i, l in enumerate(lines[cur:], cur):
            try:
                o = _json.loads(l)
            except ValueError:
                break                              # an unfinished line — we'll pick it up next time
            batch.append((o.get('t', 0), slug, i, o))
            cur = i + 1
        newcur[slug] = cur
    # edits of different authors — in time order: so an object (put) comes before the edits that refer to it
    batch.sort(key=lambda x: (x[0], x[1], x[2]))
    for t, slug, _i, o in batch:
        if o.get('acts') is None:
            skipped += 1                           # import etc.: can't be reproduced from a file
            continue
        undo, redo, first = [], [], None
        for a in o['acts']:
            a = _cg_lww(s, a, t, slug)
            if a is None:
                continue                           # we already have a fresher edit
            la = _cg_local_act(s, parsed, a)
            if la is None:
                continue
            undo.append(_collab_inverse(parsed, la))
            _collab_apply(parsed, [la])
            redo.append(la)
            first = la[1] if first is None else first
        if redo:
            _collab_push(o['type'], first, o.get('name', ''), o.get('cls', ''), o.get('prop', ''),
                         o.get('n', 1), undo=[x for u in reversed(undo) for x in u], redo=redo,
                         who=o.get('by', slug), remote=True)
            done += 1
    s['cursor'].update(newcur)
    _cg_save()
    return done, skipped


def _cg_branch():
    rc, out = _cg_git('rev-parse', '--abbrev-ref', 'HEAD')
    return out if rc == 0 and out != 'HEAD' else 'main'


def _cg_fail(msg, code=400):
    msg = _cg_mask(msg)
    _cg['err'] = msg
    return jsonify({'ok': False, 'error': msg}), code


def _cg_host_only():
    if not _collab_is_local():
        return jsonify({'ok': False, 'error': _alang('Git-синхронизацию настраивает только хост', 'Only the host configures git synchronization')}), 403
    return None


# --- transport without git: directly through the GitHub API (for the APK, which has no git binary) ---
# The same files (meta.json, base.rbxl, ops/<author>.jsonl), only instead of clone/push/fetch —
# requests to the repository's REST API. A token with access to ONE repository is needed
# (fine-grained, Contents: Read and write); the repository must not be empty (at least a README).
import base64 as _b64
import hashlib as _hashlib
import urllib.error as _urlerr
import urllib.request as _urlreq

_GH_API = os.environ.get('RSW_GH_API') or 'https://api.github.com'


def _gh_parse(remote):
    """-> (owner, repository, token-from-address) or None if this is not a GitHub address."""
    m = (_re.match(r'^(?:https?://(?:([^/@\s]+)@)?github\.com/|git@github\.com:|ssh://git@github\.com/|github\.com/)'
                   r'([\w.-]+)/([\w.-]+?)(?:\.git)?/?$', remote.strip())
         or _re.match(r'^()([\w.-]+)/([\w.-]+?)(?:\.git)?$', remote.strip()))
    if not m:
        return None
    tok = (m.group(1) or '').split(':')[-1]
    return m.group(2), m.group(3), tok


def _gh_req(method, path, token, body=None, raw=False, timeout=60):
    """-> (http code, JSON | bytes | error text). Code 0 — no connection."""
    data = _json.dumps(body).encode('utf-8') if body is not None else None
    req = _urlreq.Request(_GH_API + path, data=data, method=method)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Accept', 'application/vnd.github.raw+json' if raw else 'application/vnd.github+json')
    req.add_header('X-GitHub-Api-Version', '2022-11-28')
    req.add_header('User-Agent', 'roblox-studio-web')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    try:
        with _urlreq.urlopen(req, timeout=timeout) as r:
            payload = r.read()
            if raw:
                return r.status, payload
            return r.status, (_json.loads(payload) if payload else {})
    except _urlerr.HTTPError as e:
        try:
            msg = _json.loads(e.read()).get('message', '')
        except Exception:
            msg = ''
        return e.code, msg or str(e)
    except (_urlerr.URLError, OSError) as e:
        return 0, _alang('нет связи с GitHub (%s)', 'no connection to GitHub (%s)') % e


def _gh_err(st, msg):
    if st == 0:
        return msg
    if st == 401:
        return _alang('GitHub не принял токен (401): он неверный или истёк', 'GitHub rejected the token (401): it is invalid or expired')
    if st in (403, 404):
        return (_alang('GitHub %d: нет доступа к репозиторию. Проверьте имя и что у токена выбран именно этот '
                'репозиторий с правом Contents: Read and write (%s)', 'GitHub %d: no access to the repository. Check the name and that the token has exactly this repository selected with Contents: Read and write (%s)') % (st, msg))
    if st == 409 and 'empty' in str(msg).lower():
        return _alang('Репозиторий пустой: создайте его с файлом README (Add a README file) и повторите', 'The repository is empty: create it with a README file (Add a README file) and try again')
    return 'GitHub %d: %s' % (st, msg)


def _gh_put(token, g, path, data, message, sha=None):
    body = {'message': message, 'content': _b64.b64encode(data).decode('ascii'), 'branch': g['branch']}
    if sha:
        body['sha'] = sha
    return _gh_req('PUT', '/repos/%s/%s/contents/%s' % (g['owner'], g['repo'], path), token,
                   body=body, timeout=180)


def _gh_get(token, g, path, raw=False):
    return _gh_req('GET', '/repos/%s/%s/contents/%s?ref=%s' % (g['owner'], g['repo'], path, g['branch']),
                   token, raw=raw, timeout=120)


def _cg_setup_api(owner, repo, token, name):
    if not _re.fullmatch(r'[A-Za-z0-9_\-]{10,255}', token):
        return _cg_fail(_alang('Токен выглядит неверно: вставьте его целиком, без пробелов', 'The token looks wrong: paste it in full, without spaces'))
    with _collab_cond:
        st, info = _gh_req('GET', '/repos/%s/%s' % (owner, repo), token)
        if st != 200:
            return _cg_fail(_gh_err(st, info))
        if (info.get('permissions') or {}).get('push') is False:
            return _cg_fail(_alang('У токена нет права записи: нужен Contents: Read and write', 'The token has no write permission: Contents: Read and write is required'))
        g = {'owner': owner, 'repo': repo, 'branch': info.get('default_branch') or 'main',
             'sha': {}, 'mine': ''}
        st, meta = _gh_get(token, g, 'meta.json')
        if st not in (200, 404):
            return _cg_fail(_gh_err(st, meta))
        joining = st == 200
        slug = _re.sub(r'[^A-Za-z0-9_-]+', '_', name)[:20] + '-' + _secrets.token_hex(2)
        if joining:
            st, base = _gh_get(token, g, 'base.rbxl', raw=True)
            if st != 200:
                return _cg_fail(_alang('Не удалось скачать base.rbxl: ', 'Could not download base.rbxl: ') + _gh_err(st, base))
        else:
            parsed, src = state['parsed'], state['file_path']
            if not parsed or not src or not os.path.isfile(src):
                return _cg_fail(_alang('Сначала откройте карту (с файла на диске)', 'Open a map first (from a file on disk)'))
            if parsed.get('_modified'):
                return _cg_fail(_alang('В карте есть несохранённые изменения: сохраните её (Save) и повторите', 'The map has unsaved changes: save it (Save) and try again'))
        if os.path.exists(_CG_DIR):                # we don't delete the previous folder — we move it aside
            os.rename(_CG_DIR, _CG_DIR + '.old-%d' % int(time.time()))
        # an empty .git is needed only as a place for sync service files (rsw-sync/pending)
        os.makedirs(_cg_path('.git'))
        os.makedirs(_cg_path('ops'))
        if joining:
            work = _cg_path('work.rbxl')
            with open(work, 'wb') as f:
                f.write(base)
            try:
                parsed = parse_rbxl(work)
            except Exception as e:
                return _cg_fail(_alang('Не удалось открыть base.rbxl: %s', 'Could not open base.rbxl: %s') % e)
            state['parsed'], state['file_path'] = parsed, work
            _recents_add_file(work, name='work.rbxl (git)')
            if _collab['on']:
                _collab_reset('reload')
            bump_scene_version()
        else:
            with open(src, 'rb') as f:
                data = f.read()
            for path, blob in (('base.rbxl', data),
                               ('meta.json', _json.dumps({'format': 1, 'base': 'base.rbxl',
                                                          'created_by': name}).encode('utf-8'))):
                st, r = _gh_put(token, g, path, blob, _alang('Начало совместной работы: ', 'Collaboration started: ') + path)
                if st not in (200, 201):
                    return _cg_fail(_gh_err(st, r))
        _cg['sync'] = {'slug': slug, 'name': name, 'remote': 'github.com/%s/%s' % (owner, repo),
                       'mode': 'api', 'token': token, 'gh': g, 'cursor': {},
                       'mine': set(), 'c2l': {}, 'l2c': {}}
        _cg['on'], _cg['err'] = True, ''
        _cg_save()
        applied = skipped = 0
        if joining:
            bad = _cg_fetch_api(_cg['sync'])
            if bad:
                _cg_save()
                return _cg_fail(bad)
            applied, skipped = _cg_apply_remote()
        _cg['last'] = time.strftime('%H:%M:%S')
        _cg_save()
        return jsonify({'ok': True, 'joined': joining, 'applied': applied, 'skipped': skipped})


def _cg_fetch_api(s):
    """Downloads other people's ops files that changed since last time. -> error text or None."""
    g, token = s['gh'], s['token']
    mine = 'ops/%s.jsonl' % s['slug']
    st, lst = _gh_get(token, g, 'ops')
    if st == 404:
        lst = []                                            # nobody has sent anything yet
    elif st != 200 or not isinstance(lst, list):
        return _gh_err(st, lst)
    for e in lst:
        key = 'ops/' + e['name']
        if not e['name'].endswith('.jsonl') or key == mine or g['sha'].get(key) == e['sha']:
            continue
        st, raw = _gh_get(token, g, key, raw=True)
        if st != 200:
            return _gh_err(st, raw)
        with open(_cg_path(key), 'wb') as f:
            f.write(raw)
        g['sha'][key] = e['sha']
    return None


def _cg_sync_api():
    """Send our own ops file, download changed ones of others, apply (call under _collab_cond)."""
    s = _cg['sync']
    g, token = s['gh'], s['token']
    sent = _cg_export()          # own edits -> the local ops/<me>.jsonl (the sending below is idempotent)
    mine = 'ops/%s.jsonl' % s['slug']
    if os.path.exists(_cg_path(mine)):
        with open(_cg_path(mine), 'rb') as f:
            data = f.read()
        h = _hashlib.sha256(data).hexdigest()
        if h != g.get('mine'):
            for attempt in (1, 2):
                st, r = _gh_put(token, g, mine, data, _alang('Правки: %s', 'Edits: %s') % s['name'], sha=g['sha'].get(mine))
                if st in (200, 201):
                    g['sha'][mine], g['mine'] = r['content']['sha'], h
                    break
                if st in (409, 422) and attempt == 1:       # lost the sha (for example, the file already exists)
                    st2, meta = _gh_get(token, g, mine)
                    if st2 == 200 and isinstance(meta, dict):
                        g['sha'][mine] = meta.get('sha')
                        continue
                _cg_save()
                return _cg_fail(_gh_err(st, r))
    bad = _cg_fetch_api(s)
    if bad:
        _cg_save()
        return _cg_fail(bad)
    pulled, skipped = _cg_apply_remote()
    _cg['err'], _cg['last'] = '', time.strftime('%H:%M:%S')
    _cg_save()
    return jsonify({'ok': True, 'sent': sent, 'pulled': pulled, 'skipped': skipped})


@flask_app.route('/api/collab/git/status')
def api_cg_status():
    s = _cg['sync'] or {}
    return jsonify({'ok': True, 'git': bool(_shutil.which('git')), 'on': _cg['on'],
                    'api': s.get('mode') == 'api',
                    'remote': _cg_mask(s.get('remote', '')), 'name': s.get('name', ''),
                    'pending': _cg_pending_count() if _cg['on'] else 0,
                    'err': _cg['err'], 'last': _cg['last'],
                    'work': (state['file_path'] or '') if _cg['on'] else ''})


@flask_app.route('/api/collab/git/setup', methods=['POST'])
def api_cg_setup():
    """Connects a repository. If empty — we start from the current map (base.rbxl);
    if it has base.rbxl inside — we join: the map from the repository is opened and the edits are applied."""
    bad = _cg_host_only()
    if bad:
        return bad
    body = request.get_json(silent=True) or {}
    remote = (body.get('remote') or '').strip()
    name = (body.get('name') or '').strip()[:32] or 'Host'
    if not remote:
        return _cg_fail(_alang('Укажите адрес репозитория', 'Enter the repository address'))
    if remote.startswith('-') or any(c in remote for c in '\r\n\x00') or _re.match(r'[A-Za-z][A-Za-z0-9+.-]*::', remote):
        return _cg_fail(_alang('Некорректный адрес репозитория', 'Invalid repository address'))
    gh = _gh_parse(remote)
    token = (body.get('token') or '').strip() or (gh[2] if gh else '')
    if gh and token and (body.get('api') or not _shutil.which('git')):
        return _cg_setup_api(gh[0], gh[1], token, name)      # without git: via the GitHub API
    if not _shutil.which('git'):
        return _cg_fail(_alang('git на этом устройстве нет (так в APK). Укажите токен GitHub — тогда синхронизация '
                        'пойдёт напрямую через интернет, без git', 'There is no git on this device (as in the APK). Enter a GitHub token — then synchronization will go directly over the internet, without git'))
    with _collab_cond:
        if os.path.exists(_CG_DIR):                # we don't delete the previous folder — we move it aside
            os.rename(_CG_DIR, _CG_DIR + '.old-%d' % int(time.time()))
        rc, out = _cg_git('clone', '--', remote, _CG_DIR, cwd=os.path.dirname(_CG_DIR), timeout=180)
        if rc != 0:
            return _cg_fail('git clone: ' + out[-400:])
        joining = os.path.exists(_cg_path('base.rbxl'))
        slug = _re.sub(r'[^A-Za-z0-9_-]+', '_', name)[:20] + '-' + _secrets.token_hex(2)
        _cg_git('config', 'user.name', name)
        _cg_git('config', 'user.email', slug + '@rsw.local')
        if joining:
            work = _cg_path('work.rbxl')
            _shutil.copyfile(_cg_path('base.rbxl'), work)
            try:
                parsed = parse_rbxl(work)
            except Exception as e:
                return _cg_fail(_alang('Не удалось открыть base.rbxl: %s', 'Could not open base.rbxl: %s') % e)
            state['parsed'], state['file_path'] = parsed, work
            _recents_add_file(work, name='work.rbxl (git)')
            if _collab['on']:
                _collab_reset('reload')
            bump_scene_version()
        else:
            parsed, src = state['parsed'], state['file_path']
            if not parsed or not src or not os.path.isfile(src):
                return _cg_fail(_alang('Сначала откройте карту (с файла на диске)', 'Open a map first (from a file on disk)'))
            if parsed.get('_modified'):
                return _cg_fail(_alang('В карте есть несохранённые изменения: сохраните её (Save) и повторите', 'The map has unsaved changes: save it (Save) and try again'))
            _shutil.copyfile(src, _cg_path('base.rbxl'))
            with open(_cg_path('.gitignore'), 'w', encoding='utf-8') as f:
                f.write('work.rbxl\n')
            with open(_cg_path('meta.json'), 'w', encoding='utf-8') as f:
                _json.dump({'format': 1, 'base': 'base.rbxl', 'created_by': name}, f)
            _cg_git('checkout', '-B', 'main')
        _cg['sync'] = {'slug': slug, 'name': name, 'remote': remote, 'cursor': {},
                       'mine': set(), 'c2l': {}, 'l2c': {}}
        _cg['on'], _cg['err'] = True, ''
        _cg_save()
        if not joining:
            _cg_git('add', '-A')
            rc, out = _cg_git('commit', '-m', _alang('Начало совместной работы: исходная карта', 'Collaboration started: the original map'))
            rc, out = _cg_git('push', '-u', 'origin', 'main', timeout=180)
            if rc != 0:
                return _cg_fail('git push: ' + out[-400:])
        applied = skipped = 0
        if joining:
            applied, skipped = _cg_apply_remote()
        _cg['last'] = time.strftime('%H:%M:%S')
        return jsonify({'ok': True, 'joined': joining, 'applied': applied, 'skipped': skipped})


@flask_app.route('/api/collab/git/sync', methods=['POST'])
def api_cg_sync():
    bad = _cg_host_only()
    if bad:
        return bad
    if not _cg['on']:
        return _cg_fail(_alang('Git не подключён', 'Git is not connected'))
    with _collab_cond:
        if not state['parsed']:
            return _cg_fail(_alang('Карта не открыта: откройте work.rbxl из папки collab-git', 'The map is not open: open work.rbxl from the collab-git folder'))
        if _cg['sync'].get('mode') == 'api':
            return _cg_sync_api()
        sent = _cg_export()
        if sent:
            _cg_git('add', '-A')
            _cg_git('commit', '-m', _alang('Правки: %s (+%d)', 'Edits: %s (+%d)') % (_cg['sync']['name'], sent))
        branch = _cg_branch()
        pulled = skipped = 0
        for attempt in (1, 2):
            rc, out = _cg_git('fetch', 'origin', timeout=120)
            if rc != 0:
                return _cg_fail('git fetch: ' + out[-400:])
            if _cg_git('rev-parse', '--verify', 'origin/' + branch)[0] == 0:
                rc, out = _cg_git('rebase', 'origin/' + branch)
                if rc != 0:
                    _cg_git('rebase', '--abort')
                    return _cg_fail('git rebase: ' + out[-400:])
            d, k = _cg_apply_remote()
            pulled, skipped = pulled + d, skipped + k
            rc, out = _cg_git('push', '-u', 'origin', branch, timeout=180)
            if rc == 0:
                break
            if attempt == 2:
                return _cg_fail('git push: ' + out[-400:])   # the edits are already in the local repository
        _cg['err'], _cg['last'] = '', time.strftime('%H:%M:%S')
        return jsonify({'ok': True, 'sent': sent, 'pulled': pulled, 'skipped': skipped})


@flask_app.route('/api/collab/git/off', methods=['POST'])
def api_cg_off():
    bad = _cg_host_only()
    if bad:
        return bad
    with _collab_cond:
        _cg_disable('')
    return jsonify({'ok': True})


_cg_restore()


@flask_app.route('/collab.js')
def collab_js():
    try:
        with open('collab.js', 'r', encoding='utf-8') as f:
            src = f.read()
    except OSError:
        src = '/* collab.js not found */'
    return _no_cache(Response(src, mimetype='application/javascript'))

# Where to download from if there is no local file yet — the same list as in
# setup_termux.sh. The autoload below makes setup_termux.sh itself
# optional: the server downloads what's missing on demand by itself.
VENDOR_SOURCES = {
    # CodeMirror 5 (+ autocompletion addons) have been removed — the script editor
    # is now on CodeMirror 6, as a single bundle (see cm6-bundle.min.js below):
    # it also works properly with mobile keyboards, which CM5 couldn't do.
    'three.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'MTLLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/MTLLoader.js',
    'OBJLoader.js': 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js',
    'cannon.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js',
    'fengari-web.js': 'https://cdn.jsdelivr.net/npm/fengari-web@0.1.4/dist/fengari-web.js',
    # cm6-bundle.min.js is NOT a public CDN library but our own
    # file built by rollup (see entry.mjs/rollup.config.mjs in the root
    # of the repository — it can be rebuilt from there: `npm install
    # @codemirror/state @codemirror/view @codemirror/commands
    # @codemirror/language @codemirror/autocomplete @codemirror/legacy-modes
    # @codemirror/theme-one-dark @codemirror/search @lezer/highlight rollup
    # @rollup/plugin-node-resolve @rollup/plugin-terser && npx rollup -c`).
    # Such a file has no ready public CDN — we download it from OUR OWN
    # repository on GitHub, with the same plain HTTP GET as all the other
    # vendor files here. For this the file itself must be committed to the repo
    # at the path vendor/cm6-bundle.min.js — if the link below doesn't fit
    # (for example, the repository was renamed/moved), fix the URL.
    'cm6-bundle.min.js': 'https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/vendor/cm6-bundle.min.js',
}
    

def _download_vendor_file(fn):
    """Downloads fn from the CDN straight into VENDOR_DIR. True — success (the file is on disk)."""
    url = VENDOR_SOURCES.get(fn)
    if not url:
        return False
    # Fallback mirrors: jsdelivr/cdnjs are often unavailable without a VPN, while
    # github raw with a copy from the repository itself is usually available.
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
            raise last_err or OSError(_alang('пустой ответ', 'empty response'))
        # We write to a temporary file and rename it — if a parallel
        # request for the same file arrives at the same time, nobody will see a
        # partially written .js/.css.
        tmp = VENDOR_DIR / (fn + '.part')
        tmp.write_bytes(data)
        tmp.replace(VENDOR_DIR / fn)
        print(f'[RbxStudio] vendor: downloaded {fn} ({len(data)} bytes)')
        return True
    except (_urlerr.URLError, _urlerr.HTTPError, OSError, TimeoutError) as e:
        print(f'[RbxStudio] vendor: could not download {fn}: {e}')
        return False


@flask_app.route('/vendor/<path:fn>')
def vendor_files(fn):
    # Local copies of CodeMirror/Three.js/Cannon.js/fengari.
    # index.html loads them by the relative path 'vendor/...'; if the file
    # isn't on disk yet (the first launch, setup_termux.sh wasn't run),
    # we download it here on demand — after that all launches are offline,
    # without a network at all, because the file already lies in VENDOR_DIR.
    path = VENDOR_DIR / fn
    if not path.exists():
        if not _download_vendor_file(fn):
            return '', 404
    return send_from_directory(str(VENDOR_DIR), fn)


@flask_app.route('/api/class_icons')
def api_class_icons():
    """Class icons (data-URI) for the «Add» dialog: ?classes=Part,Script,..."""
    names = [c for c in (request.args.get('classes') or '').split(',') if c][:200]
    return jsonify({'ok': True, 'icons': {c: icon_src(c) for c in names}})


@flask_app.route('/icons/<path:fn>')
def serve_icon(fn):
    if ICONS_DIR.exists():
        return send_from_directory(str(ICONS_DIR), fn)
    return '', 404


# ============ Recent (the start screen) ============
# recent_files.json lies in the same data folder as roblox_auth.json
# (RSW_DATA_DIR on Android, otherwise next to app.py). Two kinds of entries:
#   {'kind': 'file',   'path', 'name', 'opened'}  — a local .rbxl/.rbxlx
#   {'kind': 'roblox', 'placeId', 'universeId', 'name', 'opened'} — a place from Roblox
# Files chosen via <input type=file> have no path on disk on the server, so
# their copy is put into recent_files/ (at most RECENTS_MAX of them, old ones are cleaned up).
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
    """Writes the list and cleans up copies of downloads that are no longer referenced."""
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
    """Must not break the main scenario: any errors are swallowed."""
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
    if not name:   # reopening: we keep the previous (original) name of the entry
        key = ('file', os.path.normcase(str(p)))
        name = next((e.get('name') for e in _recents_load() if _recents_key(e) == key), None)
    _recents_add({'kind': 'file', 'path': str(p), 'name': name or p.name})


@flask_app.route('/api/recents/remove', methods=['POST'])
def api_recents_remove():
    """Remove an entry from «recent» (the ⋮ item on a card). The file itself is not deleted,
    except the internal copy of a download in recent_files/."""
    body = request.get_json(silent=True) or {}
    kind = body.get('kind')
    if kind not in ('file', 'roblox'):
        return jsonify({'ok': False, 'error': _alang('kind должен быть file или roblox', 'kind must be file or roblox')}), 400
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
    """Recently opened: local files (existing ones only) and places from Roblox."""
    out = []
    for e in _recents_load():
        if e['kind'] == 'file' and not (e.get('path') and os.path.isfile(e['path'])):
            continue
        out.append(e)
    return jsonify({'ok': True, 'recents': out})


@flask_app.route('/api/open', methods=['POST'])
@_collab_track('reload')
def api_open():
    body = request.json or {}
    path = body.get('path', '')
    shown = (body.get('name') or '').strip() or None   # the real file name (Android hands over a copy imported_<digits>.rbxl)
    try:
        parsed = parse_rbxl(path)
        state['parsed'] = parsed
        state['file_path'] = path
        _recents_add_file(path, name=shown)
        return jsonify({'ok': True, 'count': len(parsed['referent_to_class'])})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@flask_app.route('/api/open/upload', methods=['POST'])
@_collab_track('reload')
def api_open_upload():
    """Opening an .rbxl/.rbxlx chosen through an ORDINARY system file
    manager (<input type=file> on the frontend, see pickRbxlFileForOpen() in
    index.html) — used everywhere except the Android APK with the SAF bridge (there
    Kotlin already puts the file into the app's private storage and passes
    the ordinary /api/open a real path on disk).
    
    Unlike /api/open, a path on the SERVER's disk for a file chosen by
    the user doesn't exist here in principle — the browser hands over only
    BYTES (this applies to desktop too: the server and the browser tab are physically
    not required to be the same machine). So we save to a temporary file
    and parse it as usual."""
    import tempfile

    if 'file' not in request.files:
        return jsonify({'ok': False, 'error': _alang('Файл не передан', 'No file provided')}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'ok': False, 'error': _alang('Имя файла пустое', 'The file name is empty')}), 400

    suffix = Path(file.filename).suffix or '.rbxl'
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Could not save the file: {e}'}), 500

    try:
        parsed = parse_rbxl(tmp_path)
        state['parsed'] = parsed
        # We have no real path on the user's disk (the temporary file
        # will be deleted now) — we leave file_path empty so that Ctrl+S/
        # saveFile() opens "Save as" itself instead of a silent write into a
        # vanished temp file.
        state['file_path'] = None
        try:   # a copy for the «recent» list (the upload has no path on disk)
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
    """As Studio itself does: AssetDelivery with the account session
    (.ROBLOSECURITY from sign-in). Works for places the account can
    edit (its own, groups, Team Create) and for copyable (uncopylocked) ones.
    Returns None if there is no sign-in."""
    if _roblox_cookie() is None:
        return None
    url = f'https://assetdelivery.roblox.com/v1/asset/?id={int(place_id)}'
    if version:
        url += f'&version={int(version)}'
    r = _req.Request(url, headers=_roblox_headers())
    with _req.urlopen(r, timeout=120) as resp:   # urllib follows the redirect to the CDN itself
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_place_bytes_key(place_id, version=None):
    """Fallback: Open Cloud Asset Delivery with x-api-key (the
    legacy-asset:manage permission). Returns None if no key is set."""
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
        raise RuntimeError(f'Open Cloud answered without a location: {meta}')
    cdn_req = _req.Request(location, headers={'Accept-Encoding': 'gzip'})
    with _req.urlopen(cdn_req, timeout=120) as resp:
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_place_bytes(place_id, version=None):
    """Downloads a place file. Order: account sign-in (as in Studio) →
    Open Cloud key. Returns (bytes, method) or (None, None) if neither
    is configured; if configured but everything failed, raises
    RuntimeError with the reasons for each method (+ .status from HTTPError)."""
    errors, status = [], None
    for name, fn in (('account sign-in', _rbx_get_place_bytes_cookie),
                     ('Open Cloud key', _rbx_get_place_bytes_key)):
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


def _rbx_group_universes(archived='false', max_groups=30):
    """Experiences of the current account's groups. Groups: groups.roblox.com/v2/users/{id}/groups/roles; group games:
    develop.roblox.com/v1/groups/{id}/universes (edit rights are needed — for other groups Roblox answers
    403, we silently skip such groups). In parallel, up to max_groups groups and 3 pages per group."""
    me = _rbx_get_json('https://users.roblox.com/v1/users/authenticated')
    uid = me.get('id') if isinstance(me, dict) else None
    if not uid:
        return []
    d = _rbx_get_json(f'https://groups.roblox.com/v2/users/{int(uid)}/groups/roles')
    groups = []
    for row in (d.get('data') or []) if isinstance(d, dict) else []:
        g = row.get('group') or {}
        if g.get('id'):
            groups.append((int(g['id']), g.get('name') or ''))
    groups = groups[:max_groups]

    def one(g):
        gid, gname = g
        out, cursor = [], None
        for _ in range(3):
            url = (f'https://develop.roblox.com/v1/groups/{gid}/universes'
                   f'?isArchived={archived}&limit=50&sortOrder=Desc')
            if cursor:
                url += '&cursor=' + _urlparse.quote(cursor)
            try:
                dd = _rbx_get_json(url)
            except Exception:
                return out      # no rights to the group / network — skip it
            for u in (dd.get('data') or []) if isinstance(dd, dict) else []:
                if not (u.get('id') and u.get('rootPlaceId')):
                    continue
                out.append({
                    'universeId': u['id'], 'placeId': u['rootPlaceId'],
                    'name': u.get('name') or str(u['id']),
                    'private': (u.get('privacyType') or 'Private') != 'Public',
                    'updated': u.get('updated') or u.get('created') or '',
                    'owner': gname or u.get('creatorName') or '',
                    'group': True, 'icon': None})
            cursor = dd.get('nextPageCursor') if isinstance(dd, dict) else None
            if not cursor:
                break
        return out

    from concurrent.futures import ThreadPoolExecutor
    res = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for part in ex.map(one, groups):
            res.extend(part)
    return res


@flask_app.route('/api/roblox/experiences')
def api_roblox_experiences():
    """The account's Experiences list — like Studio's start screen (My Recent
    Experiences). develop.roblox.com/v1/user/universes (sign-in is required;
    an Open Cloud key doesn't work for it) + icons from
    thumbnails.roblox.com. We return up to 150, newest changes first.
    ?archived=1 — the Archive section (archived experiences)."""
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'needLogin': True,
                        'error': _alang('Нужен вход в аккаунт Roblox', 'Roblox account sign-in is required')}), 401
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

    # Experiences of the GROUPS the user belongs to: /v1/user/universes returns only personal games, so
    # group games (like «Group Games» in Studio) are fetched separately. Per-group errors don't bring down the whole list.
    group_err = None
    try:
        seen = {x['universeId'] for x in items}
        for u in _rbx_group_universes(archived):
            if u['universeId'] not in seen:
                seen.add(u['universeId'])
                items.append(u)
    except Exception as e:
        group_err = str(e)

    # icons (optional: on error placeholders remain)
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
    return jsonify({'ok': True, 'experiences': items, 'groupError': group_err})


# === Studio games on the start screen ===
# The list is taken from STUDIO_GAMES_DEFAULT below; it can be overridden by a studio_games.json file (in the app's data folder
# or next to app.py). groupId — a Roblox group id: its games are pulled in automatically (public API),
# games — manually pinned ({"name": "druns", "placeId": 123, "universeId": 456}; universeId is optional).
STUDIO_GAMES_DEFAULT = {
    'title': None,      # None — the title is taken from the interface translation (st_studio); a string — shown as is
    'groupId': 0,
    'games': [],
}
# The list is loaded FROM THE SERVER: a JSON in the repository (change the file, commit — everyone is updated without rebuilding the APK).
# RSW_STUDIO_URL — your own link; "url" in a local studio_games.json overrides it too. No network — the last
# successfully loaded copy (studio_games.cache.json in the data folder), then what is baked in above.
STUDIO_GAMES_URL = os.environ.get('RSW_STUDIO_URL') or \
    'https://raw.githubusercontent.com/suscersal/roblox-studio-web/main/studio_games.json'
_STUDIO_REMOTE = {'at': 0.0, 'cfg': None}


def _studio_remote_config(url):
    """Config from the server with a 5-minute cache and a backup copy on disk. Returns a dict or None."""
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
    """Order (each next one overrides the previous): what is baked into app.py → studio_games.json next to app.py (from the repository)
    → the list from the server → a manual studio_games.json in the app's data folder (if it is set separately, RSW_DATA_DIR)."""
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
            cursor = None
            for _ in range(10):     # previously only the first 50 games of a group were taken
                url = (f'https://games.roblox.com/v2/groups/{int(group_id)}/games'
                       '?accessFilter=2&limit=50&sortOrder=Desc')
                if cursor:
                    url += '&cursor=' + _urlparse.quote(cursor)
                d = _rbx_get_json(url)
                for u in (d.get('data') or []):
                    root = (u.get('rootPlace') or {}).get('id')
                    if u.get('id') and root:
                        add(u.get('name'), root, u.get('id'), u.get('updated') or u.get('created') or '',
                            (u.get('creator') or {}).get('name') or '')
                cursor = d.get('nextPageCursor') if isinstance(d, dict) else None
                if not cursor:
                    break
        except Exception as e:
            group_err = str(e)

    # No config set — automatic mode: games of the groups of the signed-in account (like «Group Games» in Studio)
    auto, need_login = False, False
    if not (group_id or cfg.get('games')):
        auto = True
        if _roblox_cookie() is None:
            need_login = True
        else:
            try:
                for u in _rbx_group_universes('false'):
                    add(u['name'], u['placeId'], u['universeId'], u['updated'], u['owner'])
            except Exception as e:
                group_err = str(e)

    # icons (optional)
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
                    'configured': bool(group_id or cfg.get('games')), 'groupError': group_err,
                    'auto': auto, 'needLogin': need_login})


_DOH_CACHE = {}


def _doh_resolve(host):
    """An A record via DNS-over-HTTPS (bypasses a broken system DNS)."""
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
            last = _alang('нет A-записей', 'no A records')
        except Exception as e:
            last = repr(e)
    raise RuntimeError(_alang('DoH не сработал: ', 'DoH did not work: ') + str(last))


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
    """Experience icon proxy. A WebView/browser often can't open
    tr.rbxcdn.com itself (blocking, the app has no VPN), although the server
    reaches Roblox — so we serve the picture from our own origin.
    Only https hosts *.rbxcdn.com are allowed (SSRF protection)."""
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
        hdr = dict(ROBLOX_HEADERS_BASE)       # without the cookie: the CDN doesn't need it
        hdr['Referer'] = 'https://www.roblox.com/'
        hdr['Accept'] = 'image/avif,image/webp,image/png,image/*;q=0.8'
        hdr.pop('Accept-Encoding', None)      # we return the image as is, without gzip
        try:
            r = _req.Request(u, headers=hdr)
            with _req.urlopen(r, timeout=15) as resp:
                data = resp.read()
                ct = resp.headers.get('Content-Type', 'image/png')
        except Exception as e1:
            # Often rbxcdn.com isn't resolved by the system DNS (gaierror) —
            # then we resolve it ourselves via DNS-over-HTTPS and go by IP.
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


_TB_THUMB_CACHE = {}
_TB_THUMB_SEM = _threading.Semaphore(4)   # we don't flood the network with 24 simultaneous thumbnail requests
_TB_PLACEHOLDER = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 150"><rect width="150" height="150" fill="#111827"/>'
                   '<text x="75" y="95" font-size="56" text-anchor="middle">\U0001F9F0</text></svg>')


@flask_app.route('/api/toolbox/thumb/<int:asset_id>')
def api_toolbox_thumb(asset_id):
    """An asset thumbnail for Toolbox cards. A direct www.roblox.com/asset-thumbnail often doesn't open in a WebView
    (blocking/DNS) and spewed an error for every card; here the server fetches the thumbnail (with a DoH fallback path).
    The response is always 200: if fetching failed — we return an SVG placeholder (uncached), and there is not a single error in the console."""
    key = str(asset_id)
    data = _TB_THUMB_CACHE.get(key)
    if data is None:
        with _TB_THUMB_SEM:
            data = _TB_THUMB_CACHE.get(key)
            if data is None:
                try:
                    d = _rbx_get_json('https://thumbnails.roblox.com/v1/assets?assetIds=' + key +
                                      '&returnPolicy=PlaceHolder&size=150x150&format=Png&isCircular=false')
                    row = (d.get('data') or [{}])[0] if isinstance(d, dict) else {}
                    if row.get('state') == 'Completed' and row.get('imageUrl'):
                        data = _rbx_get_bytes(row['imageUrl'])
                        if len(_TB_THUMB_CACHE) >= 400:
                            _TB_THUMB_CACHE.pop(next(iter(_TB_THUMB_CACHE)))
                        _TB_THUMB_CACHE[key] = data
                except Exception as e:
                    print('[toolbox] thumb', key, _alang('не загрузилась:', 'did not load:'), repr(e)[:160])
                    data = None
    if data:
        resp = Response(data, mimetype='image/png' if data[:4] == b'\x89PNG' else 'image/jpeg')
        resp.headers['Cache-Control'] = 'public, max-age=86400'
        return resp
    resp = Response(_TB_PLACEHOLDER, mimetype='image/svg+xml')
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@flask_app.route('/api/roblox/experience/places')
def api_roblox_experience_places():
    """Places inside an Experience (many have one — then the client opens it right away)."""
    um = _re.search(r'\d+', request.args.get('universeId', ''))
    if not um:
        return jsonify({'ok': False, 'error': _alang('universeId должен быть числом', 'universeId must be a number')}), 400
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
@_collab_track('reload')
def api_open_place():
    """Download a place from Roblox by Place ID and open it in the editor.
    Body: {place_id, version?}. The account sign-in is used first
    (as in Studio), if there is none or it didn't work — the Open Cloud key.
    The result is opened the same way as /api/open/upload; publishing
    back is the ordinary /api/publish."""
    import tempfile
    body = request.get_json(silent=True) or {}
    m = _re.search(r'\d+', str(body.get('place_id', '')))
    if not m:
        return jsonify({'ok': False, 'error': _alang('Нужен числовой Place ID', 'A numeric Place ID is required')}), 400
    place_id = int(m.group())
    vm = _re.search(r'\d+', str(body.get('version', '') or ''))
    version = int(vm.group()) if vm else None

    try:
        data, via = _rbx_get_place_bytes(place_id, version)
    except Exception as e:
        hints = {
            401: _alang('вход не принят или истёк — войди в аккаунт заново', 'sign-in was not accepted or has expired — sign in to your account again'),
            403: _alang('нет доступа к месту: нужен аккаунт с правом редактирования '
                 '(владелец, группа, Team Create) или копируемое место', 'no access to the place: an account with edit rights is required (owner, group, Team Create) or a copyable place'),
            404: _alang('место или версия не найдены', 'place or version not found'),
        }
        st = getattr(e, 'status', None)
        msg = str(e) + ((' — ' + hints[st]) if st in hints else '')
        return jsonify({'ok': False, 'status': st, 'error': msg}), 502
    if data is None:
        return jsonify({'ok': False,
                        'error': _alang('Войди в аккаунт Roblox (кнопка Account) '
                                 'или сохрани Open Cloud API-ключ', 'Sign in to your Roblox account (the Account button) or save an Open Cloud API key')}), 400

    # .rbxl is binary ('<roblox!'), .rbxlx is XML ('<roblox ' / '<?xml').
    # Everything else is not a place file (for example, JSON with an error): we don't touch state.
    if data[:8] == b'<roblox!':
        suffix = '.rbxl'
    elif data[:7] == b'<roblox' or data[:5] == b'<?xml':
        suffix = '.rbxlx'
    else:
        return jsonify({'ok': False,
                        'error': f'The response does not look like a place file ({len(data)} bytes, 'f'starts with: {data[:40]!r})'}), 502
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parsed = parse_rbxl(tmp_path)
        state['parsed'] = parsed
        state['file_path'] = None   # as with upload: Ctrl+S will open «Save as»
        universe_id = None
        um = _re.search(r'\d+', str(body.get('universe_id', '') or ''))
        if um:
            universe_id = int(um.group())
        else:
            try:   # Place ID -> Universe ID (a public endpoint), needed for Publish
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
        return jsonify({'ok': False, 'error': f'Downloaded {len(data)} bytes, but could not parse it as .rbxl: {e}'}), 400
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# ============ The «Baseplate» template for the New button ============
# Built into the code (base64 of BASEPLATE.rbxl), rather than lying as a separate file: this way it is
# equally available on desktop, in the Android APK and in OTA updates (there __file__
# points to another folder, and sync-android-python.sh copies only a list of files).
# Want your own template without editing code — put templates/Baseplate.rbxl next to app.py:
# if the file exists, it is used.
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
    """Opens the Baseplate template as a fresh unsaved scene. Returns
    the number of objects; on any error raises an exception (api_new falls back to
    an empty scene)."""
    import tempfile
    tmp_path = None
    try:
        data = _baseplate_bytes()
        # parse_rbxl doesn't fail on garbage but returns an empty scene — we check ourselves
        if data[:8] != b'<roblox!':
            raise RuntimeError(_alang('шаблон Baseplate — не бинарный .rbxl', 'the Baseplate template is not a binary .rbxl'))
        with tempfile.NamedTemporaryFile(suffix='.rbxl', delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        parsed = parse_rbxl(tmp_path)
        if 'Workspace' not in parsed['referent_to_class'].values():
            raise RuntimeError(_alang('в шаблоне Baseplate нет Workspace', 'the Baseplate template has no Workspace'))
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    state['parsed'] = parsed
    state['file_path'] = None   # Ctrl+S will open «Save as», the template isn't overwritten
    return len(parsed['referent_to_class'])


@flask_app.route('/api/new', methods=['POST'])
@_collab_track('reload')
def api_new():
    """A new scene = the Baseplate template (see _load_baseplate_into_state); if
    it for some reason failed to load — an empty scene, as before:
    creates it in the server's memory (without a file on disk) — the set of
    standard top-level Roblox services, as in a new place.
    Needed so that features like importing an Instance (for example, a 3D avatar)
    work even without a previously opened .rbxl — previously PUT
    /api/instance silently failed with ok:false if state['parsed']
    was None, and the object stayed only visual in the viewport, not
    getting into either Explorer or the saved file. save_rbxl can
    rebuild the binary completely even without _raw_chunks/_raw_data
    (see the "from scratch" branch in save_rbxl), so Save/Save As afterwards
    works as usual — the path just has to be chosen when saving."""
    want_empty = ((request.get_json(silent=True) or {}).get('template') == 'empty')
    if not want_empty:
        try:
            return jsonify({'ok': True, 'count': _load_baseplate_into_state(), 'template': 'Baseplate'})
        except Exception:
            traceback.print_exc()   # the template failed to load — make an empty scene, as before
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
        'service_refs': set(referent_to_class),  # all top-level ones are services
        '_modified': True,
        # We deliberately do NOT add '_raw_chunks'/'_raw_data' — their absence
        # makes save_rbxl build the binary from scratch from
        # referent_to_class/parent_map/props instead of trying to reuse
        # someone else's raw chunks.
    }
    state['file_path'] = None
    return jsonify({'ok': True, 'count': len(referent_to_class)})


_VALUE_CLASSES = ('StringValue', 'NumberValue', 'IntValue', 'BoolValue',
                  'Vector3Value', 'CFrameValue', 'Color3Value', 'ObjectValue')


_REF_PROP_CLASSES = ('RigidConstraint', 'WeldConstraint', 'Weld', 'ManualWeld', 'Motor6D', 'Motor', 'BallSocketConstraint',
                    'NoCollisionConstraint', 'AnimationConstraint', 'HingeConstraint', 'SpringConstraint')


# Classes whose properties from the file used NOT to reach Lua (a script read nil + an emulator warning):
# the new Audio API (AudioPlayer/Wire/...), Lighting post effects, Atmosphere/Clouds, Beam, Smoke/Sparkles,
# constraints, Highlight. We take ALL properties from the file except service ones.
_FILE_PROP_CLASSES = frozenset((
    'Humanoid',   # NPC: MaxHealth/WalkSpeed/HipHeight from the file (Health defaults to MaxHealth, see luaGetGenericProp)
    'Highlight', 'Decal',   # Decal: Texture/Transparency/Face/ZIndex are read and changed from Lua (TV screens, posters)
    'AudioPlayer', 'AudioFader', 'AudioCompressor', 'AudioEqualizer', 'AudioEmitter', 'AudioListener',
    'AudioDeviceOutput', 'AudioReverb', 'AudioEcho', 'AudioDistortion', 'AudioFlanger', 'AudioChorus',
    'AudioPitchShifter', 'AudioLimiter', 'AudioTextToSpeech', 'AudioFilter', 'Wire', 'HapticEffect',
    'BloomEffect', 'DepthOfFieldEffect', 'SunRaysEffect', 'ColorCorrectionEffect', 'BlurEffect',
    'Atmosphere', 'Clouds', 'Beam', 'Smoke', 'Sparkles', 'Highlight',
    'PrismaticConstraint', 'HingeConstraint', 'ReverbSoundEffect', 'EqualizerSoundEffect',
    'CompressorSoundEffect', 'DistortionSoundEffect', 'EchoSoundEffect', 'ChorusSoundEffect',
    'FlangeSoundEffect', 'TremoloSoundEffect',
))
# Terrain in the file carries hundreds of Part properties — we take only the water ones.
_TERRAIN_PROPS = ('WaterColor', 'WaterReflectance', 'WaterTransparency', 'WaterWaveSize', 'WaterWaveSpeed', 'Decoration')
_FILE_PROP_SKIP = frozenset((
    'AttributesSerialize', 'Capabilities', 'DefinesCapabilities', 'HistoryId', 'SerializedOverrides',
    'SourceAssetId', 'Tags', 'UniqueId', 'Name', 'Transparency', 'Color3', 'Color3uint8',
))
# The name in the binary file -> the name in the Lua API (where they differ)
_FILE_PROP_RENAME = {('AudioPlayer', 'Asset'): 'AssetId'}


def _file_props_for_client(cls, q, r2c):
    """-> (gprops, tprops) for the Lua bridge.
    gprops: scalars (bool/number/string) — put into the «junk drawer» of properties;
    tprops: typed — [kind, a, b, c]: c3 (Color3), v3 (Vector3), ref (an object reference, -1 = nil)."""
    g, t = {}, {}
    if cls == 'Terrain':
        keys = [k for k in _TERRAIN_PROPS if k in q]
    else:
        keys = [k for k in q if k not in _FILE_PROP_SKIP]
    for k in keys:
        v = q[k]
        name = _FILE_PROP_RENAME.get((cls, k), k)
        if isinstance(v, bool):
            g[name] = v
        elif isinstance(v, int):
            # a reference to another object of the file (Wire.SourceInstance, Beam.Attachment0, ...) or an ordinary number/enum
            if k in ('SourceInstance', 'TargetInstance', 'Attachment0', 'Attachment1', 'PositionInstance',
                     'Adornee', 'Player', 'Part0', 'Part1'):
                t[name] = ['ref', v if v in r2c else -1]
            else:
                g[name] = v
        elif isinstance(v, float):
            if v != v or v in (float('inf'), float('-inf')):
                g[name] = 1e308 if v > 0 else -1e308
            else:
                g[name] = v
        elif isinstance(v, str):
            if len(v) <= 2048 and '\x00' not in v:
                g[name] = v
        elif isinstance(v, dict):
            if all(c in v for c in ('r', 'g', 'b')):
                t[name] = ['c3', float(v['r']), float(v['g']), float(v['b'])]
            elif all(c in v for c in ('x', 'y', 'z')):
                t[name] = ['v3', float(v['x']), float(v['y']), float(v['z'])]
    return g, t


def _attachment_cf(q):
    """Attachment.CFrame from file properties -> [x, y, z, R00..R22] (row-major, like CFrame:GetComponents())."""
    import math as _m
    cf = q.get('CFrame') if isinstance(q.get('CFrame'), dict) else {}
    pos = cf.get('position') if isinstance(cf.get('position'), dict) else (q.get('Position') if isinstance(q.get('Position'), dict) else {})
    x, y, z = (float(pos.get(k, 0.0)) for k in ('x', 'y', 'z'))
    m = cf.get('matrix')
    if isinstance(m, (list, tuple)) and len(m) == 9:
        rot = [float(v) for v in m]
    elif isinstance(cf.get('angles_deg'), (list, tuple)) and len(cf['angles_deg']) == 3:
        rx, ry, rz = (_m.radians(float(v)) for v in cf['angles_deg'])   # Orientation: the order Y, X, Z
        cx, sx, cy, sy, cz, sz = _m.cos(rx), _m.sin(rx), _m.cos(ry), _m.sin(ry), _m.cos(rz), _m.sin(rz)
        rot = [cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx,
               cx * sz, cx * cz, -sx,
               -sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx]
    else:
        rot = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    return [x, y, z] + rot


def _value_for_client(cls, v):
    # Primitives are returned as is; Vector3/CFrame/Color3/ObjectValue — as
    # {'k': kind, 'v': [...]}, the frontend assembles Lua values from them.
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
    """AttributesSerialize (Roblox's binary attribute format) -> {name: value} for string/bool/number.
    Other types (Color3, Vector, UDim...) are skipped but read to the end so as not to knock off the following attributes.
    Format: u32 attribute count; for each: u32 name length, the name, u8 type, the value (string: u32 length + bytes;
    bool: 1; int32: 4; float: 4; double: 8; UDim 8; UDim2 16; BrickColor 4; Color3/Vector3 12; Vector2 8).
    Verified on real map data (30 instances, types 0x02/0x03/0x06/0x0F/0x10, the decoder reaches the end)."""
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
                break    # an unknown type — the size is unknown, we can't read further
    except Exception:
        pass
    return out


def _decode_tags(value, shared_strings):
    """The Tags property (CollectionService) is stored as a SharedString: a string of tags separated by NUL characters."""
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
    # A flat RAW list of ALL instances of the map — ref/class/name/parent, without
    # filtering HIDDEN classes, without a depth limit and without a nested
    # children structure (unlike /api/tree, which builds exactly what
    # Explorer draws and is deliberately trimmed for that).
    #
    # The Lua bridge (see index.html, startLuaScripts) needs the FULL picture of
    # the hierarchy — script.Parent must work for any script, even
    # if it is nested inside something Explorer hides. Lua used to take the
    # parent from the same tree as Explorer (/api/tree), and any
    # script under a filtered branch got Parent=nil with no
    # real reason on the script's own side.
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
        # Attributes and tags of an object from the file (Tool: viewModel/damage/..., force fields: PinkForcefield tags etc.) —
        # used not to be read at all, so GetAttribute/GetTagged on map objects always returned nil/empty.
        _pp = pr.get(ref, {})
        _ab = _pp.get('AttributesSerialize')
        if isinstance(_ab, (bytes, bytearray)) and _ab:
            _attrs = _decode_attributes(bytes(_ab))
            if _attrs:
                item['attrs'] = _attrs
        # Tool properties from the file (TextureId — the hotbar icon, ToolTip, CanBeDropped, ...): without them tool.TextureId was empty
        # and the hotbar drew slots without pictures.
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
        # Model.WorldPivotData (OptionalCFrame, world): without it Model.WorldPivot/GetPivot were computed
        # from the center of the bounds, and scripts like ElevatorSpawner (ELEV1.WorldPivot) failed on nil.
        _wp = _pp.get('WorldPivotData')
        if isinstance(_wp, dict):
            _wx, _wy, _wz = get_pos(_wp)
            item['pivot'] = {'p': [_wx, _wy, _wz], 'r': get_rot_matrix(_wp)}
        # Model.PrimaryPart (a reference to a part): the model's pivot = this part's pivot. Without it scripts like room spawning
        # (room.PrimaryPart = a door marker; room:PivotTo(...)) placed the room not by the marker but by the center of the bounds.
        if cls == 'Model':
            _ppr = _pp.get('PrimaryPart')
            if isinstance(_ppr, int) and not isinstance(_ppr, bool) and _ppr in r2c:
                item['refs'] = {'PrimaryPart': _ppr}
        if cls == 'Team':
            item['teamColor'] = _pp.get('TeamColor')
            item['autoAssignable'] = _pp.get('AutoAssignable', True)
        if cls == 'Sound':
            # SoundId/Volume/Looped — sounds set DIRECTLY IN THE FILE (rather than via
            # Instance.new(...).SoundId = ... from Lua). They used not to
            # reach here: the Lua bridge saw only cls/name/parent, so
            # the real HTMLAudioElement (see getOrCreateSoundEl in
            # index.html) never received a src for sounds already lying
            # in the map at load — audio.src stayed empty even
            # if Sound:Play() was honestly called.
            sp = pr.get(ref, {})
            item['soundId'] = sp.get('SoundId', '')
            item['volume'] = sp.get('Volume', 0.5)
            item['looped'] = sp.get('Looped', False)
            # PlaybackSpeed — the same "set right in the file, no script
            # touches it" as Octave below: FNF maps with a
            # ready-made "sped up" variant of a track (PlaybackSpeed=2.0 on
            # several of your Sounds) played at normal speed, because
            # only soundId/volume/looped used to get here.
            ps = sp.get('PlaybackSpeed', 1.0)
            if ps != 1.0:
                item['playbackSpeed'] = ps
            # PitchShiftSoundEffect — the REAL Roblox pitch mechanism (not the
            # deprecated scalar Sound.Pitch): a separate child
            # instance with Octave (speed multiplier = 2^Octave). It used to be
            # read nowhere at all — FNF maps with "sped up"/slowed
            # variants of a track (Octave set RIGHT in the file, without a single
            # line of script) played at normal speed, because the
            # effect simply wasn't connected to the real <audio> in any way.
            for child_ref in children_by_parent.get(ref, ()):
                if r2c.get(child_ref) == 'PitchShiftSoundEffect':
                    cp = pr.get(child_ref, {})
                    if cp.get('Enabled', True):
                        item['pitchOctave'] = cp.get('Octave', 0.0)
                    break
        elif cls == 'Attachment':
            item['att'] = _attachment_cf(pr.get(ref, {}))
        elif cls in _REF_PROP_CLASSES:
            # The Part0/Part1/Attachment0/Attachment1 references (welds and constraints): scripts use them to find what
            # is attached to what (for example, an accessory to the head via a RigidConstraint).
            qq = pr.get(ref, {})
            refs = {}
            for key in ('Part0', 'Part1', 'Attachment0', 'Attachment1'):
                if key in qq:
                    vv = qq.get(key)
                    refs[key] = vv if (isinstance(vv, int) and not isinstance(vv, bool) and vv in r2c) else -1
            if refs:
                item['refs'] = refs
        elif cls in _VALUE_CLASSES:
            # A ValueBase.Value lying IN THE FILE (IntValue/CFrameValue/...) — otherwise
            # Lua sees nil until a script writes something to .Value itself.
            val = _value_for_client(cls, pr.get(ref, {}).get('Value'))
            if val is not None:
                item['value'] = val
        if cls == 'Beam':
            # Color — a ColorSequence: for a ribbon we take the color of the first keypoint
            _bc = _pp.get('Color')
            if isinstance(_bc, list) and _bc and isinstance(_bc[0], dict):
                item['beamColor'] = [float(_bc[0].get('r', 1)), float(_bc[0].get('g', 1)), float(_bc[0].get('b', 1))]
            # Transparency — a NumberSequence: the ribbon is drawn with the average value (the TV's noise: 0.8 -> a faint overlay;
            # before, transparency was ignored and the beam showed up as opaque white bars)
            _bt = _pp.get('Transparency')
            if isinstance(_bt, list) and _bt and isinstance(_bt[0], dict):
                _vals = [float(k.get('value', 0)) for k in _bt if isinstance(k, dict)]
                if _vals:
                    item['beamTransparency'] = sum(_vals) / len(_vals)
        if cls in _FILE_PROP_CLASSES or cls == 'Terrain':
            _g, _t = _file_props_for_client(cls, pr.get(ref, {}), r2c)
            if cls == 'Highlight':
                # colors as numbers: the client draws the fill/outline and for clones as well (gprops are copied on Clone())
                _hq = pr.get(ref, {})
                for _pn, _gn in (('FillColor', 'HL_Fill'), ('OutlineColor', 'HL_Out')):
                    _c = _hq.get(_pn)
                    if isinstance(_c, dict) and all(k in _c for k in ('r', 'g', 'b')):
                        _g[_gn] = [float(_c['r']), float(_c['g']), float(_c['b'])]
                    else:
                        _g[_gn] = [1.0, 0.0, 0.0] if _pn == 'FillColor' else [1.0, 1.0, 1.0]
            if _g:
                item.setdefault('gprops', {}).update(_g)
            if _t:
                item['tprops'] = _t
        out.append(item)
    return jsonify({'ok': True, 'instances': out})


@flask_app.route('/api/scripts')
def api_scripts():
    # Returns all Scripts/LocalScripts with their source — used by the Lua runtime
    # in Play (see index.html, startLuaScripts/fengari) to start the scripts
    # with one request, rather than one by one via /api/instance/<ref> for each.
    # We return ModuleScripts too (the field 'runnable': False) — they do NOT
    # start automatically themselves (as in real Roblox), but the frontend
    # needs their source in advance so that require(moduleScriptInstance) can
    # compile/execute them on demand (see __require_module in
    # index.html). ModuleScript used not to be included here at all, and require()
    # was not implemented — the bare require() from the standard
    # Lua library was used ("bad argument #1 to 'require' (string expected, got
    # table)", because scripts call require(instance), not
    # require("module_name")).
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
        # In .rbxl the disabled-script flag is stored as Disabled (not Enabled) — it used to be ignored,
        # and a Script with Disabled=true still ran in Play.
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
            # 'server' for Script, 'client' for LocalScript — see
            # SCRIPT_SIDE above. The frontend uses this only for
            # display (a badge in Output/Properties), not for real
            # network isolation.
            'side': ('client' if (cls == 'Script' and props.get('RunContext') == 2)
                     else SCRIPT_SIDE.get(cls, 'server')),
            # Script.RunContext: 0 = Legacy (server), 1 = Server, 2 = Client — a Script with Client
            # runs on the client (Players.LocalPlayer exists there), not on the server
            'runContext': props.get('RunContext'),
        })
    return jsonify({'ok': True, 'scripts': out})


@flask_app.route('/api/gui_tree')
def api_gui_tree():
    # A flat list of all GUI instances (ScreenGui and its descendants —
    # Frame/TextLabel/TextButton/TextBox/ImageLabel/ImageButton) with a narrow
    # set of properties (GUI_PROPS), which is enough for the frontend
    # (buildGuiOverlay in index.html) to assemble the overlay's DOM tree on top of the
    # 3D viewport in Play. In spirit — the same as what /api/scripts does
    # for Script/LocalScript: one request instead of N calls to
    # /api/instance/<ref> for each GUI object.
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
                # MaxDistance = inf (the default for BillboardGui) can't be sent in JSON: Infinity is invalid,
                # fetch().json() fails and the whole of Play with it. No field = no distance limit.
                if isinstance(v, float) and (v != v or v in (float('inf'), float('-inf'))):
                    continue
                item[pname] = v
        out.append(item)
    return jsonify({'ok': True, 'elements': out})


@flask_app.route('/api/tree')
def api_tree():
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('Файл не загружен', 'No file loaded')}), 400
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

        # Skip hidden classes
        if cls in HIDDEN:
            return None

        name = pr.get(ref, {}).get('Name', cls)

        # Collect children (recursively)
        kids = []
        for c in sorted(children_of.get(ref, [])):
            # Create a vis copy for each branch
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

    # Root elements (parent = -1 or missing from parent_map)
    roots = []
    # Find all refs whose parent = -1 or whose parent is missing from r2c
    root_refs = set()
    for ref in r2c:
        parent = pm.get(ref, -1)
        if parent == -1 or parent not in r2c:
            root_refs.add(ref)

    # Also add explicitly specified children of -1
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
    # Templates (ServerStorage/ReplicatedStorage): the client doesn't draw them in Play, but Clone() needs the data — we return ALL at once,
    # without a distance limit (otherwise clones of distant room/enemy templates remain without a mesh).
    if request.args.get('nw') == '1':
        if not state['parsed']:
            return jsonify({'ok': True, 'objects': []})
        return jsonify({'ok': True, 'objects': [o for o in build_all_scene_objects() if o.get('nw')]})
    # POST with the body {cx,cy,cz,load_radius,limit,chunk} — used by
    # Play streaming (see index.html, refreshStreamedGeometry): simply
    # "all objects within load_radius of the player", without raycasting and without
    # the camera direction (see get_chunk_index/gather_objects_in_radius
    # above — the chunk-based approach, as in Minecraft/UE5 World Partition).
    # GET with query parameters stays as it was for the other calls
    # (the editor's ordinary scene load) and for pts= from older versions.
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
        # Chunk-based path: fast candidate selection via the cell grid
        # (gather_objects_in_radius), already sorted by distance —
        # we just take the nearest limit.
        by_dist = gather_objects_in_radius(cx, cy, cz, load_radius)
        objs = [o for _, o in by_dist]
        total = len(objs)
        if chunk:
            objs = chunk_large_objects(objs)
            # chunk_large_objects splits large objects only AFTER the selection
            # by radius here (unlike get_chunk_index, where the splitting
            # happens before laying out into cells) — the distance order isn't
            # spoiled by this: parts of one big object stay next
            # to each other in the list.
        if limit is not None:
            objs = objs[:limit]
        return jsonify({'ok': True, 'objects': objs, 'total': total})

    # The old points-based path (used by the other calls —
    # the ordinary scene load in the editor, where raycast/radius aren't needed).
    points = []
    if cx is not None and cy is not None and cz is not None:
        points.append((cx, cy, cz))

    # pts=x,y,z;x,y,z;... — backward compatibility.
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
    return jsonify({'ok': True, 'objects': objs, 'total': total,
                    'rev': id(state.get('parsed'))})


@flask_app.route('/api/proximity_prompts')
def api_proximity_prompts():
    """All ProximityPrompts on the map — all at once and once only (the list is usually
    small, not tied to radius-based streaming, and the object itself
    may be needed by the player before it gets into the camera's LOD radius). The client measures the distance to parentRef itself every frame — here
    only the static data from the file."""
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
            continue  # the prompt isn't on a part/model — there is nothing to measure the distance from
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
            'style': props.get('Style', 0),
            'gamepadKeyCode': props.get('GamepadKeyCode', 1000),
        })
    return jsonify({'ok': True, 'prompts': out})


@flask_app.route('/api/spawn')
def api_spawn_point():
    # A separate handler, independent of which piece of the scene is currently
    # loaded in the editor — needed so that Play always finds the spawn
    # point, even if it didn't fall into the camera's current LOD radius.
    #
    # A map may have several SpawnLocations (team spawns and
    # the like). We prefer Anchored=true — an unanchored spawn often
    # hangs in the air (decorative/on a moving platform) and drops the
    # player into the void if it is chosen first just by file order.
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

    # team=auto: as in Roblox, on joining the player goes to the first AutoAssignable team and appears at the SpawnLocation
    # of THEIR team (TeamColor matches, Neutral=false); if there is none — at a neutral one. Previously just the first spawn was taken,
    # and a Pink player ended up in the green zone, on the other side of an enemy force field.
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

    candidates.sort(key=lambda c: not c[0])  # anchored=True first
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
    # Listening to a sound right from Explorer (buildSoundPreviewRow) used to
    # play it "as is", without PlaybackSpeed/PitchShiftSoundEffect —
    # it sounded different from the real game. Octave lies not in the Sound itself but
    # in the child PitchShiftSoundEffect, so we look for it separately, as in
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
    """Sends a POST request with a JSON body and returns the parsed JSON."""
    req = _req.Request(url, data=data, headers=_roblox_headers())
    req.add_header('Content-Type', 'application/json')
    try:
        with _req.urlopen(req, timeout=20) as resp:
            raw = _rbx_maybe_gunzip(resp.read())
            raw_text = raw.decode('utf-8', 'replace')
        return json.loads(raw_text)
    except _urlerr.HTTPError as e:
        body = _rbx_maybe_gunzip(e.read()).decode('utf-8', 'replace')[:300]
        raise RuntimeError(f'HTTP {e.code} from Roblox: {body}')
    except Exception as e:
        raise RuntimeError(str(e))


@flask_app.route('/api/roblox/userid', methods=['GET'])
def api_roblox_userid():
    """Get a User ID by nickname via the official Roblox API.
    Requires .ROBLOSECURITY (authorization)."""
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({'ok': False, 'error': 'Missing username'}), 400

    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': _alang('Сначала войдите в аккаунт Roblox.', 'Sign in to your Roblox account first.')}), 401

    try:
        # We use the official Roblox endpoint
        resp = _rbx_post_json(
            'https://users.roblox.com/v1/usernames/users',
            json.dumps({'usernames': [username], 'excludeBannedUsers': False}).encode(
                'utf-8')
        )
        # _rbx_get_json does a GET by default. We need a POST.
        # We'll have to change _rbx_get_json a little or write a separate function.
        # Let's rewrite _rbx_get_json to support POST.
        # Or create a new function _rbx_post_json.
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502

    # Response handling
    if isinstance(resp, dict) and resp.get('data') and len(resp['data']) > 0:
        user_data = resp['data'][0]
        return jsonify({
            'ok': True,
            'id': user_data['id'],
            'displayName': user_data.get('displayName', ''),
            'name': user_data.get('name', '')
        })
    else:
        return jsonify({'ok': False, 'error': _alang('Пользователь не найден', 'User not found')}), 404


def build_rot_matrix_from_deg(rx_deg, ry_deg, rz_deg):
    """Builds a 3x3 rotation matrix (row-major, 9 elements) from angles in
    degrees — with the same convention as get_rot_matrix() and the decomposition in
    rbxl_parser.py (R = Rx(rx) * Ry(ry) * Rz(rz)), so that Rotation and CFrame
    stay consistent in both directions."""
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


# ---- Transforms (the Move/Rotate/Scale/Pivot tools) --------------------------------------------------
# The canonical CFrame understood by both the scene (get_pos/get_rot_matrix) and saving (s_cframe):
# {'matrix': [R00..R22 by rows], 'position': {x,y,z}}. Editing Position/Rotation used to write a 12-element
# matrix with the position inside — s_cframe read only the first 9 numbers from it and lost the position on save.
_IDENT3 = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]


def _m3_to_euler_deg(m):
    """The inverse of build_rot_matrix_from_deg (R = Rx*Ry*Rz) -> (rx, ry, rz) in degrees."""
    r00, r01, r02, r10, r11, r12, r20, r21, r22 = m
    ry = math.asin(max(-1.0, min(1.0, r02)))
    if abs(r02) < 0.99999:
        rx = math.atan2(-r12, r22)
        rz = math.atan2(-r01, r00)
    else:
        rx = math.atan2(r21, r11)
        rz = 0.0
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def _cf_read(cf, fallback_pos=None):
    """CFrame dict -> (pos[3], rot[9])."""
    if isinstance(cf, dict) and ('position' in cf or 'matrix' in cf):
        pos = list(get_pos(cf))
        if fallback_pos is not None and pos == [0.0, 0.0, 0.0]:
            pos = list(fallback_pos)
        return pos, [float(v) for v in get_rot_matrix(cf)]
    return list(fallback_pos or (0.0, 0.0, 0.0)), list(_IDENT3)


def _cf_make(pos, rot):
    return {'matrix': [float(v) for v in rot], 'position': {'x': float(pos[0]), 'y': float(pos[1]), 'z': float(pos[2])}}


def _part_pose(props):
    p = props.get('Position')
    fb = (safe_float(p.get('x', 0)), safe_float(p.get('y', 0)), safe_float(p.get('z', 0))) if isinstance(p, dict) else None
    return _cf_read(props.get('CFrame'), fb)


def _part_set_size(props, size):
    """Size is stored in the file under the binary name 'size' (the serializer writes it), 'Size' is a derived
    field for the panel: editing only 'Size' was lost on save."""
    v = {'x': float(size[0]), 'y': float(size[1]), 'z': float(size[2])}
    props['Size'] = v
    props['size'] = dict(v)


def _part_set_pose(props, pos, rot):
    """A unified write of a part's pose: CFrame + the auxiliary Position/Rotation (read by the Properties panel)."""
    props['CFrame'] = _cf_make(pos, rot)
    props['Position'] = {'x': float(pos[0]), 'y': float(pos[1]), 'z': float(pos[2])}
    rx, ry, rz = _m3_to_euler_deg(rot)
    props['Rotation'] = {'x': rx, 'y': ry, 'z': rz}


_TRANSFORM_PROP_NAMES = ['CFrame', 'Position', 'Rotation', 'Size', 'PivotOffset', 'WorldPivotData']


def _subtree_refs(parsed, root):
    kids = {}
    for c, p in parsed['parent_map'].items():
        kids.setdefault(p, []).append(c)
    out, stack = [], [root]
    while stack:
        r = stack.pop()
        out.append(r)
        stack.extend(kids.get(r, ()))
    return out


def _vec3(v, default=(0.0, 0.0, 0.0)):
    try:
        return [float(v[0]), float(v[1]), float(v[2])]
    except (TypeError, ValueError, IndexError, KeyError):
        return list(default)


def _mat9(v):
    try:
        m = [float(x) for x in v]
        return m if len(m) == 9 else list(_IDENT3)
    except (TypeError, ValueError):
        return list(_IDENT3)


def _obb_corners(pos, rot, size):
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    out = []
    for sx in (-hx, hx):
        for sy in (-hy, hy):
            for sz in (-hz, hz):
                v = _m3_vec(rot, [sx, sy, sz])
                out.append([pos[0] + v[0], pos[1] + v[1], pos[2] + v[2]])
    return out


def _part_size(props):
    sz = props.get('Size', props.get('size'))
    if isinstance(sz, dict):
        return [max(0.05, safe_float(sz.get(a, 1), 1)) for a in ('x', 'y', 'z')]
    return [1.0, 1.0, 1.0]


def _part_pivot(props):
    """A part's world pivot = CFrame * PivotOffset -> (pos, rot)."""
    pos, rot = _part_pose(props)
    po = props.get('PivotOffset')
    if isinstance(po, dict):
        pp, pr = _cf_read(po)
        off = _m3_vec(rot, pp)
        return [pos[0] + off[0], pos[1] + off[1], pos[2] + off[2]], _m3_mul(rot, pr)
    return pos, rot


@flask_app.route('/api/transform_info')
def api_transform_info():
    """For the gizmo: the pivot, dimensions and (for a part) the size/pose of the selected objects."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    r2c = parsed['referent_to_class']
    out = {}
    for tok in (request.args.get('refs') or '').split(','):
        try:
            ref = int(tok)
        except ValueError:
            continue
        if ref not in r2c:
            continue
        lo, hi, n = [1e30] * 3, [-1e30] * 3, 0
        for r in _subtree_refs(parsed, ref):
            if r2c.get(r) not in PART_CLASSES:
                continue
            pr = parsed['props'].get(r, {})
            if pr.get('Visible') is False:
                pass
            pos, rot = _part_pose(pr)
            for c in _obb_corners(pos, rot, _part_size(pr)):
                for i in range(3):
                    lo[i] = min(lo[i], c[i])
                    hi[i] = max(hi[i], c[i])
            n += 1
        item = {'cls': r2c[ref], 'n': n}
        if n:
            item['min'], item['max'] = lo, hi
        props = parsed['props'].get(ref, {})
        if r2c[ref] in PART_CLASSES:
            pos, rot = _part_pose(props)
            ppos, prot = _part_pivot(props)
            item.update({'pivot': {'p': ppos, 'r': prot}, 'cf': {'p': pos, 'r': rot},
                         'size': _part_size(props), 'hasPivotOffset': isinstance(props.get('PivotOffset'), dict)})
        else:
            wp = props.get('WorldPivotData')
            pp = props.get('PrimaryPart')
            if isinstance(wp, dict):
                p, r = _cf_read(wp)
                item['pivot'] = {'p': p, 'r': r}
                item['explicitPivot'] = True
            elif isinstance(pp, int) and not isinstance(pp, bool) and pp in r2c and r2c[pp] in PART_CLASSES:
                p, r = _part_pivot(parsed['props'].get(pp, {}))
                item['pivot'] = {'p': p, 'r': r}
            elif n:
                item['pivot'] = {'p': [(lo[i] + hi[i]) / 2.0 for i in range(3)], 'r': list(_IDENT3)}
        out[str(ref)] = item
    return jsonify({'ok': True, 'refs': out})


@flask_app.route('/api/transform', methods=['POST'])
def api_transform():
    """Batch transform editing (one request for the whole gesture in the editor).
    ops: [{ref, delta:{r:[9], t:[3], pivot:[3], k}}           — a rigid shift/rotation/uniform scale of ref and ALL its descendant parts,
    {ref, cframe:{p:[3], r:[9]}, size:[3]}              — the absolute pose/size of one part,
    {ref, pivotOffset:{p,r}|null}                        — a part's PivotOffset (null = reset),
    {ref, worldPivot:{p,r}}                              — a model's WorldPivot}"""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False}), 400
    ops = (request.json or {}).get('ops')
    if not isinstance(ops, list) or not ops:
        return jsonify({'ok': False, 'error': 'ops'}), 400
    r2c = parsed['referent_to_class']
    changed = {}     # ref -> the «before» snapshot

    def touch(ref):
        if ref not in changed:
            changed[ref] = _collab_snapshot_props(parsed, ref, _TRANSFORM_PROP_NAMES) if _collab['on'] or _cg['on'] else None
        return parsed['props'].setdefault(ref, {})

    with _collab_cond:
        for op in ops:
            ref = op.get('ref') if isinstance(op, dict) else None
            if ref not in r2c:
                continue
            d = op.get('delta')
            if isinstance(d, dict):
                R = _mat9(d.get('r'))
                T = _vec3(d.get('t'))
                C = _vec3(d.get('pivot'))
                k = float(d.get('k', 1.0) or 1.0)
                for r in _subtree_refs(parsed, ref):
                    cls = r2c.get(r)
                    if cls in PART_CLASSES:
                        pr = touch(r)
                        pos, rot = _part_pose(pr)
                        rel = [pos[i] - C[i] for i in range(3)]
                        rr = _m3_vec(R, rel)
                        npos = [C[i] + k * rr[i] + T[i] for i in range(3)]
                        _part_set_pose(pr, npos, _m3_mul(R, rot))
                        if k != 1.0:
                            sz = pr.get('Size')
                            if isinstance(sz, dict):
                                _part_set_size(pr, [safe_float(sz.get(a, 1), 1) * k for a in ('x', 'y', 'z')])
                            po = pr.get('PivotOffset')
                            if isinstance(po, dict):
                                pp, prr = _cf_read(po)
                                pr['PivotOffset'] = _cf_make([v * k for v in pp], prr)
                    wp = parsed['props'].get(r, {}).get('WorldPivotData')
                    if isinstance(wp, dict):
                        pr = touch(r)
                        pos, rot = _cf_read(wp)
                        rel = [pos[i] - C[i] for i in range(3)]
                        rr = _m3_vec(R, rel)
                        pr['WorldPivotData'] = _cf_make([C[i] + k * rr[i] + T[i] for i in range(3)], _m3_mul(R, rot))
                continue
            pr = None
            cf = op.get('cframe')
            if isinstance(cf, dict) and r2c.get(ref) in PART_CLASSES:
                pr = touch(ref)
                _part_set_pose(pr, _vec3(cf.get('p')), _mat9(cf.get('r')))
            sz = op.get('size')
            if sz is not None and r2c.get(ref) in PART_CLASSES:
                pr = touch(ref)
                v = _vec3(sz, (1.0, 1.0, 1.0))
                _part_set_size(pr, [max(0.05, v[0]), max(0.05, v[1]), max(0.05, v[2])])
            if 'pivotOffset' in op and r2c.get(ref) in PART_CLASSES:
                pr = touch(ref)
                po = op.get('pivotOffset')
                if po is None:
                    pr.pop('PivotOffset', None)
                else:
                    pr['PivotOffset'] = _cf_make(_vec3(po.get('p')), _mat9(po.get('r')))
            wpv = op.get('worldPivot')
            if isinstance(wpv, dict):
                pr = touch(ref)
                pr['WorldPivotData'] = _cf_make(_vec3(wpv.get('p')), _mat9(wpv.get('r')))
        if not changed:
            return jsonify({'ok': True, 'changed': []})
        parsed['_modified'] = True
        bump_scene_version()
        if (_collab['on'] or _cg['on']):
            try:
                refs = list(changed)
                undo = [('props', r, changed[r]) for r in refs if changed[r] is not None]
                redo = [('props', r, _collab_snapshot_props(parsed, r, _TRANSFORM_PROP_NAMES)) for r in refs if changed[r] is not None]
                cls, nm = _collab_obj(parsed, refs[0])
                _collab_push('set', refs[0], nm, cls, prop='Transform', n=len(refs), undo=undo, redo=redo)
            except Exception:
                traceback.print_exc()
    return jsonify({'ok': True, 'changed': list(changed)})


@flask_app.route('/api/instance/<int:ref>', methods=['POST'])
@_collab_track('set')
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

        # CFrame in make_scene_objects has priority over Position/Rotation — we synchronize,
        # and write in canonical form (see _part_set_pose), otherwise the position was lost on save.
        if prop == 'Size' and isinstance(val, dict):
            _part_set_size(props, [safe_float(val.get('x', 1), 1), safe_float(val.get('y', 1), 1), safe_float(val.get('z', 1), 1)])
        if prop == 'Position' and isinstance(val, dict):
            _pos, _rot = _part_pose(props)
            _part_set_pose(props, [safe_float(val.get('x', 0)), safe_float(val.get('y', 0)), safe_float(val.get('z', 0))], _rot)
        elif prop == 'Rotation' and isinstance(val, dict):
            _pos, _rot = _part_pose(props)
            _part_set_pose(props, _pos, build_rot_matrix_from_deg(
                safe_float(val.get('x', 0)), safe_float(val.get('y', 0)), safe_float(val.get('z', 0))))
    return jsonify({'ok': True})


def _m3_mul(a, b):
    """3x3 (by rows, 9 numbers) * 3x3."""
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


# Template-storage containers: the objects inside don't exist in the world (they appear only when a script does Clone() into Workspace)
_NOT_IN_WORLD_ROOTS = ('ServerStorage', 'ReplicatedStorage', 'StarterPack')


def _ref_in_world(ref, pmap, r2c):
    """False if the object lies in ServerStorage/ReplicatedStorage/StarterPack (a template, not part of the world)."""
    root, g = ref, 0
    while pmap.get(root) in r2c and g < 500:
        root = pmap[root]
        g += 1
    return r2c.get(root) not in _NOT_IN_WORLD_ROOTS


@flask_app.route('/api/particles')
def api_particles():
    """All ParticleEmitters of the scene: where they stand (the emitter's world position/rotation
    and the one relative to the part) and their properties. They are drawn by the client
    (script.js, the «PARTICLES» block). The emitter's parent is an Attachment (a point) or
    the part itself (then particles appear within the part's volume)."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': True, 'emitters': []})
    r2c, pmap, allp = parsed['referent_to_class'], parsed['parent_map'], parsed['props']
    out = []
    for ref, cls in r2c.items():
        if cls != 'ParticleEmitter':
            continue
        if not _ref_in_world(ref, pmap, r2c):
            continue    # emitters of ServerStorage templates used to «burn» in the air at the template's place
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
@_collab_track('add')
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
        # Without initial Position/Size/CFrame a new object ends up
        # at (0,0,0) with a zero/default size and overlaps
        # other parts — it visually looks like "it didn't appear".
        px, py, pz = data.get('px', 0), data.get('py', 5), data.get('pz', 0)
        dsx, dsy, dsz = _ADD_SIZE_DEFAULTS.get(cls, (4, 1, 2))
        sx, sy, sz = data.get('sx', dsx), data.get('sy', dsy), data.get('sz', dsz)
        props['Position'] = {'x': safe_float(
            px), 'y': safe_float(py), 'z': safe_float(pz)}
        props['Rotation'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        props['Size'] = {'x': safe_float(sx, 4), 'y': safe_float(
            sy, 1), 'z': safe_float(sz, 2)}
        # The CFrame format in props is 9 rotation numbers (by rows) + a separate position. Previously 12 numbers were written here with the position
        # inside matrix: the position got into the rotation elements, and the new part's physics body received a garbage (non-identity) rotation.
        props['CFrame'] = {
            'matrix': [1, 0, 0, 0, 1, 0, 0, 0, 1],
            'position': {'x': safe_float(px), 'y': safe_float(py, 5), 'z': safe_float(pz)},
        }
        props['Anchored'] = data.get('anchored', True)
        props['CanCollide'] = data.get('cancollide', True)
        props['Color'] = data.get('color', {'r': 0.63, 'g': 0.63, 'b': 0.63})

    parsed['props'][new_ref] = props
    parsed['_modified'] = True
    bump_scene_version()
    return jsonify({'ok': True, 'ref': new_ref})


@flask_app.route('/api/reparent', methods=['POST'])
@_collab_track('move')
def api_reparent():
    """Moving objects to another parent (drag & drop in Explorer).
    Body: {"refs": [..], "parent": ref}. World coordinates don't change —
    as in Roblox, only the tree changes."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('Файл не загружен', 'No file loaded')}), 400
    data = request.json or {}
    try:
        refs = [int(r) for r in (data.get('refs') or [])]
        parent = int(data.get('parent'))
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': _alang('Некорректные refs/parent', 'Invalid refs/parent')}), 400
    r2c, pm = parsed['referent_to_class'], parsed['parent_map']
    if parent not in r2c:
        return jsonify({'ok': False, 'error': _alang('Родитель не найден', 'Parent not found')}), 400

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
        # you can't put an object into itself or into its descendant
        if ref in parent_chain:
            skipped.append(ref); continue
        # we don't move services (roots without a parent) and Terrain/Camera
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
@_collab_track('del')
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
        return jsonify({'ok': False, 'error': _alang('Нет данных', 'No data')}), 400
    data = request.json or {}
    path = data.get('path') or state['file_path']
    if not path:
        return jsonify({'ok': False, 'error': _alang('Нет пути', 'No path')}), 400
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
    """Publishing to Roblox. Open Cloud first (POST universes/{id}/places/{id}/versions, an API key is needed),
    then the fallback through the account session (POST data.roblox.com/Data/Upload.ashx?assetid=<Place ID>,
    as Rojo and others do). The cookie path is unofficial (Roblox asks to move to Open Cloud), only
    for Published: it has no «Saved» (a version not rolled out to players) and no Universe ID is needed.
    Previously the file lying on DISK (state['file_path']) was sent: edits not saved with the «Save» button
    didn't get into the publication, and for a new project without a file publishing didn't work at all. Now
    the CURRENT scene is published: it is serialized into a temporary .rbxl (the local file is not touched)."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('Файл не загружен', 'No file loaded')}), 400
    data = request.json or {}
    universe_id = str(data.get('universe_id', '')).strip()
    place_id = str(data.get('place_id', '')).strip()
    api_key = (data.get('api_key') or '').strip() or _roblox_api_key() or ''
    version_type = data.get('version_type', 'Published')
    if version_type not in ('Published', 'Saved'):
        version_type = 'Published'
    has_cookie = _roblox_cookie() is not None
    if not place_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('Place ID должен быть числом', 'Place ID must be a number')}), 400
    if api_key and not universe_id.isdigit() and not (has_cookie and version_type == 'Published'):
        return jsonify({'ok': False, 'error': _alang('Universe ID должен быть числом', 'Universe ID must be a number')}), 400
    if not api_key and not has_cookie:
        return jsonify({'ok': False, 'error': _alang('Нет API-ключа и входа в аккаунт: введите ключ в окне или настройте их в «Аккаунт»', 'No API key and no account sign-in: enter a key in the window or set them up in «Account»')}), 400
    if not api_key and version_type == 'Saved':
        return jsonify({'ok': False, 'error': _alang('Saved работает только с API-ключом: через вход в аккаунт Roblox всегда публикует', 'Saved works only with an API key: publishing through a Roblox account sign-in always creates a new version')}), 400
    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix='.rbxl')
    os.close(fd)
    try:
        save_rbxl(parsed, tmp_path)
        status, text, via, key_note = None, '', None, ''
        if api_key and universe_id.isdigit():
            status, text = publish_place(tmp_path, universe_id, place_id, api_key, version_type)
            via = 'api-key'
            if status == 200:
                return jsonify({'ok': True, 'status': status, 'text': text, 'via': via})
            key_note = f'key: HTTP {status}'
        # fallback path: no key or it wasn't accepted (401/403) — Published only
        if has_cookie and version_type == 'Published' and (status is None or status in (401, 403)):
            with open(tmp_path, 'rb') as f:
                raw = f.read()
            st2, d2 = _oc_cookie_call('POST', 'https://data.roblox.com/Data/Upload.ashx',
                                      query={'assetid': place_id}, raw=raw, timeout=300,
                                      headers={'User-Agent': 'Roblox/WinInet',
                                               'Content-Type': 'application/octet-stream',
                                               'Accept': 'application/json'})
            text2 = d2 if isinstance(d2, str) else json.dumps(d2, ensure_ascii=False)
            if key_note and not (200 <= st2 < 300):
                text2 = f'{key_note}; cookie: HTTP {st2}: {text2}'
            return jsonify({'ok': 200 <= st2 < 300, 'status': st2, 'text': text2, 'via': 'cookie'})
        return jsonify({'ok': False, 'status': status, 'text': text, 'via': via})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@flask_app.route('/api/save/download')
def api_save_download():
    """Saving "as" through an ordinary browser download (the native
    download manager of the OS/browser) instead of a home-grown explorer over the
    SERVER's file system (see /api/browse below) — that path made no sense at all
    whenever the server and the browser tab are physically not
    one machine (primarily the mobile case). We write to a
    temporary file on the server's disk (as the Android branch of
    saving via SAF already does), read the bytes into memory and return them as an
    attachment, deleting the temporary file immediately."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('Нет данных', 'No data')}), 400

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
    """Export of selected objects (with all descendants) to a binary .rbxm.
    
    GET  ?refs=1,2,3&name=model.rbxm — an ordinary browser download (like
    /api/save/download: blob URLs don't work in Android WebView).
    POST {refs: [...], path: "..."} — writes the file to the server's disk; this is how
    Android puts the file into the private folder before exporting via SAF."""
    parsed = state['parsed']
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('Нет данных', 'No data')}), 400
    if request.method == 'POST':
        body = request.json or {}
        raw_refs = body.get('refs') or []
    else:
        raw_refs = [x for x in (request.args.get('refs') or '').split(',') if x.strip()]
    try:
        refs = [int(x) for x in raw_refs][:20000]
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': _alang('Некорректный список объектов', 'Invalid list of objects')}), 400
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
            return jsonify({'ok': False, 'error': _alang('Нет пути', 'No path')}), 400
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


_PENDING_IMPORTS = {}   # token -> {'path', 'parent', 'ts'}: models with scripts wait for the user's confirmation


def _pending_cleanup():
    now = time.time()
    for tok in [t for t, v in _PENDING_IMPORTS.items() if now - v['ts'] > 1800]:
        _pending_drop(tok)
    while len(_PENDING_IMPORTS) > 8:
        _pending_drop(next(iter(_PENDING_IMPORTS)))


def _pending_drop(tok):
    v = _PENDING_IMPORTS.pop(tok, None)
    if v:
        try:
            os.unlink(v['path'])
        except OSError:
            pass


def _finish_rbxm_import(path, parent, confirmed=False):
    """Import of an .rbxm into the scene. If the model has scripts and the user hasn't confirmed yet — we import NOTHING and
    return a summary (how many scripts, dangerous commands found such as require/loadstring/HttpService) and a token: the client
    shows a window and calls /api/import/rbxm/confirm (or /cancel). Toolbox, an .rbxm from disk and Android all work the same way."""
    import shutil
    import tempfile
    if not state['parsed']:
        api_new()   # nothing to open — we import into a new empty scene
    if not confirmed:
        scan = scan_rbxm(path)
        if scan['scripts']['total']:
            _pending_cleanup()
            fd, keep = tempfile.mkstemp(suffix='.rbxm')
            os.close(fd)
            shutil.copyfile(path, keep)   # the caller will delete the source temporary file right after the response
            tok = _secrets.token_hex(8)
            _PENDING_IMPORTS[tok] = {'path': keep, 'parent': parent, 'ts': time.time()}
            return jsonify({'ok': False, 'needsConfirm': True, 'token': tok, 'scan': scan})
    info = {}
    try:
        roots, count, warnings = import_rbxm(state['parsed'], path, parent, info)
    except ValueError as e:
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'ok': False, 'error': str(e)}), 500
    bump_scene_version()
    return jsonify({'ok': True, 'count': count, 'roots': roots, 'warnings': warnings, 'lighting': info.get('lighting', [])})


@flask_app.route('/api/import/rbxm/confirm', methods=['POST'])
@_collab_track('import')
def api_import_rbxm_confirm():
    """Confirmation of importing a model with scripts: {token}. The file is already in _PENDING_IMPORTS."""
    tok = (request.get_json(silent=True) or {}).get('token')
    v = _PENDING_IMPORTS.get(tok)
    if not v:
        return jsonify({'ok': False, 'error': _alang('Импорт устарел — повторите вставку модели', 'The import has expired — paste the model again')}), 404
    try:
        return _finish_rbxm_import(v['path'], v['parent'], confirmed=True)
    finally:
        _pending_drop(tok)


@flask_app.route('/api/import/rbxm/cancel', methods=['POST'])
def api_import_rbxm_cancel():
    _pending_drop((request.get_json(silent=True) or {}).get('token'))
    return jsonify({'ok': True})


@flask_app.route('/api/import/rbxm', methods=['POST'])
@_collab_track('import')
def api_import_rbxm():
    """Import of an .rbxm by a path on the server's disk (Android: Kotlin has already copied
    the file chosen via SAF into the app's private folder)."""
    data = request.json or {}
    path = data.get('path')
    if not path or not os.path.isfile(path):
        return jsonify({'ok': False, 'error': _alang('Файл не найден', 'File not found')}), 400
    parent = data.get('parent')
    return _finish_rbxm_import(path, int(parent) if parent is not None else None)


@flask_app.route('/api/import/rbxm/upload', methods=['POST'])
@_collab_track('import')
def api_import_rbxm_upload():
    """Import of an .rbxm chosen with an ordinary <input type=file> (see /api/open/upload)."""
    import tempfile
    if 'file' not in request.files or not request.files['file'].filename:
        return jsonify({'ok': False, 'error': _alang('Файл не передан', 'No file provided')}), 400
    parent = request.form.get('parent')
    try:
        parent = int(parent) if parent not in (None, '', 'null') else None
    except ValueError:
        return jsonify({'ok': False, 'error': _alang('Некорректный родитель', 'Invalid parent')}), 400
    try:
        with tempfile.NamedTemporaryFile(suffix='.rbxm', delete=False) as tmp:
            request.files['file'].save(tmp.name)
            tmp_path = tmp.name
    except Exception as e:
        return jsonify({'ok': False, 'error': f'Could not save the file: {e}'}), 500
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
    """The path to the file with the saved .ROBLOSECURITY. On Android this is
    RSW_DATA_DIR/roblox_auth.json (see bridge_launcher.py and
    MainActivity.kt: RobloxLoginActivity writes there after login). Outside
    Android (an ordinary python app.py run) we use a local folder —
    so the desktop version can also pick up the cookie if it is placed there
    by hand."""
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    return Path(data_dir) / 'roblox_auth.json'


def _roblox_cookie():
    """Returns the cookie string '.ROBLOSECURITY=...' or None if there has been no login
    yet / the file is corrupted."""
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
    # CRITICAL: without this the server may send the body gzipped, and urllib
    # does NOT decompress it automatically (only requests/
    # browsers do) — the result: JSON and even the model files themselves were read as raw
    # compressed bytes and turned into unreadable "binary mush" instead of
    # text/pictures. The simplest is to ask the server not to compress at all.
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
    """Sign-in on desktop (on Android the WebView signs in, see RobloxLoginActivity).
    Body: {cookie}: the .ROBLOSECURITY value (with or without the prefix). The cookie is
    verified with a request to Roblox and saved to roblox_auth.json (0600);
    it is NOT returned in the response. Only from the local machine: the cookie gives
    full access to the account, and the server listens on 0.0.0.0."""
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return jsonify({'ok': False, 'error': _alang('Только с локального устройства', 'Only from the local device')}), 403
    body = request.get_json(silent=True) or {}
    val = str(body.get('cookie') or '').strip().strip('"\'')
    if val.upper().startswith('.ROBLOSECURITY='):
        val = val.split('=', 1)[1].strip().strip('"\'')
    if len(val) < 100 or any(c in val for c in ' ;\r\n'):
        return jsonify({'ok': False, 'error': _alang('Не похоже на значение .ROBLOSECURITY', 'This does not look like a .ROBLOSECURITY value')}), 400

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
            raise RuntimeError(_alang('в ответе нет id', 'no id in the response'))
    except Exception as e:
        # validation failed — we return the previous state
        try:
            if old is None:
                p.unlink()
            else:
                p.write_text(old, encoding='utf-8')
        except Exception:
            pass
        return jsonify({'ok': False, 'error': f'Roblox did not accept the cookie: {e}'}), 400
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
        return jsonify({'ok': False, 'error': _alang('Файл не передан', 'No file provided')}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'ok': False, 'error': _alang('Имя файла пустое', 'The file name is empty')}), 400

    try:
        # We read the contents of the uploaded file into memory
        zip_bytes = file.read()
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
            names = zf.namelist()
            obj_name = next(
                (n for n in names if n.lower().endswith('.obj')), None)
            mtl_name = next(
                (n for n in names if n.lower().endswith('.mtl')), None)
            if not obj_name or not mtl_name:
                return jsonify({'ok': False, 'error': _alang('В архиве нет .obj или .mtl — это точно экспорт аватара?', 'There is no .obj or .mtl in the archive — is this really an avatar export?')}), 400

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
        return jsonify({'ok': False, 'error': _alang('Файл повреждён или это не .zip', 'The file is corrupted or is not a .zip')}), 400
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


def _rbx_maybe_gunzip(raw: bytes) -> bytes:
    """Safety net: if some node nevertheless ignores
    Accept-Encoding: identity and sends gzip (byte signature 1f 8b),
    we decompress it ourselves — otherwise the output is an unreadable binary mush
    instead of the real JSON/OBJ/PNG."""
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
        raise RuntimeError(f'HTTP {e.code} from Roblox: {body}')
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Not JSON — almost always means that an HTML page came instead of an API response
        # (a Cloudflare/PerimeterX anti-bot check, a redirect
        # to login, etc.). We show the start of the body as is — this makes it immediately
        # visible that it's not our bug but a block on Roblox's side.
        snippet = raw_text[:300].replace('\n', ' ')
        raise RuntimeError(
            f'Roblox returned a non-JSON response (looks like an anti-bot page): {snippet}')


def _roblox_apikey_file():
    """The path to the file with the saved Open Cloud API key — the same place and
    the same principle as _roblox_auth_file() for the cookie (see nearby):
    RSW_DATA_DIR on Android, a local folder otherwise. A separate file, not
    inside roblox_auth.json — a key and a cookie are different credentials with
    different life cycles (a key isn't tied to a particular login)."""
    data_dir = os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)
    return Path(data_dir) / 'roblox_apikey.json'


def _roblox_api_key():
    """The Open Cloud API key — the official replacement for the session cookie for
    AssetDelivery. Since April 2, 2025 Roblox closed anonymous access to
    assetdelivery.roblox.com (see devforum "New Asset Delivery API
    Endpoints for Community Tools") — without authorization it is now a 401 on
    ANY request, not only for private assets. The key is created in
    Creator Dashboard → Open Cloud → API Keys, with a read-only permission on
    assets.
    
    Lookup order: the ROBLOX_API_KEY environment variable (for server
    deployments where the key is set at launch) — if not set, we read the
    key the user entered themselves via the UI (/api/roblox/api-key,
    see below) and which lies in _roblox_apikey_file(). The key is NOT stored
    in code/the repository in either variant."""
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
    """Managing the Open Cloud API key from the UI — the user enters it
    themselves (see showRobloxApiKeyDialog in index.html), the key is saved to
    disk locally (the same folder as roblox_auth.json) and never
    goes anywhere except direct requests to apis.roblox.com in
    _rbx_get_bytes_opencloud. GET returns only the fact that a key exists and its
    last 4 characters for recognition — the key itself is not returned."""
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

    # POST — save a new key
    body = request.get_json(silent=True) or {}
    key = (body.get('api_key') or '').strip()
    if not key:
        return jsonify({'ok': False, 'error': _alang('api_key пустой', 'api_key is empty')}), 400
    try:
        p.write_text(json.dumps({'api_key': key}), encoding='utf-8')
        return jsonify({'ok': True, 'last4': key[-4:]})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@flask_app.route('/api/roblox/api-key/validate', methods=['POST'])
def api_roblox_api_key_validate():
    """A real check of the saved key — previously the only way to
    find out that a key is broken/lacks the needed scope was to wait until
    something in the game stopped loading, and read 502 from
    /api/asset-proxy after the fact. We fire the same Open Cloud metadata request
    (without downloading the CDN file itself — no point moving bytes just for
    a check), with the test ID from the request body if there is one (we usually take
    the first real asset found in the scene on the frontend — so the
    check covers what will really be needed in the game), otherwise just
    the number 1 (the main thing is to tell a 401/403 about the KEY apart from an error about a
    specific asset)."""
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
        # Any OTHER error (a 404 on a specific test asset, a 5xx at
        # Roblox, etc.) does NOT mean the key is bad — the very fact that the
        # server answered (rather than rejecting by x-api-key) already means
        # the key authorized normally.
        return jsonify({'ok': True, 'valid': True, 'note': f'HTTP {e.code} on the test asset, but the key authorized'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


def _rbx_get_bytes_opencloud(asset_id):
    """GET /asset-delivery-api/v1/assetId/{id} with x-api-key → JSON with
    a location field (a temporary signed CDN link, TTL of a few
    minutes) → an ordinary GET on that link, without authorization headers.
    Returns None if no key is configured (then the calling code
    falls back to the anonymous path below), and raises an exception on
    a real request error — to tell "there is simply no key" apart from
    "there is a key, but it doesn't work"."""
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
        raise RuntimeError(f'Open Cloud answered without a location: {meta}')

    # The CDN link itself is already signed (signature+expiry in the query, see the
    # archiveteam wiki about AWS CloudFront) — there is no need to send x-api-key a second time and it won't help, this is just
    # an ordinary HTTPS GET.
    cdn_req = _req.Request(location, headers={'Accept-Encoding': 'gzip'})
    with _req.urlopen(cdn_req, timeout=20) as resp:
        return _rbx_maybe_gunzip(resp.read())


def _rbx_get_bytes(url):
    r = _req.Request(url, headers=_roblox_headers())
    with _req.urlopen(r, timeout=8) as resp:
        return _rbx_maybe_gunzip(resp.read())


# ====================== Open Cloud: Toolbox (Creator Store) and experience settings ======================
# The server part of cloud.js (the /api/cloud/* block). The order of methods is the same everywhere: FIRST the Open Cloud
# API key (_roblox_api_key()), and if there is no key or Roblox answered 401/403 — the fallback through the
# account session (.ROBLOSECURITY from «Account»; writing needs X-CSRF-TOKEN). The cookie endpoints at
# Roblox are unofficial/legacy and may change without notice. The key and the cookie go only to
# Roblox and are not returned to the browser. Key permissions: creator-store-product:read (search and details),
# legacy-asset:manage (model download), universe:read / universe:write (settings).
_OC_BASE = 'https://apis.roblox.com'
_OC_TOOLBOX_CATEGORIES = ('Audio', 'Model', 'Decal', 'Plugin', 'MeshPart', 'Video', 'FontFamily')
# Universe fields (cloud/v2) that we allow to be changed from the UI: name -> type
_OC_UNIVERSE_FIELDS = {
    'displayName': str, 'description': str, 'visibility': str,
    'voiceChatEnabled': bool, 'desktopEnabled': bool, 'mobileEnabled': bool,
    'tabletEnabled': bool, 'consoleEnabled': bool, 'vrEnabled': bool,
    'privateServerPriceRobux': int,
}
# what the cookie path can do (develop.roblox.com v1): the other fields are skipped and returned in 'skipped'
_OC_COOKIE_DEVICES = {'desktopEnabled': 'Computer', 'mobileEnabled': 'Phone',
                      'tabletEnabled': 'Tablet', 'consoleEnabled': 'Console'}
_OC_COOKIE_UNIVERSE_FIELDS = ('displayName', 'description', 'visibility') + tuple(_OC_COOKIE_DEVICES)
_OC_CSRF = {'token': ''}


def _oc_parse(status, raw):
    text = _rbx_maybe_gunzip(raw).decode('utf-8', 'replace')
    try:
        return status, json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return status, {'message': text[:300]}


def _oc_call(method, path, body=None, query=None, timeout=30):
    """A request to Open Cloud with x-api-key. Returns (status, data); data is JSON or {'message': text}."""
    key = _roblox_api_key()
    if not key:
        return 400, {'message': _alang('Нет API-ключа: сохраните его в окне «Аккаунт»', 'No API key: save it in the «Account» window')}
    url = _OC_BASE + path
    if query:
        q = {k: v for k, v in query.items() if v not in (None, '')}
        if q:
            url += '?' + _urlparse.urlencode(q)
    headers = {'x-api-key': key, 'Accept': 'application/json', 'Accept-Encoding': 'identity'}
    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    rq = _req.Request(url, data=data, headers=headers, method=method)
    try:
        with _req.urlopen(rq, timeout=timeout) as resp:
            return _oc_parse(resp.status, resp.read())
    except _urlerr.HTTPError as e:
        return _oc_parse(e.code, e.read())


def _oc_csrf_token(force=False):
    """X-CSRF-TOKEN for cookie-based writes: Roblox returns it in the header of a 403 response to a request without a token.
    We take it from auth.roblox.com/v2/logout — without a valid token this request can't sign the account out."""
    if _OC_CSRF['token'] and not force:
        return _OC_CSRF['token']
    rq = _req.Request('https://auth.roblox.com/v2/logout', data=b'', headers=_roblox_headers(), method='POST')
    try:
        with _req.urlopen(rq, timeout=15):
            pass
    except _urlerr.HTTPError as e:
        _OC_CSRF['token'] = e.headers.get('x-csrf-token') or ''
    return _OC_CSRF['token']


def _oc_cookie_call(method, url, body=None, query=None, timeout=30, raw=None, headers=None):
    """A request with the account session. For non-GET it adds X-CSRF-TOKEN and retries once when the token changes.
    body is a JSON body, raw is ready-made bytes (a file upload). Returns (status, data)."""
    if _roblox_cookie() is None:
        return 400, {'message': _alang('Нет входа в аккаунт Roblox (окно «Аккаунт»)', 'No Roblox account sign-in («Account» window)')}
    if query:
        q = {k: v for k, v in query.items() if v not in (None, '')}
        if q:
            url += ('&' if '?' in url else '?') + _urlparse.urlencode(q)
    for attempt in (0, 1):
        h = _roblox_headers()
        data = raw
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            h['Content-Type'] = 'application/json'
        if headers:
            h.update(headers)
        if method != 'GET':
            h['X-CSRF-TOKEN'] = _oc_csrf_token(force=attempt == 1)
            if data is None:
                data = b''
        rq = _req.Request(url, data=data, headers=h, method=method)
        try:
            with _req.urlopen(rq, timeout=timeout) as resp:
                return _oc_parse(resp.status, resp.read())
        except _urlerr.HTTPError as e:
            new_tok = e.headers.get('x-csrf-token')
            if e.code == 403 and method != 'GET' and new_tok and attempt == 0 and new_tok != h.get('X-CSRF-TOKEN'):
                _OC_CSRF['token'] = new_tok
                continue
            return _oc_parse(e.code, e.read())
    return 403, {'message': _alang('CSRF-токен не принят', 'CSRF token was not accepted')}


def _oc_dual(key_fn, cookie_fn):
    """Key first, then cookie. key_fn/cookie_fn -> (status, data). The cookie is tried if there is no key or
    the key returned 401/403. Returns (status, data, via): via is 'api-key' | 'cookie' | None."""
    key_st = key_data = None
    if key_fn and _roblox_api_key():
        key_st, key_data = key_fn()
        if key_st not in (401, 403):
            return key_st, key_data, 'api-key'
    if cookie_fn and _roblox_cookie() is not None:
        st, data = cookie_fn()
        if key_st is not None and not (200 <= st < 300):
            m = data.get('message') if isinstance(data, dict) else data
            data = {'message': f'key: HTTP {key_st}; cookie: HTTP {st}: {m}'}
        return st, data, 'cookie'
    if key_st is not None:
        return key_st, key_data, 'api-key'
    return 400, {'message': _alang('Нет ни API-ключа, ни входа в аккаунт: настройте любой в окне «Аккаунт»', 'Neither an API key nor an account sign-in: set up either in the «Account» window')}, None


def _oc_reply(status, data, via=None):
    ok = 200 <= status < 300
    out = {'ok': ok, 'status': status, 'data': data, 'via': via}
    if not ok:
        msg = data.get('message') if isinstance(data, dict) else None
        out['error'] = f'HTTP {status}: {msg or data}'
        if status in (401, 403) and via == 'api-key':
            out['error'] += _alang(' (проверьте API-ключ и его права)', ' (check the API key and its permissions)')
    return jsonify(out)


@flask_app.route('/api/cloud/toolbox/search')
def api_cloud_toolbox_search():
    """Creator Store search: GET toolbox-service/v2/assets:search (searchCategoryType is required)."""
    cat = request.args.get('category', 'Model')
    if cat not in _OC_TOOLBOX_CATEGORIES:
        return jsonify({'ok': False, 'error': _alang('Неизвестная категория', 'Unknown category')}), 400
    q = {'searchCategoryType': cat, 'query': request.args.get('q', '').strip()[:200],
         'pageToken': request.args.get('pageToken', '')[:500],
         'maxPageSize': request.args.get('maxPageSize', '24')}
    path = '/toolbox-service/v2/assets:search'
    try:
        st, data, via = _oc_dual(lambda: _oc_call('GET', path, query=q),
                                 lambda: _oc_cookie_call('GET', _OC_BASE + path, query=q))
    except Exception as e:
        return jsonify({'ok': False, 'error': f'No connection to Roblox: {e}'}), 502
    return _oc_reply(st, data, via)


@flask_app.route('/api/cloud/toolbox/asset/<asset_id>')
def api_cloud_toolbox_asset(asset_id):
    """Creator Store asset details: GET toolbox-service/v2/assets/{id}."""
    if not asset_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('ID ассета должен быть числом', 'Asset ID must be a number')}), 400
    path = f'/toolbox-service/v2/assets/{asset_id}'
    try:
        st, data, via = _oc_dual(lambda: _oc_call('GET', path),
                                 lambda: _oc_cookie_call('GET', _OC_BASE + path))
    except Exception as e:
        return jsonify({'ok': False, 'error': f'No connection to Roblox: {e}'}), 502
    return _oc_reply(st, data, via)


@flask_app.route('/api/cloud/toolbox/insert', methods=['POST'])
@_collab_track('import')
def api_cloud_toolbox_insert():
    """Inserting a model from the Creator Store into the scene: download (Open Cloud Asset Delivery by key first,
    then AssetDelivery with the account session) -> a binary .rbxm -> import_rbxm (like «Import .rbxm»).
    Body: {assetId, parent}."""
    import tempfile
    data = request.get_json(silent=True) or {}
    asset_id = str(data.get('assetId', '')).strip()
    if not asset_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('ID ассета должен быть числом', 'Asset ID must be a number')}), 400
    parent = data.get('parent')
    try:
        parent = int(parent) if parent not in (None, '') else None
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': _alang('Некорректный родитель', 'Invalid parent')}), 400
    raw, errors = None, []
    for name, fn in (('key', _rbx_get_bytes_opencloud), ('cookie', _rbx_get_place_bytes_cookie)):
        try:
            got = fn(asset_id)
        except _urlerr.HTTPError as e:
            errors.append(f'{name}: HTTP {e.code}')
            continue
        except Exception as e:
            errors.append(f'{name}: {e}')
            continue
        if got is not None:
            raw = got
            break
    if raw is None:
        if not errors:
            return jsonify({'ok': False, 'error': _alang('Нет ни API-ключа, ни входа в аккаунт: настройте любой в окне «Аккаунт»', 'Neither an API key nor an account sign-in: set up either in the «Account» window')}), 400
        hint = _alang(' (для ключа нужно право legacy-asset:manage)', ' (the key needs the legacy-asset:manage permission)') if 'key: HTTP 40' in ' '.join(errors) else ''
        return jsonify({'ok': False, 'error': _alang('Не удалось скачать ассет — ', 'Could not download the asset — ') + '; '.join(errors) + hint}), 502
    if raw[:8] != b'<roblox!':
        return jsonify({'ok': False, 'error': _alang('Это не бинарная модель .rbxm (XML-формат импорт не поддерживает)', 'This is not a binary .rbxm model (the XML format is not supported by import)')}), 400
    with tempfile.NamedTemporaryFile(suffix='.rbxm', delete=False) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name
    try:
        return _finish_rbxm_import(tmp_path, parent)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _oc_cookie_universe_get(uid):
    """Cookie path: develop.roblox.com/v1/universes/{id}/configuration -> the Universe shape from cloud/v2.
    Fields that aren't there (voiceChat, VR, private server price) are simply absent from the response."""
    st, d = _oc_cookie_call('GET', f'https://develop.roblox.com/v1/universes/{uid}/configuration')
    if not (200 <= st < 300) or not isinstance(d, dict):
        return st, d
    devs = d.get('playableDevices') or []
    pt = str(d.get('privacyType') or '').lower()
    return 200, {
        'displayName': d.get('name') or '', 'description': d.get('description') or '',
        'visibility': 'PUBLIC' if pt == 'public' else 'PRIVATE' if pt == 'private' else 'VISIBILITY_UNSPECIFIED',
        'desktopEnabled': 'Computer' in devs, 'mobileEnabled': 'Phone' in devs,
        'tabletEnabled': 'Tablet' in devs, 'consoleEnabled': 'Console' in devs,
    }


def _oc_cookie_universe_patch(uid, body):
    """Cookie path for PATCH: name/description/devices — PATCH develop.roblox.com/v1/universes/{id}/configuration
    (devices: we first read the current list and change only the ones sent), access — POST .../activate|deactivate.
    The other fields are skipped (returned in 'skipped')."""
    base = f'https://develop.roblox.com/v1/universes/{uid}'
    skipped = [k for k in body if k not in _OC_COOKIE_UNIVERSE_FIELDS]
    cfg = {}
    if 'displayName' in body:
        cfg['name'] = body['displayName']
    if 'description' in body:
        cfg['description'] = body['description']
    if any(k in body for k in _OC_COOKIE_DEVICES):
        st, d = _oc_cookie_call('GET', base + '/configuration')
        if not (200 <= st < 300) or not isinstance(d, dict):
            return st, d
        devs = set(d.get('playableDevices') or [])
        for k, name in _OC_COOKIE_DEVICES.items():
            if k in body:
                (devs.add if body[k] else devs.discard)(name)
        cfg['playableDevices'] = [n for n in _OC_COOKIE_DEVICES.values() if n in devs]
    last = (200, {})
    if cfg:
        last = _oc_cookie_call('PATCH', base + '/configuration', body=cfg)
        if not (200 <= last[0] < 300):
            return last
    if 'visibility' in body:
        last = _oc_cookie_call('POST', base + ('/activate' if body['visibility'] == 'PUBLIC' else '/deactivate'))
        if not (200 <= last[0] < 300):
            return last
    out = last[1] if isinstance(last[1], dict) else {}
    out['skipped'] = skipped
    return 200, out


@flask_app.route('/api/cloud/universe/<universe_id>', methods=['GET', 'PATCH'])
def api_cloud_universe(universe_id):
    """Experience settings. Open Cloud cloud/v2/universes/{id} first (key), then develop.roblox.com v1
    (cookie; it can't do all fields — the rest go to 'skipped'). PATCH accepts only fields from _OC_UNIVERSE_FIELDS;
    updateMask is assembled from the fields sent."""
    if not universe_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('Universe ID должен быть числом', 'Universe ID must be a number')}), 400
    path = f'/cloud/v2/universes/{universe_id}'
    try:
        if request.method == 'GET':
            st, data, via = _oc_dual(lambda: _oc_call('GET', path), lambda: _oc_cookie_universe_get(universe_id))
            return _oc_reply(st, data, via)
        src = request.get_json(silent=True) or {}
        body = {}
        for k, typ in _OC_UNIVERSE_FIELDS.items():
            if k not in src:
                continue
            v = src[k]
            if typ is int:
                try:
                    v = int(v)
                except (TypeError, ValueError):
                    return jsonify({'ok': False, 'error': f'{k}: an integer is required'}), 400
            elif not isinstance(v, typ):
                return jsonify({'ok': False, 'error': f'{k}: wrong type'}), 400
            body[k] = v
        if body.get('visibility') not in (None, 'PUBLIC', 'PRIVATE'):
            return jsonify({'ok': False, 'error': _alang('visibility: PUBLIC или PRIVATE', 'visibility: PUBLIC or PRIVATE')}), 400
        if not body:
            return jsonify({'ok': False, 'error': _alang('Нечего обновлять', 'Nothing to update')}), 400
        st, data, via = _oc_dual(
            lambda: _oc_call('PATCH', path, body=body, query={'updateMask': ','.join(body)}),
            lambda: _oc_cookie_universe_patch(universe_id, body))
        return _oc_reply(st, data, via)
    except Exception as e:
        return jsonify({'ok': False, 'error': f'No connection to Roblox: {e}'}), 502


@flask_app.route('/api/cloud/universe/<universe_id>/restart', methods=['POST'])
def api_cloud_universe_restart(universe_id):
    """Restarting servers after publishing: POST cloud/v2/universes/{id}:restartServers (key only —
    this method has no cookie analog)."""
    if not universe_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('Universe ID должен быть числом', 'Universe ID must be a number')}), 400
    if not _roblox_api_key():
        return jsonify({'ok': False, 'error': _alang('Перезапуск серверов работает только с API-ключом (право universe:write)', 'Restarting servers works only with an API key (universe:write permission)')}), 400
    try:
        st, data = _oc_call('POST', f'/cloud/v2/universes/{universe_id}:restartServers', body={})
    except Exception as e:
        return jsonify({'ok': False, 'error': f'No connection to Roblox: {e}'}), 502
    return _oc_reply(st, data, 'api-key')


@flask_app.route('/cloud.js')
def cloud_js():
    try:
        with open('cloud.js', 'r', encoding='utf-8') as f:
            src = f.read()
    except OSError:
        src = '/* cloud.js not found */'
    return _no_cache(Response(src, mimetype='application/javascript'))


# The asset bytes cache — pictures/sounds in the game (SongIcon.Image, the song
# audio tracks) were loaded from this endpoint again EVERY time, including
# after the app itself was restarted: _ASSET_PROXY_CACHE was only
# in-memory and was reset on every process start — i.e. every
# new launch of the app again honestly went to Roblox over the network for the same
# pictures/tracks it had downloaded a minute ago in the previous
# launch. Now there is also a persistent disk cache under it (RSW_DATA_DIR/
# asset_cache — the same place where roblox_auth.json already lies), surviving a
# restart: the in-memory cache — for repeats WITHIN one launch
# (without even going to disk), the disk one — for repeats BETWEEN launches
# (without going to the network). We deliberately don't limit the disk size — it is
# essentially a local copy of what is already stored in the .rbxl itself
# as asset ids, not something growing uncontrollably with every new
# file; if it needs cleaning, it is just a folder that can be
# deleted by hand.
_ASSET_PROXY_CACHE = {}
_ASSET_PROXY_CACHE_MAX = 64


# --- Disk cache compression -------------------------------------------------
# Cache files come in three kinds (the kind is determined by name/signature, so nothing
# breaks if the folder holds a mix):
#   <name>        — raw bytes (the old format, before compression);
#   <name>.zst    — zstd (if the zstandard package is installed — it is already needed for .rbxl);
#   <name>.gz     — gzip (a fallback without zstandard).
# Reading understands all three, and also a raw file with a ready zstd/gzip
# stream inside (detected by signature), so caches already compressed by someone are picked up.
# Writing compresses only what really shrinks: JPEG/MP3/OGG/WEBP are already compressed, and
# a compressed copy is kept only with a gain of at least 10% — otherwise the raw file stays.
# Old uncompressed files are compressed by a background task (cache_compact), once per file.
import gzip as _cgzip
import threading as _cthreading
try:
    import zstandard as _czstd
except Exception:  # no package (for example, a trimmed build) — we work through gzip
    _czstd = None

_CACHE_ZSTD_MAGIC = b'\x28\xb5\x2f\xfd'
_CACHE_GZIP_MAGIC = b'\x1f\x8b'
_CACHE_CODEC_SUFFIXES = ('.zst', '.gz')
_CACHE_SKIP_COMPRESS_CT = {'image/jpeg', 'audio/mpeg', 'audio/ogg', 'image/webp', 'video/mp4'}
_CACHE_MIN_SIZE = 256        # smaller — no point
_CACHE_MIN_GAIN = 0.90       # the compressed copy must be ≤ 90% of the original
_CACHE_SKIP_INDEX = 'compact_skip.json'   # names that we have already tried and failed to compress (we don't retry on every launch)
_cache_compact_started = False
_cache_compact_lock = _cthreading.Lock()


def _cache_compress(raw):
    """-> (suffix, bytes): zstd if available, otherwise gzip."""
    if _czstd is not None:
        return '.zst', _czstd.ZstdCompressor(level=6).compress(raw)
    return '.gz', _cgzip.compress(raw, 6, mtime=0)


def _cache_decode(data):
    """Decompresses a zstd/gzip stream by signature. An exception if it can't be decompressed."""
    if data[:4] == _CACHE_ZSTD_MAGIC:
        if _czstd is None:
            raise RuntimeError(_alang('запись сжата zstd, а пакет zstandard не установлен', 'the entry is zstd-compressed, but the zstandard package is not installed'))
        return _czstd.ZstdDecompressor().decompressobj().decompress(data)
    if data[:2] == _CACHE_GZIP_MAGIC:
        return _cgzip.decompress(data)
    raise ValueError(_alang('не сжатый поток', 'not a compressed stream'))


def _cache_read_file(f):
    """The bytes of a cache file with transparent decompression; None — can't read/decompress (= a cache miss)."""
    try:
        data = f.read_bytes()
    except OSError:
        return None
    coded = f.name.endswith(_CACHE_CODEC_SUFFIXES)
    if coded or data[:4] == _CACHE_ZSTD_MAGIC or data[:2] == _CACHE_GZIP_MAGIC:
        try:
            return _cache_decode(data)
        except Exception:
            # marked .zst/.gz but corrupted/undecompressable — a miss; a raw file that merely
            # looks like a stream by its first bytes is returned as is
            return None if coded else data
    return data


def _cache_find(base):
    """The cache file for <base> in any form (compressed is preferred — it is newer after compression) or None."""
    for sfx in _CACHE_CODEC_SUFFIXES + ('',):
        f = base.with_name(base.name + sfx)
        if f.is_file():
            return f
    return None


def _cache_store(base, raw, content_type):
    """Atomically writes <base>[.zst|.gz]. Returns the size of the written file or None on error."""
    data, suffix = raw, ''
    if content_type not in _CACHE_SKIP_COMPRESS_CT and len(raw) >= _CACHE_MIN_SIZE:
        try:
            sfx, comp = _cache_compress(raw)
            if len(comp) <= len(raw) * _CACHE_MIN_GAIN:
                data, suffix = comp, sfx
        except Exception:
            pass  # compression failed — we write as is
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
    """'123__image_png.bin(.zst)' -> 'image/png'; for other files — application/octet-stream."""
    for sfx in _CACHE_CODEC_SUFFIXES:
        if name.endswith(sfx):
            name = name[:-len(sfx)]
    if name.endswith('.json'):
        return 'application/json'
    if '__' in name and name.endswith('.bin'):
        return name[:-4].split('__', 1)[1].replace('_', '/')
    return 'application/octet-stream'


def cache_stats():
    """Cache sizes: how many files/bytes raw and compressed (and how much they would take without compression — for compressed ones
    taking the decompressed content size from the zstd/gzip header is not cheap, so we show the actual one)."""
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
    """Compresses old uncompressed cache files. Safe for parallel reading: the compressed copy is written first
    (atomically), then the raw original is deleted; the modification date is preserved (the avatar TTL is computed from it).
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
                # an «already compressed» file under the name .bin — we rename it to its real kind, recompressing nothing
                target = f.with_name(name + ('.zst' if raw[:4] == _CACHE_ZSTD_MAGIC else '.gz'))
                os.replace(f, target)
                done += 1
                continue
            if len(raw) < _CACHE_MIN_SIZE:
                skip[name] = stt.st_size; skip_changed = True
                continue
            sfx, comp = _cache_compress(raw)
            if len(comp) > len(raw) * _CACHE_MIN_GAIN:
                skip[name] = stt.st_size; skip_changed = True   # doesn't shrink — we don't try again
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
            continue  # one problematic file must not stop the others
    if skip_changed:
        try:
            idx_path.write_text(_json.dumps(skip), encoding='utf-8')
        except OSError:
            pass
    return {'compressed': done, 'saved_bytes': saved, 'skipped': skipped}


def _start_cache_compaction_once():
    """Once per launch: a background task compresses old cache files (disabled by RSW_CACHE_COMPACT=0)."""
    global _cache_compact_started
    with _cache_compact_lock:
        if _cache_compact_started or os.environ.get('RSW_CACHE_COMPACT') == '0':
            return
        _cache_compact_started = True

    def _run():
        import time as _t
        _t.sleep(10)   # we don't interfere with the app start and the first requests
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
    """Looks for an asset on disk — the file name encodes the content type, so as not to
    create a separate metadata file for every asset. Compressed entries
    (.zst/.gz) and raw ones are read the same way."""
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
            return  # already exists (in any form)
        safe_ct = content_type.replace('/', '_')
        _cache_store(d / f'{asset_id}__{safe_ct}.bin', raw_bytes, content_type)
    except Exception:
        pass  # the disk cache is best-effort, it must not fail the request itself


@flask_app.route('/api/cache/stats')
def api_cache_stats():
    return jsonify({'ok': True, **cache_stats()})


@flask_app.route('/api/cache/compact', methods=['POST'])
def api_cache_compact():
    """Compress old cache files now (synchronously) and return the result + the new statistics."""
    return jsonify({'ok': True, **cache_compact(), 'stats': cache_stats()})


@flask_app.route('/api/union_mesh')
def api_union_mesh():
    """UnionOperation geometry: {'position': [...], 'normal': [...], 'triangles': N}.
    Coordinates are local (relative to the union's CFrame). 404 — no mesh or the
    format isn't supported (the client keeps the box)."""
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
            # The mesh is stored in InitialSize, while the part's Size could have been changed (scaling) — in Roblox
            # the union's geometry is stretched by Size/InitialSize along each axis.
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
                    nn = []   # the normal under non-uniform scaling: divide by k and normalize
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
    """Assets by id are immutable (rbxassetid:// doesn't change content under
    the same id) — previously the response went out with no Cache-Control at all, and the browser
    honestly re-requested the same picture/sound on every
    GUI redraw (for example song cards in the menu) through the same
    local server, although the bytes are guaranteed to be the same."""
    resp = Response(raw_bytes, mimetype=content_type)
    resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return resp


@flask_app.route('/api/asset-export', methods=['POST'])
def api_asset_export():
    """Puts an asset (mesh/texture/sound) into a temporary file in the app's data folder — for the Android bridge
    AndroidBridge.exportRbxlFile (the system «Save as» dialog, the user picks the folder themselves).
    Takes the bytes the same way as /api/asset-proxy (memory -> disk -> network)."""
    body = request.get_json(silent=True) or {}
    data_dir = Path(os.environ.get('RSW_DATA_DIR') or str(Path(__file__).parent)).resolve()
    ids = []
    for x in (body.get('ids') or []):
        mm = _re.search(r'\d+', str(x))
        if mm and mm.group() not in ids:
            ids.append(mm.group())
    if len(ids) > 1:
        # Several assets — one ZIP (convenient to deliver as a single file). Unavailable ones are skipped and listed.
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
            return jsonify({'ok': False, 'error': _alang('ни один ассет не получен: ', 'no asset was received: ') + ', '.join(missing)}), 502
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


_ASSET_THUMB_CACHE = {}


@flask_app.route('/api/asset-proxy')
def api_asset_proxy():
    """Proxy download of a Roblox asset by id — turns rbxassetid://N
    (what really lies in Image/SoundId of an ImageLabel/Sound in the file) into a
    real downloadable URL for the browser. A proxy is needed, not a
    direct fetch from the client to assetdelivery.roblox.com/apis.roblox.com,
    because of CORS — those domains don't send headers that allow the browser to
    read the response from an arbitrary origin.
    
    Order of attempts (both branches are really tried, not "either/or"):
    1) Open Cloud (x-api-key, see _rbx_get_bytes_opencloud) — the official
    path, if ROBLOX_API_KEY is configured.
    2) Cookie/anonymous GET on /v1/asset/?id= (_roblox_headers itself decides
    whether to send the cookie or not — see _roblox_cookie) — tried if step 1
    is not configured OR is configured but really failed (network, invalid key,
    an asset outside the key's permissions, etc.). Since April 2, 2025 Roblox requires
    authorization on ANY request to AssetDelivery, so without a key AND
    without a cookie this step will usually return 401 too — then we return
    BOTH errors so it is immediately visible what exactly didn't work."""
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
        # We pull into in-memory too — the next requests in THIS session
        # won't even read the file from disk.
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

    # An anonymous fallback path only for GUI icons (thumb=1): since 2025 AssetDelivery requires authorization, while
    # public thumbnails (thumbnails.roblox.com + CDN) are served without a cookie or key. We put them into a separate cache — otherwise a
    # PNG thumbnail would settle under an id that is later requested as a mesh/sound.
    if raw_bytes is None and request.args.get('thumb'):
        thumb = _ASSET_THUMB_CACHE.get(asset_id)
        if thumb is None:
            try:
                d = _rbx_get_json('https://thumbnails.roblox.com/v1/assets?assetIds=' + asset_id +
                                  '&returnPolicy=PlaceHolder&size=420x420&format=Png&isCircular=false')
                row = (d.get('data') or [{}])[0] if isinstance(d, dict) else {}
                if row.get('state') == 'Completed' and row.get('imageUrl'):
                    thumb = _rbx_get_bytes(row['imageUrl'])
                    if len(_ASSET_THUMB_CACHE) > 300:
                        _ASSET_THUMB_CACHE.pop(next(iter(_ASSET_THUMB_CACHE)))
                    _ASSET_THUMB_CACHE[asset_id] = thumb
            except Exception as e:
                cookie_error = (cookie_error or '') + f' | thumbnail: {e}'
        if thumb:
            return _asset_response(thumb, 'image/png' if thumb[:4] == b'\x89PNG' else 'image/jpeg')

    if raw_bytes is None:
        parts = []
        if opencloud_error:
            parts.append(f'Open Cloud: {opencloud_error}')
        if cookie_error:
            has_cookie = _roblox_cookie() is not None
            parts.append(
                f'{"cookie" if has_cookie else "anonymous (no cookie)"}: {cookie_error}')
        return Response('asset fetch failed — ' + '; '.join(parts), status=502)

    # An asset may turn out to be not an image but an XML wrapper (Decal, Shirt, Pants,
    # Texture): the id of the real image lies inside. We follow the link
    # (no deeper than two levels) — otherwise <img>/TextureLoader got XML and
    # couldn't show it (clothing textures didn't appear on the body).
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

    # The content type — by the byte signature (see the same trick in the removed
    # asset/fetch feature): Roblox serves raw bytes of the picture/sound without
    # a header that could simply be carried over as is here.
    if raw_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        content_type = 'image/png'
    elif raw_bytes[:3] == b'\xff\xd8\xff':
        content_type = 'image/jpeg'
    elif raw_bytes[:4] == b'OggS':
        content_type = 'audio/ogg'
    elif raw_bytes[:3] == b'ID3' or (raw_bytes[:1] == b'\xff' and len(raw_bytes) > 1 and (raw_bytes[1] & 0xe0) == 0xe0):
        # An MP3 without an ID3 tag starts right with a frame: the 11-bit sync word
        # 0xFFE (the first byte FF, the second byte's top 3 bits are
        # ones too) — the low bits of the second byte encode the MPEG version/layer
        # and VARY from file to file (0xFB is just ONE particular
        # variant). Previously exactly this one variant was checked byte for byte,
        # so any track with another version/bitrate quietly went out as
        # application/octet-stream — a browser refuses to play that
        # ("Failed to load because no supported source was found").
        content_type = 'audio/mpeg'
    elif raw_bytes[:4] == b'RIFF' and raw_bytes[8:12] == b'WEBP':
        # RIFF — a common container format: WAV and WEBP BOTH start with
        # "RIFF", differing only by the 4-byte format tag at
        # offset 8 ("WAVE" versus "WEBP"). Previously only the
        # WAV case got here, while Roblox really serves some textures as WEBP —
        # such a picture went out with the type audio/wav, and TextureLoader/<img>
        # naturally couldn't decode it ("Failed to load part texture").
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
    """Roblox's 8 CDN nodes are equivalent — here a short timeout per node
    (8 s), so that one hung node doesn't turn a download into minutes
    of waiting: the total worst case is 8×8 s = 64 s per file, which is
    acceptable, and in practice the very first live node answers almost at once."""
    last_err = None
    for n in range(8):
        try:
            return _rbx_get_bytes(f'https://t{n}.rbxcdn.com/{hash_value}')
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(last_err or f'Could not download {hash_value}')


@flask_app.route('/api/roblox/avatar3d/status')
def api_roblox_avatar3d_status():
    """A single quick non-blocking poll of the generation state at Roblox —
    called by the client periodically (see doDownloadAvatar3d in index.html),
    rather than waited for in one long request. Roblox generates the 3D model
    asynchronously and it can take from a few seconds to ~a minute — previously we
    waited for it in one request with a fixed timeout, because of which, with
    slow generation, the request was cut off with an unclear error."""
    user_id = request.args.get('userId', '').strip()
    if not user_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('userId должен быть числом', 'userId must be a number')}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': _alang('Сначала войдите в аккаунт Roblox.', 'Sign in to your Roblox account first.')}), 401
    try:
        resp = _rbx_get_json(
            f'https://thumbnails.roblox.com/v1/users/avatar-3d?userId={user_id}')

        if isinstance(resp, dict) and 'data' in resp and resp['data']:
            item = resp['data'][0]
        elif isinstance(resp, dict) and 'targetId' in resp and 'state' in resp:
            # Roblox sometimes serves this endpoint without the {"data":[...]} wrapper
            # — as a flat object directly.
            item = resp
        elif isinstance(resp, dict) and resp.get('errors'):
            reason = resp['errors'][0].get('message', _alang('нет описания', 'no description'))
            return jsonify({
                'ok': False,
                'error': reason,
                'message': f'Roblox rejected the request: {reason}. Try signing out and signing in again.',
            }), 502
        else:
            # An unfamiliar format — we show the whole raw response so that
            # it is possible to understand what Roblox really sent (for example,
            # an anti-bot check HTML page instead of JSON).
            raw = json.dumps(resp, ensure_ascii=False)[:400]
            return jsonify({
                'ok': False,
                'error': 'unexpected_response_shape',
                'message': f"Roblox returned a response format the script does not understand. Raw response: {raw}",
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
    """Called by the client ONLY after /status returned
    ready=true — immediately downloads obj/mtl/textures from the already ready
    bundleUrl (without waiting again) and packs them into ONE .zip
    written to disk (not base64 in JSON — see below).
    
    userId is needed for the file name, savePath is the folder to put the zip in
    (on Android the client passes window.AndroidBridge.getDataDir(),
    because the server can't write directly to a place chosen by the user —
    it has no access to the SAF Uri; see androidSaveConfirm() in
    index.html, the same pattern already used for .rbxl).
    
    Previously the files were returned as base64 inside JSON, and on the client
    an <a download> with a blob: URL was created — inside Android WebView this is
    NOT a real download, the link was just "clicked into nowhere" and
    the user didn't understand where the files went."""
    import zipfile
    import tempfile as _tempfile

    bundle_url = request.args.get('bundleUrl', '').strip()
    user_id = request.args.get('userId', '').strip() or 'unknown'
    save_dir = request.args.get('savePath', '').strip()
    if not bundle_url.startswith('https://'):
        return jsonify({'ok': False, 'error': _alang('bundleUrl отсутствует или некорректен', 'bundleUrl is missing or invalid')}), 400
    if not save_dir:
        return jsonify({'ok': False, 'error': _alang('savePath отсутствует', 'savePath is missing')}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': _alang('Сначала войдите в аккаунт Roblox.', 'Sign in to your Roblox account first.')}), 401
    try:
        bundle = _rbx_get_json(bundle_url)

        # obj, mtl and each texture are independent downloads from different
        # CDN nodes; we parallelize them instead of a sequential loop so that
        # the whole process doesn't stretch to the sum of the time of all files.
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

        # BUG FIX: Roblox serves .mtl with texture references WITHOUT
        # an extension (for example "map_Kd 30DAY-abc123"), while we save the files
        # themselves as "30DAY-abc123.png" — without this fix Blender and
        # other viewers don't find the textures on import. We append
        # ".png" to every reference that matches one of the hashes.
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
        # For importing straight into the editor's 3D scene the client doesn't need
        # another trip to disk/network — we return the OBJ/MTL text and the
        # textures right away as base64 (a data URL). This does NOT duplicate the zip write —
        # the zip is needed anyway for the "just download to my disk" variant.
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
    """Color3 {'r','g','b'} (0..1) -> [r,g,b] or None."""
    if isinstance(c, dict) and all(k in c for k in ('r', 'g', 'b')):
        try:
            v = [float(c['r']), float(c['g']), float(c['b'])]
            if max(v) > 1.5:  # in case of 0..255
                v = [x / 255.0 for x in v]
            return [round(max(0.0, min(1.0, x)), 4) for x in v]
        except (TypeError, ValueError):
            return None
    return None


def _clock_hours(lp):
    """ClockTime (hours, float) or TimeOfDay 'HH:MM:SS' -> hours 0..24."""
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
    """The map's Lighting/Atmosphere settings and a list of PointLight/SpotLight with
    positions — the client builds light and a cheap glow from them (in a single Points)."""
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
        if not _ref_in_world(r, pmap, r2c):
            continue    # lamps of room templates from ServerStorage took MAX_MAP_LIGHTS slots and lit up empty space
        # the position — from the nearest ancestor with a CFrame (a Part, or an Attachment inside a Part)
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
    # The skybox (six faces) and color correction — only what can be applied without post-processing
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
    """parent_map inverted into ref -> [children]; cached per parsed map."""
    pid = id(parsed)
    if _children_cache['pid'] != pid:
        m = {}
        for ch, pa in parsed['parent_map'].items():
            m.setdefault(pa, []).append(ch)
        _children_cache.update(pid=pid, map=m)
    return _children_cache['map']


def _cf12(cf):
    """CFrame -> [x, y, z, r00..r22] (a rotation matrix by rows)."""
    return [float(v) for v in get_pos(cf)] + [float(v) for v in get_rot_matrix(cf)]


@flask_app.route('/api/outfit_item/<int:ref>')
def api_outfit_item(ref):
    """Accessory / BodyColors data FROM THE FILE for drawing on the character: the map's script
    clones them into the Character (an outfit morph), and the client draws by the original's ref."""
    parsed = state.get('parsed')
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('карта не открыта', 'map is not open')})
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
        return jsonify({'ok': False, 'error': _alang('не Accessory/BodyColors', 'not an Accessory/BodyColors')})

    parts = [k for k in kids.get(ref, []) if r2c.get(k) in ('Part', 'MeshPart')]
    handle = next((k for k in parts if props.get(k, {}).get('Name') == 'Handle'), parts[0] if parts else None)
    if handle is None:
        return jsonify({'ok': False, 'error': _alang('у аксессуара нет Handle', 'the accessory has no Handle')})
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


@flask_app.route('/api/tool_item/<int:ref>')
def api_tool_item(ref):
    """A Tool's appearance FROM THE FILE for drawing in the character's hand: all visible parts of the Tool (Handle and the rest)
    with a CFrame relative to Handle + Tool.Grip. The client builds the model by the original's ref and attaches it to the right arm."""
    parsed = state.get('parsed')
    if not parsed:
        return jsonify({'ok': False, 'error': _alang('карта не открыта', 'map is not open')})
    r2c, props = parsed['referent_to_class'], parsed['props']
    if r2c.get(ref) != 'Tool':
        return jsonify({'ok': False, 'error': _alang('не Tool', 'not a Tool')})
    kids = _children_of(parsed)
    BASE = ('Part', 'MeshPart', 'WedgePart', 'CornerWedgePart', 'TrussPart')
    parts, stack = [], list(kids.get(ref, []))
    while stack and len(parts) < 80:
        k = stack.pop(0)
        stack = list(kids.get(k, [])) + stack
        if r2c.get(k) in BASE and isinstance(props.get(k, {}).get('CFrame'), dict):
            parts.append(k)
    handle = next((k for k in kids.get(ref, []) if r2c.get(k) in BASE and props[k].get('Name') == 'Handle'),
                  parts[0] if parts else None)
    if handle is None:
        return jsonify({'ok': False, 'error': _alang('у Tool нет Handle', 'the Tool has no Handle')})
    hcf = props[handle]['CFrame']
    hp, hr = get_pos(hcf), get_rot_matrix(hcf)

    def rel_cf(cf):  # Handle^-1 * part -> [x, y, z, r00..r22]
        pp, pr = get_pos(cf), get_rot_matrix(cf)
        d = [pp[i] - hp[i] for i in range(3)]
        pos = [sum(hr[r * 3 + i] * d[r] for r in range(3)) for i in range(3)]
        rot = [sum(hr[r * 3 + i] * pr[r * 3 + j] for r in range(3)) for i in range(3) for j in range(3)]
        return [float(v) for v in pos + rot]

    out = []
    for k in parts:
        pr = props[k]
        tr = safe_float(pr.get('Transparency', 0), 0)
        if tr >= 0.99:
            continue  # an invisible Handle
        sz = pr.get('Size') if isinstance(pr.get('Size'), dict) else {}
        size = [safe_float(sz.get('x', 1), 1), safe_float(sz.get('y', 1), 1), safe_float(sz.get('z', 1), 1)]
        mesh = {'kind': 'box'}
        if r2c[k] == 'MeshPart':
            mid = _rbxassetid_num(pr.get('MeshId'))
            if mid:
                mesh = {'kind': 'meshpart', 'meshId': mid,
                        'textureId': _rbxassetid_num(pr.get('TextureID') or pr.get('TextureId'))}
        else:
            for c in kids.get(k, []):
                if r2c.get(c) == 'SpecialMesh':
                    sp = props[c]
                    mid = _rbxassetid_num(sp.get('MeshId'))
                    if mid:
                        sc, of = sp.get('Scale') or {}, sp.get('Offset') or {}
                        mesh = {'kind': 'special', 'meshId': mid,
                                'textureId': _rbxassetid_num(sp.get('TextureId')),
                                'scale': [safe_float(sc.get('x', 1), 1), safe_float(sc.get('y', 1), 1), safe_float(sc.get('z', 1), 1)],
                                'offset': [safe_float(of.get('x', 0), 0), safe_float(of.get('y', 0), 0), safe_float(of.get('z', 0), 0)]}
                    break
        shape = pr.get('shape', pr.get('Shape'))
        out.append({'ref': k, 'name': pr.get('Name'), 'size': size, 'color': get_part_color(pr), 'transparency': tr,
                    'shape': {0: 'sphere', 2: 'cylinder'}.get(shape, 'box') if r2c[k] == 'Part' else 'box',
                    'mesh': mesh, 'cf': rel_cf(pr['CFrame'])})
    if not out:
        return jsonify({'ok': False, 'error': _alang('у Tool нет видимых деталей', 'the Tool has no visible parts')})
    # joints (Motor6D/Weld): the client moves Part1 relative to the Handle when a script changes joint.C0 (a key press etc.)
    joints, st = [], list(kids.get(ref, []))
    while st:
        k = st.pop()
        st.extend(kids.get(k, []))
        if r2c.get(k) in ('Motor6D', 'Weld', 'ManualWeld'):
            try:
                joints.append({'ref': k, 'part0': int(props[k].get('Part0')), 'part1': int(props[k].get('Part1'))})
            except (TypeError, ValueError):
                pass
    grip = props[ref].get('Grip')
    return jsonify({'ok': True, 'cls': 'Tool', 'name': props[ref].get('Name'), 'parts': out, 'joints': joints,
                    'grip': _cf12(grip) if isinstance(grip, dict) else None})


@flask_app.route('/api/roblox/me')
def api_roblox_me():
    """The nickname/ID of the account that is signed in (the .ROBLOSECURITY cookie).
    No cookie or it has gone stale — loggedIn=False (the client then draws
    the standard Roblox «noob» instead of the player's avatar)."""
    if _roblox_cookie() is None:
        return jsonify({'ok': True, 'loggedIn': False})
    try:
        d = _rbx_get_json('https://users.roblox.com/v1/users/authenticated')
        uid = d.get('id') if isinstance(d, dict) else None
        if not uid:
            raise RuntimeError(_alang('в ответе нет id', 'no id in the response'))
        return jsonify({'ok': True, 'loggedIn': True, 'userId': uid,
                        'name': d.get('name') or '',
                        'displayName': d.get('displayName') or d.get('name') or ''})
    except Exception as e:
        # HTTP 401 etc. — the cookie is invalid: we consider that there is no sign-in
        return jsonify({'ok': True, 'loggedIn': False, 'error': str(e)})


PLAY_AVATAR_TTL = 7 * 24 * 3600  # a week: an avatar changes rarely, while Roblox's generation is slow (up to a minute of waiting). A stale copy is returned later too (allowStale=1) if the refresh failed


def _play_avatar_cache_path(user_id):
    return _asset_cache_dir() / f'play_avatar_{user_id}.json'


@flask_app.route('/api/roblox/play-avatar')
def api_roblox_play_avatar():
    """A 3D avatar for the character in Play (OBJ+MTL+textures as one JSON, without a zip).
    1) userId without bundleUrl — returns the disk cache if it is fresh (or with allowStale=1 — any), otherwise
    {ok, cached: false} (the client then polls /avatar3d/status and
    comes here again with a bundleUrl);
    2) userId + bundleUrl — downloads, puts it into the cache and returns it."""
    import time as _time
    user_id = request.args.get('userId', '').strip()
    if not user_id.isdigit():
        return jsonify({'ok': False, 'error': _alang('userId должен быть числом', 'userId must be a number')}), 400
    cp = _play_avatar_cache_path(user_id)
    try:
        cf = _cache_find(cp)
        allow_stale = request.args.get('allowStale', '') == '1'   # the client asks for a copy of any age (the refresh failed)
        if cf is not None and (allow_stale or _time.time() - cf.stat().st_mtime < PLAY_AVATAR_TTL):
            cached_json = _cache_read_file(cf)
            if cached_json is not None:
                return Response(cached_json, mimetype='application/json')
    except OSError:
        pass
    bundle_url = request.args.get('bundleUrl', '').strip()
    if not bundle_url:
        return jsonify({'ok': True, 'cached': False})
    if not bundle_url.startswith('https://'):
        return jsonify({'ok': False, 'error': _alang('bundleUrl некорректен', 'bundleUrl is invalid')}), 400
    if _roblox_cookie() is None:
        return jsonify({'ok': False, 'error': 'not_logged_in',
                        'message': _alang('Сначала войдите в аккаунт Roblox.', 'Sign in to your Roblox account first.')}), 401
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
        # as in /avatar3d/fetch: Roblox writes textures in .mtl without an extension
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
            for sfx in ('',) + _CACHE_CODEC_SUFFIXES:   # we replace the old entry (in any form) with a new one
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


SERVER_BUILD = '2026-11-10 · tween-easing'   # must match BUILD_LABEL in script.js and --css-build in style.css


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


# Lua Output log files — each Play run writes to its own file under logs/, and
# not only to the browser Output panel (which disappears when the
# tab is closed/the page is refreshed). One JSON entry per line — convenient both
# to look at by eye (less/tail) and to parse with a script if desired.
LOG_DIR = Path(__file__).resolve().parent / 'logs'
_log_state = {'file': None, 'session': None}


def _current_log_path():
    # A new file for every Play session (see 'session' in the request body —
    # the frontend generates one id when Play starts and sends it with every
    # log line of that session), not for each separate entry.
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
        # Logging must not fail the game itself — if writing
        # failed (no disk permissions etc.), we just quietly answer ok:false.
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
        # Only play_*.log files from LOG_DIR — we don't serve an arbitrary
        # path on request.
        safe = Path(name).name
        if not safe.startswith('play_') or not safe.endswith('.log'):
            return jsonify({'ok': False, 'error': 'bad name'}), 400
        return send_from_directory(LOG_DIR, safe, mimetype='text/plain')
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404


# Reading HTML/CSS/JS — previously all three were one file (index.html),
# because of which it grew to almost 10000 lines in one place; now they
# are split into separate files next to app.py (index.html/style.css/
# script.js), and index.html includes them via <link>/<script src>.
with open("index.html", "r", encoding="utf-8") as file:
    HTML_TEMPLATE = file.read()
with open("style.css", "r", encoding="utf-8") as file:
    CSS_TEMPLATE = file.read()
with open("script.js", "r", encoding="utf-8") as file:
    JS_TEMPLATE = file.read()


def _no_cache(resp):
    # index/style/script are read from disk ONCE at start, while a WebView/
    # browser could previously keep an old copy of script.js — after an edit
    # the old version kept working. no-cache forces revalidation.
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
    # ?v=<hash> in the links to script.js/style.css — a WebView can't serve
    # an old copy from its cache after the files are replaced.
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


# ============ AI ASSISTANT ============
# Any OpenAI-compatible provider (OpenRouter, Groq, Mistral, Ollama,
# Russian aggregators...): the address, key and model are set in the «🤖 AI» panel.
# The key is stored only on the server (it isn't sent to the browser), by default the
# endpoints accept requests only from 127.0.0.1 — the server listens on 0.0.0.0,
# and without this anyone on the local network could spend someone else's key.
# RSW_ASSISTANT_ALLOW_REMOTE=1 lifts this restriction.
try:
    with open("assistant.js", "r", encoding="utf-8") as file:
        ASSISTANT_JS = file.read()
except OSError:   # no file (an old build) — the editor works without the assistant
    ASSISTANT_JS = '/* assistant.js not found */'


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
    """A message in the interface language (the X-Lang header sent by the frontend).
    Outside a request (background threads, startup) English is used."""
    try:
        lang = (request.headers.get('X-Lang') or '').lower()
    except RuntimeError:
        lang = ''
    return ru if lang.startswith('ru') else en


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


_AI_SAFETY_LINE = _re_ai.compile(r"(?im)^[ \t]*(User Safety|Response Safety|Safety Categories)\s*:.*$\n?")


def _ai_strip_done_actions(text):
    """We replace old action blocks with a placeholder (if the client didn't substitute the «Patch applied» summary):
    otherwise free models copy them by template and go poking into the scene for any question.
    Safety service lines (leaked by nemotron-safety and the like) are removed too."""
    text = _AI_ACT_BLOCK.sub('[блок действий уже обработан]', text)
    return _AI_SAFETY_LINE.sub('', text)


def _ai_text_only(text):
    return bool(_AI_TEXT_ONLY.search(text or ''))


_ASSISTANT_ACTIONS_RU = r"""
ТЫ САМ МЕНЯЕШЬ СЦЕНУ. Редактор выполняет блок ```rbx-actions с JSON-массивом действий (один блок в самом конце ответа, метка именно rbx-actions). Не проси пользователя делать что-то вручную и не говори, что не можешь.

Действия:
{"op":"create","class":C,"name":N,"parent":P?,"props":{...}?,"source":"код"?}
{"op":"set","ref":R,"prop":P,"value":V}
{"op":"move","ref":R,"parent":P}
{"op":"delete","ref":R}
{"op":"play","seconds":S?}
{"op":"stop"}
R — число из контекста редактора. P — число или имя объекта (в том числе созданного выше в этом же блоке). Для переноса используй move, а не delete+create.

class: Part, WedgePart, SpherePart, CornerWedgePart, SpawnLocation, Folder, Model, Script, LocalScript, ModuleScript.
props/set: Position, Rotation, Size ([x,y,z]), Color ("#RRGGBB"), Transparency, Reflectance (0..1), Anchored, CanCollide, CastShadow (bool), Name, Source (только скрипты). Другие свойства (Material и т.п.) не поддерживаются, не используй.
Для каждого Part всегда задавай Size и Position. Position/Size — массивы из трёх чисел.

Размещение скриптов:
1. Скрипт управляет конкретным объектом (вращает, двигает, ловит касание/клик) — создай его ВНУТРИ этого объекта: parent = имя или ref объекта, в коде local target = script.Parent. Сам объект создай выше в том же блоке.
2. Общий серверный Script без parent попадает в ServerScriptService; объекты в нём ищи через workspace:WaitForChild("Имя").
3. LocalScript без parent попадает в StarterPlayerScripts. Не клади LocalScript в ServerScriptService/ServerStorage.
4. ModuleScript для клиента и сервера — ReplicatedStorage; только серверный — ServerScriptService.
5. Script в ServerStorage и LocalScript в ReplicatedStorage не выполняются — не создавай их там, если пользователь явно не просил.
6. Никогда не выдумывай ref и не используй parent = -1. Нет подходящего объекта в контексте — не указывай parent и скажи в ответе, куда попадёт скрипт.

Чтобы изменить код существующего скрипта: {"op":"set","ref":R,"prop":"Source","value":"новый код целиком"}.
В JSON переводы строк в source пиши как \n, кавычки экранируй: настоящих переводов строк внутри строки JSON быть не должно. Держи блок компактным (длина ответа ограничена): без лишних комментариев и дублирования кода. Максимум 30 действий в блоке.

Запуск и проверка игры: play запускает игру (S — 1..60 секунд, потом редактор сам её остановит), stop останавливает. Чтобы проверить свою работу, поставь play ПОСЛЕДНИМ действием блока, например {"op":"play","seconds":8}. Вывод игры (print/warn/error) придёт тебе в блоке «Вывод игры» контекста: найди причину ошибок и исправь. Запускай игру только если пользователь просит запустить/проверить/протестировать или это нужно, чтобы понять ошибку. Пометка [Patch error: ...] в истории значит, что патч применился не полностью: исправь причину и пришли блок только для невыполненной части.

Формат ответа на просьбу изменить сцену: 1–2 фразы о плане, затем сразу блок rbx-actions. Пример (вращающийся куб):
Создаю куб и скрипт, который его вращает.
```rbx-actions
[{"op":"create","class":"Part","name":"Cube","props":{"Size":[4,4,4],"Position":[0,5,0],"Anchored":true,"Color":"#3366FF"}},
 {"op":"create","class":"Script","name":"Spin","parent":"Cube","source":"local part = script.Parent\nlocal RunService = game:GetService(\"RunService\")\nRunService.Heartbeat:Connect(function(dt)\n    part.CFrame *= CFrame.Angles(0, dt, 0)\nend)"}]
```
"""

_ASSISTANT_ACTIONS_EN = r"""
YOU CHANGE THE SCENE YOURSELF. The editor executes a ```rbx-actions block with a JSON array of actions (one block at the very end of the reply, the tag must be exactly rbx-actions). Never ask the user to do things by hand and never say you cannot.

Actions:
{"op":"create","class":C,"name":N,"parent":P?,"props":{...}?,"source":"code"?}
{"op":"set","ref":R,"prop":P,"value":V}
{"op":"move","ref":R,"parent":P}
{"op":"delete","ref":R}
{"op":"play","seconds":S?}
{"op":"stop"}
R is a number from the editor context. P is a number or an object name (including one created earlier in the same block). To reparent use move, not delete+create.

class: Part, WedgePart, SpherePart, CornerWedgePart, SpawnLocation, Folder, Model, Script, LocalScript, ModuleScript.
props/set: Position, Rotation, Size ([x,y,z]), Color ("#RRGGBB"), Transparency, Reflectance (0..1), Anchored, CanCollide, CastShadow (bool), Name, Source (scripts only). Other properties (Material etc.) are not supported, do not use them.
Always give every Part a Size and a Position. Position/Size are arrays of three numbers.

Script placement:
1. A script that controls a specific object (spins, moves, handles touch/click) goes INSIDE that object: parent = the object's name or ref, and the code uses local target = script.Parent. Create the object earlier in the same block.
2. A general server Script without parent goes to ServerScriptService; find objects there with workspace:WaitForChild("Name").
3. A LocalScript without parent goes to StarterPlayerScripts. Never put a LocalScript in ServerScriptService/ServerStorage.
4. A ModuleScript needed by client and server goes to ReplicatedStorage; server-only goes to ServerScriptService.
5. A Script in ServerStorage and a LocalScript in ReplicatedStorage never run, so do not create them there unless explicitly asked.
6. Never invent a ref and never use parent = -1. If no suitable object is in the context, omit parent and say in the reply where the script will land.

To change an existing script's code: {"op":"set","ref":R,"prop":"Source","value":"the whole new code"}.
In JSON write newlines inside source as \n and escape quotes: a JSON string must contain no real line breaks. Keep the block compact (the reply length is limited): no needless comments or duplicated code. At most 30 actions per block.

Running and testing the game: play starts the game (S is 1..60 seconds, then the editor stops it itself), stop stops it. To test your work put play as the LAST action of the block, e.g. {"op":"play","seconds":8}. The game output (print/warn/error) reaches you in the "Game output" part of the context: find the cause of the errors and fix them. Run the game only when the user asks to run/check/test, or when you need it to understand an error. A note [Patch error: ...] in the history means the patch was not fully applied: fix the cause and send a block only for the part that is not done.

Reply format for a scene-change request: 1-2 sentences with the plan, then the rbx-actions block right away. Example (spinning cube):
Creating a cube and a script that spins it.
```rbx-actions
[{"op":"create","class":"Part","name":"Cube","props":{"Size":[4,4,4],"Position":[0,5,0],"Anchored":true,"Color":"#3366FF"}},
 {"op":"create","class":"Script","name":"Spin","parent":"Cube","source":"local part = script.Parent\nlocal RunService = game:GetService(\"RunService\")\nRunService.Heartbeat:Connect(function(dt)\n    part.CFrame *= CFrame.Angles(0, dt, 0)\nend)"}]
```
"""

_ASSISTANT_SYSTEM = {
    'ru': (
        "Ты ассистент веб-редактора Roblox Studio (клон на Flask). Помогаешь с Luau-скриптами, "
        "свойствами объектов и структурой игры. Используй только реальный Roblox API.\n"
        "Отвечай на языке пользователя, кратко и сразу по делу. Рассуждай про себя: не пиши "
        "рассуждения, черновики и план «что я сейчас подумаю». Ты не модератор: никаких меток и оценок "
        "(User Safety, Response Safety, safe/unsafe, moderation и т.п.), не комментируй безопасность запроса.\n"
        "Вопрос или просьба «только текст» — ответь текстом (2–5 предложений, код в блоках), "
        "без блока rbx-actions. Если данных не хватает — задай один уточняющий вопрос.\n"
        "Контекст редактора ниже — источник правды о сцене; в истории пометки вида [Patch applied: ...] "
        "описывают уже выполненные изменения (с ref объектов), не повторяй их. "
        "Если скрипт в контексте помечен [script truncated], не переписывай его Source целиком.\n"
        + _ASSISTANT_ACTIONS_RU
    ),
    'en': (
        "You are an assistant built into a web-based Roblox Studio editor (a Flask clone). You help with "
        "Luau scripts, object properties and game structure. Use only the real Roblox API.\n"
        "Reply in the user's language, concisely and straight to the point. Think silently: do not write "
        "out your reasoning, drafts or a 'let me think' plan. You are not a moderator: no labels or ratings "
        "(User Safety, Response Safety, safe/unsafe, moderation, etc.), do not comment on request safety.\n"
        "For a question or a 'text only' request, answer in text (2-5 sentences, code in blocks) "
        "without an rbx-actions block. If data is missing, ask one clarifying question.\n"
        "The editor context below is the source of truth about the scene; history notes like [Patch applied: ...] "
        "describe changes already made (with object refs), do not repeat them. "
        "If a script in the context is marked [script truncated], never rewrite its whole Source.\n"
        + _ASSISTANT_ACTIONS_EN
    ),
}


# ---------- Editor context: budget, token estimate, model window ----------
_AI_CTX_MAX = {'selection': 2000, 'scene': 4000, 'output': 3000, 'script': 12000}   # characters
_AI_CTX_ORDER = ('selection', 'scene', 'output', 'script')    # the scene with refs — before the script: the script is cut first
_AI_DEFAULT_WINDOW = 32768       # if the provider doesn't report the window size
_AI_REPLY_RESERVE = 3000         # a minimum reserve for the reply (if the window is unknown — see _ai_reply_tokens)
_AI_REPLY_MAX = 12000            # the max_tokens ceiling: code in rbx-actions + reasoning tokens didn't fit into 3000


def _ai_reply_tokens(window):
    """How many tokens to ask the model for the reply: up to 12k, but no more than a quarter of the window."""
    if window:
        return max(_AI_REPLY_RESERVE, min(_AI_REPLY_MAX, window // 4))
    return 6000
_AI_WIN_CACHE = {}               # (base_url, model) -> (window | None, request time)
_AI_CALIB = {}                   # model -> an estimate correction from the provider's real usage
_AI_WIN_KEYS = ('context_length', 'context_window', 'max_model_len', 'max_context_length', 'n_ctx')


def _ai_est_tokens(text):
    """A rough estimate: Cyrillic ~2.3 characters/token, the rest (English, code) ~3.5."""
    if not text:
        return 0
    cyr = sum(1 for ch in text if '\u0400' <= ch <= '\u04ff')
    return int(cyr / 2.3 + (len(text) - cyr) / 3.5) + 1


def _ai_raw_tokens(system, msgs):
    return _ai_est_tokens(system) + sum(_ai_est_tokens(m['content']) + 4 for m in msgs) + 8


def _ai_calibrate(model, real, raw):
    """We adjust the estimate to the real prompt_tokens if the provider sent it."""
    if real > 0 and raw > 0:
        old = _AI_CALIB.get(model, 1.0)
        _AI_CALIB[model] = max(0.5, min(2.5, 0.6 * old + 0.4 * real / float(raw)))


def _ai_window_from_item(m):
    if not isinstance(m, dict):
        return None
    cands = [m.get(k) for k in _AI_WIN_KEYS]
    tp = m.get('top_provider')
    if isinstance(tp, dict):
        cands.append(tp.get('context_length'))
    for v in cands:
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 512:
            return int(v)
    return None


def _ai_remember_windows(base, j):
    """Remembers the window size from the /models response; returns {id: window}."""
    items = j.get('data') if isinstance(j, dict) else j
    now = time.time()
    found = {}
    for m in items or []:
        mid = m.get('id') if isinstance(m, dict) else None
        win = _ai_window_from_item(m)
        if isinstance(mid, str) and win:
            found[mid] = win
            _AI_WIN_CACHE[(base, mid)] = (win, now)
    return found


def _ai_window(cfg):
    """The selected model's window in tokens or None if the provider doesn't report it."""
    if not cfg.get('model'):
        return None
    base = cfg['base_url'].rstrip('/')
    key = (base, cfg['model'])
    hit = _AI_WIN_CACHE.get(key)
    if hit and (hit[0] or time.time() - hit[1] < 300):     # we don't retry a failure for 5 minutes
        return hit[0]
    try:
        with _assistant_http(base + '/models', cfg['api_key'], timeout=8) as resp:
            _ai_remember_windows(base, json.loads(resp.read().decode('utf-8', 'replace')))
    except Exception:
        pass
    hit = _AI_WIN_CACHE.get(key)
    if not hit:
        _AI_WIN_CACHE[key] = hit = (None, time.time())
    return hit[0]


def _ai_cut(text, limit, tail=0.0, note=''):
    """-> (text, whether truncated). tail — the share of the limit kept from the end."""
    if len(text) <= limit:
        return text, False
    t = int(limit * tail)
    cut = text[:limit - t] + '\n[…]\n' + (text[len(text) - t:] if t else '')
    return cut + (('\n' + note) if note else ''), True


def _ai_context(d, window):
    """Editor context -> (text, whether it was shortened). Order: selection, scene, script.
    Previously everything was cut by ctx[:5000], and the scene summary (with refs) stood at the very end —
    with a long script it fell off first, and the model made up refs.
    Now each part has its own limit, and the script gets the remainder of the budget."""
    total = sum(_AI_CTX_MAX.values())
    if window:
        total = min(total, max(3000, int(window * 3 * 0.4)))
    ctx = d.get('ctx')
    if not isinstance(ctx, dict):
        legacy = d.get('context')           # an old client sent a single string
        ctx = {'selection': legacy[:total]} if isinstance(legacy, str) else {}
    out, truncated, used = [], False, 0
    for k in _AI_CTX_ORDER:
        v = ctx.get(k)
        if not (isinstance(v, str) and v.strip()):
            continue
        v = v.strip()
        if k == 'script':
            lim = max(800, min(_AI_CTX_MAX[k], total - used))
            v, tr = _ai_cut(v, lim, tail=0.3, note='[script truncated]')
        else:
            share = {'selection': 0.12, 'scene': 0.25, 'output': 0.2}[k]
            lim = min(_AI_CTX_MAX[k], int(total * share))
            # game output: we keep the header and the LAST lines — fresh errors matter more than old ones
            v, tr = _ai_cut(v, max(300, lim), tail=0.85 if k == 'output' else 0.0)
        truncated = truncated or tr
        used += len(v)
        out.append(v)
    return '\n\n'.join(out), truncated


def _ai_prepare(d, cfg):
    """Shared preparation for the chat and the indicator: history, context, mode tag, fitting to the window."""
    window = _ai_window(cfg)
    msgs = []
    for m in (d.get('messages') or [])[-12:]:                # 6 user/assistant pairs
        if not (isinstance(m, dict) and m.get('role') in ('user', 'assistant')
                and isinstance(m.get('content'), str)):
            continue
        msgs.append({'role': m['role'], 'content': m['content']})
    # old assistant messages are cut to head+tail (the rbx-actions block has already been executed)
    for m in msgs:
        if m['role'] == 'assistant':
            m['content'] = _ai_strip_done_actions(m['content'])
    keep_full = set([i for i, m in enumerate(msgs) if m['role'] == 'assistant'][-2:])
    for i, m in enumerate(msgs):
        c = m['content']
        if m['role'] == 'user':
            m['content'] = c[:3000]
        elif i in keep_full:
            m['content'] = c[:4000]
        elif len(c) > 1000:
            m['content'] = c[:400] + '\n[…]\n' + c[-600:]
    ctx_text, truncated = _ai_context(d, window)
    base_system = _alang(_ASSISTANT_SYSTEM['ru'], _ASSISTANT_SYSTEM['en'])
    system = base_system
    if ctx_text:
        system += _alang('\n\nКонтекст редактора:\n', '\n\nEditor context:\n') + ctx_text
    if msgs and msgs[-1]['role'] == 'user':
        if _ai_text_only(msgs[-1]['content']):
            msgs[-1]['content'] += _alang(
                "\n\n[Вопрос/обсуждение: ответь только текстом, 2-5 предложений, без rbx-actions.]",
                "\n\n[Question/discussion: answer in text only, 2-5 sentences, no rbx-actions.]")
        else:
            msgs[-1]['content'] += _alang(
                "\n\n[Если нужно изменить сцену: 1-2 фразы плана и сразу блок ```rbx-actions. "
                "Без длинных рассуждений. Если это вопрос — только текст.]",
                "\n\n[If the scene must change: 1-2 sentence plan, then the ```rbx-actions block right away. "
                "No long reasoning. If it is a question - text only.]")
    # if the known window overflows — we throw out the oldest messages
    dropped = 0
    if window:
        k = _AI_CALIB.get(cfg.get('model'), 1.0)
        limit = int(window * 0.9) - _ai_reply_tokens(window)
        while len(msgs) > 1 and _ai_raw_tokens(system, msgs) * k > limit:
            msgs.pop(0)
            dropped += 1
        while len(msgs) > 1 and msgs[0]['role'] == 'assistant':
            msgs.pop(0)
            dropped += 1
    return {'system': system, 'base_system': base_system, 'msgs': msgs, 'window': window,
            'ctx_text': ctx_text, 'truncated': truncated, 'dropped': dropped}


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
    ids = ids[:500]
    contexts = _ai_remember_windows(cfg['base_url'].rstrip('/'), j)    # {id: window in tokens}, if the provider reports it
    known = set(ids)
    return jsonify({'ok': True, 'models': ids, 'contexts': {k: v for k, v in contexts.items() if k in known}})


@flask_app.route('/api/assistant/usage', methods=['POST'])
def assistant_usage():
    """How much of the model's window the next request will take (an estimate): system + editor context + history + input."""
    deny = _assistant_guard()
    if deny:
        return deny
    cfg = _assistant_load()
    d = request.get_json(silent=True) or {}
    draft = d.get('draft')
    has_draft = isinstance(draft, str) and bool(draft.strip())
    if has_draft:
        d = dict(d)
        d['messages'] = list(d.get('messages') or []) + [{'role': 'user', 'content': draft[:3000]}]
    p = _ai_prepare(d, cfg)
    msgs = p['msgs']
    k = _AI_CALIB.get(cfg.get('model'), 1.0)
    inp = _ai_est_tokens(msgs[-1]['content']) + 4 if (has_draft and msgs and msgs[-1]['role'] == 'user') else 0
    hist = sum(_ai_est_tokens(m['content']) + 4 for m in (msgs[:-1] if inp else msgs))
    parts = {'system': int((_ai_est_tokens(p['base_system']) + 8) * k),
             'editor': int(_ai_est_tokens(p['ctx_text']) * k),
             'history': int(hist * k), 'input': int(inp * k)}
    if d.get('has_image'):
        parts['image'] = 1100     # a screenshot ≤1024 px — on the order of 1k tokens for most vision models
    used = sum(parts.values())
    window = p['window'] or _AI_DEFAULT_WINDOW
    return jsonify({'ok': True, 'used': used, 'window': window, 'assumed': not p['window'],
                    'percent': round(100.0 * used / window, 1), 'parts': parts,
                    'truncated': p['truncated'], 'dropped': p['dropped']})


@flask_app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    deny = _assistant_guard()
    if deny:
        return deny
    cfg = _assistant_load()
    if not cfg['model']:
        return jsonify({'ok': False, 'error': _alang('Не выбрана модель (⚙ в панели ассистента)', 'No model selected (⚙ in the assistant panel)')}), 400
        
    d = request.get_json(silent=True) or {}
    p = _ai_prepare(d, cfg)
    system, msgs = p['system'], p['msgs']
    if not msgs:
        return jsonify({'ok': False, 'error': _alang('Пустой запрос', 'Empty request')}), 400
    model = cfg['model']
    est_raw = _ai_raw_tokens(system, msgs)

    base = cfg['base_url'].rstrip('/')
    is_or = 'openrouter.ai' in base
    # a scene screenshot (only into the last user message; it doesn't go into the history)
    img = d.get('image')
    if not (isinstance(img, str) and len(img) < 6000000 and img.startswith(
            ('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/webp;base64,'))):
        img = None
    plain_msgs = [{'role': 'system', 'content': system}] + msgs
    img_msgs = None
    if img and msgs[-1]['role'] == 'user':
        note = _alang("\n\n[К сообщению приложен скриншот сцены (вид из редактора/игры).]",
                      "\n\n[A screenshot of the scene (editor/game view) is attached.]")
        img_msgs = plain_msgs[:-1] + [{'role': 'user', 'content': [
            {'type': 'text', 'text': msgs[-1]['content'] + note},
            {'type': 'image_url', 'image_url': {'url': img}}]}]

    reply_mt = _ai_reply_tokens(p['window'])

    def make(messages, reasoning, mt=None):
        pl = {'model': cfg['model'], 'stream': True, 'temperature': 0.3, 'max_tokens': mt or reply_mt, 'messages': messages}
        if reasoning:
            pl['reasoning'] = {'effort': 'low'}   # free reasoning models otherwise think for minutes before the first token
        return pl

    # request variants in order: with an image (+reasoning), with an image without reasoning,
    # without an image (+reasoning), without an image without reasoning. We move on only on 400/404/422.
    variants = []
    if img_msgs:
        variants.append((make(img_msgs, is_or), True))
        if is_or:
            variants.append((make(img_msgs, False), True))
    variants.append((make(plain_msgs, is_or), False))
    if is_or:
        variants.append((make(plain_msgs, False), False))
    if reply_mt > 3000:     # the provider didn't accept a large max_tokens — a last attempt with the old limit
        variants.append((make(plain_msgs, False, 3000), False))
    resp, last_err, sent_image = None, None, False
    for pl, with_img in variants:
        try:
            resp = _assistant_http(base + '/chat/completions', cfg['api_key'], pl)
            sent_image = with_img
            break
        except _urlerr.HTTPError as e:
            last_err = e
            if e.code not in (400, 404, 422):
                return jsonify({'ok': False, 'error': _assistant_error(e)}), 502
        except Exception as e:
            return jsonify({'ok': False, 'error': _assistant_error(e)}), 502
    if resp is None:
        return jsonify({'ok': False, 'error': _assistant_error(last_err)}), 502
    img_dropped = bool(img_msgs) and not sent_image
    msg_noimg = _alang('📷 [Модель не принимает изображения — запрос отправлен без скриншота. Выбери модель с поддержкой картинок.]\n\n',
                       '📷 [This model does not accept images — sent without the screenshot. Pick a vision model.]\n\n')

    # we prepare messages in advance: the request context is no longer inside the generator
    msg_prov = _alang('\n\n[Ошибка провайдера: %s]', '\n\n[Provider error: %s]')
    msg_stream = _alang('\n\n[Ошибка потока: %s]', '\n\n[Stream error: %s]')

    def gen():
        # \x1f — a service «pulse»: the model is thinking (reasoning tokens aren't sent out),
        # the client shows «thinking…» and doesn't look frozen
        last_ping = 0.0
        if img_dropped:
            yield msg_noimg
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
                    usage = j.get('usage')
                    if (not sent_image) and isinstance(usage, dict) and isinstance(usage.get('prompt_tokens'), int):
                        _ai_calibrate(model, usage['prompt_tokens'], est_raw)
                    delta = ((j.get('choices') or [{}])[0].get('delta')) or {}
                    t = delta.get('content')
                    if t:
                        yield t
                    elif delta.get('reasoning') or delta.get('reasoning_content') or delta.get('reasoning_details'):
                        now = time.time()
                        if now - last_ping > 1.0:
                            last_ping = now
                            yield '\x1f'
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
                    f'[RbxStudio] Loaded: {p} ({len(parsed["referent_to_class"])} objects)')
            except Exception as e:
                print(f'[RbxStudio] Load error: {e}')

    url = f'http://127.0.0.1:{PORT}'
    print(f'[RbxStudio] Starting: {url}')

    def open_browser():
        time.sleep(2)
        # On Termux there is no ordinary GUI browser that understands
        # the standard python webbrowser.open() — it may find there
        # a text browser (links/w3m/lynx) and open it RIGHT IN THE
        # TERMINAL, which looks like a "dump" of HTML instead of a real
        # server launch. termux-open-url (from the Termux:API package)
        # correctly hands the link to the system Android browser.
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
        # Not on Termux (or Termux:API isn't installed) — we try the ordinary
        # way, but only if it does NOT look like a text browser.
        if sys.platform != 'linux' or os.environ.get('TERMUX_VERSION'):
            return
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()
    # threaded=True is mandatory: without it Flask's single-threaded dev server
    # blocks ALL requests whatsoever (including the editor's ordinary work) for
    # the whole duration of a long /api/roblox/avatar3d/fetch — exactly because of
    # this the app looked "frozen" as a whole, not only the
    # avatar download dialog.
    flask_app.run(host='0.0.0.0', port=PORT, debug=False,
                  use_reloader=False, threaded=True)
