# Was ein Allplan-Report darstellen kann

Nachschlagetafel für gestaltete Reports (`.rdlc`) in Allplan 2027. Sie sagt, WAS geht. Worüber man stolpert, steht in `fallen.md`; vom Wunsch des Kunden aus gesucht: `rezepte.md`.

- **Anzeige-Maschine:** Microsoft ReportViewer 15 (Allplans eigene DLLs). Allplan liefert nur die Daten (Abfrage `@id@[Name=…] FROM [MODEL_DATA, Filter=…]`), das Layout zeichnet der ReportViewer.
- **Schema:** Gestaltete Reports bauen wir im Schema 2016 (nur dort: mehrere Formate je Textbox, HTML-Text, Messanzeigen, `Tablix`). Allplan nimmt 2005 und 2016 an; 493 von 551 Allplan-Vorlagen sind 2005; keine der 551 enthält ein Diagramm oder eine Messanzeige (nachgezählt).
- **Belegstufen:** **A** = im echten Allplan 2027 gesehen (PDF-Export aus Allplan, angesehen). **K** = nur kopflos gerendert (gleiche DLLs, aber ohne Allplan; Daten aus JSON). **V** = Vorbild in Allplans eigenen Vorlagen, nicht selbst ausgelöst. **F** = im echten Allplan-Report-Fenster bedient (Klick, Eingabe, Blättern) und fotografiert.
- **Vorrang:** Bei Widerspruch gilt A oder F vor K. Ein K-Urteil kann in Allplan anders ausfallen (Beispiele: Kultur, Dateizugriff im Code, Sprache am Textfeld).
- **Urteil:** "geht", "geht mit Kniff" (Kniff im Hinweis) oder "geht nicht".

## Diagramme

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Säule, Balken, gestapelt, 100 %, gruppierte Säulen | geht | A | Balken: erste Kategorie steht unten |
| Linie, Treppenlinie, Fläche (auch gestapelt) | geht | K | |
| Torte, Torte mit Führungslinien, Ring, Pyramide | geht | A | |
| Trichter, Radar, Bereichsdiagramm, Candlestick, ErrorBar | geht | K | Candlestick und Bereiche brauchen High/Low/Start/End |
| TreeMap, Punktwolke (log), Blasen | geht | A | TreeMap ordnet nach Größe |
| Sunburst | geht nicht | K | Beschriftung bricht unlesbar um; TreeMap nehmen |
| BoxPlot aus Rohwerten | geht mit Kniff | K | fünf Kennzahlen selbst liefern |
| Pareto: Säule plus kumulierte Linie, zweite Wertachse | geht | A | nur Schema 2016; Schema 2005 hat keine zweite Achse |
| Säule plus Linie, eine Achse | geht | K | Balken plus Linie geht nicht |
| Farbe je Datenpunkt per Ausdruck (`Switch`, `IIf`) | geht | A | Farbe in `Style/Color` des `ChartDataPoint` |
| Verlauf, Schraffur, Halbtransparenz an Säulen und Scheiben | geht | K | Marker mit Ausdrucksfarbe ohne Transparenz; Bausatz verzichtet darauf |
| Schatten | geht nicht | K | |
| 3D, `ChartBorderSkin`, Relief-Stile | geht mit Kniff | K | zeichnen, wirken aber altmodisch; weglassen |
| Datenbeschriftung oben, mittig, unten, mit Format, Ausdruck, Schwelle | geht | A | Schwelle per `IIf(…,"")` |
| Datenbeschriftung `Outside` an Säule, Drehwinkel | geht nicht | K | Drehwinkel bleibt waagerecht |
| Zahl in der Ringmitte | geht | A | zweiter `ChartTitle` mit `ChartElementPosition` |
| Filter je Diagramm | geht | A | Ausdruck `=IIf(Bedingung,"j","n")` gleich `j` |
| Diagramm in Tabellenzelle, Mini-Säulen im Gruppenkopf, 100-%-Stapel in Zelle | geht | A | Achsen aus, Maximum als Ausdruck über die Gruppe |
| Datenbalken je Zeile in langer Liste | geht | A | Diagramm in der Tabellenzelle, Achsen aus |
| Sparkline, Ring in Tablix-Zelle; Small Multiples | geht | K | |
| Fortschrittsbalken | geht | A | `Bar/Stacked`, zwei Serien, Achse 0…1 |
| Zielwertlinie, Toleranzband (Strip Line), Skalenbruch | geht | K | Titel der Strip Line weglassen |
| Trendlinie (Regression) | geht nicht | K | Schema kennt keine |
| Karte (`Map`) | geht nicht | K | ohne Geodaten nur Gitternetz |

## Messanzeigen (`GaugePanel`)

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Halbkreis-Tacho mit rot/gelb/grün | geht | A | Standardlook veraltet, eigenen Look setzen |
| Fortschrittsring (`RadialPointer` Bar) | geht | A | |
| `StateIndicator`: Kreis, Pfeile, Sterne, Quadranten, Signal | geht | A | in Allplan gesehen: Kreis- und Haken-Stile (Master Seite 4); „48 von 52 Stilen sichtbar“ ist nur kopflos gezählt (K) |
| `StateIndicator` Stile `ButtonPause`, `FaceSmile`, `FaceNeutral`, `FaceFrown`, `TrafficLight` | geht nicht | K | leer bzw. schwarzer Kasten; Stil `Circle` nehmen |
| Große Zahl als `GaugeLabel` mit Ausdruck | geht | A | |
| Zahl als Textbox über der Anzeige | geht mit Kniff | A | Zahl als `GaugeLabel` in die Anzeige |
| Zielbereich am `LinearGauge` in flachem Feld | geht mit Kniff | A | als gestapeltes Balkendiagramm bauen |
| Linearer Balken, Bullet-Graph | geht | K | |
| Digitalanzeige (`NumericIndicator`) | geht nicht | K | rendert nichts, ohne Meldung |

