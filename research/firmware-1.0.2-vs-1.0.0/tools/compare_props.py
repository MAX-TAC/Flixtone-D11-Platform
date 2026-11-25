"""Compare getprop/props and package versions between the two dumps."""
import re, sys, json

def load_props(p):
    d = {}
    for line in open(p, encoding='utf-8', errors='replace'):
        m = re.match(r'^\[([^\]]+)\]: \[(.*)\]$', line.strip())
        if m:
            d[m.group(1)] = m.group(2)
    return d

def load_pkgs_dumpsys(path):
    """Extract Package [name] (...) versionName/versionCode, path, flags from dumpsys package."""
    txt = open(path, encoding='utf-8', errors='replace').read()
    out = {}
    # blocks start with "  Package [name] (hash):"
    for m in re.finditer(r'\n\s*Package \[([^\]]+)\] \(([0-9a-f]+)\):', txt):
        name = m.group(1)
        start = m.end()
        nxt = txt.find('\n    Package [', start)
        if nxt < 0:
            nxt = txt.find('\n  Package [', start)
        if nxt < 0:
            nxt = len(txt)
        block = txt[start:nxt]
        entry = {}
        vm = re.search(r'versionName=(\S+)', block)
        vc = re.search(r'versionCode=(\d+)', block)
        ap = re.search(r'codePath=(\S+)', block)
        entry['versionName'] = vm.group(1) if vm else None
        entry['versionCode'] = vc.group(1) if vc else None
        entry['codePath'] = ap.group(1) if ap else None
        out[name] = entry
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'props':
        a = load_props(sys.argv[2])
        b = load_props(sys.argv[3])
        only_a = {k: v for k, v in a.items() if k not in b}
        only_b = {k: v for k, v in b.items() if k not in a}
        changed = {k: (b[k], a[k]) for k in a if k in b and a[k] != b[k]}
        print('total new', len(a), 'mine', len(b))
        print('\nONLY IN DUMP (%d):' % len(only_a))
        for k in sorted(only_a):
            print('  %s = %s' % (k, only_a[k]))
        print('\nONLY IN MINE (%d):' % len(only_b))
        for k in sorted(only_b):
            print('  %s = %s' % (k, only_b[k]))
        print('\nCHANGED (%d):' % len(changed))
        for k in sorted(changed):
            print('  %s : mine=%r -> dump=%r' % (k, changed[k][1], changed[k][0]))
    elif mode == 'pkgs':
        a = load_pkgs_dumpsys(sys.argv[2])
        b = load_pkgs_dumpsys(sys.argv[3])
        print('dump packages', len(a), 'mine', len(b))
        print('\nONLY IN DUMP:', sorted(set(a) - set(b)))
        print('\nONLY IN MINE:', sorted(set(b) - set(a)))
        print('\nVERSION DIFFS:')
        for k in sorted(set(a) & set(b)):
            if a[k]['versionCode'] != b[k]['versionCode'] or a[k]['versionName'] != b[k]['versionName']:
                print('  %-45s mine %s/%s -> dump %s/%s' % (k, b[k]['versionCode'], b[k]['versionName'], a[k]['versionCode'], a[k]['versionName']))
        print('\nPATH DIFFS:')
        for k in sorted(set(a) & set(b)):
            if a[k]['codePath'] != b[k]['codePath']:
                print('  %-45s mine %s -> dump %s' % (k, b[k]['codePath'], a[k]['codePath']))