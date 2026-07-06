import sys
import struct
import json
import os
import math
from pathlib import Path

# ====================== LZ4 ======================

def lz4_decompress(data: bytes, uncompressed_size: int) -> bytes:
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        token = data[i]; i += 1
        lit_len = token >> 4
        if lit_len == 15:
            while True:
                b = data[i]; i += 1
                lit_len += b
                if b != 255:
                    break
        out += data[i:i+lit_len]
        i += lit_len
        if i >= n:
            break
        offset = data[i] | (data[i+1] << 8)
        i += 2
        match_len = token & 0x0F
        if match_len == 15:
            while True:
                b = data[i]; i += 1
                match_len += b
                if b != 255:
                    break
        match_len += 4
        start = len(out) - offset
        for j in range(match_len):
            out.append(out[start + j])
    return bytes(out[:uncompressed_size])


# ====================== Chunk reading / writing ======================

def read_chunks(path):
    data = open(path, 'rb').read()
    pos = 32
    chunks = []
    while pos < len(data):
        name = data[pos:pos+4]
        compsize = int.from_bytes(data[pos+4:pos+8], 'little')
        uncompsize = int.from_bytes(data[pos+8:pos+12], 'little')
        raw = data[pos+16:pos+16+compsize]
        payload = None
        if compsize == 0:
            payload = raw[:uncompsize]
        else:
            try:
                candidate = lz4_decompress(raw, uncompsize)
                if len(candidate) == uncompsize:
                    payload = candidate
            except Exception:
                payload = None
            if payload is None:
                payload = raw
        chunks.append({
            'name': name,
            'payload': payload,
            'compsize': compsize,
            'uncompsize': uncompsize,
            'raw': raw
        })
        if name == b'END\x00':
            break
        pos += 16 + compsize
    return chunks


def write_chunk(name: bytes, payload: bytes) -> bytes:
    header = struct.pack('<4sIII',
        name,
        len(payload),
        len(payload),
        0
    )
    return header + payload


def write_chunk_raw(chunk: dict) -> bytes:
    header = struct.pack('<4sIII',
        chunk['name'],
        chunk['compsize'],
        chunk['uncompsize'],
        0
    )
    return header + chunk['raw']


# ====================== Integer transform / interleaving ======================

def untransform_i32(v):
    v &= 0xFFFFFFFF
    return (v >> 1) ^ -(v & 1)

def untransform_i64(v):
    v &= 0xFFFFFFFFFFFFFFFF
    return (v >> 1) ^ -(v & 1)

def transform_i32(v):
    v &= 0xFFFFFFFF
    if v >= 0:
        return (v << 1) & 0xFFFFFFFF
    else:
        return ((-v << 1) - 1) & 0xFFFFFFFF

def transform_i64(v):
    v &= 0xFFFFFFFFFFFFFFFF
    if v >= 0:
        return (v << 1) & 0xFFFFFFFFFFFFFFFF
    else:
        return ((-v << 1) - 1) & 0xFFFFFFFFFFFFFFFF

def read_interleaved_array(buf, count, width):
    vals = [0]*count
    for byte_i in range(width):
        base = byte_i*count
        for i in range(count):
            vals[i] = (vals[i] << 8) | buf[base+i]
    return vals

def write_interleaved_array(vals, width):
    count = len(vals)
    buf = bytearray(count * width)
    for byte_i in range(width):
        shift = (width - 1 - byte_i) * 8
        base = byte_i * count
        for i in range(count):
            buf[base + i] = (vals[i] >> shift) & 0xFF
    return bytes(buf)

def read_interleaved_u32_array(buf, count):
    return read_interleaved_array(buf, count, 4)

def write_interleaved_u32_array(vals):
    return write_interleaved_array(vals, 4)

def read_interleaved_u64_array(buf, count):
    return read_interleaved_array(buf, count, 8)

def write_interleaved_u64_array(vals):
    return write_interleaved_array(vals, 8)

def read_referents(buf, count):
    raw = read_interleaved_u32_array(buf, count)
    acc = 0
    out = []
    for r in raw:
        acc += untransform_i32(r)
        out.append(acc)
    return out

def write_referents(refs):
    raw = []
    prev = 0
    for r in refs:
        delta = r - prev
        raw.append(transform_i32(delta))
        prev = r
    return write_interleaved_u32_array(raw)


# ====================== Roblox float format ======================

def roblox_u32_to_float(u):
    sign = u & 1
    rest = u >> 1
    ieee = (sign << 31) | rest
    return struct.unpack('>f', ieee.to_bytes(4, 'big'))[0]

def float_to_roblox_u32(f):
    ieee = struct.unpack('>I', struct.pack('>f', f))[0]
    sign = (ieee >> 31) & 1
    rest = ieee & 0x7FFFFFFF
    return (rest << 1) | sign

def read_interleaved_roblox_float_array(buf, count):
    raw = read_interleaved_u32_array(buf, count)
    return [roblox_u32_to_float(v) for v in raw]

def write_interleaved_roblox_float_array(vals):
    raw = [float_to_roblox_u32(float(v)) for v in vals]
    return write_interleaved_u32_array(raw)


# ====================== String ======================

def parse_string_array(buf, count):
    pos = 0
    values = []
    for _ in range(count):
        l = int.from_bytes(buf[pos:pos+4], 'little'); pos += 4
        s = buf[pos:pos+l]; pos += l
        try:
            values.append(s.decode('utf-8'))
        except UnicodeDecodeError:
            values.append(s)
    return values, pos

