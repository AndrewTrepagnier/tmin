# TMIN - Pipe Thickness Analysis Tool

<p align="left">
  <img src="https://github.com/user-attachments/assets/52007543-8109-44ff-845e-c6a809a89a38" alt="TMIN Logo" width="700" />
</p>

[![Downloads](https://pepy.tech/badge/tmin)](https://pepy.tech/project/tmin)


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

pipe = PIPE(
    nps=2.0, schedule=40, pressure_class=300, pressure=1000,
    design_temp=900, pipe_config="straight", metallurgy="Intermediate/Low CS",
    yield_stress=35000, API_table="2025",
)
pipe_data = {"pressure": pipe.pressure, "nps": pipe.nps, "schedule": pipe.schedule,
             "pressure_class": pipe.pressure_class, "metallurgy": pipe.metallurgy,
             "API_table": pipe.API_table, "pipe_config": pipe.pipe_config}
pipe_data.update(pipe.get_table_info())

results = pipe.minimum_thickness_calculator(pipe_data, current_thickness=0.112)

print(f"Flag: {results['flag']}")
print(f"Pressure minimum: {results['tmin_pressure']:.4f} in")
print(f"Structural minimum: {results['tmin_structural']:.4f} in")
```

## License

MIT License
