# Bewehrung in Reports

Stäbe und Matten aus dem Teilbild, in einer Abfrage. Belegstufen wie in `grenzen.md`: **A** = in Allplan 2027 ausgegeben (Testteilbild mit 12 Stabpositionen und 5 Matten;
zweites, echtes Projekt mit 6 und 8 Positionen, B500B, Ø 10, 12 und 14), **V** = Vorbild in Allplans 14 Bewehrungsvorlagen (`Etc\Reports\deu\Bewehrung`, englisch `eng\Reinforcement`; die
englischen Dateien haben wörtlich dieselben Abfragen).

## Abfrage (A)

```
FROM [ENGINEERING,Filter=@793@|@792@|@1210@]
```

- Filter: `@793@` Rundstahl, `@792@` Rundstahl polygonal verlegt, `@1210@` Matten. EINE Abfrage liefert beides.
- Stab hat `@OBJ@` 257, Matte 368. Spalte `[Name=ObjId|f=@OBJ@]`, Typ Int32. (V: Allplans Vorlage „Übersicht“ nennt 366 und 368 Matte.)
- `REINFORCEMENT_DATA` mit `@10@` schlug fehl. `ENGINEERING` nehmen.
- Ohne `@10@` fasst Allplan gleiche Zeilen zusammen (`daten.md`): `@10@` gehört in die Abfrage. Auch mit `@10@` werden gleiche Zeilen EINER Position zusammengefasst: Rechenregeln unten.

## Spalten (A)

Namen und Typen sind die des gemessenen Probe-Reports; der Typ steht im `<Field>` (`rd:TypeName`).

| Attribut | Name | Typ | Inhalt im Test |
|---|---|---|---|
| `@419@` | Bauteil | String | „Erdgeschoss“ |
| `@425@` | Teilbild | String | Teilbildname |
| `@452@` | Geschoss | String | „Erdgeschoss“ |
| `@10@` | Nr | String | Bauteil-ID, je Position eine |
| `f=@OBJ@` | ObjId | Int32 | 257 Stab, 368 Matte |
| `@799@` | Gebogen | Int32 | Stab: 0 gerade, 1 gebogen; bei Matten steht 1 |
| `@767@` | Position | Int32 | Positionsnummer |
| `@766@` | Anzahl | Int32 | Stück je Position |
| `@423@` | Ausfuehrungen | Int32 | 1 |
| `@759@` | Durchmesser | Double | mm (8 bis 28); Matte 0 |
| `@785@` | Bezeichnung | String | Stab „12“, Matte „Q188A“ |
| `@422@` | Stahlguete | String | B500B (Stab), B500A (Matte) |
| `@760@\|Dim=3` | Gesamtlaenge | Double | m |
| `@757@\|Dim=3` | Einzellaenge | Double | m |
| `@765@` | Gewicht | Double | kg einer Zeile; bei zusammengefassten Zeilen nicht summiert (Rechenregeln) |
| `@756@` | KgJeM | Double | Stab kg je m (Ø 12: 0,888); Matte 3,022 (Q188A), 4,116 (Q257A) |
| `@763@` | Biegeform | String | Schlüssel ISO 4066: 00 gerade, 11, 21, 51; Matte „00q“ |
| `@751@` | Mattenname | String | Q188A, Q257A |
| `@758@\|Dim=3` | MattenBreite | Double | m (2,3); Stab 0 |
| `@205@\|Projection=0\|Width=69\|Height=25\|GText=HD_CENTERMIDDLE\|CanSave=true` | Bild | Byte[] | Biegeform mit Maßen |

Bildfeld im Report (V: Allplans Stabliste mit Biegeform): `Image`, `Source Database`, `MIMEType image/jpeg`, `Sizing FitProportional`, Wert `=Fields!Bild.Value`. Das Bild ist klein, die Linien fein; `Width` und `Height` in mm.
Jede Zeile mit `@205@` kostet Rechenzeit (`grenzen.md`, Tempo): Bildspalte nur, wenn das Bild gezeigt wird. Biegeform-Bild und 3D-Bauteilbild sind zwei Bildarten, also zwei Reports.

