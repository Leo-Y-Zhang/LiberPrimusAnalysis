# Liber Primus cryptanalysis — state of knowledge (this session)

Working dir: the repository root (run `python setup_sources.py` first; sources are cloned into `sources/`)
Set `PYTHONIOENCODING=utf-8` before running python here (runes in output).

## Toolkit (verified)
- `lp.py` — Gematria Primus (29 runes, indices 0..28 in order F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IO EA; primes 2..109),
  conversions, ciphers (vigenere/beaufort/running key with interrupt convention, atbash, shift, totient stream, autokey), stats (ioc, periodic ioc,
  doublets, chi2), an n-gram language model `Scorer()` (avg log10/rune: English ≈ -0.9, random ≈ -2.7), dictionary word-hit rate.
- `dataset.json` — all 18 sections (9 solved incl. plaintext, 9 unsolved) with rune indices, words, chapter-mark segments, tokens.
  Load with `lp.load_dataset()`, `lp.section(name)`, `lp.unsolved_sections()`.
- `verify_solved.py` — GATE: reproduces all 9 known solutions (PASSED). Solutions: 0_warning atbash; 0_welcome Vigenère DIVINITY with
  F-interrupts (F occurrences 4,5,6,7,10,11,14,18,20,21,25 pass through, key not consumed); 0_wisdom plain; 0_koan_1 atbash then +3;
  0_loss_of_divinity plain; jpg107-167 Vigenère FIRFUMFERENFE with F-interrupts (2,3); jpg229 plain; p56_an_end p_i = c_i - (prime_i - 1)
  with F-interrupt (4th F); p57_parable plain.
- Transcription: relikd's verified pages agree with cicada-library's independent transcription on EVERY unsolved rune (only 1 diff, on a solved page).

## Unsolved corpus
9 sections (book order): p0-2 (729 runes), p3-7 (1145), p8-14 (1729), p15-22 (1903), p23-26 (1021), p27-32 (1433), p33-39 (1680),
p40-53 (3008), p54-55 (308). Total 12,956 runes, 2,921 words. Word separators / sentence marks / chapter marks are preserved.
Section titles (before first chapter mark): p0-2 "8+5 runes", p54-55 "1+8 runes" (ᚪ + 8: 'A ????????'), p33-39 "2+8", p23-26 "2,6,3,5", p27-32 "3,12,4", p3-7 "2,11,3".

## Hard statistical facts (all verified twice)
1. Ciphertext is FLAT: IoC = 1.000 (random = 1.0, English/Runeglish = 1.78), chi2 vs uniform ~ df (28). Every section. Unigram order is uninformative.
2. NO periodicity: periodic IoC for periods 1..300 per section and 1..600 for the whole corpus: no peak beyond noise. Kasiski: repeated 4-grams at chance
   level. Whole-corpus autocorrelation (kappa at lags 1..400): max 0.0398 vs 0.0345 baseline (noise). This also rules out Vigenère with
   occasional key slips for periods <= 400 (kappa at the period would be ~0.05).
3. Sections do NOT share a keystream: cross-section kappa at shift 0 ≈ 1/29 for all pairs; at all relative shifts, no peak beyond noise (z<4.6 with thousands of shifts tested).
4. DOUBLETS ARE SUPPRESSED 5x: c_i == c_{i-1} in 86 of 12,955 adjacent pairs = 0.66% (random 3.45%, z = -17). Same in every section, both within words
   and across word boundaries (within 0.63%, boundary 0.80%), across chapter marks too. Which runes double: spread over all 28 runes ~uniformly.
   Lag-2 and lag-3 coincidences are NORMAL (3.4%). Δc = c_i - c_{i-1} is uniform on 1..28 and independent of c_{i-1} (chi2 801 on df 784).
   Second differences flat; the Δc stream itself shows no doublet suppression (0.0337).
5. Word-length distribution: mean 4.47 (English prose ≈ 4.1; LP solved plaintext 4.03). 2-letter words 15.5% vs 22-24% in English; 5-letter 10.9 vs 7.7-10;
   8+ letter words over-represented. Either the plaintext register differs (Latin? formal?), or the cipher alters word lengths, or dots are not word separators.
6. One repeated 6-gram in the corpus (DJUBEI at corpus positions 6555 and 12950); 6 repeated 5-grams. Expected by chance ≈ 0.14 and 4 respectively. Weak.

## Fingerprint test (encrypt the 2,979 runes of KNOWN LP plaintext with candidate ciphers, compare doublet rate 0.0066±0.0007)
| cipher on real plaintext | doublet rate |
|---|---|
| Vigenère key len 8/13/29 | .033/.021/.038 |
| totient/prime/prime²/fib/trithemius/i² streams | .035-.041 |
| ciphertext autokey c=p+c_prev | .016 (=P(F)) |
| ciphertext autokey c=p-c_prev | .030 |
| plaintext autokey (lag1, lag5), plain diff | .054/.041/.037 |
| running key English (vig/beaufort), LP text as key | .039/.037/.035 |
| any of the above with F-interrupts | .032-.041 |
| OTP | .033 |
| chain c = c_prev + p + 1 (doublet iff p=EA) | .0067 |
Conclusion: ANY cipher of the form c_i = p_i + k_i with k independent of the ciphertext gives ~3.4% doublets on English. The only family
that reproduces 0.66% is a CHAIN cipher c_i = c_{i-1} + s_i with s_i in {1..28} (never 0) except for one rare plaintext letter.
LP plaintext letter frequencies: EA = 0.67%, IO = 0.54% (all others either >1% or ~0). EA (index 28, the 29th rune) fits the doublet rate exactly.
BUT: Δc is flat (IoC 1.024, which is exactly the effect of the depleted zero), so Δc ≠ f(plaintext) for any fixed f. The increments are KEYED and flat.
Model consistent with everything: s_i = 1 + ((σ(p_i) + k_i) mod 28) for the 28 non-EA letters (σ unknown ordering), s_i = 0 (i.e., repeat rune) for EA,
with k a flat, aperiodic (period > 300 or non-periodic) 28-ary keystream. Alternative: any flat cipher + "advance the key when the output would repeat"
(predicts 0 doublets; the 86 observed argue against it unless they are pass-through interrupts).
Positional check: the second rune of the 86 doublets sits at word position 0:23, 1:12, 2:21, 3:7, 4:8, 5:6, 6:5, 7+:4. For EA one expects ~50% at
position 1 (DEATH, REAL, HEAR...) — observed 14%; for IO/-TION one expects mostly late positions. Neither fits cleanly.

