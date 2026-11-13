"""
Einmaliger Import der FB-0019 "Liste freigegebener Lieferanten" (Excel) in
LieferantenZertifizierung + Firma (Rolle "Lieferant"), siehe
docs/KONZEPT-LIEFERANTEN-ZERTIFIKATE.md.

Aufruf:
  ./venv/bin/python import_lieferanten_zertifikate.py <pfad-zur-excel>
      Dry-Run: zeigt nur die Vorschau (was würde passieren), schreibt nichts.
  ./venv/bin/python import_lieferanten_zertifikate.py <pfad-zur-excel> --commit
      Schreibt wirklich (neue Firmen, Zertifizierungszeilen, Löschung der
      Test-Lieferanten).

Ablauf (siehe Konzept Abschnitt 5):
1. Liest "Supplier_Master" + "Cert_Daten" aus der Excel.
2. Gleicht jeden eindeutigen Lieferantennamen gegen bestehende Firmen ab
   (gleicher Ähnlichkeitsvergleich wie beim Assistenten "Kunden zuordnen",
   firmen_api.normalisiere(), Schwelle 0.84) — Treffer wird verknüpft (Rolle
   "Lieferant" wird ergänzt, falls noch nicht vorhanden), sonst wird eine neue
   Firma mit Rolle "Lieferant" angelegt. Firma.warengruppe wird dabei NICHT
   überschrieben — die Excel-Warengruppe gehört auf die Zertifizierungszeile,
   nicht auf die Firma (ein Firma kann mehrere Warengruppen-Zeilen haben).
3. Legt je Excel-Zeile eine LieferantenZertifizierung an.
4. Schlägt vorher die vier erkennbaren Test-Lieferanten zur Löschung vor —
   nur wenn sie keine echten Verknüpfungen (Aufträge/Bewertungen/Aktivitäten/
   Kontakte) haben, sonst Warnung statt automatischem Löschen.

NICHT idempotent wie seed_lieferanten.py — das ist ein einmaliger Übergang
(das Portal wird danach laut Konzept alleinige Quelle). Das Skript bricht
deshalb ab, wenn schon LieferantenZertifizierung-Zeilen existieren, außer
--force wird zusätzlich angegeben.
"""
import argparse
import difflib
import sys
from datetime import date, datetime

import openpyxl

from app import app
from models import (
    db, Firma, LieferantenZertifizierung, ALLE_ZERTIFIKAT_FELDER,
    Kontakt, Aktivitaet, Lieferungsbewertung, Jahresbewertung,
)
from firmen_api import normalisiere

AEHNLICHKEIT_SCHWELLE = 0.84

TEST_LIEFERANTEN_NAMEN = [
    "Muster Industrie GmbH",
    "Regressionstest Lieferant",
    "Review Test Lieferant GmbH & Co KG",
    "Testlieferant GmbH",
]


def als_datum(wert):
    if isinstance(wert, datetime):
        return wert.date()
    if isinstance(wert, date):
        return wert
    return None


def lies_supplier_master(wb):
    """Spaltenreihenfolge laut Excel-Kopfzeile (Zeile 4): Supplier ID,
    Lieferant, Warengruppe, Status, ISO 9001 Gültig bis, Tage bis Ablauf,
    Letzte Bestellung, Letzte Bewertung, Sperr-Datum, Status2, Info."""
    ws = wb["Supplier_Master"]
    zeilen = []
    text_statt_datum = 0
    for row in ws.iter_rows(min_row=5):
        name = row[1].value
        if not name:
            continue
        letzte_bewertung_roh = row[7].value
        letzte_bewertung = als_datum(letzte_bewertung_roh)
        if letzte_bewertung_roh not in (None, "") and letzte_bewertung is None:
            text_statt_datum += 1
        zeilen.append({
            "lieferant": str(name).strip(),
            "warengruppe": (row[2].value or "").strip() if row[2].value else None,
            "iso9001_gueltig_bis": als_datum(row[4].value),
            "letzte_bestellung_jahr": row[6].value if isinstance(row[6].value, int) else None,
            "letzte_bewertung_am": letzte_bewertung,
            "sperr_datum": als_datum(row[8].value),
            "info": row[10].value,
        })
    return zeilen, text_statt_datum


