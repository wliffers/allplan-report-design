# RDLC‑Grundstruktur (XML‑Gerüst)

## 1. Was ist eine Allplan‑RDLC‑Datei?

Eine `.rdlc`‑Datei ist eine **XML**‑Datei nach Microsoft‑Report‑Definition‑Language (client-side). Allplan nutzt dieses Format, transportiert darin aber ein **eigenes Query‑Modell**: Die `<CommandText>`‑Zeichenkette enthält keine SQL‑Abfrage, sondern einen Allplan‑internen Ausdruck, der gegen das 3D‑Modell oder die Projekt‑Datenbank ausgewertet wird.

Die Datei wird vom Allplan‑Report‑Designer erzeugt und gelesen, **nicht** vom SQL‑Server‑Reporting‑Services‑Viewer.

## 2. Drei Schema‑Versionen

Die Version steht im Namespace des Wurzelelements `<Report xmlns=…>` – **nicht** im Dateinamen. Das Suffix `_2005` tragen nur die vier `Template_*_2005.rdlc`; die übrigen 489 RDL‑2005‑Dateien heißen ohne Suffix.

| Namespace | Anzahl (Etc 2027) | Struktur | Seitenmaße |
|-----------|------------------:|----------|------------|
| `http://schemas.microsoft.com/sqlserver/reporting/2005/01/reportdefinition` | 493 | `<Table>`, `<Matrix>`, `<ReportParameters>` | `PageWidth`, `LeftMargin`, `RightMargin`, `Width` direkt unter `<Report>` |
| `http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition` | 10 (Kanal) | `<Tablix>`, `<ReportSections>` | `ReportSection/Width`, `ReportSection/Page/PageWidth` usw. |
| `http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition` | 48 | `<Tablix>`, `<ReportSections>`, `<Page>` | wie 2010 |

**Regel**: Eine KI darf innerhalb einer bestehenden Datei **nur** die Elemente verwenden, die zum jeweiligen Schema passen. Kein `<Tablix>` in einer 2005‑Datei, kein `<Table>`/`<Matrix>` in einer 2010‑/2016‑Datei. Zeichen pro Zeilenende dürfen nicht verändert werden (Allplan nimmt UTF‑8, Zeilenende `\r\n`).

Im Zweifel: **die 2005‑Variante verwenden**. Sie ist der Normalfall im Bestand, und zu jedem der vier Templates gibt es eine 2005‑Fassung.

## 3. Minimal‑Skelett einer 2005‑Datei

```xml
<?xml version="1.0" encoding="utf-8"?>
<Report xmlns="http://schemas.microsoft.com/sqlserver/reporting/2005/01/reportdefinition"
        xmlns:rd="http://schemas.microsoft.com/SQLServer/reporting/reportdesigner">
  <DataSources>
    <DataSource Name="DummyDataSource">
      <rd:DataSourceID>58c077ef-da67-445a-8cc2-60008c49a79b</rd:DataSourceID>
      <ConnectionProperties>
        <DataProvider>ALLPLAN</DataProvider>
        <ConnectString></ConnectString>
      </ConnectionProperties>
    </DataSource>
  </DataSources>

  <InteractiveHeight>11in</InteractiveHeight>
  <InteractiveWidth>8.5in</InteractiveWidth>

  <ReportParameters>
    <!-- siehe 03_Standardparameter_und_Layout.md -->
  </ReportParameters>

  <rd:DrawGrid>true</rd:DrawGrid>
  <rd:GridSpacing>0.25cm</rd:GridSpacing>
  <rd:SnapToGrid>true</rd:SnapToGrid>

  <!-- Seitenmaße -->
  <PageWidth>21cm</PageWidth>
  <PageHeight>29.7cm</PageHeight>
  <LeftMargin>2cm</LeftMargin>
  <RightMargin>1cm</RightMargin>
  <TopMargin>0.5cm</TopMargin>
  <BottomMargin>0.5cm</BottomMargin>

  <PageHeader>
    <!-- Logo, Projekt, Bearbeiter, Datum, Titel -->
  </PageHeader>

  <rd:ReportID>2cdc5b66-aa6c-4050-9ab9-72a8741b687e</rd:ReportID>

  <DataSets>
    <DataSet Name="AllplanReport">
      <Fields>
        <Field Name="MyField">
          <DataField>MyField</DataField>
          <rd:TypeName>System.String</rd:TypeName>
        </Field>
      </Fields>
      <Query>
        <DataSourceName>DummyDataSource</DataSourceName>
        <CommandText>SELECT @498@[Name=MyField]
                     FROM [Type=0]</CommandText>
      </Query>
      <rd:DataSetInfo>
        <rd:DataSetName>AllplanReport</rd:DataSetName>
        <rd:TableName>Room</rd:TableName>
      </rd:DataSetInfo>
    </DataSet>
  </DataSets>

  <Author>Allplan GmbH</Author>
  <Width>18cm</Width>

  <Body>
    <ColumnSpacing>1cm</ColumnSpacing>
    <ReportItems>
      <!-- Tabelle, Textboxen etc. -->
    </ReportItems>
    <Height>1.75cm</Height>
  </Body>

  <PageFooter>
    <!-- Firmenname, Adresse, Seitenzahl -->
  </PageFooter>
</Report>
```

