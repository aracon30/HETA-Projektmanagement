import os
from datetime import datetime, date
from flask import Flask, jsonify, request, send_from_directory
from models import db, User, Item, VerlaufEintrag, Phase, LieferterminHistorie, AuftragPosition
import graph_client
from erp_import import parse_positionsansicht_auftrag, hat_offene_position
from prozesse_api import bp as prozesse_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "projektbesprechung.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.register_blueprint(prozesse_bp)


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


# ---------- Statische Auslieferung des Frontends ----------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ---------- Nutzer ----------
@app.route("/api/users")
def get_users():
    return jsonify([u.to_dict() for u in User.query.order_by(User.name).all()])


# ---------- Items (Aufträge / Angebote) ----------
@app.route("/api/items")
def get_items():
    item_type = request.args.get("type")
    query = Item.query
    if item_type:
        query = query.filter_by(type=item_type)
    items = query.order_by(Item.created_at.desc()).all()
    return jsonify([i.to_dict() for i in items])


@app.route("/api/items/<int:item_id>")
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True)
    item = Item(
        type=data["type"],
        kommission=data["kommission"],
        kunde=data["kunde"],
        lieferumfang=data.get("lieferumfang"),
        ordner_pfad=data.get("ordnerPfad"),
        erp_ab_nummer=data.get("erpAbNummer"),
        quelle=data.get("quelle", "manuell"),
    )
    if item.type == "auftrag":
        item.prio = data.get("prio", "gelb")
        item.liefertermin = parse_date(data.get("liefertermin"))
        item.auftrag_status = data.get("status", "neu")
        item.lieferbedingungen = data.get("lieferbedingungen")
        item.ursprungsauftrag = data.get("ursprungsauftrag")
        item.zul_geliefert = data.get("zulGeliefert")
        item.bu = data.get("bu")
        item.t = data.get("t")
        item.projektleiter = data.get("projektleiter")
    elif item.type == "angebot":
        item.angebot_status = data.get("status", "in_bearbeitung")
        item.wert = data.get("wert")
        item.wiedervorlage = parse_date(data.get("wiedervorlage"))
    else:
        item.anfrage_status = data.get("status", "neu")
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    if "liefertermin" in data:
        neuer_termin = parse_date(data.get("liefertermin"))
        if neuer_termin != item.liefertermin:
            db.session.add(LieferterminHistorie(
                item_id=item.id,
                alter_termin=item.liefertermin,
                neuer_termin=neuer_termin,
                kommentar=data.get("lieferterminKommentar") or None,
            ))
            item.liefertermin = neuer_termin
    if "status" in data:
        if item.type == "auftrag":
            item.auftrag_status = data["status"]
        elif item.type == "angebot":
            item.angebot_status = data["status"]
        else:
            item.anfrage_status = data["status"]
    if "prio" in data and item.type == "auftrag":
        item.prio = data["prio"]
    if "lieferbedingungen" in data and item.type == "auftrag":
        item.lieferbedingungen = data.get("lieferbedingungen")
    if "ursprungsauftrag" in data and item.type == "auftrag":
        item.ursprungsauftrag = data.get("ursprungsauftrag")
    if "zulGeliefert" in data and item.type == "auftrag":
        item.zul_geliefert = data.get("zulGeliefert")
    if "bu" in data and item.type == "auftrag":
        item.bu = data.get("bu")
    if "t" in data and item.type == "auftrag":
        item.t = data.get("t")
    if "projektleiter" in data and item.type == "auftrag":
        item.projektleiter = data.get("projektleiter")
    if "wert" in data and item.type == "angebot":
        item.wert = data.get("wert")
    if "wiedervorlage" in data and item.type == "angebot":
        item.wiedervorlage = parse_date(data.get("wiedervorlage"))
    if "zustaendig" in data and item.type == "anfrage":
        item.zustaendig = data.get("zustaendig")
    if "ablehnungsgrund" in data and item.type == "anfrage":
        item.ablehnungsgrund = data.get("ablehnungsgrund")
    if "ordnerPfad" in data:
        item.ordner_pfad = data.get("ordnerPfad")
    if "kunde" in data and data.get("kunde"):
        item.kunde = data["kunde"]
    if "lieferumfang" in data:
        item.lieferumfang = data.get("lieferumfang")
    db.session.commit()
    return jsonify(item.to_dict())


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return "", 204


