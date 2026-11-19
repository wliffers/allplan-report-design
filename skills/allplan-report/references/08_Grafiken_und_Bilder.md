# Grafiken, Bilder, Vorschau‑Darstellungen

Vorschaubilder und Zeichnungen sind ein Kernbestandteil fast jedes Allplan‑Reports. Es gibt vier Mechanismen, ein Bild in einen Report zu bringen:

1. **Attribut `@205@`** – rendert eine 3D‑Ansicht des Bauteils als Byte[].
2. **Attribut `@87@`** – liefert eine SVG‑Map.
3. **Attribut `@71@`** – eine Bild‑ID (Bild schon im Modell hinterlegt).
4. **Parameter `Company_Logo`** – lädt ein externes JPG/PNG als Firmenlogo.

## 1. `@205@` – 3D‑Vorschau eines Bauteils

Syntax:
```
@205@[Name=<FieldName>|Projection=<N>|Width=<mm>|Height=<mm>|Scale=<S>|Hidden=<0..5>|GText=<Modus>|CanSave=true|Image=true]
```

Liefert ein Byte‑Array (`System.Byte[]`). Wird im RDL als `<Image>` mit `<Source>Database</Source>` gerendert.

### Projection‑Werte

| Wert | Ansicht |
|------|---------|
| `0` | Default / Standardansicht (Bewehrung) |
| `2` | Vorderansicht |
| `5` | Isometrie |
| `8` | Seitenansicht |
| `9` | Draufsicht (sehr häufig für Wände/Decken/Stützen) |
| `10` | Untersicht / Schalung (z. B. Formwork Slabs, Wände als Abwicklung) |
| `12` | Horizontalschnitt Mitte |

### Hidden (verdeckte Kanten)

| Wert | Bedeutung |
|------|-----------|
| `0` | Alle Kanten sichtbar |
| `1` | Verdeckte Kanten unterdrückt (Standard in Vorlagen) |
| `5` | Maximale Unterdrückung (nur Silhouette) |

### GText (Grafikstil)

| Wert | Einsatz |
|------|---------|
| `HD` | Hochauflösend Default |
| `HD_CENTER` / `HD_CENTER_MIDDLE` / `HD_CENTERMIDDLE` | Zentriert ausrichten |
| `HD_CWF` | Cage with Fixture (Bewehrungskorb mit Einbauteilen – Reports 062/063) |
| `BSHDCENTERMIDDLE` | British‑Standard‑Biegeform, Bemaßung nach BS 8666 |
| `MSSK` | Mattenschneideskizze (ganzseitig) |
| `BUTTON` | Button‑Symbol (047) |

### Beispiele aus echten Vorlagen

```
@205@[Name=Graphics|Projection=9|Hidden=1|Width=45|Height=30|Scale=200|GText=HD]
      → Wand/Decke Draufsicht, 200 % Maßstab, 45×30 mm.

@205@[Name=Graphics|Hidden=5|Projection=2|Scale=100|Width=27|Height=27|GText=HD_CENTER]
      → Fenster‑Vorderansicht, zentriert, 27×27 mm.

@205@[Name=Grafik|Projection=10|GText=HD|Scale=100|Width=100]
      → Deckenschalung (Untersicht), 100 mm breit.

@205@[Name=Graphics|Projection=0|Width=69|Height=25|GText=HD_CENTERMIDDLE|CanSave=true]
      → Bewehrungsstab‑Biegeform.

@205@[Name=BiegeformBS|Scale=100|Width=55|Height=35|GText=BSHDCENTERMIDDLE|CanSave=true]
      → BS‑Biegeform.

@205@[Name=MSSK_Image|GText=MSSK|Width=356|Height=462]
      → Ganzseitige Mattenschneideskizze (A4).

@205@[Name=Graphics|Projection=9|Hidden=1|Width=55|Height=35|Scale=200|GText=HD_CWF|CanSave=true]
      → FF‑Bewehrungskorb mit Einbauteilen.
```

