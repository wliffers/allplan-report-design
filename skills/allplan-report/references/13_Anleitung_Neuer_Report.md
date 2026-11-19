# Anleitung: Neuen Allplan‑Report erstellen

Diese Schritt‑für‑Schritt‑Anweisung beschreibt das Vorgehen für eine KI oder einen menschlichen Reportdesigner beim Erstellen einer neuen `.rdlc`‑Vorlage. Sie ist so formuliert, dass jeder Schritt ohne weitere Klärung ausführbar ist.

## Schritt 1: Anforderung präzisieren

Vor dem ersten Klick / der ersten XML‑Zeile müssen folgende Fragen beantwortet sein:

| Frage | Mögliche Antworten |
|-------|--------------------|
| **Zielobjekt** | Wand, Decke, Stütze, Raum, Bewehrungsstab, Schacht, Projekt… → daraus folgt `@OBJ@` |
| **Status** | Neubau (`@49@=0`), Abbruch (`@49@=2`), beide |
| **Gewerk‑Einschränkung** | `@GW@.eq.13` (Beton), `@GW@.eq.12` (Mauer), etc. |
| **Spalten** | Welche Attribute? (siehe `05_Attribute_Referenz.md`) |
| **Gruppierung** | Keine / Geschoss / Geschoss + Material / Bauteil + Position |
| **Vorschaubild** | Ja/Nein, welche Projektion, Größe |
| **Blattformat** | A4 hoch / A4 quer / A3 hoch / A3 quer |
| **Länderstandard** | DE/EN/BS/SANS/CH/ISO |
| **Summen / Totals** | Welche Spalten aufsummieren? |
| **Sprache** | Braucht DE und EN parallel? |

Ohne diese Antworten **nicht** starten – die KI fragt den Nutzer konkret nach fehlenden Punkten.

## Schritt 2: Referenzvorlage finden

1. In `01_Dateiuebersicht_und_Kategorien.md` die thematisch nächste Vorlage suchen.
2. Die Referenzdatei in `<RDLC>/` öffnen und **komplett** lesen (nicht nur die Query). Den Ordner einer Datei nennt `RelativePath` in `<SKILL>/rdlc-index.json`.
3. Anmerken, welches Schema die Basis hat – erkennbar am Namespace `<Report xmlns=…>`, nicht am Dateinamen (Default: RDL 2005 mit `<Table>`).
4. Beispiele:
   - „Ein Report über alle Wände mit Öffnungen und Materialgruppe" → Referenz `Wände.rdlc` + `Mauerarbeiten.rdlc`.
   - „Eine Biegeliste für Biegeschlüssel nach DIN" → Referenz `Stabliste ISO 3766.rdlc`.
   - „Pfahlauswertung mit UUID" → Referenz `Bohrpfahlwand.rdlc`.

## Schritt 3: Dateinamen festlegen

- Pro Sprache eine Datei. Schema:
  - Deutsch: `<Sinnhafter Name>.rdlc`
  - Englisch: `<Meaningful Name>.rdlc`
- Keine Versionsnummern, keine Zeitstempel im Namen.
- Unterordner nicht verwenden (Allplan scannt flach).
- Nummerierte Reports nur, wenn Teil der Fertigteil‑Kategorie (040–063, 031–033, 002).

## Schritt 4: Rohgerüst anlegen

Kopie von `Template_empty_2005.rdlc` oder `Template_Grouping1_2005.rdlc` (je nach Gruppentiefe) ins Zielverzeichnis.

```bash
copy "Template_empty_2005.rdlc" "<Mein Report>.rdlc"
```

Im XML:

1. `<rd:ReportID>` neu generieren (neue GUID).
2. `<Author>` setzen.
3. `<Description>` einfügen (optional, hilft Übersicht).
4. `Heading1.Value` in die Titelzeile eintragen.

## Schritt 5: Query aufbauen

Im Element `<DataSets>/<DataSet Name="AllplanReport">/<Query>/<CommandText>`:

```xml
<CommandText>SELECT
  @452@[Name=Story|Fmt=A30],
  @452@[Name=StoryIndex|Fmt=I4],
  @83@[Name=Codetext|Fmt=A30],
  @508@[Name=Material|Fmt=A30],
  @220@[Name=Length|Dim=1|Fmt=F8.2],
  @222@[Name=Height|Dim=1|Fmt=F8.2],
  @201@[Name=Quantity|Fmt=F9.3],
  @205@[Name=Graphics|Projection=9|Hidden=1|Width=35|Height=25|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.and.@49@.eq.0]</CommandText>
```

