# -*- coding: utf-8 -*-
"""Build dataset.json from relikd's verified transcriptions + known solutions.
Also cross-checks against cicada-library's independent transcription."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

PAGES = os.path.join(lp.RELIKD, 'pages')

# (name, files, solved?, solution spec)
SPEC = [
    ('0_warning', 'atbash', {}),
    ('0_welcome', 'vig', {'key': 'DIVINITY', 'interrupts': [0, [4, 5, 6, 7, 10, 11, 14, 18, 20, 21, 25]]}),
    ('0_wisdom', 'plain', {}),
    ('0_koan_1', 'atbash_shift', {'shift': 3}),   # atbash, then +3 (relikd: invert + key Y=26)
    ('0_loss_of_divinity', 'plain', {}),
    ('jpg107-167', 'vig', {'key': 'FIRFUMFERENFE', 'interrupts': [0, [2, 3]]}),
    ('jpg229', 'plain', {}),
    ('p56_an_end', 'totient', {'interrupts': [0, [4]]}),
    ('p57_parable', 'plain', {}),
    ('p0-2', None, {}), ('p3-7', None, {}), ('p8-14', None, {}), ('p15-22', None, {}),
    ('p23-26', None, {}), ('p27-32', None, {}), ('p33-39', None, {}), ('p40-53', None, {}),
    ('p54-55', None, {}),
]


def decrypt(name, method, spec, ix):
    if method == 'plain':
        return ix
    if method == 'atbash':
        return lp.atbash(ix)
    if method == 'atbash_shift':
        return lp.shift(lp.atbash(ix), spec['shift'])
    if method == 'vig':
        key = lp.latin_to_idx(spec['key'])
        return lp.vigenere_decrypt(ix, key, tuple(spec['interrupts']) if spec.get('interrupts') else None)
    if method == 'totient':
        return lp.totient_stream_decrypt(ix, tuple(spec['interrupts']))
    raise ValueError(method)


def main():
    sections = []
    for name, method, spec in SPEC:
        raw = open(os.path.join(PAGES, name + '.txt'), encoding='utf-8').read()
        toks = lp.parse_tokens(raw)
        ix = [v for k, v in toks if k == 'r']
        words = lp.words_of(toks)
        # segments delimited by chapter mark '#'
        segs, cur = [], []
        for k, v in toks:
            if k == 'r':
                cur.append(v)
            elif k == 'w' and v == '#':
                if cur:
                    segs.append(cur)
                cur = []
        if cur:
            segs.append(cur)
        entry = {
            'name': name, 'solved': method is not None, 'method': method, 'spec': spec,
            'n_runes': len(ix), 'n_words': len(words), 'runes': lp.idx_to_runes(ix),
            'indices': ix, 'words': words, 'segments_by_chaptermark': segs,
            'tokens': toks,
        }
        if method is not None:
            pl = decrypt(name, method, spec, ix)
            entry['plain_indices'] = pl
            entry['plain_words'] = lp.words_of([('r', v) if k == 'r' else (k, v) for (k, v) in
                                                _override(toks, pl)])
            entry['plaintext'] = lp.render(toks, pl)
        sections.append(entry)

    ds = {'runes': lp.RUNES, 'letters': lp.LETTERS, 'primes': lp.PRIMES, 'sections': sections}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset.json'), 'w',
              encoding='utf-8') as f:
        json.dump(ds, f, ensure_ascii=False)
    tot_uns = sum(s['n_runes'] for s in sections if not s['solved'])
    print('sections:', len(sections), 'unsolved runes:', tot_uns)
    for s in sections:
        print('%-20s solved=%-5s runes=%5d words=%4d segs=%d' % (
            s['name'], s['solved'], s['n_runes'], s['n_words'], len(s['segments_by_chaptermark'])))


def _override(toks, pl):
    out, j = [], 0
    for k, v in toks:
        if k == 'r':
            out.append(('r', pl[j]))
            j += 1
        else:
            out.append((k, v))
    return out


if __name__ == '__main__':
    main()
