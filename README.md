# Auftragspipeline — Projektbesprechung (Prototyp mit Backend)

Flask-Backend (SQLite) + statisches Frontend. Läuft lokal per `python app.py`
oder produktiv über Gunicorn + nginx als Reverse-Proxy.

## Lokal testen

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python seed.py      # legt DB an und befüllt sie mit Beispieldaten
./venv/bin/python app.py       # Server läuft auf http://localhost:5000
```

## Deployment auf dem Ubuntu-Server

### 1. Projekt auf den Server bringen

```bash
sudo mkdir -p /opt/projektbesprechung
sudo chown $USER:$USER /opt/projektbesprechung
# Dateien hochladen, z.B.:
scp -r heta-tool/* user@server-ip:/opt/projektbesprechung/
```

### 2. Python-Umgebung einrichten

```bash
cd /opt/projektbesprechung
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python seed.py
```

Beim ersten Start wird `projektbesprechung.db` (SQLite-Datei) angelegt.
Für den produktiven Dauerbetrieb: Backup dieser Datei regelmäßig einplanen
(z.B. per Cronjob auf ein Netzlaufwerk kopieren), bis eine "echte"
Datenbank (Postgres) im Rahmen der nächsten Ausbaustufe angebunden wird.

### 3. Als Dienst einrichten (systemd + Gunicorn)

```bash
sudo cp deploy/projektbesprechung.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now projektbesprechung
sudo systemctl status projektbesprechung
```

Prüfen, ob `User=www-data` in der `.service`-Datei zum Server passt
(ggf. anpassen, z.B. auf einen eigenen Dienst-Nutzer).

### 4. nginx als Reverse-Proxy davorschalten

```bash
sudo apt install nginx -y
sudo cp deploy/nginx-projektbesprechung.conf /etc/nginx/sites-available/projektbesprechung
sudo ln -s /etc/nginx/sites-available/projektbesprechung /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

`server_name` in der nginx-Config auf den internen Hostnamen oder die
Server-IP anpassen.

### 5. Aufrufen

Im Browser die Server-IP oder den internen Hostnamen öffnen (Port 80).

## Nach Codeänderungen

```bash
sudo systemctl restart projektbesprechung
```

## Microsoft-To-Do-Anbindung aktivieren

Sobald ihr von IT/Heiko die drei Werte (Tenant-ID, Client-ID, Client-Secret)
aus der Azure-App-Registrierung erhalten habt:

```bash
sudo nano /etc/systemd/system/projektbesprechung.service
```

Die drei auskommentierten `Environment="GRAPH_..."`-Zeilen aktivieren
(`#` entfernen) und die Werte eintragen. Danach:

```bash
sudo systemctl daemon-reload
sudo systemctl restart projektbesprechung
```

Ab dann legt ein Klick auf "Aufgabe erstellen" die Aufgabe wirklich in der
persönlichen To-Do-/Outlook-Aufgabenliste der zuständigen Person an (in
einer eigenen Liste namens "Auftragspipeline", die beim ersten Mal pro
Person automatisch angelegt wird). Voraussetzung: Die Person hat in der
Datenbank eine hinterlegte E-Mail-Adresse (siehe `seed.py` bzw. Tabelle
`users`).

## Bekannte Grenzen dieses Stands

- Kein Login/Rechteverwaltung — jeder mit Netzwerkzugriff kann Einträge anlegen.
- Aufgaben landen immer in der **persönlichen** To-Do-Liste der zuständigen
  Person — Shared-Mailbox-Listen (z. B. projektbezogene Listen) sind eine
  spätere Ausbaustufe, aktuell nicht umgesetzt.
- Kein Excel/ERP-Import — Aufträge/Angebote müssen aktuell direkt in der
  Datenbank oder über die API angelegt werden (`POST /api/items`).
- Ordner-Link zeigt den Pfad nur als Tooltip an (kein echtes Öffnen des
  K-Laufwerks aus dem Browser heraus möglich).
