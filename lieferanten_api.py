"""
Lieferantenbewertung nach ISO 9001 Kap. 8.4 (Stufe 1, siehe
docs/KONZEPT-LIEFERANTEN.md): Lieferung bewerten, Jahresbewertung, Auswertung
+ CSV-Export. Übernimmt dieselbe Rechenlogik wie die bisherige Excel-Datei
Lieferantenbewertung_HETA.xlsx (siehe Testfälle in berechne_ergebnis()).

Noch nicht Teil von Stufe 1 (siehe CLAUDE.md): Maßnahmenverwaltung mit
Mail-Versand, Einstellungs-Oberfläche mit Katalogversionierung — dafür
existieren schon Felder (katalog_version), aber noch keine Bedienoberfläche.

Zertifikate mit Ablaufwarnung (FB-0019, siehe weiter unten und
docs/KONZEPT-LIEFERANTEN-ZERTIFIKATE.md) sind seit 13.11.2026 umgesetzt.
"""
import csv
import io
from datetime import date, datetime

from flask import Blueprint, jsonify, request, Response, send_file
from openpyxl import Workbook
from openpyxl.styles import Font

from models import (
    db, Firma, BewertungKriterium, BewertungEinstellung,
    Lieferungsbewertung, Jahresbewertung, BewertungNote,
    LieferantenZertifizierung, ALLE_ZERTIFIKAT_FELDER, WARN_TAGE_ZERTIFIKATE,
)

bp = Blueprint("lieferanten", __name__, url_prefix="/api")


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def einstellungen():
    """Alle bewertung_einstellungen als dict, mit den Startwerten als
    Rückfallebene, falls seed_lieferanten.py noch nicht gelaufen ist."""
    from lieferanten_daten import EINSTELLUNGEN
    werte = dict(EINSTELLUNGEN)
    werte.update({e.key: e.value for e in BewertungEinstellung.query.all()})
    return werte


def notenwerte(e):
    return {i: float(e[f"notenwert_{i}"]) for i in (1, 2, 3, 4)}


def berechne_ergebnis(noten, kriterien, nwerte):
    """noten: {kriterium_id: note (1-4)}. Nicht bewertete Kriterien (fehlen im
    dict) zählen nicht mit — siehe Konzept 2.2. Testfall: Noten 2/1/2/1 bei
    Gewichten 30/15/35/20 (Lieferungskriterien in dieser Reihenfolge) ergibt
    80,5 %."""
    gewicht_summe = 0.0
    punkte_summe = 0.0
    for k in kriterien:
        note = noten.get(k.id)
        if note is None:
            continue
        gewicht_summe += k.gewicht
        punkte_summe += k.gewicht * nwerte[note]
    if gewicht_summe == 0:
        return None
    return round(punkte_summe / gewicht_summe, 2)


def berechne_jahresergebnis(lieferungs_ergebnisse, jahresbewertung_ergebnis, e):
    """60 % Ø Lieferungsbewertungen + 40 % Jahresbewertung (einstellbar über
    anteil_lieferung/anteil_jahr). Fehlt ein Teil, zählt nur der vorhandene.
    Testfall: Ø 83,25 % + Jahr 86,5 % (60/40) ergibt 84,55 % (Klasse B)."""
    werte = [x for x in lieferungs_ergebnisse if x is not None]
    avg_lieferung = round(sum(werte) / len(werte), 2) if werte else None
    anteil_lieferung = float(e["anteil_lieferung"])
    anteil_jahr = float(e["anteil_jahr"])
    if avg_lieferung is not None and jahresbewertung_ergebnis is not None:
        return round(anteil_lieferung * avg_lieferung + anteil_jahr * jahresbewertung_ergebnis, 2), "vollständig"
    if avg_lieferung is not None:
        return avg_lieferung, "nur Lieferungen"
    if jahresbewertung_ergebnis is not None:
        return round(jahresbewertung_ergebnis, 2), "nur Jahresbewertung"
    return None, "keine Daten"


def klasse_fuer(ergebnis, e):
    if ergebnis is None:
        return None
    if ergebnis >= float(e["klasse_a_min"]):
        return "A"
    if ergebnis >= float(e["klasse_b_min"]):
        return "B"
    return "C"


def noten_aus_request(data):
    """{"noten": {"3": 2, "7": 1}} -> {3: 2, 7: 1}, überspringt leere/ungültige."""
    result = {}
    for kriterium_id, note in (data.get("noten") or {}).items():
        try:
            kid, n = int(kriterium_id), int(note)
        except (TypeError, ValueError):
            continue
        if n in (1, 2, 3, 4):
            result[kid] = n
    return result


