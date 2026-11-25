"""Diff two ext4 tree TSVs produced by ext4_tree.py (paths may contain tabs)."""
import sys


def load(p):
    rows = {}
    with open(p, encoding='utf-8') as f:
        next(f)
        for line in f:
            parts = line.rstrip('\n').rsplit('\t', 5)
            if len(parts) != 6:
                continue
            rows[parts[0]] = {'t': parts[1], 'size': int(parts[3]),
                              'mt': parts[4], 'sha': parts[5]}
    return rows


def main(pa, pb, label_a='new', label_b='mine'):
    a = load(pa)
    b = load(pb)
    print('=== %s vs %s' % (label_a, label_b))
    print('entries: %s=%d %s=%d' % (label_a, len(a), label_b, len(b)))
    oa = sorted(set(a) - set(b))
    ob = sorted(set(b) - set(a))
    common = sorted(set(a) & set(b))
    print('only in %s (%d):' % (label_a, len(oa)))
    for x in oa:
        print('  + %s  (%d)' % (x, a[x]['size']))
    print('only in %s (%d):' % (label_b, len(ob)))
    for x in ob:
        print('  - %s  (%d)' % (x, b[x]['size']))
    sd = [(x, b[x]['size'], a[x]['size']) for x in common if a[x]['size'] != b[x]['size']]
    print('size changed (%d):' % len(sd))
    for x, y, z in sd:
        print('  ~ %s  %d -> %d (%+d)' % (x, y, z, z - y))
    sh = [(x, b[x]['sha'][:12], a[x]['sha'][:12]) for x in common
          if a[x]['sha'] not in ('-',) and b[x]['sha'] not in ('-',) and a[x]['sha'] != b[x]['sha']]
    print('content changed (%d):' % len(sh))
    for x, y, z in sh:
        print('  ~ %s  %s -> %s' % (x, y, z))
    same = len([x for x in common if a[x]['sha'] == b[x]['sha'] and a[x]['sha'] != '-'])
    print('content identical: %d' % same)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])