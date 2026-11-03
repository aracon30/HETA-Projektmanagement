"""
Digitales Board (Wandbildschirm im Büro/Werkstatt): eine reine Lese-Ansicht
unter /board, die zwischen Aufträgen, Aufgaben, Kennzahlen und Infos
(News/Besucher/Termine) wechselt. Aufträge/Aufgaben/Kennzahlen kommen aus
den bestehenden Daten, nur die Infos werden über /board/pflege eigens
gepflegt (Modell BoardMeldung).
"""
from datetime import date, timedelta

from flask import Blueprint, jsonify, request

from models import db, Item, VerlaufEintrag, BoardMeldung

bp = Blueprint("board", __name__, url_prefix="/api/board")

TYPEN = ("news", "besucher", "termin")
ANGEBOT_OFFEN = ("in_bearbeitung", "versendet", "wiedervorlage")


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def offene_auftraege():
    return Item.query.filter(
        Item.type == "auftrag",
        db.or_(Item.archiviert.is_(None), Item.archiviert.is_(False)),
        db.or_(Item.auftrag_status.is_(None), Item.auftrag_status != "erledigt"),
    ).all()


def aktuelle_meldungen(heute):
    """News bis sichtbar_bis (ohne Datum = dauerhaft), Besucher/Termine ab heute."""
    meldungen = BoardMeldung.query.all()
    aktuell = []
    for m in meldungen:
        if m.sichtbar_bis and m.sichtbar_bis < heute:
            continue
        if m.typ in ("besucher", "termin") and m.datum and m.datum < heute:
            continue
        aktuell.append(m)
    aktuell.sort(key=lambda m: (m.datum or date.max, m.uhrzeit or "", -m.id))
    return aktuell


@bp.route("")
def board_daten():
    heute = date.today()
    horizont = heute + timedelta(days=14)
    woche_ende = heute + timedelta(days=6 - heute.weekday())

    auftraege = offene_auftraege()
    auftrag_liste = sorted(
        (a for a in auftraege
         if a.prio == "rot" or (a.liefertermin and a.liefertermin <= horizont)),
        key=lambda a: (a.liefertermin or date.max, a.kommission),
    )

    aufgaben = (
        VerlaufEintrag.query.join(Item)
        .filter(VerlaufEintrag.status != "erledigt",
                VerlaufEintrag.faelligkeit.isnot(None),
                VerlaufEintrag.faelligkeit <= heute + timedelta(days=7),
                db.or_(Item.archiviert.is_(None), Item.archiviert.is_(False)))
        .order_by(VerlaufEintrag.faelligkeit)
        .all()
    )

    angebote_offen = Item.query.filter(
        Item.type == "angebot", Item.angebot_status.in_(ANGEBOT_OFFEN)).count()

    return jsonify({
        "heute": heute.isoformat(),
        "kennzahlen": {
            "auftraegeOffen": len(auftraege),
            "auftraegeUeberfaellig": sum(1 for a in auftraege if a.liefertermin and a.liefertermin < heute),
            "lieferungDieseWoche": sum(1 for a in auftraege if a.liefertermin and heute <= a.liefertermin <= woche_ende),
            "prioRot": sum(1 for a in auftraege if a.prio == "rot"),
            "angeboteOffen": angebote_offen,
            "aufgabenUeberfaellig": sum(1 for v in aufgaben if v.faelligkeit < heute),
        },
        "auftraege": [{
            "kommission": a.kommission,
            "kunde": a.kunde,
            "lieferumfang": a.lieferumfang,
            "prio": a.prio,
            "status": a.auftrag_status,
            "liefertermin": a.liefertermin.isoformat() if a.liefertermin else None,
            "projektleiter": a.projektleiter,
        } for a in auftrag_liste],
        "aufgaben": [{
            "text": v.text,
            "verantwortlich": v.verantwortlich,
            "faelligkeit": v.faelligkeit.isoformat(),
            "kommission": v.item.kommission,
            "kunde": v.item.kunde,
        } for v in aufgaben],
        "meldungen": [m.to_dict() for m in aktuelle_meldungen(heute)],
    })


@bp.route("/meldungen")
def meldungen_liste():
    return jsonify([m.to_dict() for m in
                    BoardMeldung.query.order_by(BoardMeldung.created_at.desc()).all()])


@bp.route("/meldungen", methods=["POST"])
def meldung_anlegen():
    data = request.get_json(force=True)
    typ = data.get("typ")
    titel = (data.get("titel") or "").strip()
    if typ not in TYPEN or not titel:
        return jsonify({"error": "Typ und Titel sind Pflicht."}), 400
    m = BoardMeldung(
        typ=typ,
        titel=titel,
        text=(data.get("text") or "").strip() or None,
        datum=parse_date(data.get("datum")),
        uhrzeit=(data.get("uhrzeit") or "").strip() or None,
        sichtbar_bis=parse_date(data.get("sichtbarBis")),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201


@bp.route("/meldungen/<int:meldung_id>", methods=["DELETE"])
def meldung_loeschen(meldung_id):
    db.session.delete(BoardMeldung.query.get_or_404(meldung_id))
    db.session.commit()
    return "", 204
