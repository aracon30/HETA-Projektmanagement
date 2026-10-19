# HETA Projektbesprechung / Auftragspipeline — Übergabe

Dieses Dokument fasst den Stand aus einer längeren Konzeptions- und
Umsetzungs-Session mit Claude (claude.ai) zusammen, damit hier nahtlos
weitergearbeitet werden kann.

## Ziel des Tools

Internes Web-Tool für HETA Verfahrenstechnik GmbH zur Vorbereitung/Durchführung
der Projektbesprechung: laufende Aufträge und Angebote abteilungsübergreifend
verfolgen, Verlauf dokumentieren, Aufgaben an Kolleg:innen verteilen — ersetzt
eine bisherige Excel→OneNote-Kopie-Lösung.

## Tech-Stack

- **Backend:** Python / Flask + Flask-SQLAlchemy, SQLite (`projektbesprechung.db`)
- **Frontend:** einzelne statische `static/index.html` (Vanilla JS, kein Build-Step),
  wird von Flask direkt ausgeliefert
- **Deployment:** Gunicorn als systemd-Dienst (`projektbesprechung.service`),
  nginx als Reverse-Proxy davor
- **Server (seit 19.10.2026, Produktiv-VM in der HETA/PACO-Struktur):**
  `https://projektbesprechung.paco.local/` (IP `192.168.80.35/24`, VM-Name
  "Projektbesprechung" auf ESXi-Host `192.168.80.227`, 4 vCPU/4 GB RAM/60 GB),
  eingerichtet von IT (Herr Spano). Login per SSH als `admin-heta` (sudo),
  Dienst läuft unter eigenem Nutzer `heta`, Projektpfad `/opt/projektbesprechung`.
  Echtes HTTPS-Zertifikat der internen PACO-CA (CN/SAN `projektbesprechung.paco.local`,
  gültig bis 15.10.2033), liegt als PEM-Dateien unter `/etc/nginx/ssl/` (aus der
  von IT gelieferten `.pfx` per OpenSSL umgewandelt, siehe README). Über VPN auch
  aus dem Homeoffice erreichbar (Routing + interne DNS-Auflösung getestet, beides
  funktioniert).
- **Testsystem:** `192.168.80.56` (davor `.65`/`.69` — die VM hatte wiederholt
  wechselnde DHCP-Adressen; das war der ursprüngliche Server vor dem Umzug auf
  die feste Produktiv-IP, läuft aber weiter und wird jetzt aktiv als Testsystem
  genutzt, um Änderungen vor dem Produktiv-Server auszuprobieren). Gleicher
  Aufbau wie der Produktiv-Server (Git-Checkout unter `/opt/projektbesprechung`,
  Dienst `projektbesprechung`, interner Linux-Hostname ebenfalls
  „projektbesprechung“ — nicht mit dem Produktiv-Server verwechseln, IP prüfen).
  Login per SSH direkt als `heta` mit Passwort (kein separater `admin-heta`-Account
  hier). Update genauso wie auf dem Produktiv-Server: `bash
  /opt/projektbesprechung/deploy/update.sh` — ob `heta` hier sudo-Rechte für den
  Dienst-Neustart hat, war Stand 19.10.2026 noch nicht abschließend geklärt.

## Dateien im Repo

| Datei | Zweck |
|---|---|
| `app.py` | Flask-Routen (REST-API für Items/Verlauf/Users) |
| `models.py` | SQLAlchemy-Modelle: `User`, `Item` (Auftrag/Angebot), `VerlaufEintrag` |
| `seed.py` | Beispieldaten zum Neuaufsetzen der DB |
| `migrate.py` | Additive Migration (neue Spalten ergänzen, ohne Daten zu löschen) |
| `graph_client.py` | Microsoft-Graph-Anbindung (To Do), no-op ohne Env-Vars |
| `static/index.html` | Komplettes Frontend (Aufträge/Angebote/Gantt-Tabs) |
| `asme_api.py` | ASME-Dokumente: Lieferantenbestellungen + Formularerzeugung aus Word-Vorlagen |
| `vorlagen/asme/` | Word-Vorlagen je QC-Handbuch-Revision (siehe README dort) |
| `ab_api.py` | Auftragsbestätigung: Formularerzeugung aus Word-Vorlage (docxtpl) |
| `vorlagen/auftragsbestaetigung/` | Word-Vorlage der Auftragsbestätigung (Jinja-Platzhalter) |
| `requirements.txt` | Python-Abhängigkeiten |
| `deploy/projektbesprechung.service` | systemd-Unit-Vorlage |
| `deploy/nginx-projektbesprechung.conf` | nginx-Reverse-Proxy-Vorlage |
| `README.md` | Deployment-Anleitung (ausführlicher als hier) |

