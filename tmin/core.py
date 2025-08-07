from .tables.od_table import trueOD
from .tables.wsrf import WSRF
from .tables.y_coeff import ferritic_steels_y, austenitic_steels_y, other_metals_y, nickel_alloy_N06690_y, nickel_alloys_N06617_N08800_N08810_N08825_y, cast_iron_y
from .tables.api_574_2025 import API574_CS_400F, API574_SS_400F
from .tables.api_574_2009 import API574_2009_TABLE_6
from .tables.ANSI_radii import ANSI_radii

import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any
import matplotlib.pyplot as plt
from datetime import datetime
########### Checked as of 07/31/2025

@dataclass
class PIPE:

    #########Initialize Characteristics of the Pipe and Service###############

    pressure: float  # Design pressure (psi)
    metallurgy: Literal["Intermediate/Low CS", "SS 316/316L", "SS 304/304L", "Inconel 625", "Other"]
    yield_stress: float # User defined yield Stress
    schedule: float  # Pipe schedule (10, 40, 80, 120, 160)
    nps: float # Nominal pipe size (e.g., '2', '3/4', '1-1/2')
    pressure_class: Literal[150, 300, 600, 900, 1500, 2500]
    
    # Optional fields with defaults
    design_temp: Literal["<900" ,900, 950, 1000, 1050, 1100, 1150, 1200, 1250, "1250+" ] = 900
    pipe_config: Literal["straight", "90LR - Inner Elbow", "90LR - Outer Elbow"] = "straight"
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
        return self.inches_to_mils(excess_thickness) / corrosion_rate

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

    # def analysis(self, measured_thickness: float, year_inspected: Optional[int] = None, 
    #              month_inspected: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = None, 
    #              joint_type: Literal['Seamless', 'Welded'] = 'Seamless'):
    #     """
    #     Analyze pipe thickness against pressure and structural requirements
        
    #     Args:
    #         measured_thickness: Thickness measured during inspection (inches)
    #         year_inspected: Year when thickness was measured (e.g., 2020)
    #         month_inspected: Month when thickness was measured (1-12, e.g., 1 for January, 12 for December)
    #         joint_type: Joint type for calculations ('Seamless' or 'Welded')
            
    #     Returns:
    #         Dict with analysis results and governing factor
            
    #     Raises:
    #         ValueError: If inspection year is in the future or invalid parameters
            
    #     Example:
    #         >>> pipe = PIPE(nps=2.0, pressure_class=300, corrosion_rate=15.0, ...)
    #         >>> # High corrosion rate - month precision matters
    #         >>> results = pipe.analysis(0.25, 2024, 6)  # June 2024 inspection
    #         >>> # vs
    #         >>> results = pipe.analysis(0.25, 2024, 12)  # December 2024 inspection
    #         >>> # 6 months difference with 15 MPY = 7.5 mils difference in degradation
    #     """
        
    #     # Edge Case Error Messages
    #     if month_inspected is not None and not (1 <= month_inspected <= 12):
    #         raise ValueError(f"Month must be between 1 and 12, got {month_inspected}")
        
    #     if year_inspected is not None and year_inspected < 1900:
    #         raise ValueError(f"Year must be reasonable, got {year_inspected}")

    #     # Calculate present-day actual thickness based on inspection year and corrosion rate
    #     if year_inspected is not None and self.corrosion_rate is not None:
    #         # Calculate precise time elapsed including months for high corrosion rates
    #         time_elapsed = self._calculate_time_elapsed(year_inspected, month_inspected)
    #         inspection_date_str = self._format_inspection_date(year_inspected, month_inspected)
            
    #         degradation = self.corrosion_rate * time_elapsed  # Returns the amount of degradation (in Mils) since last inspection, assuming uniform, linear corrosion
            
    #         actual_thickness = measured_thickness - self.mils_to_inches(degradation)  # Last known thickness minus the amount of degradation gives true, present-day pipe wall thickness
            
    #         print(f"Time-based corrosion calculation:")
    #         if time_elapsed < 0.1:  # Less than ~1.2 months
    #             print(f"  Measured thickness: {measured_thickness:.4f} inches ({inspection_date_str})")
    #             print(f"  Corrosion rate: {self.corrosion_rate} MPY")
    #         else:
    #             print(f"  Measured thickness: {measured_thickness:.4f} inches ({inspection_date_str})")
    #             print(f"  Corrosion rate: {self.corrosion_rate} MPY")
    #             print(f"  Time elapsed: {time_elapsed:.3f} years ({time_elapsed*12:.1f} months)")
    #             print(f"  Amount of Degradation since {inspection_date_str}: {self.mils_to_inches(degradation):.4f} inches (or {degradation:.1f} Mils)")
    #             print(f"  Present-day thickness: {actual_thickness:.4f} inches (or {self.inches_to_mils(actual_thickness)} Mils)")

        
    #     else:
    #         actual_thickness = measured_thickness
    #         print(f"Using measured thickness as present-day thickness: {actual_thickness:.4f} inches")
        
    #     #### Checked 

    #     tmin_pressure = self.get_pressure_thickness_requirement(joint_type)
    #     tmin_structural = self.get_structural_thickness_requirement()

        
    #     default_retirement_limit = self.default_retirement_limit # Optional user-defined, company-specific retirement limit
        
    #     limits = {
    #         "pressure": tmin_pressure,
    #         "structural": tmin_structural,
    #     }

    #     # This conditional take the larger of the two required thicknesses, this will determine whether the pipe is structurally governed or pressure governed
    #     if limits["pressure"] >= limits["structural"]:
    #         governing_thickness = limits["pressure"]
    #         governing_type = "pressure" 
            
    #     else:
    #         governing_thickness = limits["structural"]
    #         governing_type = "structural"

    #     print("----------- THICKNESS REQUIREMENT ----------")
    #     print(f"The pipe is {governing_type} thickness governed, pipe retirement is required at {governing_thickness} inches ({self.inches_to_mils(governing_thickness)} Mils)")
    #     print("-----------------------------------------------------")
        
    #     if default_retirement_limit is not None:
    #         if default_retirement_limit - actual_thickness >= 0:
    #             below_defaultRL = default_retirement_limit - actual_thickness
    #         else:
    #             print(f"The actual thickness is greater than default (company-specified) retirement limit by {actual_thickness - default_retirement_limit}")
    #             below_defaultRL = None
    #     else:
    #         below_defaultRL = None
        
    #     if governing_type == "structural":
            
    #         api574_value = self.get_structural_thickness_requirement()
    #         if api574_value < actual_thickness:
    #             corosion_allowance = actual_thickness - api574_value
    #             print(f"There is {corosion_allowance} inches ({self.inches_to_mils(corosion_allowance)} Mils) of corrosion allowance remaining")
    #         else:
    #             print(f"Actual Thickness is {api574_value - actual_thickness} inches below corresponding API 574 Structural Retirement Limit for {self.metallurgy}, Retirement Recommended, Fit For Service assessment is needed")
    #             corosion_allowance = None

    #     else:
    #         if governing_thickness >= actual_thickness:
    #             print(f"Actual Thickness is {governing_thickness - actual_thickness} inches ({self.inches_to_mils(governing_thickness - actual_thickness)} Mils), Retire Pipe Immediately, miniumum pressure containing thickness is not satisfied")
        
    #     return {
    #         "measured_thickness": measured_thickness,
    #         "year_inspected": year_inspected,
    #         "actual_thickness": actual_thickness,
    #         "tmin_pressure": tmin_pressure,
    #         "tmin_structural": tmin_structural,
    #         "default_retirement_limit": default_retirement_limit,
    #         "below_defaultRL": below_defaultRL,
    #         "api574_RL": self.get_structural_thickness_requirement(),
    #         "above_api574RL": corosion_allowance,
    #         "life_span": self.calculate_corrosion_allowance(corosion_allowance, self.corrosion_rate) if corosion_allowance is not None and self.corrosion_rate is not None else None,
    #         "governing_thickness": governing_thickness,
    #         "governing_type": governing_type,
    #     }
    
    def analysis(self, measured_thickness : float, year_inspected : Optional[int] = None, month_inspected : Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]] = None, 
                 joint_type = 'Seamless'):

        """
        The intent of analysis is to determine the present-day nominal thickness lies on the overall, 'like-new' pipe wall thickness and compare it to industry standards to assess if it is safe to lower the retirement limit and elongate the pipe's operational life.

        This function has the logic flow:

        1) Logic that calculates present-day thicknesses using time-based corrosion analysis (if needed) -> time_elapsed, corrosion allowance, amount of degradation since last inspection

        2) Logic that takes the max of the structural min and the pressure min -> governinng type, when is the code_cal retirement limit. Any lower than this is a FFS

        3) Conditionals determine suggested actions based on the following:
        
            -If you are above API 574, but below default RL, and above pressure min then, set your next tmin to API574's and calculate the corrosion allowance between that point

            -If you are below API 574, below default RL, but above pressure min then, inform user how far below API574 they are, Fitness for service + engineering judgement is required.

            -If you are below pressure min then, immediately return FFS and Suggest Immediate Retirement and emphasize the need for risk assessment


        4) New Analysis system returns "Green", "Yellow", or "Red" Flags based off of the user-provided inspection and pipe information

            Green Flag - Criteria is satisfied - The pipe can safely remain in service based on the calculated thickness minimums, it should provide users with the corrosion allowance until the next retirement limit
                as well as how much time until the pipe reaches that next RL

            Yellow Flag - Not all of the code criteria was satisfied. User is below default min and or API574 min. Pipe requires a more advanced analysis to assess whether continuing operations is safe (e.q. FFS is recommended)

            Red Flag - Pipe is below pressure min, Retire Pipe Immediately or consider temporary leak device. Rigorous analysis is requried for continuing operations
        
        """
        ####################
        # Edge Case Handling
        ####################

        # Edge Case Error Messages
        if month_inspected is not None and not (1 <= month_inspected <= 12):
            raise ValueError(f"Month must be between 1 and 12, got {month_inspected}")
        
        if year_inspected is not None and year_inspected < 1900:
            raise ValueError(f"Year must be reasonable, got {year_inspected}")
        
        # Get default retirement limit early for validation
        default_retirement_limit = self.default_retirement_limit
        
        if default_retirement_limit is not None and default_retirement_limit < self.get_structural_thickness_requirement():
            raise ValueError(f"Default, company-specific retirement limits shall not be below API {self.API_table} appointed structural thickness requirements")

        ###############################
        # Time-Based Corrosion Analysis
        ###############################

        # Calculate present-day actual thickness based on inspection year and corrosion rate
        if year_inspected is not None and self.corrosion_rate is not None:
            # Calculate precise time elapsed including months for high corrosion rates
            time_elapsed = self._calculate_time_elapsed(year_inspected, month_inspected)
            inspection_date_str = self._format_inspection_date(year_inspected, month_inspected)
            
            degradation = self.corrosion_rate * time_elapsed  # Returns the amount of degradation (in Mils) since last inspection, assuming uniform, linear corrosion
            
            actual_thickness = measured_thickness - self.mils_to_inches(degradation)  # Last known thickness minus the amount of degradation gives true, present-day pipe wall thickness

        else:
            actual_thickness = measured_thickness
            # print(f"Using measured thickness as present-day thickness: {actual_thickness:.4f} inches")


        ###############################
        # Governing Thickness Analysis (Pressure Vs. Structural)
        ###############################


        tmin_pressure = self.get_pressure_thickness_requirement(joint_type)
        tmin_structural = self.get_structural_thickness_requirement()

        
        limits = {
            "pressure": tmin_pressure,
            "structural": tmin_structural,
        }

        # This conditional take the larger of the two required thicknesses, this will determine whether the pipe is structurally governed or pressure governed
        if limits["pressure"] >= limits["structural"]:
            governing_thickness = limits["pressure"]
            governing_type = "pressure" 
            
        else:
            governing_thickness = limits["structural"]
            governing_type = "structural"

        ###############################
        # Raise Flag (Green, Yellow, Red)
        ###############################

        # Store analysis data for flag methods
        analysis_data = {
            "measured_thickness": measured_thickness,
            "year_inspected": year_inspected,
            "month_inspected": month_inspected,
            "actual_thickness": actual_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            "default_retirement_limit": default_retirement_limit,
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,
            "limits": limits
        }

        # RED FLAG: Below pressure minimum - Immediate retirement required
        if actual_thickness <= limits["pressure"]:
            result = self.red_flag(analysis_data)
        
        # YELLOW FLAG: Above pressure but below structural or default retirement limit
        elif (actual_thickness > limits["pressure"] and 
              (actual_thickness <= limits["structural"] or 
               (default_retirement_limit is not None and actual_thickness <= default_retirement_limit and actual_thickness > limits["pressure"]))):
            result = self.yellow_flag(analysis_data)
        
        # GREEN FLAG: Above all limits - Safe to continue operation
        else:
            result = self.green_flag(analysis_data)
        
        # Store results for caching
        self._last_analysis_results = result
        return result
            
    def green_flag(self, analysis_data):
        """Green Flag: All criteria satisfied - pipe can safely continue in operation"""
        print(f"###################################")
        print(f"GREEN FLAG")
        print(f"###################################")

        print(f"Criteria Satisfied per API {self.API_table} / ASME Code")
        print(f"Piping can safely continue in operation")
        
        actual_thickness = analysis_data["actual_thickness"]
        governing_thickness = analysis_data["governing_thickness"]
        default_retirement_limit = analysis_data["default_retirement_limit"]
        
        # Determine next retirement limit (whichever is higher: governing thickness or default RL)
        if default_retirement_limit is not None and default_retirement_limit > governing_thickness:
            next_retirement_limit = default_retirement_limit
            retirement_type = "company-specified"
        else:
            next_retirement_limit = governing_thickness
            retirement_type = f"New Retirement limit is governed by {analysis_data['governing_type']} design"
        
        corrosion_allowance = actual_thickness - next_retirement_limit
        
        print(f"Current thickness: {actual_thickness:.4f} inches ({self.inches_to_mils(actual_thickness):.1f} mils)")
        print(f"Next retirement limit ({retirement_type}): {next_retirement_limit:.4f} inches ({self.inches_to_mils(next_retirement_limit):.1f} mils)")
        print(f"Corrosion allowance: {corrosion_allowance:.4f} inches ({self.inches_to_mils(corrosion_allowance):.1f} mils)")
        
        # Calculate remaining life if corrosion rate is provided
        if self.corrosion_rate is not None:
            remaining_life_years = self.calculate_corrosion_allowance(corrosion_allowance, self.corrosion_rate)
            print(f"Estimated remaining life: {remaining_life_years:.1f} years (at {self.corrosion_rate} MPY)")
        
        return {
            "flag": "GREEN",
            "status": "SAFE_TO_CONTINUE",
            "message": "All criteria satisfied - pipe can safely continue in operation",
            "corrosion_allowance": corrosion_allowance,
            "next_retirement_limit": next_retirement_limit,
            "retirement_type": retirement_type,
            "remaining_life_years": remaining_life_years if self.corrosion_rate is not None else None,
            **analysis_data
        }
    
    def yellow_flag(self, analysis_data):
        """Yellow Flag: Not all criteria satisfied - FFS assessment recommended"""
        print(f"###################################")
        print(f"YELLOW FLAG")
        print(f"###################################")
        
        print(f"Not all code criteria satisfied per API {self.API_table} / ASME Code")
        print(f"Fitness for Service (FFS) assessment recommended")
        
        actual_thickness = analysis_data["actual_thickness"]
        tmin_pressure = analysis_data["tmin_pressure"]
        tmin_structural = analysis_data["tmin_structural"]
        default_retirement_limit = analysis_data["default_retirement_limit"]
        
        # Check which limits are not met
        below_structural = actual_thickness <= tmin_structural
        below_default = default_retirement_limit is not None and actual_thickness <= default_retirement_limit
        
        print(f"Current thickness: {actual_thickness:.4f} inches ({self.inches_to_mils(actual_thickness):.1f} mils)")
        
        if below_structural:
            structural_deficit = tmin_structural - actual_thickness
            print(f"Below structural minimum by: {structural_deficit:.4f} inches ({self.inches_to_mils(structural_deficit):.1f} mils)")
        
        if below_default:
            default_deficit = default_retirement_limit - actual_thickness
            print(f"Below company retirement limit by: {default_deficit:.4f} inches ({self.inches_to_mils(default_deficit):.1f} mils)")
        
        print(f"Engineering judgment and FFS assessment required for continued operation")
        
        return {
            "flag": "YELLOW",
            "status": "FFS_RECOMMENDED",
            "message": "Not all criteria satisfied - FFS assessment recommended",
            "below_structural": below_structural,
            "below_default": below_default,
            "structural_deficit": structural_deficit if below_structural else None,
            "default_deficit": default_deficit if below_default else None,
            **analysis_data
        }
    
    def red_flag(self, analysis_data):
        """Red Flag: Below pressure minimum - Immediate retirement required"""
        print(f"###################################")
        print(f"RED FLAG")
        print(f"###################################")
        
        print(f"CRITICAL: Below pressure minimum thickness requirement")
        print(f"IMMEDIATE RETIREMENT REQUIRED")
        
        actual_thickness = analysis_data["actual_thickness"]
        tmin_pressure = analysis_data["tmin_pressure"]
        pressure_deficit = tmin_pressure - actual_thickness
        
        print(f"Current thickness: {actual_thickness:.4f} inches ({self.inches_to_mils(actual_thickness):.1f} mils)")
        print(f"Pressure minimum required: {tmin_pressure:.4f} inches ({self.inches_to_mils(tmin_pressure):.1f} mils)")
        print(f"Deficit: {pressure_deficit:.4f} inches ({self.inches_to_mils(pressure_deficit):.1f} mils)")
        print(f"Rigorous analysis required for any continued operations")
        print(f"Consider temporary leak detection devices if operation must continue")
        
        return {
            "flag": "RED",
            "status": "IMMEDIATE_RETIREMENT",
            "message": "Below pressure minimum - immediate retirement required",
            "pressure_deficit": pressure_deficit,
            **analysis_data
        }



    def report(self, report_format: Literal["CSV", "JSON", "TXT", "IPYNB"] = "TXT", 
               filename: Optional[str] = None, **analysis_kwargs) -> Dict[str, Any]:
        """
        Generate analysis report in specified format
        
        Args:
            report_format: Format of the report ("CSV", "JSON", "TXT", "IPYNB")
            filename: Optional filename (without extension) for the report
            **analysis_kwargs: Arguments to pass to analysis() method if not already called
            
        Returns:
            Dict containing report data and file paths
            
        Example:
            >>> pipe = PIPE(nps=2.0, pressure_class=300, ...)
            >>> # Generate CSV report
            >>> results = pipe.report("CSV", measured_thickness=0.25, year_inspected=2024)
            >>> # Generate JSON report with custom filename
            >>> results = pipe.report("JSON", "my_analysis", measured_thickness=0.25)
        """
        from .report_generator import ReportGenerator
        from .visualization import ThicknessVisualizer
        
        # Check if analysis has already been performed (stored in instance)
        if not hasattr(self, '_last_analysis_results'):
            # Perform analysis with provided kwargs
            if not analysis_kwargs:
                raise ValueError("Analysis arguments required. Provide measured_thickness and other parameters.")
            
            self._last_analysis_results = self.analysis(**analysis_kwargs)
        
        analysis_results = self._last_analysis_results
        actual_thickness = analysis_results['actual_thickness']
        
        # Initialize report generator
        report_gen = ReportGenerator()
        
        # Generate report based on format
        if report_format.upper() == "CSV":
            report_path = report_gen.generate_csv_report(self, analysis_results, filename)
            return {
                "format": "CSV",
                "file_path": report_path,
                "analysis_results": analysis_results
            }
            
        elif report_format.upper() == "JSON":
            report_path = report_gen.generate_json_report(self, analysis_results, filename)
            return {
                "format": "JSON", 
                "file_path": report_path,
                "analysis_results": analysis_results
            }
            
        elif report_format.upper() == "TXT":
            # Generate full text report
            report_path = report_gen.generate_report(self, analysis_results, actual_thickness, filename)
            return {
                "format": "TXT",
                "file_path": report_path,
                "analysis_results": analysis_results
            }
            
        elif report_format.upper() == "IPYNB":
            report_path = report_gen.generate_notebook_report(self, analysis_results, filename)
            return {
                "format": "IPYNB",
                "file_path": report_path,
                "analysis_results": analysis_results
            }
            
        else:
            raise ValueError(f"Unsupported report format: {report_format}. Supported formats: CSV, JSON, TXT, IPYNB")
    
    def get_last_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Get the results from the last analysis performed
        
        Returns:
            Dict containing last analysis results or None if no analysis performed
        """
        return getattr(self, '_last_analysis_results', None)
    
    def clear_analysis_cache(self):
        """Clear the cached analysis results"""
        if hasattr(self, '_last_analysis_results'):
            delattr(self, '_last_analysis_results')