"""Legt die Tabellen für den Reiter "Prozesse" an (falls noch nicht vorhanden)
und befüllt sie mit dem Startbestand aus prozess_daten.py.

Aufruf: ./venv/bin/python seed_prozesse.py

Sicher auf dem Server mit echten Daten: bestehende Tabellen (Aufträge,
Angebote, Verlauf …) werden nicht angefasst, und der Startbestand wird nur
eingespielt, solange noch KEIN Prozess in der Datenbank existiert.
"""
from models import db, Prozess, ProzessSchritt, ProzessFrage, Dokument
from prozess_daten import LANDKARTE, PROZESS_DETAILS, DOKUMENTE, SCHRITTE, FRAGEN


def _finde_prozess(nach_nummer, nummer):
    """Sucht den Prozess zur Nummer; fehlt er (z.B. U2.2), wird der nächsthöhere
    vorhandene genommen (U2.2 -> U2)."""
    while nummer:
        if nummer in nach_nummer:
            return nach_nummer[nummer]
        if "." in nummer:
            nummer = nummer.rsplit(".", 1)[0]
        else:
            return nach_nummer.get(nummer[:1])
    return None


def seed():
    """Erwartet einen aktiven App-Kontext."""
    db.create_all()
    if Prozess.query.first() is not None:
        print("Es existieren bereits Prozesse – Startbestand wird nicht erneut eingespielt.")
        return False

    nach_nummer = {}
    for i, (nummer, bezeichnung, parent, status) in enumerate(LANDKARTE, 1):
        p = Prozess(nummer=nummer, bezeichnung=bezeichnung, aufnahmestatus=status, reihenfolge=i,
                    parent_id=nach_nummer[parent].id if parent else None,
                    **PROZESS_DETAILS.get(nummer, {}))
        db.session.add(p)
        db.session.flush()
        nach_nummer[nummer] = p

    for nummer, revision, titel, geltung, prozess_nr, status in DOKUMENTE:
        p = _finde_prozess(nach_nummer, prozess_nr)
        db.session.add(Dokument(nummer=nummer, revision=revision or None, titel=titel, geltungsbereich=geltung,
                                prozess_id=p.id if p else None, auswertungsstatus=status))

    for (prozess_nr, nr, taetigkeit, ausfuehrend, eingaben, system, ergebnis, uebergabe, freigabe,
         ausnahme, bearbeitungszeit, wartezeit, nachweis) in SCHRITTE:
        db.session.add(ProzessSchritt(
            prozess_id=nach_nummer[prozess_nr].id, reihenfolge=nr, taetigkeit=taetigkeit,
            ausfuehrend=ausfuehrend or None, eingaben=eingaben or None, system=system or None,
            ergebnis=ergebnis or None, uebergabe=uebergabe or None, freigabe=freigabe or None,
            ausnahme=ausnahme or None, bearbeitungszeit=bearbeitungszeit or None,
            wartezeit=wartezeit or None, nachweis=nachweis or None,
        ))

    for f in FRAGEN:
        prozess_nr, frage, klaerung = f[:3]
        status, antwort, nachweis = f[3:] if len(f) > 3 else ("offen", None, None)
        p = _finde_prozess(nach_nummer, prozess_nr.split("/")[0])
        db.session.add(ProzessFrage(prozess_id=p.id, frage=frage, klaerung_durch=klaerung, status=status,
                                    antwort=antwort, nachweis=nachweis, erstellt_von="Startbestand"))

    db.session.commit()
    print(f"Startbestand eingespielt: {len(LANDKARTE)} Prozesse, {len(DOKUMENTE)} Arbeitsanweisungen, "
          f"{len(SCHRITTE)} Schritte, {len(FRAGEN)} Fragen.")
    return True


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed()
