# Allplan Query‑Syntax

Im `<CommandText>`‑Element jedes DataSets steht keine SQL‑Abfrage, sondern eine **Allplan‑interne Ausdruckssprache**. Sie ähnelt SQL (`SELECT … FROM …`), nutzt aber Allplan‑Tabellen und ‑Filter.

## 1. Grundform

```
SELECT   @XXX@[Name=FeldA|Fmt=F8.2|Dim=3],
         @YYY@[Name=FeldB|Projection=9|Width=35|Height=25|GText=HD]
FROM     [Tabelle, Filter=@OBJ@.eq.1.and.@233@.lt.1, ListNr=4879, Properties=512]
```

Zeilenumbrüche sind erlaubt und üblich. Die Query wird als **einzeiliger String** interpretiert (Whitespace kollabiert).

## 2. SELECT‑Klausel – Spalten‑Syntax

Jede Spalte hat die Form

```
@<AttributID>@[Name=<Fieldname>| <Modifier1>=… | <Modifier2>=… | f=<Formel>]
```

Die Modifikatoren sind pipe‑getrennt. Reihenfolge meist egal, aber Konvention: `Name=` zuerst.

### Modifikator‑Referenz

| Modifikator | Funktion | Werte / Beispiele |
|-------------|----------|-------------------|
| `Name=` | Name des Datensatz‑Feldes (Pflicht, muss zum `<Fields>`‑Block passen) | `Name=Material` |
| `Fmt=` | Formatierung beim Auslesen | `F8.2`, `F9.0`, `F12.0`, `F14.2`, `F6.1`, `F4.1`, `F11.3`, `G10.0`, `G12.0`, `I10`, `A3`, `A4`, `A9`, `A16`, `A17`, `A30`, `A40`, `A70` |
| `Dim=` | Dimensionsinterpretation (interne Einheit → Ausgabeformat) | `1`=Länge, `2`=Länge (mm), `3`=Länge (m), `4`=Einheit, `6`=Fläche, `16`=Text16, `20`=Text20, `30`=Text30, `254`=SVG |
| `Projection=` | 3D‑Vorschau‑Ansicht (nur für Grafik‑Attribute wie `@205@`) | `0`=Default, `2`=Vorne, `5`=Iso, `8`=Seite, `9`=Draufsicht, `10`=Schalung/Untersicht, `12`=Mitte‑Schnitt |
| `Width=`, `Height=` | Grafikgröße in mm | `Width=35\|Height=25` |
| `Scale=` | Zeichnungsmaßstab der Vorschau | `50`, `75`, `100`, `200` |
| `Hidden=` | Verdeckte Kanten (0=sichtbar bis 5=voll ausgeblendet) | `0…5` |
| `GText=` | Grafik‑Rendering‑Modus | `HD`, `HD_CENTER`, `HD_CENTER_MIDDLE`, `HD_CENTERMIDDLE`, `HD_CWF`, `BSHDCENTERMIDDLE`, `MSSK`, `BUTTON` |
| `Image=true` | Attribut als Bild (Byte‑Array) statt Zeichnung | |
| `CanSave=true` | Grafik in Report‑Cache serialisieren | |
| `CountValues=1` / `CountValues=true` | Aggregiert/gruppiert gleiche Werte | |
| `TotalValue=true` | Gibt einen Gesamtwert zurück (eine Zeile) | |
| `Index=` | Index bei Array‑Attributen (z. B. Biege‑Segmente) | `1..10` |
| `Hidden=1` (im Query‑Kontext) | Zeile im Output unterdrücken, wenn Bedingung greift | |
| `f=` | Berechnete Formel (siehe §5) | `f=@765@/@766@`, `f=PARENT(@507@)`, `f=_IF_(@793@.eq.1)"Stab"_ELSE_"Matte"` |

### Mehrere Attribute mit gleicher Basis

```
@205@[Name=GraphicsFront|Projection=2|Width=40|Height=40|GText=HD]
@205@[Name=GraphicsTop|Projection=9|Width=40|Height=40|GText=HD]
```

Dasselbe Attribut `@205@` kann mehrfach mit unterschiedlichem `Name=` und unterschiedlichen Modifikatoren selektiert werden → mehrere Felder im DataSet.

