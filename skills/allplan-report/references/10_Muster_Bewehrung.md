# Muster: Bewehrung

Bewehrungsreports gehören zu den komplexesten Allplan‑Reports. Sie nutzen eigene Datenquellen (`ENGINEERING`, `REINFORCEMENT_DATA`), Array‑Attribute (Segmente) und landesspezifische Biegeformen.

## 1. Die beiden zentralen Filterflags

| Flag | Einsatz |
|------|---------|
| `@793@` | Stabbewehrung‑Flag |
| `@1210@` | Mattenbewehrung‑Flag |
| `@792@` | Polygonal‑Flag (frei geformter Stab) |

Typische Filter:
```
Filter=@793@|@792@        → nur Stäbe (gerade + polygonal)
Filter=@1210@             → nur Matten
Filter=@793@.or.@792@.or.@1210@   → alles
```

## 2. Stabliste nach ISO 3766 (`Stabliste ISO 3766.rdlc`, `Stabliste Biegeformen.rdlc`)

Datenquelle: `ENGINEERING`.

```
SELECT
   @10@[Name=ID],
   @419@[Name=Component|Fmt=A30],
   @423@[Name=NumberOfComponents|Fmt=I4],
   @795@[Name=MarkNumberAndIndexMesh|Fmt=A6],
   @767@[Name=MarkNumber|Fmt=I6],
   @766@[Name=NumberOfBars|Fmt=I6],
   @759@[Name=Diameter|Dim=2|Fmt=F5.0],
   @761@[Name=DiameterComment|Fmt=A10],
   @760@[Name=TotalLength|Dim=3|Fmt=F9.2|CountValues=1],
   @765@[Name=Mass|Fmt=F9.2|CountValues=1],
   @763@[Name=BendingKey|Fmt=I3],
   @495@[Name=Steelgrade|Fmt=A10],

   @798@[Name=BarSegment_a|Index=1|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_b|Index=2|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_c|Index=3|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_d|Index=4|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_e|Index=5|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_f|Index=6|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_g|Index=7|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_h|Index=8|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_i|Index=9|Dim=1|Fmt=F8.0],
   @798@[Name=BarSegment_j|Index=10|Dim=1|Fmt=F8.0],

   @205@[Name=BendingShape|Width=69|Height=25|GText=HD_CENTERMIDDLE|CanSave=true],
   @71@[Name=ImageID]
FROM [ENGINEERING, Filter=@793@|@792@]
```

Gruppierung:
```
TableGroup1: GroupExpression = Fields!Component.Value                 (pro Bauteil)
TableGroup2: GroupExpressions = MarkNumberAndIndexMesh, DiameterComment, MaxLengthSegment, Steelgrade, BendingKey, ImageID
             (eindeutige Position)
Details:     einzelne Stäbe / Varianten
```

Aggregate (Group‑Footer):
- Anzahl Stäbe: `=Sum(Fields!NumberOfBars.Value)`
- Gesamtlänge: `=Sum(Fields!TotalLength.Value)`
- Gewicht: `=Sum(Fields!Mass.Value)`

## 3. Stabliste British Standard (`Stabliste British Standard.rdlc`, `Stabliste BS8666 2020.rdlc`)

Datenquelle: `Type=1, ListNr=4879` (Rohdaten) bzw. `ENGINEERING, ListNr=4879` (aggregiert).

Unterschiede zu ISO:
- Durchmesser `@785@` statt `@759@`
- Segment‑Array `@741@[Index=1..5]` (BS hat max. 5 Segmente, nicht 10)
- Biegekey `@786@` (BendingFormKeyBS) statt `@763@`
- `@1208@` TypeAndSizeforBS (Kombination Typ+Größe)
- `GText=BSHDCENTERMIDDLE` (Biegebild mit britischer Bemaßungsregel)
- `BendingKey = 99` → Visibility‑Hide auf Segmentfeldern

Zusätzliche Parameter:
```
Construction_project, Controlled_By, Contract, Sheet, Layout, NumberOfComponents
```

