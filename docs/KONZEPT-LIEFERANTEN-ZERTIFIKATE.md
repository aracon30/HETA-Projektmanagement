# Konzept: Zertifikatsliste je Lieferant (FB-0019 „Liste freigegebener Lieferanten“)

**Status:** Entwurf zur Abstimmung (noch nicht umgesetzt)
**Grundlage:** hochgeladene Excel `FB_16.01_Liste_freigegebener_Lieferanten_01.xlsx`
(Stand 12.11.2026, offizielles QM-Formblatt FB-0019), 314 Zeilen über 269
Firmen. Setzt die in `docs/KONZEPT-LIEFERANTEN.md` Abschnitt 6 (Stufe 2)
bereits vorgesehene, bisher nicht umgesetzte Funktion „Zertifikate mit
Ablaufwarnung“ um — dort als `lieferanten_zertifikate`-Tabelle grob skizziert,
hier anhand der echten Excel-Struktur konkretisiert.

---

## 1. Ziel

- Die separat von QM gepflegte Excel durch eine im Portal geführte Liste
  ablösen. **Nach dem einmaligen Import ist das Portal alleinige Quelle** —
  keine Parallelpflege der Excel mehr.
- Pro Lieferant auf einen Blick: welche Normen/Zertifikate sind gültig,
  welche laufen bald ab (≤ 90 Tage, wie in der Excel), welche sind
  abgelaufen, wer ist gesperrt.
- Exportierbar für Audits (FB-0019 muss weiterhin als Nachweis vorlegbar sein).

**Abgrenzung:** Das ist eine Erweiterung der bestehenden Lieferantenbewertung
im Reiter „Firmen“, kein neuer Reiter. Mit der eigentlichen
Lieferungs-/Jahresbewertung (`lieferungsbewertungen`/`jahresbewertungen`)
wird nicht verrechnet — die Excel-Spalten „Letzte Bestellung“/„Letzte
Bewertung“ sind reine Altdaten-Anzeige (siehe 3.2).

---

## 2. Warum eine neue Tabelle, nicht nur `Firma.warengruppe`

26 der 314 Excel-Zeilen gehören zu Firmen, die **mehrfach** mit
unterschiedlicher Warengruppe gelistet sind (Schlüssel in der Excel ist
`Lieferant|Warengruppe`, nicht nur der Name) — z. B. „Bieber + Marburg“ 5×,
„Flaboform GmbH“ 5×, jede Zeile mit eigenem Zertifikatsstand. `Firma` hat
aber nur ein einzelnes `warengruppe`-Feld. Deshalb: eine neue Tabelle,
**1 Firma : n Zertifizierungszeilen** (eine Zeile je Warengruppe-Kombination
aus der Excel).

---

## 3. Datenmodell (neu, in `models.py`)

### 3.1 `LieferantenZertifizierung`

| Feld | Typ | Bedeutung |
|---|---|---|
| `id` | Integer | PK |
| `firma_id` | FK → `firmen.id` | |
| `warengruppe` | String | wie Excel-Spalte C, **nicht** dasselbe Feld wie `Firma.warengruppe` |
| `iso9001_gueltig_bis` | Date, nullable | Excel Spalte E |
| `ad2000_hp0_bis` … `whg_bis` | je Date, nullable | die 11 Normen aus „Cert_Daten“, **feste Spalten** (kein Katalog, s. u.) |
| `sperr_datum` | Date, nullable | Excel „Sperr-Datum“; gesetzt ⇒ diese Zeile gilt als gesperrt |
| `info` | Text, nullable | Freitext (Excel „Info“) |
| `letzte_bestellung_jahr` | Integer, nullable | **Altdaten**, nur Anzeige |
| `letzte_bewertung_am` | Date, nullable | **Altdaten**, nur Anzeige — unabhängig von echten Portal-Bewertungen |
| `created_at` | DateTime | |

`status` (okay / bald_ablaufend / abgelaufen) wird **nicht gespeichert**,
sondern bei jedem Abruf aus `iso9001_gueltig_bis` live berechnet — wie in der
Excel-Formel, damit er nie veraltet:

```
kein Datum       → kein Status
< heute          → abgelaufen
< heute + 90 Tage → bald_ablaufend   (Warnschwelle fest im Code, WARN_TAGE = 90)
sonst            → okay
```

