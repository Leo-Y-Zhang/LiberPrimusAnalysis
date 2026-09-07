# -*- coding: utf-8 -*-
"""Fetch the community data this toolkit depends on into ./sources (they are not redistributed here).

  relikd/LiberPrayground          verified page transcriptions, page images, rune n-gram tables, dictionaries
  cicada-solvers/cicada-library   an independent transcription (used by crosscheck_transcription.py)

Optional:  python setup_sources.py --archive   also clones krisyotam/cicada3301 (about 1.1 GB; the 2012-2017
archive used only by the running-key text tests in results/tests8.txt).
Also writes pi.txt (5,000 digits via mpmath) if it is missing.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'sources')
REPOS = [
    ('relikd_LiberPrayground', 'https://github.com/relikd/LiberPrayground.git'),
    ('cicada-solvers_cicada-library', 'https://github.com/cicada-solvers/cicada-library.git'),
]
if '--archive' in sys.argv:
    REPOS.append(('krisyotam_cicada3301', 'https://github.com/krisyotam/cicada3301.git'))

os.makedirs(SRC, exist_ok=True)
for name, url in REPOS:
    dest = os.path.join(SRC, name)
    if os.path.isdir(os.path.join(dest, '.git')):
        print('present ', name)
        continue
    print('cloning ', name)
    subprocess.check_call(['git', 'clone', '--quiet', '--depth', '1', url, dest])

pi = os.path.join(HERE, 'pi.txt')
if not os.path.exists(pi):
    from mpmath import mp
    mp.dps = 5000
    open(pi, 'w').write(str(mp.pi)[2:])
    print('wrote pi.txt')
print('sources ready')