Unit‑aware Total:
```xml
<Value>=IIF(Nemetschek.Interfaces.NemAll_DataGeneral.IsGlobalImperialUnit() = true,
            Nemetschek.Interfaces.NemAll_DataGeneral.ConvertLengthToString(Sum(Fields!TotalLength.Value), 2, false),
            Sum(Fields!TotalLength.Value))</Value>
```

## 4. Stabliste SANS 282 (Südafrika)

Fast identisch zu BS, aber `FROM [ENGINEERING, ListNr=4879]` (bereits aggregiert). Zusätzlich `@765@[TotalWeight]` im Header.

## 5. Stabliste Schweiz (`Stabliste Schweiz.rdlc`)

Komplexeste Bewehrungs‑Vorlage. Verwendet **Multi‑SELECT mit `MergeDataSet`**:

```
SELECT @495@[Name=Steelgrade] FROM [REINFORCEMENT_DATA, MergeDataSet=true, Filter=@793@.or.@792@.or.@1210@]
SELECT @759@[Name=Diameter|Dim=2]  FROM [REINFORCEMENT_DATA, MergeDataSet=true, Filter=@793@.or.@792@.or.@1210@]
SELECT …                           FROM [REINFORCEMENT_DATA, MergeDataSet=true, Filter=@793@]   (Stäbe)
SELECT [Name=Counter|f=1]          FROM [ALLPLANDATA, MergeDataSet=true]                        (Zähler)
```

Zusätzliche Parameter (25+):
```
ListID, Buildingsite_Name,
Constructor, Constructor_Name, Constructor_Street, Constructor_Zip,
Engineer, Engineer_Name, Engineer_Street, Engineer_Zip,
Ingenieur_Tel, Ingenieur_Logo,
TB_Name, TB_Nr, Layout_ID, Revisor,
Biegeregeln, Bemerkungen_anzeigen, Bemerkungen_trennen, Bemerkungen_Trennzeichen
```

Plankopf aus `ALLPLANDATA`:
```
SELECT @856@..@878@ FROM [ALLPLANDATA] WHERE @OBJ@.eq.1766.and.@507@.eq."ListHeader"
```

## 6. Stabliste Benennung (`Stabliste Benennung.rdlc`)

Kompakter – nur Benennungsform:
```
FROM [ENGINEERING, Filter=@793@, ListNr=4875]
```
Felder: `@419@ Component`, `@767@ MarkNumber`, `@766@ NumberOfBars`, `@759@ Diameter`, `@760@ TotalLength`, `@495@ SteelgradeShort`, `@765@ Mass`, plus berechnetes Einzelgewicht `f=@765@/@766@`.

## 7. Mattenliste (`Mattenstahlliste.rdlc`, `Mesh reinforcement.rdlc`)

Datenquelle: `ENGINEERING, Filter=@1210@`.

Matten‑spezifische Felder:
```
@751@[Name=Meshname|Fmt=A20]
@1213@[Name=Meshtype|Fmt=A10]
@756@[Name=Meshweight|Fmt=F7.2]
@768@[Name=BarGap_L|Dim=2]    @769@[Name=BarGap_Q|Dim=2]
@770@..@773@ BarDiameter DS1..DS4
@774@..@777@ Bars_Border_L/R/S/E
@752@/@753@ Overlap_L/Q
@754@/@755@ Quantity_L/Q
@778@ DoubleRod
```

## 8. Mattenschneideskizze (`Mattenschneideskizze.rdlc`, `Mesh cutting diagram.rdlc`)

Eine Seite je Matte, nur Grafik:
```
SELECT
   @751@[Name=Meshname],
   @205@[Name=Sketch|Width=356|Height=462|GText=MSSK]
FROM [ENGINEERING, Filter=@1210@]
```

Pro Seitenumbruch eine Matte – `<PageBreakAtEnd>true</PageBreakAtEnd>` in der Gruppierung `Meshname`.

## 9. Übersicht Bewehrung (`Übersicht Bewehrung.rdlc`, `Reinforcement - overview.rdlc`)

Datenquelle: `REINFORCEMENT_DATA, Filter=@793@.or.@1210@`.
Erzeugt per `_IF_`‑Formeln eine Kreuztabelle Durchmesser × Typ (Fix / Formed / Mesh) **im Query selbst**, ohne RDL‑Matrix.

