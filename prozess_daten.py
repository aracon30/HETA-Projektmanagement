"""Startbestand der Prozessaufnahme (Reiter "Prozesse").

Einzige Quelle für:
- seed_prozesse.py  (befüllt die Datenbank, falls noch keine Prozesse existieren)
- docs/prozessaufnahme/_erzeuge_csv.py  (CSV-Dateien im Format der Excel-Vorlage
  HETA_Prozessaufnahme.xlsx)

Alle Inhalte sind aus den Arbeitsanweisungen abgeleitet bzw. Arbeitsvorschläge
und KEINE bestätigte Beschreibung der tatsächlichen Abläufe.
"""

# Aufnahmestatus eines Prozesses (Reihenfolge = Fortschritt)
AUFNAHMESTATUS = [
    ("vorgeschlagen", "Vorgeschlagen"),
    ("laut_aa", "Laut Arbeitsanweisung – Praxisabgleich offen"),
    ("aufgenommen", "Im Gespräch aufgenommen"),
    ("bestaetigt", "Von Beteiligten bestätigt"),
    ("anforderungen", "Anforderungen abgeleitet"),
]

# Weg einer Übergabe zwischen zwei Prozessen (Farbe in der Schnittstellenkarte)
UEBERGABE_WEGE = [
    ("email", "E-Mail"),
    ("dashboard", "Dashboard"),
    ("ordner", "Ordner / K-Laufwerk"),
    ("papier", "Papier"),
    ("muendlich", "Mündlich / Telefon"),
    ("sonstiges", "Sonstiges"),
    ("unklar", "Noch unklar"),
]

AUSWERTUNGSSTATUS = [
    ("nicht_gesichtet", "Nicht gesichtet"),
    ("gesichtet", "Gesichtet"),
    ("uebernommen", "In Schritte übernommen"),
]

# (nummer, bezeichnung, übergeordnete nummer, aufnahmestatus)
# Nummerierung aus den QM-Dokumentnummern der Arbeitsanweisungen abgeleitet,
# Namen der Hauptprozesse erschlossen – Abgleich mit QM-Handbuch offen.
LANDKARTE = [
    ("F", "Führungsprozesse", None, "vorgeschlagen"),
    ("K", "Kernprozesse", None, "vorgeschlagen"),
    ("U", "Unterstützungsprozesse", None, "vorgeschlagen"),
    ("F4.2", "Prüfmittelüberwachung", "F", "vorgeschlagen"),
    ("F4.5", "Kennzeichnung & Rückverfolgbarkeit", "F", "vorgeschlagen"),
    ("F4.6", "Dokumentenlenkung / Ablage", "F", "vorgeschlagen"),
    ("K1", "Vertrieb / Angebot", "K", "vorgeschlagen"),
    ("K1.05", "Angebotserstellung", "K1", "laut_aa"),
    ("K2", "Konstruktion / Entwicklung", "K", "vorgeschlagen"),
    ("K3", "Auftragsabwicklung (Name lt. QM offen)", "K", "vorgeschlagen"),
    ("K3.1", "Auftragsbearbeitung", "K3", "laut_aa"),
    ("K3.2", "Versand & Rechnung", "K3", "vorgeschlagen"),
    ("K3.3", "Fertigung", "K3", "vorgeschlagen"),
    ("K4", "Kundenzufriedenheit", "K", "vorgeschlagen"),
    ("U1", "Beschaffung", "U", "vorgeschlagen"),
    ("U1.1", "Bestellung", "U1", "vorgeschlagen"),
    ("U1.2", "Lieferantenauswahl & -freigabe", "U1", "vorgeschlagen"),
    ("U1.3", "Lieferantenbewertung", "U1", "vorgeschlagen"),
    ("U1.4", "Wareneingang & Materialeingangsprüfung", "U1", "vorgeschlagen"),
    ("U2", "Arbeitssicherheit / Umwelt", "U", "vorgeschlagen"),
    ("U4", "Verwaltung / Personal", "U", "vorgeschlagen"),
]

PROZESS_DETAILS = {
    "K1.05": dict(
        variante="Handelsware · Fertigung · HETA-Ersatzteil · Fremdfabrikat-Ersatzteil",
        verantwortlich="Vertrieb Werk 4",
        ausloeser="Kundenanfrage",
        ergebnis="Versendetes, abgelegtes Angebot mit Nachverfolgung",
        beteiligte="Mitarbeitende Vertrieb, ggf. Technik, Auslegung/Kalkulation, Geschäftsleitung (Unterschrift)",
        systeme="Dashboard, K-Laufwerk, Kalkulationsvorlage, Angebotsvorlage DE/EN, E-Mail, Papierablage",
    ),
    "K3.1": dict(
        variante="Behälterbau (Fertigung) · Ersatzteil HETA-Filter · Ersatzteil Fremd-Filter · Service",
        verantwortlich="Vertrieb/Administration Werk 4",
        ausloeser="Kundenbestellung (auf gültiges oder abgelaufenes Angebot oder ohne Angebot)",
        ergebnis="Auftrag im Dashboard erfasst, Kommissionsordner angelegt, AB beim Kunden (Ziel ≤ 3 Tage), "
                 "Rundmail mit AB an alle",
        beteiligte="Alle Mitarbeitenden (Information), ggf. Buchhaltung (Debitor)",
        systeme="Dashboard, K-Laufwerk, AB-Vorlage, E-Mail-Verteiler",
    ),
}