def lies_cert_daten(wb):
    """Spalte A = Schlüssel ("Lieferant|Warengruppe", wortgleich wie in
    Supplier_Master gebildet), Spalten D..N = die 11 Normen in genau der
    Reihenfolge von ALLE_ZERTIFIKAT_FELDER[1:]."""
    ws = wb["Cert_Daten"]
    daten = {}
    for row in ws.iter_rows(min_row=3):
        schluessel = row[0].value
        if not schluessel:
            continue
        werte = {}
        for idx, (feld, _, _) in enumerate(ALLE_ZERTIFIKAT_FELDER[1:]):
            werte[feld] = als_datum(row[3 + idx].value)
        daten[schluessel] = werte
    return daten


def firma_fuer(name, firmen_norm, neu_angelegt_cache):
    """Findet die beste bestehende Firma per Ähnlichkeitsvergleich (wie beim
    Assistenten "Kunden zuordnen") oder gibt None zurück, wenn keine über der
    Schwelle liegt — dann wird eine neue Firma angelegt (gecacht, damit
    mehrere Warengruppen-Zeilen derselben neuen Firma nicht mehrfach anlegen)."""
    if name in neu_angelegt_cache:
        return neu_angelegt_cache[name], False
    norm = normalisiere(name)
    beste_firma, beste_quote = None, 0.0
    for f_norm, f in firmen_norm.items():
        quote = difflib.SequenceMatcher(None, norm, f_norm).ratio()
        if quote > beste_quote:
            beste_quote, beste_firma = quote, f
    if beste_firma and beste_quote >= AEHNLICHKEIT_SCHWELLE:
        return beste_firma, True
    return None, True


