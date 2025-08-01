from typing import Dict, Any, Optional
from datetime import datetime
import os

class ReportGenerator:
    """
    Generates text reports for pipe thickness analysis
    """
    
    def __init__(self):
        self.report_template = """
TMIN - PIPE THICKNESS ANALYSIS REPORT
=====================================

Report Generated: {timestamp}
Analysis ID: {analysis_id}

PIPE SPECIFICATIONS
-------------------
Nominal Pipe Size (NPS): {nps}
Schedule: {schedule}
Pressure Class: {pressure_class}
Metallurgy: {metallurgy}
Design Pressure: {pressure} psi
Pipe Configuration: {pipe_config}
Corrosion Rate: {corrosion_rate} mpy

THICKNESS MEASUREMENT DATA
--------------------------
Measured Thickness: {measured_thickness:.4f} inches
Inspection Year: {year_inspected}
Present-Day Thickness: {actual_thickness:.4f} inches

DESIGN REQUIREMENTS
-------------------
Pressure Design Minimum: {tmin_pressure:.4f} inches
Structural Minimum (API 574): {tmin_structural:.4f} inches
Governing Thickness: {governing_thickness:.4f} inches
Governing Factor: {governing_type}

RETIREMENT LIMITS
-----------------
Retirement Limit: {retirement_limit}
API 574 Retirement Limit: {api574_RL:.4f} inches

THICKNESS ANALYSIS
------------------
Pressure Design Adequacy: {pressure_adequate}
Structural Adequacy: {structural_adequate}
Retirement Status: {retirement_status}
API 574 Status: {api574_status}

CORROSION ALLOWANCE
-------------------
Above API 574 RL: {above_api574} inches
Below Retirement Limit: {below_retirement} inches
Estimated Life Span: {life_span} years

RECOMMENDATIONS
---------------
{recommendations}

NOTES
-----
{notes}
"""
        # Create Reports directory if it doesn't exist
        self.reports_dir = "Reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _get_filename_with_date(self, base_name: str, filename: Optional[str] = None) -> str:
        """Generate filename with date prefix"""
        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{date_str}_{base_name}"
        
        return os.path.join(self.reports_dir, filename)
    
    def generate_report(self, pipe_instance, analysis_results: Dict[str, Any], 
                       actual_thickness: float, filename: Optional[str] = None) -> str:
        """
        Generate a text report
        
        Args:
            pipe_instance: PIPE instance
            analysis_results: Results from analyze_pipe_thickness method
            actual_thickness: The actual measured thickness
            filename: Optional filename to save the report (without extension)
            
        Returns:
            str: Path to saved report file
        """
        
        # Generate analysis ID
        analysis_id = f"TMIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine adequacy status
        pressure_adequate = "ADEQUATE" if actual_thickness >= analysis_results.get('tmin_pressure', 0) else "INADEQUATE"
        structural_adequate = "ADEQUATE" if actual_thickness >= analysis_results.get('tmin_structural', 0) else "INADEQUATE"
        
        # Replace Table 5 RL with Retirement Limit
        retirement_limit = analysis_results.get('default_retirement_limit', None)
        retirement_limit_str = f"{retirement_limit:.4f}" if retirement_limit is not None else "N/A"
        if retirement_limit is not None and actual_thickness >= retirement_limit:
            retirement_status = "ABOVE RETIREMENT LIMIT"
        elif retirement_limit is not None:
            retirement_status = f"BELOW RETIREMENT LIMIT by {retirement_limit - actual_thickness:.4f} inches"
        else:
            retirement_status = "NO DATA AVAILABLE"
        
        # API 574 status
        api574_RL = analysis_results.get('api574_RL', 0)
        if api574_RL and actual_thickness >= api574_RL:
            api574_status = "ABOVE RETIREMENT LIMIT"
        elif api574_RL:
            api574_status = f"BELOW RETIREMENT LIMIT by {api574_RL - actual_thickness:.4f} inches"
        else:
            api574_status = "NO DATA AVAILABLE"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_results, actual_thickness)
        
        # Generate notes
        notes = self._generate_notes(pipe_instance, analysis_results)
        
        # Format the report
        report_content = self.report_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            analysis_id=analysis_id,
            nps=pipe_instance.nps,
            schedule=pipe_instance.schedule,
            pressure_class=pipe_instance.pressure_class,
            metallurgy=pipe_instance.metallurgy,
            pressure=pipe_instance.pressure,
            pipe_config=pipe_instance.pipe_config,
            corrosion_rate=pipe_instance.corrosion_rate if pipe_instance.corrosion_rate else "Not specified",
            measured_thickness=analysis_results.get('measured_thickness', 'N/A'),
            year_inspected=analysis_results.get('year_inspected', 'N/A'),
            actual_thickness=actual_thickness,
            tmin_pressure=analysis_results.get('tmin_pressure', 0),
            tmin_structural=analysis_results.get('tmin_structural', 0),
            governing_thickness=analysis_results.get('governing_thickness', 0),
            governing_type=analysis_results.get('governing_type', 'Unknown'),
            retirement_limit=retirement_limit_str,
            api574_RL=api574_RL,
            pressure_adequate=pressure_adequate,
            structural_adequate=structural_adequate,
            retirement_status=retirement_status,
            api574_status=api574_status,
            above_api574=analysis_results.get('above_api574RL', 'N/A'),
            below_retirement=analysis_results.get('below_defaultRL', 'N/A'),
            life_span=analysis_results.get('life_span', 'N/A'),
            recommendations=recommendations,
            notes=notes
        )
        
        # Save the report
        if filename is None:
            filename = f"TMIN_report_{analysis_id}"
        
        filepath = self._get_filename_with_date(f"{filename}.txt")
        with open(filepath, 'w') as f:
            f.write(report_content)
        
        return filepath
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any], actual_thickness: float) -> str:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Check pressure design adequacy
        tmin_pressure = analysis_results.get('tmin_pressure', 0)
        if actual_thickness < tmin_pressure:
            recommendations.append("• IMMEDIATE ACTION REQUIRED: Actual thickness is below pressure design minimum")
            recommendations.append("• Consider pipe replacement or pressure reduction")
        
        # Check structural adequacy
        tmin_structural = analysis_results.get('tmin_structural', 0)
        if actual_thickness < tmin_structural:
            recommendations.append("• IMMEDIATE ACTION REQUIRED: Actual thickness is below structural minimum")
            recommendations.append("• Fit-for-service assessment recommended")
        
        # Check API 574 retirement limit
        api574_RL = analysis_results.get('api574_RL', 0)
        if api574_RL and actual_thickness < api574_RL:
            recommendations.append("• RETIREMENT RECOMMENDED: Below API 574 retirement limit")
            recommendations.append("• Immediate retirement or detailed engineering assessment required")
        
        # Check Retirement Limit
        retirement_limit = analysis_results.get('default_retirement_limit', 0)
        if retirement_limit and actual_thickness < retirement_limit:
            recommendations.append("• MONITORING REQUIRED: Below Retirement Limit")
            recommendations.append("• Increase inspection frequency")
        
        # Check life span
        life_span = analysis_results.get('life_span', None)
        if life_span is not None and life_span < 5:
            recommendations.append("• SHORT REMAINING LIFE: Less than 5 years estimated")
            recommendations.append("• Plan for replacement or detailed corrosion assessment")
        
        # If no issues found
        if not recommendations:
            recommendations.append("• Pipe thickness is adequate for current service conditions")
            recommendations.append("• Continue with normal inspection schedule")
        
        return "\n".join(recommendations)
    
    def _generate_notes(self, pipe_instance, analysis_results: Dict[str, Any]) -> str:
        """Generate additional notes about the analysis"""
        notes = []
        
        notes.append(f"• Analysis based on ASME B31.1 pressure design equations")
        notes.append(f"• Structural requirements from API 574 Table D.2")
        notes.append(f"• Y-coefficient used: {pipe_instance.get_Y_coefficient()}")
        
        if pipe_instance.corrosion_rate:
            notes.append(f"• Corrosion rate considered: {pipe_instance.corrosion_rate} mpy")
        else:
            notes.append("• No corrosion rate specified - life span calculation not performed")
        
        governing_type = analysis_results.get('governing_type', 'Unknown')
        notes.append(f"• Governing factor for design: {governing_type}")
        
        return "\n".join(notes)
    
    def generate_summary_report(self, pipe_instance, analysis_results: Dict[str, Any], 
                              actual_thickness: float, filename: Optional[str] = None) -> str:
        """
        Generate a brief summary report
        
        Args:
            pipe_instance: PIPE instance
            analysis_results: Results from analyze_pipe_thickness method
            actual_thickness: The actual measured thickness
            filename: Optional filename to save the report (without extension)
            
        Returns:
            str: Path to saved report file
        """
        
        # Determine overall status
        tmin_pressure = analysis_results.get('tmin_pressure', 0)
        tmin_structural = analysis_results.get('tmin_structural', 0)
        api574_RL = analysis_results.get('api574_RL', 0)
        retirement_limit = analysis_results.get('default_retirement_limit', None)

        # Filter out None values for min/max comparisons
        thickness_values = [tmin_pressure, tmin_structural, api574_RL]
        if retirement_limit is not None:
            thickness_values.append(retirement_limit)
        # Debug print
        print(f"DEBUG: tmin_pressure={tmin_pressure}, tmin_structural={tmin_structural}, api574_RL={api574_RL}, retirement_limit={retirement_limit}")
        print(f"DEBUG: thickness_values for min/max: {thickness_values}")

        # Find the maximum thickness requirement (most conservative)
        max_thickness = max(thickness_values) if thickness_values else 0
        
        # Determine overall status
        if actual_thickness >= max_thickness:
            status = "ADEQUATE"
        else:
            status = "INADEQUATE"
        
        # Generate summary content
        summary_template = """
TMIN SUMMARY REPORT
===================

Pipe Specifications:
NPS: {nps}" Schedule {schedule}
Pressure Class: {pressure_class}
Metallurgy: {metallurgy}
Design Pressure: {pressure} psi

Thickness Analysis:
Actual Thickness: {actual_thickness:.4f} inches
Governing Thickness: {governing_thickness:.4f} inches
Governing Factor: {governing_type}

Status: {status}

Key Findings:
{findings}

Recommendations:
{recommendations}

Report Generated: {timestamp}
"""
        
        # Generate findings
        findings = []
        if actual_thickness < tmin_pressure:
            findings.append("• Below pressure design minimum")
        if actual_thickness < tmin_structural:
            findings.append("• Below structural minimum")
        if api574_RL and actual_thickness < api574_RL:
            findings.append("• Below API 574 retirement limit")
        if retirement_limit and actual_thickness < retirement_limit:
            findings.append("• Below retirement limit")
        
        if not findings:
            findings.append("• All thickness requirements met")
        
        # Generate recommendations
        recommendations = []
        if status == "INADEQUATE":
            recommendations.append("• Immediate action required")
            recommendations.append("• Consider pipe replacement or pressure reduction")
        else:
            recommendations.append("• Continue with normal inspection schedule")
            if analysis_results.get('life_span'):
                recommendations.append(f"• Estimated remaining life: {analysis_results['life_span']:.1f} years")
        
        # Format summary
        summary_content = summary_template.format(
            nps=pipe_instance.nps,
            schedule=pipe_instance.schedule,
            pressure_class=pipe_instance.pressure_class,
            metallurgy=pipe_instance.metallurgy,
            pressure=pipe_instance.pressure,
            actual_thickness=actual_thickness,
            governing_thickness=analysis_results.get('governing_thickness', 0),
            governing_type=analysis_results.get('governing_type', 'Unknown'),
            status=status,
            findings="\n".join(findings),
            recommendations="\n".join(recommendations),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Save summary report
        if filename is None:
            filename = f"TMIN_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = self._get_filename_with_date(f"{filename}.txt")
        with open(filepath, 'w') as f:
            f.write(summary_content)
        
        return filepath 