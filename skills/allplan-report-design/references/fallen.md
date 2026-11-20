# Fallen und ihre Lösung

Worüber man beim Bau gestalteter Allplan-Reports stolpert. Was grundsätzlich geht, steht in `grenzen.md`. Alles gilt für Schema 2016, sofern nichts anderes dasteht. Fehler in Diagrammen meldet der Renderer nicht: jedes Bild ansehen.

## Ausdrücke und Zahlen

| Falle | Folge | Lösung |
|---|---|---|
| `&` ohne Leerzeichen (`"a"&x`) | Abbruch BC30277 | immer `"a" & x & "b"` |
| Zahl als Text in Achsen-`Minimum`/`Maximum` (`"1.14"`) | deutsche Kultur liest 114 | als Ausdruck schreiben: `=1.14` |
| `CDbl("1234.5")` | ergibt 12345 (Punkt = Tausendertrenner) | `CDbl(Fields!X.Value)` aus Zahlenfeld; Text nur mit Komma |
| `CStr(x*4) & "pt"` | `12,116pt`, Fehler `rsInvalidSize` | `CInt(x*4) & "pt"` |
| `StrDup(Round(x),"█")` | `#Error` | `StrDup(CInt(x),"█")` |
| `Globals!PageNumber`/`TotalPages` im Body | Abbruch | nur in `PageHeader`/`PageFooter` |
| Wahrheitswert groß (`False`, `True`) | Renderer lehnt ab | klein `false`/`true`; Ausnahme: Achsen-`Visible` `True`, Gitterlinien/`Margin` `Auto/True/False` |
| `FontWeight 700`, `WritingMode tb-rl` in Schema 2016 | Fehler | 2016: `Bold`, `Rotate270`, `BackgroundRepeat Clip`; 2005: `700`, `tb-rl`, `NoRepeat` |
| `IIf(x>0, a/x, 0)` | Division durch 0 (`IIf` wertet beide Zweige aus) | `IIf(x>0, a / IIf(x>0,x,1), 0)` |
| `First`/`Last`/`Previous` in Tablix-Sortierung | verboten | `Min()`/`Max()` |
| `UserSort` mit Aggregat ohne `SortExpressionScope` | Report ungültig | Gruppe als Scope angeben |
| TopN bei Gleichständen | zählt alle Gleichen mit, Zeilenzahl schwankt | eindeutigen Nachrang in den Ausdruck rechnen |
| Derselbe Text in zwei Schreibweisen im Modell („Flur“ und „FLUR“) | eine Gruppe fasst beide zu EINER Zeile zusammen, `CountDistinct` zählt aber ZWEI: Rang, „+ n weitere“ und TopN laufen auseinander (Rest-Zeile doppelt, Seite länger – an einem Wohnhaus 11 statt 10 Seiten) | `<CaseSensitivity>True</CaseSensitivity>` im DataSet (in Allplan gemessen, läuft; der Bausatz `c.dataset` setzt es): dann sind es überall zwei Werte |
| `RunningValue(…, Sum, <Kategoriegruppe>)` | summiert nicht auf | Scope `Nothing`, `"AllplanReport"` oder Diagrammname |
| `Code.Stufe` mit Zähler im `<Code>` | Zähler gilt report-weit und zählt je Auswertung: Farben verschieben sich | je Thema eigene Funktion oder `Choose(RunningValue(…))`; Nummerierung mit `RowNumber` |
| Feste Namen im Ausdruck (`Material="Beton bewehrt"`) | trifft im anderen Projekt nicht, Diagramm 0 % | Wortstamm der Materialgruppe, Bauteilart über `@OBJ@`-Nummer |
| `Language` an der Textbox | wirkt nicht | `<Language>` am Report |
| `Fmt=` oder `Dim=` für Fläche und Volumen in der Abfrage | Rundung unklar, Faktoren falsch (Dim 1 = ×10⁵) | in der Abfrage nichts formatieren; im Report `Format(x,"N2")`, Fläche und Volumen ohne `Dim` |
| Fester Text mit `@452@` (Attributnummer) | Allplan ersetzt ihn durch den Attributnamen („Topologie_Geschoss“) | nur nutzen, wenn der Attributname gewünscht ist (sprachneutraler Spaltenkopf) |
| `@68@`/`@401@` als Zahl getypt, kommt als Formeltext oder Datum | `(4.250*4.213)` statt 17,9 | `@68@` als Double typen, `@401@` als String |
| Filter `Like` mit `%` als Platzhalter (`="%makro%"`) | keine Zeile, keine Meldung | Platzhalter ist `*`: `="*makro*"` |
| `RowNumber("Gruppe")` oder `RowNumber(Nothing)` als Gruppennummer | zählt Datenzeilen (4, 8, 13, 16; im Gruppenkopf 9 statt 3) | `RunningValue(Ausdruck, CountDistinct, "Eltern")` oder `RunningValue(Feld, CountDistinct, Nothing)` |
| `Previous(Σ, "äußere Gruppe")` | liefert die Zeile gleicher Position in der Vor-Gruppe, leer wenn diese kürzer ist | `Previous(Σ, "innere Gruppe")` (läuft über die Elterngrenze) oder `RunningValue` |
| `<Variables>` in `<ReportSection>` oder hinter `<Body>` | „The definition of this report is not valid or supported“ (kopflos) | `<Variables>` direkt unter `<Report>`, Gruppenvariablen in `<Group>` |

