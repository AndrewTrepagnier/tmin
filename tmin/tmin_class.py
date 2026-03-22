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
from .tables.pmg_table import pmg_from_nps


def _parse_art_equals_1_date(value: str) -> Optional[date]:
    """Parse ``Date AR/T = 1`` values, e.g. ``01-Mar-2029``."""
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%d-%b-%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _format_ut_date_display(value: Any) -> str:
    """Pretty-print ``UT_date`` (MM-YYYY etc.) for memorandum text."""
    if value is None or value == "":
        return ""
    s = str(value).strip()
    for fmt in ("%m-%Y", "%m/%Y", "%Y-%m", "%B %Y", "%b %Y"):
        try:
            d = datetime.strptime(s, fmt)
            return d.strftime("%b %Y")
        except ValueError:
            continue
    return s


def _esl_present_art_and_threshold(art1_str: str) -> tuple[str, str]:
    """Return (``years until AR/T=1`` display, ``<`` or ``>`` vs 2-year ESL horizon)."""
    art1 = _parse_art_equals_1_date(art1_str)
    if art1 is None:
        return "", ""
    today = date.today()
    years = (art1 - today).days / 365.25
    if years >= 0:
        present = f"{years:.1f} years"
        thr = "<" if years <= 2.0 else ">"
    else:
        present = "past due"
        thr = "<"
    return present, thr


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
        ``current_thickness``, ``corrosion_allowance``, ``ca_to_ptmin``
        (current − pressure tmin), ``nominal_wall``, ``pmg`` (PMG from NPS table),
        and ``percent_cac_pmg`` (%CAC vs PMG).
        All thickness values are rounded up to the thousandths place.
        """
        pipe = self._pipe
        pipe_data = dict(pipe.get_table_info())
        pipe_data["pressure"] = pipe.pressure
        pipe_data["nps"] = pipe.nps
        pipe_data["schedule"] = pipe.schedule
        pipe_data["pressure_class"] = pipe.pressure_class
        pipe_data["metallurgy"] = pipe.metallurgy
        pipe_data["API_table"] = getattr(pipe, "API_table", "2024")
        pipe_data["pipe_config"] = getattr(pipe, "pipe_config", "straight")
        self._pipe_data = pipe_data

        current_thickness = float(self.inputs["current_thickness"])

        result = pipe.minimum_thickness_calculator(
            pipe_data,
            current_thickness=current_thickness,
            default_retirement_limit=pipe.default_retirement_limit,
        )
        # Wall in excess of B31.3 pressure tmin: current measured − Ptmin
        result["ca_to_ptmin"] = round(
            result["current_thickness"] - result["tmin_pressure"], 3
        )

        # % Corrosion Allowance Consumed (%CAC of PMG)
        # PMG = pipe minimum gauge from fixed NPS table (see tables/pmg_table.py).
        # CA (total) = Nominal wall − PMG.  Consumed = Nominal − Current TML.
        # %CAC = (Nominal − Current) / (Nominal − PMG) × 100  (>100% when Current < PMG).
        od = pipe_data["outer_diameter"]
        id_ = pipe_data["inner_diameter"]
        nominal_wall = (od - id_) / 2
        pmg = pmg_from_nps(pipe.nps)
        result["nominal_wall"] = round(nominal_wall, 3)
        result["pmg"] = pmg
        if pmg is None:
            result["percent_cac_pmg"] = None
        else:
            denom = nominal_wall - pmg
            if denom > 1e-9:
                pct_cac = (nominal_wall - current_thickness) / denom * 100.0
                result["percent_cac_pmg"] = round(pct_cac, 1)
            else:
                result["percent_cac_pmg"] = None

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

        # NPS display: always show as e.g. "8in" (strip any prior inch suffix first)
        if "Size" in values and values["Size"] is not None:
            s = str(values["Size"]).strip()
            if s.lower().endswith(" in"):
                s = s[:-3].strip()
            elif len(s) > 2 and s.lower().endswith("in"):
                s = s[:-2].strip()
            values["Size"] = f"{s}in"

        # Computed overrides for the component section
        od = pipe.get_outer_diameter()
        id_ = pipe.get_inner_diameter()
        if od and id_:
            values["Nominal Thickness"] = f"{(od - id_) / 2:.3f}"

        values["Design Pressure"] = int(pipe.pressure)
        values["Design Temperature"] = self.inputs.get("design_temp", "")
        values["Operating Pressure"] = self.inputs.get("operating_pressure", "")
        values["Operating Temperature"] = self.inputs.get("operating_temperature", "")
        values["current thickness"] = f"{res['current_thickness']:.3f}"

        # Tmin calculation display values
        joint_info = pipe_data.get(
            "joint_type",
            {"joint_efficiency": 1.0, "weld_strength_reduction": 1.0},
        )
        def _num(v):
            return int(v) if v == int(v) else v

        # Allowable stress citation for B31.3 block (single line and/or year + code source)
        basis = self.inputs.get("allowable_stress_basis")
        if isinstance(basis, str):
            basis = basis.strip()
        elif basis is not None:
            basis = str(basis).strip()
        else:
            basis = ""
        if not basis:
            y = str(self.inputs.get("allowable_stress_code_year", "")).strip()
            s = str(self.inputs.get("allowable_stress_code_source", "")).strip()
            basis = " ".join(x for x in (y, s) if x)
        if not basis:
            legacy = self.inputs.get("Allowable Stress Basis", "")
            basis = str(legacy).strip() if legacy else ""
        values["allowable stress basis"] = basis

        values["calc_P"] = _num(pipe_data["pressure"])
        values["calc_D"] = _num(pipe_data["outer_diameter"])
        s_psi = f"{pipe_data['allowable_stress']:.0f} psi"
        values["calc_S"] = f"{s_psi} ({basis})" if basis else s_psi
        values["calc_E"] = _num(joint_info["joint_efficiency"])
        values["calc_W"] = _num(joint_info["weld_strength_reduction"])
        values["calc_Y"] = _num(pipe_data["y_coefficient"])

        values["tmin_pressure"] = f"{res['tmin_pressure']:.3f}"

        values["struct_label"] = "based on API 574-2024"

        if res["tmin_structural"] is not None:
            values["tmin_structural"] = f"{res['tmin_structural']:.3f}"
        else:
            values["tmin_structural"] = "N/A"

        values["governing_thickness"] = f"{res['governing_thickness']:.3f}"
        values["governing_type"] = res["governing_type"]
        values["corrosion_allowance"] = f"{res['corrosion_allowance']:.3f}"
        values["CA to PTmin"] = f"{res['ca_to_ptmin']:.3f}"

        # Modelled LTCR from install_date → UT_date: keep user "CR description" and
        # append the automated Modelled LTCR (ESL Evaluation + ESL Summary lines).
        user_cr_description = str(self.inputs.get("CR description", "")).strip()
        if "corrosion_rate_mpy" in res:
            mpy = res["corrosion_rate_mpy"]
            values["CR"] = mpy
            detail_inner = (
                f"({res['nominal_wall']:.3f}\" nom - "
                f"{res['current_thickness']:.3f}\" current) / "
                f"{res['years_in_service']:.1f} yrs"
            )
            modelled = f"Modelled LTCR: {detail_inner}"
            if user_cr_description:
                # User text + automated LTCR (parentheses line in ESL Evaluation)
                values["CR description"] = f"{user_cr_description} {modelled}"
                values["CR description short"] = (
                    f"{user_cr_description} — {detail_inner}"
                )
            else:
                values["CR description"] = modelled
                values["CR description short"] = detail_inner
        else:
            values["CR description short"] = user_cr_description

        # ESL Summary (automated + user fields)
        values["EDD"] = str(self.inputs.get("Degradation Mechanism", "")).strip()
        art1_raw = self.inputs.get("Date AR/T = 1", "")
        present_art, esl_thr = _esl_present_art_and_threshold(str(art1_raw))
        values["Present - AR/T"] = present_art
        values["ESL threshold compare"] = esl_thr
        values["UT_date display"] = _format_ut_date_display(self.inputs.get("UT_date"))

        def _esl_input(*keys: str) -> str:
            for k in keys:
                if k in self.inputs and self.inputs[k] not in (None, ""):
                    return str(self.inputs[k]).strip()
            return ""

        values["EDD Number"] = _esl_input("EDD Number", "edd_number")
        values["percent undamaged"] = _esl_input(
            "percent undamaged", "percent_undamaged"
        )
        values["percent damaged"] = _esl_input("percent damaged", "percent_damaged")
        values["Inspection Effectiveness"] = _esl_input(
            "Inspection Effectiveness", "inspection_effectiveness"
        )
        values["Number of RT per TML"] = _esl_input(
            "Number of RT per TML", "number_of_rt_per_tml"
        )
        # %CAC of PMG (auto) unless user overrides with percent_ca_consumed
        pc_manual = _esl_input("percent CA consumed", "percent_ca_consumed")
        if pc_manual:
            values["percent CA consumed"] = pc_manual
        elif res.get("percent_cac_pmg") is not None:
            values["percent CA consumed"] = f"{res['percent_cac_pmg']:.1f}%"
        else:
            values["percent CA consumed"] = ""
        values["coating status"] = _esl_input("coating status", "coating_status")
        values["mitigation"] = _esl_input("mitigation")

        # RBMP Notes (memorandum section)
        values["design_pressure"] = int(pipe.pressure) if pipe.pressure == int(pipe.pressure) else pipe.pressure
        values["design_temp"] = self.inputs.get("design_temp", "")
        values["operating pressure"] = self.inputs.get("operating_pressure", "")
        values["operating_temp"] = self.inputs.get("operating_temperature", "")
        nps_v = float(pipe.nps)
        values["nps"] = int(nps_v) if nps_v == int(nps_v) else nps_v
        values["nominal wall thickness piping"] = f"{res['nominal_wall']:.3f}"
        pmg_rb = res.get("pmg")
        values["PMG retirement thickness"] = (
            f"{pmg_rb:.3f}" if pmg_rb is not None else "N/A"
        )
        if res["tmin_structural"] is not None:
            values["API 574 structural tmin"] = f"{res['tmin_structural']:.3f}"
        else:
            values["API 574 structural tmin"] = "N/A"
        values["B31.3 required thickness"] = f"{res['tmin_pressure']:.3f}"
        values["minimum measured thickness"] = f"{res['current_thickness']:.3f}"
        values["Mitigations"] = _esl_input("Mitigations", "mitigation")
        values["SHE Consequence Level"] = str(
            self.inputs.get("SHE consequence level", "")
        ).strip()

        # ESL Summary: conservative (manual) CR vs modelled LTCR narrative
        cr_assigned = str(self.inputs.get("CR", "")).strip()
        if not cr_assigned:
            cr_assigned = "—"
        if "corrosion_rate_mpy" in res:
            mpy = res["corrosion_rate_mpy"]
            detail_inner = (
                f"({res['nominal_wall']:.3f}\" nom - "
                f"{res['current_thickness']:.3f}\" current) / "
                f"{res['years_in_service']:.1f} yrs"
            )
            values["ESL conservative vs LTCR paragraph"] = (
                f"A conservative corrosion rate of {cr_assigned} mpy was assigned based on "
                "EDD guidance and inspection confidence/effectiveness; however, the modelled "
                f"LTCR is {mpy} mpy {detail_inner}."
            )
        else:
            values["ESL conservative vs LTCR paragraph"] = (
                f"A conservative corrosion rate of {cr_assigned} mpy was assigned based on "
                "EDD guidance and inspection confidence/effectiveness."
            )

        return values
