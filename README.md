# TMIN - Pipe Thickness Analysis Tool

<p align="left">
<img width="800" height="600" alt="newtmin" src="https://github.com/user-attachments/assets/fb260356-a59e-4608-b242-954d71847430" />
</p>

[![Downloads](https://pepy.tech/badge/tmin)](https://pepy.tech/project/tmin)


TMIN (an abbreviation for "minimum thickness") is an open source python package designed to help engineers determine if corroded process piping in refineries and pertrochemical plants are **safe** and **API-compliant** in seconds.

Many oil and gas companies are faced with maintaining thousands of miles of 100+ year old piping networks supporting multi-million dollar/year processing operations. There is rarely a simple solution to immediately shutdown a process pipe - as these shutdowns more often than not impact other units and cost companies millions in time and resources.

TMIN can be used as a conservative and rapid engineering support tool for assessing piping inspection data and determine how close the pipe is to its end of service life.

### First Time Users

First time users should use the ```tmin_workflow.ipynb``` example in tutorials.

### Repository layout

```
tmin/
├── tmin/              # Package (PIPE, analyze, report)
├── examples/          # Example JSON input for memorandum workflow
├── templates/         # Engineering memorandum template
├── tutorials/         # Notebooks and scripts
├── references/        # API 574 reference PDFs
├── pyproject.toml
├── README.md
└── LICENSE
```

### Memorandum workflow

From the repo root (with example data in `examples/`):

```python
import tmin
tmin.analyze()   # Terminal report
tmin.report()    # Writes to output/
```



## License

MIT License