## Diagramme

| Falle | Folge | Lösung |
|---|---|---|
| Werteachse ohne `Min` | Achse startet bei krummem Wert, Säulen verzerrt | `Minimum` 0 setzen |
| Beschriftung am längsten Balken | steht im Balken, dunkel auf dunkel | `Maximum` als Ausdruck: größter Wert × 1,2 |
| Automatische Achsschrift | zu groß, ungleich | `<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>` |
| Legende `Layout=Row` | schneidet ab („• • •“) | eigene Legende als kleine Tabelle |
| `BackgroundColor` am `ChartDataPoint` | keine Wirkung | `Style/Color` am `ChartDataPoint` |
| Palette `Default` | grelle Grundfarben | `Palette=Custom` mit `ChartCustomPaletteColors` oder Farbe per Ausdruck |
| Datenbeschriftung `Position=Outside` an Säule | Fehlertext im Bild, Exitcode 0 | `Top`, `Center` oder `Bottom` |
| Datenbeschriftung kleiner Scheiben | überlappt | `IIf(Anteil<0.06,"",…)` |
| Balkendiagramm | erste Kategorie unten | aufsteigend sortieren, wenn der größte oben stehen soll |
| Blasen ohne `ChartMarker Circle` | Quadrate | Marker `Circle` setzen |
| „×“ in der Blasen-Beschriftung | farbige Pünktchen | „Stk.“ schreiben |
| Sunburst | Beschriftung bricht unlesbar um | TreeMap nehmen, Gliederung in die Beschriftung |
| Punktwolke mit identischen Bauteilen | liegen exakt übereinander | hinnehmen; Marker mit Ausdrucksfarbe ohne Transparenz |
| Serienname mit Leerzeichen oder `[m²]` | Abbruch (kein CLS-Bezeichner) | einfacher Name; Legendentext über `ChartItemInLegend/LegendText` |
| Gruppen- und Elementnamen doppelt | Abbruch | im ganzen Report eindeutig: Kürzel je Seite (`S3_…`), Chart-Name als Präfix der Gruppen |
| Filter am Diagramm ohne Datentyp | `Cannot compare System.Int32 and System.String` | `FilterValue DataType="Integer"` |
| Leeres `<CustomProperties/>`, `BorderWidth` 0 pt, `ChartArea` ohne Achsen | ungültig bzw. nichts gezeichnet | weglassen; Rahmen mindestens 0,25 pt; Achsen anlegen (auch unsichtbar) |
| Datenmenge leer | Diagramm bleibt weiße Fläche | `ChartNoDataMessage` setzen |

## Messanzeigen

| Falle | Folge | Lösung |
|---|---|---|
| Textbox über einem `GaugePanel` | wird teils nicht gezeichnet | Zahl als `GaugeLabel` in die Anzeige |
| Radial-/Linear-Gauge ohne `Top/Left/Height/Width` (Prozent) | rendert nichts | alle vier setzen |
| `RadialPointer` ohne `Style/BackgroundColor` | unsichtbar | Farbe setzen |
| `BackgroundGradientType` im `Style` einer `ScaleRange` | Bänder mit Verlauf | als eigenes Kind von `ScaleRange` auf `None` setzen |
| Gauge im Standardlook | silberner Rahmen, Glas | `FrameStyle=None`, Rahmen ohne Linie, `ScaleRange` ohne Rand |
| `ScaleRange` am `LinearGauge` in flachem Feld | zu dünn oder unsichtbar | Zielbalken als gestapeltes Balkendiagramm (0,2 cm hoch) |
| `IndicatorState` ohne `ScaleFactor` | Report ungültig | `ScaleFactor` setzen |
| Halbkreis-Tacho | Zeiger sitzt zu hoch | `StartAngle=90`, `SweepAngle=180`, `PivotY` rund 68 % |

