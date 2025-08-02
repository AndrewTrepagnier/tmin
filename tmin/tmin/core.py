from .tables.od_table import trueOD
from .tables.wsrf import WSRF
from .tables.y_coeff import ferritic_steels_y, austenitic_steels_y, other_metals_y, nickel_alloy_N06690_y, nickel_alloys_N06617_N08800_N08810_N08825_y, cast_iron_y
from .tables.api_574_2025 import API574_CS_400F, API574_SS_400F
from .tables.api_574_2009 import API574_2009_TABLE_6
from .tables.ANSI_radii import ANSI_radii

import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional, Dict
import matplotlib.pyplot as plt
from datetime import datetime
########### Checked as of 07/31/2025

@dataclass
class PIPE:

    #########Initialize Characteristics of the Pipe and Service###############

    pressure: float  # Design pressure (psi)
    design_temp: Literal["<900" ,900, 950, 1000, 1050, 1100, 1150, 1200, 1250, "1250+" ] = 900


    pipe_config: Literal["straight", "90LR - Inner Elbow", "90LR - Outer Elbow"] = "straight"
    metallurgy: Literal["Intermediate/Low CS", "SS 316/316L", "SS 304/304L", "Inconel 625", "Other"]
    yield_stress: float # User defined yield Stress

    schedule: float  # Pipe schedule (10, 40, 80, 120, 160)
    nps: float # Nominal pipe size (e.g., '2', '3/4', '1-1/2')
    pressure_class: Literal[150, 300, 600, 900, 1500, 2500]
    
    
    corrosion_rate: Optional[float] = None #mpy 
    default_retirement_limit: Optional[float] = None
    API_table : Literal["2025", "2009"] = "2025"


    VALID_PIPE_TYPES = ["straight", "bend-90", "bend-45", "tee", "elbow"]
    VALID_SCHEDULES = ["10", "40", "80", "120", "160"]

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

    def get_y_coefficient(self) -> float:
        """Get Y coefficient from ASME B31.1 Table 104.1.2-1"""
        if self.metallurgy =='CS A106 GR B':
            return self.ferritic_steels_y[self.round_temperature()]
        elif self.metallurgy =='SS 316/316S':
            return self.austenitic_steels_y[self.round_temperature()]
        elif self.metallurgy =='Other':
            return self.other_metals_y[self.round_temperature()]
        elif self.metallurgy =='Nickel Alloy':
            return self.nickel_alloy_N06690_y[self.round_temperature()]
        elif self.metallurgy =='Nickel Alloys':
            return self.nickel_alloys_N06617_N08800_N08810_N08825_y[self.round_temperature()]
        elif self.metallurgy =='Cast Iron':
            return self.cast_iron_y[self.round_temperature()]
        else:
            return 0.4 # Default Y value for unknown metallurgy
        
    def round_temperature(self) -> int:
        """Round design temperature to nearest table value for lookups"""
        if self.design_temp == "<900":
            return 900
        elif self.design_temp == "1250+":
            return 1250
        else:
            return self.design_temp 
        
    def get_centerline_radius(self) -> float:
        """Get centerline radius for the pipe's NPS from ANSI standard"""
        return ANSI_radii[self.nps]
    
    def inches_to_mils(self, inches_value: float) -> float: 
        """Convert inches to mils (1 inch = 1000 mils)"""
        return inches_value * 1000
    
    def mils_to_inches(self, mils_value: float) -> float:
        """Convert mils to inches (1000 mils = 1 inch)"""
        return mils_value * 0.001
    #####################################################################################
    # Pressure Contianing Thickness Requirements Per ASME B31.3 Codes
    #####################################################################################

    def get_pressure_thickness_requirement(self, joint_type='Seamless') -> float:
        """
        Calculate minimum wall thickness for pressure design
        Based on ASME B31.1 Para. 304.1.2a Eq. 3a
        
        For seamless pipe (most common): E = 1.0, W = 1.0
        For welded pipe: E and W depend on temperature and weld type
        """
        outer_diameter = self.get_outer_diameter()
        inner_diameter = self.get_inner_diameter()
        if outer_diameter is None:
            raise ValueError(f"Invalid NPS {self.nps} for schedule {self.schedule}")
        
        allowable_stress = self.get_allowable_stress()  # Users define stress pipe's yield stress, allowable stress is (2/3)*yield_stress per ASME B31.3
        
        # Joint efficiency and weld strength reduction factors
        if joint_type == 'Seamless':
            joint_efficiency = 1.0  # Joint efficiency factor for seamless pipe
            weld_strength_reduction = 1.0  # Weld strength reduction factor for seamless pipe
        else:
            # For welded pipe, E and W depend on temperature and weld type
            # This would need to be implemented based on ASME B31.1 tables
            raise ValueError(f"Welded pipe analysis (joint_type='{joint_type}') is not yet supported. "
                           f"Currently only seamless pipe analysis is available. "
                           f"Support for seam pipe is under development.")
        
        y_coefficient = self.get_y_coefficient()
        if y_coefficient is None:
            raise ValueError(f"No Y coefficient available for NPS {self.nps}")
        
        if self.pipe_config == 'straight':
            pressure_thickness = (self.pressure * outer_diameter) / ((2 * (allowable_stress * joint_efficiency * weld_strength_reduction) + (self.pressure * y_coefficient)))
            return pressure_thickness
        elif self.pipe_config == '90LR - Inner Elbow':
        
            radius = self.get_centerline_radius() - outer_diameter/2
            intrados_factor = (4*(radius/outer_diameter) - 1) / (4*(radius/outer_diameter) - 2)
            return (self.pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(intrados_factor) + self.pressure * y_coefficient))
        
        elif self.pipe_config == '90LR - Outer Elbow':
        
            radius = self.get_centerline_radius() + outer_diameter/2
            extrados_factor = (4*(radius/outer_diameter) + 1) / (4*(radius/outer_diameter) + 2)
            return (self.pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(extrados_factor) + self.pressure * y_coefficient))
           
        else:
            raise ValueError(f"Unable to calculate minimum thickness for invalid pipe configuration: {self.pipe_config}")

    #####################################################################################
    # Structural Thickness Requirements Per API 574 Codes
    #####################################################################################

    def get_structural_thickness_requirement(self) -> float:
        """
        Get minimum structural thickness requirement from API 574 tables.
        
        Returns:
            float: Minimum structural thickness requirement in inches
            
        Raises:
            ValueError: If table lookup fails or invalid configuration
        """
        if self.API_table == "2025":
            # Handle different metallurgy types for 2025 API table
            if self.metallurgy == "Intermediate/Low CS":
                structural_requirement = self.API574_CS_400F[self.nps][self.pressure_class]
            elif self.metallurgy in ["SS 316/316L", "SS 304/304L"]:
                structural_requirement = self.API574_SS_400F[self.nps][self.pressure_class]
            else:
                # Default to carbon steel table for other metallurgies
                structural_requirement = self.API574_CS_400F[self.nps][self.pressure_class]
        elif self.API_table == "2009":
            # Use 2009 API table
            structural_requirement = self.API574_2009_TABLE_6[self.nps]["default_minimum_structural_thickness"]
        else:
            raise ValueError(f"Invalid API table version: {self.API_table}. Must be '2025' or '2009'")
        
        if structural_requirement is None:
            raise ValueError(f"No structural thickness requirement found for NPS {self.nps}, "
                           f"pressure class {self.pressure_class}, metallurgy {self.metallurgy}")
        
        return structural_requirement
    
    #####################################################################################
    # Corrosion Allowance Calculations
    #####################################################################################
    
    def calculate_corrosion_allowance(self, excess_thickness, corrosion_rate) -> float:
        """Calculate remaining life based on excess thickness and corrosion rate"""
        return np.floor(self.inches_to_mils(excess_thickness) * corrosion_rate)

    #####################################################################################
    # Calculate Time Elapsed since Inspection (Used in Analysis)
    #####################################################################################

    def _calculate_time_elapsed(self, year_inspected: int, month_inspected: Optional[int] = None) -> float:
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

    def _format_inspection_date(self, year: int, month: Optional[int] = None) -> str:
        """Format inspection date for display"""
        month_str = f"{month:02d}" if month is not None else "01"
        return f"{year}-{month_str}"
    

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

    def analysis(self, measured_thickness: float, year_inspected: Optional[int] = None, 
                 month_inspected: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = None, 
                 joint_type: Literal['Seamless', 'Welded'] = 'Seamless'):
        """
        Analyze pipe thickness against pressure and structural requirements
        
        Args:
            measured_thickness: Thickness measured during inspection (inches)
            year_inspected: Year when thickness was measured (e.g., 2020)
            month_inspected: Month when thickness was measured (1-12, e.g., 1 for January, 12 for December)
            joint_type: Joint type for calculations ('Seamless' or 'Welded')
            
        Returns:
            Dict with analysis results and governing factor
            
        Raises:
            ValueError: If inspection year is in the future or invalid parameters
            
        Example:
            >>> pipe = PIPE(nps=2.0, pressure_class=300, corrosion_rate=15.0, ...)
            >>> # High corrosion rate - month precision matters
            >>> results = pipe.analysis(0.25, 2024, 6)  # June 2024 inspection
            >>> # vs
            >>> results = pipe.analysis(0.25, 2024, 12)  # December 2024 inspection
            >>> # 6 months difference with 15 MPY = 7.5 mils difference in degradation
        """
        
        # Edge Case Error Messages
        if month_inspected is not None and not (1 <= month_inspected <= 12):
            raise ValueError(f"Month must be between 1 and 12, got {month_inspected}")
        
        if year_inspected is not None and year_inspected < 1900:
            raise ValueError(f"Year must be reasonable, got {year_inspected}")

        # Calculate present-day actual thickness based on inspection year and corrosion rate
        if year_inspected is not None and self.corrosion_rate is not None:
            # Calculate precise time elapsed including months for high corrosion rates
            time_elapsed = self._calculate_time_elapsed(year_inspected, month_inspected)
            inspection_date_str = self._format_inspection_date(year_inspected, month_inspected)
            
            degradation = self.corrosion_rate * time_elapsed  # Returns the amount of degradation (in Mils) since last inspection, assuming uniform, linear corrosion
            
            actual_thickness = measured_thickness - self.mils_to_inches(degradation)  # Last known thickness minus the amount of degradation gives true, present-day pipe wall thickness
            
            print(f"Time-based corrosion calculation:")
            if time_elapsed < 0.1:  # Less than ~1.2 months
                print(f"  Measured thickness: {measured_thickness:.4f} inches ({inspection_date_str})")
                print(f"  Corrosion rate: {self.corrosion_rate} MPY")
            else:
                print(f"  Measured thickness: {measured_thickness:.4f} inches ({inspection_date_str})")
                print(f"  Corrosion rate: {self.corrosion_rate} MPY")
                print(f"  Time elapsed: {time_elapsed:.3f} years ({time_elapsed*12:.1f} months)")
                print(f"  Amount of Degradation since {inspection_date_str}: {self.mils_to_inches(degradation):.4f} inches (or {degradation:.1f} Mils)")
                print(f"  Present-day thickness: {actual_thickness:.4f} inches (or {self.inches_to_mils(actual_thickness)} Mils)")

        
        else:
            actual_thickness = measured_thickness
            print(f"Using measured thickness as present-day thickness: {actual_thickness:.4f} inches")
        
        tmin_pressure = self.get_pressure_thickness_requirement(joint_type)
        tmin_structural = self.get_structural_thickness_requirement()

        
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
        print(f"The pipe is {governing_type} thickness governed, pipe retirement is required at {governing_thickness} inches ({self.inches_to_mils(governing_thickness)} Mils)")
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
            
            api574_value = self.get_structural_thickness_requirement()
            if api574_value < actual_thickness:
                corosion_allowance = actual_thickness - api574_value
                print(f"There is {corosion_allowance} inches ({self.inches_to_mils(corosion_allowance)} Mils) of corrosion allowance remaining")
            else:
                print(f"Actual Thickness is {api574_value - actual_thickness} inches below corresponding API 574 Structural Retirement Limit for {self.metallurgy}, Retirement Recommended, Fit For Service assessment is needed")
                corosion_allowance = None

        else:
            if governing_thickness >= actual_thickness:
                print(f"Actual Thickness is {governing_thickness - actual_thickness} inches ({self.inches_to_mils(governing_thickness - actual_thickness)} Mils), Retire Pipe Immediately, miniumum pressure containing thickness is not satisfied")
        
        return {
            "measured_thickness": measured_thickness,
            "year_inspected": year_inspected,
            "actual_thickness": actual_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            "default_retirement_limit": default_retirement_limit,
            "below_defaultRL": below_defaultRL,
            "api574_RL": self.get_structural_thickness_requirement(),
            "above_api574RL": corosion_allowance,
            "life_span": self.calculate_corrosion_allowance(corosion_allowance, self.corrosion_rate) if corosion_allowance is not None and self.corrosion_rate is not None else None,
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