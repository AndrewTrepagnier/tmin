"""
Test suite for core_dev.py - Development version of TMIN core functionality
"""
import pytest
import numpy as np
import sympy as sp
from tmin.core_dev import PIPE


class TestPIPECoreDev:
    """Test the core PIPE class functionality in core_dev.py"""
    
    def test_pipe_creation(self, sample_pipe):
        """Test basic pipe instance creation"""
        assert sample_pipe.pressure == 150.0
        assert sample_pipe.nps == 2.0
        assert sample_pipe.schedule == 40
        assert sample_pipe.pressure_class == 300
        assert sample_pipe.metallurgy == "Intermediate/Low CS"
        assert sample_pipe.yield_stress == 30000
        assert sample_pipe.corrosion_rate == 5.0
    
    def test_pipe_info_basic(self, sample_pipe):
        """Test basic pipe_info method"""
        metadata = sample_pipe.pipe_info(None)
        
        assert metadata['pressure'] == 150.0
        assert metadata['nps'] == 2.0
        assert metadata['schedule'] == 40
        assert metadata['metallurgy'] == "Intermediate/Low CS"
        assert metadata['yield_stress'] == 30000
    
    def test_get_table_info(self, sample_pipe):
        """Test table information retrieval"""
        table_info = sample_pipe.get_table_info()
        
        # Check that all expected keys are present
        expected_keys = [
            'outer_diameter', 'inner_diameter', 'allowable_stress',
            'joint_type', 'y_coefficient', 'centerline_radius'
        ]
        for key in expected_keys:
            assert key in table_info
        
        # Check that values are reasonable
        assert table_info['outer_diameter'] > 0
        assert table_info['inner_diameter'] > 0
        assert table_info['allowable_stress'] > 0
        assert table_info['y_coefficient'] > 0
    
    def test_allowable_stress_calculation(self, sample_pipe):
        """Test allowable stress calculation (2/3 of yield stress)"""
        allowable_stress = sample_pipe.get_allowable_stress()
        expected = 30000 * (2/3)
        assert abs(allowable_stress - expected) < 1e-6
    
    def test_outer_diameter_lookup(self, sample_pipe):
        """Test outer diameter lookup from NPS"""
        od = sample_pipe.get_outer_diameter()
        assert od > 0
        assert isinstance(od, float)
    
    def test_inner_diameter_lookup(self, sample_pipe):
        """Test inner diameter lookup from schedule and NPS"""
        id_val = sample_pipe.get_inner_diameter()
        assert id_val > 0
        assert isinstance(id_val, float)
    
    def test_y_coefficient_lookup(self, sample_pipe):
        """Test Y coefficient lookup"""
        y_coeff = sample_pipe.get_y_coefficient()
        assert y_coeff > 0
        assert isinstance(y_coeff, float)
    
    def test_centerline_radius_lookup(self, sample_pipe):
        """Test centerline radius lookup"""
        radius = sample_pipe.get_centerline_radius()
        assert radius > 0
        assert isinstance(radius, float)
    
    def test_joint_type_info(self, sample_pipe):
        """Test joint type information"""
        joint_info = sample_pipe.get_joint_type()
        
        assert 'joint_efficiency' in joint_info
        assert 'weld_strength_reduction' in joint_info
        assert joint_info['joint_efficiency'] == 1.0
        assert joint_info['weld_strength_reduction'] == 1.0
    
    def test_static_methods(self, sample_pipe):
        """Test static utility methods"""
        # Test inches to mils conversion
        inches_val = 0.1
        mils_val = sample_pipe.inches_to_mils(inches_val)
        assert abs(mils_val - 100.0) < 1e-6
        
        # Test mils to inches conversion
        mils_val = 100.0
        inches_val = sample_pipe.mils_to_inches(mils_val)
        assert abs(inches_val - 0.1) < 1e-6
    
    def test_time_elapsed_calculation(self, sample_pipe):
        """Test time elapsed calculation"""
        # Test with year only
        time_elapsed = sample_pipe._calculate_time_elapsed(2020)
        assert time_elapsed > 0
        
        # Test with year and month
        time_elapsed = sample_pipe._calculate_time_elapsed(2020, 6)
        assert time_elapsed > 0
    
    def test_format_inspection_date(self, sample_pipe):
        """Test inspection date formatting"""
        date_str = sample_pipe._format_inspection_date(2020)
        assert date_str == "2020-01"
        
        date_str = sample_pipe._format_inspection_date(2020, 6)
        assert date_str == "2020-06"