## 3. FROM‑Klausel – Tabellen

Die FROM‑Klausel besteht aus `[<Tabelle>, <Option1>, <Option2>, …]`. Immer in einem **einzigen** eckigen Klammerpaar.

### Hauptsächliche Tabellen

| Tabelle / Pseudo‑Tabelle | Bedeutung |
|--------------------------|-----------|
| `MODEL_DATA` | Komplettes 3D‑Modell (mit Filter einschränken!) |
| `Type=0` | Alias für MODEL_DATA mit Filter‑Kompaktform |
| `Type=1` | Roh‑Stabdaten (Bewehrung, nicht aggregiert) |
| `Type=2` | Teilflächen eines Raumes (Wand/Boden) |
| `Type=3` | Mauerarbeits‑Abrechnung (VOB) |
| `Type=5` | Fenster‑/Tür‑Unterobjekte, Öffnungen |
| `Type=8` | Koordinatenpunkte / DGM |
| `Type=10` | Geo‑Info‑Objekte |
| `Type=18` | Bauteilabrechnung (BRI/BMZ) |
| `Type=19` | Ortbeton‑/Unterzug‑Abrechnung |
| `Type=34` | Flächen für Grundstücksebene |
| `Type=51` | Deckenabrechnungs‑Layer |
| `Type=67` | Dachhaut‑Abrechnung |
| `Type=83` | Randschalung (`CASING_AREA` gleichwertig) |
| `Type=99` | Wand‑Abrechnung (Schichten) |
| `Type=160` | DIN277‑Teilflächen |
| `ENGINEERING` | Bewehrung (Stäbe/Matten) |
| `REINFORCEMENT_DATA` | Aggregierte Bewehrungsmengen (Diameter × Bauteil) |
| `CASING_AREA` | Schalungsflächen |
| `BUILDINGSTRUCTURE` | Bauwerksstruktur‑Knoten |
| `FLOOR_AREA_ARCHITECTURE` | DIN277‑Grundflächen |
| `GROUNDAREA_DIN277` | Grundstücksflächen DIN277 |
| `ALLPLANDATA` | Plankopf‑/Stempeldaten |
| `CURRENT_PROJECT` | Attribute des aktuellen Projekts |
| `ATTRIBUTES` | Generische Attribut‑Schlüssel/Werte‑Liste |
| `DOCUMENT` | Dokumentenliste / Teilbilder |
| `LAYOUT` | Plan‑Layouts |
| `LAYOUT_DRAWINGS` | Teilbilder einem Layout zugeordnet |
| `LAYOUT_HISTORY` | Plan‑Revisionen |
| `FILESET` | Teilbildsätze |
| `FixtureLibrary` | Einbauteile‑Katalog |
| `CROSSSECTIONS`, `CROSSSECTION_DIAMETERS` | Querschnitts‑ und Durchmesser‑Katalog |
| `QUANTITY_CALCULATION` | Mengenermittlungs‑Aggregate |
| `SUBSIDIARY_MODELDATA` | Untergeordnete Modelldaten (Bauwerk) |
| `PROJECT` | Projekt‑Metadaten |

**Im 2027‑Bestand belegt, Bedeutung nicht dokumentiert** – nur zusammen mit der Vorbilddatei verwenden (Pfade unter `<RDLC>/`):

| Tabelle | Vorbild |
|---------|---------|
| `Type=7` | `deu/Intelligente Verlegungen/Verlegung - Einzelteile.rdlc` |
| `Type=24` | `deu/Lageplan/Prismenliste.rdlc`, `deu/Lageplan/Ergebnisliste.rdlc` |
| `Type=26` | `deu/Bewehrung/Mattenschneideskizze Schweiz.rdlc` |
| `Type=35` | `deu/Räume, Flächen, Geschosse/Räume/Raum Grundflächen.rdlc` |
| `Type=227` | `deu/Gewerke/Betonarbeiten/Schalung Unterzüge.rdlc` |
| `SYMBOL` | `deu/Verwaltung/Bibliotheken/Symbole.rdlc` |
| `SMARTSYMBOL` | `deu/Verwaltung/Bibliotheken/Makros.rdlc` |

