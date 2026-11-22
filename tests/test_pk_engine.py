"""
Tests for src/pk_engine.py and src/validation.py.
Cases V1/V2/D1/D2 are development/regression cases from Bauer LA, Applied
Clinical Pharmacokinetics, 2nd ed., Ch.5 Examples 1-2, Ch.6 Examples 1&3.
Patient in all four cases: 70 kg, 5'10" (177.8 cm), male -- IBW=73 kg (not obese).
"""
import math
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pk_engine import (
    digoxin_maintenance_dose,
    digoxin_pk,
    gentamicin_pk,
    phenytoin_pk,
    vancomycin_pk,
    winter_tozer_correction,
)
from validation import recalculate_table1_from_source

HEIGHT_5FT10 = 177.8


def test_vancomycin_case_v1_normal_renal_function():
    result = vancomycin_pk(weight_kg=70, crcl_ml_min=97, height_cm=HEIGHT_5FT10, sex="male")
    assert result["vd_l"] == pytest.approx(49.0, abs=0.1)
    assert result["half_life_hr"] == pytest.approx(7.98, abs=0.01)


def test_vancomycin_case_v2_renal_impairment():
    result = vancomycin_pk(weight_kg=70, crcl_ml_min=25, height_cm=HEIGHT_5FT10, sex="male")
    assert result["half_life_hr"] == pytest.approx(27.11, abs=0.01)


def test_vancomycin_nonrenal_constant_scales_with_weight():
    """Regression test: nonrenal constant must scale with weight_kg (0.05*weight),
    NOT stay flat at +0.05 mL/min. Flat form would give cl_ml_min ~= 17.4 (WRONG)."""
    result = vancomycin_pk(weight_kg=70, crcl_ml_min=25, height_cm=HEIGHT_5FT10, sex="male")
    assert result["cl_ml_min"] == pytest.approx(20.88, abs=0.1)
    assert result["cl_ml_min"] != pytest.approx(17.43, abs=0.1)


def test_vancomycin_obesity_vd_correction_uses_ibw_not_actual():
    """For a genuinely obese patient (>30% over IBW), Vd must use IBW, not actual weight."""
    result = vancomycin_pk(weight_kg=130, crcl_ml_min=60, height_cm=HEIGHT_5FT10, sex="male")
    assert result["weight_used_for_vd_kg"] == pytest.approx(73.0, abs=0.5)


def test_vancomycin_non_obese_uses_actual_weight_not_ibw():
    """A non-obese patient (70 kg actual vs 73 kg IBW) must use actual weight for Vd."""
    result = vancomycin_pk(weight_kg=70, crcl_ml_min=97, height_cm=HEIGHT_5FT10, sex="male")
    assert result["weight_used_for_vd_kg"] == pytest.approx(70.0, abs=0.5)


def test_digoxin_case_d1_normal_renal_no_hf():
    result = digoxin_pk(weight_kg=70, crcl_ml_min=97, nyha_class="II", height_cm=HEIGHT_5FT10, sex="male")
    assert result["cl_ml_min"] == pytest.approx(166.39, abs=0.1)
    assert result["vd_l"] == pytest.approx(490.0, abs=0.1)
    dose = digoxin_maintenance_dose(result["cl_ml_min_unrounded"], css_target_ng_ml=1.2, bioavailability=1.0)
    assert dose["dose_ug_per_tau"] == pytest.approx(287.5, abs=0.1)


def test_digoxin_case_d2_renal_impairment_moderate_hf():
    result = digoxin_pk(weight_kg=70, crcl_ml_min=25, nyha_class="IV", height_cm=HEIGHT_5FT10, sex="male")
    assert result["cl_ml_min"] == pytest.approx(52.58, abs=0.1)
    dose = digoxin_maintenance_dose(result["cl_ml_min_unrounded"], css_target_ng_ml=0.8, bioavailability=0.7)
    assert dose["dose_ug_per_tau"] == pytest.approx(86.5, abs=0.1)


def test_digoxin_invalid_nyha_class_raises():
    with pytest.raises(ValueError):
        digoxin_pk(weight_kg=70, crcl_ml_min=80, nyha_class="V", height_cm=HEIGHT_5FT10, sex="male")


def test_gentamicin_normal_renal_function():
    result = gentamicin_pk(weight_kg=70, crcl_ml_min=80, height_cm=HEIGHT_5FT10, sex="male")
    assert result["half_life_hr"] == pytest.approx(2.79, abs=0.05)


def test_phenytoin_dose_for_target_css():
    result = phenytoin_pk(weight_kg=70, css_target_mg_l=15.0, height_cm=HEIGHT_5FT10, sex="male")
    assert result["css_target_mg_l"] == pytest.approx(15.0, abs=0.01)
    assert result["dose_mg_day"] == pytest.approx(386.8, abs=1.0)
    assert result["dose_mg_day"] < result["vmax_mg_day"]


@pytest.mark.parametrize("bad_css", [4.9, 25.1, -5.0, 0.0, float("nan"), float("inf")])
def test_phenytoin_css_outside_supported_concentration_window_raises(bad_css):
    with pytest.raises(ValueError):
        phenytoin_pk(weight_kg=70, css_target_mg_l=bad_css, height_cm=HEIGHT_5FT10, sex="male")


@pytest.mark.parametrize("bad_vmax,bad_km", [(0.0, 4.0), (-7.0, 4.0), (7.0, 0.0), (7.0, -4.0)])
def test_phenytoin_non_positive_mm_params_raise(bad_vmax, bad_km):
    with pytest.raises(ValueError):
        phenytoin_pk(
            weight_kg=70,
            css_target_mg_l=15.0,
            height_cm=HEIGHT_5FT10,
            sex="male",
            vmax_mg_kg_day=bad_vmax,
            km_mg_l=bad_km,
        )


def test_winter_tozer_hypoalbuminemia_correction():
    result = winter_tozer_correction(8.0, 2.5, severe_renal_impairment=False)
    assert result["c_corrected_mg_l"] == pytest.approx(13.33, abs=0.05)


def test_zero_and_nonfinite_inputs_raise():
    with pytest.raises(ValueError):
        vancomycin_pk(weight_kg=0, crcl_ml_min=80, height_cm=HEIGHT_5FT10, sex="male")
    with pytest.raises(ValueError):
        gentamicin_pk(weight_kg=70, crcl_ml_min=float("nan"), height_cm=HEIGHT_5FT10, sex="male")
    with pytest.raises(ValueError):
        digoxin_pk(weight_kg=70, crcl_ml_min=float("inf"), nyha_class="I", height_cm=HEIGHT_5FT10, sex="male")
    with pytest.raises(ValueError):
        winter_tozer_correction(float("nan"), 2.5, severe_renal_impairment=False)


def test_table1_recalculation_unrounded_aggregation():
    summary = recalculate_table1_from_source()
    arch = summary["archived_display"]
    live = summary["unrounded_live"]
    assert arch["mean_abs_pct_error_raw"] == pytest.approx(0.35143, abs=1e-4)
    assert arch["max_abs_pct_error_raw"] == pytest.approx(0.57471, abs=1e-4)
    assert arch["mean_abs_pct_error_2dp"] == 0.35
    assert arch["max_abs_pct_error_2dp"] == 0.57
    assert live["mean_abs_pct_error_raw"] == pytest.approx(0.34179, abs=1e-4)
    assert live["max_abs_pct_error_raw"] == pytest.approx(0.54778, abs=1e-4)
    assert live["mean_abs_pct_error_2dp"] == 0.34
    assert live["max_abs_pct_error_2dp"] == 0.55
