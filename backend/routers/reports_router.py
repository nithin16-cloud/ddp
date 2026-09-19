import os
import io
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, ParameterResult, Test, TestParameter, User, UserRole
from dependencies import require_role

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing

router = APIRouter(prefix="/reports", tags=["Diagnostic Reports & PDF"])


def generate_report_hash(booking_id: str, patient_name: str, tests: list, results: list) -> str:
    """
    Generates an immutable SHA-256 cryptographic digest of certified diagnostic results.
    Canonical representation ensures identical hash regardless of key order.
    """
    canonical_results = []
    for r in sorted(results, key=lambda x: str(x.get('key', ''))):
        obs_val = r.get('observed_value', 0.0)
        flag = r.get('status_flag', 'Normal')
        canonical_results.append(f"{r.get('key')}:{float(obs_val):.2f}:{flag}")

    canonical_payload = (
        f"ISSUER=LABLINE_CLINICAL_PATHOLOGY|"
        f"BOOKING_ID={str(booking_id).strip()}|"
        f"PATIENT={str(patient_name).strip().upper()}|"
        f"TESTS={','.join(sorted([str(t).strip().upper() for t in tests]))}|"
        f"RESULTS={';'.join(canonical_results)}"
    )
    return hashlib.sha256(canonical_payload.encode('utf-8')).hexdigest()



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
    booking_test_ids = [item.test_id for item in booking.items]

    # Collect parameter details scoped to booking tests (Issue #2 fix)
    detailed_results = []
    for r in results:
        param = db.query(TestParameter).filter(
            TestParameter.key == r.parameter_key,
            TestParameter.test_id.in_(booking_test_ids)
        ).first()
        if not param:
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
    test_names = [item.test_name for item in booking.items]

    # Compute SHA-256 cryptographic hash (Issue #12 fix: GET has no DB side-effects)
    computed_hash = generate_report_hash(booking.id, booking.patient_name, test_names, detailed_results)
    report_hash = booking.report_hash or computed_hash
    is_certified = bool(booking.is_certified and booking.report_hash)

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
            "notes": booking.technician_notes or ("Specimen integrity validated. Results certified." if is_certified else "Processing lab results.")
        },
        "tests": test_names,
        "results": detailed_results,
        "diet_recommendations": diet_tips,
        "cryptographic_verification": {
            "sha256_hash": report_hash,
            "is_certified": is_certified,
            "status": "VERIFIED_AUTHENTIC" if is_certified else "PENDING_PATHOLOGY_CERTIFICATION",
            "certified_at": booking.certified_at or (booking.time_completed.strftime("%Y-%m-%d %H:%M") if hasattr(booking.time_completed, 'strftime') else str(booking.time_completed)) if is_certified else None,
            "pathologist": "Dr. Yatish Rao, MD (Lead Pathologist)",
            "issuer": "LabLine Clinical Diagnostics & ISO 15189 Accredited Pathology Network",
            "verification_url": f"/patient/verify.html?id={booking.id}&hash={report_hash[:16]}"
        }
    }


@router.post("/{booking_id}/certify")
def certify_report(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.technician, UserRole.admin))
):
    """
    Explicit Pathology Sign-Off & Cryptographic Report Certification (Issue #12 fix).
    Only authorized Clinical Technicians and Administrators can certify reports.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()
    if not results:
        raise HTTPException(status_code=400, detail="Cannot certify a report with no lab results.")

    test_names = [item.test_name for item in booking.items]
    detailed_results = [
        {"key": r.parameter_key, "observed_value": r.observed_value, "status_flag": r.status_flag}
        for r in results
    ]

    report_hash = generate_report_hash(booking.id, booking.patient_name, test_names, detailed_results)
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M")

    booking.report_hash = report_hash
    booking.is_certified = True
    booking.certified_at = now_str
    booking.current_stage = "Results Certified"
    booking.status = "Completed"
    if not booking.time_completed:
        booking.time_completed = now_dt

    db.commit()
    db.refresh(booking)

    return {
        "success": True,
        "booking_id": booking.id,
        "is_certified": True,
        "certified_at": booking.certified_at,
        "report_hash": booking.report_hash,
        "certified_by": current_user.name,
        "message": f"Report for booking {booking.id} has been cryptographically certified."
    }


class TamperCheckRequest(BaseModel):
    booking_id: str
    patient_name: str
    tests: List[str]
    parameters: List[Dict[str, Any]]
    certified_hash: str


@router.get("/{booking_id}/verify")
def verify_report_authenticity(booking_id: str, db: Session = Depends(get_db)):
    """
    Public verification endpoint to authenticate diagnostic report integrity.
    Verifies that the SHA-256 hash matches the database record.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Report with Order ID '{booking_id}' not found")

    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()
    test_names = [item.test_name for item in booking.items]

    detailed_results = [
        {"key": r.parameter_key, "observed_value": r.observed_value, "status_flag": r.status_flag}
        for r in results
    ]

    current_hash = generate_report_hash(booking.id, booking.patient_name, test_names, detailed_results)
    is_certified = bool(booking.report_hash and booking.is_certified)

    if not is_certified:
        is_valid = False
        verification_status = "UNCERTIFIED_REPORT_PENDING_APPROVAL"
        message = "Notice: This report has not yet been cryptographically certified by a laboratory pathologist."
    else:
        is_valid = (booking.report_hash == current_hash)
        verification_status = "AUTHENTIC_CERTIFIED_REPORT" if is_valid else "TAMPER_DETECTED_INTEGRITY_FAILED"
        message = (
            "Cryptographic signature validated successfully against immutable laboratory records."
            if is_valid
            else "Security Warning: Report parameters differ from certified laboratory records."
        )

    return {
        "booking_id": booking.id,
        "patient_name": booking.patient_name,
        "is_authentic": is_valid,
        "sha256_hash": current_hash,
        "verification_status": verification_status,
        "certified_at": booking.certified_at or (booking.time_completed.strftime("%Y-%m-%d %H:%M") if hasattr(booking.time_completed, 'strftime') else str(booking.time_completed)) if is_certified else None,
        "lead_pathologist": "Dr. Yatish Rao, MD, DNB (Reg: KMC-8841)",
        "accreditation": "ISO 15189:2022 & NABL Certified Pathology Network",
        "tests": test_names,
        "parameters_analyzed": len(results),
        "message": message
    }