## Tabellen

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Gruppen, verschachtelte Gruppen, Zwischensumme, Summenzeile | geht | A | |
| Kreuztabelle mit Farbskala per Ausdruck | geht | A | Zwischensummen: `InScope()` |
| Tablix-Matrix 3×3 über `RowNumber` | geht | A | Zeile `(n-1)\3`, Spalte `(n-1) Mod 3` |
| Bildkarten nebeneinander (Spaltengruppe) | geht | A | `First(Fields!Bild.Value)` |
| Steckbrief-Karte je Bauteil (Rectangle in Ein-Spalten-Tabelle) | geht | A | feste Zellhöhe (Master: `KARTE_H` in `s06_bilder.py`) |
| Zellen-Balken aus Spalten-Raster mit Hintergrundfarbe | geht | A | |
| Zellen-Balken aus Blockzeichen `█` (Consolas) | geht | K | im PDF-Viewer feine Nähte möglich |
| Zebra, bedingte Farbe und Fettung | geht | V | `RowNumber(Nothing) Mod 2` |
| Höchstzahl (TopN) und Sortierung | geht | A | |
| `RunningValue`, `Previous` mit Scope der inneren Gruppe, Anteil an Gesamt | geht | A | `Previous` läuft über die Grenze der Elterngruppe |
| `Previous(Σ, "äußere Gruppe")` | geht nicht | A | liefert die Zeile gleicher Position in der Vor-Gruppe, leer wenn diese kürzer ist |
| `Lookup`, `LookupSet`, `Join`, `MultiLookup` | geht | A | nur Schema 2010 und 2016, nur im selben DataSet; auch in Tabellenzelle und im `Parent`-Ausdruck |
| Tabelle, die zur Laufzeit wächst | geht mit Kniff | A | Rectangle mit reservierter Größe |
| Ausgeblendetes Element gibt Platz frei | geht nicht | A | Lücke bleibt; Tabellenspalte und -zeile geben Platz frei (unten) |
| Tabellenkopf und Gruppenband wiederholen (`RepeatOnNewPage`), Seitenumbruch je Gruppe oder Karte (`PageBreak` `Between`) | geht | A | Band einer über den Seitenwechsel laufenden Gruppe steht oben wieder; eine Karte je Seite |
| Mehrspaltiger Body (`Columns`) | geht nicht | K | Spalte 2 landet auf Seite 2 (nur kopflos) |
| `RepeatWith`: Element neben der Tabelle auf jeder Seite | geht nicht | A | erscheint nur auf Seite 1; Kopf je Seite über `RepeatOnNewPage` |
| Element neben wachsender Tabelle, tiefer als deren Kopfzeile | geht nicht | K | wandert ans Tabellenende; nur Elemente auf Höhe der Kopfzeile bleiben stehen |
| `FixedData` (Kopf und erste Spalte beim Scrollen fest) | geht | A | Datei wird fehlerfrei ausgegeben; Wirkung im Fenster: Abschnitt „Bedienung“; V: `Treppe.rdlc` |
| Report-Variablen und Gruppenvariablen (`<Variables>`), auch in Kopf und Fuß | geht | A | einmal rechnen, mehrfach benutzen; `<Variables>` direkt unter `<Report>` bzw. in `<Group>` |
| Rekursive Hierarchie (`Parent`, `Level()`, `Sum(…, Recursive)`) | geht | A | Eltern per `Lookup` im `Parent`-Ausdruck; wächst mit den Daten, nur bei kleinem Bestand; V: `Fertigteile/001_…` (Wirkung unbekannt) |
| Kartenraster aus Spalten- und Zeilengruppe (`Mod 3`, `\ 3`), letzte Reihe unvollständig | geht mit Kniff | A | leere Matrixzelle mit `Hidden =CountRows() = 0` ausblenden |
| Sortieren nach Aggregat der Gruppe, `BottomN`, `TopPercent` | geht | A | `TopN` war schon A |
| `Sum(Max(…, "Gruppe"), "Eltern")`, Anteil an Elterngruppe, `CountDistinct` im Gruppenbereich | geht | A | |
| `RowNumber("Gruppe")` als Gruppennummer | geht mit Kniff | A | zählt Datenzeilen; `RunningValue(Ausdruck, CountDistinct, "Eltern")` zählt Gruppen |
| Spalte per Ausdruck ausblenden (`TablixMember` `Visibility`) | geht | A | gibt Platz frei: Elemente rechts rücken nach; Vorgabezustand gesehen |
| Zeile und Summenzeile per Ausdruck ausblenden | geht | A | Zeilen darunter rücken nach |
| Tabelle in Tabellenzelle | geht | A | Zeile wächst mit; die innere Tabelle zählt nur die Zeilen der äußeren Gruppe; V: 31 deutsche Vorlagen |
| Matrix in Listenzelle (im Rectangle) | geht | A | Deckel (`TopN`) an die Zeilengruppe der Matrix |
| `ColSpan` im statischen Raster und im Gruppenband | geht | A | |
| `RowSpan` im Tabellenkörper | geht nicht | K | harter Fehler `The TablixCell can only span one row` |
| `RowSpan` in der Ecke einer Matrix mit zwei Kopfzeilen | geht | A | V: `Erdbau Auftrag Abtrag.rdlc` |
| Senkrecht verbundene Gruppenzelle (`TablixHeader` der äußeren Gruppe) | geht | A | ersetzt `RowSpan` im Körper |
| Zeilenhöhe fest (Text abgeschnitten), `CanGrow` (Zeile wächst), `CanShrink` (Zeile schrumpft) | geht | A | `CanShrink` macht aus 1,6 cm entworfen 0,5 cm |
| Unterbericht (`<Subreport>`, zweite .rdlc im selben Ordner): Layout, Parameter je Zeile, zweite Ebene, Filter im Ziel | geht | A | das Ziel bekommt die Zeilen des HAUPTreports; gefüllt sind die Felder, die im Hauptreport gleich heißen; im Ziel `<Prompt>` an jedem Parameter |
| Unterbericht in Tabellenzelle (je Gruppe einer) | geht | A | 5 Zeilen, je eigener Parameter, 2,5 bis 3,5 s |
| Unterbericht mit eigener Abfrage, anderer Tabelle, Projekttabelle (`CURRENT_PROJECT`, `LAYOUT`) oder anderer Bildart | geht nicht | A | die Abfrage des Ziels läuft nicht; Felder anderen Namens bleiben leer, das Bild ist das des Hauptreports; zweiten Report bauen |
| Unterbericht im Seitenkopf oder Seitenfuß | geht nicht | K | Dokument ungültig: `subreports cannot be used in page headers or footers` |
| Unterbericht wächst mit seinem Inhalt | geht mit Kniff | A | eine Tabelle im Ziel ohne Deckel schiebt alles darunter weg (2 Seiten); im Ziel `TopN` setzen |
| Textboxen als Geschwister über einem gefüllten `Rectangle` | geht mit Kniff | K | teils nicht gezeichnet; Kinder im Rectangle zeichnen immer |

