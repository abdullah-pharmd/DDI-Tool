"""
Tests for the post-freeze held-out 4-drug PK benchmark and 20-scenario
multi-domain comparator evaluation (scripts/evaluate_heldout_benchmark.py).
Verifies that no file in src/ has been altered since v0.2.0-reviewer-repair-2026-11.
"""
import os
import sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from evaluate_heldout_benchmark import (
    evaluate_comparator_benchmark,
    evaluate_heldout_pk_cases,
    verify_frozen_src_hashes,
)


def test_frozen_v020_src_sha256_lock_intact():
    hashes = verify_frozen_src_hashes()
    assert len(hashes) == 11


def test_heldout_in_scope_pk_cases_across_all_four_drugs():
    res = evaluate_heldout_pk_cases()
    per_drug = res["per_drug_in_scope"]
    assert per_drug["Gentamicin"]["n_passed"] == 4
    assert per_drug["Vancomycin"]["n_passed"] == 1
    assert per_drug["Digoxin"]["n_passed"] == 1
    assert per_drug["Phenytoin"]["n_passed"] == 2
    assert res["overall_in_scope_display"]["mean_abs_pct_error_2dp"] == pytest.approx(0.60, abs=0.01)
    assert res["overall_in_scope_unrounded"]["mean_abs_pct_error_raw"] == pytest.approx(0.5862, abs=0.001)


def test_heldout_boundary_divergences_and_pediatric_abstention_reproduced():
    res = evaluate_heldout_pk_cases()
    by_id = {r["case_id"]: r for r in res["rows"]}
    assert by_id["H_G3_E2E_CRCL"]["outcome"] == "FAIL_COVARIATE_RULE"
    assert by_id["H_G3_E2E_CRCL"]["err_display_pct"] == pytest.approx(9.00, abs=0.05)
    assert by_id["H_G4_E2E_CRCL"]["outcome"] == "FAIL_COVARIATE_RULE"
    assert by_id["H_G4_E2E_CRCL"]["err_display_pct"] == pytest.approx(15.21, abs=0.05)
    assert by_id["H_V4_OBESE"]["outcome"] == "FAIL_SALAZAR_GAP"
    assert by_id["H_V4_OBESE"]["err_display_pct"] == pytest.approx(9.71, abs=0.05)
    assert by_id["H_P1_SALT"]["outcome"] == "FAIL_SALT_FACTOR"
    assert by_id["H_P1_SALT"]["err_display_pct"] == pytest.approx(-7.99, abs=0.05)
    assert by_id["H_P3_WT_25C"]["outcome"] == "FAIL_ASSAY_TEMP"
    assert by_id["H_P3_WT_25C"]["err_display_pct"] == pytest.approx(20.78, abs=0.05)
    assert by_id["H_P4_PEDIATRIC"]["outcome"] == "PASS_ABSTENTION"


def test_comparator_benchmark_numerators_and_denominators():
    comp = evaluate_comparator_benchmark()
    tot = comp["totals"]
    assert tot["v020"] == [20, 20]
    assert tot["pre_repair_5703a7c"] == [3, 20]
    assert tot["static_ddi_only"] == [4, 20]
    assert tot["single_pk_only"] == [3, 20]
