# Standardparameter und Seitenlayout

## 1. Die 12 Standard‑`<ReportParameters>`

Diese 12 Parameter gehören in jede **neue** Vorlage – sie füllen Page‑Header, Page‑Footer und Metadaten. In neuen Vorlagen stehen sie in genau dieser Reihenfolge in `<ReportParameters>`.

> **Bestand (Abgleich 2026-09-29):** Die ersten 11 (bis `Display_Logo`) sind die eigentlichen Konstanten; je 4–25 Vorlagen fehlt einer davon. Der zwölfte variiert: `Note` in 383 von 521 Altvorlagen, `Fileset_Name` in 13 (z. B. `Betonarbeiten.rdlc`). Exakt diese 12 und nichts sonst haben nur 62 Dateien; 19 beginnen mit `Werk`, 12 mit der Auftraggeber‑Gruppe. **Regel:** den Block der Ausgangsvorlage 1:1 übernehmen, eigene Parameter dahinter. Das Prüfskript prüft nur das Vorhandensein (W05), nicht die Reihenfolge.

```xml
<ReportParameter Name="Project_Name">
  <DataType>String</DataType>
  <Prompt>@405@</Prompt>
</ReportParameter>

<ReportParameter Name="Edited_By">
  <DataType>String</DataType>
  <Prompt>@20@</Prompt>
</ReportParameter>

<ReportParameter Name="Company_Name">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@410@</Prompt>
</ReportParameter>

<ReportParameter Name="Company_Address">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@411@</Prompt>
</ReportParameter>

<ReportParameter Name="Date">
  <DataType>DateTime</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@401@</Prompt>
</ReportParameter>

<ReportParameter Name="Time">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@402@</Prompt>
</ReportParameter>

<ReportParameter Name="PageNo_1">
  <DataType>Integer</DataType>
  <DefaultValue><Values><Value>1</Value></Values></DefaultValue>
  <AllowBlank>true</AllowBlank>
  <Prompt>Hier kann die Startseite eingetragen werden</Prompt>
</ReportParameter>

<ReportParameter Name="Company_Logo">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@70@</Prompt>
</ReportParameter>

<ReportParameter Name="Telephone_Number">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@302@</Prompt>
</ReportParameter>

<ReportParameter Name="E_Mail">
  <DataType>String</DataType>
  <AllowBlank>true</AllowBlank>
  <Prompt>@69@</Prompt>
</ReportParameter>

<ReportParameter Name="Display_Logo">
  <DataType>Boolean</DataType>
  <DefaultValue><Values><Value>True</Value></Values></DefaultValue>
  <AllowBlank>true</AllowBlank>
  <Prompt>Hier kann das Firmenlogo ausgeblendet werden</Prompt>
</ReportParameter>

<ReportParameter Name="Note">
  <DataType>String</DataType>
  <DefaultValue><Values><Value /></Values></DefaultValue>
  <AllowBlank>true</AllowBlank>
  <Prompt>Kommentar</Prompt>
</ReportParameter>
```

### Bedeutung der Prompt‑Codes

Die `<Prompt>@XXX@</Prompt>`‑Zahlen sind Allplan‑Lokalisierungs‑IDs. Sie bewirken, dass der Parameter‑Dialog im Report‑Manager in der jeweils eingestellten UI‑Sprache erscheint.

| Prompt | Bedeutung |
|--------|-----------|
| `@20@` | „Bearbeiter / Edited by" |
| `@69@` | „E‑Mail" |
| `@70@` | „Firmenlogo / Company logo" |
| `@302@` | „Telefonnummer / Telephone number" |
| `@401@` | „Datum / Date" |
| `@402@` | „Zeit / Time" |
| `@405@` | „Projektname / Project name" |
| `@410@` | „Firmenname / Company name" |
| `@411@` | „Firmenadresse / Company address" |

Die Prompts `Hier kann die Startseite eingetragen werden`, `Hier kann das Firmenlogo ausgeblendet werden`, `Kommentar` sind absichtlich **nicht lokalisiert**, da Text nicht in der Stringtabelle vorhanden ist – belassen.

## 2. Report‑spezifische Zusatzparameter

Nach den 12 Standards folgen optional weitere Parameter. Häufig vorkommende:

