"""Quantify how much of two images is byte-identical despite offset shifts.

Hashes every 4 KiB block of both images and reports:
  - blocks unique to each image
  - shared blocks (identical content, possibly at a different offset)
"""
import sys, hashlib, os
from collections import Counter

BLK = 4096


def block_hashes(path):
    h = {}
    with open(path, 'rb') as f:
        i = 0
        while True:
            b = f.read(BLK)
            if not b:
                break
            if len(b) < BLK:
                b = b + b'\0' * (BLK - len(b))
            h[i] = hashlib.blake2b(b, digest_size=16).digest()
            i += 1
    return h


def main(p1, p2, name):
    a = block_hashes(p1)
    b = block_hashes(p2)
    sa = set(a.values())
    sb = set(b.values())
    shared = sa & sb
    only_a = sa - sb
    only_b = sb - sa
    print('%s\tblocks_a=%d\tblocks_b=%d\tshared=%d\t(%.1f%% of a, %.1f%% of b)\tonly_new=%d\tonly_old=%d' % (
        name, len(a), len(b), len(shared),
        100.0 * len(shared) / len(sa) if sa else 0,
        100.0 * len(shared) / len(sb) if sb else 0,
        len(only_a), len(only_b)))
    return {'name': name, 'a': len(a), 'b': len(b), 'shared': len(shared),
            'only_new': len(only_a), 'only_old': len(only_b)}


if __name__ == '__main__':
    if sys.argv[1] == 'super':
        pairs = [('system_a', 'system_a'), ('vendor_a', 'vendor_a'),
                 ('product_a', 'product_a'), ('system_ext_a', 'system_ext_a')]
        for p in pairs:
            main('_cmp/ext/dump/%s.img' % p[0], '_cmp/ext/mine/%s.img' % p[1], p[0])
    else:
        main(sys.argv[1], sys.argv[2], os.path.basename(sys.argv[1]))