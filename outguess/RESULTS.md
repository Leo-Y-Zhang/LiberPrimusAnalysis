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

**Page images (raw JPEG bytes) as running keys for their own section,** every offset, raw and chain forms, both signs: 56 images tested, best IoC 1.195 (72.jpg vs p54-55), none above its per-image noise ceiling. Not the keystream. Complete.

| image | section | best IoC | noise ceiling |
|---|---|---|---|
| 17.jpg | p0-2 | 1.143 | 1.195 |
| 18.jpg | p0-2 | 1.129 | 1.194 |
| 19.jpg | p0-2 | 1.148 | 1.193 |
| 20.jpg | p3-7 | 1.144 | 1.193 |
| 21.jpg | p3-7 | 1.150 | 1.194 |
| 22.jpg | p3-7 | 1.145 | 1.194 |
| 23.jpg | p3-7 | 1.137 | 1.193 |
| 24.jpg | p3-7 | 1.154 | 1.193 |
| 25.jpg | p8-14 | 1.153 | 1.194 |
| 26.jpg | p8-14 | 1.152 | 1.194 |
| 27.jpg | p8-14 | 1.138 | 1.194 |
| 28.jpg | p8-14 | 1.151 | 1.194 |
| 29.jpg | p8-14 | 1.138 | 1.194 |
| 30.jpg | p8-14 | 1.141 | 1.194 |
| 31.jpg | p8-14 | 1.137 | 1.191 |
| 32.jpg | p15-22 | 1.141 | 1.192 |
| 33.jpg | p15-22 | 1.159 | 1.193 |
| 34.jpg | p15-22 | 1.153 | 1.193 |
| 35.jpg | p15-22 | 1.141 | 1.193 |
| 36.jpg | p15-22 | 1.152 | 1.193 |
| 37.jpg | p15-22 | 1.143 | 1.193 |
| 38.jpg | p15-22 | 1.133 | 1.193 |
| 39.jpg | p15-22 | 1.153 | 1.192 |
| 40.jpg | p23-26 | 1.138 | 1.192 |
| 41.jpg | p23-26 | 1.161 | 1.194 |
| 42.jpg | p23-26 | 1.133 | 1.194 |
| 43.jpg | p23-26 | 1.129 | 1.194 |
| 44.jpg | p27-32 | 1.120 | 1.193 |
| 45.jpg | p27-32 | 1.136 | 1.193 |
| 46.jpg | p27-32 | 1.138 | 1.193 |
| 47.jpg | p27-32 | 1.136 | 1.193 |
| 48.jpg | p27-32 | 1.144 | 1.193 |
| 49.jpg | p27-32 | 1.155 | 1.190 |
| 50.jpg | p33-39 | 1.142 | 1.192 |
| 51.jpg | p33-39 | 1.136 | 1.193 |
| 52.jpg | p33-39 | 1.130 | 1.193 |
| 53.jpg | p33-39 | 1.155 | 1.192 |
| 54.jpg | p33-39 | 1.129 | 1.192 |
| 55.jpg | p33-39 | 1.148 | 1.192 |
| 56.jpg | p33-39 | 1.146 | 1.193 |
| 57.jpg | p40-53 | 1.146 | 1.195 |
| 58.jpg | p40-53 | 1.183 | 1.195 |
| 59.jpg | p40-53 | 1.144 | 1.195 |
| 60.jpg | p40-53 | 1.149 | 1.195 |
| 61.jpg | p40-53 | 1.132 | 1.195 |
| 62.jpg | p40-53 | 1.145 | 1.195 |
| 63.jpg | p40-53 | 1.143 | 1.195 |
| 64.jpg | p40-53 | 1.137 | 1.195 |
| 65.jpg | p40-53 | 1.161 | 1.196 |
| 66.jpg | p40-53 | 1.135 | 1.194 |
| 67.jpg | p40-53 | 1.135 | 1.193 |
| 68.jpg | p40-53 | 1.130 | 1.194 |
| 69.jpg | p40-53 | 1.149 | 1.195 |
| 70.jpg | p40-53 | 1.129 | 1.195 |
| 71.jpg | p54-55 | 1.186 | 1.195 |
| 72.jpg | p54-55 | 1.195 | 1.194 |