| Name | DataType | Sinn |
|------|----------|------|
| `Display_Graphics` | Boolean | Vorschaubild ein/aus |
| `Display_Matrix` | Boolean | Matrix‑Ansicht ein/aus |
| `Sorting_Story` | String + ValidValues | „Geschoss (Bauwerksstruktur)" / „Geschossbezeichnung" / „Raumgruppen" |
| `Area_Formating` | String + ValidValues | `F1`/`F2`/`F3`/`F4` Rundung |
| `Total_Area_Formatting` | String + ValidValues | dito für Summen |
| `Nutzungsart` | String MultiValue | Filter DIN277 |
| `Umschliessungsart` | String MultiValue | Filter Region |
| `AreaType` | String MultiValue | B/U/M/V |
| `Apartment` | String MultiValue | Filter Raumgruppe |
| `Basis` | String MultiValue | Grundstücksfilter |
| `Layout` | String | Stabliste Plankopf |
| `Construction_project`, `Controlled_By`, `Contract`, `Sheet`, `Buildingsite_Name` | String | Plankopf BS/SANS |
| `ShowSteelgrade`, `Steelgrade`, `NumberOfComponents` | String | Bewehrung‑Filter |
| `Auftragsnummer`, `Auftraggeber`, `Bauvorhaben`, `Objektname`, `Bauort`, `Bearbeiter`, `Geschoss`, `Plannummer`, `Objekte` | String | AB‑ und FF‑Köpfe |
| `Bauteil_Beiblatt`, `ProjektPlannummer` | String | FF‑Körbe mit EBT |
| `Objectfilter`, `Projectnumber` | String | Übersicht Bewehrung |
| `Revisor`, `Biegeregeln`, `Bemerkungen_anzeigen`, `Bemerkungen_trennen`, `Bemerkungen_Trennzeichen` | Mix | Stabliste CH |

### Parameter mit ValidValues

```xml
<ReportParameter Name="Sorting_Story">
  <DataType>String</DataType>
  <DefaultValue>
    <Values><Value>Geschoss (Bauwerksstruktur)</Value></Values>
  </DefaultValue>
  <ValidValues>
    <ParameterValues>
      <ParameterValue><Value>Geschoss (Bauwerksstruktur)</Value></ParameterValue>
      <ParameterValue><Value>Geschossbezeichnung</Value></ParameterValue>
      <ParameterValue><Value>Raumgruppen</Value></ParameterValue>
    </ParameterValues>
  </ValidValues>
  <AllowBlank>true</AllowBlank>
  <Prompt>Sortierung</Prompt>
</ReportParameter>
```

### MultiValue‑Parameter

```xml
<ReportParameter Name="Nutzungsart">
  <DataType>String</DataType>
  <Nullable>true</Nullable>
  <AllowBlank>true</AllowBlank>
  <MultiValue>true</MultiValue>
  <UsedInQuery>False</UsedInQuery>
  <Prompt>Nutzungsart</Prompt>
</ReportParameter>
```

Aktivierung im Table‑Filter:
```xml
<Filters>
  <Filter>
    <FilterExpression>=Fields!AreaTyp.Value</FilterExpression>
    <Operator>In</Operator>
    <FilterValues><FilterValue>=Parameters!Nutzungsart.Value</FilterValue></FilterValues>
  </Filter>
</Filters>
```

## 3. Seitenformate

| Format | `<PageWidth>` | `<PageHeight>` | `<Width>` (Body) |
|--------|---------------|----------------|------------------|
| A4 Hochformat | `21cm` | `29.7cm` | `18cm` |
| A4 Querformat | `29.7cm` | `21cm` | `26.7cm` |
| A3 Hochformat | `29.7cm` | `42cm` | `26.7cm` |
| A3 Querformat | `42cm` | `29.7cm` | `39cm` |
| US Letter | `8.5in` | `11in` | `7.5in` |

Standard‑Ränder (alle 520 Dateien):
- `<LeftMargin>2cm</LeftMargin>`
- `<RightMargin>1cm</RightMargin>`
- `<TopMargin>0.5cm</TopMargin>`
- `<BottomMargin>0.5cm</BottomMargin>`

Konsistenz‑Regel: `<Width>` (Body) = `<PageWidth>` − `<LeftMargin>` − `<RightMargin>`. Bei A4 Hochformat also `18 cm`.

Zusätzlich sind `<InteractiveHeight>` und `<InteractiveWidth>` in Zoll („11in" / „8.5in") gesetzt – diese dürfen **unangetastet** bleiben.

## 4. Page‑Header (Standard, 3.5 cm hoch)

