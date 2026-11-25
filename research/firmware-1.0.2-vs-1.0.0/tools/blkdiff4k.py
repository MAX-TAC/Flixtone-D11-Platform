"""Find differing 4 KiB blocks between two files and print ranges + first/last offsets."""
import sys, hashlib, os

BLK = 4096


def diff(a, b):
    sa, sb = os.path.getsize(a), os.path.getsize(b)
    print('%s (%d) vs %s (%d)' % (os.path.basename(a), sa, os.path.basename(b), sb))
    n = min(sa, sb) // BLK
    diffs = []
    with open(a, 'rb') as fa, open(b, 'rb') as fb:
        for i in range(n):
            x = fa.read(BLK)
            y = fb.read(BLK)
            if x != y:
                diffs.append(i)
    if diffs:
        print('  diff blocks: %d of %d (%.2f%%), first offset %d, last offset %d' % (
            len(diffs), n, 100.0 * len(diffs) / n, diffs[0] * BLK, diffs[-1] * BLK))
        rng = []
        s = p = diffs[0]
        for d in diffs[1:]:
            if d == p + 1:
                p = d
                continue
            rng.append((s, p))
            s = p = d
        rng.append((s, p))
        print('  ranges (blocks):', ', '.join('%d-%d' % r for r in rng[:20]),
              ('... total %d ranges' % len(rng)) if len(rng) > 20 else '')
    else:
        print('  identical in first %d blocks' % n)


if __name__ == '__main__':
    diff(sys.argv[1], sys.argv[2])