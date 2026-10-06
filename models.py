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
    lieferbedingungen = db.Column(db.String(200), nullable=True)  # z.B. Incoterm an den Kunden
    ursprungsauftrag = db.Column(db.String(60), nullable=True)  # Referenz auf den Auftrag, aus dem dieser hervorgegangen ist
    zul_geliefert = db.Column(db.String(60), nullable=True)  # Spalte "zul. geliefert" aus dem ERP-Dashboard
    bu = db.Column(db.String(10), nullable=True)  # Business Unit: he | c | hb | s
    t = db.Column(db.String(10), nullable=True)  # Spalte "T" aus dem ERP-Dashboard: F (Fertigung) | H (Handelsware)
    projektleiter = db.Column(db.String(120), nullable=True)  # verantwortliche/r Projektleiter/in (Nutzername)

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
    liefertermin_historie = db.relationship(
        "LieferterminHistorie", backref="item", cascade="all, delete-orphan",
        order_by="LieferterminHistorie.created_at"
    )
    positionen = db.relationship(
        "AuftragPosition", backref="item", cascade="all, delete-orphan",
        order_by="AuftragPosition.reihenfolge"
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
                "lieferterminHistorie": [h.to_dict() for h in self.liefertermin_historie if h.position_id is None],
                "lieferbedingungen": self.lieferbedingungen,
                "ursprungsauftrag": self.ursprungsauftrag,
                "zulGeliefert": self.zul_geliefert,
                "bu": self.bu,
                "t": self.t,
                "projektleiter": self.projektleiter,
                "positionen": [p.to_dict() for p in self.positionen],
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


class LieferterminHistorie(db.Model):
    """Protokolliert jede Änderung eines Liefertermins, damit der ursprüngliche
    (und jeder zwischenzeitliche) Termin nachvollziehbar bleibt. Gehört entweder
    zum Auftrag selbst (position_id leer) oder zu einer seiner Positionen, da ein
    Auftrag mehrere Positionen mit je eigenem Liefertermin haben kann."""
    __tablename__ = "liefertermin_historie"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey("auftrag_positionen.id"), nullable=True)
    alter_termin = db.Column(db.Date, nullable=True)
    neuer_termin = db.Column(db.Date, nullable=True)
    kommentar = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "positionId": self.position_id,
            "alterTermin": self.alter_termin.isoformat() if self.alter_termin else None,
            "neuerTermin": self.neuer_termin.isoformat() if self.neuer_termin else None,
            "kommentar": self.kommentar,
            "erstelltAm": self.created_at.isoformat() + "Z" if self.created_at else None,
        }


