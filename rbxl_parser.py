import sys
import struct
import json
import os
import math
from pathlib import Path

try:
    import zstandard as _zstd
except Exception:
    _zstd = None

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
        # compsize == 0 по спецификации значит «чанк не сжат»: сами данные
        # лежат сразу за заголовком и занимают uncompsize байт (так хранится
        # END-чанк, и так же пишут файлы, например, Rojo без сжатия).
        stored_len = compsize if compsize else uncompsize
        raw = data[pos+16:pos+16+stored_len]
        payload = None
        if compsize == 0:
            payload = raw[:uncompsize]
        elif raw[:4] == b'\x28\xb5\x2f\xfd':
            # Zstandard frame magic — новые версии Roblox Studio (2024+)
            # сжимают чанки zstd вместо lz4 (старый Castle Warfare.rbxl был
            # ещё lz4, отсюда и падение на UTF-8: lz4_decompress() тихо
            # съедала zstd-байты как будто это lz4-поток и отдавала мусор).
            if _zstd is None:
                raise RuntimeError(
                    "Этот .rbxl сжат zstd, а пакет 'zstandard' не установлен "
                    "(pip install zstandard --break-system-packages)"
                )
            try:
                payload = _zstd.ZstdDecompressor().decompress(raw, max_output_size=uncompsize)
                if len(payload) != uncompsize:
                    payload = None
            except Exception:
                payload = None
            if payload is None:
                payload = raw
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
        pos += 16 + stored_len
    return chunks


