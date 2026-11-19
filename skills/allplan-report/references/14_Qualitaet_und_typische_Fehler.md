# Qualitätssicherung und typische Fehler

## 1. QA‑Checkliste – vor Abgabe jedes neuen/geänderten Reports

### 1.1 XML / Struktur

> Die mit ⚙ markierten Punkte prüft `python <SKILL>/scripts/validate_rdlc.py <datei>` (Kennungen in §3). Der Rest bleibt Handarbeit.

- [ ] ⚙ Datei ist **wohlgeformtes XML** (Parser läuft bis `</Report>` durch).
- [ ] ⚙ Encoding: UTF‑8 **ohne BOM**.
- [ ] ⚙ Root‑Namespace ist 2005, 2010 oder 2016 – er bestimmt das Schema, nicht der Dateiname.
- [ ] ⚙ **Kein `<Tablix>`** in einer 2005‑Datei.
- [ ] ⚙ **Kein `<Table>`/`<Matrix>`** in einer 2010‑/2016‑Datei.
- [ ] ⚙ `<rd:ReportID>` ist eine eigene GUID (Konvention; die Etc‑Vorlagen teilen alle `2cdc5b66-…`).
- [ ] `<Author>` ist gesetzt.
- [ ] `<Description>` optional, aber empfohlen.

### 1.2 DataSource / DataSet

- [ ] Genau eine `<DataSource Name="DummyDataSource">` mit `DataProvider>ALLPLAN`.
- [ ] `<rd:DataSourceID>` = `58c077ef-da67-445a-8cc2-60008c49a79b`.
- [ ] Jedes DataSet hat einen eindeutigen `Name`.
- [ ] DataSet `AllplanReport` existiert (Haupt‑DataSet‑Konvention).
- [ ] `<CommandText>` ist valid Allplan‑Query (FROM‑Klausel, korrekte Filter‑Syntax).
- [ ] `<Fields>` enthält **genau** die Spalten, die im Query als `Name=` benannt wurden.
- [ ] Feldnamen im Fields‑Block sind case‑exakt gleich wie im Query.
- [ ] Datentypen passen zum Attribut (String für `@507@`, Byte[] für `@205@`, Double für `@201@`, etc.).

### 1.3 Parameter

- [ ] Alle 12 Standardparameter sind vorhanden und in der Standard‑Reihenfolge.
- [ ] Zusatzparameter haben korrekte `DataType`, `Prompt`, ggf. `DefaultValue`, `ValidValues`, `MultiValue`.
- [ ] Jeder im Body referenzierte `Parameters!X.Value` ist deklariert.
- [ ] Keine Zirkulärreferenz zwischen Parametern.

### 1.4 Body / Tabellen

- [ ] Jede Tabelle hat `<DataSetName>` gesetzt.
- [ ] Summe der `<TableColumns>/<Width>` ≤ `<Width>` der Tabelle.
- [ ] Spaltenbreiten‑Summe der Tabelle ≤ Body‑`<Width>`.
- [ ] `<Header>/<RepeatOnNewPage>true` ist gesetzt (Spaltenköpfe auf Folgeseiten).
- [ ] `<Details>`‑Row existiert.
- [ ] Group‑Header/‑Footer haben `<Grouping>` mit gültiger `<GroupExpression>`.
- [ ] Alle `Fields!X.Value` im Body existieren im Fields‑Block.

### 1.5 Expressions

- [ ] Expressions beginnen mit `=`.
- [ ] Aggregate (`Sum`, `Count`) **nur** außerhalb Detail‑Row oder in einem Group‑Scope.
- [ ] `IIf`‑Verzweigungen durch `CDec(0)`/`Math.Max` vor Division durch 0 schützen.
- [ ] `&` als `&amp;` escaped, `<` als `&lt;`, `>` als `&gt;`.
- [ ] Datentypen passen – bei Division durch String vorher `CDbl()` casten.
- [ ] Parameter‑Arrays (`MultiValue=true`) nur mit `In`‑Filter oder `Join(…)`.

