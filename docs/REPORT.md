# The unsolved pages carry one fingerprint, and it rules out every public key

*Cicada 3301, Liber Primus. Session report, 6-7 September 2026.*

All nine known solutions of the Liber Primus were reproduced from a verified transcription. The
remaining 12,956 runes were then measured, modelled, and attacked with detectors whose power was
proven on synthetic ciphertexts first. No page was decrypted. What did emerge is a precise
statistical description of the cipher that is consistent with only one family of constructions,
and which no key source in the public Cicada corpus satisfies.

**Verdict.** Not solved. The 2012 and 2013 puzzles and 19 of the 75 Liber Primus pages (all 17
of the first set, 2 of the second) were already solved by the community; every one of those
solutions reproduces here. The 56 unsolved pages (nine sections in the verified transcription)
behave as a chain cipher whose step between consecutive runes is a flat, aperiodic 28-symbol
keystream. Without the source of that keystream, statistical cryptanalysis has nothing left to
grip.

**What is new.** The community's "86 doublets" clue is confirmed and sharpened: the step
distribution is uniform except at zero, independent of the previous rune, and shows no
periodicity, no cross-section reuse, and no match to any tested mathematical sequence, autokey,
or running text, in either the raw or the chain form. Each negative comes with a positive control.

## What is already solved, reproduced

The toolkit's gate (`verify_solved.py`) re-derives all nine solved sections from the runes
before any attack runs. Two independent community transcriptions agree on every unsolved rune
(`crosscheck_transcription.py`), so the ciphertext itself is not in doubt.

| Section | Method | Opening plaintext (Runeglish) |
|---|---|---|
| Warning (01) | Atbash on the Gematria Primus | A WARNING. BELIEVE NOTHING FROM THIS BOOK... |
| Welcome (03-04) | Vigenère, key DIVINITY, plaintext F passes through | WELCOME, PILGRIM, TO THE GREAT JOURNEY... |
| Wisdom (05) | None | THE PRIMES ARE SACRED. THE TOTIENT FUNCTION IS SACRED. |
| Koan (06-09) | Atbash, then shift +3 | A KOAN. A MAN DECIDED TO GO AND STUDY WITH A MASTER. |
| Loss of divinity (10-13) | None | THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS... |
| Koan (14-15) | Vigenère, key FIRFUMFERENFE, F interrupts | DURING A LESSON, THE MASTER EXPLAINED THE I. |
| Instruction (16) | None | QUESTION ALL THINGS. DISCOVER TRUTH INSIDE YOURSELF. |
| An end (56) | Shift down by phi(p_n) = p_n - 1, one F interrupt | WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO... |
| Parable (57) | None | LIKE THE INSTAR TUNNELING TO THE SURFACE... |

The alphabet is the 29-rune Gematria Primus, indices 0 to 28 in the order
ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ (F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IO EA),
with prime values 2 through 109. All arithmetic below is on those indices modulo 29.

## The unsolved corpus

| | |
|---|---|
| Runes | 12,956 in nine unsolved sections (729 to 3,008 each), 2,921 words, separators and chapter marks intact |
| Index of coincidence | 1.000 in every section (random 1.00, English in runes 1.78) |
| Adjacent identical runes | **86**, where 447 are expected at random: 0.66 % against 3.45 %, z = -17 |
| Periodicity | none to 300 per section and 600 corpus-wide; no Kasiski signal; no shared keystream between sections |

Apart from the doublets, the ciphertext is indistinguishable from a uniform random stream at
every order tested: unigram, bigram (once the diagonal is removed), coincidence at lags 2 and 3,
second differences, and the conditional table of each rune against its predecessor. That last
table has a chi-square of 801 on 784 degrees of freedom once the diagonal is set aside, which is
to say the step from one rune to the next carries no memory of the rune it started from.

## The fingerprint

Counts of the step Δ = c_i - c_{i-1} (mod 29) over all 12,955 adjacent pairs; a uniform stream
gives 447 per step:

```
Δ:      0    1    2    3    4    5    6    7    8    9   10   11   12   13   14
count: 86  459  504  440  438  446  430  470  426  510  497  455  449  504  474
Δ:     15   16   17   18   19   20   21   22   23   24   25   26   27   28
count: 470  449  404  434  474  467  463  421  486  468  467  457  476  431
```