```xml
<PageHeader>
  <PrintOnFirstPage>true</PrintOnFirstPage>
  <PrintOnLastPage>true</PrintOnLastPage>
  <Height>3.5cm</Height>
  <ReportItems>
    <!-- Logo -->
    <Rectangle Name="LogoPlaceholder">
      <Top>0cm</Top>
      <Left>14.5cm</Left>
      <Height>1.4cm</Height>
      <Width>3.5cm</Width>
      <ZIndex>11</ZIndex>
      <ReportItems>
        <Image Name="Logo">
          <Top>0cm</Top><Left>0cm</Left>
          <Height>1.4cm</Height><Width>3.5cm</Width>
          <Sizing>FitProportional</Sizing>
          <Source>External</Source>
          <Visibility><Hidden>=Parameters!Display_Logo.Value=false</Hidden></Visibility>
          <Value>="file:///" + Parameters!Company_Logo.Value</Value>
        </Image>
      </ReportItems>
    </Rectangle>

    <!-- Hinweis / Note -->
    <Textbox Name="Note">
      <Top>2.9cm</Top><Left>2cm</Left><Width>15.9cm</Width><Height>0.4cm</Height>
      <Style><FontSize>8pt</FontSize><VerticalAlign>Bottom</VerticalAlign>…</Style>
      <Value>=Parameters!Note.Value</Value>
    </Textbox>

    <!-- Datum / Zeit -->
    <Textbox Name="Date">
      <Top>2.5cm</Top><Left>2cm</Left><Width>15.9cm</Width><Height>0.4cm</Height>
      <Style><FontSize>8pt</FontSize><Format>d</Format>…</Style>
      <Value>=System.String.Format("{0:d}  /  {1}",Parameters!Date.Value,Parameters!Time.Value)</Value>
    </Textbox>

    <!-- Bearbeiter -->
    <Textbox Name="Created">
      <Top>2.1cm</Top><Left>2cm</Left><Width>15.9cm</Width><Height>0.4cm</Height>
      <Value>=Parameters!Edited_By.Value</Value>
    </Textbox>

    <!-- Projekt -->
    <Textbox Name="Project">
      <Top>1.7cm</Top><Left>2cm</Left><Width>15.9cm</Width><Height>0.4cm</Height>
      <Value>=Parameters!Project_Name.Value</Value>
    </Textbox>

    <!-- Labels (fester Text links) -->
    <Textbox Name="Text4"><Top>2.9cm</Top><Left>0cm</Left><Width>2cm</Width><Value>Hinweis:</Value></Textbox>
    <Textbox Name="Text3"><Top>2.5cm</Top><Left>0cm</Left><Width>2cm</Width><Value>Datum / Zeit:</Value></Textbox>
    <Textbox Name="Text2"><Top>2.1cm</Top><Left>0cm</Left><Width>2cm</Width><Value>Bearbeiter:</Value></Textbox>
    <Textbox Name="Text1"><Top>1.7cm</Top><Left>0cm</Left><Width>2cm</Width><Value>Projekt:</Value></Textbox>

    <!-- Trennlinien -->
    <Line Name="Line2"><Top>3.4cm</Top><Left>0cm</Left><Width>17.9cm</Width><Height>0cm</Height>
      <Style><BorderStyle><Default>Solid</Default></BorderStyle><BorderWidth><Default>0.5pt</Default></BorderWidth></Style></Line>
    <Line Name="Line1"><Top>1.55cm</Top>…</Line>

    <!-- Titelzeile -->
    <Textbox Name="Heading1">
      <Top>0.75cm</Top><Left>0cm</Left><Width>13.5cm</Width><Height>0.71cm</Height>
      <Style><FontSize>11pt</FontSize><FontWeight>700</FontWeight>…</Style>
      <Value>Titel des Reports</Value>
    </Textbox>
  </ReportItems>
</PageHeader>
```

### Besonderheiten

- **`Heading1`** ist der einzige Inhalt, der pro Report individuell gesetzt wird (der Titel).
- Das Logo wird via `="file:///" + Parameters!Company_Logo.Value` lokal eingelesen – funktioniert nur mit lokalen Dateisystem‑Pfaden.
- `Visibility.Hidden` blendet das Logo aus, wenn `Display_Logo = false`.
- Die Label‑Textboxen (`Text1–Text4`) sind in DE‑Reports hart „Projekt / Bearbeiter / Datum / Zeit / Hinweis", in EN‑Reports „Project / Edited by / Date / Time / Note". **Labels exakt kopieren**, nicht aus `@XXX@` herleiten (die Header‑Labels laufen nicht über die Lokalisierung).
- A3‑Varianten haben dieselbe Header‑Höhe (3.5 cm), aber die Breiten skaliert (Logo meist bei `35.5cm` Left, Note/Date/Created bei `Width=38.9cm`).