## Text und Schrift

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Segoe UI, Segoe UI Light, Segoe UI Semibold, im PDF eingebettet | geht | A | |
| Mehrere Formate in einer Textbox (`TextRun`) | geht | A | nur Schema 2016 |
| HTML-Text (`MarkupType HTML`) | geht | A | `<b> <i> <u> <s> <font> <br/> <ul> <ol> <li> <h1> <span> <a>`; nur 2016 |
| Senkrechter Text | geht | A | 2016: `Rotate270` |
| Symbole ✓ ✕ ★ █ | geht mit Kniff | A | Schrift „Segoe UI Symbol“, Blockzeichen „Consolas“ |
| Farbige Emoji | geht nicht | K | nur einfarbig; `●` mit Farbe per Ausdruck |
| Blocksatz (`Justify`), Zeilenhöhe in Prozent | geht nicht | K | harter Fehler; Zeilenhöhe nur in pt |
| Laufweite | geht mit Kniff | K | schmale Leerzeichen U+2009 oder U+200A |
| Dünne Schrift | geht mit Kniff | K | nur über Familie „Segoe UI Light“ |
| Zahl- und Datumsformat nach de-DE | geht | A | `Format(x,"N2")`; Sprache am Report, nicht am Textfeld |
| Andere Sprache (`en-US`, `de-CH`) | geht | A | `<Language>` am Report |
| Seitenzahl x/y, Datum, `Globals!ReportName`, `User!UserID` | geht | A | Seitenzahl nur in Kopf oder Fuß |
| Eigener VB-Code (`<Code>`, `Hashtable`, Zustand) | geht | A | `Math`, `Regex`, `File.Exists` laufen; Code ist nicht gesperrt |
| `Globals!RenderFormat.Name`, `IsInteractive`; Sichtbarkeit nach Ausgabeweg (`Hidden =IsInteractive`) | geht | A | PDF: `PDF` und `False`, Fenster: Abschnitt „Bedienung“; kopflos auch `IMAGE`, `EXCELOPENXML`, `WORDOPENXML` |
| `User!Language` | geht mit Kniff | A | liefert `de` (kopflos `de-DE`), Zahlenformat bleibt `de-DE`; `Left(User!Language, 2)` vergleichen |
| Fehlerzelle | – | A | Allplan schreibt `#Fehler`, kopflos steht `#Error` |
| Konstante Division durch null (`1/0`) | geht nicht | K | Report bricht beim Übersetzen ab (BC30542); Variable durch 0: Double `∞`, Ganzzahl `#Fehler` nur in der Zelle (A) |
| Allplan-Einheiten (`CodeModule NemNET_Interfaces`) | geht | A | `GetLengthUnitsSuffix`, `ConvertLengthToString` |

## Flächen und Linien

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Füllfarbe als Name, `#RRGGBB`, Ausdruck | geht | A | |
| Randloses Farbband über die ganze Breite | geht | A | Seitenränder 0, Rectangle in Seitenbreite |
| Rahmen Solid, Dashed, Dotted, Double; Breite und Farbe je Seite | geht | A | Mindestbreite 0,25 pt |
| Rahmen Groove, Ridge, Inset, Outset | geht nicht | K | 2016: harter Fehler |
| Farbverlauf an Textbox und Rectangle | geht nicht | K | akzeptiert, aber flach in der Startfarbe |
| Schraffur, Schatten | geht mit Kniff | K | stillschweigend ignoriert; Schatten imitieren mit versetztem grauem Rectangle oder PNG |
| Transparenz in Farben (`#AARRGGBB`, `Transparent`, `rgb()`) | geht nicht | K | harter Fehler; vorab hell mischen |
| Abgerundete Ecken | geht mit Kniff | K | eingebettetes PNG mit transparenten Ecken hinter der Textbox |
| Linien, schräge Linien, Überlagerung per `ZIndex` | geht | K | |
| Hintergrundfarbe der Seite (`Page/Style`) | geht nicht | K | Rand bleibt weiß |

