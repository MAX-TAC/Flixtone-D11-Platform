"""Diff two EROFS tree dumps produced by tree_dump.py."""
import sys, collections


def load(p):
    rows = {}
    with open(p, encoding='utf-8') as f:
        next(f)
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6:
                continue
            path = parts[0]
            rows[path] = {'type': parts[1], 'mode': parts[2], 'size': int(parts[3]),
                          'layout': int(parts[4]), 'sha': parts[5],
                          'mtime': parts[6] if len(parts) > 6 else ''}
    return rows


def diff(a_path, b_path, label_a='new', label_b='mine', show=True):
    a = load(a_path)  # new
    b = load(b_path)  # mine
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    common = sorted(set(a) & set(b))
    size_changed = [(p, b[p]['size'], a[p]['size']) for p in common
                    if a[p]['size'] != b[p]['size']]
    sha_changed = [(p, b[p]['sha'][:12], a[p]['sha'][:12]) for p in common
                   if a[p]['sha'] != '-' and b[p]['sha'] != '-' and a[p]['sha'] != b[p]['sha']]
    type_changed = [(p, b[p]['type'], a[p]['type']) for p in common if a[p]['type'] != b[p]['type']]
    print('===', label_a, 'vs', label_b)
    print('total: %s=%d  %s=%d  common=%d' % (label_a, len(a), label_b, len(b), len(common)))
    print('only in %s (%d):' % (label_a, len(only_a)))
    for p in only_a:
        print('  + %-70s %-4s %d' % (p, a[p]['type'], a[p]['size']))
    print('only in %s (%d):' % (label_b, len(only_b)))
    for p in only_b:
        print('  - %-70s %-4s %d' % (p, b[p]['type'], b[p]['size']))
    print('type changed (%d):' % len(type_changed))
    for p, x, y in type_changed:
        print('  ~ %-70s %s -> %s' % (p, x, y))
    print('size changed (%d):' % len(size_changed))
    for p, x, y in size_changed:
        delta = y - x
        print('  ~ %-70s %10d -> %10d (%+d)' % (p, x, y, delta))
    print('content(hash) changed: %d (of %d comparable)' % (len(sha_changed),
          len([p for p in common if a[p]['sha'] != '-'])))
    for p, x, y in sha_changed:
        print('  ~ %-70s %s -> %s' % (p, x, y))
    return {'only_a': only_a, 'only_b': only_b, 'size': size_changed, 'sha': sha_changed}


if __name__ == '__main__':
    diff(sys.argv[1], sys.argv[2])