## 4. Pflicht‑Elemente in fester Reihenfolge (Allplan‑Parser erwartet sie)

1. `<DataSources>` mit `DummyDataSource` und `DataProvider>ALLPLAN`
2. `<InteractiveHeight>`
3. `<ReportParameters>`
4. Grid/Snap (`rd:DrawGrid`, `rd:GridSpacing`, `rd:SnapToGrid`)
5. `<InteractiveWidth>`, `<LeftMargin>`, `<RightMargin>`
6. `<PageHeader>`
7. `<BottomMargin>`
8. `<rd:ReportID>`
9. `<PageWidth>`
10. `<DataSets>`
11. `<Author>`
12. `<Width>` (Body‑Breite)
13. `<Body>`
14. `<PageFooter>`
15. `<TopMargin>`
16. `<PageHeight>`

Diese Reihenfolge stammt aus dem Report‑Designer. Reihenfolgeänderungen werden zwar meist toleriert, können aber im Designer zu „zerschossenen" Reports führen. **Reihenfolge exakt wie in `Template_empty_2005.rdlc` übernehmen.**

## 5. DataSource

```xml
<DataSource Name="DummyDataSource">
  <rd:DataSourceID>58c077ef-da67-445a-8cc2-60008c49a79b</rd:DataSourceID>
  <ConnectionProperties>
    <DataProvider>ALLPLAN</DataProvider>
    <ConnectString></ConnectString>
  </ConnectionProperties>
</DataSource>
```

- `Name="DummyDataSource"` ist der Name, den `<Query>/<DataSourceName>` referenziert.
- `<rd:DataSourceID>` wird hartcodiert übernommen (GUID ist projektweit gleich).
- `<DataProvider>ALLPLAN</DataProvider>` signalisiert dem Report‑Designer die Allplan‑Query‑Engine.
- `<ConnectString>` bleibt leer.

## 6. DataSet

```xml
<DataSet Name="AllplanReport">
  <Fields> … </Fields>
  <Query>
    <DataSourceName>DummyDataSource</DataSourceName>
    <CommandText>SELECT @XXX@[Name=A], @YYY@[Name=B] FROM [Type=0,Filter=@OBJ@.eq.1]</CommandText>
  </Query>
  <rd:DataSetInfo>
    <rd:DataSetName>AllplanReport</rd:DataSetName>
    <rd:TableName>Room</rd:TableName>
  </rd:DataSetInfo>
</DataSet>
```

- `Name="AllplanReport"` ist der **Standardname** für neue Reports. Im 2027‑Bestand heißt das Haupt‑DataSet in 141 Dateien anders – meist `AllplanReport_Room`, daneben `CrossSectionDiameter`, `NemReportDataSetName`, `Projects` u. a. Beim Ändern den vorhandenen Namen beibehalten.
- `<Fields>` deklariert alle Spalten, die `<CommandText>` im `[Name=…]`‑Tag benannt hat. Namensgleichheit ist Pflicht.
- Typ‑Namen: `System.String`, `System.Double`, `System.Int32`, `System.DateTime`, `System.Byte[]` (für Bilder), `System.Object`.
- `<CommandText>` enthält die Allplan‑Query (siehe `04_Allplan_Query_Syntax.md`).
- `<rd:TableName>` wird vom Designer gesetzt (`Room`, `AllplanTable`, `Mesh`, …). In neuen Reports darf `Room` stehen bleiben.

## 7. Mehrere DataSets

Kommt regelmäßig vor, z. B.:

- Haupt‑DataSet mit Bauteildaten,
- Sekundäres DataSet mit Plankopf‑Stempel (`FROM [ALLPLANDATA] WHERE @OBJ@.eq.1766`),
- Drittes DataSet für Teilflächen (`FROM [Type=2]`).

Mehrere DataSets sind möglich. Jede Tabelle/jedes Tablix im Body referenziert **genau ein** DataSet über `<DataSetName>`.

## 8. Body

