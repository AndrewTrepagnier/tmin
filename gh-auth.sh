#!/bin/bash
# Run GitHub CLI (installed in .tools). Use: ./gh-auth.sh auth login
cd "$(dirname "$0")"
GH=".tools/gh_2.87.2_macOS_arm64/bin/gh"
if [[ ! -x "$GH" ]]; then
  echo "GitHub CLI not found. Run: curl -fsSL ... (see README)" 1>&2
  exit 1
fi
exec "$GH" "$@"