### 1.6 Layout

- [ ] Body‑`<Width>` = `<PageWidth>` − `<LeftMargin>` − `<RightMargin>`.
- [ ] Header‑Höhe `<PageHeader>/<Height>` = 3.5 cm (Standard).
- [ ] Footer‑Höhe `<PageFooter>/<Height>` = 1.35 cm (Standard).
- [ ] Heading‑Text ausgefüllt (nicht „Titel").
- [ ] Logo‑Bereich auf `Left=14.5cm` (A4) bzw. `Left=35.5cm` (A3 quer) positioniert.

### 1.7 Grafik

- [ ] `@205@`‑Projection und `GText` zum Objekttyp passend (siehe `08_Grafiken_und_Bilder.md`).
- [ ] `Width`/`Height` im sinnvollen Bereich (< 150 mm in Tabellenzellen).
- [ ] `<Image>` referenziert Byte[]‑Feld (`<Source>Database</Source>`) oder externen Pfad (`<Source>External</Source>`).
- [ ] `Company_Logo` über `"file:///" + Parameters!Company_Logo.Value` referenziert.

### 1.8 Sortierung und Gruppierung

- [ ] Geschoss‑Sortierung immer nach `StoryIndex` (numerisch).
- [ ] `Story`‑Name nur zum Anzeigen, nicht zum Sortieren.
- [ ] Mehrere `<Sorting>` für mehrstufige Sortierung innerhalb einer Gruppe.
- [ ] Numerische Gruppierung nutzt `ROUND(Fields!X.Value, n)` bei Toleranz‑Problemen.

### 1.9 Sprach‑Parallele

- [ ] DE‑Report und EN‑Report sind strukturell identisch (gleiche Spalten, gleiche Gruppierung).
- [ ] Nur Überschriften, Labels, Heading1 unterscheiden sich.
- [ ] Query‑Text identisch zwischen beiden Dateien.

### 1.10 Allgemein

- [ ] Keine hardcoded Pfade (`C:\…`, Netzlaufwerke) im Report außer über Parameter.
- [ ] Keine unbenutzten Parameter (sonst sind sie im Dialog sichtbar, verwirren den Nutzer).
- [ ] Keine unbenutzten Felder im Fields‑Block (Query noch mit optimieren).

## 2. Die typischen Fehler

### 2.1 `@XXX@`‑ID verwechselt

- Symptom: Spalte ist leer, keine Fehlermeldung.
- Ursache: `@231@` (Region) mit `@232@` (AreaType) verwechselt; `@767@` (MarkNumber) mit `@795@` (MarkWithIndex); `@220@` (Length) mit `@221@` (Thickness).
- Lösung: Referenzwert in bestehendem Report nachlesen (`05_Attribute_Referenz.md` + echte Datei).

### 2.2 FROM ohne passenden Filter

- Symptom: Report zeigt alle Modellobjekte (tausende Zeilen).
- Ursache: `FROM [Type=0]` ohne `Filter=@OBJ@.eq.…`.
- Lösung: `@OBJ@`‑Filter auf das Zielobjekt ergänzen.

### 2.3 Abbruch‑Report ohne `@49@`‑Filter

- Symptom: Auch Neubauteile erscheinen.
- Ursache: Filter fehlt.
- Lösung: `.and.@49@.eq.2` ergänzen.

### 2.4 Feldname ≠ `Name=` im Query

- Symptom: Rote Box „#Error" in der Zelle.
- Ursache: Umbenennung vergessen in `<Fields>` oder im Body.
- Lösung: Query‑`Name=` und Body‑`Fields!X.Value` auf gleichen String bringen.

### 2.5 Aggregat in Detail‑Row

- Symptom: Summe zeigt nur den Wert der eigenen Zeile statt der Gruppensumme.
- Ursache: `=Sum(…)` ohne Scope steht in einer Detail‑Row – dort bezieht sie sich nur auf die eine Zeile. Kein Ladefehler: 90 Etc‑2027‑Vorlagen nutzen das bewusst.
- Lösung: Gesamt‑ und Zwischensummen in Group‑Footer oder Table‑Footer; in der Detail‑Row nur mit ausdrücklichem Scope (`=Sum(Fields!X.Value, "AllplanReport")`).

### 2.6 Division durch 0

- Symptom: `#Error` in der Zelle.
- Ursache: `=Fields!A.Value / Fields!B.Value` ohne Prüfung auf B=0.
- Lösung: `=IIf(Fields!B.Value = 0, 0, CDec(Fields!A.Value) / CDec(Fields!B.Value))`.

### 2.7 `<Table>` in 2016‑Schema oder `<Tablix>` in 2005

- Symptom: Report lädt nicht, Parser‑Fehler.
- Lösung: Schema prüfen, Elemente ersetzen.

### 2.8 Body‑Breite überschreitet Seite

- Symptom: Spalten werden beschnitten oder umgebrochen.
- Ursache: Summe der Spaltenbreiten > Body‑`<Width>`.
- Lösung: Spalten schmaler oder Format auf A3/quer umstellen.

### 2.9 Keine `RepeatOnNewPage`

- Symptom: Ab Seite 2 fehlen die Spaltenköpfe.
- Lösung: `<Header><RepeatOnNewPage>true</RepeatOnNewPage></Header>`.

### 2.10 String‑Sortierung statt Index

- Symptom: „10.OG" steht vor „2.OG".
- Lösung: Sort‑Expression auf `StoryIndex` (numerisch).

### 2.11 `MultiValue`‑Parameter ohne `<MultiValue>true</MultiValue>`

- Symptom: Nur ein Wert wird gefiltert, obwohl im Dialog mehrere gewählt sind.
- Lösung: `<MultiValue>true</MultiValue>` ergänzen und Filter mit `In` statt `Equal`.

### 2.12 Page‑Logo zeigt rotes X

- Ursache: `Company_Logo` leer oder Pfad falsch.
- Lösung: `Display_Logo` korrekt auswerten; Pfad mit `file:///` präfixen.

### 2.13 Umlaute erscheinen als „?"

- Ursache: Datei wurde in ANSI/ISO‑8859‑1 gespeichert.
- Lösung: UTF‑8 ohne BOM.

### 2.14 Bildspalten doppelt

- Ursache: Mehrfache `@205@`‑Selects ohne eindeutige `Name=`.
- Lösung: Jedem Grafik‑Select einen eigenen Feldnamen geben.

### 2.15 `@49@.eq.2` mit falscher Objekt‑Typen‑Klammerung

- Symptom: Filter greift nicht.
- Ursache: `@OBJ@.eq.991.or.@OBJ@.eq.992.and.@49@.eq.2` – `.and.` bindet stärker als `.or.`.
- Lösung: `(@OBJ@.eq.991.or.@OBJ@.eq.992).and.@49@.eq.2`.

### 2.16 PythonPart‑UUID ohne Anführungszeichen

- Symptom: Filter greift nicht / Syntax‑Fehler.
- Lösung: `@611["0:__Allplan_PythonPart_TypeUUID__"]@.eq."<GUID>"` – beide `"` erhalten.

### 2.17 Ausbau‑Report nur `@OBJ@.eq.65`

- Symptom: Nur allgemeine Ausbauflächen, keine Spezialausbauten (Boden, Decke, Seite).
- Lösung: `FROM [Filter=ELE(@OBJ@;62;63;64;65),Type=0]`.

### 2.18 Fehlende `CountValues=1` bei Gesamtlänge

- Symptom: Gesamtlänge wird pro Zeile repliziert (bei vielen Stäben enorm inflationiert).
- Lösung: `@760@[Name=TotalLength|CountValues=1]`.

### 2.19 Gewerke‑Filter vergessen

- Symptom: Mauer‑Wände erscheinen im Beton‑Report.
- Lösung: `Filter=@GW@.eq.13` bzw. `.eq.12` ergänzen.

### 2.20 Wohnfläche falsch, weil `@233@` nicht gefiltert

- Symptom: Auch „nicht WoFlV‑relevante" Räume in der Summe.
- Lösung: `Filter=@OBJ@.eq.61.and.@233@.lt.1`.

### 2.21 Parameterloser Filter bei Länder‑Standard

- Symptom: BS‑Report zeigt ISO‑Stäbe oder umgekehrt.
- Lösung: Korrekte `ListNr=4875/4879/10783…` je Standard.

### 2.22 Plankopf‑Daten via `ALLPLANDATA` werden nicht gefunden

- Symptom: Lieferadresse leer.
- Ursache: Zweiter DataSet ohne `MergeDataSet=true`.
- Lösung: `FROM [ALLPLANDATA,MergeDataSet=true]` plus passender `WHERE`‑Teil.

### 2.23 Überlappende Textboxen

- Symptom: Text wird überzeichnet.
- Ursache: Gleiche `<Top>`/`<Left>` ohne korrekt verteilte `Z‑Index`.
- Lösung: ZIndex vergeben oder Top anpassen.

### 2.24 `Note`‑Prompt als Pflichtfeld

- Symptom: Parameter‑Dialog verweigert ohne Eingabe das Fortfahren.
- Lösung: `<AllowBlank>true</AllowBlank>` setzen.

### 2.25 RDL‑Version in `<rd:…>`‑Namespace vergessen

- Symptom: Viele Elemente werden vom Parser ignoriert.
- Lösung: `xmlns:rd="http://schemas.microsoft.com/SQLServer/reporting/reportdesigner"` im Root setzen.

### 2.26 Report bleibt im Report‑Manager weiß

- Symptom: Allplan öffnet den Report, zeigt aber nur eine leere, weiße Fläche.
- Ursache: ein RDL‑Element oder eine Query‑Funktion ohne Vorbild im Bestand (belegt an einem Leitungs‑Report, 2026-07: die Kombination `PARENT(@611["…"]@)` mit dem reservierten PythonPart‑Schlüssel).
- Lösung: vor jedem neuen Konstrukt `grep -rl "<Konstrukt>" <RDLC>` – ohne Treffer nicht verwenden. Zählung 2027 (Dateien): `<Sorting>` 231, `<Filters>` 238, `PARENT(` 108, `ToggleImage` 22, `PARENT(@611` 4, `<Description>` 2. Diese Konstrukte sind also belegt; die frühere Liste „ohne Vorbild" galt nur für den damaligen Einzelfall.

### 2.27 Falsche Zahlen durch `Dim=`

- Symptom: Werte um Faktor 1000 zu groß oder zu klein.
- Ursache: `Dim=` an einem Attribut, das schon m bzw. m³ liefert, oder `* 1000` im Ausdruck bei einem Attribut in mm.
- Lösung: Einheit mit `lookup_attribute.py` prüfen; `Dim=` nur setzen, wo das Vorbild es setzt.

## 3. Validator‑Befunde (`validate_rdlc.py`)

Kalibriert an den 551 Vorlagen von Allplan 2027: was dort vorkommt und läuft, ist höchstens eine Warnung. `--bibliothek` lässt die Konventionen für eigene Reports weg. Letzte Ausgabezeile: `AMPEL: GRUEN|ORANGE|ROT | validate_rdlc | …`.

| Kennung | Befund | Wirkung | Fix |
|---------|--------|---------|-----|
| E01 | XML nicht wohlgeformt | Allplan lädt nicht | Parserfehler an der genannten Stelle beheben |
| E02 | Namespace unbekannt | Schema unklar | Namespace aus dem Vorbild übernehmen |
| E03 | `<Tablix>` in 2005 bzw. `<Table>`/`<Matrix>` in 2010/2016 | Report lädt nicht | Element des passenden Schemas verwenden (§2.7) |
| E04 | kein DataSource mit `DataProvider` ALLPLAN | keine Daten | DataSources‑Block aus dem Vorbild |
| E05 | kein DataSet mit `CommandText` | keine Daten | Query ergänzen |
| E06 | `Fields!X` in einem Ausdruck, aber kein `<Field Name="X">` | `#Error` bzw. Report lädt nicht | Feld deklarieren oder Ausdruck korrigieren (§2.4). Bekannter Fall in Allplan 2027: `eng/Nevaris/Quantities (SVG map).rdlc` nutzt `Allright_Comp_ID`, deklariert ist `Allright_Bauteil_ID` |
| E07 | `JOIN`, `ORDER BY`, `TOP` oder `LIKE` in der FROM‑Klausel | Query scheitert | entfernen; Sortierung im RDL‑Teil |
| E08 | UTF‑16/unlesbar, mit `--bom-error` auch BOM | Umlaute kaputt | als UTF‑8 ohne BOM speichern |
| E09 | Parameter‑Vorgabe (`DefaultValue`) ist ein Ausdruck (`=…`) bei Integer, Float oder DateTime | Typfehler, Allplan erzeugt keine Datei (gemessen 2026‑11‑19; 0 Etc‑Vorlagen) | feste Vorgabe; Datum aus `Parameters!Date` (`@401@`), `=Today()` im Ausdruck statt als Vorgabe oder String‑Parameter plus `CDate` |
| E10 | `DataSetReference` in `ValidValues` oder `DefaultValue` eines Parameters | „Parameter nicht angegeben“, keine Datei (0 Etc‑Vorlagen) | feste Liste oder `<Prompt>Distinct(Fields!X.Value)</Prompt>` |
| E11 | Ausdruck in `ValidValues/ParameterValues/ParameterValue/Value` | „Parameter nicht angegeben“, keine Datei | feste Werte; abhängige Liste als Kombi‑Liste „Art\|Typ“ plus `Split` |
| E12 | DateTime‑Vorgabe weder in ISO‑ (`2026-11-19`, auch mit `T00:00:00`) noch in US‑Schreibweise (`11/19/2026`) | Definition ungültig (`DefaultValue`), keine Datei | ISO‑Schreibweise `2026-11-19` |
| E13 | Integer‑/Float‑Parameter ohne Vorgabe, ohne `Nullable`, ohne `@Nr@`‑Prompt (Unterbericht‑ und Drillthrough‑Ziele ausgenommen) | Typfehler, keine Datei | feste Vorgabe oder `<Nullable>true</Nullable>` |
| E14 | `RowSpan` größer 1 in einer Zelle des Tabellenkörpers (Tablix) | `The TablixCell can only span one row`, Report ungültig (kopflos gemessen; in der Matrix‑Ecke erlaubt) | senkrecht verbinden über den `TablixHeader` der äußeren Gruppe |
| E15 | `Subreport` oder Datenregion (Tablix, Table, Matrix, List, Chart) in `PageHeader`/`PageFooter` | Dokument ungültig (`subreports cannot be used in page headers or footers`) | in den Body setzen; im Kopf nur Textboxen und Bilder |
| E16 | konstante Division durch 0 in einem Ausdruck (`=1/0`, `=5 \ 0`) | Report bricht beim Übersetzen ab (BC30542) | Nenner aus Feld oder Variable |
| W01 | UTF‑8 mit BOM | läuft (12 Etc‑Vorlagen) | neu ohne BOM speichern |
| W02 | kein `DummyDataSource` | läuft (26 Etc‑Vorlagen) | für neue Reports Standardname |
| W03 | `rd:DataSourceID` ≠ `58c077ef-…` | läuft (6 Etc‑Vorlagen) | für neue Reports Standard‑GUID |
| W04 | kein DataSet `AllplanReport*` | läuft (141 Etc‑Vorlagen) | für neue Reports `AllplanReport` |
| W05 | Standardparameter fehlen | Kopf/Fuß unvollständig | Block der Ausgangsvorlage übernehmen (`03`) |
| W06 | Body‑ oder Seitenbreite fehlt | Breite ungeprüft | von Hand prüfen |
| W07 | Body breiter als Seite minus Ränder | leere Zwischenseiten beim Druck (57 Etc‑Vorlagen) | Spalten schmaler oder Querformat (§2.8) |
| W08 | Tabelle breiter als Body | Spalten abgeschnitten | Spaltenbreiten anpassen |
| W09 | `RepeatOnNewPage=true` fehlt | Spaltenköpfe fehlen ab Seite 2 | §2.9 |
| W10 | `Sum`/`Count` ohne Scope in einer Detailzeile | summiert nur die eine Zeile (90 Etc‑Vorlagen nutzen das bewusst) | Summe in Gruppen‑/Tabellenfuß (§2.5) |
| W11 | `@205@` nicht `System.Byte[]`, `@87@` nicht `System.String` | Bild/SVG fehlt | Typ korrigieren (§6) |
| W12 | `rd:ReportID` fehlt | – | GUID ergänzen |
| W13 | `rd:ReportID` = Allplan‑Standard‑GUID | läuft | für eigene Reports frische GUID |
| W14 | dieselbe eigene GUID in mehreren geprüften Dateien | Verwechslungsgefahr | je Datei eigene GUID |
| W15 | Sortierung nach `Fields!Story` | „10.OG" vor „2.OG" (§2.10) | nach `StoryIndex` sortieren |
| W16 | Query‑Feld ohne `<Field>` | Spalte wird geliefert, aber nicht genutzt (6 Etc‑Vorlagen) | `<Field>` ergänzen oder Spalte aus der Query nehmen |
| W17 | `Parameters!X` nicht deklariert | geht nur, wenn Allplan den Parameter selbst liefert (27 Stellen in DIN‑277‑Vorlagen: `BS_*`, `Show_*`) | `<ReportParameter>` ergänzen |
| W18 | String‑Parameter mit Ausdrucks‑Vorgabe | Allplan wertet sie nicht aus, der Wert bleibt leer | feste Vorgabe |
| W19 | `<Hyperlink>` mit festem Text ohne Schema (`www.…`) | im PDF entsteht kein Link (Stabliste Schweiz der Etc‑Bibliothek betrifft es) | `https://…` oder `mailto:…` |
| W20 | mehr als eine `<ReportSection>` | alle Seiten bekommen die Größe der ersten Sektion, breitere laufen über | je Seitengröße ein eigener Report |
| W21 | `<RepeatWith>` | wirkungslos, das Element steht nur auf Seite 1 (2 Etc‑Vorlagen) | `RepeatOnNewPage` an der Kopfzeile oder `PageHeader` |
| W22 | Filter `Like` mit `%` im festen Vergleichswert | trifft nichts, der Platzhalter ist `*` | `="*text*"` |
| W23 | `<Subreport>` (Hinweis) | Allplan gibt dem Unterbericht die Zeilen des Hauptreports, seine eigene Abfrage läuft nicht; gefüllt sind nur Felder gleichen Namens | Feldnamen des Hauptreports verwenden; andere Daten oder Bildart: zweiter Report |
| W24 | Unterbericht (Zieldatei im selben Ordner): Felder des Ziels fehlen im Hauptreport | die Felder sind in Allplan leer | Feldnamen des Hauptreports verwenden |
| W25 | Unterbericht (Zieldatei im selben Ordner): Parameter des Ziels ohne `<Prompt>` | Allplan fordert den Unterbericht nicht an | `<Prompt>` an jedem Parameter des Ziels |
| W26 | `BookmarkLink` auf ein `<Bookmark>` (kein `Zoom:`/`Edit:`) | im PDF kein Sprung | Lesezeichen (`DocumentMapLabel`) statt Sprungmarke |
| W27 | `BreakLocation` End an einem Element und Start am direkt folgenden | LEERE Seite dazwischen | nur eines von beiden setzen |
| W28 | Geschwister-Elemente desselben Containers (Body, Rectangle, Seitenkopf/‑fuß) überlappen sich um mehr als 0,01 cm in X und Y (Linien nur, wenn sie durch die Fläche laufen). Meldung nennt beide Namen, Container und Maß, größte Fläche zuerst; „Streifen“ = kleineres Maß ≤ 0,05 cm, „Überlappung“ = mehr. Ausgenommen: Paare, bei denen beide Elemente zu Allplans Standard‑Kopf/‑Fuß gehören (`Footer1`–`Footer3`, `Line6`, `PageNumber`; `Heading1`, `Line1/2`, `Text1`–`Text4`, `Project`, `Created`, `Date`, `Note`, `LogoPlaceholder`, `Logo`) | PDF unverändert, aber das Report‑Fenster schiebt eines der beiden unter bzw. neben das andere (Text abgeschnitten, Blöcke verrutscht, Seite länger); gemessen schon bei einem Streifen von 0,02 cm, auch bei unsichtbarem oder leerem Element – ein Streifen ist in Feldern fester Höhe kritisch Entweder‑oder‑Paare, bei denen beide Elemente einen eigenen Sichtbarkeits‑Ausdruck (`<Visibility><Hidden>=…`) tragen, melden nicht, sondern erscheinen als eine Hinweiszeile; trägt nur eines einen Ausdruck, bleibt es W28 mit Zusatz | Abstand ≥ 0,05 cm lassen; Alternativen mit Gegen‑Ausdruck an beiden Elementen bauen; für Bausätze `validate_rdlc.find_overlaps(<Pfad oder XML>)` und `is_alternative` |

## 4. Review‑Prozess (empfohlen)

1. **Statisch** – `python <SKILL>/scripts/validate_rdlc.py <datei>`; Befunde nach §3 einordnen.
2. **Parameter‑Prüfung** – Alle `Parameters!X.Value`‑Referenzen haben ein `<ReportParameter Name="X">`.
3. **Smoke‑Test** – Report auf einem kleinen Testmodell ausführen.
4. **Realtest** – Report auf einem vollständigen Projekt ausführen und Plausibilität prüfen.
5. **Bilingual‑Abgleich** (nur wenn DE+EN) – `diff` der beiden Dateien zeigt nur Label‑Änderungen.

## 5. Automatisierbare Checks (nützlich für KI)

```regex
# Alle @XXX@-Codes im Query extrahieren
@(\d+)@

# Alle Fields-Namen im Query
\[Name=([A-Za-z_0-9]+)[|\]]

# Alle Fields-Definitionen
<Field Name="([^"]+)">

# Alle Parameter-Referenzen
Parameters!([A-Za-z_0-9]+)\.Value

# Alle Field-Referenzen
Fields!([A-Za-z_0-9]+)\.Value
```

Regel: Die Menge der Names aus dem Query muss gleich der Menge der Field‑Definitions sein. Die Menge der `Parameters!X` muss Teilmenge der `<ReportParameter Name="X">` sein. Die Menge der `Fields!X` muss Teilmenge der `<Field Name="X">` sein. Jede Verletzung ist ein Fehler.

## 6. Spezielle Plausibilitätsregeln

- Wenn `@205@` in Query → Feld im Fields‑Block muss `System.Byte[]` sein.
- Wenn `@87@` in Query → Feld‑Typ `System.String`.
- Wenn `CountValues=1` oder `TotalValue=true` → Feld liefert **eine** Zeile, nicht pro Objekt.
- Wenn `@49@` nicht gefiltert und das Modell sowohl Abbruch als auch Neubau enthält → erwarte doppelt viele Zeilen.
- Wenn `@VOB@` nicht im Filter bei Schalung/Ortbeton → alle Abrechnungseinträge, auch unbelastete.
