# -*- coding: utf-8 -*-
"""Page 56 says a deep-web page hashes to a given SHA-512. Hash every candidate we can lay hands on:
known Cicada strings and onion addresses (with the usual framing variants), every text file in the
2012-2017 archive, every page image, every outguess payload, and the Liber Primus plaintexts.
Usage: python hash_hunt.py <dir-or-file> [...]   (directories are walked; files up to 50 MB are hashed)"""
import hashlib, os, re, sys

TARGET = ('36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b'
          '464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4')
assert len(TARGET) == 128

hits = []
def check(label, data):
    h = hashlib.sha512(data).hexdigest()
    if h == TARGET:
        hits.append(label)
        print('*** HIT:', label)
    return h

def variants(s):
    for pre in ('', 'http://', 'https://'):
        for suf in ('', '/', '\n', '/\n', '\r\n'):
            yield pre + s + suf

STRINGS = ['3301', '1033', 'cicada', 'Cicada 3301', 'cicada3301', 'liber primus', 'Liber Primus', 'LIBER PRIMUS',
           'intus', 'an end', 'parable', 'divinity', 'circumference', 'instar', 'emergence', 'the primes are sacred',
           'the totient function is sacred', 'all things should be encrypted', 'know this', 'question all things',
           'command your own self', 'seek and you will be found', 'liber primus is the way', 'epiphany seeks the devoted',
           'the path lies empty', 'it is the duty of every pilgrim to seek out this page', 'welcome pilgrim',
           'do four unreasonable things each day', 'find the divinity within and emerge', 'we must shed our own circumferences',
           'hello', 'Hello.', 'Good luck.', '7A35090F', '181F01E57A35090F', '845145127', '761', '167', '107', '229', '1595277641']
n = 0
for s in STRINGS:
    for v in variants(s):
        check('string %r' % v, v.encode()); n += 1
        check('string upper %r' % v.upper(), v.upper().encode()); n += 1

onions = set()
for root in sys.argv[1:]:
    for dp, dn, fn in os.walk(root) if os.path.isdir(root) else [(os.path.dirname(root), [], [os.path.basename(root)])]:
        if '.git' in dp:
            continue
        for f in fn:
            p = os.path.join(dp, f)
            try:
                if os.path.getsize(p) > 50 * 1024 * 1024:
                    continue
                data = open(p, 'rb').read()
            except OSError:
                continue
            check('file ' + p, data); n += 1
            # also hash the file with line endings normalised and stripped
            try:
                t = data.decode('utf-8')
                for v in (t.replace('\r\n', '\n'), t.strip(), t.replace('\r\n', '\n').strip() + '\n'):
                    check('file-normalised ' + p, v.encode()); n += 1
                for line in t.splitlines():
                    line = line.strip()
                    if line:
                        check('line %s | %r' % (p, line[:60]), line.encode()); n += 1
                for m in re.findall(r'[a-z2-7]{16}\.onion|[a-z2-7]{56}\.onion', t):
                    onions.add(m)
            except UnicodeDecodeError:
                pass
for o in sorted(onions):
    for v in variants(o):
        check('onion %r' % v, v.encode()); n += 1
print('onion addresses found in the archive:', len(onions), sorted(onions)[:40])
print('candidates hashed:', n)
print('HITS:', hits if hits else 'none')
