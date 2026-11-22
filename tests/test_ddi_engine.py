"""Tests for src/ddi_engine.py and data/ddi_knowledge_base.csv."""
import inspect
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from ddi_engine import (
    ALERT_ANALYTICAL,
    ALERT_HIGH,
    ALERT_LABELS,
    ALERT_MODERATE,
    ALERT_NEGATIVE_SEARCH,
    ALERT_NOT_IN_KB,
    DDIEngine,
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ddi_knowledge_base.csv")


def test_known_pair_found():
    engine = DDIEngine(DATA_PATH)
    result = engine.check_pair("Vancomycin", "Gentamicin")
    assert result["pair_found_in_kb"] is True
    assert result["severity"] == "High"
    assert result["alert_class"] == ALERT_HIGH
    assert ALERT_LABELS[result["alert_class"]] == "HIGH-SEVERITY INTERACTION: REVIEW REQUIRED"


def test_reversed_order_same_result():
    engine = DDIEngine(DATA_PATH)
    forward = engine.check_pair("Vancomycin", "Gentamicin")
    reversed_ = engine.check_pair("Gentamicin", "Vancomycin")
    assert forward["severity"] == reversed_["severity"]
    assert forward["alert_class"] == reversed_["alert_class"]


def test_unknown_pair_not_confused_with_confirmed_negative():
    engine = DDIEngine(DATA_PATH)
    result = engine.check_pair("Vancomycin", "Ibuprofen")
    assert result["pair_found_in_kb"] is False
    assert result["alert_class"] == ALERT_NOT_IN_KB
    assert "does NOT mean" in result["note"]


def test_all_six_kb_pairs_classification_and_verified_citations():
    engine = DDIEngine(DATA_PATH)

    vg = engine.check_pair("Vancomycin", "Gentamicin")
    assert vg["alert_class"] == ALERT_HIGH
    assert "Rybak MJ" in vg["reference"]

    gd = engine.check_pair("Gentamicin", "Digoxin")
    assert gd["alert_class"] == ALERT_MODERATE
    assert ALERT_LABELS[gd["alert_class"]] == "MODERATE INTERACTION: MONITORING REVIEW"
    assert "PMID 15085946" in gd["reference"]
    assert "PMID 1323465" in gd["reference"]
    assert "Elrggal" not in gd["reference"]

    pd = engine.check_pair("Phenytoin", "Digoxin")
    assert pd["alert_class"] == ALERT_MODERATE
    assert "PMID 4054206" in pd["reference"]
    assert "Eur J Clin Pharmacol" in pd["reference"]
    assert "CYP3A4" not in pd["mechanism"]

    gp = engine.check_pair("Gentamicin", "Phenytoin")
    assert gp["pair_found_in_kb"] is True
    assert gp["interaction_present"] == "NO"
    assert gp["alert_class"] == ALERT_NEGATIVE_SEARCH
    assert "NOT PROOF OF SAFETY" in ALERT_LABELS[gp["alert_class"]]

    vd = engine.check_pair("Vancomycin", "Digoxin")
    assert vd["pair_found_in_kb"] is True
    assert vd["interaction_present"] == "NO"
    assert vd["alert_class"] == ALERT_ANALYTICAL
    assert ALERT_LABELS[vd["alert_class"]] == "ASSAY/SPECIMEN LIMITATION: NOT A DRUG INTERACTION"
    assert "PMID 35541501" in vd["reference"]
    assert "PMID 1323465" not in vd["reference"]

    vp = engine.check_pair("Vancomycin", "Phenytoin")
    assert vp["pair_found_in_kb"] is True
    assert vp["interaction_present"] == "NO"
    assert vp["alert_class"] == ALERT_NEGATIVE_SEARCH


def test_ddi_lookup_accepts_no_renal_input_and_stays_identical():
    sig = inspect.signature(DDIEngine.check_pair)
    assert list(sig.parameters.keys()) == ["self", "drug_a", "drug_b"]
    engine = DDIEngine(DATA_PATH)
    r1 = engine.check_pair("Vancomycin", "Gentamicin")
    r2 = engine.check_pair("Vancomycin", "Gentamicin")
    assert r1 == r2


def test_check_all_pairs_covers_full_combination():
    engine = DDIEngine(DATA_PATH)
    results = engine.check_all_pairs(["Vancomycin", "Gentamicin", "Digoxin"])
    assert len(results) == 3  # 3 choose 2