Beispiel berechnete Felder:
```
[Name=FixBar10|f=_IF_((@OBJ@.ne.368.and.@OBJ@.ne.366).and.@799@.eq.0.and.@759@.eq.10.and.@423@.gt.0)@765@*@423@_ELSE_0|CountValues=1]
[Name=FormedBar10|f=_IF_((@OBJ@.ne.368.and.@OBJ@.ne.366).and.@799@.eq.1.and.@759@.eq.10.and.@423@.gt.0)@765@*@423@_ELSE_0|CountValues=1]
[Name=Mesh10|f=_IF_((@OBJ@.eq.368.or.@OBJ@.eq.366).and.@759@.eq.10)@765@_ELSE_0|CountValues=1]
```

Gruppierung: `Listnumber → Bauteil → NumberOfComponents`.

## 10. Anschlussbewehrung – Reports 031/032/033

`031_Stückliste_AnsBew.rdlc`: Datenquelle `Type=0, ListNr=10783`.
`032_Stückliste_AnsBew_Form.rdlc`: `MODEL_DATA, ListNr=10784`.
`033_Stückliste_AnsBew_Detail.rdlc`: `MODEL_DATA, ListNr=10785`.

Spezielle AB‑Felder:
- `@1450@[Name=Bezeichnung]`
- `@1451@[Name=Anzahl]`
- `@1452@[Name=Zulagen]`
- `@1453@[Name=Gewicht]`
- `@1454@[Name=Wanddicke]`

Parameter (AB‑spezifisch):
```
Auftragsnummer, Auftraggeber, Bauvorhaben, Objektname, Bauort,
Bearbeiter, Geschoss, Plannummer, Objekte, Hinweis
```

## 11. FF‑Bewehrungskörbe (040–063)

### Basis (`040_FF-Bewehrungskörbe - A4.rdlc`, `040  FF reinforcement cages - A4.rdlc`)

```
FROM [Type=0, Filter=@1044@.eq.1;]      (Objekte mit FF‑Korb‑Flag)
```

Spalten:
```
@1046@[Name=FFBuegelkoerbe_Sortierungsnummer|Fmt=I10]
@903@[Name=Elementbezeichnung|Dim=16]
@199@[Name=Dicke_absolut|Dim=3|Fmt=F8.2]
@1045@[Name=FFBuegelkoerbe_Kode]
@205@[Name=Graphics|Scale=75|Width=55|Height=35|GText=HD|CanSave=true]
@1081@[Name=Gesamtgewicht|Fmt=F6.1]
```

A3 (041) nutzt `Projection=0` + größere Grafikmaße. A4 ohne Projection (Default).

### 062/063 – Bewehrungskörbe **mit Einbauteilen**

Einziger Unterschied zu 040/041: `GText=HD_CWF` (Cage With Fixture). Parameter um 17 zusätzliche Felder erweitert (Plankopf, Bauteil‑Beiblatt, ProjektPlannummer).

### 045/046 – Bauseitige Bügelkörbe

```
FROM [MODEL_DATA, Filter=@1047@.eq.1;]       (Lagerware)
FROM [MODEL_DATA, Filter=@1048@.eq.1;]       (Spezialbewehrung)
```

### 047 – Stäbe + Bügel (bauseitig)

```
FROM [ENGINEERING, ListNr=10799, Filter=@1415@.eq.3]
```
`GText=BUTTON` → symbolische Darstellung.

### 060/061 – MSA‑Bewehrungsgruppe

```
FROM [Type=0, Filter=@1982@.eq.1]
```
Statt `@1081@` (FF‑Gesamtgewicht) wird `@756@` verwendet.

## 12. Custom Mesh Overview / Listenmatten

```
FROM [CROSSSECTIONS, Properties=512]                                          (Kopfdaten)
FROM [CROSSSECTION_DIAMETERS, Properties=1024]                                (Durchmesser‑Details)
```

Mattenspezifische Darstellung pro Querschnitt.

## 13. Muffen, Muttern, Gewinde

