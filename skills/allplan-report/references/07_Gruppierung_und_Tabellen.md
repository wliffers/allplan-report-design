# Gruppierung und Tabellen

Allplan‑Reports nutzen fast ausschließlich **`<Table>`** (RDL 2005) bzw. **`<Tablix>`** (RDL 2016). Echte Matrizen (`<Matrix>`) kommen selten vor, meist in Flächen‑Kennwert‑Reports.

## 1. `<Table>`‑Grundgerüst (RDL 2005)

```xml
<Table Name="Table1">
  <DataSetName>AllplanReport</DataSetName>

  <Header>
    <TableRows>
      <TableRow>
        <TableCells>
          <TableCell><ReportItems><Textbox Name="HdrA">…</Textbox></ReportItems></TableCell>
          <TableCell><ReportItems><Textbox Name="HdrB">…</Textbox></ReportItems></TableCell>
        </TableCells>
        <Height>0.8cm</Height>
      </TableRow>
    </TableRows>
    <RepeatOnNewPage>true</RepeatOnNewPage>
  </Header>

  <Details>
    <TableRows>
      <TableRow>
        <TableCells>
          <TableCell><ReportItems><Textbox Name="CellA"><Value>=Fields!A.Value</Value></Textbox></ReportItems></TableCell>
          <TableCell><ReportItems><Textbox Name="CellB"><Value>=Fields!B.Value</Value></Textbox></ReportItems></TableCell>
        </TableCells>
        <Height>0.5cm</Height>
      </TableRow>
    </TableRows>
  </Details>

  <Footer>
    <TableRows>
      <TableRow>
        <TableCells>
          <TableCell><ReportItems><Textbox Name="FtrA"><Value>Summe</Value></Textbox></ReportItems></TableCell>
          <TableCell><ReportItems><Textbox Name="FtrB"><Value>=Sum(Fields!B.Value)</Value></Textbox></ReportItems></TableCell>
        </TableCells>
        <Height>0.5cm</Height>
      </TableRow>
    </TableRows>
  </Footer>

  <TableColumns>
    <TableColumn><Width>4cm</Width></TableColumn>
    <TableColumn><Width>3cm</Width></TableColumn>
  </TableColumns>

  <Top>0.28cm</Top>
  <Left>0cm</Left>
  <Height>1.8cm</Height>
  <Width>7cm</Width>
</Table>
```

Wichtige Attribute:
- `<DataSetName>` ist Pflicht.
- `<RepeatOnNewPage>` im Header sorgt dafür, dass Spaltenköpfe auf jeder Seite erscheinen.
- `<Details>` enthält eine oder mehrere Zeilen, die pro Datensatz einmal erscheinen.
- `<TableColumns>` definiert Spaltenbreiten (Pflicht). Summe = `<Width>` der Table.
- `<Footer>` ist optional und erscheint **einmal am Ende**.
- `<TableGroups>` für Gruppierung (s. u.).

## 2. TableGroups – einfache Gruppierung

```xml
<TableGroups>
  <TableGroup>
    <Grouping Name="Table_Group1">
      <GroupExpressions>
        <GroupExpression>=Fields!Story.Value</GroupExpression>
      </GroupExpressions>
      <PageBreakAtStart>false</PageBreakAtStart>
      <PageBreakAtEnd>false</PageBreakAtEnd>
    </Grouping>
    <Header>
      <TableRows>
        <TableRow>
          <TableCells>
            <TableCell>
              <ColSpan>3</ColSpan>
              <ReportItems>
                <Textbox Name="GroupHdrStory">
                  <Style>
                    <BorderStyle><Bottom>Solid</Bottom></BorderStyle>
                    <FontSize>8pt</FontSize>
                    <FontWeight>700</FontWeight>
                  </Style>
                  <Value>=Fields!Story.Value</Value>
                </Textbox>
              </ReportItems>
            </TableCell>
          </TableCells>
          <Height>0.5cm</Height>
        </TableRow>
      </TableRows>
      <RepeatOnNewPage>true</RepeatOnNewPage>
    </Header>
    <Footer>
      <TableRows>
        <TableRow>
          <TableCells>
            <TableCell>
              <ColSpan>2</ColSpan>
              <ReportItems>
                <Textbox Name="GroupFtrLabel"><Value>="Summe " + Fields!Story.Value</Value></Textbox>
              </ReportItems>
            </TableCell>
            <TableCell>
              <ReportItems>
                <Textbox Name="GroupFtrSum"><Value>=Sum(Fields!Quantity.Value)</Value></Textbox>
              </ReportItems>
            </TableCell>
          </TableCells>
          <Height>0.5cm</Height>
        </TableRow>
      </TableRows>
    </Footer>
  </TableGroup>
</TableGroups>
```

