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

    data_storage : Dict[str, Any] = None

    def pipe_info(self, data_storage, table_info: Optional[Dict[str, Any]] = None, 
                  flag_info: Optional[Dict[str, Any]] = None, 
                  result_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        pipe_info is a property of the PIPE instance that will store all of the information as it is recieved, parsed, or computed. It is packed into a python dict called
        named after whatever it is called as (e.g. in analysis, it is saved as all_data = pipe_info(metadata, table_info, result_data) in its final form)

        this is in an attempt to reduce instance referals like selfs from cluttering the script. It is essentially a way to pack and unpack all the data through the workflow of 
        core workflow. In the beginning, the metadata is an empty py dict that is initialized. It is then populated with the initilized kwargs(pressure, nps, ect.). After which,
        get functions will parse all of the tables using those kwargs to get more information such as outer diameters, inner diameters, WSRFs, ect. , this can then be populated into the original pipe_info dict by recalling the 
        old dict with another argument, table_info, it should use ** to add it in and overwrite the None values set before it. Now you have a new packed dict that can statefully be called into flags, then updated, then run in analysis.
        """

        """
        Progressive data enrichment through workflow stages:
        
        1. metadata = pipe.pipe_info()  # Basic pipe properties
        2. enriched = pipe.pipe_info(metadata, get_table_info())  # Add table lookups
        3. flagged = pipe.pipe_info(enriched, flag_info)  # Add flag analysis
        4. final = pipe.pipe_info(flagged, None, result_data)  # Add analysis results
        """
        
        if data_storage is None:
            data_storage = {
                'pressure': self.pressure,
                'design_temp': self.design_temp,
                'nps': self.nps,
                'schedule': self.schedule,
                'pressure_class': self.pressure_class,
                'metallurgy': self.metallurgy,
                'yield_stress': self.yield_stress,
                'pipe_config': self.pipe_config,
                'corrosion_rate': self.corrosion_rate,
                'default_retirement_limit': self.default_retirement_limit,
                'API_table': self.API_table,
                'joint_type': self.joint_type,
            }


        # Stage 1: Merge in table_info (dimensions, material properties, etc.)
        if table_info:
            data_storage.update(table_info)
        
        # Stage 2: Merge in flag_info (analysis flags and status)
        if flag_info:
            data_storage.update(flag_info)
            
        # Stage 3: Merge in result_data (final analysis calculations)
        if result_data:
            data_storage.update(result_data)
            
        return data_storage



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
    


    def get_table_info(self):

        outer_diameter = self.get_outer_diameter()
        inner_diameter = self.get_inner_diameter()
        allowable_stress = self.get_allowable_stress()
        joint_type = self.get_joint_type()
        y_coefficient = self.get_y_coefficient()
        centerline_radius = self.get_centerline_radius()

        table_info = {
            'outer_diameter': outer_diameter,
            'inner_diameter': inner_diameter,
            'allowable_stress': allowable_stress,
            'joint_type': joint_type,
            'y_coefficient' : y_coefficient,
            'centerline_radius': centerline_radius,
            'API574_CS_400F': self.API574_CS_400F,
            'API574_SS_400F': self.API574_SS_400F,
            'API574_2009_TABLE_6': self.API574_2009_TABLE_6
        }
        return table_info
    
    """
    See the get_table_info above, this can be tacked into the the pipe info function to make a new dict with more data in it. 
    Next, we can run analysis, we have all the data we need with that new dictionary we made, it should run and tack on its findings into an even newer dict with more
    information that analysis() calculated for us, like
      "measured_thickness": measured_thickness,
            "year_inspected": year_inspected,
            "month_inspected": month_inspected,
            "actual_thickness": actual_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            "default_retirement_limit": default_retirement_limit,
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,

    After which, when the new dict is run, we can send it to the flags function below.
    """
    
    def get_flag_info(self):
        pass



    #####################################################################################
    # Pressure Contianing Thickness Requirements Per ASME B31.3 Codes
    #####################################################################################

    
    def tmin_pressure(self, pipe_data: Dict[str, Any]) -> float:

        # passes the enriched data dictionaries through each method instead of using self references. This approach is  for eliminating state dependencies.

        outer_diameter = pipe_data['outer_diameter']
        pressure = pipe_data['pressure']
        pipe_config = pipe_data['pipe_config']
        allowable_stress = pipe_data['allowable_stress']
        y_coefficient = pipe_data['y_coefficient']
        centerline_radius = pipe_data['centerline_radius']

        joint_info = pipe_data['joint_type']
        joint_efficiency = joint_info['joint_efficiency']
        weld_strength_reduction = joint_info['weld_strength_reduction']
        
        
        if outer_diameter is None:
            raise ValueError(f"Invalid NPS {pipe_data['nps']} for schedule {pipe_data['schedule']}")
        if y_coefficient is None:
            raise ValueError(f"No Y coefficient available for NPS {pipe_data['nps']}")
        
        """
        Calculate minimum wall thickness for pressure design
        Based on ASME B31.1 Para. 304.1.2a Eq. 3a
        
        For seamless pipe (most common): E = 1.0, W = 1.0
        For welded pipe: E and W depend on temperature and weld type
        """
        
        if pipe_config == 'straight':
            pressure_thickness = (pressure * outer_diameter) / ((2 * (allowable_stress * joint_efficiency * weld_strength_reduction) + (pressure * y_coefficient)))
            return pressure_thickness
        elif pipe_config == '90LR - Inner Elbow':
            radius = centerline_radius - outer_diameter/2
            intrados_factor = (4*(radius/outer_diameter) - 1) / (4*(radius/outer_diameter) - 2)
            return (pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(intrados_factor) + pressure * y_coefficient))
        
        elif pipe_config == '90LR - Outer Elbow':
            radius = centerline_radius + outer_diameter/2
            extrados_factor = (4*(radius/outer_diameter) + 1) / (4*(radius/outer_diameter) + 2)
            return (pressure * outer_diameter) / (2 * ((allowable_stress*joint_efficiency*weld_strength_reduction)/(extrados_factor) + pressure * y_coefficient))
           
        else:
            raise ValueError(f"Unable to calculate minimum thickness for invalid pipe configuration: {pipe_config}")




    #####################################################################################
    # Structural Thickness Requirements Per API 574 Codes
    #####################################################################################


    def tmin_structural(self, pipe_data: Dict[str, Any]) -> float:
        """
        Get minimum structural thickness requirement using enriched pipe data
        """
        # Extract values from the enriched pipe_data dict
        nps = pipe_data['nps']
        pressure_class = pipe_data['pressure_class']
        metallurgy = pipe_data['metallurgy']
        API_table = pipe_data['API_table']
        
        if API_table == "2025":
            if metallurgy == "Intermediate/Low CS":
                structural_requirement = pipe_data['API574_CS_400F'][nps][pressure_class]
            elif metallurgy in ["SS 316/316L", "SS 304/304L"]:
                structural_requirement = pipe_data['API574_SS_400F'][nps][pressure_class]
            else:
                structural_requirement = pipe_data['API574_CS_400F'][nps][pressure_class]
        elif API_table == "2009":
            structural_requirement = pipe_data['API574_2009_TABLE_6'][nps]["default_minimum_structural_thickness"]
        else:
            raise ValueError(f"Invalid API table version: {API_table}. Must be '2025' or '2009'")
        
        if structural_requirement is None:
            raise ValueError(f"No structural thickness requirement found for NPS {nps}, "
                           f"pressure class {pressure_class}, metallurgy {metallurgy}")
        
        return structural_requirement
    




    def calculate_all(self, pipe_data: Dict[str, Any], measured_thickness: float, 
                           year_inspected: Optional[int] = None, 
                           month_inspected: Optional[int] = None) -> Dict[str, Any]:
        """ Determines the governing thickness based on metadata and raises flags(Green, yellow, or Red) to assess safety and compliance of continued pipe operation"""

        #Unpack our pipe_data to use for calculations
        corrosion_rate = pipe_data["corrosion_rate"]
        default_retirement_limit = pipe_data["default_retirement_limit"]




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
        
        if default_retirement_limit is not None and default_retirement_limit < self.tmin_structural(pipe_data):
            raise ValueError(f"Default, company-specific retirement limits shall not be below API {self.API_table} appointed structural thickness requirements")

        if measured_thickness > pipe_data['outer_diameter'] - pipe_data['inner_diameter']:
            raise ValueError(f"Measured thickness cannot be greater than nominal pipe wall thickness: units should be in inches")





        # selfs in here are utility functions, do not remove
        if year_inspected is not None and corrosion_rate is not None:

            """Need to make error handling and more if statements to ensure that if there is any time difference between current year and month and 
            inspection year and month, that a time-elapsed and degradation operation is excecuted, otherwise current_thickness = measured thickness. Same with None values, this
            assumes it is all current readins so they can pass to current_thickness = measured thickness"""

            time_elapsed = self._calculate_time_elapsed(year_inspected, month_inspected)
            degradation = corrosion_rate * time_elapsed
            current_thickness = measured_thickness - self.mils_to_inches(degradation)

        else:
            current_thickness = measured_thickness #if no is some time difference between the current year and month and inspection year and month

        # Calculate thickness requirements using enriched pipe data
        tmin_pressure = self.tmin_pressure(pipe_data) #float, inches
        tmin_structural = self.tmin_structural(pipe_data)#float, inches


         # Determine governing thickness
        if tmin_pressure >= tmin_structural:
            governing_thickness = tmin_pressure
            governing_type = "pressure"
        else:
            governing_thickness = tmin_structural
            governing_type = "structural"
            

        
        # Calculate remaining life if corrosion rate is provided
        if corrosion_rate is not None:
            # Define corrosion_allowance here for GREEN flag case
            corrosion_allowance = current_thickness - governing_thickness
            remaining_life_years = self.calculate_corrosion_allowance(corrosion_allowance, corrosion_rate)
        else:
            remaining_life_years = None
            corrosion_allowance = None


        #################################
        # Flag Logic
        #################################


        #Red flag:
        if current_thickness <= tmin_pressure:
            pressure_thick_deficit = tmin_pressure - current_thickness
            raised_flag = {
                "flag": "RED",
                "status": "IMMEDIATE_RETIREMENT",
                "message": "Below pressure minimum - risk-based analysis needed to continue operation",
                "pressure_deficit": pressure_thick_deficit
            }

        #Yellow Flag:
        elif (current_thickness > tmin_pressure and 
              (current_thickness <= tmin_structural or 
               (default_retirement_limit is not None and current_thickness <= default_retirement_limit and current_thickness > tmin_pressure))):

                # Check which limits are not met
                below_structural = current_thickness <= tmin_structural
                below_default = default_retirement_limit is not None and current_thickness <= default_retirement_limit
                
                
                if below_structural:
                    structural_deficit = tmin_structural - current_thickness
                    
                
                if below_default:
                    default_deficit = default_retirement_limit - current_thickness
                    
                raised_flag = {
                    "flag": "YELLOW",
                    "status": "FFS_RECOMMENDED",
                    "message": "Not all criteria satisfied - FFS assessment recommended",
                    "below_structural": below_structural,
                    "below_default": below_default,
                    "structural_deficit": structural_deficit if below_structural else None,
                    "default_deficit": default_deficit if below_default else None,
                }
    
        #Green Flag
        else:

            if default_retirement_limit is not None and default_retirement_limit > governing_thickness:
                next_retirement_limit = default_retirement_limit
                retirement_type = "company-specified"
            else:
                next_retirement_limit = governing_thickness  
                retirement_type = f"New Retirement limit is governed by {governing_type} design"
        
            corrosion_allowance = current_thickness - next_retirement_limit

            raised_flag = {
                "flag": "GREEN",
                "status": "SAFE_TO_CONTINUE",
                "message": "All criteria satisfied - pipe can safely continue in operation",
                "corrosion_allowance": corrosion_allowance,
                "next_retirement_limit": next_retirement_limit,
                "retirement_type": retirement_type,
                "remaining_life_years": remaining_life_years,  # Fixed: was conditional
            }


        #The flag conditonal will return a small python dictionary "raised_flag" contianing key and values of the final verdict if the pipe is safe or not
        # we can append this one last time into the overall pipe_info dictionary, completeing all computations with large, easily-callable python dictionary of the instance

        # Pack all analysis results and flag information into one dictionary
        analysis_results = {
            # Basic analysis inputs
            "measured_thickness": measured_thickness,
            "year_inspected": year_inspected,
            "month_inspected": month_inspected,
            
            # Calculated thickness values
            "current_thickness": current_thickness,
            "tmin_pressure": tmin_pressure,
            "tmin_structural": tmin_structural,
            
            # Governing thickness information
            "governing_thickness": governing_thickness,
            "governing_type": governing_type,
            
            # Time and corrosion analysis
            "time_elapsed": time_elapsed if year_inspected is not None and corrosion_rate is not None else None,
            "degradation_mils": degradation if year_inspected is not None and corrosion_rate is not None else None,
            
            # Flag analysis results (this spreads in all the flag-specific keys)
            **raised_flag
        }
        
        return analysis_results
    


    def analyze(self, measured_thickness: float, year_inspected: Optional[int] = None, 
                month_inspected: Optional[int] = None) -> Dict[str, Any]:
        """
        Main analysis method that automatically orchestrates the entire dict enrichment process.
        This is the one-stop method users call to get a complete analysis package.
        
        Usage:
            tml_161 = PIPE(kwargs)
            complete_analysis = tml_161.analyze(measured_thickness, year_inspected, month_inspected)
        
        Returns:
            Complete dictionary containing all pipe information, analysis results, and flags
        """
        # Stage 1: Get basic pipe metadata
        metadata = self.pipe_info(None)
        
        # Stage 2: Enrich with table lookups (dimensions, material properties, etc.)
        table_info = self.get_table_info()
        enriched_data = self.pipe_info(metadata, table_info)
        
        # Stage 3: Run analysis calculations and get results (including flags)
        analysis_results = self.calculate_all(enriched_data, measured_thickness, year_inspected, month_inspected)
        
        # Stage 4: Final enrichment - combine everything into one complete package
        final_data = self.pipe_info(enriched_data, None, None, analysis_results)
        
        # Stage 5: Generate SymPy mathematical report
        sympy_report = self.quick_report(final_data)
        final_data['sympy_report'] = sympy_report
        
        return final_data




    def calculate_corrosion_allowance(self, excess_thickness: float, corrosion_rate: float) -> float:
        """Calculate remaining life based on excess thickness and corrosion rate"""
        return self.inches_to_mils(excess_thickness) / corrosion_rate

    

    def quick_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a lightweight SymPy-based report showing equations and calculations.
        
        This creates a symbolic representation of the pressure design equation and displays
        input parameters and computed outputs in a clean, mathematical format.
        
        Args:
            analysis_data: Complete analysis data from analyze() or analyze_generator()
            
        Returns:
            Dict containing SymPy equations, input table, and output table
        """
        
        # Define symbolic variables
        P, D, S, E, W, Y = symbols('P D S E W Y')
        
        # ASME B31.1 Pressure Design Equation (Eq. 3a)
        # t = (P * D) / (2 * (S * E * W) + (P * Y))
        pressure_eq = (P * D) / (2 * (S * E * W) + (P * Y))
        
        # Substitute actual values
        pressure_eq_substituted = pressure_eq.subs({
            P: analysis_data['pressure'],
            D: analysis_data['outer_diameter'],
            S: analysis_data['allowable_stress'],
            E: analysis_data['joint_type']['joint_efficiency'],
            W: analysis_data['joint_type']['weld_strength_reduction'],
            Y: analysis_data['y_coefficient']
        })
        
        # Create input parameters table
        input_table = {
            'Parameter': ['Design Pressure (P)', 'Outside Diameter (D)', 'Allowable Stress (S)', 
                         'Joint Efficiency (E)', 'Weld Strength Reduction (W)', 'Y Coefficient (Y)'],
            'Symbol': ['P', 'D', 'S', 'E', 'W', 'Y'],
            'Value': [
                f"{analysis_data['pressure']:.1f} psi",
                f"{analysis_data['outer_diameter']:.3f} in",
                f"{analysis_data['allowable_stress']:.0f} psi",
                f"{analysis_data['joint_type']['joint_efficiency']:.1f}",
                f"{analysis_data['joint_type']['weld_strength_reduction']:.1f}",
                f"{analysis_data['y_coefficient']:.3f}"
            ],
            'Units': ['psi', 'in', 'psi', '-', '-', '-']
        }
        
        # Create computed outputs table
        output_table = {
            'Result': ['Pressure Minimum Thickness', 'Structural Minimum Thickness', 
                      'Governing Thickness', 'Actual Thickness', 'Corrosion Allowance',
                      'Flag Status', 'Governing Type'],
            'Value': [
                f"{analysis_data['tmin_pressure']:.4f} in",
                f"{analysis_data['tmin_structural']:.4f} in",
                f"{analysis_data['governing_thickness']:.4f} in",
                f"{analysis_data['current_thickness']:.4f} in",
                f"{analysis_data.get('corrosion_allowance', 'N/A')}",
                f"{analysis_data['flag']}",
                f"{analysis_data['governing_type']}"
            ],
            'Units': ['in', 'in', 'in', 'in', 'in', '-', '-']
        }
        
        # Create SymPy report
        sympy_report = {
            'equation': {
                'symbolic': pressure_eq,
                'substituted': pressure_eq_substituted,
                'latex': latex(pressure_eq),
                'latex_substituted': latex(pressure_eq_substituted)
            },
            'input_parameters': input_table,
            'computed_outputs': output_table,
            'pipe_specs': {
                'NPS': f"{analysis_data['nps']}\"",
                'Schedule': f"{analysis_data['schedule']}",
                'Pressure Class': f"{analysis_data['pressure_class']}",
                'Metallurgy': analysis_data['metallurgy'],
                'Pipe Config': analysis_data['pipe_config']
            },
            'analysis_summary': {
                'flag': analysis_data['flag'],
                'status': analysis_data['status'],
                'message': analysis_data['message'],
                'governing_factor': analysis_data['governing_type']
            }
        }
        
        return sympy_report

    def analyze_generator(self, measured_thickness: float, year_inspected: Optional[int] = None, 
                         month_inspected: Optional[int] = None):
        """
        Generator version of analyze() that yields each stage of the analysis pipeline.
        
        This method provides the same functionality as analyze() but orchestrates each data enrichment stage iteratively
        so the results can be seen at each stage if needed for debugging. 

        Stages:
            - "metadata": Basic pipe properties
            - "enriched": Pipe properties + table lookups (dimensions, material properties)
            - "analysis_results": Analysis calculations and flag determination
            - "final": Complete analysis package with all data
            - "sympy_report": SymPy mathematical equations and formatted tables

        Example:
            >>> pipe = PIPE(...)
            >>> for stage_name, data in pipe.analyze_generator(0.25, 2024):
            ...     print(f"Stage: {stage_name}")
            ...     if stage_name == "enriched":
            ...         print(f"OD: {data['outer_diameter']}")
            ...     elif stage_name == "final":
            ...         print(f"Flag: {data['flag']}")
            ...     elif stage_name == "sympy_report":
            ...         print(f"Equation: {data['equation']['latex']}")
        """
        
        # Stage 1: Basic metadata
        metadata = self.pipe_info(None)
        yield "metadata", metadata
        
        # Stage 2: Add table lookups (dimensions, material properties, etc.)
        table_info = self.get_table_info()
        enriched_data = self.pipe_info(metadata, table_info)
        yield "enriched", enriched_data
        
        # Stage 3: Run analysis calculations and get results (including flags)
        analysis_results = self.calculate_all(enriched_data, measured_thickness, year_inspected, month_inspected)
        yield "analysis_results", analysis_results
        
        # Stage 4: Final enrichment - combine everything into one complete package
        final_data = self.pipe_info(enriched_data, analysis_results)
        yield "final", final_data
        
        # Stage 5: SymPy mathematical report
        sympy_report = self.quick_report(final_data)
        yield "sympy_report", sympy_report

    def report(self, report_format: str = "TXT", filename: Optional[str] = None, **analysis_kwargs) -> Dict[str, Any]:
        """
        Generate analysis report in specified format
        
        Args:
            report_format: Format of the report ("CSV", "JSON", "TXT", "IPYNB")
            filename: Optional filename (without extension) for the report
            **analysis_kwargs: Arguments to pass to analyze() method if not already called
            
        Returns:
            Dict containing report data and file paths
        """
        from .report_generator import ReportGenerator
        
        # Check if analysis has already been performed (stored in instance)
        if not hasattr(self, '_last_analysis_results'):
            # Perform analysis with provided kwargs
            if not analysis_kwargs:
                raise ValueError("Analysis arguments required. Provide measured_thickness and other parameters.")
            
            self._last_analysis_results = self.analyze(**analysis_kwargs)
        
        analysis_results = self._last_analysis_results
        actual_thickness = analysis_results['current_thickness']
        
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
        
        return getattr(self, '_last_analysis_results', None)
    
    def generate_report(self, measured_thickness: float, year_inspected: Optional[int] = None, 
                       month_inspected: Optional[int] = None, filename: Optional[str] = None) -> str:
        
        from .report_generator import ReportGenerator
        
        # Perform analysis
        analysis_results = self.analyze(measured_thickness, year_inspected, month_inspected)
        
        # Generate report
        report_gen = ReportGenerator()
        report_path = report_gen.generate_report_from_core_dev(self, analysis_results, filename)
        
        return report_path
