from .asmetables.od_table import trueOD_40, trueOD_80, trueOD_10, trueOD_120, trueOD_160
from .asmetables.wsrf import WSRF
from .asmetables.y_coeff import ferritic_steels_y, austenitic_steels_y, other_metals_y, nickel_alloy_N06690_y, nickel_alloys_N06617_N08800_N08810_N08825_y, cast_iron_y
from .asmetables.api_574_2025 import API574_CS_400F, API574_SS_400F
from .asmetables.api_574_2009 import API574_2009_TABLE_6
from .asmetables.ANSI_radii import ANSI_radii

import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional, Dict
import matplotlib.pyplot as plt
from datetime import datetime

@dataclass
class PIPE:

    schedule: str  # Pipe schedule (10, 40, 80, 120, 160)
    nps: str  # Nominal pipe size (e.g., '2', '3/4', '1-1/2')
    pressure: float  # Design pressure (psi)
    pressure_class: Literal[150, 300, 600, 900, 1500, 2500]
    metallurgy: Literal["Intermediate/Low CS", "SS 316/316L", "SS 304/304L", "Inconel 625", "Other"]
    allowable_stress: float # User defined Allowable Stress
    design_temp: Literal["<900" ,900, 950, 1000, 1050, 1100, 1150, 1200, 1250, "1250+" ] = 900 
    pipe_config: Literal["straight", "90LR - Inner Elbow", "90LR - Outer Elbow"] = "straight"
    corrosion_rate: Optional[float] = None #mpy 
    default_retirement_limit: Optional[float] = None
    API_table : Literal["2025", "2009"] = "2025"

    VALID_PIPE_TYPES = ["straight", "bend-90", "bend-45", "tee", "elbow"]
    VALID_SCHEDULES = ["10", "40", "80", "120", "160"]

    trueOD_10 = trueOD_10
    trueOD_40 = trueOD_40
    trueOD_80 = trueOD_80
    trueOD_120 = trueOD_120
    trueOD_160 = trueOD_160
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

    def _convert_nps_to_float(self, nps_str: str) -> float:
        """Convert NPS string to float, handling fractions like '3/4'"""
        try:
            return float(nps_str)
        except ValueError:
            try:
                if '-' in nps_str:
                    parts = nps_str.split('-')
                    if len(parts) == 2:
                        whole = float(parts[0])
                        fraction = eval(parts[1])
                        return whole + fraction
                    else:
                        raise ValueError(f"Invalid NPS format: {nps_str}")
                else:
                    return eval(nps_str)
            except:
                raise ValueError(f"Could not convert NPS '{nps_str}' to float")

    def _convert_nps_to_table_key(self, nps_str: str) -> str:
        """Convert NPS to table key format - strips .0 from whole numbers"""
        nps_float = self._convert_nps_to_float(nps_str)
        nps_str_formatted = str(nps_float)
        if nps_str_formatted.endswith('.0'):
            nps_str_formatted = nps_str_formatted[:-2]
        return nps_str_formatted

    def allowable(self, Syield) -> float:
        return Syield*(2/3)

    def get_OD(self) -> float:
        """Get outside diameter based on schedule and NPS"""
        if self.schedule == "10":
            return self.trueOD_10.get(self.nps)
        elif self.schedule == "40":
            return self.trueOD_40.get(self.nps)
        elif self.schedule == "80":
            return self.trueOD_80.get(self.nps)
        elif self.schedule == "120":
            return self.trueOD_120.get(self.nps)
        elif self.schedule == "160":
            return self.trueOD_160.get(self.nps)
        else:
            raise ValueError(f"Invalid schedule: {self.schedule}")

    def get_ID(self) -> float:
        """Get nominal inside diameter based on schedule and NPS"""
        from .asmetables.id_table import trueID_10, trueID_40, trueID_80, trueID_120, trueID_160
        
        if self.schedule == "10":
            return trueID_10.get(self.nps)
        elif self.schedule == "40":
            return trueID_40.get(self.nps)
        elif self.schedule == "80":
            return trueID_80.get(self.nps)
        elif self.schedule == "120":
            return trueID_120.get(self.nps)
        elif self.schedule == "160":
            return trueID_160.get(self.nps)
        else:
            raise ValueError(f"Invalid schedule: {self.schedule}")

    def get_Y_coefficient(self) -> float:
        """Get Y coefficient from ASME B31.1 Table 104.1.2-1"""
        if self.metallurgy =='CS A106 GR B':
            return self.ferritic_steels_y[self.round_temp()]
        elif self.metallurgy =='SS 316/316S':
            return self.austenitic_steels_y[self.round_temp()]
        elif self.metallurgy =='Other':
            return self.other_metals_y[self.round_temp()]
        elif self.metallurgy =='Nickel Alloy':
            return self.nickel_alloy_N06690_y[self.round_temp()]
        elif self.metallurgy =='Nickel Alloys':
            return self.nickel_alloys_N06617_N08800_N08810_N08825_y[self.round_temp()]
        elif self.metallurgy =='Cast Iron':
            return self.cast_iron_y[self.round_temp()]
        else:
            return 0.4 # Default Y value for unknown metallurgy
        
    def round_temp(self) -> int:
        """Used in temperature dependent look-up tables"""
        if self.design_temp == "<900":
            return 900
        else:
            return self.design_temp 
        
    def get_radii(self) -> float:
        """Get centerline radius for the pipe's NPS from ANSI standard"""
        nps_key = self._convert_nps_to_table_key(self.nps)
        
        radius = ANSI_radii.get(nps_key)
        
        if radius is None:
            raise ValueError(f"No ANSI radius data available for NPS {self.nps}")
        
        return radius

    def tmin_pressure(self, joint_type='Seamless') -> float:
        """
        Calculate minimum wall thickness for pressure design
        Based on ASME B31.1 Para. 304.1.2a Eq. 3a
        
        For seamless pipe (most common): E = 1.0, W = 1.0
        For welded pipe: E and W depend on temperature and weld type
        """
        D = self.get_OD()
        if D is None:
            raise ValueError(f"Invalid NPS {self.nps} for schedule {self.schedule}")
        
        S = self.allowable_stress  # User-defined allowable stress
        
        # Joint efficiency and weld strength reduction factors
        if joint_type == 'Seamless':
            E = 1.0  # Joint efficiency factor for seamless pipe
            W = 1.0  # Weld strength reduction factor for seamless pipe
        else:
            # For welded pipe, E and W depend on temperature and weld type
            # This would need to be implemented based on ASME B31.1 tables
            raise ValueError(f"Welded pipe analysis (joint_type='{joint_type}') is not yet supported. "
                           f"Currently only seamless pipe analysis is available. "
                           f"Support for seam pipe is under development.")
        
        Y = self.get_Y_coefficient()
        if Y is None:
            raise ValueError(f"No Y coefficient available for NPS {self.nps}")
        
        if self.pipe_config == 'straight':
            tmin_pressure = (self.pressure * D) / (2 * (S * E * W + self.pressure * Y))
            return tmin_pressure
        
        elif self.pipe_config == '90LR - Inner Elbow':
            R_ = self.get_radii()
            def intrados(R, D):
                return (4*(R/D) - 1) / (4*(R/D) - 2)
            def extrados(R, D): 
                return (4*(R/D) + 1) / (4*(R/D) +2)

            if self.pipe_config == '90LR - Outer Elbow':
                return (self.pressure * D) / (2 * ((S*E*W)/(intrados(R_, D)) + self.pressure * Y))
        
            elif self.pipe_config == '90LR - Outer Elbow':
                return (self.pressure * D) / (2 * ((S*E*W)/(extrados(R_, D)) + self.pressure * Y))
        
    def tmin_structural(self) -> float:
        """API 574 Table D.2"""
        if self.API_table == "2025":
            nps_key = self._convert_nps_to_table_key(self.nps)
            min_structural = self.API574_CS_400F[nps_key][self.pressure_class]
            return min_structural
        
        else:
            nps_key = self._convert_nps_to_table_key(self.nps)
            min_structural = self.API574_2009_TABLE_6[nps_key]["default_minimum_structural_thickness"]
            return min_structural
    
    def life_span(self, excess, corrosion_rate) -> float:
        return np.floor(self.mil_conv(excess)*corrosion_rate)

    def mil_conv(self, a): # Converts to mils
        return a*1000

    # Old functions commented out for clarity and reference


    # def percent_RL(self, actual_thickness):
    #     """
    #     Calculate percentage of retirement limit (Table 5) remaining
    #     RL = actual thickness / retirement limit from Table 5
    #     """
    #     RL = self.table5_1_RL.get(self.nps)
    #     if RL is None:
    #         raise ValueError(f"No retirement limit available for NPS {self.nps}")
    #     percent_remaining = (actual_thickness / RL) * 100
    #     return percent_remaining

    # def check_RL_status(self, actual_thickness):
    #     """
    #     Check if pipe meets retirement limit requirements
    #     Returns status and percentage remaining
    #     """
    #     RL = self.table5_1_RL.get(self.nps)
    #     if RL is None:
    #         return {"status": "No RL data", "percent_remaining": None}
    #     percent_remaining = (actual_thickness / RL) * 100
    #     if actual_thickness >= RL:
    #         status = "Above RL"
    #     else:
    #         status = "Below RL - Consider Retirement"
    #     return {
    #             "status": status,
    #             "retirement_limit": RL,
    #             "actual_thickness": actual_thickness,
    #             "percent_remaining": percent_remaining
    #         }

    # def compare_thickness(self, actual_thickness, temp_f=1000, joint_type='Seamless'):
    #     """
    #     Comprehensive thickness analysis comparing actual vs calculated t-min and RL
    #     Returns comparison metrics for both pressure design and retirement limit
    #     """
    #     # Calculate pressure design requirements
    #     tmin = self.calculate_tmin_pressure(temp_f, joint_type)
    #     tmin_excess = actual_thickness - tmin
    #     tmin_percent_excess = (tmin_excess / actual_thickness) * 100
    #     # Check retirement limit
    #     rl_status = self.check_RL_status(actual_thickness)
    #     return {
    #             'actual_thickness': actual_thickness,
    #             'calculated_tmin': tmin,
    #             'tmin_excess': tmin_excess,
    #             'tmin_percent_excess': tmin_percent_excess,
    #             'rl_status': rl_status['status'],
    #             'retirement_limit': rl_status['retirement_limit'],
    #             'rl_percent_remaining': rl_status['percent_remaining'],
    #             'pressure_design_adequate': tmin_excess > 0,
    #             'rl_adequate': actual_thickness >= rl_status['retirement_limit'] if rl_status['retirement_limit'] else None
    #         }

    #####################################################################################
    # ANALYSIS
    ####################################################################################

    def analysis(self, measured_thickness: float, year_inspected: Optional[int] = None, joint_type='Seamless'):
        """
        Analyze pipe thickness against pressure and structural requirements
        
        Args:
            measured_thickness: Thickness measured during inspection (inches)
            year_inspected: Year when thickness was measured (e.g., 2020)
            joint_type: Joint type for calculations
            
        Returns:
            Dict with analysis results and governing factor
        """
        
        # Calculate present-day actual thickness based on inspection year and corrosion rate
        if year_inspected is not None and self.corrosion_rate is not None:
            current_year = 2025
            years_elapsed = current_year - year_inspected
            
            if years_elapsed < 0:
                raise ValueError(f"Inspection year {year_inspected} cannot be in the future")
            
            corrosion_loss_inches = (self.corrosion_rate * 0.001) * years_elapsed
            
            actual_thickness = measured_thickness - corrosion_loss_inches
            
            print(f"Time-based corrosion calculation:")
            print(f"  Measured thickness: {measured_thickness:.4f} inches (year {year_inspected})")
            print(f"  Years elapsed: {years_elapsed}")
            print(f"  Corrosion rate: {self.corrosion_rate} mpy")
            print(f"  Corrosion loss: {corrosion_loss_inches:.4f} inches")
            print(f"  Present-day thickness: {actual_thickness:.4f} inches")
            
        else:
            actual_thickness = measured_thickness
            print(f"Using measured thickness as present-day thickness: {actual_thickness:.4f} inches")
        
        tmin_pressure = self.tmin_pressure(joint_type)
        tmin_structural = self.tmin_structural()

        
        default_retirement_limit = self.default_retirement_limit
        
        limits = {
            "pressure": tmin_pressure,
            "structural": tmin_structural,
        }

        if limits["pressure"] >= limits["structural"]:
            governing_thickness = limits["pressure"]
            governing_type = "pressure"
            
        else:
            governing_thickness = limits["structural"]
            governing_type = "structural"

        print("-----------GOVERNING THICKNESS REQUIREMENT ----------")
        print(f"The pipe is {governing_type} thickness governed, pipe retirement is required at {governing_thickness} inches ({self.mil_conv(governing_thickness)} Mils)")
        print("-----------------------------------------------------")
        
        if default_retirement_limit is not None:
            if default_retirement_limit - actual_thickness >= 0:
                below_defaultRL = default_retirement_limit - actual_thickness
            else:
                print(f"The actual thickness is greater than default (company-specified) retirement limit by {actual_thickness - default_retirement_limit}")
                below_defaultRL = None
        else:
            below_defaultRL = None
        
        if governing_type == "structural":
            
            api574_value = self.tmin_structural()
            if api574_value < actual_thickness:
                corosion_allowance = actual_thickness - api574_value
                print(f"There is {corosion_allowance} inches ({self.mil_conv(corosion_allowance)} Mils) of corrosion allowance remaining")
            else:
                print(f"Actual Thickness is {api574_value - actual_thickness} inches below corresponding API 574 Structural Retirement Limit for {self.metallurgy}, Retirement Recommended, Fit For Service assessment is needed")
                corosion_allowance = None

        else:
            if governing_thickness >= actual_thickness:
                print(f"Actual Thickness is {governing_thickness - actual_thickness} inches ({self.mil_conv(governing_thickness - actual_thickness)} Mils), Retire Pipe Immediately, miniumum pressure containing thickness is not satisfied")
        
        return {
            "measured_thickness": measured_thickness,
            "year_inspected": year_inspected,
            "actual_thickness": actual_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            "default_retirement_limit": default_retirement_limit,
            "below_defaultRL": below_defaultRL,
            "api574_RL": self.tmin_structural(),
            "above_api574RL": corosion_allowance,
            "life_span": self.life_span(corosion_allowance, self.corrosion_rate) if corosion_allowance is not None and self.corrosion_rate is not None else None,
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,
        }

    def report(self, measured_thickness: float, year_inspected: Optional[int] = None, joint_type='Seamless') -> Dict[str, str]:
        """
        Generate analysis with text report and visualizations
        
        Args:
            measured_thickness: Thickness measured during inspection (inches)
            year_inspected: Year when thickness was measured (e.g., 2020)
            joint_type: Joint type for calculations
            
        Returns:
            Dict containing paths to generated files
        """
        from .report_generator import ReportGenerator
        from .visualization import ThicknessVisualizer
        
        # Perform analysis
        analysis_results = self.analysis(measured_thickness, year_inspected, joint_type)
        
        # Get the present-day actual thickness from results
        actual_thickness = analysis_results['actual_thickness']
        
        # Generate reports
        report_gen = ReportGenerator()
        full_report_path = report_gen.generate_report(self, analysis_results, actual_thickness)
        summary_report_path = report_gen.generate_summary_report(self, analysis_results, actual_thickness)
        
        # Generate visualizations
        visualizer = ThicknessVisualizer()
        number_line_path = visualizer.create_thickness_number_line(self, analysis_results, actual_thickness)
        comparison_chart_path = visualizer.create_comparison_chart(analysis_results, actual_thickness)
        
        return {
            "full_report": full_report_path,
            "summary_report": summary_report_path,
            "number_line_plot": number_line_path,
            "comparison_chart": comparison_chart_path,
            "analysis_results": analysis_results
        }