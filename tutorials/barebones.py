"""Minimal workflow: tmin.analyze() then tmin.report(). Run from project root or tutorials/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tmin

if __name__ == "__main__":
    tmin.analyze()
    tmin.report()
