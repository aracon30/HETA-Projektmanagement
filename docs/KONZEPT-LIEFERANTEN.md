# Konzept: Reiter „Lieferanten“ – Lieferantenbewertung nach ISO 9001 Kap. 8.4

**Status:** Entwurf v0.1 zur Abstimmung (noch nicht umgesetzt)
**Grundlage:** Excel-Datei `Lieferantenbewertung_HETA.xlsx` (Neuaufbau 10/2026,
ersetzt die alte Makro-Datei `Lieferanten-_bewertung-Blanco.xls`). Das Tool
übernimmt **dieselbe Bewertungslogik**, damit Excel und Tool während des
Übergangs dieselben Ergebnisse liefern.

> **Sprachregelung:** wie im Reiter „Prozesse“ – kein ERP-Produktname in der
> Oberfläche. Die Kriterien sind bewusst so gebaut, dass sie bei einer
> möglichen Einführung eines ERP-Systems 1:1 übernommen werden können.

---

## 1. Ziel

- Lieferanten **nachvollziehbar und regelmäßig** bewerten (Nachweis fürs
  ISO-9001-Audit, Kap. 8.4: Kriterien für Beurteilung, Auswahl,
  Leistungsüberwachung und Neubeurteilung + dokumentierte Ergebnisse und
  Maßnahmen).
- Bewertung so schnell machen, dass sie im Wareneingang tatsächlich passiert
  (Ziel: < 30 Sekunden pro Lieferung).
- Schwache Lieferanten früh erkennen und Maßnahmen bis zur Wirksamkeitsprüfung
  verfolgen.

**Abgrenzung:** Kernelement des Tools bleibt der Verlauf in den Aufträgen. Die
Lieferantenbewertung ist ein **eigener Reiter**: Die Auftrags-Detailansicht
ändert sich nicht. Die Verknüpfung zu Aufträgen ist optional (Kommission
auswählbar). Es gibt kein Bestell- oder Einkaufsmodul, also kein ERP-Ersatz.

---

## 2. Bewertungsmodell (identisch zur Excel-Datei)

### 2.1 Zwei Ebenen

| Ebene | Wann / wer | Kriterien (Gewicht) |
|---|---|---|
| **Lieferung** | bei jedem Wareneingang, Lager/Einkauf/Projektleitung | Termintreue (30 %), Mengentreue (15 %), Anlieferqualität (35 %), Dokumentation & Zeugnisse (20 %) |
| **Jahr** | 1× pro Lieferant und Jahr, Einkauf/QM | Preisniveau/Preis-Leistung (20 %), Kommunikation (15 %), Flexibilität (15 %), Reklamationsabwicklung (15 %), technische Kompetenz (10 %), Zertifizierungen & Nachweise (15 %), Nachhaltigkeit & Lieferkette (10 %) |

Jede Note 1–4 hat je Kriterium eine **konkrete Definition**. Beispiel
Termintreue: 1 = termingerecht · 2 = bis 3 AT Verzug, angekündigt · 3 = 4–10 AT
oder nicht angekündigt · 4 = > 10 AT oder Auftragstermin gefährdet. Der
vollständige Katalog steht als Startbestand in `lieferanten_daten.py` (siehe 5.3).

### 2.2 Rechnung

- Notenskala: 1 = 100 %, 2 = 70 %, 3 = 30 %, 4 = 0 % (einstellbar).
- **Ergebnis einer Bewertung** = Σ(Gewicht × Notenwert) / Σ(Gewicht der
  bewerteten Kriterien). Nicht bewertete Kriterien (leer) zählen nicht.
- **Jahresergebnis Lieferant** = 60 % × Ø aller Lieferungsbewertungen des
  Jahres + 40 % × Jahresbewertung (einstellbar). Fehlt ein Teil, zählt nur der
  vorhandene; das wird als „Datenbasis“ angezeigt.
- **Klassen:** A ≥ 90 % (bevorzugt) · B ≥ 75 % (Gespräch zu Schwachstellen) ·
  C < 75 % (Maßnahmenplan, ggf. bedingte Freigabe/Sperre). Grenzen und
  Konsequenztexte sind einstellbar.
