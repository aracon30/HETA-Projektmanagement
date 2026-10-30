"""Legt die Tabellen für die Lieferantenbewertung an (falls noch nicht
vorhanden) und spielt den Startbestand aus lieferanten_daten.py ein.

Aufruf: ./venv/bin/python seed_lieferanten.py   (läuft auch in deploy/update.sh)

Ein Kriterium wird über (ebene, reihenfolge) identifiziert, nicht über die
Bezeichnung — vorhandene Zeilen werden auf Name/Gewicht/Notentexte aus
lieferanten_daten.py synchronisiert (solange es keine Einstellungs-Oberfläche
gibt, über die jemand eigene Anpassungen vornehmen könnte, siehe dort).
bewertung_noten verweisen auf die stabile kriterium_id, nicht auf den Namen,
bleiben also auch bei geändertem Wortlaut gültig. Neue Kriterien (neue
reihenfolge) werden ergänzt, nichts wird gelöscht.
"""
from models import db, BewertungKriterium, BewertungEinstellung
from lieferanten_daten import KRITERIEN, EINSTELLUNGEN


def seed():
    """Erwartet einen aktiven App-Kontext."""
    db.create_all()

    vorhandene = {(k.ebene, k.reihenfolge): k for k in BewertungKriterium.query.all()}
    neu = 0
    aktualisiert = 0
    for ebene, reihenfolge, bezeichnung, gewicht, n1, n2, n3, n4 in KRITERIEN:
        werte = dict(bezeichnung=bezeichnung, gewicht=gewicht,
                     note1_text=n1, note2_text=n2, note3_text=n3, note4_text=n4)
        k = vorhandene.get((ebene, reihenfolge))
        if k is None:
            db.session.add(BewertungKriterium(ebene=ebene, reihenfolge=reihenfolge, **werte))
            neu += 1
        elif any(getattr(k, feld) != wert for feld, wert in werte.items()):
            for feld, wert in werte.items():
                setattr(k, feld, wert)
            aktualisiert += 1
    if neu or aktualisiert:
        print(f"{neu} Bewertungskriterien ergänzt, {aktualisiert} auf aktuellen Wortlaut gebracht.")
    else:
        print("Bewertungskriterien bereits auf aktuellem Stand.")

    vorhandene_einstellungen = {e.key: e for e in BewertungEinstellung.query.all()}
    neu = 0
    aktualisiert = 0
    for key, value in EINSTELLUNGEN.items():
        e = vorhandene_einstellungen.get(key)
        if e is None:
            db.session.add(BewertungEinstellung(key=key, value=value))
            neu += 1
        elif e.value != value:
            e.value = value
            aktualisiert += 1
    if neu or aktualisiert:
        print(f"{neu} Bewertungseinstellungen ergänzt, {aktualisiert} auf aktuellen Wert gebracht.")
    else:
        print("Bewertungseinstellungen bereits auf aktuellem Stand.")

    db.session.commit()
    return True


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed()
