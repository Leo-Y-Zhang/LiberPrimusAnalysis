# -*- coding: utf-8 -*-
"""Test archive key material as running keys against the unsolved sections (raw mod 29 and chain mod 28 forms):
 - the 2014 'growing string' (3.6 M hex characters from the second onion) as bytes, against every section
 - the raw JPEG bytes of each page image against the section printed on that page
   (dump page k corresponds to image k+17 of the 75-image set; section pN-M spans images N+17..M+17)
Usage: python scan_key_material.py <growing-string.txt> <images-dir> [gs|img|both]"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lp, fastscan

unsolved = lp.unsolved_sections()
gs_path, img_dir = sys.argv[1], sys.argv[2]
what = sys.argv[3] if len(sys.argv) > 3 else 'both'

if what in ('gs', 'both'):
    hexs = ''.join(ch for ch in open(gs_path, encoding='utf-8', errors='ignore').read() if ch in '0123456789abcdefABCDEF')
    byt = np.array([int(hexs[i:i + 2], 16) for i in range(0, len(hexs) - 1, 2)], dtype=np.int64)
    print('growing string: %d hex chars -> %d bytes; null threshold about %.3f' % (len(hexs), len(byt), fastscan.null_threshold(len(byt))), flush=True)
    fastscan.scan_material(byt, 'gs-bytes', unsolved)
    sys.stdout.flush()

if what in ('img', 'both'):
    print('PAGE IMAGES (raw bytes) against their own section:', flush=True)
    for s in unsolved:
        lo, hi = [int(x) for x in s['name'][1:].split('-')]
        for page in range(lo, hi + 1):
            f = os.path.join(img_dir, '%02d.jpg' % (page + 17))
            if not os.path.exists(f):
                continue
            b = np.frombuffer(open(f, 'rb').read(), dtype=np.uint8).astype(np.int64)
            print('image %02d.jpg (%d bytes, null ~%.3f) vs %s' % (page + 17, len(b), fastscan.null_threshold(len(b)), s['name']), flush=True)
            fastscan.scan_material(b, '%02d.jpg' % (page + 17), [s])
            sys.stdout.flush()
print('SCAN DONE', flush=True)
