# -*- coding: utf-8 -*-
"""
lp.py - shared Liber Primus toolkit (Gematria Primus, ciphers, scoring, dataset).

All ciphers operate on rune INDICES 0..28 (Gematria Primus order).
Interrupt convention (as used by the community for solved pages):
  interrupts = (rune_index, {occurrence numbers, 1-based}) -> those occurrences of that
  rune in the CIPHERTEXT are passed through unchanged and do NOT consume key material.
"""
import json, math, os, sys, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = os.path.join(HERE, 'sources')          # populated by setup_sources.py
RELIKD = os.path.join(SOURCES, 'relikd_LiberPrayground')
DATA = os.path.join(RELIKD, 'data')

RUNES = 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
LETTERS = ['F', 'U', 'TH', 'O', 'R', 'C', 'G', 'W', 'H', 'N', 'I', 'J', 'EO', 'P', 'X',
           'S', 'T', 'B', 'E', 'M', 'L', 'NG', 'OE', 'D', 'A', 'AE', 'Y', 'IO', 'EA']
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
          79, 83, 89, 97, 101, 103, 107, 109]
N = 29
RUNE_TO_IDX = {r: i for i, r in enumerate(RUNES)}
# alternative spellings accepted when converting latin -> runes
LATIN_ALIASES = {'V': 'U', 'K': 'C', 'Z': 'S', 'Q': 'C', 'IA': 'IO'}
MULTI = sorted([l for l in LETTERS if len(l) > 1] + ['IA'], key=len, reverse=True)

WHITE = {'•': ' ', '⁘': '.', '⁚': ',', '⁖': ';', '⁜': '#'}


# ----------------------------------------------------------------------------
# conversions
# ----------------------------------------------------------------------------
def runes_to_idx(s):
    return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]


def idx_to_runes(ix):
    return ''.join(RUNES[i] for i in ix)


def idx_to_text(ix, sep=''):
    return sep.join(LETTERS[i] for i in ix)


def latin_to_idx(text):
    """Convert English/Runeglish text to rune indices (greedy multi-letter first).
    Non-letters are dropped. 'QU'->'CW' like the community convention."""
    out = []
    for t in re.findall(r'[A-Z]+', text.upper().replace('QU', 'CW')):
        i = 0
        while i < len(t):
            hit = None
            for m in MULTI:
                if t.startswith(m, i):
                    hit = m
                    break
            if hit is None:
                hit = t[i]
            i += len(hit)
            hit = LATIN_ALIASES.get(hit, hit)
            if hit not in LETTERS:
                raise ValueError('cannot map %r' % hit)
            out.append(LETTERS.index(hit))
    return out


def gp_sum(ix):
    return sum(PRIMES[i] for i in ix)


# ----------------------------------------------------------------------------
# page parsing (relikd notation: • space, ⁘ period, ⁚ comma, ⁖ semicolon, ⁜ chapter)
# ----------------------------------------------------------------------------
def parse_tokens(raw):
    """Return list of tokens: ('r', idx) for runes, ('w', char) for separators/others.
    Newlines are dropped (they are line wraps in the book, not word boundaries) -
    words continue across line breaks in relikd files."""
    toks = []
    for c in raw:
        if c in RUNE_TO_IDX:
            toks.append(('r', RUNE_TO_IDX[c]))
        elif c in WHITE:
            toks.append(('w', WHITE[c]))
        elif c in '\r\n':
            continue
        else:
            toks.append(('o', c))  # digits, quotes, hex, etc.
    return toks


def words_of(toks):
    """Split token stream into words (lists of rune idx). Any 'w' token ends a word."""
    words, cur = [], []
    for k, v in toks:
        if k == 'r':
            cur.append(v)
        else:
            if cur:
                words.append(cur)
                cur = []
    if cur:
        words.append(cur)
    return words


def render(toks, ix_override=None):
    """Render tokens to Runeglish; ix_override replaces rune indices in order."""
    out = []
    j = 0
    for k, v in toks:
        if k == 'r':
            i = ix_override[j] if ix_override is not None else v
            j += 1
            out.append(LETTERS[i])
        else:
            out.append(v)
    return ''.join(out)


# ----------------------------------------------------------------------------
# ciphers (decrypt direction unless stated). ix = ciphertext indices
# ----------------------------------------------------------------------------
def _skip_set(ix, interrupts):
    """Return set of positions (in ix) that are interrupt pass-throughs."""
    if not interrupts:
        return set()
    r, occ = interrupts
    occ = set(occ)
    skip = set()
    n = 0
    for p, v in enumerate(ix):
        if v == r:
            n += 1
            if n in occ:
                skip.add(p)
    return skip


def running_key_decrypt(ix, keystream, interrupts=None, mode='vig'):
    """keystream: iterable of ints (consumed only on non-skipped runes).
    mode: 'vig'  p = c - k
          'beau' p = k - c   (Beaufort)
          'add'  p = c + k   (variant / encrypt-direction)"""
    skip = _skip_set(ix, interrupts)
    it = iter(keystream)
    out = []
    for p, c in enumerate(ix):
        if p in skip:
            out.append(c)
            continue
        k = next(it)
        if mode == 'vig':
            out.append((c - k) % N)
        elif mode == 'beau':
            out.append((k - c) % N)
        elif mode == 'add':
            out.append((c + k) % N)
        else:
            raise ValueError(mode)
    return out


def vigenere_decrypt(ix, key, interrupts=None, mode='vig'):
    def ks():
        while True:
            for k in key:
                yield k
    return running_key_decrypt(ix, ks(), interrupts, mode)