# ---------- Excel-Import (Positionsansicht Auftrag) ----------
@app.route("/api/import/auftraege/preview", methods=["POST"])
def import_auftraege_preview():
    """Liest eine hochgeladene 'Positionsansicht Auftrag.xlsm' ein und liefert
    die daraus erkannten Aufträge, die noch nicht im Tool angelegt sind."""
    upload = request.files.get("file")
    if not upload or not upload.filename:
        return jsonify({"error": "Keine Datei hochgeladen."}), 400
    try:
        kandidaten = parse_positionsansicht_auftrag(upload.stream)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Datei konnte nicht gelesen werden: " + str(exc)}), 400

    bestehende_ab = {
        i.erp_ab_nummer for i in Item.query.filter(Item.erp_ab_nummer.isnot(None)).all()
    }
    bestehende_kommission = {i.kommission for i in Item.query.filter_by(type="auftrag").all()}

    neu = []
    uebersprungen = 0
    historisch = 0
    for k in kandidaten:
        if not hat_offene_position(k):
            historisch += 1
            continue
        if k["erpAbNummer"] in bestehende_ab or k["kommission"] in bestehende_kommission:
            uebersprungen += 1
            continue
        neu.append({**k, "liefertermin": k["liefertermin"].isoformat() if k["liefertermin"] else None})

    neu.sort(key=lambda k: (k["jahr"], k["abNummer"]), reverse=True)
    for k in neu:
        del k["jahr"]
        del k["abNummer"]

    return jsonify({"neu": neu, "uebersprungen": uebersprungen, "historisch": historisch})


@app.route("/api/import/auftraege/confirm", methods=["POST"])
def import_auftraege_confirm():
    """Legt die vom Nutzer ausgewählten Import-Kandidaten als Aufträge an."""
    data = request.get_json(force=True)
    erstellt = []
    for k in data.get("items", []):
        item = Item(
            type="auftrag",
            kommission=k["kommission"],
            kunde=k["kunde"],
            lieferumfang=k.get("lieferumfang"),
            ordner_pfad=k.get("ordnerPfad"),
            erp_ab_nummer=k.get("erpAbNummer"),
            quelle="erp-import",
            prio="gelb",
            liefertermin=parse_date(k.get("liefertermin")),
            auftrag_status="neu",
            lieferbedingungen=k.get("lieferbedingungen"),
            ursprungsauftrag=k.get("ursprungsauftrag"),
            zul_geliefert=k.get("zulGeliefert"),
            bu=k.get("bu"),
            t=k.get("t"),
        )
        db.session.add(item)
        db.session.flush()  # item.id wird für die Positionen benötigt
        for i, pos in enumerate(k.get("positionen", [])):
            db.session.add(AuftragPosition(
                item_id=item.id,
                position=pos.get("position"),
                beschreibung=pos.get("beschreibung") or "",
                liefertermin=parse_date(pos.get("liefertermin")),
                reihenfolge=i,
            ))
        erstellt.append(item)
    db.session.commit()
    return jsonify([i.to_dict() for i in erstellt]), 201


# ---------- Verlaufseinträge ----------
@app.route("/api/items/<int:item_id>/verlauf", methods=["POST"])
def add_verlauf(item_id):
    Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    eintrag = VerlaufEintrag(
        item_id=item_id,
        text=data["text"],
        erstellt_von=data.get("erstelltVon", "Unbekannt"),
        verantwortlich=data.get("verantwortlich"),
        faelligkeit=parse_date(data.get("faelligkeit")),
        status="offen",
        aufgabe_erstellt=False,
    )
    db.session.add(eintrag)
    db.session.commit()
    return jsonify(eintrag.to_dict()), 201


@app.route("/api/verlauf/<int:eintrag_id>/aufgabe", methods=["POST"])
def create_aufgabe(eintrag_id):
    """Legt die Aufgabe in Microsoft To Do der zuständigen Person an (falls
    GRAPH_* Umgebungsvariablen gesetzt sind), sonst nur lokale Markierung."""
    eintrag = VerlaufEintrag.query.get_or_404(eintrag_id)
    data = request.get_json(force=True)
    eintrag.verantwortlich = data.get("verantwortlich", eintrag.verantwortlich)
    if data.get("faelligkeit"):
        eintrag.faelligkeit = parse_date(data.get("faelligkeit"))
    if data.get("text"):
        eintrag.text = data.get("text")

    if graph_client.is_configured() and eintrag.verantwortlich:
        user = User.query.filter_by(name=eintrag.verantwortlich).first()
        if user and user.email:
            item = eintrag.item
            title = f"{item.kommission} — {item.kunde}"
            due_iso = eintrag.faelligkeit.isoformat() if eintrag.faelligkeit else None
            try:
                result = graph_client.create_task(user.email, title, eintrag.text, due_iso)
                if result:
                    eintrag.msgraph_list_id, eintrag.msgraph_task_id = result
            except Exception as exc:
                return jsonify({"error": "Graph-API-Fehler: " + str(exc)}), 502

    eintrag.aufgabe_erstellt = True
    db.session.commit()
    return jsonify(eintrag.to_dict())


@app.route("/api/verlauf/<int:eintrag_id>", methods=["PATCH"])
def update_verlauf(eintrag_id):
    eintrag = VerlaufEintrag.query.get_or_404(eintrag_id)
    data = request.get_json(force=True)
    if "status" in data and data["status"] != eintrag.status:
        eintrag.status = data["status"]
        eintrag.status_changed_at = datetime.utcnow()
    if "text" in data:
        eintrag.text = data["text"]
    if "verantwortlich" in data:
        eintrag.verantwortlich = data["verantwortlich"]
    if "faelligkeit" in data:
        eintrag.faelligkeit = parse_date(data["faelligkeit"])
    db.session.commit()
    return jsonify(eintrag.to_dict())