Grouping‑Eigenschaften:
- `<GroupExpression>` = Feldwert oder Ausdruck, nach dem gruppiert wird.
- Pro `<Grouping>` dürfen mehrere `<GroupExpression>`‑Elemente stehen (komposit‑gruppieren).
- `<PageBreakAtStart>` / `<PageBreakAtEnd>` erzwingen neuen Seitenumbruch.
- `<Header>` der Gruppe → einmalige Gruppenüberschrift.
- `<Footer>` der Gruppe → Gruppensumme.
- `<RepeatOnNewPage>true` – der Gruppenkopf wird auf Folgeseiten erneut dargestellt.

## 3. Mehrstufige Gruppierung

Die Ebenen werden als mehrere `<TableGroup>`‑Elemente **ineinander verschachtelt** (via Reihenfolge): die erste `<TableGroup>` ist die äußerste Gruppe, die letzte ist die innerste. `<Details>` steht **unterhalb** aller Gruppen.

```xml
<TableGroups>
  <TableGroup>
    <Grouping Name="Table_GroupStory">
      <GroupExpressions>
        <GroupExpression>=Fields!StoryIndex.Value</GroupExpression>
      </GroupExpressions>
    </Grouping>
    <Sorting>
      <Sortings>
        <Sorting><SortExpression>=Fields!StoryIndex.Value</SortExpression></Sorting>
      </Sortings>
    </Sorting>
    <Header>…</Header>
  </TableGroup>

  <TableGroup>
    <Grouping Name="Table_GroupMaterial">
      <GroupExpressions>
        <GroupExpression>=Fields!Material.Value</GroupExpression>
      </GroupExpressions>
    </Grouping>
    <Header>…</Header>
    <Footer>…</Footer>
  </TableGroup>

  <TableGroup>
    <Grouping Name="Table_GroupComponent">
      <GroupExpressions>
        <GroupExpression>=Fields!ComponentID.Value</GroupExpression>
      </GroupExpressions>
    </Grouping>
  </TableGroup>
</TableGroups>
```

Tiefster gefundener Stapel in den 520 Vorlagen: **6 Ebenen** in `Betonarbeiten - Ortbeton.rdlc`:
1. `GroupStory (StoryIndex)`
2. `GroupMaterial`
3. `GroupOID (ObjectIdentifier)`
4. `FundamenteG_Group (ObjectIdentifier + ObjectName)`
5. `FundamenteG_CoID_Group (ComponentID)`
6. `DeckenG1_Details_Group (Dimensions + Quantity)`

Und **12 Felder komposit** in einer einzigen Gruppe bei `Fenster (detailliert).rdlc` (Parent, Codetext, Material, WingId, gerundete Width/Height, Langtext, Wall_thickness, GraphicsId, Swing, SmartPart).

## 4. Sortierung innerhalb einer Gruppe

```xml
<TableGroup>
  <Grouping> … </Grouping>
  <Sorting>
    <Sortings>
      <Sorting>
        <SortExpression>=Fields!StoryIndex.Value</SortExpression>
        <Direction>Ascending</Direction>
      </Sorting>
    </Sortings>
  </Sorting>
</TableGroup>
```

Sortierung **immer nach numerischem Feld** (Story**Index**, nicht Story**Name**).

## 5. Bewehrungs‑Gruppierung

Typisches zweistufiges Schema (Stabliste ISO 3766):