## Bilder aus dem Modell (`@205@`)

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| 3D-Ansicht je Bauteil (`Projection`), Strichzeichnung | geht | A | Ansichten sind Weltrichtungen |
| Farbig in Bauteilfarbe, Textur | geht mit Kniff | A | `Hidden` ist ein Bitfeld: 5 Farbe, 67 Textur (nur Holzfenster gesehen) |
| 2D-Planausschnitt wie im Teilbild (`Image=true`, ohne `Projection`) | geht | A | Schraffur, Türschwenk, Fensterstrich |
| Grundriss des ganzen Geschosses | geht mit Kniff | A | `Image=true` an der Decke oder Bodenplatte |
| Raumbild | geht mit Kniff | A | nur im Planmodus; Raum-Maßskizze mit `Type=35` |
| 3D-Bild des ganzen Gebäudes | geht nicht | A | Decke zeigt nur die graue Platte |
| Bild für Sammelobjekte (Decke gesamt, Gesamtwand …) | geht mit Kniff | A | nur im Planmodus |
| Zwei verschiedene Bildarten im selben Report | geht nicht | A | Ausnahme: Untertabelle `Type=35` bringt ein eigenes Bildfeld |
| Dickere Linien, Schattierung, Animation | geht nicht | A | feste Stiftbreiten |
| Klick auf das Bild zoomt auf das Bauteil (`BookmarkLink Zoom:`) | geht nicht | F | im PDF wirkungslos; im Fenster wie „Sprung auf Bauteil“ (Abschnitt „Bedienung“) |
| Bild als JPEG, rund 190 dpi | geht | A | Auflösung folgt Width/Height (7,56 px je mm) |
| `@87@` als Karte | geht nicht | A | liefert nur Polygon-Text je Bauteil, kein SVG |

## Bilder aus Dateien

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Fester Pfad, Pfad aus Parameter, Pfad aus Datenfeld je Zeile | geht | A | `file:///`-Pfad, auch mit Leerzeichen und Umlauten |
| Eingebettetes Bild, Auswahl per Ausdruck (Ampel-Icons) | geht | A | PNG, JPG, GIF, BMP |
| TIFF, SVG | geht nicht | A | rotes Kreuz |
| WebP, EMF | geht nicht | K | rotes Kreuz; eingebettet ungültiger MIME-Typ |
| Voll transparente PNG-Ecken | geht | A | halbtransparente Pixel erscheinen deckend |
| Wasserzeichen, Kachelhintergrund (`BackgroundImage`) | geht mit Kniff | A | Naturgröße von links oben, nie skaliert; vorab hell rechnen |
| Fehlende Datei | geht mit Kniff | A | rotes Kreuz, kein Abbruch; Vorab-Prüfung mit `File.Exists` im Code |
| Bild per VB-Code zeichnen (`System.Drawing`) | geht mit Kniff | A | nur kleines Bild (300×150 lief); 1600-px-Karte fiel zeitlich mit einem Allplan-Absturz zusammen, nicht einsetzen |
| Rahmen am Bild, `Sizing` FitProportional und Fit, Clip, AutoSize | geht | A | Fit verzerrt, AutoSize lässt die Zelle wachsen |

## Parameter (Stellschrauben)

Gemessen bei der Datei-Ausgabe (PDF) mit den Vorgaben der Datei. Allplan nimmt feste Werte und eigene Hilfen (`<Prompt>@Nr@`, `Distinct(…)`); **Ausdrücke in Vorgaben und Listen wertet es nicht aus** (kopflos schon: dort weicht das Ergebnis ab). Im Fenster macht ein einziger ungültiger Parameter den ganzen Report leer (Abschnitt „Bedienung“).

| Vorgabe in der Datei | Urteil | Beleg | Was Allplan liefert |
|---|---|---|---|
| String, Integer, Float, Boolean, Liste mit Label, fester Wert | geht | A | der Wert; `Parameters!x.Label` liefert den Anzeigetext |
| DateTime fest: `2026-11-19`, `2026-11-19T00:00:00`, `11/19/2026` | geht | A | `19.11.2026 00:00:00`; deutsch `19.11.2026`: Definition ungültig, keine Datei |
| `MultiValue` mit festen Vorgaben | geht | A | genau diese; `Join`, `Count`, Filter `In` |
| `MultiValue` ohne Vorgabe, feste Liste | geht mit Kniff | A | nur der ERSTE Listenwert; Vorgabewerte nennen |
| `MultiValue` mit `<Prompt>Distinct(Fields!X.Value)</Prompt>`, ohne Vorgabe | geht | A | ALLE Werte, leerer zuerst („keine Auswahl = alle“); V: 188 von 551 Vorlagen; Fenster: Abschnitt „Bedienung“ |
| String ohne Vorgabe mit `AllowBlank`; `Nullable` (String, DateTime) ohne Vorgabe | geht | A | leerer Text; `Nothing` (`IsNothing`) |
| Integer ohne Vorgabe | geht nicht | A | Typfehler, keine Datei |
| Vorgabe als Ausdruck, String (`="A" & "B"`, abhängig von anderem Parameter) | geht nicht | A | leerer Text, wie „keine Vorgabe“ |
| Vorgabe als Ausdruck, Integer (`=1+1`) oder DateTime (`=Today()`) | geht nicht | A | Typfehler, keine Datei; Datum stattdessen: Prompt `@401@`, `=Today()` im Ausdruck oder String-Parameter plus `CDate` |
| Liste als Ausdruck in `ValidValues`; `ValidValues` oder `DefaultValue` per `DataSetReference` | geht nicht | A | „Parameter nicht angegeben“, keine Datei |
| Abhängige Liste | geht mit Kniff | A | Kombi-Liste „Art\|Typ“ plus `Split`, oder zwei freie Listen plus Passungsprüfung im Report |
| `Hidden` mit Vorgabe | geht nicht | F | im PDF gilt der Vorgabewert; im Fenster steht der Parameter sichtbar und änderbar da |
| Datum als String-Parameter plus `CDate` im Ausdruck | geht | A | ISO und deutsch lesbar, `DateAdd` geht |
| Parameter steuert Gruppe, Sortierung, `TopN` (`=Parameters!S_TopN.Value`), Titel, Schwelle, Sichtbarkeit | geht | A | mit den Vorgaben der Datei; ausgeblendetes Element lässt Lücke |
| Wert nicht in `ValidValues` | geht nicht | K | gilt als fehlender Wert |
| Parameterwert beim kopflosen Rendern setzen (`Name=Wert`) | geht | K | nur Werkstatt; in Allplan gilt die Vorgabe |

