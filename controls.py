# -*- coding: utf-8 -*-
"""Positive controls: do our detectors find known ciphers on synthetic ciphertexts built from real LP plaintext?"""
import os, sys, math, random
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import numpy as np

random.seed(3301)
ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]
P = [i for s in solved for i in s['plain_indices']]
WP = lp.runes_to_idx(open(os.path.join(lp.DATA, 'baseline-rune-stream.txt'), encoding='utf-8').read())[:50000]
LONG = WP[:3000]          # 3000 runes of English-in-runes (same length as p40-53)


def kappa_lag(x, lag):
    n = len(x) - lag
    return sum(1 for i in range(n) if x[i] == x[i + lag]) / n


def zk(k, n):
    return (k - 1 / 29) / math.sqrt((1 / 29) * (28 / 29) / n)


def enc_vig(p, key, interrupts=False, skip_on_collision=False):
    out, j, prev = [], 0, None
    for x in p:
        if interrupts and x == 0:
            out.append(0); prev = 0
            continue
        c = (x + key[j % len(key)]) % 29
        j += 1
        if skip_on_collision and c == prev:
            c = (x + key[j % len(key)]) % 29
            j += 1
        out.append(c); prev = c
    return out


print('C1: Vigenère period-13 random key on 3000 runes: periodic IoC peak + kappa at lag 13')
key = [random.randrange(29) for _ in range(13)]
for name, c in (('plain', enc_vig(LONG, key)), ('F-interrupts', enc_vig(LONG, key, interrupts=True)),
                ('skip-on-collision', enc_vig(LONG, key, skip_on_collision=True)),
                ('interrupts+skip', enc_vig(LONG, key, True, True))):
    prof = [(m, lp.periodic_ioc(c, m)) for m in range(1, 60)]
    best = max(prof, key=lambda t: t[1])
    kl = kappa_lag(c, 13)
    dbl = lp.doublets(c) / (len(c) - 1)
    print('   %-18s periodicIoC best=%d (%.3f) ; kappa@13=%.4f z=%.1f ; kappa@26=%.4f ; doublet=%.4f' % (
        name, best[0], best[1], kl, zk(kl, len(c) - 13), kappa_lag(c, 26), dbl))
print('   observed corpus: max kappa over lags 1..400 = 0.0398 (z≈3.3), sections max ≈ 0.04-0.065 (n small)')

print()
print('C2: chain cipher in Z28 with sequence key (prime_n), EA -> zero step; can tests4-style attack recover it?')
def enc_chain(p, keyseq):
    out, prev = [], 0
    for i, x in enumerate(p):
        if x == 28:
            s = 0
        else:
            s = 1 + ((x + keyseq[i]) % 28)
        prev = (prev + s) % 29
        out.append(prev)
    return out
g = lp.prime_gen(); PR = [next(g) for _ in range(6000)]
c = enc_chain(LONG, PR)
u = [((c[i] - c[i - 1]) % 29 - 1) % 28 for i in range(1, len(c)) if c[i] != c[i - 1]]
# key alignment: u index j corresponds to plaintext index i (skipping EA and the first rune) -> offset drift; test offsets
def ioc_mod(x, m):
    n = len(x); cc = Counter(x); return sum(v * (v - 1) for v in cc.values()) / (n * (n - 1) / m)
best = (0, None)
for off in range(0, 40):
    for sign in (1, -1):
        v = ioc_mod([(u[j] - sign * PR[j + off]) % 28 for j in range(min(len(u), 400))], 28)
        best = max(best, (v, (off, sign)))
print('   doublet rate of synthetic chain ciphertext: %.4f ; IoC of Δc: %.3f ; best decrypt IoC(28) on first 400 = %.3f at %s' % (
    lp.doublets(c) / (len(c) - 1), lp.ioc([(c[i] - c[i - 1]) % 29 for i in range(1, len(c))]), best[0], best[1]))
print('   (note: EA positions shift the alignment by one each time, so windows after an EA need offset+1: the scan handles small drifts only)')

print()
print('C3: running key (English) at offset 1234, vig: IoC of c - K at the right offset on a 400-rune window')
K = WP[10000:]
c = [(LONG[i] + K[1234 + i]) % 29 for i in range(len(LONG))]
vals = []
for off in range(0, 3000):
    vals.append(lp.ioc([(c[i] - K[off + i]) % 29 for i in range(400)]))
vals = np.array(vals)
print('   IoC at true offset=%.3f ; null mean=%.3f sd=%.3f ; z=%.1f' % (vals[1234], np.delete(vals, 1234).mean(), np.delete(vals, 1234).std(),
                                                                (vals[1234] - np.delete(vals, 1234).mean()) / np.delete(vals, 1234).std()))

print()
print('C4: two sections sharing one running key with a relative shift of 300: cross kappa at the right shift')
a = [(LONG[i] + K[i]) % 29 for i in range(1500)]
b = [(WP[20000 + i] + K[300 + i]) % 29 for i in range(1500)]
ks = [(sft, sum(1 for i in range(1200) if a[i + sft] == b[i]) / 1200) for sft in range(0, 300 + 1)]
best = max(ks, key=lambda t: t[1])
print('   best shift=%d kappa=%.4f z=%.1f (true 300)' % (best[0], best[1], zk(best[1], 1200)))

print()
print('C5: ciphertext autokey c_i = p_i + c_{i-1}: does Δc IoC expose it?')
c = []; prev = 0
for x in LONG:
    prev = (x + prev) % 29; c.append(prev)
print('   Δc IoC=%.3f (English ≈1.78) doublets=%.4f' % (lp.ioc([(c[i] - c[i - 1]) % 29 for i in range(1, len(c))]), lp.doublets(c) / (len(c) - 1)))

print()
print('C6: hill-climb-free check of Scorer discrimination: score of English vs random vs Vigenère-decrypted-with-wrong-key')
sc = lp.Scorer()
print('   english %.3f  random %.3f  wrongkey %.3f' % (sc.score(LONG[:500]), sc.score([random.randrange(29) for _ in range(500)]),
                                                     sc.score(lp.vigenere_decrypt(enc_vig(LONG[:500], key), [1, 2, 3]))))
