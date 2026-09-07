# -*- coding: utf-8 -*-
"""(1) Chain-model sequence-key attack with correct alignment (key indexed by ciphertext position; doublets are
placeholders that may or may not consume a key element), all bijections {1..28}->Z28 incl. discrete logs.
(2) Power of IoC-of-differences vs kappa for shared running keys, then a re-scan of cross-section shared keys."""
import os, sys, math, random
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import numpy as np

random.seed(7)
ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]
WP = lp.runes_to_idx(open(os.path.join(lp.DATA, 'baseline-rune-stream.txt'), encoding='utf-8').read())[:60000]


def ioc_mod(x, m):
    n = len(x)
    if n < 2:
        return 0
    cc = Counter(x)
    return sum(v * (v - 1) for v in cc.values()) / (n * (n - 1) / m)


# ---------------- sequences (as in tests4 + more) ----------------
LIM = 4000
g = lp.prime_gen(); PR = [next(g) for _ in range(LIM + 400)]
def fib(n, a=1, b=1):
    out = []
    for _ in range(n):
        out.append(a); a, b = b, a + b
    return out
def totient(n):
    out = list(range(n + 1))
    for i in range(2, n + 1):
        if out[i] == i:
            for j in range(i, n + 1, i):
                out[j] -= out[j] // i
    return out