Regeln:
- Jede Spalte hat `Name=<eindeutig>`.
- `@OBJ@` wählt den Bauteiltyp (siehe `05_Attribute_Referenz.md`).
- Immer `@49@`‑Filter setzen, wenn der Report spezifisch Neubau oder Abbruch sein soll.
- `FROM`-Tabelle aus `04_Allplan_Query_Syntax.md` übernehmen.
- Keine echte SQL‑Syntax (kein `JOIN`, `ORDER BY`, `TOP`).

## Schritt 6: Fields‑Block synchronisieren

Zu jeder `Name=<X>` im Query muss ein `<Field>` im `<Fields>`‑Block stehen:

```xml
<Fields>
  <Field Name="Story"><DataField>Story</DataField><rd:TypeName>System.String</rd:TypeName></Field>
  <Field Name="StoryIndex"><DataField>StoryIndex</DataField><rd:TypeName>System.Int32</rd:TypeName></Field>
  <Field Name="Codetext"><DataField>Codetext</DataField><rd:TypeName>System.String</rd:TypeName></Field>
  <Field Name="Material"><DataField>Material</DataField><rd:TypeName>System.String</rd:TypeName></Field>
  <Field Name="Length"><DataField>Length</DataField><rd:TypeName>System.Double</rd:TypeName></Field>
  <Field Name="Height"><DataField>Height</DataField><rd:TypeName>System.Double</rd:TypeName></Field>
  <Field Name="Quantity"><DataField>Quantity</DataField><rd:TypeName>System.Double</rd:TypeName></Field>
  <Field Name="Graphics"><DataField>Graphics</DataField><rd:TypeName>System.Byte[]</rd:TypeName></Field>
</Fields>
```

Datentypen:
- `System.String` für alphanumerische Attribute (`@507@`, `@508@`, `@83@`, `@498@`, `@452@` wenn `Fmt=A…`)
- `System.Int32` für Integer (`@452@ StoryIndex`, `@215@`, `@206@`, `@767@`)
- `System.Double` für Dezimalwerte (`@201@`, `@220@-@226@`, `@760@`, `@765@`)
- `System.DateTime` nur für Datum
- `System.Byte[]` für `@205@` (Grafiken) – außer bei `@87@` SVG (dann String)
- `System.Object` als Fallback

## Schritt 7: Tabelle aufbauen

Im `<Body>/<ReportItems>` eine `<Table Name="Table1">` platzieren. Siehe `07_Gruppierung_und_Tabellen.md`.

- Jede Spaltenbreite ergibt in Summe die Body‑Breite (abhängig vom Papierformat, siehe `03_Standardparameter_und_Layout.md`).
- Header‑Row mit Label‑Textboxen (`FontWeight=700`, `BorderStyle.Bottom=Solid`).
- Detail‑Row mit `=Fields!<Name>.Value`.
- Optional: Footer‑Row mit `=Sum(Fields!Quantity.Value)`.

Bei Gruppierung: `<TableGroups>`‑Block ergänzen, Group‑Header mit `=Fields!Story.Value`, Group‑Footer mit Summen.

## Schritt 8: Zusatz‑Parameter integrieren

Nach den 12 Standardparametern ergänzen:

```xml
<ReportParameter Name="Display_Graphics">
  <DataType>Boolean</DataType>
  <DefaultValue><Values><Value>True</Value></Values></DefaultValue>
  <AllowBlank>true</AllowBlank>
  <Prompt>Grafik anzeigen</Prompt>
</ReportParameter>
```

Verwendung im Body:
```xml
<Visibility><Hidden>=Parameters!Display_Graphics.Value=false</Hidden></Visibility>
```

## Schritt 9: Page‑Header/Footer prüfen

Nichts ändern – die Standardblöcke aus Template übernehmen. Lediglich:
- `Heading1.Value` an den Report‑Titel anpassen (fester String).
- Bei A3/Querformat die Breiten (`Width` der Logo‑Rectangle, `Width` der Lines, `Left` der Note/Date/Project) neu berechnen.

## Schritt 10: Sprach‑Parallele anlegen

Wenn DE+EN benötigt:
1. Datei kopieren, englischer Name.
2. Alle Labels in Header/Footer/Table übersetzen.
3. Query unverändert lassen (ist sprachfrei).
4. `Heading1.Value` übersetzen.
5. Parameter‑`Prompt>@XXX@</Prompt>` unverändert lassen – Allplan lokalisiert automatisch.

## Schritt 11: Testen im Allplan‑Report‑Manager (Report‑Gate Stufe R2)

