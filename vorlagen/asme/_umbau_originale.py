"""Macht aus den Word-Originalen (QC-Handbuch) docxtpl-Vorlagen mit Platzhaltern.
Aufruf: python3 umbau.py <entpackt_bestellung> <entpackt_we>"""
import copy
import re
import sys
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
q = lambda tag: f"{{{W}}}{tag}"


def text(el):
    return "".join(t.text or "" for t in el.iter(q("t")))


def saubere_rpr(rpr):
    rpr = copy.deepcopy(rpr) if rpr is not None else etree.Element(q("rPr"))
    for tag in ("rStyle", "color", "noProof", "vanish"):
        for e in rpr.findall(f"w:{tag}", NS):
            rpr.remove(e)
    return rpr


def neuer_run(txt, rpr=None, font=None):
    r = etree.Element(q("r"))
    rp = saubere_rpr(rpr)
    if font:
        for e in rp.findall("w:rFonts", NS):
            rp.remove(e)
        f = etree.Element(q("rFonts"))
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            f.set(q(a), font)
        rp.insert(0, f)
    r.append(rp)
    t = etree.SubElement(r, q("t"))
    t.text = txt
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def erster_rpr(el):
    r = el.find(".//w:r", NS)
    return r.find("w:rPr", NS) if r is not None else None


def ersetze_sdt(sdt, txt):
    """Inhaltssteuerelement (Lauf- oder Zellebene) durch festen Text ersetzen."""
    inhalt = sdt.find("w:sdtContent", NS)
    tc = inhalt.find("w:tc", NS)
    if tc is not None:  # Zelle steckt im Steuerelement
        sdt.getparent().replace(sdt, tc)
        setze_zelle(tc, txt)
        return
    p_in = inhalt.find("w:p", NS)
    if p_in is not None:  # Absatz-Ebene
        rpr = erster_rpr(p_in)
        for r in p_in.findall("w:r", NS):
            p_in.remove(r)
        p_in.append(neuer_run(txt, rpr))
        sdt.getparent().replace(sdt, p_in)
        return
    rpr = erster_rpr(inhalt)
    sdt.getparent().replace(sdt, neuer_run(txt, rpr))


def zerlege_laeufe(p):
    """Jeden Lauf in Einzelläufe (ein Inhaltselement je Lauf) aufteilen,
    damit Feldanfang/-ende sauber getrennt sind."""
    for r in list(p.findall("w:r", NS)):
        kinder = [c for c in r if c.tag != q("rPr")]
        if len(kinder) <= 1:
            continue
        rpr = r.find("w:rPr", NS)
        pos = p.index(r)
        for i, c in enumerate(kinder):
            nr = etree.Element(q("r"))
            if rpr is not None:
                nr.append(copy.deepcopy(rpr))
            nr.append(c)
            p.insert(pos + i, nr)
        p.remove(r)


def felder(p, typ):
    """Liefert je Formularfeld (FORMTEXT/FORMCHECKBOX) die Liste seiner Läufe."""
    zerlege_laeufe(p)
    erg, aktuell, ist_typ = [], None, False
    for r in p.findall("w:r", NS):
        arten = [f.get(q("fldCharType")) for f in r.findall("w:fldChar", NS)]
        it = r.find("w:instrText", NS)
        if "begin" in arten:
            aktuell, ist_typ = [r], False
            continue
        if aktuell is not None:
            aktuell.append(r)
            if it is not None and typ in (it.text or ""):
                ist_typ = True
            if "end" in arten:
                if ist_typ:
                    erg.append(aktuell)
                aktuell = None
    return erg


def ersetze_feld(laeufe, txt, font=None):
    rpr = laeufe[0].find("w:rPr", NS)
    p = laeufe[0].getparent()
    p.insert(p.index(laeufe[0]), neuer_run(txt, rpr, font))
    for r in laeufe:
        p.remove(r)


def setze_zelle(tc, txt, rpr=None):
    p = tc.find("w:p", NS)
    rpr = rpr if rpr is not None else erster_rpr(tc)
    if rpr is None:
        prp = p.find("w:pPr/w:rPr", NS)
        rpr = prp
    for r in p.findall("w:r", NS):
        p.remove(r)
    for extra in tc.findall("w:p", NS)[1:]:
        tc.remove(extra)
    p.append(neuer_run(txt, rpr))
    return p