def speichere_noten(bewertung_typ, bewertung_id, noten):
    BewertungNote.query.filter_by(bewertung_typ=bewertung_typ, bewertung_id=bewertung_id).delete()
    for kriterium_id, note in noten.items():
        db.session.add(BewertungNote(
            bewertung_typ=bewertung_typ, bewertung_id=bewertung_id, kriterium_id=kriterium_id, note=note,
        ))


@bp.route("/bewertung/katalog")
def get_katalog():
    kriterien = BewertungKriterium.query.filter_by(aktiv=True).order_by(
        BewertungKriterium.ebene, BewertungKriterium.reihenfolge
    ).all()
    return jsonify({
        "kriterien": [k.to_dict() for k in kriterien],
        "einstellungen": einstellungen(),
    })


# ---------- Lieferungsbewertung ----------
@bp.route("/lieferungsbewertungen", methods=["GET"])
def list_lieferungsbewertungen():
    q = Lieferungsbewertung.query
    firma_id = request.args.get("firmaId", type=int)
    if firma_id:
        q = q.filter_by(firma_id=firma_id)
    jahr = request.args.get("jahr", type=int)
    if jahr:
        q = q.filter(db.extract("year", Lieferungsbewertung.datum) == jahr)
    bewertungen = q.order_by(Lieferungsbewertung.datum.desc()).all()
    return jsonify([b.to_dict() for b in bewertungen])


@bp.route("/lieferungsbewertungen", methods=["POST"])
def add_lieferungsbewertung():
    data = request.get_json(force=True)
    firma_id = data.get("firmaId")
    if not firma_id or not Firma.query.get(firma_id):
        return jsonify({"error": "Firma ist ein Pflichtfeld."}), 400
    noten = noten_aus_request(data)
    if not noten:
        return jsonify({"error": "Mindestens ein Kriterium muss bewertet werden."}), 400

    kriterien = BewertungKriterium.query.filter_by(ebene="lieferung", aktiv=True).all()
    ergebnis = berechne_ergebnis(noten, kriterien, notenwerte(einstellungen()))

    b = Lieferungsbewertung(
        firma_id=firma_id,
        datum=parse_date(data.get("datum")) or date.today(),
        bestell_nr=data.get("bestellNr"),
        item_id=data.get("itemId"),
        bewerter=data.get("bewerter"),
        bemerkung=data.get("bemerkung"),
        ergebnis_gespeichert=ergebnis,
    )
    db.session.add(b)
    db.session.flush()
    speichere_noten("lieferung", b.id, noten)
    db.session.commit()
    result = b.to_dict()
    result["klasse"] = klasse_fuer(ergebnis, einstellungen())
    return jsonify(result), 201


@bp.route("/lieferungsbewertungen/<int:bewertung_id>", methods=["DELETE"])
def delete_lieferungsbewertung(bewertung_id):
    b = Lieferungsbewertung.query.get_or_404(bewertung_id)
    BewertungNote.query.filter_by(bewertung_typ="lieferung", bewertung_id=b.id).delete()
    db.session.delete(b)
    db.session.commit()
    return "", 204


# ---------- Jahresbewertung ----------
@bp.route("/jahresbewertungen", methods=["GET"])
def list_jahresbewertungen():
    q = Jahresbewertung.query
    jahr = request.args.get("jahr", type=int)
    if jahr:
        q = q.filter_by(jahr=jahr)
    firma_id = request.args.get("firmaId", type=int)
    if firma_id:
        q = q.filter_by(firma_id=firma_id)
    return jsonify([b.to_dict() for b in q.order_by(Jahresbewertung.jahr.desc()).all()])


@bp.route("/jahresbewertungen/faellig")
def jahresbewertungen_faellig():
    """Freigegebene Lieferanten mit Lieferungen im Jahr, aber ohne
    Jahresbewertung (Konzept 3.3)."""
    jahr = request.args.get("jahr", type=int) or date.today().year
    bewertete_firma_ids = {b.firma_id for b in Jahresbewertung.query.filter_by(jahr=jahr).all()}
    firma_ids_mit_lieferung = {
        b.firma_id for b in Lieferungsbewertung.query.filter(
            db.extract("year", Lieferungsbewertung.datum) == jahr
        ).all()
    }
    faellige_ids = firma_ids_mit_lieferung - bewertete_firma_ids
    firmen = Firma.query.filter(Firma.id.in_(faellige_ids)).order_by(Firma.name).all() if faellige_ids else []
    return jsonify([f.to_dict() for f in firmen])


