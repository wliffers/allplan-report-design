# Muster: Bauteile, Abbruch, Neubau

Dieses Dokument enthält die konkreten Query‑ und Struktur‑Muster für alle architektonischen Bauteile (Wand, Decke, Stütze, Fundament, Fenster, Tür, Dachhaut, Unterzug, Treppe, Schornstein) sowie die spiegelgleichen Abbruch‑ und Neubau‑Varianten.

## 1. Das Abbruch/Neubau‑Prinzip

Jedes Architekturbauteil kann einen **Status‑Flag** `@49@` tragen:

| `@49@` | Bedeutung |
|--------|-----------|
| `0` | Neubau (Default in unverändertem Modell) |
| `2` | Abbruch |
| (fehlend / ‑1) | unspezifiziert |

In den Vorlagen sind Abbruch‑ und Neubau‑Reports **identisch aufgebaut**; einziger Unterschied ist der Filter:

```
Neubau:  Filter=@OBJ@.eq.1.and.@49@.eq.0
Abbruch: Filter=@OBJ@.eq.1.and.@49@.eq.2
```

Manche Bauteile vererben den Flag vom Parent, z. B. Dachhaut:
```
Filter=@OBJ@.eq.1000.and.PARENT(@49@).eq.2
```

Für ODER‑Kombinationen (z. B. Fenster‑ oder Tür‑Makros):
```
Filter=(@OBJ@.eq.991.or.@OBJ@.eq.992).and.@49@.eq.2
```

Wand‑Sonderreport „Wände Größer 2,5":
```
Filter=@OBJ@.eq.1.and.@49@.eq.2.and.@229@.gt.0.and.@229@.lt.-2.5
```
(Der Bereichsausdruck wirkt als Typenschutz: zusätzlicher Filter auf Geschossfläche.)

## 2. Muster Wand

### Wand – Basis (aus `Wände.rdlc` / `Walls.rdlc`)

```
SELECT
   @452@[Name=Story|Fmt=A30],
   @452@[Name=StoryIndex|Fmt=I6],
   @10@[Name=ComponentID|Fmt=I10],
   @83@[Name=Codetext|Fmt=A30],
   @508@[Name=Material|Fmt=A30],
   @507@[Name=Name|Fmt=A30],
   @225@[Name=Dimensions|Dim=30],
   @220@[Name=Length|Dim=1|Fmt=F8.2],
   @221@[Name=Thickness|Dim=1|Fmt=F8.2],
   @222@[Name=Height|Dim=1|Fmt=F8.2],
   @224@[Name=BaseArea|Fmt=F9.2],
   @223@[Name=Volume|Fmt=F9.3],
   @81@[Name=VOB_Area|Fmt=F9.2],
   @296@[Name=NetArea|Fmt=F9.2],
   @205@[Name=Graphics|Projection=9|Hidden=1|Width=45|Height=30|Scale=200|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.and.@49@.eq.0]
```

Gruppierung: `StoryIndex → Material → ComponentID`.
Aggregat: `Sum(Fields!Volume.Value)` im Group‑Footer.

### Wand nach Abrechnungsart (`Wände nach Abrechnungsart.rdlc`)

Zusätzlich `Type=99`‑Query für Schichten:
```
SELECT @210@[Name=TierNumber], @211@[Name=TierThickness], @99@[Name=NetQuantity|Fmt=F9.3]
FROM [Type=99, Filter=@OBJ@.eq.1;]
```

## 3. Muster Decke

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.4.and.@49@.eq.0]                     (neue Klasse: @OBJ@.eq.1005)
```

Spalten wie Wand + `@228@[Outline]`. Zusätzlich parallele Query für Deckenabzüge:
```
SELECT @224@[Name=OpeningArea|Fmt=F9.3]
FROM [Type=51, Filter=@OBJ@.eq.4.and.@224@&gt;0|@224@&lt;-2.5]
```

## 4. Muster Stütze

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.3.and.@49@.eq.0]
```
Spezifische Spalten:
- `@91@[Name=Corners|Fmt=I2]` – Eckenzahl (4 = rechteckig, 0 = rund)
- `@759@[Name=Diameter|Dim=3|Fmt=F6.0]` – Durchmesser
- `@225@[Name=Dimensions]` – Abmessungsstring

