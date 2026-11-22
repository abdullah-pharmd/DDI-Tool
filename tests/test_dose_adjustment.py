"""
Tests for src/dose_adjustment.py, src/tdm.py, src/batch_processing.py,
src/report_generator.py, and cross-path consistency on data/adjudicated_synthetic_cases.csv.
"""
import csv
import os
import sys
import pypdf
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from batch_processing import (
    HEPATIC_VALUES,
    group_by_patient,
    screen_patient,
    validate_csv_rows,
)
from ddi_engine import DDIEngine
from dose_adjustment import assess_regimen, summarize
from renal import crcl_cockcroft_gault, renal_category
from report_generator import generate_report
from tdm import INDETERMINATE, interpret_tdm

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KB_PATH = os.path.join(DATA_DIR, "ddi_knowledge_base.csv")
SYNTHETIC_CASES_PATH = os.path.join(DATA_DIR, "adjudicated_synthetic_cases.csv")


def test_moderate_pair_normal_renal_preserves_monitoring_review():
    engine = DDIEngine(KB_PATH)
    findings = engine.check_all_pairs(["Phenytoin", "Digoxin"])
    assessment = assess_regimen("Normal", findings, tdm_status=None, hepatic_flag=False)
    summary = summarize(assessment)
    assert assessment["interaction_found"] is True
    assert assessment["monitoring_review"] is True
    assert assessment["dose_review"] is False
    assert summary["headline"] == "MONITORING REVIEW INDICATED"


def test_hepatic_caution_alone_never_sets_dose_review():
    engine = DDIEngine(KB_PATH)
    findings = engine.check_all_pairs(["Gentamicin", "Phenytoin"])  # negative search
    assessment = assess_regimen("Normal", findings, tdm_status=None, hepatic_flag=True)
    summary = summarize(assessment)
    assert assessment["dose_review"] is False
    assert len(assessment["cautions"]) == 1
    assert summary["headline"] == "CAUTION NOTED (NO DOSING CHANGE CALCULATED)"


def test_unknown_hepatic_status_recorded_as_insufficient_information():
    assessment = assess_regimen("Normal", [], tdm_status=None, hepatic_flag=None)
    summary = summarize(assessment)
    assert "hepatic status unknown" in assessment["insufficient_information"]
    assert assessment["dose_review"] is False
    assert summary["headline"] == "INSUFFICIENT INFORMATION"


@pytest.mark.parametrize(
    "crcl,expected_cat,expected_dose_review",
    [
        (90.0, "Normal", False),
        (89.9, "Mild", False),
        (60.0, "Mild", False),
        (59.9, "Moderate", True),
        (30.0, "Moderate", True),
        (29.9, "Severe", True),
    ],
)
def test_renal_boundaries_with_and_without_high_pair(crcl, expected_cat, expected_dose_review):
    cat = renal_category(crcl)["category"]
    assert cat == expected_cat
    no_pair = assess_regimen(cat, [], tdm_status=None, hepatic_flag=False)
    assert no_pair["dose_review"] is expected_dose_review

    engine = DDIEngine(KB_PATH)
    high_pair = engine.check_all_pairs(["Vancomycin", "Gentamicin"])
    with_pair = assess_regimen(cat, high_pair, tdm_status=None, hepatic_flag=False)
    assert with_pair["interaction_found"] is True
    assert with_pair["monitoring_review"] is True
    assert with_pair["dose_review"] is expected_dose_review


@pytest.mark.parametrize("bad_val", [float("nan"), float("inf"), float("-inf"), None, "abc", True, -1.0])
def test_tdm_rejects_nonfinite_missing_and_negative_values_as_indeterminate(bad_val):
    res = interpret_tdm("digoxin", bad_val, measurement_type="post_distribution", unit="ng/mL")
    assert res["status"] == INDETERMINATE


def test_tdm_requires_explicit_measurement_type_and_matching_unit():
    missing_type = interpret_tdm("vancomycin", 450.0, measurement_type=None, unit="mg*h/L")
    assert missing_type["status"] == INDETERMINATE

    wrong_unit = interpret_tdm("vancomycin", 450.0, measurement_type="auc24", unit="ug/mL")
    assert wrong_unit["status"] == INDETERMINATE

    valid_vanco = interpret_tdm("vancomycin", 450.0, measurement_type="auc24", unit="mg*h/L")
    assert valid_vanco["status"] == "within range"
    assert any("serious MRSA" in lim for lim in valid_vanco["limitations"])

    phenytoin_renal = interpret_tdm(
        "phenytoin",
        15.0,
        measurement_type="total_steady_state",
        unit="mg/L",
        context={"renal_or_hepatic_disease": True},
    )
    assert phenytoin_renal["status"] == "within range"
    assert any("unbound phenytoin" in lim for lim in phenytoin_renal["limitations"])


