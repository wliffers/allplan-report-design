# Projektlisten: Pläne, Teilbilder, Projekt, Bauwerksstruktur

Reports, deren Abfrage nicht auf Bauteile geht, sondern auf Tabellen des Projekts. Belegstufen wie in `grenzen.md`: **A** = in Allplan 2027 ausgegeben, **V** = Vorbild in Allplans Vorlagen
(deutsch im Ordner „Verwaltung“, englisch „Administration“; die englischen Dateien haben dieselben Abfragen und Zeilennummern).

## Was geht (A)

- Eine Projekttabelle als ERSTE Abfrage liefert Zeilen und wird als PDF und DOCX normal ausgegeben (18 Proben).
- Die Ausgabe als XLSX öffnet statt einer Datei das Report-Fenster („Report“): PDF oder DOCX nehmen.
- Ohne Zeilen und ohne Datei blieben `LAYOUT_HISTORY` allein, `ATTRIBUTES` und `FILESET` mit `WHERE @1155@.eq."Item"`; Allplan meldet dann das Fenster „keine Bauteile gefunden“ (`fallen.md`).
- Ein Report auf einer Projekttabelle hat keine Bauteildaten: Allplan füllt nur das ERSTE DataSet (`grenzen.md`, harte Grenzen). Bauteile und Projektdaten im selben Report:
  Projektattribute als Spalten der Modellabfrage (`daten.md`).
- `LAYOUT` plus `LAYOUT_DRAWINGS` als zweites `SELECT` im selben `<CommandText>` geht: eine Zeile je Plan und Teilbild, die Plan-Spalten stehen auf jeder dieser Zeilen; ein Plan ohne Teilbild ist eine Zeile mit leeren
  Teilbild-Spalten; ein Teilbild, das zweimal auf einem Plan liegt, ergibt zwei gleiche Zeilen. Im Report: `First()` im Plan-Bereich, `CountDistinct(Plannummer)` für die Zahl der Pläne.
- Der Teilbildname kommt mit Leerzeichen auf 70 Zeichen aufgefüllt: `Trim`.
- `Baugruppe=2` an `LAYOUT` ändert nichts, was sich messen ließe.

## Welche Tabelle was liefert

| Tabelle | Inhalt | Im Test (A) | Spalten (V) |
|---|---|---|---|
| `LAYOUT` | Pläne | 22 Zeilen in allen Proben; gefüllt: Plannummer, Erstellungs- und Änderungsdatum, Dateigröße, Eigentümer, Breite und Höhe (in Millimetern, 1189 × 841 usw.); Name bei 12 von 22; leer bei allen: Ersteller, Planstruktur, Plantyp, Planformat, Maßstab, Prüfer, Freigabedatum | `@446@` Plannummer, `@445@` Planname, `@432@` Erstellungsdatum, `@481@` Ersteller, `@436@` Dateigröße, `@743@` Planstruktur, `@205@` Vorschau (`GText=HD`) |
| `LAYOUT_DRAWINGS` | Teilbilder je Plan | allein nur 1 Zeile (nicht die Teilbilder aller Pläne); mit `LAYOUT` zusammen 25 Zeilen für 22 Pläne; `@436@` ist hier die Projektgröße, nicht die Teilbildgröße | `@512@` Teilbildnummer, `@425@` Teilbildname, `@448@` Bezugsmaßstab, `@589@` (bei allen derselbe Wert) |
| `LAYOUT_HISTORY` | Indexverlauf je Plan | allein keine Zeile; mit `LAYOUT` zusammen 22 Zeilen, alle Indexspalten leer (kein Plan hat einen Index) | `@389@` Index, `@397@` Index-Datum, `@396@` Index-Ersteller, `@447@` Notiz, `@426@` Typ |
| `DOCUMENT` | Teilbilder des Projekts | Zeilenzahl schwankt je Abfrage: 172 (String), 76 (typisiert, mit `ForeignKey`), 38 (13 Spalten); Teilbilder, die auf Plänen liegen, fehlen; Gliederungscode und ListID bei allen leer; `Properties=512` ohne Wirkung | `@512@` Nummer, `@425@` Name, `@436@` Größe, `@430@` Gliederungscode, `@433@` Änderungsdatum, `@420@` Listennummer |
| `CURRENT_PROJECT` | das offene Projekt | 1 Zeile; Bauherr, Projektleiter, Bauvorhaben, Auftraggeber, Projektstatus sind leer (nicht gesetzt) | `@697@` Projektnummer, `@405@` Projektname, `@431@` Eigentümer, `@432@` Erstellt |
| `PROJECT` | Projektliste | alle Projekte des Rechners (39 Zeilen), „verfügbar“; Zeile 1 ist ein Platzhalter (Projektnummer 0, Name `<        >`) | dazu `@403@` Rechner, `@412@` Pfad, `@368@` Verfügbarkeit, `@449@` Version, `@436@` Größe |
| `BUILDINGSTRUCTURE` | Bauwerksstruktur (`Properties=512`) | 299 Zeilen: Knoten (`Node`) und Teilbilder (`Item`), Reihenfolge wie im Baum (Knoten, danach seine Items); Ebene `@518@` 0 bis 4, ein Item trägt die Ebene seines Elternknotens; bei Items steht in `@409@` der Name des Elternknotens | `@409@` Knotenname, `@1155@` Knotentyp, `@518@` Ebene, `@512@` Dateinummer, `@416@` Dateiname |
| `FILESET` | Zeichnungen (`Properties=512`) | mit `WHERE @1155@.eq."Item"` keine Zeile; ohne `WHERE` nur der Wurzelknoten | `@409@` Name, `@408@` Nummer, `@412@` Pfad, `@512@` Dateinummer, `@433@` geändert, `@432@` erstellt, `@416@` Dateiname |
| `ATTRIBUTES` | Projektattribute | keine Zeile, keine Datei | `@16@` Kenner, `@17@` Wert |

