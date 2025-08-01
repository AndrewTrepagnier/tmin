# TMIN CLI Tutorial

## Quick Start

TMIN provides a command-line interface for quick pipe analysis. Here's how to use it:

## Basic Usage

### 1. Install TMIN
```bash
pip install tmin
```

### 2. Basic Analysis
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060
```

**What this does:**
- `-s 40` = Schedule 40 pipe
- `-n "2"` = 2" nominal pipe size
- `-p 50` = 50 psi design pressure
- `-c 150` = Pressure class 150
- `-m "Intermediate/Low CS"` = Carbon steel metallurgy
- `-a 23333` = Allowable stress (psi)
- `-t 0.060` = Measured thickness (inches)

### 3. Analysis with Corrosion Rate
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060 -r 10 -y 2023
```

**Additional options:**
- `-r 10` = 10 MPY corrosion rate
- `-y 2023` = Inspection year 2023

### 4. Custom Output Directory
```bash
tmin -s 40 -n "2" -p 50 -c 150 -m "Intermediate/Low CS" -a 23333 -t 0.060 -o ./my_reports
```

## Using Configuration Files

### 1. Create a TOML Configuration File
Create `pipe_config.toml`:
```toml
# Pipe configuration
schedule = "40"
nps = "2"
pressure = 50.0
pressure_class = 150
metallurgy = "Intermediate/Low CS"
allowable_stress = 23333.0
corrosion_rate = 10.0
year_inspected = 2023
```

### 2. Run with Configuration File
```bash
tmin -f pipe_config.toml -t 0.060
```

## Command Options

### Required Arguments
- `-s, --schedule` - Pipe schedule (10, 40, 80, 120, 160)
- `-n, --nps` - Nominal pipe size (e.g., "2", "3/4", "1-1/2")
- `-p, --pressure` - Design pressure (psi)
- `-c, --pressure-class` - Pressure class (150, 300, 600, 900, 1500, 2500)
- `-m, --metallurgy` - Metallurgy type
- `-a, --allowable-stress` - Allowable stress (psi)
- `-t, --measured-thickness` - Measured thickness (inches)

### Optional Arguments
- `-d, --design-temp` - Design temperature (default: 900)
- `--pipe-config` - Pipe configuration (default: straight)
- `-r, --corrosion-rate` - Corrosion rate (MPY)
- `--default-retirement-limit` - Default retirement limit (inches)
- `--api-table` - API table version (default: 2025)
- `-y, --year-inspected` - Year when thickness was measured
- `-o, --output` - Output directory (default: Reports)
- `-f, --file` - Load configuration from TOML file
- `--no-disclaimer` - Skip disclaimer message

## Examples

### Example 1: Simple Analysis
```bash
tmin -s 40 -n "3" -p 100 -c 300 -m "Intermediate/Low CS" -a 23333 -t 0.080
```

### Example 2: High-Pressure Steam Line
```bash
tmin -s 80 -n "1.5" -p 150 -c 600 -m "Intermediate/Low CS" -a 23333 -t 0.095 -r 5 -y 2022
```

### Example 3: Stainless Steel Pipe
```bash
tmin -s 40 -n "4" -p 75 -c 300 -m "SS 316/316L" -a 20000 -t 0.120 -r 2 -y 2023
```

### Example 4: Using TOML File
```bash
# Create config.toml
echo 'schedule = "40"
nps = "2"
pressure = 50.0
pressure_class = 150
metallurgy = "Intermediate/Low CS"
allowable_stress = 23333.0
corrosion_rate = 10.0
year_inspected = 2023' > config.toml

# Run analysis
tmin -f config.toml -t 0.060
```

## Output

TMIN generates several files in the output directory:
- **Full Report** - Detailed analysis report
- **Summary Report** - Brief overview
- **Number Line Plot** - Cross-sectional visualization
- **Comparison Chart** - Bar chart comparison

## Get Help

```bash
tmin --help
```

This shows all available options and examples.

## Tips

1. **Use TOML files** for repeated analyses with the same pipe
2. **Check the Reports folder** for generated files
3. **Use short options** for quick commands
4. **Use long options** for clarity in scripts
5. **Always verify** your input parameters

## Common Values

### Allowable Stress (psi)
- A106 GR B: 23333 (35000 × 2/3)
- A312 316: 20000 (30000 × 2/3)
- A312 304: 20000 (30000 × 2/3)

### Corrosion Rates (MPY)
- Low: 1-5 MPY
- Medium: 5-15 MPY
- High: 15+ MPY

### Metallurgy Options
- "Intermediate/Low CS" - Carbon Steel
- "SS 316/316L" - Stainless Steel 316
- "SS 304/304L" - Stainless Steel 304
- "Inconel 625" - Nickel Alloy
- "Other" - Other materials 