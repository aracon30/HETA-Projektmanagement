"""Befüllt die Datenbank mit Beispieldaten. Aufruf: ./venv/bin/python seed.py"""
from datetime import date
from app import app
from models import db, User, Item, VerlaufEintrag

NUTZER = [
    ("Heiko Hensel", "Geschäftsführung", "hensel@heta.de"),
    ("Erik Scharmann", "Vertrieb", "scharmann@heta.de"),
    ("Gabriele Häfer", "Administration", "haefer@heta.de"),
    ("Sandra Voigt", "Vertrieb", "voigt@heta.de"),
    ("Thomas Berger", "Qualität", "berger@heta.de"),
    ("Julia Krämer", "Dokumentation", "kraemer@heta.de"),
    ("Markus Lindt", "Einkauf", "lindt@heta.de"),
    ("Nina Osei", "Versand", "osei@heta.de"),
    ("Philipp Schreiber", "Vertrieb", "p.schreiber@heta.de"),
]


def d(iso):
    return date.fromisoformat(iso) if iso else None


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        for name, abt, email in NUTZER:
            db.session.add(User(name=name, abteilung=abt, email=email))

        auftraege = [
            dict(kommission="K-04856/26", kunde="Lanxess AG", prio="rot",
                 lieferumfang="Dreistufige Filterkaskade inkl. Grundrahmen und Instrumentierung",
                 liefertermin="2026-09-12", status="offen",
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\K-04856_26_Lanxess",
                 verlauf=[
                     ("Technische Klärung Kaskadenstufen mit Konstruktion abgeschlossen, Freigabe Zeichnung steht noch aus.", "Erik Scharmann", "Erik Scharmann", "2026-08-22", "offen", False),
                     ("Rückfrage von Lanxess zu Werkstoffzeugnissen für die zweite Stufe eingegangen, Antwort noch offen.", "Heiko Hensel", "Sandra Voigt", "2026-08-20", "offen", True),
                     ("Vorabinfo vom Kunden telefonisch bestätigt, Auftragsbestätigung folgt schriftlich.", "Heiko Hensel", None, None, "erledigt", False),
                 ]),
            dict(kommission="K-04901/26", kunde="Covestro Deutschland AG", prio="gelb",
                 lieferumfang="Ersatz-Filterkerzen Baugröße 2, Nachbau nach Kundenzeichnung",
                 liefertermin="2026-09-05", status="offen",
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\K-04901_26_Covestro",
                 verlauf=[
                     ("Zeichnungsprüfung durch Dokumentation abgeschlossen, Stückliste angepasst.", "Julia Krämer", "Julia Krämer", None, "erledigt", False),
                     ("Bestellung der Rohmaterialien beim Einkauf einreichen.", "Erik Scharmann", "Markus Lindt", "2026-08-25", "offen", False),
                 ]),
            dict(kommission="K-04732/25", kunde="Evonik Operations GmbH", prio="gruen",
                 lieferumfang="Wartungsvertrag Filterservice, jährliche Inspektion",
                 liefertermin="2026-10-01", status="offen",
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\K-04732_25_Evonik",
                 verlauf=[
                     ("Termin für Vor-Ort-Inspektion mit Kunde abgestimmt.", "Nina Osei", "Nina Osei", "2026-09-28", "offen", False),
                 ]),
            dict(kommission="K-04888/26", kunde="BASF Personal Care", prio="rot",
                 lieferumfang="Sonderanfertigung Metallfilterkerzen, NDE-Prüfung nach ASME",
                 liefertermin="2026-08-29", status="offen",
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\K-04888_26_BASF",
                 verlauf=[
                     ("ASME-Prüfbericht liegt noch nicht vor, Rückfrage an Prüfstelle nötig.", "Thomas Berger", "Thomas Berger", "2026-08-19", "offen", True),
                     ("Fertigung Grundkörper abgeschlossen, wartet auf Prüfung.", "Markus Lindt", None, None, "erledigt", False),
                     ("Versandtermin mit Spedition vorabgestimmt, Bestätigung ausstehend.", "Nina Osei", "Nina Osei", "2026-08-27", "offen", False),
                 ]),
            dict(kommission="K-04799/25", kunde="Wacker Chemie AG", prio="gelb",
                 lieferumfang="Angebotsnachverfolgung Filterkaskade Erweiterung Halle 3",
                 liefertermin="2026-09-19", status="offen",
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\K-04799_25_Wacker",
                 verlauf=[
                     ("Angebot versendet, Rückmeldung des Kunden noch offen.", "Sandra Voigt", "Sandra Voigt", "2026-08-24", "offen", False),
                 ]),
            dict(kommission="K-04650/25", kunde="Currenta GmbH", prio="gruen",
                 lieferumfang="Lieferung Standardfilterkerzen aus Lagerbestand",
                 liefertermin="2026-08-21", status="erledigt",
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\K-04650_25_Currenta",
                 verlauf=[
                     ("Ware kommissioniert und verpackt.", "Nina Osei", None, None, "erledigt", False),
                     ("Lieferschein erstellt, Versand erfolgt morgen.", "Nina Osei", "Nina Osei", "2026-08-19", "erledigt", False),
                 ]),
        ]

        angebote = [
            dict(kommission="A-05123/26", kunde="Sanofi-Aventis Deutschland GmbH", status="wiedervorlage",
                 lieferumfang="Filterkaskade dreistufig für neue Produktionslinie, Vorabkalkulation",
                 wert="128.000 €", wiedervorlage="2026-08-25",
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\A-05123_26_Sanofi",
                 verlauf=[
                     ("Angebot am 08.08. versendet, telefonische Nachfrage für KW34 vereinbart.", "Sandra Voigt", "Sandra Voigt", "2026-08-25", "offen", True),
                     ("Technische Rückfrage des Kunden zu Werkstoffen mit Konstruktion geklärt.", "Erik Scharmann", None, None, "erledigt", False),
                 ]),
            dict(kommission="A-05144/26", kunde="Merck KGaA", status="in_bearbeitung",
                 lieferumfang="Ersatzteilangebot Filterelemente für Bestandsanlage",
                 wert="18.400 €", wiedervorlage=None,
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\A-05144_26_Merck",
                 verlauf=[
                     ("Kalkulation läuft, Preise vom Einkauf für Rohmaterial noch ausstehend.", "Sandra Voigt", "Markus Lindt", "2026-08-21", "offen", False),
                 ]),
            dict(kommission="A-05098/26", kunde="Boehringer Ingelheim Pharma", status="gewonnen",
                 lieferumfang="Wartungsvertrag Filterservice, mehrjährig",
                 wert="64.000 €", wiedervorlage=None,
                 ordner_pfad=r"K:\01 HETA\02 AUFTRÄGE\01 ab 2022\A-05098_26_Boehringer",
                 verlauf=[
                     ("Auftragsbestätigung vom Kunden erhalten, Übergabe an Auftragsabwicklung erfolgt.", "Sandra Voigt", None, None, "erledigt", False),
                 ]),
            dict(kommission="A-05156/26", kunde="Symrise AG", status="versendet",
                 lieferumfang="Sonderanfertigung Metallfilterkerzen, NDE-Prüfung erforderlich",
                 wert="41.200 €", wiedervorlage="2026-08-28",
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\A-05156_26_Symrise",
                 verlauf=[
                     ("Angebot versendet, Wiedervorlage in einer Woche eingeplant.", "Sandra Voigt", "Sandra Voigt", "2026-08-28", "offen", False),
                 ]),
            dict(kommission="A-05077/25", kunde="Bayer AG", status="verloren",
                 lieferumfang="Filterkaskade Erweiterung, Wettbewerber günstiger",
                 wert="95.000 €", wiedervorlage=None,
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\A-05077_25_Bayer",
                 verlauf=[
                     ("Absage des Kunden erhalten, Begründung: Preis. Für Nachkalkulation dokumentiert.", "Sandra Voigt", None, None, "erledigt", False),
                 ]),
            dict(kommission="A-05162/26", kunde="Fresenius Kabi Deutschland", status="in_bearbeitung",
                 lieferumfang="Neuanfrage Filterkaskade für Pilotanlage, erste Vorabstimmung",
                 wert="—", wiedervorlage=None,
                 ordner_pfad=r"K:\01 HETA\01 ANGEBOTE\01 ab 2022\A-05162_26_Fresenius",
                 verlauf=[
                     ("Erstgespräch mit Kunde geführt, technische Unterlagen angefordert.", "Sandra Voigt", "Sandra Voigt", "2026-08-26", "offen", False),
                 ]),
        ]

        for a in auftraege:
            item = Item(
                type="auftrag", kommission=a["kommission"], kunde=a["kunde"],
                lieferumfang=a["lieferumfang"], ordner_pfad=a["ordner_pfad"],
                prio=a["prio"], liefertermin=d(a["liefertermin"]), auftrag_status=a["status"],
                quelle="manuell",
            )
            db.session.add(item)
            db.session.flush()
            for text, von, verantw, faellig, status, aufgabe in a["verlauf"]:
                db.session.add(VerlaufEintrag(
                    item_id=item.id, text=text, erstellt_von=von, verantwortlich=verantw,
                    faelligkeit=d(faellig), status=status, aufgabe_erstellt=aufgabe,
                ))

        for a in angebote:
            item = Item(
                type="angebot", kommission=a["kommission"], kunde=a["kunde"],
                lieferumfang=a["lieferumfang"], ordner_pfad=a["ordner_pfad"],
                angebot_status=a["status"], wert=a["wert"], wiedervorlage=d(a["wiedervorlage"]),
                quelle="manuell",
            )
            db.session.add(item)
            db.session.flush()
            for text, von, verantw, faellig, status, aufgabe in a["verlauf"]:
                db.session.add(VerlaufEintrag(
                    item_id=item.id, text=text, erstellt_von=von, verantwortlich=verantw,
                    faelligkeit=d(faellig), status=status, aufgabe_erstellt=aufgabe,
                ))

        db.session.commit()
        print("Datenbank befüllt.")


if __name__ == "__main__":
    run()