- **Sofort-Hinweise:** Note 4 in einer Lieferungsbewertung → Hinweis
  „Reklamation/Maßnahme prüfen“ mit Button „Maßnahme anlegen“ (vorbelegt).

**Prüfkriterium für die Umsetzung:** Für dieselben Eingaben liefern Tool und
Excel-Datei dieselben Werte (Testfälle aus der Excel-Prüfung, z. B. Noten
2/1/2/1 → 80,5 %; Ø 83,25 % + Jahr 86,5 % → 84,55 %, Klasse B).

### 2.3 Ergebnis festschreiben?

Der Rechenweg muss für das Audit nachvollziehbar bleiben, auch wenn Gewichte
später geändert werden. Vorschlag:
- Gespeichert werden **die Einzelnoten**. Zusätzlich wird das Ergebnis zum
  Zeitpunkt des Speicherns als `ergebnis_gespeichert` abgelegt.
- Gewichte und Definitionen werden **versioniert** (`katalog_version`). Jede
  Bewertung merkt sich ihre Version. Ein geänderter Katalog wirkt erst auf
  neue Bewertungen, alte Jahre bleiben unverändert.
- Kriterien werden nie gelöscht, nur deaktiviert.

---

## 3. Oberfläche: Reiter „Lieferanten“

Neuer Tab-Button nach „Prozesse“. Innerhalb des Reiters gibt es Unteransichten
als Umschalter, so wie die Prozesskette/der Baum im Reiter „Prozesse“.

### 3.1 Lieferanten (Stammliste)
Tabelle mit Suche/Filter: Name, Warengruppe, Ansprechpartner, Freigabestatus
(freigegeben / bedingt freigegeben / gesperrt / neu – in Prüfung), aktuelle
Klasse, Zertifikate mit Ablaufdatum und Ampel (gültig / läuft in 90 Tagen ab /
abgelaufen). Klick öffnet den **Lieferanten-Steckbrief**: Stammdaten,
Zertifikate, Verlauf aller Bewertungen (kleine Linie Ergebnis über Zeit),
Maßnahmen, Notizen.

### 3.2 Lieferung bewerten
Schnellformular, optimiert für den Wareneingang:
- Lieferant (Suchfeld), Datum (vorbelegt heute), Bestell-Nr., **Kommission
  optional** (Auswahl aus offenen Aufträgen), Bewerter (vorbelegt zuletzt
  gewählter Nutzer).
- Je Kriterium vier Klick-Buttons 1–4, der Definitionstext steht unter dem
  Button (kein Nachschlagen). „–“ = nicht bewertet.
- Bei Note 3/4 ist ein Bemerkungsfeld Pflicht. Bei Note 4 erscheint der Button
  „Maßnahme anlegen“.
- Nach dem Speichern wird das Ergebnis mit Klasse sofort angezeigt, das
  Formular bleibt für die nächste Lieferung offen.

### 3.3 Jahresbewertung
Liste „fällig im Jahr X“: alle freigegebenen Lieferanten mit Lieferungen im
Jahr, aber ohne Jahresbewertung. Gleiches Button-Formular mit 7 Kriterien.

### 3.4 Auswertung
Jahr wählen. Tabelle je Lieferant: Lieferungen (Anzahl), Ø Lieferungen,
Jahresbewertung, Gesamt, Datenbasis, Klasse, Vorjahr, Trend, Konsequenz,
offene Maßnahmen, Zertifikatsstatus, Ø Note je Lieferkriterium (zeigt die
Schwachstelle). Darüber Kennzahlen: Anzahl A/B/C, „C ohne offene Maßnahme“
(rot), fällige Jahresbewertungen, ablaufende Zertifikate.
**CSV-Export** im Spaltenformat der Excel-Datei (für Audit und Ablage), analog
zum CSV-Export im Reiter „Prozesse“.

