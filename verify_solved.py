# -*- coding: utf-8 -*-
"""Gate: the toolkit must reproduce every known Liber Primus solution."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp

EXPECT = {
    '0_warning': 'A WARNNG#BELIEUE NOTHNG FROM THIS BOOC.EXCEPT WHAT YOU CNOW TO BE TRUE.',
    '0_welcome': 'WELCOME#WELCOME,PILGRIM,TO THE GREAT JOURNEY TOWARD THE END OF ALL THNGS.',
    '0_wisdom': 'SOME WISDOM#THE PRIMES ARE SACRED.THE TOTIENT FUNCTIAN IS SACRED.',
    '0_koan_1': 'A COAN#A MAN DECIDED TO GO AND STUDY WITH A MASTER.',
    '0_loss_of_divinity': 'THE LOSS OF DIUINITY.THE CIRCUMFERENCE PRACTICES THREE BEHAUIORS WHICH CAUSE THE LOSS OF DIUINITY.',
    'jpg107-167': 'A COAN#DURNG A LESSON,THE MASTER EXPLAINED THE I.',
    'jpg229': 'AN INSTRUCTIAN#CWESTION ALL THNGS.',
    'p56_an_end': 'AN END#WITHIN THE DEEP WEB,THERE EXISTS A PAGE THAT HASHES TO#',
    'p57_parable': 'PARABLE#LICE THE INSTAR TUNNELNG TO THE SURFACE.',
}

ok = True
for s in lp.load_dataset()['sections']:
    if not s['solved']:
        continue
    pt = s['plaintext']
    exp = EXPECT[s['name']]
    e_ix = lp.latin_to_idx(exp)
    hit = s['plain_indices'][:len(e_ix)] == e_ix
    ok &= hit
    print('%-20s %s' % (s['name'], 'OK ' if hit else 'FAIL'), '|', pt[:110].replace('\n', ' '))
    if not hit:
        print('   expected:', exp)
sc = lp.Scorer()
print()
print('scores (avg log10 per rune): higher = more English-like')
for s in lp.load_dataset()['sections']:
    ix = s['plain_indices'] if s['solved'] else s['indices']
    print('%-20s solved=%-5s score=%.3f  ioc=%.3f  words_in_dict=%.2f' % (
        s['name'], s['solved'], sc.score(ix), lp.ioc(ix),
        lp.word_hit_rate(s['plain_words'] if s['solved'] else s['words'], external_only=True)))
print()
print('GATE', 'PASSED' if ok else 'FAILED')
sys.exit(0 if ok else 1)
