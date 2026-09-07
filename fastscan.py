# -*- coding: utf-8 -*-
"""Fast running-key scan: for a candidate keystream K (ints) and a section, the index of coincidence of
(c - K[off:off+W]) mod m over EVERY offset, chunked and vectorised. Used for arbitrary key material
(archive strings, image bytes, outguess payloads). Both forms: raw (mod 29) and chain steps (mod 28)."""
import numpy as np
import lp

W_DEFAULT = 400


def chain_steps(ix, W):
    u = np.array([((ix[i] - ix[i - 1]) % 29 - 1) % 28 if ix[i] != ix[i - 1] else -1 for i in range(1, W + 1)])
    return u


def scan_stream(c, K, m, chunk=2048):
    """c: (W,) ints in Z_m (entries < 0 are masked out); K: (N,) ints. Returns (best_ioc, best_off, ioc_array)."""
    W = len(c)
    N = len(K)
    if N < W + 1:
        return 0.0, -1, None
    mask = c >= 0
    cm = c[mask]
    Wm = int(mask.sum())
    idx = np.nonzero(mask)[0]
    n_off = N - W
    out = np.empty(n_off, dtype=np.float64)
    denom = Wm * (Wm - 1) / m
    for start in range(0, n_off, chunk):
        offs = np.arange(start, min(n_off, start + chunk))
        win = K[offs[:, None] + idx[None, :]]                 # (chunk, Wm)
        M = (cm[None, :] - win) % m
        acc = np.zeros(len(offs), dtype=np.int64)
        for r in range(m):
            cnt = (M == r).sum(axis=1)
            acc += cnt * (cnt - 1)
        out[offs] = acc / denom
    j = int(out.argmax())
    return float(out[j]), j, out


def scan_material(K, name, sections, W=W_DEFAULT, signs=(1, -1), forms=('raw', 'chain')):
    """K: 1-D int array (any range). Prints and returns the best (ioc, section, form, sign, offset) per section."""
    K = np.asarray(K, dtype=np.int64)
    results = []
    for s in sections:
        ix = s['indices']
        if len(ix) < W + 1:
            Wc = len(ix) - 1
        else:
            Wc = W
        best = (0.0, None)
        for form in forms:
            if form == 'raw':
                c = np.array(ix[:Wc]); m = 29; Km = K % 29
            else:
                c = chain_steps(ix, Wc); m = 28; Km = K % 28
            for sg in signs:
                v, off, _ = scan_stream(c, sg * Km, m)
                if v > best[0]:
                    best = (v, (form, sg, off))
        results.append((s['name'], best))
        print('  %-12s %-8s best IoC=%.3f %s' % (name[:12], s['name'], best[0], best[1]))
    return results


def null_threshold(n_offsets, W=W_DEFAULT):
    """Rough max-over-offsets noise level for IoC on W-rune windows: 1 + z*sd, sd ~ 0.75/sqrt(W)."""
    import math
    z = math.sqrt(2 * math.log(max(2, n_offsets)))
    return 1 + z * 0.75 / math.sqrt(W)
