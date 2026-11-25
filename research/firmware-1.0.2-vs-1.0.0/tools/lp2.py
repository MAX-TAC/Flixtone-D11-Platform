import struct, sys, json


def parse(p):
    f = open(p, 'rb')
    f.seek(0x3000)
    h = f.read(256)
    ts = struct.unpack('<I', h[44:48])[0]
    descs = [struct.unpack('<III', h[56 + i * 12:68 + i * 12]) for i in range(6)]
    groups_d, pflags_d, bsz_d, skip_d, ext_d, part_d = descs
    tbl = f.read(ts)

    def unfrag(off, n, es):
        return len(tbl[off:off + n * es].split(b'\0'))  # not used

    # extents: u64 sectors, u32 type, u64 data, u32 source = 24 bytes
    eo, en, ee = ext_d
    extents = []
    for i in range(en):
        e = tbl[eo + i * ee: eo + (i + 1) * ee]
        ns, tt, td, tsrc = struct.unpack('<QIQI', e[:24])
        extents.append({'num_sectors': ns, 'target_type': tt, 'target_data': td, 'target_source': tsrc})

    go, gn, ge = groups_d
    groups = []
    for i in range(gn):
        g = tbl[go + i * ge: go + (i + 1) * ge]
        name = g[:36].split(b'\0')[0].decode()
        flags = struct.unpack('<I', g[36:40])[0]
        mx = struct.unpack('<Q', g[40:48])[0]
        groups.append({'name': name, 'flags': flags, 'max_size': mx})

    po, pn, pe = part_d
    partitions = []
    for i in range(pn):
        e = tbl[po + i * pe: po + (i + 1) * pe]
        name = e[:36].split(b'\0')[0].decode()
        attrs, first, num, grp = struct.unpack('<IIII', e[36:52])
        ps = extents[first:first + num]
        total = sum(x['num_sectors'] for x in ps) * 512
        partitions.append({'name': name, 'attributes': attrs, 'group': groups[grp]['name'] if grp < len(groups) else grp,
                           'size_mb': round(total / 1048576, 2),
                           'extents': [{'sectors': x['num_sectors'], 'type': x['target_type'],
                                        'off_mb': round(x['target_data'] * 512 / 1048576, 2), 'src': x['target_source']} for x in ps]})

    # block device sizes from block sizes table
    bo, bn, be = bsz_d
    bsizes = []
    for i in range(bn):
        e = tbl[bo + i * be: bo + (i + 1) * be]
        bsizes.append(struct.unpack('<Q', e[:8])[0])
    return {'tables_size': ts, 'groups': groups, 'partitions': partitions, 'blockdev_sizes': bsizes}


if __name__ == '__main__':
    a = parse(sys.argv[1])
    b = parse(sys.argv[2])
    print('=== DUMP ===', sys.argv[1])
    print('groups', [(g['name'], g['max_size'] // 1048576) for g in a['groups']], 'blkdevs', [x // 1048576 for x in a['blockdev_sizes']])
    for p in a['partitions']:
        print('  %-15s size=%-9s grp=%-8s attrs=%08x %s' % (p['name'], p['size_mb'], p['group'], p['attributes'], p['extents']))
    print()
    print('=== MINE ===', sys.argv[2])
    print('groups', [(g['name'], g['max_size'] // 1048576) for g in b['groups']], 'blkdevs', [x // 1048576 for x in b['blockdev_sizes']])
    for p in b['partitions']:
        print('  %-15s size=%-9s grp=%-8s attrs=%08x %s' % (p['name'], p['size_mb'], p['group'], p['attributes'], p['extents']))
    print()
    an = [p['name'] for p in a['partitions']]
    bn_ = [p['name'] for p in b['partitions']]
    print('only in dump:', [x for x in an if x not in bn_])
    print('only in mine:', [x for x in bn_ if x not in an])
    for p in a['partitions']:
        for q in b['partitions']:
            if p['name'] == q['name'] and (p['size_mb'] != q['size_mb'] or p['extents'] != q['extents']):
                print('DIFF', p['name'], 'dump', p['size_mb'], p['extents'], '| mine', q['size_mb'], q['extents'])
    json.dump({'dump': a, 'mine': b}, open('_cmp/lp_meta.json', 'w'), indent=1)