from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_pdf(report_text: str, filename: str | Path):
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=A4,
        title="Rapport medical",
    )
    styles = getSampleStyleSheet()
    elements = [Paragraph("Rapport medical final", styles["Title"]), Spacer(1, 18)]

    for line in report_text.splitlines():
        if line.strip():
            elements.append(Paragraph(line, styles["BodyText"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    return filename