Ob die leeren Spalten an den Daten des Testprojekts oder an der Abfrage liegen, ist nicht gemessen (kein Plan mit gepflegtem Plankopf, keine gesetzten Projektattribute).

## Grenzen der Auswertung

- **`DOCUMENT` ist keine verlässliche Gesamtliste der Teilbilder:** die Zeilenzahl hängt von der Abfrage ab, die Ursache ist offen. Pläne (`LAYOUT`) sind stabil.
- Teilbilder je Gebäude oder Geschoss zählen geht nicht über `@589@`, `@451@`, `@452@`: sie tragen bei allen Teilbildern denselben Zusammenhangswert. Die Zuordnung steht nur in der Reihenfolge von `BUILDINGSTRUCTURE` und im Elternnamen am Item.
- Leere Spalten aushalten: ein Diagramm oder Filter auf eine leere Spalte braucht Ersatzzeile „keine Angabe“ und `<NoRows>`.
- Planvorschau (`@205@` an `LAYOUT`): Bild nur bei 2 von 22 Plänen; die anderen bleiben ohne Bild.
- Zeitwerte: Erstellungs- und Änderungsdatum sind bei allen Plänen gefüllt und tragen ein Diagramm „Pläne je Monat“.
- Klick ins Modell (`@10@`) gibt es nicht: Pläne und Teilbilder sind keine Modellelemente.

## Regeln aus Allplans Vorlagen (V)

- Ein Filter in der Abfrage kommt nur als `WHERE @1155@.eq."Item"` vor; alles andere filtert der Report über einen Parameter (`Prompt` `Distinct(Fields!…)`, Filter `In`).
- Katalogtyp und Typ in der Vorlage weichen ab (Datumsspalten, `@408@`, `@16@`); in Allplan liefen DateTime-, Int32- und Double-Typen an `LAYOUT`.
- Bauwerksstruktur als Baum: Einrückung `Level * TabSize` pt; Anzeige `IIf(NodeType="Node", Nodename, Dateinummer & "  " & Dateiname)`.

Nicht geprüft: Laufzeit bei großen Projekten; `Objectfilter` der Vorlage „Planliste mit Dokumenten“; Drillthrough von der Projektliste zu den Projektdetails im Fenster; `Last(Index_Datum)` (kein Plan hat einen Index); Projektattribute mit Werten.

## Englische Begriffe (V: Allplans deutsche und englische Vorlagen im Vergleich)

| Deutsch | Englisch |
|---|---|
| Planliste mit Dokumenten | Layout list with documents |
| Planübersicht mit Struktur | Layout overview with structure |
| Bauwerksstruktur | Building structure |
| Zeichnungen | Filesets |
| Projektattribute / Projektdetails / Projektübersicht | Project attributes / Project details / Project overview |
| Plan / Plannummer / Planname | Layout / Layout number / Layout name |
| Teilbild / Teilbildnummer / Teilbildname | Drawing file (DF) / Drawing file number / Drawing file name |
| Plan ohne Teilbilder | Layout without drawing files |
| Planstruktur | Layout structure |
| Ersteller / Erstellungsdatum | Created by / Created on |
| Änderungsdatum / Dateigröße (Bytes) | Date of change / File size (bytes) |
| Maßstab / Bezugsmaßstab | Scale / Reference scale |
| Planformat / Plantyp / Planversion | Layout format / Layout type / Layout version |
| Gliederungscode | Hierarchic code |
| Planprüfer / Plan-Freigabedatum | Checked by / Layout release date |
| Index / Index-Datum / letzter Index am | Index / Index date / last index on |
| Eigentümer / Projektname | Owner / Project name |
| Rechner / Projektpfad / Verfügbarkeit | Computer / Project path / Availability |
| Programmversion | Release |
| Knotentyp / Dateiname / Dateinummer | Node_type / File name / File number |
| Attributname / Attributwert | Attribute name / Attribute value |
| Details ein- und ausblenden | Show and hide details |

Allplans Vorlagen übersetzen „Erstellt am:“ falsch als „Created by on:“; „Prüfer“ steht in der Spalte als „Checking eng.“, „Freigabe-Name“ als „Appr. name“: nicht übernehmen.

