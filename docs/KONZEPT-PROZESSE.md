# Konzept: Reiter „Prozesse“ – Prozessaufnahme zur Vorbereitung einer möglichen ERP-Einführung

**Status:** Entwurf v0.3 zur Abstimmung (noch nicht umgesetzt)
**Änderung zu v0.1:** Stand der parallel laufenden Prozessaufnahme eingearbeitet
(Organigramm 08/2026, Excel-Vorlage `HETA_Prozessaufnahme.xlsx`, vorhandene
Arbeitsanweisungen, Angebotsprozess). Sprachregelung angepasst.

> **Sprachregelung:** Intern – also auch überall in der Oberfläche des Tools –
> heißt es **„mögliche Einführung eines ERP-Systems“**. Kein Produktname
> (ERPNext o.ä.), keine vorweggenommene Entscheidung. Ein konkretes System
> taucht höchstens als optionales, später befüllbares Feld auf.

---

## 1. Ziel

Schnell einen strukturierten, **von den Beteiligten bestätigten** Überblick
über die tatsächlichen Abläufe bei HETA bekommen – von grob (Prozesslandkarte)
bis fein (einzelner Arbeitsschritt) – und daraus Anforderungen an ein mögliches
ERP-System ableiten.

Die Aufnahme beantwortet:

- Welche Prozesse und Arbeitsschritte gibt es?
- Wer führt aus, wer entscheidet, wer gibt frei?
- Welche Informationen und Unterlagen werden benötigt?
- Welche Programme, Excel-Listen, E-Mails, Papierunterlagen und Ablagen werden genutzt?
- Wie laufen Übergaben zwischen Personen und Bereichen?
- Wo entstehen Wartezeiten, Rückfragen, doppelte Eingaben?
- Welche Anforderungen ergeben sich für ein mögliches ERP-System?

**Grundprinzip: Ist zuerst.** Probleme, Verbesserungsideen und ERP-Anforderungen
werden **getrennt** vom Ablauf erfasst (eigene Listen), damit die
Ist-Beschreibung nicht mit Wunschdenken vermischt wird.

---

## 2. Rolle des Tools neben der Excel-Vorlage

Die Excel-Vorlage `HETA_Prozessaufnahme.xlsx` ist das Arbeitsmittel für die
schnelle Erstaufnahme (3-Tage-Plan, Interviews). Das Tool übernimmt **dieselbe
Struktur**, damit nichts doppelt gedacht werden muss:

| Excel-Arbeitsblatt | Im Tool |
|---|---|
| Prozessübersicht | Prozess (Baum, Ebenen 1–2) |
| Ablaufschritte | Prozessschritte (Ebene 3) |
| Probleme | Liste „Probleme & Anforderungen“ |
| Offene Fragen | Liste „Offene Fragen“ (mit To-Do-Aufgabe wie beim Verlauf) |
| Systeme und Daten | Liste „Systeme & Daten“ |
| Ausfüllhilfe | Hilfetext/Gesprächsleitfaden direkt im Reiter |

Mehrwert des Tools gegenüber Excel: gemeinsames, gleichzeitiges Arbeiten,
Änderungshistorie, Landkarte mit Fortschritt, Verknüpfung mit den
Arbeitsanweisungen und mit realen Aufträgen/Angeboten als Beispielvorgänge.

**Übergang:** Excel-Import (einmalig, pro Arbeitsblatt) und Excel/CSV-Export
in genau diesem Format, damit beide Wege parallel funktionieren, solange das
Tool noch nicht von allen genutzt wird.

---

## 3. Gliederung von grob bis fein

| Ebene | Name | Beispiel |
|---|---|---|
| **0** | Kategorie | Kernprozesse |
| **1** | Hauptprozess | K1 Vertrieb |
| **2** | Teilprozess / Variante | K1.1 Angebotserstellung (Variante: Ersatzteil / Fertigung) |
| **3** | Arbeitsschritt | „Kundenstatus prüfen (Neu-/Bestandskunde)“ |
| (4) | Arbeitsanweisung | verknüpftes Dokument, z.B. AA K1_01 Werk4 |