Every non-zero step occurs about 447 times; the largest deviation among the 28 non-zero counts is
z = +3.0, consistent with noise. The zero step is at z = -17.

This one deficit is the whole signal, and it is a demanding one. For any cipher of the form
c_i = p_i + k_i in which the key does not depend on the ciphertext, a doublet occurs whenever the
plaintext difference cancels the key difference, and on English that happens about 3.4 % of the
time no matter what the key is. The table below encrypts the 2,979 runes of known Liber Primus
plaintext with each candidate family and records the doublet rate it produces
(`fingerprint.py`).

| Cipher applied to the real solved plaintext | Doublet rate | Matches 0.66 % ± 0.07 %? |
|---|---|---|
| Vigenère, random key of length 8 / 13 / 29 | 3.3 / 2.1 / 3.8 % | no |
| Stream keys: phi(p_n), p_n, p_n², Fibonacci, n, n² | 3.5 - 4.1 % | no |
| Any of the above with F interrupts (as on the solved pages) | 3.2 - 4.1 % | no |
| Running key from English text, Vigenère or Beaufort | 3.9 / 3.7 % | no |
| Plaintext autokey (lag 1, lag 5); plaintext differences | 5.4 / 4.1 / 3.7 % | no |
| Ciphertext autokey c = p + c_prev | 1.6 % (the frequency of F) | no, and its step stream is English (IoC 1.76) |
| One-time pad | 3.3 % | no |
| Vigenère with the key advanced whenever the output would repeat | 0.4 - 0.7 % | yes, but its period signature is absent (below) |
| **Chain cipher c_i = c_{i-1} + s_i, s_i in 1..28, zero step for one rare letter** | **0.67 %** | **yes** |

The chain family is the only one that reproduces the deficit, and the rest of the statistics
pin it down further. The step stream is flat and memoryless, so the steps are keyed rather than
a fixed function of the plaintext (a fixed function would make the step stream as English as the
text). The step stream shows no period to 300 per section, so the key is aperiodic or longer
than the sections. And the zero step occurs at 0.66 %, which happens to equal the frequency of
the rune ᛠ (EA, the 29th and last rune) in the solved plaintext; the natural reading is a
28-symbol keyed step alphabet with EA as a full turn of the wheel, though the word-position
statistics of the 86 doublets do not match EA's usage in English, so that reading remains a
conjecture rather than a result.

## Exclusion ledger

Each row is a family that was attacked, the detector used, the proof that the detector has
power, and the outcome on the real text. A negative without a positive control is not listed.
Controls are in `controls.py` and `tests5.py`.

