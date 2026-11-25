"""Compare two raw (non-sparse) super/partition images block by block, with hashing."""
import sys, hashlib, json, os

BLK = 1 << 20


def digest_blocks(path, blk=BLK, skip_zeros=False):
    """Yield (block_index, sha256 or None for all-zero)."""
    with open(path, 'rb') as f:
        i = 0
        while True:
            b = f.read(blk)
            if not b:
                return
            if skip_zeros and not any(b):
                yield (i, None)
            else:
                yield (i, hashlib.sha256(b).hexdigest()[:16])
            i += 1


def diff(p1, p2, blk=BLK, out='diff.json'):
    a = digest_blocks(p1, blk)
    b = digest_blocks(p2, blk)
    diffs = []
    za = zb = 0
    total = 0
    for (i1, h1), (i2, h2) in zip(a, b):
        total += 1
        if h1 is None:
            za += 1
        if h2 is None:
            zb += 1
        if h1 != h2:
            diffs.append(i1)
    print(json.dumps({
        'blocks': total, 'block_size': blk,
        'nonzero_dump': za, 'nonzero_mine': zb,
        'diff_blocks': len(diffs),
        'diff_mb': len(diffs) * blk / 1048576,
        'ranges': ranges(diffs),
    }, indent=1))
    with open(out, 'w') as f:
        json.dump(diffs, f)


def ranges(xs):
    out = []
    if not xs:
        return out
    s = p = xs[0]
    for x in xs[1:]:
        if x == p + 1:
            p = x
            continue
        out.append([s, p, p - s + 1])
        s = p = x
    out.append([s, p, p - s + 1])
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'diff':
        diff(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'ranges':
        diff(sys.argv[2], sys.argv[3], out=sys.argv[4] if len(sys.argv) > 4 else 'diff.json')