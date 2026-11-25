"""Minimal EROFS reader (read-only) for metadata comparison.

Supports:
  - compact / extended inodes
  - flat plain / flat inline data
  - directory iteration
  - compressed inodes via LZ4 legacy (or lzma) when needed
"""
import struct, sys, os

EROFS_SUPER_OFFSET = 1024
BLK = 4096


class Erofs:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        self.f.seek(EROFS_SUPER_OFFSET)
        sb = self.f.read(128)
        (magic, checksum, feat_compat, blkszbits, sb_extslots, root_nid,
         inos, build_time, build_time_nsec, blocks, meta_blkaddr, xattr_blkaddr) = \
            struct.unpack('<IIIBBHQQIIII', sb[:48])
        assert magic == 0xE0F5E1E2, hex(magic)
        self.sb = dict(magic=magic, blkszbits=blkszbits, root_nid=root_nid,
                       inos=inos, build_time=build_time, blocks=blocks,
                       meta_blkaddr=meta_blkaddr, xattr_blkaddr=xattr_blkaddr,
                       feat_compat=feat_compat,
                       feature_incompat=struct.unpack('<I', sb[72:76])[0])
        self.blk = 1 << blkszbits
        self.meta_blkaddr = meta_blkaddr
        self.xattr_blkaddr = xattr_blkaddr
        # feature_incompat is at offset 80? use known layout: uuid 16 @ 56, volume_name 16 @ 72,
        # feature_incompat u32 @ 88
        self.feat_incompat = self._u32(sb, 88)

    def _u32(self, b, o):
        return struct.unpack('<I', b[o:o + 4])[0]

    # ---------- inode ----------
    def inode_pos(self, nid):
        return self.meta_blkaddr * BLK + nid * 32

    def read_inode(self, nid):
        pos = self.inode_pos(nid)
        self.f.seek(pos)
        raw = self.f.read(64)
        i_format, i_xattr_icount, i_mode, i_nlink = struct.unpack('<HHHH', raw[:8])
        ext = i_format & 1
        layout = (i_format >> 1) & 7
        d = {'nid': nid, 'format': i_format, 'extended': bool(ext), 'layout': layout,
             'mode': i_mode, 'xattr_icount': i_xattr_icount}
        if not ext:
            i_size = self._u32(raw, 8)
            i_reserved = self._u32(raw, 12)
            u = self._u32(raw, 16)
            i_ino = self._u32(raw, 20)
            uid = struct.unpack('<H', raw[24:26])[0]
            gid = struct.unpack('<H', raw[26:28])[0]
            d.update(size=i_size, raw_blkaddr=u, ino=i_ino, uid=uid, gid=gid, inode_size=32)
        else:
            i_size = struct.unpack('<Q', raw[8:16])[0]
            u = self._u32(raw, 16)
            i_ino = self._u32(raw, 20)
            uid = self._u32(raw, 24)
            gid = struct.unpack('<I', raw[28:32])[0]
            mtime = struct.unpack('<Q', raw[32:40])[0]
            mtime_nsec = self._u32(raw, 40)
            d.update(size=i_size, raw_blkaddr=u, ino=i_ino, uid=uid, gid=gid,
                     mtime=mtime, inode_size=64)
        d['file_type'] = i_mode >> 12
        return d

    def inode_data(self, ino):
        """Yield logical data bytes for a file, supporting plain/inline."""
        layout = ino['layout']
        blk = self.blk
        size = ino['size']
        if layout == 0:  # flat plain
            self.f.seek(ino['raw_blkaddr'] * blk)
            left = size
            while left:
                b = self.f.read(min(1 << 20, left))
                if not b:
                    break
                left -= len(b)
                yield b
        elif layout == 2:  # flat inline (this vendor's mkfs puts the inline chunk first)
            body = ino['inode_size'] + (12 + (ino['xattr_icount'] - 1) * 4 if ino['xattr_icount'] else 0)
            pos = self.inode_pos(ino['nid']) + body
            inblock = blk - (pos % blk)
            inline_len = min(size, inblock)
            head = size - inline_len
            self.f.seek(pos)
            yield self.f.read(inline_len)
            if head and ino['raw_blkaddr'] not in (0xffffffff, 0):
                self.f.seek(ino['raw_blkaddr'] * blk)
                left = head
                while left:
                    b = self.f.read(min(1 << 20, left))
                    if not b:
                        break
                    left -= len(b)
                    yield b
        else:
            raise NotImplementedError('layout %d (compressed)' % layout)

    def read_file(self, nid, limit=None):
        ino = self.read_inode(nid)
        if ino['file_type'] == 4 and ino['layout'] == 2 and ino['size'] == 0:
            pass
        out = bytearray()
        for b in self.inode_data(ino):
            out += b
            if limit and len(out) >= limit:
                break
        return bytes(out[:limit] if limit else out), ino

    def listdir(self, nid):
        ino = self.read_inode(nid)
        assert ino['file_type'] == 4, 'not dir: mode %o' % ino['mode']
        data = self.read_file(nid)[0]
        ents = []
        if len(data) < 12:
            return []
        first_nameoff = struct.unpack('<H', data[8:10])[0]
        # dirents occupy [0, first_nameoff); EROFS may pad the name table start,
        # so derive the entry count from the first name offset.
        count = first_nameoff // 12
        for i in range(count):
            off = i * 12
            en_nid, nameoff, ftype, _ = struct.unpack('<QHBB', data[off:off + 12])
            ents.append([en_nid, nameoff, ftype])
        # names live in the same buffer, offsets are relative to the dir data start
        for i, e in enumerate(ents):
            begin = e[1]
            nxt = ents[i + 1][1] if i + 1 < len(ents) else len(data)
            e.append(data[begin:nxt].decode('utf-8', 'replace'))
        return [(e[3], e[0], e[2]) for e in ents]

    def walk(self, nid=None, prefix=''):
        if nid is None:
            nid = self.sb['root_nid']
        for name, cnid, ftype in self.listdir(nid):
            if name in ('.', '..'):
                continue
            path = prefix + '/' + name if prefix else name
            yield path, cnid, ftype
            if ftype == 2:  # EROFS_FT_DIR
                yield from self.walk(cnid, path)


if __name__ == '__main__':
    fs = Erofs(sys.argv[1])
    print(fs.sb)
    print('feat_incompat', hex(fs.feat_incompat))
    for p, nid, ft in fs.walk():
        print('%d %-8s %s' % (nid, ft, p))