### Prozesslandkarte: aus der vorhandenen QM-Nummerierung abgeleitet

Die Dateinamen der Arbeitsanweisungen (vollständige Liste:
`docs/arbeitsanweisungen.csv`) bestätigen eine bestehende Landkarte mit
**F = Führungs-, K = Kern-, U = Unterstützungsprozessen**. Wir übernehmen
diese Nummerierung. Die **Namen der Hauptprozesse sind aus den Titeln der
Anweisungen erschlossen** und müssen mit dem QM-Handbuch (Frau Häfer)
abgeglichen werden:

| Nr. | Vermuteter Prozess | Vorhandene AA |
|---|---|---|
| F1–F3 | ? (keine AA – vermutlich nur im QM-Handbuch) | – |
| F4.2 | Prüfmittelüberwachung | Prüfmittelüberwachung, Kalibrierung Schweißgeräte |
| F4.5 | Kennzeichnung & Rückverfolgbarkeit | Werkstoffprüfzeugnis, Kennzeichnungen in der Fertigung |
| F4.6 | Dokumentenlenkung / Ablage | Projektordnerstruktur, Nummernschlüssel |
| **K1** | **Vertrieb / Angebot** | Dashboard, Namenskürzel, E-Mail-Ablage, Projektdokumentation, **Erstellen von Angeboten** |
| **K2** | **Konstruktion / Entwicklung** | Anweisung Konstruktion, Zeichnungsänderung, Prüfung Konstruktionsunterlagen, Zeichnungen als PDF, Konstruktionsrichtlinien |
| **K3.1** | **Auftragsbearbeitung** | Auftragsbearbeitung |
| **K3.2** | **Versand & Rechnung** | Versand, Rechnungserstellung (R0!) |
| **K3.3** | **Fertigung** (K3.3.1–.10 ohne AA; .11 = Fertigungshilfsprozesse?) | Druckproben, Schweißzusätze, Rücktrocknung Elektroden, Umstempelung, Lagerwesen, Maschinenwartung |
| K4 | Kundenzufriedenheit | Kundenzufriedenheit |
| **U1** | **Beschaffung** | U1.1 Bestellung, U1.2 Lieferantenauswahl/-freigabe, U1.3 Lieferantenbewertung, U1.4 Wareneingang & Materialeingangsprüfung |
| U2 | Arbeitssicherheit / Umwelt | Anschlagmittel, Erstunterweisung, Abfallentsorgung |
| U3 | ? (keine AA) | – |
| U4 | Verwaltung / Personal | Sanktionslistenprüfung, U4.3 Arbeitszeiterfassung/-nachweis |

Fett = Kette „Anfrage bis Rechnung“, die für ein mögliches ERP-System
zuerst relevant ist: **K1 → K3.1 → K2 → U1 → K3.3 → K3.2**.

**Auffälligkeiten (als offene Fragen erfassen, keine Bewertung):**
- Rechnungserstellung steht auf **Revision 0** – Entwurf, nie freigegeben?
- Die K3.3.11-AA und AA U2_01 tragen **keinen Zusatz „Werk4“** – anderer
  Geltungsbereich oder nur uneinheitliche Benennung?
- **Lagerwesen** ist unter Fertigung (K3.3.11) einsortiert, Wareneingang unter
  Beschaffung (U1.4) – wer ist tatsächlich für Lager zuständig?
- Kein eigener Prozess für **Service / Ersatzteilgeschäft**, obwohl es laut
  Organigramm eine Funktion „Standard- und Ersatzteile“ gibt – steckt das
  in K1/K3.1?
- Keine AA für **Auslegung/Kalkulation, Projektmanagement,
  Fertigungsplanung, Inbetriebnahme** – Lücke oder anderswo geregelt?
