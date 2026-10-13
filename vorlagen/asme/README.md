# ASME-Formularvorlagen

Je Ausgabe des QC-Handbuchs ein Ordner (aktuell `Original/`, später z. B. `Rev_06/`) mit
den Word-Vorlagen und einer `formulare.json`. Das Tool füllt die Platzhalter
aus den Daten der Lieferantenbestellung (Reiter Aufträge → „Lieferantenbestellungen
& ASME-Dokumente“ → „Dokumente erzeugen“).

`Original/` ist aus den Word-Originalen `DE_Bestellung_ASME.docx` und
`Sample_Form_3_Wareneingangskontrolle.docx` umgebaut (Skript
`_umbau_originale.py`, als Vorlage für künftige Umbauten). Layout, Kopf-/Fußzeilen
und Festtexte sind unverändert; ersetzt wurden nur die Eingabefelder.
Bei der Bestellung stehen „Zahlungsbedingungen“ jetzt direkt unter der
Positionstabelle (statt fest positioniert) und Seite 2 beginnt mit einem echten
Seitenumbruch – so bricht eine lange Positionsliste sauber auf Folgeseiten um.

## Neue Handbuch-Ausgabe einspielen

1. Ordner kopieren, z. B. `Original/` → `Rev_06/`.
2. Word-Originale der neuen Ausgabe hineinlegen und die Platzhalter unten an die
   Stelle der Eingabefelder setzen (Inhaltssteuerelemente/Dropdowns entfernen,
   statt dessen `{{ … }}` schreiben).
3. In `formulare.json` des neuen Ordners `revision` eintragen,
   `"aktuell": true`, `"vorlaeufig": false`; im alten Ordner `"aktuell": false`.
4. Commit + `deploy/update.sh` auf dem Server. Alte Ordner **nicht löschen** –
   damit lassen sich Dokumente alter Aufträge in ihrer damaligen Form nachdrucken
   (Auswahl „Revision“ an der Bestellung).

## Platzhalter

Jinja-Syntax (docxtpl). Typografische Anführungszeichen, die Word beim Tippen
erzeugt, stören nicht.

| Platzhalter | Inhalt |
|---|---|
| `{{ bestell_nr }}` | Bestell-Nr. (V-…) |
| `{{ datum }}` | Bestelldatum (TT.MM.JJJJ) |
| `{{ lieferant }}` | Name und Anschrift des Lieferanten (mehrzeilig) |
| `{{ ihr_angebot }}`, `{{ ihr_sachbearbeiter }}`, `{{ unser_zeichen }}` | Bestellkopf |
| `{{ kommission }}`, `{{ kunde }}` | aus dem Auftrag |
| `{{ bestell_nr_kommission }}` | „V-… / K-…“ für den WE-Kontrollschein |
| `{{ lieferdatum }}`, `{{ versand }}`, `{{ zahlungsbedingungen }}` | |
| `{{ asme_edition }}` | z. B. Sec. VIII Div. 1 Ed. 2025 |
| `{{ coded_marking }}` | |
| `{{ material_art }}` | „Material nach Sec. II Part A“ (Edelstahl, Kohlenstoffstahl …) |
| `{{ spezifikationen }}`, `{{ werkstoffe }}` | alle Werte der Positionen, kommagetrennt |
| `{{ std['B16.5'] }}` | ☒ oder ☐ je Standard aus `auswahl.weitere_standards` |
| `{{ summe_netto }}`, `{{ mwst_satz }}`, `{{ mwst }}`, `{{ summe_brutto }}` | deutsch formatiert, ohne € |
| `{{ form_nr }}`, `{{ revision }}`, `{{ erzeugt_am }}` | aus `formulare.json` bzw. Zeitpunkt |

Positionen (`p.` innerhalb einer Schleife): `p.pos`, `p.menge`, `p.einheit`,
`p.menge_einheit`, `p.bezeichnung`, `p.werkstoff`, `p.spezifikation`,
`p.stueckliste_pos`, `p.preis`, `p.gesamt`.

Schleifen:

- **Tabellenzeile je Position** (Bestellung): eine Zeile nur mit
  `{%tr for p in positionen %}`, darunter die Datenzeile, darunter eine Zeile nur
  mit `{%tr endfor %}`.
- **Seite je Position** (WE-Kontrollschein): Absätze, die jeweils allein stehen:
  `{%p for p in positionen %}` – Formulartabelle – `{%p if not loop.last %}` –
  Seitenumbruch – `{%p endif %}` – `{%p endfor %}`.
- Optionaler Text: `{% if p.werkstoff %}Werkstoff: {{ p.werkstoff }}{% endif %}`.

## Auswahllisten

`auswahl` in `formulare.json`: `weitere_standards` (Ankreuzliste der Bestellung),
`spezifikation`, `material_art`, `coded_marking`, `versand`,
`zahlungsbedingungen` (Vorschlagslisten in den Eingabemasken, übernommen aus den
Dropdowns der Original-Bestellvorlage) und `bauteil` (Schnellwahl-Knöpfe für die
Positionsbezeichnung: Flansch, Blech, Rohr …).