def write_string_array(strings):
    buf = bytearray()
    for s in strings:
        if isinstance(s, str):
            s = s.encode('utf-8')
        elif not isinstance(s, bytes):
            s = str(s).encode('utf-8')
        buf.extend(struct.pack('<I', len(s)))
        buf.extend(s)
    return bytes(buf)


# ====================== INST / PRNT / PROP framing ======================

def parse_inst(payload):
    pos = 0
    class_id = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    name_len = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    class_name = payload[pos:pos+name_len].decode('utf-8'); pos += name_len
    object_format = payload[pos]; pos += 1
    instance_count = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    ref_buf = payload[pos:pos+4*instance_count]; pos += 4*instance_count
    referents = read_referents(ref_buf, instance_count)
    return class_id, class_name, object_format, referents

def write_inst(class_id: int, class_name: str, referents: list) -> bytes:
    buf = bytearray()
    buf.extend(struct.pack('<I', class_id))
    name_bytes = class_name.encode('utf-8')
    buf.extend(struct.pack('<I', len(name_bytes)))
    buf.extend(name_bytes)
    buf.append(0)
    buf.extend(struct.pack('<I', len(referents)))
    buf.extend(write_referents(referents))
    return bytes(buf)

def parse_prnt(payload):
    pos = 0
    version = payload[pos]; pos += 1
    count = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    child_buf = payload[pos:pos+4*count]; pos += 4*count
    parent_buf = payload[pos:pos+4*count]; pos += 4*count
    children = read_referents(child_buf, count)
    parents = read_referents(parent_buf, count)
    return list(zip(children, parents))

def write_prnt(pairs: list) -> bytes:
    buf = bytearray()
    buf.append(0)
    buf.extend(struct.pack('<I', len(pairs)))
    children = [p[0] for p in pairs]
    parents = [p[1] for p in pairs]
    buf.extend(write_referents(children))
    buf.extend(write_referents(parents))
    return bytes(buf)

def parse_prop_header(payload):
    pos = 0
    class_id = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    name_len = int.from_bytes(payload[pos:pos+4], 'little'); pos += 4
    prop_name = payload[pos:pos+name_len].decode('utf-8'); pos += name_len
    type_id = payload[pos]; pos += 1
    rest = payload[pos:]
    return class_id, prop_name, type_id, rest

def write_prop_header(class_id: int, prop_name: str, type_id: int) -> bytes:
    buf = bytearray()
    buf.extend(struct.pack('<I', class_id))
    name_bytes = prop_name.encode('utf-8')
    buf.extend(struct.pack('<I', len(name_bytes)))
    buf.extend(name_bytes)
    buf.append(type_id)
    return bytes(buf)


# ====================== TYPE DECODERS (read) ======================

def t_string(buf, count):
    values, _ = parse_string_array(buf, count)
    return values

def t_bool(buf, count):
    return [b == 1 for b in buf[:count]]

def t_int32(buf, count):
    raw = read_interleaved_u32_array(buf, count)
    return [untransform_i32(v) for v in raw]

def t_float32(buf, count):
    return read_interleaved_roblox_float_array(buf, count)

def t_float64(buf, count):
    return [struct.unpack_from('<d', buf, i*8)[0] for i in range(count)]

def t_udim(buf, count):
    scales = read_interleaved_roblox_float_array(buf[:4*count], count)
    offsets = t_int32(buf[4*count:8*count], count)
    return [{'scale': s, 'offset': o} for s, o in zip(scales, offsets)]

def t_udim2(buf, count):
    sx = read_interleaved_roblox_float_array(buf[0:4*count], count)
    sy = read_interleaved_roblox_float_array(buf[4*count:8*count], count)
    ox = t_int32(buf[8*count:12*count], count)
    oy = t_int32(buf[12*count:16*count], count)
    return [{'x': {'scale': sx[i], 'offset': ox[i]},
             'y': {'scale': sy[i], 'offset': oy[i]}} for i in range(count)]

