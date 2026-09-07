# -*- coding: utf-8 -*-
"""Sequence-key attacks:
 (a) chain model: u_i = (c_i - c_{i-1} - 1) mod 28 (28-ary increments), p = u -/+ k_i (mod 28)
 (b) raw model:   p = c_i -/+ k_i (mod 29)
for many integer sequences, offsets 0..199, both signs; score by IoC of output (28- or 29-ary).
Also: which plaintext letter has ~0.66% frequency (doublet-as-letter hypothesis)."""
import os, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import numpy as np

ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]
P = [i for s in solved for i in s['plain_indices']]
cnt = Counter(P)
print('LP plaintext letter frequencies (n=%d):' % len(P))
print('  ', ' '.join('%s:%.4f' % (lp.LETTERS[i], cnt.get(i, 0) / len(P)) for i in range(29)))
print('  target doublet rate 0.0066 +- 0.0007 -> candidates:',
      [lp.LETTERS[i] for i in range(29) if 0.004 < cnt.get(i, 0) / len(P) < 0.010])
print()

# ---------------- sequences ----------------
LIMIT = 4000
def primes_list(n):
    g = lp.prime_gen()
    return [next(g) for _ in range(n)]
PR = primes_list(LIMIT + 300)
def fib(n):
    a, b, out = 1, 1, []
    for _ in range(n):
        out.append(a)
        a, b = b, a + b
    return out
def lucas(n):
    a, b, out = 2, 1, []
    for _ in range(n):
        out.append(a)
        a, b = b, a + b
    return out
def totient(n):
    out = [0] * (n + 1)
    for i in range(n + 1):
        out[i] = i
    for i in range(2, n + 1):
        if out[i] == i:
            for j in range(i, n + 1, i):
                out[j] -= out[j] // i
    return out
TOT = totient(LIMIT + 300)
def digits(s):
    return [int(c) for c in s if c.isdigit()]
PI = digits(open(os.path.join(os.path.dirname(__file__), 'pi.txt')).read()) if os.path.exists(os.path.join(os.path.dirname(__file__), 'pi.txt')) else []

SEQS = {
    'n': list(range(LIMIT + 300)),
    'n+1': list(range(1, LIMIT + 301)),
    'n^2': [i * i for i in range(LIMIT + 300)],
    'n^3': [i ** 3 for i in range(LIMIT + 300)],
    'tri': [i * (i + 1) // 2 for i in range(LIMIT + 300)],
    'prime': PR,
    'prime-1': [p - 1 for p in PR],
    'prime+1': [p + 1 for p in PR],
    '2*prime': [2 * p for p in PR],
    'prime^2': [p * p for p in PR],
    'prime_gap': [PR[i + 1] - PR[i] for i in range(len(PR) - 1)],
    'prime_cumsum': list(np.cumsum(PR)),
    'fib': fib(LIMIT + 300),
    'lucas': lucas(LIMIT + 300),
    'phi(n)': TOT,
    'phi(prime_n)=prime-1 dup': [p - 1 for p in PR],
    '2^n': [pow(2, i, 29 * 28) for i in range(LIMIT + 300)],
    '3^n': [pow(3, i, 29 * 28) for i in range(LIMIT + 300)],
    '3301*n': [3301 * i for i in range(LIMIT + 300)],
    'n*29+...': [i * 29 for i in range(LIMIT + 300)],
    'prime_index_of_prime': [PR[p] for p in range(500)],  # p_{p_n}
    'catalan': [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, 58786, 208012, 742900, 2674440, 9694845, 35357670] * 200,
    'factorial': [math.factorial(i) % (29 * 28) for i in range(LIMIT + 300)],
    'pi_digits': PI,
}
SEQS = {k: v for k, v in SEQS.items() if len(v) > 400}


def attack(stream_fn, mod, name):
    """stream_fn(section) -> list of ints in Z_mod (the 'ciphertext' to decrypt)."""
    print('=== %s (mod %d) ===' % (name, mod))
    results = []
    for s in unsolved:
        x = np.array(stream_fn(s))
        n = len(x)
        best = (0, None, None, None)
        for sname, seq in SEQS.items():
            seq = np.array([int(v) % mod for v in seq[:n + 200]], dtype=np.int64)
            if len(seq) < n + 200:
                continue
            for off in range(0, 200):
                k = seq[off:off + n]
                for sign in (1, -1):
                    out = (x - sign * k) % mod
                    v = lp.ioc(out.tolist()) * (29 / mod) if mod != 29 else lp.ioc(out.tolist())
                    # normalise: ioc computed with N=29 inside lp; rescale so random ~1.0
                    if v > best[0]:
                        best = (v, sname, off, sign)
        results.append((s['name'], best))
        print('  %-8s best ioc=%.3f seq=%s off=%s sign=%s' % (s['name'], best[0], best[1], best[2], best[3]))
    return results


def ioc_mod(x, mod):
    n = len(x)
    c = Counter(x)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1) / mod)


# monkeypatch lp.ioc for mod-28 correctness inside attack: we compute properly here instead
def attack2(stream_fn, mod, name):
    print('=== %s (mod %d) ===' % (name, mod))
    for s in unsolved:
        x = np.array(stream_fn(s))
        n = len(x)
        best = (0, None, None, None)
        cands = []
        for sname, seq in SEQS.items():
            seq = np.array([int(v) % mod for v in seq[:n + 200]], dtype=np.int64)
            if len(seq) < n + 200:
                continue
            for off in range(0, 200):
                k = seq[off:off + n]
                for sign in (1, -1):
                    out = (x - sign * k) % mod
                    v = ioc_mod(out.tolist(), mod)
                    cands.append((v, sname, off, sign))
        cands.sort(reverse=True)
        print('  %-8s n=%d top: %s' % (s['name'], n, ' | '.join('%.3f %s@%d%s' % (v, sn, o, '+' if sg > 0 else '-') for v, sn, o, sg in cands[:3])))


def chain_u(s):
    ix = s['indices']
    return [((ix[i] - ix[i - 1]) % 29 - 1) % 28 for i in range(1, len(ix)) if ix[i] != ix[i - 1]]


def chain_u_neg(s):  # backwards ring
    ix = s['indices']
    return [((ix[i - 1] - ix[i]) % 29 - 1) % 28 for i in range(1, len(ix)) if ix[i] != ix[i - 1]]


def raw(s):
    return s['indices']


def raw_atbash(s):
    return [28 - i for i in s['indices']]


attack2(chain_u, 28, 'chain increments u=(Δc-1) mod 28, sequence key')
attack2(chain_u_neg, 28, 'chain increments backwards, sequence key')
attack2(chain_u, 29, 'chain increments as 29-ary (Δc), sequence key mod 29')
attack2(raw, 29, 'raw ciphertext, sequence key mod 29 (community-style)')
attack2(raw_atbash, 29, 'atbash ciphertext, sequence key mod 29')

# running key over Z28 using LP plaintext (letters 0..27, EA->0) on chain increments
print('=== chain increments, running key = LP solved plaintext mod 28 ===')
K = np.array([p % 28 for p in P])
for s in unsolved:
    x = np.array(chain_u(s))
    n = min(len(x), 400)
    x = x[:n]
    best = (0, None, None)
    for off in range(0, len(K) - n):
        k = K[off:off + n]
        for sign in (1, -1):
            v = ioc_mod(((x - sign * k) % 28).tolist(), 28)
            if v > best[0]:
                best = (v, off, sign)
    print('  %-8s best ioc=%.3f off=%s sign=%s' % (s['name'], *best))
