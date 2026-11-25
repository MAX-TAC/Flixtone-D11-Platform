"""Decompress a gzip ramdisk (cpio newc) and dump its entries: path, size, sha256."""
import sys, gzip, io, hashlib


def parse_cpio(data, label, out):
    pos = 0
    rows = []
    while pos + 110 <= len(data):
        magic = data[pos:pos + 6]
        if magic != b'070701':
            break
        def h(o, n=8):
            return int(data[pos + o:pos + o + n], 16)
        ino, mode, uid, gid, nlink, mtime, size = h(6), h(14), h(22), h(30), h(38), h(46), h(54)
        devmaj, devmin, rdevmaj, rdevmin = h(62), h(70), h(78), h(86)
        namesize = h(94)
        name = data[pos + 110:pos + 110 + namesize - 1].decode('utf-8', 'replace')
        pos += 110 + namesize
        pos = (pos + 3) & ~3
        body = data[pos:pos + size]
        pos += size
        pos = (pos + 3) & ~3
        if name == 'TRAILER!!!':
            break
        sha = hashlib.sha256(body).hexdigest() if size else '-'
        rows.append((name, oct(mode), size, sha))
    with open(out, 'w', encoding='utf-8') as f:
        f.write('path\tmode\tsize\tsha\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    print(label, 'entries', len(rows))


if __name__ == '__main__':
    for img, out in zip(sys.argv[1::2], sys.argv[2::2]):
        # ramdisk offset differs per image; caller passes "path:offset" or we locate gzip
        if ':' in img:
            path, off = img.rsplit(':', 1)
            off = int(off)
        else:
            path, off = img, None
        if off is None:
            with open(path, 'rb') as f:
                data = f.read()
            i = data.find(b'\x1f\x8b\x08')
            off = i
        with open(path, 'rb') as f:
            f.seek(off)
            raw = f.read()
        import zlib
        d = zlib.decompressobj(31).decompress(raw)
        parse_cpio(d, path, out)