- Hohe Revisionsstände (Wareneingang R4, Namenskürzel R3,
  Lieferantenauswahl R3) zeigen, wo sich Abläufe schon öfter geändert haben.
- `AA_VORLAGE.docx` liefert das Gliederungsschema der Anweisungen – ideal,
  um das Tool-Format für Arbeitsschritte daran anzulehnen.

---

## 4. Personen und Rollen

Grundlage ist das **Organigramm Stand 08/2026**. Da viele Personen mehrere
Funktionen haben, wird an jedem Arbeitsschritt **Person *und* Rolle**
erfasst („Linker als Vertriebsadministration“, nicht nur „Linker“).

- Neue Tabelle **Rolle/Funktion** (aus dem Organigramm: Geschäftsleitung,
  Vertrieb, Projekte, Standard- und Ersatzteile, Vertriebsadministration,
  Projektmanagement, Auslegung und Kalkulation, Entwicklung/Konstruktion,
  Fertigung, Schweißaufsicht, Dokumentation, Einkauf, Buchhaltung,
  Auftragsabwicklung, IT, QMB/QM).
- Zuordnung Person ↔ Rolle (n:m) in der Nutzerverwaltung.
- **Wareneingang, Lager, Versand, Service** stehen nicht im Organigramm →
  zunächst als Rolle „ungeklärt“ anlegen; wird bei der Aufnahme geklärt und
  landet automatisch in „Offene Fragen“.

Je Arbeitsschritt drei Rollenfelder (einfaches RACI):
**führt aus** · **entscheidet/gibt frei** · **wird informiert/übernimmt danach**.

---

## 5. Was wird erfasst?

### Prozess (Ebene 1–2) – entspricht Excel „Prozessübersicht“

Prozess-ID · Name · Bereich/Variante · Prozessverantwortliche:r · Auslöser ·
Ergebnis · Beteiligte · Systeme · Beispielvorgang · **Aufnahmestatus** ·
Prüfung (wer/wann bestätigt) · Vorgänge pro Monat · verknüpfte
Arbeitsanweisungen.

### Arbeitsschritt (Ebene 3) – entspricht Excel „Ablaufschritte“

| Feld | Pflicht |
|---|---|
| Schritt-Nr. (automatisch, verschiebbar per Pfeil) | ✔ |
| Tätigkeit | ✔ |
| führt aus (Person + Rolle) | ✔ |
| Eingaben / benötigte Informationen | |
| System / Liste / Ablage | |
| Ergebnis | |
| Übergabe an wen, auf welchem Weg (Mail, Dashboard, Zuruf, Papier) | |
| Freigabe durch | |
| Ausnahme / was passiert bei fehlenden Angaben | |
| Bearbeitungszeit · Wartezeit | |
| **Quelle / Nachweis** | ✔ |

**Quelle / Nachweis** ist neu und zentral: *laut Arbeitsanweisung* /
*im Gespräch mit X am …* / *an Beispielvorgang nachvollzogen* /
*von Beteiligten bestätigt*. So bleibt jederzeit sichtbar, wie belastbar
eine Beschreibung ist.

### Probleme & Anforderungen (getrennte Liste) – Excel „Probleme“

Problem-ID · Prozess-/Schrittbezug · Ist-Problem · Beispiel · Auswirkung ·
Häufigkeit · Verbesserung / **Anforderung an mögliches ERP-System** ·
Priorität · zuständig · Status.

Hinweis im Formular: *„Klärungsbedarf ist kein Problem – dafür gibt es
‚Offene Fragen‘.“*

### Offene Fragen – Excel „Offene Fragen“

Frage-ID · Bezug · Frage · Klärung durch · nächster Schritt · Fälligkeit ·
Status · Antwort/Entscheidung · Nachweis. Technisch wie der bestehende
Verlauf, inkl. „Aufgabe erstellen“ → Microsoft To Do.

