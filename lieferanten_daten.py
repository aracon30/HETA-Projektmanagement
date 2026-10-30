"""Startbestand für die Lieferantenbewertung (Stufe 1, siehe
docs/KONZEPT-LIEFERANTEN.md): Kriterienkatalog und Grundeinstellungen der
Berechnung. **Wortlaut, Gewichte und Einstellungen 1:1 aus der echten
Lieferantenbewertung_HETA.xlsx übernommen** (Blätter "Kriterien" und
"Einstellungen", Stand 30.10.2026) — damit liefern Tool und Excel-Datei für
dieselben Eingaben dieselben Ergebnisse (Prüfkriterium aus dem Konzept).
Kriterien werden laut Konzept nie gelöscht, nur deaktiviert. Identität eines
Kriteriums ist (ebene, reihenfolge), nicht die Bezeichnung — seed_lieferanten.py
synchronisiert Name/Gewicht/Notentexte vorhandener Zeilen auf diesen Stand,
solange es keine Einstellungs-Oberfläche (Stufe 3) gibt, über die jemand
eigene Anpassungen vornehmen könnte. Ändert sich hier ein Wortlaut, zieht ihn
der nächste `update.sh`-Lauf automatisch nach, ohne doppelte Zeilen oder
verwaiste `bewertung_noten` (die hängen an der stabilen kriterium_id, nicht
am Namen).
"""

# ebene, reihenfolge, bezeichnung, gewicht (%), note1, note2, note3, note4
KRITERIEN = [
    ("lieferung", 1, "Termintreue", 30.0,
     "termingerecht (oder abgestimmt früher)",
     "bis 3 AT Verzug, rechtzeitig angekündigt",
     "4–10 AT Verzug oder Verzug nicht angekündigt",
     "> 10 AT Verzug oder Auftragstermin gefährdet"),
    ("lieferung", 2, "Mengentreue", 15.0,
     "Menge und Positionen vollständig",
     "geringe Abweichung ohne Auswirkung",
     "Teil-/Nachlieferung erforderlich",
     "falsche Ware oder erhebliche Fehlmenge"),
    ("lieferung", 3, "Anlieferqualität (Maß, Werkstoff, Oberfläche, Verpackung)", 35.0,
     "ohne Befund",
     "geringe Mängel, intern ohne Aufwand behebbar",
     "Reklamation oder Nacharbeit erforderlich",
     "Rücksendung/Ausschuss oder sicherheitsrelevanter Mangel"),
    ("lieferung", 4, "Dokumentation & Zeugnisse (z. B. 3.1 nach EN 10204, Kennzeichnung)", 20.0,
     "vollständig und korrekt mit der Lieferung",
     "kleine formale Fehler oder kurzfristig nachgereicht",
     "fehlte, erst nach Anforderung geliefert",
     "fehlend/fehlerhaft – Rückverfolgbarkeit nicht gegeben"),

    ("jahr", 1, "Preisniveau / Preis-Leistung", 20.0,
     "deutlich besser als Wettbewerb",
     "marktüblich",
     "eher teuer, Leistung rechtfertigt es nur teilweise",
     "deutlich zu teuer"),
    ("jahr", 2, "Kommunikation & Erreichbarkeit", 15.0,
     "schnell, proaktiv, feste Ansprechpartner",
     "in der Regel zeitnah",
     "häufig nachhaken nötig",
     "schwer erreichbar, Anfragen bleiben liegen"),
    ("jahr", 3, "Flexibilität (Eilaufträge, Änderungen)", 15.0,
     "Änderungen/Eilaufträge problemlos",
     "meist möglich",
     "nur eingeschränkt möglich",
     "keine Flexibilität"),
    ("jahr", 4, "Reklamationsabwicklung", 15.0,
     "schnell, kulant, Ursachen abgestellt",
     "angemessen",
     "schleppend oder nur teilweise",
     "verweigert bzw. ungelöst"),
    ("jahr", 5, "Technische Kompetenz / Beratung", 10.0,
     "aktive Fachberatung, Lösungsvorschläge",
     "solide Fachkenntnis",
     "nur auf Nachfrage, oberflächlich",
     "keine Unterstützung"),
    ("jahr", 6, "Zertifizierungen & Nachweise (ISO 9001, AD 2000 HP0/DGRL, ASME)", 15.0,
     "alle erforderlichen gültig vorhanden",
     "vorhanden, kleine Lücken",
     "wesentliche Nachweise fehlen/abgelaufen",
     "keine Nachweise"),
    ("jahr", 7, "Nachhaltigkeit & Lieferkette (Umwelt, Verhaltenskodex)", 10.0,
     "zertifiziert/dokumentiert (z. B. ISO 14001)",
     "Grundsätze vorhanden",
     "kaum Angaben",
     "keine Angaben / Verstöße bekannt"),
]

# Rechenregeln — 1:1 aus dem Blatt "Einstellungen" der Excel-Datei.
EINSTELLUNGEN = {
    "notenwert_1": "100",
    "notenwert_2": "70",
    "notenwert_3": "30",
    "notenwert_4": "0",
    "klasse_a_min": "90",
    "klasse_b_min": "75",
    "konsequenz_a": "freigegeben – bevorzugt anfragen",
    "konsequenz_b": "freigegeben – Schwachstellen im Lieferantengespräch ansprechen",
    "konsequenz_c": "Maßnahmenplan erforderlich – ggf. bedingte Freigabe/Sperre, Alternativlieferant prüfen",
    "anteil_lieferung": "0.6",
    "anteil_jahr": "0.4",
    "zertifikat_warn_tage": "90",
}
