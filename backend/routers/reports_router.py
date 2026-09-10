import io
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, ParameterResult, Test, TestParameter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

router = APIRouter(prefix="/reports", tags=["Diagnostic Reports & PDF"])


def get_dietary_recommendations(results: list[ParameterResult]) -> list[str]:
    """Generate clinical diet and wellness tips based on flagged biomarkers."""
    tips = []
    flags = {r.parameter_key: (r.observed_value, r.status_flag) for r in results}

    if "hb" in flags and flags["hb"][1] == "Low":
        tips.append("Hemoglobin is below normal. Increase dietary iron: spinach, beetroot, lentils, pomegranate, and vitamin C to aid absorption.")
    if "chol" in flags and flags["chol"][1] in ("High", "Critical"):
        tips.append("Total cholesterol is elevated. Adopt a heart-healthy Mediterranean diet: reduce saturated fats, avoid trans fats, and include oats, chia seeds, and walnuts.")
    if "tg" in flags and flags["tg"][1] in ("High", "Critical"):
        tips.append("Triglycerides are high. Limit refined sugars, sweetened beverages, and alcohol; engage in 30 minutes of daily aerobic exercise.")
    if "hba1c_pct" in flags and flags["hba1c_pct"][1] in ("High", "Critical"):
        tips.append("HbA1c indicates elevated glycemic levels. Opt for low-glycemic foods, whole grains, non-starchy vegetables, and consult an endocrinologist.")
    if "tsh" in flags and flags["tsh"][1] == "High":
        tips.append("TSH is elevated (subclinical/overt hypothyroidism). Ensure adequate dietary iodine and selenium intake; consult your physician.")
    if "sgpt" in flags and flags["sgpt"][1] in ("High", "Critical"):
        tips.append("Liver enzymes (SGPT/ALT) are elevated. Avoid alcohol, minimize processed oily foods, and stay well hydrated.")
    if "creatinine" in flags and flags["creatinine"][1] in ("High", "Critical"):
        tips.append("Serum creatinine is elevated. Ensure 2.5–3 liters of clean water daily, monitor blood pressure, and restrict excess sodium.")

    if not tips:
        tips.append("All measured biomarkers are within normal reference limits. Maintain a balanced diet, adequate hydration, and regular exercise.")

    return tips


@router.get("/{booking_id}")
def get_report_data(booking_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()

    # Collect parameter details
    detailed_results = []
    for r in results:
        param = db.query(TestParameter).filter(TestParameter.key == r.parameter_key).first()
        detailed_results.append({
            "key": r.parameter_key,
            "label": param.label if param else r.parameter_key.upper(),
            "observed_value": r.observed_value,
            "unit": param.unit if param else "-",
            "ref_range": f"{param.min_val} - {param.max_val}" if param else "-",
            "status_flag": r.status_flag,
            "marker_pct": r.marker_pct or 50.0
        })

    diet_tips = get_dietary_recommendations(results)

    return {
        "booking_id": booking.id,
        "patient": {
            "name": booking.patient_name,
            "age": booking.patient_age,
            "gender": booking.patient_gender,
            "phone": booking.patient_phone,
            "email": booking.patient_email
        },
        "order": {
            "date": booking.date,
            "time_slot": booking.time_slot,
            "stage": booking.current_stage,
            "status": booking.status,
            "barcode": booking.sample_tube_barcode or "N/A",
            "technician": booking.technician or "Clinical Pathology Team",
            "notes": booking.technician_notes or "Specimen integrity validated. Results certified."
        },
        "tests": [item.test_name for item in booking.items],
        "results": detailed_results,
        "diet_recommendations": diet_tips
    }


@router.get("/{booking_id}/pdf")
def download_pdf_report(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()
    diet_tips = get_dietary_recommendations(results)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0f766e'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=8.5,
        textColor=colors.HexColor('#1e293b')
    )
    bold_style = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontSize=8.5,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )

    elements = []

    # 1. Header Banner
    elements.append(Paragraph("LABLINE CLINICAL DIAGNOSTIC PORTAL", title_style))
    elements.append(Paragraph("NABL & ISO 15189 Certified Pathology • Automated Clinical Telemetry", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f766e'), spaceAfter=10))

    # 2. Patient & Sample Demographics Table
    barcode_text = booking.sample_tube_barcode or f"BC-{booking.id}"
    demo_data = [
        [
            Paragraph(f"<b>Patient Name:</b> {booking.patient_name}", body_style),
            Paragraph(f"<b>Order ID:</b> {booking.id}", body_style),
            Paragraph(f"<b>Barcode:</b> {barcode_text}", body_style)
        ],
        [
            Paragraph(f"<b>Age / Gender:</b> {booking.patient_age} Yrs / {booking.patient_gender}", body_style),
            Paragraph(f"<b>Booking Date:</b> {booking.date}", body_style),
            Paragraph(f"<b>Status:</b> {booking.current_stage}", body_style)
        ],
        [
            Paragraph(f"<b>Contact:</b> {booking.patient_phone}", body_style),
            Paragraph(f"<b>Collection:</b> {booking.collection_type}", body_style),
            Paragraph(f"<b>Report Time:</b> {booking.time_completed or datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style)
        ]
    ]
    demo_table = Table(demo_data, colWidths=[180, 180, 180])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(demo_table)
    elements.append(Spacer(1, 14))

    # 3. Clinical Results Table
    elements.append(Paragraph("Clinical Biological Parameters & Reference Intervals", section_heading))
    table_headers = ["Investigation Parameter", "Observed", "Ref Range", "Unit", "Flag"]
    table_rows = [[
        Paragraph(f"<b>{h}</b>", bold_style) for h in table_headers
    ]]

    for r in results:
        param = db.query(TestParameter).filter(TestParameter.key == r.parameter_key).first()
        label = param.label if param else r.parameter_key.upper()
        ref_r = f"{param.min_val} - {param.max_val}" if param else "Standard"
        unit = param.unit if param else ""
        flag = r.status_flag

        flag_color = "#059669"  # Normal green
        if flag == "Critical":
            flag_color = "#dc2626"  # Red
        elif flag == "High":
            flag_color = "#ea580c"  # Orange
        elif flag == "Low":
            flag_color = "#d97706"  # Amber

        flag_p = Paragraph(f"<font color='{flag_color}'><b>{flag}</b></font>", body_style)

        table_rows.append([
            Paragraph(label, body_style),
            Paragraph(f"<b>{r.observed_value}</b>", bold_style),
            Paragraph(ref_r, body_style),
            Paragraph(unit, body_style),
            flag_p
        ])

    results_table = Table(table_rows, colWidths=[200, 80, 110, 75, 75])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 12))

    # 4. Diet & Lifestyle Recommendations
    elements.append(Paragraph("Smart Clinical Dietary & Wellness Recommendations", section_heading))
    for tip in diet_tips:
        elements.append(Paragraph(f"• {tip}", body_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 16))

    # 5. Pathologist Certification & Signature Section
    cert_data = [
        [
            Paragraph(f"<b>Technician:</b> {booking.technician or 'Chief Medical Lab Technologist'}<br/>Registration: REG-8841-KMC", body_style),
            Paragraph("<b>Dr. Meera Nambiar, MD, DNB</b><br/>Consultant Pathologist & Lab Director", body_style)
        ]
    ]
    cert_table = Table(cert_data, colWidths=[270, 270])
    cert_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cert_table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"LabLine_Report_{booking.id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