@app.route("/api/sync-aufgaben", methods=["POST"])
def sync_aufgaben():
    """Fragt bei Microsoft To Do nach, ob mit einer echten To-Do-Aufgabe
    verknüpfte Verlaufseinträge dort inzwischen als erledigt markiert wurden,
    und übernimmt das lokal (einseitig: To Do -> Auftragspipeline)."""
    if not graph_client.is_configured():
        return jsonify({"error": "Microsoft-To-Do-Anbindung ist nicht konfiguriert."}), 400

    kandidaten = VerlaufEintrag.query.filter(
        VerlaufEintrag.aufgabe_erstellt.is_(True),
        VerlaufEintrag.msgraph_task_id.isnot(None),
        VerlaufEintrag.status != "erledigt",
    ).all()

    aktualisiert = 0
    fehler = 0
    for eintrag in kandidaten:
        user = User.query.filter_by(name=eintrag.verantwortlich).first()
        if not user or not user.email:
            continue
        try:
            erledigt = graph_client.get_task_status(
                user.email, eintrag.msgraph_list_id, eintrag.msgraph_task_id
            )
            if erledigt:
                eintrag.status = "erledigt"
                eintrag.status_changed_at = datetime.utcnow()
                aktualisiert += 1
        except Exception:
            fehler += 1

    db.session.commit()
    return jsonify({"geprueft": len(kandidaten), "aktualisiert": aktualisiert, "fehler": fehler})


@app.route("/api/verlauf/<int:eintrag_id>", methods=["DELETE"])
def delete_verlauf(eintrag_id):
    eintrag = VerlaufEintrag.query.get_or_404(eintrag_id)
    db.session.delete(eintrag)
    db.session.commit()
    return "", 204


# ---------- Phasen (detailliertes Gantt je Auftrag) ----------
@app.route("/api/items/<int:item_id>/phasen", methods=["POST"])
def add_phase(item_id):
    Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    phase = Phase(
        item_id=item_id,
        bezeichnung=data["bezeichnung"],
        start=parse_date(data["start"]),
        ende=parse_date(data["ende"]),
    )
    db.session.add(phase)
    db.session.commit()
    return jsonify(phase.to_dict()), 201


@app.route("/api/phasen/<int:phase_id>", methods=["PATCH"])
def update_phase(phase_id):
    phase = Phase.query.get_or_404(phase_id)
    data = request.get_json(force=True)
    if "bezeichnung" in data:
        phase.bezeichnung = data["bezeichnung"]
    if "start" in data:
        phase.start = parse_date(data["start"])
    if "ende" in data:
        phase.ende = parse_date(data["ende"])
    db.session.commit()
    return jsonify(phase.to_dict())


@app.route("/api/phasen/<int:phase_id>", methods=["DELETE"])
def delete_phase(phase_id):
    phase = Phase.query.get_or_404(phase_id)
    db.session.delete(phase)
    db.session.commit()
    return "", 204


# ---------- Auftrags-Positionen (mehrere Liefertermine je Auftrag) ----------
@app.route("/api/items/<int:item_id>/positionen", methods=["POST"])
def add_position(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    beschreibung = data.get("beschreibung")
    if not beschreibung:
        return jsonify({"error": "Beschreibung ist ein Pflichtfeld."}), 400
    position = AuftragPosition(
        item_id=item.id,
        position=data.get("position"),
        beschreibung=beschreibung,
        liefertermin=parse_date(data.get("liefertermin")),
        reihenfolge=len(item.positionen),
    )
    db.session.add(position)
    db.session.commit()
    return jsonify(position.to_dict()), 201


@app.route("/api/positionen/<int:position_id>", methods=["PATCH"])
def update_position(position_id):
    position = AuftragPosition.query.get_or_404(position_id)
    data = request.get_json(force=True)
    if "position" in data:
        position.position = data.get("position")
    if "beschreibung" in data:
        position.beschreibung = data["beschreibung"]
    if "liefertermin" in data:
        neuer_termin = parse_date(data.get("liefertermin"))
        if neuer_termin != position.liefertermin:
            db.session.add(LieferterminHistorie(
                item_id=position.item_id,
                position_id=position.id,
                alter_termin=position.liefertermin,
                neuer_termin=neuer_termin,
                kommentar=data.get("lieferterminKommentar") or None,
            ))
            position.liefertermin = neuer_termin
    db.session.commit()
    return jsonify(position.to_dict())


@app.route("/api/positionen/<int:position_id>", methods=["DELETE"])
def delete_position(position_id):
    position = AuftragPosition.query.get_or_404(position_id)
    db.session.delete(position)
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
