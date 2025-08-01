###########################################
# Tutorial 1
###########################################

# Step 1: Install TMIN (uncomment if needed)
# pip install tmin

import tmin as tmin


# Make a variable of your thickness measurement and when it was measured 
measured_thickness = 0.060 #in
year_inspected = 2023

# Step 3: Instatiate with details about the pipe
pipe = tmin.PIPE(
    schedule="40",
    nps="2",
    pressure=200.0,
    pressure_class=300,
    metallurgy="Intermediate/Low CS",
    allowable_stress=23333.0,
    corrosion_rate=5.0,
    default_retirement_limit=0.080
)

# Step 4: Run analysis
results = pipe.analysis(measured_thickness, year_inspected)

# Step 5: Generate reports and visuals
# Generate full report with visualizations
report_files = pipe.report(measured_thickness, year_inspected)


print("\nDone! Check the Reports folder for your files.") 