`Muffen, Muttern, Gewinde.rdlc` / `Couplers, nuts, threads.rdlc`:
```
FROM [MODEL_DATA, Filter=@OBJ@.eq.0.and.ELE(@1102@;"Coupler";"Nut";"Thread")]
```
`@1102@` = Hierarchic_function (Leviat‑Klassifizierung).

## 14. Hersteller‑Stücklisten (Leviat/PEIKKO/PHILIPP/Schöck)

### Leviat
```
FROM [MODEL_DATA, Filter=(@OBJ@.eq.0.or.@OBJ@.eq.5.or.@OBJ@.eq.135.or.@OBJ@.eq.136.or.@OBJ@.eq.137.or.@OBJ@.eq.138.or.@OBJ@.eq.1766.or.@OBJ@.eq.1780).and.(@708@.eq."HALFEN-DEHA".or.@708@.eq."HALFEN".or.@708@.eq."Leviat".or.@1136@.eq."Leviat".or.@1136@.eq."Leviat AG".or.@1136@.eq."HALFEN".or.@1136@.eq."Halfen")]
```

### Schöck
```
FROM [MODEL_DATA, Filter=@OBJ@.eq.135.and.(@1136@.eq."*Sch*ck*".or.@708@.eq."*Sch*ck*".or.@1236@.eq."*Sch*ck*".or.@1136@.eq."*sch*ck*" …)]
```
Wildcards `*Sch*ck*` decken „Schöck"/„Schoeck"/„Schock" ab.

### PEIKKO / PHILIPP
```
FROM [MODEL_DATA, Filter=@OBJ@.eq.135.and.@708@.eq."PEIKKO"]
FROM [MODEL_DATA, Filter=@OBJ@.eq.135.and.@708@.eq."PHILIPP"]
```

Allgemeine Einbauteil‑Liste:
```
FROM [MODEL_DATA, Filter=@OBJ@.eq.135.or.@OBJ@.eq.136.or.@OBJ@.eq.137.or.@OBJ@.eq.972]
```

## 15. Verbindungsplan (Stahlbau)

`Verbindungsplan-metrisch.rdlc`, `Verbindungsplan-imperial.rdlc` / `ConnectionSchedule-Metric/Imperial.rdlc`:
```
FROM [MODEL_DATA, Filter=@498@.eq."Structural Framing Connection"]
```
Felder: `@498@` Verbindungstyp, `@504@` MaxWeldSize, `@785@` MaxBoltDia, `@1102@` Function.

## 16. Imperial‑/Metrisch‑Gabel

- Metrische Vorlage zeigt Längen in mm/cm.
- Imperiale Vorlage nutzt `ConvertLengthToString(value, decimals, useFraction)` in jeder Ausgabe.
- Filterung über `IsGlobalImperialUnit()` in Expressions.

## 17. Typische Gruppierung

| Report | Gruppierung |
|--------|-------------|
| Stabliste ISO 3766 | Component → Mark/DiaComment/MaxLength/Steelgrade/BendingKey/ImageID |
| Stabliste BS | dito mit BS‑Segmentfeldern |
| Mattenstahlliste | Meshtype → Meshname |
| Mattenschneideskizze | Meshname (PageBreak) |
| Übersicht Bewehrung | Listnumber → Bauteil → NumberOfComponents |
| FF‑Korb | Sortierungsnummer → Elementbezeichnung |

## 18. Bewehrungs‑spezifische Stolpersteine

- **`@795@` vs. `@767@`**: `@795@` kombiniert Markennummer+Index (z. B. „3.2"), `@767@` nur die Nummer.
- **`@759@[Dim=2]`** liefert Durchmesser in **mm**, `[Dim=3]` in m. Für ISO immer `Dim=2`, für Stahlbau oft `Dim=3`.
- **Segmentreihenfolge**: Segmente a–j laufen `Index=1..10`. `Index=0` **funktioniert nicht**.
- **Rundung der Gruppierfelder** (`ROUND(Fields!Width.Value, 3)`) ist nötig, um Millimeter‑Duplikate zu vermeiden.
- **`CountValues=1`** im Query erzeugt pro Wert **eine** Zeile – typisch für Gesamtsummen‑Zeilen. Ohne Flag entsteht pro Bauteil eine Zeile.
