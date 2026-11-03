"""Baut Versandliste.docx aus dem HETA-Blanko-Briefbogen (Blanco_Querformat.docx,
Querformat A4) auf: Seitengröße auf A3 Querformat, Titel + Tabelle mit
docxtpl-Platzhaltern (Zeilen-Schleife im 3-Zeilen-Muster wie in
vorlagen/auftragsbestaetigung/DE/Auftragsbestaetigung.docx). Aufruf:
./venv/bin/python vorlagen/versandliste/_umbau_original.py (dann Ergebnis per
PDF-Export + Blick ins Original vergleichen, siehe README.md hier)."""
import os

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

HETA_BLAU = RGBColor(0x02, 0x35, 0x60)

ORDNER = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.join(ORDNER, "Blanco_Querformat.docx")
ZIEL = os.path.join(ORDNER, "Versandliste.docx")

SPALTEN = [
    ("liefertermin_de", "Liefertermin", 22),
    ("kommission", "Kommission", 28),
    ("kunde", "Kunde", 48),
    ("lieferumfang", "Lieferumfang", 95),
    ("prioLabel", "Priorität", 20),
    ("statusLabel", "Status", 32),
    ("lieferbedingungen", "Lieferbedingungen", 32),
    ("projektleiter", "Projektleiter", 28),
]


