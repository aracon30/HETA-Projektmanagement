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