## Strichcode und QR-Code

Allplan hat kein Strichcode-Feld. Es geht als Bild aus dem `<Code>`-Block (`werkzeug/vb/codes.vb`, Einbau und Grenzen: `codes.md`); aus dem Allplan-PDF mit einem Decoder gelesen.

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Code 128 als Bild aus VB, auch je Tabellenzeile | geht | A | 9 von 9 Codes gelesen; ASCII 32 bis 126; auch mit echten Bauteil-IDs im fließenden Report (Etikettenblatt: alle 8 QR- und 8 Strichcodes je PDF aus dem Allplan-PDF zurückgelesen, deutsch und englisch, an zwei Projekten) |
| Code 39 als Bild aus VB | geht | A | nur `0-9 A-Z - .` und Leerzeichen; Großbuchstaben |
| Code 39 aus Tabellenzellen (fester Text) | geht mit Kniff | A | 127 Zellen für 6 Zeichen, 120 KB; besser das VB-Bild |
| QR-Code aus eigenem VB-Generator (Version 1 bis 5) | geht | A | 8 von 8 Codes gelesen, auch mit echten Bauteil-IDs im fließenden Report; höchstens 106 Byte, sonst leeres Bild ohne Fehler (Kürzung: `Code.EtikettText`, `codes.md`); `System.Drawing` als `CodeModule` |

## Zweite Datenquelle im Code (CSV)

Einbau und Grenzen: `codes.md`, VB-Code `werkzeug/vb/zweite_datenquelle.vb`.

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| CSV im `<Code>`-Block lesen, je Zeile über Bauteil-ID (`@10@`) oder `RowNumber` zuordnen | geht | A | **absoluter Pfad; das Arbeitsverzeichnis ist der Allplan-Programmordner** |
| Ordner lesen, Umgebungsvariablen, Registry (HKCU, HKLM lesen), Datei schreiben | geht | A | Allplan gibt dem Code Vollzugriff; kopflos gesperrt (`SecurityException`), dort `--fulltrust` |
| `CodeModules` `System.Windows.Forms`, `System.Web.Extensions`; `<Classes>` | geht | A | Screen, JSON-Parser, Klasseninstanz liefen; `System` selbst nicht eintragen |

## Bedienung im Allplan-Fenster

Beleg F: im Report-Fenster bedient und fotografiert; die Zeilen zeigen, was der Anwender dort erlebt.

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Parameter mit Vorgabe erscheint links unter „Benutzerinteraktion“ | geht | A | String, Zahl, Boolean, Float, Datum, `ValidValues` |
| Parameter mit `<Prompt>@Nr@` | geht | A | bekommt den Attributwert (Projektname, Geschoss) |
| Parameterwert beim Export von außen setzen | geht nicht | A | es gilt die Vorgabe |
| Boolean-Stellschraube umschalten | geht | F | die Tabelle rechnet sofort neu |
| Zahl-Stellschraube eingeben | geht | F | Wertfeld anklicken, tippen, Enter; der Report rechnet sofort neu |
| Listen-Stellschraube wählen | geht | F | Aufklapp-Knopf im Wertfeld; Gruppe, Sortierung, `TopN` gehen mit |
| Mehrfachliste aus den Daten (`Distinct`) | geht | F | Modellwerte, alle gewählt, der leere Wert heißt „nicht definiert“; Auswahl im Mehrfach-Dialog nicht geprüft |
| Ein ungültiger Parameter (Ausdruck als Datum oder Zahl, abhängige Liste) | geht nicht | F | Leiste leer, Report leer, Meldung „Im Project_Name-Parameter fehlt ein Wert.“ – sie nennt den falschen Parameter |
| `Hidden` | geht nicht | F | der Parameter steht sichtbar und änderbar in der Leiste |
| Auf- und Zuklappen (`ToggleItem`) | geht | F | Klick aufs Plus, rund 5 s Rechenpause |
| Sortieren per Klick (`UserSort`) | geht | F | Pfeil am Spaltenkopf |
| Sprung in zweiten Report (`<Drillthrough>`) | geht | F | der Zurück-Knopf erscheint erst nach dem Sprung; Ziel im selben Ordner, 6 Allplan-Vorlagen (Schema 2005) |
| Interner Sprung (`BookmarkLink` auf `<Bookmark>`) | geht mit Kniff | F | springt, zeigt vorher aber ein Meldungsfenster mit dem Namen der Sprungmarke |
| Dokumentstruktur (`DocumentMapLabel`) | geht | F | die Leiste erscheint links von selbst, Ebenen aufklappbar, Eintrag springt zur Seite |
| Fixierter Kopf (`FixedData`) | geht | F | sichtbar nur, wenn die Seite höher ist als das Fenster (Zoom 200 %) |
| Unterbericht | geht | F | wie im PDF |
| `Globals!RenderFormat`, `IsInteractive` | geht | F | im Fenster `RPL` und `True`, im PDF `PDF` und `False` |
| Sprung auf Bauteil (`BookmarkLink Zoom:`) | geht nicht gesichert | F | im Testfenster ohne Wirkung und ohne Meldung; im Report über Allplans Befehl „Reports“ nicht geprüft, dem Kunden nicht versprechen; V: 259 Allplan-Vorlagen |
| Bearbeiten-Sprung (`Edit:`) | nicht geprüft | V | Allplan-Vorlagen nutzen es |
| Sichtbarkeit per Parameter oder Datenlage | geht | F | eine ausgeblendete Tabellenspalte gibt Platz frei |
| Interaktion im PDF, DOCX oder XLSX | geht nicht | A | nur im Allplan-Fenster |
| Layout im Fenster wie im PDF | geht, wenn nichts überlappt | F | Text ab 9 pt ist im Fenster 0,5 bis 3 % schmaler als im PDF, Text bis 8,5 pt dagegen 3 bis 8 % BREITER (gemessen: 8,5 pt +3 %, 8 pt +8 %, 6,5 pt +5 %) – kleinem Text 10 % Breitenreserve geben; überlappen sich zwei Elemente im selben Container (auch unsichtbar, auch nur um 0,02 cm), schiebt das Fenster eines davon weg; mindestens 0,05 cm Abstand (`fallen.md`) |
| Ausgeblendetes Feld neben fremden Elementen | geht mit Kniff | F | Ausgeblendete Felder (`Hidden`-Ausdruck) verschieben im Fenster sichtbare Elemente im selben Behälter, wenn ihre Kanten nicht auf deren Kanten liegen (gemessen bis 2,4 cm, auch bei 8 cm Abstand); ein eigener Behälter (Rectangle über die volle Breite, Sichtbarkeit am Behälter) behebt es. Beispiel: drei ausgeblendete Textfelder (Left 1,5 / 7,6 / 13,7 cm) schoben weiter oben auf der Seite die 3. und 4. Kachel einer Vierer-Reihe nach links; sichtbare Nachbarn allein taten es nicht. Ob schon jede kleine Kantenabweichung genügt, ist nicht gemessen |

