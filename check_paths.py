# -*- coding: utf-8 -*-
"""Fail if any tracked text file carries a machine-local path (a public repository must not leak one).
Usage: python check_paths.py --check"""
import os, re, subprocess, sys

PAT = re.compile(r'([A-Za-z]:\\Users\\[^\\\s]+\\|/Users/[^/\s]+/|/home/[^/\s]+/|AppData\\Local\\Temp)')
files = subprocess.check_output(['git', 'ls-files'], text=True).split('\n')
bad = []
for f in files:
    if not f or not os.path.isfile(f):
        continue
    try:
        t = open(f, encoding='utf-8').read()
    except (UnicodeDecodeError, OSError):
        continue
    if f == 'check_paths.py':
        continue
    for m in PAT.finditer(t):
        bad.append((f, m.group(0)))
if bad:
    for f, m in bad[:20]:
        print('machine path in %s: %s' % (f, m))
    sys.exit(1)
print('no machine-local paths in %d tracked files' % len(files))
