#!/usr/bin/env python3
"""
Basic TMIN Example
==================

Minimal example showing core TMIN functionality.
"""

from tmin.core import PIPE

# Create a pipe instance

pipe = PIPE(
    nps=2.0,
    schedule=40,
    pressure_class=300,
    pressure=1000,
    design_temp=900,
    pipe_config="straight",
    metallurgy="Intermediate/Low CS",
    yield_stress=35000,
    corrosion_rate=10.0,
    API_table="2025"
)

# Perform analysis
results = pipe.analysis(
    measured_thickness=0.200,
    year_inspected=2024,
    month_inspected=6,
    joint_type='Seamless'
)




# Print basic results
print(f"Flag: {results['flag']}")
print(f"Actual Thickness: {results['actual_thickness']:.4f} inches")
print(f"Pressure Minimum: {results['tmin_pressure']:.4f} inches")
print(f"Structural Minimum: {results['tmin_structural']:.4f} inches")

# Generate a report using cached analysis
report = pipe.report("IPYNB")
print(f"Report saved: {report['file_path']}") 