# Konzept: Reiter „Firmen“ – gemeinsame Firmenliste mit schlankem CRM

**Status:** Entwurf v0.1 zur Abstimmung (noch nicht umgesetzt)
**Zusammenhang:** Bildet die Grundlage für die Lieferantenbewertung
(`docs/KONZEPT-LIEFERANTEN.md`). Kunden und Lieferanten werden **nicht** in zwei
getrennten Listen geführt, sondern in einer Firmenliste mit Rollen.

> **Leitplanke:** Das Tool bleibt ein Werkzeug zur Projektverfolgung, kein ERP
> (siehe CLAUDE.md). Das CRM ist bewusst schlank: Es gibt kein Angebots- oder
> Preiswesen und keine Umsatz- oder Provisionsauswertung. Firmen und Kontakte
> sind genau die Daten, die bei einer möglichen Einführung eines ERP-Systems
> umziehen würden. Deshalb ist der Export dafür von Anfang an mitgedacht.

---

## 1. Ziel

- **Eine Firma = ein Datensatz.** Heute steht der Kunde als Freitext an jeder
  Anfrage, jedem Angebot und jedem Auftrag (`items.kunde`, `kunden_adresse`,
  `versand_adresse`). Das führt zu Schreibvarianten und Doppelerfassung, und
  man sieht nicht, was bei einem Kunden insgesamt läuft.
- **Akquise nachvollziehbar machen:** Ansprechpartner, Kontakthistorie
  (Anruf, Mail, Besuch, Messe) und Wiedervorlagen an einer Stelle, statt
  verteilt über Outlook, Excel-Listen und Visitenkarten.
- **Firmen-Steckbrief:** alle Anfragen, Angebote, Aufträge, Kontakte,
  Aktivitäten und bei Lieferanten die Bewertung auf einen Blick.

---

## 2. Voraussetzung: Login und Datenschutz

Das CRM speichert **personenbezogene Daten** (Namen, Telefon, Mail,
Gesprächsnotizen). Das Tool ist heute für jeden im Netz bzw. per VPN offen.
Deshalb gilt:

1. **Login/Rechteverwaltung (Ausbaustufe 1 laut CLAUDE.md) kommt vor dem
   CRM-Modul.** Mindestens: Anmeldung pro Nutzer, Rolle „Vertrieb/Einkauf“
   für Kontakte und Notizen, Protokoll „angelegt/geändert von“.
2. **Datenschutz-Grundregeln** (vorab mit dem Datenschutzbeauftragten der
   PACO-Gruppe abstimmen):
   - nur geschäftliche Kontaktdaten, keine privaten Notizen über Personen
   - Löschkonzept: Kontakte ohne Aktivität seit X Jahren werden zur Prüfung
     angezeigt, Löschen mit einem Klick
   - Auskunft: Export aller Daten zu einer Person auf Knopfdruck
3. **Feld „Kontaktweg erlaubt“ je Kontakt** (Mail-Werbung / Telefon /
   nur auf Anfrage). Hintergrund: Werbe-Mails ohne vorherige Einwilligung
   sind in Deutschland auch im B2B-Bereich unzulässig (§ 7 UWG). Bei
   Visitenkarten-Kontakten wird festgehalten, ob und wann eine Einwilligung
   vorliegt.

---

## 3. Datenmodell (neu, in `models.py`)

| Tabelle | Wichtige Felder |
|---|---|
| `firmen` | id, name, kurzname (Suchbegriff), konzern_id (optional → übergeordnete Firma, z. B. BASF SE ↔ BASF Lampertheim), rollen (Kunde / Interessent / Lieferant / Partner, mehrfach möglich), branche, land, website, lieferantenportal (Name + Status der Registrierung beim Kunden, z. B. „ORLEN Connect – freigegeben“), quelle (Messe, Patt, Visitenkarte, Bestandskunde …), status (aktiv / ruhend / kein Interesse), notiz, aktiv, created_at/by |
| `firmen_adressen` | id, firma_id, art (Haupt / Rechnung / Lieferung / Werk), zeilen (mehrzeilig, wie heute `kunden_adresse`), standard (bool) |
| `kontakte` | id, firma_id, anrede, vorname, nachname, funktion, abteilung, telefon, mobil, email, kontaktweg_erlaubt, einwilligung_am, aktiv, notiz |
| `aktivitaeten` | id, firma_id, kontakt_id (optional), item_id (optional → Anfrage/Angebot/Auftrag), art (Anruf / Mail / Besuch / Messe / Teams / Sonstiges), datum, nutzer, inhalt, wiedervorlage_am, wiedervorlage_status (offen / erledigt) |