## Tabellen und Layout

| Falle | Folge | Lösung |
|---|---|---|
| Tabelle ohne reserviertes Feld | wachsende Tabelle schiebt alles darunter und rechts davon weg, Leerseiten | jede Tabelle und Kreuztabelle in ein `Rectangle` fester Größe, Breite höchstens Nutzbreite |
| Ausgeblendetes Element | Lücke bleibt | Sichtbarkeit nur innerhalb eines Feldes schalten |
| Liste, Legende oder Diagramm ohne Höchstzahl | wächst auf Folgeseiten (13 statt 7 Seiten bei 101 Zeilen, 20 bei 3.545) | TopN passend zur Höhe, Hinweiszeile „… und n weitere“; Seite mit allen Datensätzen prüfen (`master`, `master_en`, `gross`) |
| Kartenreihe (Spaltengruppe) ohne Deckel | bricht bei 6+ Typen waagerecht um | TopN an die Spaltengruppe |
| Zeile 0,52 cm mit 2 pt Innenabstand | Kommafuß abgeschnitten („36,4“ wirkt wie „36.4“) | 0 pt oben und unten |
| Lange Namen | Zelle wächst nicht (`CanGrow false`), Text abgeschnitten | Spalte für 25 Zeichen oder kleinere Schrift |
| Zahl in Kachel | steht rechtsbündig | `TextAlign Left` |
| Zwischensumme in Matrix (Schema 2005) | übernimmt das Zellformat | im Zellausdruck `InScope()` unterscheiden |
| Leere `TableCell` nach `ColSpan` (Schema 2005) | Deserialisierungsfehler | Folgezellen weglassen |
| `Sorting` direkt an der `Table` für TopN (Schema 2005) | Fehler | `Sorting` in `<Details>` |
| Diagramm in Tabellen-Detailzeile (Schema 2005) | alle Balken gleich lang | Schema 2016: Diagramm mit eigener Kategoriegruppe in der Zelle |
| Nullzustand nie angesehen | `#Error`, `NaN` oder leere Achsen | Zustand ohne Treffer per Parameter herstellen und ansehen; `<NoRows>`, „–“ als Leertext |
| Element neben wachsender Tabelle, tiefer als deren Kopfzeile | wandert ans Tabellenende, ggf. auf Seite 3 (kopflos) | auf Höhe der Kopfzeile setzen oder in den Seitenkopf |
| Element rechts neben einer Tabelle mit bedingter Spalte | rückt mit, wenn die Spalte ausgeblendet wird (die Lücke schließt sich) | rechts daneben nichts Festes setzen, oder Element in dasselbe Rectangle mit fester Breite |
| `RepeatWith` für Kopf oder Hinweis je Seite | wirkt nicht: Element nur auf Seite 1 | `RepeatOnNewPage` an der Kopfzeile, oder `PageHeader` |
| Kartenraster aus Spalten- und Zeilengruppe, letzte Reihe unvollständig | leere Karte mit leeren Werten („Sonstiges“, „0 Zeilen“) | `Hidden =CountRows() = 0` am Karten-Rectangle (Vorbild: Raumkarten im Grundriss-Report) |
| `RowSpan` im Tabellenkörper | harter Fehler `The TablixCell can only span one row` (kopflos) | senkrecht verbinden mit dem `TablixHeader` der äußeren Gruppe; `RowSpan` nur in der Matrix-Ecke |
| Zelle mit festem Zeilenmaß und langem Text (`CanGrow` aus) | Text abgeschnitten (PDF: erste Zeile bis zum Zellrand) | `CanGrow` an oder Text kürzen |
| Rekursive Hierarchie ohne Deckel | 35 Seiten und 63 s bei 3.000 Zeilen (kopflos) | nur bei kleinem Bestand; sonst nach Art und Material gruppieren |
| `BreakLocation` End an einem Block und Start am nächsten | LEERE Seite dazwischen | nur eines von beiden setzen |
| Mehrere `<ReportSection>` mit verschiedenen Seitengrößen | alle Seiten in der Größe der ersten Sektion, breite Sektionen laufen auf Folgeseiten über | je Seitengröße ein eigener Report |
| Tabelle ohne `KeepTogether` am Seitenende | wird geteilt | `KeepTogether` setzen; sie wandert ganz auf die Folgeseite, die Lücke bleibt |
| Kopfzeile ohne `KeepWithGroup` und `RepeatOnNewPage` | Kopf allein am Seitenende, auf Folgeseiten kein Kopf (kopflos gemessen) | beides setzen (der Bausatz `c.tablix` tut es) |
| Kopfelement soll nur auf Seite 1 oder erst ab Seite 2 stehen | `PrintOnFirstPage` gilt für die ganze Zeile | `Hidden` als Ausdruck `=Globals!PageNumber > 1` am Element im `PageHeader` |
| Textboxen als Geschwister über einem gefüllten `Rectangle` | teils nicht gezeichnet (kopflos) | Kinder im Rectangle |

