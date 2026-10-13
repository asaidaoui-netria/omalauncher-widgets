#!/usr/bin/env bash
# Refuses a commit that would publish anything listed in local.env: the two addresses and PRIVATE_WORDS. It checks
# everything staged, so it's the pre-commit hook: ln -s ../../tools/check-public.sh .git/hooks/pre-commit
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
[ -f local.env ] || exit 0
set -a; . ./local.env; set +a
pat=$(printf '%s\n' "${MAC_IP:-}" "${PHONE_IP:-}" | grep -v '^$' | sed 's/\./\\./g' | paste -sd'|' -)
pat=$(printf '%s\n' "$pat" "${PRIVATE_WORDS:-}" | grep -v '^$' | paste -sd'|' -)
[ -n "$pat" ] || exit 0
if git grep --cached -nIiE -e "$pat"; then
  echo "check-public: the lines above contain private details from local.env; not committing." >&2
  exit 1
fi