def write_chunk(name: bytes, payload: bytes) -> bytes:
    # Несжатый чанк: compressed length = 0, uncompressed length = len(payload)
    # (см. комментарий в read_chunks). Раньше сюда писали len(payload) в оба
    # поля — формально это «сжатый» чанк, который настоящие читатели пытаются
    # распаковать как LZ4.
    header = struct.pack('<4sIII',
        name,
        0,
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
    # БАГ-ФИКС: раньше маскирование "v &= 0xFFFFFFFF" выполнялось ДО
    # проверки знака. В Python это приводит к тому, что отрицательные v
    # после маскирования превращаются в большие положительные числа
    # (двоичное дополнение), поэтому "if v >= 0" была ВСЕГДА истинной —
    # ветка для отрицательных чисел никогда не выполнялась, и zigzag-
    # кодирование отрицательных дельт референсов было битым. Это ломало
    # родительские связи (PRNT-чанк) при полной пересборке .rbxl с нуля
    # (см. save_rbxl), как только порядок referent'ов давал отрицательную
    # дельту между соседними записями — типичный случай, когда новый
    # объект вставляется куда-то в середину дерева. Проверяем знак ДО
    # маскирования.
    if v >= 0:
        return (v << 1) & 0xFFFFFFFF
    else:
        return ((-v << 1) - 1) & 0xFFFFFFFF

def transform_i64(v):
    # Тот же фикс, что и в transform_i32 — см. комментарий выше.
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

def untransform_referent_delta(v):
    # Обычный zigzag-декод (как и untransform_i32), ПЛЮС компенсация старого
    # бага в transform_i32 (см. комментарий у него): та версия маскировала
    # v в 0xFFFFFFFF ДО проверки знака, из-за чего отрицательные дельты
    # референсов кодировались как ((v & 0xFFFFFFFF) << 1) вместо честного
    # zigzag. Файлы, пересохранённые ТОЙ версией (например, если карта
    # когда-то была открыта/сохранена этим инструментом до фикса),
    # физически содержат испорченные PRNT/INST-referent'ы — при обычном
    # zigzag-декодировании такая запись даёт дельту, отличающуюся от
    # настоящей ровно на 2^31 (или -2^31), и поскольку это ДЕЛЬТА,
    # прибавляемая к аккумулятору, одна испорченная запись сдвигает ВСЕ
    # референсы после неё на миллиарды — что и превращало parent_map в
    # мусор для virtualtually каждого объекта после первого же такого
    # случая. Настоящие дельты референсов в файле с несколькими тысячами
    # объектов заведомо малы (даже в огромной карте не превышают
    # текущего количества объектов), так что неправдоподобно большая
    # дельта — надёжный признак именно этой порчи, а не осознанного
    # большого шага.
    delta = (v >> 1) ^ -(v & 1)
    if delta > (1 << 30):
        delta -= (1 << 31)
    elif delta < -(1 << 30):
        delta += (1 << 31)
    return delta


def read_referents(buf, count):
    raw = read_interleaved_u32_array(buf, count)
    acc = 0
    out = []
    for r in raw:
        acc += untransform_referent_delta(r)
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

def write_inst(class_id: int, class_name: str, referents: list, service_flags=None) -> bytes:
    buf = bytearray()
    buf.extend(struct.pack('<I', class_id))
    name_bytes = class_name.encode('utf-8')
    buf.extend(struct.pack('<I', len(name_bytes)))
    buf.extend(name_bytes)
    # object_format 1 = у класса есть сервисы: после referent'ов идёт по
    # байту-флагу на каждый инстанс (1 — это сервис, например Workspace).
    has_services = bool(service_flags) and any(service_flags)
    buf.append(1 if has_services else 0)
    buf.extend(struct.pack('<I', len(referents)))
    buf.extend(write_referents(referents))
    if has_services:
        buf.extend(bytes(1 if f else 0 for f in service_flags))
    return bytes(buf)


def parse_inst_service_flags(payload, count):
    """Флаги «этот инстанс — сервис» из INST-чанка с object_format == 1."""
    name_len = int.from_bytes(payload[4:8], 'little')
    pos = 8 + name_len + 1 + 4 + 4 * count
    return list(payload[pos:pos + count])


def parse_sstr(payload):
    """SSTR-чанк -> список (md5-хеш 16 байт, данные). Индекс в списке — это
    значение свойств типа SharedString (0x1c)."""
    count = int.from_bytes(payload[4:8], 'little')
    pos = 8
    out = []
    for _ in range(count):
        h = payload[pos:pos + 16]; pos += 16
        ln = int.from_bytes(payload[pos:pos + 4], 'little'); pos += 4
        out.append((h, payload[pos:pos + ln])); pos += ln
    return out


def write_sstr(strings):
    buf = bytearray(struct.pack('<II', 0, len(strings)))
    for h, data in strings:
        buf.extend(h)
        buf.extend(struct.pack('<I', len(data)))
        buf.extend(data)
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
    # bytes (не-UTF-8 строки, например AttributesSerialize) остаются как есть:
    # раньше str(v) превращал их в литерал "b'...'" и портил данные при записи.
    return write_string_array([
        v if isinstance(v, (str, bytes)) else ('' if v is None else str(v))
        for v in vals
    ])

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


def _infer_type_id(sample_value):
    """Угадывает type_id по Python-значению. Только запасной вариант для
    свойств, тип которых не известен из файла (созданных в редакторе)."""
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
                # UDim2 (x/y — вложенные {scale, offset}) отличаем от
                # Vector2 (x/y — голые числа, например GuiObject.
                # AnchorPoint — то, что реально есть почти в любом
                # UI-меню). Раньше здесь безусловно делали
                # sample_value.get('x', {}) и тут же проверяли
                # 'scale' in <результат> — для Vector2 результат был
                # float, а не dict, и "in" на float падал с
                # TypeError, спуская ЛЮБОЕ сохранение файла с хотя бы
                # одним Vector2-свойством где-то в дереве.
                xval = sample_value.get('x')
                if isinstance(xval, dict) and 'scale' in xval:
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
    return type_id


# ====================== Запись бинарного формата (rbxl / rbxm) ======================

RBX_MAGIC = b'<roblox!\x89\xff\r\n\x1a\n\x00\x00'   # сигнатура + версия формата (u16 = 0)

# Служебные ключи, которые parse_rbxl добавляет для удобства редактора — в
# реальном файле таких свойств нет, писать их нельзя.
_SYNTHETIC_PROPS = {'_assets'}
# Производные имена: настоящее свойство лежит под другим именем (size,
# Color3uint8/BrickColor, TextureID...). Пишем их, только если файл сам
# содержал свойство с таким именем у этого класса.
_DERIVED_PROPS = {'Size', 'Color3', 'Transparency', 'Texture', 'Decal'}
# Значения свойств по умолчанию (только отличающиеся от нулевых), из
# rbx_reflection_database (rojo-rbx/rbx-dom, MIT). Studio не пишет свойства,
# у которых все объекты класса имеют дефолт, поэтому у импортированных или
# созданных объектов их нет, а массив свойства в файле обязан покрывать все
# объекты класса. Формат: {класс: {свойство: значение}}, zlib+base64.
_DEFAULTS_B64 = (
    "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"
)
_defaults_cache = None
# В файле эти свойства лежат под другими именами, чем в базе рефлексии.
_BINARY_TO_REFLECTION_NAME = {'Color3uint8': 'Color', 'size': 'Size', 'shape': 'Shape', 'formFactorRaw': 'FormFactor'}


def _class_defaults(cls):
    global _defaults_cache
    if _defaults_cache is None:
        import zlib, base64, json
        _defaults_cache = json.loads(zlib.decompress(base64.b64decode(_DEFAULTS_B64)))
    return _defaults_cache.get(cls, {})




def _norm_cframe(cf):
    """CFrame в двух внутренних видах -> {'matrix': 9 чисел, 'position': {...}}.
    Парсер отдаёт 9 чисел + position, а редактор при правке Rotation/Position
    пишет 12 чисел построчно (r00 r01 r02 px r10 ...)."""
    if isinstance(cf, dict):
        mat = cf.get('matrix')
        if isinstance(mat, (list, tuple)) and len(mat) >= 12:
            m = [float(x) for x in mat[:12]]
            return {
                'matrix': [m[0], m[1], m[2], m[4], m[5], m[6], m[8], m[9], m[10]],
                'position': {'x': m[3], 'y': m[7], 'z': m[11]},
            }
    return cf


def _writable_props(cls, p, known):
    """Оставляет только то, что реально существует как свойство в файле Roblox.
    known — имена свойств этого класса, увиденные в исходном файле."""
    out = {}
    has_cframe = 'CFrame' in p
    for name, val in p.items():
        if name in _SYNTHETIC_PROPS:
            continue
        # У частей Position/Rotation — производные от CFrame, а у GuiObject
        # это настоящие свойства (UDim2 / float): их отличает CFrame.
        if name in ('Position', 'Rotation') and has_cframe and name not in known:
            continue
        if known and name not in known and name in _DERIVED_PROPS:
            continue
        out[name] = val
    # Часть, созданная в редакторе: есть CFrame и Size, но нет настоящих
    # size/Color3uint8. (Без CFrame не трогаем: парсер сам подставляет
    # дефолтный Size частям без size, это не пользовательские данные.)
    sz = p.get('Size')
    if has_cframe and 'size' not in p and 'Size' not in known and isinstance(sz, dict) and 'z' in sz:
        out['size'] = sz
        col = p.get('Color')
        if ('Color3uint8' not in p and 'Color' not in known
                and isinstance(col, dict) and all(k in col for k in 'rgb')):
            out.pop('Color', None)
            scale = 255 if all(float(col[k]) <= 1.0 for k in 'rgb') else 1
            out['Color3uint8'] = {k: max(0, min(255, int(round(float(col[k]) * scale)))) for k in 'rgb'}
    return out


def build_rbx_binary(referent_to_class, parent_map, props, refs=None, prop_types=None,
                     shared_strings=None, service_refs=None, renumber=True):
    """Собирает бинарный .rbxl/.rbxm. Возвращает (bytes, warnings).

    refs — какие инстансы писать и в каком порядке (по умолчанию все, по
    возрастанию referent'а); родитель, которого нет в refs, превращается в
    «нет родителя» (-1) — так у rbxm появляются корни. Referent'ы в файле
    перенумеровываются 0..N-1 (renumber=True; для rbxm), либо остаются как
    есть (renumber=False; для сохранения сцены — номера стабильны между
    сохранениями). Ссылки-свойства (Part0, PrimaryPart...) на инстансы вне
    refs становятся nil."""
    warnings = []
    refs = sorted(referent_to_class) if refs is None else [r for r in refs if r in referent_to_class]
    idx = {r: i for i, r in enumerate(refs)} if renumber else {r: r for r in refs}
    prop_types = prop_types or {}
    shared_strings = shared_strings or []
    service_refs = service_refs or ()
    known = {}
    for (c, n) in prop_types:
        known.setdefault(c, set()).add(n)

    class_order, by_class = [], {}
    for r in refs:
        c = referent_to_class[r]
        if c not in by_class:
            by_class[c] = []
            class_order.append(c)
        by_class[c].append(r)
    class_id = {c: i for i, c in enumerate(class_order)}
    if not renumber:
        for c in class_order:
            by_class[c].sort()   # как в исходных файлах: referent'ы класса по возрастанию

    sstr_new, sstr_map = [], {}   # старый индекс SSTR -> новый

    inst_chunks, prop_chunks = [], []
    for c in class_order:
        rs = by_class[c]
        flags = [r in service_refs for r in rs]
        inst_chunks.append(write_chunk(b'INST', write_inst(class_id[c], c, [idx[r] for r in rs], flags)))

        per_prop = {}
        for r in rs:
            for name, val in _writable_props(c, props.get(r, {}), known.get(c, ())).items():
                per_prop.setdefault(name, {})[r] = val

        for name, ref_values in per_prop.items():
            sample = next((v for v in ref_values.values() if v is not None), None)
            type_id = prop_types.get((c, name)) or _infer_type_id(sample)
            vals = [ref_values.get(r) for r in rs]
            if None in vals:
                cd = _class_defaults(c)
                dv = cd.get(_BINARY_TO_REFLECTION_NAME.get(name, name))
                if dv is None and type_id == 0x0b:
                    dv = 194   # BrickColor 0 невалиден; 194 = Medium stone grey (серый по умолчанию)
                if dv is not None:
                    vals = [dv if v is None else v for v in vals]
            try:
                if type_id == 0x10:
                    vals = [_norm_cframe(v) for v in vals]
                elif type_id == 0x13:
                    vals = [idx.get(v, -1) if v is not None else -1 for v in vals]
                elif type_id == 0x1c:
                    remapped = []
                    for v in vals:
                        if v is None or not (0 <= int(v) < len(shared_strings)):
                            v = -1
                        else:
                            v = int(v)
                            if v not in sstr_map:
                                sstr_map[v] = len(sstr_new)
                                sstr_new.append(shared_strings[v])
                            v = sstr_map[v]
                        remapped.append(v)
                    # значения без SSTR-записи -> пустая строка в конце списка
                    if any(v == -1 for v in remapped):
                        empty = len(sstr_new)
                        sstr_new.append((b'\x00' * 16, b''))
                        remapped = [empty if v == -1 else v for v in remapped]
                    vals = remapped
                serializer = TYPE_SERIALIZERS.get(type_id)
                if serializer is None:
                    raise ValueError('нет сериализатора для типа 0x%02x' % type_id)
                payload = write_prop_header(class_id[c], name, type_id) + serializer(vals)
            except Exception as e:
                warnings.append('%s.%s пропущено: %s' % (c, name, e))
                continue
            prop_chunks.append(write_chunk(b'PROP', payload))

    pairs = []
    for r in refs:
        par = parent_map.get(r, -1)
        pairs.append((idx[r], idx.get(par, -1)))

    out = bytearray(RBX_MAGIC)
    out.extend(struct.pack('<II', len(class_order), len(refs)))
    out.extend(b'\x00' * 8)
    if sstr_new:
        out.extend(write_chunk(b'SSTR', write_sstr(sstr_new)))
    for ch in inst_chunks:
        out.extend(ch)
    for ch in prop_chunks:
        out.extend(ch)
    if pairs:
        out.extend(write_chunk(b'PRNT', write_prnt(pairs)))
    out.extend(write_chunk(b'END\x00', b'</roblox>'))
    return bytes(out), warnings


# ====================== rbxm: экспорт выбранных объектов / импорт в сцену ======================

# Сервисы нельзя положить в модель (rbxm — набор обычных инстансов). Основной
# признак — флаги object_format из файла (parsed['service_refs']), это — запасной
# список для файлов, где флагов нет.
_CORE_SERVICES = {
    'DataModel', 'Workspace', 'Lighting', 'ReplicatedStorage', 'ReplicatedFirst',
    'ServerScriptService', 'ServerStorage', 'StarterGui', 'StarterPack',
    'StarterPlayer', 'SoundService', 'Players', 'Teams', 'Chat', 'TextChatService',
    'MaterialService', 'TweenService', 'RunService', 'HttpService',
}


def collect_subtree(parsed, root_refs):
    """Выбранные корни -> (roots, refs). roots — без дублей и без потомков других
    выбранных (иначе объект попал бы в файл дважды); refs — все инстансы
    поддеревьев в порядке обхода в глубину (порядок детей как в сцене).
    ValueError, если выбран сервис или несуществующий объект."""
    r2c = parsed['referent_to_class']
    pmap = parsed['parent_map']
    services = parsed.get('service_refs') or ()

    wanted = []
    for r in root_refs:
        r = int(r)
        if r not in r2c:
            raise ValueError('Объект %d не найден' % r)
        if r in services or r2c[r] in _CORE_SERVICES:
            raise ValueError('«%s» — сервис, его нельзя экспортировать как модель. '
                             'Выберите объекты внутри него.' % parsed['props'].get(r, {}).get('Name', r2c[r]))
        if r not in wanted:
            wanted.append(r)
    if not wanted:
        raise ValueError('Ничего не выбрано')

    chosen = set(wanted)
    roots = []
    for r in wanted:
        par, guard, nested = pmap.get(r, -1), 0, False
        while par in r2c and guard < 100000:
            if par in chosen:
                nested = True
                break
            par, guard = pmap.get(par, -1), guard + 1
        if not nested:
            roots.append(r)

    children_of = {}
    for child, parent in pmap.items():          # порядок dict = порядок детей (PRNT)
        if child in r2c:
            children_of.setdefault(parent, []).append(child)

    refs, seen = [], set()
    stack = list(reversed(roots))
    while stack:
        r = stack.pop()
        if r in seen:
            continue
        seen.add(r)
        refs.append(r)
        stack.extend(reversed(children_of.get(r, [])))
    return roots, refs


def export_rbxm(parsed, root_refs):
    """Выбранные объекты со всеми потомками -> байты .rbxm.
    Возвращает (bytes, count, warnings)."""
    roots, refs = collect_subtree(parsed, root_refs)
    data, warnings = build_rbx_binary(
        parsed['referent_to_class'], parsed['parent_map'], parsed['props'], refs=refs,
        prop_types=parsed.get('prop_types'), shared_strings=parsed.get('shared_strings'),
        renumber=True,
    )
    # Свойства, которые парсер не умеет читать, при открытии файла были
    # потеряны — честно говорим об этом, а не молчим.
    classes = {parsed['referent_to_class'][r] for r in refs}
    lost = sorted({'%s.%s' % (c, n) for (c, n, _t) in parsed.get('skipped_props', []) if c in classes})
    if lost:
        warnings.append('не удалось прочитать при открытии файла и потому не попало в rbxm: ' + ', '.join(lost[:8])
                        + (' …' if len(lost) > 8 else ''))
    return data, len(refs), warnings


def import_rbxm(parsed, path, parent=None):
    """Читает .rbxm и добавляет его объекты в parsed под родителя parent.
    Возвращает (новые_корни, количество_объектов, warnings)."""
    with open(path, 'rb') as f:
        head = f.read(16)
    if not head.startswith(b'<roblox!'):
        if head.lstrip().startswith(b'<roblox') or head.lstrip().startswith(b'<?xml'):
            raise ValueError('XML-модели (.rbxmx) не поддерживаются — сохраните как бинарный .rbxm')
        raise ValueError('Это не файл Roblox (.rbxm)')
    other = parse_rbxl(path)
    if other.get('service_refs'):
        raise ValueError('В файле есть сервисы — это сцена (.rbxl), а не модель. Откройте её через Open.')
    if not other['referent_to_class']:
        raise ValueError('В файле нет объектов')

    r2c, pmap, props = parsed['referent_to_class'], parsed['parent_map'], parsed['props']
    if parent is None or parent == -1:
        parent = next((r for r, c in r2c.items() if c == 'Workspace'), -1)
    elif parent not in r2c:
        raise ValueError('Родитель %s не найден' % parent)

    base = max(r2c.keys(), default=-1) + 1
    old_refs = sorted(other['referent_to_class'])
    mapping = {old: base + i for i, old in enumerate(old_refs)}

    parsed_types = parsed.setdefault('prop_types', {})
    for k, v in other['prop_types'].items():
        parsed_types.setdefault(k, v)
    parsed.setdefault('skipped_props', []).extend(other.get('skipped_props', []))
    sstr = parsed.setdefault('shared_strings', [])
    sstr_offset = len(sstr)
    sstr.extend(other.get('shared_strings', []))

    import copy
    for old in old_refs:
        new = mapping[old]
        cls = other['referent_to_class'][old]
        r2c[new] = cls
        pr = copy.deepcopy(other['props'].get(old, {}))
        for name in list(pr):
            tid = other['prop_types'].get((cls, name))
            if tid == 0x13:            # ссылка на другой инстанс модели
                pr[name] = mapping.get(pr[name], -1)
            elif tid == 0x1c and pr[name] is not None:   # индекс в SSTR
                pr[name] = pr[name] + sstr_offset
        props[new] = pr

    roots = []
    # порядок детей = порядок записей PRNT исходного файла
    for old in [r for r in other['parent_map'] if r in mapping] + \
               [r for r in old_refs if r not in other['parent_map']]:
        par = other['parent_map'].get(old, -1)
        if par in mapping:
            pmap[mapping[old]] = mapping[par]
        else:
            pmap[mapping[old]] = parent
            roots.append(mapping[old])

    parsed['_modified'] = True
    warnings = []
    if other.get('skipped_props'):
        lost = sorted({'%s.%s' % (c, n) for (c, n, _t) in other['skipped_props']})
        warnings.append('не удалось прочитать свойства: ' + ', '.join(lost[:8]) + (' …' if len(lost) > 8 else ''))
    return roots, len(old_refs), warnings


# ====================== Parse / Save ======================

def parse_rbxl(path):
    """Парсит .rbxl файл и возвращает структуру данных"""
    chunks = read_chunks(path)
    class_id_to_referents = {}
    class_id_to_name = {}
    referent_to_class = {}
    service_refs = set()   # инстансы-сервисы (Workspace и т.п.) — нужны при записи
    shared_strings = []    # SSTR: значения свойств SharedString — индексы сюда
    
    for chunk in chunks:
        if chunk['name'] == b'INST':
            class_id, class_name, obj_fmt, referents = parse_inst(chunk['payload'])
            class_id_to_referents[class_id] = referents
            class_id_to_name[class_id] = class_name
            for r in referents:
                referent_to_class[r] = class_name
            if obj_fmt == 1:
                flags = parse_inst_service_flags(chunk['payload'], len(referents))
                service_refs.update(r for r, f in zip(referents, flags) if f)
        elif chunk['name'] == b'SSTR':
            try:
                shared_strings = parse_sstr(chunk['payload'])
            except Exception:
                shared_strings = []

    parent_map = {}
    for chunk in chunks:
        if chunk['name'] == b'PRNT':
            for child, parent in parse_prnt(chunk['payload']):
                parent_map[child] = parent

    props = {}
    skipped = 0
    # (класс, свойство) -> type_id из файла. Нужен при записи: тип нельзя
    # надёжно угадать по значению (enum и referent выглядят как обычный int).
    prop_types = {}
    skipped_props = []   # (класс, свойство, type_id), которые не удалось разобрать
    for chunk in chunks:
        if chunk['name'] == b'PROP':
            class_name = prop_name = type_id = None
            try:
                class_id, prop_name, type_id, rest = parse_prop_header(chunk['payload'])
                class_name = class_id_to_name.get(class_id)
                referents = class_id_to_referents.get(class_id, [])
                count = len(referents)
                decoder = TYPE_DECODERS.get(type_id)
                if decoder is None:
                    skipped += 1
                    skipped_props.append((class_name, prop_name, type_id))
                    continue
                values = decoder(rest, count)
                prop_types[(class_name, prop_name)] = type_id
                for r, v in zip(referents, values):
                    props.setdefault(r, {})[prop_name] = v
            except Exception:
                skipped += 1
                if prop_name is not None:
                    skipped_props.append((class_name, prop_name, type_id))
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
                    
                    # Матрица собрана как R = Rx(rx) * Ry(ry) * Rz(rz)
                    # (см. app.py: rot_matrix), поэтому раскладываем в тех же осях.
                    cy = math.sqrt(m00*m00 + m01*m01)
                    singular = cy < 1e-6
                    
                    if not singular:
                        rx = math.atan2(-m12, m22)
                        ry = math.atan2(m02, cy)
                        rz = math.atan2(-m01, m00)
                    else:
                        # Gimbal lock: ry = ±90°, ось X и Z сливаются, берём rz = 0
                        ry = math.pi / 2 if m02 > 0 else -math.pi / 2
                        rx = math.atan2(m10, m11) if m02 > 0 else -math.atan2(m10, m11)
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
        'skipped_props': skipped_props,
        'prop_types': prop_types,
        'shared_strings': shared_strings,
        'service_refs': service_refs,
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
    
    r2c = parsed['referent_to_class']
    pmap = parsed['parent_map']
    # Порядок детей у Roblox = порядок записей в PRNT, а parent_map (dict)
    # его сохраняет: пишем в этом порядке, новые инстансы — в конец.
    refs = [r for r in pmap if r in r2c] + [r for r in sorted(r2c) if r not in pmap]

    data, warnings = build_rbx_binary(
        r2c, pmap, parsed['props'], refs=refs,
        prop_types=parsed.get('prop_types'),
        shared_strings=parsed.get('shared_strings'),
        service_refs=parsed.get('service_refs'), renumber=False,
    )
    for w in warnings:
        print('save_rbxl:', w)

    with open(path, 'wb') as f:
        f.write(data)

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