class AuftragPosition(db.Model):
    """Eine Position im Lieferumfang eines Auftrags mit eigenem Liefertermin —
    ein Auftrag kann mehrere Positionen mit unterschiedlichen Lieferterminen
    haben (z.B. Teillieferungen)."""
    __tablename__ = "auftrag_positionen"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    position = db.Column(db.String(40), nullable=True)  # z.B. "R0-001"
    beschreibung = db.Column(db.Text, nullable=False)
    liefertermin = db.Column(db.Date, nullable=True)
    reihenfolge = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    historie = db.relationship(
        "LieferterminHistorie", backref="position", cascade="all, delete-orphan",
        order_by="LieferterminHistorie.created_at"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "beschreibung": self.beschreibung,
            "liefertermin": self.liefertermin.isoformat() if self.liefertermin else None,
            "historie": [h.to_dict() for h in self.historie],
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


# ---------- Prozessaufnahme (Reiter "Prozesse") ----------

def _iso(d):
    return d.isoformat() if d else None


class Prozess(db.Model):
    """Knoten der Prozesslandkarte: Kategorie (F/K/U, ohne parent), Haupt- oder
    Teilprozess. Nummerierung folgt der QM-Nummerierung (z.B. K3.1)."""
    __tablename__ = "prozesse"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=True)
    nummer = db.Column(db.String(30), nullable=True)
    bezeichnung = db.Column(db.String(200), nullable=False)
    variante = db.Column(db.String(300), nullable=True)
    verantwortlich = db.Column(db.String(200), nullable=True)
    ausloeser = db.Column(db.Text, nullable=True)
    ergebnis = db.Column(db.Text, nullable=True)
    beteiligte = db.Column(db.Text, nullable=True)
    systeme = db.Column(db.Text, nullable=True)
    vorgaenge_monat = db.Column(db.String(40), nullable=True)
    # vorgeschlagen | laut_aa | aufgenommen | bestaetigt | anforderungen
    aufnahmestatus = db.Column(db.String(30), default="vorgeschlagen")
    geprueft_von = db.Column(db.String(200), nullable=True)
    geprueft_am = db.Column(db.Date, nullable=True)
    notiz = db.Column(db.Text, nullable=True)
    reihenfolge = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kinder = db.relationship(
        "Prozess", backref=db.backref("parent", remote_side=[id]),
        order_by="Prozess.reihenfolge"
    )
    schritte = db.relationship(
        "ProzessSchritt", backref="prozess", cascade="all, delete-orphan",
        order_by="ProzessSchritt.reihenfolge"
    )
    fragen = db.relationship(
        "ProzessFrage", backref="prozess", cascade="all, delete-orphan",
        order_by="ProzessFrage.created_at"
    )
    dokumente = db.relationship("Dokument", backref="prozess", order_by="Dokument.nummer")
    verbindungen_aus = db.relationship(
        "ProzessVerbindung", foreign_keys="ProzessVerbindung.von_id", backref="von",
        cascade="all, delete-orphan"
    )
    verbindungen_ein = db.relationship(
        "ProzessVerbindung", foreign_keys="ProzessVerbindung.nach_id", backref="nach",
        cascade="all, delete-orphan"
    )

    def to_summary(self):
        return {
            "id": self.id,
            "parentId": self.parent_id,
            "nummer": self.nummer,
            "bezeichnung": self.bezeichnung,
            "verantwortlich": self.verantwortlich,
            "aufnahmestatus": self.aufnahmestatus,
            "reihenfolge": self.reihenfolge,
            "anzahlSchritte": len(self.schritte),
            "anzahlFragenOffen": sum(1 for f in self.fragen if f.status == "offen"),
            "anzahlDokumente": len(self.dokumente),
        }

    def to_dict(self):
        base = self.to_summary()
        base.update({
            "variante": self.variante,
            "ausloeser": self.ausloeser,
            "ergebnis": self.ergebnis,
            "beteiligte": self.beteiligte,
            "systeme": self.systeme,
            "vorgaengeMonat": self.vorgaenge_monat,
            "geprueftVon": self.geprueft_von,
            "geprueftAm": _iso(self.geprueft_am),
            "notiz": self.notiz,
            "geaendertAm": self.updated_at.isoformat() + "Z" if self.updated_at else None,
            "schritte": [s.to_dict() for s in self.schritte],
            "fragen": [f.to_dict() for f in self.fragen],
            "dokumente": [d.to_dict() for d in self.dokumente],
        })
        return base


class ProzessSchritt(db.Model):
    """Arbeitsschritt eines Prozesses – Spalten wie Excel-Blatt "Ablaufschritte"."""
    __tablename__ = "prozess_schritte"
    id = db.Column(db.Integer, primary_key=True)
    prozess_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=False)
    reihenfolge = db.Column(db.Integer, default=0)
    taetigkeit = db.Column(db.Text, nullable=False)
    ausfuehrend = db.Column(db.String(300), nullable=True)
    eingaben = db.Column(db.Text, nullable=True)
    system = db.Column(db.Text, nullable=True)
    ergebnis = db.Column(db.Text, nullable=True)
    uebergabe = db.Column(db.Text, nullable=True)
    freigabe = db.Column(db.Text, nullable=True)
    ausnahme = db.Column(db.Text, nullable=True)
    bearbeitungszeit = db.Column(db.String(60), nullable=True)
    wartezeit = db.Column(db.String(60), nullable=True)
    nachweis = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    FELDER = ["taetigkeit", "ausfuehrend", "eingaben", "system", "ergebnis", "uebergabe",
              "freigabe", "ausnahme", "bearbeitungszeit", "wartezeit", "nachweis"]

    def to_dict(self):
        d = {"id": self.id, "prozessId": self.prozess_id, "reihenfolge": self.reihenfolge}
        d.update({f: getattr(self, f) for f in self.FELDER})
        return d


