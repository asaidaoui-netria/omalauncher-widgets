#!/usr/bin/env bash
# Installs a widget on the phone through the launcher's terminal: tools/push.sh widgets/10-today.owl [PHONE_SHA256]
# The phone's copy is replaced only if it's still the last committed version (or the checksum given), so push before
# committing. The Mac's and the phone's addresses come from local.env (see local.env.example).
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./local.env; set +a
f=$1
w=$(basename "$f")
was=${2:-$(git show "HEAD:$f" | shasum -a 256 | cut -d' ' -f1)}
mkdir -p out
sed -e "s/@WIDGET@/$w/g" -e "s/@SHA@/$was/" -e "s/@MAC_IP@/$MAC_IP/g" tools/install-widget.sh > out/install.sh
pkill -f "serve.py (send|recv|save) 87" || true
python3 tools/serve.py send 8769 out/install.sh > /dev/null &
python3 tools/serve.py send 8771 "$f" > /dev/null &
python3 tools/serve.py save 8768 "out/${w%.owl}.screen.png" > /dev/null &
echo "In the phone's launcher terminal, type:  bash < /dev/tcp/$MAC_IP/8769"
python3 tools/serve.py recv 8767
echo "Screen preview: out/${w%.owl}.screen.png"
