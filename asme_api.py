"""
ASME-Auftragsdokumente: Lieferantenbestellungen je Auftrag erfassen und daraus
die Formulare laut QC-Handbuch erzeugen (Bestellung, WE-Kontrollschein).

Trennung:
  Daten     -> Tabellen lieferanten_bestellungen / bestell_positionen
  Layout    -> Word-Vorlagen in vorlagen/asme/<Revision>/ (Platzhalter im Jinja-Stil,
               gerendert mit docxtpl), Konfiguration in formulare.json
  Generator -> dieser Blueprint

Neue Handbuch-Ausgabe: Revisionsordner kopieren, Word-Vorlagen anpassen,
in formulare.json die Revision eintragen und "aktuell": true setzen (beim
alten Ordner auf false). Alte Revisionen bleiben für Nachdrucke erhalten.
"""
import io
import json
import os
import re
import zipfile
from datetime import datetime

from flask import Blueprint, jsonify, request, send_file
from docxtpl import DocxTemplate

from models import db, Item, LieferantenBestellung, BestellPosition

bp = Blueprint("asme", __name__, url_prefix="/api")

VORLAGEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vorlagen", "asme")


# ---------- Vorlagen-Revisionen ----------
def lade_revisionen():
    """Alle Revisionsordner mit formulare.json, aktuelle zuerst."""
    revisionen = []
    if not os.path.isdir(VORLAGEN_DIR):
        return revisionen
    for ordner in sorted(os.listdir(VORLAGEN_DIR)):
        pfad = os.path.join(VORLAGEN_DIR, ordner, "formulare.json")
        if not os.path.isfile(pfad):
            continue
        with open(pfad, encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["ordner"] = ordner
        revisionen.append(cfg)
    revisionen.sort(key=lambda c: (not c.get("aktuell"), c["ordner"]))
    return revisionen


def finde_revision(ordner):
    revisionen = lade_revisionen()
    if not revisionen:
        return None
    if not ordner:
        return revisionen[0]
    return next((r for r in revisionen if r["ordner"] == ordner), None)


@bp.route("/asme/config")
def asme_config():
    return jsonify([
        {
            "ordner": r["ordner"],
            "revision": r.get("revision"),
            "beschreibung": r.get("beschreibung"),
            "aktuell": bool(r.get("aktuell")),
            "vorlaeufig": bool(r.get("vorlaeufig")),
            "formulare": [{"key": f["key"], "titel": f["titel"], "formNr": f.get("form_nr")} for f in r["formulare"]],
            "auswahl": r.get("auswahl", {}),
            "vorgaben": r.get("vorgaben", {}),
        }
        for r in lade_revisionen()
    ])


# ---------- Hilfsfunktionen ----------
class Ankreuzliste(dict):
    """{{ std['B16.5'] }} -> ☒/☐; auch für Standards, die nur in der Vorlage stehen."""
    def __init__(self, gewaehlt, alle):
        super().__init__({s: ("☒" if s in gewaehlt else "☐") for s in alle})
        self.gewaehlt = set(gewaehlt)

    def __missing__(self, key):
        return "☒" if key in self.gewaehlt else "☐"


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_float(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(".", "").replace(",", ".")) if "," in str(value) else float(value)


def fmt_datum(d):
    return d.strftime("%d.%m.%Y") if d else ""


def fmt_zahl(wert, nachkomma=2):
    if wert is None:
        return ""
    s = f"{wert:,.{nachkomma}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_menge(wert):
    if wert is None:
        return ""
    return fmt_zahl(wert, 0) if float(wert).is_integer() else fmt_zahl(wert, 3).rstrip("0").rstrip(",")


def sicherer_dateiname(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text or "").strip("-") or "ohne-Nr"


BESTELLUNG_FELDER = {
    # JSON-Name -> (Spalte, Parser)
    "bestellNr": ("bestell_nr", str),
    "datum": ("datum", parse_date),
    "lieferant": ("lieferant", str),
    "ihrAngebot": ("ihr_angebot", str),
    "ihrSachbearbeiter": ("ihr_sachbearbeiter", str),
    "unserZeichen": ("unser_zeichen", str),
    "lieferdatum": ("lieferdatum", parse_date),
    "versand": ("versand", str),
    "asmeEdition": ("asme_edition", str),
    "codedMarking": ("coded_marking", str),
    "materialArt": ("material_art", str),
    "zahlungsbedingungen": ("zahlungsbedingungen", str),
    "mwstSatz": ("mwst_satz", parse_float),
}

POSITION_FELDER = {
    "pos": ("pos", str),
    "menge": ("menge", parse_float),
    "einheit": ("einheit", str),
    "bezeichnung": ("bezeichnung", str),
    "werkstoff": ("werkstoff", str),
    "spezifikation": ("spezifikation", str),
    "stuecklistePos": ("stueckliste_pos", str),
    "preis": ("preis", parse_float),
}


def uebernehme_felder(obj, data, felder):
    for json_name, (spalte, parser) in felder.items():
        if json_name not in data:
            continue
        wert = data[json_name]
        if isinstance(wert, str):
            wert = wert.strip()
        if wert in ("", None):
            setattr(obj, spalte, None)
        else:
            setattr(obj, spalte, parser(wert))


# ---------- Bestellungen ----------
@bp.route("/items/<int:item_id>/bestellungen")
def get_bestellungen(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify([b.to_dict() for b in item.lieferanten_bestellungen])


@bp.route("/items/<int:item_id>/bestellungen", methods=["POST"])
def add_bestellung(item_id):
    item = Item.query.get_or_404(item_id)
    if not item.asme:
        return jsonify({"error": "Erst beim Auftrag „ASME-Auftrag“ anhaken."}), 400
    data = request.get_json(force=True)
    if not (data.get("bestellNr") or "").strip():
        return jsonify({"error": "Bestell-Nr. ist ein Pflichtfeld."}), 400
    vorgaben = (finde_revision(None) or {}).get("vorgaben", {})
    bestellung = LieferantenBestellung(
        item_id=item.id,
        versand=vorgaben.get("versand"),
        asme_edition=vorgaben.get("asme_edition"),
        zahlungsbedingungen=vorgaben.get("zahlungsbedingungen"),
        mwst_satz=vorgaben.get("mwst_satz", 19),
    )
    uebernehme_felder(bestellung, data, BESTELLUNG_FELDER)
    if "weitereStandards" in data:
        bestellung.weitere_standards = ",".join(data.get("weitereStandards") or [])
    db.session.add(bestellung)
    db.session.commit()
    return jsonify(bestellung.to_dict()), 201


@bp.route("/bestellungen/<int:bestellung_id>", methods=["PATCH"])
def update_bestellung(bestellung_id):
    bestellung = LieferantenBestellung.query.get_or_404(bestellung_id)
    data = request.get_json(force=True)
    if "bestellNr" in data and not (data.get("bestellNr") or "").strip():
        return jsonify({"error": "Bestell-Nr. ist ein Pflichtfeld."}), 400
    uebernehme_felder(bestellung, data, BESTELLUNG_FELDER)
    if "weitereStandards" in data:
        bestellung.weitere_standards = ",".join(data.get("weitereStandards") or [])
    db.session.commit()
    return jsonify(bestellung.to_dict())


@bp.route("/bestellungen/<int:bestellung_id>", methods=["DELETE"])
def delete_bestellung(bestellung_id):
    bestellung = LieferantenBestellung.query.get_or_404(bestellung_id)
    db.session.delete(bestellung)
    db.session.commit()
    return "", 204


# ---------- Bestellpositionen ----------
@bp.route("/bestellungen/<int:bestellung_id>/positionen", methods=["POST"])
def add_bestellposition(bestellung_id):
    bestellung = LieferantenBestellung.query.get_or_404(bestellung_id)
    data = request.get_json(force=True)
    if not (data.get("bezeichnung") or "").strip():
        return jsonify({"error": "Bezeichnung ist ein Pflichtfeld."}), 400
    position = BestellPosition(bestellung_id=bestellung.id, reihenfolge=len(bestellung.positionen))
    uebernehme_felder(position, data, POSITION_FELDER)
    if not position.pos:
        position.pos = str((len(bestellung.positionen) + 1) * 10)
    db.session.add(position)
    db.session.commit()
    return jsonify(position.to_dict()), 201


@bp.route("/bestellpositionen/<int:position_id>", methods=["PATCH"])
def update_bestellposition(position_id):
    position = BestellPosition.query.get_or_404(position_id)
    data = request.get_json(force=True)
    if "bezeichnung" in data and not (data.get("bezeichnung") or "").strip():
        return jsonify({"error": "Bezeichnung ist ein Pflichtfeld."}), 400
    uebernehme_felder(position, data, POSITION_FELDER)
    db.session.commit()
    return jsonify(position.to_dict())


@bp.route("/bestellpositionen/<int:position_id>", methods=["DELETE"])
def delete_bestellposition(position_id):
    position = BestellPosition.query.get_or_404(position_id)
    db.session.delete(position)
    db.session.commit()
    return "", 204


# ---------- Dokumente erzeugen ----------
def baue_kontext(bestellung, revision, formular):
    item = bestellung.item
    standards = set(bestellung.standards_liste())
    auswahl_standards = revision.get("auswahl", {}).get("weitere_standards", [])

    positionen = []
    summe = 0.0
    for p in bestellung.positionen:
        gesamt = p.gesamt()
        if gesamt is not None:
            summe += gesamt
        positionen.append({
            "pos": p.pos or "",
            "menge": fmt_menge(p.menge),
            "einheit": p.einheit or "",
            "menge_einheit": " ".join(x for x in (fmt_menge(p.menge), p.einheit or "") if x),
            "bezeichnung": p.bezeichnung or "",
            "werkstoff": p.werkstoff or "",
            "spezifikation": p.spezifikation or "",
            "stueckliste_pos": p.stueckliste_pos or "",
            "preis": fmt_zahl(p.preis),
            "gesamt": fmt_zahl(gesamt),
        })
    mwst_satz = bestellung.mwst_satz if bestellung.mwst_satz is not None else 19.0
    mwst = round(summe * mwst_satz / 100, 2)

    kommission = item.kommission or ""
    return {
        "bestell_nr": bestellung.bestell_nr or "",
        "datum": fmt_datum(bestellung.datum),
        "lieferant": bestellung.lieferant or "",
        "ihr_angebot": bestellung.ihr_angebot or "",
        "ihr_sachbearbeiter": bestellung.ihr_sachbearbeiter or "",
        "unser_zeichen": bestellung.unser_zeichen or "",
        "kommission": kommission,
        "kunde": item.kunde or "",
        "bestell_nr_kommission": " / ".join(x for x in (bestellung.bestell_nr, kommission) if x),
        "lieferdatum": fmt_datum(bestellung.lieferdatum),
        "versand": bestellung.versand or "",
        "asme_edition": bestellung.asme_edition or "",
        "coded_marking": bestellung.coded_marking or "",
        "material_art": bestellung.material_art or "",
        "spezifikationen": ", ".join(dict.fromkeys(p["spezifikation"] for p in positionen if p["spezifikation"])),
        "werkstoffe": ", ".join(dict.fromkeys(p["werkstoff"] for p in positionen if p["werkstoff"])),
        "std": Ankreuzliste(standards, auswahl_standards),
        "zahlungsbedingungen": bestellung.zahlungsbedingungen or "",
        "positionen": positionen,
        "summe_netto": fmt_zahl(summe),
        "mwst_satz": fmt_menge(mwst_satz),
        "mwst": fmt_zahl(mwst),
        "summe_brutto": fmt_zahl(summe + mwst),
        "revision": revision.get("revision", revision["ordner"]),
        "form_nr": formular.get("form_nr", ""),
        "erzeugt_am": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }


def rendere_formular(bestellung, revision, formular):
    vorlage = os.path.join(VORLAGEN_DIR, revision["ordner"], formular["datei"])
    if not os.path.isfile(vorlage):
        raise FileNotFoundError(f"Vorlage fehlt: {revision['ordner']}/{formular['datei']}")
    doc = DocxTemplate(vorlage)
    doc.render(baue_kontext(bestellung, revision, formular), autoescape=True)
    puffer = io.BytesIO()
    doc.save(puffer)
    dateiname = formular.get("dateiname", formular["datei"]).replace(
        "{bestell_nr}", sicherer_dateiname(bestellung.bestell_nr))
    return dateiname, puffer.getvalue()


@bp.route("/bestellungen/<int:bestellung_id>/dokumente")
def erzeuge_dokumente(bestellung_id):
    """Erzeugt die Formulare der gewählten Revision.
    ?rev=<Ordner> (Standard: aktuelle), ?formular=<key> für ein einzelnes .docx,
    ohne formular-Parameter alle Formulare als ZIP."""
    bestellung = LieferantenBestellung.query.get_or_404(bestellung_id)
    revision = finde_revision(request.args.get("rev"))
    if not revision:
        return jsonify({"error": "Keine Vorlagen-Revision gefunden."}), 404
    if not bestellung.item.asme:
        return jsonify({"error": "Der Auftrag ist nicht als ASME-Auftrag gekennzeichnet."}), 400
    if not bestellung.positionen:
        return jsonify({"error": "Die Bestellung hat noch keine Positionen."}), 400

    formulare = revision["formulare"]
    gewuenscht = request.args.get("formular")
    if gewuenscht:
        formulare = [f for f in formulare if f["key"] == gewuenscht]
        if not formulare:
            return jsonify({"error": f"Formular '{gewuenscht}' gibt es in dieser Revision nicht."}), 404

    try:
        dateien = [rendere_formular(bestellung, revision, f) for f in formulare]
    except FileNotFoundError as err:
        return jsonify({"error": str(err)}), 500

    docx_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if len(dateien) == 1:
        name, inhalt = dateien[0]
        return send_file(io.BytesIO(inhalt), mimetype=docx_mime, as_attachment=True, download_name=name)

    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, inhalt in dateien:
            zf.writestr(name, inhalt)
    puffer.seek(0)
    zip_name = f"ASME-Dokumente_{sicherer_dateiname(bestellung.bestell_nr)}_{revision['ordner']}.zip"
    return send_file(puffer, mimetype="application/zip", as_attachment=True, download_name=zip_name)