## Seite und Export

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| A4 hoch, Querformat, A3 | geht | K | |
| Eigener Seitenfuß statt Allplan-Kopf | geht | A | `PageFooter` mit `Globals!PageNumber` |
| Deckblatt (eigene erste Seite) | geht | K | Seitenumbruch Start; Kopf erst ab Seite 2: siehe unten |
| PDF mit Lesezeichen (`Label`, `DocumentMapLabel`), bis 3 Ebenen | geht | A | je Gruppe, Rectangle, Textbox verschachtelt; Leiste im Fenster: Abschnitt „Bedienung“ |
| Link im PDF: `https`, `mailto`, Ausdruck | geht | A | `<Hyperlink>` an Textbox |
| Link im PDF: `file:///` | geht | A | steht als Link im PDF; Ausführung im Betrachter nicht geprüft |
| Link ohne Schema (`www.…`) | geht nicht | A | kein Link; Allplans Stabliste Schweiz nutzt diese Schreibweise |
| Interner Sprung im PDF (`BookmarkLink` auf `<Bookmark>`) | geht nicht | A | kein Link im PDF; Sprung im Fenster: Abschnitt „Bedienung“ |
| Mehrere `<ReportSection>`, eigene Seitengröße je Sektion | geht nicht | A | alle Seiten haben die Größe der ersten Sektion, breitere laufen über; für Hoch und Quer zwei Reports |
| Seitenzählung je Gruppe neu (`ResetPageNumber`), `OverallPageNumber`, `Globals!PageName` | geht | A | `PageBreak` `Between` und `ResetPageNumber` an der Gruppe oder am Rectangle; Seitenzahl nur im Fuß |
| Seitenname (`PageName` an Rectangle oder Gruppe) in Kopf und Fuß | geht | A | `Globals!PageName`; Excel-Blattnamen nicht gemessen |
| Seitenumbruch Start, End an Rectangle, Start an Tablix, Between an Gruppe | geht | A | End der Vorseite plus Start der Folgeseite gibt eine leere Seite |
| `KeepTogether` an Tablix, `KeepWithGroup` After an der Kopfzeile | geht | A | passende Tabelle beginnt auf der Folgeseite, Kopf wandert mit der ersten Zeile |
| Kopf- und Fußzeile nicht auf erster oder letzter Seite (`PrintOnFirstPage`, `PrintOnLastPage`) | geht | A | gilt für die ganze Zeile |
| Kopfelement nur auf Seite 1 | geht mit Kniff | A | `Hidden` als Ausdruck `=Globals!PageNumber > 1` |
| PDF | geht | A | Schriften eingebettet, Bilder 1:1 |
| DOCX mit allen Bildern | geht | A | |
| XLSX | geht mit Kniff | A | nur Rohdatenauszug: keine Layout-Elemente, keine Bilder; Zahlen auf 3 Stellen gerundet, als String voll |
| Layout im XLSX-Export | geht nicht | A | |

