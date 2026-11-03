# Versandliste-Vorlage

`Blanco_Querformat.docx` ist der leere HETA-Briefbogen im Querformat (A4),
von Philipp bereitgestellt (03.11.2026) — Kopf mit Logo/Firmenname, Fußzeile
mit Adresse/Bank/Zertifikat als eingebettete Grafiken (`media/image2.emf` +
`image3.emf`). Wird unverändert als Original aufbewahrt.

`Versandliste.docx` ist die daraus gebaute docxtpl-Vorlage (Skript
`_umbau_original.py`, als Vorlage für künftige Umbauten dieser Art):

- Seite auf **A3 Querformat** umgestellt (420 × 297 mm) — HETA-Blanko-Vorlagen
  sind sonst immer A4, aber eine Versandliste mit vielen Spalten
  (Liefertermin/Kommission/Kunde/Lieferumfang/Priorität/Status/
  Lieferbedingungen/Projektleiter) braucht mehr Breite für die Werkstatt.
- **Fußzeile ersetzt**: Das Original-EMF-Bild mit dem Fußzeilentext ist absolut
  positioniert (`wp:anchor`, `positionH relativeFrom="column"`, `positionV
  relativeFrom="page"`) passend zur ursprünglichen A4-Breite/-Höhe. Bei A3
  verschiebt sich die column-relative Verankerung, und beim PDF-Export über
  `soffice --headless --convert-to pdf` erscheinen zwei leicht versetzte,
  überlappende Kopien des Fußzeilentexts (getestet 03.11.2026 — im unveränderten
  A4-Original tritt der Fehler nicht auf). Da der Bild-Fußzeilentext ohnehin
  nicht live bearbeitbar ist, wurde er durch echten, kurzen Text ersetzt (siehe
  `baue_footer()` im Skript) — robust unabhängig von der Seitengröße.
- Kopf (Logo + „// HETA Verfahrenstechnik GmbH") ist **unverändert** — nutzt
  echten Text + ein normales Bild (`media/image1.jpeg`), kein fragiles EMF mit
  Absolut-Positionierung, skaliert daher auf A3 problemlos.
- Tabellen-Kopfzeile wiederholt sich auf jeder Folgeseite (`w:tblHeader`).
- Zeilen-Schleife im **3-Zeilen-Muster** wie bei der Auftragsbestätigung
  (`vorlagen/auftragsbestaetigung/DE/Auftragsbestaetigung.docx`): eigene Zeile
  mit `{%tr for a in auftraege %}`, die eigentliche Datenzeile mit
  `{{ a.feld }}`-Platzhaltern, eigene Zeile mit `{%tr endfor %}`.

## Platzhalter

| Platzhalter | Inhalt |
|---|---|
| `{{ zeitraum_text }}` | z.B. „Zeitraum 03.11.2026 – 17.11.2026" oder „Alle offenen Aufträge bis 17.11.2026" (ohne gesetztes "von") |
| `{{ erzeugt_am }}` | Zeitstempel der PDF-Erzeugung |
| `{{ a.liefertermin_de }}`, `{{ a.kommission }}`, `{{ a.kunde }}`, `{{ a.lieferumfang }}`, `{{ a.prioLabel }}`, `{{ a.statusLabel }}`, `{{ a.lieferbedingungen }}`, `{{ a.projektleiter }}` | je Zeile der Tabelle, siehe `versandliste_api.py:auftrag_zeile()` |

## Layout-Änderung

`_umbau_original.py` erneut ausführen (baut `Versandliste.docx` komplett neu
aus `Blanco_Querformat.docx`) oder `Versandliste.docx` direkt in Word
anpassen — Platzhalter dabei nicht verändern. Immer als PDF rendern und mit
einem Beispiel vergleichen, nicht nur die Struktur/XML ansehen (siehe
CLAUDE.md, Lehre aus der Auftragsbestätigung-Kundenadresse).
