# -*- coding: utf-8 -*-
"""Unit checks for the shared library: the Gematria Primus table, the transliteration, and the
index-of-coincidence statistics every exclusion is judged by. Offline; no sources/ needed.
Run: python -m unittest test_lp"""
import math, os, sys, unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
import fastscan

# The Gematria Primus as printed in the Liber Primus (rune, transliteration, prime).
GEMATRIA = [
    ('ᚠ', 'F', 2), ('ᚢ', 'U', 3), ('ᚦ', 'TH', 5), ('ᚩ', 'O', 7), ('ᚱ', 'R', 11), ('ᚳ', 'C', 13),
    ('ᚷ', 'G', 17), ('ᚹ', 'W', 19), ('ᚻ', 'H', 23), ('ᚾ', 'N', 29), ('ᛁ', 'I', 31), ('ᛄ', 'J', 37),
    ('ᛇ', 'EO', 41), ('ᛈ', 'P', 43), ('ᛉ', 'X', 47), ('ᛋ', 'S', 53), ('ᛏ', 'T', 59), ('ᛒ', 'B', 61),
    ('ᛖ', 'E', 67), ('ᛗ', 'M', 71), ('ᛚ', 'L', 73), ('ᛝ', 'NG', 79), ('ᛟ', 'OE', 83), ('ᛞ', 'D', 89),
    ('ᚪ', 'A', 97), ('ᚫ', 'AE', 101), ('ᚣ', 'Y', 103), ('ᛡ', 'IO', 107), ('ᛠ', 'EA', 109),
]


class TestGematriaPrimus(unittest.TestCase):
    def test_table(self):
        self.assertEqual(lp.N, 29)
        self.assertEqual(list(lp.RUNES), [g[0] for g in GEMATRIA])
        self.assertEqual(lp.LETTERS, [g[1] for g in GEMATRIA])
        self.assertEqual(lp.PRIMES, [g[2] for g in GEMATRIA])

    def test_primes_are_the_first_29(self):
        g = lp.prime_gen()
        self.assertEqual(lp.PRIMES, [next(g) for _ in range(29)])

    def test_digraphs_take_one_rune(self):
        for word, want in (('THE', ['TH', 'E']), ('EOH', ['EO', 'H']), ('KING', ['C', 'I', 'NG']),
                           ('OEAE', ['OE', 'AE']), ('IA', ['IO']), ('IO', ['IO']), ('EAT', ['EA', 'T']),
                           ('QUEST', ['C', 'W', 'E', 'S', 'T']), ('VZ', ['U', 'S'])):
            self.assertEqual(lp.idx_to_text(lp.latin_to_idx(word), ' ').split(), want, word)

    def test_rune_round_trip(self):
        ix = list(range(29))
        self.assertEqual(lp.runes_to_idx(lp.idx_to_runes(ix)), ix)
        self.assertEqual(lp.gp_sum(ix), sum(lp.PRIMES))


class TestIndexOfCoincidence(unittest.TestCase):
    def test_normalised_by_n_n_minus_1_over_29(self):
        # counts 2 and 2 out of 4: sum c(c-1) = 4, n(n-1)/29 = 12/29
        self.assertAlmostEqual(lp.ioc([0, 0, 1, 1]), 4 * 29 / 12)
        self.assertEqual(lp.ioc([5]), 0.0)
        self.assertEqual(lp.ioc(list(range(29))), 0.0)

    def test_uniform_text_has_ioc_one(self):
        rng = np.random.default_rng(1)
        vals = [lp.ioc(list(rng.integers(0, 29, 400))) for _ in range(4000)]
        self.assertAlmostEqual(float(np.mean(vals)), 1.0, delta=0.002)

    def test_null_sd_matches_simulation(self):
        """The spread of the IoC of uniform text is sqrt(2*28)/(n-1): it shrinks like 1/n. The
        0.75/sqrt(n) rule the scans used agrees only near n = 100."""
        rng = np.random.default_rng(2)
        for n in (100, 400, 1200):
            x = rng.integers(0, 29, size=(20000, n))
            cnt = np.stack([(x == r).sum(axis=1) for r in range(29)], axis=1)
            vals = (cnt * (cnt - 1)).sum(axis=1) / (n * (n - 1) / 29)
            self.assertAlmostEqual(float(vals.std()) / lp.ioc_null_sd(n), 1.0, delta=0.05, msg=n)

    def test_scan_noise_ceiling_matches_simulation(self):
        """fastscan.null_threshold(k, W) is the IoC one of k random W-rune alignments reaches by
        chance. Checked against the median, over repeats, of the maximum of k uniform windows."""
        rng = np.random.default_rng(3)
        W, k = 400, 5000
        maxima = []
        for _ in range(15):
            x = rng.integers(0, 29, size=(k, W))
            cnt = np.stack([(x == r).sum(axis=1) for r in range(29)], axis=1)
            maxima.append(((cnt * (cnt - 1)).sum(axis=1) / (W * (W - 1) / 29)).max())
        self.assertAlmostEqual(fastscan.null_threshold(k, W), float(np.median(maxima)), delta=0.02)


if __name__ == '__main__':
    unittest.main()
