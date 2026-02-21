"""Módulo de infraestructura `quotations`."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _currency(value: float | int | Decimal | None) -> str:
    if value is None:
        value = 0
    amount = int(round(float(value), 0))
    return f'${amount:,.0f}'.replace(',', '.')


def _dt(value: str | datetime | None) -> str:
    if value is None:
        return '-'
    if isinstance(value, datetime):
        return value.strftime('%d/%m/%Y')
    try:
        return datetime.fromisoformat(str(value)).strftime('%d/%m/%Y')
    except ValueError:
        return str(value)


def generate_quotation_pdf_bytes(quotation: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 25 * mm
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(20 * mm, y, 'XENITH')
    pdf.setFont('Helvetica', 9)
    pdf.drawString(20 * mm, y - 5 * mm, 'Ingenieria Robotica y Desarrollo de Software')

    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawRightString(width - 20 * mm, y, quotation.get('quotationNumber', 'Cotizacion'))
    pdf.setFont('Helvetica', 9)
    pdf.drawRightString(width - 20 * mm, y - 5 * mm, f"Fecha: {_dt(quotation.get('createdAt'))}")
    pdf.drawRightString(width - 20 * mm, y - 9 * mm, f"Valida hasta: {_dt(quotation.get('validUntil'))}")

    y -= 20 * mm
    client = quotation.get('client') or {}
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(20 * mm, y, 'Cliente')
    pdf.setFont('Helvetica', 9)
    y -= 5 * mm
    pdf.drawString(20 * mm, y, client.get('name') or '-')
    if client.get('company'):
        y -= 4 * mm
        pdf.drawString(20 * mm, y, client['company'])

    y -= 8 * mm
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(20 * mm, y, quotation.get('title') or 'Cotizacion')
    y -= 6 * mm
    pdf.setFont('Helvetica', 9)
    if quotation.get('description'):
        pdf.drawString(20 * mm, y, str(quotation['description'])[:110])
        y -= 6 * mm

    pdf.setFont('Helvetica-Bold', 9)
    pdf.drawString(20 * mm, y, 'Descripcion')
    pdf.drawRightString(width - 60 * mm, y, 'Cantidad')
    pdf.drawRightString(width - 35 * mm, y, 'Unitario')
    pdf.drawRightString(width - 20 * mm, y, 'Total')
    y -= 3 * mm
    pdf.line(20 * mm, y, width - 20 * mm, y)
    y -= 5 * mm

    all_rows: list[dict] = []
    for item in quotation.get('items') or []:
        all_rows.append({'kind': 'item', 'order': item.get('order', 0), 'data': item})
    for group in quotation.get('groups') or []:
        all_rows.append({'kind': 'group', 'order': group.get('order', 0), 'data': group})
    all_rows.sort(key=lambda row: row['order'])

    pdf.setFont('Helvetica', 8)
    for row in all_rows:
        data = row['data']
        description = str(data.get('description') or data.get('name') or '-')[:70]
        if y < 35 * mm:
            pdf.showPage()
            y = height - 25 * mm
            pdf.setFont('Helvetica', 8)

        pdf.drawString(20 * mm, y, description)
        pdf.drawRightString(width - 60 * mm, y, str(data.get('quantity') or 0))
        pdf.drawRightString(width - 35 * mm, y, _currency(data.get('unitPrice')))
        pdf.drawRightString(width - 20 * mm, y, _currency(data.get('total')))
        y -= 5 * mm

    y -= 3 * mm
    pdf.line(width - 70 * mm, y, width - 20 * mm, y)
    y -= 6 * mm
    pdf.setFont('Helvetica', 9)
    pdf.drawRightString(width - 35 * mm, y, 'Subtotal:')
    pdf.drawRightString(width - 20 * mm, y, _currency(quotation.get('subtotal')))
    y -= 5 * mm
    pdf.drawRightString(width - 35 * mm, y, 'Impuestos:')
    pdf.drawRightString(width - 20 * mm, y, _currency(quotation.get('tax')))
    y -= 5 * mm
    pdf.drawRightString(width - 35 * mm, y, 'Descuento:')
    pdf.drawRightString(width - 20 * mm, y, _currency(quotation.get('discount')))
    y -= 7 * mm
    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawRightString(width - 35 * mm, y, 'TOTAL:')
    pdf.drawRightString(width - 20 * mm, y, _currency(quotation.get('total')))

    if quotation.get('notes'):
        y -= 12 * mm
        pdf.setFont('Helvetica-Bold', 9)
        pdf.drawString(20 * mm, y, 'Notas:')
        y -= 5 * mm
        pdf.setFont('Helvetica', 8)
        pdf.drawString(20 * mm, y, str(quotation['notes'])[:130])

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
