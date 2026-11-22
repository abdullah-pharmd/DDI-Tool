# Stage 21 & Reviewer Recalculation — Literature Development/Regression Cases

## Scope Clarification
The four included rows from Bauer LA, *Applied Clinical Pharmacokinetics*, 2nd ed. (`V1`, `V2`, `D1`, `D2`) cover **two drugs** (`Vancomycin`, `Digoxin`), **two renal conditions** (CrCl `97` and `25 mL/min`), **one adult male demographic profile** (`50 yr`, `70 kg`, `5 ft 10 in` / `177.8 cm`), and **two distinct endpoints** (`half_life_hr` for vancomycin; `maintenance_dose_ug_day` via `digoxin_maintenance_dose` for digoxin). Because `V2` exposed a coding defect during development (`0.05 * weight_kg` vs flat `+0.05 mL/min`), these four rows function as **development and regression cases**, not an unseen independent test set. Gentamicin and phenytoin have no comparable worked-case benchmark in this cohort.

## Primary-Page Resolution of Excluded Case `D3_EXCLUDED` (Bauer Ch. 6 Example 4, pp. 316–317)
Primary-page inspection of Bauer (2nd ed., Chapter 6, pp. 316–317) on `2026-11-22` resolved the discrepancy surrounding `D3_EXCLUDED` (`Vd = 288 L`):
- **True Textbook Patient (`Ch. 6 Example 4`, pp. 316–317):** Patient OI is a **65-year-old, 170-kg (`5 ft 5 in` / `165.1 cm`) obese female** with NYHA Class III moderate heart failure and stable `SCr = 4.7 mg/dL` (`IBW = 57 kg`).
- **True Textbook Calculation:** Bauer estimates obese female creatinine clearance via the **Salazar-Corcoran equation** (`CrCl = 22 mL/min`, giving digoxin `CL = 1.303(22) + 20 = 48 mL/min` and IV maintenance dose `56 ug/day`), and computes volume of distribution in renal impairment via the **Jusko-Koup renal-dysfunction $V_d(\text{CrCl})$ formula** (Ch. 6, p. 312 & p. 317):
  $$V = \left(226 + \frac{298 \cdot \text{CrCl}}{29.1 + \text{CrCl}}\right) \cdot \left(\frac{\text{IBW}}{70\text{ kg}}\right) = \left(226 + \frac{298 \cdot 22}{29.1 + 22}\right) \cdot \left(\frac{57}{70}\right) = 288.50\text{ L} \approx 288\text{ L}$$
- **Verdict:** Bauer's reported `288 L` volume is **mathematically exact (NOT a textbook erratum)**. The case cannot be evaluated by `digoxin_pk()` because `src/pk_engine.py` implements only the fixed normal-renal scalar $V_d = 7.0\text{ L/kg} \times \text{IBW}$ (`399.0 L` at `IBW = 57 kg`, whereas an earlier project draft had also misrecorded the patient demographics as a `50-yr, 140-kg, 5 ft 10 in male, SCr 1.0 mg/dL`, yielding `511.0 L` IBW / `980.0 L` TBW) and `src/renal.py` does not implement Salazar-Corcoran obese `CrCl`. Thus `D3_EXCLUDED` is retained in `data/validation_cases.csv` as `EXCLUDED_OUT_OF_MODEL_SCOPE`.

## Recalculated Results (Generated from `src/validation.py`, Unrounded Aggregation)

| Case | Role | Drug | Endpoint | Reported | Calculated (Display) | Calculated (Unrounded) | Error (Display) | Error (Unrounded) | Source |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| V1 | Development/regression | Vancomycin | t1/2 (hr) | 8.0 | 7.98 | 7.98068 | -0.25% | -0.24% | Bauer Ch.5 Ex.1 |
| V2 | Calibration/bug-discovery | Vancomycin | t1/2 (hr) | 27.0 | 27.11 | 27.11138 | +0.41% | +0.41% | Bauer Ch.5 Ex.2 |
| D1 | Development/regression | Digoxin | Maintenance dose (ug/day) | 288.0 | 287.5 | 287.52365 | -0.17% | -0.17% | Bauer Ch.6 Ex.1 |
| D2 | Development/regression | Digoxin | Maintenance dose (ug/day) | 87.0 | 86.5 | 86.52343 | -0.57% | -0.55% | Bauer Ch.6 Ex.3 |

- **Archived display endpoints (`7.98/8`, `27.11/27`, `287.5/288`, `86.5/87`):** Mean absolute percent error = `0.35143%` (`0.35%` at 2 d.p.); Maximum absolute percent error = `0.57471%` (`0.57%` at 2 d.p.).
- **Full-precision unrounded live outputs:** Mean absolute percent error = `0.34179%` (`0.34%` at 2 d.p.); Maximum absolute percent error = `0.54778%` (`0.55%` at 2 d.p.).

## Defect Caught & Locked During Development (`V2`)
Testing against Case `V2` initially showed a `20.3%` error (`V1` showed `4.9%`) because the initial draft entered vancomycin's nonrenal clearance term as a flat `+0.05 mL/min` instead of scaling by patient weight (`0.05 * weight_kg`). Fixing the scaling term reconciled `V2` to `27.11 hr` (`+0.41%`) and is locked by `test_vancomycin_nonrenal_constant_scales_with_weight`.