Vorher Stufe R1: `python <SKILL>/scripts/validate_rdlc.py out/<Datei>` – 0 Fehler.

1. Datei in den Büro‑Bereich kopieren: `C:\allplandaten\2027\Std\Reports\deu\<Kategorie>\` (Allplan 2027, Pfad aus `AllplanPaths.GetStdPath()`; bei anderem Datenpfad entsprechend).
2. Im Report‑Manager öffnen.
3. Parameterdialog öffnen: erscheinen alle Felder wie erwartet?
4. Report ausführen auf einem Testprojekt. Plausibilitätsprüfung:
   - Anzahl Datensätze passt?
   - Summen passen?
   - Bilder werden gerendert?
   - Umlaute korrekt?
   - Seitenzahlen korrekt?

## Schritt 12: Review mit Checkliste

`python <SKILL>/scripts/validate_rdlc.py <Datei>` ausführen und die Befunde über ihre Kennung in `14_Qualitaet_und_typische_Fehler.md`, §3 einordnen; danach die dortige Checkliste für alles durchgehen, was das Skript nicht sieht.

## Schritt 13: Deployment

Ablagen in Allplan 2027 (gelesen aus `NemAll_Python_AllplanSettings.AllplanPaths` am 2026-09-29):

| Bereich | Pfad | Hinweis |
|---------|------|---------|
| Standard | `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports\deu\<Kategorie>\` | Allplan‑Auslieferung – **nie** hineinschreiben |
| Büro | `C:\allplandaten\2027\Std\Reports\deu\<Kategorie>\` | `GetStdPath()` + `Reports`; existiert |
| Projekt | `C:\allplandaten\2027\Prj\<Projekt>.prj\Reports\` | `GetCurPrjPath()` + `Reports`; Ordner bei Bedarf anlegen – aus dem Büromuster abgeleitet, in Allplan noch nicht bestätigt |
| Privat | `%USERPROFILE%\Documents\Nemetschek\Allplan\2027\Usr\Local\Reports\` | `GetUsrPath()` + `Reports`; ebenso abgeleitet |

Die älteren Pfade `…\std\rep\`, `…\prj\<ID>\rep\`, `…\usr\rep\` gelten für 2027 nicht mehr.

## Schritt 14: Dokumentieren

Wenn der Report an andere Nutzer weitergegeben wird, mindestens:
- Zweck (1 Satz)
- Voraussetzungen (welche Attribute müssen am Modell befüllt sein?)
- Parameter (welche Werte erwartet werden)
- Bekannte Einschränkungen

Diese Notes gehen in eine Begleit‑Markdown‑Datei neben den Report, nicht in den Report selbst.

## Häufige „Abkürzungen" – wann sie sicher sind

| Situation | Abkürzung | Sicher? |
|-----------|-----------|---------|
| Neuer Raum‑Report | Kopie von `Raumbuch.rdlc` | ✅ |
| Neuer Wand‑Report | Kopie von `Wände.rdlc` | ✅ |
| Neuer Abbruch‑Report aus Neubau | Nur `@49@`‑Filter umdrehen | ✅ |
| Neue Biegeliste | Kopie von `Stabliste ISO 3766.rdlc` | ✅ |
| Neuer PythonPart‑Report | Kopie von `Bohrpfahlwand.rdlc` und UUID anpassen | ✅ |
| Report mit anderem Blattformat | Kopie aus 040 (A4) nach 041 (A3)‑Prinzip | ⚠ Layoutmaße anpassen |
| SVG‑Map‑Variante eines Reports | Kopie, `@205@[Image]` durch `@87@[SVG_Map\|Dim=254]` ersetzen | ✅ |
| Excel‑Export‑Variante | Alle Bilder entfernen, Spaltenbreiten glätten, Autor auf `Allplan Schweiz AG` | ⚠ eigenes Testen |

## Don’ts

- **Nie** die 12 Standardparameter umbenennen.
- **Nie** `DataSource Name="DummyDataSource"` ändern.
- **Nie** `DataProvider` von `ALLPLAN` wegbauen.
- **Nie** die `rd:DataSourceID`‑GUID neu erfinden (muss exakt `58c077ef-da67-445a-8cc2-60008c49a79b` bleiben).
- **Nie** `<Tablix>` in einer RDL‑2005‑Datei verwenden (Namespace entscheidet, nicht der Dateiname).
- **Nie** `<Table>` in einer 2016‑`.rdlc` verwenden.
- **Nie** Attributcodes raten – lieber im Referenzreport nachlesen.
- **Nie** JOIN, ORDER BY, TOP oder LIKE in der FROM‑Klausel verwenden – gibt es nicht.
