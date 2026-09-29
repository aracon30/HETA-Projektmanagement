"""REST-API für den Reiter "Prozesse" (Prozessaufnahme zur Vorbereitung einer
möglichen ERP-Einführung). Wird in app.py als Blueprint registriert."""
import csv
import io
from datetime import datetime

from flask import Blueprint, Response, jsonify, request

from models import db, Prozess, ProzessSchritt, ProzessFrage, Dokument, ProzessVerbindung
from prozess_daten import AUFNAHMESTATUS, AUSWERTUNGSSTATUS, UEBERGABE_WEGE

bp = Blueprint("prozesse", __name__, url_prefix="/api")

AUFNAHMESTATUS_WERTE = {k for k, _ in AUFNAHMESTATUS}
AUSWERTUNGSSTATUS_WERTE = {k for k, _ in AUSWERTUNGSSTATUS}
WEG_WERTE = {k for k, _ in UEBERGABE_WEGE}

PROZESS_FELDER = {
    "nummer": "nummer", "bezeichnung": "bezeichnung", "variante": "variante",
    "verantwortlich": "verantwortlich", "ausloeser": "ausloeser", "ergebnis": "ergebnis",
    "beteiligte": "beteiligte", "systeme": "systeme", "vorgaengeMonat": "vorgaenge_monat",
    "geprueftVon": "geprueft_von", "notiz": "notiz",
}
FRAGE_FELDER = {
    "frage": "frage", "klaerungDurch": "klaerung_durch", "naechsterSchritt": "naechster_schritt",
    "antwort": "antwort", "nachweis": "nachweis",
}


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _text(value):
    """Leere Strings als NULL speichern."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _fehler(msg, code=400):
    return jsonify({"error": msg}), code


# ---------- Konfiguration (Statuswerte für das Frontend) ----------
@bp.route("/prozesse/config")
def prozess_config():
    return jsonify({
        "aufnahmestatus": [{"value": k, "label": v} for k, v in AUFNAHMESTATUS],
        "auswertungsstatus": [{"value": k, "label": v} for k, v in AUSWERTUNGSSTATUS],
        "wege": [{"value": k, "label": v} for k, v in UEBERGABE_WEGE],
    })


# ---------- Prozesse ----------
@bp.route("/prozesse")
def list_prozesse():
    prozesse = Prozess.query.order_by(Prozess.reihenfolge, Prozess.id).all()
    return jsonify([p.to_summary() for p in prozesse])


@bp.route("/prozesse/<int:prozess_id>")
def get_prozess(prozess_id):
    return jsonify(Prozess.query.get_or_404(prozess_id).to_dict())


@bp.route("/prozesse", methods=["POST"])
def create_prozess():
    data = request.get_json(force=True)
    bezeichnung = _text(data.get("bezeichnung"))
    if not bezeichnung:
        return _fehler("Bezeichnung ist ein Pflichtfeld.")
    parent_id = data.get("parentId")
    if parent_id is not None:
        Prozess.query.get_or_404(parent_id)
    letzte = db.session.query(db.func.max(Prozess.reihenfolge)).scalar() or 0
    prozess = Prozess(parent_id=parent_id, reihenfolge=letzte + 1, aufnahmestatus="vorgeschlagen")
    for key, attr in PROZESS_FELDER.items():
        if key in data:
            setattr(prozess, attr, _text(data[key]))
    prozess.bezeichnung = bezeichnung
    prozess.geprueft_am = _parse_date(data.get("geprueftAm"))
    db.session.add(prozess)
    db.session.commit()
    return jsonify(prozess.to_dict()), 201


@bp.route("/prozesse/<int:prozess_id>", methods=["PATCH"])
def update_prozess(prozess_id):
    prozess = Prozess.query.get_or_404(prozess_id)
    data = request.get_json(force=True)
    for key, attr in PROZESS_FELDER.items():
        if key in data:
            setattr(prozess, attr, _text(data[key]))
    if not prozess.bezeichnung:
        return _fehler("Bezeichnung ist ein Pflichtfeld.")
    if "geprueftAm" in data:
        prozess.geprueft_am = _parse_date(data["geprueftAm"])
    if "aufnahmestatus" in data:
        if data["aufnahmestatus"] not in AUFNAHMESTATUS_WERTE:
            return _fehler("Unbekannter Aufnahmestatus.")
        prozess.aufnahmestatus = data["aufnahmestatus"]
    if "parentId" in data and data["parentId"] != prozess.parent_id:
        neuer_parent = data["parentId"]
        # Zyklen verhindern: der neue übergeordnete Prozess darf nicht dieser selbst
        # oder einer seiner Unterprozesse sein.
        pruef = Prozess.query.get_or_404(neuer_parent) if neuer_parent is not None else None
        while pruef is not None:
            if pruef.id == prozess.id:
                return _fehler("Ein Prozess kann nicht unter sich selbst eingeordnet werden.")
            pruef = pruef.parent
        prozess.parent_id = neuer_parent
    db.session.commit()
    return jsonify(prozess.to_dict())


@bp.route("/prozesse/<int:prozess_id>", methods=["DELETE"])
def delete_prozess(prozess_id):
    prozess = Prozess.query.get_or_404(prozess_id)
    if prozess.kinder:
        return _fehler("Der Prozess hat noch Unterprozesse. Bitte diese zuerst löschen oder verschieben.", 409)
    for dok in prozess.dokumente:
        dok.prozess_id = None
    db.session.delete(prozess)
    db.session.commit()
    return "", 204


# ---------- Arbeitsschritte ----------
def _schritt_felder_setzen(schritt, data):
    for feld in ProzessSchritt.FELDER:
        if feld in data:
            setattr(schritt, feld, _text(data[feld]))


def _neu_nummerieren(prozess):
    for i, s in enumerate(sorted(prozess.schritte, key=lambda s: (s.reihenfolge, s.id)), 1):
        s.reihenfolge = i


@bp.route("/prozesse/<int:prozess_id>/schritte", methods=["POST"])
def add_schritt(prozess_id):
    prozess = Prozess.query.get_or_404(prozess_id)
    data = request.get_json(force=True)
    if not _text(data.get("taetigkeit")):
        return _fehler("Tätigkeit ist ein Pflichtfeld.")
    schritt = ProzessSchritt(prozess_id=prozess.id, reihenfolge=len(prozess.schritte) + 1)
    _schritt_felder_setzen(schritt, data)
    db.session.add(schritt)
    db.session.commit()
    return jsonify(schritt.to_dict()), 201


@bp.route("/schritte/<int:schritt_id>", methods=["PATCH"])
def update_schritt(schritt_id):
    schritt = ProzessSchritt.query.get_or_404(schritt_id)
    data = request.get_json(force=True)
    _schritt_felder_setzen(schritt, data)
    if not schritt.taetigkeit:
        return _fehler("Tätigkeit ist ein Pflichtfeld.")
    db.session.commit()
    return jsonify(schritt.to_dict())


@bp.route("/schritte/<int:schritt_id>/verschieben", methods=["POST"])
def move_schritt(schritt_id):
    """Verschiebt einen Schritt um eine Position nach oben oder unten."""
    schritt = ProzessSchritt.query.get_or_404(schritt_id)
    richtung = request.get_json(force=True).get("richtung")
    prozess = schritt.prozess
    _neu_nummerieren(prozess)
    liste = sorted(prozess.schritte, key=lambda s: s.reihenfolge)
    idx = liste.index(schritt)
    ziel = idx - 1 if richtung == "hoch" else idx + 1
    if 0 <= ziel < len(liste):
        liste[idx].reihenfolge, liste[ziel].reihenfolge = liste[ziel].reihenfolge, liste[idx].reihenfolge
    db.session.commit()
    return jsonify(prozess.to_dict())


@bp.route("/schritte/<int:schritt_id>", methods=["DELETE"])
def delete_schritt(schritt_id):
    schritt = ProzessSchritt.query.get_or_404(schritt_id)
    prozess = schritt.prozess
    ProzessVerbindung.query.filter_by(schritt_id=schritt.id).update({"schritt_id": None})
    prozess.schritte.remove(schritt)  # delete-orphan löscht den Schritt beim Commit
    _neu_nummerieren(prozess)
    db.session.commit()
    return "", 204


# ---------- Offene Fragen ----------
def _frage_felder_setzen(frage, data):
    for key, attr in FRAGE_FELDER.items():
        if key in data:
            setattr(frage, attr, _text(data[key]))
    if "faelligkeit" in data:
        frage.faelligkeit = _parse_date(data["faelligkeit"])
    if "status" in data:
        frage.status = "beantwortet" if data["status"] == "beantwortet" else "offen"


@bp.route("/prozesse/<int:prozess_id>/fragen", methods=["POST"])
def add_frage(prozess_id):
    Prozess.query.get_or_404(prozess_id)
    data = request.get_json(force=True)
    if not _text(data.get("frage")):
        return _fehler("Die Frage darf nicht leer sein.")
    frage = ProzessFrage(prozess_id=prozess_id, status="offen", erstellt_von=_text(data.get("erstelltVon")))
    _frage_felder_setzen(frage, data)
    db.session.add(frage)
    db.session.commit()
    return jsonify(frage.to_dict()), 201


@bp.route("/fragen/<int:frage_id>", methods=["PATCH"])
def update_frage(frage_id):
    frage = ProzessFrage.query.get_or_404(frage_id)
    data = request.get_json(force=True)
    _frage_felder_setzen(frage, data)
    if not frage.frage:
        return _fehler("Die Frage darf nicht leer sein.")
    db.session.commit()
    return jsonify(frage.to_dict())


@bp.route("/fragen/<int:frage_id>", methods=["DELETE"])
def delete_frage(frage_id):
    frage = ProzessFrage.query.get_or_404(frage_id)
    db.session.delete(frage)
    db.session.commit()
    return "", 204


# ---------- Dokumente (Arbeitsanweisungen) ----------
@bp.route("/dokumente")
def list_dokumente():
    return jsonify([d.to_dict() for d in Dokument.query.order_by(Dokument.nummer).all()])


@bp.route("/dokumente/<int:dokument_id>", methods=["PATCH"])
def update_dokument(dokument_id):
    dok = Dokument.query.get_or_404(dokument_id)
    data = request.get_json(force=True)
    if "auswertungsstatus" in data:
        if data["auswertungsstatus"] not in AUSWERTUNGSSTATUS_WERTE:
            return _fehler("Unbekannter Auswertungsstatus.")
        dok.auswertungsstatus = data["auswertungsstatus"]
    if "prozessId" in data:
        if data["prozessId"] is not None:
            Prozess.query.get_or_404(data["prozessId"])
        dok.prozess_id = data["prozessId"]
    if "notiz" in data:
        dok.notiz = _text(data["notiz"])
    db.session.commit()
    return jsonify(dok.to_dict())


# ---------- Schnittstellen (Übergaben zwischen Prozessen) ----------
def _verbindung_setzen(v, data):
    if "vonId" in data:
        v.von_id = Prozess.query.get_or_404(data["vonId"]).id
    if "nachId" in data:
        v.nach_id = Prozess.query.get_or_404(data["nachId"]).id
    if "inhalt" in data:
        v.inhalt = _text(data["inhalt"])
    if "weg" in data:
        if data["weg"] not in WEG_WERTE:
            return "Unbekannter Übergabeweg."
        v.weg = data["weg"]
    if "schrittId" in data:
        schritt_id = data["schrittId"]
        if schritt_id is not None:
            schritt = ProzessSchritt.query.get_or_404(schritt_id)
            if schritt.prozess_id not in (v.von_id, v.nach_id):
                return "Der Schritt gehört zu keinem der beiden Prozesse."
        v.schritt_id = schritt_id
    if "problem" in data:
        v.problem = bool(data["problem"])
    if "notiz" in data:
        v.notiz = _text(data["notiz"])
    if not v.inhalt:
        return "Bitte angeben, was übergeben wird."
    if v.von_id == v.nach_id:
        return "Ein Prozess kann nicht an sich selbst übergeben."
    return None


@bp.route("/verbindungen")
def list_verbindungen():
    return jsonify([v.to_dict() for v in ProzessVerbindung.query.order_by(ProzessVerbindung.id).all()])


@bp.route("/verbindungen", methods=["POST"])
def create_verbindung():
    data = request.get_json(force=True)
    if "vonId" not in data or "nachId" not in data:
        return _fehler("Von- und Nach-Prozess sind Pflichtfelder.")
    v = ProzessVerbindung(weg="unklar", problem=False)
    fehler = _verbindung_setzen(v, data)
    if fehler:
        return _fehler(fehler)
    db.session.add(v)
    db.session.commit()
    return jsonify(v.to_dict()), 201


@bp.route("/verbindungen/<int:verbindung_id>", methods=["PATCH"])
def update_verbindung(verbindung_id):
    v = ProzessVerbindung.query.get_or_404(verbindung_id)
    fehler = _verbindung_setzen(v, request.get_json(force=True))
    if fehler:
        db.session.rollback()
        return _fehler(fehler)
    db.session.commit()
    return jsonify(v.to_dict())


@bp.route("/verbindungen/<int:verbindung_id>", methods=["DELETE"])
def delete_verbindung(verbindung_id):
    db.session.delete(ProzessVerbindung.query.get_or_404(verbindung_id))
    db.session.commit()
    return "", 204


# ---------- CSV-Export im Format der Excel-Vorlage ----------
def _csv_antwort(dateiname, kopf, zeilen):
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(kopf)
    w.writerows(zeilen)
    # BOM, damit Excel Umlaute korrekt erkennt
    return Response(
        "﻿" + buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{dateiname}"'},
    )


def _prozess_label(p):
    return p.nummer or p.bezeichnung if p else ""


@bp.route("/prozesse/export/<blatt>.csv")
def export_csv(blatt):
    if blatt == "ablaufschritte":
        schritte = (ProzessSchritt.query.join(Prozess)
                    .order_by(Prozess.reihenfolge, Prozess.id, ProzessSchritt.reihenfolge).all())
        return _csv_antwort("ablaufschritte.csv", [
            "Prozess-ID", "Prozess", "Schritt-Nr.", "Tätigkeit", "Ausführende Person / Rolle", "Eingaben",
            "System", "Ergebnis", "Übergabe", "Freigabe", "Ausnahme / nächster Schritt",
            "Bearbeitungszeit", "Wartezeit", "Nachweis / Prüfstatus",
        ], [[_prozess_label(s.prozess), s.prozess.bezeichnung, s.reihenfolge,
             *[getattr(s, f) or "" for f in ProzessSchritt.FELDER]] for s in schritte])
    if blatt == "offene_fragen":
        fragen = ProzessFrage.query.join(Prozess).order_by(Prozess.reihenfolge, Prozess.id, ProzessFrage.id).all()
        return _csv_antwort("offene_fragen.csv", [
            "Frage-ID", "Prozessbezug", "Frage", "Klärung durch", "Nächster Schritt", "Fälligkeit",
            "Status", "Antwort / Entscheidung", "Nachweis",
        ], [[f"Q{f.id:03d}", _prozess_label(f.prozess), f.frage, f.klaerung_durch or "",
             f.naechster_schritt or "", f.faelligkeit.strftime("%d.%m.%Y") if f.faelligkeit else "",
             f.status, f.antwort or "", f.nachweis or ""] for f in fragen])
    if blatt == "prozessuebersicht":
        labels = dict(AUFNAHMESTATUS)
        prozesse = Prozess.query.order_by(Prozess.reihenfolge, Prozess.id).all()
        return _csv_antwort("prozessuebersicht.csv", [
            "Prozess-ID", "Prozessname", "Übergeordnet", "Bereich / Variante", "Verantwortlicher", "Auslöser",
            "Ergebnis", "Beteiligte", "Systeme", "Aufnahmestatus", "Prüfung", "Vorgänge pro Monat",
        ], [[p.nummer or "", p.bezeichnung, _prozess_label(p.parent), p.variante or "", p.verantwortlich or "",
             p.ausloeser or "", p.ergebnis or "", p.beteiligte or "", p.systeme or "",
             labels.get(p.aufnahmestatus, p.aufnahmestatus),
             " ".join(x for x in [p.geprueft_von or "",
                                  p.geprueft_am.strftime("%d.%m.%Y") if p.geprueft_am else ""] if x),
             p.vorgaenge_monat or ""] for p in prozesse])
    if blatt == "arbeitsanweisungen":
        labels = dict(AUSWERTUNGSSTATUS)
        doks = Dokument.query.order_by(Dokument.nummer).all()
        return _csv_antwort("arbeitsanweisungen.csv",
                            ["Nummer", "Revision", "Titel", "Geltungsbereich", "Prozess", "Auswertungsstatus"],
                            [[d.nummer, d.revision or "", d.titel, d.geltungsbereich or "",
                              _prozess_label(d.prozess), labels.get(d.auswertungsstatus, d.auswertungsstatus)]
                             for d in doks])
    if blatt == "schnittstellen":
        wege = dict(UEBERGABE_WEGE)
        verbindungen = ProzessVerbindung.query.order_by(ProzessVerbindung.id).all()
        schritte = {s.id: s for s in ProzessSchritt.query.filter(
            ProzessSchritt.id.in_([v.schritt_id for v in verbindungen if v.schritt_id])).all()}
        return _csv_antwort("schnittstellen.csv", [
            "Von Prozess", "Von", "Nach Prozess", "Nach", "Was wird übergeben", "Weg", "Zu Schritt",
            "Problem", "Notiz",
        ], [[v.von.nummer or "", v.von.bezeichnung, v.nach.nummer or "", v.nach.bezeichnung, v.inhalt,
             wege.get(v.weg, v.weg),
             f"{schritte[v.schritt_id].prozess.nummer or ''} Schritt {schritte[v.schritt_id].reihenfolge}"
             if v.schritt_id in schritte else "",
             "ja" if v.problem else "", v.notiz or ""] for v in verbindungen])
    return _fehler("Unbekanntes Arbeitsblatt.", 404)