### Rendering im Body

```xml
<Image Name="PreviewImage">
  <Sizing>FitProportional</Sizing>
  <Source>Database</Source>
  <Value>=Fields!Graphics.Value</Value>
  <Top>0cm</Top><Left>0cm</Left>
  <Height>2.5cm</Height><Width>4cm</Width>
</Image>
```

`<Sizing>` sinnvolle Werte: `FitProportional` (Standard), `Fit`, `Clip`, `AutoSize`.

### Visibility über Parameter

```xml
<Image>
  <Visibility><Hidden>=Parameters!Display_Graphics.Value=false</Hidden></Visibility>
  …
</Image>
```

### Mehrere Ansichten pro Bauteil

```
SELECT
  @205@[Name=GraphicFront|Projection=2|Width=40|Height=40|GText=HD],
  @205@[Name=GraphicTop  |Projection=9|Width=40|Height=40|GText=HD],
  @205@[Name=GraphicIso  |Projection=5|Width=40|Height=40|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.1]
```

Daraus werden drei Bildspalten im DataSet.

## 2. `@87@` – SVG‑Map

Einziger Einsatz‑Beispielreport: `Mengen (SVG Map).rdlc`.

Query:
```
@87@[Name=SVG_Map|Dim=254]
```

Der Wert ist eine **SVG‑XML‑Zeichenkette** (Text, nicht Byte[]). Rendering:
```xml
<Textbox Name="SVG_Map_Cell">
  <Style><FontSize>1pt</FontSize></Style>
  <Value>=Fields!SVG_Map.Value</Value>
</Textbox>
```

SVG‑Maps sind interaktiv (Zoom, Pan im Allplan‑Report‑Viewer) und skalieren verlustfrei. Ideal für geografische/koordinierte Übersichten.

## 3. `@71@` – ImageID

```
@71@[Name=ImageID]
```

Feldtyp `Int`. Allplan rendert intern anhand dieser ID ein Vorschaubild (typisch verwendet bei Querschnittskatalogen und Steel cross‑sections).

## 4. Firmenlogo (Parameter‑basiert)

Schon im Page‑Header:
```xml
<Image Name="Logo">
  <Sizing>FitProportional</Sizing>
  <Source>External</Source>
  <Visibility><Hidden>=Parameters!Display_Logo.Value = false</Hidden></Visibility>
  <Value>="file:///" + Parameters!Company_Logo.Value</Value>
  <Height>1.4cm</Height><Width>3.5cm</Width>
</Image>
```

- `Source=External` bedeutet: Pfad wird als URL interpretiert.
- `file:///C:/pfad/zum/logo.png` funktioniert lokal.
- Wenn `Company_Logo` leer ist, zeigt Allplan ein „kein Bild"‑Symbol – deshalb `Display_Logo` als Schalter.

## 5. Bewehrungs‑Biegeformen

Für Biegeformen gibt es länderspezifische `GText`-Modi:

| Report | GText | Zusätzliche Felder |
|--------|-------|--------------------|
| `Stabliste ISO 3766.rdlc` | `HD_CENTERMIDDLE` | `@798@[Index=1..10]` BarSegment_a..j |
| `Stabliste British Standard.rdlc`, `Stabliste BS8666 2020.rdlc` | `BSHDCENTERMIDDLE` | `@741@[Index=1..5]` SegmentLengthBS + `@1208@` TypeAndSizeforBS |
| `Stabliste SANS 282.rdlc` | `BSHDCENTERMIDDLE` | wie BS |
| `Stabliste Schweiz.rdlc` | `HD_CENTERMIDDLE` | zusätzliche Schweizer Stempelfelder |

Biegekey:
- `@763@` = Biegeschlüssel (ISO)
- `@786@` = BendingFormKeyBS
- `@1438@` = BendingKey‑ISO

