import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import os

class ThicknessVisualizer:
    """
    Creates visualizations for pipe thickness analysis
    """
    
    def __init__(self):
        self.reports_dir = "Reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _get_filename_with_date(self, base_name: str, filename: Optional[str] = None) -> str:
        """Generate filename with date prefix"""
        if filename is None:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{date_str}_{base_name}"
        
        return os.path.join(self.reports_dir, filename)
    
    def create_thickness_number_line(self, pipe_instance, analysis_results: Dict[str, Any], 
                                   actual_thickness: float, filename: Optional[str] = None) -> str:
        """
        Create a cross-sectional pipe wall profile visualization showing all thickness values and regions.
        Thickness measurements are from OD inward.
        """
        # Extract values
        tmin_pressure = analysis_results.get('tmin_pressure', 0)
        tmin_structural = analysis_results.get('tmin_structural', 0)
        api574_RL = analysis_results.get('api574_RL', 0)
        default_retirement_limit = analysis_results.get('default_retirement_limit', None)
        measured_thickness = analysis_results.get('measured_thickness', 0)
        
        # Get actual pipe dimensions
        try:
            nominal_id = pipe_instance.get_ID()
            od = pipe_instance.get_OD()
        except:
            # Fallback if we can't get the actual dimensions
            nominal_id = 0.0
            od = measured_thickness + 0.02
        
        # Calculate positions from OD inward (thickness measurements)
        # OD is at the rightmost position
        od_pos = od
        actual_id_pos = od - measured_thickness  # Actual ID position from OD
        nominal_id_pos = nominal_id  # Nominal ID position
        
        # Calculate limit positions from OD inward
        api574_rl_pos = od - api574_RL if api574_RL else None
        default_rl_pos = od - default_retirement_limit if default_retirement_limit else None
        min_pressure_pos = od - tmin_pressure
        
        # Create figure with proper graph style
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Set up the plot with proper axis
        ax.set_xlim(nominal_id_pos - 0.01, od_pos + 0.01)
        ax.set_ylim(0, 1)
        
        # Add grid and tick marks
        ax.grid(True, alpha=0.3, axis='x')
        ax.set_xticks(np.arange(nominal_id_pos, od_pos + 0.01, 0.01))
        ax.set_xticklabels([f'{x:.3f}' for x in np.arange(nominal_id_pos, od_pos + 0.01, 0.01)], rotation=45, ha='right')
        ax.set_yticks([])
        
        # Fill regions
        # Fluid region (from nominal ID to actual ID)
        ax.fill_betweenx([0, 1], nominal_id_pos, actual_id_pos, color='#b3e6ff', alpha=0.7, label='Fluid')
        # Remaining wall (from actual ID to OD)
        ax.fill_betweenx([0, 1], actual_id_pos, od_pos, color='#e6e6e6', alpha=0.7, label='Remaining Pipe Wall')
        # OD bar
        ax.fill_betweenx([0, 1], od_pos-0.002, od_pos, color='gray', alpha=1, label='OD')

        # Draw vertical lines for all limits with proper styles
        ax.axvline(nominal_id_pos, color='black', linewidth=3, label='Nominal ID')
        ax.axvline(actual_id_pos, color='blue', linewidth=3, label='Actual Thk.')
        if api574_rl_pos:
            ax.axvline(api574_rl_pos, color='purple', linestyle='--', linewidth=3, label='API 574 RL')
        if default_rl_pos:
            ax.axvline(default_rl_pos, color='orange', linestyle='--', linewidth=3, label='Default RL')
        ax.axvline(min_pressure_pos, color='red', linestyle='--', linewidth=3, label='Min. Pressure Thk.')

        # Add value labels at the top
        ax.text(nominal_id_pos, 1.05, f'Nominal Inner Dia.\n{nominal_id_pos:.3f}"', 
               color='black', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)
        
        if default_rl_pos:
            ax.text(default_rl_pos, 1.05, f'Default Retirement Limit\n{default_retirement_limit:.3f}"', 
                   color='orange', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)
        
        ax.text(actual_id_pos, 1.05, f'Actual Inner Dia.\n{measured_thickness:.3f}" from OD', 
               color='blue', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)
        
        if api574_rl_pos:
            ax.text(api574_rl_pos, 1.05, f'API 574 Retirement Limit\n{api574_RL:.3f}" from OD', 
                   color='purple', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)
        
        ax.text(min_pressure_pos, 1.05, f'Min. Pressure Containing\n{tmin_pressure:.3f}" from OD', 
               color='red', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)
        
        ax.text(od_pos, 1.05, f'Outer Dia.\n{od_pos:.3f}"', 
               color='gray', fontsize=12, fontweight='bold', ha='center', va='bottom', rotation=90)

        # Add axis labels
        ax.text(nominal_id_pos - 0.01, 0.5, 'Nominal Inner Dia.', 
               color='black', fontsize=14, fontweight='bold', ha='right', va='center', rotation=90)
        ax.text(od_pos + 0.01, 0.5, 'Outer Dia.', 
               color='gray', fontsize=14, fontweight='bold', ha='left', va='center', rotation=90)

        # Set labels and title
        ax.set_xlabel('Profile of Pipe Wall (inches)', fontsize=14, fontweight='bold')
        ax.set_title('TMIN - Pipe Wall Thickness Analysis', fontsize=16, fontweight='bold')

        # Custom legend
        custom_lines = [
            plt.Line2D([0], [0], color='#b3e6ff', lw=10, label='Fluid'),
            plt.Line2D([0], [0], color='#e6e6e6', lw=10, label='Remaining Pipe Wall'),
            plt.Line2D([0], [0], color='gray', lw=10, label='OD'),
            plt.Line2D([0], [0], color='black', lw=3, label='Nominal ID'),
            plt.Line2D([0], [0], color='blue', lw=3, label='Actual Thk.'),
            plt.Line2D([0], [0], color='purple', lw=3, linestyle='--', label='API 574 RL'),
            plt.Line2D([0], [0], color='orange', lw=3, linestyle='--', label='Default RL'),
            plt.Line2D([0], [0], color='red', lw=3, linestyle='--', label='Min. Pressure Thk.'),
        ]
        ax.legend(handles=custom_lines, loc='lower right', fontsize=10, frameon=True)

        plt.tight_layout()

        # Save plot
        if filename is None:
            filename = f"thickness_analysis_number_line"
        filepath = self._get_filename_with_date(f"{filename}.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return filepath
    
    def create_comparison_chart(self, analysis_results: Dict[str, Any], 
                               actual_thickness: float, filename: Optional[str] = None) -> str:
        """
        Create a bar chart comparing different thickness values
        
        Args:
            analysis_results: Results from analyze_pipe_thickness method
            actual_thickness: The actual measured thickness
            filename: Optional filename to save the plot (without extension)
            
        Returns:
            str: Path to saved plot file
        """
        
        # Extract values
        tmin_pressure = analysis_results.get('tmin_pressure', 0)
        tmin_structural = analysis_results.get('tmin_structural', 0)
        api574_RL = analysis_results.get('api574_RL', 0)
        retirement_limit = analysis_results.get('default_retirement_limit', None)
        governing_thickness = analysis_results.get('governing_thickness', 0)
        
        # Prepare data for plotting
        categories = ['Actual', 'Pressure t-min', 'Structural t-min', 'Governing']
        values = [actual_thickness, tmin_pressure, tmin_structural, governing_thickness]
        colors = ['blue', 'red', 'orange', 'darkred']
        
        # Add API 574 RL if available
        if api574_RL:
            categories.append('API 574 RL')
            values.append(api574_RL)
            colors.append('purple')
        
        # Add retirement limit if available
        if retirement_limit:
            categories.append('Retirement Limit')
            values.append(retirement_limit)
            colors.append('green')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bars
        bars = ax.bar(categories, values, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.4f}"', ha='center', va='bottom')
        
        # Customize plot
        ax.set_ylabel('Thickness (inches)', fontsize=12)
        ax.set_title('TMIN - Thickness Comparison Chart', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save plot
        if filename is None:
            filename = f"thickness_comparison_chart"
        
        filepath = self._get_filename_with_date(f"{filename}.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath 