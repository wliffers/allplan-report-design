# Muster: Räume, Flächen, Gebäude

Reports über Räume, Geschossflächen, Wohnflächen (WoFlV) und DIN277‑Kennwerte nutzen spezialisierte Datenquellen (`FLOOR_AREA_ARCHITECTURE`, `GROUNDAREA_DIN277`) und inline‑Formeln, um Bereichstypen und Regionen dynamisch zu klassifizieren.

## 1. Objekt‑Codes (`@OBJ@`) für Räume / Flächen

| `@OBJ@` | Bedeutung |
|---------|-----------|
| `60` | Grundfläche (BGF/NGF) |
| `61` | **Raum** |
| `62` | Seitenfläche (Ausbau Wand) |
| `63` | Deckenfläche (Ausbau) |
| `64` | Bodenfläche (Ausbau) |
| `65` | Ausbaufläche (allgemein) |
| `69` | Raumgruppe / Apartment |
| `81` | Gebäude |
| `112` | Geschoss (Allfa) |
| `997`, `998` | BMZ‑Flächen |
| `999` | Hüllflächen |

## 2. Basis‑Raumabfrage (`Raumbuch.rdlc`, `Raumgeometrie.rdlc`)

```
SELECT
   @10@[Name=RoomID],
   @246@[Name=StoryName|Fmt=A30],
   @452@[Name=Story],
   @452@[Name=StoryIndex|Fmt=I4],
   @507@[Name=Name|Fmt=A30],
   @506@[Name=Function|Fmt=A40],
   @224@[Name=BaseArea|Fmt=F8.2],
   @223@[Name=Volume|Fmt=F8.3],
   @222@[Name=Height|Dim=1|Fmt=F6.2],
   @228@[Name=Outline|Fmt=F8.2],
   @205@[Name=Graphics|Projection=9|Width=35|Height=25|GText=HD],
   @507@[Name=StoryGroup|f=PARENT(@507@)|Fmt=A30]
FROM [Type=0,Filter=@OBJ@.eq.61;]
```

Raumgruppe wird über `f=PARENT(@507@)` aufgelöst (Parent = Raumgruppen‑Objekt).

## 3. Muster Wohnfläche (WoFlV)

```
SELECT
   @10@[Name=RoomID],
   @507@[Name=Name],
   @264@[Name=Factor|Fmt=F3.2],
   @82@[Name=BaseArea|Fmt=F8.2],
   @68@[Name=Wohnfl|Fmt=F8.2|TotalValue=true]
FROM [Filter=@OBJ@.eq.61.and.@233@.lt.1,Type=0]
```

- `@233@.lt.1` = nur Räume, die für WoFlV ausgewiesen sind.
- `@264@` liefert den Reduktionsfaktor (1.0, 0.5, 0.25).
- `@68@` ist das fertig berechnete WoFlV‑Ergebnis (BaseArea × Factor – von Allplan).
- `TotalValue=true` bewirkt Ausgabe einer Gesamtsumme.

### Wohnfläche mit einstellbarer Rundung (`Wohnflächen (Rundung einstellbar).rdlc`)

Zusätzlicher Parameter:
```xml
<ReportParameter Name="Total_Area_Formatting">
  <DataType>String</DataType>
  <DefaultValue><Values><Value>F2</Value></Values></DefaultValue>
  <ValidValues>
    <ParameterValues>
      <ParameterValue><Value>F1</Value></ParameterValue>
      <ParameterValue><Value>F2</Value></ParameterValue>
      <ParameterValue><Value>F3</Value></ParameterValue>
      <ParameterValue><Value>F4</Value></ParameterValue>
    </ParameterValues>
  </ValidValues>
</ReportParameter>
```

Pad‑Trick in der Summenzelle:
```xml
<Value>=CStr(Format(Sum(CDbl(Format(Fields!Wohnfl.Value,
         Parameters!Total_Area_Formatting.Value))),
         Parameters!Total_Area_Formatting.Value))
  + StrDup(Math.Max(0,
         CInt(Parameters!Area_Formating.Value.Substring(1))
         - CInt(Parameters!Total_Area_Formatting.Value.Substring(1))),
         ChrW(8199))</Value>
```

## 4. BGF / BRI (DIN277) – Brutto

`Brutto-Grundflächen Abmessungen.rdlc`, `Brutto-Rauminhalte Abmessungen.rdlc`:

```
SELECT
   @10@[Name=ID], @82@[Name=BaseArea],
   @231@[Name=Region|Fmt=A3],
   @232@[Name=AreaType|Fmt=A3],
   @266@[Name=Factor|Fmt=F3.2],
   @201@[Name=Quantity|Fmt=F9.2],

   [Name=AreaType_a_B|f=_IF_((@231@.eq."a".or.@231@.eq."R").and.(@232@.eq."B"))@201@*@266@_ELSE_0|Fmt=F9.0],
   [Name=AreaType_b_B|f=_IF_((@231@.eq."b".or.@231@.eq."S").and.(@232@.eq."B"))@201@*@266@_ELSE_0|Fmt=F9.0],
   [Name=AreaType_c_B|f=_IF_((@231@.eq."c").and.(@232@.eq."B"))@201@*@266@_ELSE_0|Fmt=F9.0]
FROM [Type=0,Filter=@OBJ@.eq.60.and.ELE(@232@;"B";"U";"M";"V")]
```

Für Rauminhalte analog, mit `@82@*@266@` statt `@201@*@266@`.

### DIN277 2005 ↔ 2016 umrechnen

```
[Name=Region2005DIN277|f=_IF_(@231@.eq."R")"a"_ELSE_(_IF_(@231@.eq."S")"b"_ELSE_@231@)|Fmt=A3]
[Name=Region2016DIN277|f=_IF_(@231@.eq."a".or.@231@.eq."R")"R"_ELSE_"S"|Fmt=A3]
[Name=Occupancy2016DIN277|f=_IF_(@235@.eq."NF*")"NUF"+MID(@235@;3;2)_ELSE_@235@|Fmt=A4]
[Name=Occupancy2005DIN277|f=_IF_(@235@.eq."NUF*")"NF"+MID(@235@;4;2)_ELSE_@235@|Fmt=A4]
```

## 5. Netto‑Grundflächen (NGF) & Netto‑Raumflächen (NRF)

`Netto-Grundflächen.rdlc`, `Netto-Raumflächen Abmessungen.rdlc`:

```
FROM [Type=0,Filter=@OBJ@.eq.60.and.ELE(@232@;"N";"L")]         (NGF Typ N oder L)
FROM [FLOOR_AREA_ARCHITECTURE, Filter=@OBJ@.eq.61.and.@233@.lt.1]  (NRF)
```

Bedingte Summen nach Nutzungstyp:
```xml
<Value>=Sum(IIF(Fields!AreaTypDIN277.Value = "N",
              CDec(Fields!NFA.Value),
              CDec(0)))</Value>
```

Kreuztabelle (Region × Nutzung) als Matrix oder per `_IF_`‑Formel.

## 6. Grundstück, GRZ, GFZ, BMZ

### `BMZ - Grundstück.rdlc`, `Baumasse mit Baumassenzahl.rdlc`

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.997]                          BMZ‑Gesamtflächen
FROM [MODEL_DATA, Filter=@OBJ@.eq.998]                          BMZ‑Einzelflächen
```

Felder:
```
@551@..@560@   Grundstücks‑Kennwerte (Nutzung, Flurstück, GRZ, GFZ, BMZ, Dachform, Vollgeschosse)
@565@         Vollgeschosse
@567@         Wohneinheiten
@568@         Obergeschosse
```

### `GFZ-GRZ - Grundstück.rdlc`, `Grundfläche Geschossfläche mit GRZ GFZ.rdlc`

```
FROM [GROUNDAREA_DIN277]
```
Liefert aggregierte Grundstückswerte mit GRZ/GFZ‑Flags (`@234@`, `@250@`).

## 7. Raumgruppen (`Raumgruppen.rdlc`, `Room groups.rdlc`)

```
SELECT
   @10@[Name=ApartmentID],
   @507@[Name=Name|Fmt=A40],
   @506@[Name=Function],
   @82@[Name=TotalArea]
FROM [Filter=@OBJ@.eq.69,Type=0,Properties=48]
```

Mitgliedsräume: Zweites DataSet mit `PARENT(@10@)`‑Verweis:
```
SELECT @10@[Name=RoomID], @507@[Name=RoomName|f=PARENT(@507@)]
FROM [Type=0,Filter=@OBJ@.eq.61]
```

Filter auf Table‑Ebene:
```xml
<Filters>
  <Filter>
    <FilterExpression>=Fields!Apartment.Value</FilterExpression>
    <Operator>In</Operator>
    <FilterValues><FilterValue>=Parameters!Apartment.Value</FilterValue></FilterValues>
  </Filter>
</Filters>
```

## 8. Ausbauflächen (`Ausbau Bodenflächen.rdlc` etc.)

```
FROM [Filter=ELE(@OBJ@;62;63;64;65),Type=0]
```
Pro Ausbauart eine Vorlage (62=Seite, 63=Decke, 64=Boden, 65=Allgemein). Zusätzlich:
- `Ausbauflächen Material.rdlc` gruppiert nach `@508@ Material`.
- `Ausbauflächen Übersicht.rdlc` ist ein Roll‑up.

## 9. FM‑Räume und Kostenstellen

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.112]                          FM‑Geschoss/Nutzung
```
Felder: `@315@` (Allfa‑Nutzungstext), `@82@` (Grundfläche), `@506@` (Funktion).

