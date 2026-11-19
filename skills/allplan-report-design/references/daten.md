# Daten aus Allplan: eine Abfrage für alles

Alles im echten Allplan 2027 gemessen (Test-Teilbild des Masters, Export PDF/XLSX). Schema 2005 oder 2016.

## Kernregel

- **Nur das ERSTE DataSet wird gefüllt.** Jedes weitere hat 0 Zeilen (egal ob `MODEL_DATA`, `PROJECT`, `LAYOUT`, `MergeDataSet=true`,
  anderer Name). Reihenfolge getauscht = das andere ist gefüllt. Aggregate über ein leeres zweites DataSet: 0/leer, kein Fehler.
  Auch ein Unterbericht führt keine eigene Abfrage aus: Allplan gibt ihm die Zeilen des Hauptreports, gefüllt werden Felder gleichen Namens.
- Mehrere `SELECT … FROM [Type=0…]` in einem DataSet: nur das erste liefert Zeilen. Unter-Tabellen (`Type=2`, `Type=35`) kommen als
  Folgezeilen unter der Hauptzeile (Hauptspalten leer); allein liefern `Type=2/3/5/10/18/19/34/35` nichts.
- **Eine breite Abfrage, Trennung im Report** per Tabellen-/Diagrammfilter auf die Objektnummer
  (`Val(Fields!ObjNr.Value)=991`) und `Sum(IIf(…), "AllplanReport")`.
- Schreibweisen gleichwertig: `FROM [Type=0,Filter=…;]`, `[Filter=…,Type=0]`, `[MODEL_DATA, Filter=…]`. `FROM [MODEL_DATA]` ohne
  Filter = 129 Zeilen im Test-Teilbild und enthält Sammelobjekte und Öffnungen mit **negativer** Fläche → immer nach `@OBJ@` filtern.

## Objektnummern (`@OBJ@`, Feld per `[Name=ObjNr|f=@OBJ@]`)

| Nr | Objekt | Art |
|---|---|---|
| 1 | Wand | Hauptbauteil, **eine Zeile je Wandschicht** |
| 3 / 4 / 6 / 704 | Stütze / Decke / Unterzug / Bodenplatte | Hauptbauteil |
| 61 | Raum | Raum |
| 991 / 992 | Fenster- / Tür-SmartPart (Makro) | positive Fläche |
| 43 / 42 | Fenster- / Türelement | Öffnung, negative Fläche/Volumen |
| 23 / 22 | Fenster- / Türöffnung (je Wandschale) | negative Werte |
| 2, 1005, 1107, 1095, 1094 | Gesamtwand, Decke gesamt, Gesamt-Plattenfundament, Gesamtfenster-/türöffnung | **Sammelobjekte** (Fläche/Volumen 0) |

Nicht aufnehmen: Sammelobjekte und Öffnungszeilen (verfälschen Summen). Rohbau-Filter (24 Zeilen im Test-Teilbild): `@OBJ@.eq.1.or.@OBJ@.eq.3.or.@OBJ@.eq.4.or.@OBJ@.eq.6.or.@OBJ@.eq.704`.
Decke/Bodenplatte: `@221@` = Plattenbreite, Stärke steht in `@222@` (Hilfsspalte `Staerke = _IF_(@OBJ@.eq.4.or.@OBJ@.eq.704)@222@_ELSE_@221@`).
Stütze: `@229@` = Mantelfläche. `@97@`/`@98@` UK/OK in **Millimeter**, `@204@`/`@222@` in Meter.

## Master-Abfrage (master/bausteine.py, wörtlich)