# (dokumentnummer, revision, titel, geltungsbereich, prozessnummer, auswertungsstatus)
# Prozessnummern ohne eigenen Knoten (z.B. U2.2) werden beim Seed dem nächsthöheren
# vorhandenen Prozess zugeordnet.
DOKUMENTE = [
    ("AA_F4.2_01", "R2", "Prüfmittelüberwachung", "Werk4", "F4.2", "nicht_gesichtet"),
    ("AA_F4.2_02", "R1", "Kalibrierung Schweißgeräte", "Werk4", "F4.2", "nicht_gesichtet"),
    ("AA_F4.5_01", "R1", "Umgang Werkstoffprüfzeugnis", "Werk4", "F4.5", "nicht_gesichtet"),
    ("AA_F4.5_02", "R1", "Kennzeichnungen in der Fertigung", "Werk4", "F4.5", "nicht_gesichtet"),
    ("AA_F4.6_01", "R1", "Projektordnerstruktur", "Werk4", "F4.6", "nicht_gesichtet"),
    ("AA_F4.6_02", "R1", "Nummernschlüssel", "Werk4", "F4.6", "nicht_gesichtet"),
    ("AA_K1_01", "R1", "Anwendung DASHBOARD", "Werk4", "K1", "nicht_gesichtet"),
    ("AA_K1_02", "R3", "Verwendung Namenskürzel", "Werk4", "K1", "nicht_gesichtet"),
    ("AA_K1_03", "R1", "Ablagesystem E-Mails", "Werk4", "K1", "nicht_gesichtet"),
    ("AA_K1_04", "R1", "Dokumentation von projektbezogenen Informationen", "Werk4", "K1", "nicht_gesichtet"),
    ("AA_K1_05", "R1", "Erstellen von Angeboten", "Werk4", "K1.05", "uebernommen"),
    ("AA_K2_01", "R2", "Anweisung Konstruktion", "Werk4", "K2", "nicht_gesichtet"),
    ("AA_K2_02", "R2", "Zeichnungsänderung", "Werk4", "K2", "nicht_gesichtet"),
    ("AA_K2_03", "R2", "Prüfung Konstruktionsunterlagen", "Werk4", "K2", "nicht_gesichtet"),
    ("AA_K2_04", "R2", "Zeichnungen als PDF-Format", "Werk4", "K2", "nicht_gesichtet"),
    ("AA_K2_05", "R1", "Interne Konstruktionsrichtlinien", "Werk4", "K2", "nicht_gesichtet"),
    ("AA_K3.1_01", "R1", "Auftragsbearbeitung", "Werk4", "K3.1", "uebernommen"),
    ("AA_K3.2_01", "R1", "Versand", "Werk4", "K3.2", "nicht_gesichtet"),
    ("AA_K3.2_02", "R0", "Rechnungserstellung", "Werk4", "K3.2", "nicht_gesichtet"),
    ("AA_K3.3.11-01", "R1", "Vorbereitung von Druckproben", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K3.3.11-02", "R1", "Schweisszusatzwerkstoffe", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K3.3.11-03", "R1", "Rücktrocknung von Elektroden", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K3.3.11-04", "R2", "Umstempelung", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K3.3.11-05", "R1", "Lagerwesen", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K3.3.11-06", "R1", "Maschinenwartung", "ohne Angabe", "K3.3", "nicht_gesichtet"),
    ("AA_K4_01", "R1", "Kundenzufriedenheit", "Werk4", "K4", "nicht_gesichtet"),
    ("AA_U1.1_01", "R2", "Bestellung", "Werk4", "U1.1", "nicht_gesichtet"),
    ("AA_U1.2_01", "R3", "Lieferantenauswahl + Lieferantenfreigabe", "Werk4", "U1.2", "nicht_gesichtet"),
    ("AA_U1.3_01", "R1", "Lieferantenbewertung", "Werk4", "U1.3", "nicht_gesichtet"),
    ("AA_U1.4_01", "R1", "Materialeingangsprüfung", "Werk4", "U1.4", "nicht_gesichtet"),
    ("AA_U1.4_02", "R4", "Wareneingang", "Werk4", "U1.4", "nicht_gesichtet"),
    ("AA_U2_01", "R1", "Prüfung von Anschlagmitteln", "ohne Angabe", "U2", "nicht_gesichtet"),
    ("AA_U2.2_01", "R2", "Erstunterweisung", "Werk4", "U2.2", "nicht_gesichtet"),
    ("AA_U2.4_01", "R2", "Abfallentsorgung", "Werk4", "U2.4", "nicht_gesichtet"),
    ("AA_U4_01", "R1", "Sanktionslistenprüfung", "Werk4", "U4", "nicht_gesichtet"),
    ("AA_U4.3_01", "R1", "Arbeitszeiterfassung", "Werk4", "U4.3", "nicht_gesichtet"),
    ("AA_U4.3_02", "R1", "Arbeitszeitnachweis", "Werk4", "U4.3", "nicht_gesichtet"),
    ("ES", "", "Interne Konstruktionsrichtlinien mit Anlage C (ES-Fassung?)", "ohne Angabe", "K2", "nicht_gesichtet"),
]

AA_ANG = "Laut AA K1_05 Rev. 1 – Praxisabgleich offen"
AA_AUF = "Laut AA K3.1_01 Rev. 1 – Praxisabgleich offen"
V = "Vertrieb Werk 4 (Person offen)"
VA = "Vertrieb/Administration Werk 4 (Person offen)"

# Spalten wie Excel-Arbeitsblatt "Ablaufschritte":
# Prozess-ID, Schritt-Nr., Tätigkeit, Ausführende Person / Rolle, Eingaben, System,
# Ergebnis, Übergabe, Freigabe, Ausnahme / nächster Schritt, Bearbeitungszeit,
# Wartezeit, Nachweis / Prüfstatus
SCHRITTE = [
    ["K1.05", 1, "Kundenstatus prüfen (Neu- oder Bestandskunde), bei Neukunden Sanktionslistenprüfung", V,
     "Kundenanfrage", "Sanktionsliste (AA U4_01), Dashboard?", "Kunde eingeordnet, Sanktionsprüfung erledigt",
     "", "", "Negative Sanktionsprüfung: Vorgehen offen", "", "", AA_ANG],
    ["K1.05", 2, "Anfrage einordnen: Handelsware oder Fertigung, HETA-Ersatzteil oder Fremdfabrikat", V,
     "Kundenanfrage", "", "Anfrageart festgelegt", "", "", "", "", "", AA_ANG],
    ["K1.05", 3, "Technisch prüfen: HETA-Ersatzteil gegen Ursprungsauftrag, Fremdfabrikat technisch, "
     "Fertigung auf Machbarkeit (Spezifikation, Auslegungsdaten, Werkstoffe)", V + ", ggf. Technik",
     "Anfrage, Ursprungsauftrag, Kundenspezifikation", "", "Machbarkeit bestätigt", "ggf. Technik", "",
     "Fehlende Machbarkeit: Entscheidung offen", "", "", AA_ANG],
    ["K1.05", 4, "Anfrage im Dashboard erfassen, Ordner mit Länderkürzel (ISO 3166-1 Alpha-2) anlegen, "
     "ggf. Ursprungs-/Wiederholungsauftrag vermerken", V, "Anfrage",
     "Dashboard (AA K1_01), K-Laufwerk (AA F4.6_01/F4.6_02)", "Anfrage erfasst, Ordner angelegt",
     "", "", "", "", "", AA_ANG],
    ["K1.05", 5, "Eingang der Anfrage beim Kunden schriftlich bestätigen", V, "", "E-Mail",
     "Eingangsbestätigung versendet", "Kunde", "", "", "", "", AA_ANG],
    ["K1.05", 6, "Lieferanten auswählen, Preis/Lieferzeit anfragen, kalkulieren (Handelsware: Lieferantenangebot; "
     "Fertigung: Material + Fertigungs-, Konstruktions-, Dokumentationsstunden)", V + ", ggf. Auslegung/Kalkulation",
     "Lieferantenangebote, Rohmaterialpreise", "Kalkulationsvorlage, E-Mail", "Kalkulation / Verkaufspreis",
     "", "offen", "", "", "", AA_ANG],
    ["K1.05", 7, "Lieferbedingungen festlegen (Standard FCA Lich, abweichend verhandelbar)", V, "", "",
     "Lieferbedingung", "", "", "", "", "", AA_ANG],
    ["K1.05", 8, "Zahlungskonditionen festlegen, Bonität prüfen (abhängig von Angebotshöhe und Land)", V,
     "Angebotshöhe, Land", "offen", "Zahlungskondition", "", "", "Negative Bonität: Vorgehen offen",
     "", "", AA_ANG],
    ["K1.05", 9, "Angebot mit DE-/EN-Vorlage erstellen (Technik, Preis, Gültigkeit), nach Unterschriftenregelung "
     "unterschreiben lassen", V, "Kalkulation, Konditionen", "Angebotsvorlage DE/EN", "Unterschriebenes Angebot",
     "", "Unterschriftenregelung (offen)", "", "", "", AA_ANG],
    ["K1.05", 10, "Angebot an Kunden senden, als Hard- und Softcopy ablegen", V, "Angebot",
     "E-Mail, K-Laufwerk, Papierablage", "Angebot versendet und abgelegt", "Kunde", "", "", "", "", AA_ANG],
    ["K1.05", 11, "Angebot nach ca. 2–4 Wochen nachfassen", V, "", "offen (Wiedervorlage wo?)",
     "Rückmeldung Kunde", "", "", "Absage/Verlustgrund: Erfassung offen", "", "", AA_ANG],

    ["K3.1", 1, "Auftragseingang prüfen: Bestellung auf gültiges Angebot, abgelaufenes Angebot oder ohne Angebot; "
     "Preis, Lieferzeit, Artikel, ggf. Zeichnungsnummer prüfen", VA, "Kundenbestellung, Angebot",
     "Dashboard (Angebotsliste)", "Bestellung geprüft", "", "", "Abweichung zum Angebot: Vorgehen offen",
     "", "", AA_AUF],
    ["K3.1", 2, "Debitorenstamm prüfen, bei neuem Debitor Sanktionslistenprüfung", VA, "Kundendaten",
     "Debitorenstamm (System offen), AA U4_01", "Debitor vorhanden/angelegt, Sanktionsprüfung erledigt",
     "ggf. Buchhaltung", "", "Wortlaut der AA widersprüchlich (siehe Offene Fragen)", "", "", AA_AUF],
    ["K3.1", 3, "Auftragsart einordnen: Behälterbau (Fertigung), Ersatzteil HETA-Filter (Fertigung/Handelsware), "
     "Ersatzteil Fremd-Filter (Fertigung/Handelsware), Service (Wartung, Reparatur)", VA, "Bestellung", "",
     "Auftragsart festgelegt", "", "", "", "", "", AA_AUF],
    ["K3.1", 4, "Auftrag in der Auftragsliste im Dashboard erfassen: aus Angebotsliste übernehmen oder manuell",
     VA, "Bestellung, Angebot", "Dashboard (AA K1_01)", "Auftrag erfasst, Kommissionsnummer (AA F4.6_02)",
     "", "", "Ohne Angebot: manuelle Erfassung", "", "", AA_AUF],
    ["K3.1", 5, "Auftragsordner über Dashboard anlegen: Angebotsordner in Kommission umwandeln bzw. neu anlegen",
     VA, "Angebotsordner", "Dashboard, K-Laufwerk", "Auftragsordner / Kommission", "", "",
     "Ohne Angebot: Ordner ohne Vorinformationen", "", "", AA_AUF],
    ["K3.1", 6, "Kundenbestellung und ggf. Zeichnungen im Dashboard verknüpfen, Bezug zu Ursprungsauftrag / "
     "letzter identischer Lieferung herstellen", VA, "Bestellung, Zeichnungen, Altaufträge", "Dashboard",
     "Verknüpfte Auftragsunterlagen", "", "", "", "", "", AA_AUF],
    ["K3.1", 7, "Info-Mail „neuer Auftrag“ an alle MA mit eigener E-Mail-Adresse (Liefertermin, Umfang, "
     "Ursprungsauftrag/letzte Lieferung, ggf. PM-Verantwortliche:r)", VA, "Auftragsdaten", "E-Mail-Verteiler",
     "Alle MA informiert", "Alle MA (PM, Konstruktion, Einkauf, Fertigung …)", "",
     "Praxis: Rundmail an alle mit beigefügter AB (lt. Philipp Schreiber) – Reihenfolge zu Schritt 8/9 klären",
     "", "", AA_AUF + ", Praxisangabe liegt vor"],
    ["K3.1", 8, "AB im Vorlageformular schreiben, parallel Wunschliefertermin prüfen/ggf. revidieren, Preis, "
     "Lieferumfang, Liefer- und Zahlungsbedingungen prüfen", VA + ", Liefertermin-Prüfung mit ? (offen)",
     "Bestellung, Angebot", "AB-Vorlage", "AB, bestätigter Liefertermin", "", "offen", "", "", "", AA_AUF],
    ["K3.1", 9, "AB innerhalb von 3 Tagen versenden, bei Verzögerung Bestelleingang vorab per E-Mail bestätigen",
     VA, "AB", "E-Mail", "AB beim Kunden", "Kunde", "", "Verzögerung: Vorab-Eingangsbestätigung", "",
     "Ziel max. 3 Tage", AA_AUF],
]

# (prozessbezug, frage, klärung durch[, status, antwort, nachweis])
FRAGEN = [
    ("F", "Offizielle Namen der Hauptprozesse laut QM-Handbuch? Was verbirgt sich hinter F1–F3 und U3 (keine AA vorhanden)?", "Häfer"),
    ("F4.6", "Geltungsbereich „Werk4“: Gilt er für alle Bereiche? Warum tragen die K3.3.11-AA und AA U2_01 keinen Zusatz „Werk4“?", "Häfer"),
    ("K", "Service- und Ersatzteilgeschäft hat keinen eigenen Prozess, obwohl es laut Organigramm eine Funktion „Standard- und Ersatzteile“ gibt. Steckt es in K1/K3.1?", "Brühl / Linker / Nitzsche"),
    ("K", "Für Auslegung/Kalkulation, Projektmanagement, Fertigungsplanung und Inbetriebnahme gibt es keine AA. Lücke oder anderswo geregelt?", "Hensel / Häfer"),
    ("K3.2", "Rechnungserstellung steht auf Revision R0: Entwurf, nie freigegeben?", "Häfer / Brühl"),
    ("K3.3", "Lagerwesen ist unter Fertigung (K3.3.11) einsortiert, Wareneingang unter Beschaffung (U1.4). Wer ist tatsächlich für Lager, Wareneingang und Versand zuständig?", "Justus / Köhler"),
    ("K1.05", "Wer bearbeitet die einzelnen Schritte? Wann werden Technik, Einkauf oder Geschäftsleitung eingebunden?", "Linker"),
    ("K1.05", "Dashboard: Welche Felder und Status werden genutzt? Wer pflegt die Daten?", "Linker"),
    ("K1.05", "Kalkulation: Wie werden Stundensätze, Zuschläge, Marge und Verkaufspreis festgelegt und freigegeben?", "Hensel / Mühlberger"),
    ("K1.05", "Sanktions- und Bonitätsprüfung: Wer prüft, wo wird das Ergebnis dokumentiert?", "Linker"),
    ("K1.05", "Unterschriftenregelung: Wer darf welche Angebote unterschreiben? Gibt es Wertgrenzen?", "Hensel"),
    ("K1.05", "Wie wird mit unvollständigen Kundendaten umgegangen?", "Linker"),
    ("K1.05", "Negative Prüfung / fehlende Machbarkeit: Wer entscheidet über das weitere Vorgehen?", "Hensel"),
    ("K1.05", "Angebotsrevisionen: Wie werden Änderungen und ältere Angebotsstände gekennzeichnet?", "Linker"),
    ("K1.05", "Nachverfolgung: Wer setzt Wiedervorlagen? Wo werden Rückmeldungen, Absagen und Verlustgründe erfasst?", "Linker"),
    ("K1.05/K3.1", "Übergang zum Auftrag: Welche Angebotsdaten werden übernommen, welche erneut eingegeben?", "Linker"),
    ("K3.1", "AA-Wortlaut: „wurde der Kunde bereits als Debitor erfasst, muss ggf. eine Sanktionsprüfung erfolgen“ – gemeint ist vermutlich „noch nicht erfasst“? Wird bei Bestandskunden erneut geprüft?", "Linker"),
    ("K3.1", "Wo wird der Debitorenstamm geführt (Buchhaltungssoftware? Dashboard?) und wer legt neue Debitoren an?", "Brühl / Buchhaltung"),
    ("K3.1", "Bestellung auf abgelaufenes Angebot oder mit abweichendem Preis/Lieferzeit: Wer entscheidet, wie wird der Kunde informiert?", "Linker / Hensel"),
    ("K3.1", "Wie und von wem wird die Kommissionsnummer vergeben? Automatisch durch das Dashboard?", "Linker"),
    ("K3.1", "Liefertermin prüfen: Mit wem (Konstruktion, Einkauf, Fertigung)? Gibt es eine Kapazitätsübersicht?", "Linker / Justus"),
    ("K3.1", "Wer benennt die PM-Verantwortliche Person und wann? Gibt es Kriterien (Auftragsart, Wert)?", "Hensel / Brühl"),
    ("K3.1", "Die Info-Mail an alle ist die einzige beschriebene Übergabe: Woher wissen Konstruktion, Einkauf und Fertigung, dass sie konkret etwas tun müssen?", "Linker, Scharmann, Köhler, Justus",
     "beantwortet", "Übergabe erfolgt per Rundmail an alle, der die Auftragsbestätigung beiliegt.",
     "Aussage Philipp Schreiber, 28.09.2026"),
    ("K3.1", "Rundmail mit AB: Wird sie erst nach Erstellung der AB verschickt (laut AA kommt die Info-Mail vor der AB)? Gibt es bei Verzögerung der AB vorab eine Info-Mail ohne AB?", "Linker"),
    ("K3.1", "Nach der Rundmail: Leitet jeder Bereich seine Aufgaben selbst aus der AB ab, oder beauftragt jemand (z.B. PM) Konstruktion, Einkauf und Fertigung ausdrücklich? Wer merkt, wenn niemand reagiert?", "Linker, Häfer, Hamp, Schreiber"),
    ("K3.1", "Welche Informationen fehlen den Bereichen in der AB (interne Hinweise, Ursprungsauftrag, PM-Verantwortliche:r) und werden anders nachgereicht?", "Scharmann, Köhler, Justus"),
    ("K3.1", "Wer unterschreibt/gibt die AB frei? Gilt die Unterschriftenregelung des Angebots?", "Hensel"),
    ("K3.1", "Wo wird die AB abgelegt und wo wird die AB-Nummer vergeben?", "Linker"),
    ("K3.1", "Unterscheidet sich der Ablauf je Auftragsart (Behälterbau, Ersatzteil, Service)? Wer übernimmt Serviceaufträge?", "Brühl / Linker / Nitzsche"),
    ("K3.1", "Wird die 3-Tage-Frist für die AB gemessen oder nachgehalten?", "Linker"),
    ("K3.1", "Kundenseitige Auftragsänderungen nach AB: Wie laufen sie ab (keine AA vorhanden)?", "Linker"),
    ("K3.1", "Mitgeltende Dokumente: Sanktionslistenprüfung (AA U4_01) und Projektordnerstruktur (AA F4.6_01) werden im Text genutzt, aber nicht als mitgeltend aufgeführt – ergänzen?", "Häfer"),
]

# Spalten wie Excel-Arbeitsblatt "Systeme und Daten"
SYSTEME = [
    ["S01", "Dashboard (Excel-Makrodateien: MASTERDATEN AUFTRAG.xlsx, Auftragsübersicht.xlsm, Positionsansicht Auftrag.xlsm)",
     "Anfrage-, Angebots- und Auftragslisten, Ordneranlage, Verknüpfung Bestellung/Zeichnungen", "K1.05, K3.1",
     "offen", "ja (vermutlich)", r"K:\Datenstruktur\Systemdateien\DB_Statistik\ (Positionsansicht)",
     "manuelle Eingabe, Übernahme Angebot → Auftrag", "offen", "hoch – zentrale Datenquelle"],
    ["S02", "Projekt-/Auftragsordner K-Laufwerk", "Angebots- und Auftragsunterlagen, Kommission", "K1.05, K3.1",
     "Vertrieb/Administration", "", "K-Laufwerk (Struktur lt. AA F4.6_01)", "Anlage über Dashboard", "offen", "offen"],
    ["S03", "Kalkulationsvorlage", "Material, Stunden, Preis", "K1.05", "offen", "", "offen", "", "offen", "offen"],
    ["S04", "Angebotsvorlage DE/EN", "Angebotsdokument", "K1.05", "offen", "", "offen", "", "", ""],
    ["S05", "AB-Vorlageformular", "Auftragsbestätigung", "K3.1", "offen", "", "offen", "", "", ""],
    ["S06", "Debitorenstamm", "Kundenstammdaten", "K3.1, Buchhaltung", "offen", "offen", "offen (System?)", "", "offen", "hoch"],
    ["S07", "E-Mail / Verteiler „alle MA“", "Auftragsinformation mit AB (Rundmail), Eingangsbestätigungen", "K1.05, K3.1",
     "", "", "Outlook (Ablage lt. AA K1_03)", "", "", ""],
    ["S08", "Papierablage (Hardcopy)", "Angebote", "K1.05", "", "", "offen", "", "", ""],
    ["S09", "Material-Deadline-Liste (MDL, Excel)", "Zu bestellende Teile je Auftrag, Bestellstatus", "U1.1",
     "Einkauf", "offen", "offen", "aus Stückliste (von Hand?)", "offen", "hoch"],
    ["S10", "Dashboard – Bestellliste", "Bestellnummern, Bestelldaten, Lieferungen, Rechnungswerte", "U1.1",
     "Einkauf", "offen", "Dashboard", "manuell aus Bestellung, Lieferschein, DATEV", "offen", "hoch"],
    ["S11", "DATEV", "Eingangsrechnungen, Prüfung und Freigabe", "U1.1, Buchhaltung", "Buchhaltung/Einkauf",
     "ja (Rechnungen)", "DATEV", "", "", "Schnittstelle prüfen"],
    ["S12", "Lagerbestandsliste (Excel, FB_K3.3.11-26)", "Rohre, Flansche, Stangenmaterial: Zugänge/Entnahmen",
     "Lager, U1.4, U1.1", "Justus, Köhler, Häfer", "ja (einzige Bestandsführung)", r"K:\02 Lager\Lagerbestand",
     "Wareneingang, Entnahme, Zettel", "offen (Zettel-Entnahmen)", "hoch"],
    ["S13", "Wareneingang: Stempel, Ordner WE, Ablagekästen rot/blau", "Lieferscheine unbearbeitet/bearbeitet",
     "U1.4, U1.1", "Wareneingang", "", "Papier + Scan", "Papier", "", "mittel"],
]


# ---------------------------------------------------------------------------
# Ergänzungen zum Startbestand
# ---------------------------------------------------------------------------
# Jede Ergänzung wird von seed_prozesse.py genau einmal eingespielt (Stand wird
# in der Tabelle startbestand_stand gemerkt). Dabei werden Änderungen aus dem
# Tool nicht überschrieben: fehlende Prozesse/Dokumente werden angelegt,
# Steckbrief-Felder nur gefüllt, wenn sie leer sind, Status nur von
# "vorgeschlagen" bzw. "nicht_gesichtet" aus hochgesetzt, Schritte nur ergänzt,
# wenn der Prozess noch keine hat.

AA_KON = "Laut AA K2_01 Rev. 2 – Praxisabgleich offen"
KON = "Konstrukteur:in (Konstruktion Werk 4, Person offen)"

ERGAENZUNGEN = [
    (2, dict(
        titel="AA K2_01 Anweisung Konstruktion ausgewertet (29.09.2026)",
        landkarte=[],
        details={
            "K2": dict(
                verantwortlich="Leiter Konstruktion, PM",
                beteiligte="Konstruktion Werk 4 (Scharmann, Hennig, Abdani), Einkauf, Schweißaufsicht (Justus, Abdani)",
                ausloeser="Neuer Auftrag (vermutlich Rundmail mit AB – Zuweisung an Konstrukteur:in offen)",
                ergebnis="Vollständige, kundenspezifische Konstruktionsunterlagen an alle betroffenen Abteilungen "
                         "verteilt, Werkstoffe und Bestelltexte mit Einkauf abgestimmt",
                systeme="CAD (System offen), Zeichnungsvorlagen (Stutzentabelle, Technische Daten), "
                        "Kundenspezifikationen (z.B. BASF-Werksnorm, Thyssen Krupp/UHDE)",
                variante="Auslegung nach AD 2000/DGRL oder ASME · kundenspezifische Unterlagen (BASF, Thyssen Krupp/UHDE)",
            ),
        },
        status={"K2": "laut_aa"},
        dokument_status={"AA_K2_01": "uebernommen"},
        schritte=[
            ["K2", 1, "Aufgabe übernehmen und alle erforderlichen Unterlagen beschaffen: Projektspezifikation, "
             "Kundennormen/-vorschriften (z.B. BASF-Werksnorm), Bestellung des Kunden", KON,
             "AB/Kundenbestellung, Projektspezifikation, Kundennormen", "K-Laufwerk (Auftragsordner)?",
             "Vollständige Auslegungsgrundlagen", "", "", "Fehlende Unterlagen: Konstrukteur:in muss sie beschaffen",
             "", "", AA_KON],
            ["K2", 2, "Fertigbarkeit mit der Schweißtechnik abstimmen: Schweißverfahren und Schweißzusatz "
             "rechtzeitig planen", KON + ", Schweißaufsicht", "Konstruktionsentwurf, Werkstoffe", "",
             "Schweißtechnisch abgestimmte Konstruktion", "Schweißaufsicht", "", "", "", "", AA_KON],
            ["K2", 3, "Werkstoffe anhand der Vorgaben aus Prozess und Spezifikation festlegen", KON,
             "Spezifikation, Prozessdaten", "", "Werkstoffauswahl", "", "", "", "", "", AA_KON],
            ["K2", 4, "Bestelltexte für die Materialbestellung mit dem Einkauf absprechen, Einsatz von "
             "Alternativmaterial aus dem Lager abstimmen, Auswahl in die Konstruktionsunterlagen einarbeiten",
             KON + ", Einkauf", "Werkstoffauswahl, Lagerbestand", "offen (Mail? Liste? Zeichnung?)",
             "Abgestimmte Bestelltexte / Materialauswahl", "Einkauf (Materialbestellung, U1.1)", "",
             "Stückliste wird in der AA nicht erwähnt (siehe Offene Fragen)", "", "", AA_KON],
            ["K2", 5, "Konstruktionsunterlagen nach allgemeinen Regeln erstellen: Benennung wie in der Kundenbestellung "
             "(ggf. mit Pos./Item-Nr.), HETA-Typennummer im Schriftfeld, Stutzentabelle nach Vorlage, "
             "Tabelle Technische Daten vollständig (DGRL/AD 2000 mit Kategorie/Modul oder ASME mit MAWP/MDMT)",
             KON, "Auslegungsdaten, Kundenbestellung", "CAD, Zeichnungsvorlagen",
             "Zeichnungen mit Stutzentabelle und Technischen Daten", "", "",
             "Fehlende technische Daten müssen in Erfahrung gebracht werden (keine leeren Zeilen)",
             "", "", AA_KON],
            ["K2", 6, "Kundenspezifische Angaben ergänzen – z.B. BASF (WN): Benennung mit Größe/Druck/Temperatur/"
             "Werkstoff, Bestellangaben, zugehörige Zeichnungen, äußere Lasten, Anzugsmomente, Schweißangaben, "
             "Toleranzen, Kennzeichnung, Oberfläche; Thyssen Krupp (UHDE): TK-Schriftkopf auf jeder Unterlage, "
             "Stutzenlasten, Anzugsmomente, Hinweise, Oberfläche", KON,
             "Kundenspezifikation, Kundenbestellung", "CAD, Kundenvorlagen (z.B. TK-Logo/Schriftkopf)",
             "Kundenkonforme Konstruktionsunterlagen", "", "", "", "", "", AA_KON],
            ["K2", 7, "Alle zutreffenden Abteilungen frühzeitig und vollständig mit den Zeichnungsunterlagen "
             "versorgen", KON, "Fertige Konstruktionsunterlagen", "offen (K-Laufwerk? Mail? Papier?)",
             "Abteilungen haben aktuelle Unterlagen",
             "Fertigung, Einkauf, PM, Dokumentation (Weg offen)", "Prüfung/Freigabe vorher? (AA K2_03)",
             "", "", "", AA_KON],
            ["K2", 8, "Änderungsdienst bei Kundenänderungen nach AA K2_02 Zeichnungsänderung: Unterlagen ändern und "
             "intern alle informieren, damit Bestellungen bei Lieferanten angepasst werden können", KON,
             "Änderungswunsch des Kunden", "CAD, AA K2_02", "Geänderte Unterlagen, alle informiert",
             "Alle Betroffenen, insbesondere Einkauf", "", "", "", "", AA_KON],
        ],
        fragen=[
            ("K2", "Wie erfährt die Konstruktion von einem neuen Auftrag (Rundmail mit AB?) und wer weist ihn einer "
                   "Konstrukteurin/einem Konstrukteur zu – Leiter Konstruktion oder PM?", "Scharmann"),
            ("K2", "Stückliste: Wird eine erstellt, in welchem System (CAD, Excel?) und wie gelangt sie zum Einkauf? "
                   "Die AA nennt nur das Abstimmen der Bestelltexte.", "Scharmann / Köhler"),
            ("K2", "Bestelltexte an den Einkauf: In welcher Form werden sie übergeben (Mail, Liste, Zeichnung) und "
                   "wann – alles auf einmal oder Langläufer vorab?", "Scharmann / Köhler"),
            ("K2", "Alternativmaterial aus dem Lager: Woher weiß die Konstruktion, was am Lager ist? Gibt es eine "
                   "Bestandsliste?", "Köhler / Justus"),
            ("K2", "Festigkeitsberechnung (AD 2000 / ASME): Wer rechnet, mit welchem Programm, und wo wird das "
                   "Ergebnis abgelegt? Nicht Teil der AA.", "Scharmann"),
            ("K2", "Prüfung und Freigabe der Zeichnungen vor der Verteilung: Läuft das nach AA K2_03? Die AA ist "
                   "nicht als mitgeltend aufgeführt.", "Scharmann / Häfer"),
            ("K2", "Verteilung der Zeichnungen: Auf welchem Weg erhalten Fertigung, Einkauf, PM und Dokumentation die "
                   "Unterlagen, und wie wird sichergestellt, dass alle den aktuellen Änderungsstand haben?",
                   "Scharmann, Justus"),
            ("K2", "Kundenfreigabe von Zeichnungen (Zeichnungen zur Genehmigung): Wer schickt sie, wie wird die "
                   "Freigabe nachgehalten?", "Scharmann / PM"),
            ("K2", "Welches CAD-System wird genutzt, wo werden Zeichnungen abgelegt, und wie wird die "
                   "Zeichnungsnummer vergeben (AA F4.6_02 Nummernschlüssel?)", "Scharmann"),
            ("K2", "HETA-Typennummer: Nach welcher Systematik wird sie vergeben und wo ist sie hinterlegt?",
                   "Scharmann"),
            ("K2", "Kundenspezifikationen (BASF-Werksnorm, Thyssen Krupp/UHDE u.a.): Wo liegen sie, und wer hält sie "
                   "aktuell?", "Scharmann / Häfer"),
            ("K2", "Werden Konstruktionsstunden auf die Kommission gebucht (für die Nachkalkulation)?",
                   "Scharmann / Brühl"),
        ],
    )),
]

ERGAENZUNGEN.append((3, dict(
    titel="Schnittstellen aus den ausgewerteten Arbeitsanweisungen (29.09.2026)",
    # (von, nach, was wird übergeben, weg, problem, notiz, (prozess, schritt-nr) oder None)
    verbindungen=[
        ("K1.05", "K3.1", "Angebot (Angebotsliste im Dashboard, Angebotsordner) als Basis der Auftragserfassung",
         "dashboard", False, "Laut AA K3.1_01 Schritt 4/5", ("K3.1", 4)),
        ("K1.05", "U4", "Sanktionslistenprüfung bei Neukunden", "unklar", False,
         "Laut AA K1_05; wer prüft und wo dokumentiert wird, ist offen", ("K1.05", 1)),
        ("K3.1", "U4", "Sanktionslistenprüfung bei neuem Debitor", "unklar", False,
         "Laut AA K3.1_01", ("K3.1", 2)),
        ("K3.1", "K2", "Auftragsbestätigung (Rundmail an alle)", "email", False,
         "Praxisangabe P. Schreiber: Rundmail mit AB; ob Konstruktion ausdrücklich beauftragt wird, ist offen",
         ("K3.1", 7)),
        ("K3.1", "U1.1", "Auftragsbestätigung (Rundmail an alle)", "email", False,
         "Praxisangabe P. Schreiber: Rundmail mit AB", ("K3.1", 7)),
        ("K3.1", "K3.3", "Auftragsbestätigung (Rundmail an alle)", "email", False,
         "Praxisangabe P. Schreiber: Rundmail mit AB", ("K3.1", 7)),
        ("K2", "U1.1", "Bestelltexte / Materialauswahl, Info bei Zeichnungsänderungen", "unklar", True,
         "Laut AA K2_01. Ob eine Stückliste übergeben wird und in welcher Form, ist ungeklärt.", ("K2", 4)),
        ("K2", "K3.3", "Freigegebene Zeichnungsunterlagen", "unklar", False,
         "Laut AA K2_01 Schritt 7; Weg der Verteilung offen", ("K2", 7)),
        ("K3.3", "K2", "Schweißtechnische Abstimmung (Schweißverfahren, Zusatz)", "muendlich", False,
         "Laut AA K2_01 Schritt 2 (Schweißaufsicht); Weg angenommen", ("K2", 2)),
    ],
)))

AA_BEST = "Laut AA U1.1_01 Rev. 2 – Praxisabgleich offen"
AA_WE = "Laut AA U1.4_02 Rev. 4 – Praxisabgleich offen"
AA_LAG = "Laut AA K3.3.11-05 Rev. 1 – Praxisabgleich offen"
EK = "Einkauf Werk 4 (Köhler, Hamp)"
WE = "Wareneingang: MA Fertigung Werk 4 (Person offen)"
LAGER = "Lager, Bestandsführung und Inventur"

ERGAENZUNGEN.append((4, dict(
    titel="AA U1.1_01 Bestellung, U1.4_02 Wareneingang, K3.3.11-05 Lagerwesen ausgewertet (30.09.2026)",
    # Lagerprozess unter U (wie in der Prozessliste vorgeschlagen); ist er schon von Hand angelegt,
    # wird er über die Bezeichnung gefunden und nicht doppelt angelegt.
    landkarte=[(None, LAGER, "U", "vorgeschlagen")],
    details={
        "U1.1": dict(
            verantwortlich="Einkauf Werk 4",
            beteiligte="Geschäftsleitung, PM, Konstruktion (technische Prüfung), Fertigungsleiter/Schweißaufsicht",
            ausloeser="Kundenauftrag mit HETA-AB und freigegebene Zeichnungen/Stücklisten",
            ergebnis="Unterschriebene Bestellung beim Lieferanten, erfasst in Dashboard und MDL; nach Lieferung "
                     "Lieferschein und Rechnungswert in der Dashboard-Bestellliste",
            systeme="Material-Deadline-Liste (MDL, Excel), Dashboard (Bestellliste, Bestellnummer), Bestellvorlage, "
                    "DATEV (Rechnungsprüfung/-freigabe)",
            variante="Teile für Druckbehälter · Schweißzusatz (Zeugnis 3.1) · Gefahrstoffe (Sicherheitsdatenblatt)",
        ),
        "U1.4": dict(
            verantwortlich="Fertigungsleiter Werk 4",
            beteiligte="MA Fertigung, Einkauf, PM/Dokumentation, Konstruktion",
            ausloeser="Anlieferung (Spedition, Paketdienst) mit Lieferschein",
            ergebnis="Ware geprüft und freigegeben (oder gesperrt), der Kommission zugeordnet bzw. eingelagert; "
                     "bearbeiteter Lieferschein im blauen Ablagekasten für den Einkauf",
            systeme="Wareneingangsstempel, Lieferschein (Scan + Kopie), Ordner WE, Ablagekästen rot/blau, "
                    "Liste Lagerbestandsführung, Umstempelbescheinigung, Sperrzettel, Mängelbericht",
        ),
        LAGER: dict(
            verantwortlich="Justus, Köhler, Häfer (verwalten die Lagerbestandsliste)",
            beteiligte="Alle MA Fertigung Werk 4, Einkauf",
            ausloeser="Zugang von Lagermaterial (Wareneingang) oder Entnahme für einen Auftrag",
            ergebnis="Aktuelle Lagerbestandsliste; Einkauf erkennt Nachbestellbedarf",
            systeme=r"Excel-Liste K:\02 Lager\Lagerbestand (FB_K3.3.11-26), Aufkleber/Kennzeichnung, formloser Zettel",
            variante="Nur Rohre, Flansche, Stangenmaterial (Rund, Flach, Winkel)",
        ),
    },
    status={"U1.1": "laut_aa", "U1.4": "laut_aa", LAGER: "laut_aa"},
    dokumente=[
        ("AA_F4_01", "", "Steuerung von Nichtkonformitäten", "Werk4", "F", "nicht_gesichtet"),
        ("AA_U2.3_01", "", "Umgang Gefahrstoffe", "", "U2", "nicht_gesichtet"),
    ],
    dokument_prozess={"AA_K3.3.11-05": LAGER},
    dokument_status={"AA_U1.1_01": "uebernommen", "AA_U1.4_02": "uebernommen", "AA_K3.3.11-05": "uebernommen"},
    schritte=[
        ["U1.1", 1, "Voraussetzungen prüfen: Kundenauftrag und HETA-AB liegen vor, Zeichnungen und Stücklisten sind "
         "von der Konstruktion erstellt und freigegeben", EK, "AB, freigegebene Zeichnungen und Stücklisten", "",
         "Bestellung kann vorbereitet werden", "", "", "", "", "", AA_BEST],
        ["U1.1", 2, "Material-Deadline-Liste (MDL) aus den Stücklisten erzeugen: alle zu bestellenden Teile des "
         "Druckbehälters mit Daten zur Nachverfolgung", EK + " (Person offen)", "Stücklisten", "Excel (MDL)",
         "MDL – Bestellstatus für alle Abteilungen sichtbar", "alle Abteilungen (Ablage offen)", "",
         "Übertrag Stückliste → MDL von Hand? (siehe Offene Fragen)", "", "", AA_BEST],
        ["U1.1", 3, "Mindestens ein schriftliches Lieferantenangebot einholen (Ausnahme: langjährige Lieferanten/"
         "Rahmenvertrag, z.B. TÜV Hessen, Ingenieurbüro Hardt)", EK, "MDL / Stückliste", "E-Mail?",
         "Lieferantenangebot", "", "", "", "", "", AA_BEST],
        ["U1.1", 4, "Angebot technisch und kommerziell prüfen", EK, "Lieferantenangebot, Zeichnung", "",
         "Geprüftes Angebot", "", "", "", "", "", AA_BEST],
        ["U1.1", 5, "Bestellung auf Vorlage erstellen; immer Art der Prüfbescheinigung nach DIN EN 10204 angeben "
         "(Schweißzusatz: 3.1; Gefahrstoffe: Sicherheitsdatenblätter anfordern, AA U2.3_01)", EK,
         "Geprüftes Angebot", "Bestellvorlage (PB U1.1)", "Bestellentwurf", "", "", "", "", "", AA_BEST],
        ["U1.1", 6, "Bestellung technisch prüfen und parafieren", "Konstruktion oder dafür Verantwortliche:r",
         "Bestellentwurf, Zeichnung", "", "Technisch freigegebene Bestellung", "", "Konstruktion",
         "", "", "", AA_BEST],
        ["U1.1", 7, "Bestellung nach Unterschriftenregelung unterschreiben (= Freigabe) und an Lieferanten senden",
         "Unterschriftsberechtigte (lt. Regelung)", "Technisch geprüfte Bestellung", "E-Mail? (Versandweg offen)",
         "Bestellung beim Lieferanten", "Lieferant", "Unterschriftenregelung", "", "", "", AA_BEST],
        ["U1.1", 8, "Bestellnummer = nächste laufende Nummer im Dashboard (je Kommission); Bestelldaten im Dashboard "
         "ergänzen; Bestell-Nr. mit Datum und Lieferant in der MDL eintragen", EK, "Bestellung",
         "Dashboard (Bestellliste), MDL", "Bestellung in Dashboard und MDL erfasst", "", "",
         "Gleiche Daten in Dashboard und MDL", "", "", AA_BEST],
        ["U1.1", 9, "Nach dem Wareneingang: Original-Lieferscheine aus dem blauen Ablagekasten in der "
         "Dashboard-Bestellliste erfassen (Lieferdatum, gelieferte Positionen, Wert bei Teillieferung, Freigabedatum)",
         EK, "Bearbeitete Lieferscheine (blauer Kasten)", "Dashboard (Bestellliste)", "Lieferung erfasst", "", "",
         "", "", "", AA_BEST],
        ["U1.1", 10, "Rechnung über DATEV erhalten, dort prüfen und freigeben; Rechnungswert in die "
         "Dashboard-Bestellliste eintragen", EK + ", Buchhaltung", "Lieferantenrechnung", "DATEV, Dashboard",
         "Rechnung freigegeben, Wert im Dashboard", "Buchhaltung", "", "", "", "", AA_BEST],

        ["U1.4", 1, "Ware annehmen (Tor Straßenseite); Lieferschein auf Bestell- und/oder Kommissionsnummer prüfen",
         WE, "Lieferung mit Lieferschein", "", "Ware angenommen", "Einkauf, falls Nummern fehlen", "",
         "Keine Bestell-/Kommissions-Nr.: Einkauf klärt mit dem Lieferanten", "", "", AA_WE],
        ["U1.4", 2, "Sichtkontrolle von Verpackung und Ware", WE, "Lieferung", "", "Ware unbeschädigt/vollständig",
         "Einkauf bei Schaden oder Fehlmenge", "", "Beschädigt/unvollständig: Einkauf informieren (Reklamation)",
         "", "", AA_WE],
        ["U1.4", 3, "Lieferschein stempeln (Datum + Wareneingangsstempel, Unterschrift Annehmer), scannen und "
         "kopieren (1x an die Ware, 1x in Ordner WE), Original in roten Ablagekasten (= unbearbeitet)", WE,
         "Lieferschein", "WE-Stempel, Scanner, Ordner WE, roter Kasten", "Lieferschein erfasst", "", "", "", "",
         "", AA_WE],
        ["U1.4", 4, "Ware prüfen (spätestens 1 Arbeitstag nach Annahme): alle Positionen vollständig, Maßkontrolle "
         "nach Zeichnung, Schmelze Lieferschein = Material, Kennzeichnung = Zeugnis, ggf. Umstempeln mit "
         "Umstempelbescheinigung, PMI bei Kundenforderung; Ergebnis im WE-Stempel eintragen",
         WE, "Ware, Lieferschein, Zeichnung, Zeugnis, Bestellung", "WE-Stempel, FB_K3.3.11-04 Umstempelbescheinigung",
         "Prüfergebnis", "PM bei fehlendem Zeugnis / fehlender Schmelze", "",
         "Keine Schmelzangabe: Rücksprache PM", "", "max. 1 Arbeitstag", AA_WE],
        ["U1.4", 5, "Bei negativer Prüfung: Ware sperren nach AA F4_01 Steuerung von Nichtkonformitäten "
         "(Sperrzettel, Mängelbericht)", WE, "Negatives Prüfergebnis", "FB_U1.4.1_02 Sperrzettel, FB_U1.4.1_01 "
         "Mängelbericht", "Ware gesperrt", "Einkauf / QM (offen)", "", "", "", "", AA_WE],
        ["U1.4", 6, "Freigegebene Ware der Kommission zuordnen (A4-Blatt mit 4-stelliger Auftragsnummer an Palette/"
         "Karton), bereitstellen für interne/externe Bearbeitung, bei Handelsware umpacken/etikettieren",
         WE, "Freigegebene Ware", "A4-Blatt", "Ware der Kommission zugeordnet", "Fertigung / Versand", "", "",
         "", "", AA_WE],
        ["U1.4", 7, "Lagermaterial (Rohre, Standardflansche DIN, Stangenmaterial) in Liste Lagerbestandsführung "
         "erfassen, mit Schmelze und Werkstoff kennzeichnen und einlagern", WE,
         "Freigegebenes Lagermaterial", r"Excel-Liste Lagerbestand (K:\02 Lager), FB_K3.3.11-26",
         "Lagerzugang erfasst", LAGER, "", "", "", "", AA_WE],
        ["U1.4", 8, "Original-Lieferschein: Qualitätskontrolle im WE-Stempel ausfüllen (freigegeben, Datum, Kürzel, "
         "Unterschrift), scannen, in blauen Ablagekasten (= bearbeitet)", WE, "Geprüfte Ware", "WE-Stempel, "
         "Scanner, blauer Kasten", "Lieferschein bearbeitet", "Einkauf (blauer Kasten)", "", "", "", "", AA_WE],

        [LAGER, 1, "Zugang: Material, das zusätzlich zur Kommission für Lager bestellt wurde (Rohre, Flansche, "
         "Stangenmaterial), beim Wareneingang als Neuzugang in der Lagerbestandsliste erfassen",
         "Justus, Köhler, Häfer (lt. AA), in der Praxis Wareneingang?", "Freigegebenes Lagermaterial",
         r"Excel K:\02 Lager\Lagerbestand (FB_K3.3.11-26)", "Neuzugang in der Liste", "", "", "", "", "", AA_LAG],
        [LAGER, 2, "Material mit Schmelze und Werkstoffnummer kennzeichnen (ggf. Aufkleber) und an den Lagerort "
         "bringen", "MA Fertigung", "Lagermaterial", "Aufkleber", "Gekennzeichnetes Material am Lagerort", "", "",
         "", "", "", AA_LAG],
        [LAGER, 3, "Entnahme für einen Auftrag nur durch autorisierte MA; entnommene Menge/Länge mit Datum in der "
         "Liste austragen – dadurch sieht der Einkauf, wann nachbestellt werden muss",
         "Justus, Köhler, Häfer", "Materialbedarf eines Auftrags", r"Excel K:\02 Lager\Lagerbestand",
         "Bestand aktualisiert", "Einkauf (Nachbestellbedarf über die Liste)", "", "", "", "", AA_LAG],
        [LAGER, 4, "Ausnahme bei akutem Bedarf in der Fertigung: Fertigungs-MA entnimmt selbst, notiert Abmessung, "
         "Schmelze, Werkstoff auf einem formlosen Zettel und gibt ihn einer zuständigen Person zum Austragen",
         "MA Fertigung → Justus/Köhler/Häfer", "Akuter Materialbedarf", "Formloser Zettel, Excel-Liste",
         "Bestand (verzögert) aktualisiert", "zuständige Person (Zettel)", "", "Zettel geht verloren → Bestand falsch?",
         "", "bis Zettel übertragen ist", AA_LAG],
    ],
    fragen=[
        ("U1.1", "Wird vor einer Bestellung auf Kommission geprüft, ob das Material am Lager ist? Die AA Bestellung "
                 "sieht keinen solchen Schritt vor; die Lagerliste dient laut AA Lagerwesen nur dazu, Nachbestellbedarf "
                 "zu erkennen.", "Köhler / Justus"),
        ("U1.1", "MDL: Wer erstellt sie, wird die Stückliste von Hand übertragen, und wo liegt sie für alle "
                 "Abteilungen?", "Köhler / Hamp"),
        ("U1.1", "Bestellnummer, Bestelldaten, Lieferscheine und Rechnungswert werden in Dashboard UND MDL (und "
                 "DATEV) geführt – welche Liste ist führend, und wo wird doppelt eingetragen?", "Köhler / Brühl"),
        ("U1.1", "Unterschriftenregelung für Bestellungen: Wer darf bis zu welchem Wert unterschreiben?",
                 "Hensel / Köhler"),
        ("U1.1", "Auf welchem Weg geht die Bestellung an den Lieferanten, und wird dessen Auftragsbestätigung "
                 "(Liefertermin) irgendwo erfasst und überwacht?", "Köhler"),
        ("U1.4", "Woher weiß der Wareneingang, was bestellt wurde (Bestellpositionen für die Vollständigkeitsprüfung) – "
                 "Ausdruck der Bestellung, Dashboard, MDL?", "Justus / Köhler"),
        ("U1.4", "Wer ist „Fertigungsleiter Werk 4“ (verantwortlich laut AA) und wer nimmt die Ware in der Praxis an?",
                 "Justus / Scharmann"),
        ("U1.4", "Zeugnisse: Wie kommen die Werkstoffzeugnisse vom Lieferanten zu PM/Dokumentation und werden der "
                 "Kommission zugeordnet?", "Hamp / Häfer"),
        ("U1.4", "Wird die Frist „max. 1 Arbeitstag zwischen Annahme und Prüfung“ eingehalten bzw. nachgehalten?",
                 "Justus"),
        (LAGER, "Lagerwesen nennt die Liste „Lagerbestand“, Wareneingang „Lagerbestandsführung“ (beide "
                "FB_K3.3.11-26) – ist das dieselbe Excel-Liste?", "Häfer"),
        (LAGER, "Nur Rohre, Flansche und Stangenmaterial werden geführt. Gibt es weitere Lagerartikel (Normteile, "
                "Dichtungen, Schweißzusatz, Standard-/Ersatzteile) ohne Bestandsführung?", "Justus / Köhler"),
        (LAGER, "Gibt es Mindestbestände, und wer schaut regelmäßig in die Liste, um nachzubestellen?", "Köhler"),
        (LAGER, "Wird Lagermaterial für eine Kommission reserviert, bevor es entnommen wird?", "Justus"),
        (LAGER, "Wie oft kommt die Entnahme per Zettel vor, und wie genau ist die Liste im Vergleich zum tatsächlichen "
                "Bestand (Inventur)?", "Justus / Häfer"),
        ("F", "AA F4_01 „Steuerung von Nichtkonformitäten“ und AA U2.3_01 „Umgang Gefahrstoffe“ werden als "
              "mitgeltend genannt, fehlen aber in der Dateiliste der Arbeitsanweisungen – wo liegen sie?", "Häfer"),
    ],
    verbindungen=[
        ("K2", "U1.1", "Freigegebene Zeichnungen und Stücklisten (Voraussetzung jeder Bestellung)", "unklar", False,
         "Laut AA U1.1_01", ("U1.1", 1)),
        ("U1.1", "K2", "Bestellung zur technischen Prüfung und Paraphe", "unklar", False,
         "Laut AA U1.1_01 Schritt 6", ("U1.1", 6)),
        ("U1.1", "U1.4", "Bestelldaten für die Prüfung auf Vollständigkeit", "unklar", True,
         "Wie der Wareneingang die Bestellpositionen kennt, ist offen", ("U1.4", 4)),
        ("U1.4", "U1.1", "Bearbeitete Original-Lieferscheine (blauer Ablagekasten)", "papier", False,
         "Laut AA U1.4_02 / U1.1_01", ("U1.4", 8)),
        ("U1.4", "U1.1", "Meldung bei Schaden oder Fehlmenge (Reklamation beim Lieferanten)", "unklar", False,
         "Laut AA U1.4_02", ("U1.4", 2)),
        ("K2", "U1.4", "Zeichnungen für die Maßkontrolle", "unklar", False, "Laut AA U1.4_02 Schritt 4", ("U1.4", 4)),
        ("U1.4", "K3.3", "Freigegebene Ware, der Kommission zugeordnet (A4-Blatt an Palette/Karton)", "papier", False,
         "Laut AA U1.4_02", ("U1.4", 6)),
        ("U1.4", LAGER, "Lagermaterial: Zugang in der Lagerbestandsliste", "ordner", False,
         r"Excel-Liste K:\02 Lager\Lagerbestand", ("U1.4", 7)),
        (LAGER, "U1.1", "Lagerbestandsliste – Nachbestellbedarf", "ordner", True,
         "Einkauf erkennt Bedarf nur durch Blick in die Liste; keine Prüfung je Bestellung beschrieben", None),
        ("K3.3", LAGER, "Entnahmezettel bei akutem Materialbedarf", "papier", True,
         "Laut AA K3.3.11-05: formloser Zettel", (LAGER, 4)),
    ],
)))

# Aktueller Stand = höchste Ergänzungsnummer (Startbestand oben = 1)
STARTBESTAND_VERSION = max([1] + [v for v, _ in ERGAENZUNGEN])


def alle_schritte():
    """Startbestand + alle Ergänzungen (für den CSV-Export)."""
    return SCHRITTE + [s for _, e in ERGAENZUNGEN for s in e.get("schritte", [])]


def alle_fragen():
    return FRAGEN + [f for _, e in ERGAENZUNGEN for f in e.get("fragen", [])]


def alle_dokumente():
    """Dokumentenliste mit dem Auswertungsstatus nach allen Ergänzungen."""
    status, prozess, liste = {}, {}, list(DOKUMENTE)
    for _, e in ERGAENZUNGEN:
        liste += e.get("dokumente", [])
        status.update(e.get("dokument_status", {}))
        prozess.update(e.get("dokument_prozess", {}))
    return [(n, r, t, g, prozess.get(n, p), status.get(n, s)) for n, r, t, g, p, s in liste]
