"""
DelayRay Project Executive Risk Brief PDF Generator
Adheres strictly to docs/BUILD_SPEC.md Sections 1 and 8.1.
Uses ReportLab to generate a clean, publication-grade executive brief with
a persistent "Synthetic demo data" banner and advisory notices.
"""

from io import BytesIO
from typing import Dict, Any, List
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_project_risk_brief(data: Dict[str, Any]) -> BytesIO:
    """
    Generates an executive risk brief PDF document in-memory.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    badge_style = ParagraphStyle(
        'SyntheticBadge',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#991B1B'),
        fontName='Helvetica-Bold'
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569')
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=8,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E3A8A')
    )

    story = []

    # 1. Top Header with Synthetic Demo Data Badge
    badge_table_data = [[
        Paragraph("<b>DelayRay</b> | MoSPI PAIMANA Predictive Intelligence System", meta_style),
        Paragraph("<b>DEMO BADGE: SYNTHETIC DEMO DATA ONLY</b>", badge_style)
    ]]
    badge_table = Table(badge_table_data, colWidths=[4.0 * inch, 3.5 * inch])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF2F2')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#FECACA')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 10))

    # 2. Project Title and Basic Header
    proj_id = data.get("project_id", "PRJ-UNKNOWN")
    proj_name = data.get("project_name", "Infrastructure Project")
    story.append(Paragraph(f"{proj_name}", title_style))
    story.append(Paragraph(
        f"<b>Project ID:</b> {proj_id} &nbsp;|&nbsp; "
        f"<b>Sector:</b> {data.get('sector', 'N/A')} &nbsp;|&nbsp; "
        f"<b>Ministry:</b> {data.get('ministry', 'N/A')} &nbsp;|&nbsp; "
        f"<b>State:</b> {data.get('primary_state', 'N/A')}",
        meta_style
    ))
    story.append(Spacer(1, 10))

    # 3. Key Predictive Analytics Cards
    risk_score = data.get("risk_score", 0.0)
    risk_band = data.get("risk_band", "Low")
    var_cr = data.get("value_at_risk_cr", 0.0)
    pred_overrun_pct = data.get("cost_overrun_p50", 0.0)
    pred_delay_mo = data.get("delay_p50", 0.0)
    orig_cost = data.get("original_cost_cr", 0.0)

    band_color = "#22C55E"
    if risk_band == "Critical":
        band_color = "#EF4444"
    elif risk_band == "High":
        band_color = "#F97316"
    elif risk_band == "Moderate":
        band_color = "#EAB308"

    kpi_data = [
        [
            Paragraph("<b>Calibrated Risk Score</b>", meta_style),
            Paragraph("<b>Predicted Cost Overrun</b>", meta_style),
            Paragraph("<b>Projected Schedule Delay</b>", meta_style),
            Paragraph("<b>Value at Risk (VaR)</b>", meta_style)
        ],
        [
            Paragraph(f"<font size=16 color='{band_color}'><b>{risk_score:.1f} / 100</b></font><br/><b>Band: {risk_band}</b>", body_style),
            Paragraph(f"<font size=16 color='#0F172A'><b>+{pred_overrun_pct:.1f}%</b></font><br/>Approved: ₹{orig_cost:,.0f} Cr", body_style),
            Paragraph(f"<font size=16 color='#0F172A'><b>+{pred_delay_mo:.1f} Mo</b></font><br/>P10-P90: [{data.get('delay_p10', 0.0):.0f}, {data.get('delay_p90', 0.0):.0f}] Mo", body_style),
            Paragraph(f"<font size=16 color='#991B1B'><b>₹{var_cr:,.1f} Cr</b></font><br/>At-risk exposure", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[1.85 * inch, 1.85 * inch, 1.85 * inch, 1.95 * inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # 4. As-of Execution Status Table
    story.append(Paragraph("<b>Monitoring & Execution Health (As-Of Snapshot)</b>", h2_style))
    exec_data = [
        ["Metric", "Value", "Metric", "Value"],
        [
            "Sanction Date", str(data.get("sanction_date", "N/A")),
            "Original Completion Date", str(data.get("original_completion_date", "N/A"))
        ],
        [
            "Anticipated Completion", str(data.get("latest_anticipated_date", "N/A")),
            "Time Elapsed %", f"{data.get('time_elapsed_pct', 0.0):.1f}%"
        ],
        [
            "Physical Progress", f"{data.get('latest_physical_progress_pct', 0.0):.1f}%",
            "Cumulative Expenditure", f"₹{data.get('latest_expenditure_cr', 0.0):,.1f} Cr"
        ],
        [
            "Schedule Perf Index (SPI)", f"{data.get('spi', 1.0):.2f}",
            "Cost Efficiency Index", f"{data.get('cost_efficiency', 1.0):.2f}"
        ],
        [
            "Land Handover %", f"{data.get('land_acquisition_pct', 0.0):.1f}%",
            "Statutory Clearance", str(data.get("env_clearance_status", "N/A"))
        ]
    ]
    exec_table = Table(exec_data, colWidths=[2.0 * inch, 1.75 * inch, 2.0 * inch, 1.75 * inch])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 10))

    # 5. Top SHAP Risk Drivers
    story.append(Paragraph("<b>Primary Causal Drivers (SHAP Explainability)</b>", h2_style))
    drivers = data.get("drivers", [])
    if drivers:
        driver_rows = [["Rank", "Feature / Factor", "Impact", "Causal Narrative"]]
        for d in drivers[:5]:
            dir_text = "Increases Risk" if d.get("direction") == "increases_risk" else "Mitigates Risk"
            dir_color = "#DC2626" if d.get("direction") == "increases_risk" else "#16A34A"
            driver_rows.append([
                str(d.get("rank", "-")),
                d.get("display_name", d.get("feature", "N/A")),
                f"<font color='{dir_color}'><b>{dir_text}</b></font>",
                Paragraph(d.get("sentence", ""), body_style)
            ])
        driver_table = Table(driver_rows, colWidths=[0.5 * inch, 2.1 * inch, 1.3 * inch, 3.6 * inch])
        driver_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(driver_table)
    else:
        story.append(Paragraph("No significant SHAP anomaly drivers detected for this asset.", body_style))

    story.append(Spacer(1, 10))

    # 6. Prescriptive Playbook Actions
    story.append(Paragraph("<b>Prescriptive Action Playbook Recommendations</b>", h2_style))
    actions = data.get("recommended_playbook_actions", [])
    if actions:
        act_rows = [["Owner", "Targeted Intervention Action", "Projected Empirical Impact"]]
        for a in actions[:3]:
            act_rows.append([
                Paragraph(f"<b>{a.get('owner_level', 'Project').upper()}</b>", body_style),
                Paragraph(a.get("action", ""), body_style),
                Paragraph(a.get("expected_effect", ""), body_style)
            ])
        act_table = Table(act_rows, colWidths=[1.1 * inch, 3.8 * inch, 2.6 * inch])
        act_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(act_table)
    else:
        story.append(Paragraph("No immediate playbook intervention required at current risk score threshold.", body_style))

    story.append(Spacer(1, 14))

    # 7. Regulatory & Advisory Disclaimer Footer
    footer_text = (
        "<b>ADVISORY & LEGAL DISCLAIMER:</b> This executive risk brief was automatically generated by the "
        "DelayRay AI Early Warning Platform. Predictive scores, confidence intervals, and recommended interventions "
        "are advisory estimates designed to aid administrative prioritization and do not replace formal contractual, "
        "engineering, or financial determinations. All underlying demo datasets are synthetically generated."
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, leading=9, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    buffer.seek(0)
    return buffer
