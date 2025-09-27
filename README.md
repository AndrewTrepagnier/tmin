# TMIN - Pipe Thickness Analysis Tool

<p align="left">
  <img src="https://github.com/user-attachments/assets/52007543-8109-44ff-845e-c6a809a89a38" alt="TMIN Logo" width="700" />
</p>

[![Downloads](https://pepy.tech/badge/tmin)](https://pepy.tech/project/tmin)
[![PyPI version](https://badge.fury.io/py/tmin.svg)](https://badge.fury.io/py/tmin)
![License](https://img.shields.io/pypi/l/tmin)
[![Tests](https://github.com/AndrewTrepagnier/tmin/workflows/Tests/badge.svg)](https://github.com/AndrewTrepagnier/tmin/actions)
[![codecov](https://codecov.io/gh/AndrewTrepagnier/tmin/branch/main/graph/badge.svg)](https://codecov.io/gh/AndrewTrepagnier/tmin)
[![Python Versions](https://img.shields.io/pypi/pyversions/tmin.svg)](https://pypi.org/project/tmin/)
[![Blog](https://img.shields.io/badge/Updates-blog-purple)](https://your-blog-link.com)
[![Blog](https://img.shields.io/badge/dev-wiki-gold)](https://github.com/AndrewTrepagnier/tmin/wiki)
[![Blog](https://img.shields.io/badge/Important-DesignDoc-pink)](https://your-blog-link.com)

TMIN (an abbreviation for "minimum thickness") is an open source python package designed to help engineers determine if corroded process piping in refineries and pertrochemical plants are **safe** and **API-compliant** — in seconds.

Many oil and gas companies are faced with maintaining thousands of miles of 100+ year old piping networks supporting multi-million dollar/year processing operations. There is rarely a simple solution to immediately shutdown a process pipe - as these shutdowns more often than not impact other units and cost companies millions in time and resources.

***TMIN can be used as a conservative and rapid engineering support tool for assessing piping inspection data and determine how close the pipe is to its end of service life.***

---

# How to install and get started

### Installation:

```bash
pip install tmin
```

### Basic Usage
```python
from tmin import PIPE

# Create pipe instance
pipe = PIPE(
    pressure=50,           # Design pressure (psi)
    nps=2,                 # Nominal pipe size (inches)
    schedule=40,           # Pipe schedule
    pressure_class=150,    # Pressure class
    metallurgy="Intermediate/Low CS",
    yield_stress=23333     # Yield stress (psi)
)

# Analyze measured thickness
results = pipe.analyze(
    measured_thickness=0.060,  # Measured thickness (inches)
    year_inspected=2023        # Optional: inspection year
)

print(f"Flag: {results['flag']}")
print(f"Status: {results['status']}")
print(f"Governing thickness: {results['governing_thickness']:.4f} inches")
```

## Docker Usage

Run TMIN in a container:

```bash
# Build and run
./docker.sh build
./docker.sh run

# Or test functionality
./docker.sh test
```

## License

MIT License