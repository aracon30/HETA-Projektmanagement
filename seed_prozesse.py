"""Legt die Tabellen für den Reiter "Prozesse" an (falls noch nicht vorhanden)
und spielt den Startbestand aus prozess_daten.py ein.

Aufruf: ./venv/bin/python seed_prozesse.py   (läuft auch in deploy/update.sh)

Sicher auf dem Server mit echten Daten:
- bestehende Tabellen (Aufträge, Angebote, Verlauf …) werden nicht angefasst
- der Grundbestand wird nur in eine leere Prozess-Datenbank eingespielt
- jede Ergänzung (prozess_daten.ERGAENZUNGEN) läuft genau einmal; der Stand
  steht in der Tabelle startbestand_stand. Änderungen aus dem Tool werden dabei
  nicht überschrieben (siehe _ergaenzung_einspielen).
"""
from models import db, Prozess, ProzessSchritt, ProzessFrage, Dokument, ProzessVerbindung, StartbestandStand
from prozess_daten import LANDKARTE, PROZESS_DETAILS, DOKUMENTE, SCHRITTE, FRAGEN, ERGAENZUNGEN


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


def _neuer_schritt(prozess_id, reihenfolge, zeile):
    (_, _, taetigkeit, ausfuehrend, eingaben, system, ergebnis, uebergabe, freigabe,
     ausnahme, bearbeitungszeit, wartezeit, nachweis) = zeile
    return ProzessSchritt(
        prozess_id=prozess_id, reihenfolge=reihenfolge, taetigkeit=taetigkeit,
        ausfuehrend=ausfuehrend or None, eingaben=eingaben or None, system=system or None,
        ergebnis=ergebnis or None, uebergabe=uebergabe or None, freigabe=freigabe or None,
        ausnahme=ausnahme or None, bearbeitungszeit=bearbeitungszeit or None,
        wartezeit=wartezeit or None, nachweis=nachweis or None,
    )


def _neue_frage(nach_nummer, f):
    prozess_nr, frage, klaerung = f[:3]
    status, antwort, nachweis = f[3:] if len(f) > 3 else ("offen", None, None)
    p = _finde_prozess(nach_nummer, prozess_nr.split("/")[0])
    return ProzessFrage(prozess_id=p.id, frage=frage, klaerung_durch=klaerung, status=status,
                        antwort=antwort, nachweis=nachweis, erstellt_von="Startbestand")


def _grundbestand_einspielen():
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

    for zeile in SCHRITTE:
        db.session.add(_neuer_schritt(nach_nummer[zeile[0]].id, zeile[1], zeile))
    for f in FRAGEN:
        db.session.add(_neue_frage(nach_nummer, f))
    db.session.flush()
    print(f"Grundbestand eingespielt: {len(LANDKARTE)} Prozesse, {len(DOKUMENTE)} Arbeitsanweisungen, "
          f"{len(SCHRITTE)} Schritte, {len(FRAGEN)} Fragen.")


def _ergaenzung_einspielen(version, e):
    """Spielt eine Ergänzung ein, ohne Änderungen aus dem Tool zu überschreiben."""
    nach_nummer = {p.nummer: p for p in Prozess.query.all() if p.nummer}
    reihenfolge = db.session.query(db.func.max(Prozess.reihenfolge)).scalar() or 0

    for nummer, bezeichnung, parent, status in e.get("landkarte", []):
        eltern = _finde_prozess(nach_nummer, parent) if parent else None
        # Von Hand angelegte Prozesse nicht doppeln: gleiche Nummer oder gleiche
        # Bezeichnung unter demselben übergeordneten Prozess gilt als vorhanden.
        name = bezeichnung.strip().lower()
        if (nummer and nummer in nach_nummer) or any(
                p.bezeichnung.strip().lower() == name and p.parent_id == (eltern.id if eltern else None)
                for p in Prozess.query.all()):
            continue
        reihenfolge += 1
        p = Prozess(nummer=nummer, bezeichnung=bezeichnung, aufnahmestatus=status, reihenfolge=reihenfolge,
                    parent_id=eltern.id if eltern else None)
        db.session.add(p)
        db.session.flush()
        if nummer:
            nach_nummer[nummer] = p

    for nummer, felder in e.get("details", {}).items():
        p = nach_nummer.get(nummer)
        if p:
            for feld, wert in felder.items():
                if not getattr(p, feld):
                    setattr(p, feld, wert)

    for nummer, status in e.get("status", {}).items():
        p = nach_nummer.get(nummer)
        if p and p.aufnahmestatus == "vorgeschlagen":
            p.aufnahmestatus = status

    for nummer, status in e.get("dokument_status", {}).items():
        dok = Dokument.query.filter_by(nummer=nummer).first()
        if dok and dok.auswertungsstatus == "nicht_gesichtet":
            dok.auswertungsstatus = status

    schritte_neu = 0
    for nummer in dict.fromkeys(z[0] for z in e.get("schritte", [])):
        p = nach_nummer.get(nummer)
        if not p:
            continue
        if p.schritte:
            print(f"Hinweis: {nummer} hat bereits Schritte – die Schritte aus der Ergänzung werden nicht "
                  f"eingespielt (siehe docs/prozessaufnahme/ablaufschritte.csv).")
            continue
        for zeile in (z for z in e.get("schritte", []) if z[0] == nummer):
            db.session.add(_neuer_schritt(p.id, zeile[1], zeile))
            schritte_neu += 1

    for f in e.get("fragen", []):
        db.session.add(_neue_frage(nach_nummer, f))
    db.session.flush()

    verbindungen_neu = 0
    for von_nr, nach_nr, inhalt, weg, problem, notiz, schritt_ref in e.get("verbindungen", []):
        von, nach = nach_nummer.get(von_nr), nach_nummer.get(nach_nr)
        if not von or not nach or ProzessVerbindung.query.filter_by(
                von_id=von.id, nach_id=nach.id, inhalt=inhalt).first():
            continue
        schritt = None
        if schritt_ref and schritt_ref[0] in nach_nummer:
            schritt = ProzessSchritt.query.filter_by(
                prozess_id=nach_nummer[schritt_ref[0]].id, reihenfolge=schritt_ref[1]).first()
        db.session.add(ProzessVerbindung(von_id=von.id, nach_id=nach.id, inhalt=inhalt, weg=weg, problem=problem,
                                         notiz=notiz, schritt_id=schritt.id if schritt else None))
        verbindungen_neu += 1
    db.session.flush()
    print(f"Ergänzung {version} eingespielt ({e['titel']}): {schritte_neu} Schritte, "
          f"{len(e.get('fragen', []))} Fragen, {verbindungen_neu} Schnittstellen.")


def seed():
    """Erwartet einen aktiven App-Kontext."""
    db.create_all()
    stand = StartbestandStand.query.first()
    if stand is None:
        # Datenbanken aus der Zeit vor den Ergänzungen haben den Grundbestand (= 1) schon
        version = 1 if Prozess.query.first() is not None else 0
        stand = StartbestandStand(version=version)
        db.session.add(stand)

    if stand.version < 1:
        _grundbestand_einspielen()
        stand.version = 1

    for version, e in sorted(ERGAENZUNGEN, key=lambda x: x[0]):
        if version > stand.version:
            _ergaenzung_einspielen(version, e)
            stand.version = version

    db.session.commit()
    print(f"Startbestand der Prozessaufnahme ist auf Stand {stand.version}.")
    return True


if __name__ == "__main__":
    from app import app
    with app.app_context():
        seed()