## Text und Zeichen

| Falle | Folge | Lösung |
|---|---|---|
| „Segoe UI“ für ✓ ✕ ★ █ | Kästchen | „Segoe UI Symbol“; Blockzeichen „Consolas“ |
| Symbol („Segoe UI Symbol“) und Folgetext in EINER Textbox | Folgetext fehlt in Allplan | Symbol und Wort in getrennte Textboxen |
| Farbige Emoji | einfarbig, schraffierte Kreise | `●` mit Farbe per Ausdruck plus Text |
| `TextAlign=Justify`, `LineHeight` in Prozent | harter Fehler | `Left`; Zeilenhöhe in pt |
| Transparente Farbe (`#80E11D48`, `Transparent`, `rgb()`) | harter Fehler | `#RRGGBB`, vorab hell mischen |
| Fehlende Schrift (feste Familie, die der öffnende Rechner nicht hat) | stiller Ersatz, sieht aus wie Arial; neuere Messung (2026-11-20): alles in „Microsoft Sans Serif“, Gewichte weg, einzelne Zeichen (Farbkästchen der Legende) als leere Kästchen | Schrift nur über `F`, `F_LIGHT`, `F_SEMI`, `F_ZAHL` aus `core.py`: der Report wählt beim Öffnen selbst und nimmt sonst Segoe UI (`design.md`); feste Namen nur für Systemschriften |
| Zwei Elemente im selben Container überlappen sich, auch nur um 0,02 cm, auch ein unsichtbares oder leeres Feld | das Report-Fenster schiebt eines unter oder neben das andere: Text rutscht in die nächste Zeile oder wird in festen Rahmen abgeschnitten, Blöcke rücken nach unten, die Seite wird länger; PDF und Vorschau lassen beide am Platz | mindestens 0,05 cm Abstand zwischen allen Geschwistern; Hintergrundflächen als Eltern-Rectangle, Striche als Rahmen, Titel und Untertitel nebeneinander; Warnung W28 „Elemente überlappen sich“ von `validate_rdlc.py` beachten |
| Feld mit `Hidden`-Ausdruck liegt direkt auf der Seite neben fremden Elementen, seine Kanten liegen nicht auf deren Kanten | im Report-Fenster rücken sichtbare Elemente desselben Behälters nach links (gemessen bis 2,4 cm, auch 8 cm entfernt); PDF und Vorschau zeigen es nicht, das Prüfskript auch nicht | das Feld (oder die Felder) in EIN Rectangle über die volle Breite legen, `Hidden` an das Rectangle; Reihen aus mehreren Kacheln ebenfalls in ein eigenes Rectangle |
| Text bis 8,5 pt knapp bemessen | im Report-Fenster 3 bis 8 % breiter als im PDF: bricht um oder wird abgeschnitten | 10 % Breitenreserve; ab 9 pt ist das Fenster 0,5 bis 3 % schmaler (gemessen mit Segoe UI; die Passkontrolle der Seiten rechnet mit den Breiten von Roboto) |
| Strich-Feld als Platzhalter über einem Zahlenfeld | Zahlenzeile zerfällt treppenförmig, die Karte wird mehrfach so hoch | Strich als Rahmen am Zahlenfeld oder unter die Felder setzen |
| Kopfzeile endet bei 0,52 cm, die Satzzeile beginnt bei 0,50 cm | Satzzeile rutscht unter den Kopf und wird vom Rahmen abgeschnitten | Kopfhöhe verkürzen oder Satz tiefer setzen, Rahmenhöhe anpassen |
| Unsichtbares Ankerfeld über die ganze Kopfhöhe | Kopf wächst auf mehr als das Doppelte, Inhalt rutscht nach unten | Ankerfeld weglassen oder auf 0,05 cm Höhe am unteren Rand setzen |
| Titel in voller Breite neben einem rechtsbündigen Untertitel (Titelfeld reicht unter den Untertitel) | Untertitel rutscht in eine eigene Zeile unter den Titel, Akzentlinie fehlt | Titelbreite nur bis zum Beginn des Untertitels |
| Feld einer schmalen Spalte so breit wie die Spalte minus 0,1 cm, der Nachbartext beginnt bei 0,85 cm | Nachbartext rutscht darunter | Feldbreite bis höchstens zum Beginn des Nachbarn |

