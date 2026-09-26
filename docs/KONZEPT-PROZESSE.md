# Konzept: Reiter „Prozesse“ – Prozessdokumentation zur ERPNext-Einführung

**Status:** Entwurf v0.1 zur Abstimmung (noch nicht umgesetzt)
**Ziel:** Jede:r Mitarbeiter:in kann beschreiben, wie Arbeit *heute* tatsächlich
abläuft. Am Ende steht eine Übersicht **von grob bis fein**, die direkt als
Grundlage für die ERPNext-Einführung (Fit-Gap-Analyse, Customizing,
Schulung) dient.

---

## 1. Leitgedanken

1. **Ist vor Soll.** Zuerst dokumentieren, wie es wirklich läuft – inkl.
   Excel-Listen, Outlook-Ordner, Zettel, Zurufe. Erst danach entscheiden, wie
   es in ERPNext laufen soll. Wer gleich „Soll“ schreibt, beschreibt Wunschdenken.
2. **Grob → fein, top-down vorgegeben, bottom-up befüllt.** Die obersten
   Ebenen (Prozesslandkarte) legt die Geschäftsführung mit den
   Abteilungsleitungen fest. Die feinen Ebenen (Schritte) schreiben die Leute,
   die die Arbeit machen.
3. **Niedrige Hürde.** Ein Schritt muss in 2 Minuten erfassbar sein. Pflicht
   sind nur *Was* und *Wer*; alles andere darf später ergänzt werden.
4. **Ein Prozess – eine verantwortliche Person.** Jede:r darf beitragen, aber
   der/die Prozessverantwortliche gibt frei.
5. **ERPNext-Bezug von Anfang an mitdenken, aber nicht erzwingen.** Jeder
   Schritt bekommt ein (optionales) Feld „Wie in ERPNext?“.
6. **Kein Kanban** (siehe CLAUDE.md) – Darstellung als Baum, Tabelle und
   Swimlane-Ansicht.

---

## 2. Gliederung: vier Ebenen von grob bis fein

| Ebene | Name | Beispiel | Wer legt an? |
|---|---|---|---|
| **0** | Prozesslandkarte (Kategorie) | *Kernprozesse* | GF (fix, 3 Stück) |
| **1** | Hauptprozess | *1.2 Auftragsabwicklung* | GF + Abteilungsleitungen |
| **2** | Teilprozess | *1.2.3 Bestellung Zukaufteile* | Prozessverantwortliche:r |
| **3** | Prozessschritt | *Bestellanforderung aus Stückliste erzeugen* | alle Mitarbeitenden |

Optional **Ebene 4 „Arbeitsanweisung/Checkliste“** als Freitext bzw. Anhang
an einem Schritt (z.B. „So lege ich einen Lieferanten im alten System an“) –
wichtig für ERPNext-Schulungsunterlagen, aber kein eigenes Objekt.

Nummerierung wird automatisch vergeben (`1.2.3`), damit man in der
Projektbesprechung eindeutig darauf verweisen kann.

### Vorschlag Prozesslandkarte HETA (Startgerüst, zum Diskutieren)

**Führungsprozesse**
- F1 Unternehmenssteuerung & Controlling
- F2 Qualitätsmanagement (Audits, Reklamationen, KVP)

**Kernprozesse** (Wertschöpfungskette – entspricht grob Anfrage → Angebot → Auftrag im Tool)
- K1 Vertrieb: Anfrage bis Angebot
- K2 Auftragsklärung & Auftragsbestätigung
- K3 Konstruktion / Engineering (inkl. Stückliste)
- K4 Einkauf & Beschaffung
- K5 Fertigung / Montage
- K6 Prüfung, Abnahme & Dokumentation
- K7 Versand, Lieferung & Inbetriebnahme
- K8 Service, Ersatzteile & Reklamation

**Unterstützungsprozesse**
- U1 Rechnungsstellung & Buchhaltung
- U2 Lager & Materialwirtschaft
- U3 Personal & Zeiterfassung
- U4 IT & Stammdatenpflege (Kunden, Lieferanten, Artikel)

---

## 3. Was wird pro Ebene erfasst?

### Haupt-/Teilprozess (Ebene 1 + 2)

| Feld | Pflicht | Hinweis |
|---|---|---|
| Bezeichnung | ✔ | |
| Übergeordneter Prozess | ✔ | ergibt den Baum |
| Prozessverantwortliche:r | ✔ | Nutzer aus der bestehenden `users`-Tabelle |
| Beteiligte Abteilungen | | Mehrfachauswahl |
| Zweck / Ziel | | 1–2 Sätze |
| Auslöser (Start) | | „Kunde schickt Anfrage per Mail“ |
| Ergebnis (Ende) | | „Angebot ist beim Kunden“ |
| Häufigkeit | | z.B. „ca. 15× pro Woche“ |
| Status | ✔ | siehe Abschnitt 5 |
| ERPNext-Modul | | CRM, Verkauf, Einkauf, Lager, Fertigung, Projekte, Buchhaltung, Qualität … |

