# -*- coding: utf-8 -*-
"""Two structural tests whose outputs are quoted in the report:
 (a) coincidence rate at every lag per section (survives interrupts and key-skipping, unlike periodic IoC),
     with the random-text null for the best lag; harmonics of any candidate period;
 (b) parity of doublet positions modulo 2..8 relative to section and sentence starts (block-cipher signature)."""
import math, os, random, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

ds = lp.load_dataset()
unsolved = [s for s in ds['sections'] if not s['solved']]


def kappa(x, lag):
    n = len(x) - lag
    return sum(1 for i in range(n) if x[i] == x[i + lag]) / n, n


def z(k, n):
    return (k - 1 / 29) / math.sqrt((1 / 29) * (28 / 29) / n)


print('(a) best lags by z per section (lags 1..min(300, n/3))')
for s in unsolved:
    ix = s['indices']
    prof = sorted(((z(*kappa(ix, lag)), lag) for lag in range(1, min(300, len(ix) // 3))), reverse=True)
    print('  %-8s n=%d %s' % (s['name'], len(ix), ' '.join('%d:z%.1f' % (l, zz) for zz, l in prof[:5])))
random.seed(1)
mx = []
for _ in range(200):
    r = [random.randrange(29) for _ in range(729)]
    mx.append(max(z(*kappa(r, lag)) for lag in range(1, 243)))
print('  null: best-lag z for random 729-rune text: mean %.2f sd %.2f' % (sum(mx) / len(mx), (sum((v - sum(mx) / len(mx)) ** 2 for v in mx) / len(mx)) ** 0.5))
ix = lp.section('p0-2')['indices']
print('  p0-2 harmonics of 35:', ' '.join('%d:z%.1f' % (lag, z(*kappa(ix, lag))) for lag in (35, 70, 105, 140)))

print('(b) doublet position parity')
rows = []
for s in unsolved:
    ix, toks = s['indices'], s['tokens']
    srel, cnt = [], 0
    for k, v in toks:
        if k == 'r':
            srel.append(cnt); cnt += 1
        elif k == 'w' and v in '.#;':
            cnt = 0
    for i in range(1, len(ix)):
        if ix[i] == ix[i - 1]:
            rows.append((i, srel[i]))
print('  doublets:', len(rows))
for m in range(2, 9):
    for label, col in (('section', 0), ('sentence', 1)):
        c = Counter(r[col] % m for r in rows)
        e = len(rows) / m
        chi = sum((c.get(k, 0) - e) ** 2 / e for k in range(m))
        print('  mod %d %-8s counts=%s chi2=%.1f (df %d)' % (m, label, [c.get(k, 0) for k in range(m)], chi, m - 1))
