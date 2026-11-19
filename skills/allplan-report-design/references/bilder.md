# Bilder aus dem Modell und aus Dateien

Alles im echten Allplan 2027 gemessen (Test-Teilbild des Masters, PDF-Export). Gilt für `@205@` (Bauteilbild) und `<Image>`.

## Zwei Betriebsarten von `@205@`

| Art | Abfragezeile (kopierbar) | Liefert |
|---|---|---|
| 3D (`Projection`) | `@205@[Name=Bild\|Projection=7\|Hidden=5\|Width=60\|Height=40\|GText=HD_CENTERMIDDLE]` | Ansicht des einzelnen Bauteils, farbig/texturiert wählbar |
| Plan (`Image=true`, ohne `Projection`) | `@205@[Name=Bild\|Image=true\|Scale=100\|Width=70\|Height=60\|GText=HD]` | 2D-Planausschnitt wie im Teilbild (Schraffur, Türschwenk, Fensterstrich), auf das Bauteil samt Nachbarn zugeschnitten |

- `Image=true` mit `Projection=7`: Projektion gewinnt (3D). `Projection=0` mit `Image=true`: Planbild.
- Im Planmodus wirkt `Hidden` nicht; `Scale=50`/ohne füllt den Kasten, `Scale=200` verkleinert.
- **Regel: Die erste `@205@`-Spalte bestimmt alle Bilder des Reports.** Weitere `@205@`-Spalten (andere Ansicht, Größe,
  Planmodus) zeigen dasselbe Bild. Zwei Bildarten = zwei Reports (zweites DataSet bleibt leer, siehe daten.md).
  Ausnahme: Untertabelle `SELECT … FROM [Type=35]` bringt für Räume ein eigenes Bild (Bemaßungsskizze der Fläche):
  `@205@[Name=Graphics|Scale=100|Projection=10|Hidden=1|Width=70|Height=60|GText=HD] FROM [Type=35]`.
- Je Abfrage genau eine Bildart planen; keine Linienstärke, keine Animation; Alpha-Pixel erscheinen deckend.
- Bildformat im PDF: JPEG, DeviceRGB. Report-Feld: `rd:TypeName System.Byte[]`, Image `Source=Database` mit `MIMEType`.

## Ansichtsnummern (`Projection=`, Ziffernblock)

Die Ansichten sind **Weltrichtungen**, nicht Bauteilachsen (eine in Y laufende Wand zeigt bei 2 nur ihr Schmalende).

| Wert | Ansicht |
|---|---|
| 0, 5 | Draufsicht (Grundriss) |
| 2, 8 | von vorn / von hinten |
| 4, 6 | von links / von rechts |
| 1, 3, 7, 9 | Isometrie aus den vier Ecken (9 = Standard der Allplan-Vorlagen; Bausatz nutzt 9, Empfehlung 7) |
| 12 | schmale Seitenansicht (Schnitt quer) |
| 10, 11, 13, 14 | leer (Ausnahme: 10 mit `Type=35`, s. o.) |

## `Hidden` (Bitfeld, nur 3D)

Merksatz: Bit 1 anlassen. +2 Textur (grau, wenn das Bauteil keine hat), +4 Bauteilfarbe, +16 verdeckte Kanten
gestrichelt, +64 SmartParts in der Wand mitzeichnen. Bits 8, 32, 128: keine/kaum Wirkung.

| Wert | Wirkung |
|---|---|
| fehlt / 0 | Wand, Stütze: Drahtmodell mit sichtbaren verdeckten Kanten, Wandöffnung unsichtbar; **Fenster: kein Bild** |
| 1 | verdeckte Kanten weg, Strichzeichnung grau |
| 3, 7 | Fläche gefüllt grau; mit Textur, wenn vorhanden (Holzfenster: Holz) |
| 5 | Flächen in **Bauteilfarbe** (Fenster beige, Wand/Stütze grau), Farbe im PDF |
| 13 | wie 5 mit mehr Binnenlinien (Flügeldetail) |
| 17 / 21 | wie 1 / 5, verdeckte Kanten hell gestrichelt |
| 64 | Wand: farbiges Drahtmodell mit eingebautem Fenster-SmartPart; Fenster allein: kein Bild |
| 65 / 69 | wie 1 / 5, SmartParts in der Wand mitgezeichnet |
| 67, 71 | Holztextur, SmartParts in der Wand (`SmartParts Übersicht` nutzt 67 mit `Dim=1`) |
| 75, 79, 83, 255 | wie 67 mit mehr Detail / bis ca. 4000 Farbwerte |
| 2, 4, 6, 8, 16, 32, 128 (ohne Bit 1), 66, 257 | Fenster/Stütze ohne Bild bzw. Wand wie 0 |