## Datenmodell (Kurzfassung)

`Item` deckt sowohl Aufträge als auch Angebote ab (`type` = `auftrag`/`angebot`),
mit typ-spezifischen Feldern:
- Auftrag: `prio` (rot/gelb/gruen), `liefertermin`, `auftrag_status` (offen/erledigt)
- Angebot: `angebot_status` (in_bearbeitung/versendet/wiedervorlage/gewonnen/verloren),
  `wert`, `wiedervorlage`

`VerlaufEintrag` (n:1 zu Item): Text, `erstellt_von`, `verantwortlich` (freie
Zuweisung an jeden Nutzer, kein Abteilungs-Lock), `faelligkeit`, `status`
(offen/erledigt), `aufgabe_erstellt` (bool), `msgraph_list_id`/`msgraph_task_id`
(gefüllt sobald To-Do-Anbindung aktiv ist).

`Phase` (n:1 zu Item): `bezeichnung`, `start`, `ende` (beide Pflicht) — frei
anlegbare Zeitabschnitte innerhalb eines Auftrags (z.B. Konstruktion,
Fertigung, Prüfung) für das detaillierte Gantt je Auftrag.

`User`: `name`, `abteilung`, `email` (Muster bei HETA: `nachname@heta.de`,
Ausnahme Philipp Schreiber: `p.schreiber@heta.de`).

## Fertige Funktionen

- Aufträge/Angebote anlegen, ansehen, löschen (mit Bestätigungsdialog)
- Verlaufseinträge hinzufügen, frei Verantwortliche zuweisen
- "Aufgabe erstellen" — legt bei konfigurierter Graph-Anbindung eine echte
  Aufgabe in der **persönlichen** Microsoft-To-Do-Liste (`Auftragspipeline`)
  der zuständigen Person an; ohne Konfiguration nur lokale Markierung
- **Gantt-Tab**: alle offenen Aufträge als Balken (Start = Erstelldatum,
  Ende = Liefertermin), farbig nach Priorität, Klick auf Balken öffnet
  Dialog zum Ändern des Liefertermins (kein Drag-Resize, bewusst einfach
  gehalten für Robustheit)
- **Detailliertes Gantt je Auftrag** (im "Zeitplan"-Abschnitt der
  Auftrags-Detailansicht, nur für Aufträge, nicht für Angebote): frei
  anlegbare/bearbeitbare/löschbare `Phase`n als Balken (eigener Start/Ende),
  plus die Verlaufseinträge mit Fälligkeit als Marker (Raute, grün wenn
  erledigt) auf derselben Zeitachse. Ohne Phasen und ohne fällige
  Verlaufseinträge erscheint ein Hinweistext statt eines leeren Diagramms.
- Ordner-Pfad (K-Laufwerk) wird pro Auftrag/Angebot als Tooltip angezeigt
  (nur Anzeige, kein echtes Öffnen aus dem Browser)

## Ausdrücklich NICHT gewollt / entfernt

- **Kein Kanban mehr** — es gab zwischenzeitlich sowohl ein übergeordnetes
  Kalenderwochen-Kanban als auch ein kleines Verlaufs-Kanban
  (Offen/In Bearbeitung/Erledigt) mit Drag & Drop. Beides wurde auf
  ausdrücklichen Wunsch komplett entfernt und durch das Gantt-Tab ersetzt.
  **Bitte kein Kanban wieder einführen, ohne explizit danach zu fragen.**

## Offene Ausbaustufen (in Priorität, wie zuletzt besprochen)

1. **Login/Rechteverwaltung** — aktuell offen für jeden mit Netzwerkzugriff.
2. **Echter Excel/ERP-Import** statt manuellem Anlegen (`POST /api/items`).
3. **Verknüpfung Angebot→Auftrag** beim Gewinnen eines Angebots (aktuell
   zwei unabhängige Listen).

