# Attribut‑Referenz (`@XXX@`‑Codes)

Alle Codes sind **numerische Attribut‑IDs** der Allplan‑Stringtabelle. Im Query‑Kontext liefern sie den Wert des Attributs für das aktuelle Objekt; im `<Prompt>`‑Kontext liefern sie eine lokalisierte Beschriftung.

## 0. Quelle der Wahrheit: der Attributkatalog von Allplan 2027

Jede ID wird gegen den Katalog der Installation geprüft, nicht gegen die Tabellen unten:

```
python <SKILL>/scripts/lookup_attribute.py 220 507 205
python <SKILL>/scripts/lookup_attribute.py --suche Wohnfläche
```

- Quelle: `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Xml\*AttributeDefinitionCollection*_{de,en}.xml` (Allplan 1–1999, Allplan2 ab 18001, _08 ab 27500, PassiveHouse ab 35100, Precast ab 36000, Bridge ab 37000, BSDD ab 45000; zusammen 2 438 Einträge).
- `lookup_attribute.py` liest den Katalog der Allplan-Installation. Ohne Allplan auf dem Rechner gibt es keinen Attributkatalog.
- Abgleich 2026-09-29: **jede** der rund 640 IDs, die im 2027‑Vorlagenbestand vorkommen, steht im Katalog. Findet das Skript eine ID nicht, ist sie falsch – nicht die Suche.

**Datentyp → `<rd:TypeName>`** (gezählt an allen Query‑Feldern der Etc‑2027‑Bibliothek):

| Datatype | Bedeutung | `rd:TypeName` | Beleg |
|----------|-----------|---------------|-------|
| `C` | Text | `System.String` | 3 351 von 3 574 Feldern |
| `R` | Zahl | `System.Double` | 1 614 von 1 662 |
| `I` | Ganzzahl | `System.Int32` | 951 von 1 061 |
| `B` | Grafik (`@205@`) | `System.Byte[]` | 315 von 315 |
| `E` | Aufzählung (z. B. `@49@` Status) | `System.String` | 112 von 112 |
| `D` | Datum | `System.DateTime` oder `System.String` | je 17 |
| `S`, `P`, `Y` | Textliste / ? | – | im Bestand nicht als Feld belegt |

Abweichungen (z. B. `C` als `Int32`) kommen vor, wenn ein Textattribut Zahlen trägt – dann dem Vorbild folgen.

Die folgenden Tabellen sind eine **kuratierte Auswahl** aus dem älteren Bestand (~400–500 IDs, ~12 400 Vorkommen in 520 Vorlagen), nach Themen geordnet.

## 1. Kopf‑ und Prompt‑IDs (in `<Prompt>`)

| `@XXX@` | Zweck |
|---------|-------|
| `@20@` | Bearbeiter |
| `@69@` | E‑Mail |
| `@70@` | Firmenlogo‑Pfad |
| `@302@` | Telefonnummer |
| `@401@` | Datum |
| `@402@` | Zeit |
| `@405@` | Projektname |
| `@410@` | Firmenname |
| `@411@` | Firmenadresse |

Diese werden nur in `<Prompt>` verwendet, nie als Datenfeld.

## 2. Basis‑Objektattribute (sehr häufig)