class ProzessFrage(db.Model):
    """Offene Frage zu einem Prozess – Spalten wie Excel-Blatt "Offene Fragen"."""
    __tablename__ = "prozess_fragen"
    id = db.Column(db.Integer, primary_key=True)
    prozess_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=False)
    frage = db.Column(db.Text, nullable=False)
    klaerung_durch = db.Column(db.String(200), nullable=True)
    naechster_schritt = db.Column(db.Text, nullable=True)
    faelligkeit = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="offen")  # offen | beantwortet
    antwort = db.Column(db.Text, nullable=True)
    nachweis = db.Column(db.String(300), nullable=True)
    erstellt_von = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "prozessId": self.prozess_id,
            "frage": self.frage,
            "klaerungDurch": self.klaerung_durch,
            "naechsterSchritt": self.naechster_schritt,
            "faelligkeit": _iso(self.faelligkeit),
            "status": self.status,
            "antwort": self.antwort,
            "nachweis": self.nachweis,
            "erstelltVon": self.erstellt_von,
            "erstelltAm": self.created_at.isoformat() + "Z" if self.created_at else None,
        }


class ProzessVerbindung(db.Model):
    """Übergabe von einem Prozess an einen anderen (Schnittstelle), z.B.
    K3.1 -> K2 "AB per Rundmail". Grundlage der Schnittstellenkarte."""
    __tablename__ = "prozess_verbindungen"
    id = db.Column(db.Integer, primary_key=True)
    von_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=False)
    nach_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=False)
    inhalt = db.Column(db.String(300), nullable=False)
    # email | dashboard | ordner | papier | muendlich | sonstiges | unklar
    weg = db.Column(db.String(20), default="unklar")
    schritt_id = db.Column(db.Integer, db.ForeignKey("prozess_schritte.id"), nullable=True)
    problem = db.Column(db.Boolean, default=False)
    notiz = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "vonId": self.von_id,
            "nachId": self.nach_id,
            "inhalt": self.inhalt,
            "weg": self.weg,
            "schrittId": self.schritt_id,
            "problem": bool(self.problem),
            "notiz": self.notiz,
        }


class StartbestandStand(db.Model):
    """Merkt sich, bis zu welcher Ergänzung (prozess_daten.ERGAENZUNGEN) der
    Startbestand eingespielt ist, damit jede Ergänzung genau einmal läuft."""
    __tablename__ = "startbestand_stand"
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)


class Dokument(db.Model):
    """Vorhandene Arbeitsanweisung (QM-Dokument) mit Auswertungsstand."""
    __tablename__ = "dokumente"
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(40), unique=True, nullable=False)
    titel = db.Column(db.String(300), nullable=False)
    revision = db.Column(db.String(10), nullable=True)
    geltungsbereich = db.Column(db.String(60), nullable=True)
    prozess_id = db.Column(db.Integer, db.ForeignKey("prozesse.id"), nullable=True)
    # nicht_gesichtet | gesichtet | uebernommen
    auswertungsstatus = db.Column(db.String(30), default="nicht_gesichtet")
    notiz = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nummer": self.nummer,
            "titel": self.titel,
            "revision": self.revision,
            "geltungsbereich": self.geltungsbereich,
            "prozessId": self.prozess_id,
            "auswertungsstatus": self.auswertungsstatus,
            "notiz": self.notiz,
        }