Weitere Schlüssel: `Dim=0/1` bildgleich, `Dim=2` an Fenster = kein Bild; `CanSave=true` ohne Wirkung. Unbekannte Schlüssel
(`Farbe`, `Fill`, `Hight` …) werden **ignoriert** (Tippfehler wirkt nicht!). Schlüssel nicht groß/klein-empfindlich,
**Werte schon** (`hd` ≠ `HD`). Farbe/Füllung/Textur gibt es nur über `Hidden`.

## `GText`

| Wert | Wirkung |
|---|---|
| `HD` | Zeichnung linksbündig im Kasten |
| `HD_CENTER`, `HD_CENTERMIDDLE`, `HD_CENTER_MIDDLE`, `BSHDCENTERMIDDLE` | pixelgleich, waagerecht zentriert (flache Bauteile in Zellenmitte) |
| `HD_CWF`, `HD_WDL` | wie `HD` am Bauteil Wand |
| fehlt, `BUTTON`, `hd`, unbekannt | Notbild 130×113 px, `Width`/`Height` wirkungslos |
| `MSSK`, `MSSK_SCH` | Mini-Tabelle / farbiger Text „Summe 0 0,00“ (Bewehrungsskizze, an Bauteilen sinnlos) |
| `Stapel` | kein Bild |

## Width, Height, Scale, Pixelgröße

- **Immer `GText=HD…` mit `Width` setzen.** Ohne `Width` kein Bild (nur `Height`=40 → kein Bild).
- 7,56 Pixel je mm (192 dpi). `Width`/`Height` (mm) sind Obergrenzen; die Höhe wird auf den Inhalt gekürzt.

| Width×Height mm | Pixel |
|---|---|
| 45×30 | 340×226 |
| 60×40 | 454×302 (Karte) |
| 90×60 / 180×120 | 680×454 / 1360×908 |
| 180×250 | 1360×994 (Höhe auf Seitenverhältnis gekürzt) |
| nur Width=60 | 454×332 (Höhe automatisch) |

- Nur `Image=true|GText=HD` ohne Maße: volles Bild 1442×914 px (190×120 mm).
- `Scale` ist ein **Zielmaßstab**: 100 → echter Maßstab 1:100, Zeichnung kleiner, Höhe gekürzt; 25/50/ohne füllen den Kasten.
  Vergrößert nie über den Kasten.
- Sizing am Image: `FitProportional` maßstäblich (Standard), `Fit` verzerrt, `Clip` abgeschnitten, `AutoSize` Zelle wächst.
- Bildzeilen kosten Rechenzeit auch ungezeigt (51 Zeilen 4–6 s, 3.545 Zeilen ca. 3 min): bei großen Modellen Bildspalte weglassen.

## Objektart → Bild

| Objektart (`@OBJ@`) | 3D (`Projection`) | Plan (`Image=true`) |
|---|---|---|
| Wand 1 | ja: 7, Längsansicht 4/6; Hidden 65/69 mit Fenstern | Wandstreifen mit Öffnung, Schraffur |
| Stütze 3, Unterzug 6 | ja: 7 | Umriss und Nachbarlinien |
| Decke 4, Bodenplatte 704 | Rechteck (0/5) oder Platte (7), **kein Gebäude** | **ganzer Grundriss des Teilbilds** |
| Raum 61 | **kein Bild** | Grundriss des Raums mit Wänden, Türen, Fenstern: **nur im Planmodus** |
| Fenster 991, Tür 992 | ja: 2 (von vorn), 7; `Hidden` ungerade | Wandausschnitt mit Symbol und Schwenkbogen |
| Fenster-/Türöffnung 23/22, -element 43/42 | ja (grauer Negativkörper), 7 | wie SmartPart |
| Sammelobjekte: Gesamtwand 2, Decke gesamt 1005, Gesamt-Plattenfundament 1107, Gesamtfenster-/türöffnung 1095/1094 | kein Bild | Bild vorhanden (Decke gesamt = ganzer Grundriss) |

