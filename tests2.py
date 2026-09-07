# -*- coding: utf-8 -*-
"""Cheap decisive tests:
T1 word-level Caesar/affine hypothesis via difference-tuple dictionary lookup
T2 anatomy of the 86 doublets
T3 title segments of every unsolved section
A5 cross-section kappa at all shifts (shared running key with offsets?)
A6 running-key attack using the solved LP plaintext / ciphertext as key, all offsets
"""
import os, sys, math
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import numpy as np

ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]
C = [i for s in unsolved for i in s['indices']]
P = [i for s in solved for i in s['plain_indices']]

# ---------------- T1 ----------------
print('T1: word-level Caesar (difference-tuple) test')
ext = lp.load_external_dictionary()
diff_set = set()
diff_set_rev = set()
for w in ext:
    if len(w) >= 4:
        d = tuple((w[i] - w[i - 1]) % 29 for i in range(1, len(w)))
        diff_set.add(d)
        diff_set_rev.add(d[::-1])
# affine-normalised: multiply diffs by inverse of first nonzero diff
def norm(d):
    for x in d:
        if x != 0:
            inv = pow(x, -1, 29)
            return tuple((y * inv) % 29 for y in d)
    return d
aff_set = set(norm(d) for d in diff_set)
import random
random.seed(1)
for L in range(4, 9):
    cw = [w for s in unsolved for w in s['words'] if len(w) == L]
    hits = sum(1 for w in cw if tuple((w[i] - w[i - 1]) % 29 for i in range(1, L)) in diff_set)
    hits_rev = sum(1 for w in cw if tuple((w[i] - w[i - 1]) % 29 for i in range(1, L)) in diff_set_rev)
    hits_aff = sum(1 for w in cw if norm(tuple((w[i] - w[i - 1]) % 29 for i in range(1, L))) in aff_set)
    # random baseline
    rw = [[random.randrange(29) for _ in range(L)] for _ in range(2000)]
    rh = sum(1 for w in rw if tuple((w[i] - w[i - 1]) % 29 for i in range(1, L)) in diff_set) / len(rw)
    rha = sum(1 for w in rw if norm(tuple((w[i] - w[i - 1]) % 29 for i in range(1, L))) in aff_set) / len(rw)
    pw = [w for s in solved for w in s['plain_words'] if len(w) == L]
    ph = sum(1 for w in pw if tuple((w[i] - w[i - 1]) % 29 for i in range(1, L)) in diff_set) / max(1, len(pw))
    print('  len %d: cipher words %4d  caesar-hit %.3f  reversed %.3f  affine %.3f | random %.3f / affine %.3f | LP-plain %.3f' % (
        L, len(cw), hits / len(cw), hits_rev / len(cw), hits_aff / len(cw), rh, rha, ph))

# ---------------- T2 ----------------
print()
print('T2: doublet anatomy (rune, count) and context')
dbl = Counter()
ctx = []
pos = 0
for s in unsolved:
    ix = s['indices']
    toks = s['tokens']
    # map rune-position -> (word index, position in word)
    wpos = []
    wi, pi = 0, 0
    for k, v in toks:
        if k == 'r':
            wpos.append((wi, pi))
            pi += 1
        elif k == 'w':
            if pi > 0:
                wi += 1
            pi = 0
    for i in range(1, len(ix)):
        if ix[i] == ix[i - 1]:
            dbl[ix[i]] += 1
            w1, p1 = wpos[i - 1]
            w2, p2 = wpos[i]
            ctx.append((s['name'], i, lp.LETTERS[ix[i]], 'within' if w1 == w2 else 'boundary', p2))
print('  doubled runes:', [(lp.LETTERS[r], c) for r, c in dbl.most_common()])
exp = Counter(C)
print('  expected if random (freq^2 * pairs):', [(lp.LETTERS[r], round(exp[r] ** 2 / len(C), 1)) for r, _ in dbl.most_common()])
print('  position-in-word of 2nd rune of doublet:', Counter(p for *_, p in ctx).most_common())
print('  sample:', ctx[:12])

# ---------------- T3 ----------------
print()
print('T3: title segments (before first chapter mark) of unsolved sections')
for s in unsolved:
    toks = s['tokens']
    seg = []
    for k, v in toks:
        if k == 'w' and v == '#':
            break
        seg.append((k, v))
    words = lp.words_of(seg)
    print('  %-8s %s  lens=%s  %s' % (s['name'], lp.render(seg), [len(w) for w in words],
                                     ' '.join(lp.idx_to_runes(w) for w in words)))
# also every chapter-mark-delimited short segment (<= 40 runes) anywhere
print('  short segments anywhere (<=40 runes):')
for s in unsolved:
    for j, seg in enumerate(s['segments_by_chaptermark']):
        if len(seg) <= 40:
            print('    %-8s seg%d n=%d %s' % (s['name'], j, len(seg), lp.idx_to_text(seg, ' ')))

# ---------------- A5 ----------------
print()
print('A5: cross-section kappa over all relative shifts (peak z-scores)')
arr = {s['name']: np.array(s['indices']) for s in unsolved}
names = [s['name'] for s in unsolved]
def kappa_shifts(a, b, minover=150):
    best = []
    for sft in range(-(len(b) - minover), len(a) - minover):
        if sft >= 0:
            x = a[sft:sft + len(b)]
            y = b[:len(x)]
        else:
            y = b[-sft:-sft + len(a)]
            x = a[:len(y)]
        n = len(x)
        if n < minover:
            continue
        m = int((x == y).sum())
        z = (m - n / 29) / math.sqrt(n * (1 / 29) * (28 / 29))
        best.append((z, sft, n, m))
    best.sort(reverse=True)
    return best[:3]
for i, a in enumerate(names):
    for b in names[i:]:
        if a == b:
            # self at nonzero shift
            top = [t for t in kappa_shifts(arr[a], arr[b]) if t[1] != 0][:2]
        else:
            top = kappa_shifts(arr[a], arr[b])[:2]
        print('  %-8s %-8s  %s' % (a, b, ' '.join('z=%.1f@%d(n=%d)' % (z, sft, n) for z, sft, n, m in top)))

# ---------------- A6 ----------------
print()
print('A6: running-key attack with LP solved plaintext (and cipher) as key, all offsets, 4 modes')
keys = {
    'solved_plain': np.array(P),
    'solved_plain_atbash': np.array([28 - x for x in P]),
    'solved_cipher': np.array([i for s in solved for i in s['indices']]),
}
sc = lp.Scorer()
for kname, K in keys.items():
    for s in unsolved:
        c = np.array(s['indices'])
        n = min(len(c), 400)
        c = c[:n]
        best = (0, None, None)
        for off in range(0, len(K) - n):
            k = K[off:off + n]
            for mode, out in (('vig', (c - k) % 29), ('beau', (k - c) % 29), ('add', (c + k) % 29)):
                v = lp.ioc(out.tolist())
                if v > best[0]:
                    best = (v, off, mode)
        print('  key=%-20s %-8s best ioc=%.3f at off=%s mode=%s' % (kname, s['name'], best[0], best[1], best[2]))
