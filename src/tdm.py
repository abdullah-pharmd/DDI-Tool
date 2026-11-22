"""
Module 6 — TDM Interpretation (NOT wired into the UI or batch route in this build)
A single value is interpreted only when its measurement identity, units and
timing are stated explicitly. Missing or non-finite inputs return
"indeterminate" -- never "within range".

Scope notes:
- Vancomycin AUC24 400-600 mg*h/L comes from the 2020 consensus guideline for
  serious MRSA infection (Rybak et al. 2020); it is not a general target.
- Phenytoin: the label highlights unbound (free) concentrations in renal or
  hepatic disease or hypoalbuminaemia; a total level is flagged as limited there.
"""
import math

# measurement key -> (low, high, unit)
THERAPEUTIC_RANGES = {
    "gentamicin": {
        "peak": (5.0, 10.0, "mg/L"),             # conventional dosing peak
        "trough": (None, 2.0, "mg/L"),           # conventional dosing trough
    },
    "vancomycin": {
        "auc24": (400.0, 600.0, "mg*h/L"),       # serious MRSA infection only
    },
    "phenytoin": {
        "total_steady_state": (10.0, 20.0, "mg/L"),
        "free_steady_state": (1.0, 2.0, "mg/L"),
    },
    "digoxin": {
        "post_distribution": (0.5, 1.0, "ng/mL"),  # >=6-8 h after dose
    },
}

INDETERMINATE = "indeterminate"


def interpret_tdm(drug: str, measured_value, measurement_type: str = None,
                  unit: str = None, context: dict = None) -> dict:
    """
    Compares one measured level to a sourced range for an explicitly named
    measurement. Returns a qualitative flag only — it never recalculates a dose.
    context (optional): {"albumin_g_dl": float, "renal_or_hepatic_disease": bool}
    """
    drug_key = (drug or "").strip().lower()
    if drug_key not in THERAPEUTIC_RANGES:
        raise ValueError(f"TDM not defined for '{drug}' in this project's scope")
    context = context or {}
    ranges = THERAPEUTIC_RANGES[drug_key]
    result = {"drug": drug, "measured_value": measured_value,
              "measurement_type": measurement_type, "unit": unit,
              "limitations": [],
              "note": "Qualitative flag only — a clinician determines any dose change."}

    missing = []
    if measurement_type not in ranges:
        missing.append(f"measurement_type must be one of {sorted(ranges)}")
    if not _is_finite_number(measured_value):
        missing.append("measured_value must be a finite number")
    if missing:
        result.update(status=INDETERMINATE, reasons=missing)
        return result

    low, high, expected_unit = ranges[measurement_type]
    if unit != expected_unit:
        result.update(status=INDETERMINATE,
                      reasons=[f"unit must be stated as '{expected_unit}' (got {unit!r})"])
        return result
    value = float(measured_value)
    if value < 0:
        result.update(status=INDETERMINATE, reasons=["measured_value cannot be negative"])
        return result

    if drug_key == "vancomycin":
        result["limitations"].append("AUC24 400-600 target applies to serious MRSA infection")
    if drug_key == "phenytoin" and measurement_type == "total_steady_state":
        alb = context.get("albumin_g_dl")
        if context.get("renal_or_hepatic_disease") or (alb is not None and alb < 3.5):
            result["limitations"].append(
                "total level is unreliable here; measure unbound phenytoin")

    if low is not None and value < low:
        status = "below range"
    elif value > high:
        status = "above range"
    else:
        status = "within range"
    result.update(status=status, range=(low, high, expected_unit), reasons=[])
    return result


def _is_finite_number(x) -> bool:
    if isinstance(x, bool):
        return False
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False