## Attacks already run (all negative, IoC of output ≈ 1.0)
- Word-level Caesar/affine/reversed (difference-tuple dictionary test): hit rate = random baseline.
- Sequence keys (n, n², n³, tri, prime, prime±1, 2p, p², gaps, cumsum, fib, lucas, φ(n), 2^n, 3^n, 3301n, factorial, catalan, π digits),
  offsets 0..199, both signs, on: raw c (mod 29), atbash c, chain increments u=(Δc-1) mod 28 (both ring directions), Δc mod 29.
- Running key = solved LP plaintext / atbash / solved ciphertext at all offsets, vig/beaufort/add, on raw c and on chain increments mod 28.
- Prime-value keyed variants: c ± prime(c_prev), c·prime(c_prev)^-1, s ± prime(c_prev), p = c ∓ prime(p_prev) all seeds, plaintext autokey lags 1-3.
- relikd's community DB (db/db_high.txt): Vigenère key lengths 1..20 with optimized F-interrupt sets → best IoC ~1.3-1.4 (overfit noise).

## Hints from Cicada (verbatim)
- 2016 PGP tweet: "The path lies empty; epiphany seeks the devoted. Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction. Seek and you will be found."
- 2017: "Beware false paths. Always verify PGP signature from 7A35090F."
- Page 56 (solved): "Within the deep web there exists a page that hashes to 36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4. It is the duty of every pilgrim to seek out this page." (SHA-512; page never found)
- Page 57: "Parable: like the instar tunneling to the surface, we must shed our own circumferences. Find the divinity within and emerge."
- Solved wisdom page: "The primes are sacred. The totient function is sacred. All things should be encrypted."
- Outguess on 03/04.jpg: "Let the text guide you." Outguess on several unsolved images yields "58.2 kB garbage" (likely LSB noise; unverified).

## What has NOT been tried here yet (candidates for agents)
- Chain model with other bijections {1..28}<->Z28 (discrete log for each of the 12 primitive roots mod 29; reversed ring) with sequence keys.
- Hill-climb Vigenère over Z29 with LM scoring incl. interrupt/skip-on-collision models (expected negative by fingerprint, but a proper check).
- Keys derived from outguess data / image bytes / page numbers / the 2013-2014 puzzle artifacts (onion strings, "growing string", hashes).
- Non-English plaintext (Latin, Old English, Enochian, Cicada's Runeglish with unusual spelling).
- Transcription-independent checks of the doublet statistic directly from the page images (are doubled runes visibly rendered differently?).
- Are the 86 doublet positions structured (spacing, gematria sums of words containing them, page positions)?

## Addendum (2026-09-07, after positive-control audit)
- controls.py: lag-kappa detects a period-13 Vigenère at n=3000 even with F-interrupts (z 6.4) and key-skip-on-collision (z 5.5) where periodic IoC is destroyed
  (1.15 / 1.08). Running-key detection z=34 on 400-rune windows. Ciphertext autokey exposed by Δc IoC 1.76. Scorer separates English/random by 2 log10 per rune.
  Key-skip-on-collision Vigenère produces 0.4-0.7% doublets on real plaintext (leak via adjacent equal key letters) — the only c=p+k variant matching the fingerprint;
  but its kappa signature at the period is absent in every section (tests7: best-lag z per section 2.5-3.8, equal to the random-text null 3.1±0.5; p0-2's lag 35 has
  no harmonics at 70/105/140).
- tests5.py: chain-model sequence attack fixed for alignment (doublets as placeholders, both key conventions, 14 bijections incl. 12 discrete logs): positive control
  recovers a synthetic chain cipher (IoC 1.66); real sections best IoC28 1.08-1.15 = noise. IoC-of-differences has z 7.8 power for a shared running key at overlap 1200
  (kappa only 4.0); re-scan of all section pairs and self-shifts: max z 3.3 -> no shared keystream between sections.
- tests6.py: chain + ciphertext-autokey (lags 1-60, both signs, multiplicative) and chain + plaintext-autokey (lags 1-3, all 28^L seeds; control recovers IoC 1.67):
  all sections 1.01-1.15 = noise.
- crop_doublets.py: doublet sites cropped from the page images; visual check of samples (p0 l5 TH·TH across a word gap, p1 l8 ᛠᛠ, p9 l2 ᚠᚠ): both runes normal,
  identical glyphs; no diacritics/rubrication. The doublets are genuine.
- Doublet positions are uniform mod 2..8 relative to section and sentence starts (no digraphic/block cipher). Doublet-word position/length statistics do not match
  EA or IO (or F/X/J) usage in English: the "doublet = a rare letter" reading is weak.
- Ciphertext ᚠ counts per section do not show the excess an F-interrupt pass-through scheme would produce (p3-7: 26 vs 57 expected).
- Community wiki (Frequency Analysis Unsolved Pages) independently reports 86 doublets and calls it "so far the only solid clue"; no explanation there.