```
SELECT
       @498@[Name=Objekt],
       [Name=ObjNr|f=@OBJ@],
       @507@[Name=Bezeichnung],
       @506@[Name=Funktion],
       @508@[Name=Material],
       @209@[Name=Gewerk],
       @220@[Name=Laenge],
       @221@[Name=Dicke],
       @222@[Name=Hoehe],
       @229@[Name=Flaeche],
       @223@[Name=Volumen],
       @10@[Name=Nr],
       @205@[Name=Bild|Projection=9|Width=60|Height=40|Hidden=5|GText=HD_CENTERMIDDLE]
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.or.@OBJ@.eq.3.or.@OBJ@.eq.4.or.@OBJ@.eq.6.or.@OBJ@.eq.704.or.@OBJ@.eq.61.or.@OBJ@.eq.991.or.@OBJ@.eq.992]
```
Feldtypen im Bausatz: Laenge…Volumen `Double`, Bild `Byte[]`, alle übrigen `String` (auch `ObjNr`, daher `Val(Fields!ObjNr.Value)`).
Weitere Spalten (gemessen): Art als Formel `[Name=Art|f=_IF_(@OBJ@.eq.61)"Raum"_ELSE__IF_(@OBJ@.eq.991)"Fenster"_ELSE__IF_(@OBJ@.eq.992)"Tuer"_ELSE_"Bauteil"]`,
`[Name=UK_m|f=@97@/1000]`, `@120@` Einheit, `@224@` Grundfläche, `@226@` Nettovolumen, `@452@` Geschoss, `@683@` IFC-GUID (eindeutig, `@10@` ist stabiler für Verweise),
`@49@` Status. Vollständige Spaltenliste in einem Lauf: nicht geprüft.

## Zusammenfassen und Sortieren

- Allplan **fasst identische Zeilen zusammen** (17 Objektnamen statt 129 Zeilen) – ohne ID-Spalte (`@10@`) schrumpft das Ergebnis.
  `CountValues=1` summiert dann die zusammengefassten Zeilen.
- Sortierung **aufsteigend nach den Spalten in Abfragereihenfolge**. Kein `GROUP BY`: Summen/Gruppen im Report.

## Attribute je Objektart

| Objekt | Werte tragen (gemessen) |
|---|---|
| Raum 61 | Name in **`@506@` Funktion** (nicht `@507@`); `@224@` Grundfläche, `@248@` Netto, `@68@` Wohnfläche (als **Double** typen, als String Formeltext), `@228@` Umfang, `@222@` Höhe, `@223@` Volumen, `@249@` Netto-Rauminhalt, `@235@` DIN 277, `@232@` Flächenart, `@683@`. Leer: `@507@`, `@326@`, `@244@/@245@`, `@1101@` |
| Fenster 991 / Tür 992 | `@220@` Breite, `@222@` Höhe, `@229@` Fläche, `f=@97@/1000` Brüstung (m), `f=@98@/1000` Oberkante, `@427@` Anschlag, `@694@` Art, `@507@` Typ, `@71@` Typ-Nr, `@453@` Raumname; Fenster zusätzlich `@1228@/@1229@` Fensterbank, `@1105@` Lichte Höhe |
| Zugehörigkeit | `PARENT(@10@)` = **Raum**-ID (nicht die Wand); `MT_Wand(@10@)` Wand-ID, `MT_Wand(@508@)` Material, `MT_Wand(@221@)` Dicke, `MT_Wand(@209@)` Gewerk; `MT_Wand(PARENT(@221@))` Wanddicke; `MT_Raum(@506@)` Raumfunktion |
| leer/0 | `MT_Fenstermakro(@83@)`, `MT_Tuer(MT_Tuermakro(@83@))`, `PARENT(PARENT(…))`; immer leer: Layer `@141@`, Stift `@122@`, Gewicht `@721@`, U-Wert `@981@`, Brand-/Schallschutz, Preis → am Bauteil nicht gesetzt |

Fester Text mit `@<Nr>@` (z. B. Kopfzelle „Geschoss @452@“) wird **ganz durch den Attributnamen** der Programmsprache ersetzt.

## Rechnen in der Abfrage (`f=`), `Dim=`

