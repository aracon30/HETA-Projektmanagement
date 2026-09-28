"""Erzeugt die CSV-Dateien der Prozessaufnahme (Spalten wie Excel-Vorlage
HETA_Prozessaufnahme.xlsx) aus prozess_daten.py.
Aufruf (aus dem Projektverzeichnis): python3 docs/prozessaufnahme/_erzeuge_csv.py
Trennzeichen ';' und UTF-8 mit BOM, damit Excel die Dateien direkt öffnet."""
import csv
import sys
from pathlib import Path

HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent))

from prozess_daten import DOKUMENTE, SCHRITTE, FRAGEN, SYSTEME, AUSWERTUNGSSTATUS  # noqa: E402

SCHRITTE_KOPF = ["Prozess-ID", "Schritt-Nr.", "Tätigkeit", "Ausführende Person / Rolle", "Eingaben",
                 "System", "Ergebnis", "Übergabe", "Freigabe", "Ausnahme / nächster Schritt",
                 "Bearbeitungszeit", "Wartezeit", "Nachweis / Prüfstatus"]
FRAGEN_KOPF = ["Frage-ID", "Prozessbezug", "Frage", "Klärung durch", "Nächster Schritt", "Fälligkeit",
               "Status", "Antwort / Entscheidung", "Nachweis"]
SYSTEME_KOPF = ["Daten-ID", "System / Datei / Ablage", "Inhalt", "Prozessbezug", "Pflegeverantwortlicher",
                "Führende Datenquelle", "Speicherort", "Übertragungswege", "Datenqualität", "Migrationsbedarf"]
DOKUMENTE_KOPF = ["Nummer", "Revision", "Titel", "Geltungsbereich", "Prozess", "Auswertungsstatus"]


def schreibe(pfad, kopf, zeilen):
    with open(pfad, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(kopf)
        w.writerows(zeilen)


if __name__ == "__main__":
    schreibe(HIER / "ablaufschritte.csv", SCHRITTE_KOPF, SCHRITTE)
    schreibe(HIER / "offene_fragen.csv", FRAGEN_KOPF,
             [[f"Q{i:02d}", f[0], f[1], f[2], "", "", *(f[3:] if len(f) > 3 else ("offen", "", ""))]
              for i, f in enumerate(FRAGEN, 1)])
    schreibe(HIER / "systeme_daten.csv", SYSTEME_KOPF, SYSTEME)
    labels = dict(AUSWERTUNGSSTATUS)
    schreibe(HIER.parent / "arbeitsanweisungen.csv", DOKUMENTE_KOPF,
             [[n, r, t, g, p, labels[s]] for n, r, t, g, p, s in DOKUMENTE])
