# -*- coding: utf-8 -*-
"""Statistical characterization of every unsolved section (and chapter-mark segment).
Writes stats.json and prints a human summary."""
import json, math, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

ds = lp.load_dataset()
solved = [s for s in ds['sections'] if s['solved']]
unsolved = [s for s in ds['sections'] if not s['solved']]

# ---- reference plaintext stats from solved pages (Runeglish) ----
plain_all = [i for s in solved for i in s['plain_indices']]
plain_words = [w for s in solved for w in s['plain_words']]
ref_uni = Counter(plain_all)
ref_doublet_rate = lp.doublets(plain_all) / (len(plain_all) - 1)
ref_wordlen = Counter(len(w) for w in plain_words)
ref_first = Counter(w[0] for w in plain_words)
ref_ioc = lp.ioc(plain_all)

# ---- ciphertext across all unsolved ----
cipher_all = [i for s in unsolved for i in s['indices']]
cipher_words = [w for s in unsolved for w in s['words']]


def top_periods(ix, maxp=120, k=12):
    vals = [(p, lp.periodic_ioc(ix, p)) for p in range(1, min(maxp, len(ix) // 4) + 1)]
    vals.sort(key=lambda x: -x[1])
    return vals[:k]


def kasiski(ix, n=4, minrep=2):
    pos = defaultdict(list)
    for i in range(len(ix) - n + 1):
        pos[tuple(ix[i:i + n])].append(i)
    reps = {g: p for g, p in pos.items() if len(p) >= minrep}
    dist = Counter()
    for g, p in reps.items():
        for a, b in zip(p, p[1:]):
            dist[b - a] += 1
    # factor counts
    fac = Counter()
    for d, c in dist.items():
        for f in range(2, 80):
            if d % f == 0:
                fac[f] += c
    return len(reps), sorted(reps.items(), key=lambda x: -len(x[1]))[:8], fac.most_common(12)


def autocorr(ix, maxlag=60):
    out = []
    n = len(ix)
    for lag in range(1, maxlag + 1):
        m = sum(1 for i in range(n - lag) if ix[i] == ix[i + lag])
        out.append((lag, m / (n - lag)))
    return out


def kappa(a, b):
    """coincidence rate between two aligned streams (expected 1/29=0.0345 if independent)."""
    n = min(len(a), len(b))
    if n == 0:
        return 0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def diff_ioc(a, b):
    n = min(len(a), len(b))
    return lp.ioc([(a[i] - b[i]) % 29 for i in range(n)]) if n > 30 else None


stats = {'reference': {
    'plain_ioc': ref_ioc, 'plain_doublet_rate': ref_doublet_rate,
    'plain_unigram': {lp.LETTERS[i]: c / len(plain_all) for i, c in sorted(ref_uni.items())},
    'plain_wordlen': dict(sorted(ref_wordlen.items())),
    'plain_first_letter': {lp.LETTERS[i]: c / len(plain_words) for i, c in ref_first.most_common()},
    'n_plain_runes': len(plain_all),
}, 'sections': []}

print('REFERENCE (solved plaintext): ioc=%.3f doublet_rate=%.4f  n=%d' % (ref_ioc, ref_doublet_rate, len(plain_all)))
print('ALL CIPHER: ioc=%.3f doublet_rate=%.4f n=%d  expected random doublet rate=%.4f' % (
    lp.ioc(cipher_all), lp.doublets(cipher_all) / (len(cipher_all) - 1), len(cipher_all), 1 / 29))
print()

for s in unsolved:
    ix = s['indices']
    n = len(ix)
    uni = Counter(ix)
    chi = lp.chi2_uniform(ix)
    dbl = lp.doublets(ix)
    exp_dbl = (n - 1) / 29
    tp = top_periods(ix)
    nrep, reps, fac = kasiski(ix)
    ac = autocorr(ix)
    ac_top = sorted(ac, key=lambda x: -x[1])[:6]
    wl = Counter(len(w) for w in s['words'])
    first = Counter(w[0] for w in s['words'])
    # doublets within words only
    dbl_w = sum(lp.doublets(w) for w in s['words'])
    n_w_pairs = sum(len(w) - 1 for w in s['words'])
    # segments
    seg_stats = []
    for j, seg in enumerate(s['segments_by_chaptermark']):
        seg_stats.append({'idx': j, 'n': len(seg), 'ioc': lp.ioc(seg), 'doublets': lp.doublets(seg),
                          'exp_doublets': (len(seg) - 1) / 29})
    entry = {
        'name': s['name'], 'n': n, 'ioc': lp.ioc(ix), 'chi2_uniform': chi, 'chi2_df': 28,
        'doublets': dbl, 'expected_doublets_random': exp_dbl,
        'doublets_within_words': dbl_w, 'expected_within_words_random': n_w_pairs / 29,
        'unigram_counts': {lp.LETTERS[i]: uni.get(i, 0) for i in range(29)},
        'top_periodic_ioc': tp, 'kasiski_4gram_repeats': nrep,
        'kasiski_top_repeats': [(lp.idx_to_text(g), p) for g, p in reps],
        'kasiski_factor_counts': fac, 'autocorr_top': ac_top,
        'wordlen': dict(sorted(wl.items())),
        'first_letter_top': [(lp.LETTERS[i], c) for i, c in first.most_common(8)],
        'segments': seg_stats,
    }
    stats['sections'].append(entry)
    print('== %s  n=%d words=%d' % (s['name'], n, len(s['words'])))
    print('   ioc=%.3f chi2(uniform,df28)=%.1f doublets=%d (random exp %.1f; english-rate exp %.1f) within-word dbl=%d (exp %.1f)' % (
        entry['ioc'], chi, dbl, exp_dbl, ref_doublet_rate * (n - 1), dbl_w, n_w_pairs / 29))
    print('   top periodic IoC:', ' '.join('%d:%.2f' % (p, v) for p, v in tp[:8]))
    print('   kasiski 4-gram repeats=%d top=%s' % (nrep, entry['kasiski_top_repeats'][:4]))
    print('   kasiski factors:', fac[:8])
    print('   autocorr top:', ' '.join('%d:%.3f' % (l, v) for l, v in ac_top))
    print('   least/most frequent:', sorted(entry['unigram_counts'].items(), key=lambda x: x[1])[:4],
          sorted(entry['unigram_counts'].items(), key=lambda x: -x[1])[:4])
    print('   segments:', [(x['n'], round(x['ioc'], 2), x['doublets']) for x in seg_stats])

# ---- cross-section tests: same keystream? ----
print()
print('CROSS-SECTION kappa (aligned from start; independent ~0.0345) and diff-IoC (independent ~1.0):')
names = [s['name'] for s in unsolved]
cross = {}
for i, a in enumerate(unsolved):
    for b in unsolved[i + 1:]:
        k = kappa(a['indices'], b['indices'])
        d = diff_ioc(a['indices'], b['indices'])
        cross['%s|%s' % (a['name'], b['name'])] = (k, d)
        flag = ' <==' if k > 0.05 or (d and d > 1.15) else ''
        print('   %-8s %-8s kappa=%.4f diffioc=%s%s' % (a['name'], b['name'], k, ('%.3f' % d) if d else '-', flag))
stats['cross_section'] = cross

# ---- self-kappa at shifts (periodicity of key incl. long periods) for concatenated cipher ----
print()
print('Whole-corpus autocorrelation peaks (lags 1..400):')
allc = cipher_all
peaks = []
for lag in range(1, 401):
    m = sum(1 for i in range(len(allc) - lag) if allc[i] == allc[i + lag]) / (len(allc) - lag)
    peaks.append((lag, m))
peaks.sort(key=lambda x: -x[1])
print('   ', ' '.join('%d:%.4f' % (l, v) for l, v in peaks[:15]))
stats['corpus_autocorr_top'] = peaks[:30]

# ---- the repeated long n-grams across the whole unsolved corpus ----
print()
for n in (5, 6, 7):
    pos = defaultdict(list)
    for i in range(len(allc) - n + 1):
        pos[tuple(allc[i:i + n])].append(i)
    reps = [(lp.idx_to_text(g), p) for g, p in pos.items() if len(p) >= 2]
    print('corpus repeated %d-grams: %d ->' % (n, len(reps)), reps[:10])
    stats['corpus_repeated_%dgram' % n] = reps

# ---- word-level: identical cipher words repeated (would indicate short/periodic key or plain) ----
wc = Counter(tuple(w) for w in cipher_words if len(w) >= 3)
rep_words = [(lp.idx_to_text(w), c) for w, c in wc.most_common(15) if c > 1]
print('repeated cipher words (len>=3):', rep_words)
stats['repeated_cipher_words'] = rep_words

# ---- word length distributions compare ----
print()
tot_c = len(cipher_words)
tot_p = len(plain_words)
print('wordlen  cipher%%  plain%%')
cw = Counter(len(w) for w in cipher_words)
for L in range(1, 16):
    print('  %2d    %5.1f    %5.1f' % (L, 100 * cw.get(L, 0) / tot_c, 100 * ref_wordlen.get(L, 0) / tot_p))
stats['wordlen_cipher'] = dict(sorted(cw.items()))

# ---- per-position-in-word rune distribution vs plaintext (transposition test) ----
cu = Counter(cipher_all)
print()
print('unigram cipher vs plain (sorted by plain freq):')
for i, c in ref_uni.most_common():
    print('  %-3s plain %.3f  cipher %.3f' % (lp.LETTERS[i], c / len(plain_all), cu.get(i, 0) / len(cipher_all)))

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=1, default=str)
print('\nwrote stats.json')
