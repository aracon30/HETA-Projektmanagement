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
