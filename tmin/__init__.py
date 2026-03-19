"""
tmin — pipe minimum thickness analysis.

Quick start::

    import tmin

    input_dict = {
        "pressure": 285,
        "nps": 8,
        "schedule": 40,
        "pressure_class": 150,
        "metallurgy": "Intermediate/Low CS",
        "yield_stress": 35000,
        "current_thickness": 0.112,
    }

    instance = tmin.TMIN(input_dict)
    result   = instance.calculate()
    print(instance.report())
"""

from .tmin_class import TMIN
from .core_exp import PIPE

__all__ = ["TMIN", "PIPE"]
