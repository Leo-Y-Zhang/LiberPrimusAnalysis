# Key-source hunt: outguess payloads, the page-56 hash, and archive key material

Run on 7 September 2026, after the cryptanalysis in `docs/REPORT.md` had reduced the problem to
"find the keystream source". Scripts in this directory; raw payloads (121 MB of noise) are not
committed.

## 1. Outguess over all 75 page images

`outguess_run.sh` ran in a Debian container (`outguess` 0.2 from the distribution package)
over the 75 images of the complete Liber Primus set, once with no key and once with each of the
96 keys in `keys.txt` (Cicada lexicon, solved-page keys, PGP identifiers, numbers from the
puzzle). Result: 4,521 non-empty payloads, 115 MB.

**Positive control passed.** With no key the run recovered, byte for byte, every payload the
community found in 2014: the PGP-signed hex blocks on pages 00, 01 and 02 (2,899 bytes each,
identical to the archive copies), the "Let the text guide you" message with its embedded JPEG
on page 03 (31,809 bytes), the "For those who have fallen behind" note on page 08 (140 bytes), and
the "Create one Tor hidden service" instruction on pages 10 to 13 (1,234 bytes each). Page 04
gives the 7.5 kB of noise the community recorded.

**The unsolved pages carry nothing recoverable.** Every no-key payload from an unsolved page
(images 17, 21, 43, 57 to 65, 68 to 71) is exactly 58,152 bytes with entropy 7.99 bits per byte
and no structure: this is outguess reading random least-significant bits up to the image's
capacity, which is the same for these near-identical pages. That is the "58.2 kB garbage" of the
community record, now explained.

**Keyed extraction is an artifact.** For every key, roughly 66 of the 73 images that yield a
payload give the *same* first six bytes and the *same* payload length (for example 69 of 73
images under `emerge`, 66 of 70 under `1033`). Wrong-key extraction reads the least-significant
bits of the DCT coefficients that the key's generator selects; on pages that are mostly white
those coefficients are identical from page to page, so the bytes repeat. No keyed payload has
entropy below 7.5 bits per byte at any size above 700 bytes, none contains a PGP marker, an
onion address, "3301" or "http", and no two payloads from different keys agree.

## 2. The page-56 hash

Page 56 says a deep-web page hashes to the SHA-512 value
`36367763ab73...c2a8b4`. `hash_hunt.py` hashed 692,438 candidates from the archive (every file,
every normalised file, every non-empty line, 41 Cicada phrases and the 13 onion addresses found
in the archive, each in 30 framing variants with and without scheme and trailing newline or slash),
plus all 4,521 outguess payloads. No match. This was never likely (the page is a document, not a
phrase), but it is now on the record.

## 3. Archive key material as running keys

`scan_key_material.py` and `fastscan.py` test a byte stream as a running key against a section
at every offset, in the raw form (c - k mod 29) and the chain form (step - k mod 28), both signs,
on 400-rune windows; the positive control recovers a planted key at the right offset with IoC
1.77 against a noise ceiling near 1.19 for 200,000 offsets.

**No-key payloads as keystreams** (own-page section; bytes and 5-bit groups; raw and chain forms; both signs): 15 payloads tested, best IoC minus its noise ceiling at most -0.029, so every one is below noise. The run was still finishing its last payloads at commit time.

**Growing string** (2014 second onion, 1,820,650 bytes) **as a running key,** every offset, raw and chain forms, both signs: best IoC per section p0-2 1.145, p3-7 1.170, p8-14 1.159, p15-22 1.147, p23-26 1.145, p27-32 1.156, p33-39 1.156, p40-53 1.151, p54-55 1.206 (307-rune window, ceiling about 1.23), against a noise ceiling of about 1.20 for 1.8 million offsets. Not the keystream. Complete.

**Page images (raw JPEG bytes) as running keys for their own section:** scan in progress at commit time (4 of 58 images, all below noise so far: best 1.144 against about 1.19); the final table is appended when it completes.
