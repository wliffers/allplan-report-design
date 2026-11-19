# Expressions und Aggregate (RDL‑Seite)

Dieser Abschnitt beschreibt die **Report‑Definition‑Language‑Ausdrücke** im `<Value>`‑Element von Textboxen, Visibility‑Bedingungen, Sort/Group‑Expressions und Filter‑Ausdrücken der Tabellen. Sie werden **nach** der Query‑Ausführung vom RDL‑Engine ausgewertet, nicht von Allplan selbst.

RDL‑Expressions beginnen mit `=`. Ohne `=` gilt der Wert als Literal.

## 1. Standard‑Ausdrücke

### Feldzugriff

```xml
<Value>=Fields!ObjectName.Value</Value>
<Value>=Fields!Quantity.Value</Value>
```

Der Feldname nach `Fields!` muss 1:1 mit `<Field Name="…">` und dem `Name=`‑Tag im Query übereinstimmen.

### Parameterzugriff

```xml
<Value>=Parameters!Project_Name.Value</Value>
<Value>=Parameters!Company_Logo.Value</Value>
```

### Globals

```xml
<Value>=Globals!PageNumber</Value>
<Value>=Globals!TotalPages</Value>
<Value>=Globals!ExecutionTime</Value>
<Value>=Globals!ReportName</Value>
```

### Konstanten + Verkettung

```xml
<Value>="Seite: " &amp; Globals!PageNumber &amp; " / " &amp; Globals!TotalPages</Value>
<Value>=Parameters!Telephone_Number.Value + "  " + Parameters!E_Mail.Value</Value>
```

**Entity‑Hinweis**: In RDL‑XML wird `&` zu `&amp;`, `<` zu `&lt;`, `>` zu `&gt;`. Ausdrücke wie `a < b` stehen als `a &lt; b` im XML.

## 2. Bedingungen

### `IIf` (ternär)

```xml
<Value>=IIF(Fields!Quantity.Value > 0, Fields!Quantity.Value, "")</Value>
<Hidden>=Parameters!Display_Logo.Value = false</Hidden>
<Value>=IIF(Parameters!Sorting_Story.Value = "Geschoss (Bauwerksstruktur)",
            Fields!Story.Value, Fields!StoryName.Value)</Value>
```

Achtung: IIf ist **nicht** kurzschließend – beide Zweige werden ausgewertet. Deshalb:

```vb
=IIf(Fields!Count.Value > 0, Fields!Sum.Value / Fields!Count.Value, 0)
```
kann eine Division durch 0 werfen. In Allplan‑Reports meist mit `CDec(0)` abgesichert:
```vb
=IIf(Fields!Count.Value > 0, CDec(Fields!Sum.Value / Fields!Count.Value), CDec(0))
```

### `Switch`

```xml
<Value>=Switch(
   Fields!Swing.Value = "DIN R", "R",
   Fields!Swing.Value = "DIN L", "L",
   true, "?")</Value>
```

### `Choose`

```xml
<Value>=Choose(Fields!WingIdentifier.Value And 3, "R", "L", "LR")</Value>
<Value>=Choose((Fields!WingIdentifier.Value >> 2) And 3, "R", "L", "LR")</Value>
```

`Choose(n, v1, v2, …)` liefert `vn` (1‑basiert). Nützlich für Bitmasken.

### Kombiniert

```vb
=IIF((Fields!SmartPart.Value = "SmartPartCompressed") or (Fields!SmartPart.Value = "SmartPart"),
     (Switch(Fields!Swing.Value = "DIN R", "R", Fields!Swing.Value = "DIN L", "L")),
     (Choose(Fields!WingIdentifier.Value And 3, "R", "L", "LR")))
```

(aus `Fenster (detailliert).rdlc`)

## 3. Casts

| Funktion | Zweck |
|----------|-------|
| `CDec(x)` | → Decimal (exakt) |
| `CDbl(x)` | → Double |
| `CInt(x)` | → Integer |
| `CStr(x)` | → String |
| `CBool(x)` | → Boolean |
| `CDate(x)` | → DateTime |

Bei Summen über Felder immer `CDec`/`CDbl` verwenden, wenn das Feld als String deklariert ist aber numerisch behandelt werden soll.

## 4. Aggregate

Ausschließlich in Group‑/Tabellen‑Scopes (Header, Footer, Group‑Header, Group‑Footer, Body außerhalb der Detail‑Zeile).

