"""
Engineering memorandum report utilities.

Provides template loading and placeholder filling for the text-based
engineering memorandum.  The primary user interface is now the ``TMIN``
class (see ``tmin_class.py``); this module supplies helpers used internally.
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional

_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_TEMPLATE_PATH = _PACKAGE_DIR / "templates" / "engineering_memorandum.txt"


def get_default_template_path() -> Path:
    return _DEFAULT_TEMPLATE_PATH


def load_template(path: Optional[Path] = None) -> str:
    p = Path(path) if path is not None else get_default_template_path()
    return p.read_text(encoding="utf-8")


def extract_placeholders(template_text: str) -> list:
    seen: set = set()
    order: list = []
    for m in re.finditer(r"\[([^\]]+)\]", template_text):
        placeholder = m.group(0)
        if placeholder not in seen:
            seen.add(placeholder)
            order.append(placeholder)
    return order


def _normalize_key(key: str) -> str:
    k = key.strip()
    if k.startswith("[") and k.endswith("]"):
        k = k[1:-1].strip()
    return k


def fill_template(template_text: str, values: Dict[str, Any]) -> str:
    """Replace each ``[placeholder]`` in *template_text* with matching values."""
    by_bracket: Dict[str, str] = {}
    for k, v in values.items():
        norm = _normalize_key(k)
        bracket_key = f"[{norm}]"
        by_bracket[bracket_key] = "" if v is None else str(v).strip()

    def repl(m: re.Match) -> str:
        full = m.group(0)
        return by_bracket.get(full, full)

    return re.sub(r"\[[^\]]+\]", repl, template_text)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point (``tmin`` command)."""
    import argparse
    parser = argparse.ArgumentParser(
        description="TMIN: pipe thickness analysis and engineering memorandum report."
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run the bundled example and print the report to the terminal.",
    )
    args = parser.parse_args()

    if args.example:
        from .tmin_class import TMIN
        example = {
            "pressure": 285,
            "nps": 8,
            "schedule": 40,
            "pressure_class": 150,
            "metallurgy": "Intermediate/Low CS",
            "allowable_stress": 23333,
            "allowable_stress_code_year": "1966",
            "allowable_stress_code_source": "B31.3 Allowables",
            "current_thickness": 0.112,
            "Site Name": "Example Site",
            "Fixed Equipment Department": "Fixed Equipment",
            "Unit": "CRUDE UNIT",
            "Company": "Example Co.",
            "Pipe Circuit No.": "077-072-01",
            "Size": "8",
            "Circuit Fluid Service": "Spent Caustic",
            "Type of Equipment": "pipe",
            "subcomponent": "straight-run",
            "Author Name": "tmin",
            "Author Phone Number": "",
            "Inspection type": "RT",
            "TML number": "TML-01",
            "Current thickness to date": "0.112 in",
            "Internal/External": "internal",
            "Degradation Mechanism": "alkaline corrosion",
            "Incoming Outage timestamp": "January 2027",
            "SHE consequence level": "II",
            "failure types": "pinhole",
            "Consequence type": "fire scenario",
            "Date AR/T = 1": "01-Mar-2029",
            "CR": "5",
            "CR description": "General",
            "ESL Evaluation": "Acceptable to next outage",
            "AR/T Basis": "Calculated from inspection data",
            "AR/T progression": "Fill in by user",
            "General Notes": "",
        }
        inst = TMIN(example)
        print(inst.report())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
