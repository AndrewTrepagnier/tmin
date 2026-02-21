from .tables.od_table import trueOD
from .tables.wsrf import WSRF
from .tables.y_coeff import ferritic_steels_y, austenitic_steels_y, other_metals_y, nickel_alloy_N06690_y, nickel_alloys_N06617_N08800_N08810_N08825_y, cast_iron_y
from .tables.api_574_2025 import API574_CS_400F, API574_SS_400F
from .tables.api_574_2009 import API574_2009_TABLE_6
from .tables.ANSI_radii import ANSI_radii
from .report import generate_memorandum as _generate_memorandum

import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Dict, Any, Union
import matplotlib.pyplot as plt
from datetime import datetime
import sympy as sp
from sympy import symbols, latex, pprint




@dataclass
class PIPE:

    #########Initialize Characteristics of the Pipe and Service###############

    pressure: float  # Design pressure (psi)
    nps: float # Nominal pipe size in decimal form (e.g. '0.75', '1.5', '2')
    schedule: float  # Pipe schedule (10, 40, 80, 120, 160)
    pressure_class: Literal[150, 300, 600, 900, 1500, 2500]
    metallurgy: Literal["Intermediate/Low CS", "SS 316/316L", "SS 304/304L", "Inconel 625", "Other"]
    yield_stress: float # psi, yield stresses vary from year to year of manufactured piping, ensure the correct year's yield stress is used
    
    # Optional fields with defaults
    design_temp: Literal["<900" ,900, 950, 1000, 1050, 1100, 1150, 1200, 1250, "1250+" ] = 900 #Design temp in Fahrenheit
    pipe_config: Literal["straight", "90LR - Inner Elbow", "90LR - Outer Elbow"] = "straight"
    corrosion_rate: Optional[float] = None #Mils per Year (MPY) 
    default_retirement_limit: Optional[float] = None
    API_table : Literal["2025", "2009"] = "2025" # Optional, year 2025 is assumed if left blank
    joint_type: Literal["seamless"] = "seamless" # As of now, TMIN only supports seamless piping analysis, TODO: Add arc butt welded pipe configs

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
        """Get allowable stress based on yield stress (2/3 of yield stress)"""
        return self.yield_stress * (2/3)

    def get_outer_diameter(self) -> float:
        """Get outside diameter based on NPS"""
        return trueOD[self.nps]

    def get_y_coefficient(self) -> float:
        """Get Y coefficient from ASME B31.1 Table 104.1.2-1"""
        temp = self.round_temperature()
        if self.metallurgy in ("CS A106 GR B", "Intermediate/Low CS"):
            return self.ferritic_steels_y.get(temp, 0.4)
        elif self.metallurgy in ("SS 316/316S", "SS 316/316L", "SS 304/304L"):
            return self.austenitic_steels_y.get(temp, 0.4)
        else:
            return 0.4  # Default Y for Other / Inconel / unknown 

    def round_temperature(self) -> int:
        """Round design temperature to nearest table value for lookups"""
        if self.design_temp == "<900":
            return 900
        elif self.design_temp == "1250+":
            return 1250
        else:
            return self.design_temp 

    ##########################
    # Static methods
    ##########################


    @staticmethod
    def inches_to_mils(inches_value: float) -> float: 
        """Convert inches to mils (1 inch = 1000 mils)"""
        return inches_value * 1000
    
    @staticmethod
    def mils_to_inches(mils_value: float) -> float:
        """Convert mils to inches (1000 mils = 1 inch)"""
        return mils_value * 0.001


    def get_table_info(self):
        """Build enriched pipe data from table lookups for use in tmin_pressure / tmin_structural."""
        outer_diameter = self.get_outer_diameter()
        inner_diameter = self.get_inner_diameter()
        allowable_stress = self.get_allowable_stress()  # not technically a table
        joint_type = self.get_joint_type()
        y_coefficient = self.get_y_coefficient()
        centerline_radius = self.get_centerline_radius()

        table_info = {
            'outer_diameter': outer_diameter,
            'inner_diameter': inner_diameter,
            'allowable_stress': allowable_stress,
            'joint_type': joint_type,
            'y_coefficient': y_coefficient,
            'centerline_radius': centerline_radius,
            'API574_CS_400F': self.API574_CS_400F,
            'API574_SS_400F': self.API574_SS_400F,
            'API574_2009_TABLE_6': self.API574_2009_TABLE_6
        }
        return table_info



    #####################################################################################
    # Pressure Containing Thickness Requirements Per ASME B31.3 Codes
    #####################################################################################

    # MVP: simple hoop stress calculation, use lookup tables, store data to compare to
    # structural and current thickness. Pass enriched pipe_data (no self refs) to eliminate state dependencies.
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
        
        """
        Minimum wall thickness for pressure design.
        ASME B31.1 Para. 304.1.2a Eq. 3a: t = (P*D) / (2*(S*E*W + P*Y))
        Seamless: E = 1.0, W = 1.0.
        """
        if pipe_config == 'straight':
            sew = allowable_stress * joint_efficiency * weld_strength_reduction
            pressure_thickness = (pressure * outer_diameter) / (2 * (sew + pressure * y_coefficient))
            return pressure_thickness
        # elif pipe_config == '90LR - Inner Elbow':
        #     radius = centerline_radius - outer_diameter/2
        #     intrados_factor = (4*(radius/outer_diameter) - 1) / (4*(radius/outer_diameter) - 2)
        #     return (pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(intrados_factor) + pressure * y_coefficient))
        
        # elif pipe_config == '90LR - Outer Elbow':
        #     radius = centerline_radius + outer_diameter/2
        #     extrados_factor = (4*(radius/outer_diameter) + 1) / (4*(radius/outer_diameter) + 2)
        #     return (pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(extrados_factor) + pressure * y_coefficient))
           
        else:
            raise ValueError(f"Unable to calculate minimum thickness for invalid pipe configuration: {pipe_config}")




    #####################################################################################
    # Structural Thickness Requirements Per API 574 Codes
    #####################################################################################