**Microsoft-To-Do-Anbindung — bewusst nicht weiterverfolgt (Entscheidung
21.10.2026):** Code für die echte Graph-Anbindung ist fertig und bleibt im
Repo (`graph_client.py`, `GRAPH_TENANT_ID`/`GRAPH_CLIENT_ID`/
`GRAPH_CLIENT_SECRET`, Platzhalter in `deploy/projektbesprechung.service`),
die Azure-AD-App-Registrierung bei IT (Herr Spano) wurde aber auf
ausdrücklichen Wunsch von Philipp **geschlossen** — die E-Mail-
Benachrichtigung (siehe unten) deckt den Bedarf ausreichend ab, der
Zusatzaufwand für die Graph-App lohnt sich nicht mehr. Falls doch wieder
gewünscht (z.B. für automatischen Erledigt-Abgleich oder native
To-Do-Einträge ohne manuelles Flaggen der Mail): neue Anfrage an Heiko
Hensel bzw. IT nötig, Code ist startbereit.

**Aufgaben-Benachrichtigung (dauerhaft aktiv):** "Aufgabe erstellen" nutzt
der Reihe nach Microsoft Graph (nicht konfiguriert, s.o.) → **E-Mail per
SMTP** (`mail_client.py`, `SMTP_HOST=192.168.80.30` `hetamsx01.paco.local`,
Port 25, anonymer interner Relay, kein Login nötig — das ist die aktive
Dauerlösung, kein Übergang mehr) → persönlicher Power-Automate-Webhook
(bei HETA durch eine DLP-Richtlinie der PACO-Gruppe gesperrt, Code bleibt
für andere Tenants/falls sich das ändert) → nur lokale Markierung.
`aufgabe_kanal` am `VerlaufEintrag` hält fest, welcher Kanal tatsächlich
gegriffen hat.

Optional später: Shared-Mailbox-Aufgabenlisten statt nur persönlicher
Liste (aktuell bewusst nicht umgesetzt, siehe `graph_client.py` Docstring —
nur relevant, falls die Graph-Anbindung doch nochmal aktiviert wird).

## Prozessaufnahme / Reiter „Prozesse“ (Stufe 1 umgesetzt)

Konzept: `docs/KONZEPT-PROZESSE.md`. Umgesetzt: Landkarte, Baum, Steckbrief,
Ablaufschritte (sortierbar per ↑/↓), offene Fragen, Arbeitsanweisungen mit
Auswertungsstatus, CSV-Export im Excel-Vorlagenformat. Code: `prozesse_api.py`
(Blueprint), Modelle `Prozess`/`ProzessSchritt`/`ProzessFrage`/`Dokument` in
`models.py`, Startbestand in `prozess_daten.py` (auch Quelle für
`docs/prozessaufnahme/_erzeuge_csv.py`), Einspielen per `seed_prozesse.py`
(idempotent, legt nur fehlende Tabellen an). **Neue Auswertungen (weitere
Arbeitsanweisungen) als neuen Eintrag in `ERGAENZUNGEN` (prozess_daten.py,
Version hochzählen) anlegen** – nie den Grundbestand ändern: die Server-DB
ist schon befüllt, Ergänzungen werden per `update.sh` genau einmal
eingespielt (Stand in Tabelle `startbestand_stand`), ohne Nutzeränderungen zu
überschreiben. Ergänzungen finden Prozesse per Nummer oder (bei von Hand angelegten) per Bezeichnung. Ausgewertet: K1_05, K3.1_01, K2_01, U1.1_01, U1.4_02, K3.3.11-05, K1_01, K3.2_01, K3.2_02, F4.6_01, F4.6_02 (Ergänzungen 2–5). Ergänzung 6 = Vorschläge für weiße Flecken (typische Abläufe, Nachweis „Vorschlag: typischer Ablauf – im Gespräch prüfen“, Übergaben „noch unklar“) – keine HETA-Fakten. Wichtig: HETA nutzt laut AA K1_01 bewusst nicht das PPS-System der PACO Gruppe (Frage an GL offen).
**Einstieg = Prozesskette** (Standardansicht des Reiters, `PZ_KETTE_GLIEDER`):
Glieder entlang eines Auftrags (Anfrage & Angebot … Rechnung, Service), Zuordnung
der Prozesse über den nächsten passenden Schlüssel (Nummer oder Bezeichnung),
Klick = Teilprozesse + „bekommt von/gibt weiter an“, ohne Auswahl Liste „Wo es
hakt“. Baum links zeigt nur Hauptprozesse, Teilprozesse klappen bei Auswahl auf.
**Schnittstellenkarte** (Eintrag im Prozess-Baum): Modell `ProzessVerbindung`
(von → nach, Inhalt, Weg, optional Schritt, „hakt“), API `/api/verbindungen`,
im Frontend eigenes SVG ohne Bibliothek (feste Bahnen Führung/Kern/
Unterstützung, Kernprozesse in Auftragsreihenfolge `PZ_KARTE_KERN`,
Klick = Fokus auf einen Prozess), dazu Schnittstellenmatrix und
CSV-Export „schnittstellen“. Bewusst kein frei schwebendes Kraft-Layout. Noch offen: Änderungshistorie,
Probleme/Anforderungen, Systeme & Daten, Swimlane, Excel-Import. **Sprachregelung:** intern und in der
Oberfläche immer „mögliche Einführung eines ERP-Systems“ — keinen
Produktnamen (ERPNext) verwenden, keine Entscheidung vorwegnehmen.
Struktur spiegelt die Excel-Vorlage `HETA_Prozessaufnahme.xlsx`.
Es heißt **Frau Häfer**.