## Daten und Abfrage

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Mehrere DataSets | geht nicht | A | nur das ERSTE wird gefüllt |
| Mehrere `SELECT … FROM [Type=0]` in einem DataSet | geht nicht | A | nur das erste liefert Zeilen |
| Untertabelle (`Type=35`, `Type=2`) hinter der Hauptzeile | geht | A | kommt als Folgezeile mit leeren Hauptspalten |
| Eine breite Abfrage, Themen per Filter im Report trennen | geht | A | Spalte `ObjId` aus `@OBJ@` |
| Filter nach Objektart (`@OBJ@.eq.n.or.…`) | geht | A | |
| Rechnen in der Abfrage (`f=`, `_IF_`, `MID`, `VALUE`, `FORMAT`) | geht | A | `GROUP BY` gibt es nicht |
| Wand zum Fenster oder zur Tür | geht mit Kniff | A | `MT_Wand(…)`; `PARENT(…)` liefert den Raum |
| Aggregate `Sum`, `Avg`, `Min`, `Max`, `Count`, `CountDistinct`, `StDev`, `First`, `Last` | geht | A | `Aggregate()` liefert leer |
| Projekttabelle als ERSTE Abfrage (`CURRENT_PROJECT`, `DOCUMENT`, `LAYOUT`, `PROJECT`, `BUILDINGSTRUCTURE`, `LAYOUT_DRAWINGS`) | geht | A | Zeilen kommen (`LAYOUT_DRAWINGS` allein nur 1); PDF und DOCX normal (18 Proben); `projektlisten.md` |
| Projekttabelle als XLSX ausgeben | geht nicht | A | öffnet das Report-Fenster statt einer Datei |
| `DOCUMENT` als Gesamtliste der Teilbilder | geht nicht | A | die Zeilenzahl schwankt je Abfrage (172, 76, 38), Teilbilder auf Plänen fehlen; Pläne (`LAYOUT`) sind stabil |
| Projekttabelle `LAYOUT_HISTORY`, `ATTRIBUTES`, `FILESET` mit `WHERE @1155@.eq."Item"` als erste Abfrage | geht nicht | A | im Test ohne Zeilen; ob Daten oder Tabelle die Ursache sind, ist offen; `FILESET` ohne `WHERE` liefert eine Knotenzeile |
| Bauteildaten im Report auf einer Projekttabelle | geht nicht | A | nur ein DataSet wird gefüllt |
| Filter `In`, `Between` an der Tabelle | geht | A | `Between`: zwei `FilterValue` gleichen Typs, z. B. `=1.0` |
| Filter `Like` an der Tabelle | geht mit Kniff | A | Platzhalter `*`; `%` trifft nichts |
| Deckblattdaten | geht mit Kniff | A | Projektattribute als Spalten der Modellabfrage oder Parameter mit Prompt |
| Layer, Stiftnummer als Attribut | geht nicht | A | Wert immer leer |
| Abfrage ohne Treffer im ersten DataSet | geht nicht | A | Meldungsfenster, keine Datei |
| Leere Tabelle durch Filter im Report | geht | A | `NoRows` zeigt den Text |

## Bewehrung

Spalten, Rechenregeln, englische Begriffe: `bewehrung.md`.

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Stäbe und Matten in EINER Abfrage: `FROM [ENGINEERING,Filter=@793@\|@792@\|@1210@]` | geht | A | Stab `@OBJ@` 257, Matte 368 |
| `FROM [REINFORCEMENT_DATA]` mit `@10@` | geht nicht | A | die Abfrage schlug fehl; `ENGINEERING` nehmen |
| Stab oder Matte unterscheiden | geht mit Kniff | A | über `@OBJ@` (`ObjId`), nie über einen Text aus der Abfrage |
| Gewicht, Länge, Stückzahl je Position | geht | A | kommen aus Allplan; die Summen gleichen Allplans „Übersicht Bewehrung“ (912,6 kg Rundstahl, 217,9 kg Matten im Testteilbild) |
| Biegeform-Bild (`@205@` mit `Projection=0`, `GText=HD_CENTERMIDDLE`) | geht | A | Biegeform mit Maßen, klein |
| Schenkelmaße a bis j (`@798@` mit `Index`) | geht nicht | A | liefert 0 |
| Länge in lfdm (`@797@`) | geht nicht | A | Text mit Komma; `@757@` mit `Dim=3` ist die Zahl in m |

## Tempo

| Was | Urteil | Beleg | Hinweis |
|---|---|---|---|
| Export ohne Bild (129 Zeilen) | geht | A | 4,4 s; Grundlast je Export 2–5 s |
| Kleine Bauteilbilder (129 Zeilen, 90 verschiedene) | geht | A | 6,7 s; gleiche Geometrie gleiches Bild |
| Seite mit 51 Bauteilbildern, Diagrammen, Messanzeigen | geht | A | 4–6 s |
| Master (10 Seiten, 1,2 MB) im Report-Fenster | geht mit Kniff | F | erste Seite nach 22–24 s, jede weitere 5–15 s; das PDF einer Einzelseite braucht 6 s |
| Tausende Zeilen mit `@205@` | geht mit Kniff | A | 3.545 Zeilen rund 3 Minuten, Allplan „reagiert nicht“; Bildspalte weglassen oder Abfrage einschränken |
| Sehr viele Report-Ausgaben in EINER Allplan-Sitzung | geht nicht unbegrenzt | A | Allplan gibt je Ausgabe rund 30 Fenster-Handles und 10 bis 20 MB nicht zurück (auch mit Allplans eigener Vorlage gemessen); nach einigen hundert Ausgaben stürzt Allplan ab. Bei Serien Allplan zwischendurch neu starten |
| Groß- und Kleinschreibung beim Gruppieren | geht mit Kniff | A | ohne Angabe gruppiert der Report „Flur“ und „FLUR“ zusammen und zählt sie doch doppelt; `<CaseSensitivity>True</CaseSensitivity>` im DataSet macht beides gleich (`fallen.md`) |
| Mehrere Exporte gleichzeitig | geht nicht | A | Allplan meldet „busy“; ein Export nach dem anderen (Absturz mit parallelem Helfer, Ursache offen) |

