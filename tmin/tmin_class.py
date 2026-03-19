"""
TMIN — primary user-facing class for pipe minimum thickness analysis.

Usage::

    import tmin

    input_dict = {
        # --- Pipe / tmin calculation inputs ---
        "pressure": 285,
        "nps": 8,
        "schedule": 40,
        "pressure_class": 150,
        "metallurgy": "Intermediate/Low CS",
        "allowable_stress": 23333,
        "current_thickness": 0.112,

        # --- Memorandum fields ---
        "Site Name": "Example Site",
        "Unit": "CRUDE UNIT",
        # ... all other memo fields ...
    }

    instance = tmin.TMIN(input_dict)
    result   = instance.calculate()
    report   = instance.report()
    print(report)
"""

from datetime import datetime, date
from typing import Any, Dict, Optional

from .core_exp import PIPE, _round_up
from .report import fill_template, load_template


def _parse_month_year(value: str) -> date:
    """Parse a month/year string into a date (day=1).

    Accepts ``"MM-YYYY"``, ``"MM/YYYY"``, ``"YYYY-MM"``, or
    ``"Month YYYY"`` (e.g. ``"January 2020"``).
    """
    s = str(value).strip()
    for fmt in ("%m-%Y", "%m/%Y", "%Y-%m", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse date '{value}'. Use MM-YYYY, MM/YYYY, YYYY-MM, "
        f"or 'Month YYYY' (e.g. '01-1985', 'January 1985')."
    )


