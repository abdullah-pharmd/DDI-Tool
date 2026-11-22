# ddi-pk-assistant

An educational four-drug pharmacokinetic calculation and drug-drug interaction lookup prototype built in Python and Streamlit.

> **Status & Clinical Disclaimer:** Unsubmitted research-in-progress educational software prototype. It is **not clinically validated**, not approved as a medical device, and not valid for acute kidney injury (unstable serum creatinine), dialysis/CRRT, or patients under 18 years. No patient records exist in this repository. Independent clinical adjudication and external unseen-case evaluation remain open before any clinical claims.

### What this build actually does (Entry-Point Capabilities)

| Entry Point | Modules Invoked | Outputs Produced | Explicitly Not Assessed / Excluded |
|---|---|---|---|
| **Single Patient Workstation** (`app.py` Tab 1) | `renal.py`, `pk_engine.py`, `ddi_engine.py`, `dose_adjustment.py` | Adult Cockcroft-Gault CrCl & FDA renal category; drug-specific PK (`Gentamicin`, `Vancomycin`, `Digoxin` + maintenance dose, `Phenytoin`); 6-pair DDI lookup cards; independent `assess_regimen` / `summarize` flags | Live TDM (`tdm_status=None`), AKI/dialysis, patients < 18 yr, automatic interval extension, renal-based DDI alert escalation |
| **PDF Audit Summary** (`src/report_generator.py`) | Formats single-patient dicts via `summarize()` and `ALERT_LABELS` | Timestamped educational/research audit PDF matching single-patient flags and cards | Does not recalculate inputs or run TDM |
| **Batch Cohort Screening** (`app.py` Tab 2 / `src/batch_processing.py`) | `validate_csv_rows`, `group_by_patient`, `screen_patient` (`renal.py`, `ddi_engine.py`, `dose_adjustment.py`) | Per-patient renal category, 6-pair DDI flags, and `summarize()` status after strict pre-grouping validation | Drug-specific PK calculations (`pk_engine.py`) and TDM (both listed under `Not assessed` in every batch row) |
| **TDM Helper** (`src/tdm.py`) | Standalone `interpret_tdm()` | Qualitative flag (`below range`, `within range`, `above range`, or `indeterminate`) with scope caveats | Not wired into UI or batch workflow in this build |
| **ML Audit Illustration** (`src/ddi_ml.py`, `src/explainability.py`) | Standalone `train_audit_model()` | Illustrative training-set fit on the 6-row lookup table | Does NOT provide independent evidence of predictive performance |

### Key Architectural Boundaries
- **Independent Renal & DDI Flags:** `DDIEngine` (`src/ddi_engine.py`) takes `(drug_a, drug_b)` only and does not read renal function. `assess_regimen` (`src/dose_adjustment.py`) displays renal `dose_review`, DDI `interaction_found` / `monitoring_review`, `cautions` (hepatic flag is caution-only, never a calculated dose change), `insufficient_information`, and `not_assessed` side by side without escalating pair severity or extending dosing intervals automatically.
- **Structured Alert Classification:** UI cards and PDF exports map directly from `alert_class` (`ALERT_HIGH`, `ALERT_MODERATE`, `ALERT_ANALYTICAL`, `ALERT_NEGATIVE_SEARCH`, `ALERT_NOT_IN_KB`), keeping the `Vancomycin + Digoxin` PETINIA immunoassay artifact (`Tang et al. 2022, PMID 35541501`) separate from pharmacologic interactions and distinguishing documented negative searches from unassessed pairs.
- **Input & Dimensional Guards:** Non-finite (`NaN`, `inf`), boolean, and paediatric (`age < 18`) inputs are rejected before grouping or calculation. `phenytoin_pk` validates finite concentrations within a tool-scope total-concentration window (`5.0-25.0 mg/L`) rather than comparing concentration (`mg/L`) to `Vmax` (`mg/day`).