### Systeme & Daten – Excel „Systeme und Daten“

System/Datei/Ablage · Inhalt · Prozessbezug · Pflegeverantwortliche:r ·
führende Datenquelle · Speicherort · Übertragungswege · Datenqualität ·
Migrationsbedarf. Beispiele: Dashboard, Kalkulationsvorlage,
Angebotsvorlagen DE/EN, Projektordner K-Laufwerk, E-Mail-Ablage.

### Dokumente (Arbeitsanweisungen)

Dokumentnummer · Titel · Revision · letzte Änderung · Ersteller:in ·
Prüfer:in · Ablageort · Geltungsbereich (z.B. „Werk4“ – Aktualität offen) ·
**Auswertungsstatus** (nicht gesichtet / gesichtet / in Schritte übernommen).
n:m mit Prozessen, inkl. „mitgeltende Dokumente“.

---

## 6. Aufnahmestatus (Workflow)

```
Vorgeschlagen
  → Laut Arbeitsanweisung – Praxisabgleich offen
  → Im Gespräch aufgenommen
  → Von Beteiligten bestätigt (Ist)
  → Anforderungen abgeleitet
```

- *Vorgeschlagen*: nur Überschrift / Arbeitshypothese.
- *Laut Arbeitsanweisung – Praxisabgleich offen*: aus AA übernommen, aber
  nicht geprüft, ob es heute so gemacht wird.
- *Im Gespräch aufgenommen*: mit den tatsächlich Bearbeitenden durchgegangen.
- *Von Beteiligten bestätigt*: Beteiligte haben die Beschreibung geprüft.
- *Anforderungen abgeleitet*: Probleme/Anforderungen sind vollständig erfasst.

Alle Änderungen landen in einer Änderungshistorie (wer, wann, welches Feld) –
wie `LieferterminHistorie`. Ohne Login wählt man den eigenen Namen aus.

---

## 7. Ansichten im Reiter „Prozesse“

1. **Landkarte** (grob): Kacheln je Hauptprozess, farbig nach Aufnahmestatus,
   Zähler für Schritte, offene Fragen, Probleme.
2. **Baum + Detail**: aufklappbare Gliederung, rechts Steckbrief und
   Schritt-Tabelle.
3. **Swimlane-Ansicht** (fein): automatisch aus den Schritten erzeugt, eine
   Bahn je Rolle – zeigt Übergaben und Medienbrüche. Nur Anzeige.
4. **Durchgängiger Ablauf „Anfrage bis Rechnung“**: Teilprozesse
   hintereinander mit ihren Übergaben (Ergebnis des einen = Auslöser des
   nächsten). Lücken fallen hier auf.
5. **Listen** Probleme & Anforderungen / Offene Fragen / Systeme & Daten /
   Dokumente – filterbar, exportierbar.
6. **Beispielvorgänge**: ein Prozess kann mit einem echten Auftrag/Angebot
   aus dem Tool verknüpft werden (Projektauftrag, Ersatzteilauftrag).
7. **Druck-/Export**: Prozesshandbuch grob → fein; Excel-Export im
   Vorlagenformat.

Kein Kanban.

---

## 8. Datenmodell (Entwurf, additiv)