| Konstrukt | Beispiel |
|---|---|
| Arithmetik, `ABS()`, `/1000.` | `f=@229@*@221@`, `f=ABS(@229@)`, `f=@223@/1000.` |
| `_IF_(…)a_ELSE_b`, verschachtelt, Platzhalter `*`, Text | `f=_IF_(@508@.eq."Beton*")"B"_ELSE_"X"` |
| Text | `f=@498@+" ("+@508@+")"`, `f=MID(@10@;1;4)`, `f=VALUE(MID(@10@;8;10))`, `f=FORMAT("%.2f";@229@)` (Punkt) |
| Konstante, Objektnummer | `f="Text"`, `f=@OBJ@` |

`Dim` an Länge: 1 = ×100 (cm), 2 = ×10, 3 = ×1, 4 = ×0,1. Fläche/Volumen folgen **anderen** Faktoren: `Dim` dort nicht benutzen.
`Fmt=`, `TotalValue`, `Index`: nicht belastbar, im Report mit `Format(x,"N2")` runden. XLSX rundet Doubles auf 3 Stellen, PDF/String voll.

## Projekt- und Deckblattdaten

- Projekttabellen (`CURRENT_PROJECT`, `DOCUMENT`, `LAYOUT`, `PROJECT`, `BUILDINGSTRUCTURE`, `LAYOUT_DRAWINGS`) liefern als ERSTE Abfrage Zeilen und werden als PDF und DOCX normal ausgegeben
  (18 Proben); nur die Ausgabe als XLSX öffnet das Report-Fenster statt einer Datei. `LAYOUT_HISTORY`, `ATTRIBUTES` und `FILESET` mit `WHERE @1155@.eq."Item"` blieben ohne Zeilen.
  Als zweites DataSet sind sie leer: ein Report auf einer Projekttabelle hat keine Bauteildaten. Tabellen und Spalten: `projektlisten.md`.
- Brauchen Bauteile UND Projektdaten denselben Report, dann Spalten der Modellabfrage: `@405@` Projektname, `@697@` Projektnummer, `@431@` Eigentümer, `@449@` Programmversion, `@20@` Benutzer,
  `@401@` Datum (als String typen), `@451@` Gebäude, `@452@` Geschoss, `@425@`/`@4@` Teilbildname/-ID, `@1501@/@1502@` Referenzebenen, `@70@` Firmenlogo-Pfad.
  Oft leer: `@460@` Bauherr, `@1093@/@1094@` Bauvorhaben, `@991@`, `@410@/@411@`, `@479@`, `@15@`.
- Oder Standardparameter (Namen/Prompts wie `Template_Grouping0_2005.rdlc`): `Project_Name`, `Edited_By`, `Date`, `Time`, `Company_Logo`, `Company_Name`, `Company_Address`, `Telephone_Number`, `E_Mail`, `Display_Logo`, `PageNo_1`, `Note`.

## Bewehrung

- Stäbe und Matten kommen aus EINER Abfrage: `FROM [ENGINEERING,Filter=@793@\|@792@\|@1210@]`; Stab `@OBJ@` 257, Matte 368 (Nummern 366 und 368 gelten in Allplans Vorlagen als Matte).
  `REINFORCEMENT_DATA` mit `@10@` schlug fehl. Spalten mit Typ, Rechenregeln, Biegeform-Bild, englische Begriffe: `bewehrung.md`.

## Parameter

- Von außen setzbar ist nichts: `ExportDrawingFileReport` nimmt keine Parameter. Es gelten `DefaultValue` oder der Prompt-Attributwert; im Betrachter editierbar.
- Welche Vorgaben Allplan annimmt (feste Werte ja, Ausdrücke und `DataSetReference` nein, Integer ohne Vorgabe scheitert): `grenzen.md`, Abschnitt „Parameter (Stellschrauben)“. Float `3.14` → Ausgabe `3,14`.
- `<Prompt>@405@</Prompt>` (Projektname), `@452@` (Geschoss) bindet den **Attributwert** und überschreibt einen DefaultValue. `DefaultValue` `@431@` bleibt Text.
- Parameter mit Vorgabe stehen im Betrachter unter „Benutzerinteraktion“.

