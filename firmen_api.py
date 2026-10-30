"""
Firmen-CRM: eine gemeinsame Firmenliste statt Freitext an jeder Anfrage/jedem
Angebot/Auftrag (Stufe 1), dazu Kontakte und Aktivitäten/Zeitstrahl inkl.
Wiedervorlage (Stufe 2, siehe docs/KONZEPT-FIRMEN-CRM.md). Stufe 2 speichert
personenbezogene Daten, obwohl das Konzept dafür eigentlich erst
Login/Rechteverwaltung vorsieht — bewusste Entscheidung von Philipp, siehe
CLAUDE.md; Datenschutz-Abstimmung mit der PACO-Gruppe steht noch aus.
"""
import difflib
import re
from datetime import date, datetime

from flask import Blueprint, jsonify, request

from models import db, Firma, FirmaAdresse, Kontakt, Aktivitaet, Item

bp = Blueprint("firmen", __name__, url_prefix="/api")


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

RECHTSFORMEN = [
    "gmbh", "ag", "se", "kg", "ohg", "ug", "co kg", "inc", "ltd",
    "llc", "sa", "sarl", "bv", "nv", "spa", "srl", "oy", "ab", "plc",
]


def normalisiere(name):
    """Für den Ähnlichkeitsvergleich beim Zuordnen: klein, Rechtsform/Satzzeichen
    weg, Mehrfach-Leerzeichen zusammengefasst. "GmbH & Co KG" muss vor dem
    Entfernen der Satzzeichen behandelt werden, sonst ist das "&" schon weg
    und der Ausdruck matcht nie."""
    s = (name or "").lower()
    s = re.sub(r"\bgmbh\s*&\s*co\.?\s*kg\b", " ", s)
    s = re.sub(r"[.,&/]", " ", s)
    for form in RECHTSFORMEN:
        s = re.sub(rf"\b{re.escape(form)}\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def firma_aus_dict(data, firma=None):
    firma = firma or Firma()
    for feld, spalte in [
        ("name", "name"), ("kurzname", "kurzname"), ("branche", "branche"), ("land", "land"),
        ("website", "website"), ("lieferantenportal", "lieferantenportal"), ("quelle", "quelle"),
        ("status", "status"), ("notiz", "notiz"), ("warengruppe", "warengruppe"),
        ("freigabestatus", "freigabestatus"),
    ]:
        if feld in data:
            setattr(firma, spalte, data.get(feld))
    if "rollen" in data:
        rollen = data.get("rollen") or []
        firma.rollen = ",".join(rollen) if isinstance(rollen, list) else (rollen or "")
    if "bewertungspflichtig" in data:
        firma.bewertungspflichtig = bool(data.get("bewertungspflichtig"))
    if "aktiv" in data:
        firma.aktiv = bool(data.get("aktiv"))
    if "konzernId" in data:
        firma.konzern_id = data.get("konzernId") or None
    return firma


@bp.route("/firmen", methods=["GET"])
def list_firmen():
    q = Firma.query
    rolle = request.args.get("rolle")
    if rolle:
        q = q.filter(Firma.rollen.like(f"%{rolle}%"))
    status = request.args.get("status")
    if status:
        q = q.filter_by(status=status)
    if request.args.get("aktiv") != "alle":
        q = q.filter(Firma.aktiv.is_(True))
    term = (request.args.get("q") or "").strip().lower()
    firmen = q.order_by(Firma.name).all()
    if term:
        firmen = [f for f in firmen if term in (f.name or "").lower() or term in (f.kurzname or "").lower()]
    return jsonify([f.to_dict() for f in firmen])


@bp.route("/firmen", methods=["POST"])
def add_firma():
    data = request.get_json(force=True)
    if not data.get("name"):
        return jsonify({"error": "Name ist ein Pflichtfeld."}), 400
    firma = firma_aus_dict(data)
    firma.created_at = datetime.utcnow()
    firma.created_by = data.get("erstelltVon")
    db.session.add(firma)
    db.session.commit()
    return jsonify(firma.to_dict()), 201


@bp.route("/firmen/<int:firma_id>", methods=["GET"])
def get_firma(firma_id):
    firma = Firma.query.get_or_404(firma_id)
    return jsonify(firma.to_dict(detail=True))


@bp.route("/firmen/<int:firma_id>", methods=["PATCH"])
def update_firma(firma_id):
    firma = Firma.query.get_or_404(firma_id)
    data = request.get_json(force=True)
    firma_aus_dict(data, firma)
    db.session.commit()
    return jsonify(firma.to_dict(detail=True))


@bp.route("/firmen/<int:firma_id>/adressen", methods=["POST"])
def add_adresse(firma_id):
    firma = Firma.query.get_or_404(firma_id)
    data = request.get_json(force=True)
    if not data.get("zeilen"):
        return jsonify({"error": "Adresse darf nicht leer sein."}), 400
    standard = bool(data.get("standard"))
    if standard:
        FirmaAdresse.query.filter_by(firma_id=firma.id, standard=True).update({"standard": False})
    adresse = FirmaAdresse(
        firma_id=firma.id, art=data.get("art") or "haupt", zeilen=data.get("zeilen"),
        standard=standard,
    )
    db.session.add(adresse)
    db.session.commit()
    return jsonify(adresse.to_dict()), 201


@bp.route("/adressen/<int:adresse_id>", methods=["PATCH"])
def update_adresse(adresse_id):
    adresse = FirmaAdresse.query.get_or_404(adresse_id)
    data = request.get_json(force=True)
    if "art" in data:
        adresse.art = data.get("art")
    if "zeilen" in data:
        adresse.zeilen = data.get("zeilen")
    if "standard" in data:
        standard = bool(data.get("standard"))
        if standard:
            FirmaAdresse.query.filter(
                FirmaAdresse.firma_id == adresse.firma_id, FirmaAdresse.id != adresse.id, FirmaAdresse.standard.is_(True)
            ).update({"standard": False})
        adresse.standard = standard
    db.session.commit()
    return jsonify(adresse.to_dict())


@bp.route("/adressen/<int:adresse_id>", methods=["DELETE"])
def delete_adresse(adresse_id):
    adresse = FirmaAdresse.query.get_or_404(adresse_id)
    db.session.delete(adresse)
    db.session.commit()
    return "", 204


# ---------- Assistent "Kunden zuordnen" (Konzept CRM 5.1) ----------
@bp.route("/firmen/zuordnen/vorschlag")
def zuordnen_vorschlag():
    """Gruppiert alle noch nicht verknüpften items.kunde-Werte nach Ähnlichkeit
    und schlägt für jede Gruppe vor, ob sie zu einer bestehenden Firma passt
    oder eine neue Firma werden sollte."""
    offene = (
        db.session.query(Item.kunde)
        .filter(Item.firma_id.is_(None), Item.kunde.isnot(None), Item.kunde != "")
        .distinct()
        .all()
    )
    namen = sorted({k for (k,) in offene})
    firmen = Firma.query.filter(Firma.aktiv.is_(True)).all()
    firmen_norm = {normalisiere(f.name): f for f in firmen}
    if firmen_norm:
        for f in firmen:
            n = normalisiere(f.kurzname) if f.kurzname else None
            if n:
                firmen_norm.setdefault(n, f)

    gruppen = []  # je {schluessel, namen: [...], firmaVorschlag: {id,name}|None}
    zugeordnet = set()
    for name in namen:
        if name in zugeordnet:
            continue
        norm = normalisiere(name)
        gruppe_namen = [name]
        zugeordnet.add(name)
        for andere in namen:
            if andere in zugeordnet:
                continue
            if difflib.SequenceMatcher(None, norm, normalisiere(andere)).ratio() >= 0.84:
                gruppe_namen.append(andere)
                zugeordnet.add(andere)

        firma_treffer = None
        beste_quote = 0.0
        for f_norm, f in firmen_norm.items():
            quote = difflib.SequenceMatcher(None, norm, f_norm).ratio()
            if quote > beste_quote:
                beste_quote, firma_treffer = quote, f
        gruppen.append({
            "namen": gruppe_namen,
            "anzahlAuftraege": sum(
                Item.query.filter_by(kunde=n, firma_id=None).count() for n in gruppe_namen
            ),
            "firmaVorschlag": firma_treffer.to_dict() if firma_treffer and beste_quote >= 0.84 else None,
        })
    return jsonify(gruppen)


@bp.route("/firmen/zuordnen/bestaetigen", methods=["POST"])
def zuordnen_bestaetigen():
    """body: {"gruppen": [{"namen": [...], "firmaId": 3} | {"namen": [...], "neueFirma": {"name": "..."}}]}"""
    data = request.get_json(force=True)
    verknuepft = 0
    firmen_neu = 0
    for gruppe in data.get("gruppen", []):
        namen = gruppe.get("namen") or []
        if not namen:
            continue
        if gruppe.get("firmaId"):
            firma = Firma.query.get(gruppe["firmaId"])
            if not firma:
                continue
        elif gruppe.get("neueFirma", {}).get("name"):
            firma = firma_aus_dict(gruppe["neueFirma"])
            firma.created_at = datetime.utcnow()
            db.session.add(firma)
            db.session.flush()
            firmen_neu += 1
        else:
            continue
        updated = Item.query.filter(Item.kunde.in_(namen), Item.firma_id.is_(None)).update(
            {"firma_id": firma.id}, synchronize_session=False
        )
        verknuepft += updated
    db.session.commit()
    return jsonify({"firmenNeu": firmen_neu, "auftraegeVerknuepft": verknuepft})


# ---------- Kontakte (Firmen-CRM Stufe 2) ----------
@bp.route("/firmen/<int:firma_id>/kontakte", methods=["GET"])
def list_kontakte(firma_id):
    Firma.query.get_or_404(firma_id)
    kontakte = Kontakt.query.filter_by(firma_id=firma_id, aktiv=True).order_by(Kontakt.nachname).all()
    return jsonify([k.to_dict() for k in kontakte])


@bp.route("/firmen/<int:firma_id>/kontakte", methods=["POST"])
def add_kontakt(firma_id):
    Firma.query.get_or_404(firma_id)
    data = request.get_json(force=True)
    if not (data.get("nachname") or "").strip():
        return jsonify({"error": "Nachname ist ein Pflichtfeld."}), 400
    kontakt = Kontakt(
        firma_id=firma_id,
        anrede=data.get("anrede") or None,
        vorname=(data.get("vorname") or "").strip() or None,
        nachname=data.get("nachname").strip(),
        funktion=data.get("funktion") or None,
        abteilung=data.get("abteilung") or None,
        telefon=data.get("telefon") or None,
        mobil=data.get("mobil") or None,
        email=data.get("email") or None,
        kontaktweg_erlaubt=data.get("kontaktwegErlaubt") or "anfrage",
        einwilligung_am=parse_date(data.get("einwilligungAm")),
        notiz=data.get("notiz") or None,
    )
    db.session.add(kontakt)
    db.session.commit()
    return jsonify(kontakt.to_dict()), 201


@bp.route("/kontakte/<int:kontakt_id>", methods=["PATCH"])
def update_kontakt(kontakt_id):
    kontakt = Kontakt.query.get_or_404(kontakt_id)
    data = request.get_json(force=True)
    for feld, spalte in [
        ("anrede", "anrede"), ("vorname", "vorname"), ("nachname", "nachname"),
        ("funktion", "funktion"), ("abteilung", "abteilung"), ("telefon", "telefon"),
        ("mobil", "mobil"), ("email", "email"), ("notiz", "notiz"),
    ]:
        if feld in data:
            setattr(kontakt, spalte, data.get(feld))
    if "kontaktwegErlaubt" in data:
        kontakt.kontaktweg_erlaubt = data.get("kontaktwegErlaubt") or "anfrage"
    if "einwilligungAm" in data:
        kontakt.einwilligung_am = parse_date(data.get("einwilligungAm"))
    if "aktiv" in data:
        kontakt.aktiv = bool(data.get("aktiv"))
    db.session.commit()
    return jsonify(kontakt.to_dict())


@bp.route("/kontakte/<int:kontakt_id>", methods=["DELETE"])
def delete_kontakt(kontakt_id):
    kontakt = Kontakt.query.get_or_404(kontakt_id)
    db.session.delete(kontakt)
    db.session.commit()
    return "", 204


# ---------- Aktivitäten / Zeitstrahl (Firmen-CRM Stufe 2) ----------
@bp.route("/firmen/<int:firma_id>/aktivitaeten", methods=["GET"])
def list_aktivitaeten(firma_id):
    Firma.query.get_or_404(firma_id)
    aktivitaeten = Aktivitaet.query.filter_by(firma_id=firma_id).order_by(Aktivitaet.datum.desc(), Aktivitaet.id.desc()).all()
    return jsonify([a.to_dict() for a in aktivitaeten])


@bp.route("/firmen/<int:firma_id>/aktivitaeten", methods=["POST"])
def add_aktivitaet(firma_id):
    Firma.query.get_or_404(firma_id)
    data = request.get_json(force=True)
    datum = parse_date(data.get("datum")) or date.today()
    aktivitaet = Aktivitaet(
        firma_id=firma_id,
        kontakt_id=data.get("kontaktId") or None,
        item_id=data.get("itemId") or None,
        art=data.get("art") or "sonstiges",
        datum=datum,
        nutzer=data.get("nutzer") or None,
        inhalt=data.get("inhalt") or None,
        wiedervorlage_am=parse_date(data.get("wiedervorlageAm")),
        wiedervorlage_status="offen",
    )
    db.session.add(aktivitaet)
    db.session.commit()
    return jsonify(aktivitaet.to_dict()), 201


@bp.route("/aktivitaeten/<int:aktivitaet_id>", methods=["PATCH"])
def update_aktivitaet(aktivitaet_id):
    aktivitaet = Aktivitaet.query.get_or_404(aktivitaet_id)
    data = request.get_json(force=True)
    for feld, spalte in [("art", "art"), ("nutzer", "nutzer"), ("inhalt", "inhalt")]:
        if feld in data:
            setattr(aktivitaet, spalte, data.get(feld))
    if "kontaktId" in data:
        aktivitaet.kontakt_id = data.get("kontaktId") or None
    if "datum" in data:
        aktivitaet.datum = parse_date(data.get("datum")) or aktivitaet.datum
    if "wiedervorlageAm" in data:
        aktivitaet.wiedervorlage_am = parse_date(data.get("wiedervorlageAm"))
    if "wiedervorlageStatus" in data:
        aktivitaet.wiedervorlage_status = data.get("wiedervorlageStatus") or "offen"
    db.session.commit()
    return jsonify(aktivitaet.to_dict())


@bp.route("/aktivitaeten/<int:aktivitaet_id>", methods=["DELETE"])
def delete_aktivitaet(aktivitaet_id):
    aktivitaet = Aktivitaet.query.get_or_404(aktivitaet_id)
    db.session.delete(aktivitaet)
    db.session.commit()
    return "", 204
