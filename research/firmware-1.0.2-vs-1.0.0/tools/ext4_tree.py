"""Dump an ext4 image tree as TSV (path, type, mode, size, mtime, sha256)."""
import sys, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_pylibs'))
from ext4 import Volume
from ext4.directory import DirectoryEntry2  # noqa: F401


def mode_type(mode):
    t = mode & 0o170000
    return {0o040000: 'dir', 0o100000: 'reg', 0o120000: 'lnk', 0o020000: 'chr',
            0o060000: 'blk', 0o010000: 'fifo', 0o140000: 'sock'}.get(t, oct(t))


def dump(img, out):
    v = Volume(open(img, 'rb'))
    rows = []
    seen = set()

    def walk(inode, prefix, depth=0):
        if depth > 40:
            return
        try:
            gen = inode.opendir()
        except Exception:
            return
        for de, ft in gen:
            name = de.name.decode('utf-8', 'replace')
            if name in ('.', '..'):
                continue
            path = prefix + '/' + name if prefix else name
            try:
                ino = v.inodes[de.inode]
            except Exception as e:
                rows.append((path, 'ERR', '', 0, 0, 'read_err'))
                continue
            mt = mode_type(ino.i_mode)
            size = ino.i_size
            sha = '-'
            if mt == 'reg':
                key = (de.inode, size)
                if key in seen:
                    sha = 'hardlink:' + str(de.inode)
                else:
                    seen.add(key)
                    try:
                        h = hashlib.sha256()
                        f = ino.open()
                        while True:
                            b = f.read(1 << 20)
                            if not b:
                                break
                            h.update(b)
                        sha = h.hexdigest()
                    except Exception as e:
                        sha = 'ERR:' + type(e).__name__
            rows.append((path, mt, oct(ino.i_mode), size, int(ino.i_mtime), sha))
            if mt == 'dir':
                walk(ino, path, depth + 1)

    walk(v.root, '')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('path\ttype\tmode\tsize\tmtime\tsha\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print(img, 'entries', len(rows))


if __name__ == '__main__':
    for img, out in zip(sys.argv[1::2], sys.argv[2::2]):
        dump(img, out)