Alle Tabellen einer Vorlage stehen im Index `<SKILL>/rdlc-index.json` unter `DataSets[].FromTables`.

### FROM‑Optionen

| Option | Wirkung |
|--------|---------|
| `Filter=<Ausdruck>` | Datensätze einschränken (Filter‑Sprache s. §4) |
| `ListNr=NNNN` | Fest verdrahtete Listen‑Nr. (Allplan‑Vordefinition, z. B. `4875` Stabbewehrung Benennung, `4879` BS/SANS Roh‑Stäbe, `10783–10799` Fertigteil‑AB/FF/MSA, `7425` spezifisch, `13313` DGM) |
| `Type=N` | Objektfilter‑Shortcut |
| `Properties=512` | Lädt Basis‑Properties |
| `Properties=1024` | Lädt erweiterte Properties |
| `Properties=48` | Erweiterte Raum‑/Flächen‑Properties |
| `Properties=4096` | IBD‑Spezial‑Properties |
| `Baugruppe=N` | Baugruppen‑Scope (`1`=Zeichnung, `2`=Modell) |
| `RemoveZero=1` | Zeilen mit Menge=0 ausblenden |
| `MergeDataSet=true` | Kombiniert mehrere `SELECT ... FROM ...`‑Anweisungen in ein DataSet |

### Beispiele echter FROM‑Klauseln

```
FROM [Type=0,Filter=@OBJ@.eq.61;]                             Raum
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.and.@49@.eq.0]            Neubau‑Wand
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.and.@49@.eq.2]            Abbruch‑Wand
FROM [Type=0,Filter=@OBJ@.eq.60.and.ELE(@232@;"B";"U";"M";"V")]  BGF alle Typen
FROM [FLOOR_AREA_ARCHITECTURE, Filter=@OBJ@.eq.61.and.@233@.lt.1]  Wohnflächen nur gültig
FROM [ENGINEERING, Filter=@793@|@792@]                        Bewehrung (Stab ODER polygonal)
FROM [ENGINEERING, Filter=@1210@;]                            nur Mattenbewehrung
FROM [Type=1, ListNr=4879]                                    Stabliste BS Roh
FROM [Type=0, Filter=@1044@.eq.1;]                            FF‑Bewehrungskorb‑Flag
FROM [CASING_AREA, Filter=@VOB@;]                             Schalungsfläche
FROM [MODEL_DATA, Filter=(@539@.eq."Pipework_Macro".and.@498@.eq."Schacht")]   Kanalschacht
FROM [MODEL_DATA, Filter=@OBJ@.eq.100.and.@611["__Allplan_PythonPart_TypeUUID__"]@.eq."0e6de672-…"]  PythonPart Bohrpfahlwand
FROM [ALLPLANDATA,MergeDataSet=true] WHERE @OBJ@.eq.1766.and.@507@.eq."ListHeader"   Plankopf
FROM [BUILDINGSTRUCTURE, Properties=512]                      Bauwerksstruktur
FROM [DOCUMENT,Properties=512]                                Dokumentenliste
FROM [CURRENT_PROJECT]                                        Projekt‑Attribute
FROM [PROJECT]                                                Projekt‑Meta
```

## 4. Filter‑Sprache

**Zwei Dialekte** kommen im Bestand vor (Index‑Feld `FilterDialect`):

- **Punkt‑Notation** (Normalfall, für neue Reports): `Filter=@OBJ@.eq.1.and.@49@.eq.2`
- **Alt‑Notation** (66 Vorlagen ganz oder gemischt, z. B. `deu/Ausbau/Fenster, Türen/Fensteröffnungen.rdlc`): `Filter=@OBJ@=1031&@49@=2` – `=` für gleich, `&` (im XML `&amp;`) für UND.

Beim Ändern einer Datei den vorhandenen Dialekt beibehalten.

Im `Filter=…`‑Teil gelten folgende Operatoren und Funktionen:

### Vergleichsoperatoren (Punkt‑Notation!)