class TestAnalysisMethods:
    """Test analysis calculation methods"""
    
    def test_tmin_pressure_straight(self, sample_pipe):
        """Test pressure thickness calculation for straight pipe"""
        # Get enriched data
        metadata = sample_pipe.pipe_info(None)
        table_info = sample_pipe.get_table_info()
        enriched_data = sample_pipe.pipe_info(metadata, table_info)
        
        # Calculate pressure thickness
        tmin_pressure = sample_pipe.tmin_pressure(enriched_data)
        
        assert tmin_pressure > 0
        assert isinstance(tmin_pressure, float)
    
    def test_tmin_pressure_elbow(self, sample_pipe_elbow):
        """Test pressure thickness calculation for elbow pipe"""
        # Get enriched data
        metadata = sample_pipe_elbow.pipe_info(None)
        table_info = sample_pipe_elbow.get_table_info()
        enriched_data = sample_pipe_elbow.pipe_info(metadata, table_info)
        
        # Calculate pressure thickness
        tmin_pressure = sample_pipe_elbow.tmin_pressure(enriched_data)
        
        assert tmin_pressure > 0
        assert isinstance(tmin_pressure, float)
    
    def test_tmin_structural(self, sample_pipe):
        """Test structural thickness calculation"""
        # Get enriched data
        metadata = sample_pipe.pipe_info(None)
        table_info = sample_pipe.get_table_info()
        enriched_data = sample_pipe.pipe_info(metadata, table_info)
        
        # Calculate structural thickness
        tmin_structural = sample_pipe.tmin_structural(enriched_data)
        
        assert tmin_structural > 0
        assert isinstance(tmin_structural, float)
    
    def test_calculate_corrosion_allowance(self, sample_pipe):
        """Test corrosion allowance calculation"""
        excess_thickness = 0.05  # inches
        corrosion_rate = 5.0  # MPY
        
        remaining_life = sample_pipe.calculate_corrosion_allowance(excess_thickness, corrosion_rate)
        
        assert remaining_life > 0
        assert isinstance(remaining_life, float)


class TestCompleteAnalysis:
    """Test complete analysis workflow"""
    
    def test_analyze_method(self, sample_pipe):
        """Test the main analyze method"""
        result = sample_pipe.analyze(measured_thickness=0.25, year_inspected=2024)
        
        # Check that all expected keys are present
        expected_keys = [
            'pressure', 'nps', 'schedule', 'metallurgy', 'yield_stress',
            'outer_diameter', 'inner_diameter', 'allowable_stress',
            'measured_thickness', 'current_thickness', 'tmin_pressure',
            'tmin_structural', 'governing_thickness', 'governing_type',
            'flag', 'status', 'message', 'sympy_report'
        ]
        
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Check flag values
        assert result['flag'] in ['GREEN', 'YELLOW', 'RED']
        assert result['status'] in ['SAFE_TO_CONTINUE', 'FFS_RECOMMENDED', 'IMMEDIATE_RETIREMENT']
        
        # Check thickness values
        assert result['tmin_pressure'] > 0
        assert result['tmin_structural'] > 0
        assert result['governing_thickness'] > 0
        assert result['current_thickness'] > 0
    
    def test_analyze_generator(self, sample_pipe):
        """Test the analyze_generator method"""
        stages = []
        for stage_name, data in sample_pipe.analyze_generator(measured_thickness=0.25, year_inspected=2024):
            stages.append(stage_name)
        
        # Check that all expected stages are present
        expected_stages = ["metadata", "enriched", "analysis_results", "final", "sympy_report"]
        assert stages == expected_stages
        
        # Test that we can get the final result
        final_result = list(sample_pipe.analyze_generator(measured_thickness=0.25, year_inspected=2024))[-1][1]
        assert 'equation' in final_result  # SymPy report should have equation
        assert 'input_parameters' in final_result  # SymPy report should have input parameters


