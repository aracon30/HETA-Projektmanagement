from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    abteilung = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(160), nullable=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "abteilung": self.abteilung, "email": self.email}


class Item(db.Model):
    """Eine Anfrage, ein Angebot oder ein Auftrag (type unterscheidet)."""
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'anfrage' | 'angebot' | 'auftrag'
    kommission = db.Column(db.String(60), nullable=False)  # bei Anfragen leer (bekommen erst bei Annahme eine Angebotsnummer)
    kunde = db.Column(db.String(200), nullable=False)
    lieferumfang = db.Column(db.Text, nullable=True)
    ordner_pfad = db.Column(db.String(500), nullable=True)
    erp_ab_nummer = db.Column(db.String(60), nullable=True)
    quelle = db.Column(db.String(20), nullable=True, default="manuell")  # 'erp-import' | 'manuell'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Auftrag-spezifisch
    prio = db.Column(db.String(10), nullable=True)          # rot | gelb | gruen
    liefertermin = db.Column(db.Date, nullable=True)
    auftrag_status = db.Column(db.String(20), nullable=True)  # neu | in_bearbeitung | in_fertigung | versandbereit | erledigt

    # Angebot-spezifisch
    angebot_status = db.Column(db.String(20), nullable=True)  # in_bearbeitung | versendet | wiedervorlage | gewonnen | verloren
    wert = db.Column(db.String(40), nullable=True)
    wiedervorlage = db.Column(db.Date, nullable=True)

    # Anfrage-spezifisch
    anfrage_status = db.Column(db.String(20), nullable=True)  # neu | in_pruefung | angenommen | abgelehnt
    zustaendig = db.Column(db.String(120), nullable=True)
    ablehnungsgrund = db.Column(db.String(300), nullable=True)

    verlauf = db.relationship(
        "VerlaufEintrag", backref="item", cascade="all, delete-orphan",
        order_by="VerlaufEintrag.created_at"
    )
    phasen = db.relationship(
        "Phase", backref="item", cascade="all, delete-orphan",
        order_by="Phase.start"
    )

    def to_dict(self):
        base = {
            "id": self.id,
            "type": self.type,
            "kommission": self.kommission,
            "kunde": self.kunde,
            "lieferumfang": self.lieferumfang,
            "ordnerPfad": self.ordner_pfad,
            "erstelltAm": self.created_at.isoformat() if self.created_at else None,
            "verlauf": [v.to_dict() for v in self.verlauf],
            "phasen": [p.to_dict() for p in self.phasen],
        }
        if self.type == "auftrag":
            base.update({
                "prio": self.prio,
                "liefertermin": self.liefertermin.isoformat() if self.liefertermin else None,
                "status": self.auftrag_status,
            })
        elif self.type == "angebot":
            base.update({
                "status": self.angebot_status,
                "wert": self.wert,
                "wiedervorlage": self.wiedervorlage.isoformat() if self.wiedervorlage else None,
            })
        else:
            base.update({
                "status": self.anfrage_status,
                "zustaendig": self.zustaendig,
                "ablehnungsgrund": self.ablehnungsgrund,
            })
        return base


class Phase(db.Model):
    """Ein Zeitabschnitt innerhalb eines Auftrags (z.B. Konstruktion, Fertigung),
    für das detaillierte Gantt-Diagramm in der Auftragsansicht."""
    __tablename__ = "phasen"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    bezeichnung = db.Column(db.String(120), nullable=False)
    start = db.Column(db.Date, nullable=False)
    ende = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "bezeichnung": self.bezeichnung,
            "start": self.start.isoformat() if self.start else None,
            "ende": self.ende.isoformat() if self.ende else None,
        }


class VerlaufEintrag(db.Model):
    __tablename__ = "verlauf_eintraege"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    erstellt_von = db.Column(db.String(120), nullable=True)
    verantwortlich = db.Column(db.String(120), nullable=True)
    faelligkeit = db.Column(db.Date, nullable=True)
    # Auftrag: offen | in_bearbeitung | wartet_intern | wartet_extern | erledigt
    # Angebot: offen | in_bearbeitung | wartet_kunde | erledigt
    status = db.Column(db.String(20), default="offen")
    aufgabe_erstellt = db.Column(db.Boolean, default=False)
    msgraph_list_id = db.Column(db.String(200), nullable=True)
    msgraph_task_id = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status_changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "erstelltVon": self.erstellt_von,
            "erstelltAm": self.created_at.isoformat() + "Z" if self.created_at else None,
            "statusGeaendertAm": self.status_changed_at.isoformat() + "Z" if self.status_changed_at else None,
            "verantwortlich": self.verantwortlich,
            "faelligkeit": self.faelligkeit.isoformat() if self.faelligkeit else None,
            "status": self.status,
            "aufgabe": self.aufgabe_erstellt,
        }
