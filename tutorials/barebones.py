"""Minimal tmin workflow — one script, one dictionary, three calls."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tmin

input_dict = {
    # ---- Memorandum fields ----
    "Site Name": "Beaumont Refinery",
    "Fixed Equipment Department": "BAES",
    "Unit": "OMCC1",
    "Company": "ExxonMobil",
    "Pipe Circuit No.": "077-072-01",
    "Size": "6",
    "Circuit Fluid Service": "Gas Oil",
    "Type of Equipment": "pipe",
    "subcomponent": "straight-run",
    "Author Name": "Andrew Trepagnier",
    "Author Phone Number": "409-XXX-XXXX",
    "Inspection type": "RT",
    "TML number": "TML-400.EXT",


    "Current thickness to date": "0.097 in",
    "Internal/External": "external",
    "Degradation Mechanism": "Corrosion Under Insulation",
    "Incoming Outage timestamp": "January 2027", # Delete this
    "SHE consequence level": "II",
    "failure types": "corrosion hole",
    "Consequence type": "fire scenario",


    "Date AR/T = 1": "01-Sep-2029",
    "CR": "8",
    "CR description": "Conservative assessment based on EDD guidance.",
    "ESL Evaluation": "ESL - Above FFS",
    "AR/T Basis": "(AR/T Basis to be filled in by user)",
    "AR/T progression": "(AR/T progression to be filled in by user)",



    # ---- ESL Evaluation Summary ----
    "EDD Number": "1B (CUI)",
    "percent_undamaged": "0%",
    "percent_damaged": "100%",
    "inspection_effectiveness": "Medium",
    "number_of_rt_per_tml": "1",
    # Omit percent_ca_consumed to auto-fill %CAC vs PMG from TML vs nominal/PMG
    "coating_status": "failed", #adequate or failed or unknown
    "mitigation": "recoating, insulation removal",
    "General Notes": "", # Remove this




    # ---- Pipe / tmin calculation inputs ----
    # Design basis (used for B31.3 pressure tmin):
    "nps": 6, 
    "pressure": 285,
    "design_temp": 100,
    # Operating conditions (for memorandum only — what the line actually runs at):
    "operating_pressure": 50,
    "operating_temperature": 100,


    
    "schedule": 40,
    "pressure_class": 150,
    "metallurgy": "Intermediate/Low CS",
    "allowable_stress": 15000,     
    "allowable_stress_code_year": "1959",
    "allowable_stress_code_source": "MATDAT ASME Sec. IIV Div. 1", # Or set one line instead: "allowable_stress_basis": "1966 B31.3 Allowables",
    "current_thickness": 0.097,

    # ---- Corrosion rate calculation (optional) ----
    "install_date": "01-1966",       # MM-YYYY
    "UT_date": "03-2026",            # MM-YYYY of latest UT readings
}

instance = tmin.TMIN(input_dict)
result = instance.calculate()
print(instance.report())
