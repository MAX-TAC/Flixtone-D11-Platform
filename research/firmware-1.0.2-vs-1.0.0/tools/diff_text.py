import difflib, sys, os

names = sys.argv[1:]
for n in names:
    a = os.path.join('_cmp/tvcfg_new', n)
    b = os.path.join('_cmp/tvcfg_mine', n)
    if not (os.path.exists(a) and os.path.exists(b)):
        print('MISSING', n)
        continue
    al = open(a, encoding='utf-8', errors='replace').read().splitlines()
    bl = open(b, encoding='utf-8', errors='replace').read().splitlines()
    d = list(difflib.unified_diff(bl, al, fromfile='mine/' + n, tofile='new/' + n, lineterm='', n=2))
    print('=' * 80)
    print(n, 'lines mine=%d new=%d diff=%d' % (len(bl), len(al), len(d)))
    print('\n'.join(d[:400]))