def t_ray(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        vals = struct.unpack_from('<6f', buf, pos); pos += 24
        out.append({'origin': vals[0:3], 'direction': vals[3:6]})
    return out

def t_faces(buf, count):
    return list(buf[:count])

def t_axes(buf, count):
    return list(buf[:count])

def t_brickcolor(buf, count):
    return read_interleaved_u32_array(buf, count)

def t_color3(buf, count):
    r = read_interleaved_roblox_float_array(buf[0:4*count], count)
    g = read_interleaved_roblox_float_array(buf[4*count:8*count], count)
    b = read_interleaved_roblox_float_array(buf[8*count:12*count], count)
    return [{'r': r[i], 'g': g[i], 'b': b[i]} for i in range(count)]

def t_vector2(buf, count):
    x = read_interleaved_roblox_float_array(buf[0:4*count], count)
    y = read_interleaved_roblox_float_array(buf[4*count:8*count], count)
    return [{'x': x[i], 'y': y[i]} for i in range(count)]

def t_vector3(buf, count):
    x = read_interleaved_roblox_float_array(buf[0:4*count], count)
    y = read_interleaved_roblox_float_array(buf[4*count:8*count], count)
    z = read_interleaved_roblox_float_array(buf[8*count:12*count], count)
    return [{'x': x[i], 'y': y[i], 'z': z[i]} for i in range(count)]

_CFRAME_ANGLE_IDS = {
    0x02:(0,0,0), 0x03:(90,0,0), 0x05:(0,180,180), 0x06:(-90,0,0),
    0x07:(0,180,90), 0x09:(0,90,90), 0x0a:(0,0,90), 0x0c:(0,-90,90),
    0x0d:(-90,-90,0), 0x0e:(0,-90,0), 0x10:(90,-90,0), 0x11:(0,90,180),
    0x14:(0,180,0), 0x15:(-90,-180,0), 0x17:(0,0,180), 0x18:(90,180,0),
    0x19:(0,0,-90), 0x1b:(0,-90,-90), 0x1c:(0,-180,-90), 0x1e:(0,90,-90),
    0x1f:(90,90,0), 0x20:(0,90,0), 0x22:(-90,90,0), 0x23:(0,-90,180),
}

def t_cframe(buf, count):
    pos = 0
    entries = []
    for _ in range(count):
        cid = buf[pos]; pos += 1
        if cid == 0x00:
            mat = struct.unpack_from('<9f', buf, pos); pos += 36
            entries.append({'matrix': list(mat)})
        else:
            entries.append({'special_id': cid, 'angles_deg': _CFRAME_ANGLE_IDS.get(cid)})
    positions = t_vector3(buf[pos:pos+12*count], count)
    for e, p in zip(entries, positions):
        e['position'] = p
    return entries

def t_enum(buf, count):
    return read_interleaved_u32_array(buf, count)

def t_referent(buf, count):
    return read_referents(buf, count)

def t_vector3int16(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        x, y, z = struct.unpack_from('<3h', buf, pos); pos += 6
        out.append({'x': x, 'y': y, 'z': z})
    return out

def t_numbersequence(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        n = int.from_bytes(buf[pos:pos+4], 'little'); pos += 4
        keypoints = []
        for _ in range(n):
            t, v, env = struct.unpack_from('<3f', buf, pos); pos += 12
            keypoints.append({'time': t, 'value': v, 'envelope': env})
        out.append(keypoints)
    return out

def t_colorsequence(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        n = int.from_bytes(buf[pos:pos+4], 'little'); pos += 4
        keypoints = []
        for _ in range(n):
            t, r, g, b, env = struct.unpack_from('<5f', buf, pos); pos += 20
            keypoints.append({'time': t, 'r': r, 'g': g, 'b': b})
        out.append(keypoints)
    return out

def t_numberrange(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        mn, mx = struct.unpack_from('<2f', buf, pos); pos += 8
        out.append({'min': mn, 'max': mx})
    return out

def t_rect(buf, count):
    minx = read_interleaved_roblox_float_array(buf[0:4*count], count)
    miny = read_interleaved_roblox_float_array(buf[4*count:8*count], count)
    maxx = read_interleaved_roblox_float_array(buf[8*count:12*count], count)
    maxy = read_interleaved_roblox_float_array(buf[12*count:16*count], count)
    return [{'min': (minx[i], miny[i]), 'max': (maxx[i], maxy[i])} for i in range(count)]

def t_physicalproperties(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        flag = buf[pos]; pos += 1
        if flag & 1:
            n = 6 if (flag & 2) else 5
            vals = struct.unpack_from(f'<{n}f', buf, pos); pos += 4*n
            keys = ['density','friction','elasticity','frictionWeight','elasticityWeight']
            if n == 6:
                keys.append('acousticAbsorption')
            out.append(dict(zip(keys, vals)))
        else:
            out.append(None)
    return out

def t_color3uint8(buf, count):
    r = buf[0:count]; g = buf[count:2*count]; b = buf[2*count:3*count]
    return [{'r': r[i], 'g': g[i], 'b': b[i]} for i in range(count)]

def t_int64(buf, count):
    raw = read_interleaved_u64_array(buf, count)
    return [untransform_i64(v) for v in raw]

def t_sharedstring(buf, count):
    return read_interleaved_u32_array(buf, count)

def t_uniqueid(buf, count):
    raw = read_interleaved_array(buf, count, 16)
    out = []
    for v in raw:
        index = (v >> 96) & 0xFFFFFFFF
        time_ = (v >> 64) & 0xFFFFFFFF
        random = v & 0xFFFFFFFFFFFFFFFF
        out.append({'index': index, 'time': time_, 'random': random})
    return out

def t_font(buf, count):
    out = []
    pos = 0
    for _ in range(count):
        l = int.from_bytes(buf[pos:pos+4], 'little'); pos += 4
        family = buf[pos:pos+l].decode('utf-8', 'replace'); pos += l
        weight = int.from_bytes(buf[pos:pos+2], 'little'); pos += 2
        style = buf[pos]; pos += 1
        l2 = int.from_bytes(buf[pos:pos+4], 'little'); pos += 4
        cached = buf[pos:pos+l2].decode('utf-8', 'replace'); pos += l2
        out.append({'family': family, 'weight': weight, 'style': style, 'cachedFaceId': cached})
    return out


# ====================== TYPE SERIALIZERS (write) ======================

def s_string(vals):
    return write_string_array([str(v) if v is not None else '' for v in vals])

def s_bool(vals):
    return bytes([1 if v else 0 for v in vals])

def s_int32(vals):
    raw = [transform_i32(int(v) if v is not None else 0) for v in vals]
    return write_interleaved_u32_array(raw)

def s_float32(vals):
    return write_interleaved_roblox_float_array([float(v) if v is not None else 0.0 for v in vals])

def s_float64(vals):
    return struct.pack(f'<{len(vals)}d', *[float(v) if v is not None else 0.0 for v in vals])

def s_udim(vals):
    scales = []
    offsets = []
    for v in vals:
        if isinstance(v, dict):
            scales.append(float(v.get('scale', 0)))
            offsets.append(int(v.get('offset', 0)))
        else:
            scales.append(0.0)
            offsets.append(0)
    return write_interleaved_roblox_float_array(scales) + s_int32(offsets)

def s_udim2(vals):
    sx, sy, ox, oy = [], [], [], []
    for v in vals:
        if isinstance(v, dict):
            x = v.get('x', {})
            y = v.get('y', {})
            if isinstance(x, dict):
                sx.append(float(x.get('scale', 0)))
                ox.append(int(x.get('offset', 0)))
            else:
                sx.append(0.0); ox.append(0)
            if isinstance(y, dict):
                sy.append(float(y.get('scale', 0)))
                oy.append(int(y.get('offset', 0)))
            else:
                sy.append(0.0); oy.append(0)
        else:
            sx.append(0.0); sy.append(0.0)
            ox.append(0); oy.append(0)
    return (write_interleaved_roblox_float_array(sx) +
            write_interleaved_roblox_float_array(sy) +
            s_int32(ox) + s_int32(oy))

def s_ray(vals):
    buf = bytearray()
    for v in vals:
        if isinstance(v, dict):
            origin = v.get('origin', [0,0,0])
            direction = v.get('direction', [0,0,0])
            buf.extend(struct.pack('<6f', 
                float(origin[0]) if len(origin) > 0 else 0.0,
                float(origin[1]) if len(origin) > 1 else 0.0,
                float(origin[2]) if len(origin) > 2 else 0.0,
                float(direction[0]) if len(direction) > 0 else 0.0,
                float(direction[1]) if len(direction) > 1 else 0.0,
                float(direction[2]) if len(direction) > 2 else 0.0
            ))
        else:
            buf.extend(struct.pack('<6f', 0,0,0,0,0,0))
    return bytes(buf)

def s_faces(vals):
    return bytes([int(v) if v is not None else 0 for v in vals])

def s_axes(vals):
    return bytes([int(v) if v is not None else 0 for v in vals])

def s_brickcolor(vals):
    return write_interleaved_u32_array([int(v) if v is not None else 0 for v in vals])

def s_color3(vals):
    r, g, b = [], [], []
    for v in vals:
        if isinstance(v, dict):
            r.append(float(v.get('r', 0)))
            g.append(float(v.get('g', 0)))
            b.append(float(v.get('b', 0)))
        else:
            r.append(0.0); g.append(0.0); b.append(0.0)
    return (write_interleaved_roblox_float_array(r) +
            write_interleaved_roblox_float_array(g) +
            write_interleaved_roblox_float_array(b))

def s_vector2(vals):
    x, y = [], []
    for v in vals:
        if isinstance(v, dict):
            x.append(float(v.get('x', 0)))
            y.append(float(v.get('y', 0)))
        else:
            x.append(0.0); y.append(0.0)
    return (write_interleaved_roblox_float_array(x) +
            write_interleaved_roblox_float_array(y))

def s_vector3(vals):
    x, y, z = [], [], []
    for v in vals:
        if isinstance(v, dict):
            x.append(float(v.get('x', 0)))
            y.append(float(v.get('y', 0)))
            z.append(float(v.get('z', 0)))
        else:
            x.append(0.0); y.append(0.0); z.append(0.0)
    return (write_interleaved_roblox_float_array(x) +
            write_interleaved_roblox_float_array(y) +
            write_interleaved_roblox_float_array(z))

_ANGLE_IDS_TO_CFRAME = {v: k for k, v in _CFRAME_ANGLE_IDS.items()}

def s_cframe(vals):
    buf = bytearray()
    positions = []
    for v in vals:
        if isinstance(v, dict):
            if 'special_id' in v:
                buf.append(v['special_id'])
            elif 'angles_deg' in v:
                angles = tuple(v['angles_deg'])
                buf.append(_ANGLE_IDS_TO_CFRAME.get(angles, 0x02))
            elif 'matrix' in v:
                buf.append(0x00)
                mat = v['matrix']
                if len(mat) >= 9:
                    buf.extend(struct.pack('<9f', *[float(x) for x in mat[:9]]))
                else:
                    buf.extend(struct.pack('<9f', 1,0,0,0,1,0,0,0,1))
            else:
                buf.append(0x02)
            positions.append(v.get('position', {'x':0,'y':0,'z':0}))
        else:
            buf.append(0x02)
            positions.append({'x':0,'y':0,'z':0})
    buf.extend(s_vector3(positions))
    return bytes(buf)

def s_enum(vals):
    return write_interleaved_u32_array([int(v) if v is not None else 0 for v in vals])

def s_referent(vals):
    return write_referents([int(v) if v is not None else 0 for v in vals])

def s_vector3int16(vals):
    buf = bytearray()
    for v in vals:
        if isinstance(v, dict):
            buf.extend(struct.pack('<3h', 
                int(v.get('x', 0)), int(v.get('y', 0)), int(v.get('z', 0))))
        else:
            buf.extend(struct.pack('<3h', 0, 0, 0))
    return bytes(buf)

def s_numbersequence(vals):
    buf = bytearray()
    for v in vals:
        keypoints = v if isinstance(v, list) else []
        buf.extend(struct.pack('<I', len(keypoints)))
        for kp in keypoints:
            if isinstance(kp, dict):
                buf.extend(struct.pack('<3f', 
                    float(kp.get('time', 0)),
                    float(kp.get('value', 0)),
                    float(kp.get('envelope', 0))))
            else:
                buf.extend(struct.pack('<3f', 0.0, 0.0, 0.0))
    return bytes(buf)

def s_colorsequence(vals):
    buf = bytearray()
    for v in vals:
        keypoints = v if isinstance(v, list) else []
        buf.extend(struct.pack('<I', len(keypoints)))
        for kp in keypoints:
            if isinstance(kp, dict):
                buf.extend(struct.pack('<5f',
                    float(kp.get('time', 0)),
                    float(kp.get('r', 0)),
                    float(kp.get('g', 0)),
                    float(kp.get('b', 0)),
                    0.0))
            else:
                buf.extend(struct.pack('<5f', 0.0, 0.0, 0.0, 0.0, 0.0))
    return bytes(buf)

def s_numberrange(vals):
    buf = bytearray()
    for v in vals:
        if isinstance(v, dict):
            buf.extend(struct.pack('<2f', 
                float(v.get('min', 0)), float(v.get('max', 0))))
        else:
            buf.extend(struct.pack('<2f', 0.0, 0.0))
    return bytes(buf)

def s_rect(vals):
    minx, miny, maxx, maxy = [], [], [], []
    for v in vals:
        if isinstance(v, dict):
            mn = v.get('min', (0,0))
            mx = v.get('max', (0,0))
            minx.append(float(mn[0]) if len(mn) > 0 else 0.0)
            miny.append(float(mn[1]) if len(mn) > 1 else 0.0)
            maxx.append(float(mx[0]) if len(mx) > 0 else 0.0)
            maxy.append(float(mx[1]) if len(mx) > 1 else 0.0)
        else:
            minx.append(0.0); miny.append(0.0)
            maxx.append(0.0); maxy.append(0.0)
    return (write_interleaved_roblox_float_array(minx) +
            write_interleaved_roblox_float_array(miny) +
            write_interleaved_roblox_float_array(maxx) +
            write_interleaved_roblox_float_array(maxy))

def s_physicalproperties(vals):
    buf = bytearray()
    for v in vals:
        if v is None:
            buf.append(0)
        else:
            flag = 1
            keys = ['density', 'friction', 'elasticity', 'frictionWeight', 'elasticityWeight']
            if isinstance(v, dict) and 'acousticAbsorption' in v:
                flag |= 2
                keys.append('acousticAbsorption')
            buf.append(flag)
            for k in keys:
                buf.extend(struct.pack('<f', float(v.get(k, 0)) if isinstance(v, dict) else 0.0))
    return bytes(buf)

def s_color3uint8(vals):
    r, g, b = [], [], []
    for v in vals:
        if isinstance(v, dict):
            r.append(int(v.get('r', 0)))
            g.append(int(v.get('g', 0)))
            b.append(int(v.get('b', 0)))
        else:
            r.append(0); g.append(0); b.append(0)
    return bytes(r + g + b)

def s_int64(vals):
    raw = [transform_i64(int(v) if v is not None else 0) for v in vals]
    return write_interleaved_u64_array(raw)

def s_sharedstring(vals):
    return write_interleaved_u32_array([int(v) if v is not None else 0 for v in vals])

def s_uniqueid(vals):
    buf = bytearray()
    for v in vals:
        if isinstance(v, dict):
            index = int(v.get('index', 0))
            time_ = int(v.get('time', 0))
            random = int(v.get('random', 0))
        else:
            index = time_ = random = 0
        val = (index << 96) | (time_ << 64) | random
        buf.extend(struct.pack('<QQ', val & 0xFFFFFFFFFFFFFFFF, val >> 64))
    return bytes(buf)

def s_font(vals):
    buf = bytearray()
    for v in vals:
        if isinstance(v, dict):
            family = str(v.get('family', ''))
            family_bytes = family.encode('utf-8')
            buf.extend(struct.pack('<I', len(family_bytes)))
            buf.extend(family_bytes)
            buf.extend(struct.pack('<H', int(v.get('weight', 400))))
            buf.append(int(v.get('style', 0)))
            cached = str(v.get('cachedFaceId', ''))
            cached_bytes = cached.encode('utf-8')
            buf.extend(struct.pack('<I', len(cached_bytes)))
            buf.extend(cached_bytes)
        else:
            buf.extend(struct.pack('<I', 0))
            buf.extend(struct.pack('<H', 400))
            buf.append(0)
            buf.extend(struct.pack('<I', 0))
    return bytes(buf)


# ====================== TYPE MAPS ======================

TYPE_DECODERS = {
    0x01: t_string, 0x02: t_bool, 0x03: t_int32, 0x04: t_float32,
    0x05: t_float64, 0x06: t_udim, 0x07: t_udim2, 0x08: t_ray,
    0x09: t_faces, 0x0a: t_axes, 0x0b: t_brickcolor, 0x0c: t_color3,
    0x0d: t_vector2, 0x0e: t_vector3, 0x10: t_cframe, 0x12: t_enum,
    0x13: t_referent, 0x14: t_vector3int16, 0x15: t_numbersequence,
    0x16: t_colorsequence, 0x17: t_numberrange, 0x18: t_rect,
    0x19: t_physicalproperties, 0x1a: t_color3uint8, 0x1b: t_int64,
    0x1c: t_sharedstring, 0x1d: t_string, 0x1f: t_uniqueid, 0x20: t_font,
}

TYPE_SERIALIZERS = {
    0x01: s_string, 0x02: s_bool, 0x03: s_int32, 0x04: s_float32,
    0x05: s_float64, 0x06: s_udim, 0x07: s_udim2, 0x08: s_ray,
    0x09: s_faces, 0x0a: s_axes, 0x0b: s_brickcolor, 0x0c: s_color3,
    0x0d: s_vector2, 0x0e: s_vector3, 0x10: s_cframe, 0x12: s_enum,
    0x13: s_referent, 0x14: s_vector3int16, 0x15: s_numbersequence,
    0x16: s_colorsequence, 0x17: s_numberrange, 0x18: s_rect,
    0x19: s_physicalproperties, 0x1a: s_color3uint8, 0x1b: s_int64,
    0x1c: s_sharedstring, 0x1d: s_string, 0x1f: s_uniqueid, 0x20: s_font,
}


# ====================== Parse / Save ======================

def parse_rbxl(path):
    """Парсит .rbxl файл и возвращает структуру данных"""
    chunks = read_chunks(path)
    class_id_to_referents = {}
    class_id_to_name = {}
    referent_to_class = {}
    
    for chunk in chunks:
        if chunk['name'] == b'INST':
            class_id, class_name, obj_fmt, referents = parse_inst(chunk['payload'])
            class_id_to_referents[class_id] = referents
            class_id_to_name[class_id] = class_name
            for r in referents:
                referent_to_class[r] = class_name

    parent_map = {}
    for chunk in chunks:
        if chunk['name'] == b'PRNT':
            for child, parent in parse_prnt(chunk['payload']):
                parent_map[child] = parent

    props = {}
    skipped = 0
    for chunk in chunks:
        if chunk['name'] == b'PROP':
            try:
                class_id, prop_name, type_id, rest = parse_prop_header(chunk['payload'])
                referents = class_id_to_referents.get(class_id, [])
                count = len(referents)
                decoder = TYPE_DECODERS.get(type_id)
                if decoder is None:
                    skipped += 1
                    continue
                values = decoder(rest, count)
                for r, v in zip(referents, values):
                    props.setdefault(r, {})[prop_name] = v
            except Exception:
                skipped += 1
                continue

    # Пост-обработка: разбиваем CFrame на Position и Rotation
    for ref, obj_props in props.items():
        if 'CFrame' in obj_props:
            cf = obj_props['CFrame']
            
            if isinstance(cf, dict) and 'matrix' in cf:
                matrix = cf['matrix']
                
                # Безопасно извлекаем позицию
                position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                if len(matrix) > 3:
                    position['x'] = float(matrix[3])
                if len(matrix) > 7:
                    position['y'] = float(matrix[7])
                if len(matrix) > 11:
                    position['z'] = float(matrix[11])
                
                obj_props['Position'] = position
                
                # Безопасно извлекаем rotation
                if len(matrix) >= 12:
                    m00 = float(matrix[0]) if len(matrix) > 0 else 1.0
                    m01 = float(matrix[1]) if len(matrix) > 1 else 0.0
                    m02 = float(matrix[2]) if len(matrix) > 2 else 0.0
                    m10 = float(matrix[4]) if len(matrix) > 4 else 0.0
                    m11 = float(matrix[5]) if len(matrix) > 5 else 1.0
                    m12 = float(matrix[6]) if len(matrix) > 6 else 0.0
                    m20 = float(matrix[8]) if len(matrix) > 8 else 0.0
                    m21 = float(matrix[9]) if len(matrix) > 9 else 0.0
                    m22 = float(matrix[10]) if len(matrix) > 10 else 1.0
                    
                    sy = math.sqrt(m00*m00 + m10*m10)
                    singular = sy < 1e-6
                    
                    if not singular:
                        rx = math.atan2(m21, m22)
                        ry = math.atan2(-m20, sy)
                        rz = math.atan2(m10, m00)
                    else:
                        rx = math.atan2(-m12, m11)
                        ry = math.atan2(-m20, sy)
                        rz = 0
                    
                    rotation = {
                        'x': round(math.degrees(rx), 2),
                        'y': round(math.degrees(ry), 2),
                        'z': round(math.degrees(rz), 2)
                    }
                else:
                    rotation = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                
                obj_props['Rotation'] = rotation
                
            elif isinstance(cf, dict) and 'position' in cf:
                obj_props['Position'] = cf['position']
                
                if 'angles_deg' in cf and cf['angles_deg']:
                    angles = cf['angles_deg']
                    obj_props['Rotation'] = {
                        'x': float(angles[0]) if len(angles) > 0 else 0.0,
                        'y': float(angles[1]) if len(angles) > 1 else 0.0,
                        'z': float(angles[2]) if len(angles) > 2 else 0.0
                    }
                else:
                    obj_props['Rotation'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            else:
                obj_props['Position'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                obj_props['Rotation'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Обработка Size
        cls = referent_to_class.get(ref, '')
        if cls in ('Part', 'WedgePart', 'SpherePart', 'MeshPart', 'TrussPart', 
                    'CornerWedgePart', 'SpawnLocation', 'Seat', 'VehicleSeat'):
            
            if 'size' in obj_props and 'Size' not in obj_props:
                obj_props['Size'] = obj_props['size']
            
            size = obj_props.get('Size', obj_props.get('size', {}))
            
            if isinstance(size, dict):
                obj_props['Size'] = {
                    'x': float(size.get('x', size.get('X', 4.0))),
                    'y': float(size.get('y', size.get('Y', 1.2))),
                    'z': float(size.get('z', size.get('Z', 2.0)))
                }
            elif isinstance(size, (list, tuple)) and len(size) >= 3:
                obj_props['Size'] = {
                    'x': float(size[0]),
                    'y': float(size[1]),
                    'z': float(size[2])
                }
            else:
                obj_props['Size'] = {'x': 4.0, 'y': 1.2, 'z': 2.0}
        
        # Обработка цвета
        if 'Color3' in obj_props or 'Color' in obj_props or 'BrickColor' in obj_props:
            color = obj_props.get('Color3') or obj_props.get('Color') or obj_props.get('BrickColor')
            if isinstance(color, dict) and 'r' in color and 'g' in color and 'b' in color:
                r = color['r']
                g = color['g']
                b = color['b']
                if r > 1 or g > 1 or b > 1:
                    r = r / 255.0
                    g = g / 255.0
                    b = b / 255.0
                obj_props['Color3'] = {'r': round(r, 3), 'g': round(g, 3), 'b': round(b, 3)}
            elif isinstance(color, (int, float)):
                brick_colors = {
                    1: {'r': 0.95, 'g': 0.95, 'b': 0.95},
                    5: {'r': 0.76, 'g': 0.69, 'b': 0.50},
                    11: {'r': 0.39, 'g': 0.58, 'b': 0.93},
                    21: {'r': 0.77, 'g': 0.15, 'b': 0.15},
                    23: {'r': 0.05, 'g': 0.41, 'b': 0.79},
                    26: {'r': 0.16, 'g': 0.16, 'b': 0.16},
                    28: {'r': 0.15, 'g': 0.68, 'b': 0.38},
                    37: {'r': 0.29, 'g': 0.51, 'b': 0.27},
                    38: {'r': 0.63, 'g': 0.37, 'b': 0.15},
                    101: {'r': 0.79, 'g': 0.42, 'b': 0.48},
                    102: {'r': 0.38, 'g': 0.37, 'b': 0.69},
                    104: {'r': 0.42, 'g': 0.20, 'b': 0.69},
                    105: {'r': 0.89, 'g': 0.60, 'b': 0.30},
                    106: {'r': 0.96, 'g': 0.54, 'b': 0.21},
                    107: {'r': 0.05, 'g': 0.63, 'b': 0.73},
                    119: {'r': 0.64, 'g': 0.75, 'b': 0.36},
                    125: {'r': 0.91, 'g': 0.62, 'b': 0.38},
                    135: {'r': 0.47, 'g': 0.60, 'b': 0.67},
                    141: {'r': 0.16, 'g': 0.20, 'b': 0.22},
                    194: {'r': 0.39, 'g': 0.39, 'b': 0.39},
                    199: {'r': 0.38, 'g': 0.37, 'b': 0.33},
                    217: {'r': 0.50, 'g': 0.30, 'b': 0.16},
                    226: {'r': 0.99, 'g': 0.84, 'b': 0.39},
                }
                color_obj = brick_colors.get(int(color), {'r': 0.6, 'g': 0.6, 'b': 0.6})
                obj_props['Color3'] = color_obj
            else:
                obj_props['Color3'] = {'r': 0.6, 'g': 0.6, 'b': 0.6}
        
        # Обработка прозрачности
        if 'Transparency' in obj_props:
            trans = obj_props['Transparency']
            if isinstance(trans, (int, float)):
                obj_props['Transparency'] = max(0.0, min(1.0, float(trans)))
            else:
                obj_props['Transparency'] = 0.0
        else:
            obj_props['Transparency'] = 0.0
        
        # Обработка текстур
        if 'Texture' in obj_props or 'TextureID' in obj_props:
            texture = obj_props.get('Texture') or obj_props.get('TextureID')
            if isinstance(texture, str):
                obj_props['Texture'] = texture
            elif isinstance(texture, bytes):
                try:
                    obj_props['Texture'] = texture.decode('utf-8')
                except:
                    obj_props['Texture'] = ''
        
        if 'Decal' in obj_props:
            decal = obj_props['Decal']
            if isinstance(decal, str):
                obj_props['Decal'] = decal
            elif isinstance(decal, bytes):
                try:
                    obj_props['Decal'] = decal.decode('utf-8')
                except:
                    pass
        
        # Собираем пути к ассетам
        asset_paths = []
        for key in ['Texture', 'TextureID', 'Decal', 'MeshId', 'Image', 'SoundId']:
            val = obj_props.get(key)
            if isinstance(val, str) and val:
                asset_paths.append(val)
        
        if asset_paths:
            obj_props['_assets'] = asset_paths

    # Сохраняем сырые данные
    raw_data = open(path, 'rb').read()
    file_size = os.path.getsize(path)
    
    return {
        'referent_to_class': referent_to_class,
        'parent_map': parent_map,
        'props': props,
        'class_id_to_name': class_id_to_name,
        'class_id_to_referents': class_id_to_referents,
        'skipped_prop_chunks': skipped,
        '_raw_chunks': chunks,
        '_raw_data': raw_data,
        '_file_size': file_size,
        '_file_path': str(Path(path).absolute()),
    }


def save_rbxl(parsed: dict, path: str):
    """Сохранить в бинарный формат RBXL"""
    
    if not parsed.get('_modified', False) and '_raw_data' in parsed:
        with open(path, 'wb') as f:
            f.write(parsed['_raw_data'])
        return True
    
    raw_chunks = parsed.get('_raw_chunks', [])
    if raw_chunks and not parsed.get('_modified', False):
        file_data = bytearray()
        if '_raw_data' in parsed:
            file_data.extend(parsed['_raw_data'][:32])
        
        for chunk in raw_chunks:
            if chunk['name'] == b'END\x00':
                continue
            file_data.extend(write_chunk_raw(chunk))
        
        file_data.extend(write_chunk(b'END\x00', b''))
        
        with open(path, 'wb') as f:
            f.write(bytes(file_data))
        return True
    
    referent_to_class = parsed['referent_to_class']
    parent_map = parsed['parent_map']
    props = parsed['props']
    class_id_to_name = parsed.get('class_id_to_name', {})
    class_id_to_referents = parsed.get('class_id_to_referents', {})
    
    class_to_refs = {}
    if class_id_to_name and class_id_to_referents:
        for class_id, class_name in class_id_to_name.items():
            referents = class_id_to_referents.get(class_id, [])
            if referents:
                class_to_refs[class_name] = sorted(referents)
    
    if not class_to_refs:
        for ref, cls in referent_to_class.items():
            if cls not in class_to_refs:
                class_to_refs[cls] = []
            class_to_refs[cls].append(ref)
        for cls in class_to_refs:
            class_to_refs[cls] = sorted(class_to_refs[cls])
    
    class_id_map = {}
    class_id = 0
    for cls_name in sorted(class_to_refs.keys()):
        class_id_map[cls_name] = class_id
        class_id += 1
    
    file_data = bytearray()
    
    file_data.extend(b'roblox!\x00')
    file_data.extend(struct.pack('<I', 0))
    file_data.extend(struct.pack('<I', len(class_to_refs)))
    file_data.extend(struct.pack('<I', len(referent_to_class)))
    file_data.extend(struct.pack('<I', 0))
    file_data.extend(b'\x00' * 8)
    
    for cls_name in sorted(class_to_refs.keys()):
        referents = class_to_refs[cls_name]
        cid = class_id_map[cls_name]
        inst_payload = write_inst(cid, cls_name, referents)
        file_data.extend(write_chunk(b'INST', inst_payload))
    
    pairs = [(child, parent) for child, parent in parent_map.items()]
    if pairs:
        prnt_payload = write_prnt(pairs)
        file_data.extend(write_chunk(b'PRNT', prnt_payload))
    
    for cls_name, referents in class_to_refs.items():
        cid = class_id_map[cls_name]
        class_props = {}
        for ref in referents:
            if ref in props:
                for pname, pval in props[ref].items():
                    if pname not in class_props:
                        class_props[pname] = {}
                    class_props[pname][ref] = pval
        
        for pname, ref_values in class_props.items():
            sample_value = next((v for v in ref_values.values() if v is not None), None)
            
            type_id = 0x01
            if sample_value is not None:
                if isinstance(sample_value, str):
                    type_id = 0x01
                elif isinstance(sample_value, bool):
                    type_id = 0x02
                elif isinstance(sample_value, int):
                    type_id = 0x03
                elif isinstance(sample_value, float):
                    type_id = 0x04
                elif isinstance(sample_value, dict):
                    if 'r' in sample_value and 'g' in sample_value and 'b' in sample_value:
                        r = sample_value.get('r', 0)
                        if isinstance(r, float) and r <= 1.0:
                            type_id = 0x0c
                        else:
                            type_id = 0x1a
                    elif 'matrix' in sample_value or 'position' in sample_value:
                        type_id = 0x10
                    elif 'x' in sample_value and 'y' in sample_value and 'z' in sample_value:
                        type_id = 0x0e
                    elif 'x' in sample_value and 'y' in sample_value:
                        if 'scale' in sample_value.get('x', {}):
                            type_id = 0x07
                        else:
                            type_id = 0x0d
                    elif 'scale' in sample_value and 'offset' in sample_value:
                        type_id = 0x06
                    elif 'index' in sample_value and 'time' in sample_value:
                        type_id = 0x1f
                    elif 'family' in sample_value:
                        type_id = 0x20
                    elif 'min' in sample_value and 'max' in sample_value:
                        type_id = 0x17
                    else:
                        type_id = 0x01
            
            values = [ref_values.get(ref) for ref in referents]
            
            serializer = TYPE_SERIALIZERS.get(type_id, s_string)
            try:
                serialized_values = serializer(values)
            except Exception:
                serialized_values = s_string(values)
            
            prop_header = write_prop_header(cid, pname, type_id)
            prop_payload = prop_header + serialized_values
            file_data.extend(write_chunk(b'PROP', prop_payload))
    
    file_data.extend(write_chunk(b'END\x00', b''))
    
    with open(path, 'wb') as f:
        f.write(bytes(file_data))
    
    return True


def publish_place(rbxl_path, universe_id, place_id, api_key, version_type="Published"):
    """Публикует плейс в Roblox через Open Cloud API"""
    url = f"https://apis.roblox.com/universes/v1/{universe_id}/places/{place_id}/versions"
    params = {"versionType": version_type}
    headers = {"x-api-key": api_key, "Content-Type": "application/octet-stream"}
    with open(rbxl_path, "rb") as f:
        data = f.read()
    try:
        import requests
        resp = requests.post(url, params=params, headers=headers, data=data)
        return resp.status_code, resp.text
    except ImportError:
        import urllib.request, urllib.parse
        full_url = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(full_url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()