def absatz_mit(root, start, nur_body=False):
    for p in root.iter(q("p")):
        if text(p).strip().startswith(start):
            return p
    raise ValueError("Absatz nicht gefunden: " + start)


def ersetze_in_t(p, alt, neu):
    """Ersetzt Text auch dann, wenn er über mehrere Läufe verteilt ist
    (Ersatz landet im Lauf, in dem der Text beginnt)."""
    ts = [t for t in p.iter(q("t"))]
    gesamt = "".join(t.text or "" for t in ts)
    start = gesamt.find(alt)
    if start < 0:
        raise ValueError("Text nicht gefunden: " + alt)
    ende = start + len(alt)
    pos = 0
    eingefuegt = False
    for t in ts:
        s = t.text or ""
        a, b = pos, pos + len(s)
        pos = b
        if b <= start or a >= ende:
            continue
        links = s[: max(0, start - a)]
        rechts = s[max(0, ende - a):] if ende < b else ""
        t.text = links + ("" if eingefuegt else neu) + rechts
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        eingefuegt = True


def naechster_absatz(p):
    n = p.getnext()
    while n is not None and n.tag != q("p"):
        n = n.getnext()
    return n


def schreibe(path, tree):
    tree.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)


# ================= Bestellung =================
def bestellung(d):
    path = f"{d}/word/document.xml"
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("w:body", NS)

    p = absatz_mit(root, "Kommission")
    ersetze_feld(felder(p, "FORMTEXT")[0], "{{ kommission }}")
    ersetze_sdt(absatz_mit(root, "Lieferdatum").find(".//w:sdt", NS), "{{ lieferdatum }}")
    ersetze_sdt(absatz_mit(root, "Versand").find(".//w:sdt", NS), "{{ versand }}")
    ersetze_in_t(absatz_mit(root, "Wir bestellen gemäß ASME"), "Sec. VIII Div. 1 Ed. 2025", "{{ asme_edition }}")
    ersetze_sdt(absatz_mit(root, "Spezifikation").find(".//w:sdt", NS), "{{ spezifikationen }}")
    p = absatz_mit(root, "Material nach Sec. II")
    ersetze_sdt(p.find(".//w:sdt", NS), "{{ material_art or werkstoffe }}")
    for f in felder(p, "FORMTEXT"):
        ersetze_feld(f, "{% if material_art and werkstoffe %} ({{ werkstoffe }}){% endif %}")
    ersetze_sdt(absatz_mit(root, "Coded marking").find(".//w:sdt", NS), "{{ coded_marking }}")

    # Ankreuzliste weitere Standards: Feld n gehört zum n-ten Standard im Absatztext
    for p in list(root.iter(q("p"))):
        cbs = felder(p, "FORMCHECKBOX")
        if not cbs:
            continue
        namen = text(p).split()
        assert len(namen) == len(cbs), (namen, len(cbs))
        for f, name in zip(cbs, namen):
            ersetze_feld(f, "{{ std['%s'] }}" % name, font="Segoe UI Symbol")

    # Titel-Auswahl Bestellung/Order -> fest „Bestellung“
    ersetze_sdt(absatz_mit(root, "Bestellung").find(".//w:sdt", NS), "Bestellung")

    # Infobox rechts
    p_nr = absatz_mit(root, "V-xxxxx")
    rpr_wert = erster_rpr(p_nr)
    t_nr = next(t for t in p_nr.iter(q("t")) if "V-xxxxx" in (t.text or ""))
    t_nr.text = "{{ bestell_nr }}"
    for label, ph in (("Datum / Date", "{{ datum }}"), ("Ihr Angebot", "{{ ihr_angebot }}"),
                      ("Ihr Sachbearbeiter", "{{ ihr_sachbearbeiter }}"), ("Unser Zeichen", "{{ unser_zeichen }}")):
        ziel = naechster_absatz(absatz_mit(root, label))
        assert text(ziel).strip() == "", label
        ziel.append(neuer_run(ph, rpr_wert))

    # Anschriftenfeld (Textfeld 79, Choice + Fallback)
    for anchor_doc in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr"):
        pass
    boxen = root.findall(".//w:txbxContent", NS)
    anschrift = [b for b in boxen if "Filtration" not in text(b)]
    assert len(anschrift) == 2, len(anschrift)
    rpr_adr = etree.fromstring(
        f'<w:rPr xmlns:w="{W}"><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>')
    for b in anschrift:
        b.find("w:p", NS).append(neuer_run("{{ lieferant }}", rpr_adr))

    ersetze_sdt(absatz_mit(root, "Zahlungsbedingungen").getparent().find(".//w:sdt", NS) if False else
                next(s for s in root.iter(q("sdt")) if (s.find("w:sdtPr/w:alias", NS) is not None and
                     s.find("w:sdtPr/w:alias", NS).get(q("val")) == "Zahlungsbedingungen")), "{{ zahlungsbedingungen }}")

    # Positionstabelle
    tbl = body.find("w:tbl", NS)
    rows = tbl.findall("w:tr", NS)
    # Zeile 2: Lieferumfang-Zelle steckt im Steuerelement
    for sdt in rows[2].findall("w:sdt", NS):
        ersetze_sdt(sdt, "")
    datenzeile = rows[2]
    zellen = datenzeile.findall("w:tc", NS)
    assert len(zellen) == 5
    rpr_pos = erster_rpr(rows[0])  # Schrift wie Tabellenkopf, aber ohne fett
    rpr_pos = saubere_rpr(rpr_pos)
    for e in rpr_pos.findall("w:b", NS):
        rpr_pos.remove(e)
    for e in rpr_pos.findall("w:sz", NS) + rpr_pos.findall("w:szCs", NS):
        e.set(q("val"), "18")
    setze_zelle(zellen[0], "{{ p.pos }}", rpr_pos)
    setze_zelle(zellen[1], "{{ p.menge_einheit }}", rpr_pos)
    p_bez = setze_zelle(zellen[2], "{{ p.bezeichnung }}{% if p.werkstoff %}\nWerkstoff: {{ p.werkstoff }}{% endif %}", rpr_pos)
    for i, ph in ((3, "{{ p.preis }} €"), (4, "{{ p.gesamt }} €")):
        p_z = setze_zelle(zellen[i], ph, rpr_pos)
        ppr = p_z.find("w:pPr", NS)
        if ppr is None:
            ppr = etree.SubElement(p_z, q("pPr"))
            p_z.insert(0, ppr)
        for j in ppr.findall("w:jc", NS):
            ppr.remove(j)
        jc = etree.Element(q("jc")); jc.set(q("val"), "right")
        ppr.insert(len([c for c in ppr if c.tag in (q("pStyle"), q("keepNext"), q("spacing"), q("ind"))]), jc)
    setze_zelle(rows[1].findall("w:tc", NS)[0], "{%tr for p in positionen %}")
    setze_zelle(rows[3].findall("w:tc", NS)[0], "{%tr endfor %}")
    for r in rows[5:8]:  # überzählige Leerzeilen (Zeile 4 bleibt als Abstand)
        tbl.remove(r)
    for idx, ph in ((8, "{{ summe_netto }} €"), (9, "{{ mwst }} €"), (10, "{{ summe_brutto }} €")):
        z = rows[idx].findall("w:tc", NS)[4]
        for t in z.iter(q("t")):
            if "€" in (t.text or ""):
                t.text = ph
                break
    ersetze_in_t(rows[9], "19", "{{ mwst_satz }}")
    # Summenblock nicht über einen Seitenwechsel trennen
    for r in (rows[4], rows[8], rows[9]):
        for p_ in r.iter(q("p")):
            ppr = p_.find("w:pPr", NS)
            if ppr is None:
                ppr = etree.Element(q("pPr")); p_.insert(0, ppr)
            if ppr.find("w:keepNext", NS) is None:
                ppr.insert(1 if ppr.find("w:pStyle", NS) is not None else 0, etree.Element(q("keepNext")))
    zb = absatz_mit(root, "Zahlungsbedingungen")
    zb_absaetze = [zb]
    n = zb.getnext()
    while n is not None and n.tag == q("p") and n.find("w:pPr/w:framePr", NS) is not None:
        zb_absaetze.append(n)
        n = n.getnext()
    anker = tbl
    for i, za in enumerate(zb_absaetze):
        za.find("w:pPr", NS).remove(za.find("w:pPr/w:framePr", NS))
        if i == 0:
            sp = za.find("w:pPr/w:spacing", NS)
            if sp is None:
                sp = etree.SubElement(za.find("w:pPr", NS), q("spacing"))
            sp.set(q("before"), "360")
        anker.addnext(za)
        anker = za
    # leere Absätze bis „Bitte senden Sie …“ entfernen, dort Seitenumbruch davor
    seite2 = absatz_mit(root, "Bitte senden Sie Ihre Auftragsbestätigung")
    n = anker.getnext()
    while n is not None and n is not seite2:
        nxt = n.getnext()
        if n.tag == q("p") and text(n).strip() == "" and n.find(".//w:drawing", NS) is None and n.find(".//w:sectPr", NS) is None:
            body.remove(n)
        n = nxt
    ppr = seite2.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.Element(q("pPr")); seite2.insert(0, ppr)
    pbb = etree.Element(q("pageBreakBefore"))
    ppr.insert(1 if ppr.find("w:pStyle", NS) is not None else 0, pbb)
    schreibe(path, tree)

    # Kopfzeile Folgeseiten: Bestellnummer
    hpath = f"{d}/word/header1.xml"
    htree = etree.parse(hpath)
    ts = [t for t in htree.iter(q("t"))]
    i = next(i for i, t in enumerate(ts) if t.text == "V-")
    ts[i].text = "{{ bestell_nr }}"
    for t in ts[i + 1:i + 5]:
        assert t.text in ("xxxxx", "/", "xxxx", "/xx"), t.text
        t.text = ""
    schreibe(hpath, htree)