**Normen fest im Code** (Nutzer-Entscheidung): die 11 Spalten sind feste
Modellfelder, kein pflegbarer Katalog wie bei den Bewertungskriterien. Eine
neue Norm braucht künftig eine Migration + Code-Änderung — dafür ist die
Tabelle einfacher und das Formular eine simple feste Maske statt eines
generischen Editors.

### 3.2 Verhältnis zu bestehenden Tabellen

- **Keine Änderung** an `Firma.freigabestatus` durch den Import — bleibt wie
  bisher manuell gepflegt. Eine `LieferantenZertifizierung` mit gesetztem
  `sperr_datum` ist unabhängig davon „gesperrt“. *(Siehe offene Frage 7.1.)*
- `letzte_bestellung_jahr`/`letzte_bewertung_am` werden **1:1 aus der Excel
  übernommen und nur angezeigt** — keine Verrechnung mit
  `lieferungsbewertungen`/`jahresbewertungen`. Für die echten, laufenden
  Bewertungen bleibt das bestehende Formular im Reiter „Firmen“ die einzige
  Quelle.

---

## 4. Oberfläche

Neue Unteransicht **„Zertifikate“** in der Sub-Navigation des Firmen-Reiters,
neben „Lieferung bewerten“ / „Jahresbewertung“ / „Auswertung“ (gleiches
Muster, `fm-subnav`):

- Kennzahlen oben wie im Excel-Dashboard: Gesamt / Okay / Bald ablaufend /
  Kritisch / Gesperrt (einfache Zählung über alle Zeilen).
- Tabelle wie `Supplier_Master`: Firma, Warengruppe, ISO-9001-Status (farbig),
  Tage bis Ablauf, Info — mit Suche und Status-Filter.
- Klick auf eine Zeile öffnet die Detailmaske mit allen 12 Datumsfeldern
  (ISO 9001 + 11 Normen), Sperr-Datum, Info.
- Im Firma-Steckbrief (wo schon die Bewertungen stehen) zusätzlich eine
  kompakte Zertifikats-Übersicht, wenn die Firma mindestens eine
  Zertifizierungszeile hat.

---

## 5. Import (einmalig)

Neues Skript `import_lieferanten_zertifikate.py`, Vorschau + Bestätigen wie
beim Assistenten „Kunden zuordnen“ bzw. dem ERP-Import:

1. Liest `Supplier_Master` + `Cert_Daten` aus der hochgeladenen Excel.
2. Gleicht jeden Lieferantennamen gegen bestehende Firmen ab
   (Ähnlichkeitsvergleich wie beim Zuordnen-Assistenten) — Treffer verknüpft,
   sonst wird eine neue Firma mit Rolle „Lieferant“ angelegt.
   `warengruppe` am Firma-Datensatz wird dabei **nicht** überschrieben (die
   Excel-Warengruppe gehört auf die neue Zertifizierungszeile, nicht auf die
   Firma).
3. Legt je Excel-Zeile eine `LieferantenZertifizierung` an.
4. **Vorher:** die vier erkennbaren Test-Lieferanten (Muster Industrie GmbH,
   Regressionstest Lieferant, Review Test Lieferant GmbH & Co KG,
   Testlieferant GmbH) werden gelöscht — *aber nur, wenn sie keine echten
   Verknüpfungen (Aufträge, Bewertungen, Aktivitäten) haben*; sonst Warnung
   statt automatischem Löschen, damit nichts Echtes verloren geht.

Einmaliges Skript, kein wiederkehrender Abgleich wie beim ERP-Import — das
Portal wird ja laut Entscheidung die alleinige Quelle, eine neue Excel ist
danach nicht mehr vorgesehen.

---

## 6. Export für Audits

Vorschlag: **Excel-Export** (`GET /api/lieferanten/zertifikate/export`,
openpyxl) statt eines Word/PDF-Dokuments wie bei der Versandliste — hier geht
es um eine reine, breite Datentabelle (12+ Spalten), kein Brief mit
Briefkopf. Format entspricht in etwa der Ursprungs-Excel (Supplier_Master +
Legende), damit ein Auditor nichts Neues lernen muss.

*Bitte bestätigen: passt Excel, oder soll es doch wie bei der Versandliste
ein PDF sein?*

---

## 7. Erinnerungsmail an den Einkauf (13.11.2026 ergänzt)