### Prozessschritt (Ebene 3) – das Herzstück

| Feld | Pflicht | Beispiel |
|---|---|---|
| Was passiert? | ✔ | „Preise der Zukaufteile beim Lieferanten anfragen“ |
| Wer (Rolle/Abteilung)? | ✔ | Einkauf |
| Womit? (Systeme heute) | | Excel „Preisliste.xlsx“, Outlook, K-Laufwerk |
| Input / benötigt | | Stückliste aus Konstruktion |
| Output / Ergebnis | | Preise in Angebotskalkulation |
| Übergabe an | | nächster Schritt / anderer Teilprozess |
| Dauer (ca.) | | 30 min |
| **Probleme / Ärgernisse** | | „Stückliste kommt oft unvollständig“ |
| **Verbesserungsidee** | | |
| ERPNext-Abbildung | | Doctype, z.B. *Request for Quotation* |
| ERPNext-Abdeckung | | *Standard* / *Anpassung nötig* / *Lücke* / *entfällt* / *unklar* |
| Reihenfolge | ✔ | per Hoch/Runter-Pfeil (kein Drag & Drop nötig) |

„Probleme“ und „Verbesserungsidee“ sind bewusst prominente Felder: Sie sind
für die ERPNext-Einführung das Wertvollste, was die Mitarbeitenden liefern.

---

## 4. Ansichten im Reiter „Prozesse“

1. **Landkarte (Startseite des Reiters)** – drei Spalten (Führung / Kern /
   Unterstützung), jede Hauptprozess-Kachel zeigt Verantwortliche:n,
   Fortschrittsbalken (wie viele Teilprozesse beschrieben/freigegeben) und
   Anzahl offener Fragen. *Das ist die „grobe“ Übersicht.*
2. **Baum** – links aufklappbare Gliederung 1 → 1.2 → 1.2.3, rechts das
   Detail des gewählten Knotens. Suchfeld wie in den anderen Tabs.
3. **Prozess-Detail (Teilprozess)** – Kopfdaten + Schritt-Tabelle, darunter
   eine automatisch erzeugte **Swimlane-Ansicht** (eine Zeile je Abteilung,
   Schritte als Kästchen von links nach rechts, Übergaben zwischen Bahnen
   sichtbar). Nur Anzeige, wird aus der Tabelle generiert – niemand muss
   Diagramme zeichnen.
4. **Diskussion / offene Fragen** je Prozess – funktioniert wie der
   bestehende Verlauf (`VerlaufEintrag`): Text, Verantwortliche:r,
   Fälligkeit, erledigt; „Aufgabe erstellen“ → Microsoft To Do.
5. **ERPNext-Fit-Gap-Übersicht** – Tabelle aller Schritte, filterbar nach
   Modul und Abdeckung. Beantwortet: *Wo reicht Standard, wo brauchen wir
   Anpassung, wo gibt es Lücken?* Export als CSV/Excel für den
   ERPNext-Implementierungspartner.
6. **Druck-/Exportansicht** – gesamtes Prozesshandbuch als eine lange Seite
   (Browser-Druck → PDF), gegliedert grob → fein.

---

## 5. Status & Freigabe (Workflow)

```
Leer → In Arbeit → Zur Prüfung → Freigegeben (Ist)
                                     │
                                     └─→ Soll definiert (ERPNext) → Umgesetzt
```

- **Leer**: nur Überschrift angelegt (von GF/Abteilungsleitung vorgegeben).
- **In Arbeit**: jemand beschreibt gerade.
- **Zur Prüfung**: Beschreibung fertig, Prozessverantwortliche:r prüft.
- **Freigegeben (Ist)**: gilt als korrekte Beschreibung des heutigen Ablaufs.
- **Soll definiert / Umgesetzt**: Phase 2 der ERPNext-Einführung.

Jede Änderung wird in einer **Änderungshistorie** protokolliert (wer, wann,
welches Feld) – analog zur bestehenden `LieferterminHistorie`. Da es noch kein
Login gibt, wählt man wie beim Verlauf den eigenen Namen aus.

---

## 6. Ist und Soll: wie wird der Übergang abgebildet?

Empfehlung: **Kein zweites, paralleles Prozessmodell.** Stattdessen hat jeder
Schritt zusätzlich die Felder „ERPNext-Abbildung“ und „Abdeckung“. Wenn sich
ein Ablauf durch ERPNext grundlegend ändert, wird der Schritt als *entfällt*
markiert und ein neuer Schritt mit Kennzeichen *Soll* hinzugefügt. So bleibt
der Ist-Stand nachvollziehbar und die Soll-Welt entsteht in derselben Struktur.

