"""Parse Android boot image, AVB vbmeta, and DTBO headers; print comparable facts."""
import struct, sys, hashlib, os


def sha(path, off=0, size=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        f.seek(off)
        left = size
        while True:
            n = 1 << 20 if left is None else min(1 << 20, left)
            if n <= 0:
                break
            b = f.read(n)
            if not b:
                break
            h.update(b)
            if left is not None:
                left -= len(b)
    return h.hexdigest()


def boot(path, label):
    with open(path, 'rb') as f:
        raw = f.read(4096)
    magic = raw[:8]
    if magic != b'ANDROID!':
        print(label, 'not an Android boot image:', magic)
        return
    (kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr,
     tags_addr, page_size, header_version, os_version) = struct.unpack('<10I', raw[8:48])
    name = raw[48:64].split(b'\0')[0].decode('utf-8', 'replace')
    cmdline = raw[64:576].split(b'\0')[0].decode('utf-8', 'replace')
    extra = raw[576:608]
    print('%s: header v%d  name=%r page=%d' % (label, header_version, name, page_size))
    print('  kernel size=%d addr=%#x sha256=%s' % (kernel_size, kernel_addr, sha(path, 4096, kernel_size)))
    kpages = (kernel_size + page_size - 1) // page_size
    roff = 4096 + kpages * page_size
    print('  ramdisk size=%d addr=%#x sha256=%s' % (ramdisk_size, ramdisk_addr, sha(path, roff, ramdisk_size)))
    print('  os_version=%#x cmdline=%r' % (os_version, cmdline))
    print('  extra=%s' % extra.hex())
    # vendor_boot v3/v4 have extra fields
    if header_version >= 3:
        hdr_size = struct.unpack('<I', raw[20:24])[0]
        print('  header_size field=%d' % hdr_size)


def vbmeta(path, label):
    with open(path, 'rb') as f:
        raw = f.read(4096)
    magic = raw[:4]
    if magic != b'AVB0':
        print(label, 'not vbmeta:', magic)
        return
    ver_maj, ver_min = struct.unpack('<II', raw[4:12])
    auth_size, aux_size, algo = struct.unpack('<QQI', raw[12:32])
    rollback = struct.unpack('<Q', raw[24:32])[0]
    flags = struct.unpack('<I', raw[120:124])[0]
    rollback_index = struct.unpack('<Q', raw[112:120])[0]
    rollback_index_location = struct.unpack('<I', raw[120:124])[0]
    release_string = raw[128:128 + 48].split(b'\0')[0].decode('utf-8', 'replace')
    print('%s: AVB v%d.%d algo=%d auth=%d aux=%d flags=%d rollback_index=%d loc=%d release=%r' % (
        label, ver_maj, ver_min, algo, auth_size, aux_size, rollback_index_location,
        rollback_index, rollback_index_location, release_string))
    print('  file sha256=%s size=%d' % (sha(path), os.path.getsize(path)))
    # descriptors
    desc_off = 256 + auth_size
    end = desc_off + aux_size
    pos = desc_off
    with open(path, 'rb') as f:
        f.seek(desc_off)
        buf = f.read(aux_size)
    while pos < end and pos + 8 <= len(buf) + desc_off:
        rel = pos - desc_off
        if rel + 8 > len(buf):
            break
        t, n = struct.unpack('<QQ', buf[rel:rel + 16]) if rel + 16 <= len(buf) else (0, 0)
        tag = n & 0xFFFFFFFF
        if tag == 0:
            break
        size = n >> 32
        d = buf[rel:rel + size]
        if tag == 2:  # hash tree
            print('  descriptor HASHTREE: image=%r size=%d flags=%d' % (
                d[16:16 + 32].split(b'\0')[0].decode('utf-8', 'replace'),
                struct.unpack('<Q', d[8:16])[0], struct.unpack('<I', d[16 + 32:16 + 36])[0]))
        elif tag == 3:  # hash
            print('  descriptor HASH: image=%r size=%d' % (
                d[16:16 + 32].split(b'\0')[0].decode('utf-8', 'replace'),
                struct.unpack('<Q', d[8:16])[0]))
        elif tag == 0:
            break
        else:
            print('  descriptor tag=%d size=%d' % (tag, size))
        pos += size


def dtbo(path, label):
    with open(path, 'rb') as f:
        h = f.read(40)
    magic, total, hdr, dtb_off, dtb_size, dtb_count, entry_size, dtb_ver, total_size = struct.unpack('<9I', h[:36])
    print('%s: magic=%#x total=%d hdr=%d dtb_offset=%d dtb_size=%d count=%d entry=%d version=%d' % (
        label, magic, total, hdr, dtb_off, dtb_size, dtb_count, entry_size, dtb_ver))
    print('  sha256=%s' % sha(path))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'boot':
        for p in sys.argv[2:]:
            boot(p, os.path.basename(p))
    elif cmd == 'vbmeta':
        for p in sys.argv[2:]:
            vbmeta(p, os.path.basename(p))
    elif cmd == 'dtbo':
        for p in sys.argv[2:]:
            dtbo(p, os.path.basename(p))