def atbash(ix):
    return [(N - 1 - i) for i in ix]


def shift(ix, n):
    return [(i + n) % N for i in ix]


def prime_gen():
    D = {}
    q = 2
    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1


def totient_stream_decrypt(ix, interrupts=None, offset=0):
    """Page-56 cipher: p_i = c_i - (prime_i - 1)  (phi of nth prime)."""
    def ks():
        g = prime_gen()
        for _ in range(offset):
            next(g)
        for p in g:
            yield p - 1
    return running_key_decrypt(ix, ks(), interrupts, 'vig')


def autokey_decrypt(ix, seed, interrupts=None, variant='plain'):
    """Autokey. variant 'plain': key = seed + plaintext ; 'cipher': key = seed + ciphertext."""
    skip = _skip_set(ix, interrupts)
    key = list(seed)
    out = []
    kpos = 0
    for p, c in enumerate(ix):
        if p in skip:
            out.append(c)
            continue
        k = key[kpos]
        kpos += 1
        pl = (c - k) % N
        out.append(pl)
        key.append(pl if variant == 'plain' else c)
    return out


# ----------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------
def ioc(ix):
    n = len(ix)
    if n < 2:
        return 0.0
    c = Counter(ix)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1) / N)


def periodic_ioc(ix, period):
    vals = [ioc(ix[k::period]) for k in range(period)]
    return sum(vals) / len(vals)


def doublets(ix):
    return sum(1 for a, b in zip(ix, ix[1:]) if a == b)


def chi2_uniform(ix):
    n = len(ix)
    e = n / N
    c = Counter(ix)
    return sum((c.get(i, 0) - e) ** 2 / e for i in range(N))


# ----------------------------------------------------------------------------
# language model scoring (rune-level n-grams from War & Peace transliterated)
# ----------------------------------------------------------------------------
_NG = {}


def load_ngrams(n, prefix=''):
    key = (n, prefix)
    if key in _NG:
        return _NG[key]
    d = {}
    fn = os.path.join(DATA, 'p%s-%dgram.txt' % (prefix, n))
    with open(fn, encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                d[tuple(RUNE_TO_IDX[c] for c in parts[0])] = int(parts[1])
    _NG[key] = d
    return d


class Scorer:
    """Log10 probability per rune with stupid backoff over 4/3/2/1-grams."""

    def __init__(self, prefix=''):
        self.g = {n: load_ngrams(n, prefix) for n in (1, 2, 3, 4)}
        self.tot = {n: sum(self.g[n].values()) for n in (1, 2, 3, 4)}
        self.floor = math.log10(0.4 / self.tot[1])

    def lp(self, gram):
        n = len(gram)
        g = self.g[n]
        if gram in g:
            if n == 1:
                return math.log10(g[gram] / self.tot[1])
            ctx = self.g[n - 1].get(gram[:-1], 0)
            if ctx > 0:
                return math.log10(g[gram] / ctx)
        if n == 1:
            return self.floor
        return math.log10(0.4) + self.lp(gram[1:])

    def score(self, ix):
        """average log10 prob per rune (higher = more English-like). ~-1.0 for English,
        ~-1.9 for random."""
        if not ix:
            return -9.0
        t = tuple(ix)
        s = 0.0
        for i in range(len(t)):
            g = t[max(0, i - 3):i + 1]
            s += self.lp(g)
        return s / len(t)


_DICT = None


def load_dictionary():
    global _DICT
    if _DICT is None:
        d = set()
        with open(os.path.join(DATA, 'dictionary_all-rune.txt'), encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w:
                    d.add(tuple(RUNE_TO_IDX[c] for c in w if c in RUNE_TO_IDX))
        # add words from solved pages (Runeglish spellings)
        try:
            ds = load_dataset()
            for s in ds['sections']:
                if s['solved'] and s.get('plain_words'):
                    for w in s['plain_words']:
                        d.add(tuple(w))
        except Exception:
            pass
        _DICT = d
    return _DICT


_EXT = None


def load_external_dictionary():
    global _EXT
    if _EXT is None:
        d = set()
        with open(os.path.join(DATA, 'dictionary_all-rune.txt'), encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w:
                    d.add(tuple(RUNE_TO_IDX[c] for c in w if c in RUNE_TO_IDX))
        _EXT = d
    return _EXT


def word_hit_rate(words, external_only=False):
    """fraction of words (lists of idx) found in dictionary; words of len>=2 only."""
    d = load_external_dictionary() if external_only else load_dictionary()
    ws = [tuple(w) for w in words if len(w) >= 2]
    if not ws:
        return 0.0
    return sum(1 for w in ws if w in d) / len(ws)


# ----------------------------------------------------------------------------
# dataset
# ----------------------------------------------------------------------------
_DS = None


def load_dataset():
    global _DS
    if _DS is None:
        with open(os.path.join(HERE, 'dataset.json'), encoding='utf-8') as f:
            _DS = json.load(f)
    return _DS


def section(name):
    for s in load_dataset()['sections']:
        if s['name'] == name:
            return s
    raise KeyError(name)


def unsolved_sections():
    return [s for s in load_dataset()['sections'] if not s['solved']]


if __name__ == '__main__':
    sc = Scorer()
    eng = latin_to_idx('WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS')
    import random
    rnd = [random.randrange(29) for _ in range(len(eng))]
    print('english score', sc.score(eng))
    print('random  score', sc.score(rnd))
    print(idx_to_text(eng, ' '))
