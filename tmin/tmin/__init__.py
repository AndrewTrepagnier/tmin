"""
tmin: pipe minimum thickness analysis and engineering memorandum reports.

Two main entry points::

    import tmin
    tmin.analyze()   # Terminal report: pressure & structural thicknesses
    tmin.report()    # Write full engineering memorandum to OUTPUTS/

Both read from Input/ (first .json). Use analyze() for a quick check, then
report() to generate the memorandum text file.
"""

from .core_exp import PIPE
from .report import analyze, report, run, run_report_from_input, get_default_template_path

__all__ = [
    "analyze",
    "report",
    "run",
    "PIPE",
    "run_report_from_input",
    "get_default_template_path",
]