## ASME-Auftragsdokumente (Stufe 1 umgesetzt, Branch `claude/asme-dokumente`)

Ziel: Daten einmal erfassen, daraus die Formulare laut QC-Handbuch erzeugen –
ohne Abtippen. Freigeschaltet nur bei Aufträgen mit Haken „ASME-Auftrag“
(Spalte `items.asme`, Feld in der zweiten Meta-Zeile); ohne Haken ist der
Abschnitt ausgeblendet, vorhandene Bestellungen bleiben erhalten, die API
lehnt neue Bestellungen/Dokumenterzeugung ab. In der Auftrags-Detailansicht Abschnitt „Lieferantenbestellungen
& ASME-Dokumente“: Bestellung (Kopf) + Positionen anlegen, „Dokumente erzeugen“
liefert ZIP mit `Bestellung_<Nr>.docx` und `WE-Kontrollscheine_<Nr>.docx`
(eine Seite je Bestellposition). Code: `asme_api.py` (Blueprint, docxtpl),
Modelle `LieferantenBestellung`/`BestellPosition` in `models.py`, Frontend-Block
„ASME-Dokumente“ in `static/index.html` (`renderAsmeBestellungen`).
Vorlagen je Handbuch-Revision in `vorlagen/asme/<Ordner>/` mit `formulare.json`,
Anleitung und Platzhalterliste in `vorlagen/asme/README.md`. Layout-Änderung =
nur Vorlage tauschen, kein Code.
Festgelegt: Werkstoff/Spezifikation hängen an der **Position** (WE-Schein ist je
Position); Prüfdaten des WE-Kontrollscheins werden **von Hand** ausgefüllt –
das Tool füllt nur den Kopf (Bestell-Nr./Kommission, Pos., Stücklisten-Pos.,
Bezeichnung, Werkstoff, Menge). Laut Philipp gehören zum ASME-Paket nur diese
zwei Formulare. Vorlagen in `vorlagen/asme/Original/` sind aus Philipps
Word-Originalen umgebaut (Dropdown-Listen in `auswahl` übernommen; Kopffeld
„Material nach Sec. II Part A“ = `material_art` am Bestellkopf, Spezifikation
und Werkstoff je Position). Offen: Handbuch-Revision und Form-Nr. der
Bestellung in `formulare.json` eintragen; englische Bestellvorlage (Titel-Dropdown
„Bestellung/Order“ deutet darauf hin) ggf. als eigenes Formular ergänzen.

## Auftragsbestätigung (Stufe 1 umgesetzt)