| Operator | SQL‑Gegenstück | Beispiel |
|----------|----------------|----------|
| `.eq.` | `=` | `@OBJ@.eq.1` |
| `.ne.` | `<>` | `@OBJ@.ne.61` |
| `.lt.` | `<` | `@233@.lt.1` |
| `.le.` | `<=` | `@222@.le.2.5` |
| `.gt.` | `>` | `@229@.gt.0` |
| `.ge.` | `>=` | `@215@.ge.1` |
| `&gt;&lt;` (im XML) / `><` (dekodiert) | `<>` (alternative Form) | `@232@><"L"` |
| `=` (direktes Zeichen) | `=` | `@OBJ@=1` |

### Verknüpfungen

| | Bedeutung |
|---|-----------|
| `.and.` | AND |
| `.or.` | OR |
| `!(…)` | NOT |
| `;` am Ende | Filter‑Abschluss (oft aber auch ohne); Semikolon ist optional, aber üblich |
| `\|` (Pipe) | Abkürzung für ODER zwischen Flags: `Filter=@793@|@792@` = `@793@.eq.1.or.@792@.eq.1` |

### Listen‑ und Stringfunktionen

| Funktion | Bedeutung |
|----------|-----------|
| `ELE(@X@;1;2;3)` | `@X@` ∈ {1,2,3} |
| `!ELE(@X@;…)` | Negation davon |
| `PARENT(@X@)` | Attribut vom Parent‑Objekt (Raum → Raumgruppe, Makro → Makrotyp, …) |
| `PARENT(PARENT(@X@))` | Zwei Ebenen nach oben |
| `MID(@X@;start;len)` | Teil‑String (1‑basiert) |
| `MT_Wand(…)` | Sonderfunktion „Wanddicke aus Makro berechnen" |
| `ROUND(@X@, n)` | (nur in RDL‑Expressions, nicht Filter) |
| `like "X*"` | Wildcard‑Match (in IIf‑Expression, nicht in Filter) |

### Filter‑Syntax mit Parametern (dynamische Attribute)

```
Filter=@611["0:__Allplan_PythonPart_TypeUUID__"]@.eq."0e6de672-a222-4c63-b900-47ce0c44b74e"
```

`@611[<key>]@` adressiert ein **benamtes Unter‑Attribut** – typisch für PythonPart‑Objekte, deren Typ‑UUID so abgefragt wird.

### Komplex‑Beispiele

```
Filter=(@OBJ@.eq.0.or.@OBJ@.eq.5.or.@OBJ@.eq.135.or.@OBJ@.eq.136.or.@OBJ@.eq.137.or.@OBJ@.eq.138.or.@OBJ@.eq.1766.or.@OBJ@.eq.1780).and.(@708@.eq."HALFEN-DEHA".or.@708@.eq."HALFEN".or.@708@.eq."Leviat".or.@1136@.eq."Leviat".or.@1136@.eq."Leviat AG".or.@1136@.eq."HALFEN".or.@1136@.eq."Halfen")

Filter=@MAK@.ne.2.and.!ELE(@OBJ@;60;61;1000).and.@230@.gt.0

Filter=(@OBJ@.eq.72.and.ELE(@18@;1;3;4;5;6;7;8;9;10;12)).or.@OBJ@.eq.1781

Filter=@OBJ@.eq.1780.and.(@18417@.gt.0.or.@18418@.gt.0)

Filter=@GW@.gt.0.and.@OBJ@.ne.1003
```

### Stringvergleich

String‑Vergleichswerte immer in doppelten Anführungszeichen: `@498@.eq."Schacht"`. In der XML‑Form werden die `"` als `&quot;` bzw. direkt belassen (beide Formen treten auf). Unicode, Umlaute und Wildcards (`*`) sind zulässig.

## 5. Berechnete Felder im Query (`f=…`)

`f=` erlaubt eine inline‑Rechenformel im Query (nicht RDL‑Expression!). Syntax‑Elemente:

- Arithmetik: `+ - * /`
- Vergleiche: `.eq. .ne. .lt. .le. .gt. .ge.`
- Verknüpfung: `.and. .or.`
- Konditional: `_IF_(<Bedingung>)<ThenWert>_ELSE_<ElseWert>`
- Verschachtelung erlaubt
- Funktionsaufrufe: `PARENT(@X@)`, `MID(@X@;1;2)`, `MT_Wand(…)`

