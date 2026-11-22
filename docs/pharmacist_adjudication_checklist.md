# Independent Clinical Pharmacist Adjudication Dossier & Sign-Off Sheet

> **Purpose:** Per peer-review recommendations, all six pairwise interaction records in `data/ddi_knowledge_base.csv` and all five structured UI/PDF badge templates (`ALERT_LABELS` in `src/ddi_engine.py`) require review and sign-off by at least one (preferably two) independent licensed clinical pharmacists before any clinical-readiness claim is made. In the repository, `reviewer_signoff` remains `PENDING pharmacist review` until a human pharmacist completes and signs this sheet.

---

## 1. Displayed Alert Class & Badge Wording Review (`src/ddi_engine.py`)

| Internal `alert_class` | Displayed UI / PDF Badge Text | Trigger Condition (`classify_record`) | Pharmacist Wording Approval (Initials / Notes) |
|---|---|---|---|
| `high_severity_interaction` | `HIGH-SEVERITY INTERACTION: REVIEW REQUIRED` | `interaction_present=YES`, `severity=High` | [ ] Approved / Notes: |
| `moderate_interaction` | `MODERATE INTERACTION: MONITORING REVIEW` | `interaction_present=YES`, `severity=Moderate` | [ ] Approved / Notes: |
| `analytical_interference` | `ASSAY/SPECIMEN LIMITATION: NOT A DRUG INTERACTION` | `interaction_category=analytical_interference` | [ ] Approved / Notes: |
| `no_interaction_found_in_documented_search` | `NO INTERACTION FOUND IN DOCUMENTED SEARCH (NOT PROOF OF SAFETY)` | `interaction_present=NO`, `interaction_category=none` | [ ] Approved / Notes: |
| `not_in_knowledge_base` | `NOT IN KNOWLEDGE BASE: STATUS UNKNOWN` | `pair_found_in_kb=False` | [ ] Approved / Notes: |

---

## 2. Six-Pair Literature & Negative-Search Adjudication Matrix (`data/ddi_knowledge_base.csv`)

### Pair 1: Vancomycin + Gentamicin (`high_severity_interaction`)
- **Stored Fields:** `interaction_present=YES`, `category=pharmacologic`, `type=PD`, `severity=High`.
- **Observed Effect & Mechanism:** Additive risk of acute kidney injury (proximal tubular nephrotoxicity) and ototoxicity; both agents are independently nephrotoxic. *(Software note: the DDI engine does NOT accept a renal input and does not auto-escalate text below any CrCl threshold; renal staging is displayed independently.)*
- **Clinical Recommendation:** `"monitor renal function and serum concentrations of both drugs; clinician to review whether the combination is needed"`
- **Primary Source Verified (`2026-11-22`):** Rybak MJ et al. *Am J Health-Syst Pharm.* 2020;77(11):835-864 (`PMID 32191793`, serious MRSA infection consensus guideline); Bauer LA. *Applied Clinical Pharmacokinetics* 2nd ed. (2008), Ch. 4 p. 109 & Ch. 5 p. 214.
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

### Pair 2: Gentamicin + Digoxin (`moderate_interaction`)
- **Stored Fields:** `interaction_present=YES`, `category=pharmacologic`, `type=PK/PD (mechanism not established)`, `severity=Moderate`.
- **Observed Effect & Mechanism Boundary:** Increased serum digoxin concentration (accompanied by increased serum creatinine) reported in 24 diabetic/congestive heart failure patients receiving digoxin 0.25 mg/day + gentamicin 80 mg IM twice daily for 7 days (vs 12 healthy volunteers). Reduced renal digoxin elimination secondary to gentamicin-associated renal change is a proposed explanation but was not mechanistically isolated. Supporting animal data in rabbits/guinea-pigs/cats.
- **Clinical Recommendation:** `"monitor digoxin concentration and renal function"`
- **Primary Source Verified (`2026-11-22`):** Alkadi HO, Nooman MA, Raja'a YA. *Pharm World Sci.* 2004;26(2):107-109 (`PMID 15085946`); Staneva-Stoytcheva D, Kristeva E, Prodanova K. *Eur J Drug Metab Pharmacokinet.* 1992;17(1):1-8 (`PMID 1323465`).
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

### Pair 3: Phenytoin + Digoxin (`moderate_interaction`)
- **Stored Fields:** `interaction_present=YES`, `category=pharmacologic`, `type=PK (mechanism not established)`, `severity=Moderate`.
- **Observed Effect & Mechanism Boundary:** Open, randomized, single-blind crossover trial in 6 healthy male volunteers at steady state showed digoxin $t_{1/2}$ decreased from 33.9 to 23.7 h and $\text{AUC}_{0-48}$ decreased from 31.6 to 24.4 ng·h/mL. Renal digoxin clearance was unchanged (135.7 vs 120.3 mL/min); assuming unchanged $\beta$-acetyldigoxin absorption, total digoxin clearance increased from 258.6 to 328.3 mL/min. Specific transporter/enzyme causality (e.g., CYP3A4/P-gp) was not established by this study.
- **Clinical Recommendation:** `"monitor digoxin concentration and clinical response"`
- **Primary Source Verified (`2026-11-22`):** Rameis H. *Eur J Clin Pharmacol.* 1985;29(1):49-53 (`PMID 4054206`).
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