@bp.route("/jahresbewertungen", methods=["POST"])
def add_jahresbewertung():
    data = request.get_json(force=True)
    firma_id = data.get("firmaId")
    jahr = data.get("jahr")
    if not firma_id or not Firma.query.get(firma_id):
        return jsonify({"error": "Firma ist ein Pflichtfeld."}), 400
    if not jahr:
        return jsonify({"error": "Jahr ist ein Pflichtfeld."}), 400
    if Jahresbewertung.query.filter_by(firma_id=firma_id, jahr=jahr).first():
        return jsonify({"error": f"Für dieses Jahr ({jahr}) existiert bereits eine Jahresbewertung."}), 400
    noten = noten_aus_request(data)
    if not noten:
        return jsonify({"error": "Mindestens ein Kriterium muss bewertet werden."}), 400

    kriterien = BewertungKriterium.query.filter_by(ebene="jahr", aktiv=True).all()
    ergebnis = berechne_ergebnis(noten, kriterien, notenwerte(einstellungen()))

    b = Jahresbewertung(
        firma_id=firma_id, jahr=jahr,
        datum=parse_date(data.get("datum")) or date.today(),
        bewerter=data.get("bewerter"),
        bemerkung=data.get("bemerkung"),
        ergebnis_gespeichert=ergebnis,
    )
    db.session.add(b)
    db.session.flush()
    speichere_noten("jahr", b.id, noten)
    db.session.commit()
    result = b.to_dict()
    result["klasse"] = klasse_fuer(ergebnis, einstellungen())
    return jsonify(result), 201


@bp.route("/jahresbewertungen/<int:bewertung_id>", methods=["DELETE"])
def delete_jahresbewertung(bewertung_id):
    b = Jahresbewertung.query.get_or_404(bewertung_id)
    BewertungNote.query.filter_by(bewertung_typ="jahr", bewertung_id=b.id).delete()
    db.session.delete(b)
    db.session.commit()
    return "", 204


# ---------- Auswertung ----------
def _auswertung_zeilen(jahr):
    e = einstellungen()
    kriterien_lieferung = BewertungKriterium.query.filter_by(ebene="lieferung", aktiv=True).order_by(
        BewertungKriterium.reihenfolge
    ).all()
    lieferanten = [f for f in Firma.query.filter(Firma.aktiv.is_(True)).order_by(Firma.name).all()
                   if "lieferant" in f.rollen_liste()]

    zeilen = []
    for firma in lieferanten:
        lieferungen = Lieferungsbewertung.query.filter(
            Lieferungsbewertung.firma_id == firma.id,
            db.extract("year", Lieferungsbewertung.datum) == jahr,
        ).all()
        jahresbewertung = Jahresbewertung.query.filter_by(firma_id=firma.id, jahr=jahr).first()

        if not lieferungen and not jahresbewertung:
            continue  # nichts zu diesem Lieferanten in diesem Jahr

        ergebnisse_lieferung = [l.ergebnis_gespeichert for l in lieferungen]
        gesamt, datenbasis = berechne_jahresergebnis(
            ergebnisse_lieferung, jahresbewertung.ergebnis_gespeichert if jahresbewertung else None, e
        )
        klasse = klasse_fuer(gesamt, e)

        # Vorjahresvergleich wie im Blatt "Auswertung" der Excel-Datei:
        # "Gesamt <Vorjahr>" aus denselben zwei Teilen wie oben (nicht nur
        # die rohe Jahresbewertung — sonst vergleicht man zwei
        # unterschiedliche Kennzahlen), plus "Trend (%-Pkt.)" = Gesamt - Gesamt Vorjahr.
        lieferungen_vorjahr = Lieferungsbewertung.query.filter(
            Lieferungsbewertung.firma_id == firma.id,
            db.extract("year", Lieferungsbewertung.datum) == jahr - 1,
        ).all()
        jahresbewertung_vorjahr = Jahresbewertung.query.filter_by(firma_id=firma.id, jahr=jahr - 1).first()
        gesamt_vorjahr, _ = berechne_jahresergebnis(
            [l.ergebnis_gespeichert for l in lieferungen_vorjahr],
            jahresbewertung_vorjahr.ergebnis_gespeichert if jahresbewertung_vorjahr else None,
            e,
        )
        trend = round(gesamt - gesamt_vorjahr, 2) if gesamt is not None and gesamt_vorjahr is not None else None

        avg_je_kriterium = {}
        for k in kriterien_lieferung:
            noten = [n.note for l in lieferungen for n in l.noten_liste() if n.kriterium_id == k.id]
            avg_je_kriterium[k.bezeichnung] = round(sum(noten) / len(noten), 2) if noten else None

        zeilen.append({
            "firma": firma,
            "anzahlLieferungen": len(lieferungen),
            "avgLieferungen": round(sum(ergebnisse_lieferung) / len(ergebnisse_lieferung), 2) if ergebnisse_lieferung else None,
            "jahresbewertung": jahresbewertung.ergebnis_gespeichert if jahresbewertung else None,
            "gesamt": gesamt,
            "datenbasis": datenbasis,
            "klasse": klasse,
            "gesamtVorjahr": gesamt_vorjahr,
            "trend": trend,
            "konsequenz": e.get(f"konsequenz_{klasse.lower()}") if klasse else None,
            "avgJeKriterium": avg_je_kriterium,
        })
    return zeilen