### Beispiele

```
[Name=SingleWeight|f=@765@/@766@]

[Name=Counter|f=1]

[Name=FixBar10|f=_IF_((@OBJ@.ne.368.and.@OBJ@.ne.366).and.@799@.eq.0.and.@759@.eq.10.and.@423@.gt.0)@765@*@423@_ELSE_0|CountValues=1]

[Name=Region2005DIN277|f=_IF_(@231@.eq."R")"a"_ELSE_(_IF_(@231@.eq."S")"b"_ELSE_@231@)|Fmt=A3]

[Name=Occupancy2016DIN277|f=_IF_(@235@.eq."NF*")"NUF"+MID(@235@;3;2)_ELSE_@235@|Fmt=A4]

[Name=AreaType_a_B|f=_IF_((@231@.eq."a".or.@231@.eq."R").and.(@232@.eq."B"))@201@*@266@_ELSE_0|Fmt=F9.0]

[Name=Formula_1|f=PARENT(PARENT(@507@))|Dim=30]
```

## 6. Multiple SELECTs – DataSet‑Merge

```xml
<CommandText>
  SELECT @202@[Name=Unit]
    FROM [MODEL_DATA, Filter=@OBJ@=255]
  SELECT @508@[Name=Material], @207@[Name=Brief_text], @452@[Name=Story]
    FROM [SUBSIDIARY_MODELDATA]
  SELECT @215@[Name=Piece], @198@[Name=Absolut_Length|Fmt=F8.2], @225@[Name=Dimensions|Dim=30]
    FROM [QUANTITY_CALCULATION, Filter=@VOB@;]
</CommandText>
```

- Mehrere `SELECT … FROM …`‑Blöcke hintereinander werden zu einem DataSet gemergt, wenn eine der Tabellen `MergeDataSet=true` enthält.
- `ALLPLANDATA,MergeDataSet=true` wird häufig für Plankopf‑Zusatzattribute verwendet.
- Sonst werden separate DataSets aus separaten `<DataSet>`‑Blöcken im XML zusammengestellt.

## 7. WHERE (alternative Syntax)

Manche Reports nutzen nach `FROM [Tabelle]` ein explizites `WHERE`:

```
SELECT @507@[Name=Nodename], @1155@[Name=NodeType]
FROM [BUILDINGSTRUCTURE]
WHERE @OBJ@.eq.1766.and.@507@.eq."ListHeader"
```

Funktional äquivalent zu `Filter=` in der FROM‑Klausel. Beide Formen sind gültig. **Konvention**: bei `MODEL_DATA`, `Type=N`, `ENGINEERING`, `FLOOR_AREA_ARCHITECTURE` → `Filter=` in FROM; bei `BUILDINGSTRUCTURE`, `ALLPLANDATA`, `PROJECT`, `DOCUMENT` → oft `WHERE` separat.

## 8. CommandText‑XML‑Spezialitäten

- Newlines (`\n`) sind zulässig und wurden in vielen Vorlagen zur Lesbarkeit eingefügt.
- **Zeichen‑Entities beachten**: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`, `"` kann direkt stehen.
- Die Filter‑Form `@232@&gt;&lt;"U"` dekodiert sich zu `@232@><"U"` (= „ungleich U"). Beim Schreiben in neue Dateien immer als Entity `&gt;&lt;` schreiben.
- Anführungszeichen innerhalb der Query: einfache Strings in `"…"`; in XML nicht nötig zu escapen, da der CommandText selber in `<…>`‑Tags liegt.

## 9. ORDER BY / TOP / LIMIT

**Existiert nicht.** Die Sortierung erfolgt ausschließlich im RDL‑Teil (`<Sorting>` innerhalb `<TableGroup>`, siehe `07_Gruppierung_und_Tabellen.md`). `TOP`‑Klauseln gibt es nicht – stattdessen Filter.

## 10. JOIN

**Existiert nicht.** Jeder DataSet zieht aus **einer** Tabelle (optionally gemergt). Beziehungen werden über `PARENT(@X@)` und `f=` aufgelöst.
