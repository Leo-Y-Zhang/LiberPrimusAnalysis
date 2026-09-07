# -*- coding: utf-8 -*-
"""Fingerprint discriminator: which cipher families, applied to known Runeglish plaintext,
reproduce the unsolved ciphertext's statistics (flat IoC, 5x doublet suppression, uniform
difference distribution)?"""
import json, math, os, random, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

random.seed(3301)
ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]
P = [i for s in solved for i in s['plain_indices']]          # 2979 runes of real LP plaintext
C = [i for s in unsolved for i in s['indices']]              # 12956 unsolved cipher runes

# bigger English plaintext: War & Peace in runes (stream)
WP = lp.runes_to_idx(open(os.path.join(lp.DATA, 'baseline-rune-stream.txt'), encoding='utf-8').read())
WP = WP[:60000]


def dbl_rate(x):
    return lp.doublets(x) / (len(x) - 1)


def diffs(x, lag=1):
    return [(x[i] - x[i - lag]) % 29 for i in range(lag, len(x))]


def sums(x, lag=1):
    return [(x[i] + x[i - lag]) % 29 for i in range(lag, len(x))]


print('P(F) in LP plaintext = %.4f ; in W&P = %.4f' % (P.count(0) / len(P), WP.count(0) / len(WP)))
print('doublet rate: LP plain %.4f, W&P %.4f, unsolved cipher %.4f (random %.4f)' % (
    dbl_rate(P), dbl_rate(WP), dbl_rate(C), 1 / 29))
print('cipher doublet count %d of %d pairs; binomial std if rate=1/29: %.1f' % (
    lp.doublets(C), len(C) - 1, math.sqrt((len(C) - 1) * (1 / 29) * (28 / 29))))
print()

# ---- difference distribution of ciphertext ----
print('Cipher Δc = c_i - c_{i-1} distribution (count, z vs uniform):')
n = len(C) - 1
e = n / 29
sd = math.sqrt(e * (28 / 29))
d1 = Counter(diffs(C))
for d in range(29):
    z = (d1.get(d, 0) - e) / sd
    flag = ' <==' if abs(z) > 3 else ''
    print('  Δ=%2d  n=%4d  z=%+.1f%s' % (d, d1.get(d, 0), z, flag))
print('IoC of Δc(lag1)=%.3f  Δc(lag2)=%.3f  Σc(lag1)=%.3f  Δc(lag3)=%.3f' % (
    lp.ioc(diffs(C)), lp.ioc(diffs(C, 2)), lp.ioc(sums(C)), lp.ioc(diffs(C, 3))))
print('doublet rate at lag2 (c_i==c_{i-2}): %.4f  lag3: %.4f' % (
    sum(1 for i in range(2, len(C)) if C[i] == C[i - 2]) / (len(C) - 2),
    sum(1 for i in range(3, len(C)) if C[i] == C[i - 3]) / (len(C) - 3)))
# also within each section separately (chains may reset per section / per word)
print()
print('Per-section doublets: total / at word boundary / within word / expected random:')
for s in unsolved:
    ix = s['indices']
    words = s['words']
    within = sum(lp.doublets(w) for w in words)
    total = lp.doublets(ix)
    print('  %-8s total=%3d boundary=%3d within=%3d  exp_total=%.1f' % (
        s['name'], total, total - within, within, (len(ix) - 1) / 29))
print()

# ---- candidate encryptions of real plaintext ----
def primes():
    g = lp.prime_gen()
    while True:
        yield next(g)


def enc_vig(p, key):
    return [(x + key[i % len(key)]) % 29 for i, x in enumerate(p)]


def enc_stream(p, ks):
    it = iter(ks)
    return [(x + next(it)) % 29 for x in p]


def enc_cipher_autokey(p, seed=0):
    out, prev = [], seed
    for x in p:
        c = (x + prev) % 29
        out.append(c)
        prev = c
    return out


def enc_cipher_autokey_minus(p, seed=0):
    out, prev = [], seed
    for x in p:
        c = (x - prev) % 29
        out.append(c)
        prev = c
    return out


def enc_plain_autokey(p, seed=(0,), lag=1):
    key = list(seed)
    out = []
    for i, x in enumerate(p):
        out.append((x + key[i]) % 29)
        key.append(x)
    return out


def enc_running_english(p, k, mode='vig'):
    if mode == 'vig':
        return [(x + k[i]) % 29 for i, x in enumerate(p)]
    return [(k[i] - x) % 29 for i, x in enumerate(p)]


def enc_affine(p, a, b):
    return [(a * x + b) % 29 for x in p]


def fib():
    a, b = 1, 1
    while True:
        yield a
        a, b = b, a + b


def enc_plain_diff(p, seed=0):
    # c_i = p_i - p_{i-1}
    out, prev = [], seed
    for x in p:
        out.append((x - prev) % 29)
        prev = x
    return out


