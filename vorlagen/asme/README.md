# ASME-Formularvorlagen

Je Ausgabe des QC-Handbuchs ein Ordner (z. B. `Entwurf/`, später `Rev_05/`) mit
den Word-Vorlagen und einer `formulare.json`. Das Tool füllt die Platzhalter
aus den Daten der Lieferantenbestellung (Reiter Aufträge → „Lieferantenbestellungen
& ASME-Dokumente“ → „Dokumente erzeugen“).

`Entwurf/` ist nach Screenshots nachgebaut und **vorläufig**. Sobald die
Word-Originale vorliegen, daraus einen echten Revisionsordner machen.

## Neue Handbuch-Ausgabe einspielen

1. Ordner kopieren, z. B. `Entwurf/` → `Rev_06/`.
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
`werkstoff`, `spezifikation`, `coded_marking` (Vorschlagslisten in den
Eingabemasken). Die Einträge aus den Dropdowns der Original-Bestellvorlage
gehören hierher.
