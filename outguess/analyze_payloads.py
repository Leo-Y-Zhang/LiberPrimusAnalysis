# -*- coding: utf-8 -*-
"""Characterise every outguess payload (size, entropy, magic bytes, printable share, markers, identity across
images and keys), then keystream-test the no-key payloads and any anomalous payload against the section printed
on the same page (image NN.jpg = dump page NN-17), in raw (mod 29) and chain (mod 28) forms, as bytes and 5-bit groups.
Usage: python analyze_payloads.py <out-dir>"""
import hashlib, math, os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lp, fastscan
import numpy as np

root = sys.argv[1]
unsolved = lp.unsolved_sections()
page_to_section = {}
for s in unsolved:
    lo, hi = [int(x) for x in s['name'][1:].split('-')]
    for p in range(lo, hi + 1):
        page_to_section[p + 17] = s


def entropy(b):
    c = Counter(b)
    n = len(b)
    return -sum(v / n * math.log2(v / n) for v in c.values())


rows, seen = [], {}
for dp, dn, fn in os.walk(root):
    for f in sorted(fn):
        p = os.path.join(dp, f)
        b = open(p, 'rb').read()
        if not b:
            continue
        h = hashlib.sha256(b).hexdigest()[:12]
        rel = os.path.relpath(p, root)
        seen.setdefault(h, []).append(rel)
        printable = sum(1 for x in b if 32 <= x < 127 or x in (9, 10, 13)) / len(b)
        mark = (b'PGP' in b) or (b'BEGIN' in b) or (b'3301' in b) or (b'http' in b) or (b'.onion' in b)
        rows.append((rel, len(b), round(entropy(b), 3), b[:6].hex(), round(printable, 2), mark, h))
print('payloads: %d ; total bytes: %d' % (len(rows), sum(r[1] for r in rows)))
ent = [r[2] for r in rows]
print('entropy (bits/byte): min %.3f median %.3f max %.3f ; printable share max %.2f' % (min(ent), sorted(ent)[len(ent) // 2], max(ent), max(r[4] for r in rows)))
low = [r for r in rows if r[2] < 7.8 or r[4] > 0.5 or r[5]]
print('anomalous payloads (entropy < 7.8, printable > 0.5, or a text marker):')
for r in sorted(low, key=lambda r: r[2])[:40]:
    print('   %-44s %7d bytes H=%.3f magic=%s print=%.2f mark=%s' % (r[0], r[1], r[2], r[3], r[4], r[5]))
if not low:
    print('   none')
dups = {h: ps for h, ps in seen.items() if len(ps) > 1}
print('identical payloads across images/keys: %d groups' % len(dups))
for h, ps in list(dups.items())[:10]:
    print('   ', ps[:6])
print('size distribution (top):', Counter(r[1] for r in rows).most_common(6))
print('no-key payloads:', sorted(r[0] for r in rows if r[0].startswith('nopass')))

print()
print('keystream test against the own-page section (best IoC over all offsets vs noise ceiling)')
targets = [r for r in rows if r[0].startswith('nopass')] + [r for r in low if not r[0].startswith('nopass')]
excess = []
for r in targets:
    p = os.path.join(root, r[0])
    b = np.frombuffer(open(p, 'rb').read(), dtype=np.uint8).astype(np.int64)
    if len(b) < 420:
        continue
    try:
        page = int(os.path.basename(r[0]).split('.')[0])
    except ValueError:
        continue
    s = page_to_section.get(page)
    if s is None:
        print('  %-44s image %02d has no unsolved section' % (r[0], page))
        continue
    bits = np.unpackbits(b.astype(np.uint8))
    k = len(bits) // 5 * 5
    g5 = bits[:k].reshape(-1, 5).dot(np.array([16, 8, 4, 2, 1]))
    best = (0.0, None)
    for kname, K in (('bytes', b), ('5bit', g5)):
        for form in ('raw', 'chain'):
            ix = s['indices']
            if form == 'raw':
                c = np.array(ix[:400]); m = 29
            else:
                c = fastscan.chain_steps(ix, 400); m = 28
            for sg in (1, -1):
                v, off, _ = fastscan.scan_stream(c, sg * (K % m), m)
                if v > best[0]:
                    best = (v, (kname, form, sg, off))
    thr = fastscan.null_threshold(len(b))
    flag = '  <== ABOVE NOISE' if best[0] > thr + 0.03 else ''
    print('  %-44s vs %-7s best IoC=%.3f (noise ~%.3f) %s%s' % (r[0], s['name'], best[0], thr, best[1], flag), flush=True)
    excess.append((round(best[0] - thr, 3), r[0]))
excess.sort(reverse=True)
print('largest excess over the noise ceiling:', excess[:5])
print('ANALYSIS DONE')