Ziel: aus den ohnehin im Auftrag erfassten Daten per Klick die Auftragsbestätigung
als Word-Datei erzeugen, die an den Kunden geschickt wird – ohne Abtippen. Abschnitt
„Auftragsbestätigung“ in der Auftrags-Detailansicht (nur für Aufträge, nicht
Angebote/Anfragen): AB-Nummer (read-only, wird aus der Kommission abgeleitet,
siehe unten – nicht aus `items.erp_ab_nummer`, der nur für den ERP-Import-
Abgleich gebraucht wird), Unser Zeichen,
Ihr Zeichen (Kunde), Bestell-Nr. Kunde, Zahlungsbedingungen, Kundenadresse
und Versandanschrift (eigenes Feld, s.u.) frei editierbar; Lieferbedingungen
und Liefertermin kommen aus den ohnehin vorhandenen Auftragsfeldern.
„Auftragsbestätigung erzeugen“ lädt
`Auftragsbestaetigung_<AB-Nr-oder-Kommission>.docx`. Code: `ab_api.py`
(Blueprint, docxtpl, reicht die Formatierungs-Helfer aus `asme_api.py` weiter),
Felder an `Item` (`unser_zeichen`/`kunden_zeichen`/`kunden_bestellnr`/
`kunden_adresse`/`versand_adresse`/`zahlungsbedingungen`) und `AuftragPosition`
(`menge`/`einheit`/`preis_je_einheit`, optional – nur gebraucht, wenn die
Position auch in der Auftragsbestätigung einen Preis haben soll; ohne Preis
bleiben Menge/Preis/Gesamtbetrag in der Tabelle leer). Vorlage
`vorlagen/auftragsbestaetigung/Auftragsbestaetigung.docx` ist Philipps
Original-Formular (Dropdown-Kopf „Auftragsbestätigung/Lieferschein/
Rechnung/…“ unverändert gelassen, nur für „Auftragsbestätigung“ ausgefüllt),
Platzhalter direkt in den Wert-Zeilen ergänzt, Positionstabelle auf eine
Jinja-Schleifenzeile (`{%tr for %}`/`{%tr endfor %}`, docxtpl-Syntax) reduziert.
Layout-Änderung = nur Vorlage tauschen, kein Code – Platzhalter dabei nicht
verändern. AB-Nummer bildet sich aus der Kommission: Kommission entsteht
beim ERP-Import aus der AB-Nummer (`K-{AB:05d}/{Jahr zweistellig}`, siehe
`erp_import.py`) – `ab_nummer_suffix()` in `ab_api.py` kehrt das nur wieder
um (`K-01234/26` → Rest nach „AB-“ = `1234/26`, in der Vorlage zu
„AB-1234/26“ zusammengesetzt), funktioniert dadurch für jeden Auftrag mit
Kommission, nicht nur ERP-importierte.

**Kundenadresse (korrigiert nach Vergleich mit einer echten Auftragsbestätigung
von Philipp):** Die Vorlage hat sehr wohl ein Anschriftfeld oben links –
es ist nur ein leeres, seitenfest verankertes Textfeld (floating
`wps:txbx`/`v:textbox`-Paar, kein normaler Absatz), das beim ersten
Durchgehen der Vorlage übersehen wurde. Gefüllt wird es über einen
docxtpl-Absatzschleife (`{%p for line in adresse_zeilen %}`/`{%p endfor %}`,
je Zeile ein eigener `<w:p>` innerhalb des Textfelds). `adresse_zeilen` in
`ab_api.py` = `kunde` + die freien Zeilen aus `kunden_adresse`.

**Versandanschrift ist ein eigenes Feld** (`items.versand_adresse`,
mehrzeilig frei, z.B. mit abweichendem Ansprechpartner wie im Beispiel von
Philipp „Frau Helima Nougal“) – kann bewusst von der Kundenadresse oben
abweichen (andere Lieferadresse, Ansprechpartner vor Ort). Ohne eigene
Eintragung übernimmt `ab_api.py` die Kundenadresse als Fallback. Füllt die
„Versandanschrift/Shipping Address“ (erste Zeile auf gleicher Höhe wie
„FCA Lich“, weitere Zeilen darunter über eine zweite Absatzschleife
`versand_weitere_zeilen`).

