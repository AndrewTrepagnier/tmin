#!/usr/bin/env bash
# Test TMIN in a fresh environment: build, install into a new venv, run from an
# empty directory (no examples/) to verify bundled template + example work.
# Usage: from repo root, run:  bash scripts/test_fresh_install.sh
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/tmin_fresh_test_$$"
mkdir -p "$WORK"
trap 'rm -rf "$WORK"' EXIT

echo "=== Fresh install test: $WORK ==="
PYTHON="${REPO_ROOT}/.venv/bin/python"
[[ ! -x "$PYTHON" ]] && PYTHON=$(command -v python3 || command -v python)
echo "   Using: $PYTHON"
echo "1. Building wheel..."
"$PYTHON" -m pip install -q build 2>/dev/null || true
cd "$REPO_ROOT"
"$PYTHON" -m build --wheel -q -o "$WORK/wheels"
WHEEL=$(echo "$WORK"/wheels/*.whl)
echo "   Built: $WHEEL"

echo "2. Creating fresh venv..."
"$PYTHON" -m venv "$WORK/venv"
if [[ -d "$WORK/venv/Scripts" ]]; then
  PIP="$WORK/venv/Scripts/pip"
  TMIN="$WORK/venv/Scripts/tmin"
  PY="$WORK/venv/Scripts/python"
else
  PIP="$WORK/venv/bin/pip"
  TMIN="$WORK/venv/bin/tmin"
  PY="$WORK/venv/bin/python"
fi

echo "3. Installing tmin into venv (no repo context)..."
"$PIP" install -q "$WHEEL"

echo "4. Running tmin from empty directory (must use bundled example)..."
cd "$WORK"
mkdir -p run_here
cd run_here
# No examples/ here -> code must use package's bundled JSON and template
if [[ -x "$TMIN" ]]; then
  "$TMIN" 2>&1
else
  "$PY" -m tmin.report 2>&1
fi

echo "5. Checking output..."
MEMO="output/engineering_memorandum.txt"
if [[ ! -f "$MEMO" ]]; then
  echo "FAIL: $MEMO not created"
  exit 1
fi
if [[ ! -s "$MEMO" ]]; then
  echo "FAIL: $MEMO is empty"
  exit 1
fi
echo "   OK: $MEMO exists and has content"
grep -q "ENGINEERING MEMORANDUM" "$MEMO" || { echo "FAIL: memo content wrong"; exit 1; }
echo "=== Fresh install test PASSED ==="
