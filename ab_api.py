"""
Auftragsbestätigung als Word-Dokument: Daten stehen schon am Auftrag (Kunde,
Liefertermin, Lieferbedingungen, Positionen …), zusätzlich ein paar nur dafür
gebrauchte Felder (Unser Zeichen, Kundenreferenz, Zahlungsbedingungen,
Kundenadresse, Sprache). "Auftragsbestätigung erzeugen" rendert daraus eine
der beiden Vorlagen vorlagen/auftragsbestaetigung/DE|EN/Auftragsbestaetigung.docx
(docxtpl, komplett deutsch bzw. komplett englisch — bewusst kein zweisprachiges
Dokument) und liefert sie als .docx zum Download.

Layout-Änderungen: nur die Word-Vorlagen anpassen, kein Code — die Platzhalter
({{ ... }}) darin dürfen dabei nicht verändert werden, und beide Sprachvarianten
müssen dieselben Platzhalter/Jinja-Tags enthalten.
"""
import io
import os
from datetime import date

from flask import Blueprint, jsonify, request, send_file
from docxtpl import DocxTemplate

from models import Item
from asme_api import fmt_datum, fmt_zahl, fmt_menge, sicherer_dateiname

bp = Blueprint("ab", __name__, url_prefix="/api")

VORLAGEN_ORDNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vorlagen", "auftragsbestaetigung")


def vorlage_pfad(sprache):
    """Komplett deutsche oder komplett englische Vorlage — bewusst kein
    zweisprachiges Dokument mehr (Entscheidung 21.10.2026)."""
    ordner = "EN" if sprache == "en" else "DE"
    return os.path.join(VORLAGEN_ORDNER, ordner, "Auftragsbestaetigung.docx")


def fmt_euro(wert):
    """€-Betrag wie im Original-Formular ("€ 00,00"-Platzhalter) – leer bleibt leer."""
    formatiert = fmt_zahl(wert)
    return f"€ {formatiert}" if formatiert else ""


def ab_nummer_suffix(kommission):
    """Teil nach "AB-" für die Auftragsbestätigung: die Kommissionsnummer
    bildet sich ihrerseits aus der AB-Nummer (K-01234/26 aus AB 1234/Jahr 26,
    siehe erp_import.py) — das kehrt das nur wieder um, K-01234/26 wird zu
    AB-1234/26. Funktioniert unabhängig vom ERP-Import, da jeder Auftrag eine
    Kommission hat (nicht jeder eine erp_ab_nummer)."""
    if not kommission:
        return ""
    if kommission.startswith("K-0"):
        return kommission[len("K-0"):]
    if kommission.startswith("K-"):
        return kommission[len("K-"):]
    return kommission


def baue_kontext(item):
    positionen = []
    summe = 0.0
    for p in item.positionen:
        gesamt = p.gesamt()
        if gesamt is not None:
            summe += gesamt
        positionen.append({
            "pos": p.position or "",
            "menge_einheit": " ".join(x for x in (fmt_menge(p.menge), p.einheit or "") if x),
            "bezeichnung": p.beschreibung or "",
            "preis": fmt_euro(p.preis_je_einheit),
            "gesamt": fmt_euro(gesamt),
        })
    mwst_anwenden = item.mwst_anwenden if item.mwst_anwenden is not None else True
    mwst_satz = 19.0
    mwst = round(summe * mwst_satz / 100, 2) if mwst_anwenden else 0.0
    # Zwischensumme ("Summe") nur zeigen, wenn sie sich von der Gesamtsumme
    # unterscheidet (MwSt wird aufgeschlagen) UND mehr als eine Position
    # addiert wird — sonst ist sie nur eine Wiederholung der Gesamtsumme bzw.
    # des einzigen Positions-Gesamtbetrags.
    zeige_summe = mwst_anwenden and len(positionen) > 1

    kundenreferenz_zeile = " / ".join(x for x in (
        item.kunden_zeichen, item.kunden_bestellnr, fmt_datum(item.bestelleingang)
    ) if x)
    # Kunden-Adresse: die frei eingetragenen Zeilen (Firma gehört als erste
    # Zeile bereits in dieses Feld, nicht noch einmal aus "Kunde" vorangestellt
    # — sonst erscheint der interne Kurzname doppelt über der vollen Adresse).
    # Nur falls das Feld komplett leer ist, "Kunde" als Notlösung verwenden.
    adresse_zeilen = [x.strip() for x in (item.kunden_adresse or "").split("\n") if x.strip()]
    if not adresse_zeilen and item.kunde:
        adresse_zeilen = [item.kunde]
    # Versandanschrift: eigenes Feld, da sie von der Kundenadresse abweichen
    # kann (andere Lieferadresse, Ansprechpartner vor Ort o.ä.) — ohne eigene
    # Eintragung wird die Kundenadresse übernommen.
    versand_zeilen = [x.strip() for x in (item.versand_adresse or "").split("\n") if x.strip()] or adresse_zeilen

    return {
        "ab_nummer": ab_nummer_suffix(item.kommission),
        "datum": fmt_datum(date.today()),
        "auftrags_nr": item.kommission or "",
        "unser_zeichen": item.unser_zeichen or "",
        "kundenreferenz_zeile": kundenreferenz_zeile,
        "lieferbedingungen": item.lieferbedingungen or "",
        "adresse_zeilen": adresse_zeilen,
        "versand_erste_zeile": versand_zeilen[0] if versand_zeilen else "",
        "versand_weitere_zeilen": versand_zeilen[1:],
        "liefertermin": fmt_datum(item.liefertermin),
        "zahlungsbedingungen": item.zahlungsbedingungen or "30 Tage netto",
        "positionen": positionen,
        "summe_netto": fmt_euro(summe),
        "mwst_anwenden": mwst_anwenden,
        "zeige_summe": zeige_summe,
        "mwst": fmt_euro(mwst),
        "summe_brutto": fmt_euro(summe + mwst),
    }


@bp.route("/items/<int:item_id>/auftragsbestaetigung")
def erzeuge_auftragsbestaetigung(item_id):
    item = Item.query.get_or_404(item_id)
    if item.type != "auftrag":
        return jsonify({"error": "Nur für Aufträge verfügbar."}), 400
    pfad = vorlage_pfad(item.ab_sprache)
    if not os.path.isfile(pfad):
        return jsonify({"error": f"Vorlage fehlt: {os.path.relpath(pfad, os.path.dirname(os.path.abspath(__file__)))}"}), 500

    doc = DocxTemplate(pfad)
    doc.render(baue_kontext(item), autoescape=True)
    puffer = io.BytesIO()
    doc.save(puffer)
    puffer.seek(0)

    suffix = ab_nummer_suffix(item.kommission)
    ab_name = f"AB-{suffix.replace('/', '.')}" if suffix else (item.kommission or "Auftragsbestaetigung")
    dateiname = f"{sicherer_dateiname(ab_name)}.docx"
    return send_file(
        puffer,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=dateiname,
    )