## Rechenregeln (A: an zwei Teilbildern eines echten Projekts und am Probemodell mit Allplans Stabliste, Mattenliste und „Übersicht Bewehrung“ verglichen)

- **Allplan fasst gleiche Zeilen einer Position zusammen** (gleiche Nr `@10@`, gleiche Stückzahl). Dabei werden addiert: Anzahl (`@766@`), Gesamtlänge (`@760@`) und Einzellänge (`@757@`);
  das Gewicht (`@765@`) NICHT, es bleibt das Gewicht einer Zeile (ebenso `@423@`, `@799@`, `@767@`, `@759@`, `@756@`).
  Beispiel: Allplans Stabliste nennt für Position 1 152 Stück, 2,62 m, 398,24 m, 245,71 kg; die Abfrage lieferte zwei Zeilen mit Anzahl 80 und 72, Einzellänge 2,62 und 5,24, Gewicht 129,32 und 58,20.
- **Stab-kg immer Gesamtlaenge × KgJeM** (398,24 × 0,617 = 245,71), nie aus dem Feld Gewicht und nie `Sum(Gewicht)`: am echten Projekt ergab das 683,1 statt 944,6 kg Rundstahl.
  Dieselbe Formel rechnet Allplans „Stabliste Zusammenfassung“ (V). Nur bei nicht zusammengefassten Zeilen (Probemodell) ist `Gewicht` gleich `Gesamtlaenge × KgJeM`.
- Stück je Position = Summe Anzahl; Länge gesamt je Position = Summe Gesamtlaenge; Einzellänge = Summe Gesamtlaenge ÷ Summe Anzahl, nie das Feld Einzellaenge (bei zusammengefassten Zeilen ein Vielfaches: 12,64 statt 6,32 m).
- Meterware erkennt man an `@794@` ≥ 1 (Spalte `[Name=LfdM]`, String; in der Probe gemessen, als Spalte der Abfrage mit `@1210@` noch zu bestätigen): Stück 1, Länge „lfdm“, nie Überlänge; Gesamtlänge und kg wie bei Stäben.
- Matten: kg aus `@765@` je Matte (jede verlegte Matte ist eine Zeile mit eigener Nr, Anzahl 1). Mattenliste gruppieren je Teilbild, Bauteil, Position, Typ, Länge, Breite; Allplan rundet je Matte auf 2 Stellen (5 × 17,653 → 5 × 17,65 = 88,25 kg).
  Ob Allplan Matten zusammenfassen kann, ist nicht gesehen: dann stimmte `@765@` nicht.
- Ausführungen (`@423@`): Faktor je Zeile, in `@766@`, `@760@`, `@765@` nicht enthalten; Summen der „Übersicht“ sind Summe × Ausführungen (V: Allplans Vorlagen rechnen `@765@*@423@` bzw. mit dem Parameter `NumberOfComponents`).
  Gemessen ist überall Ausführungen = 1; **nicht an Daten mit Ausführungen über 1 bestätigt**.
- Summen, Report und Allplan gleich: echtes Projekt Teilbild A Rundstahl 944,61 kg, Matten 668,00 kg; Teilbild B 1.011,09 und 713,91 kg; Probemodell 912,56 und 217,85 kg.
- Kennzahlen: Positionen Stab `CountDistinct(Nr)`, Matte `CountDistinct(Teilbild|Bauteil|Position)`; Anteil gebogen = kg mit `@799@` = 1 ÷ kg Rundstahl; mittlerer Ø = `Sum(Ø × kg)` ÷ `Sum(kg)`.
- kg je Durchmesser: `Sum(IIf(Fields!Durchmesser.Value = CDbl(12), Fields!Gesamtlaenge.Value * Fields!KgJeM.Value, CDbl(0)))`.
- Stab oder Matte entscheidet die ObjId, nie ein Text, den die Abfrage setzt (`f=_IF_…"Matte"`): der Sprachschalter übersetzt Zeichenketten im Ausdruck, nicht Werte aus der Abfrage.
- Einheiten: Allplans Vorlagen schalten jede Zahl über `IsGlobalImperialUnit()` (V, nicht geprüft).