**PDF-Vorschau in diesem Dev-Setup:** `soffice`/LibreOffice ist nur mit
`libreoffice-core`/`-common` vorinstalliert, **`libreoffice-writer` fehlt**
(`Error: source file could not be loaded` bei jedem `--convert-to pdf`,
auch bei trivialen Dateien – nicht an der jeweiligen Datei liegend). Abhilfe:
`apt-get install -y libreoffice-writer poppler-utils`, danach funktioniert
`soffice --headless --convert-to pdf` und `pdftoppm` zum Rendern als Bild
normal. Vorher ließen sich Vorlagenänderungen nur strukturell/inhaltlich
prüfen (python-docx/Tabellenwerte), nicht visuell – das hat zu der oben
beschriebenen übersehenen Kundenadresse geführt. Bei künftigen
Vorlagen-Änderungen: immer als PDF rendern und mit einem echten Beispiel
vergleichen, bevor man sich auf die reine XML-Analyse verlässt.

## Wichtige Betriebs-Hinweise / Stolperfallen

- **Deployment per Git:** `/opt/projektbesprechung` ist ein Git-Checkout
  (eigener Deploy-Key `~/.ssh/github_deploy` im Home von `admin-heta`,
  read-only, neu erzeugt beim Serverumzug). Update:
  `bash /opt/projektbesprechung/deploy/update.sh` (sichert DB, `git pull`,
  `migrate.py`, `seed_prozesse.py`, Neustart). Der Server folgt dem Branch
  `main` (feature branches wie `claude/asme-dokumente` werden nach dem Merge
  auf GitHub gelöscht — falls `git pull`/`git fetch` mit "couldn't find
  remote ref" fehlschlägt, folgt die lokale Remote-Konfiguration noch einem
  gelöschten Branch: `git remote set-branches origin '*' && git fetch origin`
  behebt das dauerhaft, danach `git checkout -B main origin/main`). Nur auf
  dem Server vorhanden (nicht im Repo): `import_orders.py`.
- **Nie `seed.py` auf dem Server ausführen** — setzt die Datenbank zurück.

- **Nach jedem `sudo cp ... /opt/projektbesprechung/...` sofort**
  `sudo chown -R heta:heta /opt/projektbesprechung` **ausführen** — sonst
  crasht Gunicorn beim Neustart mit `PermissionError`, weil `sudo cp`
  Dateien als `root` anlegt, der Dienst aber als Nutzer `heta` läuft.
- Nach mehreren schnellen Fehlstarts blockiert systemd mit
  "Start request repeated too quickly" — vorher
  `sudo systemctl reset-failed projektbesprechung` ausführen.
- `app.py`/`models.py`/`graph_client.py`-Änderungen brauchen
  `sudo systemctl restart projektbesprechung`.
  `static/index.html`-Änderungen **nicht** (Flask liefert sie live aus).
- Bei Schema-Änderungen an `models.py`: **nicht** einfach `projektbesprechung.db`
  löschen, wenn schon echte Daten drin sind — stattdessen `migrate.py`
  erweitern (additive `ALTER TABLE`, siehe bestehende Struktur dort) und
  ausführen. Es gab schon einmal echte, selbst angelegte Testdaten auf dem
  Server, die erhalten bleiben sollten.
- Philipp arbeitet über SSH/PowerShell auf Windows und tendiert dazu,
  mehrzeilige Befehlsblöcke komplett auf einmal einzufügen, was die Shell
  als einen zusammenhängenden Befehl interpretiert. Im Zweifel Befehle
  einzeln und mit ausdrücklichem Hinweis "einzeln ausführen" liefern.

## Kontaktpersonen für Azure/IT-Themen

- **Heiko Hensel** (Geschäftsführer) — ursprünglich für die Azure-AD-App-
  Registrierung (Microsoft-To-Do-Anbindung) vorgesehen; das zugehörige
  IT-Ticket wurde am 21.10.2026 auf Philipps Wunsch geschlossen (siehe
  "Offene Ausbaustufen" oben), nur bei künftigem erneuten Bedarf relevant.
- **Herr Spano** (IT-Abteilungsleiter, PACO-Gruppe, Helpdesk-Tickets unter
  `svrosticket.paco.local`) — zuständig für Server-/Netzwerk-Infrastruktur
  (VM-Bereitstellung, DNS, interne Zertifizierungsstelle, SMTP-Relay,
  VPN/Routing). Hat den Serverumzug am 19.10.2026 abgewickelt.
