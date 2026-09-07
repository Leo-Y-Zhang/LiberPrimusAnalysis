# -*- coding: utf-8 -*-
"""Difference-stream (chain cipher) analysis: is Δc = c_i - c_{i-1} a periodic Vigenere over 28/29 symbols?"""
import os, sys, math
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import numpy as np

ds = lp.load_dataset()
unsolved = [s for s in ds['sections'] if not s['solved']]
INV = {a: pow(a, -1, 29) for a in range(1, 29)}


def streams(ix):
    d1 = [(ix[i] - ix[i - 1]) % 29 for i in range(1, len(ix))]
    s1 = [(ix[i] + ix[i - 1]) % 29 for i in range(1, len(ix))]
    d2 = [(ix[i] - ix[i - 2]) % 29 for i in range(2, len(ix))]
    r1 = [(ix[i] * INV[ix[i - 1]]) % 29 if ix[i - 1] != 0 and ix[i] != 0 else -1 for i in range(1, len(ix))]
    return {'raw': ix, 'diff1': d1, 'sum1': s1, 'diff2': d2, 'ratio': [x for x in r1 if x >= 0]}


def pioc_profile(x, maxp=300):
    x = [v for v in x if v >= 0]
    res = []
    for p in range(1, min(maxp, len(x) // 6) + 1):
        res.append((p, lp.periodic_ioc(x, p)))
    vals = np.array([v for _, v in res])
    # z relative to periods > 1 excluding top few
    mu, sd = vals.mean(), vals.std() + 1e-9
    top = sorted(res, key=lambda t: -t[1])[:6]
    return [(p, round(v, 3), round((v - mu) / sd, 1)) for p, v in top]


def kasiski_factors(x, n=4):
    pos = defaultdict(list)
    for i in range(len(x) - n + 1):
        pos[tuple(x[i:i + n])].append(i)
    dist = Counter()
    for g, p in pos.items():
        if len(p) > 1:
            for a, b in zip(p, p[1:]):
                dist[b - a] += 1
    fac = Counter()
    for d, c in dist.items():
        for f in range(3, 100):
            if d % f == 0:
                fac[f] += c
    return sum(dist.values()), fac.most_common(6)


for s in unsolved:
    st = streams(s['indices'])
    print('== %s n=%d' % (s['name'], s['n_runes']))
    for name, x in st.items():
        print('   %-6s ioc=%.3f  top periodic IoC (period, ioc, z): %s | kasiski reps=%d factors=%s' % (
            name, lp.ioc([v for v in x if v >= 0]), pioc_profile(x), *kasiski_factors([v for v in x if v >= 0])))

# whole corpus concatenated diff stream (in case one long key spans the book)
allc = [i for s in unsolved for i in s['indices']]
st = streams(allc)
print('== ALL n=%d' % len(allc))
for name, x in st.items():
    print('   %-6s ioc=%.3f  top periodic IoC: %s' % (name, lp.ioc([v for v in x if v >= 0]), pioc_profile(x, 600)))

# Conditional structure: is Δc independent of the previous rune? (chi2 of 29x29 table c_{i-1} vs Δc)
print()
tab = np.zeros((29, 29))
for i in range(1, len(allc)):
    tab[allc[i - 1], (allc[i] - allc[i - 1]) % 29] += 1
exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
chi = ((tab - exp) ** 2 / np.maximum(exp, 1e-9)).sum()
print('independence of Δc from previous rune: chi2=%.1f df=%d (expect ~%d if independent)' % (chi, 28 * 28, 28 * 28))
tab2 = np.zeros((29, 29))
for i in range(1, len(allc)):
    tab2[allc[i - 1], allc[i]] += 1
exp2 = tab2.sum(1, keepdims=True) * tab2.sum(0, keepdims=True) / tab2.sum()
chi2 = ((tab2 - exp2) ** 2 / np.maximum(exp2, 1e-9)).sum()
print('bigram table c_{i-1},c_i chi2=%.1f df=784; diagonal contribution=%.1f' % (
    chi2, ((np.diag(tab2) - np.diag(exp2)) ** 2 / np.diag(exp2)).sum()))
# largest off-diagonal cells
cells = [(tab2[a, b], exp2[a, b], a, b) for a in range(29) for b in range(29) if a != b]
cells.sort(key=lambda t: -(t[0] - t[1]) ** 2 / t[1])
print('most anomalous off-diagonal bigrams:', [(lp.LETTERS[a] + lp.LETTERS[b], int(o), round(e, 1)) for o, e, a, b in cells[:8]])

# word-boundary: is Δ across word boundaries different from within?
print()
within, boundary = Counter(), Counter()
for s in unsolved:
    ix = s['indices']
    toks = s['tokens']
    wpos = []
    wi, pi = 0, 0
    for k, v in toks:
        if k == 'r':
            wpos.append(wi)
            pi += 1
        elif k == 'w':
            if pi > 0:
                wi += 1
            pi = 0
    for i in range(1, len(ix)):
        d = (ix[i] - ix[i - 1]) % 29
        (within if wpos[i] == wpos[i - 1] else boundary)[d] += 1
print('Δ=0 rate within words %.4f (n=%d), across boundaries %.4f (n=%d)' % (
    within[0] / sum(within.values()), sum(within.values()), boundary[0] / sum(boundary.values()), sum(boundary.values())))

# first rune of each word vs last rune of previous word etc: is the first rune of words uniform?
firsts = Counter(w[0] for s in unsolved for w in s['words'])
lasts = Counter(w[-1] for s in unsolved for w in s['words'])
n = sum(firsts.values())
print('first-rune chi2 vs uniform: %.1f ; last-rune chi2: %.1f (df 28)' % (
    sum((firsts.get(i, 0) - n / 29) ** 2 / (n / 29) for i in range(29)),
    sum((lasts.get(i, 0) - n / 29) ** 2 / (n / 29) for i in range(29))))
print('top first runes:', [(lp.LETTERS[i], c) for i, c in firsts.most_common(6)], 'top last:', [(lp.LETTERS[i], c) for i, c in lasts.most_common(6)])
# 1-letter words: which runes
ones = Counter(w[0] for s in unsolved for w in s['words'] if len(w) == 1)
print('1-rune words:', [(lp.LETTERS[i], c) for i, c in ones.most_common()])
twos = Counter(tuple(w) for s in unsolved for w in s['words'] if len(w) == 2)
print('2-rune words total %d distinct %d; most common: %s' % (sum(twos.values()), len(twos), [(lp.idx_to_text(w), c) for w, c in twos.most_common(8)]))
