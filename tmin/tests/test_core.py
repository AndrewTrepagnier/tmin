#!/usr/bin/env python3
"""
Test script for TMIN package
Contains usage examples and test cases for pipe thickness analysis
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import the tmin module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tmin.core import PIPE

def test_basic_pipe_analysis():
    """Test basic pipe analysis functionality"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,  # 35000 * 2/3 for A106 GR B
        corrosion_rate=10.0,
        default_retirement_limit=0.050
    )
    
    results = pipe.analysis(measured_thickness=0.060)
    
    assert results is not None
    assert "tmin_pressure" in results
    assert "tmin_structural" in results
    assert "governing_thickness" in results
    assert "governing_type" in results
    assert "measured_thickness" in results
    assert "actual_thickness" in results

def test_time_based_corrosion_calculation():
    """Test time-based corrosion calculation with inspection year"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        corrosion_rate=10.0,  # 10 mpy = 0.010 inches per year
        default_retirement_limit=0.050
    )
    
    # Test with inspection 2 years ago
    results = pipe.analysis(measured_thickness=0.060, year_inspected=2023)
    
    assert results is not None
    assert results["measured_thickness"] == 0.060
    assert results["year_inspected"] == 2023
    # Corrosion loss should be 0.010 * 2 = 0.020 inches
    # Present-day thickness should be 0.060 - 0.020 = 0.040 inches
    assert abs(results["actual_thickness"] - 0.040) < 0.001

def test_pipe_without_corrosion_rate():
    """Test pipe analysis without corrosion rate"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        default_retirement_limit=0.050
    )
    
    results = pipe.analysis(measured_thickness=0.060, year_inspected=2023)
    
    assert results is not None
    assert results["life_span"] is None  # Should be None when no corrosion rate
    assert results["actual_thickness"] == 0.060  # Should use measured thickness as-is

def test_pipe_without_retirement_limit():
    """Test pipe analysis without default retirement limit"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        corrosion_rate=10.0
    )
    
    results = pipe.analysis(measured_thickness=0.060)
    
    assert results is not None
    assert results["default_retirement_limit"] is None
    assert results["below_defaultRL"] is None

def test_edge_case_thickness_below_api574():
    """Test case where actual thickness is below API 574 retirement limit"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        corrosion_rate=10.0,
        default_retirement_limit=0.050
    )
    
    # Use a very low measured thickness that should result in present-day thickness below API 574 limit
    results = pipe.analysis(measured_thickness=0.030, year_inspected=2023)
    
    assert results is not None
    assert results["above_api574RL"] is None  # Should be None when below limit

def test_practice_scenario():
    """Test a realistic practice scenario"""
    pipe = PIPE(
        schedule="40",
        nps="3",
        pressure=75.0,
        pressure_class=300,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        corrosion_rate=15.0,
        default_retirement_limit=0.080
    )
    
    results = pipe.analysis(measured_thickness=0.120, year_inspected=2022)
    
    assert results is not None
    assert results["measured_thickness"] == 0.120
    assert results["year_inspected"] == 2022
    # Corrosion loss should be 0.015 * 3 = 0.045 inches
    # Present-day thickness should be 0.120 - 0.045 = 0.075 inches
    assert abs(results["actual_thickness"] - 0.075) < 0.001

def test_future_inspection_year_error():
    """Test that future inspection years raise an error"""
    pipe = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0,
        corrosion_rate=10.0
    )
    
    with pytest.raises(ValueError, match="cannot be in the future"):
        pipe.analysis(measured_thickness=0.060, year_inspected=2030)

def test_nps_fraction_conversion():
    """Test that NPS fraction conversion works correctly"""
    # Test simple fractions
    pipe1 = PIPE(
        schedule="40",
        nps="3/4",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0
    )
    
    # Test mixed fractions
    pipe2 = PIPE(
        schedule="40",
        nps="1-1/2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0
    )
    
    # Test whole numbers
    pipe3 = PIPE(
        schedule="40",
        nps="2",
        pressure=50.0,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        allowable_stress=23333.0
    )
    
    assert pipe1._convert_nps_to_float("3/4") == 0.75
    assert pipe2._convert_nps_to_float("1-1/2") == 1.5
    assert pipe3._convert_nps_to_float("2") == 2.0

if __name__ == "__main__":
    pytest.main([__file__])
