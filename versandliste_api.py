"""
Versandliste: Übersicht aller offenen Aufträge, deren Liefertermin in einem
wählbaren Zeitraum liegt (Standard: die kommenden 14 Tage) — für Fertigung
und Versand, damit immer klar ist, was als Nächstes fertig werden muss.
Löst den bisherigen Ausdruck aus dem Dashboard ab, der nie aktuell war
(besprochen 03.11.2026, siehe CLAUDE.md): die Live-Seite /versandliste liest
bei jedem Aufruf direkt aus der DB, und "PDF erzeugen" macht genau in diesem
Moment ein PDF daraus — kein veralteter Zettel mehr.

Eigene schlanke Seite statt eigener Tab in der Haupt-App, bewusst ohne das
App-Chrome (Sidebar/Tabs) — soll auf einem Bildschirm/Drucker in der
Werkstatt laufen, nicht im normalen Büro-Workflow bedient werden.

PDF-Erzeugung: docxtpl rendert vorlagen/versandliste/Versandliste.docx (HETA-
Blanko-Briefbogen "Blanco_Querformat.docx" auf A3 Querformat umgestellt,
siehe vorlagen/versandliste/README.md), anschließend wandelt `soffice
--headless --convert-to pdf` das Ergebnis in ein PDF um. Das braucht
LibreOffice Writer auf dem Server (`apt-get install -y libreoffice-writer`,
siehe CLAUDE.md) — ohne das Paket schlägt nur der PDF-Button fehl, die
Live-Ansicht funktioniert unabhängig davon.

Fund 03.11.2026: `soffice` wird per `shutil.which()` + Fallback-Pfaden
gesucht (`soffice_pfad()`), nicht einfach "soffice" an subprocess übergeben —
der systemd-Dienst (deploy/projektbesprechung.service) setzt
`Environment="PATH=..."` ausschließlich auf das venv-Verzeichnis, wodurch
/usr/bin (und damit ein per apt installiertes soffice) für den Dienst
unsichtbar war, obwohl LibreOffice korrekt installiert war. Die PATH-Variable
in der .service-Datei wurde deshalb um die üblichen System-Pfade ergänzt;
der Fallback im Code bleibt als zweite Absicherung bestehen.
"""
import io
import os
import shutil
import subprocess
import tempfile
from datetime import date, datetime, timedelta

from flask import Blueprint, current_app, jsonify, request, send_file, send_from_directory
from docxtpl import DocxTemplate

from models import Item
from asme_api import fmt_datum, sicherer_dateiname

bp = Blueprint("versandliste", __name__)

# Fallback-Pfade, falls "soffice" nicht über PATH gefunden wird — z.B. weil
# der systemd-Dienst (deploy/projektbesprechung.service) PATH auf das
# venv-Verzeichnis einschränkt und /usr/bin dadurch nicht mehr durchsucht
# wird (Fund 03.11.2026). Die Umgebungsvariable ist jetzt zwar erweitert,
# dieser Fallback macht den Code aber unabhängig von der Service-Konfiguration.
SOFFICE_FALLBACK_PFADE = ["/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"]


def soffice_pfad():
    gefunden = shutil.which("soffice")
    if gefunden:
        return gefunden
    for pfad in SOFFICE_FALLBACK_PFADE:
        if os.path.isfile(pfad):
            return pfad
    return None

VORLAGE_PFAD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vorlagen", "versandliste", "Versandliste.docx"
)

PRIO_LABEL = {"rot": "Rot", "gelb": "Gelb", "gruen": "Grün"}
STATUS_LABEL = {
    "neu": "Neu",
    "in_bearbeitung": "In Bearbeitung",
    "in_fertigung": "In Fertigung",
    "versandbereit": "Versandbereit",
    "erledigt": "Erledigt",
}

DEFAULT_TAGE = 14


