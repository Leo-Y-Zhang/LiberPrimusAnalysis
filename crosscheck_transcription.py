# -*- coding: utf-8 -*-
"""Gate: the two independent community transcriptions must agree on every unsolved rune."""
import difflib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

lib_path = os.path.join(lp.SOURCES, 'cicada-solvers_cicada-library', 'cicada', 'liber_primus.txt')
lib = lp.runes_to_idx(open(lib_path, encoding='utf-8').read())
order = ['0_warning', '0_welcome', '0_wisdom', '0_koan_1', '0_loss_of_divinity', 'jpg107-167', 'jpg229',
         'p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26', 'p27-32', 'p33-39', 'p40-53', 'p54-55', 'p56_an_end', 'p57_parable']
rel = []
bounds = {}
for n in order:
    s = lp.section(n)
    bounds[n] = (len(rel), len(rel) + s['n_runes'], s['solved'])
    rel += s['indices']
a, b = lp.idx_to_runes(rel), lp.idx_to_runes(lib)
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
ops = [op for op in sm.get_opcodes() if op[0] != 'equal']
print('relikd runes %d, cicada-library runes %d, differing regions %d' % (len(a), len(b), len(ops)))
bad = 0
for tag, i1, i2, j1, j2 in ops:
    where = [n for n, (lo, hi, solved) in bounds.items() if lo <= i1 < hi]
    solved = bounds[where[0]][2] if where else None
    print('  %s at %d-%d (%s, %s): %r -> %r' % (tag, i1, i2, where, 'solved' if solved else 'UNSOLVED',
                                                a[max(0, i1 - 4):i2 + 4], b[max(0, j1 - 4):j2 + 4]))
    if not solved:
        bad += 1
print('GATE', 'PASSED' if bad == 0 else 'FAILED', '(differences on unsolved pages: %d)' % bad)
sys.exit(0 if bad == 0 else 1)