### 3.5 Maßnahmen (eigene Liste)
Lieferant, Anlass (Klasse C / Klasse B / Reklamation – Note 4 / Zertifikat
abgelaufen / Lieferantengespräch / Sonstiges), Beschreibung, Verantwortlich
(Nutzerliste), Termin, Status (offen / in Arbeit / erledigt), Wirksamkeit
geprüft am + Ergebnis. Überfällige Termine rot. Bei „Verantwortlich zuweisen“
geht eine **Mail über den bestehenden SMTP-Weg** (`mail_client.py`) raus,
genauso wie bei „Aufgabe erstellen“ im Verlauf. Maßnahmen tauchen zusätzlich im
Reiter „Aufgaben“ auf (gleiche Darstellung wie offene Verlaufseinträge), damit
es nur eine Stelle für „was liegt bei mir“ gibt.

### 3.6 Einstellungen (Zahnrad im Reiter)
Kriterienkatalog (Namen, Gewichte, Notendefinitionen; Summenprüfung 100 %),
Notenskala, Klassengrenzen und Konsequenzen, Anteil Lieferung/Jahr,
Vorwarnzeit Zertifikate. Speichern erzeugt eine neue Katalogversion (2.3).

**Live-Aktualisierung:** Der Reiter wird in `pollForUpdates()` aufgenommen.
Das Schnellformular zählt als offene Eingabe (`hasOpenComposeForm()`), damit
beim Bewerten nichts verloren geht.

---

## 4. Datenmodell (neu, in `models.py`)

| Tabelle | Wichtige Felder |
|---|---|
| `lieferanten` | id, name (unique), warengruppe, ansprechpartner, kontakt, freigabestatus, notiz, aktiv, created_at |
| `lieferanten_zertifikate` | id, lieferant_id, art (ISO 9001, AD 2000 HP0, DGRL, ASME, ISO 14001 …), nummer, gueltig_bis, datei_pfad (K-Laufwerk-Link wie bei Aufträgen) |
| `bewertung_kriterien` | id, ebene (`lieferung`/`jahr`), reihenfolge, bezeichnung, gewicht, note1..note4 (Definitionstexte), aktiv, katalog_version |
| `bewertung_einstellungen` | key/value: notenwerte, klassengrenzen, konsequenzen, anteil_lieferung, anteil_jahr, warn_tage, aktuelle katalog_version |
| `lieferungsbewertungen` | id, lieferant_id, datum, bestell_nr, item_id (optional → Kommission), bewerter (User), bemerkung, katalog_version, ergebnis_gespeichert, created_at |
| `jahresbewertungen` | id, lieferant_id, jahr, datum, bewerter, bemerkung, katalog_version, ergebnis_gespeichert; unique (lieferant_id, jahr) |
| `bewertung_noten` | id, bewertung_typ (`lieferung`/`jahr`), bewertung_id, kriterium_id, note (1–4) – nur bewertete Kriterien als Zeile |
| `lieferanten_massnahmen` | id, lieferant_id, anlass, beschreibung, verantwortlich (User), termin, status, wirksam_geprueft_am, wirksam_ergebnis, ausloeser_bewertung_id (optional), mail_gesendet, created_at |

Alle Berechnungen (2.2) laufen in einer Funktion in `lieferanten_api.py`, die
sowohl die API als auch der CSV-Export nutzen. So gibt es einen einzigen
Rechenweg, der mit Testfällen abgesichert ist.

---

## 5. Technik & Betrieb

### 5.1 Code-Struktur (Muster wie `prozesse_api.py` / `asme_api.py`)
- `lieferanten_api.py` als Blueprint, registriert in `app.py`.
- Frontend-Block im `static/index.html` (Vanilla JS, kein Build-Step), eigene
  Render-Funktionen `renderLieferanten…`.