## Was nicht geht (A)

| Wunsch | Ergebnis | Weg |
|---|---|---|
| Schenkelmaße a bis j als Zahlen (`@798@` mit `Index`) | liefert 0 | die Maße stehen im Biegeform-Bild |
| Länge aus `@797@` | Text mit Komma („2,62“), bei Metermaterial „Lfdm“ | `@757@` mit `Dim=3` |
| `REINFORCEMENT_DATA` mit `@10@` | Abfrage schlägt fehl | `ENGINEERING` |
| Stab/Matte aus Abfragetext | englische Fassung falsch | `ObjId` |

Nicht geprüft: Bildparameter `GText=HD_CWF`, `MSSK` (Mattenschneideskizze), `BUTTON`; Attribute ohne Vorbild (Biegerolle `@18478@`, Betondeckung, Block `@18511@` bis `@18529@`); `Gebogen` bei Matten; Mattenbreite bei Anzahl über 1.

## Englische Begriffe (V: Allplans deutsche und englische Vorlagen im Vergleich)

| Deutsch | Englisch |
|---|---|
| Stabliste | Reinforcement schedule |
| Mattenstahlliste - Biegeformen | Mesh schedule - bending shapes |
| Matten - Schneideskizze | Mesh cutting diagram |
| Mengenliste | Quantities |
| Zusammenfassung der Stabliste | Summary of reinforcement schedule |
| Rundstahl / Matten | Reinforcing bars / Meshes |
| Position / Anzahl der Positionen | Mark / Number of marks |
| Anzahl / Stück | Number / Pcs. |
| Bauteil | Component |
| Stahlgüte | Steel grade |
| Einzellänge [m] / Gesamtlänge | Individual length [m] / Total length |
| Gewicht [kg] / Gesamtgewicht | Weight [kg] / Total weight |
| Masse [kg / m] / Gesamtmasse [kg] | Mass [kg / m] / Total mass [kg] |
| Summe / Summe über alle Bauteile | Sum / Sum of all components |
| gerade Stäbe / gebogene Stäbe | straight bars / bent bars |
| Alle Stabformen / Bemaßte Biegeform | All bar shapes / Dimensioned bending shape |
| Schenkel | Segment |
| Mattenbezeichnung / Typ | Mesh identifier / Type |
| Lagermatten | Custom meshes |
| Bearbeitet [kg] / Fix- und Lagerlängen | Edited [kg] / Fixed and stock lengths |
| Anzahl der Ausführungen | Number of elements (Kopf), Number of times (Attributname) |
| Durchmesser Ø 12 bis Ø 16 | Diameter Ø 12 to Ø 16 |

Allplans Übersetzung hat Fehler: „Gesamtmasse (…)“ steht dort als „Total volume (…)“ (Masse ist kein Volumen: nicht übernehmen), „Fixlängen [kg]“ und „bis“ in „Ø 8 bis Ø 10“ bleiben deutsch.
Attributnamen für Spaltenköpfe (Katalog): 767 Positionsnummer der Matten/Stäbe = Wwm/Reinf. bar marks, 766 Anzahl der Matten/Stäbe = No. of wwm/reinforcing bars, 759 Durchmesser = Diameter,
760 Gesamtlänge = Total length, 765 Gesamtgewicht = Total_weight, 422 Stahlgüte der Querschnittsreihe = Steel grade of cross-section catalog, 799 Lieferung verbogen = Delivery bent,
763 Stabform-Schlüssel ISO 4066 = Bar shape key ISO 4066.