## 5. Page‑Footer (Standard, 1.35 cm hoch)

```xml
<PageFooter>
  <PrintOnFirstPage>true</PrintOnFirstPage>
  <PrintOnLastPage>true</PrintOnLastPage>
  <Height>1.35cm</Height>
  <ReportItems>
    <!-- Firmenname -->
    <Textbox Name="Footer1">
      <Top>0.1cm</Top><Left>0cm</Left><Width>15cm</Width><Height>0.45cm</Height>
      <Style><FontSize>8pt</FontSize>…</Style>
      <Value>=Parameters!Company_Name.Value</Value>
    </Textbox>

    <!-- Firmenadresse -->
    <Textbox Name="Footer2">
      <Top>0.5cm</Top><Left>0cm</Left><Width>15cm</Width><Height>0.5cm</Height>
      <Value>=Parameters!Company_Address.Value</Value>
    </Textbox>

    <!-- Telefon + E-Mail -->
    <Textbox Name="Footer3">
      <Top>0.9cm</Top><Left>0cm</Left><Width>15cm</Width><Height>0.45cm</Height>
      <Style><FontSize>7pt</FontSize>…</Style>
      <Value>=Parameters!Telephone_Number.Value + "  " + Parameters!E_Mail.Value</Value>
    </Textbox>

    <!-- Trennlinie oben -->
    <Line Name="Line6">
      <Top>0.08cm</Top><Left>0cm</Left><Width>17.9cm</Width><Height>0cm</Height>
      <Style><BorderStyle><Default>Solid</Default></BorderStyle><BorderWidth><Default>0.5pt</Default></BorderWidth></Style>
    </Line>

    <!-- Seitennummer rechts -->
    <Textbox Name="PageNumber">
      <Top>0.1cm</Top><Left>15.2cm</Left><Width>2.7cm</Width><Height>0.5cm</Height>
      <Style><FontSize>8pt</FontSize><TextAlign>Right</TextAlign>…</Style>
      <Value>=Globals!PageNumber+Parameters!PageNo_1.Value-1 &amp; "/" &amp; Globals!TotalPages+Parameters!PageNo_1.Value-1</Value>
    </Textbox>
  </ReportItems>
</PageFooter>
```

### Besonderheiten

- Seitenformat: **"aktuelle Seite / Gesamt"**, per `PageNo_1` verschiebbar – erlaubt es, den Bericht als Teildokument ab Seite N einzufügen.
- Footer‑Breite: `Width="17.9cm"` für die Trennlinie bei A4, `38.9cm` bei A3.
- In den 2016‑Varianten steht der Inhalt in einem `<PageFooter>`‑Rectangle; das Muster ist identisch.

## 6. Body‑Kopfbereich (optional)

Viele Reports beginnen den Body mit einer **Zusatz‑Zeile** über der Tabelle, z. B. für Filterangaben:

```xml
<Textbox Name="FilterInfo">
  <Top>0.1cm</Top><Left>0cm</Left><Width>18cm</Width><Height>0.4cm</Height>
  <Style><FontSize>8pt</FontSize><FontStyle>Italic</FontStyle></Style>
  <Value>="Nutzungsart: " + Join(Parameters!Nutzungsart.Value, ", ")</Value>
</Textbox>
```

## 7. Reihenfolge und ZIndex

- `<ZIndex>` im Header meist aufsteigend 1..11 (höher = vorne). Logo ZIndex=11, Labels 3–6.
- Bei neuen Textboxen einfach eine höhere ZIndex‑Nummer vergeben als vorhandene Elemente.

## 8. Umgang mit Ländervarianten

CH/UK/US‑Reports pflegen denselben Header, nutzen aber zusätzliche Ingenieur/Plankopf‑Parameter (siehe Abschnitt 2). Für CH werden Labels auch in **Französisch** geliefert (`Projet:`, `Révisé:`, …) – Vorbild: `Stabliste Schweiz.rdlc`, `Mattenschneideskizze Schweiz.rdlc`.