### Verification & Regression Suite
- **Bauer 2nd ed. Development/Regression Cases (`data/validation_cases.csv`):** 4 included adult male cases (`V1`, `V2`, `D1`, `D2`) covering `Vancomycin` (`t1/2`: `7.98` vs `8` hr; `27.11` vs `27` hr) and `Digoxin` (`maintenance dose`: `287.5` vs `288` ug/day; `86.5` vs `87` ug/day). Aggregating unrounded errors via `src/validation.py` yields MAPE `0.35%` (`0.35143%`) and MaxAPE `0.57%` (`0.57471%`) on displayed endpoints (`0.34%` / `0.55%` on full-precision floats). Case `V2` exposed the Stage 21 nonrenal clearance weight-scaling defect (`0.05 * weight_kg` vs flat `+0.05 mL/min`) during development and is retained as a regression check. One obese renal-impaired digoxin example (`D3_EXCLUDED`, Bauer Ch.6 Ex.4 pp. 316–317: 65-yr, 170-kg female, `SCr 4.7 mg/dL`, `Vd = 288 L`) was verified against the primary textbook pages: Bauer's `288 L` is exact under the Jusko-Koup renal-dysfunction volume formula $V = [226 + 298 \cdot \text{CrCl}/(29.1+\text{CrCl})] \cdot (\text{IBW}/70) = 288.5\text{ L}$ with Salazar-Corcoran `CrCl = 22 mL/min` and `IBW = 57 kg` (not a textbook erratum), and is excluded as outside the prototype's fixed-$7.0\text{ L/kg}$ / Cockcroft-Gault model scope.
- **Adjudicated Synthetic Consistency Matrix (`data/adjudicated_synthetic_cases.csv`):** 16 synthetic cases testing boundary renal thresholds (`90/60/50/30 mL/min`), Moderate and High DDI pairs, assay interference, hepatic caution alone, unknown hepatic status, and cross-path agreement across single-patient logic, PDF output, and batch CSV screening.
- **Post-Freeze Held-Out 4-Drug Benchmark & Comparator Study (`data/heldout_pk_cases.csv`, `data/heldout_comparator_scenarios.csv`, `scripts/evaluate_heldout_benchmark.py`, `HELDOUT_BENCHMARK_REPORT.md`):**
  - **Cryptographic Code Freeze Lock:** Verifies all `11/11` files in `src/` match the SHA-256 digests of frozen release `v0.2.0-reviewer-repair-2026-11` (`commit dd22acb`) with zero post-freeze edits to calculation modules.
  - **14 Unseen Bauer (2nd ed.) Worked Cases Across All 4 Drugs:**
    - *In-scope equations (`8/8` passing prespecified `<= 2.0%` tolerance):* Gentamicin (`4/4`, MAPE `1.04%`), Vancomycin (`1/1`, APE `0.15%`), Digoxin (`1/1`, APE `0.32%`), Phenytoin (`2/2`, MAPE `0.09%`); combined in-scope MAPE = `0.60%` (`0.5862%` unrounded), MaxAPE = `1.50%` (`1.2680%` unrounded).
    - *5 Newly Exposed Covariate/Formulation Boundary Divergences (`> 2.0%`) + 1 Verified Paediatric Abstention Gate:* Overweight-non-obese (`1.0-1.3 x IBW`) Cockcroft-Gault IBW vs TBW weight rule (`+9.00%` and `+15.21%` gentamicin $t_{1/2}$ in Ch.4 Ex.4-5), obese Cockcroft-Gault ABW vs Salazar-Corcoran CrCl (`+9.71%` vancomycin $t_{1/2}$ in Ch.5 Ex.3), phenytoin sodium salt factor $S = 0.92$ vs free acid $S = 1.0$ (`-7.99%` dose in Ch.10 Ex.1/3), Winter-Tozer $37^\circ\text{C}$ vs $25^\circ\text{C}$ coefficient (`+20.78%` in Ch.10 p.490 Ex.1), and paediatric rejection (`age = 10` blocked in Ch.10 Ex.2/4).
  - **20-Scenario Multi-Domain Comparator Benchmark:** Frozen Repaired Prototype (`20/20`, `100%`) vs Pre-Repair Prototype `5703a7c` (`3/20`, `15%`), Static Pair-Only DDI Checker (`4/20`, `20%`), and Single-Drug PK-Only Calculator (`3/20`, `15%`).

### Reproducible Setup & Verification
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -v
python scripts/verify_release.py
python scripts/evaluate_heldout_benchmark.py
streamlit run app.py
```

### Authorship, Roles & AI Assistance
- **Author:** Muhammad Abdullah Khan (Department of Pharmacy Practice, GCUF, Faisalabad, Pakistan) — conceived the prototype, implemented the modules, curated primary citations, audited defects, and prepared the verification suite and manuscript.
- **Independent Verification Status:** Unit tests and synthetic consistency checks pass locally; independent clinical pharmacist adjudication of the 6-pair table (`reviewer_signoff = PENDING pharmacist review`) and external evaluation on unseen clinical cases remain open.
- **AI Assistance:** AI coding/editing tools were used to assist code refactoring, test generation, and manuscript structural cleanup under author review and verification of all equations, primary PubMed records, and executed test outputs.