**Ganzer Grundriss:** `Image=true` an der Decke (auch Bodenplatte, Decke gesamt, Gesamt-Plattenfundament):
```
SELECT @498@[Name=Objekt], @205@[Name=Bild|Image=true|Width=180|Height=250|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.4]
```
Body-Höhe des Bildes nicht über 24,5 cm wählen (sonst zweite Seite). Mehrere Decken im Teilbild: ein Bild über Gruppe `=1` und `First()`.
`Mengen (Grafik).rdlc` zeigte im Test-Teilbild keine Bilder (Grund ungeklärt).

## Grundriss: m², Maße, was ins Bild kommt (gemessen 2026-11-18)

- Das Planbild (`Image=true`) zeigt, was im Teilbild liegt **und innerhalb der Kante des abgefragten Bauteils**
  (Decke = ganzer Grundriss, Raum = Raumausschnitt).
- **Raumbeschriftung** (Name, m²) erscheint, wenn sie im Teilbild als Text bzw. Beschriftung liegt. Der Report
  schreibt nichts ins Bild; fehlt die Beschriftung im Teilbild, fehlt sie im Bild.
- **Maßketten innerhalb** der Deckenkante erscheinen; **Maßketten außerhalb werden abgeschnitten**. Maße, die
  im Report zählen, gehören nach innen oder als Zahl neben das Bild (Länge/Breite aus der Abfrage).
- Bei mehreren Decken die größte nehmen (kleine Decken zeigen nur ihren Ausschnitt).

## Raum-Abwicklung (gemessen 2026-11-18, alles in Allplan bewiesen)

**Der Report zeichnet nicht selbst – er zeigt nur, was im Teilbild liegt.** Die Abwicklungs-Zeichnung muss vorher
im Teilbild liegen. Ohne sie bleibt der Abschnitt leer.

Drei Wege wurden in Allplan ausprobiert, einer trägt:

| Weg | Ergebnis |
|---|---|
| Allplans Aufmaßskizze (`@205@` mit `Projection=10` an den Ausbau-Seitenflächen, `@OBJ@` 62) | **verworfen**: Wandstücke kreuz und quer, Zahlen übereinander, auch vergrößert unlesbar (Urteil des Anwenders). Die Zahlen daneben (Fläche je Belag, Leibung) stimmen und bleiben im Report „Wandbeläge“. |
| Echte Allplan-Ansichten (`CreateSectionsAndViews`) | **geht nicht**: Die Abfrage kennt Ansichten nicht als Objekt; im Planbild eines Rahmens erscheinen nur Überschrift und Maßkette der Ansicht, ihr Inhalt (Wandkanten, Türen) nicht. |
| Eigene 2D-Zeichnung im Teilbild + Rahmen | **geht**: Linien, Füllflächen und Texte erscheinen im Planbild vollständig und farbig. |

### Wie die Zeichnung aussieht

EIN zusammenhängendes Band je Raum: Wände im Uhrzeigersinn ab der längsten (von innen gesehen links nach rechts),
Knicklinien an den Ecken, jede Wand in wahrer Länge – L-förmige Räume und schräge Wände gehen. Dazu eine
durchlaufende Maßlinie mit JEDEM Abschnitt (enge Zahlen rücken in eine tiefere Zeile und bekommen einen Hinweisstrich),
Türen und Fenster farbig mit Kürzel T1/F1, eine Legende (bis 3 Zeilen) und eine Lageskizze mit Wandnummern und Startmarke.
Ab Maßstab 1:300 bricht das Band an einer Ecke in eine zweite Reihe um. Deutsch und englisch (`--sprache=de|en`).

### Die Werkzeuge (`<REPORT>/werkzeug/`)