@bp.route("/lieferanten/auswertung")
def auswertung():
    jahr = request.args.get("jahr", type=int) or date.today().year
    zeilen = _auswertung_zeilen(jahr)

    if request.args.get("format") == "csv":
        kriterien_lieferung = BewertungKriterium.query.filter_by(ebene="lieferung", aktiv=True).order_by(
            BewertungKriterium.reihenfolge
        ).all()
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(
            ["Lieferant", "Warengruppe", "Freigabestatus", f"Lieferungen {jahr}", f"Ø Lieferungen {jahr}",
             f"Jahresbewertung {jahr}", f"Gesamt {jahr}", "Datenbasis", f"Klasse {jahr}", f"Gesamt {jahr - 1}",
             "Trend (%-Pkt.)", "Konsequenz"] +
            [f"Ø Note: {k.bezeichnung}" for k in kriterien_lieferung]
        )
        for z in zeilen:
            writer.writerow([
                z["firma"].name, z["firma"].warengruppe or "", z["firma"].freigabestatus or "",
                z["anzahlLieferungen"], z["avgLieferungen"], z["jahresbewertung"], z["gesamt"],
                z["datenbasis"], z["klasse"], z["gesamtVorjahr"], z["trend"], z["konsequenz"],
            ] + [z["avgJeKriterium"].get(k.bezeichnung) for k in kriterien_lieferung])
        return Response(
            buf.getvalue(), mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="lieferanten_auswertung_{jahr}.csv"'},
        )

    return jsonify([{
        "firmaId": z["firma"].id,
        "firmaName": z["firma"].name,
        "warengruppe": z["firma"].warengruppe,
        "freigabestatus": z["firma"].freigabestatus,
        "anzahlLieferungen": z["anzahlLieferungen"],
        "avgLieferungen": z["avgLieferungen"],
        "jahresbewertung": z["jahresbewertung"],
        "gesamt": z["gesamt"],
        "datenbasis": z["datenbasis"],
        "klasse": z["klasse"],
        "gesamtVorjahr": z["gesamtVorjahr"],
        "trend": z["trend"],
        "konsequenz": z["konsequenz"],
        "avgJeKriterium": z["avgJeKriterium"],
    } for z in zeilen])


# ====================================================================
# Zertifikate (FB-0019 "Liste freigegebener Lieferanten", siehe
# docs/KONZEPT-LIEFERANTEN-ZERTIFIKATE.md) — 13.11.2026 umgesetzt
# ====================================================================

def zertifizierung_aus_dict(data, z=None):
    z = z or LieferantenZertifizierung()
    if "firmaId" in data:
        z.firma_id = data.get("firmaId")
    if "warengruppe" in data:
        z.warengruppe = data.get("warengruppe")
    for feld, json_key, _ in ALLE_ZERTIFIKAT_FELDER:
        if json_key in data:
            setattr(z, feld, parse_date(data.get(json_key)))
    if "sperrDatum" in data:
        z.sperr_datum = parse_date(data.get("sperrDatum"))
    if "info" in data:
        z.info = data.get("info")
    if "letzteBestellungJahr" in data:
        z.letzte_bestellung_jahr = data.get("letzteBestellungJahr") or None
    if "letzteBewertungAm" in data:
        z.letzte_bewertung_am = parse_date(data.get("letzteBewertungAm"))
    return z


@bp.route("/lieferanten/zertifikate/normen")
def zertifikat_normen():
    """Feste Liste der 12 Datumsfelder (ISO 9001 + 11 Normen) fürs
    Detailformular im Frontend — eine Quelle statt Duplikat in JS."""
    return jsonify([{"feld": json_key, "label": label} for _, json_key, label in ALLE_ZERTIFIKAT_FELDER])