| Funktion | Bedeutung |
|----------|-----------|
| `Sum(Fields!X.Value)` | Summe |
| `Count(Fields!X.Value)` | Zeilen zählen |
| `CountDistinct(Fields!X.Value)` | Verschiedene Werte zählen |
| `Avg(Fields!X.Value)` | Durchschnitt |
| `Min`, `Max` | Min/Max |
| `First(Fields!X.Value)` | Erster Wert der Gruppe |
| `Last(Fields!X.Value)` | Letzter Wert |
| `RunningValue(Fields!X.Value, Sum, "ScopeName")` | Kumulierter Wert |

### Scope

Zweites Argument bei `Sum/Count/RunningValue`:
- Keines → aktuelle Gruppe
- `"DataSetName"` → gesamtes DataSet
- `"TableGroupName"` → spezielle Tabellengruppe

### Beispiele aus echten Vorlagen

```xml
<Value>=Sum(Fields!Quantity.Value)</Value>

<Value>=Sum(Fields!Marks.Value)</Value>

<Value>=Sum(IIF(Fields!AreaTypDIN277.Value = "N",
              CDec(Fields!NFA.Value),
              CDec(0)))</Value>

<Value>=IIF(Sum(IIF(Fields!AreaTypDIN277.Value = "N" and
                    Fields!BaseAreaTypDIN277.Value like "N*",
                    CDec(Fields!NFA.Value), CDec(0))) = 0,
             "",
             Sum(IIF(Fields!AreaTypDIN277.Value = "N" and
                     Fields!BaseAreaTypDIN277.Value like "N*",
                     CDec(Fields!NFA.Value), CDec(0))))</Value>
```

Das Muster `=IIF(Sum(…) = 0, "", Sum(…))` unterdrückt „0,00"-Zellen und ersetzt sie durch einen leeren String.

## 5. `like` und `Math`/`String`

RDL stellt zahlreiche VB‑Funktionen bereit:

| Funktion | Beispiel |
|----------|----------|
| `Math.Max(a, b)`, `Math.Min`, `Math.Round`, `Math.Abs` | `Math.Max(0, x)` |
| `Format(x, "F2")` | Zahl als String |
| `Format(Date, "dd.MM.yyyy")` | Datumsstring |
| `System.String.Format("{0:d} / {1}", Parameters!Date.Value, Parameters!Time.Value)` | Composite‑Formatter |
| `Join(Parameters!X.Value, ", ")` | MultiValue‑Parameter als Zeile |
| `UCase(x)`, `LCase(x)` | Groß/klein |
| `Left(s, n)`, `Right(s, n)`, `Mid(s, start, len)` | Substring |
| `Len(s)` | Länge |
| `Trim(s)`, `LTrim`, `RTrim` | Trim |
| `Replace(s, a, b)` | Ersetzen |
| `InStr(s, sub)` | Index (1‑basiert) |
| `StrDup(n, ch)` | Zeichen wiederholen |
| `ChrW(n)` | Unicode‑Zeichen aus Codepunkt |
| `like "NF*"` | Wildcard‑Match |

### Pad‑Trick (Wohnflächen‑Tabellen)

```xml
<Value>=CStr(Format(Sum(CDbl(Format(Fields!Wohnfl.Value,
         Parameters!Total_Area_Formatting.Value))),
         Parameters!Total_Area_Formatting.Value))
  + StrDup(Math.Max(0,
         CInt(Parameters!Area_Formating.Value.Substring(1))
         - CInt(Parameters!Total_Area_Formatting.Value.Substring(1))),
         ChrW(8199))</Value>
```

`ChrW(8199)` ist der Unicode‑**Figure Space**, damit Spaltenbreiten nach der Rundung erhalten bleiben.

## 6. Unit‑aware Ausgabe (Imperial ↔ Metric)

Für britische/US‑Reports:

```xml
<Value>=IIF(Nemetschek.Interfaces.NemAll_DataGeneral.IsGlobalImperialUnit() = true,
            Nemetschek.Interfaces.NemAll_DataGeneral.ConvertLengthToString(Sum(Fields!TotalLength.Value), 2, false),
            Sum(Fields!TotalLength.Value))</Value>
```

Die Assembly `Nemetschek.Interfaces.NemAll_DataGeneral` liefert:
- `IsGlobalImperialUnit()` – `true`/`false`
- `ConvertLengthToString(value, decimals, useFraction)` – formatiert Zoll/Fuß

In `<CodeModules>` bzw. `<References>` muss die Assembly nicht extra deklariert werden – Allplan registriert sie global.

## 7. Seitennummerierung

```xml
<Value>=Globals!PageNumber + Parameters!PageNo_1.Value - 1
       &amp; "/" &amp;
       Globals!TotalPages + Parameters!PageNo_1.Value - 1</Value>
```

Ergibt z. B. `3/12` bei `PageNo_1 = 1`, oder `13/22` bei `PageNo_1 = 11` (Teilbericht ab Seite 11).