| Datei | Aufgabe | Braucht Allplan? |
|---|---|---|
| `abwicklung_kern.py` | Rechenkern, reines Python: Raumumriss + Höhe + Körper der Öffnungen → Zeichenelemente. 8 Tests in `werkzeug/tests/` | nein |
| `abwicklung_zeichnen.py` | Datei → Zeichenauftrag (`<auftrag.json>`): `python abwicklung_zeichnen.py <elemente.json> <auftrag.json> [--scale=100] [--sprache=de\|en]` | nein |
| `abwicklung_vorschau.py` | Auftrag → Bild je Raum: `python abwicklung_vorschau.py <auftrag.json> <ordner>` | nein |

Ein Beispiel ohne Allplan: `python werkzeug/tests/test_abwicklung_kern.py <ordner>` schreibt `faelle.json` (L-Raum, schräger Raum,
langer Flur); danach `abwicklung_zeichnen.py faelle.json auftrag.json` und `abwicklung_vorschau.py auftrag.json <bilder>` (in der
angelegten Werkstatt durchgespielt).

Eingabeform (a) des Zeichners ist die eigene Form des Kerns (`raeume` mit `punkte`, `oeffnungen` mit `ecken`, Meter) und kennt den
echten Raumumriss.

### Welche Daten der Kern braucht (in Allplan gemessen)

| Was | Woher |
|---|---|
| Körper der Öffnungen | nur die Elemente `DoorTier`/`WindowTier` und `DoorReveal`/`WindowReveal`: `GetModelGeometry()` liefert ein Polyhedron3D mit 8 Ecken. Die Hauptelemente `Door`/`Window` liefern nichts. |
| Raumumriss | `GetGroundViewArchitectureElementGeometry()` |
| Raumhöhe | `GetPureArchitectureElementGeometry()` |
| Teilbildmaßstab | `document.GetScalingFactor()` |

### Die Zeichnung in Allplan ablegen

**Dieses Paket legt keine Zeichnung in Allplan ab.** Der Rechenkern liefert die Geometrie, `abwicklung_zeichnen.py` den Zeichenauftrag und
`abwicklung_vorschau.py` das Bild je Raum – alles ohne Allplan. Ein Werkzeug, das die Elemente ins Teilbild schreibt und den Rahmen je Raum anlegt,
ist nicht Teil des Pakets; die Zeichnung im Beispiel wurde eigens angelegt. Ohne Zeichnung im Teilbild bleibt die Vorlage
„Report Master Raum-Abwicklung“ leer – das dem Anwender vor der Übergabe sagen. Der Rahmen je Raum ist eine Decke mit Material „Abwicklung“ (1 cm dick,
unter Null) und trägt in Attribut 507 die Bauteil-ID des Raums. Der Report wird über das Modell-Teilbild UND das Zeichnungs-Teilbild ausgegeben
(Abfrage `@OBJ@.eq.4.or.61`, Bild `@205@[…|Image=true|Width=170|Height=90]`); die Raumwerte holt `Lookup` über die Bezeichnung des Rahmens.

### Regeln dahinter

- **Schrift im Bild rechnet man vom Report her**: Das Bildfeld ist 170 × 90 mm; der Rahmen hat dasselbe Seitenverhältnis, und jede
  Texthöhe ist in Report-Millimetern festgelegt (2,7 bzw. 2,3 mm) und wird mit dem Maßstab des Rahmens ins Modell umgerechnet.
  So ist die Schrift in jedem Raum gleich groß, egal wie lang die Wände sind.
- **Allplans Maßketten nicht verwenden**: ihre Texthöhe hängt am Teilbildmaßstab und wird im Bild winzig. Maßlinien selbst
  zeichnen (Strich, Marken, Zahl nur wo sie hineinpasst).
- **Abstand zum Modell**: Das Modell-Teilbild ist beim Report mitgeladen. Zeichnungen mindestens 15 m neben das Gebäude legen,
  sonst ragt der Grundriss ins Bild (`abwicklung_zeichnen.py` rückt selbst unter das Gebäude).