---

## 7. Datenmodell (Entwurf, additiv – bestehende Tabellen bleiben unverändert)

```
Prozess
  id, parent_id (→ Prozess, NULL = Ebene 0/1), kategorie (fuehrung|kern|unterstuetzung)
  nummer (z.B. "K4.2"), bezeichnung, verantwortlich (→ User.name)
  abteilungen (kommagetrennt), zweck, ausloeser, ergebnis, haeufigkeit
  erpnext_modul, status, reihenfolge, created_at, updated_at

ProzessSchritt
  id, prozess_id (→ Prozess), reihenfolge, was, wer_abteilung
  systeme_heute, input, output, uebergabe_an, dauer
  probleme, verbesserung, erpnext_doctype, erpnext_abdeckung, ist_soll
  created_at, updated_at

ProzessKommentar          (offene Fragen / Diskussion, wie VerlaufEintrag)
  id, prozess_id, schritt_id (optional), text, erstellt_von, verantwortlich,
  faelligkeit, status, aufgabe_erstellt, msgraph_list_id, msgraph_task_id

ProzessHistorie
  id, prozess_id, schritt_id (optional), feld, alt, neu, geaendert_von, created_at
```

Neue Tabellen werden per `db.create_all()` angelegt; `migrate.py` bleibt für
Spaltenergänzungen zuständig. Keine Änderung an `Item`/`VerlaufEintrag`.

**API (Skizze):** `GET/POST /api/prozesse`, `GET/PUT/DELETE /api/prozesse/<id>`,
`POST /api/prozesse/<id>/schritte`, `PUT/DELETE /api/schritte/<id>`,
`POST /api/schritte/<id>/verschieben`, `GET /api/prozesse/fitgap(.csv)`.

**Später möglich:** Verknüpfung zu Aufträgen/Angeboten („dieser Auftrag hängt
gerade in Schritt K4.2“) – bewusst *nicht* in Phase 1.

---

## 8. Vorgehen in der Firma (organisatorisch)

| Woche | Schritt | Beteiligte |
|---|---|---|
| 1 | Kick-off-Workshop (90 min): Prozesslandkarte Ebene 0–1 festlegen, Verantwortliche benennen | GF, Abteilungsleitungen |
| 1 | Ebene 2 (Teilprozesse) als leere Hüllen anlegen | Prozessverantwortliche |
| 2–4 | Ist-Beschreibung der Schritte, je Abteilung ca. 1 h/Woche reservieren | alle |
| wöchentlich | 10 min in der Projektbesprechung: Fortschritt der Landkarte, offene Fragen | alle |
| 5 | Review & Freigabe „Ist“ | Prozessverantwortliche |
| 6+ | Fit-Gap-Workshops mit ERPNext-Partner anhand der Fit-Gap-Übersicht | GF, Key-User |

Tipp: Mit **einem** durchgängigen Kernprozess starten (z.B. K1–K2 Anfrage →
Auftragsbestätigung), daran das Format testen und nachschärfen, dann ausrollen.

---

## 9. Umsetzung im Tool – Stufen

1. **MVP:** Modelle + API, Reiter „Prozesse“ mit Baum, Detail, Schritt-Tabelle,
   Status. Seed mit der Landkarte aus Abschnitt 2.
2. Landkarten-Startansicht mit Fortschritt, offene Fragen/Kommentare,
   Änderungshistorie.
3. Swimlane-Ansicht, Fit-Gap-Tabelle mit CSV-Export, Druckansicht.
4. (Später) Verknüpfung zu Aufträgen, Anhänge/Vorlagen, Login-gebundene Freigabe.

---

## 10. Offene Entscheidungen

1. Passt die Prozesslandkarte aus Abschnitt 2 grob zu HETA? Was fehlt / ist zu fein?
2. Darf jede:r direkt ändern (mit Historie), oder sollen Änderungen an
   freigegebenen Prozessen erst als Vorschlag laufen?
3. Reichen Tabelle + automatische Swimlane, oder wird ein echter
   Diagramm-Editor (BPMN) gewünscht? (Empfehlung: nein – zu hohe Hürde.)
4. Gibt es schon Prozessbeschreibungen (z.B. QM-Handbuch / ISO 9001), die als
   Startbestand übernommen werden sollen?
5. Welche ERPNext-Module sind geplant, und gibt es schon einen
   Implementierungspartner, dessen Fit-Gap-Format wir übernehmen sollten?
6. Wer sind die Prozessverantwortlichen für die Hauptprozesse?
