from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.medication import Medication


PSF_NAME = "São Carlos II"
ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
PERIOD_IMAGES = {
    "cedo": ASSETS_DIR / "cedo.png",
    "tarde": ASSETS_DIR / "tarde.png",
    "noite": ASSETS_DIR / "noite.png",
}


def export_medications_pdf(file_path: str, medications: list[Medication], patient_name: str = "") -> None:
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        path = path.with_suffix(".pdf")

    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        leftMargin=0.7 * cm,
        rightMargin=0.7 * cm,
        topMargin=0.7 * cm,
        bottomMargin=0.7 * cm,
    )
    styles = getSampleStyleSheet()
    styles["Title"].fontSize = 21
    styles["Title"].alignment = TA_CENTER
    styles["Normal"].fontSize = 12
    styles["Normal"].leading = 14
    cell_style = styles["Normal"]
    emphasis_cell_style = ParagraphStyle(
        "EmphasisCell",
        parent=cell_style,
        fontSize=14,
        leading=16,
        alignment=TA_CENTER,
    )
    meta_style = ParagraphStyle(
        "MetaCentered",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        leading=14,
    )
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.black,
    )
    period_header_style = ParagraphStyle(
        "PeriodHeader",
        parent=header_style,
        fontSize=11,
        leading=12,
    )

    patient = patient_name.strip() or "Não identificado"
    elements = [
        Paragraph("Hora do Remédio", styles["Title"]),
        Paragraph(f"<b>PSF:</b> {_safe(PSF_NAME)} &nbsp;&nbsp; <b>Paciente:</b> {_safe(patient)}", meta_style),
        Spacer(1, 0.25 * cm),
    ]

    header = [
        Paragraph("Medicamento", header_style),
        Paragraph("Dose", header_style),
        Paragraph("Posologia", header_style),
        _period_header("cedo", "Cedo", period_header_style),
        _period_header("tarde", "Tarde", period_header_style),
        _period_header("noite", "Noite", period_header_style),
        Paragraph("Observações", header_style),
    ]
    data = [header]
    for med in medications:
        data.append(
            [
                Paragraph(_safe(med.medicamento), cell_style),
                Paragraph(_safe(med.dose), cell_style),
                Paragraph(_safe(med.posologia_original), cell_style),
                Paragraph(_bold_safe(med.period_text("cedo")), emphasis_cell_style),
                Paragraph(_bold_safe(med.period_text("tarde")), emphasis_cell_style),
                Paragraph(_bold_safe(med.period_text("noite")), emphasis_cell_style),
                Paragraph(_bold_safe(med.observacoes), emphasis_cell_style),
            ]
        )

    table = Table(
        data,
        colWidths=[4.4 * cm, 2.8 * cm, 7.0 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 5.1 * cm],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("LEADING", (0, 0), (-1, -1), 14),
                ("GRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#555555")),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
                ("VALIGN", (3, 1), (5, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (3, 1), (5, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F9FB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
                ("TOPPADDING", (0, 0), (-1, 0), 3),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)


def _period_header(period: str, label: str, header_style: ParagraphStyle) -> Table:
    image_path = PERIOD_IMAGES[period]
    if image_path.exists():
        image = Image(str(image_path), width=1.04 * cm, height=1.04 * cm)
        data = [[image], [Paragraph(label, header_style)]]
    else:
        data = [[Paragraph(label, header_style)]]

    table = Table(data, colWidths=[1.7 * cm])
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _safe(value: str) -> str:
    return (value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bold_safe(value: str) -> str:
    safe = _safe(value)
    return f"<b>{safe}</b>" if safe else ""