Projektion: `Projection=9` Draufsicht.

## 5. Muster Fundament

```
FROM [MODEL_DATA, Filter=(@OBJ@.eq.705.or.@OBJ@.eq.703.or.@OBJ@.eq.704.or.@OBJ@.eq.701).and.@49@.eq.0]
```
- `701` = Sonder, `703` = Einzel, `704` = Platte, `705` = Streifen
- `@226@[Name=Net_Volume]` – Nettovolumen
- `@224@[Name=BaseArea]`

## 6. Muster Unter-/Überzug

```
FROM [MODEL_DATA, Filter=(@OBJ@.eq.6.or.@OBJ@.eq.8).and.@49@.eq.0]
```
- `@OBJ@=6` Unterzug, `@OBJ@=8` Überzug

## 7. Muster Schornstein

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.10.and.@49@.eq.0]
```

## 8. Muster Dachhaut

```
SELECT … FROM [MODEL_DATA, Filter=@OBJ@.eq.1000.and.@49@.eq.0]
SELECT @201@[Name=Quantity|Fmt=F9.3] FROM [Type=67, Filter=@VOB@]
```
Zwei‑stufige Query: Materialliste (Type=0) + Abrechnungs‑Rows (Type=67).

## 9. Muster Fenster

### Einfach (`Fenster.rdlc`)

```
SELECT
   @452@[Name=Story],
   @83@[Name=Codetext|Fmt=A30],
   @507@[Name=Name|Fmt=A30],
   @215@[Name=Piece|Fmt=I6|CountValues=1],
   @220@[Name=Width|Dim=3|Fmt=F6.0],
   @222@[Name=Height|Dim=3|Fmt=F6.0],
   @205@[Name=Graphics|Projection=2|Hidden=5|Scale=100|Width=27|Height=27|GText=HD_CENTER]
FROM [MODEL_DATA, Filter=@OBJ@.eq.991.and.@49@.eq.0]
```

### Detailliert (`Fenster (detailliert).rdlc`)

Zusätzliche Felder:
- `@363@[Name=WingIdentifier]` – Flügelbitmask
- `@427@[Name=Swing]` – DIN L/R
- `@539@[Name=SmartPart]`
- `@207@[Name=Langtext|Dim=254]`
- `f=MT_Wand(PARENT(@221@))` → berechnet Wanddicke aus Parent‑Makro
- `f=PARENT(@507@)` → Elternraum‑Name

### Mit Preis

Variante mit zusätzlicher Preisspalte – via Attribut, das Herstellerdaten trägt (z. B. `@1102@` Hersteller‑Function). Nicht alle Projekte haben Preisdaten befüllt.

## 10. Muster Tür

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.992.and.@49@.eq.0]
```
Wie Fenster, mit zusätzlich:
- `@427@` Swing = „DIN R", „DIN L"
- Für SmartPart‑Türen: `Choose(Fields!WingIdentifier.Value And 3, "R","L","LR")`
- Für Classic‑Türen: `Switch(Fields!Swing.Value = "DIN R", "R", Fields!Swing.Value = "DIN L", "L")`
- Bitmask‑Interpretation für Anschlag: `Choose((WingIdentifier >> 2) And 3, "R","L","LR")`

Übergabe‑Varianten (`Türen (für Übergabe …).rdlc`):
- Kurzfassung: nur Hauptattribute
- Komplett: alle `@207@…@215@`
- Alle Attribute: `FROM [MODEL_DATA, Properties=48]` (lädt extended attributes)

## 11. Muster Treppe

```
FROM [MODEL_DATA, Filter=@OBJ@.eq.72.and.ELE(@18@;1;3;4;5;6;7;8;9;10;12)]
```
`@18@`‑Subtyp selektiert Treppenklassen (gerade, Wendel, Gewendelt, Podest). Für Auswertung aller Stufen und Maße → `Treppe - komplette auswertung.rdlc`.

## 12. Muster Räume (als Bauteil‑Kontext)

