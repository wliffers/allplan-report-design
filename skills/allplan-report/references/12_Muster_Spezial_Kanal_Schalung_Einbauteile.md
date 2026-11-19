# Muster: Schalung, Kanal, Einbauteile, Sonderbauteile

## 1. Schalung (`CASING_AREA`, `Type=83`)

### Wand-/Stützen-/Pfeiler‑Schalung

```
SELECT
  @452@[Name=Story], @452@[Name=StoryIndex|Fmt=I4],
  @83@[Name=Codetext], @508@[Name=Material],
  @215@[Name=Piece|CountValues=1], @225@[Name=Dimensions|Dim=30],
  @201@[Name=Quantity|Fmt=G10.0|CountValues=1],
  @206@[Name=AreaNumber|Fmt=I6],
  @205@[Name=Grafik|Projection=10|GText=HD|Scale=100|Width=100]
FROM [CASING_AREA, Filter=@VOB@;]
```

Zusätzlich Haupt‑DataSet zur Bauteilseite:
```
FROM [MODEL_DATA, Filter=@GW@.eq.13.and.(@OBJ@.eq.1.or.@OBJ@.eq.13.or.@OBJ@.eq.3)]
```

### Decken‑Schalung (Untersicht)

```
FROM [CASING_AREA, Filter=@VOB@]     (Schalungsflächen)
FROM [Type=51]                       (Deckenabzüge für Öffnungen)
```
Projection **10** (Untersicht).

### Randschalung Decken / Fundamente

```
FROM [Type=83,Filter=@VOB@;]         (Rand-Casing)
```

### Formbau‑Schalungselemente

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.14106]   Formbau (Element)
FROM [MODEL_DATA, Filter=@OBJ@.eq.14101]   Formbau (Variante)
FROM [MODEL_DATA, Filter=@1417@="Formwork Element"]   alternative
```
Mit `@903@` Fertigteil‑PosNr und `@199@` Dicke_absolut.

Parallele synthetische Felder:
```
[Name=Formula_1|f=PARENT(PARENT(@507@))|Dim=30]
[Name=Quantity|f=1|CountValues=1|Index=1]
```

## 2. Kanal / Drainage (Pipework_Macro)

Die Entwässerung ist in Allplan über **Pipework_Macros** organisiert. Der Subtyp (`@498@`) unterscheidet Schacht / Rohr / Formteil.

### Gesamtübersicht

```
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.!(@538@.eq."Pipework_Path".or.@538@.eq."Pipework_Group")).and.!(@764@.eq."Längenprofil").and.!(@764@.eq."Zulauf").and.!(@764@.eq."Ablauf")]
```
- Schließt Pfade/Gruppen aus (nur finale Elemente)
- Schließt Sub‑Ablaufpunkte aus (`@764@`)

### Schächte

```
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.@498@.eq."Schacht")]
```

Felder:
- `@1165@` Schachtnummer
- `@1178@` Schachthöhe
- `@1126@` Deckelhöhe
- `@1127@` Sohlenhöhe
- `@163@/@164@` X/Y‑Koordinaten
- `@764@` Pipework‑Subtyp

### Rohre

```
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.@498@.eq."Rohr")]
```
Felder: `@220@` Länge, `@759@` Durchmesser, `@419@` Komponente.

### Formteile

```
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.@498@.eq."Formteil")]
```

### Koordinaten Excel

Minimalistisches Excel‑freundliches Layout:
```
SELECT
   @10@[ID], @1165@[Nummer],
   @163@[X_Koordinate|fmt=F11.3],
   @164@[Y_Koordinate|fmt=F11.3],
   @1126@[Deckelhoehe|fmt=F8.3],
   @1127@[Sohlenhoehe|fmt=F8.3]
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.@498@.eq."Schacht")]
```
Keine Grafiken, keine Gruppierung, feste Spaltenbreiten. Autor `Allplan Schweiz AG`.

## 3. Leitungen (`@OBJ@=979/980`)

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.979.and.@1188@.eq."AW Ltg"]     Haltung (Abwasser)
FROM [MODEL_DATA, Filter=@OBJ@.eq.979.and.@1188@.eq."WA Ltg"]     Wasser
FROM [MODEL_DATA, Filter=@OBJ@.eq.980.and.@1188@.eq."WA LtgP"]    Leitungspunkte Wasser
FROM [MODEL_DATA, Filter=@OBJ@.eq.980.and.@1188@.eq."AW LtgP"]    Leitungspunkte Abwasser
```

`@1188@` ist die Leitungs‑Kategorie‑Kennung.

## 4. Spezialtiefbau (PythonParts mit TypeUUID)