class TestSymPyIntegration:
    """Test SymPy mathematical report integration"""
    
    def test_quick_report_structure(self, sample_pipe):
        """Test SymPy report structure"""
        # Get analysis data
        analysis_data = sample_pipe.analyze(measured_thickness=0.25, year_inspected=2024)
        
        # Check SymPy report is included
        assert 'sympy_report' in analysis_data
        sympy_report = analysis_data['sympy_report']
        
        # Check report structure
        expected_keys = ['equation', 'input_parameters', 'computed_outputs', 'pipe_specs', 'analysis_summary']
        for key in expected_keys:
            assert key in sympy_report
    
    def test_sympy_equation_generation(self, sample_pipe):
        """Test SymPy equation generation"""
        analysis_data = sample_pipe.analyze(measured_thickness=0.25, year_inspected=2024)
        sympy_report = analysis_data['sympy_report']
        
        # Check equation components
        equation = sympy_report['equation']
        assert 'symbolic' in equation
        assert 'substituted' in equation
        assert 'latex' in equation
        assert 'latex_substituted' in equation
        
        # Check that LaTeX is generated
        assert isinstance(equation['latex'], str)
        assert len(equation['latex']) > 0
    
    def test_input_parameters_table(self, sample_pipe):
        """Test input parameters table"""
        analysis_data = sample_pipe.analyze(measured_thickness=0.25, year_inspected=2024)
        sympy_report = analysis_data['sympy_report']
        
        input_table = sympy_report['input_parameters']
        
        # Check table structure
        assert 'Parameter' in input_table
        assert 'Symbol' in input_table
        assert 'Value' in input_table
        assert 'Units' in input_table
        
        # Check that all lists have same length
        lengths = [len(input_table[key]) for key in input_table.keys()]
        assert all(length == lengths[0] for length in lengths)
    
    def test_computed_outputs_table(self, sample_pipe):
        """Test computed outputs table"""
        analysis_data = sample_pipe.analyze(measured_thickness=0.25, year_inspected=2024)
        sympy_report = analysis_data['sympy_report']
        
        output_table = sympy_report['computed_outputs']
        
        # Check table structure
        assert 'Result' in output_table
        assert 'Value' in output_table
        assert 'Units' in output_table
        
        # Check that all lists have same length
        lengths = [len(output_table[key]) for key in output_table.keys()]
        assert all(length == lengths[0] for length in lengths)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_schedule(self):
        """Test error handling for invalid schedule"""
        pipe = PIPE(
            pressure=150.0,
            nps=2.0,
            schedule=999,  # Invalid schedule
            pressure_class=300,
            metallurgy="Intermediate/Low CS",
            yield_stress=30000
        )
        
        with pytest.raises(ValueError):
            pipe.get_inner_diameter()
    
    def test_future_inspection_date(self, sample_pipe):
        """Test error handling for future inspection date"""
        with pytest.raises(ValueError):
            sample_pipe._calculate_time_elapsed(2030)  # Future date
    
    def test_invalid_month(self, sample_pipe):
        """Test error handling for invalid month"""
        with pytest.raises(ValueError):
            sample_pipe.analyze(measured_thickness=0.25, year_inspected=2020, month_inspected=13)  # Invalid month
    
    def test_measured_thickness_too_large(self, sample_pipe):
        """Test error handling for measured thickness larger than wall thickness"""
        with pytest.raises(ValueError):
            sample_pipe.analyze(measured_thickness=10.0)  # Unreasonably large


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""
    
    def test_carbon_steel_pipe_scenario(self):
        """Test realistic carbon steel pipe scenario"""
        pipe = PIPE(
            pressure=200.0,
            nps=4.0,
            schedule=40,
            pressure_class=300,
            metallurgy="Intermediate/Low CS",
            yield_stress=35000,
            corrosion_rate=8.0
        )
        
        result = pipe.analyze(measured_thickness=0.28, year_inspected=2022, month_inspected=6)
        
        # Should be a reasonable analysis
        assert result['flag'] in ['GREEN', 'YELLOW', 'RED']
        assert result['tmin_pressure'] > 0
        assert result['tmin_structural'] > 0
    
    def test_stainless_steel_pipe_scenario(self, sample_pipe_ss):
        """Test realistic stainless steel pipe scenario"""
        result = sample_pipe_ss.analyze(measured_thickness=0.15, year_inspected=2023)
        
        # Should be a reasonable analysis
        assert result['flag'] in ['GREEN', 'YELLOW', 'RED']
        assert result['tmin_pressure'] > 0
        assert result['tmin_structural'] > 0
    
    def test_elbow_pipe_scenario(self, sample_pipe_elbow):
        """Test realistic elbow pipe scenario"""
        result = sample_pipe_elbow.analyze(measured_thickness=0.22, year_inspected=2021, month_inspected=3)
        
        # Should be a reasonable analysis
        assert result['flag'] in ['GREEN', 'YELLOW', 'RED']
        assert result['tmin_pressure'] > 0
        assert result['tmin_structural'] > 0
