# TMIN - Pipe Thickness Analysis Tool

<p align="left">
  <img src="https://github.com/user-attachments/assets/52007543-8109-44ff-845e-c6a809a89a38" alt="TMIN Logo" width="700" />
</p>

[![Downloads](https://pepy.tech/badge/tmin)](https://pepy.tech/project/tmin)


TMIN (an abbreviation for "minimum thickness") is an open source python package designed to help engineers determine if corroded process piping in refineries and pertrochemical plants are **safe** and **API-compliant** — in seconds.

Many oil and gas companies are faced with maintaining thousands of miles of 100+ year old piping networks supporting multi-million dollar/year processing operations. There is rarely a simple solution to immediately shutdown a process pipe - as these shutdowns more often than not impact other units and cost companies millions in time and resources.

***TMIN can be used as a conservative and rapid engineering support tool for assessing piping inspection data and determine how close the pipe is to its end of service life.***

---

### Install & run (Mac or Windows)

**Option A – From GitHub (clone then install)**

```bash
git clone https://github.com/AndrewTrepagnier/tmin.git
cd tmin
pip install .
tmin
```

**Option B – Install directly from GitHub**

```bash
pip install "git+https://github.com/AndrewTrepagnier/tmin.git"
tmin
```

**Option C – From PyPI** (if published)

```bash
pip install tmin
tmin
```

- `tmin` runs the analysis and writes the memorandum to `output/` in the current directory. If there is no `examples/` folder (or no `.json` in it), the bundled example is used so it works out of the box.
- To only print the terminal report: `tmin --analyze-only`
- To only write the report file: `tmin --report-only`
- From Python: `import tmin; tmin.analyze(); tmin.report()`

Requires **Python 3.8+**. For a reliable setup on any machine, use a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
# or:  source .venv/bin/activate   # Mac/Linux
pip install .
tmin
```

If `tmin` is not on your PATH, run: `python -m tmin.report`

---

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