# Structural tmin: API 2025 only (multiple year selections removed). Simplified.
    def tmin_structural(self, pipe_data: Dict[str, Any]) -> float:
        """
        Get minimum structural thickness requirement using enriched pipe data.
        API 574 (2025) only.
        """
        nps = pipe_data['nps']
        pressure_class = pipe_data['pressure_class']
        metallurgy = pipe_data['metallurgy']
        API_table = pipe_data.get('API_table', '2025')
        if API_table != "2025":
            raise ValueError(f"Only API 2025 is supported; got API_table={API_table!r}")

        if metallurgy == "Intermediate/Low CS":
            structural_requirement = pipe_data['API574_CS_400F'][nps][pressure_class]
        elif metallurgy in ["SS 316/316L", "SS 304/304L"]:
            structural_requirement = pipe_data['API574_SS_400F'][nps][pressure_class]
        else:
            structural_requirement = pipe_data['API574_CS_400F'][nps][pressure_class]

        if structural_requirement is None:
            raise ValueError(f"No structural thickness requirement found for NPS {nps}, "
                           f"pressure class {pressure_class}, metallurgy {metallurgy}")

        return structural_requirement

    # Take pipe data -> compute pressure tmin -> compare to tabulated structural tmin.
    # RED = at or below governing minimum. YELLOW = above minimum, nearing limit (report corrosion allowance left).
    def minimum_thickness_calculator(
        self,
        pipe_data: Dict[str, Any],
        current_thickness: float,
        default_retirement_limit: Optional[float] = None,
        output_txt_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Minimum thickness check: compute pressure tmin and tabulated structural tmin.
        Governing limit is the larger (closer to current). RED if current <= governing minimum;
        YELLOW if above minimum, with corrosion allowance remaining to the governing limit.
        """
        tmin_pressure = self.tmin_pressure(pipe_data)
        tmin_structural = self.tmin_structural(pipe_data)

        if tmin_pressure >= tmin_structural:
            governing_thickness = tmin_pressure
            governing_type = "pressure"
        else:
            governing_thickness = tmin_structural
            governing_type = "structural"

        if current_thickness <= governing_thickness:
            deficit = governing_thickness - current_thickness
            raised_flag = {
                "flag": "RED",
                "status": "IMMEDIATE_RETIREMENT",
                "message": f"Below {governing_type} minimum - not acceptable for continued operation",
                "deficit_to_governing": deficit,
            }
            if governing_type == "pressure":
                raised_flag["pressure_deficit"] = deficit
            if output_txt_path:
                self.write_pressure_tmin_report(pipe_data, tmin_pressure, current_thickness, output_txt_path)
        else:
            if default_retirement_limit is not None and default_retirement_limit > governing_thickness:
                next_retirement_limit = default_retirement_limit
                retirement_type = "company-specified"
            else:
                next_retirement_limit = governing_thickness
                retirement_type = f"Retirement limit governed by {governing_type} design"
            corrosion_allowance = current_thickness - next_retirement_limit
            raised_flag = {
                "flag": "YELLOW",
                "status": "NEARING_LIMIT",
                "message": f"Nearing {governing_type} minimum; {corrosion_allowance:.4f} in corrosion allowance remaining",
                "corrosion_allowance": corrosion_allowance,
                "next_retirement_limit": next_retirement_limit,
                "retirement_type": retirement_type,
            }
            if output_txt_path:
                self.write_pressure_tmin_report(pipe_data, tmin_pressure, current_thickness, output_txt_path)

        return {
            "current_thickness": current_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,
            **raised_flag,
        }

    def write_pressure_tmin_report(
        self,
        pipe_data: Dict[str, Any],
        tmin_pressure: float,
        current_thickness: float,
        path: str,
    ) -> None:
        """Write a simple txt file: inputs, pressure tmin math, and conclusion."""
        P = pipe_data["pressure"]
        D = pipe_data["outer_diameter"]
        S = pipe_data["allowable_stress"]
        joint_info = pipe_data.get("joint_type", {"joint_efficiency": 1.0, "weld_strength_reduction": 1.0})
        E = joint_info["joint_efficiency"]
        W = joint_info["weld_strength_reduction"]
        Y = pipe_data["y_coefficient"]
        lines = [
            "Pressure tmin report",
            "=" * 40,
            "",
            "Inputs:",
            f"  P = {P} psi   D = {D} in   S = {S:.0f} psi",
            f"  E = {E}   W = {W}   Y = {Y}",
            "",
            "ASME B31.1 Eq. 3a:  tmin = (P*D) / (2*(S*E*W + P*Y))",
            f"  tmin = ({P}*{D}) / (2*({S*E*W:.0f} + {P*Y:.0f})) = {tmin_pressure:.6f} in",
            "",
            f"  tmin_pressure (required) = {tmin_pressure:.6f} in",
            f"  current thickness        = {current_thickness:.6f} in",
        ]
        with open(path, "w") as f:
            f.write("\n".join(lines))

    def generate_memorandum(
        self,
        json_path: Union[Path, str],
        output_path: Union[Path, str],
        current_thickness: Optional[float] = None,
        *,
        template_path: Optional[Path] = None,
        append_tmin: bool = False,
        tmin_output_path: Optional[Union[Path, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate the engineering memorandum from a JSON file, using this pipe for tmin when current_thickness is given.

        Fills [placeholder] blocks in the template from the JSON; if current_thickness is provided,
        runs the pressure tmin calculation and can override Design Pressure, Design Temperature,
        Nominal Thickness, current thickness, and Current tmin in the memo, and optionally append
        or write the tmin inputs/outputs to the memo or a separate file.

        Args:
            json_path: Path to JSON file mapping placeholder names to values.
            output_path: Where to write the filled memorandum.
            current_thickness: If provided, run tmin and merge results into the memo (inches).
            template_path: Optional template path; default uses package template.
            append_tmin: If True and current_thickness given, append tmin calculations to memo.
            tmin_output_path: If set, also write tmin calculations to this file.

        Returns:
            Dict with "memorandum_path", and optionally "tmin_result", "tmin_section_path".
        """
        return _generate_memorandum(
            Path(output_path),
            json_path=Path(json_path),
            template_path=Path(template_path) if template_path is not None else None,
            append_tmin=append_tmin,
            tmin_output_path=Path(tmin_output_path) if tmin_output_path is not None else None,
            pipe=self,
            current_thickness=current_thickness,
        )


# Helper Function pile, everything below this ignore for now

    def get_inner_diameter(self) -> float:
        """Get nominal inside diameter based on schedule and NPS"""
        from .tables.id_table import trueID_10, trueID_40, trueID_80, trueID_120, trueID_160
        
        if self.schedule == 10:
            return trueID_10.get(self.nps)
        elif self.schedule == 40:
            return trueID_40.get(self.nps)
        elif self.schedule == 80:
            return trueID_80.get(self.nps)
        elif self.schedule == 120:
            return trueID_120.get(self.nps)
        elif self.schedule == 160:
            return trueID_160.get(self.nps)
        else:
            raise ValueError(f"Invalid schedule: {self.schedule}")



    def get_centerline_radius(self) -> float:
        """Get centerline radius for the pipe's NPS from ANSI standard"""
        return ANSI_radii[self.nps]
    
    def get_joint_type(self) -> Dict[str, float]:
        """Get joint efficiency and weld strength reduction factors"""
        if self.joint_type == 'seamless':
            return {
                'joint_efficiency': 1.0,
                'weld_strength_reduction': 1.0
            }
        else:
            raise ValueError(f"Welded pipe analysis (joint_type='{self.joint_type}') is not yet supported. "
                           f"Currently only seamless pipe analysis is available.")


# Nice to haves later

   
    @staticmethod
    def _calculate_time_elapsed(year_inspected: int, month_inspected: Optional[int] = None) -> float:
        """
        Calculate precise time elapsed since inspection date
        
        Args:
            year_inspected: Year of inspection
            month_inspected: Month of inspection (1-12), defaults to January if None
            
        Returns:
            float: Time elapsed in years (including fractional years for months)
            
        Raises:
            ValueError: If inspection date is in the future
        """
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Use January(1) if no month provided (most conservative assumption)
        inspection_month = month_inspected if month_inspected is not None else 1
        
        years_diff = current_year - year_inspected
        months_diff = current_month - inspection_month
        
        # Convert to total years elapsed
        time_elapsed = years_diff + (months_diff / 12)
        
        if time_elapsed < 0:
            raise ValueError(f"Inspection date {year_inspected}-{inspection_month:02d} cannot be in the future")
        
        return time_elapsed
    
    @staticmethod
    def _format_inspection_date(year: int, month: Optional[int] = None) -> str:
        """Format inspection date for display"""
        month_str = f"{month:02d}" if month is not None else "01"
        return f"{year}-{month_str}"

        # AR/T Calculations