## 10. Gebäude‑Übersicht

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.81.and.@229@.gt.0;]
```
Felder: `@215@` (Anzahl), `@229@` (Geschossfläche), `@565@..@568@` (Geschosse, Wohneinheiten).

## 11. Flächenkennwerte‑Matrix (`Flächenübersicht (Kennwerte).rdlc`, `Area overview (characteristics).rdlc`)

Echter `<Matrix>`‑Report:
- `RowGrouping`: Geschoss → AreaType (BGF/NGF/NUF/VF/TF)
- `ColumnGrouping`: Region (a/b/c oder R/S)
- `MatrixCell`: `=Sum(Fields!Value.Value)`
- `Subtotal` pro Ebene → automatische Zwischensummen

## 12. Standard‑Gruppierungen

```xml
<GroupExpression>=IIF(Parameters!Sorting_Story.Value = "Geschoss (Bauwerksstruktur)",
                     Fields!Story.Value, Fields!StoryName.Value)</GroupExpression>

<GroupExpression>=Fields!RoomID.Value</GroupExpression>

<GroupExpression>=Fields!Apartment.Value</GroupExpression>

<GroupExpression>=IIF(Parameters!Sorting_Story.Value = "Raumgruppen",
                     Fields!StoryGroup.Value, Fields!Story.Value)</GroupExpression>
```

## 13. Aggregate typisch

```xml
=Sum(Fields!Quantity.Value)

=Sum(IIF(Fields!AreaTypDIN277.Value = "N",
        CDec(Fields!NFA.Value), CDec(0)))

=IIF(Sum(IIF(Fields!AreaTypDIN277.Value = "N" and
             Fields!BaseAreaTypDIN277.Value like "N*",
             CDec(Fields!NFA.Value), CDec(0))) = 0,
     "",
     Sum(IIF(Fields!AreaTypDIN277.Value = "N" and
             Fields!BaseAreaTypDIN277.Value like "N*",
             CDec(Fields!NFA.Value), CDec(0))))

=Count(Fields!RoomID.Value, "Table_GroupStory")
```

## 14. Format‑Bindung über Parameter

```xml
<Textbox>
  <Style><Format>=Parameters!Area_Formating.Value</Format></Style>
  <Value>=Fields!Quantity.Value</Value>
</Textbox>
```

`Area_Formating`‑Parameter erlaubt F1/F2/F3/F4 (0–3 Nachkommastellen). Summen oft mit separatem `Total_Area_Formatting`.

## 15. Nutzungsart / Umschliessungsart als MultiValue‑Filter

```xml
<ReportParameter Name="Nutzungsart">
  <DataType>String</DataType>
  <MultiValue>true</MultiValue>
  <AllowBlank>true</AllowBlank>
  <Nullable>true</Nullable>
  <Prompt>Nutzungsart</Prompt>
</ReportParameter>
```

Anwendung auf Tabelle:
```xml
<Filters>
  <Filter>
    <FilterExpression>=Fields!Nutzungsart.Value</FilterExpression>
    <Operator>In</Operator>
    <FilterValues><FilterValue>=Parameters!Nutzungsart.Value</FilterValue></FilterValues>
  </Filter>
</Filters>
```

Wirkungs‑Logik: Wenn `Nutzungsart` leer ist, werden keine Filter angewandt (alle Werte durchreichen).

## 16. Raumbuch (nested tables)

Raumbuch zeigt für jeden Raum eine eigene Untertabelle mit Teilflächen/Ausbauflächen:

Äußeres DataSet: `AllplanReport` (Räume, `FROM [Type=0,Filter=@OBJ@.eq.61;]`).
Inneres DataSet: `AllplanReport_Room` (Teilflächen, `FROM [Type=2,Filter=@OBJ@.eq.61;]`).

Die Query verwendet `PARENT(@10@)` zur Beziehung zwischen beiden DataSets.

## 17. Typische Stolpersteine

- **`@231@` vs. `@232@` verwechseln** → falsche BGF/BRI‑Summen.
- **`@233@.lt.1` vergessen** bei WoFlV → unvollständige Räume erscheinen.
- **Doppelte Zeilen** bei multi‑SELECT ohne `MergeDataSet=true`.
- **String‑Sortierung** der Geschosse statt StoryIndex.
- **Matrix‑Subtotals** vergessen → keine Zeilensumme.
- **MultiValue‑Parameter** ohne `<MultiValue>true</MultiValue>` → `Operator=In` verhält sich wie `Equal`.