- Der Rahmen ist eine echte Decke: nie ins Modell-Teilbild legen, sonst zählt er in Mengen mit.
- Die Zeichnung ist ein Abzug: nach Änderungen am Modell neu rechnen und einbauen. Die Zahlen der Kopfzeile kommen live aus Allplan.
- Beleg: Die gerechnete Netto-Wandfläche des Bandes ist gegen Allplans `@295@` geprüft – Test
  `test_netto_wandflaeche_stimmt_mit_allplan_ueberein` in `werkzeug/tests/` (8 Tests insgesamt).

## Bilder aus Dateien (`<Image>`, unabhängig von `@205@`)

| Fall | Ergebnis |
|---|---|
| External, fester Pfad `file:///C:/…` | geht |
| External, Pfad aus ReportParameter (`=Parameters!Bildpfad.Value`) | geht |
| External, Pfad aus Datenfeld (`="file:///C:/Bilder/material_" & Fields!Material.Value & ".png"`) | geht, auch Leerzeichen und Umlaute |
| Embedded (`<EmbeddedImages>`), Auswahl per Ausdruck (`IIF`/`Switch`) | geht, PNG mit Transparenz sauber |
| `BackgroundImage` (Rectangle/Textbox) | Naturgröße ab links oben, abgeschnitten, nicht skaliert; `BackgroundRepeat`: Repeat, NoRepeat, RepeatX, RepeatY |
| Formate | PNG, JPG, GIF, BMP; **TIFF und SVG = rotes Kreuz** |
| Datei fehlt | rotes Kreuz 15×17 px oben links, kein Fenster, kein Abbruch (Abfangen: Leerbild-Datei oder `Code.DateiDa`) |
| großes Bild (2480×3508) | verlustfrei 1:1 im PDF |
| http | lokaler Server geht, 404 = Kreuz |

Pfade immer `file:///` mit Schrägstrichen; der Firmenlogo-Pfad kann ein Allplan-Systemparameter sein (`Company_Logo`).
`@87@` (SVG-Map) liefert nur Polygon-Text (mm, y negativ), kein SVG.

## Export-Formate

PDF: `@205@` als JPEG, Dateibilder 1:1. **XLSX: keine Bilder** (`@205@`-Spalte wird eine Zahl). **DOCX: alle Bilder.**

## XML-Ausschnitte (Schema 2016)

```xml
<Image Name="Karte"><Source>Database</Source><Value>=First(Fields!Bild.Value)</Value><MIMEType>image/jpeg</MIMEType>
  <Sizing>FitProportional</Sizing>
  <ActionInfo><Actions><Action><BookmarkLink>="Zoom:" + First(Fields!Nr.Value) + ",Mark:" + First(Fields!Nr.Value)</BookmarkLink></Action></Actions></ActionInfo>
  <ToolTip>Klick: in Allplan zoomen</ToolTip></Image>
<Image Name="MatIcon"><Source>External</Source>
  <Value>="file:///C:/Bilder/material_" &amp; Fields!Material.Value &amp; ".png"</Value><Sizing>FitProportional</Sizing></Image>
<EmbeddedImages><EmbeddedImage Name="ampel_rot"><MIMEType>image/png</MIMEType><ImageData>…base64…</ImageData></EmbeddedImage></EmbeddedImages>
<Image Name="Ampel"><Source>Embedded</Source><MIMEType>image/png</MIMEType><Sizing>FitProportional</Sizing>
  <Value>=IIF(Fields!Laenge.Value&gt;15,"ampel_rot","ampel_gruen")</Value></Image>
<Style><BackgroundImage><Source>Embedded</Source><Value>wasser</Value><BackgroundRepeat>NoRepeat</BackgroundRepeat></BackgroundImage></Style>
```
Zoom-Klick: im PDF wirkungslos, im Testfenster ohne Wirkung gemessen (`grenzen.md`, Bedienung); `@10@` als `Nr` ins DataSet nehmen. Schema 2005: `<Action>` direkt am
Image, `<EmbeddedImages>` steht **vor** `<PageWidth>`, Reihenfolge Sizing, Source, MIMEType, Value.

Nicht geprüft: Internet-http; Hidden-Bits 8/32/128/256; Textur an Beton/Wand; `HD_CWF`/`MSSK` an Bewehrung; welche Ebenen der Planmodus zeigt; `BackgroundColor` am Image; SVG-Karte per Code im echten Allplan.

