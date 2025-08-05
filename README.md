# TMIN: The Fast Pipe Thickness Analysis Tool

<p align="left">
  <img src="https://github.com/user-attachments/assets/52007543-8109-44ff-845e-c6a809a89a38" alt="TMIN Logo" width="700" />
</p>

[![Downloads per month](https://pepy.tech/badge/tmin/month)](https://pepy.tech/project/tmin)
[![PyPI version](https://badge.fury.io/py/tmin.svg)](https://badge.fury.io/py/tmin)
![License](https://img.shields.io/pypi/l/tmin)
[![Blog](https://img.shields.io/badge/Updates-blog-purple)](https://your-blog-link.com)
[![Blog](https://img.shields.io/badge/dev-wiki-gold)](https://your-blog-link.com)
[![Blog](https://img.shields.io/badge/Important-DesignDoc-pink)](https://your-blog-link.com)

TMIN is an open source software designed to help engineers determine if corroded process piping in refineries and pertrochemical plants are **safe** and **API-compliant** — in seconds.

Many oil and gas companies are faced with maintaining thousands of miles of 100+ year old piping networks supporting multi-million dollar/year processing operations. There is rarely a simple solution to immediately shutdown a process pipe - as these shutdowns more often than not impact other units and cost companies millions in time and resources.

***This is more than a python package, it is a comprehensive engineering decision support system for critical infrastructure safety and operational continuity.***

---

# Getting Started

### Installation:

```bash
pip install tmin
```


### Suppose the following scenario:

   <img width="400" height="250" alt="image" src="https://github.com/user-attachments/assets/1f87dcb1-7d17-4c25-888b-6d9131098ec0"/>



RT findings show your 2" Schedule 40 pipe has 0.060" wall thickness. You need to know if it's safe to operate and how much time remains before pipe retirement.




**The Previous Way:** time consuming handwritten calculations, tedious code book lookups, and hours of typing full assessment reports

**With TMIN:** One Python script, instant answers.

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



