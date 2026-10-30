"""Legt die Tabellen für die Lieferantenbewertung an (falls noch nicht
vorhanden) und spielt den Startbestand aus lieferanten_daten.py ein.

Aufruf: ./venv/bin/python seed_lieferanten.py   (läuft auch in deploy/update.sh)

Sicher auf dem Server mit echten Daten: legt nur fehlende Kriterien/Einstellungen
an (Prüfung über Bezeichnung+Ebene bzw. Schlüssel), überschreibt nichts
Vorhandenes — Gewichte/Definitionen lassen sich also über das Tool oder von
Hand anpassen, ohne dass ein erneuter Lauf das wieder zurücksetzt.
"""
from models import db, BewertungKriterium, BewertungEinstellung
from lieferanten_daten import KRITERIEN, EINSTELLUNGEN


def seed():
    """Erwartet einen aktiven App-Kontext."""
    db.create_all()

    vorhandene = {(k.ebene, k.bezeichnung) for k in BewertungKriterium.query.all()}
    neu = 0
    for ebene, reihenfolge, bezeichnung, gewicht, n1, n2, n3, n4 in KRITERIEN:
        if (ebene, bezeichnung) in vorhandene:
            continue
        db.session.add(BewertungKriterium(
            ebene=ebene, reihenfolge=reihenfolge, bezeichnung=bezeichnung, gewicht=gewicht,
            note1_text=n1, note2_text=n2, note3_text=n3, note4_text=n4,
        ))
        neu += 1
    if neu:
        print(f"{neu} Bewertungskriterien ergänzt.")
    else:
        print("Bewertungskriterien bereits vollständig.")

    vorhandene_keys = {e.key for e in BewertungEinstellung.query.all()}
    neu = 0
    for key, value in EINSTELLUNGEN.items():
        if key in vorhandene_keys:
            continue
        db.session.add(BewertungEinstellung(key=key, value=value))
        neu += 1
    if neu:
        print(f"{neu} Bewertungseinstellungen ergänzt.")
    else:
        print("Bewertungseinstellungen bereits vollständig.")

    db.session.commit()
    return True


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed()