# ================= WE-Kontrollschein =================
def we(d):
    path = f"{d}/word/document.xml"
    tree = etree.parse(path)
    root = tree.getroot()
    body = root.find("w:body", NS)
    tbls = body.findall("w:tbl", NS)
    rows = tbls[1].findall("w:tr", NS)
    zelle = lambda r, c: rows[r].findall("w:tc", NS)[c]
    rpr_wert = etree.fromstring(
        f'<w:rPr xmlns:w="{W}"><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>')
    setze_zelle(zelle(1, 1), "{{ bestell_nr_kommission }}", rpr_wert)
    setze_zelle(zelle(1, 3), "{{ p.pos }}", rpr_wert)
    setze_zelle(zelle(2, 3), "{{ p.stueckliste_pos }}", rpr_wert)
    setze_zelle(zelle(3, 1), "{{ p.bezeichnung }}", rpr_wert)
    setze_zelle(zelle(4, 1), "{{ p.werkstoff }}", rpr_wert)
    setze_zelle(zelle(5, 1), "{{ p.menge_einheit }}", rpr_wert)

    # Je Position eine Seite: Schleife um Kopf- und Formulartabelle,
    # Seitenumbruch ab der zweiten Position im ersten Absatz der Schleife.
    erster = body[0]
    assert erster.tag == q("p")
    pb = f'<w:r xmlns:w="{W}"><w:t xml:space="preserve">{{% if not loop.first %}}</w:t></w:r>'
    erster.append(etree.fromstring(pb))
    br = etree.fromstring(f'<w:r xmlns:w="{W}"><w:br w:type="page"/></w:r>')
    erster.append(br)
    erster.append(etree.fromstring(f'<w:r xmlns:w="{W}"><w:t xml:space="preserve">{{% endif %}}</w:t></w:r>'))
    tag_p = lambda code: etree.fromstring(f'<w:p xmlns:w="{W}"><w:r><w:t xml:space="preserve">{code}</w:t></w:r></w:p>')
    body.insert(0, tag_p("{%p for p in positionen %}"))
    body.insert(body.index(tbls[1]) + 1, tag_p("{%p endfor %}"))
    schreibe(path, tree)


if __name__ == "__main__":
    bestellung(sys.argv[1])
    we(sys.argv[2])
    print("umgebaut")