```
Rolle            id, bezeichnung, quelle ('organigramm'|'ungeklaert')
UserRolle        user_id, rolle_id
Prozess          id, parent_id, nummer, bezeichnung, variante, verantwortlich,
                 ausloeser, ergebnis, beteiligte, systeme, vorgaenge_monat,
                 aufnahmestatus, geprueft_von, geprueft_am, beispiel_item_id,
                 reihenfolge, created_at, updated_at
ProzessSchritt   id, prozess_id, reihenfolge, taetigkeit,
                 ausfuehrend_user, ausfuehrend_rolle_id, freigabe_rolle_id,
                 eingaben, system, ergebnis, uebergabe, ausnahme,
                 bearbeitungszeit, wartezeit, quelle, nachweis
Problem          id, prozess_id, schritt_id, problem, beispiel, auswirkung,
                 haeufigkeit, anforderung, prioritaet, zustaendig, status
OffeneFrage      id, prozess_id, schritt_id, frage, klaerung_durch,
                 naechster_schritt, faelligkeit, status, antwort, nachweis,
                 aufgabe_erstellt, msgraph_list_id, msgraph_task_id
SystemDaten      id, bezeichnung, inhalt, pflegeverantwortlich, fuehrend,
                 speicherort, uebertragung, datenqualitaet, migrationsbedarf
                 (+ n:m zu Prozess)
Dokument         id, nummer, titel, revision, geaendert_am, ersteller, pruefer,
                 ablageort, geltungsbereich, auswertungsstatus
                 (+ n:m zu Prozess, + mitgeltend n:m zu Dokument)
ProzessHistorie  id, objekt_typ, objekt_id, feld, alt, neu, geaendert_von, created_at
```

Neue Tabellen via `db.create_all()`; bestehende Tabellen und Daten bleiben
unberührt.

---

## 9. Startbestand (Seed) – aus dem bisherigen Stand

- **Rollen** und Personen-Zuordnung laut Organigramm 08/2026.
- **Dokumente**: alle 38 Dateien aus `docs/arbeitsanweisungen.csv`
  (Nummer, Revision, Titel, Status „nicht gesichtet“); AA K1_05 Angebotserstellung vollständig (Rev. 1,
  09.09.2025, Ersteller: Carina Linker, Prüfer: Heiko Hensel, Bereich
  Vertrieb Werk 4) mit mitgeltenden Dokumenten AA F4.6_02, F4.6_01, K1_01,
  U4_01.
- **Prozess „Angebotserstellung“** mit den elf Schritten aus der
  Arbeitsanweisung, Aufnahmestatus *Laut Arbeitsanweisung – Praxisabgleich
  offen*, Quelle je Schritt „AA Erstellen von Angeboten, Rev. 1“.
- **Offene Fragen** zum Angebotsprozess (Zuständigkeiten, Dashboard,
  Kalkulation, Sanktions-/Bonitätsprüfung, Unterschriftenregelung, fehlende
  Angaben, negative Prüfung, Angebotsrevisionen, Nachverfolgung, Übergang
  zum Auftrag).
- **Systeme & Daten**: Dashboard, Kalkulationsvorlage, Angebotsvorlagen
  DE/EN, Projektordner, Hard-/Softcopy-Ablage.
- Weitere Hauptprozesse als leere Hüllen mit Status *Vorgeschlagen*.

Diese Einträge sind **Arbeitsvorschläge**, keine bestätigte Beschreibung.

---

## 10. Umsetzungsstufen im Tool

1. **MVP**: Modelle, API, Reiter mit Baum/Detail/Schritt-Tabelle,
   Aufnahmestatus, Offene Fragen, Seed (Abschnitt 9).
2. Probleme & Anforderungen, Systeme & Daten, Dokumente, Änderungshistorie,
   Landkarte.
3. Swimlane, durchgängiger Ablauf, Excel-Import/-Export im Vorlagenformat,
   Druckansicht.
4. Später: Verknüpfung zu echten Aufträgen/Angeboten, Login-gebundene Bestätigung.

---

## 11. Offene Entscheidungen

1. Offizielle Namen der Hauptprozesse F1–F4, K1–K4, U1–U4 (QM-Handbuch) – stimmt die Tabelle in Abschnitt 3?
2. Soll das Tool die Excel-Vorlage ablösen oder parallel laufen
   (dann Import/Export in Stufe 1 vorziehen)?
3. Dürfen Mitarbeitende selbst Schritte anlegen, oder erfasst zunächst nur
   die aufnehmende Person (Philipp) und die Beteiligten bestätigen?
4. Geltungsbereich „Werk4“ – gilt das für alle Bereiche/Standorte?
