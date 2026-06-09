from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

DARK = colors.HexColor('#1a1a2e')
ACCENT = colors.HexColor('#2563eb')
LIGHT = colors.HexColor('#f8fafc')
GRAY = colors.HexColor('#64748b')
BORDER = colors.HexColor('#e2e8f0')

def fmt_money(n):
    try:
        v = float(n or 0)
        return f"$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "$ 0,00"

def build_pdf_comprobante(comp: dict, empresa: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=22, textColor=DARK, fontName='Helvetica-Bold', spaceAfter=2)
    sub_style = ParagraphStyle('sub', fontSize=9, textColor=GRAY, fontName='Helvetica')
    label_style = ParagraphStyle('label', fontSize=8, textColor=GRAY, fontName='Helvetica', spaceAfter=1)
    value_style = ParagraphStyle('value', fontSize=10, textColor=DARK, fontName='Helvetica-Bold')
    normal = ParagraphStyle('normal', fontSize=9, textColor=DARK, fontName='Helvetica')
    right_style = ParagraphStyle('right', fontSize=9, textColor=DARK, fontName='Helvetica', alignment=TA_RIGHT)
    total_style = ParagraphStyle('total', fontSize=13, textColor=ACCENT, fontName='Helvetica-Bold', alignment=TA_RIGHT)

    story = []
    page_w = A4[0] - 3*cm

    # ── HEADER ──────────────────────────────────────────────
    header_data = [[
        Paragraph(f"<b>{empresa.get('razon','Mi Empresa')}</b>", ParagraphStyle('h', fontSize=18, textColor=DARK, fontName='Helvetica-Bold')),
        Paragraph(
            f"<b>{comp['tipo'].upper()}</b><br/>"
            f"<font size=22 color='#2563eb'>N° {str(comp.get('numero',1)).zfill(8)}</font>",
            ParagraphStyle('nr', fontSize=9, textColor=DARK, fontName='Helvetica-Bold', alignment=TA_RIGHT)
        )
    ]]
    header_tbl = Table(header_data, colWidths=[page_w*0.55, page_w*0.45])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_tbl)

    emp_info = (
        f"CUIT: {empresa.get('cuit','—')}  |  {empresa.get('condicion_iva','Monotributista')}<br/>"
        f"{empresa.get('direccion','—')}  |  Tel: {empresa.get('telefono','—')}<br/>"
        f"{empresa.get('email','—')}"
    )
    fecha_dt = comp.get('fecha','')
    if isinstance(fecha_dt, datetime):
        fecha_str = fecha_dt.strftime('%d/%m/%Y %H:%M')
    else:
        fecha_str = str(fecha_dt)[:16]

    info_data = [[
        Paragraph(emp_info, sub_style),
        Paragraph(
            f"<b>Fecha:</b> {fecha_str}<br/>"
            f"<b>Forma de pago:</b> {comp.get('forma_pago','Efectivo')}<br/>"
            f"<b>Estado:</b> {comp.get('estado','Pendiente')}",
            ParagraphStyle('inf', fontSize=9, textColor=DARK, fontName='Helvetica', alignment=TA_RIGHT)
        )
    ]]
    info_tbl = Table(info_data, colWidths=[page_w*0.55, page_w*0.45])
    info_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(info_tbl)
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=8, spaceBefore=6))

    # ── CLIENTE ─────────────────────────────────────────────
    story.append(Paragraph("DATOS DEL CLIENTE", ParagraphStyle('sec', fontSize=7, textColor=ACCENT, fontName='Helvetica-Bold', spaceAfter=4)))
    cli_data = [[
        Paragraph(f"<b>{comp.get('cliente_nombre','Consumidor Final')}</b>", value_style),
        Paragraph(comp.get('cliente_cuit',''), normal),
        Paragraph(comp.get('cliente_dir',''), normal),
        Paragraph(comp.get('cliente_iva','Consumidor Final'), sub_style),
    ]]
    cli_tbl = Table(cli_data, colWidths=[page_w*0.35, page_w*0.2, page_w*0.3, page_w*0.15])
    cli_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),LIGHT),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[LIGHT]),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(0,-1),10),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(cli_tbl)
    story.append(Spacer(1, 10))

    # ── ITEMS ────────────────────────────────────────────────
    story.append(Paragraph("DETALLE", ParagraphStyle('sec2', fontSize=7, textColor=ACCENT, fontName='Helvetica-Bold', spaceAfter=4)))
    items_header = ['Código', 'Descripción', 'Cant.', 'P. Unit.', 'Imp.', 'Subtotal']
    items_data = [items_header]
    for it in (comp.get('items') or []):
        qty = float(it.get('qty', 1))
        precio = float(it.get('precio', 0))
        imp_pct = float(it.get('imp_pct', 0))
        subtotal = qty * precio
        items_data.append([
            str(it.get('codigo','')),
            Paragraph(str(it.get('desc','')), ParagraphStyle('d', fontSize=8, fontName='Helvetica')),
            str(int(qty)),
            fmt_money(precio),
            f"{imp_pct:.0f}%" if imp_pct else "—",
            fmt_money(subtotal),
        ])

    col_w = [page_w*0.1, page_w*0.38, page_w*0.07, page_w*0.15, page_w*0.1, page_w*0.2]
    items_tbl = Table(items_data, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (1,-1), 'LEFT'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT]),
        ('GRID', (0,0), (-1,-1), 0.3, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 10))

    # ── TOTALES ──────────────────────────────────────────────
    subtotal = float(comp.get('subtotal', 0))
    desc_pct = float(comp.get('descuento_pct', 0))
    desc_val = float(comp.get('descuento_val', 0))
    imp_val = float(comp.get('impuestos_val', 0))
    total = float(comp.get('total', 0))

    totales_rows = [['Subtotal', fmt_money(subtotal)]]
    if desc_val:
        totales_rows.append([f'Descuento ({desc_pct:.0f}%)', f'- {fmt_money(desc_val)}'])
    for imp in (comp.get('impuestos_detalle') or []):
        totales_rows.append([f"{imp['nombre']} ({imp['pct']:.0f}%)", fmt_money(imp['valor'])])
    totales_rows.append(['TOTAL', fmt_money(total)])

    tot_tbl_data = [[Paragraph(r[0], ParagraphStyle('tr', fontSize=9, fontName='Helvetica-Bold' if r[0]=='TOTAL' else 'Helvetica', alignment=TA_RIGHT)),
                     Paragraph(r[1], ParagraphStyle('tv', fontSize=11 if r[0]=='TOTAL' else 9,
                         fontName='Helvetica-Bold', alignment=TA_RIGHT,
                         textColor=ACCENT if r[0]=='TOTAL' else DARK))]
                    for r in totales_rows]
    tot_tbl = Table(tot_tbl_data, colWidths=[page_w*0.75, page_w*0.25])
    tot_tbl.setStyle(TableStyle([
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tot_tbl)

    # ── OBSERVACIONES ────────────────────────────────────────
    if comp.get('observaciones'):
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
        story.append(Paragraph("OBSERVACIONES", ParagraphStyle('obs_title', fontSize=7, textColor=ACCENT, fontName='Helvetica-Bold', spaceAfter=3)))
        story.append(Paragraph(comp['observaciones'], normal))

    # ── FOOTER ───────────────────────────────────────────────
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Paragraph(
        f"Documento generado por GestiónPro · {empresa.get('razon','')} · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle('ft', fontSize=7, textColor=GRAY, fontName='Helvetica', alignment=TA_CENTER, spaceBefore=4)
    ))

    doc.build(story)
    return buf.getvalue()


def build_pdf_orden(orden: dict, empresa: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    page_w = A4[0] - 3*cm
    normal = ParagraphStyle('n', fontSize=9, fontName='Helvetica')
    story = []

    story.append(Paragraph(f"ORDEN DE COMPRA N° {str(orden.get('numero',1)).zfill(6)}", ParagraphStyle('t', fontSize=16, fontName='Helvetica-Bold', textColor=DARK)))
    story.append(Paragraph(f"Proveedor: <b>{orden.get('proveedor_nombre','—')}</b>  |  Fecha: {str(orden.get('fecha',''))[:10]}  |  Estado: {orden.get('estado','Borrador')}", ParagraphStyle('s', fontSize=9, fontName='Helvetica', textColor=GRAY, spaceBefore=4, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=10))

    header = ['Código', 'Descripción', 'Cantidad', 'Costo Unit.', 'Subtotal']
    rows = [header]
    for it in (orden.get('items') or []):
        qty = float(it.get('qty',1))
        costo = float(it.get('costo',0))
        rows.append([it.get('codigo',''), Paragraph(it.get('desc',''), normal), str(int(qty)), fmt_money(costo), fmt_money(qty*costo)])

    col_w = [page_w*0.1, page_w*0.42, page_w*0.1, page_w*0.18, page_w*0.2]
    tbl = Table(rows, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),DARK), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),8),
        ('ALIGN',(2,0),(-1,-1),'RIGHT'), ('GRID',(0,0),(-1,-1),0.3,BORDER),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),6), ('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(tbl)
    story.append(Spacer(1,8))
    story.append(Paragraph(f"<b>TOTAL: {fmt_money(orden.get('total',0))}</b>", ParagraphStyle('tot', fontSize=12, fontName='Helvetica-Bold', textColor=ACCENT, alignment=TA_RIGHT)))
    if orden.get('observaciones'):
        story.append(Spacer(1,10))
        story.append(Paragraph(f"<b>Obs:</b> {orden['observaciones']}", normal))
    doc.build(story)
    return buf.getvalue()
