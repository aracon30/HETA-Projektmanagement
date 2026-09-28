#!/bin/bash
# Aktualisiert die Projektbesprechung auf dem Server aus GitHub.
# Aufruf (als Nutzer heta):  bash /opt/projektbesprechung/deploy/update.sh
#
# Sichert vorher die Datenbank, holt den neuesten Stand, ergänzt fehlende
# Spalten/Tabellen (ohne Daten zu löschen) und startet den Dienst neu.
set -e
cd /opt/projektbesprechung

sicherung="projektbesprechung.db.bak-$(date +%Y%m%d-%H%M%S)"
if [ -f projektbesprechung.db ]; then
    cp projektbesprechung.db "$sicherung"
    echo "Datenbank gesichert: $sicherung"
    # nur die 10 neuesten Sicherungen behalten
    ls -1t projektbesprechung.db.bak-* 2>/dev/null | tail -n +11 | xargs -r rm --
fi

git pull --ff-only
./venv/bin/pip install -q -r requirements.txt
./venv/bin/python migrate.py
./venv/bin/python seed_prozesse.py

sudo systemctl restart projektbesprechung
sleep 2
if systemctl is-active --quiet projektbesprechung; then
    echo "Fertig – Dienst läuft (Stand: $(git log -1 --format='%h %s'))."
else
    echo "FEHLER: Dienst läuft nicht. Details:"
    sudo journalctl -u projektbesprechung -n 30 --no-pager
    exit 1
fi
