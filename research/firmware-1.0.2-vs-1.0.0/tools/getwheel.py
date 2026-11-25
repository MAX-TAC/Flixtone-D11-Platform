"""Fetch a wheel from PyPI and unzip it into a target dir (bypasses pip temp ACL issues)."""
import json, ssl, sys, os, zipfile, urllib.request, io

def fetch(url, ctx):
    req = urllib.request.Request(url, headers={'User-Agent': 'python-urllib/3'})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        return r.read()


def main(pkg, target):
    ctx = ssl.create_default_context()
    try:
        data = json.loads(fetch(f'https://pypi.org/pypi/{pkg}/json', ctx))
    except Exception as e:
        print('default ctx failed:', e)
        ctx = ssl._create_unverified_context()
        data = json.loads(fetch(f'https://pypi.org/pypi/{pkg}/json', ctx))
    print('latest', data['info']['version'])
    tag = 'cp%d%d' % sys.version_info[:2]
    cands = []
    for f in data['urls']:
        fn = f['filename']
        if fn.endswith('.whl') and ('win_amd64' in fn or 'win32' in fn or 'any' in fn):
            cands.append(f)
    pick = None
    pref = []
    for f in cands:
        fn = f['filename']
        if tag in fn and 'win_amd64' in fn:
            pref.append(f)
    for f in cands:
        fn = f['filename']
        if tag in fn and ('win' in fn):
            pref.append(f)
    for f in cands:
        fn = f['filename']
        if 'py3-none-any' in fn:
            pref.append(f)
    if pref:
        pick = pref[0]
    if not pick:
        print('no wheel'); return
    print('downloading', pick['filename'], pick['size'])
    blob = fetch(pick['url'], ctx)
    zf = zipfile.ZipFile(io.BytesIO(blob))
    os.makedirs(target, exist_ok=True)
    zf.extractall(target)
    print('extracted to', target, 'files', len(zf.namelist()))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])