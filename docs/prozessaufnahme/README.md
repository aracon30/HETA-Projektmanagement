# Prozessaufnahme – Arbeitsstand

Dateien in diesem Ordner folgen den Arbeitsblättern der Excel-Vorlage
`HETA_Prozessaufnahme.xlsx` (Trennzeichen `;`, UTF-8 – öffnen direkt in Excel,
Inhalte lassen sich in die Vorlage kopieren) und dienen später als
Startbestand für den Reiter „Prozesse“ im Tool.

| Datei | Excel-Arbeitsblatt |
|---|---|
| `ablaufschritte.csv` | Ablaufschritte |
| `offene_fragen.csv` | Offene Fragen |
| `systeme_daten.csv` | Systeme und Daten |
| `../arbeitsanweisungen.csv` | (Dokumentenliste) |

Erzeugt aus `_erzeuge_csv.py` – Änderungen dort vornehmen und neu erzeugen.

**Alle Inhalte sind aus den Arbeitsanweisungen abgeleitet
(Status „Laut Arbeitsanweisung – Praxisabgleich offen“) und keine bestätigte
Beschreibung der tatsächlichen Abläufe.**

---

## Prozesssteckbriefe

### K1.05 Angebotserstellung

| | |
|---|---|
| Quelle | AA K1_05 Werk4 „Erstellen von Angeboten“, Rev. 1, 09.09.2025, Ersteller: Carina Linker, Prüfer: Heiko Hensel |
| Verantwortlich / mitwirkend | Vertrieb Werk 4 / Mitarbeitende Vertrieb |
| Auslöser | Kundenanfrage |
| Ergebnis | Versendetes, abgelegtes Angebot mit Nachverfolgung |
| Varianten | Handelsware · Fertigung · HETA-Ersatzteil · Fremdfabrikat-Ersatzteil |
| Mitgeltend | AA F4.6_02 Nummernschlüssel, AA F4.6_01 Projektordnerstruktur, AA K1_01 Dashboard, AA U4_01 Sanktionslistenprüfung |
| Schritte | 11 (siehe `ablaufschritte.csv`) |

### K3.1 Auftragsbearbeitung

| | |
|---|---|
| Quelle | AA K3.1_01 Werk4 „Auftragsbearbeitung“, Rev. 1, 08.09.2025, Ersteller: Carina Linker, Freigabe: Heiko Hensel |
| Verantwortlich / mitwirkend | Vertrieb/Administration Werk 4 / alle Mitarbeitenden |
| Ziel laut AA | Alle Informationen zu neuen Aufträgen bereitstellen, damit alle MA entsprechend ihrer Funktion handeln können |
| Auslöser | Kundenbestellung (auf gültiges oder abgelaufenes Angebot oder ohne Angebot) |
| Ergebnis | Auftrag im Dashboard erfasst, Kommissionsordner angelegt, alle MA informiert, AB beim Kunden (Ziel ≤ 3 Tage) |
| Auftragsarten | Behälterbau (Fertigung) · Ersatzteil HETA-Filter (Fertigung/Handelsware) · Ersatzteil Fremd-Filter (Fertigung/Handelsware) · Service (Wartung, Reparatur) |
| Mitgeltend | AA K1_02 Namenskürzel, AA F4.6_02 Nummernschlüssel, AA K1_01 Dashboard |
| Schritte | 9 (siehe `ablaufschritte.csv`) |

---

### K2 Konstruktion / Entwicklung

| | |
|---|---|
| Quelle | AA K2_01 Werk4 „Anweisung Konstruktion“, Rev. 2, 04.08.2026 (Rev. 1: 13.08.2025), Ersteller: Gabriele Häfer, Freigabe: Erik Scharmann |
| Verantwortlich / mitwirkend | Leiter Konstruktion, PM / Konstruktion Werk 4, Einkauf, Schweißaufsicht |
| Ziel laut AA | Qualitätsaspekte (Sicherheit, Leistung, Zuverlässigkeit) schon in der Konstruktion festlegen – fehlerhaftes Design ist Hauptursache für Qualitätsprobleme |
| Auslöser | Neuer Auftrag (wie die Konstruktion davon erfährt, steht nicht in der AA) |
| Ergebnis | Vollständige, kundenspezifische Konstruktionsunterlagen, an alle Abteilungen verteilt; Werkstoffe und Bestelltexte mit Einkauf abgestimmt |
| Varianten | AD 2000/DGRL (Kategorie/Modul) oder ASME (MAWP, MDMT, Einheiten nach ASME) · Kundenspezifikationen z.B. BASF-Werksnorm, Thyssen Krupp/UHDE |
| Mitgeltend | AA K2_02 Zeichnungsänderung |
| Schritte | 8 (siehe `ablaufschritte.csv`) |

Ein großer Teil der AA (Abschnitte 4.1–4.4) sind **Gestaltungsregeln für
Zeichnungen** (Schriftfeld, Stutzentabelle, Tabelle Technische Daten,
kundenspezifische Angaben). Sie sind in den Schritten 5 und 6
zusammengefasst; für ein mögliches ERP-System sind sie vor allem als
**Stammdaten/Merkmale** interessant (Typennummer, technische Daten,
Stutzenliste).