def pruefe_test_lieferanten():
    """Welche der vier Test-Lieferanten existieren und haben KEINE echten
    Verknüpfungen (Aufträge/Bewertungen/Aktivitäten/Kontakte)? Nur die werden
    zur Löschung vorgeschlagen."""
    loeschbar, nicht_loeschbar = [], []
    for name in TEST_LIEFERANTEN_NAMEN:
        f = Firma.query.filter_by(name=name).first()
        if not f:
            continue
        hat_kontakte = Kontakt.query.filter_by(firma_id=f.id).count() > 0
        hat_aktivitaeten = Aktivitaet.query.filter_by(firma_id=f.id).count() > 0
        hat_bewertungen = (
            Lieferungsbewertung.query.filter_by(firma_id=f.id).count() > 0
            or Jahresbewertung.query.filter_by(firma_id=f.id).count() > 0
        )
        if len(f.items) or len(f.adressen) or hat_kontakte or hat_aktivitaeten or hat_bewertungen:
            nicht_loeschbar.append(f)
        else:
            loeschbar.append(f)
    return loeschbar, nicht_loeschbar


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("excel_pfad")
    parser.add_argument("--commit", action="store_true", help="wirklich schreiben (sonst nur Vorschau)")
    parser.add_argument("--force", action="store_true", help="auch ausführen, wenn schon Zertifizierungszeilen existieren")
    args = parser.parse_args()

    with app.app_context():
        bestehende_zeilen = LieferantenZertifizierung.query.count()
        if bestehende_zeilen and not args.force:
            print(f"ABBRUCH: Es existieren bereits {bestehende_zeilen} LieferantenZertifizierung-Zeilen.")
            print("Das Skript ist für einen einmaligen Import gedacht (siehe Docstring).")
            print("Mit --force trotzdem ausführen (legt zusätzliche Zeilen an, keine Duplikat-Prüfung!).")
            sys.exit(1)

        print(f"Lese {args.excel_pfad} ...")
        wb = openpyxl.load_workbook(args.excel_pfad, data_only=True)
        supplier_zeilen, text_statt_datum = lies_supplier_master(wb)
        cert_daten = lies_cert_daten(wb)
        print(f"{len(supplier_zeilen)} Zeilen in Supplier_Master, {len(cert_daten)} Schlüssel in Cert_Daten.")
        if text_statt_datum:
            print(f"Hinweis: {text_statt_datum}x 'Letzte Bewertung' war kein eindeutiges Datum "
                  f"(z.B. mehrere Daten in einer Zelle) — wird ohne Datum übernommen.")

        eindeutige_namen = sorted({z["lieferant"] for z in supplier_zeilen})
        print(f"{len(eindeutige_namen)} eindeutige Lieferantennamen.")

        firmen = Firma.query.filter(Firma.aktiv.is_(True)).all()
        firmen_norm = {normalisiere(f.name): f for f in firmen}
        for f in firmen:
            if f.kurzname:
                firmen_norm.setdefault(normalisiere(f.kurzname), f)

        name_zu_firma = {}
        neu_angelegt_cache = {}
        treffer, neu = 0, 0
        for name in eindeutige_namen:
            firma, _ = firma_fuer(name, firmen_norm, neu_angelegt_cache)
            if firma:
                name_zu_firma[name] = firma
                treffer += 1
            else:
                neu += 1
                if args.commit:
                    firma = Firma(name=name, rollen="lieferant", aktiv=True, created_at=datetime.utcnow(), created_by="Import FB-0019")
                    db.session.add(firma)
                    db.session.flush()
                name_zu_firma[name] = firma
                neu_angelegt_cache[name] = firma

        print(f"Firmen-Abgleich: {treffer} bestehende Firmen verknüpft, {neu} neue Firmen anzulegen.")

        rollen_ergaenzt = 0
        for name, firma in name_zu_firma.items():
            if firma is None:
                continue
            if "lieferant" not in firma.rollen_liste():
                rollen_ergaenzt += 1
                if args.commit:
                    firma.rollen = ",".join(firma.rollen_liste() + ["lieferant"])
        if rollen_ergaenzt:
            print(f"{rollen_ergaenzt} bestehende Firmen bekommen zusätzlich die Rolle 'Lieferant'.")

        loeschbar, nicht_loeschbar = pruefe_test_lieferanten()
        if loeschbar:
            print(f"\nTest-Lieferanten ohne echte Verknüpfung, werden gelöscht: "
                  f"{', '.join(f.name for f in loeschbar)}")
            if args.commit:
                for f in loeschbar:
                    db.session.delete(f)
        if nicht_loeschbar:
            print(f"ACHTUNG: Test-Lieferanten MIT echter Verknüpfung, werden NICHT automatisch gelöscht: "
                  f"{', '.join(f.name for f in nicht_loeschbar)} — bitte von Hand prüfen.")

        angelegt = 0
        for z in supplier_zeilen:
            firma = name_zu_firma.get(z["lieferant"])
            schluessel = f"{z['lieferant']}|{z['warengruppe'] or ''}"
            normen = cert_daten.get(schluessel, {})
            angelegt += 1  # zählt auch im Dry-Run, selbst wenn firma dort noch None ist
            if args.commit:
                zert = LieferantenZertifizierung(
                    firma_id=firma.id,
                    warengruppe=z["warengruppe"],
                    iso9001_gueltig_bis=z["iso9001_gueltig_bis"],
                    sperr_datum=z["sperr_datum"],
                    info=z["info"],
                    letzte_bestellung_jahr=z["letzte_bestellung_jahr"],
                    letzte_bewertung_am=z["letzte_bewertung_am"],
                    created_at=datetime.utcnow(),
                    **normen,
                )
                db.session.add(zert)

        print(f"\nZertifizierungszeilen anzulegen: {angelegt}")

        if args.commit:
            db.session.commit()
            print("\nFertig — Änderungen wurden gespeichert.")
        else:
            db.session.rollback()
            print("\nDRY-RUN — nichts wurde gespeichert. Mit --commit ausführen, um wirklich zu schreiben.")


if __name__ == "__main__":
    main()