**Änderung an `items`** (additiv über `migrate.py`): `firma_id`, `kontakt_id`,
`adresse_id`, `versand_adresse_id` (alle optional). Die bisherigen
Freitextfelder bleiben erhalten und dienen als Fallback. Die
Auftragsbestätigung (`ab_api.py`) nimmt die Adresse der verknüpften Firma,
wenn eine gesetzt ist, sonst wie heute den Freitext.

**Lieferantenbewertung:** Die Tabelle `lieferanten` aus dem
Lieferanten-Konzept entfällt. Bewertungen, Zertifikate und Maßnahmen hängen an
`firmen` (Rolle Lieferant). `LieferantenBestellung.lieferant` (heute
Freitext) kann später ebenfalls auf eine Firma zeigen.

---

## 4. Oberfläche: Reiter „Firmen“

Ein Reiter statt zwei (Kunden + Lieferanten), damit die Tab-Leiste nicht
wächst. Unteransichten als Umschalter:

### 4.1 Firmenliste
Suche (Name, Kurzname, Ort, Kontaktname), Filter nach Rolle, Status, Branche,
Quelle. Spalten: Name, Rollen, Ort, letzter Kontakt, nächste Wiedervorlage,
offene Angebote (Anzahl/Wert), laufende Aufträge, bei Lieferanten die Klasse
A/B/C.

### 4.2 Firmen-Steckbrief
- Kopf: Stammdaten, Adressen, Lieferantenportal, Konzernzugehörigkeit
- Kontakte (mit Kontaktweg-Ampel)
- **Zeitstrahl:** Aktivitäten + Anfragen/Angebote/Aufträge der Firma
  chronologisch; Klick auf einen Vorgang springt in den bestehenden Reiter
- „+ Aktivität“: Schnellerfassung (Art, Kontakt, Text, optional Wiedervorlage)
- bei Rolle Lieferant: Bereich „Bewertung“ (aus dem Lieferanten-Konzept)

### 4.3 Wiedervorlagen
Liste aller offenen Wiedervorlagen, nach Datum, filterbar nach Nutzer.
Wiedervorlagen erscheinen **zusätzlich im Reiter „Aufgaben“**, damit es nur
eine Stelle für „was liegt bei mir“ gibt. Optional geht am Fälligkeitstag eine
Erinnerungs-Mail über den bestehenden SMTP-Weg (`mail_client.py`) raus.

### 4.4 Lieferantenbewertung
Die Ansichten aus `docs/KONZEPT-LIEFERANTEN.md` (Lieferung bewerten,
Jahresbewertung, Auswertung, Maßnahmen) liegen als weitere Unteransichten im
selben Reiter.

### 4.5 Einbindung in die bestehenden Reiter
- Anfrage/Angebot/Auftrag anlegen: Feld „Kunde“ wird ein Suchfeld über
  `firmen`. Gibt es keinen Treffer, legt „+ neue Firma“ die Firma direkt an.
  Danach Kontakt- und Adressauswahl.
- Kundenname in Listen und Detailansicht wird klickbar und führt zum
  Firmen-Steckbrief.
- Kein neues Modul in der Auftrags-Detailansicht (Layout-Regel aus
  CLAUDE.md), nur der Link.

---

## 5. Übernahme der vorhandenen Daten

1. **Freitext-Kunden zuordnen:** Assistent „Kunden zuordnen“ zeigt alle
   unterschiedlichen `items.kunde`-Werte. Ähnliche Schreibweisen werden
   gruppiert (Normalisierung: Groß-/Kleinschreibung, GmbH/AG/SE, Leerzeichen,
   Ähnlichkeitsvergleich) und als Vorschlag „gleiche Firma“ angeboten.
   Ablauf wie beim ERP-Import der Aufträge: Vorschau → Bestätigen. Es entstehen
   keine Duplikate, und nichts wird ohne Bestätigung verknüpft.
