"""
Auftragsbestätigung als Word-Dokument: Daten stehen schon am Auftrag (Kunde,
Liefertermin, Lieferbedingungen, Positionen …), zusätzlich ein paar nur dafür
gebrauchte Felder (Unser Zeichen, Kundenreferenz, Zahlungsbedingungen,
Kundenadresse). "Auftragsbestätigung erzeugen" rendert daraus die Vorlage
vorlagen/auftragsbestaetigung/Auftragsbestaetigung.docx (docxtpl) und liefert
sie als .docx zum Download.

Layout-Änderungen: nur die Word-Vorlage anpassen, kein Code — die Platzhalter
({{ ... }}) darin dürfen dabei nicht verändert werden.
"""
import io
import os
from datetime import date

from flask import Blueprint, jsonify, request, send_file
from docxtpl import DocxTemplate

from models import Item
from asme_api import fmt_datum, fmt_zahl, fmt_menge, sicherer_dateiname

bp = Blueprint("ab", __name__, url_prefix="/api")

VORLAGE_PFAD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vorlagen", "auftragsbestaetigung", "Auftragsbestaetigung.docx"
)


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
            "preis": fmt_zahl(p.preis_je_einheit) if p.preis_je_einheit is not None else "",
            "gesamt": fmt_zahl(gesamt) if gesamt is not None else "",
        })
    mwst_satz = 19.0
    mwst = round(summe * mwst_satz / 100, 2)

    kundenreferenz_zeile = " / ".join(x for x in (
        item.kunden_zeichen, item.kunden_bestellnr, fmt_datum(item.bestelleingang)
    ) if x)
    versandanschrift = ", ".join(
        x.strip() for x in ((item.kunde or ""), (item.kunden_adresse or "").replace("\n", ", ")) if x.strip()
    )

    return {
        "ab_nummer": ab_nummer_suffix(item.kommission),
        "datum": fmt_datum(date.today()),
        "auftrags_nr": item.kommission or "",
        "unser_zeichen": item.unser_zeichen or "",
        "kundenreferenz_zeile": kundenreferenz_zeile,
        "lieferbedingungen": item.lieferbedingungen or "",
        "versandanschrift": versandanschrift,
        "liefertermin": fmt_datum(item.liefertermin),
        "zahlungsbedingungen": item.zahlungsbedingungen or "30 Tage netto",
        "positionen": positionen,
        "summe_netto": fmt_zahl(summe),
        "mwst": fmt_zahl(mwst),
        "summe_brutto": fmt_zahl(summe + mwst),
    }


@bp.route("/items/<int:item_id>/auftragsbestaetigung")
def erzeuge_auftragsbestaetigung(item_id):
    item = Item.query.get_or_404(item_id)
    if item.type != "auftrag":
        return jsonify({"error": "Nur für Aufträge verfügbar."}), 400
    if not os.path.isfile(VORLAGE_PFAD):
        return jsonify({"error": "Vorlage fehlt: vorlagen/auftragsbestaetigung/Auftragsbestaetigung.docx"}), 500

    doc = DocxTemplate(VORLAGE_PFAD)
    doc.render(baue_kontext(item), autoescape=True)
    puffer = io.BytesIO()
    doc.save(puffer)
    puffer.seek(0)

    suffix = ab_nummer_suffix(item.kommission)
    dateiname = f"Auftragsbestaetigung_{sicherer_dateiname('AB-' + suffix if suffix else item.kommission)}.docx"
    return send_file(
        puffer,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=dateiname,
    )