| Code | Bedeutung | Datentyp |
|------|-----------|----------|
| `@10@` | Element‑ID / Component‑ID | Integer |
| `@16@` | Attribut‑Name (generisch) | String |
| `@17@` | Attribut‑Wert (generisch) | String |
| `@71@` | Image‑ID / Grafik‑ID | Int/Byte[] |
| `@120@` | Einheit (z. B. „m³") | String |
| `@198@` | Absolut_Length | Double |
| `@199@` | Absolut_Thickness / Dicke | Double |
| `@201@` | Quantity / Mengenauswertung | Double |
| `@202@` | Unit / Einheit | String |
| `@204@` | Absolut_Height | Double |
| `@205@` | Graphics (Vorschaubild) | Byte[] |
| `@206@` | AreaNumber / Flächennummer | Int |
| `@207@` | Kurztext / Brief_text | String |
| `@208@` | Langtext | String |
| `@209@` | Gewerk‑Code | Int |
| `@214@` | Bauteilnummer | String |
| `@215@` | Stückzahl / Piece | Int |
| `@220@` | Length / Länge | Double |
| `@221@` | Thickness / Dicke | Double |
| `@222@` | Height / Höhe | Double |
| `@223@` | Volume / Volumen | Double |
| `@224@` | BaseArea / Grundfläche | Double |
| `@225@` | Dimensions / Abmessungs‑String (z. B. „3.40 × 5.20 = 17.68") | String |
| `@226@` | Net_Volume | Double |
| `@228@` | Outline / Umfang / Umriss | Double |
| `@229@` | Geschossfläche / Surface | Double |
| `@230@` | Generic Quantity | Double |
| `@293@` | Bodenfläche (Ausbau) | Double |
| `@294@` | Deckenfläche (Ausbau) | Double |
| `@296@` | Netto‑Fläche | Double |
| `@419@` | Component / Bauteil (Name) | String |
| `@420@` | Listnumber | Int |
| `@422@` | Steelgrade / Stahlgüte | String |
| `@423@` | NumberOfComponents | Int |
| `@425@` | ComponentbyTBName / Teilbild‑Bauteilname | String |
| `@452@` | Story / Geschoss‑Name bzw. Index | String/Int |
| `@495@` | SteelgradeShort | String |
| `@498@` | **ObjectName** / Objektname | String |
| `@505@` | Text5 | String |
| `@506@` | Function / Zweckbestimmung | String |
| `@507@` | Name / Bezeichnung (Raum, Bauteil, Parent) | String |
| `@508@` | Material | String |
| `@512@` | Teilbild‑Nr / DocumentNumber | String/Int |
| `@538@` | Macro‑Untertyp | String |
| `@539@` | SmartPart / Macro‑Name | String |
| `@611[<key>]@` | PythonPart‑benamtes Sub‑Attribut (z. B. `"0:__Allplan_PythonPart_TypeUUID__"`) | String |

## 3. Spezial‑Objekt‑Kategorien (`@OBJ@`)

`@OBJ@` ist der Objekttyp‑Code. Die wichtigsten Werte:

| `@OBJ@` | Objekt |
|---------|--------|
| `0` | Beliebiges (Makro‑unabhängig) |
| `1` | **Wand** |
| `3` | Stütze |
| `4` | Decke |
| `5` | Generischer Körper |
| `6` | Unterzug |
| `8` | Überzug |
| `10` | Schornstein |
| `11`, `13` | Weitere Betonbauteile |
| `22` | Türöffnung |
| `60` | Grundfläche (BGF/NGF) |
| `61` | **Raum** |
| `62` | Seitenfläche (Ausbau Wand) |
| `63` | Deckenfläche (Ausbau) |
| `64` | Bodenfläche (Ausbau) |
| `65` | Ausbaufläche (allgemein) |
| `69` | Raumgruppe / Apartment |
| `72` | Spezial‑Makro (div.) |
| `81` | Gebäude |
| `100` | Montagebauteil (Schachtbauwerk, PythonParts) |
| `112` | Geschoss (Allfa) |
| `135`, `136`, `137`, `138` | Einbauteile |
| `255` | Generisches 3D‑Körper |
| `366`, `368` | Matten‑Objekte |
| `701`, `703`, `704`, `705` | Fundament‑Varianten |
| `972`, `1003` | Sonder‑Einbauten |
| `979` | Leitung (Rohrsegment) |
| `980` | Leitungspunkt |
| `991` | Fenster‑Makro |
| `992` | Tür‑Makro |
| `997`, `998` | BMZ‑Flächen |
| `999` | Hüllflächen |
| `1000` | Dachhaut |
| `1005` | Decke (neue Klasse) |
| `1011` | Dachflächenfenster |
| `1013` | Einbauteil mit Lokaleinbau |
| `1031` | Abbruchkörper |
| `1080`, `1081`, `1089` | Ortbeton‑Klassen |
| `1136` | (als Attribut: Manufacturer) |
| `1405` | (Geo‑Anlage) |
| `1415` | Bauseitige Bewehrung (mit Flag `@1415@.eq.3`) |
| `1417` | Formbau‑Kategorie |
| `1766` | Listenkopf |
| `1768`, `1780`, `1781` | Sonder‑Ausbauten / Baugrube |
| `3001`, `3002`, `3004`, `3005`, `3006` | Haustechnik, Heizung, Sanitär |
| `14101`, `14106` | Formbau‑Schalungselemente |
| `21051`, `21250` | Dach‑/Makrowurzel (ROOTOBJ) |

Auswahl per Disjunktion:
```
Filter=@OBJ@.eq.1.or.@OBJ@.eq.3.or.@OBJ@.eq.13   (Wände + Stützen + Betonsonder)
Filter=ELE(@OBJ@;62;63;64;65)                     (alle Ausbauflächen)
Filter=ELE(@OBJ@;991;992)                         (Fenster‑ oder Türmakro)
```

## 4. Geometrie / Abrechnung

| Code | Bedeutung |
|------|-----------|
| `@49@` | **Neubau/Abbruch‑Flag** (`0`=Neubau, `2`=Abbruch, `-1`=unspezifiziert) |
| `@81@` | VOB‑Fläche |
| `@82@` | Grundfläche (Kontur) |
| `@83@` | Codetext / Material‑Code |
| `@91@` | Eckenzahl (Stütze rund vs. eckig) |
| `@99@` | Netto‑Menge |
| `@163@` | X‑Koordinate |
| `@164@` | Y‑Koordinate |
| `@165@` | Z‑Koordinate |
| `@194@` | Position‑Mark |
| `@210@` | TierNumber / Schicht |
| `@211@` | Thickness der Schicht |
| `@363@` | WingIdentifier (Türflügel) |
| `@427@` | Swing / Anschlag (DIN L/R) |
| `@708@` | Hersteller (Leviat/HALFEN) |
| `@759@` | Durchmesser (mm) |
| `@764@` | Pipework‑Subtyp („Schacht", „Rohr", „Formteil", „Zulauf", „Ablauf") |
| `@800@` | Punktnummer (DGM) |
| `@856@–@878@` | Lieferadresse‑Felder Stabliste |
| `@903@` | Elementbezeichnung (FF‑Korb) |
| `@1081@` | Gesamtgewicht Bügelkorb |
| `@1126@` | Deckelhöhe (Schacht) |
| `@1127@` | Sohlenhöhe (Schacht) |
| `@1136@` | Manufacturer (Leviat/HALFEN alt) |
| `@1155@` | NodeType (BWS) |
| `@1165@` | Schachtnummer |
| `@1167@` | DKBemerkung |
| `@1178@` | Schachthöhe |
| `@1188@` | Leitungs‑Kennung („AW Ltg", „WA Ltg", „AW LtgP", „WA LtgP") |
| `@1236@` | Alt‑Hersteller‑Feld |
| `@1360@` | DGM‑Nummer |

## 5. Räume / Flächen / DIN277

| Code | Bedeutung |
|------|-----------|
| `@68@` | Wohnfläche (WoFlV‑Ergebnis) |
| `@231@` | Region (R/S/a/b/c – DIN277 2005/2016) |
| `@232@` | AreaType (B=Brutto, U=Unterm Dach, M=Mittelträger, V=Vertikal, N=Netto, L=Loggia, …) |
| `@233@` | WoFlV‑/Gültigkeits‑Flag (`< 1` = gültig) |
| `@234@` | GRZ‑Flag |
| `@235@` | Nutzungsart DIN277 (NUF, HNF1…7, VF, TF, NF*, …) |
| `@246@` | StoryName |
| `@250@` | GFZ‑Flag |
| `@264@` | Factor WoFlV (1 / 0.5 / 0.25) |
| `@266@` | FactorDIN277 |
| `@315@` | Allfa‑Nutzungstext |
| `@497@` | FloorAreaLessPercentage |
| `@551@–@560@` | Grundstücks‑Kennwerte (Nutzung, Flurstück, GRZ, GFZ, BMZ, Dachform, Vollgeschosse) |
| `@565@` | Vollgeschosse |
| `@567@` | Wohneinheiten |
| `@568@` | Obergeschosse |
| `@ROOTOBJ@` | Wurzel‑Objekttyp |

## 6. Bewehrung

### Stab

| Code | Bedeutung |
|------|-----------|
| `@741@` | SegmentLengthBS (Array, Index 1..5) |
| `@756@` | Mesh/Bügel‑Einzelgewicht |
| `@757@` | Length (einfach) |
| `@760@` | TotalLength |
| `@761@` | DiameterComment |
| `@763@` | BendingKey (Biegeschlüssel ISO) |
| `@765@` | Mass / TotalWeight |
| `@766@` | NumberOfBars |
| `@767@` | Position / MarkNumber |
| `@785@` | Diameter (BS/SANS) |
| `@786@` | BendingFormKeyBS |
| `@792@` | Polygonal‑Flag |
| `@793@` | Stabfilter‑Flag |
| `@794@` | LfdM |
| `@795@` | MarkBarSegment / MarkNumberAndIndexMesh |
| `@797@` | Einzellänge |
| `@798@` | BarSegment_a..j (Index 1..10) |
| `@799@` | StraightBar‑Flag |
| `@1208@` | TypeAndSizeforBS |
| `@1210@` | Mattenfilter‑Flag |
| `@1437@` | SegmentLength‑ISO (Index 1..8) |
| `@1438@` | BendingKey‑ISO |

### Matten

| Code | Bedeutung |
|------|-----------|
| `@751@` | Meshname |
| `@752@` / `@753@` | OverlapL / OverlapQ |
| `@754@` / `@755@` | QuantityL / QuantityQ |
| `@768@` / `@769@` | BarGap_L / BarGap_Q |
| `@770@–@773@` | BarDiameter DS1..4 |
| `@774@–@777@` | Bars_Border_L/R/S/E |
| `@778@` | DoubleRod |
| `@779@–@782@` | Overlap_A/E/L/R |
| `@783@` / `@784@` | Length_KS_AK / Length_KS_LK |
| `@1213@` | Meshtype |

### Bewehrungskörbe / MSA / AB / Leviat

| Code | Bedeutung |
|------|-----------|
| `@1044@` | FF‑Korb‑Flag |
| `@1045@` | FFBuegelkoerbe_Kode |
| `@1046@` | Sortierungsnummer |
| `@1047@` | Stirrup cages (from stock)‑Flag |
| `@1048@` | Stirrup cages (special reinforcement)‑Flag |
| `@1102@` | Hierarchic_function (Leviat) |
| `@1415@` | Bauseitig‑Stabliste‑Flag |
| `@1450@–@1454@` | AB‑Felder: Bezeichnung / Anzahl / Zulagen / Gewicht / Wanddicke |
| `@1982@` | MSA‑Bewehrungsgruppen‑Flag |
| `@18417@`, `@18418@` | Baugrube Cut/Fill |

## 7. Projekt / Layout / Dokumente

| Code | Bedeutung |
|------|-----------|
| `@368@` | ProjectAvailability |
| `@403@` | Projecthost |
| `@409@` | Nodename (BWS) |
| `@412@` | Projectpath |
| `@425@` | Documentname / Zeichnungsname |
| `@430@` | Groupingcode |
| `@431@` | Owner |
| `@432@` | Created |
| `@433@` | Modificationdate |
| `@436@` | Size |
| `@449@` | Version |
| `@518@` | Level (Einrücktiefe BWS) |
| `@697@` | Projectnumber |

## 8. Systemattribute (Pseudo‑Felder)

| Code | Zweck |
|------|-------|
| `@OBJ@` | Objektart (siehe §3) |
| `@GW@` | Gewerk (13=Beton, 12=Mauer, 36=Boden, 39=Trockenbau, …) |
| `@MAK@` | Makrotyp (0=Inventar, 62–65=Ausbau, 22–27/35=Spezialausbau, 2=Besondere Ebene) |
| `@VOB@` | VOB‑Abrechnungsflag |
| `@ROOTOBJ@` | Wurzel‑Objekttyp (Makrofamilie) |

## 9. SVG / Besondere Felder

| Code | Bedeutung |
|------|-----------|
| `@87@` | SVG‑Map‑Content (als Text/SVG) |

Einsatz: `@87@[Name=SVG_Map|Dim=254]` – nur in `Mengen (SVG Map).rdlc` verwendet. Rendert im Textbox `=Fields!SVG_Map.Value`.

## 10. Regeln für KI‑Arbeit mit Attributen

1. **Nie IDs raten.** Jede Annahme anhand der Referenzvorlage aus `01_Dateiuebersicht_und_Kategorien.md` verifizieren, dann übernehmen.
2. **Sprachunabhängig.** Die Attribut‑IDs sind dieselben in DE/EN/FR/CH. Nur der angezeigte Prompt wechselt über die Stringtabelle.
3. **Mehrfachverwendung** desselben Attributs (`@205@`, `@452@`) ist erlaubt und üblich – jeweils mit eigenem `Name=`.
4. **Unbekannte IDs**: Liegt die gewünschte ID nicht in obiger Liste, zuerst `lookup_attribute.py` (§0), dann im Referenz‑Report nachschlagen – lieber direkt lesen als raten.
5. **Plausibilitätscheck**: `@49@`‑Filter muss zu Abbruch/Neubau passen; `@233@.lt.1` ist immer WoFlV‑Flag; `@232@`‑Regionen sind `B/U/M/V/N/L`; `@OBJ@` im einstelligen Bereich = Architekturbauteile, 3‑stellig = Makros, 4‑stellig = Spezial.

## 11. Neu im Allplan‑2027‑Bestand

Diese IDs kommen erst in den 2027‑Vorlagen vor (nicht im älteren flachen Bestand). Name und Datentyp aus dem 2027‑Katalog; Vorbild relativ zu `<RDLC>/`, Zahl = Anzahl Vorlagen.

| ID | Name (Katalog 2027) | Datatype → TypeName | Vorbild |
|----|---------------------|---------------------|---------|
| `@521@` | Topologie_Index_Struktur | I → Int32 | `deu/Gewerke/Betonarbeiten/Betonarbeiten - Ortbeton.rdlc` (52) |
| `@522@` | Topologie_Index_Gebäude | I → Int32 | wie `@521@` (52) |
| `@524@` | Topologie_Index_Geschoss | I → Int32 | wie `@521@` (52) |
| `@528@` | Topologie_Index_Standort | I → Int32 | wie `@521@` (52) |
| `@440@` | Anzahl_Änderungen | I → Int32 | `deu/Fertigteile/001_Fertigteil EL. für Wand&Decke (BS+ID).rdlc` (4) |
| `@1058@` | Stahlgewicht | R → Double | wie `@440@` (4) |
| `@1063@` | Material Fertigteil | C → String | wie `@440@` (6) |
| `@1075@` | Fertigteiltyp | C → String | wie `@440@` (6) |
| `@1464@` / `@1466@` | Zusatz‑ID / Zusatz‑IDs (selbe Positionsnr.) | C → String | wie `@440@` (4) |
| `@1877@` / `@1929@` | Fertigteil‑ID / Fertigteil‑IDs (selbe Positionsnr.) | I / C | wie `@440@` (4) |
| `@36001@` | Elementbezeichnung | C → String | wie `@440@` (10) |
| `@36094@` / `@36095@` | Precast‑Elementtyp / Stückfaktor | I → Int32 | wie `@440@` (4) |
| `@1074@` `@1079@` `@1080@` | Pos‑Nr. für Stapelliste / Stapelnummer / Sortierungs‑ID | I → Int32 | `deu/Fertigteile/050_Stapelliste.rdlc` (2) |
| `@1077@` `@1089@` `@1983@` | Abmessungen [m] / Seitenumbruch / Stapelbezeichnung | C → String | wie `@1074@` (2) |
| `@1857@` | LKW Nummer | I → Int32 | wie `@1074@` (2) |
| `@1350@` | Katalogslistentext | C → String | `deu/Fertigteile/003_Einbauteile pro Element.rdlc` (2) |
| `@1461@` / `@1463@` | Gitterträgerbezeichnung / ‑gewicht | C / R | `deu/Fertigteile/006_Gitterträger pro Element.rdlc` (2) |
| `@1943@` `@1946@` | Pos‑Nr. / Anzahl der Matten/Stäbe im Elementplan | I → Int32 | `deu/Fertigteile/004_Rundstahl pro Element.rdlc` |
| `@1948@` `@1955@` | Gewicht / Länge der Matten/Stäbe im Elementplan | R → Double | wie `@1943@` |
| `@1905@` | Betonfestigkeitsklasse | C → String | `deu/Grundbau/Bohrpfahlwand.rdlc` (2) |
| `@18316@` / `@18320@` | Bohrverfahren / Größtkorn | C → String | wie `@1905@` (2) |
| `@18321@` / `@18322@` | Stahlgüte / Trägereinbau | C → String | `deu/Grundbau/Trägerbohlwand.rdlc` (2) |
| `@611@` (ohne Schlüssel) | NOI_StringVectorObject | S | `deu/Grundbau/Baugrube Bediener Übersicht.rdlc` (2) |
