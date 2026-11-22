"""
Module 5 — Regimen review flags (integration point)
Reads Module 2 (renal category), Module 3 (DDI pair records), Module 6 (TDM)
and the hepatic flag, and reports each finding in its OWN field. Renal and
drug-pair flags are independent: renal category does NOT escalate or alter any
drug-pair alert in this build, and no dosing interval is changed automatically.

Fields (all three output routes -- screen, PDF, batch -- use summarize()):
  interaction_found        a sourced drug-pair interaction (High or Moderate) is present
  monitoring_review        interaction or assay limitation that warrants monitoring review
  dose_review              renal category Moderate/Severe, or a TDM value outside range
  cautions                 caution-only items (hepatic) -- never a dosing change
  insufficient_information inputs needed for a check are missing/unknown
  not_assessed             checks this route did not perform
Hepatic impairment is a caution flag only, never a calculated dose change,
per docs/project_scope.md.
"""
from ddi_engine import (ALERT_HIGH, ALERT_MODERATE, ALERT_ANALYTICAL,
                        ALERT_NOT_IN_KB, classify_record)

TDM_FLAG_STATES = ("above range", "below range")
TDM_OK_STATES = ("within range",)


def assess_regimen(renal_category: str, ddi_findings: list,
                   tdm_status: str = None, hepatic_flag=False,
                   not_assessed: list = None) -> dict:
    """
    Aggregates review flags from upstream modules. Computes no new dose.
    hepatic_flag: True (documented), False (documented absent) or None (unknown).
    tdm_status: None means TDM was not assessed on this route; "indeterminate"
    means it was attempted but required information was missing.
    """
    interaction_reasons, monitoring_reasons, dose_reasons = [], [], []
    cautions, insufficient = [], []
    not_assessed = list(not_assessed or [])

    if renal_category in ("Moderate", "Severe"):
        dose_reasons.append(f"renal impairment ({renal_category}) — review drug-specific "
                            f"renally-cleared dosing (Module 4)")
    elif renal_category not in ("Normal", "Mild"):
        insufficient.append("renal category unavailable")

    for f in ddi_findings:
        alert = f.get("alert_class") or classify_record(f)
        pair = f"{f['drug_a']}+{f['drug_b']}"
        if alert in (ALERT_HIGH, ALERT_MODERATE):
            level = "High" if alert == ALERT_HIGH else "Moderate"
            interaction_reasons.append(f"{level} interaction: {pair}")
            monitoring_reasons.append(f"{pair}: {f.get('clinical_recommendation', '')}")
        elif alert == ALERT_ANALYTICAL:
            monitoring_reasons.append(f"{pair}: assay/specimen limitation, not a drug "
                                      f"interaction — {f.get('clinical_recommendation', '')}")
        elif alert == ALERT_NOT_IN_KB:
            insufficient.append(f"{pair}: not in knowledge base (interaction status unknown)")

    if tdm_status is None:
        not_assessed.append("therapeutic drug monitoring")
    elif tdm_status in TDM_FLAG_STATES:
        dose_reasons.append(f"measured concentration is {tdm_status} — clinician "
                            f"judgment required on any adjustment")
    elif tdm_status not in TDM_OK_STATES:
        insufficient.append(f"TDM interpretation {tdm_status}")

    if hepatic_flag is True:
        cautions.append("hepatic impairment documented — CAUTION ONLY; no calculated "
                        "adjustment is provided for this factor")
    elif hepatic_flag is None:
        insufficient.append("hepatic status unknown")

    return {
        "interaction_found": bool(interaction_reasons),
        "interaction_reasons": interaction_reasons,
        "monitoring_review": bool(monitoring_reasons),
        "monitoring_reasons": monitoring_reasons,
        "dose_review": bool(dose_reasons),
        "dose_reasons": dose_reasons,
        "cautions": cautions,
        "insufficient_information": insufficient,
        "not_assessed": not_assessed,
        "note": "Flags identify what a clinician should review. They do not "
                "replace clinical judgment, and no dose or interval is changed "
                "automatically.",
    }


def summarize(assessment: dict) -> dict:
    """
    One headline status plus its supporting lines. The headline is never
    reassuring: the most favourable possible status says only that none of
    the checks performed raised a flag, and lists what was not assessed.
    """
    a = assessment
    if a["dose_review"]:
        headline = "DOSE REVIEW INDICATED"
    elif a["monitoring_review"]:
        headline = "MONITORING REVIEW INDICATED"
    elif a["insufficient_information"]:
        headline = "INSUFFICIENT INFORMATION"
    elif a["cautions"]:
        headline = "CAUTION NOTED (NO DOSING CHANGE CALCULATED)"
    else:
        headline = "NO FLAGS FROM THE CHECKS PERFORMED"
    lines = []
    lines += [f"Dose review: {r}" for r in a["dose_reasons"]]
    lines += [f"Interaction: {r}" for r in a["interaction_reasons"]]
    lines += [f"Monitoring: {r}" for r in a["monitoring_reasons"]]
    lines += [f"Caution: {r}" for r in a["cautions"]]
    lines += [f"Insufficient information: {r}" for r in a["insufficient_information"]]
    lines += [f"Not assessed: {r}" for r in a["not_assessed"]]
    return {"headline": headline, "lines": lines}
