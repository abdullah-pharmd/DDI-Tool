# Verification Report — Four-Drug PK & DDI Decision-Support Prototype

- **Generated (UTC):** 2026-11-22 03:07:30 UTC
- **Generated (Local):** 2026-11-22 08:07:30
- **Git Branch / Base Commit:** `reviewer-repair-2026-11` (`1c308fb`)
- **Python / Platform:** 3.12.10 (Windows-10-10.0.19045-SP0)
- **Automated Test Suite (`pytest -v`):** `============================= 65 passed in 2.13s ==============================`

## 1. Table 1 Recalculation From Source (`src/validation.py`)

| Case ID | Role | Drug | Endpoint | Reported | Calc (Display) | Calc (Unrounded) | Err % (Display) | Err % (Unrounded) |
|---|---|---|---|---:|---:|---:|---:|---:|
| V1 | development/regression | Vancomycin | half_life_hr | 8.0 | 7.98 | 7.98068 | -0.25000% (-0.25%) | -0.24149% (-0.24%) |
| V2 | calibration/bug-discovery regression | Vancomycin | half_life_hr | 27.0 | 27.11 | 27.11138 | +0.40741% (+0.41%) | +0.41251% (+0.41%) |
| D1 | development/regression | Digoxin | maintenance_dose_ug_day | 288.0 | 287.5 | 287.52365 | -0.17361% (-0.17%) | -0.16540% (-0.17%) |
| D2 | development/regression | Digoxin | maintenance_dose_ug_day | 87.0 | 86.5 | 86.52343 | -0.57471% (-0.57%) | -0.54778% (-0.55%) |

- **Archived Display Endpoints (`7.98/8, 27.11/27, 287.5/288, 86.5/87`):** MAPE = `0.35143%` (`0.35%` at 2 d.p.); MaxAPE = `0.57471%` (`0.57%` at 2 d.p.).
- **Live Unrounded Outputs:** MAPE = `0.34179%` (`0.34%` at 2 d.p.); MaxAPE = `0.54778%` (`0.55%` at 2 d.p.).
- **Excluded Case (`D3_EXCLUDED`):** Primary-page inspection (2026-11-22) of Bauer Ch.6 Example 4 (pp. 316-317: 65-yr, 170-kg female, SCr 4.7 mg/dL, IBW 57 kg, Salazar-Corcoran CrCl 22 mL/min) confirmed `Vd = 288 L` is mathematically exact under the Jusko-Koup renal-dysfunction Vd equation `V = [226 + 298*CrCl/(29.1+CrCl)]*(IBW/70) = 288.50 L` (NOT a textbook erratum); retained in `data/validation_cases.csv` as `EXCLUDED_OUT_OF_MODEL_SCOPE` because `digoxin_pk()` implements only the fixed normal-renal scalar `7.0 L/kg` and `renal.py` does not implement Salazar-Corcoran.

## 2. Knowledge Base Audit (`data/ddi_knowledge_base.csv`)

| ID | Pair | Alert Class | Displayed Label | Severity | Verified | Pharmacist Sign-off | Citation |
|---|---|---|---|---|---|---|---|
| 1 | Vancomycin + Gentamicin | `high_severity_interaction` | HIGH-SEVERITY INTERACTION: REVIEW REQUIRED | High | 2026-11-22 (PubMed PMID 32191793 + Bauer Ch.4 p.109/Ch.5 p.214) | PENDING pharmacist review | Rybak MJ et al. Am J Health-Syst Pharm. 2020;77(11):835-864. PMID 32191793; Bauer LA. Applied Clinical Pharmacokinetics 2nd ed. Ch.4 p.109, Ch.5 p.214 |
| 2 | Gentamicin + Digoxin | `moderate_interaction` | MODERATE INTERACTION: MONITORING REVIEW | Moderate | 2026-11-22 (PubMed abstract) | PENDING pharmacist review | Alkadi HO, Nooman MA, Raja'a YA. Pharm World Sci. 2004;26(2):107-9. PMID 15085946; animal data: Staneva-Stoytcheva D et al. Eur J Drug Metab Pharmacokinet. 1992;17(1):1-8. PMID 1323465 |
| 3 | Phenytoin + Digoxin | `moderate_interaction` | MODERATE INTERACTION: MONITORING REVIEW | Moderate | 2026-11-22 (PubMed abstract) | PENDING pharmacist review | Rameis H. Eur J Clin Pharmacol. 1985;29(1):49-53. PMID 4054206 |
| 4 | Gentamicin + Phenytoin | `no_interaction_found_in_documented_search` | NO INTERACTION FOUND IN DOCUMENTED SEARCH (NOT PROOF OF SAFETY) | None | 2026-11-22 (PubMed MeSH/TIAB + openFDA negative search) | PENDING pharmacist review | PubMed search 2026-11-22: Gentamicins[mh] AND Phenytoin[mh] AND Drug Interactions[mh] (2 hits: general TDM assay review PMID 6362953 & compilation of unrelated pairs PMID 6825563; 0 primary interaction studies); TIAB query (16 hits: 0 interaction studies); openFDA drug_interactions query (0 hits) |
| 5 | Vancomycin + Digoxin | `analytical_interference` | ASSAY/SPECIMEN LIMITATION: NOT A DRUG INTERACTION | N/A (assay) | 2026-11-22 (PubMed abstract) | PENDING pharmacist review | Tang NY, Walewski K, Carey-Ballough R, Sykes E, Sun Q. Pract Lab Med. 2022;30:e00277. PMID 35541501 |
| 6 | Vancomycin + Phenytoin | `no_interaction_found_in_documented_search` | NO INTERACTION FOUND IN DOCUMENTED SEARCH (NOT PROOF OF SAFETY) | None | 2026-11-22 (PubMed MeSH/TIAB + openFDA negative search) | PENDING pharmacist review | PubMed search 2026-11-22: Vancomycin[mh] AND Phenytoin[mh] AND Drug Interactions[mh] (0 hits); TIAB query with induction/pharmacokinet* (18 hits: 0 interaction studies); openFDA drug_interactions query (0 hits); earlier hepatic-induction claim unsupported |

