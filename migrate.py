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
    "Jessica Weiz": "weiz@heta.de",
    "Weiz, Jessica": "weiz@heta.de",
    "Sascha Diehl": "diehl@heta.de",
    "Diehl, Sascha": "diehl@heta.de",
    "Steffen Schmidt": "schmidt@heta.de",
    "Schmidt, Steffen": "schmidt@heta.de",
    "Michael Hennig": "hennig@heta.de",
    "Hennig, Michael": "hennig@heta.de",
    "Shahram Abdani": "abdani@heta.de",
    "Abdani, Shahram": "abdani@heta.de",
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

    NEUE_NUTZER = [
        ("Weiz, Jessica", "weiz@heta.de"),
        ("Diehl, Sascha", "diehl@heta.de"),
        ("Schmidt, Steffen", "schmidt@heta.de"),
        ("Hennig, Michael", "hennig@heta.de"),
        ("Abdani, Shahram", "abdani@heta.de"),
    ]
    for name, email in NEUE_NUTZER:
        cur.execute("SELECT id FROM users WHERE name = ?", (name,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (name, abteilung, email) VALUES (?, ?, ?)",
                (name, None, email),
            )
            print(f"Nutzer '{name}' ergänzt.")
        else:
            print(f"Nutzer '{name}' existiert bereits.")

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

    if not column_exists(cur, "items", "mwst_anwenden"):
        cur.execute("ALTER TABLE items ADD COLUMN mwst_anwenden BOOLEAN DEFAULT 1")
        cur.execute("UPDATE items SET mwst_anwenden = 1 WHERE mwst_anwenden IS NULL")
        print("Spalte items.mwst_anwenden ergänzt (Auftragsbestätigung, Standard: 19% MwSt anwenden).")
    else:
        print("Spalte items.mwst_anwenden existiert bereits.")

    if not column_exists(cur, "items", "ab_sprache"):
        cur.execute("ALTER TABLE items ADD COLUMN ab_sprache VARCHAR(10) DEFAULT 'de'")
        cur.execute("UPDATE items SET ab_sprache = 'de' WHERE ab_sprache IS NULL")
        print("Spalte items.ab_sprache ergänzt (Auftragsbestätigung komplett Deutsch/Englisch, Standard: de).")
    else:
        print("Spalte items.ab_sprache existiert bereits.")

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

    # ---- Firmen / CRM (Stufe 1, siehe docs/KONZEPT-FIRMEN-CRM.md) ----
    if not table_exists(cur, "firmen"):
        cur.execute("""
            CREATE TABLE firmen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                kurzname VARCHAR(80),
                konzern_id INTEGER REFERENCES firmen(id),
                rollen VARCHAR(120) DEFAULT 'kunde',
                branche VARCHAR(120),
                land VARCHAR(80),
                website VARCHAR(200),
                lieferantenportal VARCHAR(200),
                quelle VARCHAR(80),
                status VARCHAR(20) DEFAULT 'aktiv',
                notiz TEXT,
                warengruppe VARCHAR(120),
                freigabestatus VARCHAR(20),
                bewertungspflichtig BOOLEAN DEFAULT 1,
                aktiv BOOLEAN DEFAULT 1,
                created_at DATETIME,
                created_by VARCHAR(120)
            )
        """)
        print("Tabelle firmen angelegt (Firmen-CRM Stufe 1).")
    else:
        print("Tabelle firmen existiert bereits.")

    if not table_exists(cur, "firmen_adressen"):
        cur.execute("""
            CREATE TABLE firmen_adressen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma_id INTEGER NOT NULL REFERENCES firmen(id),
                art VARCHAR(20) DEFAULT 'haupt',
                zeilen TEXT NOT NULL,
                standard BOOLEAN DEFAULT 0,
                created_at DATETIME
            )
        """)
        print("Tabelle firmen_adressen angelegt.")
    else:
        print("Tabelle firmen_adressen existiert bereits.")

    for spalte, typ in [("firma_id", "INTEGER REFERENCES firmen(id)"),
                        ("adresse_id", "INTEGER REFERENCES firmen_adressen(id)"),
                        ("versand_adresse_id", "INTEGER REFERENCES firmen_adressen(id)")]:
        if not column_exists(cur, "items", spalte):
            cur.execute(f"ALTER TABLE items ADD COLUMN {spalte} {typ}")
            print(f"Spalte items.{spalte} ergänzt (Firmen-Verknüpfung).")
        else:
            print(f"Spalte items.{spalte} existiert bereits.")

    # ---- Lieferantenbewertung (Stufe 1, siehe docs/KONZEPT-LIEFERANTEN.md) ----
    if not table_exists(cur, "bewertung_kriterien"):
        cur.execute("""
            CREATE TABLE bewertung_kriterien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ebene VARCHAR(20) NOT NULL,
                reihenfolge INTEGER DEFAULT 0,
                bezeichnung VARCHAR(200) NOT NULL,
                gewicht FLOAT NOT NULL,
                note1_text TEXT,
                note2_text TEXT,
                note3_text TEXT,
                note4_text TEXT,
                aktiv BOOLEAN DEFAULT 1,
                katalog_version INTEGER DEFAULT 1
            )
        """)
        print("Tabelle bewertung_kriterien angelegt (Lieferantenbewertung Stufe 1).")
    else:
        print("Tabelle bewertung_kriterien existiert bereits.")

    if not table_exists(cur, "bewertung_einstellungen"):
        cur.execute("""
            CREATE TABLE bewertung_einstellungen (
                "key" VARCHAR(60) PRIMARY KEY,
                value VARCHAR(200) NOT NULL
            )
        """)
        print("Tabelle bewertung_einstellungen angelegt.")
    else:
        print("Tabelle bewertung_einstellungen existiert bereits.")

    if not table_exists(cur, "lieferungsbewertungen"):
        cur.execute("""
            CREATE TABLE lieferungsbewertungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma_id INTEGER NOT NULL REFERENCES firmen(id),
                datum DATE NOT NULL,
                bestell_nr VARCHAR(60),
                item_id INTEGER REFERENCES items(id),
                bewerter VARCHAR(120),
                bemerkung TEXT,
                katalog_version INTEGER DEFAULT 1,
                ergebnis_gespeichert FLOAT,
                created_at DATETIME
            )
        """)
        print("Tabelle lieferungsbewertungen angelegt.")
    else:
        print("Tabelle lieferungsbewertungen existiert bereits.")

    if not table_exists(cur, "jahresbewertungen"):
        cur.execute("""
            CREATE TABLE jahresbewertungen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firma_id INTEGER NOT NULL REFERENCES firmen(id),
                jahr INTEGER NOT NULL,
                datum DATE NOT NULL,
                bewerter VARCHAR(120),
                bemerkung TEXT,
                katalog_version INTEGER DEFAULT 1,
                ergebnis_gespeichert FLOAT,
                created_at DATETIME,
                UNIQUE (firma_id, jahr)
            )
        """)
        print("Tabelle jahresbewertungen angelegt.")
    else:
        print("Tabelle jahresbewertungen existiert bereits.")

    if not table_exists(cur, "bewertung_noten"):
        cur.execute("""
            CREATE TABLE bewertung_noten (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bewertung_typ VARCHAR(20) NOT NULL,
                bewertung_id INTEGER NOT NULL,
                kriterium_id INTEGER NOT NULL REFERENCES bewertung_kriterien(id),
                note INTEGER NOT NULL
            )
        """)
        print("Tabelle bewertung_noten angelegt.")
    else:
        print("Tabelle bewertung_noten existiert bereits.")

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
