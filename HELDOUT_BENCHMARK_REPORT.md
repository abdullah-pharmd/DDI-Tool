# Post-Freeze Held-Out 4-Drug Benchmark & Comparator Study Report

- **Generated (UTC):** 2026-11-22 03:07:29 UTC
- **Frozen Code Release Tested:** `v0.2.0-reviewer-repair-2026-11` (`commit dd22acb`)
- **Cryptographic Freeze Verification:** `11/11` files in `src/` verified identical to `v0.2.0-reviewer-repair-2026-11` SHA-256 lock (zero post-freeze edits to calculation modules).

## 1. Frozen `src/` Module SHA-256 Lock Receipt

| Module (`src/`) | Verified SHA-256 Digest (`v0.2.0-reviewer-repair-2026-11`) |
|---|---|
| `__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `batch_processing.py` | `2646ddef45a38f44d30278c228955132d0e75eb3f74f02841ae2e47a53ec25ee` |
| `ddi_engine.py` | `dec35e86b73dc4ae9b63853b12bb196cdb8238c9ed37059494d4101941a013e4` |
| `ddi_ml.py` | `018712d552d7b3d0b529bb3ff89f812f6aa053ac7492708c2affb35e04980447` |
| `dose_adjustment.py` | `5313ff4af144319e40da3df46e469da30a24cf31c6e515964cfb49fa5f2d7d8b` |
| `explainability.py` | `571b9e5d3b33ec72271ed2e335bbaa5a7e853e67f03275ece7c3b4ff7a0fed1f` |
| `pk_engine.py` | `4d96d2dca79b8a16c30d57d65faadae61d6027b56164611fb3aa6f2475c66943` |
| `renal.py` | `68eb2e031c40b25c893610eeabd58869b18a790799fafcfa2f423f58ed9318e2` |
| `report_generator.py` | `af12e94e3cfc2f14bc5a3791fca61efe49ab9803901c08248135749f6d656003` |
| `tdm.py` | `2a5865877871496e5f1a527dab57d008a14ebfbc1de0790b8ec73127a4c06c6c` |
| `validation.py` | `67f48dd0d08c961a6114e3cf3bb3300583ed80c8c24a6a6724c7c604f26471ff` |

## 2. Held-Out Unseen Published PK Cases Across All 4 Drugs (`data/heldout_pk_cases.csv`)

### 2A. Per-Drug Summary on In-Scope Unseen Cases (Prespecified Tolerance `<= 2.0%`)

| Drug | Unseen In-Scope Cases (`Passed / Total`) | MAPE % (Display / Unrounded) | MaxAPE % (Display / Unrounded) | Primary Endpoints Evaluated |
|---|---:|---:|---:|---|
| Gentamicin | `4 / 4` | `1.04%` (`1.0100%`) | `1.50%` (`1.2680%`) | Half-life t1/2 (hr), ke (hr^-1), Vd (L) — Bauer Ch.4 Ex.1, Ex.2, Ex.4, Ex.5 |
| Vancomycin | `1 / 1` | `0.15%` (`0.1617%`) | `0.15%` (`0.1617%`) | Half-life t1/2 (hr), k (hr^-1), Vd (L), CrCl — Bauer Ch.5 Trough Ex.1 (55 yr, 78 kg) |
| Digoxin | `1 / 1` | `0.32%` (`0.3277%`) | `0.32%` (`0.3277%`) | Daily maintenance dose (ug/day), CL (mL/min) — Bauer Ch.6 Ex.2 (AFib, CrCl 25) |
| Phenytoin | `2 / 2` | `0.09%` (`0.0801%`) | `0.17%` (`0.1603%`) | Michaelis-Menten Vmax (mg/day) & Winter-Tozer severe-renal normalization — Bauer Ch.10 |
| **All 4 Drugs Combined (In-Scope)** | **`8 / 8` (`100%`)** | **`0.60%` (`0.58620%`)** | **`1.50%` (`1.26799%`)** | All 8 unseen in-scope endpoints across 4 medicines within `<= 2.0%` tolerance |

### 2B. Case-by-Case Held-Out Results (8 In-Scope Passes + 5 Covariate/Formulation Boundary Divergences + 1 Paediatric Abstention)

| Case ID | Tier | Drug | Endpoint | Reported | Frozen Code (Display / Unrounded) | Error % (Display / Unrounded) | Outcome (`<=2.0%` Tol) | Source & Finding |
|---|---|---|---|---:|---|---|---|
| H_G1 | `IN_SCOPE_EQUATION` | Gentamicin | `half_life_hr` | 2.3 | `2.32` / `2.3239` | `+0.87%` / `+1.04%` | `PASS` | Bauer 2nd ed. Ch.4 Ex.1 pp.113-116 & Linear Ex.1 pp.134-135 — Also matches Vd=18.2 L (0.00%) and ke=0.2982 vs 0.298 h^-1 (+0.07%) |
| H_G2 | `IN_SCOPE_EQUATION` | Gentamicin | `half_life_hr` | 8.0 | `7.94` / `7.9427` | `-0.75%` / `-0.72%` | `PASS` | Bauer 2nd ed. Ch.4 Ex.2 pp.116-117 — Also matches Vd=18.2 L (0.00%) and ke=0.0872 vs 0.087 h^-1 (+0.23%) |
| H_G3_PK | `IN_SCOPE_EQUATION` | Gentamicin | `half_life_hr` | 2.0 | `1.97` / `1.9746` | `-1.50%` / `-1.27%` | `PASS` | Bauer 2nd ed. Ch.4 Ex.4 pp.119-120 — At Bauer's reported CrCl=115 mL/min, matches Vd=19.76 vs 19.8 L (-0.20%) and ke=0.3509 vs 0.351 h^-1 (-0.03%) |
| H_G4_PK | `IN_SCOPE_EQUATION` | Gentamicin | `half_life_hr` | 4.8 | `4.85` / `4.8489` | `+1.04%` / `+1.02%` | `PASS` | Bauer 2nd ed. Ch.4 Ex.5 p.120 — At Bauer's reported CrCl=44 mL/min, matches ke=0.1429 vs 0.143 h^-1 (-0.07%) and t1/2=4.85 vs 4.8 h (+1.04%) |
| H_V3 | `IN_SCOPE_EQUATION` | Vancomycin | `half_life_hr` | 13.6 | `13.62` / `13.6220` | `+0.15%` / `+0.16%` | `PASS` | Bauer 2nd ed. Ch.5 Trough-Method Ex.1 pp.235-236 — Unseen 55-yr/78-kg/6'1" profile (IBW=79.9 kg); matches Vd=54.6 vs 55 L (-0.73%), k=0.0509 h^-1 (0.00%), and CG CrCl=61.4 vs 61 mL/min |
| H_D4 | `IN_SCOPE_EQUATION` | Digoxin | `maintenance_dose_ug_day` | 125.0 | `125.4` / `125.4096` | `+0.32%` / `+0.33%` | `PASS` | Bauer 2nd ed. Ch.6 Ex.2 pp.315-316 — Unseen atrial fibrillation renal-impairment case (no moderate/severe HF -> ClNR=40 mL/min); CL=72.57 vs 73 mL/min and IV maintenance dose=125.4 vs 125 ug/d |
| H_P1_MM | `IN_SCOPE_EQUATION` | Phenytoin | `vmax_mg_day` | 525.0 | `525.0` / `525.0000` | `+0.00%` / `+0.00%` | `PASS` | Bauer 2nd ed. Ch.10 Ex.1 & Ex.3 pp.503-505 — Unseen 75-kg adult male; matches Vmax=525 mg/d (0.00%) and Vd=52.5 vs rounded 53 L (-0.94%) |
| H_P2_WT_RENAL | `IN_SCOPE_EQUATION` | Phenytoin | `c_corrected_mg_l` | 23.4 | `23.44` / `23.4375` | `+0.17%` / `+0.16%` | `PASS` | Bauer 2nd ed. Ch.10 Ex.2 p.490 — Winter-Tozer severe renal + hypoalbuminaemia (0.1*Alb + 0.1): 23.44 vs 23.4 mg/L (+0.17%) |
| H_G3_E2E_CRCL | `BOUNDARY_DIVERGENCE` | Gentamicin | `half_life_hr` | 2.0 | `2.18` / `2.1823` | `+9.00%` / `+9.12%` | `FAIL_COVARIATE_RULE` | Bauer 2nd ed. Ch.4 Ex.4 pp.119-120 — Exposes overweight-non-obese CG weight rule divergence: 76 kg is 11.1% over IBW (68.4 kg); renal.py uses IBW (CrCl=103.6 vs Bauer's actual-weight 115 mL/min, -9.9%), shifting t1/2 to 2.18 vs 2.0 h (+9.00%) |
| H_G4_E2E_CRCL | `BOUNDARY_DIVERGENCE` | Gentamicin | `half_life_hr` | 4.8 | `5.53` / `5.5290` | `+15.21%` / `+15.19%` | `FAIL_COVARIATE_RULE` | Bauer 2nd ed. Ch.4 Ex.5 p.120 & Ch.5 Ex.4 p.222 — Exposes overweight-non-obese CG weight rule divergence: 80 kg is 17.0% over IBW (68.4 kg); renal.py uses IBW (CrCl=38.0 vs Bauer's actual-weight 44 mL/min, -13.6%), shifting t1/2 to 5.53 vs 4.8 h (+15.21%) |
| H_V4_OBESE | `BOUNDARY_DIVERGENCE` | Vancomycin | `half_life_hr` | 3.4 | `3.73` / `3.7338` | `+9.71%` / `+9.82%` | `FAIL_SALAZAR_GAP` | Bauer 2nd ed. Ch.5 Ex.3 pp.221-222 — Exposes obese CrCl method divergence: at Bauer's Salazar-Corcoran CrCl=184 mL/min vancomycin_pk gives t1/2=3.40 h (0.00%), but end-to-end renal.py uses CG ABW (CrCl=166.8 mL/min, -9.3%), shifting t1/2 to 3.73 vs 3.4 h (+9.71%) |
| H_P1_SALT | `BOUNDARY_DIVERGENCE` | Phenytoin | `dose_mg_day` | 428.0 | `393.8` / `393.7500` | `-7.99%` / `-8.00%` | `FAIL_SALT_FACTOR` | Bauer 2nd ed. Ch.10 Ex.1 & Ex.3 pp.503-505 — Exposes salt-factor boundary: phenytoin_pk computes free-acid dose (393.8 mg/d, S=1.0) without dividing by S=0.92 for phenytoin sodium capsules/injection (428 mg/d reported, -7.99%) |
| H_P3_WT_25C | `BOUNDARY_DIVERGENCE` | Phenytoin | `c_corrected_mg_l` | 11.5 | `13.89` / `13.8889` | `+20.78%` / `+20.77%` | `FAIL_ASSAY_TEMP` | Bauer 2nd ed. Ch.10 Ex.1 p.490 — Exposes Winter-Tozer temperature coefficient boundary: winter_tozer_correction uses 37C factor (0.2*Alb+0.1 -> 13.89 mg/L), whereas Bauer p.490 Ex.1 uses 25C factor (0.25*Alb+0.1 -> 11.5 mg/L, +20.78%) |
| H_P4_PEDIATRIC | `UNSUPPORTED_POPULATION_GATE` | Phenytoin | `abstention_gate` | 240.0 | REJECTED (age<18) | N/A (Abstained) | `PASS_ABSTENTION` | Bauer 2nd ed. Ch.10 Ex.2 & Ex.4 pp.504-505 — 10-yr/40-kg child (paediatric Vmax=9 mg/kg/d, Km=6 mg/L -> 240 mg/d acid): frozen renal.py and batch validator correctly reject age<18 rather than silently applying adult Vmax=7/Km=4 (which would miscalculate 210 mg/d) |

## 3. Prespecified Multi-Domain Comparator Benchmark (`data/heldout_comparator_scenarios.csv`)

### 3A. Task-by-Task Numerators and Denominators (`Correct / Total` Against Prespecified Reference Standard)

| Task Category | Frozen Repaired Prototype (`v0.2.0`) | Pre-Repair Prototype (`5703a7c`) | Static Pair-Only DDI Checker | Single-Drug PK-Only Calculator |
|---|---:|---:|---:|---:|
| Task 1: Joint Renal + DDI Regimen Triage | `6 / 6` | `3 / 6` | `3 / 6` | `2 / 6` |
| Task 2: PETINIA Assay Artifact Separation (`PMID 35541501`) | `3 / 3` | `0 / 3` | `0 / 3` | `0 / 3` |
| Task 3: Caution-Only (`Hepatic`) vs Dose Action Separation | `3 / 3` | `0 / 3` | `1 / 3` | `1 / 3` |
| Task 4: Abstention & Input/Conflict Quarantine (`age<18`, `NaN`, Out-of-KB) | `6 / 6` | `0 / 6` | `0 / 6` | `0 / 6` |
| Task 5: Standalone TDM Non-Finite & Unit/Type Guards | `2 / 2` | `0 / 2` | `0 / 2` | `0 / 2` |
| **Total Across All 20 Prespecified Scenarios** | **`20 / 20` (`100%`)** | **`3 / 20` (`15%`)** | **`4 / 20` (`20%`)** | **`3 / 20` (`15%`)** |

### 3B. Error & Failure-Mode Breakdown Across Comparators (`20` Scenarios)

| Failure Category | Frozen Repaired Prototype (`v0.2.0`) | Pre-Repair Prototype (`5703a7c`) | Static Pair-Only DDI Checker | Single-Drug PK-Only Calculator |
|---|---:|---:|---:|---:|
| Incorrect Reassurance / Missed Clinical Flag | `0 / 20` | `3 / 20` | `7 / 20` | `11 / 20` |
| False Positive DDI Alert / Unwarranted Dose Trigger | `0 / 20` | `7 / 20` | `3 / 20` | `0 / 20` |
| Silent Input Corruption / Unblocked Invalid or Paediatric Input | `0 / 20` | `7 / 20` | `4 / 20` | `4 / 20` |
| Unassessed TDM / Missing Context Guard | `0 / 20` | `0 / 20` | `2 / 20` | `2 / 20` |

### 3C. Scenario-by-Scenario Decisions Across All 4 Systems

| Scenario ID | Task | Reference Standard | Frozen `v0.2.0` | Pre-Repair `5703a7c` | Static DDI-Only | Single-Drug PK-Only |
|---|---|---|---|---|---|---|
| C01_HIGH_DDI_NORM_RENAL | `Task1_Joint_Triage` | `MONITORING_REVIEW_ONLY` | `MONITORING_REVIEW_ONLY` (PASS) | `OVERACTION_CRITICAL_CONTRAINDICATION_DOSE_TRIGGER` (FAIL) | `MONITORING_REVIEW_ONLY` (PASS) | `MISSED_DDI_PAIR` (FAIL) |
| C02_HIGH_DDI_SEV_RENAL | `Task1_Joint_Triage` | `DOSE_AND_MONITORING_REVIEW` | `DOSE_AND_MONITORING_REVIEW` (PASS) | `DOSE_AND_MONITORING_REVIEW` (PASS) | `DDI_ALERT_ONLY_MISSED_RENAL_IMPAIRMENT` (FAIL) | `MISSED_DDI_PAIR` (FAIL) |
| C03_MOD_DDI_NORM_RENAL_1 | `Task1_Joint_Triage` | `MONITORING_REVIEW_ONLY` | `MONITORING_REVIEW_ONLY` (PASS) | `FALSE_REASSURANCE_STANDARD_REGIMEN_ON_MODERATE_DDI` (FAIL) | `MONITORING_REVIEW_ONLY` (PASS) | `MISSED_DDI_PAIR` (FAIL) |
| C04_MOD_DDI_NORM_RENAL_2 | `Task1_Joint_Triage` | `MONITORING_REVIEW_ONLY` | `MONITORING_REVIEW_ONLY` (PASS) | `FALSE_REASSURANCE_STANDARD_REGIMEN_ON_MODERATE_DDI` (FAIL) | `MONITORING_REVIEW_ONLY` (PASS) | `MISSED_DDI_PAIR` (FAIL) |
| C05_NEG_DDI_MOD_RENAL | `Task1_Joint_Triage` | `DOSE_REVIEW_ONLY` | `DOSE_REVIEW_ONLY` (PASS) | `DOSE_REVIEW_ONLY` (PASS) | `NO_ALERT_MISSED_RENAL_IMPAIRMENT` (FAIL) | `DOSE_REVIEW_ONLY` (PASS) |
| C06_SINGLE_DRUG_SEV_RENAL | `Task1_Joint_Triage` | `DOSE_REVIEW_ONLY` | `DOSE_REVIEW_ONLY` (PASS) | `DOSE_REVIEW_ONLY` (PASS) | `NO_ALERT_MISSED_RENAL_IMPAIRMENT` (FAIL) | `DOSE_REVIEW_ONLY` (PASS) |
| C07_ARTIFACT_NORM_RENAL | `Task2_Assay_Artifact` | `ASSAY_ARTIFACT_MONITORING_NOT_DDI` | `ASSAY_ARTIFACT_MONITORING_NOT_DDI` (PASS) | `MISCLASSIFIED_ARTIFACT_AS_CLINICAL_DDI` (FAIL) | `FALSE_DDI_ALERT_ON_ASSAY_ARTIFACT` (FAIL) | `MISSED_ASSAY_ARTIFACT` (FAIL) |
| C08_ARTIFACT_SEV_RENAL | `Task2_Assay_Artifact` | `ASSAY_ARTIFACT_PLUS_RENAL_DOSE_REVIEW` | `ASSAY_ARTIFACT_PLUS_RENAL_DOSE_REVIEW` (PASS) | `MISCLASSIFIED_ARTIFACT_AS_CLINICAL_DDI` (FAIL) | `FALSE_DDI_ALERT_ON_ASSAY_ARTIFACT` (FAIL) | `MISSED_ASSAY_ARTIFACT` (FAIL) |
| C09_ARTIFACT_THREE_DRUG | `Task2_Assay_Artifact` | `TRUE_DDI_PLUS_ASSAY_ARTIFACT_DISTINGUISHED` | `TRUE_DDI_PLUS_ASSAY_ARTIFACT_DISTINGUISHED` (PASS) | `MISCLASSIFIED_ARTIFACT_AS_CLINICAL_DDI` (FAIL) | `FALSE_DDI_ALERT_ON_ASSAY_ARTIFACT` (FAIL) | `MISSED_DDI_PAIR` (FAIL) |
| C10_HEPATIC_CAUTION_SINGLE | `Task3_Caution_vs_Action` | `CAUTION_ONLY_NO_DOSE_CHANGE` | `CAUTION_ONLY_NO_DOSE_CHANGE` (PASS) | `FALSE_DOSE_ADJUSTMENT_FROM_HEPATIC_CAUTION` (FAIL) | `NO_ALERT_MISSED_HEPATIC_CAUTION` (FAIL) | `IGNORED_HEPATIC_STATUS` (FAIL) |
| C11_HEPATIC_CAUTION_NEG_PAIR | `Task3_Caution_vs_Action` | `CAUTION_ONLY_NO_DOSE_CHANGE` | `CAUTION_ONLY_NO_DOSE_CHANGE` (PASS) | `FALSE_DOSE_ADJUSTMENT_FROM_HEPATIC_CAUTION` (FAIL) | `NO_ALERT_MISSED_HEPATIC_CAUTION` (FAIL) | `IGNORED_HEPATIC_STATUS` (FAIL) |
| C12_NEG_SEARCH_NOT_SAFE | `Task3_Caution_vs_Action` | `NO_FLAGS_WITH_SCOPE_CAVEAT` | `NO_FLAGS_WITH_SCOPE_CAVEAT` (PASS) | `FALSE_MONITORING_BADGE_ON_NEGATIVE_PAIR` (FAIL) | `NO_FLAGS_WITH_SCOPE_CAVEAT` (PASS) | `NO_FLAGS_WITH_SCOPE_CAVEAT` (PASS) |
| C13_OUT_OF_KB_DRUG_PAIR | `Task4_Abstention_Input_Guards` | `ABSTAIN_INSUFFICIENT_INFO` | `ABSTAIN_INSUFFICIENT_INFO` (PASS) | `FALSE_REASSURANCE_STANDARD_REGIMEN` (FAIL) | `UNRECOGNIZED_PAIR_NO_ALERT` (FAIL) | `MISSED_DDI_PAIR` (FAIL) |
| C14_UNKNOWN_HEPATIC_STATUS | `Task4_Abstention_Input_Guards` | `ABSTAIN_INSUFFICIENT_INFO` | `ABSTAIN_INSUFFICIENT_INFO` (PASS) | `MAPPED_UNKNOWN_TO_FALSE_STANDARD_REGIMEN` (FAIL) | `IGNORED_UNKNOWN_HEPATIC` (FAIL) | `IGNORED_HEPATIC_STATUS` (FAIL) |
| C15_PEDIATRIC_AGE_REJECT | `Task4_Abstention_Input_Guards` | `REJECT_UNSUPPORTED_AGE` | `REJECT_UNSUPPORTED_AGE` (PASS) | `ACCEPTED_PEDIATRIC_ADULT_EQUATIONS` (FAIL) | `ACCEPTED_NO_AGE_CHECK` (FAIL) | `ACCEPTED_NO_PEDIATRIC_GATE` (FAIL) |
| C16_NAN_CREATININE_REJECT | `Task4_Abstention_Input_Guards` | `REJECT_NONFINITE_INPUT` | `REJECT_NONFINITE_INPUT` (PASS) | `PASSED_INITIAL_VALIDATOR_NAN_OR_HEIGHT` (FAIL) | `ACCEPTED_NO_LAB_CHECK` (FAIL) | `UNHANDLED_NAN_COMPARISON` (FAIL) |
| C17_NONNUMERIC_HEIGHT_REJECT | `Task4_Abstention_Input_Guards` | `REJECT_NONFINITE_INPUT` | `REJECT_NONFINITE_INPUT` (PASS) | `PASSED_INITIAL_VALIDATOR_NAN_OR_HEIGHT` (FAIL) | `ACCEPTED_NO_LAB_CHECK` (FAIL) | `UNHANDLED_NAN_COMPARISON` (FAIL) |
| C18_CONFLICTING_PATIENT_ROWS | `Task4_Abstention_Input_Guards` | `QUARANTINE_CONFLICTING_PATIENT` | `QUARANTINE_CONFLICTING_PATIENT` (PASS) | `SILENT_OVERWRITE_AGE_60` (FAIL) | `NO_PATIENT_DEMOGRAPHIC_CHECK` (FAIL) | `NO_MULTIROW_PATIENT_CHECK` (FAIL) |
| C19_TDM_NAN_VALUE | `Task5_TDM_Context_Guards` | `TDM_INDETERMINATE` | `TDM_INDETERMINATE` (PASS) | `TDM_WITHIN_RANGE_FALSE_REASSURANCE` (FAIL) | `NOT_SUPPORTED_UNFLAGGED` (FAIL) | `NOT_SUPPORTED_UNFLAGGED` (FAIL) |
| C20_TDM_MISSING_TYPE_UNIT | `Task5_TDM_Context_Guards` | `TDM_INDETERMINATE` | `TDM_INDETERMINATE` (PASS) | `TDM_WITHIN_RANGE_FALSE_REASSURANCE` (FAIL) | `NOT_SUPPORTED_UNFLAGGED` (FAIL) | `NOT_SUPPORTED_UNFLAGGED` (FAIL) |
