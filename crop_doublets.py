# -*- coding: utf-8 -*-
"""Locate every doublet in the relikd page .txt files (line-accurate) and crop the corresponding page image line."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp
from PIL import Image, ImageDraw

PAGES = os.path.join(lp.RELIKD, 'pages')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crops')
os.makedirs(OUT, exist_ok=True)
FILES = ['p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26', 'p27-32', 'p33-39', 'p40-53', 'p54-55']

report = []
for fname in FILES:
    lo, hi = [int(x) for x in fname[1:].split('-')]
    raw = open(os.path.join(PAGES, fname + '.txt'), encoding='utf-8').read()
    pages = raw.split('\n\n')
    pages = [p for p in pages if p.strip()]
    pagenums = list(range(lo, hi + 1))
    if len(pages) != len(pagenums):
        print('WARNING %s: %d page blocks vs %d page numbers' % (fname, len(pages), len(pagenums)))
    prev_rune = None
    for pi, block in enumerate(pages):
        pn = pagenums[pi] if pi < len(pagenums) else None
        lines = block.split('\n')
        nlines = len(lines)
        for li, line in enumerate(lines):
            runes_in_line = [c for c in line if c in lp.RUNE_TO_IDX]
            for ri, ch in enumerate(line):
                if ch in lp.RUNE_TO_IDX:
                    if prev_rune is not None and ch == prev_rune[0]:
                        report.append({'file': fname, 'page': pn, 'line': li, 'nlines': nlines, 'col_char': ri,
                                       'rune': ch, 'letter': lp.LETTERS[lp.RUNE_TO_IDX[ch]],
                                       'prev_loc': prev_rune[1], 'line_text': line})
                    prev_rune = (ch, (pn, li, ri))
                elif ch in lp.WHITE:
                    pass  # separators do not reset chain
print('doublets located:', len(report))
json.dump(report, open(os.path.join(OUT, 'doublets.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# crop: page image pN.jpg ; estimate the text band and line height from image size and line count
for k, d in enumerate(report):
    if d['page'] is None:
        continue
    img_path = os.path.join(PAGES, 'p%d.jpg' % d['page'])
    if not os.path.exists(img_path):
        continue
    im = Image.open(img_path)
    W, H = im.size
    # text block roughly occupies the central area; lines evenly spaced; use generous margins
    top, bottom = int(H * 0.08), int(H * 0.92)
    lh = (bottom - top) / max(1, d['nlines'])
    y0 = int(top + d['line'] * lh - lh * 0.8)
    y1 = int(top + (d['line'] + 1) * lh + lh * 0.8)
    crop = im.crop((0, max(0, y0), W, min(H, y1)))
    if crop.width > 1400:
        crop = crop.resize((1400, int(crop.height * 1400 / crop.width)))
    out = os.path.join(OUT, 'd%02d_p%d_line%d_%s.png' % (k, d['page'], d['line'], d['letter']))
    crop.save(out)
    d['crop'] = out
json.dump(report, open(os.path.join(OUT, 'doublets.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for d in report[:90]:
    print('%s p%s line %d/%d %s  | %s' % (d['file'], d['page'], d['line'], d['nlines'], d['letter'], d['line_text']))