```xml
<TableGroup>
  <Grouping Name="Table_Group1">
    <GroupExpressions>
      <GroupExpression>=Fields!Component.Value</GroupExpression>
    </GroupExpressions>
  </Grouping>
</TableGroup>

<TableGroup>
  <Grouping Name="Table_Group2">
    <GroupExpressions>
      <GroupExpression>=Fields!MarkNumberAndIndexMesh.Value</GroupExpression>
      <GroupExpression>=Fields!DiameterComment.Value</GroupExpression>
      <GroupExpression>=Fields!MaxLengthSegment.Value</GroupExpression>
      <GroupExpression>=Fields!Steelgrade.Value</GroupExpression>
      <GroupExpression>=Fields!BendingKey.Value</GroupExpression>
      <GroupExpression>=Fields!ImageID.Value</GroupExpression>
    </GroupExpressions>
  </Grouping>
</TableGroup>
```

Erste Ebene = Bauteil; zweite Ebene = eindeutige Kombination aus Markennr. / Durchmesser / Segmentlänge / Stahlgüte / Biegekey / Bildreferenz.

## 6. ColSpan

Für Gruppen‑Header/Footer, die über mehrere Spalten reichen:
```xml
<TableCell>
  <ColSpan>3</ColSpan>
  <ReportItems> … </ReportItems>
</TableCell>
```

## 7. Filter innerhalb der Tabelle

```xml
<Table>
  <DataSetName>AllplanReport</DataSetName>
  <Filters>
    <Filter>
      <FilterExpression>=Fields!AreaType.Value</FilterExpression>
      <Operator>In</Operator>
      <FilterValues>
        <FilterValue>=Parameters!AreaType.Value</FilterValue>
      </FilterValues>
    </Filter>
  </Filters>
  …
</Table>
```

Vorteil: gleiches DataSet kann mehrfach mit unterschiedlicher Auswahl dargestellt werden (mehrere Tables für BGF, NGF, VF).

## 8. `<Matrix>` (RDL 2005) / Tablix‑Matrix (2016)

Verwendet in:
- `Flächenübersicht (Kennwerte).rdlc` / `Area overview (characteristics).rdlc`
- `Netto-Raumflächen Abmessungen.rdlc`
- einigen Kennwert‑Reports

Grundstruktur:
```xml
<Matrix Name="AreaMatrix">
  <DataSetName>AllplanReport</DataSetName>
  <RowGroupings>
    <RowGrouping>
      <Width>3cm</Width>
      <DynamicRows>
        <Grouping Name="Story">
          <GroupExpressions><GroupExpression>=Fields!Story.Value</GroupExpression></GroupExpressions>
        </Grouping>
      </DynamicRows>
    </RowGrouping>
    <RowGrouping>
      <Width>2cm</Width>
      <DynamicRows>
        <Grouping Name="AreaType"><GroupExpressions><GroupExpression>=Fields!AreaType.Value</GroupExpression></GroupExpressions></Grouping>
      </DynamicRows>
    </RowGrouping>
  </RowGroupings>
  <ColumnGroupings>
    <ColumnGrouping>
      <DynamicColumns>
        <Grouping Name="Region"><GroupExpressions><GroupExpression>=Fields!Region.Value</GroupExpression></GroupExpressions></Grouping>
      </DynamicColumns>
      <Height>0.5cm</Height>
    </ColumnGrouping>
  </ColumnGroupings>
  <MatrixColumns>
    <MatrixColumn><Width>2cm</Width></MatrixColumn>
  </MatrixColumns>
  <MatrixRows>
    <MatrixRow>
      <MatrixCells>
        <MatrixCell><ReportItems><Textbox><Value>=Sum(Fields!Value.Value)</Value></Textbox></ReportItems></MatrixCell>
      </MatrixCells>
      <Height>0.5cm</Height>
    </MatrixRow>
  </MatrixRows>
</Matrix>
```

`Subtotal`‑Elemente innerhalb einer Grouping erzeugen automatische Zwischensummen:
```xml
<Grouping Name="AreaType">
  <GroupExpressions><GroupExpression>=Fields!AreaType.Value</GroupExpression></GroupExpressions>
  <Subtotal>…</Subtotal>
</Grouping>
```

## 9. Tablix (RDL 2016)

`<Tablix>` vereint Table und Matrix. Strukturschema:

