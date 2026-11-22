"""
Module — Literature Validation Comparison
Compares tool output against cited literature/textbook worked examples
(data/validation_cases.csv). Does NOT generate or assume clinical patient data.

All aggregation (mean and max absolute percent error) is performed on unrounded
float percent errors first, and rounded only once at the summary output.
"""
from pk_engine import vancomycin_pk, digoxin_pk, digoxin_maintenance_dose


def numerical_error(calculated: float, reported: float) -> dict:
    """
    Percent error of a calculated PK value against a reported literature value.
    Preserves unrounded `pct_error_raw` for downstream aggregation and provides
    2-decimal and 1-decimal display-rounded fields.
    """
    if reported == 0:
        raise ValueError("reported value cannot be zero (division by zero)")
    pct_error_raw = ((calculated - reported) / reported) * 100.0
    if pct_error_raw > 0:
        direction = "overestimate"
    elif pct_error_raw < 0:
        direction = "underestimate"
    else:
        direction = "exact"
    return {
        "calculated": calculated,
        "reported": reported,
        "pct_error_raw": pct_error_raw,
        "pct_error": round(pct_error_raw, 2),
        "pct_error_1dp": round(pct_error_raw, 1),
        "direction": direction,
    }


def categorical_agreement(calculated_category: str, reported_category: str) -> dict:
    """
    For categorical results (DDI severity, renal category) — simple match/mismatch,
    reported plainly rather than as a percentage given small case counts.
    """
    return {
        "calculated": calculated_category,
        "reported": reported_category,
        "match": calculated_category == reported_category,
    }


def summarize_validation_run(results: list) -> dict:
    """
    Aggregates a list of numerical_error/categorical_agreement results.
    Uses unrounded `pct_error_raw` through aggregation and rounds once at the
    summary level to avoid pre-rounding drift.
    """
    numeric_results = [r for r in results if "pct_error_raw" in r or "pct_error" in r]
    categorical_results = [r for r in results if "match" in r]

    summary = {"total_cases": len(results)}
    if numeric_results:
        errors = [
            abs(r["pct_error_raw"] if "pct_error_raw" in r else r["pct_error"])
            for r in numeric_results
        ]
        mean_raw = sum(errors) / len(errors)
        max_raw = max(errors)
        summary["numeric_cases"] = len(numeric_results)
        summary["mean_abs_pct_error_raw"] = mean_raw
        summary["max_abs_pct_error_raw"] = max_raw
        summary["mean_abs_pct_error_2dp"] = round(mean_raw, 2)
        summary["max_abs_pct_error_2dp"] = round(max_raw, 2)
        summary["mean_abs_pct_error_1dp"] = round(mean_raw, 1)
        summary["max_abs_pct_error_1dp"] = round(max_raw, 1)
        # Keep backward-friendly keys rounded once at 2 decimal places
        summary["mean_abs_pct_error"] = summary["mean_abs_pct_error_2dp"]
        summary["max_abs_pct_error"] = summary["max_abs_pct_error_2dp"]
    if categorical_results:
        matches = sum(1 for r in categorical_results if r["match"])
        summary["categorical_cases"] = len(categorical_results)
        summary["categorical_matches"] = f"{matches} of {len(categorical_results)}"
    return summary


def recalculate_table1_from_source() -> dict:
    """
    Regenerates Table 1 validation metrics directly from live pk_engine calls
    for the four Bauer development/regression cases (V1, V2, D1, D2).
    Returns both:
      - `archived_display`: errors computed from the displayed endpoints
        (7.98/8, 27.11/27, 287.5/288, 86.5/87)
      - `unrounded_live`: errors computed from full-precision unrounded floats
    """
    height_5ft10 = 177.8
    v1 = vancomycin_pk(weight_kg=70, crcl_ml_min=97, height_cm=height_5ft10, sex="male")
    v2 = vancomycin_pk(weight_kg=70, crcl_ml_min=25, height_cm=height_5ft10, sex="male")
    d1_pk = digoxin_pk(weight_kg=70, crcl_ml_min=97, nyha_class="II", height_cm=height_5ft10, sex="male")
    d1_dose = digoxin_maintenance_dose(d1_pk["cl_ml_min_unrounded"], css_target_ng_ml=1.2, bioavailability=1.0)
    d2_pk = digoxin_pk(weight_kg=70, crcl_ml_min=25, nyha_class="IV", height_cm=height_5ft10, sex="male")
    d2_dose = digoxin_maintenance_dose(d2_pk["cl_ml_min_unrounded"], css_target_ng_ml=0.8, bioavailability=0.7)

    raw_cases = [
        ("V1", "Vancomycin", "half_life_hr", 8.0, v1["half_life_hr"], v1["half_life_hr_unrounded"],
         "development/regression", "Bauer Ch.5 Example 1 (pp.218-220)"),
        ("V2", "Vancomycin", "half_life_hr", 27.0, v2["half_life_hr"], v2["half_life_hr_unrounded"],
         "calibration/bug-discovery regression", "Bauer Ch.5 Example 2 (pp.220-221)"),
        ("D1", "Digoxin", "maintenance_dose_ug_day", 288.0, round(d1_dose["dose_ug_per_tau"], 1), d1_dose["dose_ug_per_tau"],
         "development/regression", "Bauer Ch.6 Example 1 (pp.314-315)"),
        ("D2", "Digoxin", "maintenance_dose_ug_day", 87.0, round(d2_dose["dose_ug_per_tau"], 1), d2_dose["dose_ug_per_tau"],
         "development/regression", "Bauer Ch.6 Example 3 (p.316)"),
    ]

    rows = []
    archived_errs = []
    unrounded_errs = []
    for case_id, drug, metric, rep, calc_disp, calc_unr, role, source in raw_cases:
        err_disp = numerical_error(calc_disp, rep)
        err_unr = numerical_error(calc_unr, rep)
        archived_errs.append(err_disp)
        unrounded_errs.append(err_unr)
        rows.append({
            "case_id": case_id,
            "drug": drug,
            "metric": metric,
            "reported": rep,
            "calculated_display": calc_disp,
            "calculated_unrounded": calc_unr,
            "pct_error_display_raw": err_disp["pct_error_raw"],
            "pct_error_display_2dp": err_disp["pct_error"],
            "pct_error_unrounded_raw": err_unr["pct_error_raw"],
            "pct_error_unrounded_2dp": err_unr["pct_error"],
            "case_role": role,
            "source": source,
        })

    return {
        "rows": rows,
        "archived_display": summarize_validation_run(archived_errs),
        "unrounded_live": summarize_validation_run(unrounded_errs),
    }