```
Bohrpfahlwand:
FROM [MODEL_DATA, Filter=@OBJ@.eq.100.and.@611["__Allplan_PythonPart_TypeUUID__"]@.eq."0e6de672-a222-4c63-b900-47ce0c44b74e"]

Bodenanker:
FROM [MODEL_DATA, Filter=@611["0:__Allplan_PythonPart_TypeUUID__"]@.eq."b09e7590-bba1-4e6e-94b2-1245c1aa4be5"]

Spundwand:
FROM [MODEL_DATA, Filter=@611["0:__Allplan_PythonPart_TypeUUID__"]@.eq."e555e8ea-c2cf-4e39-bf53-1c71f81ef3fd"]

Trägerbohlwand:
FROM [MODEL_DATA, Filter=@611["0:__Allplan_PythonPart_TypeUUID__"]@.eq."7abaae25-6cd3-4906-a848-254a5da14ae0"]
```

Diese UUIDs sind **Allplan‑intern fest**. Für neue PythonPart‑Typen gilt: UUID einmalig vom Entwickler besorgen, dann stabil verwenden.

### Baugrube

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.1780.and.(@18417@.gt.0.or.@18418@.gt.0)]
```
`@18417@` = Cut‑Volumen, `@18418@` = Fill‑Volumen. Zusätzlicher Report: `Erdbau Auftrag Abtrag.rdlc`.

## 5. Einbauteile / Hersteller

### Generische Einbauteile

```
FROM [MODEL_DATA, Filter=(@OBJ@.eq.0.or.@OBJ@.eq.5.or.@OBJ@.eq.135.or.@OBJ@.eq.136.or.@OBJ@.eq.137.or.@OBJ@.eq.138.or.@OBJ@.eq.1766.or.@OBJ@.eq.1780)]
```

### Katalog

```
FROM [FixtureLibrary, Properties=512]
```

### Hersteller‑Filter

Siehe Kapitel 10, §14.

## 6. Sonderbauteile

| Report | Filter |
|--------|--------|
| `Kranbahn.rdlc` / `Crane runway.rdlc` | `FROM [MODEL_DATA, Filter=@OBJ@=255]` + `FROM [SUBSIDIARY_MODELDATA]` |
| `Außenanlagen.rdlc` / `Outdoor facilities.rdlc` | `FROM [MODEL_DATA, Filter=@MAK@.ne.2.and.!ELE(@OBJ@;60;61;1000).and.@230@.gt.0]` |
| `Baumbestandsplan.rdlc` | `FROM [MODEL_DATA, Filter=@OBJ@.eq.1013]` |
| `Pflanzen.rdlc` | `FROM [MODEL_DATA, Filter=@OBJ@.eq.1013]` (mit BCM‑Sonderattributen) |
| `Wegeflächen nach Abrechnungsart.rdlc` | `FROM [MODEL_DATA, Filter=@OBJ@.eq.65.and.@GW@.gt.0]` |

## 7. Mengen (3D‑Körper)

`Auswertung 3D Körper und Flächen.rdlc`:
```
SELECT @202@[Name=Unit] FROM [MODEL_DATA, Filter=@OBJ@=255]
SELECT @508@[Name=Material], @207@[Name=Brief_text], @452@[Name=Story], …
       @205@[Name=Graphics|Width=45|Height=30|Scale=200|Projection=9|GText=HD]
       FROM [SUBSIDIARY_MODELDATA]
SELECT @215@[Name=Piece], @198@[Name=Absolut_Length|Fmt=F8.2], …
       @225@[Name=Dimensions|Dim=30], @201@[Name=Quantity]
       FROM [QUANTITY_CALCULATION, Filter=@VOB@;]
```
Drei SELECT‑Blöcke im selben DataSet.

`Mengenkörper.rdlc`:
```
FROM [Type=0,Filter=@OBJ@.eq.5;]
```

`Mengenübersicht.rdlc`:
```
FROM [Type=0,Filter=(@OBJ@.ge.3.and.@OBJ@.le.36).or.@OBJ@.eq.1.or.@OBJ@.eq.701.or…]
```

`Mengenliste Ö-Norm.rdlc`:
```
FROM [ENGINEERING,Filter=@793@|@792@]
```

## 8. SVG‑Map (`Mengen (SVG Map).rdlc`)

Einziger Unterschied zu `Mengen (Grafik).rdlc`: das Feld `@87@[Name=SVG_Map|Dim=254]` ersetzt `@205@[Name=Image|Projection=10|Width=74]`.

Layout, Gruppierungen, Bookmarks (`"Zoom:" + Fields!Allright_Bauteil_ID.Value`) identisch.

## 9. Projekt / Bauwerksstruktur / Layouts

### Projektattribute

```
SELECT @697@[Projectnumber], @405@[Projectname], @431@[Owner], @432@[Created]
FROM [CURRENT_PROJECT]