## Sprache, Kultur, Ausdrücke

- Kultur de-DE: `Format(1234.5678,"N2")` = `1.234,57`, `"P1"` = `25,6 %`, `FormatCurrency` = `1.234,50 €`; `CDbl("1234,5")` = 1234,5, `CDbl("1234.5")` = **12345**.
- `<Language>en-US</Language>` oder `de-CH` am **Report** wirkt; am Textfeld (`<Style><Language>`) nicht. `Globals!ReportName`, `ExecutionTime`, `User!UserID` verfügbar.
- `&` immer mit Leerzeichen (`"a" & x`), sonst Abbruch BC30277. `Globals!PageNumber`/`TotalPages` nur in Kopf-/Fußzeile (im Body Abbruch).

## Eigener Code

- `<Code>` mit VB-Funktionen läuft (`=Code.Ampel(0.8)`, mit Zustand/Zähler, `Hashtable`). **Nicht gesperrt:** `System.IO.File.Exists`, `File.ReadAllText`,
  `Environment.UserName` laufen. `System.Drawing` zeichnet ein einfaches Bild; ein komplexer Zeichenversuch (1600 px, `@87@`-Polygone) ging einem Allplan-Absturz
  voraus (Ursache unbelegt) → kein Bildzeichnen per Code, erst kopflos prüfen.
- Strichcode, QR-Code und CSV als zweite Datenquelle laufen aus dem `<Code>`-Block: `codes.md`.
- `<CodeModules><CodeModule>NemNET_Interfaces, Version=2011.0.0.0, Culture=neutral, PublicKeyToken=null</CodeModule></CodeModules>`:
  `Nemetschek.Interfaces.NemAll_DataGeneral.IsGlobalImperialUnit()`, `GetLengthUnitsSuffix(1,1)`=cm, `(0,1)`=mm, `(3,1)`=m, `GetWeightUnitsSuffix(1)`=kg, `ConvertLengthToString(1234.5,2,true)`=`1.23 m` (Eingabe mm).

## Aggregate

Laufen (Schema 2005): Sum, Avg, Min, Max, Count, CountRows, CountDistinct, StDev, Var, First, Last, RunningValue, Previous, RowNumber, `Sum(IIf(…))`.
`Lookup`/`LookupSet`/`Join` nur Schema 2010/2016 (Textfelder im Body). `Aggregate()` liefert leer. `Lookup` zwischen zwei DataSets nicht prüfbar.

## Leere Ergebnisse

- **Erstes DataSet leer = keine Datei**, Allplan zeigt das Meldungsfenster „Es wurden keine Bauteile gefunden …“ (`ok=False`).
- Leere weitere DataSets oder per Filter leere Tabellen rendern normal; `<NoRows>` zeigt den Text, Zähler `Sum(IIf(…,1,0), "AllplanReport")` = 0.
- Darum eine breite Abfrage; Teilmengen (Türen) per Filter mit `<NoRows>`. Division über `quote()`, nie `#Error`/`NaN`.

## Datenfest (master/GESTALTUNG.md)

Der Master sah auf 51 Zeilen perfekt aus und riss auf echten Projekten (13 statt 7 Seiten bei 101 Zeilen, 20 bei 3.545).
- Jede Liste, jedes Diagramm, jede Kartenreihe hat einen **Deckel** (`c.topn(ausdruck, n)`; Diagramme 6–8 Kategorien) und nennt das Weggelassene („… und 303 weitere“).
- Keine Projektnamen im Ausdruck (nie `Material="Beton bewehrt"`, `Funktion="Verkehrsfläche"`): **Materialgruppe am Wortstamm** (`Code.MatArt`: „StB C45“ = Beton, „MW“ = Mauerwerk), Verkehrsfläche `Code.IstVerkehr`.
- **Bauteilart über `@OBJ@`** (`Code.Art(Fields!ObjNr.Value)`), nicht über den Objektnamen.
- Wachsende Tabellen in `Rectangle` mit fester Größe; lange Namen abschneiden (Spalte für 25 Zeichen); große Zahlen `#,##0`.
- Jede Seite muss mit den drei ausgelieferten Datensätzen (`master`, `master_en`, `gross`) genau ein Blatt ergeben (Befehle: pruefstrecke.md).