def test_batch_validator_blocks_nan_nonnumeric_pediatric_and_conflicting_patient_rows():
    base = {
        "patient_id": "P1",
        "age": "50",
        "sex": "male",
        "weight_kg": "70",
        "height_cm": "175",
        "scr_mg_dl": "1.0",
        "hepatic_impairment": "No",
        "drug": "Vancomycin",
        "nyha_class": "",
    }
    assert validate_csv_rows([base]) == []

    # Non-numeric height, NaN SCr, age 5, and invalid hepatic value must fail
    bad_rows = [
        {**base, "height_cm": "abc"},
        {**base, "scr_mg_dl": "NaN"},
        {**base, "age": "5"},
        {**base, "hepatic_impairment": "maybe"},
    ]
    for r in bad_rows:
        errs = validate_csv_rows([r])
        assert len(errs) >= 1

    # Unknown hepatic status passes validation and maps to None (not False)
    unk_row = {**base, "hepatic_impairment": "Unknown"}
    assert validate_csv_rows([unk_row]) == []
    grouped_unk = group_by_patient([unk_row])
    assert grouped_unk["P1"]["hepatic_impairment"] is None

    # Conflicting demographics across two rows for one patient must fail before grouping
    row1 = {**base, "age": "50", "drug": "Vancomycin"}
    row2 = {**base, "age": "60", "drug": "Gentamicin"}
    conflict_errs = validate_csv_rows([row1, row2])
    assert len(conflict_errs) == 1
    assert "row 2" in conflict_errs[0].lower()
    assert "row 3" in conflict_errs[0].lower()


def test_adjudicated_synthetic_cases_agree_across_screen_pdf_and_batch(tmp_path):
    engine = DDIEngine(KB_PATH)
    with open(SYNTHETIC_CASES_PATH, newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))
    assert len(cases) >= 14

    for case in cases:
        drugs = [d.strip() for d in case["drugs"].split(";") if d.strip()]
        age = int(case["age"])
        sex = case["sex"].strip().lower()
        wt = float(case["weight_kg"])
        ht = float(case["height_cm"])
        scr = float(case["scr_mg_dl"])
        hep_str = case["hepatic_impairment"].strip().lower()
        hep_flag = HEPATIC_VALUES[hep_str]

        # 1. Single-patient path
        renal_res = crcl_cockcroft_gault(age, wt, ht, sex, scr)
        cat_res = renal_category(renal_res["crcl_ml_min"])
        ddi_findings = engine.check_all_pairs(drugs) if len(drugs) >= 2 else []
        single_assess = assess_regimen(cat_res["category"], ddi_findings, tdm_status=None, hepatic_flag=hep_flag)
        single_summary = summarize(single_assess)

        assert cat_res["category"] == case["expected_renal_category"], case["case_id"]
        assert single_summary["headline"] == case["expected_headline"], case["case_id"]
        assert ("YES" if single_assess["interaction_found"] else "NO") == case["expected_interaction_found"], case["case_id"]
        assert ("YES" if single_assess["monitoring_review"] else "NO") == case["expected_monitoring_review"], case["case_id"]
        assert ("YES" if single_assess["dose_review"] else "NO") == case["expected_dose_review"], case["case_id"]
        assert ("YES" if single_assess["cautions"] else "NO") == case["expected_caution"], case["case_id"]
        assert ("YES" if single_assess["insufficient_information"] else "NO") == case["expected_insufficient"], case["case_id"]

        # 2. Batch path
        batch_rows = [
            {
                "patient_id": case["case_id"],
                "age": case["age"],
                "sex": case["sex"],
                "weight_kg": case["weight_kg"],
                "height_cm": case["height_cm"],
                "scr_mg_dl": case["scr_mg_dl"],
                "hepatic_impairment": case["hepatic_impairment"],
                "drug": d,
                "nyha_class": case["nyha_class"],
            }
            for d in drugs
        ]
        assert validate_csv_rows(batch_rows) == [], case["case_id"]
        grouped = group_by_patient(batch_rows)
        batch_out = screen_patient(case["case_id"], grouped[case["case_id"]], engine)
        assert batch_out["Renal Category"] == case["expected_renal_category"], case["case_id"]
        assert batch_out["Status"] == single_summary["headline"], case["case_id"]
        assert batch_out["Interaction Found"] == case["expected_interaction_found"], case["case_id"]
        assert batch_out["Monitoring Review"] == case["expected_monitoring_review"], case["case_id"]
        assert batch_out["Dose Review"] == case["expected_dose_review"], case["case_id"]
        assert "drug-specific PK calculations" in batch_out["Details"], case["case_id"]

        # 3. PDF export path
        pdf_path = tmp_path / f"{case['case_id']}.pdf"
        generate_report(
            str(pdf_path),
            {"Patient ID": case["case_id"], "Age": age, "Sex": sex, "Medications": ", ".join(drugs)},
            renal_res,
            cat_res,
            {},
            ddi_findings,
            single_assess,
        )
        pdf_text = " ".join((p.extract_text() or "") for p in pypdf.PdfReader(str(pdf_path)).pages)
        assert single_summary["headline"] in pdf_text, case["case_id"]
        assert "Standard Regimen Maintained" not in pdf_text
        assert "CRITICAL CONTRAINDICATION" not in pdf_text