TOT = totient(LIM + 400)
PI = [int(c) for c in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pi.txt')).read() if c.isdigit()]
SEQS = {
    'n': list(range(LIM + 400)), 'n^2': [i * i for i in range(LIM + 400)], 'n^3': [i ** 3 for i in range(LIM + 400)],
    'tri': [i * (i + 1) // 2 for i in range(LIM + 400)], 'prime': PR, 'prime-1': [p - 1 for p in PR], 'prime+1': [p + 1 for p in PR],
    '2prime': [2 * p for p in PR], 'prime^2': [p * p for p in PR], 'gap': [PR[i + 1] - PR[i] for i in range(len(PR) - 1)],
    'cumsum_prime': list(np.cumsum(PR)), 'fib': fib(LIM + 400), 'lucas': fib(LIM + 400, 2, 1), 'phi(n)': TOT,
    '2^n': [pow(2, i, 812) for i in range(LIM + 400)], '3^n': [pow(3, i, 812) for i in range(LIM + 400)],
    '3301n': [3301 * i for i in range(LIM + 400)], 'pi': PI, 'primeidx': [PR[i] for i in range(LIM + 400)],
    'emirp': [p for p in PR if str(p) != str(p)[::-1] and int(str(p)[::-1]) in set(PR)],
    'twin': [p for i, p in enumerate(PR[:-1]) if PR[i + 1] - p == 2],
    'pell': fib(LIM + 400, 0, 1) if False else (lambda: (lambda o: o)([0]))(),
}
# pell properly
pell = [0, 1]
while len(pell) < LIM + 400:
    pell.append(2 * pell[-1] + pell[-2])
SEQS['pell'] = pell
trib = [0, 0, 1]
while len(trib) < LIM + 400:
    trib.append(trib[-1] + trib[-2] + trib[-3])
SEQS['trib'] = trib
SEQS = {k: v for k, v in SEQS.items() if len(v) >= 500}

PRIM_ROOTS = [2, 3, 8, 10, 11, 14, 15, 18, 19, 21, 26, 27]
DLOG = {}
for gg in PRIM_ROOTS:
    t = {}
    v = 1
    for e in range(28):
        t[v] = e
        v = (v * gg) % 29
    DLOG[gg] = t
BIJ = {'s-1': lambda s: s - 1, '28-s': lambda s: 28 - s}
for gg in PRIM_ROOTS:
    BIJ['dlog%d' % gg] = (lambda t: (lambda s: t[s]))(DLOG[gg])


def steps(ix):
    return [(ix[i] - ix[i - 1]) % 29 for i in range(1, len(ix))]


def attack_chain(ix, label, window=500):
    """returns best (ioc, seq, off, sign, bij, convention)."""
    st = steps(ix)[:window]
    best = (0, None)
    for bname, B in BIJ.items():
        u = [B(s) if s != 0 else -1 for s in st]           # placeholder at doublets
        u_c = [x for x in u if x >= 0]                     # convention B: doublets do not consume key
        for sname, seq in SEQS.items():
            seq28 = [int(v) % 28 for v in seq[:len(st) + 400]]
            if len(seq28) < len(st) + 400:
                continue
            for off in range(0, 300):
                k = seq28[off:off + len(st)]
                for sign in (1, -1):
                    # convention A: key consumed at every position (incl. doublets)
                    outA = [(u[i] - sign * k[i]) % 28 for i in range(len(u)) if u[i] >= 0]
                    vA = ioc_mod(outA, 28)
                    # convention B
                    outB = [(u_c[i] - sign * k[i]) % 28 for i in range(len(u_c))]
                    vB = ioc_mod(outB, 28)
                    for v, conv in ((vA, 'A'), (vB, 'B')):
                        if v > best[0]:
                            best = (v, (sname, off, sign, bname, conv))
    return best


print('POSITIVE CONTROL: synthetic chain (prime key, s-1 embedding, EA->0, key consumed at EA):')
def enc_chain(p, keyseq, consume_at_ea=True):
    out, prev, j = [], 0, 0
    for x in p:
        if x == 28:
            s = 0
            if consume_at_ea:
                j += 1
        else:
            s = 1 + ((x + keyseq[j]) % 28); j += 1
        prev = (prev + s) % 29; out.append(prev)
    return out
for conv in (True, False):
    c = enc_chain(WP[:1500], [p % 28 for p in PR[50:]], conv)
    print('   consume_at_EA=%s -> best %s' % (conv, attack_chain(c, 'ctl')))
print()
print('ATTACK on unsolved sections (first 500 steps, all bijections, 300 offsets, both signs, both conventions):')
for s in unsolved:
    b = attack_chain(s['indices'], s['name'])
    print('   %-8s best IoC28=%.3f %s' % (s['name'], b[0], b[1]))

# ---------------- (2) shared-key power ----------------
print()
print('POWER: shared running key between two English texts, overlap 1200: kappa vs IoC-of-differences')
K = WP[30000:]
a = [(WP[i] + K[i]) % 29 for i in range(1200)]
b = [(WP[5000 + i] + K[i]) % 29 for i in range(1200)]
d = [(a[i] - b[i]) % 29 for i in range(1200)]
kap = sum(1 for i in range(1200) if a[i] == b[i]) / 1200
print('   true alignment: kappa=%.4f  IoC(diff)=%.3f' % (kap, lp.ioc(d)))
# null distribution of IoC(diff) and kappa for random alignments
nk, ni = [], []
for t in range(300):
    off = random.randrange(2000, 20000)
    b2 = [(WP[off + i] + K[3000 + i]) % 29 for i in range(1200)]
    nk.append(sum(1 for i in range(1200) if a[i] == b2[i]) / 1200)
    ni.append(lp.ioc([(a[i] - b2[i]) % 29 for i in range(1200)]))
print('   null kappa mean=%.4f sd=%.4f -> z=%.1f ; null IoCdiff mean=%.3f sd=%.3f -> z=%.1f' % (
    np.mean(nk), np.std(nk), (kap - np.mean(nk)) / np.std(nk), np.mean(ni), np.std(ni), (lp.ioc(d) - np.mean(ni)) / np.std(ni)))

print()
print('RE-SCAN cross-section shared key with IoC(diff) at all shifts (overlap >= 300):')
arr = {s['name']: np.array(s['indices']) for s in unsolved}
names = [s['name'] for s in unsolved]
allbest = []
for i, x in enumerate(names):
    for y in names[i:]:
        A, Bv = arr[x], arr[y]
        best = (0, 0, 0)
        for sft in range(-(len(Bv) - 300), len(A) - 300):
            if x == y and sft == 0:
                continue
            if sft >= 0:
                aa = A[sft:sft + len(Bv)]; bb = Bv[:len(aa)]
            else:
                bb = Bv[-sft:-sft + len(A)]; aa = A[:len(bb)]
            n = len(aa)
            if n < 300:
                continue
            dd = (aa - bb) % 29
            cnt = np.bincount(dd, minlength=29)
            v = (cnt * (cnt - 1)).sum() / (n * (n - 1) / 29)
            # crude z using sd ≈ 0.75/sqrt(n) (empirical for IoC of uniform data)
            z = (v - 1.0) / (0.75 / math.sqrt(n))
            if z > best[0]:
                best = (z, sft, n)
        allbest.append((best[0], x, y, best[1], best[2]))
allbest.sort(reverse=True)
for z, x, y, sft, n in allbest[:12]:
    print('   %-8s %-8s z=%.1f shift=%d overlap=%d' % (x, y, z, sft, n))