cands = []
cands.append(('vigenere key len 8 (random key)', enc_vig(P, [random.randrange(29) for _ in range(8)])))
cands.append(('vigenere key len 13 (random key)', enc_vig(P, [random.randrange(29) for _ in range(13)])))
cands.append(('vigenere key len 29 (random key)', enc_vig(P, [random.randrange(29) for _ in range(29)])))
cands.append(('totient stream (p_n - 1)', enc_stream(P, (q - 1 for q in primes()))))
cands.append(('prime stream (p_n)', enc_stream(P, primes())))
cands.append(('prime stream squared', enc_stream(P, (q * q for q in primes()))))
cands.append(('fibonacci stream', enc_stream(P, fib())))
cands.append(('trithemius (i)', enc_stream(P, iter(range(10 ** 6)))))
cands.append(('i^2 stream', enc_stream(P, (i * i for i in range(10 ** 6)))))
cands.append(('ciphertext autokey c=p+c_prev', enc_cipher_autokey(P)))
cands.append(('ciphertext autokey c=p-c_prev', enc_cipher_autokey_minus(P)))
cands.append(('plaintext autokey c=p+p_prev', enc_plain_autokey(P)))
cands.append(('plaintext autokey lag5', enc_plain_autokey(P, seed=[0] * 5)))
cands.append(('plain diff c=p-p_prev', enc_plain_diff(P)))
cands.append(('running key English (W&P) vig', enc_running_english(P, WP)))
cands.append(('running key English (W&P) beaufort', enc_running_english(P, WP, 'beau')))
cands.append(('running key LP plaintext itself offset 500', enc_running_english(P, P[500:] + P[:500])))
cands.append(('affine a=2 b=7 (monoalphabetic)', enc_affine(P, 2, 7)))
cands.append(('OTP random', [random.randrange(29) for _ in P]))
# doublet-avoiding chain: c_i = c_{i-1} + p_i + 1 (step never 0 when p != 28)
cands.append(('chain c=c_prev+p+1', enc_cipher_autokey([(x + 1) % 29 for x in P])))
# Vigenere but with F-interrupts like solved pages: F plaintext passes unchanged, key not consumed
def enc_vig_interrupt(p, key):
    out, k = [], 0
    for x in p:
        if x == 0:
            out.append(0)
            continue
        out.append((x + key[k % len(key)]) % 29)
        k += 1
    return out
cands.append(('vigenere len 8 with F-interrupts', enc_vig_interrupt(P, [random.randrange(29) for _ in range(8)])))
cands.append(('totient with F-interrupts', (lambda: (
    lambda out: out)([0]))()))  # placeholder replaced below
cands = [c for c in cands if c[0] != 'totient with F-interrupts']
def enc_stream_interrupt(p, ks):
    it = iter(ks)
    out = []
    for x in p:
        if x == 0:
            out.append(0)
        else:
            out.append((x + next(it)) % 29)
    return out
cands.append(('totient with F-interrupts', enc_stream_interrupt(P, (q - 1 for q in primes()))))
cands.append(('running key English with F-interrupts', (lambda: [
    (x if x == 0 else (x + WP[i]) % 29) for i, x in enumerate(P)])()))

print('%-45s %7s %6s %7s %7s' % ('encryption of LP plaintext (n=%d)' % len(P), 'dblrate', 'ioc', 'chi2', 'lag2dbl'))
print('%-45s %7.4f %6.3f %7.1f %7.4f   <== TARGET (unsolved cipher)' % ('UNSOLVED CIPHERTEXT', dbl_rate(C), lp.ioc(C), lp.chi2_uniform(C) * len(P) / len(C), sum(1 for i in range(2, len(C)) if C[i] == C[i - 2]) / (len(C) - 2)))
for name, c in cands:
    print('%-45s %7.4f %6.3f %7.1f %7.4f' % (name, dbl_rate(c), lp.ioc(c), lp.chi2_uniform(c),
                                            sum(1 for i in range(2, len(c)) if c[i] == c[i - 2]) / (len(c) - 2)))

# ---- word length distributions ----
print()
WPW = [w for w in open(os.path.join(lp.DATA, 'baseline-rune-words.txt'), encoding='utf-8').read().split() if w]
wpl = Counter(len(lp.runes_to_idx(w)) for w in WPW[:100000])
cw = Counter(len(w) for s in unsolved for w in s['words'])
pw = Counter(len(w) for s in solved for w in s['plain_words'])
tc, tp, tw = sum(cw.values()), sum(pw.values()), sum(wpl.values())
print('wordlen  cipher%  LPplain%  W&P%')
for L in range(1, 15):
    print('  %2d    %5.1f    %5.1f    %5.1f' % (L, 100 * cw.get(L, 0) / tc, 100 * pw.get(L, 0) / tp, 100 * wpl.get(L, 0) / tw))
print('mean word length: cipher %.2f  LP plain %.2f  W&P %.2f' % (
    sum(L * c for L, c in cw.items()) / tc, sum(L * c for L, c in pw.items()) / tp, sum(L * c for L, c in wpl.items()) / tw))