### 5.2 API (Auszug)
`GET/POST /api/lieferanten`, `GET/PATCH /api/lieferanten/<id>` ·
`POST /api/lieferanten/<id>/zertifikate` ·
`GET/POST /api/lieferungsbewertungen` · `GET/POST /api/jahresbewertungen` ·
`GET/POST/PATCH /api/lieferanten-massnahmen` ·
`GET /api/lieferanten/auswertung?jahr=2026` (+ `&format=csv`) ·
`GET/PUT /api/bewertung/katalog`

### 5.3 Migration & Startbestand
- Neue Tabellen über `migrate.py` (additiv, keine bestehende Tabelle wird
  angefasst).
- Startbestand (Kriterienkatalog v1, Einstellungen, Lieferantennamen aus der
  alten Excel-Datei) in `lieferanten_daten.py`. Eingespielt wird er idempotent
  über ein `seed_lieferanten.py`, das `update.sh` aufruft, nach demselben
  Prinzip wie `seed_prozesse.py`/`startbestand_stand`. Nutzeränderungen werden
  nie überschrieben.
- **Excel-Übergang:** einmaliger Import der Blätter „Lieferanten“,
  „Lieferungsbewertung“, „Jahresbewertung“, „Maßnahmen“ aus
  `Lieferantenbewertung_HETA.xlsx` (Vorschau + Bestätigen, Abgleich über
  Lieferantenname, keine Duplikate, also dasselbe Muster wie beim ERP-Import
  der Aufträge).

### 5.4 Bekannte Grenze: kein Login
Solange es keine Login-/Rechteverwaltung gibt (Ausbaustufe 1 laut
CLAUDE.md), wird der Bewerter aus der Nutzerliste **ausgewählt**, nicht
automatisch erkannt. Fürs Audit reicht das als Nachweis „wer hat bewertet“.
Manipulationssicher ist es nicht. Sobald Login kommt, wird das Feld automatisch
befüllt.

---

## 6. Ausbaustufen

1. **Stufe 1 – Grundfunktion:** Lieferantenliste, Lieferung bewerten,
   Jahresbewertung, Auswertung + CSV-Export, Katalog als Startbestand (noch
   ohne Einstellungs-Oberfläche).
2. **Stufe 2 – Maßnahmen & Zertifikate:** Maßnahmenliste mit Mail und
   Einbindung in den Reiter „Aufgaben“, Zertifikate mit Ablaufwarnung,
   Lieferanten-Steckbrief.
3. **Stufe 3 – Pflege & Übergang:** Einstellungs-Oberfläche mit
   Katalogversionierung, Excel-Import.
4. **Später/optional:**
   - Verknüpfung mit den ASME-Lieferantenbestellungen
     (`LieferantenBestellung.lieferant` ist heute Freitext → Auswahl aus
     `lieferanten`). Beim Erzeugen des WE-Kontrollscheins könnte gleich die
     Lieferungsbewertung angeboten werden.
   - Termintreue automatisch aus Lieferdatum (Bestellung) vs. Datum Wareneingang.

---

## 7. Offene Fragen (vor der Umsetzung klären)

1. **Kriterien & Gewichte:** Katalog v1 ist ein Vorschlag. Abstimmung mit
   QM/Einkauf vor dem Audit? Insbesondere 60/40 und die Klassengrenzen.
2. **Wer bewertet Lieferungen?** Lager/Wareneingang, Einkauf oder
   Projektleitung? Davon hängt ab, ob das Schnellformular auch am Tablet im
   Wareneingang laufen muss (Layout für schmale Bildschirme).
3. **Welche Lieferanten werden bewertet?** Alle, oder nur
   qualitätsrelevante Warengruppen (z. B. Werkstoffe, Zukaufteile Druckgeräte,
   Lohnfertigung)? Dann gäbe es ein Feld „bewertungspflichtig“.
4. **Festschreiben (2.3):** Ist Katalogversionierung gewünscht, oder reicht
   „Gewichtsänderung rechnet alles neu“? Versionierung ist audit-sicherer,
   macht aber mehr Aufwand.
5. **Freigabestatus:** Soll „gesperrt“ irgendwo im Tool eine Wirkung haben
   (z. B. Warnung bei der ASME-Bestellung), oder ist er nur Information?