## Startvorlagen und Standardblöcke

Allplans Startvorlagen (`Template_*.rdlc` aus `Etc\Reports` der Installation) gehören zu Allplan und werden nicht mitgeliefert. Jeder gestaltete Report
braucht zwei Standardblöcke, die Allplan erwartet: die Datenquelle und die Standardparameter (Liste oben, Abschnitt „Projekt- und Deckblattdaten“).
`master/rahmen.xml` trägt beide Blöcke; `core.py` setzt sie in jeden erzeugten Report. `werkzeug/datenprobe.py` baut dagegen auf Allplans eigene
Startvorlage `Template_Grouping0_2005.rdlc` und holt sie aus der Installation (`C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports`); die Umgebungsvariable
`ALLPLAN_REPORTS` geht vor. Ohne Allplan-Installation `ALLPLAN_REPORTS` auf einen Ordner setzen, der diese Datei enthält – sonst bricht das Skript mit einer Meldung ab.

## Attribut-Nummern nachschlagen

`python werkzeug/pruefen/lookup_attribute.py 220 507 --suche Volumen` liest den Attributkatalog der Allplan-Installation
(`C:\ProgramData\Nemetschek\Allplan\2027\Etc\Xml`; `--etc <Ordner>` oder die Umgebungsvariable `ALLPLAN_ETC` nennen einen anderen Ordner). Dieses Paket
liefert keine Kopie des Katalogs mit. Als Rückfall dient die Datei `werkzeug/data/attributes_2027.json`; auf einem Rechner mit Allplan erzeugt sie
`python werkzeug/pruefen/lookup_attribute.py --export`. Fehlen Installation und Datei, meldet das Skript „Kein Attributkatalog gefunden“ und endet mit Exit-Code 2.
Eine Nummer ohne Treffer gilt als unbelegt: ein Vorbild in Allplans Bibliothek suchen, nie raten.

## Beispieldaten für den kopflosen Bau (`<REPORT>/master/daten/`)

| Datensatz | Inhalt |
|---|---|
| `master.json` | 51 Zeilen, das Master-Testgebäude, deutsche Materialnamen |
| `master_en.json` | dieselben Zeilen mit englischen Materialnamen (Concrete, Masonry, Insulation, Plasterboard) |
| `gross.json` | rund 3.000 künstliche Zeilen aus `master.json` (`make_gross.py`): 40 Raumnutzungen mit teils sehr langen Namen, je Materialgruppe 8 Schreibweisen (deutsch und englisch gemischt, dazu Bauteile ohne Material), 20 Fenster- und 15 Türtypen, sehr große und sehr kleine Zahlen |

Für den Begleit-Report Wandbeläge gibt es `master/abwicklung/daten/wandbelag_bsp.json` (18 Zeilen: 9 Räume des Master-Testgebäudes, je Innenputz und Anstrich;
`make_wandbelag_bsp.py` erzeugt sie aus `master_abw.json`). Die Leibung ist dort ein fester, erfundener Wert je Raum – das Testgebäude hat keine Raumausbau-Seitenflächen.

Bildfelder sind Platzhalter (`"file:bilder/<ObjNr>.png"`); echte Bilder liefert nur der Export aus Allplan. Eigene Daten:
`datenprobe.py` baut einen Probe-Report, den der Anwender in Allplan als Excel ausgibt, `xlsx_zu_json.py` macht daraus den Datensatz
(Ablauf: `pruefstrecke.md`, Abschnitt (b)).

Nicht geprüft: vollständige Master-Spaltenliste in einem Lauf; `MergeDataSet` in der Bewehrungsbibliothek; Tabellen `Type=24/51/67/99`; IFC-Typ außer Fenstern.

