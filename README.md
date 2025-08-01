# TMIN
[![PyPI downloads](https://img.shields.io/pypi/dm/tmin.svg)](https://pypi.org/project/tmin/)
![License](https://img.shields.io/pypi/l/tmin)    
[![PyPI version](https://badge.fury.io/py/tmin.svg)](https://badge.fury.io/py/tmin)
![Python](https://img.shields.io/pypi/pyversions/tmin)

**The 5-minute pipe thickness analysis tool that tells you if your process pipe is safe to operate.**

All process pipes corrode over time, this package helps determine whether the pipe has structural/pressure integrity and is ASME/API-compliant, all with one python function.

---
## You have an inspection report. Now what?

**Scenario:** UT readings show your 2" Schedule 40 pipe has 0.060" wall thickness. You need to know if it's safe to operate and how much time remains before pipe retirement.

**The Previous Way:** Hours of manual calculations, code book lookups, and hoping you didn't miss anything.

**The TMIN way:** One Python script, instant answers.

![pipe_thinning](https://github.com/user-attachments/assets/abba85a5-096e-4824-98ee-4d90ff32e206)


---

## Get Started in 60 Seconds

### 1. Install
```bash
pip install tmin
```

### 2. Run ASME/API-Compliant Analysis in 1 Minute
```python
import tmin

# Create pipe instance
pipe = tmin.PIPE(
    schedule="40",
    nps="2", 
    pressure=50.0,
    pressure_class=150,
    metallurgy="Intermediate/Low CS",
    allowable_stress=23333.0
)

# Analyze thickness
results = pipe.analysis(measured_thickness=0.060)
print(f"Safe to operate: {results['actual_thickness'] > results['governing_thickness']}")
print(f"Remaining life: {results['life_span']} years")
```

**Result:** Professional report with compliance status, remaining life, and visual analysis in under 30 seconds.

### 3. Get Results
```python
print(f"✅ Pressure Design: {results['tmin_pressure']:.4f}\" minimum required")
print(f"✅ Structural: {results['tmin_structural']:.4f}\" minimum required")
print(f"✅ Current: {results['actual_thickness']:.4f}\" measured thickness")
print(f"✅ Status: {'SAFE TO OPERATE' if results['actual_thickness'] > results['governing_thickness'] else 'RETIRE IMMEDIATELY'}")
print(f"✅ Remaining Life: {results['life_span']} years at {pipe.corrosion_rate} mpy corrosion")
```

**Generate Full Report:**
```python
# Create professional reports and visualizations
report_files = pipe.report(measured_thickness=0.060)
print("Generated:", list(report_files.keys()))
```

---

## Engineering Problems Solved

**"Is this pipe safe?"**
```python
import tmin
pipe = tmin.PIPE(schedule="40", nps="2", pressure=50.0, 
                pressure_class=150, metallurgy="Intermediate/Low CS", 
                allowable_stress=23333.0)
results = pipe.analysis(measured_thickness=0.060)
print(f"Safe to operate: {results['actual_thickness'] > results['governing_thickness']}")
```

**"How much time do we have?"**
```python
# TMIN automatically calculates remaining life based on corrosion rate
print(f"Remaining life: {results['life_span']} years")
```

**"Are we code compliant?"**
```python
# TMIN checks against ASME B31.1 and API 574 automatically
print(f"API 574 compliant: {results['actual_thickness'] > results['api574_RL']}")
```

**"What's our corrosion allowance?"**
```python
# TMIN calculates safety margin above retirement limits
print(f"Corrosion allowance: {results['above_api574RL']:.4f}\" inches")
```

---

## Why TMIN

**Speed**
30 seconds from inspection data to compliance report. No manual calculations or code book lookups. Instant visual analysis.

**Accuracy**
Built on ASME B31.1 and API 574 standards. Automatic governing factor determination. Time-based corrosion adjustment.

**Professional Output**
Auto-generated reports with timestamps. Visual thickness analysis charts. Compliance documentation for audits.

**Real-World Ready**
Handles corrosion rates and inspection dates. Supports multiple metallurgies and pipe schedules. TOML configuration for batch analysis.

---

## What TMIN Analyzes

**Pressure Design (ASME B31.1)**
Minimum wall thickness for pressure containment. Temperature effects and material properties. Y-coefficient calculations.

**Structural Requirements (API 574)**
Minimum thickness for structural integrity. Pipe deflection and weight loading. Table D.2 compliance.

**Corrosion Analysis**
Time-based thickness adjustment. Remaining life prediction. Corrosion allowance calculations.

**Compliance Reporting**
Governing factor identification. Safety margin analysis. Professional documentation.

---

## Supported Specifications

| Schedules | NPS Sizes | Pressure Classes | Metallurgies |
|-----------|-----------|------------------|--------------|
| 10, 40, 80, 120, 160 | 0.5" to 24" | 150, 300, 600, 900, 1500, 2500 | Carbon Steel, Stainless Steel, Nickel Alloys |

---

## Perfect For

**Mechanical Integrity Engineers** - Quick compliance checks
**Reliability Specialists** - Life extension analysis  
**Operations Teams** - Emergency thickness evaluations
**Inspection Contractors** - Professional reporting
**Engineering Consultants** - Client deliverables

---

## Command Line Interface

**Basic Analysis**
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060
```

**With Corrosion Rate**
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060 -r 10 -y 2023
```

**Using Configuration File**
```bash
# Create pipe_config.toml with your parameters
tmin -f pipe_config.toml -t 0.060
```

**Custom Output Directory**
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060 -o ./my_reports
```

---

## Test It Yourself

```bash
# Install and test
pip install tmin
python -m pytest tests/test_core.py -v
```

---

## Need Help?

**Documentation:** Built-in help with `tmin --help`
**Examples:** See `example_pipe_config.toml`
**Contact:** andrew[dot]trepagnier[at]icloud[dot]com

---

## Disclaimer

TMIN is a decision support tool for qualified engineers. Always use professional judgment and follow applicable codes and standards.

**License:** MIT



