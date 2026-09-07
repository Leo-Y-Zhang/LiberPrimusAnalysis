# LiberPrimusAnalysis

Cryptanalysis of the unsolved pages of Cicada 3301's *Liber Primus* (2014), done in one
session on 6-7 September 2026. The book was **not solved**. What the repository holds is a
reproducible toolkit, the nine known solutions re-derived from a verified transcription, a
precise statistical fingerprint of the unsolved cipher, and an exclusion ledger in which every
negative result carries a positive control.

The findings are written up in **[docs/REPORT.md](docs/REPORT.md)**. The raw state of knowledge,
with every number, is in [docs/FINDINGS.md](docs/FINDINGS.md); the test outputs quoted there are
under [results/](results/).

## The result in three sentences

The 12,956 unsolved runes are statistically flat at every order except one: adjacent identical
runes occur 86 times where 447 are expected (0.66 % against 3.45 %, z = -17), the step between
consecutive runes is uniform on 1..28 and independent of the rune before it, and there is no
periodicity, no Kasiski signal and no keystream shared between sections. Encrypting the *known*
plaintext with every standard family shows that any cipher adding a ciphertext-independent key
gives about 3.4 % doublets on English; only a chain cipher (each rune is the previous rune plus a
non-zero step drawn from a flat, aperiodic 28-symbol keystream) reproduces the fingerprint.
Every public key source and key family tested (periodic keys with and without the F-interrupt and
key-skip rules Cicada used, 46 integer sequences in raw and chain form, autokeys, prime-value
feedback, running keys from Cicada-linked texts, shared keys between sections, digraphic ciphers)
is excluded with a detector whose power was proven on synthetic ciphertext first.

The key-source hunt that followed is in [outguess/RESULTS.md](outguess/RESULTS.md): outguess over
all 75 page images (no key and 96 keys) recovers every known 2014 payload and nothing else, the
page-56 SHA-512 matches none of 697,000 archive candidates, and the archive's long strings and the
page images themselves are not the keystream.

## Reproduce

Python 3.13 with numpy, scipy, sympy, mpmath and pillow. Set `PYTHONIOENCODING=utf-8` (runes in
output).

```
python setup_sources.py            # clones the community transcriptions and n-gram tables into sources/
python build_dataset.py            # dataset.json: all 18 sections, words, segments, known plaintexts
python verify_solved.py            # GATE: the nine known solutions must reproduce
python crosscheck_transcription.py # GATE: two independent transcriptions agree on every unsolved rune
python characterize.py             # statistics of the unsolved sections (results/characterize.txt)
python fingerprint.py              # doublet rate of each cipher family on the real plaintext
python controls.py                 # positive controls for every detector used
python tests2.py ... tests5.py     # the attack families (outputs under results/)
python lag_and_parity_tests.py     # coincidence-at-lag and doublet-parity tests
python crop_doublets.py            # crops every doublet site from the page images into crops/
```

`lp.py` is the shared library: the 29-rune Gematria Primus, the community's interrupt convention,
the ciphers (Vigenère, Beaufort, running key, atbash, totient stream, autokey), the statistics, an
n-gram language model over English transliterated into runes, and the dataset loader.

## Sources, and what is not here

The transcriptions, page images, n-gram tables and dictionaries come from
[relikd/LiberPrayground](https://github.com/relikd/LiberPrayground) and
[cicada-solvers/cicada-library](https://github.com/cicada-solvers/cicada-library). They are fetched
by `setup_sources.py` and are not redistributed in this repository; `dataset.json` is generated from
them. The puzzle history used for context is
[scream314/cicada3301](https://github.com/scream314/cicada3301) and the 2012-2017 archive
[krisyotam/cicada3301](https://github.com/krisyotam/cicada3301) (optional, `--archive`). The
community's own statistics are on the Uncovering Cicada wiki ("Frequency Analysis Unsolved Pages",
"Liber Primus Ideas and Suggestions"), which independently reports the same 86 doublets.

The continuous-integration gate re-fetches the sources and re-runs `verify_solved.py` and
`crosscheck_transcription.py` on every push, and scans the history with gitleaks.

## Licence

Proprietary source-available: read it, run it, check it, publish what you find. See
[LICENSE](LICENSE).