## Die harten Grenzen

1. Nur das ERSTE DataSet wird gefüllt, jedes weitere hat 0 Zeilen; ebenso liefert nur das erste `SELECT … FROM [Type=0]` Zeilen. Ein Report braucht EINE breite Abfrage.
2. Je Report nur EINE Bildart aus dem Modell: die erste `@205@`-Spalte bestimmt alle Bilder (Ausnahme Untertabelle `Type=35`).
   Unterberichte heben beide Grenzen NICHT auf: Allplan führt die Abfrage eines Unterberichts nicht aus, sondern gibt ihm die Zeilen des Hauptreports.
3. Kein Farbverlauf, keine Schraffur, kein Schatten, keine Transparenz in Farben, keine Rahmen Groove/Ridge/Inset/Outset an Textbox und Rectangle; runde Ecken nur als PNG.
4. Bilddateien nur PNG, JPG, GIF, BMP; SVG und TIFF zeigen ein rotes Kreuz; halbtransparente PNG-Pixel erscheinen deckend.
5. Bedienung (Parameter, Klicksprung, Aufklappen) gibt es nur im Allplan-Fenster, nicht im PDF, DOCX oder XLSX; Parameterwerte lassen sich beim Export nicht von außen setzen.
6. Liefert das erste DataSet keine Zeile, öffnet Allplan ein Meldungsfenster und schreibt keine Datei; eine Projekttabelle als XLSX öffnet das Report-Fenster statt einer Datei.
7. XLSX enthält nur Rohdaten (keine Bilder, kein Layout, Zahlen auf 3 Stellen); DOCX und PDF enthalten die Bilder.
8. `Globals!PageNumber` und `TotalPages` nur in Kopf oder Fuß; im Body bricht der Report ab.
9. Tempo: jede Zeile mit `@205@` kostet Rechenzeit, auch wenn das Bild nirgends gezeigt wird (3.545 Zeilen rund 3 Minuten).
10. Fehler in Diagrammen erscheinen nur als Text im Bild, der Renderer meldet nichts; jedes Bild muss angesehen werden.
11. Eine wachsende Tabelle schiebt alles darunter und daneben weg, ausgeblendete Elemente lassen ihre Lücke (ausgeblendete Tabellenspalten und -zeilen nicht); Seitenzahl und Layout hängen an den Daten.
12. Nicht auswertbar: Layer und Stiftnummer; `@87@` liefert nur Polygon-Text, keine Karte; Bauteilbild kennt keine Linienstärke und zeigt Raum und Sammelobjekte nur im Planmodus.
13. Vorgaben und Listen von Parametern sind feste Werte: Ausdrücke, `DataSetReference` und Integer ohne Vorgabe führen zu leerem Text, Typfehler oder „Parameter nicht angegeben“ (Abschnitt „Parameter“).

## Nicht geprüft

- Im Fenster: Klick ins Modell (`Zoom:`, `Edit:`) in einem Report, den Allplans Befehl „Reports“ öffnet; Tooltips; angeklickte Hyperlinks; Auswahl im Mehrfach-Dialog (`Distinct`); Export aus dem Fenster; ob das Meldungsfenster beim internen Sprung auch über „Reports“ erscheint.
- Mehrspaltiger Body (`Columns=2`/`3`) in Allplan; Allplan-Vorlagen nutzen ihn in 6 Dateien.
- `MergeDataSet` und Vorlagen mit mehreren DataSets (Bewehrung); `Lookup` zwischen zwei DataSets ist nicht messbar (nur das erste DataSet wird gefüllt).
- Karte aus `@87@` per VB-Code in Allplan; Ursache des Allplan-Absturzes vom 2026-11-18 ist offen.
- Laufzeit mit mittleren und großen Bildern und mit 130 Zeilen im Planmodus; Druckerrand bei Seitenrändern 0.
- Bildparameter `GText=HD_CWF`, `MSSK`, `BUTTON`, `Stapel` an Bewehrung; `Hidden`-Bits 8, 32, 128, 256; Textur an Beton.
- `HideDuplicates`, Diagramm in Seitenkopf, HTML `<sup> <sub> <p> <div>`.
- `Writable`, `DeferVariableEvaluation`; Zeichenumbruch bei `CanGrow` ohne Leerzeichen; `Like` mit `?` und `#`.
- Excel-Blattnamen (`PageName`), `InitialPageName`, Tooltips im PDF, `BreakLocation` End an Tablix, Start und End an Gruppe, `KeepWithGroup` Before, `file:///`-Link im PDF-Betrachter, DataSet-Name und mehrere DataSets im Unterbericht-Ziel.
- Parameter: String ohne Vorgabe und ohne `AllowBlank`; ob `DataSetReference` an der Referenz oder an der fehlenden Vorgabe scheitert.
- Weitere Codes (EAN, Data Matrix, Code 93), QR über Version 5; Strichcodes bei 3.000 Zeilen in Allplan; CSV mit anderem Trennzeichen als Semikolon.
- Projekttabellen: Ursache der leeren Ausgabe bei `LAYOUT_HISTORY`, `ATTRIBUTES`, `FILESET` mit Filter (Daten oder Tabelle).
- Bewehrung: Attribute ohne Vorbild (Biegerolle `@18478@`, Betondeckung, Block `@18511@` bis `@18529@`).
- Internet-URLs für Bilder, WMF, animierte GIF; Hintergrundfarbe am `Image`.
- Alle mit K belegten Zeilen (Linie, Fläche, Radar, Trichter, Strip Line …) sind in Allplan nicht angesehen.

