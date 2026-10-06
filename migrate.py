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

    # Nutzer ergänzen, falls auf dem Server noch nicht angelegt
    cur.execute("SELECT id FROM users WHERE name = ?", ("Gabriele Häfer",))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (name, abteilung, email) VALUES (?, ?, ?)",
            ("Gabriele Häfer", "Administration", "haefer@heta.de"),
        )
        print("Nutzer 'Gabriele Häfer' ergänzt.")
    else:
        print("Nutzer 'Gabriele Häfer' existiert bereits.")

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
