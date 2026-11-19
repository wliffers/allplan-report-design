# Referenz-Beispiele (Verweise auf Allplans Vorlagen)

Dieses Repo liefert keine Ausschnitte aus Allplans eigenen Vorlagen mit. Die Liste nennt zehn Vorlagen aus der
Allplan-Installation, die je ein Muster besonders klar zeigen. Die Vorlage selbst liegt unter `<RDLC>`
(Standard: `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports`, deutsch im Unterordner `deu\<Kategorie>\`,
die Startvorlagen `Template_*.rdlc` direkt in `<RDLC>`). Die Datei mit der Dateisuche oder über den Katalog finden
(`python "<SKILL>/scripts/build_report_index.py"` baut ihn) und GANZ lesen, bevor ein Muster übernommen wird.

| Beispiel | Vorlage in `<RDLC>` | Was sie zeigt |
|---|---|---|
| Beispiel 1 – Minimalreport | `Template_empty_2005.rdlc` | kleinster möglicher valider Allplan‑Report. Leerer Body, Standard‑Header/‑Footer, eine Spalte im DataSet. |
| Beispiel 2 – Einfache Gruppierung mit Bild | `Template_Grouping1_2005.rdlc` | Einstufig gruppierte Tabelle (Gruppenkopf über alle Spalten) mit 3 Datenspalten, von denen die dritte ein `@205@`‑Vorschaubild ist. |
| Beispiel 3 – Abbruch‑Filter und Multi‑SELECT | `Abbruch Wände.rdlc` | zeigt, wie der `@49@`‑Filter für Abbruch gesetzt wird **und** wie zwei `SELECT`‑Blöcke hintereinander im selben DataSet stehen (Haupt‑Bauteilspalten + Abrechnungs‑Subquery). |
| Beispiel 4 – Bauwerksstruktur mit berechnetem Feld und bedingtem Styling | `Bauwerksstruktur.rdlc` | zeigt selteneres, aber wichtiges Muster |
| Beispiel 5 – Bewehrung mit mehrstufiger Gruppierung | `Stabliste Biegeformen.rdlc` | das typische Bewehrungs‑Muster mit Array‑Attributen (`@798@[Index=N]`), mehrfacher Gruppierung und Biegeform‑Grafik. |
| Beispiel 6 – PythonPart‑Filter mit TypeUUID | `Bohrpfahlwand.rdlc` | zeigt, wie PythonPart‑Objekte über ihre feste Type‑UUID gefiltert werden. |
| Beispiel 7 – Raum‑ und Wohnflächen‑Query | `Wohnflächen.rdlc` | zeigt den WoFlV‑Kernfilter und den Einsatz von `TotalValue=true` für Gesamtkennzahlen. |
| Beispiel 8 – Koordinaten‑Excel‑Export | `Kanal Schachtkoordinaten Excel.rdlc` | zeigt ein Layout, das für Excel‑Export optimiert ist (keine Bilder, feste Spaltenbreiten, einfache Zahlenformate). |
| Beispiel 9 – SVG‑Map statt Raster‑Bild | `Mengen (SVG Map).rdlc` | der einzige Unterschied zur Geschwister‑Vorlage `Mengen (Grafik).rdlc` ist **ein** Attribut. |
| Beispiel 10 – Plankopf‑Stempel als zweiter DataSet | `Stabliste Schweiz.rdlc` | zeigt das `ALLPLANDATA`‑Muster, mit dem ein Report aus dem Plankopf (Stempel) Lieferadresse, Ingenieur usw. zieht. |

## Wie diese Beispiele eingesetzt werden

1. **Wählen:** die fachlich nächstliegende Vorlage aus der Liste.
2. **Lesen:** Query, Fields und den Tabellenteil der Vorlage ansehen.
3. **Anpassen:** nur Attribut-IDs, Filter und Spaltennamen ändern – nie Reihenfolge oder Standard-Rahmen.
4. **Prüfen:** gegen die Checkliste aus `14_Qualitaet_und_typische_Fehler.md`.