## Bilder

| Falle | Folge | Lösung |
|---|---|---|
| `@205@` ohne `Width` (nur `Height`) | kein Bild | immer `Width` setzen (Obergrenze in mm, Höhe wird auf Inhalt gekürzt) |
| `GText` fehlt, falsch oder klein (`hd`) | Notbild 113 px, `Width`/`Height` wirkungslos | `GText=HD_CENTERMIDDLE` oder `HD` exakt groß; Schlüsselname ist egal |
| Tippfehler im Schlüssel (`Hight`) | wirkt nicht | `Height`; unbekannte Schlüssel werden still ignoriert |
| `Hidden` fehlt, 0 oder gerade bei Fenster | Fenster: kein Bild; Wand: Drahtmodell mit verdeckten Kanten | `Hidden` ungerade: 1 grau, 5 Bauteilfarbe, 67 Textur, +16 verdeckte Kanten gestrichelt, +64 SmartParts mitzeichnen |
| `Dim=2` am Fenster | kein Bild | `Dim` weglassen oder 0/1 |
| `Projection` an Raum oder Sammelobjekt | leer | `Image=true` ohne `Projection` (Planmodus); Raummaße mit `Type=35` |
| `Image=true` zusammen mit `Projection` | `Projection` gewinnt, 3D-Bild | `Projection` weglassen |
| `Hidden`, `Scale` im Planmodus | `Hidden` wirkt nicht, `Scale` kürzt die Höhe | `Hidden` weglassen; `Scale` nur als Zielmaßstab (100 = echter Maßstab) |
| Ansichtsnummern aus der Werkstatt-Tabelle (9 = Draufsicht) | falsche Ansicht | Draufsicht 0/5, vorn 2, hinten 8, links 4, rechts 6, Isometrie 1/3/7/9, Querschnitt 12 |
| Ansicht je Bauteil gewählt | Ansichten sind Weltrichtungen: eine Y-Wand zeigt bei 2 nur ihr Schmalende | Isometrie 7 oder 9 als neutrale Wahl |
| Weitere `@205@`-Spalte mit anderer Ansicht | zeigt dasselbe Bild wie die erste | eine Bildart je Report planen; zweite Ansicht = zweiter Report |
| Zeilen mit gleichen Feldwerten | werden zusammengefasst (11 statt 16), Bilder fehlen | `@10@` (Bauteil-ID) in die Abfrage |
| Decke oder Bodenplatte in 3D | nur graue Platte, Draufsicht nur Rechteck | für den Grundriss Planmodus an der Decke |
| Bild im Body höher als 24,5 cm | zweite Seite | Body-Höhe unter 24,5 cm halten |
| Dateipfad ohne `file:///` oder relativ | Fehler bzw. rotes Kreuz | `="file:///" & Pfad`, absolut; Feld mit eigenem `file:///` wird doppelt: eines von beiden |
| Datei fehlt | rotes Kreuz 15×17 px oben links | `Code.DateiDa(pfad)` in `Hidden` oder `Value`, oder Leerbild-Datei als Ersatz |
| `<EmbeddedImages>` an falscher Stelle, `Source=Database` ohne `MIMEType` | Fehler | Schema 2005: vor `<PageWidth>`; `MIMEType` immer; nur png, jpeg, gif, bmp |
| `BackgroundImage` mit halbtransparentem PNG | Pixel erscheinen deckend, Bild nie skaliert | PNG vorab hell rechnen; Werte `Repeat`, `NoRepeat` (2005) bzw. `Clip` (2016), `RepeatX`, `RepeatY` |
| `Sizing=AutoSize` am Bild | Zelle wächst, Spalten auf Folgeseiten | `FitProportional` (`Fit` verzerrt) |
| Bild im XLSX erwartet | Bildspalte wird laufende Zahl | PDF oder DOCX |
| Bildzeichnen per VB-Code (1600 px) | Allplan stürzte zeitlich nah ab | kein Bildzeichnen per Code; höchstens kleine Bilder |