Siehe auch `11_Muster_Flaechen_Raeume.md`. Standard:
```
FROM [Type=0,Filter=@OBJ@.eq.61;]
```

## 13. Muster Öffnungen

```
FROM [Type=5, Filter=@OBJ@.eq.22]                    Türöffnungen
FROM [Type=5, Filter=@OBJ@.eq.28]                    Fensteröffnungen
FROM [Type=5]                                        Alle Öffnungen
```
`Type=5` liefert Öffnungs‑Sub‑Elemente der Eltern‑Wand.

## 14. Spiegelregel Abbruch ↔ Neubau

Beim Ableiten eines Abbruch‑Reports aus der Neubau‑Vorlage:

1. Dateikopie mit Präfix `Abbruch ` anlegen.
2. `<Author>`, `<Description>` und `Heading1.Value` anpassen.
3. **Nur** den `@49@`‑Filter umstellen: `.eq.0` → `.eq.2`.
4. Alle anderen Expressions, Spalten, Sortierungen bleiben.
5. Die englische Parallele benennt `Demolition – <teil>.rdlc`.

Gegenbeispiel: `Abbruch Dachhaut.rdlc` – dort wird `PARENT(@49@)` genutzt, weil die Dachhaut selbst keinen Status‑Flag trägt, aber ihre Parent‑Decke.

## 15. Häufige Expressions

```vb
=IIF(Parameters!Location_from_Room.Value = True,
     Fields!ParentName.Value,
     Fields!Text5.Value)

=IIF(Parameters!Display_Graphics.Value = False,
     Fields!Dimensions.Value,
     Fields!ComponentID.Value)

=Math.Round(Fields!Width.Value, 3)   ' Toleranz‑Normalisierung vor Gruppierung
```

## 16. Betonarbeiten (Spezialfall)

`Betonarbeiten - Ortbeton.rdlc` verschachtelt **drei** SELECT‑Blöcke in einem DataSet:

```
SELECT … FROM [Type=0, Filter=@GW@.eq.13.and.(@OBJ@.eq.1.or.@OBJ@.eq.3.or.@OBJ@.eq.4.or.@OBJ@.eq.6.or.@OBJ@.eq.8.or.@OBJ@.eq.10.or.(@OBJ@.ge.701.and.@OBJ@.le.705))]
SELECT … FROM [Type=5,  Filter=@GW@.eq.13]                  (Öffnungen)
SELECT … FROM [Type=19, Filter=@VOB@;]                       (Abrechnung)
```

Gruppierung über 4–6 Ebenen (StoryIndex → Material → ObjectIdentifier → FundamenteG_Group → CoID_Group → Details). Ausschluss spezieller Materialklassen über `!ELE(@MAK@;22;23;24;25;27;35)`.

## 17. Mauerarbeiten (Spezialfall)

```
FROM [MODEL_DATA, Filter=@GW@.eq.12.and.@OBJ@.eq.1]      (Wand, Mauergewerk)
FROM [Type=5,  Filter=@GW@.eq.12.and.@OBJ@.eq.1]           (Öffnungen)
FROM [Type=3,  Filter=@GW@.eq.12]                          (VOB‑Abrechnung)
```

Gruppierung: `GroupUnit → GroupMaterial → GroupBrief_text(Thickness_cm + Brief_text) → GroupID`.

## 18. Geschoss‑Sortierung

**Regel**: Nach `Fields!StoryIndex.Value` sortieren, **nicht** `Fields!Story.Value`. Nur das numerische Feld ergibt die tatsächliche Etagen‑Reihenfolge (UG, EG, 1.OG, 2.OG, …). Bei Namenssortierung steht „10.OG" vor „2.OG".

## 19. Summen‑Zeilen über Gewerk

Bei gemischten Reports (`Trades - overview.rdlc` / `Übersicht Gewerke.rdlc`) wird nach `@GW@` gruppiert. Aggregate:
```xml
<Value>=Sum(Fields!Quantity.Value)</Value>
<Value>=CStr(Sum(Fields!Quantity.Value)) + " " + First(Fields!Unit.Value)</Value>
```