## 3. Adjudicated Synthetic Matrix Consistency (`data/adjudicated_synthetic_cases.csv`)

| Case ID | CrCl (Category) | Drugs | Hepatic | Status Headline | Interaction | Monitoring | Dose Review | Cross-Path Result |
|---|---|---|---|---|---|---|---|---|
| S01_MOD_PAIR_NORM_RENAL | 90.2 (Normal) | Phenytoin, Digoxin | No | MONITORING REVIEW INDICATED | YES | YES | NO | PASS (Screen=PDF=Batch) |
| S02_HIGH_PAIR_NORM_RENAL | 90.2 (Normal) | Vancomycin, Gentamicin | No | MONITORING REVIEW INDICATED | YES | YES | NO | PASS (Screen=PDF=Batch) |
| S03_HIGH_PAIR_SEV_RENAL | 25.0 (Severe) | Vancomycin, Gentamicin | No | DOSE REVIEW INDICATED | YES | YES | YES | PASS (Screen=PDF=Batch) |
| S04_B90_NORMAL | 90.2 (Normal) | Gentamicin, Phenytoin | No | NO FLAGS FROM THE CHECKS PERFORMED | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S05_B89_MILD | 89.3 (Mild) | Gentamicin, Phenytoin | No | NO FLAGS FROM THE CHECKS PERFORMED | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S06_B60_MILD | 60.3 (Mild) | Gentamicin, Phenytoin | No | NO FLAGS FROM THE CHECKS PERFORMED | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S07_B59_MODERATE | 59.5 (Moderate) | Gentamicin, Phenytoin | No | DOSE REVIEW INDICATED | NO | NO | YES | PASS (Screen=PDF=Batch) |
| S08_B30_MODERATE | 30.1 (Moderate) | Gentamicin, Phenytoin | No | DOSE REVIEW INDICATED | NO | NO | YES | PASS (Screen=PDF=Batch) |
| S09_B29_SEVERE | 29.7 (Severe) | Gentamicin, Phenytoin | No | DOSE REVIEW INDICATED | NO | NO | YES | PASS (Screen=PDF=Batch) |
| S10_HEPATIC_CAUTION_ONLY | 90.2 (Normal) | Gentamicin, Phenytoin | Yes | CAUTION NOTED (NO DOSING CHANGE CALCULATED) | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S11_HEPATIC_UNKNOWN | 90.2 (Normal) | Gentamicin, Phenytoin | Unknown | INSUFFICIENT INFORMATION | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S12_ASSAY_ARTIFACT | 90.2 (Normal) | Vancomycin, Digoxin | No | MONITORING REVIEW INDICATED | NO | YES | NO | PASS (Screen=PDF=Batch) |
| S13_NEG_SEARCH_PAIR | 90.2 (Normal) | Vancomycin, Phenytoin | No | NO FLAGS FROM THE CHECKS PERFORMED | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S14_SINGLE_DRUG_VANCO | 90.2 (Normal) | Vancomycin | No | NO FLAGS FROM THE CHECKS PERFORMED | NO | NO | NO | PASS (Screen=PDF=Batch) |
| S15_B50_ABOVE_HIGH | 50.3 (Moderate) | Vancomycin, Gentamicin | No | DOSE REVIEW INDICATED | YES | YES | YES | PASS (Screen=PDF=Batch) |
| S16_B50_BELOW_HIGH | 49.7 (Moderate) | Vancomycin, Gentamicin | No | DOSE REVIEW INDICATED | YES | YES | YES | PASS (Screen=PDF=Batch) |