| Family | Detector and coverage | Positive control | Result on the unsolved sections |
|---|---|---|---|
| Monoalphabetic, transposition | Unigram distribution | IoC 1.78 on plaintext | Flat (IoC 1.000). Excluded. |
| Word-level Caesar or affine | Difference-tuple dictionary lookup, lengths 4-8 | 100 % hit on plaintext words | Hit rate equals the random baseline. Excluded. |
| Periodic Vigenère / Beaufort, with or without F interrupts or key-skipping | Periodic IoC 1-300 per section, 1-600 corpus; coincidence at lags 1-300 (survives interrupts and skips) | period 13 at n = 3000: z 8.5 plain, 6.4 with interrupts, 5.5 with skips | Best lag per section z 2.5-3.8; random text gives 3.1 ± 0.5. The one candidate (p0-2, lag 35) has no harmonics. Excluded for periods ≤ 300 in large sections, ≤ 400 corpus-wide. |
| Digraphic / block ciphers (Playfair-type) | Parity of doublet positions mod 2-8 (section and sentence aligned) | by construction | Uniform; within-word skew matches word lengths. Excluded. |
| Mathematical-sequence keys, raw form (mod 29) | 24 sequences × 200 offsets × 2 signs on raw and Atbash text | stream detection IoC 1.7 | Max IoC 1.03-1.12 (n-dependent noise). Excluded. |
| Mathematical-sequence keys, chain form (mod 28) | 22 sequences × 300 offsets × 2 signs × 14 step-alphabet bijections (including discrete logs to all 12 primitive roots) × 2 doublet conventions | synthetic chain cipher recovered, IoC 1.66 | Max IoC 1.08-1.15. Excluded. |
| Autokeys inside the chain (ciphertext lags 1-60, plaintext lags 1-3 with all 28^L seeds, multiplicative) | IoC of decrypted step stream | plaintext autokey seed recovered, IoC 1.67 | 1.01-1.15. Excluded. |
| Prime-value feedback (shift by the Gematria prime of the previous rune, six variants) | IoC of output, all seeds | Δc test exposes ciphertext autokey (1.76) | 0.97-1.06. Excluded. |
| Running key from Cicada-linked texts (solved Liber Primus text, its Atbash and ciphertext, Emerson's Self-Reliance, the Mabinogion, War and Peace as a control text), raw and chain form | IoC of c - K, K - c, c + K at every offset, 400-rune windows | known offset found at z = 34 | Max 1.13-1.14; random text against the same keys also reaches 1.128. Excluded. |
| Shared keystream between sections (or with itself at a shift) | IoC of rune differences at every relative shift, overlap ≥ 300 | z 7.8 at overlap 1200 | Max z 3.3, all at the shortest overlaps. Excluded for overlaps ≥ 600. |
| Progressive key (k_i = a + δ·i) | Requires an English letter-difference rarer than 0.66 % | measured on two corpora | Rarest difference is 1.3 %. Excluded. |

## Two smaller findings

**The doublets are on the page.** Every doublet site was located to page and line and cropped
from the original images (`crop_doublets.py`). In the samples inspected (ᚦ·ᚦ across a word gap on
page 0, ᛠᛠ on page 1, ᚠᚠ on page 9; see `results/crops/`) both runes are ordinary, identical
glyphs with no rubrication, dots, or size change. The anomaly is in the cipher, not in the
transcription.

**The words are long for English.** Mean cipher word length is 4.47 runes against 4.03 for the
solved pages and 4.12 for English prose in runes; two-rune words are 15.5 % of the text where
English gives 22 to 24 %. Either the plaintext is in a different register or language, or the
separators are not plain word boundaries.

## What would be needed

A flat, aperiodic keystream is exactly what a running key from an unavailable text, a
pseudo-random generator, or a hash-derived pad looks like. Cicada's own pointers fit that
reading: the solved page 56 sends every pilgrim to a deep-web page identified only by a SHA-512
hash that has never been found, and the 2016 signed message says the book's "numbers are the
direction". The tests above make it unlikely that the key is any published integer sequence or
any text in the public archive, applied in any of the simple ways Cicada used on the solved
pages. Solving the remaining pages therefore looks like a search for the key source rather than
a cryptanalytic problem, and the community's decade of work points the same way.

Two of the three cheap threads were then run to the end (`outguess/RESULTS.md`). Outguess over
all 75 page images, with no key and with 96 Cicada-lexicon keys, recovered every known 2014
payload byte for byte and nothing else: the unsolved pages give 58,152 bytes of 7.99-bit noise
without a key, and every keyed extraction repeats the same bytes across most pages because the
near-white pages share DCT coefficients at the key-selected positions. Hashing 692,438
candidates from the archive and all 4,521 payloads against the page-56 SHA-512 found no match.
The archive's 3.6-million-character growing string and the raw bytes of every page image were also scanned as running keys at every offset and are below noise. The remaining thread is a physical re-examination of the doublet sites on the print edition.

## Sources

- Verified transcriptions and page images: relikd/LiberPrayground (GitHub); independent
  transcription: cicada-solvers/cicada-library (GitHub).
- Puzzle history and solved-page methods: scream314/cicada3301 (GitHub); 2012-2017 archive:
  krisyotam/cicada3301 (GitHub).
- Community statistics: Uncovering Cicada Wiki, "Frequency Analysis Unsolved Pages" and "Liber
  Primus Ideas and Suggestions" (report the same 86 doublets as "so far the only solid clue").
- Cryptanalysis briefing: cicadasolvers.com/quickstart (DJUBEI dis legomenon, n-gram counts,
  prime-Fibonacci observations).
- 2016 signed message via infotomb 4gq25.jpg; 2017 signed message (pastebin yEiTHhvF); PGP key
  7A35090F.
