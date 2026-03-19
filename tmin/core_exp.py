import math
from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any
from datetime import datetime

from .tables.od_table import trueOD
from .tables.wsrf import WSRF
from .tables.y_coeff import (
    ferritic_steels_y, austenitic_steels_y, other_metals_y,
    nickel_alloy_N06690_y, nickel_alloys_N06617_N08800_N08810_N08825_y,
    cast_iron_y,
)
from .tables.api_574_2025 import API574_CS_400F, API574_SS_400F
from .tables.api_574_2009 import API574_2009_TABLE_6
from .tables.ANSI_radii import ANSI_radii


def _round_up(value: float, decimals: int = 3) -> float:
    """Round up (ceiling) to the specified number of decimal places.

    Uses an intermediate ``round`` to eliminate floating-point noise
    (e.g. 0.052000000000000001) before applying ``ceil``.
    """
    factor = 10 ** decimals
    shifted = round(value * factor, 6)
    return math.ceil(shifted) / factor


@dataclass
class PIPE:

    pressure: float
    nps: float
    schedule: float
    pressure_class: Literal[150, 300, 600, 900, 1500, 2500]
    metallurgy: Literal["Intermediate/Low CS", "SS 316/316L", "SS 304/304L", "Inconel 625", "Other"]
    allowable_stress: float

    design_temp: Literal["<900", 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, "1250+"] = 900
    pipe_config: Literal["straight", "90LR - Inner Elbow", "90LR - Outer Elbow"] = "straight"
    corrosion_rate: Optional[float] = None
    default_retirement_limit: Optional[float] = None
    API_table: Literal["2025", "2009"] = "2025"
    joint_type: Literal["seamless"] = "seamless"

    trueOD = trueOD
    WSRF = WSRF
    ferritic_steels_y = ferritic_steels_y
    austenitic_steels_y = austenitic_steels_y
    other_metals_y = other_metals_y
    nickel_alloy_N06690_y = nickel_alloy_N06690_y
    nickel_alloys_N06617_N08800_N08810_N08825_y = nickel_alloys_N06617_N08800_N08810_N08825_y
    cast_iron_y = cast_iron_y
    API574_CS_400F = API574_CS_400F
    API574_SS_400F = API574_SS_400F
    API574_2009_TABLE_6 = API574_2009_TABLE_6
    ANSI_radii = ANSI_radii

    def get_allowable_stress(self) -> float:
        return self.allowable_stress

    def get_outer_diameter(self) -> float:
        return trueOD[self.nps]

    def get_y_coefficient(self) -> float:
        temp = self.round_temperature()
        if self.metallurgy in ("CS A106 GR B", "Intermediate/Low CS"):
            return self.ferritic_steels_y.get(temp, 0.4)
        elif self.metallurgy in ("SS 316/316S", "SS 316/316L", "SS 304/304L"):
            return self.austenitic_steels_y.get(temp, 0.4)
        else:
            return 0.4

    def round_temperature(self) -> int:
        if self.design_temp == "<900":
            return 900
        elif self.design_temp == "1250+":
            return 1250
        else:
            return self.design_temp

    @staticmethod
    def inches_to_mils(inches_value: float) -> float:
        return inches_value * 1000

    @staticmethod
    def mils_to_inches(mils_value: float) -> float:
        return mils_value * 0.001

    def get_table_info(self) -> Dict[str, Any]:
        """Build enriched pipe data from table lookups for use in tmin_pressure / tmin_structural."""
        return {
            'outer_diameter': self.get_outer_diameter(),
            'inner_diameter': self.get_inner_diameter(),
            'allowable_stress': self.get_allowable_stress(),
            'joint_type': self.get_joint_type(),
            'y_coefficient': self.get_y_coefficient(),
            'centerline_radius': self.get_centerline_radius(),
            'API574_CS_400F': self.API574_CS_400F,
            'API574_SS_400F': self.API574_SS_400F,
            'API574_2009_TABLE_6': self.API574_2009_TABLE_6,
        }

    # -------------------------------------------------------------------------
    # Pressure tmin — ASME B31.3 Para. 304.1.2 Eq. 3a
    # t = (P*D) / (2*(S*E*W + P*Y))
    # -------------------------------------------------------------------------

    def tmin_pressure(self, pipe_data: Dict[str, Any]) -> float:
        outer_diameter = pipe_data['outer_diameter']
        pressure = pipe_data['pressure']
        pipe_config = pipe_data.get('pipe_config', 'straight')
        allowable_stress = pipe_data['allowable_stress']
        y_coefficient = pipe_data['y_coefficient']

        joint_info = pipe_data.get('joint_type', {'joint_efficiency': 1.0, 'weld_strength_reduction': 1.0})
        joint_efficiency = joint_info['joint_efficiency']
        weld_strength_reduction = joint_info['weld_strength_reduction']

        if outer_diameter is None:
            raise ValueError(f"Invalid NPS {pipe_data['nps']} for schedule {pipe_data['schedule']}")
        if y_coefficient is None:
            raise ValueError(f"No Y coefficient available for NPS {pipe_data['nps']}")

        if pipe_config == 'straight':
            sew = allowable_stress * joint_efficiency * weld_strength_reduction
            return (pressure * outer_diameter) / (2 * (sew + pressure * y_coefficient))
        else:
            raise ValueError(f"Unable to calculate minimum thickness for invalid pipe configuration: {pipe_config}")

    # -------------------------------------------------------------------------
    # Structural tmin — API 574
    # Returns None when API 574 does not provide a value for the metallurgy.
    # -------------------------------------------------------------------------

    def tmin_structural(self, pipe_data: Dict[str, Any]) -> Optional[float]:
        """
        Structural thickness per API 574.  Returns None when the standard does
        not cover the given metallurgy / table edition combination.
        """
        nps = pipe_data['nps']
        pressure_class = pipe_data['pressure_class']
        metallurgy = pipe_data['metallurgy']
        API_table = pipe_data.get('API_table', '2025')

        if API_table == "2025":
            if metallurgy == "Intermediate/Low CS":
                table = pipe_data.get('API574_CS_400F', API574_CS_400F)
                row = table.get(nps)
                if row is None:
                    return None
                return row.get(pressure_class)
            elif metallurgy in ("SS 316/316L", "SS 304/304L"):
                table = pipe_data.get('API574_SS_400F', API574_SS_400F)
                row = table.get(nps)
                if row is None:
                    return None
                return row.get(pressure_class)
            else:
                return None

        elif API_table == "2009":
            if metallurgy in ("Intermediate/Low CS",):
                table = pipe_data.get('API574_2009_TABLE_6', API574_2009_TABLE_6)
                row = table.get(nps)
                if row is None:
                    return None
                return row.get("default_minimum_structural_thickness")
            else:
                return None

        return None

    # -------------------------------------------------------------------------
    # Combined calculator (pressure + structural → governing)
    # -------------------------------------------------------------------------

    def minimum_thickness_calculator(
        self,
        pipe_data: Dict[str, Any],
        current_thickness: float,
        default_retirement_limit: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Compute pressure and structural tmin, determine governing thickness,
        and report corrosion allowance remaining.
        """
        tmin_pressure_raw = self.tmin_pressure(pipe_data)
        tmin_structural_raw = self.tmin_structural(pipe_data)

        tmin_p = _round_up(tmin_pressure_raw)
        tmin_s = _round_up(tmin_structural_raw) if tmin_structural_raw is not None else None

        if tmin_s is not None and tmin_s > tmin_p:
            governing_thickness = tmin_s
            governing_type = "structural"
        else:
            governing_thickness = tmin_p
            governing_type = "pressure"

        if default_retirement_limit is not None and default_retirement_limit > governing_thickness:
            retirement_limit = default_retirement_limit
        else:
            retirement_limit = governing_thickness

        corrosion_allowance = current_thickness - retirement_limit

        return {
            "current_thickness": current_thickness,
            "tmin_pressure": tmin_p,
            "tmin_structural": tmin_s,
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,
            "corrosion_allowance": _round_up(corrosion_allowance) if corrosion_allowance > 0 else 0.0,
        }

    # -------------------------------------------------------------------------
    # Helper look-ups
    # -------------------------------------------------------------------------

    def get_inner_diameter(self) -> float:
        from .tables.id_table import trueID_10, trueID_40, trueID_80, trueID_120, trueID_160

        schedule_map = {
            10: trueID_10, 40: trueID_40, 80: trueID_80,
            120: trueID_120, 160: trueID_160,
        }
        table = schedule_map.get(self.schedule)
        if table is None:
            raise ValueError(f"Invalid schedule: {self.schedule}")
        return table.get(self.nps)

    def get_centerline_radius(self) -> float:
        return ANSI_radii[self.nps]

    def get_joint_type(self) -> Dict[str, float]:
        if self.joint_type == 'seamless':
            return {'joint_efficiency': 1.0, 'weld_strength_reduction': 1.0}
        raise ValueError(
            f"Welded pipe analysis (joint_type='{self.joint_type}') is not yet supported. "
            f"Currently only seamless pipe analysis is available."
        )

    @staticmethod
    def _calculate_time_elapsed(year_inspected: int, month_inspected: Optional[int] = None) -> float:
        current_year = datetime.now().year
        current_month = datetime.now().month
        inspection_month = month_inspected if month_inspected is not None else 1
        years_diff = current_year - year_inspected
        months_diff = current_month - inspection_month
        time_elapsed = years_diff + (months_diff / 12)
        if time_elapsed < 0:
            raise ValueError(f"Inspection date {year_inspected}-{inspection_month:02d} cannot be in the future")
        return time_elapsed

    @staticmethod
    def _format_inspection_date(year: int, month: Optional[int] = None) -> str:
        month_str = f"{month:02d}" if month is not None else "01"
        return f"{year}-{month_str}"
