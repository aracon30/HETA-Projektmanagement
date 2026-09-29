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
- **Server:** Ubuntu-Testserver, erreichbar unter `192.168.80.65` (bis 09/2026: .69 — Adresse hat sich geändert, SSH-Host-Key ebenfalls; interner
  Testserver, Nutzer `heta`, Projektpfad `/opt/projektbesprechung`)

## Dateien im Repo

| Datei | Zweck |
|---|---|
| `app.py` | Flask-Routen (REST-API für Items/Verlauf/Users) |
| `models.py` | SQLAlchemy-Modelle: `User`, `Item` (Auftrag/Angebot), `VerlaufEintrag` |
| `seed.py` | Beispieldaten zum Neuaufsetzen der DB |
| `migrate.py` | Additive Migration (neue Spalten ergänzen, ohne Daten zu löschen) |
| `graph_client.py` | Microsoft-Graph-Anbindung (To Do), no-op ohne Env-Vars |
| `static/index.html` | Komplettes Frontend (Aufträge/Angebote/Gantt-Tabs) |
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

1. **Microsoft-To-Do-Anbindung aktivieren**: Code ist fertig
   (`graph_client.py`), wartet auf drei Werte von IT/Heiko
   (`GRAPH_TENANT_ID`, `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`) aus einer
   Azure-AD-App-Registrierung mit Anwendungsberechtigung `Tasks.ReadWrite`.
   Werte werden als `Environment=` in der systemd-Unit gesetzt (siehe
   auskommentierte Platzhalter in `deploy/projektbesprechung.service`).
2. **Login/Rechteverwaltung** — aktuell offen für jeden mit Netzwerkzugriff.
3. **Echter Excel/ERP-Import** statt manuellem Anlegen (`POST /api/items`).
4. **Verknüpfung Angebot→Auftrag** beim Gewinnen eines Angebots (aktuell
   zwei unabhängige Listen).
5. Optional später: Shared-Mailbox-Aufgabenlisten statt nur persönlicher
   Liste (aktuell bewusst nicht umgesetzt, siehe `graph_client.py`
   Docstring).

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
überschreiben. Ausgewertet: K1_05, K3.1_01, K2_01. Noch offen: Änderungshistorie,
Probleme/Anforderungen, Systeme & Daten, Swimlane, Excel-Import. **Sprachregelung:** intern und in der
Oberfläche immer „mögliche Einführung eines ERP-Systems“ — keinen
Produktnamen (ERPNext) verwenden, keine Entscheidung vorwegnehmen.
Struktur spiegelt die Excel-Vorlage `HETA_Prozessaufnahme.xlsx`.
Es heißt **Frau Häfer**.

## Wichtige Betriebs-Hinweise / Stolperfallen

- **Deployment per Git (seit 28.09.2026):** `/opt/projektbesprechung` ist ein
  Git-Checkout (Deploy-Key `~/.ssh/github_deploy`, read-only). Update:
  `bash /opt/projektbesprechung/deploy/update.sh` (sichert DB, `git pull`,
  `migrate.py`, `seed_prozesse.py`, Neustart). Der Server folgt aktuell dem
  Branch `claude/erpnext-prozess-dokumentation-ino6q8`; nach Merge auf `main`
  umstellen (`git checkout main && bash deploy/update.sh`). Nur auf dem Server
  vorhanden (nicht im Repo): `import_orders.py`.
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

## Kontaktperson für Azure/IT-Themen

Heiko Hensel (Geschäftsführer). E-Mail-Entwurf für die App-Registrierungs-
Anfrage wurde bereits einmal erstellt und (vermutlich) verschickt — Status
beim Fortsetzen erfragen.
