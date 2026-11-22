"""
Module — PDF Report Export
Assembles one patient's renal/PK/DDI/regimen-review results into a clearly
labeled educational/research decision-support report. NOT a clinical document.
"""
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ddi_engine import ALERT_LABELS, ALERT_NOT_IN_KB, classify_record
from dose_adjustment import summarize


def generate_report(output_path: str, patient_info: dict, renal_result: dict,
                     cat_result: dict, pk_results: dict, ddi_findings: list,
                     adjustment: dict) -> str:
    """
    Builds a PDF report for one patient. All inputs are the same dicts already
    produced by the renal/pk_engine/ddi_engine/dose_adjustment modules — this
    function only formats, it does not recalculate anything.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"], textColor=colors.HexColor("#8B0000"),
        borderColor=colors.HexColor("#8B0000"), borderWidth=1, borderPadding=8,
        backColor=colors.HexColor("#FFF0F0"),
    )
    story = []

    # ---- Header + disclaimer (first thing on the page, not buried) ----
    story.append(Paragraph("DDI + PK Decision-Support Prototype — Audit Summary", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>EDUCATIONAL / RESEARCH DECISION-SUPPORT PROTOTYPE (FOUR-DRUG SCOPE).</b> "
        "This report is NOT clinically validated and is NOT a substitute for a physician, "
        "pharmacist, official prescribing information, or hospital protocol. Renal and "
        "drug-pair flags are displayed independently; no automatic dosing or interval "
        "changes are performed. Not valid for acute kidney injury, dialysis, or patients "
        "under 18 years.", disclaimer_style))
    story.append(Spacer(1, 16))

    # ---- Patient inputs ----
    story.append(Paragraph("Patient Information", styles["Heading2"]))
    patient_table_data = [[escape(str(k)), escape(str(v))] for k, v in patient_info.items()]
    story.append(_make_table(patient_table_data))
    story.append(Spacer(1, 12))

    # ---- Renal function ----
    story.append(Paragraph("Renal Function", styles["Heading2"]))
    renal_data = [
        ["CrCl (mL/min)", escape(str(renal_result["crcl_ml_min"]))],
        ["Category", escape(str(cat_result["category"]))],
        ["Weight basis", escape(str(renal_result["weight_basis"]))],
        ["Reference", escape(str(renal_result["reference"]))],
    ]
    story.append(_make_table(renal_data))
    story.append(Spacer(1, 12))

    # ---- PK calculations, per drug ----
    story.append(Paragraph("Pharmacokinetic Calculations", styles["Heading2"]))
    if not pk_results:
        story.append(Paragraph("No drug-specific PK outputs included.", styles["Normal"]))
    for drug, result in pk_results.items():
        story.append(Paragraph(f"<b>{escape(str(drug))}</b>", styles["Heading3"]))
        pk_data = [
            [escape(str(k)), escape(str(v))]
            for k, v in result.items()
            if k != "reference" and not k.endswith("_unrounded")
        ]
        story.append(_make_table(pk_data))
        story.append(Paragraph(f"<i>Source: {escape(str(result.get('reference', '')))}</i>", styles["Normal"]))
        story.append(Spacer(1, 8))

    # ---- DDI findings ----
    story.append(Paragraph("Drug-Drug Interaction Assessment", styles["Heading2"]))
    if not ddi_findings:
        story.append(Paragraph("No drug pairs assessed (fewer than 2 drugs selected).",
                                styles["Normal"]))
    for finding in ddi_findings:
        alert_class = finding.get("alert_class") or classify_record(finding)
        badge = ALERT_LABELS.get(alert_class, alert_class)
        pair_title = f"{escape(str(finding['drug_a']))} + {escape(str(finding['drug_b']))}"
        if finding.get("pair_found_in_kb"):
            story.append(Paragraph(
                f"<b>{pair_title}</b> — <b>{escape(badge)}</b><br/>"
                f"Category: {escape(str(finding.get('interaction_category', '')))} | "
                f"Severity: {escape(str(finding.get('severity', '')))}<br/>"
                f"Observed effect: {escape(str(finding.get('effect', '')))}<br/>"
                f"Mechanism / scope: {escape(str(finding.get('mechanism', '')))}<br/>"
                f"Recommendation: {escape(str(finding.get('clinical_recommendation', '')))}<br/>"
                f"Source population: {escape(str(finding.get('source_population', 'N/A')))}<br/>"
                f"Verification: {escape(str(finding.get('last_verified', '')))} "
                f"({escape(str(finding.get('reviewer_signoff', '')))})<br/>"
                f"<i>Reference: {escape(str(finding.get('reference', '')))}</i>",
                styles["Normal"],
            ))
        else:
            not_in_kb_label = ALERT_LABELS[ALERT_NOT_IN_KB]
            story.append(Paragraph(
                f"<b>{pair_title}</b> — <b>{escape(not_in_kb_label)}</b><br/>"
                f"{escape(str(finding.get('note', '')))}",
                styles["Normal"],
            ))
        story.append(Spacer(1, 8))

    # ---- Regimen review summary ----
    story.append(Paragraph("Regimen Review Summary", styles["Heading2"]))
    summary = summarize(adjustment)
    story.append(Paragraph(f"<b>Status: {escape(summary['headline'])}</b>", styles["Normal"]))
    story.append(Spacer(1, 6))
    flag_table = [
        ["Interaction Found", "YES" if adjustment["interaction_found"] else "NO"],
        ["Monitoring Review", "YES" if adjustment["monitoring_review"] else "NO"],
        ["Dose Review", "YES" if adjustment["dose_review"] else "NO"],
        ["Caution Only", "YES" if adjustment["cautions"] else "NO"],
        ["Insufficient Information", "YES" if adjustment["insufficient_information"] else "NO"],
        ["Not Assessed", escape(", ".join(adjustment["not_assessed"]) or "None")],
    ]
    story.append(_make_table(flag_table))
    story.append(Spacer(1, 8))
    for line in summary["lines"]:
        story.append(Paragraph(f"• {escape(line)}", styles["Normal"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{escape(adjustment['note'])}</i>", styles["Normal"]))
    story.append(Spacer(1, 16))

    # ---- References ----
    story.append(Paragraph("References", styles["Heading2"]))
    refs = [
        "Bauer LA. Applied Clinical Pharmacokinetics, 2nd ed. McGraw-Hill; 2008.",
        "Winter ME. Basic Clinical Pharmacokinetics, 5th/6th ed.",
        "Rybak MJ et al. Am J Health-Syst Pharm. 2020;77(11):835-864.",
        "Cockcroft DW, Gault MH. Nephron. 1976;16(1):31-41.",
        "FDA Guidance for Industry, Pharmacokinetics in Patients with Impaired Renal Function.",
        "Alkadi HO, Nooman MA, Raja'a YA. Pharm World Sci. 2004;26(2):107-109. PMID 15085946.",
        "Staneva-Stoytcheva D et al. Eur J Drug Metab Pharmacokinet. 1992;17(1):1-8. PMID 1323465.",
        "Rameis H. Eur J Clin Pharmacol. 1985;29(1):49-53. PMID 4054206.",
        "Tang NY et al. Pract Lab Med. 2022;30:e00277. PMID 35541501.",
    ]
    for ref in refs:
        story.append(Paragraph(f"• {escape(ref)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # ---- Final disclaimer, repeated at the end (not just the top) ----
    story.append(Paragraph(
        "This report was generated by an educational/research prototype tool. It has "
        "not been clinically validated for patient care use. Do not use for actual "
        "treatment decisions without independent verification by a qualified "
        "healthcare professional.", disclaimer_style))

    doc.build(story)
    return output_path


def _make_table(data: list) -> Table:
    t = Table(data, colWidths=[180, 320])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F0F0")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t