class TMIN:
    """Pipe minimum thickness analysis and engineering memorandum report.

    Accepts a single dictionary containing both pipe calculation inputs and
    memorandum fields.  Call ``calculate()`` for the numeric tmin results or
    ``report()`` for the full engineering memorandum as a string.
    """

    _REQUIRED_KEYS = {
        "pressure", "nps", "schedule", "pressure_class",
        "metallurgy", "allowable_stress", "current_thickness",
    }

    _OPTIONAL_PIPE_KEYS = {
        "design_temp", "pipe_config", "corrosion_rate",
        "default_retirement_limit", "API_table", "joint_type",
    }

    def __init__(self, input_dict: dict):
        self.inputs: Dict[str, Any] = dict(input_dict)
        self._validate()
        self._pipe: PIPE = self._build_pipe()
        self._result: Optional[Dict[str, Any]] = None
        self._pipe_data: Optional[Dict[str, Any]] = None

    def _validate(self):
        missing = self._REQUIRED_KEYS - set(self.inputs.keys())
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")

    def _build_pipe(self) -> PIPE:
        kwargs: Dict[str, Any] = {
            "pressure": float(self.inputs["pressure"]),
            "nps": float(self.inputs["nps"]),
            "schedule": int(self.inputs["schedule"]),
            "pressure_class": int(self.inputs["pressure_class"]),
            "metallurgy": str(self.inputs["metallurgy"]),
            "allowable_stress": float(self.inputs["allowable_stress"]),
        }
        for key in self._OPTIONAL_PIPE_KEYS:
            if key in self.inputs and self.inputs[key] is not None:
                kwargs[key] = self.inputs[key]
        return PIPE(**kwargs)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def calculate(self) -> Dict[str, Any]:
        """Run the pressure and structural tmin calculations.

        Returns a dict with keys: ``tmin_pressure``, ``tmin_structural``
        (or ``None``), ``governing_thickness``, ``governing_type``,
        ``current_thickness``, and ``corrosion_allowance``.
        All thickness values are rounded up to the thousandths place.
        """
        pipe = self._pipe
        pipe_data = dict(pipe.get_table_info())
        pipe_data["pressure"] = pipe.pressure
        pipe_data["nps"] = pipe.nps
        pipe_data["schedule"] = pipe.schedule
        pipe_data["pressure_class"] = pipe.pressure_class
        pipe_data["metallurgy"] = pipe.metallurgy
        pipe_data["API_table"] = getattr(pipe, "API_table", "2025")
        pipe_data["pipe_config"] = getattr(pipe, "pipe_config", "straight")
        self._pipe_data = pipe_data

        current_thickness = float(self.inputs["current_thickness"])

        result = pipe.minimum_thickness_calculator(
            pipe_data,
            current_thickness=current_thickness,
            default_retirement_limit=pipe.default_retirement_limit,
        )

        # Corrosion rate from install_date → UT_date
        if "install_date" in self.inputs and "UT_date" in self.inputs:
            install = _parse_month_year(self.inputs["install_date"])
            ut = _parse_month_year(self.inputs["UT_date"])
            years_elapsed = (ut - install).days / 365.25
            if years_elapsed <= 0:
                raise ValueError(
                    f"UT_date ({ut}) must be after install_date ({install})."
                )
            od = pipe_data["outer_diameter"]
            id_ = pipe_data["inner_diameter"]
            nominal_wall = (od - id_) / 2
            wall_loss = nominal_wall - current_thickness
            cr_inches_per_year = wall_loss / years_elapsed
            cr_mpy = round(cr_inches_per_year * 1000, 1)
            result["nominal_wall"] = round(nominal_wall, 3)
            result["wall_loss"] = round(wall_loss, 3)
            result["years_in_service"] = round(years_elapsed, 2)
            result["corrosion_rate_mpy"] = cr_mpy

        self._result = result
        return dict(self._result)

    def report(self) -> str:
        """Build the engineering memorandum as a string.

        Fills the memorandum template with user-provided values and
        computed tmin results.  Calls ``calculate()`` automatically
        if it has not been called yet.
        """
        if self._result is None:
            self.calculate()

        template_text = load_template()
        values = self._build_template_values()
        return fill_template(template_text, values)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_template_values(self) -> Dict[str, Any]:
        """Merge user inputs with calculated values for template filling."""
        values: Dict[str, Any] = dict(self.inputs)
        res = self._result
        pipe = self._pipe
        pipe_data = self._pipe_data

        values["Date of generation"] = datetime.now().strftime("%d-%b-%Y")

        # Computed overrides for the component section
        od = pipe.get_outer_diameter()
        id_ = pipe.get_inner_diameter()
        if od and id_:
            values["Nominal Thickness"] = f"{(od - id_) / 2:.3f}"

        values["Design Pressure"] = int(pipe.pressure)
        values["Design Temperature"] = self.inputs.get("design_temp", "")
        values["current thickness"] = f"{res['current_thickness']:.3f}"
        values["Current tmin"] = f"{res['governing_thickness']:.3f}"

        # Tmin calculation display values
        joint_info = pipe_data.get(
            "joint_type",
            {"joint_efficiency": 1.0, "weld_strength_reduction": 1.0},
        )
        def _num(v):
            return int(v) if v == int(v) else v

        values["calc_P"] = _num(pipe_data["pressure"])
        values["calc_D"] = _num(pipe_data["outer_diameter"])
        values["calc_S"] = f"{pipe_data['allowable_stress']:.0f}"
        values["calc_E"] = _num(joint_info["joint_efficiency"])
        values["calc_W"] = _num(joint_info["weld_strength_reduction"])
        values["calc_Y"] = _num(pipe_data["y_coefficient"])

        values["tmin_pressure"] = f"{res['tmin_pressure']:.3f}"

        api_edition = self.inputs.get("API_table", "2025")
        values["struct_label"] = f"API 574-{api_edition}"

        if res["tmin_structural"] is not None:
            values["tmin_structural"] = f"{res['tmin_structural']:.3f}"
        else:
            values["tmin_structural"] = "N/A"

        values["governing_thickness"] = f"{res['governing_thickness']:.3f}"
        values["governing_type"] = res["governing_type"]
        values["corrosion_allowance"] = f"{res['corrosion_allowance']:.3f}"

        # Calculated corrosion rate overrides the manual CR field
        if "corrosion_rate_mpy" in res:
            values["CR"] = res["corrosion_rate_mpy"]
            values["CR description"] = (
                f"Calculated: ({res['nominal_wall']:.3f}\" nom - "
                f"{res['current_thickness']:.3f}\" current) / "
                f"{res['years_in_service']:.1f} yrs"
            )

        return values
