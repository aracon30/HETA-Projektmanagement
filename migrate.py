"""
Migriert eine bestehende projektbesprechung.db auf das neue Schema,
OHNE vorhandene Daten zu löschen. Aufruf:
  ./venv/bin/python migrate.py

Kann gefahrlos mehrfach ausgeführt werden (prüft vorher, ob eine
Spalte schon existiert).
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projektbesprechung.db")

# NUTZER-E-Mail-Muster wie in seed.py: nachname@heta.de, außer Philipp Schreiber
EMAIL_MAP = {
    "Heiko Hensel": "hensel@heta.de",
    "Erik Scharmann": "scharmann@heta.de",
    "Gabriele Häfer": "haefer@heta.de",
    "Häfer, Gabriele": "haefer@heta.de",
    "Sandra Voigt": "voigt@heta.de",
    "Thomas Berger": "berger@heta.de",
    "Julia Krämer": "kraemer@heta.de",
    "Markus Lindt": "lindt@heta.de",
    "Nina Osei": "osei@heta.de",
    "Philipp Schreiber": "p.schreiber@heta.de",
}


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def table_exists(cur, table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def main():
    if not os.path.exists(DB_PATH):
        print(f"Keine Datenbank unter {DB_PATH} gefunden — nichts zu migrieren.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if not column_exists(cur, "users", "email"):
        cur.execute("ALTER TABLE users ADD COLUMN email VARCHAR(160)")
        print("Spalte users.email ergänzt.")
    else:
        print("Spalte users.email existiert bereits.")

    if not column_exists(cur, "users", "webhook_url"):
        cur.execute("ALTER TABLE users ADD COLUMN webhook_url VARCHAR(500)")
        print("Spalte users.webhook_url ergänzt (persönlicher Power-Automate-Flow).")
    else:
        print("Spalte users.webhook_url existiert bereits.")

    if not column_exists(cur, "verlauf_eintraege", "aufgabe_kanal"):
        cur.execute("ALTER TABLE verlauf_eintraege ADD COLUMN aufgabe_kanal VARCHAR(20)")
        print("Spalte verlauf_eintraege.aufgabe_kanal ergänzt (graph/mail/webhook/lokal).")
    else:
        print("Spalte verlauf_eintraege.aufgabe_kanal existiert bereits.")

    if not column_exists(cur, "verlauf_eintraege", "msgraph_list_id"):
        cur.execute("ALTER TABLE verlauf_eintraege ADD COLUMN msgraph_list_id VARCHAR(200)")
        print("Spalte verlauf_eintraege.msgraph_list_id ergänzt.")
    else:
        print("Spalte verlauf_eintraege.msgraph_list_id existiert bereits.")

    if not column_exists(cur, "verlauf_eintraege", "msgraph_task_id"):
        cur.execute("ALTER TABLE verlauf_eintraege ADD COLUMN msgraph_task_id VARCHAR(200)")
        print("Spalte verlauf_eintraege.msgraph_task_id ergänzt.")
    else:
        print("Spalte verlauf_eintraege.msgraph_task_id existiert bereits.")

    if not column_exists(cur, "verlauf_eintraege", "status_changed_at"):
        cur.execute("ALTER TABLE verlauf_eintraege ADD COLUMN status_changed_at DATETIME")
        cur.execute("UPDATE verlauf_eintraege SET status_changed_at = created_at WHERE status_changed_at IS NULL")
        print("Spalte verlauf_eintraege.status_changed_at ergänzt (mit created_at befüllt).")
    else:
        print("Spalte verlauf_eintraege.status_changed_at existiert bereits.")

    if not column_exists(cur, "items", "anfrage_status"):
        cur.execute("ALTER TABLE items ADD COLUMN anfrage_status VARCHAR(20)")
        print("Spalte items.anfrage_status ergänzt.")
    else:
        print("Spalte items.anfrage_status existiert bereits.")

    if not column_exists(cur, "items", "zustaendig"):
        cur.execute("ALTER TABLE items ADD COLUMN zustaendig VARCHAR(120)")
        print("Spalte items.zustaendig ergänzt.")
    else:
        print("Spalte items.zustaendig existiert bereits.")

    if not column_exists(cur, "items", "ablehnungsgrund"):
        cur.execute("ALTER TABLE items ADD COLUMN ablehnungsgrund VARCHAR(300)")
        print("Spalte items.ablehnungsgrund ergänzt.")
    else:
        print("Spalte items.ablehnungsgrund existiert bereits.")

    if not column_exists(cur, "items", "erp_ab_nummer"):
        cur.execute("ALTER TABLE items ADD COLUMN erp_ab_nummer VARCHAR(60)")
        print("Spalte items.erp_ab_nummer ergänzt.")
    else:
        print("Spalte items.erp_ab_nummer existiert bereits.")

    if not column_exists(cur, "items", "quelle"):
        cur.execute("ALTER TABLE items ADD COLUMN quelle VARCHAR(20)")
        cur.execute("UPDATE items SET quelle = 'manuell' WHERE quelle IS NULL")
        print("Spalte items.quelle ergänzt (bestehende Einträge als 'manuell' markiert).")
    else:
        print("Spalte items.quelle existiert bereits.")

    if not table_exists(cur, "phasen"):
        cur.execute("""
            CREATE TABLE phasen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id),
                bezeichnung VARCHAR(120) NOT NULL,
                start DATE NOT NULL,
                ende DATE NOT NULL,
                created_at DATETIME
            )
        """)
        print("Tabelle phasen angelegt (für detailliertes Gantt je Auftrag).")
    else:
        print("Tabelle phasen existiert bereits.")

    if not column_exists(cur, "items", "lieferbedingungen"):
        cur.execute("ALTER TABLE items ADD COLUMN lieferbedingungen VARCHAR(200)")
        print("Spalte items.lieferbedingungen ergänzt.")
    else:
        print("Spalte items.lieferbedingungen existiert bereits.")

    if not column_exists(cur, "items", "ursprungsauftrag"):
        cur.execute("ALTER TABLE items ADD COLUMN ursprungsauftrag VARCHAR(60)")
        print("Spalte items.ursprungsauftrag ergänzt.")
    else:
        print("Spalte items.ursprungsauftrag existiert bereits.")

    if not column_exists(cur, "items", "zul_geliefert"):
        cur.execute("ALTER TABLE items ADD COLUMN zul_geliefert VARCHAR(60)")
        print("Spalte items.zul_geliefert ergänzt.")
    else:
        print("Spalte items.zul_geliefert existiert bereits.")

    if not column_exists(cur, "items", "bu"):
        cur.execute("ALTER TABLE items ADD COLUMN bu VARCHAR(10)")
        print("Spalte items.bu ergänzt.")
    else:
        print("Spalte items.bu existiert bereits.")

    if not column_exists(cur, "items", "t"):
        cur.execute("ALTER TABLE items ADD COLUMN t VARCHAR(10)")
        print("Spalte items.t ergänzt.")
    else:
        print("Spalte items.t existiert bereits.")

    if not column_exists(cur, "items", "projektleiter"):
        cur.execute("ALTER TABLE items ADD COLUMN projektleiter VARCHAR(120)")
        print("Spalte items.projektleiter ergänzt.")
    else:
        print("Spalte items.projektleiter existiert bereits.")

    if not table_exists(cur, "liefertermin_historie"):
        cur.execute("""
            CREATE TABLE liefertermin_historie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id),
                alter_termin DATE,
                neuer_termin DATE,
                kommentar TEXT,
                created_at DATETIME
            )
        """)
        print("Tabelle liefertermin_historie angelegt (Versionierung des Liefertermins).")
    else:
        print("Tabelle liefertermin_historie existiert bereits.")

    if not table_exists(cur, "auftrag_positionen"):
        cur.execute("""
            CREATE TABLE auftrag_positionen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id),
                position VARCHAR(40),
                beschreibung TEXT NOT NULL,
                liefertermin DATE,
                reihenfolge INTEGER DEFAULT 0,
                created_at DATETIME
            )
        """)
        print("Tabelle auftrag_positionen angelegt (mehrere Liefertermine je Position).")
    else:
        print("Tabelle auftrag_positionen existiert bereits.")

    if not column_exists(cur, "liefertermin_historie", "position_id"):
        cur.execute("ALTER TABLE liefertermin_historie ADD COLUMN position_id INTEGER REFERENCES auftrag_positionen(id)")
        print("Spalte liefertermin_historie.position_id ergänzt (Historie je Position statt nur je Auftrag).")
    else:
        print("Spalte liefertermin_historie.position_id existiert bereits.")

    if not table_exists(cur, "verlauf_updates"):
        cur.execute("""
            CREATE TABLE verlauf_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verlauf_id INTEGER NOT NULL REFERENCES verlauf_eintraege(id),
                text TEXT NOT NULL,
                erstellt_von VARCHAR(120),
                created_at DATETIME
            )
        """)
        print("Tabelle verlauf_updates angelegt (datierte Updates je Verlaufseintrag).")
    else:
        print("Tabelle verlauf_updates existiert bereits.")

    if not column_exists(cur, "items", "bestelleingang"):
        cur.execute("ALTER TABLE items ADD COLUMN bestelleingang DATE")
        print("Spalte items.bestelleingang ergänzt (Datum des Bestelleingangs im Auftragskopf).")
    else:
        print("Spalte items.bestelleingang existiert bereits.")

    if not column_exists(cur, "items", "archiviert"):
        cur.execute("ALTER TABLE items ADD COLUMN archiviert BOOLEAN DEFAULT 0")
        print("Spalte items.archiviert ergänzt (manuelles Archivieren erledigter Aufträge).")
    else:
        print("Spalte items.archiviert existiert bereits.")

    # Nutzer ergänzen/umbenennen: Namenskonvention in der echten Nutzerliste ist
    # "Nachname, Vorname" (nicht "Vorname Nachname" wie im seed.py-Beispielbestand)
    cur.execute("SELECT id FROM users WHERE name = ?", ("Häfer, Gabriele",))
    if cur.fetchone() is None:
        cur.execute("SELECT id FROM users WHERE name = ?", ("Gabriele Häfer",))
        alt = cur.fetchone()
        if alt is not None:
            cur.execute("UPDATE users SET name = ? WHERE id = ?", ("Häfer, Gabriele", alt[0]))
            print("Nutzer 'Gabriele Häfer' zu 'Häfer, Gabriele' umbenannt (Namenskonvention).")
        else:
            cur.execute(
                "INSERT INTO users (name, abteilung, email) VALUES (?, ?, ?)",
                ("Häfer, Gabriele", "Administration", "haefer@heta.de"),
            )
            print("Nutzer 'Häfer, Gabriele' ergänzt.")
    else:
        print("Nutzer 'Häfer, Gabriele' existiert bereits.")

    if not column_exists(cur, "items", "asme"):
        cur.execute("ALTER TABLE items ADD COLUMN asme BOOLEAN DEFAULT 0")
        print("Spalte items.asme ergänzt (Kennzeichen ASME-Auftrag).")
    else:
        print("Spalte items.asme existiert bereits.")

    if not table_exists(cur, "lieferanten_bestellungen"):
        cur.execute("""
            CREATE TABLE lieferanten_bestellungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL REFERENCES items(id),
                bestell_nr VARCHAR(60) NOT NULL,
                datum DATE,
                lieferant TEXT,
                ihr_angebot VARCHAR(120),
                ihr_sachbearbeiter VARCHAR(120),
                unser_zeichen VARCHAR(120),
                lieferdatum DATE,
                versand VARCHAR(120),
                asme_edition VARCHAR(120),
                coded_marking VARCHAR(200),
                material_art VARCHAR(120),
                weitere_standards TEXT,
                zahlungsbedingungen VARCHAR(200),
                mwst_satz FLOAT DEFAULT 19.0,
                created_at DATETIME
            )
        """)
        print("Tabelle lieferanten_bestellungen angelegt (ASME-Dokumente).")
    else:
        print("Tabelle lieferanten_bestellungen existiert bereits.")

    if not column_exists(cur, "lieferanten_bestellungen", "material_art"):
        cur.execute("ALTER TABLE lieferanten_bestellungen ADD COLUMN material_art VARCHAR(120)")
        print("Spalte lieferanten_bestellungen.material_art ergänzt.")

    if not table_exists(cur, "bestell_positionen"):
        cur.execute("""
            CREATE TABLE bestell_positionen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bestellung_id INTEGER NOT NULL REFERENCES lieferanten_bestellungen(id),
                pos VARCHAR(20),
                menge FLOAT,
                einheit VARCHAR(20),
                bezeichnung TEXT NOT NULL,
                werkstoff VARCHAR(120),
                spezifikation VARCHAR(200),
                stueckliste_pos VARCHAR(40),
                preis FLOAT,
                reihenfolge INTEGER DEFAULT 0,
                created_at DATETIME
            )
        """)
        print("Tabelle bestell_positionen angelegt (ASME-Dokumente).")
    else:
        print("Tabelle bestell_positionen existiert bereits.")

    if not column_exists(cur, "items", "unser_zeichen"):
        cur.execute("ALTER TABLE items ADD COLUMN unser_zeichen VARCHAR(120)")
        print("Spalte items.unser_zeichen ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte items.unser_zeichen existiert bereits.")

    if not column_exists(cur, "items", "kunden_zeichen"):
        cur.execute("ALTER TABLE items ADD COLUMN kunden_zeichen VARCHAR(120)")
        print("Spalte items.kunden_zeichen ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte items.kunden_zeichen existiert bereits.")

    if not column_exists(cur, "items", "kunden_bestellnr"):
        cur.execute("ALTER TABLE items ADD COLUMN kunden_bestellnr VARCHAR(60)")
        print("Spalte items.kunden_bestellnr ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte items.kunden_bestellnr existiert bereits.")

    if not column_exists(cur, "items", "kunden_adresse"):
        cur.execute("ALTER TABLE items ADD COLUMN kunden_adresse TEXT")
        print("Spalte items.kunden_adresse ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte items.kunden_adresse existiert bereits.")

    if not column_exists(cur, "items", "zahlungsbedingungen"):
        cur.execute("ALTER TABLE items ADD COLUMN zahlungsbedingungen VARCHAR(120)")
        print("Spalte items.zahlungsbedingungen ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte items.zahlungsbedingungen existiert bereits.")

    if not column_exists(cur, "items", "versand_adresse"):
        cur.execute("ALTER TABLE items ADD COLUMN versand_adresse TEXT")
        print("Spalte items.versand_adresse ergänzt (Auftragsbestätigung, nur falls abweichend).")
    else:
        print("Spalte items.versand_adresse existiert bereits.")

    if not column_exists(cur, "auftrag_positionen", "menge"):
        cur.execute("ALTER TABLE auftrag_positionen ADD COLUMN menge FLOAT")
        print("Spalte auftrag_positionen.menge ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte auftrag_positionen.menge existiert bereits.")

    if not column_exists(cur, "auftrag_positionen", "einheit"):
        cur.execute("ALTER TABLE auftrag_positionen ADD COLUMN einheit VARCHAR(20)")
        print("Spalte auftrag_positionen.einheit ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte auftrag_positionen.einheit existiert bereits.")

    if not column_exists(cur, "auftrag_positionen", "preis_je_einheit"):
        cur.execute("ALTER TABLE auftrag_positionen ADD COLUMN preis_je_einheit FLOAT")
        print("Spalte auftrag_positionen.preis_je_einheit ergänzt (Auftragsbestätigung).")
    else:
        print("Spalte auftrag_positionen.preis_je_einheit existiert bereits.")

    # Bekannte Nutzer mit E-Mail-Adresse befüllen (nur wenn noch leer)
    cur.execute("SELECT id, name, email FROM users")
    updated = 0
    for user_id, name, email in cur.fetchall():
        if not email and name in EMAIL_MAP:
            cur.execute("UPDATE users SET email = ? WHERE id = ?", (EMAIL_MAP[name], user_id))
            updated += 1
    if updated:
        print(f"{updated} Nutzer mit E-Mail-Adresse befüllt.")

    conn.commit()
    conn.close()
    print("Migration abgeschlossen. Bestehende Aufträge/Angebote/Verlauf sind unverändert.")


if __name__ == "__main__":
    main()