2. **Kontakte importieren:** CSV-Import im Outlook-Kontakte-Format (Export aus
   Outlook) und eine einfache Excel-Vorlage, z. B. für die Visitenkarten.
   Abgleich über E-Mail-Adresse bzw. Firma + Nachname.
3. **Lieferanten:** Übernahme aus der Excel-Lieferantenbewertung (siehe
   Lieferanten-Konzept 5.3), Zuordnung zu bestehenden Firmen wie in Schritt 1.
4. **Export:** Firmen, Adressen, Kontakte und Aktivitäten als CSV, mit
   sprechenden Spaltennamen. Damit ist ein späterer Umzug in ein ERP-System
   oder ein anderes CRM ohne Programmierung möglich.

---

## 6. Technik

- `firmen_api.py` als Blueprint (Muster wie `prozesse_api.py`), registriert in
  `app.py`. Frontend-Block in `static/index.html` (Vanilla JS).
- API (Auszug): `GET/POST /api/firmen`, `GET/PATCH /api/firmen/<id>`,
  `…/<id>/kontakte`, `…/<id>/adressen`, `…/<id>/aktivitaeten`,
  `GET /api/wiedervorlagen`, `POST /api/firmen/zuordnen/preview|confirm`,
  `POST /api/kontakte/import/preview|confirm`, `GET /api/firmen/export`.
- Live-Aktualisierung: Firmenliste und Wiedervorlagen werden in
  `pollForUpdates()` aufgenommen. Die Formulare „+ Aktivität“/„+ Kontakt“
  zählen als offene Eingabe (`hasOpenComposeForm()`).
- Migration additiv (`migrate.py`), kein Startbestand nötig. Daten kommen
  ausschließlich über die Zuordnung/Importe aus Abschnitt 5.

---

## 7. Ausbaustufen

0. **Login/Rechteverwaltung** (Voraussetzung, siehe Abschnitt 2)
1. **Firmen & Zuordnung:** Firmenliste, Steckbrief, Adressen, Verknüpfung mit
   Anfragen/Angeboten/Aufträgen, Assistent „Kunden zuordnen“, AB nutzt
   Firmenadresse
2. **Kontakte & Aktivitäten:** Kontakte, Zeitstrahl, Wiedervorlagen inkl.
   Reiter „Aufgaben“ und Erinnerungs-Mail
3. **Lieferantenbewertung** auf Basis der Firmenliste (Lieferanten-Konzept
   Stufen 1–3)
4. **Import/Export:** Outlook-/Visitenkarten-Import, CSV-Export,
   Löschkonzept-Ansicht

---

## 8. Offene Fragen

1. **Welches System führt Firmen langfristig?** ServiceHub
   (`aracon30/HETA-Filterservice`) hat eigene Kunden und Kundenrollen. Es
   sollte keine dritte Kundenliste neben ServiceHub und einem möglichen
   ERP-System entstehen. Vorschlag: Dieses Tool führt die Firmen, ServiceHub
   übernimmt per Export/Abgleich. Das wird bei der Entscheidung zur möglichen
   ERP-Einführung neu bewertet.
2. **Wer pflegt?** Nur Vertrieb/Einkauf oder alle Abteilungen? Davon hängt
   ab, wer Kontakte und Notizen sehen darf (Rechte, Abschnitt 2).
3. **Standort vs. Konzern:** Wird z. B. „BASF Lampertheim“ als eigene Firma
   mit Konzern „BASF SE“ geführt (Vorschlag), oder als Adresse unter einer
   Firma?
4. **Datenschutz:** Abstimmung mit dem Datenschutzbeauftragten der
   PACO-Gruppe. Sind Löschfristen und Einwilligungsfeld so ausreichend?
5. **Outlook:** Reicht der einmalige/gelegentliche CSV-Import, oder sollen
   Kontakte dauerhaft mit Outlook abgeglichen werden? Das ginge nur über die
   Graph-Anbindung (bewusst nicht weiterverfolgt, siehe CLAUDE.md) und ist
   deshalb hier nicht vorgesehen.
