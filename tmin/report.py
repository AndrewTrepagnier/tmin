"""
Engineering memorandum report generation.

Fills a text template (with [placeholder] blocks) from a JSON file and optionally
appends or writes pressure tmin calculations (inputs and outputs) to the memo or
a separate file.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Default template in project templates/ folder
_DEFAULT_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_DEFAULT_TEMPLATE_PATH = _DEFAULT_TEMPLATE_DIR / "engineering_memorandum.txt"


def get_default_template_path() -> Path:
    """Return the path to the built-in engineering memorandum template."""
    return _DEFAULT_TEMPLATE_PATH


def load_template(path: Optional[Path] = None) -> str:
    """Load memorandum template text from path, or use default template."""
    p = Path(path) if path is not None else get_default_template_path()
    return p.read_text(encoding="utf-8")


def extract_placeholders(template_text: str) -> list[str]:
    """Return all unique [placeholder] tokens in the template, in order of first appearance."""
    seen: set[str] = set()
    order: list[str] = []
    for m in re.finditer(r"\[([^\]]+)\]", template_text):
        placeholder = m.group(0)  # "[...]"
        if placeholder not in seen:
            seen.add(placeholder)
            order.append(placeholder)
    return order


def _normalize_key(key: str) -> str:
    """Normalize a key for lookup: strip brackets and leading/trailing space."""
    k = key.strip()
    if k.startswith("[") and k.endswith("]"):
        k = k[1:-1].strip()
    return k


def fill_template(template_text: str, values: Dict[str, Any]) -> str:
    """
    Replace each [placeholder] in template_text with values from `values`.

    Keys in `values` can be with or without brackets, e.g. "Site Name" or "[Site Name]".
    Placeholders not present in `values` are left as-is (unchanged).
    """
    # Build map: "[Placeholder]" -> str value (coerce to str for substitution)
    by_bracket: Dict[str, str] = {}
    for k, v in values.items():
        norm = _normalize_key(k)
        bracket_key = f"[{norm}]"
        by_bracket[bracket_key] = "" if v is None else str(v).strip()

    def repl(m: re.Match) -> str:
        full = m.group(0)
        return by_bracket.get(full, full)

    return re.sub(r"\[[^\]]+\]", repl, template_text)


def _strip_json_comments(text: str) -> str:
    """Remove // comment lines so JSON-with-comments parses as valid JSON."""
    lines = text.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        out.append(line)
    return "\n".join(out)


# Keys used to build PIPE from JSON; all others are memo placeholders only.
_PIPE_REQUIRED_KEYS = {"pressure", "nps", "schedule", "pressure_class", "metallurgy", "yield_stress"}
_PIPE_OPTIONAL_KEYS = {
    "design_temp", "pipe_config", "corrosion_rate", "default_retirement_limit",
    "API_table", "joint_type",
}
_CURRENT_THICKNESS_KEY = "current_thickness"


def _pipe_from_values(values: Dict[str, Any]) -> Tuple[Any, float]:
    """Build a PIPE instance and current_thickness from a values dict. Returns (pipe, current_thickness)."""
    from .core_exp import PIPE  # Lazy to avoid circular import

    missing = _PIPE_REQUIRED_KEYS - set(values.keys())
    if missing:
        raise ValueError(f"JSON pipe section missing required keys: {missing}")
    if _CURRENT_THICKNESS_KEY not in values:
        raise ValueError("JSON must include 'current_thickness' (inches) to run tmin from JSON.")

    current_thickness = float(values[_CURRENT_THICKNESS_KEY])
    kwargs = {
        "pressure": float(values["pressure"]),
        "nps": float(values["nps"]),
        "schedule": int(values["schedule"]),
        "pressure_class": int(values["pressure_class"]),
        "metallurgy": str(values["metallurgy"]),
        "yield_stress": float(values["yield_stress"]),
    }
    for key in _PIPE_OPTIONAL_KEYS:
        if key in values and values[key] is not None:
            kwargs[key] = values[key]
    pipe = PIPE(**kwargs)
    return pipe, current_thickness


def _can_build_pipe_from_values(values: Dict[str, Any]) -> bool:
    """True if values contains all keys needed to build PIPE and run tmin."""
    if not _PIPE_REQUIRED_KEYS.issubset(values.keys()):
        return False
    if _CURRENT_THICKNESS_KEY not in values or values[_CURRENT_THICKNESS_KEY] is None:
        return False
    return True


