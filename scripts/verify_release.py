"""
Executable Release Verification Script
Runs pytest, recalculates Table 1 from source, audits all 6 KB pairs,
exercises the 16 adjudicated synthetic cases across single-patient, batch,
and PDF output paths, and writes VERIFICATION_REPORT.md.
"""
import csv
import datetime
import os
import platform
import subprocess
import sys
import tempfile

import pypdf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from batch_processing import HEPATIC_VALUES, group_by_patient, screen_patient, validate_csv_rows
from ddi_engine import ALERT_LABELS, DDIEngine
from dose_adjustment import assess_regimen, summarize
from renal import crcl_cockcroft_gault, renal_category
from report_generator import generate_report
from validation import recalculate_table1_from_source


def main() -> int:
    now_local = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Run pytest
    py_res = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if py_res.returncode != 0:
        print(py_res.stdout)
        print(py_res.stderr)
        return py_res.returncode

    summary_line = [ln for ln in py_res.stdout.splitlines() if "passed" in ln][-1]

    # 2. Git branch & commit
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()

    # 3. Table 1 recalculation
    t1 = recalculate_table1_from_source()
    arch = t1["archived_display"]
    live = t1["unrounded_live"]

    # 4. KB audit
    kb_path = os.path.join(ROOT, "data", "ddi_knowledge_base.csv")
    engine = DDIEngine(kb_path)
    with open(kb_path, newline="", encoding="utf-8") as f:
        kb_rows = list(csv.DictReader(f))
    kb_checks = []
    for row in kb_rows:
        res = engine.check_pair(row["drug_a"], row["drug_b"])
        kb_checks.append((row["pair_id"], f"{row['drug_a']} + {row['drug_b']}", res["alert_class"], ALERT_LABELS[res["alert_class"]], row["severity"], row["last_verified"], row["reviewer_signoff"], row["reference"]))

    # 5. Adjudicated synthetic matrix across all 3 paths
    syn_path = os.path.join(ROOT, "data", "adjudicated_synthetic_cases.csv")
    with open(syn_path, newline="", encoding="utf-8") as f:
        syn_cases = list(csv.DictReader(f))

    syn_results = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for case in syn_cases:
            drugs = [d.strip() for d in case["drugs"].split(";") if d.strip()]
            age = int(case["age"])
            sex = case["sex"].strip().lower()
            wt = float(case["weight_kg"])
            ht = float(case["height_cm"])
            scr = float(case["scr_mg_dl"])
            hep_flag = HEPATIC_VALUES[case["hepatic_impairment"].strip().lower()]

            renal_res = crcl_cockcroft_gault(age, wt, ht, sex, scr)
            cat_res = renal_category(renal_res["crcl_ml_min"])
            ddi_findings = engine.check_all_pairs(drugs) if len(drugs) >= 2 else []
            single_assess = assess_regimen(cat_res["category"], ddi_findings, tdm_status=None, hepatic_flag=hep_flag)
            single_sum = summarize(single_assess)

            batch_rows = [{
                "patient_id": case["case_id"], "age": case["age"], "sex": case["sex"],
                "weight_kg": case["weight_kg"], "height_cm": case["height_cm"],
                "scr_mg_dl": case["scr_mg_dl"], "hepatic_impairment": case["hepatic_impairment"],
                "drug": d, "nyha_class": case["nyha_class"],
            } for d in drugs]
            errs = validate_csv_rows(batch_rows)
            assert not errs, f"{case['case_id']} validation failed: {errs}"
            batch_out = screen_patient(case["case_id"], group_by_patient(batch_rows)[case["case_id"]], engine)

            pdf_file = os.path.join(tmpdir, f"{case['case_id']}.pdf")
            generate_report(
                pdf_file,
                {"Patient ID": case["case_id"], "Age": age, "Sex": sex, "Medications": ", ".join(drugs)},
                renal_res, cat_res, {}, ddi_findings, single_assess,
            )
            pdf_text = " ".join((p.extract_text() or "") for p in pypdf.PdfReader(pdf_file).pages)

            ok = (
                cat_res["category"] == case["expected_renal_category"]
                and single_sum["headline"] == case["expected_headline"]
                and batch_out["Status"] == single_sum["headline"]
                and batch_out["Interaction Found"] == case["expected_interaction_found"]
                and batch_out["Monitoring Review"] == case["expected_monitoring_review"]
                and batch_out["Dose Review"] == case["expected_dose_review"]
                and single_sum["headline"] in pdf_text
            )
            assert ok, f"Consistency check failed on {case['case_id']}"
            syn_results.append((
                case["case_id"],
                f"{renal_res['crcl_ml_min']} ({cat_res['category']})",
                ", ".join(drugs),
                case["hepatic_impairment"],
                single_sum["headline"],
                batch_out["Interaction Found"],
                batch_out["Monitoring Review"],
                batch_out["Dose Review"],
                "PASS (Screen=PDF=Batch)",
            ))

    # 6. Write report
    lines = [
        "# Verification Report — Four-Drug PK & DDI Decision-Support Prototype",
        "",
        f"- **Generated (UTC):** {now_utc}",
        f"- **Generated (Local):** {now_local}",
        f"- **Git Branch / Base Commit:** `{branch}` (`{commit}`)",
        f"- **Python / Platform:** {sys.version.split()[0]} ({platform.platform()})",
        f"- **Automated Test Suite (`pytest -v`):** `{summary_line}`",
        "",
        "## 1. Table 1 Recalculation From Source (`src/validation.py`)",
        "",
        "| Case ID | Role | Drug | Endpoint | Reported | Calc (Display) | Calc (Unrounded) | Err % (Display) | Err % (Unrounded) |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in t1["rows"]:
        lines.append(
            f"| {r['case_id']} | {r['case_role']} | {r['drug']} | {r['metric']} | "
            f"{r['reported']} | {r['calculated_display']} | {r['calculated_unrounded']:.5f} | "
            f"{r['pct_error_display_raw']:+.5f}% ({r['pct_error_display_2dp']:+.2f}%) | "
            f"{r['pct_error_unrounded_raw']:+.5f}% ({r['pct_error_unrounded_2dp']:+.2f}%) |"
        )
    lines += [
        "",
        f"- **Archived Display Endpoints (`7.98/8, 27.11/27, 287.5/288, 86.5/87`):** "
        f"MAPE = `{arch['mean_abs_pct_error_raw']:.5f}%` (`{arch['mean_abs_pct_error_2dp']:.2f}%` at 2 d.p.); "
        f"MaxAPE = `{arch['max_abs_pct_error_raw']:.5f}%` (`{arch['max_abs_pct_error_2dp']:.2f}%` at 2 d.p.).",
        f"- **Live Unrounded Outputs:** "
        f"MAPE = `{live['mean_abs_pct_error_raw']:.5f}%` (`{live['mean_abs_pct_error_2dp']:.2f}%` at 2 d.p.); "
        f"MaxAPE = `{live['max_abs_pct_error_raw']:.5f}%` (`{live['max_abs_pct_error_2dp']:.2f}%` at 2 d.p.).",
        "- **Excluded Case (`D3_EXCLUDED`):** Primary-page inspection (2026-11-22) of Bauer Ch.6 Example 4 (pp. 316-317: 65-yr, 170-kg female, SCr 4.7 mg/dL, IBW 57 kg, Salazar-Corcoran CrCl 22 mL/min) confirmed `Vd = 288 L` is mathematically exact under the Jusko-Koup renal-dysfunction Vd equation `V = [226 + 298*CrCl/(29.1+CrCl)]*(IBW/70) = 288.50 L` (NOT a textbook erratum); retained in `data/validation_cases.csv` as `EXCLUDED_OUT_OF_MODEL_SCOPE` because `digoxin_pk()` implements only the fixed normal-renal scalar `7.0 L/kg` and `renal.py` does not implement Salazar-Corcoran.",
        "",
        "## 2. Knowledge Base Audit (`data/ddi_knowledge_base.csv`)",
        "",
        "| ID | Pair | Alert Class | Displayed Label | Severity | Verified | Pharmacist Sign-off | Citation |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, pair, acls, lbl, sev, ver, sign, ref in kb_checks:
        lines.append(f"| {cid} | {pair} | `{acls}` | {lbl} | {sev} | {ver} | {sign} | {ref} |")

    lines += [
        "",
        "## 3. Adjudicated Synthetic Matrix Consistency (`data/adjudicated_synthetic_cases.csv`)",
        "",
        "| Case ID | CrCl (Category) | Drugs | Hepatic | Status Headline | Interaction | Monitoring | Dose Review | Cross-Path Result |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cid, crcl_s, drugs_s, hep_s, head, inter, mon, dose, res_s in syn_results:
        lines.append(f"| {cid} | {crcl_s} | {drugs_s} | {hep_s} | {head} | {inter} | {mon} | {dose} | {res_s} |")

    lines.append("")
    out_path = os.path.join(ROOT, "VERIFICATION_REPORT.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_path} ({summary_line}, {len(syn_results)}/{len(syn_results)} synthetic cases consistent)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
