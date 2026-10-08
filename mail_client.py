"""
E-Mail-Benachrichtigung für zugewiesene Aufgaben — Alternative zur
Microsoft-To-Do-Anbindung, falls die zuständige Person nicht ins Tool
schauen soll/kann. Braucht keine Azure-AD-App-Registrierung, nur Zugangsdaten
für einen SMTP-Server/Relay (von IT erfragen — deutlich kleinere Anfrage als
eine Graph-App-Registrierung mit Tasks.ReadWrite).

Konfiguration über Umgebungsvariablen:
  SMTP_HOST      (erforderlich, sonst ist die Integration "deaktiviert")
  SMTP_PORT      (Standard: 587)
  SMTP_USER      (optional, falls der Relay Authentifizierung verlangt)
  SMTP_PASSWORD  (optional)
  SMTP_USE_SSL   ("1" für direktes SMTPS/Port 465, sonst STARTTLS falls möglich)
  MAIL_FROM      (Absenderadresse; Standard: SMTP_USER, sonst "auftragspipeline@heta.de")
  APP_BASE_URL   (optional, z.B. "http://192.168.80.65" — als Link in der Mail)

Ist SMTP_HOST nicht gesetzt, tut send_task_mail() nichts und wirft keinen
Fehler — das Tool funktioniert dann weiter wie bisher (nur lokale Markierung).
"""
import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_USE_SSL = os.environ.get("SMTP_USE_SSL") == "1"
MAIL_FROM = os.environ.get("MAIL_FROM") or SMTP_USER or "auftragspipeline@heta.de"
APP_BASE_URL = os.environ.get("APP_BASE_URL")


def is_configured():
    return bool(SMTP_HOST)


def send_task_mail(to_email, title, body_text=None, due_date_iso=None):
    """
    Schickt eine einfache Text-E-Mail mit der Aufgabe an die zuständige Person.
    Gibt None zurück, wenn die Integration nicht konfiguriert ist. Wirft eine
    Exception bei einem echten SMTP-Fehler (der Aufruf in app.py fängt das ab).
    """
    if not is_configured():
        return None

    lines = [f"Dir wurde in der Auftragspipeline eine Aufgabe zugewiesen:", "", title]
    if body_text:
        lines += ["", body_text]
    if due_date_iso:
        lines += ["", f"Fällig: {due_date_iso}"]
    if APP_BASE_URL:
        lines += ["", f"Zum Tool: {APP_BASE_URL}"]

    msg = MIMEText("\n".join(lines), _charset="utf-8")
    msg["Subject"] = f"Aufgabe: {title}"
    msg["From"] = MAIL_FROM
    msg["To"] = to_email

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) if SMTP_USE_SSL \
        else smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    try:
        if not SMTP_USE_SSL:
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPNotSupportedError:
                pass
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(MAIL_FROM, [to_email], msg.as_string())
    finally:
        server.quit()
    return True
