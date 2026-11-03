# Digitales Board am Wandbildschirm (Raspberry Pi)

Das Board läuft als Seite der Projektbesprechung:

- Anzeige: `https://projektbesprechung.paco.local/board`
  (wechselt alle 20 s zwischen Aufträge → Aufgaben → Kennzahlen → Infos,
  lädt die Daten jede Minute neu)
- Feste Seite für einen zweiten Bildschirm: `/board?seite=3` (1 = Aufträge,
  2 = Aufgaben, 3 = Kennzahlen, 4 = Infos)
- Pflege von News/Besuchern/Terminen: `https://projektbesprechung.paco.local/board/pflege`

## Hardware

- TV ab ca. 50", HDMI, Querformat, Augenhöhe
- Raspberry Pi 4 (2 GB) oder Pi 5 + Netzteil, 32-GB-microSD, Micro-HDMI-Kabel
- Netzwerk: LAN-Kabel bevorzugt; **vorher mit IT (Herr Spano) klären**, dass
  der Pi ins Firmennetz darf und `projektbesprechung.paco.local` auflöst

## Einrichtung (einmalig)

1. Mit dem Raspberry Pi Imager „Raspberry Pi OS (64-bit)“ **mit Desktop**
   aufspielen. Im Imager unter „Einstellungen“: Hostname `heta-board`,
   Benutzer `board`, SSH aktivieren, Zeitzone Europe/Berlin.
2. Pi starten, per SSH anmelden (`ssh board@heta-board`) und die folgenden
   Befehle **einzeln** ausführen.

Interne PACO-CA vertrauen (sonst Zertifikatswarnung im Browser) — die
`.crt`-Datei der CA von IT besorgen und auf den Pi kopieren:

```
sudo cp paco-ca.crt /usr/local/share/ca-certificates/
```
```
sudo update-ca-certificates
```
```
sudo apt install -y libnss3-tools
```
```
mkdir -p ~/.pki/nssdb && certutil -d sql:$HOME/.pki/nssdb -A -t "C,," -n PACO-CA -i /usr/local/share/ca-certificates/paco-ca.crt
```

Bildschirmschoner/Abschalten verhindern:

```
sudo raspi-config nonint do_blanking 1
```

Autostart des Boards im Kiosk-Modus (Pi OS mit Wayland/labwc):

```
mkdir -p ~/.config/labwc && echo 'chromium --kiosk --noerrdialogs --disable-infobars --incognito --check-for-update-interval=31536000 https://projektbesprechung.paco.local/board &' >> ~/.config/labwc/autostart
```

```
sudo reboot
```

Danach startet der Pi direkt ins Board. Das Board lädt sich jede Nacht um
03:00 selbst neu, Änderungen am Board kommen also ohne Eingriff am Pi an.

## TV ein/aus zu Arbeitszeiten (optional, per HDMI-CEC)

```
sudo apt install -y cec-utils
```
```
(crontab -l 2>/dev/null; echo "0 7 * * 1-5 echo 'on 0' | cec-client -s -d 1"; echo "0 18 * * 1-5 echo 'standby 0' | cec-client -s -d 1") | crontab -
```

Falls der TV kein CEC kann: einfache Zeitschaltuhr an der Steckdose des TV
(der Pi bleibt dauerhaft an).
