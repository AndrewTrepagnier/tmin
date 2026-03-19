"""Minimal tmin workflow — one script, one dictionary, three calls."""

import tmin

input_dict = {
    # ---- Memorandum fields ----
    "Site Name": "Example Site",
    "Fixed Equipment Department": "Fixed Equipment",
    "Unit": "CRUDE UNIT",
    "Company": "Example Co.",
    "Pipe Circuit No.": "077-072-01",
    "Size": "8",
    "Circuit Fluid Service": "Spent Caustic",
    "Type of Equipment": "pipe",
    "subcomponent": "straight-run",
    "Author Name": "tmin",
    "Author Phone Number": "",
    "Inspection type": "RT",
    "TML number": "TML-01",


    "Current thickness to date": "0.112 in",
    "Internal/External": "internal",
    "Degradation Mechanism": "alkaline corrosion",
    "Incoming Outage timestamp": "January 2027",
    "SHE consequence level": "II",
    "failure types": "pinhole",
    "Consequence type": "fire scenario",


    "Date AR/T = 1": "01-Mar-2029",
    "CR": "5",
    "CR description": "General",
    "ESL Evaluation": "Acceptable to next outage",
    "AR/T Basis": "Calculated from inspection data",
    "General Notes": "",

    # ---- Pipe / tmin calculation inputs ----
    "pressure": 285,
    "design_temp": 100,
    "nps": 8,
    "schedule": 40,
    "pressure_class": 150,
    "metallurgy": "Intermediate/Low CS",
    "allowable_stress": 23333,
    "current_thickness": 0.112,

    # ---- Corrosion rate calculation (optional) ----
    "install_date": "01-1985",       # MM-YYYY
    "UT_date": "03-2026",            # MM-YYYY of latest UT readings
}

instance = tmin.TMIN(input_dict)
result = instance.calculate()
print(instance.report())