def parse_datum(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def zeitraum_aus_request():
    """"von" ist standardmäßig OHNE untere Grenze (nicht "heute") — ein
    bereits überschrittener Liefertermin soll in der Liste nicht
    verschwinden, sondern (rot hervorgehoben) weiter auftauchen, bis der
    Auftrag erledigt/archiviert ist. Wer gezielt nur einen Zeitraum sehen
    will, setzt "von" selbst (Datumsfeld in der Live-Ansicht)."""
    heute = date.today()
    von = parse_datum(request.args.get("von"))
    bis = parse_datum(request.args.get("bis")) or (heute + timedelta(days=DEFAULT_TAGE))
    if von and bis < von:
        bis = von
    return von, bis


def zeitraum_text(von, bis):
    if von:
        return f"Zeitraum {fmt_datum(von)} – {fmt_datum(bis)}"
    return f"Alle offenen Aufträge bis {fmt_datum(bis)}"


def hole_auftraege(von, bis):
    bedingungen = [
        Item.type == "auftrag",
        Item.liefertermin.isnot(None),
        Item.liefertermin <= bis,
        Item.auftrag_status != "erledigt",
        Item.archiviert.isnot(True),
    ]
    if von:
        bedingungen.append(Item.liefertermin >= von)
    return (
        Item.query.filter(*bedingungen)
        .order_by(Item.liefertermin, Item.kommission)
        .all()
    )


def auftrag_zeile(item):
    return {
        "id": item.id,
        "kommission": item.kommission or "",
        "kunde": item.kunde or "",
        "liefertermin": item.liefertermin.isoformat() if item.liefertermin else None,
        "liefertermin_de": fmt_datum(item.liefertermin),
        "prio": item.prio,
        "prioLabel": PRIO_LABEL.get(item.prio, item.prio or "—"),
        "status": item.auftrag_status,
        "statusLabel": STATUS_LABEL.get(item.auftrag_status, item.auftrag_status or "—"),
        "lieferbedingungen": item.lieferbedingungen or "",
        "projektleiter": item.projektleiter or "",
        "lieferumfang": item.lieferumfang or "",
    }


@bp.route("/versandliste")
def versandliste_seite():
    return send_from_directory("static", "versandliste.html")


@bp.route("/api/versandliste")
def api_versandliste():
    von, bis = zeitraum_aus_request()
    auftraege = [auftrag_zeile(a) for a in hole_auftraege(von, bis)]
    return jsonify({
        "von": von.isoformat() if von else None,
        "bis": bis.isoformat(),
        "zeitraumText": zeitraum_text(von, bis),
        "erzeugtAm": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "auftraege": auftraege,
    })


@bp.route("/api/versandliste/pdf")
def api_versandliste_pdf():
    von, bis = zeitraum_aus_request()
    auftraege = [auftrag_zeile(a) for a in hole_auftraege(von, bis)]

    if not os.path.isfile(VORLAGE_PFAD):
        return jsonify({"error": f"Vorlage fehlt: {VORLAGE_PFAD}"}), 500

    soffice = soffice_pfad()
    if not soffice:
        current_app.logger.error(
            "Versandliste-PDF: 'soffice' weder über PATH (%s) noch unter %s gefunden.",
            os.environ.get("PATH", ""), SOFFICE_FALLBACK_PFADE,
        )
        return jsonify({
            "error": "PDF konnte nicht erzeugt werden: LibreOffice (soffice) wurde auf dem Server nicht "
                     "gefunden. Siehe README.md (libreoffice-writer installieren)."
        }), 500

    doc = DocxTemplate(VORLAGE_PFAD)
    doc.render({
        "zeitraum_text": zeitraum_text(von, bis),
        "erzeugt_am": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "auftraege": auftraege,
    }, autoescape=True)

    with tempfile.TemporaryDirectory() as tmp:
        docx_pfad = os.path.join(tmp, "Versandliste.docx")
        doc.save(docx_pfad)
        profil_pfad = os.path.join(tmp, "lo_profile")
        try:
            ergebnis = subprocess.run(
                [
                    soffice, "--headless", "--norestore",
                    f"-env:UserInstallation=file://{profil_pfad}",
                    "--convert-to", "pdf", "--outdir", tmp, docx_pfad,
                ],
                timeout=60, capture_output=True,
            )
        except subprocess.TimeoutExpired:
            current_app.logger.error("Versandliste-PDF: soffice-Aufruf nach 60s abgebrochen (TimeoutExpired).")
            return jsonify({"error": "PDF konnte nicht erzeugt werden: Zeitüberschreitung bei der Konvertierung."}), 500
        except OSError as exc:
            current_app.logger.error("Versandliste-PDF: Fehler beim Aufruf von soffice: %s", exc)
            return jsonify({"error": f"PDF konnte nicht erzeugt werden: {exc}"}), 500

        if ergebnis.returncode != 0:
            current_app.logger.error(
                "Versandliste-PDF: soffice beendet mit Code %s\nSTDOUT: %s\nSTDERR: %s",
                ergebnis.returncode,
                ergebnis.stdout.decode("utf-8", "replace"),
                ergebnis.stderr.decode("utf-8", "replace"),
            )
            return jsonify({
                "error": f"PDF konnte nicht erzeugt werden (soffice-Fehlercode {ergebnis.returncode}). "
                         "Details im Server-Log (journalctl -u projektbesprechung)."
            }), 500

        pdf_pfad = os.path.join(tmp, "Versandliste.pdf")
        if not os.path.isfile(pdf_pfad):
            current_app.logger.error(
                "Versandliste-PDF: soffice lief durch (Code 0), aber keine PDF-Datei im Ausgabeordner.\n"
                "STDOUT: %s\nSTDERR: %s",
                ergebnis.stdout.decode("utf-8", "replace"),
                ergebnis.stderr.decode("utf-8", "replace"),
            )
            return jsonify({"error": "PDF konnte nicht erzeugt werden (keine Ausgabedatei)."}), 500

        with open(pdf_pfad, "rb") as f:
            inhalt = f.read()

    von_teil = von.strftime("%Y%m%d") if von else "alle"
    dateiname = f"Versandliste_{von_teil}-{bis.strftime('%Y%m%d')}.pdf"
    return send_file(
        io.BytesIO(inhalt),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=sicherer_dateiname(dateiname.replace(".pdf", "")) + ".pdf",
    )
