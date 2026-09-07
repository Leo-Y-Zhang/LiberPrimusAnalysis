#!/bin/sh
# Runs inside a Debian container: extract outguess payloads from every page image, with no key and
# with each key in keys.txt. Outputs land in /out/<key>/<image>.bin (empty results are removed).
set -u
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq outguess >/dev/null 2>&1 || { echo "outguess install failed"; exit 1; }
outguess 2>&1 | head -2
mkdir -p /out/nopass
for img in /img/*.jpg; do
  b=$(basename "$img" .jpg)
  outguess -r "$img" "/out/nopass/$b.bin" >/dev/null 2>&1
done
find /out/nopass -size 0 -delete
echo "nopass done: $(ls /out/nopass | wc -l) non-empty outputs"
while IFS= read -r key; do
  [ -z "$key" ] && continue
  d="/out/key_$(echo "$key" | tr -c 'A-Za-z0-9' '_')"
  mkdir -p "$d"
  for img in /img/*.jpg; do
    b=$(basename "$img" .jpg)
    outguess -k "$key" -r "$img" "$d/$b.bin" >/dev/null 2>&1
  done
  find "$d" -size 0 -delete
  n=$(ls "$d" | wc -l)
  echo "key '$key': $n non-empty outputs"
done < /work/keys.txt
echo "ALL DONE"