SELECT @16@[AttributName], @17@[AttributValue]
FROM [ATTRIBUTES]
```

### Projektübersicht (mit PROJECT‑Tabelle)

```
SELECT @697@[Projectnumber], @405@[Projectname], @403@[Projecthost],
       @412@[Projectpath], @431@[Owner], @368@[ProjectAvailability],
       @449@[Version], @432@[Created], @436@[Size]
FROM [PROJECT]
```

### Projektdetails (Dokumente)

```
FROM [DOCUMENT,Properties=512]
```
Felder: `@512@` Documentnumber, `@425@` Documentname, `@436@` Size, `@430@` Groupingcode, `@433@` Modificationdate, `@420@` ListID.

### Bauwerksstruktur

```
FROM [BUILDINGSTRUCTURE, Properties=512]
```
Felder: `@409@` Nodename, `@1155@` NodeType, `@518@` Level. Einrücken über `Padding = Level * TabSize`.

### Planliste mit Dokumenten

```
FROM [LAYOUT]
```
Zweites DataSet: `FROM [LAYOUT_DRAWINGS]` für die Teilbild‑Zuordnung pro Plan.

## 10. Koordinatenlisten

### DGM‑Punkte

```
SELECT @1360@[DGM_Nr], @425@[DGM], @800@[Punktnummer],
       @163@[X_Koordinate|Dim=3|Fmt=G12.3],
       @164@[Y_Koordinate|Dim=3|Fmt=G12.3],
       @165@[Z_Koordinate|Dim=3|Fmt=G12.3]
FROM [Type=8,Properties=512,ListNr=13313]
```

### Allgemeine Koordinatenliste

Nutzt `Type=8` und liefert typische Messpunkte.

## 11. Plankopf‑Stempel (`ALLPLANDATA`)

In komplexen Reports wird aus dem aktuellen Plankopf ein Zweit‑DataSet geladen:

```
SELECT
  @856@[Name=DeliveryStreet], @857@[Name=DeliveryZip], @858@[Name=DeliveryCity],
  @859@[Name=DeliveryCountry], @860@[Name=Constructor_Street], @875@[Name=Constructor_Street2],
  @1167@[Name=DKBemerkung]
FROM [ALLPLANDATA]
WHERE @OBJ@.eq.1766.and.@507@.eq."ListHeader"
```

Dieses Ergebnis speist Header/Footer‑Textboxen des Reports.

## 12. Außenanlagen, Pflanzen, Baumbestand

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.1013]             Allgemeine Pflanzen
```
Pflanzen‑BCM‑Daten: zusätzliche `@611[...]@`‑Keys mit Pflanzendaten.

## 13. Fassade

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.1781]   Fassadenelemente
```
Varianten: Linear‑, Punkt‑, Flächen‑Elemente, Übersichten.

## 14. Dach

```
FROM [MODEL_DATA, Filter=@ROOTOBJ@.eq.21250]    Dach (Wurzel)
FROM [MODEL_DATA, Filter=ELE(@OBJ@;100).or.@ROOTOBJ@.eq.21051]   Sparrenkonstruktion
```

## 15. Außergewöhnliche Kombinationen

`Trades - overview.rdlc`:
```
FROM [MODEL_DATA, Filter=@GW@.gt.0.and.@OBJ@.ne.1003, RemoveZero=1]
```
Alle Bauteile eines Gewerks, außer Sonderbauteil `1003`. `RemoveZero=1` blendet Zeilen mit Menge=0 aus.

`OneClick LCA.rdlc`:
```
FROM [MODEL_DATA]
```
Breite Auswertung aller Bauteile mit spezifischen LCA‑Attributen.

## 16. Typische Stolpersteine

- **Pipework_Macro**: unterschiedliche Filter für Subtypen – **exakt kopieren**, nicht abkürzen. Parser akzeptiert keine andere Klammersetzung.
- **PythonPart‑UUID** muss in einfache doppelte Anführungszeichen stehen: `@611["__Allplan_PythonPart_TypeUUID__"]@.eq."…"`.
- **`@539@`** ist Makro‑Typ (in `"…"`); `@538@` ist Makro‑Untertyp. Nicht verwechseln.
- **`Type=83` ≙ `CASING_AREA`** – beide Schreibweisen kommen vor, äquivalent.
- **Koordinaten‑Excel** soll **keine Grafik** enthalten. Wenn jemand `@205@` ergänzt, bricht Excel‑Export.
- **SVG‑Map**: `@87@` liefert keinen Byte[], sondern String. Rendering als Textbox, nicht Image.
