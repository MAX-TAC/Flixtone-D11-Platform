"""Extract logical partitions from an Android super image using the LP metadata
layout found on this vendor build, and compute per-partition SHA-256.

Descriptor block location in header (empirically): offset 80, 4 descriptors of
12 bytes: partitions, extents, groups, block_devices.
"""
import struct, sys, os, hashlib, json

RES = 4 * 1024


def parse_tables(path):
    with open(path, 'rb') as f:
        f.seek(0x3000)
        h = f.read(256)
        if h[:4] != b'0PLA':
            raise SystemExit('bad magic in ' + path)
        ts = struct.unpack('<I', h[44:48])[0]
        t = f.read(ts)
    pd, ed, gd, bd = [struct.unpack('<III', h[80 + i * 12:92 + i * 12]) for i in range(4)]
    groups = []
    for i in range(gd[1]):
        g = t[gd[0] + i * gd[2]: gd[0] + (i + 1) * gd[2]]
        groups.append(g[:36].split(b'\0')[0].decode())
    extents = []
    for i in range(ed[1]):
        e = t[ed[0] + i * ed[2]: ed[0] + (i + 1) * ed[2]]
        ns, tt, td, tsrc = struct.unpack('<QIQI', e[:24])
        extents.append({'sectors': ns, 'type': tt, 'data': td, 'src': tsrc})
    parts = []
    for i in range(pd[1]):
        e = t[pd[0] + i * pd[2]: pd[0] + (i + 1) * pd[2]]
        name = e[:36].split(b'\0')[0].decode()
        attrs, first, num, grp = struct.unpack('<IIII', e[36:52])
        ps = extents[first:first + num] if num else []
        parts.append({'name': name, 'attrs': attrs, 'group': groups[grp] if grp < len(groups) else grp,
                      'extents': ps,
                      'size': sum(x['sectors'] for x in ps) * 512})
    bdev = None
    if bd[1]:
        b = t[bd[0]: bd[0] + bd[2]]
        first_ls, align, align_off, size = struct.unpack('<QIIQ', b[:24])
        bdev = {'name': b[24:60].split(b'\0')[0].decode(), 'size': size,
                'first_logical_sector': first_ls, 'alignment': align}
    return {'parts': parts, 'blockdev': bdev}


def extract(path, outdir):
    meta = parse_tables(path)
    os.makedirs(outdir, exist_ok=True)
    with open(path, 'rb') as src:
        for p in meta['parts']:
            out = os.path.join(outdir, p['name'] + '.img')
            h = hashlib.sha256()
            with open(out, 'wb') as dst:
                for e in p['extents']:
                    src.seek(e['data'] * 512)
                    left = e['sectors'] * 512
                    while left:
                        b = src.read(min(8 << 20, left))
                        if not b:
                            break
                        dst.write(b)
                        h.update(b)
                        left -= len(b)
            p['file'] = out
            p['sha256'] = h.hexdigest()
            print('%-14s %10d  %s' % (p['name'], p['size'], h.hexdigest()))
    return meta


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'meta':
        for p in sys.argv[2:]:
            m = parse_tables(p)
            print('=', p, 'blockdev', m['blockdev'])
            for x in m['parts']:
                print('  %-14s group=%-12s size=%-10d extents=%s' % (
                    x['name'], x['group'], x['size'],
                    [(e['sectors'], e['data'] * 512) for e in x['extents']]))
    elif cmd == 'extract':
        m = extract(sys.argv[2], sys.argv[3])
        json.dump(m, open(os.path.join(sys.argv[3], 'meta.json'), 'w'), indent=1)