## Abfrage

| Falle | Folge | Lösung |
|---|---|---|
| Zweites DataSet oder zweites `SELECT … FROM [Type=0]` | bleibt leer, Aggregate 0 | EINE breite Abfrage mit Spalte `ObjId`; Themen per Tabellenfilter `=Fields!ObjId.Value` |
| `FROM [MODEL_DATA]` ohne Filter | auch Unterobjekte: negative Flächen, Sammelobjekte „Decke gesamt“ | nach `@OBJ@` filtern (Wand 1, Stütze 3, Decke 4, Unterzug 6, Bodenplatte 704, Raum 61, Fenster 991, Tür 992) |
| Material oder Gewerk als Auswertungsschlüssel | Projekte schreiben „StB C45“, „MW“ | Materialgruppe am Wortstamm erkennen |
| `@221@` bei Decke und Bodenplatte | ist die Plattenbreite | Hilfsspalte `f=_IF_(@OBJ@.eq.4.or.@OBJ@.eq.704)@222@_ELSE_@221@` |
| `@97@`/`@98@` | Millimeter, `@204@`/`@222@` Meter | `f=@97@/1000` |
| Raumname in `@507@` gesucht | leer | Raumname steht in `@506@` |
| `PARENT(…)` bei Fenster und Tür | liefert den Raum, nicht die Wand | `MT_Wand(@10@)`, `MT_Wand(@508@)`, `MT_Wand(@221@)` |
| Projekttabelle (`CURRENT_PROJECT`, `DOCUMENT`, `LAYOUT` …) als XLSX ausgeben | Report-Fenster öffnet sich, keine Datei | als PDF oder DOCX ausgeben (die Zeilen kommen normal) |
| Projekttabelle als erste Abfrage, Bauteilspalten im selben Report | nur ein DataSet wird gefüllt: Bauteilspalten leer | Projektattribute als Spalten der Modellabfrage (`@405@`, `@697@`, `@431@`, `@449@`, `@20@`, `@401@`) oder zwei Reports (`projektlisten.md`) |
| `DOCUMENT` als Gesamtliste der Teilbilder | Zeilenzahl schwankt je Abfrage (172, 76, 38), Teilbilder auf Plänen fehlen | Pläne (`LAYOUT`) oder `BUILDINGSTRUCTURE` nehmen; Ursache offen |
| `LAYOUT_DRAWINGS` allein als erste Abfrage | nur 1 Zeile, nicht die Teilbilder aller Pläne | zusammen mit `LAYOUT` als zweites `SELECT` im selben `<CommandText>` |
| `LAYOUT_HISTORY`, `ATTRIBUTES`, `FILESET` mit `WHERE @1155@.eq."Item"` als erste Abfrage | keine Zeilen | `LAYOUT`, `DOCUMENT` oder Projektattribute als Spalten der Modellabfrage; Ursache offen |
| Parameter ohne `DefaultValue` | String mit `AllowBlank`: leerer Text; Integer: Typfehler, keine Datei | immer feste Vorgabe; `<Prompt>@405@` holt den Attributwert und überschreibt die Vorgabe |
| Unterbericht mit eigener Abfrage (Projekttabelle, Räume, Bewehrung, anderes `@205@`) | die Abfrage läuft nicht; `CountRows` = Zeilen des Hauptreports, Felder anderen Namens leer, Bild wie im Hauptreport | die Felder des Ziels so nennen wie im Hauptreport und per Filter auswählen; andere Daten oder Bildart: zweiter Report |
| Feld im Unterbericht heißt anders als im Hauptreport | Wert leer, Zeile trotzdem da (Zuordnung nach Feldname, nicht nach Reihenfolge) | Feldnamen des Hauptreports verwenden |
| Unterbericht: übergebener Parameter ohne `<Prompt>` im Ziel | Unterbericht wird nicht angefordert, Fehlerzeile statt Inhalt (kopflos) | `<Prompt>` an jedem Parameter des Ziels |
| Unterbericht im kopflosen Renderer | `Error: Subreport could not be shown`, obwohl Allplan ihn zeigt | Unterbericht in Allplan beurteilen; ein Renderer, der dem Ziel eigene Daten gibt, zeigt MEHR als Allplan liefert |
| Unterbericht mit Tabelle ohne Deckel | wächst über die Seite, schiebt alles darunter weg (2 Seiten) | `TopN` im Ziel; Höhe des Unterberichts nicht höher als der Platz |
| `Rectangle` als Rahmen hinter einem Unterbericht | verdeckt den Inhalt (kopflos in drei Proben) | Rahmen als `Style/Border` am `<Subreport>` |
| `DefaultValue` `@431@` | bleibt Text | `<Prompt>` statt `DefaultValue` |
| Layer, Stift, Gewicht, U-Wert, Brandschutz | immer leer (Layer nicht lesbar, Rest nicht am Bauteil gesetzt) | nicht auswerten; Attribut erst am Bauteil setzen |
| Verweis über Elementkennung (GUID) | ändert sich beim Setzen von Attributen | Bauteil-ID `@10@` verwenden |