### U1.1 Bestellung · U1.4 Wareneingang · Lager

| | U1.1 Bestellung | U1.4 Wareneingang | Lager, Bestandsführung |
|---|---|---|---|
| Quelle | AA U1.1_01, Rev. 2, 25.09.2025 (Häfer / Köhler) | AA U1.4_02, Rev. 4, 24.09.2026 (Häfer / Scharmann) | AA K3.3.11-05, Rev. 1, 23.06.2026 (Häfer / Justus) |
| Verantwortlich | Einkauf Werk 4 | Fertigungsleiter Werk 4 | Justus, Köhler, Häfer |
| Kernaussage | Bestellung erst mit AB + freigegebener Stückliste; MDL (Excel) aus Stückliste; ≥1 schriftliches Angebot; technische Prüfung durch Konstruktion; Unterschriftenregelung; Nr. aus Dashboard; nach Lieferung LS und Rechnungswert (aus DATEV) ins Dashboard | Annahme, Sichtkontrolle, LS stempeln/scannen (roter Kasten), Prüfung ≤ 1 Arbeitstag (Vollständigkeit, Maße, Schmelze, Zeugnis, ggf. PMI), sperren oder freigeben, Kommission zuordnen, Lagermaterial erfassen, LS in blauen Kasten | Excel-Liste nur für Rohre, Flansche, Stangenmaterial; Zugang beim WE, Entnahme mit Datum austragen; bei akutem Bedarf Zettel |
| Schritte | 10 | 8 | 4 |

### Dashboard, Nummernschlüssel, Projektordner, Versand, Rechnung

| AA | Kernaussage |
|---|---|
| K1_01 Dashboard (Rev. 1, 31.10.2023) | HETA arbeitet **abweichend vom PPS-System der PACO Gruppe** mit Excel-Listen; das Dashboard ist die zentrale Oberfläche darüber (Passwörter/Berechtigungen je Bereich). Die eigentliche Beschreibung steht in der Anleitung „Arbeit mit den neuen Excellisten HETA“ (Stand 12.04.2022). Verantwortlich: Julia Greb (nicht im Organigramm). |
| F4.6_02 Nummernschlüssel (Rev. 1, 29.04.2022) | „da hier kein PPS-System zum Einsatz kommt“: Angebot `L-XXXXX/JJ-Kunde` (Länderkürzel), Kommission `K-XXXXX/JJ-Kunde`, AB `AB-XXXX/JJ`, Bestellung `V-XXXXX/Komm/JJ`, Rechnung und Lieferschein `JJ/XXXX`, Revisionen `-R1…`. QM-Dokumente: AA, FB, PA und **PB = Prozesssteckbrief**. |
| F4.6_01 Projektordnerstruktur (Rev. 1, 20.10.2022) | Anfrage → Angebotsnummer → Dashboard legt Musterordner auf K: an → bei Bestellung Umwandlung in Auftragsordner. |
| K3.2_01 Versand (Rev. 1, ohne Datum) | Wöchentliche Versandliste der Vertriebsadministration, Reinigen, Verpacken je Warenart, Fotos in den Auftragsordner, Packliste (Grundlage Spedition), ggf. Versandbereitschaftsmeldung, Lieferschein in roter Tasche, danach Rechnung. → 11 Schritte |
| K3.2_02 Rechnungserstellung (**R0**) | Nur Vorbereitung (Packzettel + Versandbelege an Buchhaltung) und Prüfung gegen Lieferschein und Auftrag; die Abläufe für Deutschland, EU und Drittländer sind **leere Platzhalter** („? DATEV“). → 5 Schritte, Rest im Gespräch |

**Wichtigste Erkenntnisse:**
1. Es gibt ein **PPS-System der PACO Gruppe**, das HETA bewusst nicht nutzt. Warum und ob es eine Option ist, muss vor jeder weiteren Systemüberlegung mit der Geschäftsleitung geklärt werden.
2. Es gibt **Prozesssteckbriefe (PB)** im QM – vermutlich die offizielle Prozessbeschreibung zur Landkarte. Unbedingt anfordern.
3. Die **Rechnungsstellung** ist nicht dokumentiert – Gespräch mit der Buchhaltung nötig.
4. Nummernkreise haben Doppelbelegungen (`V-` für Versuchsauftrag und Bestellung, `JJ/XXXX` für Rechnung und Lieferschein).

## Wird geprüft, ob Material am Lager ist?

**Nein – nicht als fester Schritt.** Die AA Bestellung beginnt mit Stückliste →
MDL → Lieferantenangebot; ein Abgleich mit dem Lagerbestand ist nicht
vorgesehen. Die Lagerliste dient laut AA Lagerwesen nur dazu, dass der Einkauf
**Nachbestellbedarf** erkennt. Einziger Bezug im Konstruktionsprozess: das
Abstimmen von „Alternativmaterial aus dem Lager“ (AA K2_01). Bestand wird
zudem nur für Rohre, Flansche und Stangenmaterial geführt, Entnahmen bei
akutem Bedarf per Zettel.

