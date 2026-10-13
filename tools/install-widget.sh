# Runs on the phone; tools/push.sh fills in @WIDGET@, @SHA@ and @MAC_IP@. Replaces the widget only if the phone
# still has version @SHA@ (the last committed one, unless given), rolls it back if owl-check says it doesn't
# compile, and sends the result, the checksum, any runtime errors and the screen preview back to the computer.
cd ~/.config/omalauncher/widgets || exit 1
mkdir -p ~/.cache/stage
: > ~/.cache/stage/check.txt
if echo "@SHA@  @WIDGET@" | sha256sum -c --quiet 2>/dev/null; then
  cp @WIDGET@ ~/.cache/stage/@WIDGET@.prev
  cat < /dev/tcp/@MAC_IP@/8771 > ~/.cache/stage/@WIDGET@ && mv ~/.cache/stage/@WIDGET@ .
  rm -f .errors/@WIDGET@.txt
  owl-check @WIDGET@ >> ~/.cache/stage/check.txt 2>&1
  grep -q "doesn't compile" ~/.cache/stage/check.txt && { cp ~/.cache/stage/@WIDGET@.prev @WIDGET@; echo "ROLLED BACK" >> ~/.cache/stage/check.txt; }
else
  echo "@WIDGET@ changed on the phone: left alone" >> ~/.cache/stage/check.txt
  cat < /dev/tcp/@MAC_IP@/8771 > /dev/null
fi
# Runtime errors (a canvas over its 2000 drawing calls, say) show up once it has drawn for a while.
sleep 20
{ cat ~/.cache/stage/check.txt; sha256sum @WIDGET@; echo "--- errors:"; cat .errors/@WIDGET@.txt 2>&1; } > /dev/tcp/@MAC_IP@/8767
cat .preview/@WIDGET@.screen.png > /dev/tcp/@MAC_IP@/8768
cd
clear
