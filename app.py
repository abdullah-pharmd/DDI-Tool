"""
Educational Four-Drug Pharmacokinetic & Drug Interaction Decision Support Prototype
Faculty of Pharmaceutical Sciences | Educational / Research Software Prototype
"""
import html
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from batch_processing import (
    BATCH_NOT_ASSESSED,
    parse_csv_text,
    results_to_csv,
    screen_patient,
    validate_csv_rows,
    group_by_patient,
)
from ddi_engine import (
    ALERT_ANALYTICAL,
    ALERT_HIGH,
    ALERT_LABELS,
    ALERT_MODERATE,
    ALERT_NEGATIVE_SEARCH,
    ALERT_NOT_IN_KB,
    DDIEngine,
    classify_record,
)
from dose_adjustment import assess_regimen, summarize
from pk_engine import (
    digoxin_maintenance_dose,
    digoxin_pk,
    gentamicin_pk,
    phenytoin_pk,
    vancomycin_pk,
)
from renal import crcl_cockcroft_gault, renal_category
from report_generator import generate_report

st.set_page_config(
    page_title="Clinical PK & DDI Prototype",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .hospital-header {
        background: #FFFFFF;
        border-top: 4px solid #1E40AF;
        border-bottom: 1px solid #E2E8F0;
        border-left: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .hospital-subtitle {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #1E40AF;
        margin-bottom: 0.35rem;
    }
    .hospital-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 0.4rem 0;
        line-height: 1.25;
    }
    .hospital-desc {
        font-size: 0.88rem;
        color: #475569;
        margin: 0;
        line-height: 1.5;
    }
    .scope-banner {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        border-left: 4px solid #C2410C;
        border-radius: 6px;
        padding: 0.85rem 1.15rem;
        margin-bottom: 1.25rem;
        font-size: 0.84rem;
        color: #7C2D12;
        line-height: 1.45;
    }
    .card-surface {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .lab-metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 0.75rem;
        margin: 0.75rem 0;
    }
    .lab-metric-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.75rem 0.9rem;
    }
    .lab-metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.25rem;
    }
    .lab-metric-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0F172A;
        font-variant-numeric: tabular-nums;
        line-height: 1.2;
    }
    .lab-metric-unit {
        font-size: 0.75rem;
        font-weight: 500;
        color: #64748B;
        margin-left: 0.2rem;
    }
    .lab-metric-target {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
    }
    .lab-metric-target .lab-metric-label {
        color: #1D4ED8;
    }
    .lab-metric-target .lab-metric-val {
        color: #1E40AF;
    }
    .triage-card {
        background: #FFFFFF;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .triage-high {
        border: 1px solid #FEE2E2;
        border-left: 4px solid #DC2626;
        background: #FFFDFD;
    }
    .triage-mod {
        border: 1px solid #FEF3C7;
        border-left: 4px solid #D97706;
        background: #FFFEF9;
    }
    .triage-artifact {
        border: 1px solid #EDE9FE;
        border-left: 4px solid #7C3AED;
        background: #FCFAFF;
    }
    .triage-none {
        border: 1px solid #CBD5E1;
        border-left: 4px solid #475569;
        background: #F8FAFC;
    }
    .triage-unknown {
        border: 1px solid #E2E8F0;
        border-left: 4px solid #64748B;
        background: #F8FAFC;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .stage-normal { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
    .stage-mild { background: #FEF9C3; color: #854D0E; border: 1px solid #FEF08A; }
    .stage-moderate { background: #FFEDD5; color: #9A3412; border: 1px solid #FED7AA; }
    .stage-severe { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #CBD5E1 !important;
        gap: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.6rem 0.2rem !important;
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1E40AF !important;
        border-bottom: 2px solid #1E40AF !important;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 0.55rem 1.25rem;
        letter-spacing: 0.01em;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hospital-header">
    <div class="hospital-subtitle">Educational / Research Prototype • Four-Drug Scope</div>
    <div class="hospital-title">Pharmacokinetics &amp; Drug-Interaction Decision-Support Prototype</div>
    <div class="hospital-desc">Cockcroft-Gault adult renal staging (1976 / FDA 2020), deterministic pharmacokinetic calculations (Bauer 2nd ed.; Richens &amp; Dunlop 1975), and a 6-pair literature-indexed drug-interaction lookup displayed side-by-side.</div>
</div>
<div class="scope-banner">
    <b>Scope &amp; Boundary Notice:</b> This educational prototype covers four adult medications (Gentamicin, Vancomycin, Digoxin, Phenytoin) and is <b>not clinically validated</b>. It is not valid for acute kidney injury (unstable serum creatinine), dialysis/CRRT, or patients under 18 years. Renal category and drug-pair flags are displayed independently—renal function does not escalate or alter drug-pair text, and no dosing interval is changed automatically. Therapeutic drug monitoring (TDM) is not live-connected in this workstation or batch workflow.
</div>
""", unsafe_allow_html=True)

DRUGS = ["Gentamicin", "Vancomycin", "Digoxin", "Phenytoin"]
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ddi_knowledge_base.csv")
HEPATIC_OPTIONS = {"No": False, "Yes": True, "Unknown": None}

ALERT_STYLE_MAP = {
    ALERT_HIGH: ("triage-high", "background:#FEE2E2; color:#B91C1C; border:1px solid #FECACA;"),
    ALERT_MODERATE: ("triage-mod", "background:#FEF3C7; color:#B45309; border:1px solid #FDE68A;"),
    ALERT_ANALYTICAL: ("triage-artifact", "background:#EDE9FE; color:#6D28D9; border:1px solid #DDD6FE;"),
    ALERT_NEGATIVE_SEARCH: ("triage-none", "background:#E2E8F0; color:#334155; border:1px solid #CBD5E1;"),
    ALERT_NOT_IN_KB: ("triage-unknown", "background:#F1F5F9; color:#475569; border:1px solid #CBD5E1;"),
}

tab_single, tab_batch = st.tabs(["Single Patient Workstation", "Batch Cohort Screening (CSV)"])

# ============================================================
# TAB 1: Single Patient Workstation
# ============================================================
with tab_single:
    col_input, col_renal = st.columns([3, 2])

    with col_input:
        st.markdown("##### 1. Adult Patient Demographics & Intake")
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age (years, adult >= 18)", min_value=18, max_value=120, value=65)
            sex = st.selectbox("Biological Sex", ["male", "female"])
        with c2:
            weight_kg = st.number_input("Total Weight (kg)", min_value=1.0, value=70.0, step=0.5)
            height_cm = st.number_input("Height (cm)", min_value=50.0, value=175.0, step=0.5)
        with c3:
            scr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, value=1.0, step=0.1)
            hepatic_choice = st.selectbox("Hepatic Impairment Status", ["No", "Yes", "Unknown"], index=0)
            hepatic_flag = HEPATIC_OPTIONS[hepatic_choice]

        st.markdown("##### Target Pharmacotherapy")
        selected_drugs = st.multiselect(
            "Select medications for concurrent regimen evaluation",
            DRUGS,
            default=["Vancomycin", "Gentamicin"],
        )

        nyha_class = "I"
        digoxin_css_target = 1.2
        digoxin_route = "IV (F = 1.0)"
        if "Digoxin" in selected_drugs:
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                nyha_class = st.selectbox(
                    "NYHA Heart Failure Class",
                    ["I", "II", "III", "IV"],
                    index=0,
                )
            with dc2:
                digoxin_css_target = st.number_input(
                    "Digoxin Target Css (ng/mL)", min_value=0.4, max_value=2.0, value=1.2, step=0.1
                )
            with dc3:
                digoxin_route = st.selectbox("Digoxin Route", ["IV (F = 1.0)", "Oral tablet (F = 0.7)"])

    try:
        renal_result = crcl_cockcroft_gault(age, weight_kg, height_cm, sex, scr)
        cat_result = renal_category(renal_result["crcl_ml_min"])
        crcl_val = renal_result["crcl_ml_min"]
        category = cat_result["category"]

        stage_class = {
            "Normal": "stage-normal",
            "Mild": "stage-mild",
            "Moderate": "stage-moderate",
            "Severe": "stage-severe",
        }.get(category, "stage-mild")

        with col_renal:
            st.markdown("##### 2. Independent Renal Clearance Staging")
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:1.2rem; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
                <div style="font-size:0.75rem; color:#64748B; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">Estimated Creatinine Clearance</div>
                <div style="font-size:2.2rem; font-weight:800; color:#0F172A; margin:0.25rem 0; font-variant-numeric:tabular-nums;">
                    {crcl_val:.1f} <span style="font-size:1rem; font-weight:500; color:#64748B;">mL/min</span>
                </div>
                <div style="margin: 0.4rem 0 0.8rem 0;">
                    <span class="stage-badge {stage_class}">{html.escape(category)} Renal Category</span>
                </div>
                <div style="font-size:0.8rem; color:#475569; border-top:1px solid #F1F5F9; padding-top:0.6rem; line-height:1.5;">
                    <b>Dosing Weight Basis:</b> {html.escape(renal_result['weight_basis'].capitalize())}<br/>
                    <b>Method:</b> Cockcroft-Gault (1976) | FDA Guidance Staging (evaluated independently from DDI lookup)
                </div>
            </div>
            """, unsafe_allow_html=True)
    except ValueError as e:
        st.error(f"Renal computation error: {e}")
        st.stop()

    st.markdown("---")
    st.markdown("##### 3. Individualized Pharmacokinetic Profile")
    if not selected_drugs:
        st.info("Select one or more medications above to compute deterministic pharmacokinetic parameters.")

    pk_results = {}
    for drug in selected_drugs:
        try:
            if drug == "Gentamicin":
                res = gentamicin_pk(weight_kg, renal_result["crcl_ml_min"], height_cm, sex)
                pk_results[drug] = res
                st.markdown(f"""
                <div class="card-surface">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <span style="font-size:1.05rem; font-weight:700; color:#0F172A;">Gentamicin (One-Compartment Model)</span>
                        <span style="font-size:0.75rem; background:#F1F5F9; color:#475569; padding:0.2rem 0.5rem; border-radius:4px; font-weight:600;">Aminoglycoside</span>
                    </div>
                    <div class="lab-metric-grid">
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Distribution Vol (Vd)</div>
                            <div class="lab-metric-val">{res['vd_l']}<span class="lab-metric-unit">L</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Elimination Rate (ke)</div>
                            <div class="lab-metric-val">{res['ke_per_hr']:.4f}<span class="lab-metric-unit">hr⁻¹</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Systemic Clearance</div>
                            <div class="lab-metric-val">{res['cl_l_hr']:.2f}<span class="lab-metric-unit">L/hr</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Half-Life (t½)</div>
                            <div class="lab-metric-val">{res['half_life_hr']:.2f}<span class="lab-metric-unit">hr</span></div>
                        </div>
                        <div class="lab-metric-box lab-metric-target">
                            <div class="lab-metric-label">Initial Loading Dose</div>
                            <div class="lab-metric-val">{res['loading_dose_mg']:.1f}<span class="lab-metric-unit">mg</span></div>
                        </div>
                    </div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:0.5rem;">
                        <b>Equation Trace:</b> ke = 0.00293 × CrCl + 0.014 | Vd = 0.26 L/kg | {html.escape(res['reference'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif drug == "Vancomycin":
                res = vancomycin_pk(weight_kg, renal_result["crcl_ml_min"], height_cm, sex)
                pk_results[drug] = res
                st.markdown(f"""
                <div class="card-surface">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <span style="font-size:1.05rem; font-weight:700; color:#0F172A;">Vancomycin (Matzke Weight-Adjusted Model)</span>
                        <span style="font-size:0.75rem; background:#F1F5F9; color:#475569; padding:0.2rem 0.5rem; border-radius:4px; font-weight:600;">Glycopeptide</span>
                    </div>
                    <div class="lab-metric-grid">
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Distribution Vol (Vd)</div>
                            <div class="lab-metric-val">{res['vd_l']}<span class="lab-metric-unit">L</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Systemic CL</div>
                            <div class="lab-metric-val">{res['cl_ml_min']:.2f}<span class="lab-metric-unit">mL/min</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Elimination (k)</div>
                            <div class="lab-metric-val">{res['k_per_hr']:.4f}<span class="lab-metric-unit">hr⁻¹</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Half-Life (t½)</div>
                            <div class="lab-metric-val">{res['half_life_hr']:.2f}<span class="lab-metric-unit">hr</span></div>
                        </div>
                        <div class="lab-metric-box lab-metric-target">
                            <div class="lab-metric-label">Target Daily Dose (AUC 500, MRSA scope)</div>
                            <div class="lab-metric-val">{res['daily_dose_mg']:.0f}<span class="lab-metric-unit">mg/day</span></div>
                        </div>
                    </div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:0.5rem;">
                        <b>Equation Trace:</b> CL = 0.695 × CrCl + 0.05 × Wt | AUC24 500 mg·hr/L (serious MRSA infection scope) | {html.escape(res['reference'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif drug == "Digoxin":
                res = digoxin_pk(weight_kg, renal_result["crcl_ml_min"], nyha_class, height_cm, sex)
                f_bio = 1.0 if digoxin_route.startswith("IV") else 0.7
                dose_res = digoxin_maintenance_dose(
                    res["cl_ml_min_unrounded"], css_target_ng_ml=digoxin_css_target, bioavailability=f_bio
                )
                res_with_dose = {**res, "maintenance_dose_ug_day": round(dose_res["dose_ug_per_tau"], 1)}
                pk_results[drug] = res_with_dose
                st.markdown(f"""
                <div class="card-surface">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <span style="font-size:1.05rem; font-weight:700; color:#0F172A;">Digoxin (Jusko-Koup Model)</span>
                        <span style="font-size:0.75rem; background:#F1F5F9; color:#475569; padding:0.2rem 0.5rem; border-radius:4px; font-weight:600;">Cardiac Glycoside (NYHA {html.escape(nyha_class)})</span>
                    </div>
                    <div class="lab-metric-grid">
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Distribution Vol (Vd)</div>
                            <div class="lab-metric-val">{res['vd_l']:.1f}<span class="lab-metric-unit">L</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Total Clearance</div>
                            <div class="lab-metric-val">{res['cl_ml_min']:.2f}<span class="lab-metric-unit">mL/min</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Non-Renal CL</div>
                            <div class="lab-metric-val">{res['cl_nr_used']}<span class="lab-metric-unit">mL/min</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Half-Life (t½)</div>
                            <div class="lab-metric-val">{res['half_life_hr']:.1f}<span class="lab-metric-unit">hr</span></div>
                        </div>
                        <div class="lab-metric-box lab-metric-target">
                            <div class="lab-metric-label">Maintenance Dose (F={f_bio})</div>
                            <div class="lab-metric-val">{res_with_dose['maintenance_dose_ug_day']:.1f}<span class="lab-metric-unit">µg/day</span></div>
                        </div>
                    </div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:0.5rem;">
                        <b>Equation Trace:</b> CL = 1.303 × CrCl + ClNR(NYHA); Dose = Css × CL × τ / F | {html.escape(res['reference'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            elif drug == "Phenytoin":
                css_target = st.number_input(
                    "Target Steady-State Total Css (mg/L, tool window 5.0-25.0)",
                    min_value=5.0, max_value=25.0, value=15.0, step=1.0,
                )
                res = phenytoin_pk(weight_kg, css_target, height_cm, sex)
                pk_results[drug] = res
                st.markdown(f"""
                <div class="card-surface">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                        <span style="font-size:1.05rem; font-weight:700; color:#0F172A;">Phenytoin (Michaelis-Menten Capacity-Limited Kinetics)</span>
                        <span style="font-size:0.75rem; background:#F1F5F9; color:#475569; padding:0.2rem 0.5rem; border-radius:4px; font-weight:600;">Antiepileptic (Total Css scope)</span>
                    </div>
                    <div class="lab-metric-grid">
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Max Velocity (Vmax)</div>
                            <div class="lab-metric-val">{res['vmax_mg_day']:.0f}<span class="lab-metric-unit">mg/day</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Michaelis Const (Km)</div>
                            <div class="lab-metric-val">{res['km_mg_l']}<span class="lab-metric-unit">mg/L</span></div>
                        </div>
                        <div class="lab-metric-box">
                            <div class="lab-metric-label">Target Css</div>
                            <div class="lab-metric-val">{res['css_target_mg_l']}<span class="lab-metric-unit">mg/L</span></div>
                        </div>
                        <div class="lab-metric-box lab-metric-target">
                            <div class="lab-metric-label">Calculated Daily Dose</div>
                            <div class="lab-metric-val">{res['dose_mg_day']:.1f}<span class="lab-metric-unit">mg/day</span></div>
                        </div>
                    </div>
                    <div style="font-size:0.75rem; color:#64748B; margin-top:0.5rem;">
                        <b>Equation Trace:</b> Dose = (Vmax × Css) / (Km + Css) (unbound concentrations highlighted in renal/hepatic disease or hypoalbuminaemia) | {html.escape(res['reference'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except (ValueError, NotImplementedError) as e:
            st.error(f"{drug} parameter calculation: {e}")

    st.markdown("---")
    st.markdown("##### 4. Independent Pairwise Drug-Drug Interaction Lookup (6-Pair Sourced Matrix)")
    ddi_findings = []
    if len(selected_drugs) >= 2:
        try:
            engine = DDIEngine(DATA_PATH)
            ddi_findings = engine.check_all_pairs(selected_drugs)

            for f in ddi_findings:
                alert_class = f.get("alert_class") or classify_record(f)
                badge_label = ALERT_LABELS[alert_class]
                card_class, badge_style = ALERT_STYLE_MAP[alert_class]
                pair_title = f"{html.escape(f['drug_a'])} + {html.escape(f['drug_b'])}"

                if f["pair_found_in_kb"]:
                    st.markdown(f"""
                    <div class="triage-card {card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:0.45rem;">
                            <span style="font-size:1rem; font-weight:700; color:#0F172A;">{pair_title}</span>
                            <span style="font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:4px; {badge_style}">{html.escape(badge_label)}</span>
                        </div>
                        <div style="font-size:0.84rem; color:#334155; line-height:1.45; margin:0.2rem 0;">
                            <b>Category:</b> {html.escape(f.get('interaction_category', ''))} &nbsp;|&nbsp;
                            <b>Severity:</b> {html.escape(f.get('severity', ''))} &nbsp;|&nbsp;
                            <b>Evidence Level:</b> {html.escape(f.get('evidence_level', ''))}
                        </div>
                        <div style="font-size:0.86rem; color:#334155; line-height:1.45; margin:0.2rem 0;"><b>Observed Effect:</b> {html.escape(f.get('effect', ''))}</div>
                        <div style="font-size:0.86rem; color:#334155; line-height:1.45; margin:0.2rem 0;"><b>Proposed / Known Mechanism:</b> {html.escape(f.get('mechanism', ''))}</div>
                        <div style="font-size:0.86rem; color:#334155; line-height:1.45; margin:0.2rem 0;"><b>Clinical Recommendation:</b> {html.escape(f.get('clinical_recommendation', ''))}</div>
                        <div style="font-size:0.78rem; color:#475569; line-height:1.4; margin:0.25rem 0;">
                            <b>Source Population:</b> {html.escape(f.get('source_population', 'N/A'))} &nbsp;|&nbsp;
                            <b>Verification Status:</b> {html.escape(f.get('last_verified', ''))} ({html.escape(f.get('reviewer_signoff', ''))})
                        </div>
                        <div style="font-size:0.75rem; color:#64748B; margin-top:0.35rem;"><b>Reference:</b> {html.escape(f.get('reference', ''))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="triage-card {card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                            <span style="font-size:0.95rem; font-weight:700; color:#334155;">{pair_title}</span>
                            <span style="font-size:0.72rem; font-weight:700; padding:0.2rem 0.55rem; border-radius:4px; {badge_style}">{html.escape(badge_label)}</span>
                        </div>
                        <div style="font-size:0.82rem; color:#475569;">{html.escape(f.get('note', ''))}</div>
                    </div>
                    """, unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("DDI database file not located at expected path.")
    else:
        st.info("Select at least two concurrent medications above to run pairwise lookup.")

    st.markdown("---")
    st.markdown("##### 5. Regimen Review Summary")
    assessment = assess_regimen(
        renal_category=cat_result["category"],
        ddi_findings=ddi_findings,
        tdm_status=None,
        hepatic_flag=hepatic_flag,
    )
    summary = summarize(assessment)

    if assessment["dose_review"]:
        box_bg, box_border, title_col = "#FEF2F2", "#FCA5A5", "#991B1B"
    elif assessment["monitoring_review"] or assessment["cautions"] or assessment["insufficient_information"]:
        box_bg, box_border, title_col = "#FFFBEB", "#FCD34D", "#92400E"
    else:
        box_bg, box_border, title_col = "#F8FAFC", "#CBD5E1", "#334155"

    st.markdown(f"""
    <div style="background:{box_bg}; border:1px solid {box_border}; border-radius:6px; padding:1rem 1.25rem; margin-bottom:0.75rem;">
        <div style="font-size:0.95rem; font-weight:700; color:{title_col}; margin-bottom:0.45rem;">{html.escape(summary['headline'])}</div>
        <div style="font-size:0.83rem; color:#334155; line-height:1.5;">
            <b>Interaction Found:</b> {'YES' if assessment['interaction_found'] else 'NO'} &nbsp;|&nbsp;
            <b>Monitoring Review:</b> {'YES' if assessment['monitoring_review'] else 'NO'} &nbsp;|&nbsp;
            <b>Dose Review:</b> {'YES' if assessment['dose_review'] else 'NO'} &nbsp;|&nbsp;
            <b>Caution Only:</b> {'YES' if assessment['cautions'] else 'NO'} &nbsp;|&nbsp;
            <b>Insufficient Information:</b> {'YES' if assessment['insufficient_information'] else 'NO'} &nbsp;|&nbsp;
            <b>Not Assessed:</b> {html.escape(', '.join(assessment['not_assessed']) or 'None')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    for line in summary["lines"]:
        st.markdown(f"- {line}")
    st.caption(assessment["note"])

    st.markdown("---")
    st.markdown("##### 6. Audit Documentation Export (PDF)")
    st.caption("Generates a timestamped educational/research PDF summary mirroring all inputs, equation traces, DDI cards, and review flags.")

    if st.button("Generate Audited PDF Summary", type="primary"):
        patient_info = {
            "Age": age,
            "Sex": sex,
            "Weight (kg)": weight_kg,
            "Height (cm)": height_cm,
            "SCr (mg/dL)": scr,
            "Hepatic Impairment": hepatic_choice,
            "Medications": ", ".join(selected_drugs),
        }
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            generate_report(
                tmp.name, patient_info, renal_result, cat_result,
                pk_results, ddi_findings, assessment,
            )
            with open(tmp.name, "rb") as f:
                st.download_button(
                    "Download Official PDF Summary",
                    f.read(),
                    file_name=f"Clinical_PK_Report_Pt_{age}_{sex[0].upper()}.pdf",
                    mime="application/pdf",
                )

# ============================================================
# TAB 2: Batch Cohort Screening (CSV Upload)
# ============================================================
with tab_batch:
    st.markdown("##### Cohort Screening (Batch CSV)")
    st.info(
        "Batch screening computes Cockcroft-Gault renal category, pairwise DDI lookup flags, and the "
        "unified regimen review summary only. Drug-specific PK calculations and TDM are NOT executed on "
        "the batch route and are recorded under 'Not assessed' in every output row."
    )

    uploaded_file = st.file_uploader("Upload patient cohort CSV", type=["csv"])

    if uploaded_file is not None:
        csv_text = uploaded_file.getvalue().decode("utf-8")
        rows = parse_csv_text(csv_text)
        errors = validate_csv_rows(rows)

        if errors:
            st.error("Validation failed — inconsistent or invalid records quarantined before grouping:")
            for err in errors:
                st.markdown(f"- {err}")
        else:
            st.success(f"Validated {len(rows)} rows across consistent patient records. Running batch screening...")
            patients = group_by_patient(rows)
            engine = DDIEngine(DATA_PATH)
            results = [screen_patient(pid, p, engine) for pid, p in patients.items()]

            st.dataframe(results, use_container_width=True)
            st.caption(f"Not assessed in batch mode: {', '.join(BATCH_NOT_ASSESSED)}.")
            csv_out = results_to_csv(results)
            st.download_button(
                "Export Processed Cohort Screening Results (CSV)",
                csv_out,
                file_name="cohort_screening_results.csv",
                mime="text/csv",
            )

st.markdown("---")
st.caption(
    "Educational Four-Drug PK & DDI Prototype • Government College University Faisalabad • "
    "Deterministic equations from Bauer (2nd ed.) and Richens & Dunlop (1975); not clinically validated."
)