## 8. Visibility

```xml
<Visibility>
  <Hidden>=Parameters!Display_Graphics.Value = false</Hidden>
</Visibility>

<Visibility>
  <Hidden>=Fields!SmartPart.Value &lt;&gt; "SmartPart"</Hidden>
</Visibility>
```

Ergibt `true` → Element ist **versteckt**. Komplementäre Logik beachten.

## 9. Filter auf Table/Group‑Ebene

```xml
<Filters>
  <Filter>
    <FilterExpression>=Fields!Apartment.Value</FilterExpression>
    <Operator>In</Operator>
    <FilterValues>
      <FilterValue>=Parameters!Apartment.Value</FilterValue>
    </FilterValues>
  </Filter>
</Filters>
```

Operatoren: `Equal`, `NotEqual`, `Less`, `Greater`, `In`, `Like`, `GreaterOrEqual`, `LessOrEqual`, `Between`. Für MultiValue‑Parameter immer `In`.

## 10. Sort‑Expressions

```xml
<Sortings>
  <Sorting>
    <SortExpression>=Fields!StoryIndex.Value</SortExpression>
    <Direction>Ascending</Direction>
  </Sorting>
  <Sorting>
    <SortExpression>=Fields!ComponentID.Value</SortExpression>
  </Sorting>
</Sortings>
```

Sortierung **immer nach numerischem Index** (`StoryIndex`, `Listnumber`, `MarkNumber`), **nicht nach Name** – Namen sind Strings und werden alphabetisch sortiert („EG" nach „2.OG"). Pro `<Sorting>` ein Schlüssel; mehrere `<Sorting>` ergeben mehrstufige Sortierung.

## 11. Group‑Expressions

```xml
<Grouping Name="Table_GroupStory">
  <GroupExpressions>
    <GroupExpression>=IIF(Parameters!Sorting_Story.Value = "Geschoss (Bauwerksstruktur)",
                           Fields!Story.Value,
                           Fields!StoryName.Value)</GroupExpression>
  </GroupExpressions>
  <PageBreakAtStart>false</PageBreakAtStart>
  <PageBreakAtEnd>false</PageBreakAtEnd>
</Grouping>
```

Dynamische Gruppierung über Parameter ist zulässig. Für mehrstufige Gruppierung siehe `07_Gruppierung_und_Tabellen.md`.

## 12. Zellformatierung

### `<Format>` (statisch)

```xml
<Style>
  <Format>F2</Format>
</Style>
```

VB‑kompatible Format‑Codes: `F0`, `F2`, `N2`, `G`, `d`, `dd.MM.yyyy`, `#,##0.00`, `0.##`, `p` (Prozent).

### `<Format>` (dynamisch über Parameter)

```xml
<Style>
  <Format>=Parameters!Area_Formating.Value</Format>
</Style>
```

### `<TextAlign>`, `<VerticalAlign>`

`Left | Center | Right | General` bzw. `Top | Middle | Bottom`.

## 13. Bookmarks und Actions

```xml
<Action>
  <Hyperlink>="Zoom:" + Fields!Allright_Bauteil_ID.Value</Hyperlink>
</Action>
```

`Zoom:<ID>` öffnet im Allplan‑Report den referenzierten Bauteil‑Bereich im Modell (zoomt dorthin).

Bookmarks:
```xml
<Bookmark>="Zoom:" + Fields!ID.Value</Bookmark>
```

## 14. Custom‑Code

RDL erlaubt optional `<Code>` mit VB‑Funktionen:

```xml
<Code>
  Public Function Runde(v As Double, n As Integer) As Double
    Return Math.Round(v, n)
  End Function
</Code>
```

Aufruf in Expressions: `=Code.Runde(Fields!X.Value, 2)`. In den 520 Vorlagen selten genutzt (< 5 Dateien).

## 15. Typische Fehlerquellen

1. **Aggregat in Detail‑Zeile** → RDL‑Fehler „Scope is not valid". Aggregat nur in Header/Footer oder Group‑Scope.
2. **Division durch 0** in IIf → `Math.Max` oder vorher prüfen.
3. **Case‑sensitive Feldnamen** → `Fields!material.Value` ist nicht `Fields!Material.Value`.
4. **`&` ohne Escape** → `&amp;` im XML.
5. **`=` vergessen** → Literal statt Expression.
6. **`CDec`/`CDbl` fehlt** bei Sum über String‑Feldern.
7. **`Parameters!X.Value` bei MultiValue** → ist ein Array, nicht ein Skalar. Mit `Join(...)` oder `In`‑Filter behandeln.
