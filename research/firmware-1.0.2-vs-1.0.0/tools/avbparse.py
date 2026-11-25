"""Correct AVB vbmeta and DTBO header parsers."""
import struct, sys, os, hashlib


def vbmeta(path):
    with open(path, 'rb') as f:
        raw = f.read(256)
    assert raw[:4] == b'AVB0', raw[:4]
    maj, mn = struct.unpack('<II', raw[4:12])
    auth_size, aux_size = struct.unpack('<QQ', raw[12:28])
    algo = struct.unpack('<I', raw[28:32])[0]
    hash_off, hash_size = struct.unpack('<QQ', raw[32:48])
    sig_off, sig_size = struct.unpack('<QQ', raw[48:64])
    pk_off, pk_size = struct.unpack('<QQ', raw[64:80])
    pkm_off, pkm_size = struct.unpack('<QQ', raw[80:96])
    desc_off, desc_size = struct.unpack('<QQ', raw[96:112])
    rollback_index = struct.unpack('<Q', raw[112:120])[0]
    flags = struct.unpack('<I', raw[120:124])[0]
    rollback_loc = struct.unpack('<I', raw[124:128])[0]
    release = raw[128:176].split(b'\0')[0].decode('utf-8', 'replace')
    print('%s: AVB %d.%d algo=%d auth=%d aux=%d hash=%d sig=%d pubkey=%d desc=%d rollback=%d loc=%d flags=%d release=%r' % (
        path, maj, mn, algo, auth_size, aux_size, hash_size, sig_size, pk_size,
        desc_size, rollback_index, rollback_loc, flags, release))
    with open(path, 'rb') as f:
        f.seek(256 + auth_size + desc_off)
        d = f.read(desc_size)
    pos = 0
    while pos + 16 <= len(d):
        tag, n = struct.unpack('<QQ', d[pos:pos + 16])
        if tag == 0:
            break
        size = n >> 32
        body = d[pos:pos + size]
        if tag == 3:
            img = body[16:48].split(b'\0')[0].decode('utf-8', 'replace')
            isz = struct.unpack('<Q', body[8:16])[0]
            digest = body[60:60 + 32].hex()[:32] if len(body) >= 92 else '?'
            print('  HASH     %-18s size=%-10d digest=%s' % (img, isz, digest))
        elif tag == 2:
            img = body[16:48].split(b'\0')[0].decode('utf-8', 'replace')
            isz = struct.unpack('<Q', body[8:16])[0]
            print('  HASHTREE %-18s size=%-10d' % (img, isz))
        elif tag == 1:
            # chain partition: rollback_index u32, flags u32, pubkey...
            pass
        pos += size


def dtbo(path):
    with open(path, 'rb') as f:
        h = f.read(32)
    magic, total, hdr, entry_size, count, entries_off, page, version = struct.unpack('<8I', h)
    print('%s: magic=%#x total=%d hdr=%d entry_size=%d count=%d offset=%d page=%d ver=%d' % (
        path, magic, total, hdr, entry_size, count, entries_off, page, version))
    with open(path, 'rb') as f:
        f.seek(entries_off)
        ents = f.read(entry_size * count)
    for i in range(min(count, 6)):
        e = ents[i * entry_size:(i + 1) * entry_size]
        dts_size, dts_off = struct.unpack('<II', e[:8])
        idv, rev, custom = struct.unpack('<III', e[8:20])
        print('  entry %d: dtb_size=%d off=%d id=%d rev=%d custom=%d' % (i, dts_size, dts_off, idv, rev, custom))
    # hash of first dtb
    if count:
        dts_size, dts_off = struct.unpack('<II', ents[:8])
        with open(path, 'rb') as f:
            f.seek(dts_off)
            b = f.read(dts_size)
        print('  dtb0 sha256=%s' % hashlib.sha256(b).hexdigest())


if __name__ == '__main__':
    mode = sys.argv[1]
    for p in sys.argv[2:]:
        (vbmeta if mode == 'vbmeta' else dtbo)(p)