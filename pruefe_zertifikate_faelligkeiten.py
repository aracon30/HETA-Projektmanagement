"""
Wöchentliche Erinnerungsmail an einkauf@heta.de für Lieferanten-Zertifikate,
die bald ablaufen oder schon abgelaufen sind (siehe
docs/KONZEPT-LIEFERANTEN-ZERTIFIKATE.md Abschnitt 7).

Entscheidungen (13.11.2026):
  - Inhalt: "bald ablaufend" + "abgelaufen" — gesperrte Lieferanten bewusst
    NICHT mit drin (eine Sperre ist eine bewusste Entscheidung, kein
    übersehener Ablauf).
  - Immer der volle aktuelle Stand, kein Abgleich gegen die letzte Mail —
    ein liegen gebliebener Fall taucht dadurch bewusst jede Woche wieder auf,
    bis er erledigt ist. Kein zusätzlicher "zuletzt gemeldet"-Stand nötig.
  - Verschickt nur, wenn es mindestens einen Fall gibt (keine leeren
    "alles in Ordnung"-Mails).

Dies ist der erste wiederkehrende Hintergrund-Job im Tool (bisher lief alles
nutzergetrieben oder per Live-Polling vom Browser aus) — läuft nicht von
allein, sondern braucht einen Cron-Eintrag auf dem Server:

  crontab -e   (als Nutzer heta)
  0 7 * * 1 cd /opt/projektbesprechung && ./venv/bin/python pruefe_zertifikate_faelligkeiten.py >> /var/log/zertifikate_mail.log 2>&1

Aufruf manuell zum Testen:
  ./venv/bin/python pruefe_zertifikate_faelligkeiten.py            # schickt die Mail wirklich (falls SMTP konfiguriert)
  ./venv/bin/python pruefe_zertifikate_faelligkeiten.py --dry-run  # zeigt nur, was verschickt würde
"""
import argparse
import sys

import mail_client
from app import app
from models import LieferantenZertifizierung

EMPFAENGER = "einkauf@heta.de"


def sammle_faellige():
    bald_ablaufend, abgelaufen = [], []
    for z in LieferantenZertifizierung.query.join(LieferantenZertifizierung.firma).order_by(
        LieferantenZertifizierung.iso9001_gueltig_bis
    ).all():
        status = z.status()
        if status == "bald_ablaufend":
            bald_ablaufend.append(z)
        elif status == "abgelaufen":
            abgelaufen.append(z)
    return bald_ablaufend, abgelaufen


def formatiere_zeile(z):
    datum = z.iso9001_gueltig_bis.strftime("%d.%m.%Y") if z.iso9001_gueltig_bis else "—"
    warengruppe = f" ({z.warengruppe})" if z.warengruppe else ""
    return f"  - {z.firma.name}{warengruppe}: ISO 9001 gültig bis {datum} ({z.tage_bis_ablauf()} Tage)"


def baue_mailtext(bald_ablaufend, abgelaufen):
    zeilen = ["Automatische wöchentliche Übersicht aus dem HETA Cockpit (Zertifikate, FB-0019)."]
    if abgelaufen:
        zeilen += ["", f"ABGELAUFEN ({len(abgelaufen)}):"]
        zeilen += [formatiere_zeile(z) for z in abgelaufen]
    if bald_ablaufend:
        zeilen += ["", f"BALD ABLAUFEND, < 90 Tage ({len(bald_ablaufend)}):"]
        zeilen += [formatiere_zeile(z) for z in bald_ablaufend]
    if mail_client.APP_BASE_URL:
        zeilen += ["", f"Zur Zertifikate-Ansicht: {mail_client.APP_BASE_URL.rstrip('/')}/?tab=firmen&fmview=zertifikate"]
    return "\n".join(zeilen)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts verschicken")
    args = parser.parse_args()

    with app.app_context():
        bald_ablaufend, abgelaufen = sammle_faellige()

        if not bald_ablaufend and not abgelaufen:
            print("Keine bald ablaufenden oder abgelaufenen Zertifikate — keine Mail nötig.")
            return

        text = baue_mailtext(bald_ablaufend, abgelaufen)
        betreff = f"Zertifikate-Erinnerung: {len(abgelaufen)} abgelaufen, {len(bald_ablaufend)} bald ablaufend"

        if args.dry_run:
            print(f"DRY-RUN — würde senden an {EMPFAENGER}:\n")
            print(f"Betreff: {betreff}\n")
            print(text)
            return

        if not mail_client.is_configured():
            print("SMTP ist nicht konfiguriert (SMTP_HOST fehlt) — Mail wird nicht verschickt.")
            print(f"Betreff: {betreff}\n{text}")
            sys.exit(1)

        mail_client.send_mail(EMPFAENGER, betreff, text)
        print(f"Mail an {EMPFAENGER} verschickt ({len(abgelaufen)} abgelaufen, {len(bald_ablaufend)} bald ablaufend).")


if __name__ == "__main__":
    main()