```xml
<Body>
  <ColumnSpacing>1cm</ColumnSpacing>
  <ReportItems>
    <Table Name="Table"> … </Table>
    <Textbox Name="Heading"> … </Textbox>
  </ReportItems>
  <Height>1.75cm</Height>
</Body>
```

- `<Height>` ist die **initiale** Body‑Höhe; dynamische Tabellen können sie überlappen.
- `<ColumnSpacing>1cm</ColumnSpacing>` wird beibehalten.
- `<ReportItems>` enthält alle sichtbaren Report‑Elemente in der Reihenfolge ihrer Z‑Index‑Stapelung (niedrig = hinten).

## 9. Textbox‑Grundmuster

```xml
<Textbox Name="MyText">
  <Top>1.7cm</Top>
  <Left>0cm</Left>
  <Width>5cm</Width>
  <Height>0.4cm</Height>
  <Style>
    <FontSize>8pt</FontSize>
    <VerticalAlign>Bottom</VerticalAlign>
    <PaddingLeft>2pt</PaddingLeft>
    <PaddingRight>2pt</PaddingRight>
    <PaddingTop>1pt</PaddingTop>
    <PaddingBottom>1pt</PaddingBottom>
  </Style>
  <CanGrow>true</CanGrow>
  <Value>=Fields!MyField.Value</Value>
</Textbox>
```

Standard‑Typographie in allen 520 Vorlagen:
- Default‑Schriftgröße: **8 pt** (Body), **7 pt** (Footer 3. Zeile), **11 pt/Bold** (Heading1).
- `<VerticalAlign>Bottom</VerticalAlign>` für Text in Tabellenzellen.
- Padding Links/Rechts je 2 pt, Oben/Unten je 1–2 pt.
- `CanGrow>true</CanGrow>` wird fast immer gesetzt – verhindert Abschneiden.

## 10. Table (2005)

```xml
<Table Name="Table">
  <DataSetName>AllplanReport</DataSetName>
  <Header>
    <TableRows>
      <TableRow>
        <TableCells>
          <TableCell><ReportItems><Textbox …>Spaltenkopf</Textbox></ReportItems></TableCell>
        </TableCells>
        <Height>0.8cm</Height>
      </TableRow>
    </TableRows>
  </Header>
  <Details>
    <TableRows>
      <TableRow>
        <TableCells>
          <TableCell><ReportItems><Textbox …>=Fields!A.Value</Textbox></ReportItems></TableCell>
        </TableCells>
        <Height>0.5cm</Height>
      </TableRow>
    </TableRows>
  </Details>
  <TableColumns>
    <TableColumn><Width>3.5cm</Width></TableColumn>
  </TableColumns>
  <Footer>…</Footer>
  <TableGroups>…</TableGroups>
</Table>
```

Siehe `07_Gruppierung_und_Tabellen.md` für Details.

## 11. Report‑GUID

Das Element `<rd:ReportID>…</rd:ReportID>` ist ein GUID. In neuen Vorlagen **neu generieren**, je Sprachdatei eine eigene.

Befund 2027: **Alle 551** ausgelieferten Vorlagen tragen dieselbe GUID `2cdc5b66-aa6c-4050-9ab9-72a8741b687e` und laufen. Die frühere Aussage, eine kopierte GUID führe zu Konflikten im Report‑Manager, ist damit nicht belegt. Die frische GUID bleibt Konvention für eigene Reports (so laufen eigene Leitungs‑Reports); das Prüfskript meldet die Standard‑GUID (W13) und doppelte eigene GUIDs (W14) als Warnung.

## 12. Author & Metadaten

- `<Author>` und ggf. `<Description>` oberhalb von `<Width>` setzen.
- Für offizielle Allplan‑Reports: `Allplan GmbH`. Schweizer Varianten: `Allplan Schweiz AG`. Eigenentwicklungen: den Entwickler‑Namen verwenden.

## 13. XML‑Encoding

- UTF‑8 ohne BOM. 12 der 551 Etc‑Vorlagen tragen einen BOM und laufen trotzdem (u. a. `Template_empty_2005.rdlc`, Leitungskataster). Neu erzeugte Dateien immer ohne BOM speichern; das Prüfskript meldet einen BOM als Warnung (W01).
- Umlaute (`ä`, `ö`, `ü`, `ß`) stehen direkt im XML, nicht als Entities.
- Zeichen `<`, `>`, `&`, `"`, `'` werden als Entities (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&apos;`) geschrieben – Ausdrücke wie `&gt;<` (ungleich) im Query‑Text bleiben in `&lt;&gt;`‑Form erhalten.