Bei `BendingKey = 99` = „frei geformter Stab" werden die Segmentfelder ausgeblendet; Darstellung per `GText=BSHDCENTERMIDDLE` zeigt statt Koten das reine Polygon.

## 6. Mattenschneideskizze

Ganzseitige Skizze:
```
@205@[Name=MSSK|Width=356|Height=462|GText=MSSK]
```

Weitere Matten‑Grafik:
```
@205@[Name=Sketch|Width=100|Height=80|GText=HD|Projection=9]
```

## 7. Bewehrungskörbe – Cage‑Grafik

Reports 040/041/062/063:
```
@205@[Name=Graphics|Projection=0|Scale=75|Width=55|Height=35|GText=HD|CanSave=true]      (040)
@205@[Name=Graphics|Projection=9|Hidden=1|Width=55|Height=35|Scale=200|GText=HD_CWF|CanSave=true]   (062/063)
```

`HD_CWF` bindet Einbauteile mit in die Darstellung ein. Ohne `HD_CWF` werden Einbauteile ausgeblendet.

## 8. Schalungs‑Grafiken

Formbau (Schalung):
```
@205@[Name=Grafik|Projection=10|GText=HD|Scale=100|Width=100|Height=150]
```

Wand‑Schalung – Draufsicht:
```
@205@[Name=Graphics|Projection=9|Hidden=1|Width=55|Height=35|Scale=200|GText=HD]
```

Decke‑Schalung (Untersicht):
```
@205@[Name=Graphics|Projection=10|Hidden=1|Width=55|Height=35|Scale=100|GText=HD]
```

## 9. Türen / Fenster – Vorderansicht

```
@205@[Name=Graphics|Projection=2|Width=27|Height=27|Hidden=5|Scale=100|GText=HD_CENTER]
```

`Hidden=5` blendet Material‑ und Beschlags‑Kanten aus → saubere Silhouette.

## 10. Sonstige Bild‑Situationen

- **Querschnittskatalog** (`Cross-section catalogs.rdlc`): `@71@[Name=ImageID]` + interne Auflösung in Allplan.
- **Mesh cross‑sections** (`MattenQuerschnitte.rdlc`): `@205@[GText=HD]` mit Mattenansicht.
- **Key plan / Positionsplan**: Reines Layout‑Template ohne Bild; nur Parameter.
- **3D Körper** (`Auswertung 3D Körper und Flächen.rdlc`): dreistufige SELECT‑Kombi mit `@205@[Projection=9|GText=HD]`.

## 11. Performance‑Hinweise

- `CanSave=true` cacht das gerenderte Bild im Report – stark verkürzt die Exportdauer beim wiederholten Ausführen.
- Große `Width/Height`‑Werte erhöhen Export‑RAM. Für A4‑Tabellen selten > 60 mm breit.
- `Scale=200` liefert doppelte Linienbreite/Beschriftung – sinnvoll bei kleinen Darstellungsflächen.
- Ganz‑Seiten‑Skizzen (`MSSK`) erzeugen ~800×1000 px Bilder und sind deutlich langsamer.

## 12. Fehlerbilder

| Symptom | Ursache |
|---------|---------|
| Leeres Bild (rot durchgestrichen) | Pfad für Logo falsch (Parameter `Company_Logo` oder Datei existiert nicht) |
| Zu kleine Skizze | `Scale` zu klein oder `Width/Height` zu groß |
| Grafik enthält Hilfslinien | `Hidden` < 5 – höhere Stufe wählen |
| Farbe fehlt | `GText=HD` verwendet Monochrom – `HD_CENTERMIDDLE` unterstützt Farbe nicht |
| Bild wird mehrfach doppelt gerendert | DataSet‑Zeile existiert mehrmals, weil Gruppierung fehlt – aggregieren via `First(Fields!Graphics.Value)` oder geeignete Gruppierung |
