import os
from datetime import datetime, date
from flask import Flask, jsonify, request, send_from_directory
from models import db, User, Item, VerlaufEintrag, Phase
import graph_client

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "projektbesprechung.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


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
        item.auftrag_status = data.get("status", "offen")
    else:
        item.angebot_status = data.get("status", "in_bearbeitung")
        item.wert = data.get("wert")
        item.wiedervorlage = parse_date(data.get("wiedervorlage"))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(force=True)
    if "liefertermin" in data:
        item.liefertermin = parse_date(data.get("liefertermin"))
    if "status" in data:
        if item.type == "auftrag":
            item.auftrag_status = data["status"]
        else:
            item.angebot_status = data["status"]
    if "prio" in data and item.type == "auftrag":
        item.prio = data["prio"]
    db.session.commit()
    return jsonify(item.to_dict())


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return "", 204


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
    if "status" in data:
        eintrag.status = data["status"]
    db.session.commit()
    return jsonify(eintrag.to_dict())


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
