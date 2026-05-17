import logging
import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)


def calculate_totals(line_items: list[dict], tax_rate: float) -> dict:
    validated: list[dict] = []
    subtotal = 0.0
    for item in line_items:
        try:
            qty = max(0.0, float(item.get("qty", 0)))
            unit_price = max(0.0, float(item.get("unit_price", 0)))
        except (TypeError, ValueError):
            qty, unit_price = 0.0, 0.0
        item_total = round(qty * unit_price, 2)
        validated.append({**item, "qty": qty, "unit_price": unit_price, "total": item_total})
        subtotal += item_total

    subtotal = round(subtotal, 2)
    tax_amount = round(subtotal * max(0.0, float(tax_rate)), 2)
    total = round(subtotal + tax_amount, 2)
    return {"line_items": validated, "subtotal": subtotal, "tax_amount": tax_amount, "total": total}


def render_invoice_pdf(
    client_info: dict,
    line_items: list[dict],
    invoice_meta: dict,
    subtotal: float,
    tax_amount: float,
    total: float,
    currency: str = "USD",
    branding: str = "",
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("INVOICE", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    meta_rows = [
        ["Invoice #:", invoice_meta.get("invoice_number", "")],
        ["Issue Date:", invoice_meta.get("issue_date", "")],
        ["Due Date:", invoice_meta.get("due_date", "")],
        ["Currency:", currency],
    ]
    meta_table = Table(meta_rows, colWidths=[4 * cm, 11 * cm])
    meta_table.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Bill To", styles["Heading2"]))
    for field in ("name", "address", "email", "tax_id"):
        value = client_info.get(field)
        if value:
            elements.append(Paragraph(str(value), styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Line Items", styles["Heading2"]))
    headers = ["Description", "Qty", f"Unit Price ({currency})", f"Total ({currency})"]
    rows: list[list[str]] = [headers]
    for item in line_items:
        rows.append(
            [
                str(item.get("description", "")),
                str(item.get("qty", 0)),
                f"{float(item.get('unit_price', 0)):.2f}",
                f"{float(item.get('total', 0)):.2f}",
            ]
        )
    rows += [
        ["", "", "Subtotal:", f"{subtotal:.2f}"],
        ["", "", "Tax:", f"{tax_amount:.2f}"],
        ["", "", "Total Due:", f"{total:.2f}"],
    ]
    col_widths = [9 * cm, 2 * cm, 4.5 * cm, 4.5 * cm]
    items_table = Table(rows, colWidths=col_widths)
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4A4A4A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.lightgrey),
                ("LINEABOVE", (2, -3), (-1, -3), 1, colors.grey),
                ("FONTNAME", (2, -3), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (2, -1), (-1, -1), colors.HexColor("#E8F4E8")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(items_table)

    if branding:
        elements.append(Spacer(1, 1 * cm))
        elements.append(Paragraph(branding[:800], styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


# TODO: remade it to s3 buckets
def save_invoice_file(pdf_bytes: bytes, filename: str, storage_dir: str) -> str:
    os.makedirs(storage_dir, exist_ok=True)
    path = os.path.join(storage_dir, filename)
    with open(path, "wb") as fh:
        fh.write(pdf_bytes)
    logger.info("Invoice saved: %s", path)
    return path