def set_cell_text(cell, text, bold=False, size=10, color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Arial"
    if color:
        run.font.color.rgb = color


def make_marker_row(table, tag_text):
    """Fügt eine Zeile mit genau einer Zelle an, die nur den docxtpl-Steuer-Tag
    enthält (z.B. "{%tr for a in auftraege %}") — wird beim Rendern entfernt,
    siehe docxtpl-Zeilenschleifen-Muster."""
    row = table.add_row()
    # alle bis auf die erste Zelle der Zeile wieder entfernen, damit es wie im
    # Original-Muster (vorlagen/auftragsbestaetigung) eine einzellige Zeile ist
    tr = row._tr
    tcs = tr.findall(qn("w:tc"))
    for tc in tcs[1:]:
        tr.remove(tc)
    set_cell_text(row.cells[0], tag_text, size=1)
    return row


def set_top_border(paragraph, color="023560", size=6):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.makeelement(qn("w:pBdr"), {})
    top = pBdr.makeelement(qn("w:top"), {
        qn("w:val"): "single", qn("w:sz"): str(size), qn("w:space"): "4", qn("w:color"): color,
    })
    pBdr.append(top)
    pPr.append(pBdr)


FOOTER_TEXT = (
    "HETA Verfahrenstechnik GmbH   ·   Gottlieb-Daimler-Straße 7, 35423 Lich, Germany   ·   "
    "Tel. +49 (0) 6404 6677-0   ·   www.heta.de          // Member of PACO GRUPPE"
)


def baue_footer(footer):
    """Ersetzt den Original-Fußzeilen-Inhalt (zwei als EMF-Bild eingebettete
    Textblöcke, media/image2.emf + image3.emf) durch echten, kurzen Text.
    Grund: Das große EMF-Bild (image3.emf) ist in der Vorlage absolut
    positioniert (wp:anchor, positionH relativeFrom="column", positionV
    relativeFrom="page") passend zur ursprünglichen A4-Seitenbreite/-höhe —
    bei A3 verschiebt sich die column-relative Verankerung, während LibreOffice
    das Bild zusätzlich an der alten Position zu rendern scheint: Ergebnis sind
    zwei überlappende, leicht versetzte Kopien des Fußzeilentexts beim
    PDF-Export (getestet 03.11.2026). Da der Bild-Fußzeilentext ohnehin nicht
    live bearbeitbar ist (reine Rastergrafik), lohnt sich ein Fix der
    Verankerung nicht — echter Text ist robuster und zweckmäßig genug für eine
    interne Versand-/Fertigungsliste."""
    footer.is_linked_to_previous = False
    for p in list(footer.paragraphs):
        p._element.getparent().remove(p._element)
    p = footer.add_paragraph()
    set_top_border(p)
    p.paragraph_format.space_before = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(FOOTER_TEXT)
    run.font.size = Pt(8)
    run.font.name = "Arial"
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def main():
    doc = Document(BASIS)

    # --- Seite auf A3 Querformat umstellen (Original ist A4 Querformat) ---
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Mm(420)
    section.page_height = Mm(297)

    baue_footer(section.footer)
    baue_footer(section.first_page_footer)

    # --- Titel + Zeitraum-Zeile im Dokumentkörper (leer in der Vorlage) ---
    # vorhandene leere Absätze im Körper: ersten als Titel verwenden, Rest
    # entfernen (sonst unnötiger Leerraum vor der Tabelle)
    body_paragraphs = doc.paragraphs
    titel_p = body_paragraphs[0] if body_paragraphs else doc.add_paragraph()
    for p in body_paragraphs[1:]:
        p._element.getparent().remove(p._element)
    titel_p.text = ""
    run = titel_p.add_run("Versandliste")
    run.bold = True
    run.font.size = Pt(22)
    run.font.name = "Arial"
    run.font.color.rgb = HETA_BLAU

    sub_p = doc.add_paragraph()
    sub_run = sub_p.add_run("{{ zeitraum_text }}     ·     erzeugt am {{ erzeugt_am }}")
    sub_run.font.size = Pt(11)
    sub_run.font.name = "Arial"
    sub_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    sub_p.paragraph_format.space_after = Pt(14)

    # --- Tabelle ---
    table = doc.add_table(rows=1, cols=len(SPALTEN))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.makeelement(qn("w:tblW"), {qn("w:w"): "0", qn("w:type"): "auto"})
    tblPr.append(tblW)
    borders = tblPr.makeelement(qn("w:tblBorders"), {})
    for kante in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = borders.makeelement(qn(f"w:{kante}"), {
            qn("w:val"): "single", qn("w:sz"): "4", qn("w:space"): "0", qn("w:color"): "BFBFBF",
        })
        borders.append(b)
    tblPr.append(borders)

    header_row = table.rows[0]
    trPr = header_row._tr.get_or_add_trPr()
    trPr.append(trPr.makeelement(qn("w:tblHeader"), {qn("w:val"): "true"}))
    for cell, (_, label, breite_mm) in zip(header_row.cells, SPALTEN):
        cell.width = Mm(breite_mm)
        set_cell_text(cell, label, bold=True, size=10, color=RGBColor(0xFF, 0xFF, 0xFF))
        shd = cell._tc.get_or_add_tcPr().makeelement(qn("w:shd"), {
            qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): "023560",
        })
        cell._tc.get_or_add_tcPr().append(shd)

    make_marker_row(table, "{%tr for a in auftraege %}")

    data_row = table.add_row()
    for cell, (feld, _, breite_mm) in zip(data_row.cells, SPALTEN):
        cell.width = Mm(breite_mm)
        set_cell_text(cell, "{{ a." + feld + " }}", size=10)

    make_marker_row(table, "{%tr endfor %}")

    hinweis_p = doc.add_paragraph()
    hinweis_p.paragraph_format.space_before = Pt(10)
    hinweis_run = hinweis_p.add_run(
        "Nur offene Aufträge (nicht erledigt/archiviert) mit Liefertermin im gewählten Zeitraum. "
        "Live-Ansicht unter /versandliste — dieses PDF ist der Stand zum Erzeugungszeitpunkt."
    )
    hinweis_run.italic = True
    hinweis_run.font.size = Pt(8)
    hinweis_run.font.name = "Arial"
    hinweis_run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

    doc.save(ZIEL)
    print("gespeichert:", ZIEL)


if __name__ == "__main__":
    main()