## Parameter und Code

Regeltabelle der Vorgaben: `grenzen.md`, Abschnitt „Parameter (Stellschrauben)“; Strichcode, QR und CSV: `codes.md`.

| Falle | Folge | Lösung |
|---|---|---|
| Vorgabe als Ausdruck (`=Today()`, `=1+1`, `=IIf(Parameters!…)`) | String: leerer Text; Integer und DateTime: Meldungsfenster „Wert … für dessen Typ ungültig“, keine Datei; im Fenster bleibt die Parameterleiste leer und der ganze Report leer („Im Project_Name-Parameter fehlt ein Wert.“, falscher Parameter genannt); kopflos läuft es | feste Vorgabe; Datum aus `Parameters!Date` (`@401@`), `=Today()` im Ausdruck oder String-Parameter plus `CDate` |
| DateTime-Vorgabe `19.11.2026` | `DefinitionInvalid … DefaultValue` | ISO `2026-11-19` oder `11/19/2026` |
| `ValidValues` oder `DefaultValue` per `DataSetReference`, Ausdruck in `ValidValues` | „Mindestens einer der Parameter … wurde nicht angegeben“, keine Datei | Prompt `Distinct(Fields!X.Value)` oder feste Liste; abhängige Liste als Kombi-Liste „Art\|Typ“ |
| `MultiValue` ohne Vorgabe (feste Liste) | nur der erste Listenwert, nicht alle | Vorgabewerte nennen |
| `Hidden` am Parameter, um ihn zu verstecken | im Fenster steht er sichtbar und änderbar da | nicht als Versteck für Werte nutzen |
| Mehrfachliste per Distinct-Prompt, niemand wählt | alle Werte inklusive leerem Wert | gewollt; leeren Wert im Filter beachten |
| Pfad „neben dem Report“ im Code | Arbeitsverzeichnis ist `C:\Program Files\Allplan\Allplan 2027` | absoluten Pfad als Parameter |
| Dateizugriff im kopflosen Test | `SecurityException`, weicht von Allplan ab | Renderer mit `--fulltrust` oder in Allplan prüfen |
| Fehlerzelle suchen nach „#Error“ | Allplan schreibt `#Fehler` | nach beiden suchen |
| `User!Language` vergleichen mit `de-DE` | Allplan liefert `de` | `Left(User!Language, 2)` |
| `<CodeModule>System, …</CodeModule>` | BC2000, schon referenziert | weglassen |
| `System.Windows.Forms` im Code ohne System.Drawing als CodeModule | BC30652 | beide eintragen |
| Konstante Division durch null (`1/0`) im Ausdruck | ganzer Report bricht beim Übersetzen ab (BC30542) | Nenner aus Feld oder Variable |
| Code 39 mit `/ + $ %` oder Kleinbuchstaben | Decoder liest ein anderes Zeichen, Großschreibung geht verloren | Code 128 oder nur `A–Z 0–9 - .` und Leerzeichen |
| QR-Text über 106 Byte | leeres Bild ohne Fehler | Text kürzen (`Code.EtikettText`, `codes.md`) oder Verweis-ID statt Klartext |

## Bewehrung

Abfrage, Spalten, Rechenregeln: `bewehrung.md`.