**Ziel:** `einkauf@heta.de` soll automatisch benachrichtigt werden, wenn bei
der Zertifikatsliste etwas zu tun ist — niemand soll die Unteransicht erst
manuell aufrufen müssen, um einen bald ablaufenden Nachweis zu bemerken.

**Kanal:** dieselbe SMTP-Infrastruktur wie bei der Aufgaben-Benachrichtigung
(`mail_client.py`, `SMTP_HOST=192.168.80.30`, s. CLAUDE.md) — `mail_client.py`
bekommt dafür eine generische `send_mail(to, subject, body_text)`-Funktion
(die bestehende `send_task_mail()` ruft sie dann intern auch auf), damit
nicht zweimal dieselbe SMTP-Verbindungslogik existiert.

**Neu für dieses Tool: der erste wiederkehrende Hintergrund-Job.** Bisher
passiert in der Auftragspipeline alles nutzergetrieben (Klick → Aktion) oder
per Live-Polling vom Browser aus — es gibt noch keinen serverseitigen
Zeitplan. Vorschlag: ein neues, eigenständiges Skript
`pruefe_zertifikate_faelligkeiten.py` (Muster wie `seed_lieferanten.py` —
direkt ausführbar, nutzt dieselbe Flask-App/DB), das:

1. alle `LieferantenZertifizierung`-Zeilen mit Status `bald_ablaufend` oder
   `abgelaufen` sammelt (gesperrte Lieferanten bewusst **nicht** mit in
   dieser Mail — eine Sperre ist eine bewusste Entscheidung, kein
   übersehener Ablauf),
2. daraus eine Übersichtsmail an `einkauf@heta.de` zusammenstellt — **immer
   der volle aktuelle Stand**, kein Abgleich gegen die letzte Mail (einfacher,
   kein zusätzlicher "zuletzt gemeldet"-Stand nötig; ein liegen gebliebener
   Fall taucht dadurch bewusst jede Woche wieder auf, bis er erledigt ist),
3. nur verschickt, wenn es mindestens einen Fall gibt (keine leeren
   "alles in Ordnung"-Mails).

Das Skript selbst läuft nicht von allein — es braucht einen **Cron-Eintrag
auf dem Server** (`crontab -e` für den Nutzer `heta`, **wöchentlich, montags
7 Uhr**: `0 7 * * 1 cd /opt/projektbesprechung && ./venv/bin/python
pruefe_zertifikate_faelligkeiten.py`). Das ist einmalig von Hand auf
Produktiv- **und** Testserver einzurichten (wie bei den anderen
Server-Stolperfallen in CLAUDE.md dokumentiert) — `update.sh` kann das nicht
automatisch übernehmen, weil es selbst nur bei einem manuellen Update läuft,
nicht als Dauer-Prozess.

---

## 8. Offene Punkte (bitte vor der Umsetzung klären)

1. **Sperr-Granularität:** Gilt eine Sperre nur für die betroffene
   Warengruppen-Zeile, oder immer gleich für die ganze Firma? Laut Rückmeldung
   noch intern zu klären — bis dahin bleibt `sperr_datum` nur auf der
   Zertifizierungszeile gespeichert, `Firma.freigabestatus` unangetastet. Lässt
   sich später verknüpfen, ohne das Datenmodell zu ändern.
2. **Export-Format:** Excel (Vorschlag oben) oder PDF wie Versandliste?
3. ~~Warnschwelle 90 Tage~~ — **entschieden (13.11.2026):** fest im Code,
   `WARN_TAGE = 90`, wie in der Excel. Passt zur Entscheidung „Normen fest im
   Code" — keine Einstellungs-Oberfläche dafür.
4. **Wer pflegt künftig?** Vermutlich QM/Einkauf — relevant für die Frage, ob
   die neue Unteransicht wie die übrige Lieferantenbewertung ganz normal im
   Reiter „Firmen“ für jeden sichtbar ist, oder ob da (später, mit Login)
   Rechte eingeschränkt werden sollten.
5. ~~Häufigkeit/Inhalt/Wiederholung der Erinnerungsmail~~ — **entschieden
   (13.11.2026):** wöchentlich (montags 7 Uhr), Inhalt „bald ablaufend" +
   „abgelaufen" (gesperrte Lieferanten nicht mit drin), immer der volle
   aktuelle Stand ohne Wiederholungs-Tracking.
