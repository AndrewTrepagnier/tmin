"""
PMG (pipe minimum gauge) thickness for %CAC — user-provided NPS table.

Ranges::
    3/4" through 2"   → 0.083"
    3" through 18"    → 0.134"
    20" through 22"   → 0.148"
    24"               → 0.165"

NPS 1/2" (0.5) is not listed; we use the 3/4"–2" value (0.083") as the same
small-bore bracket. NPS between defined brackets (e.g. between 2" and 3") returns
``None`` so callers can skip %CAC or supply an override.
"""

from __future__ import annotations

from typing import Optional


def pmg_from_nps(nps: float) -> Optional[float]:
    """Return PMG wall thickness (inches) for nominal pipe size, or ``None`` if unknown."""
    n = float(nps)
    if n <= 0:
        return None

    # 1/2" not in table — align with 3/4"–2" small line
    if n < 0.75:
        return 0.083
    if n <= 2.0:
        return 0.083
    if n < 3.0:
        return None
    if n <= 18.0:
        return 0.134
    if n < 20.0:
        return None
    if n <= 22.0:
        return 0.148
    if n < 24.0:
        return None
    if n <= 24.0:
        return 0.165
    return None