### Pair 4: Gentamicin + Phenytoin (`no_interaction_found_in_documented_search`)
- **Stored Fields:** `interaction_present=NO`, `category=none`, `severity=None`.
- **Dated Negative Search Log (`2026-11-22`):**
  1. **PubMed MeSH Query:** `"gentamicins"[MeSH Terms] AND "phenytoin"[MeSH Terms] AND "drug interactions"[MeSH Terms]` -> `2` hits: `PMID 6362953` (Yosselson-Superstine 1984 general review of TDM plasma assay interferences across 8 drugs) and `PMID 6825563` (D'Arcy 1983 compilation of unrelated interaction pairs: azapropazone–phenytoin and gentamicin–furosemide). **0 primary gentamicin–phenytoin interaction studies.**
  2. **PubMed Title/Abstract Query:** `"gentamicin"[Title/Abstract] AND "phenytoin"[Title/Abstract] AND ("interaction*"[Title/Abstract] OR "pharmacokinet*"[Title/Abstract])` -> `16` hits (`PMIDs 22941939, 20508871, 16928154, 15135115, 12739981, 1554952, 2651322, 3820943, 3536257, 3840458, 3882303, 6825563, 7104175, 7282680, 7249607, 7372379`), all multi-drug TDM, hemofiltration sieving, or PK software surveys. **0 primary interaction studies.**
  3. **openFDA Drug Label Query (`api.fda.gov/drug/label.json`):** `openfda.generic_name:phenytoin AND drug_interactions:gentamicin` (`0` hits) and `openfda.generic_name:gentamicin AND drug_interactions:phenytoin` (`0` hits).
- **Clinical Recommendation:** `"no pair-specific action; single-drug monitoring still applies"` (displayed with `NOT PROOF OF SAFETY`).
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

### Pair 5: Vancomycin + Digoxin (`analytical_interference`)
- **Stored Fields:** `interaction_present=NO`, `category=analytical_interference`, `severity=N/A (assay)`.
- **Observed Effect & Causal Unit:** Case report of a 53-year-old patient receiving IV vancomycin and digoxin whose concentrations repeatedly read `<1.1 ug/mL` and `<0.2 ng/mL` on the Abbott particle-enhanced turbidimetric inhibition immunoassay (PETINIA) platform while alternative methods showed toxic concentrations. Investigation implicated elevated patient free kappa light chains (paraprotein turbidity artifact), **not** an in vivo interaction or cross-reactivity caused by co-administering vancomycin and digoxin.
- **Clinical Recommendation:** `"if a result does not fit the clinical picture, ask the laboratory to check for interference or use an alternative method"`
- **Primary Source Verified (`2026-11-22`):** Tang NY, Walewski K, Carey-Ballough R, Sykes E, Sun Q. *Pract Lab Med.* 2022;30:e00277 (`PMID 35541501`).
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

### Pair 6: Vancomycin + Phenytoin (`no_interaction_found_in_documented_search`)
- **Stored Fields:** `interaction_present=NO`, `category=none`, `severity=None`.
- **Dated Negative Search Log (`2026-11-22`):**
  1. **PubMed MeSH Query:** `"vancomycin"[MeSH Terms] AND "phenytoin"[MeSH Terms] AND "drug interactions"[MeSH Terms]` -> `0` hits.
  2. **PubMed Title/Abstract Query:** `"vancomycin"[Title/Abstract] AND "phenytoin"[Title/Abstract] AND ("interaction*"[Title/Abstract] OR "pharmacokinet*"[Title/Abstract] OR "induction"[Title/Abstract])` -> `18` hits (`PMIDs 42132248, 42128896, 41408689, 40529505, 37765152, 35215240, 30559497, 30036982, 29199252, 28911598, 24947446, 22941939, 16928154, 12739981, 1356738, 2660626, 3524955, 10270729`), all general TDM service, teaching, or multi-drug animal liver-flow studies. **0 primary interaction or hepatic-induction studies.**
  3. **openFDA Drug Label Query (`api.fda.gov/drug/label.json`):** `openfda.generic_name:phenytoin AND drug_interactions:vancomycin` (`0` hits) and `openfda.generic_name:vancomycin AND drug_interactions:phenytoin` (`0` hits).
- **Clinical Recommendation:** `"no pair-specific action; single-drug monitoring still applies"` (displayed with `NOT PROOF OF SAFETY`).
- **Reviewer 1 Verdict:** [ ] Agree [ ] Modify: ___________ | **Reviewer 2 Verdict:** [ ] Agree [ ] Modify: ___________

---

## 3. Pharmacist Sign-Off & Disagreement Resolution Log

| Role | Name & Credentials (PharmD / RPh) | Institution & License # | Date Reviewed | Signature |
|---|---|---|---|---|
| **Independent Reviewer 1** | | | | |
| **Independent Reviewer 2** | | | | |
| **Disagreement Resolution** | | | | |