@router.post("/tamper-check")
def simulated_tamper_check(payload: TamperCheckRequest):
    """
    Placement demonstration endpoint:
    Compares the original certified hash against an arbitrarily modified parameter set
    to prove cryptographic tamper resistance.
    """
    recalculated_hash = generate_report_hash(
        booking_id=payload.booking_id,
        patient_name=payload.patient_name,
        tests=payload.tests,
        results=payload.parameters
    )

    is_match = (recalculated_hash.lower() == payload.certified_hash.lower())

    return {
        "certified_hash": payload.certified_hash,
        "computed_hash": recalculated_hash,
        "tampered": not is_match,
        "status": "PASS_UNMODIFIED" if is_match else "FAIL_TAMPER_DETECTED",
        "explanation": (
            "Cryptographic integrity confirmed: Hash matches certified digest exactly."
            if is_match
            else "Tamper detected: Changing an observed analyte value or demographic field immediately alters the 256-bit hash digest, invalidating digital verification."
        )
    }


@router.get("/{booking_id}/pdf")
def download_pdf_report(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()
    diet_tips = get_dietary_recommendations(results)
    test_names = [item.test_name for item in booking.items]

    detailed_results = [
        {"key": r.parameter_key, "observed_value": r.observed_value, "status_flag": r.status_flag}
        for r in results
    ]
    report_hash = booking.report_hash or generate_report_hash(booking.id, booking.patient_name, test_names, detailed_results)

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
    elements.append(Spacer(1, 10))

    # 4. Diet & Lifestyle Recommendations
    elements.append(Paragraph("Smart Clinical Dietary & Wellness Recommendations", section_heading))
    for tip in diet_tips:
        elements.append(Paragraph(f"• {tip}", body_style))
        elements.append(Spacer(1, 2))

    elements.append(Spacer(1, 10))

    # 5. Cryptographic QR Verification & Tamper-Proof Signature Box
    frontend_base = os.getenv("FRONTEND_BASE_URL", "http://localhost:5500").rstrip("/")
    qr_drawing = Drawing(55, 55)
    qr_widget = QrCodeWidget(f"{frontend_base}/patient/verify.html?id={booking.id}&hash={report_hash[:16]}")
    qr_widget.barWidth = 55
    qr_widget.barHeight = 55
    qr_widget.qrVersion = 1
    qr_drawing.add(qr_widget)

    crypto_style = ParagraphStyle(
        'CryptoText',
        parent=styles['Normal'],
        fontSize=7.5,
        textColor=colors.HexColor('#334155'),
        leading=9
    )
    hash_style = ParagraphStyle(
        'HashText',
        parent=styles['Normal'],
        fontSize=6.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f766e'),
        leading=8
    )

    crypto_content = [
        Paragraph("<b>DIGITALLY VERIFIED IMMUTABLE REPORT (SHA-256)</b>", crypto_style),
        Spacer(1, 2),
        Paragraph(f"<b>Cryptographic Hash:</b> {report_hash}", hash_style),
        Spacer(1, 2),
        Paragraph("Scan QR code with any smartphone to verify laboratory authenticity. If any biomarker value or patient demographic is altered, verification fails immediately.", crypto_style)
    ]

    crypto_table = Table([[qr_drawing, crypto_content]], colWidths=[65, 475])
    crypto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdfa')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#0f766e')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(crypto_table)
    elements.append(Spacer(1, 12))

    # 6. Pathologist Certification & Signature Section
    cert_data = [
        [
            Paragraph(f"<b>Technician:</b> {booking.technician or 'Chief Medical Lab Technologist'}<br/>Registration: REG-8841-KMC", body_style),
            Paragraph("<b>Dr. Yatish Rao, MD, DNB</b><br/>Consultant Pathologist & Lab Director", body_style)
        ]
    ]
    cert_table = Table(cert_data, colWidths=[270, 270])
    cert_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(cert_table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"LabLine_Report_{booking.id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

