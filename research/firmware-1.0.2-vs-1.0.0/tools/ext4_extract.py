"""Extract files from an ext4 image matching a regex on their path (bytes-safe)."""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_pylibs'))
from ext4 import Volume


def walk(v, inode, prefix=b'', depth=0):
    if depth > 40:
        return
    try:
        gen = inode.opendir()
    except Exception:
        return
    for de, ft in gen:
        nm = de.name
        if nm in (b'.', b'..'):
            continue
        path = prefix + b'/' + nm if prefix else nm
        try:
            ino = v.inodes[de.inode]
        except Exception:
            continue
        if (ino.i_mode & 0o170000) == 0o040000:
            yield from walk(v, ino, path, depth + 1)
        else:
            yield path, ino


def main(img, pattern, outdir):
    v = Volume(open(img, 'rb'))
    pat = re.compile(pattern.encode())
    os.makedirs(outdir, exist_ok=True)
    found = 0
    for path, ino in walk(v, v.root):
        if pat.search(path):
            found += 1
            name = re.sub(r'[^A-Za-z0-9._-]+', '_', path.decode('utf-8', 'replace'))
            with open(os.path.join(outdir, name), 'wb') as f:
                fh = ino.open()
                while True:
                    b = fh.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            print('extracted', path.decode('utf-8', 'replace'), ino.i_size)
    print('matched', found)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])