def load_memorandum_values(json_path: Path) -> Dict[str, Any]:
    """Load a JSON file into a flat dict for template filling. Strips // comment lines."""
    path = Path(json_path)
    text = path.read_text(encoding="utf-8")
    text = _strip_json_comments(text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Memorandum JSON must be a JSON object (key-value map).")
    # Omit keys that are only for section headers (e.g. _section_*)
    return {k: v for k, v in data.items() if not (isinstance(k, str) and k.startswith("_"))}


def format_tmin_section(pipe_data: Dict[str, Any], result: Dict[str, Any]) -> str:
    """Format the pressure tmin inputs and outputs as a text block for the memo or separate file."""
    P = pipe_data["pressure"]
    D = pipe_data["outer_diameter"]
    S = pipe_data["allowable_stress"]
    joint_info = pipe_data.get("joint_type", {"joint_efficiency": 1.0, "weld_strength_reduction": 1.0})
    E = joint_info["joint_efficiency"]
    W = joint_info["weld_strength_reduction"]
    Y = pipe_data["y_coefficient"]
    tmin_p = result["tmin_pressure"]
    current = result["current_thickness"]
    lines = [
        "",
        "Pressure tmin calculations (tmin package)",
        "=" * 50,
        "",
        "Inputs:",
        f"  P (design pressure) = {P} psi",
        f"  D (outer diameter) = {D} in",
        f"  S (allowable stress) = {S:.0f} psi",
        f"  E (joint efficiency) = {E}   W (weld strength reduction) = {W}   Y = {Y}",
        "",
        "ASME B31.1 Eq. 3a:  tmin = (P*D) / (2*(S*E*W + P*Y))",
        f"  tmin = ({P}*{D}) / (2*({S*E*W:.0f} + {P*Y:.0f})) = {tmin_p:.6f} in",
        "",
        "Outputs:",
        f"  tmin_pressure (required) = {tmin_p:.6f} in",
        f"  tmin_structural          = {result['tmin_structural']:.6f} in",
        f"  governing thickness      = {result['governing_thickness']:.6f} in ({result['governing_type']})",
        f"  current thickness        = {current:.6f} in",
        f"  status                   = {result.get('status', '')}",
    ]
    if "corrosion_allowance" in result:
        lines.append(f"  corrosion_allowance       = {result['corrosion_allowance']:.6f} in")
    if "pressure_deficit" in result:
        lines.append(f"  pressure_deficit          = {result['pressure_deficit']:.6f} in")
    if "deficit_to_governing" in result:
        lines.append(f"  deficit_to_governing      = {result['deficit_to_governing']:.6f} in")
    lines.append("")
    return "\n".join(lines)


def generate_memorandum(
    output_path: Path,
    *,
    json_path: Optional[Path] = None,
    values: Optional[Dict[str, Any]] = None,
    template_path: Optional[Path] = None,
    append_tmin: bool = False,
    tmin_output_path: Optional[Path] = None,
    pipe: Optional[Any] = None,
    current_thickness: Optional[float] = None,
    pipe_data_override: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate the engineering memorandum and optional tmin run.

    Provide either json_path (load from file) or values (in-memory dict), not both.
    - output_path: Where to write the filled memorandum text file.
    - json_path: Path to JSON file (optional if values is provided).
    - values: In-memory dict of placeholder keys and pipe section (optional if json_path is provided).
    - template_path: Optional path to template; if None, uses package default.
    - append_tmin, tmin_output_path, pipe, current_thickness, pipe_data_override: as before.

    Returns dict with keys: "memorandum_path", "tmin_result" (if tmin was run), "tmin_section_path" (if written to file).
    """
    if values is not None and json_path is not None:
        raise ValueError("Provide either json_path or values, not both.")
    if values is None and json_path is None:
        raise ValueError("Provide either json_path or values.")

    template_text = load_template(template_path)
    if values is not None:
        values = dict(values)
    else:
        values = load_memorandum_values(Path(json_path))

    # Always set Date of generation to current date (DD-MMM-YYYY)
    values["Date of generation"] = datetime.now().strftime("%d-%b-%Y")

    tmin_result: Optional[Dict[str, Any]] = None
    tmin_section: Optional[str] = None
    pipe_built_from_json = False

    # If no pipe passed but JSON has pipe section, build PIPE and run tmin from JSON
    if pipe is None and _can_build_pipe_from_values(values):
        pipe, current_thickness = _pipe_from_values(values)
        pipe_built_from_json = True

    run_tmin = (pipe is not None and current_thickness is not None) or (
        pipe_data_override is not None and current_thickness is not None
    )
    if run_tmin:
        if pipe is None:
            raise ValueError("pipe is required when running tmin or when providing pipe_data_override.")
        if pipe_data_override is not None:
            pipe_data = pipe_data_override
        else:
            pipe_data = dict(pipe.get_table_info())
            pipe_data["pressure"] = pipe.pressure
            pipe_data["nps"] = pipe.nps
            pipe_data["schedule"] = pipe.schedule
            pipe_data["pressure_class"] = pipe.pressure_class
            pipe_data["metallurgy"] = pipe.metallurgy
            pipe_data["API_table"] = getattr(pipe, "API_table", "2025")
            pipe_data["pipe_config"] = getattr(pipe, "pipe_config", "straight")

        tmin_result = pipe.minimum_thickness_calculator(
            pipe_data,
            current_thickness=current_thickness,
            default_retirement_limit=pipe.default_retirement_limit,
            output_txt_path=None,
        )
        tmin_section = format_tmin_section(pipe_data, tmin_result)

        # Override memo placeholders that tmin can supply
        values["Design Pressure"] = pipe_data["pressure"]
        values["Design Temperature"] = getattr(pipe, "design_temp", "")
        values["Nominal Thickness"] = get_nominal_thickness_for_display(pipe)
        values["current thickness"] = current_thickness
        values["Current tmin"] = tmin_result["tmin_pressure"]

    body = fill_template(template_text, values)

    # When pipe was built from JSON, append tmin by default so one JSON file is enough
    do_append_tmin = True if pipe_built_from_json else append_tmin
    if do_append_tmin and tmin_section:
        body = body.rstrip() + "\n" + tmin_section

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(body, encoding="utf-8")

    out: Dict[str, Any] = {"memorandum_path": str(output_path), "tmin_result": tmin_result}

    if tmin_output_path and tmin_section:
        tmin_output_path = Path(tmin_output_path)
        tmin_output_path.parent.mkdir(parents=True, exist_ok=True)
        tmin_output_path.write_text("Pressure tmin report\n" + "=" * 50 + "\n" + tmin_section.strip(), encoding="utf-8")
        out["tmin_section_path"] = str(tmin_output_path)

    return out


def get_nominal_thickness_for_display(pipe: Any) -> str:
    """Nominal wall thickness for display (e.g. from schedule tables if available)."""
    try:
        od = pipe.get_outer_diameter()
        id_ = pipe.get_inner_diameter()
        if od is not None and id_ is not None:
            return f"{(od - id_) / 2:.4f}"
    except Exception:
        pass
    return ""


def _find_project_root(input_dirname: str = "Input", start: Optional[Path] = None) -> Path:
    """Walk up from start (default cwd) until we find a directory containing input_dirname."""
    current = Path(start) if start is not None else Path.cwd()
    for _ in range(10):
        if (current / input_dirname).exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return Path.cwd()


def _get_input_json_path(root: Path, input_dirname: str = "examples") -> Path:
    """Return path to first .json in the input directory. Raises FileNotFoundError if none."""
    input_dir = root / input_dirname
    input_dir.mkdir(parents=True, exist_ok=True)
    jsons = sorted(input_dir.glob("*.json"))
    if not jsons:
        raise FileNotFoundError(
            f"No .json files in {input_dir}. Put memorandum_values_example.json there and run again."
        )
    return jsons[0]


def analyze(
    root: Optional[Path] = None,
    *,
    data: Optional[Dict[str, Any]] = None,
    values: Optional[Dict[str, Any]] = None,
    input_dirname: str = "examples",
) -> Dict[str, Any]:
    """
    Run tmin and print a terminal report of pressure and structural thicknesses.

    Use data= or values= to pass an in-memory dict (e.g. from a notebook). Otherwise
    reads the first JSON in the examples/ directory (or input_dirname).

    Does not write any files. Use tmin.report() to generate the memorandum.

    Returns the tmin result dict (current_thickness, tmin_pressure, tmin_structural,
    governing_thickness, governing_type, status, etc.).
    """
    in_memory = data if data is not None else values
    if in_memory is not None:
        values = dict(in_memory)
        source_name = "inline values"
    else:
        root = Path(root) if root is not None else _find_project_root(input_dirname)
        json_path = _get_input_json_path(root, input_dirname)
        values = load_memorandum_values(json_path)
        source_name = json_path.name

    if not _can_build_pipe_from_values(values):
        raise ValueError(
            "JSON must include the pipe section (pressure, nps, schedule, pressure_class, "
            "metallurgy, yield_stress, current_thickness) to run analyze()."
        )

    pipe, current_thickness = _pipe_from_values(values)
    pipe_data = dict(pipe.get_table_info())
    pipe_data["pressure"] = pipe.pressure
    pipe_data["nps"] = pipe.nps
    pipe_data["schedule"] = pipe.schedule
    pipe_data["pressure_class"] = pipe.pressure_class
    pipe_data["metallurgy"] = pipe.metallurgy
    pipe_data["API_table"] = getattr(pipe, "API_table", "2025")
    pipe_data["pipe_config"] = getattr(pipe, "pipe_config", "straight")

    result = pipe.minimum_thickness_calculator(
        pipe_data,
        current_thickness=current_thickness,
        default_retirement_limit=pipe.default_retirement_limit,
        output_txt_path=None,
    )

    # Terminal report
    print(f"\ntmin analysis  ({source_name})")
    print("-" * 50)
    print(f"  Pressure tmin:     {result['tmin_pressure']:.6f} in")
    print(f"  Structural tmin:  {result['tmin_structural']:.6f} in")
    print(f"  Governing:         {result['governing_thickness']:.6f} in ({result['governing_type']})")
    print(f"  Current thickness: {result['current_thickness']:.6f} in")
    print(f"  Status:            {result.get('flag', '')} – {result.get('message', '')}")
    if "corrosion_allowance" in result:
        print(f"  Corrosion allowance: {result['corrosion_allowance']:.6f} in")
    if "pressure_deficit" in result:
        print(f"  Pressure deficit:    {result['pressure_deficit']:.6f} in")
    if "deficit_to_governing" in result:
        print(f"  Deficit to governing: {result['deficit_to_governing']:.6f} in")
    print()

    return result


def run_report_from_input(
    root: Optional[Path] = None,
    *,
    values: Optional[Dict[str, Any]] = None,
    input_dirname: str = "examples",
    output_dirname: str = "output",
    memo_filename: str = "engineering_memorandum.txt",
    tmin_filename: str = "tmin_calcs.txt",
) -> Dict[str, Any]:
    """
    Run tmin and write memorandum and tmin report to the output directory.

    Use values= to pass an in-memory dict. Otherwise reads the first .json from examples/.
    If root is None, searches upward from cwd for a directory containing the input dir.

    Returns the same dict as generate_memorandum (memorandum_path, tmin_result, etc.).
    Raises FileNotFoundError if no values and no .json files in the input directory.
    """
    root = Path(root) if root is not None else _find_project_root(input_dirname)
    output_dir = root / output_dirname
    output_dir.mkdir(parents=True, exist_ok=True)

    if values is not None:
        result = generate_memorandum(
            output_dir / memo_filename,
            values=values,
            template_path=get_default_template_path(),
            tmin_output_path=output_dir / tmin_filename,
        )
    else:
        json_path = _get_input_json_path(root, input_dirname)
        result = generate_memorandum(
            output_dir / memo_filename,
            json_path=json_path,
            template_path=get_default_template_path(),
            tmin_output_path=output_dir / tmin_filename,
        )

    return result


def report(
    root: Optional[Path] = None,
    *,
    data: Optional[Dict[str, Any]] = None,
    values: Optional[Dict[str, Any]] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Generate the engineering memorandum and write it to the output directory.

    Use data= or values= to pass an in-memory dict (e.g. from a notebook). Otherwise
    reads the first JSON from the examples/ directory.

    If root is None, the project root is found by searching upward from the
    current directory for a folder named examples/ (or the configured input dir).

    Returns the result dict (memorandum_path, tmin_result, tmin_section_path).
    If verbose is True, prints where the report was written.
    """
    in_memory = data if data is not None else values
    result = run_report_from_input(root=root, values=in_memory)
    if verbose:
        print("Report written to output/")
        print(" ", result["memorandum_path"])
        if result.get("tmin_section_path"):
            print(" ", result["tmin_section_path"])
        if result.get("tmin_result"):
            print("Tmin:", result["tmin_result"].get("status", ""))
    return result


def run(root: Optional[Path] = None, verbose: bool = True) -> Dict[str, Any]:
    """Alias for tmin.report(). Writes the memorandum to the output directory."""
    return report(root=root, verbose=verbose)
