"""
Batch screening — CSV upload processing.
Format: one row per patient-drug combination, grouped by patient_id.
The batch route computes renal category, drug-pair flags and the review
summary ONLY. It does NOT run the drug-specific PK calculations or TDM;
those are listed under "not assessed" in every output row.
All rows are validated before grouping; any invalid row stops the run and
is reported by row number.
"""
import csv
import io
import math
from collections import defaultdict

REQUIRED_COLUMNS = {"patient_id", "age", "sex", "weight_kg", "height_cm",
                    "scr_mg_dl", "hepatic_impairment", "drug", "nyha_class"}
VALID_DRUGS = {"Gentamicin", "Vancomycin", "Digoxin", "Phenytoin"}
HEPATIC_VALUES = {"yes": True, "no": False, "unknown": None}
MIN_ADULT_AGE = 18          # Cockcroft-Gault and the Bauer adult equations
MAX_AGE = 120
DEMOGRAPHIC_FIELDS = ("age", "sex", "weight_kg", "height_cm", "scr_mg_dl",
                      "hepatic_impairment")
BATCH_NOT_ASSESSED = ["drug-specific PK calculations (single-patient route only)",
                      "therapeutic drug monitoring"]


def _finite(value: str):
    """Parses a finite float or returns None (rejects '', 'nan', 'inf', text)."""
    try:
        x = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def validate_csv_rows(rows: list) -> list:
    """
    Validates every row, then cross-row consistency per patient, before any
    grouping. Returns a list of error strings — empty list means valid.
    """
    errors = []
    if not rows:
        return ["CSV is empty."]

    missing_cols = REQUIRED_COLUMNS - set(rows[0].keys())
    if missing_cols:
        return [f"Missing required column(s): {', '.join(sorted(missing_cols))}"]

    first_seen = {}
    drugs_seen = defaultdict(set)
    for i, row in enumerate(rows, start=2):  # start=2 accounts for header row
        pid = (row.get("patient_id") or "").strip()
        line = f"Row {i} (patient_id={pid or '?'})"
        if not pid:
            errors.append(f"{line}: missing patient_id")

        age = _finite(row.get("age"))
        if age is None or age != int(age):
            errors.append(f"{line}: age must be a whole number")
        elif not (MIN_ADULT_AGE <= age <= MAX_AGE):
            errors.append(f"{line}: age {int(age)} outside supported adult scope "
                          f"({MIN_ADULT_AGE}-{MAX_AGE})")
        for field, label in (("weight_kg", "weight_kg"), ("height_cm", "height_cm"),
                             ("scr_mg_dl", "scr_mg_dl")):
            val = _finite(row.get(field))
            if val is None:
                errors.append(f"{line}: {label} must be a finite number")
            elif val <= 0:
                errors.append(f"{line}: {label} must be positive")

        if (row.get("sex") or "").strip().lower() not in ("male", "female"):
            errors.append(f"{line}: sex must be 'male' or 'female'")
        hep = (row.get("hepatic_impairment") or "").strip().lower()
        if hep not in HEPATIC_VALUES:
            errors.append(f"{line}: hepatic_impairment must be Yes, No or Unknown")

        drug = (row.get("drug") or "").strip()
        if drug not in VALID_DRUGS:
            errors.append(f"{line}: drug '{drug}' not in this project's scope "
                          f"({', '.join(sorted(VALID_DRUGS))})")
        elif drug in drugs_seen[pid]:
            errors.append(f"{line}: duplicate drug '{drug}' for this patient")
        drugs_seen[pid].add(drug)
        if drug == "Digoxin" and (row.get("nyha_class") or "").strip() not in ("I", "II", "III", "IV"):
            errors.append(f"{line}: Digoxin requires a valid nyha_class (I-IV)")

        if pid:
            demo = tuple(_norm(row.get(f)) for f in DEMOGRAPHIC_FIELDS)
            if pid not in first_seen:
                first_seen[pid] = (i, demo)
            elif first_seen[pid][1] != demo:
                errors.append(f"{line}: demographics differ from row {first_seen[pid][0]} "
                              f"for the same patient; record quarantined")
    return errors


def _norm(value) -> str:
    s = (value or "").strip().lower()
    x = _finite(s)
    return repr(x) if x is not None else s


def group_by_patient(rows: list) -> dict:
    """Groups VALIDATED rows into one record per patient_id with a drug list.
    Call validate_csv_rows first; this function assumes consistent rows."""
    patients = defaultdict(lambda: {"drugs": [], "nyha_class": None})
    for row in rows:
        pid = row["patient_id"].strip()
        patients[pid]["age"] = int(float(row["age"]))
        patients[pid]["sex"] = row["sex"].strip().lower()
        patients[pid]["weight_kg"] = float(row["weight_kg"])
        patients[pid]["height_cm"] = float(row["height_cm"])
        patients[pid]["scr_mg_dl"] = float(row["scr_mg_dl"])
        patients[pid]["hepatic_impairment"] = HEPATIC_VALUES[row["hepatic_impairment"].strip().lower()]
        patients[pid]["drugs"].append(row["drug"].strip())
        if row["drug"].strip() == "Digoxin":
            patients[pid]["nyha_class"] = row["nyha_class"].strip()
    return dict(patients)


def screen_patient(pid: str, p: dict, engine) -> dict:
    """Runs the batch pipeline for one grouped patient and returns one output row."""
    from renal import crcl_cockcroft_gault, renal_category
    from dose_adjustment import assess_regimen, summarize
    try:
        renal = crcl_cockcroft_gault(p["age"], p["weight_kg"], p["height_cm"],
                                     p["sex"], p["scr_mg_dl"])
        cat = renal_category(renal["crcl_ml_min"])
        ddi_findings = engine.check_all_pairs(p["drugs"]) if len(p["drugs"]) >= 2 else []
        assessment = assess_regimen(cat["category"], ddi_findings, tdm_status=None,
                                    hepatic_flag=p["hepatic_impairment"],
                                    not_assessed=[BATCH_NOT_ASSESSED[0]])
        summary = summarize(assessment)
        return {
            "Patient ID": pid,
            "CrCl (mL/min)": renal["crcl_ml_min"],
            "Renal Category": cat["category"],
            "Regimen": "; ".join(p["drugs"]),
            "Status": summary["headline"],
            "Interaction Found": "YES" if assessment["interaction_found"] else "NO",
            "Monitoring Review": "YES" if assessment["monitoring_review"] else "NO",
            "Dose Review": "YES" if assessment["dose_review"] else "NO",
            "Details": " | ".join(summary["lines"]),
        }
    except (ValueError, NotImplementedError) as e:
        return {"Patient ID": pid, "CrCl (mL/min)": None, "Renal Category": "ERROR",
                "Regimen": "; ".join(p["drugs"]), "Status": "ERROR",
                "Interaction Found": "ERROR", "Monitoring Review": "ERROR",
                "Dose Review": "ERROR", "Details": str(e)}


def parse_csv_text(csv_text: str) -> list:
    """Parses uploaded CSV text into a list of row dicts."""
    return list(csv.DictReader(io.StringIO(csv_text)))


def results_to_csv(results: list) -> str:
    """Flattens batch results back into a downloadable CSV string."""
    if not results:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
    return output.getvalue()
