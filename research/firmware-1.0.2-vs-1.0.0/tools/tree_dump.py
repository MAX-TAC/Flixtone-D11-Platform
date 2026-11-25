"""Dump an EROFS tree as TSV: path, type, mode, size, layout, sha256 (for plain/inline data)."""
import sys, hashlib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from erofs import Erofs

FTS = {1: 'reg', 2: 'dir', 7: 'lnk', 3: 'chr', 4: 'blk', 5: 'fifo', 6: 'sock'}


def dump(img, out):
    fs = Erofs(img)
    seen = set()
    rows = []
    for path, nid, ft in fs.walk():
        if nid in seen:
            continue
        seen.add(nid)
        ino = fs.read_inode(nid)
        typ = FTS.get(ft, str(ft))
        sha = '-'
        if typ in ('reg', 'lnk') and ino['layout'] in (0, 2):
            h = hashlib.sha256()
            try:
                for b in fs.inode_data(ino):
                    h.update(b)
                sha = h.hexdigest()
            except Exception as e:
                sha = 'ERR:' + type(e).__name__
        rows.append((path, typ, oct(ino['mode']), ino['size'], ino['layout'], sha, ino.get('mtime', '')))
    with open(out, 'w', encoding='utf-8') as f:
        f.write('path\ttype\tmode\tsize\tlayout\tsha\tmtime\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print(img, 'entries', len(rows))


if __name__ == '__main__':
    for img, out in zip(sys.argv[1::2], sys.argv[2::2]):
        dump(img, out)