| Falle | Folge | Lösung |
|---|---|---|
| `FROM [REINFORCEMENT_DATA]` mit `@10@` | Abfrage schlägt fehl | `FROM [ENGINEERING,Filter=@793@\|@792@\|@1210@]` |
| Stab-kg aus dem Feld Gewicht (`Sum(Gewicht)`) | Allplan fasst gleiche Zeilen einer Position zusammen und addiert dabei Anzahl, Gesamt- und Einzellänge, das Gewicht aber nicht: 683,1 statt 944,6 kg Rundstahl am echten Projekt | Gesamtlänge × kg je m (`@756@`); Einzellänge = Summe Gesamtlänge ÷ Summe Anzahl, nie das Feld `@757@` |
| Meterware (`@794@` ≥ 1) wie ein Stab behandelt | Einzellänge doppelt so groß, als „Überlänge“ gezählt | Stück 1, Länge „lfdm“, nie Überlänge |
| `@798@` mit `Index` (Schenkelmaße a bis j) | liefert 0 | nicht abfragen; die Maße stehen im Biegeform-Bild |
| `@797@` (Länge in lfdm) | Text mit Komma, bei Metermaterial „Lfdm“ | `@757@` mit `Dim=3` (Zahl in m) |
| Stab oder Matte am Text erkennen, den die Abfrage setzt (`f=_IF_…"Matte"`) | in der englischen Fassung falsch: der Sprachschalter übersetzt Zeichenketten im Ausdruck, nicht Werte aus der Abfrage | über `@OBJ@` (`ObjId`: 257 Stab, 368 Matte) |

## Export und Allplan-Fenster

| Falle | Folge | Lösung |
|---|---|---|
| Abfrage ohne Treffer, ungültige Definition, Betrachterfenster „Report“ | Fenster wartet auf OK | Fenster mit OK schließen; Abfrage und Filter prüfen; Titel `…DefinitionInvalidException` nennt Element und Fehler |
| XLSX | Rohdaten, 3 Stellen gerundet, keine Bilder | PDF oder DOCX; für volle Genauigkeit Zahlen als String liefern |
| Klicksprung (`Zoom:`) im PDF | wirkungslos | im Testfenster ebenfalls ohne Wirkung (`grenzen.md`, Bedienung): dem Kunden nicht versprechen, in Allplan ausprobieren lassen |
| Interner Sprung (`BookmarkLink` auf `<Bookmark>`) im Report-Fenster | springt, aber vorher öffnet sich ein Meldungsfenster mit dem Namen der Sprungmarke | OK drücken; dem Anwender vorher sagen |
| `file:///`-Link im PDF | kommt als Link an | nur `https://` und `mailto:` sind überall sicher; Link ohne Schema (`www.…`) wird gestrichen |
| Interner Sprung (`BookmarkLink` auf `<Bookmark>`) im PDF | kein Link | Lesezeichen (`DocumentMapLabel`) statt Sprungmarke nehmen |
| Zusammengefasster Hinweis („9 Räume ohne Bezeichnung“) | zoomt nur auf EIN Bauteil | je Bauteil eine Zeile oder auf den ersten verweisen |
| Tausende Zeilen mit `@205@` | rund 3 Minuten, Allplan „reagiert nicht“ | Bildspalte weglassen oder auf Bauteile mit Bild einschränken |
| Zahl in der Ringmitte (`ChartTitle` mit `ChartElementPosition`) | bei großen Zahlen links abgeschnitten oder aus der Mitte gerückt | `Position` `TopCenter`, Feld fast so breit wie das Diagramm, Schriftgröße als Ausdruck nach Stellenzahl |
| Kennwert nur für ein Gebäude gedacht (Raumfläche zu Bodenplatte) | am mehrgeschossigen Haus „>999 %“ | Bezug wählen, der an jedem Gebäude Sinn ergibt (Decken + Bodenplatte); an `gross` ansehen |
| Zieltext und Ampelregel getrennt gepflegt | Ampel „im Ziel“, obwohl der Text „15–30 %“ sagt und 44 % gemessen sind | Zieltext aus denselben Schwellen bilden wie die Regel |
| Summen mit verschiedenem Bezug (mit / ohne Bauteile ohne Material) | Seite 1 nennt 4.456 m³, Seite 3 5.193 m³ | ein Bezug je Report (`b.MIT_MATERIAL`), Abweichung als Hinweis ausweisen |