```xml
<Tablix Name="Tablix1">
  <TablixBody>
    <TablixColumns>
      <TablixColumn><Width>3.5cm</Width></TablixColumn>
      …
    </TablixColumns>
    <TablixRows>
      <TablixRow>
        <Height>0.8cm</Height>
        <TablixCells>
          <TablixCell><CellContents><Textbox …/></CellContents></TablixCell>
          …
        </TablixCells>
      </TablixRow>
    </TablixRows>
  </TablixBody>
  <TablixRowHierarchy>
    <TablixMembers>
      <TablixMember>
        <Group Name="Table_Group1">
          <GroupExpressions><GroupExpression>=Fields!Story.Value</GroupExpression></GroupExpressions>
        </Group>
        <SortExpressions>…</SortExpressions>
        <TablixHeader>…</TablixHeader>
        <TablixMembers>
          <TablixMember>…</TablixMember>
        </TablixMembers>
      </TablixMember>
    </TablixMembers>
  </TablixRowHierarchy>
  <TablixColumnHierarchy>
    <TablixMembers><TablixMember/></TablixMembers>
  </TablixColumnHierarchy>
  <DataSetName>AllplanReport</DataSetName>
</Tablix>
```

Umrechnung 2005 → 2016:
- `<Table>` → `<Tablix>` mit leerer `<TablixColumnHierarchy>`
- `<Matrix>` → `<Tablix>` mit gefüllter `<TablixColumnHierarchy>`
- `<TableGroup>` → geschachteltes `<TablixMember>` innerhalb `TablixRowHierarchy`
- `<Grouping>` → `<Group>` (gleiche Inhalte)
- `<Header>/<Details>/<Footer>` → `TablixRow`‑Sequenzen mit passendem Scope

## 10. Details‑Zeile mit Image

```xml
<TableCell>
  <ReportItems>
    <Image Name="Preview">
      <Sizing>FitProportional</Sizing>
      <Source>Database</Source>
      <Value>=Fields!Graphics.Value</Value>
      <Top>0cm</Top><Left>0cm</Left>
      <Height>2cm</Height><Width>4cm</Width>
    </Image>
  </ReportItems>
</TableCell>
```

`<Source>Database</Source>` für Byte[]‑Felder, `<Source>External</Source>` für Dateisystem‑Pfade (Logo).

## 11. Zeilen‑Höhe

- `<Height>` in Details wird **als Mindesthöhe** interpretiert, wenn `<CanGrow>true</CanGrow>` gesetzt ist.
- Für Bildzellen: Höhe = `<Height>` des Image‑Elements, nicht der TableCell.

## 12. Layout‑Regel für Spalten

| Blatt | Body‑Breite | Typische Spaltenbreiten |
|-------|-------------|-------------------------|
| A4 hoch | 18 cm | 1.5/2.0/2.5/3.0/3.5/4.0 cm |
| A4 quer | 26.7 cm | bis 5 cm |
| A3 hoch | 26.7 cm | wie A4 quer |
| A3 quer | 39 cm | bis 6 cm |

Die Summe der Spaltenbreiten darf `<Width>` der Table nicht überschreiten (sonst Umbrüche oder abgeschnittene Spalten).

## 13. Nested Tables (Tabelle in Tabelle)

Kommt z. B. in `Raumbuch.rdlc` vor: eine innere Tabelle zeigt Teilflächen des Raumes, eingebettet in die Zelle der äußeren Raumtabelle.

```xml
<TableCell>
  <ReportItems>
    <Table Name="InnerTable">
      <DataSetName>AllplanReport_Room</DataSetName>
      …
    </Table>
  </ReportItems>
</TableCell>
```

Die innere Tabelle braucht ein eigenes DataSet (via zweite `<DataSet>`‑Definition im Report). Beziehung zwischen beiden DataSets wird in der Query über `PARENT(@10@)` aufgelöst.

## 14. Typische Stolpersteine

- **`<ColSpan>`** muss numerisch passen – bei 3 Spalten und `ColSpan=4` fehlen ungeschlossene Zellen.
- **Scope von Sum/Count** muss zum Ort passen: Sum im Detail = aktuelle Gruppe; Sum im Footer (äußerster) = Total.
- **Sortierung überschreibt Gruppierung nicht**: Innerhalb einer Gruppe kann nur die Reihenfolge der Detail‑Zeilen geändert werden.
- **`RepeatOnNewPage`** nur am Header oder Group‑Header nützlich.
- **Kein `<Tablix>` in 2005**, kein `<Table>` in 2016 – Schema ist strikt.