@bp.route("/lieferanten/zertifikate", methods=["GET"])
def list_zertifikate():
    q = LieferantenZertifizierung.query
    firma_id = request.args.get("firmaId", type=int)
    if firma_id:
        q = q.filter_by(firma_id=firma_id)
    zeilen = q.join(Firma).order_by(Firma.name, LieferantenZertifizierung.warengruppe).all()

    status_filter = request.args.get("status")
    term = (request.args.get("q") or "").strip().lower()
    ergebnisse = []
    for z in zeilen:
        if status_filter == "gesperrt":
            if not z.gesperrt():
                continue
        elif status_filter:
            if z.status() != status_filter:
                continue
        if term and term not in (z.firma.name or "").lower() and term not in (z.warengruppe or "").lower():
            continue
        ergebnisse.append(z.to_dict())
    return jsonify(ergebnisse)


@bp.route("/lieferanten/zertifikate/dashboard")
def zertifikate_dashboard():
    """Kennzahlen wie im Excel-Dashboard: Gesamt / Okay / Bald ablaufend /
    Kritisch (abgelaufen) / Gesperrt."""
    zeilen = LieferantenZertifizierung.query.all()
    return jsonify({
        "gesamt": len(zeilen),
        "okay": sum(1 for z in zeilen if z.status() == "okay"),
        "baldAblaufend": sum(1 for z in zeilen if z.status() == "bald_ablaufend"),
        "kritisch": sum(1 for z in zeilen if z.status() == "abgelaufen"),
        "gesperrt": sum(1 for z in zeilen if z.gesperrt()),
        "warnTage": WARN_TAGE_ZERTIFIKATE,
    })


@bp.route("/lieferanten/zertifikate", methods=["POST"])
def add_zertifikat():
    data = request.get_json(force=True)
    firma_id = data.get("firmaId")
    if not firma_id or not Firma.query.get(firma_id):
        return jsonify({"error": "Firma ist ein Pflichtfeld."}), 400
    z = zertifizierung_aus_dict(data)
    z.created_at = datetime.utcnow()
    db.session.add(z)
    db.session.commit()
    return jsonify(z.to_dict()), 201


@bp.route("/lieferanten/zertifikate/<int:zertifizierung_id>", methods=["PATCH"])
def update_zertifikat(zertifizierung_id):
    z = LieferantenZertifizierung.query.get_or_404(zertifizierung_id)
    data = request.get_json(force=True)
    zertifizierung_aus_dict(data, z)
    db.session.commit()
    return jsonify(z.to_dict())


@bp.route("/lieferanten/zertifikate/<int:zertifizierung_id>", methods=["DELETE"])
def delete_zertifikat(zertifizierung_id):
    z = LieferantenZertifizierung.query.get_or_404(zertifizierung_id)
    db.session.delete(z)
    db.session.commit()
    return "", 204


@bp.route("/lieferanten/zertifikate/export")
def export_zertifikate():
    """Excel-Export für Audits (Entscheidung 12.11.2026: Excel statt PDF wie
    bei der Versandliste, da reine Datentabelle ohne Briefkopf)."""
    zeilen = LieferantenZertifizierung.query.join(Firma).order_by(
        Firma.name, LieferantenZertifizierung.warengruppe
    ).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Zertifikate"
    header = ["Lieferant", "Warengruppe", "Status", "Tage bis Ablauf", "Gesperrt seit"] + \
        [label for _, _, label in ALLE_ZERTIFIKAT_FELDER] + \
        ["Info", "Letzte Bestellung (Jahr)", "Letzte Bewertung"]
    ws.append(header)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    status_label = {"okay": "Okay", "bald_ablaufend": "Bald ablaufend", "abgelaufen": "Abgelaufen"}
    for z in zeilen:
        zeile = [
            z.firma.name if z.firma else "",
            z.warengruppe or "",
            status_label.get(z.status(), "") if z.status() else "",
            z.tage_bis_ablauf(),
            z.sperr_datum.strftime("%d.%m.%Y") if z.sperr_datum else "",
        ]
        for feld, _, _ in ALLE_ZERTIFIKAT_FELDER:
            wert = getattr(z, feld)
            zeile.append(wert.strftime("%d.%m.%Y") if wert else "—")
        zeile += [
            z.info or "",
            z.letzte_bestellung_jahr or "",
            z.letzte_bewertung_am.strftime("%d.%m.%Y") if z.letzte_bewertung_am else "",
        ]
        ws.append(zeile)

    for col in ws.columns:
        laenge = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(laenge + 2, 10), 40)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    dateiname = f"FB-0019_Liste_freigegebener_Lieferanten_{date.today().isoformat()}.xlsx"
    return send_file(
        buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True, download_name=dateiname,
    )
