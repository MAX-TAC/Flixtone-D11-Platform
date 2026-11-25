import os

def load(p):
    d = {}
    for line in open(p, encoding='utf-8'):
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 4 or parts[0] == 'path':
            continue
        d[parts[0]] = (parts[1], int(parts[2]), parts[3])
    return d

a = load('_cmp/ramdisk_new.tsv')
b = load('_cmp/ramdisk_mine.tsv')
common = sorted(set(a) & set(b))
changed = [x for x in common if a[x][2] != b[x][2]]
resized = [(x, b[x][1], a[x][1]) for x in common if a[x][1] != b[x][1]]
out = []
out.append('ramdisk: entries new=%d mine=%d' % (len(a), len(b)))
out.append('added: %s' % sorted(set(a) - set(b)))
out.append('removed: %s' % sorted(set(b) - set(a)))
out.append('content changed: %d' % len(changed))
out.append('size changed: %d' % len(resized))
for x, y, z in resized:
    out.append('  %s  %d -> %d (%+d)' % (x, y, z, z - y))
out.append('changed list:')
out.extend('  ' + x for x in changed)
open('_cmp/ramdisk_diff_summary.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out[:8]))