Für ein mögliches ERP-System ist das eine zentrale Anforderung
(Verfügbarkeitsprüfung, Reservierung je Kommission, Bestandsführung für alle
Lagerartikel) – im Praxisabgleich mit Köhler und Justus klären, wie es heute
tatsächlich läuft (Fragen im Tool bei U1.1 und Lager).

**Mehrfacherfassung:** Bestelldaten stehen in Dashboard **und** MDL,
Lieferscheine werden gestempelt, gescannt, kopiert und ins Dashboard
übertragen, Rechnungswerte aus DATEV von Hand ins Dashboard.

## Übergabe Konstruktion → Einkauf (Nahtstelle K2 → U1.1)

Laut AA stimmt die Konstruktion **Bestelltexte** und den Einsatz von
**Alternativmaterial aus dem Lager** mit dem Einkauf ab und informiert bei
Zeichnungsänderungen alle, „damit Bestellungen bei Lieferanten berücksichtigt
werden können“. **Nicht beschrieben** ist:

- ob und wie eine **Stückliste** entsteht und an den Einkauf geht
  (Bestellanforderung),
- in welcher Form und zu welchem Zeitpunkt die Bestelltexte übergeben werden
  (z.B. Langläufer vorab),
- woher die Konstruktion den **Lagerbestand** kennt,
- wie bei Zeichnungsänderungen **bereits bestellte Teile** erkannt werden.

Das ist die zentrale Nahtstelle für die Beschaffung und sollte im Gespräch mit
Konstruktion **und** Einkauf gemeinsam aufgenommen werden (danach AA U1.1_01
Bestellung auswerten).

## Übergabe Angebot → Auftrag (Nahtstelle K1.05 → K3.1)

```
Anfrage ──K1.05──▶ Angebot (Dashboard: Angebotsliste, Angebotsordner)
                        │  Bestellung des Kunden
                        ▼
              K3.1  Prüfung gegen Angebot ─▶ Übernahme in Auftragsliste
                        │                    Angebotsordner → Kommission
                        ▼
              Info-Mail an alle MA + AB an Kunden
                        │
                        ▼
      ??? Konstruktion (K2) · Einkauf (U1) · Fertigung (K3.3) · PM
```

Was die Anweisungen **abdecken**: Erfassung, Ordner, Verknüpfung der
Unterlagen und Kommunikation mit dem Kunden.

Was sie **offen lassen**, also die wichtigsten Punkte für den Praxisabgleich:
1. **Übergabe an die ausführenden Bereiche.** Beschrieben ist nur eine
   Info-Mail an alle. *Praxisangabe (Philipp Schreiber, 28.09.2026):* Die
   Übergabe erfolgt per **Rundmail an alle, der die Auftragsbestätigung
   beiliegt**. Die AB ist damit faktisch das Übergabedokument an Konstruktion,
   Einkauf und Fertigung. Noch offen ist, ob jemand die Bereiche ausdrücklich
   beauftragt oder ob sich jeder seine Aufgaben selbst aus der AB ableitet,
   und wer bemerkt, wenn niemand reagiert.
2. **Liefertermin.** Er wird „geprüft, ggf. revidiert“. Mit wem und auf
   welcher Grundlage (Kapazität, Materialverfügbarkeit), ist nicht
   beschrieben.
3. **Datenübernahme.** Ob und welche Angebotsdaten ins Dashboard übernommen
   oder neu eingetippt werden, zum Beispiel beim Schreiben der AB im
   Vorlageformular.
4. **Freigaben.** Wer die AB unterschreibt, fehlt.
5. **Auftragsarten.** Die AA unterscheidet vier Auftragsarten, beschreibt
   aber einen gemeinsamen Ablauf. Der Service-Auftrag hat keinen eigenen
   Prozess in der QM-Landkarte.

## Relevanz für ein mögliches ERP-System (noch keine Anforderungen)

Diese Punkte erst nach dem Praxisabgleich als Anforderungen erfassen:
- **Dashboard ist das führende System** für Anfragen, Angebote und
  Aufträge. Es besteht aus Excel-Makrodateien (siehe `systeme_daten.csv`).
  Damit ist das Dashboard der wichtigste Kandidat für Datenmigration und für
  den Funktionsvergleich.
- **Nummernlogik übernehmen.** Kommissionsnummer `K-<AB fünfstellig>/<JJ>`,
  Länderkürzel nach ISO 3166-1, Namenskürzel (AA F4.6_02, K1_02). Ein
  ERP-System müsste diese Nummernkreise abbilden können.
- **Verkettung Anfrage → Angebot → Auftrag → Ursprungs- bzw.
  Wiederholungsauftrag.** Wird heute über das Dashboard und den Ordner
  hergestellt.
- **Sanktionslisten- und Bonitätsprüfung** als Prüfschritt bei Neukunden
  bzw. neuen Debitoren.
