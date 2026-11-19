# Wunsch → Weg

Die erste Datei bei einem neuen Wunsch des Kunden: Wunsch in Alltagssprache, Urteil, womit man ihn baut. Das Urteil gilt für die Ausgabe in Allplan;
steht „(K)“ oder „(V)“, ist es dort noch nicht bewiesen (Belegstufen: `grenzen.md`).

- **Kennung** (K010, D040 …): fertiger Baustein, Bauplan in `bausteine.md`, Maße und Parameter in `masse.md`; bestellen mit `master/build_auswahl.py`.
- **`c.…`** = Bausatz-Funktion in `master/core.py`, **`viz.…`** in `master/viz.py`.
- **`grenzen.md` · Abschnitt**, **`fallen.md` · Abschnitt**: Urteil und Kniff stehen dort; **Datei** = eigene Referenz.
- Ein Wunsch, der hier fehlt oder dessen Zeile „(K)“ trägt: erst `grenzen.md` lesen, dann bauen, in Allplan ansehen (SKILL.md, Regel „Der Beweis ist Allplan“).

## Diagramme und Anzeigen

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „Balken, größter oben, Wert am Balken“ | geht | D040 (Rangliste), D010 (je Materialgruppe) |
| „Säulen je Bauteilart“, „gestapelt“, „Anteile in Prozent“ | geht | D030, D050 (gestapelt), D060 (100 %) |
| „Kuchen“, „Ring mit Zahl in der Mitte“ | geht | D020, D090, D100; höchstens 5 bis 7 Segmente, eigene Legende |
| „Summenlinie“ (Pareto) | geht | D070 (zweite Achse, nur Schema 2016) |
| „Fläche gegen Volumen“, „Blasen“, „Rechtecke nach Größe“ | geht | D130 (Punkte), D140 (Blasen), D120 (TreeMap) |
| „Verlauf über die Zeit“ (Linie, Fläche) | geht (K) | `viz.chart` mit Typ Line; `grenzen.md` · Diagramme |
| „Trendlinie“, „Karte“, „Schatten“, „Sunburst“ | geht nicht | `grenzen.md` · Diagramme; statt Karte Tabelle oder Grundriss (B080), statt Sunburst TreeMap (D120) |
| „kleines Diagramm in der Tabellenzeile“ | geht | T010, T050, T070 (Zellenbalken, Stapel, Mini-Säulen) |
| „Tacho“, „Fortschrittsring“, „Ziel erreicht?“ | geht | M020, M030, M040 (Zielbalken), M050 |
| „Ampel“, „Digitalanzeige“ | Ampel geht, Digitalanzeige nicht | M060 (Stil `Circle`; `TrafficLight`, `FaceSmile` gehen nicht); statt Digitalanzeige große Zahl als Kachel (K020, K030) |

## Kennzahlen und Text

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „die wichtigsten Zahlen oben“ | geht | K020 (Kacheln), K030 (mit Vergleich); `bausteine.kpi` |
| „ein Satz, der sagt, was auffällt“ | geht | K010, K040 |
| „Text mit Fettung und Farbe mitten im Satz“ | geht | X020 (`TextRun`, HTML, nur Schema 2016) |
| „Haken, Kreuz, Sterne“, „farbige Emoji“ | Symbole mit Kniff, Emoji nicht | X040; Schrift „Segoe UI Symbol“, Symbol und Folgetext in getrennte Textboxen; statt Emoji `●` mit Farbe per Ausdruck (`fallen.md` · Text und Zeichen) |
| „Verlauf, Schatten, abgerundete Ecken am Kasten“ | geht nicht (Ecken: Kniff) | flache Farbflächen; runde Ecken nur als PNG; `grenzen.md` · Flächen und Linien |

## Tabellen

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „gruppiert, mit Zwischensummen“, „Baum, Unterliste in der Zeile“ | geht | T060; `c.tablix` mit `group`; Baum und Tabelle in Tabellenzelle: `grenzen.md` · Tabellen (Hierarchie nur bei kleinem Bestand) |
| „Rangliste mit Balken in der Zelle“ | geht | T020 |
| „Kreuztabelle mit Farbskala“ | geht | T040 |
| „Symbol je Zeile nach Schwelle“ | geht | T030 |
| „Anteil an Gesamt“, „laufende Summe“, „Vorgänger“ | geht | `grenzen.md` · Tabellen; `Previous` nur mit innerer Gruppe |
| „Tabelle darf so lang werden, wie die Daten sind“ | geht mit Kniff | `c.rect` fester Größe, `c.topn` als Deckel, Hinweiszeile „… und n weitere“ (`fallen.md` · Tabellen und Layout) |
| „Spalte oder Summenzeile per Schalter ausblenden“ | geht | `Visibility` am `TablixMember`, Schalter `c.parameter(…, "Boolean", …)`; Elemente rechts rücken nach |
| „aufklappen, nach Spalte sortieren“ | geht (F) | U040; Klick aufs Plus, Pfeil am Spaltenkopf; je Klick 5 bis 15 s Rechenpause |
| „je Raum eine Karte, eine Karte je Seite“ | geht | B090 (Raumkarten), `grenzen.md` · Tabellen (Kartenraster, `PageBreak`); letzte Reihe mit `Hidden =CountRows() = 0` |
| „Excel mit Formatierung und Bildern“ | geht nicht | XLSX ist ein Rohdatenauszug; PDF oder DOCX (`grenzen.md` · Seite und Export) |

## Bilder

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „Bild des Bauteils neben der Zeile“ | geht | B010, B020, B030 (3D-Bild); `bilder.md` |
| „Grundriss des Geschosses, Raumplan“ | geht mit Kniff | B080, B090 im Begleit-Report Grundriss (Planausschnitt, zweiter Report) |
| „3D-Ansicht des ganzen Hauses“ | geht nicht | `grenzen.md` · Bilder aus dem Modell |
| „3D-Bild und Grundriss im selben Report“ | geht nicht | zwei Reports (harte Grenze 2) |
| „Abwicklung der Wände je Raum“ | geht mit Kniff | B100; die Zeichnung muss vorher im Teilbild liegen (SKILL.md, Raum-Abwicklung; `bilder.md`) |
| „Firmenlogo, Muster, Piktogramme“ | geht | B060, B050, B040; nur PNG, JPG, GIF, BMP |
| „Klick aufs Bild oder auf die Zeile springt ins Modell“ | geht nicht gesichert | `bausteine.klick` (U020, U040, B010); im PDF und im Testfenster ohne Wirkung, über Allplans Befehl „Reports“ nicht geprüft: nicht versprechen |
| „Biegeform der Stäbe“ | geht | `bewehrung.md` |
| „Strichcode oder QR-Code je Zeile, Etikett mit QR-Code“ | geht | B110 (Etiketten mit QR-Code), B120 (Strichcode 128, unten auf jedem Etikett); `codes.md` |
| „Etiketten zum Ausschneiden für Bauteile“ | geht | B110; 8 je Seite, Bauteilart und Anzahl sind Stellschrauben (`Etiketten_Art`, `Etiketten_Anzahl`); der QR-Code zeigt beim Scannen Klartext (`codes.md`) |

## Seite und Aufbau

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „Seitenzahl x von y“, „eigener Fuß“, „Kopf erst ab Seite 2“ | geht | `c.report` (Fuß; `header_first=False`, oder `Hidden =Globals!PageNumber > 1`); Seitenzahl nur in Kopf und Fuß |
| „Hochformat und Querformat in einem Report“ | geht nicht | zwei Reports (`grenzen.md` · Seite und Export) |
| „Liste je Objektart, jede Art auf eigener Seite, Zählung neu, Auswahl nach Wahl“ | geht | Report Master Listen (K100, K110, U060 Auswertung nach Wahl, U070 Auswahl aus den Daten, T150 Bauteilliste je Art): fließend, Seitenumbruch und eigene Seitenzählung je Art, Gruppenname im Fuß, Lesezeichen je Gruppe (`grenzen.md` · Seite und Export) |
| „Lesezeichen im PDF“, „Gliederungsleiste im Fenster“ | geht (A, F) | `c.report(labels=…)` je Seite; Ebenen über `DocumentMapLabel` an Gruppen (bis 3 Ebenen); die Leiste erscheint links von selbst |
| „Sprung in einen zweiten Report, mit Zurück“ | geht (F) | `c.drillthrough`; der Zurück-Knopf erscheint erst nach dem Sprung; ohne Parameter zeigt das Ziel den Vorgabetext |
| „Tabellenkopf bleibt beim Scrollen stehen“ | geht mit Kniff (F) | `FixedData`; sichtbar nur, wenn die Seite höher ist als das Fenster (Zoom 200 %) |
| „Link auf eine Webseite“ | geht | `c.hyperlink` mit `https://` oder `mailto:`; `file:///` kommt als Link an; interne Sprungmarke im PDF geht nicht |
| „Unterbericht für jede Gruppe“ | geht | `c.subreport`; bekommt die Zeilen des Hauptreports, keine eigene Abfrage (`grenzen.md` · Tabellen) |

## Parameter (Stellschrauben)

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „Schalter, Zahlenfeld oder Auswahlliste links im Fenster“ | geht (F) | `c.parameter` (Preise U030, Ziele M020, Zeilenzahl `c.topn` mit `Parameters!…`); Haken und Liste wirken sofort, Zahl: Wertfeld anklicken, tippen, Enter; Regeltabelle `grenzen.md` · Parameter |
| „einen Parameter vor dem Leser verstecken“ | geht nicht | `Hidden` wird im Fenster ignoriert: der Parameter steht sichtbar und änderbar da |
| „Vorgabe: heutiges Datum“ | geht mit Kniff | Prompt `@401@` oder `=Today()` im Ausdruck; als Vorgabe geht kein Ausdruck |
| „Auswahlliste aus den Daten (Material, Geschoss)“ | geht | `c.parameter(…, distinct="Feld")`; keine Auswahl = alle |
| „zweite Liste hängt von der ersten ab“ | geht mit Kniff | Kombi-Liste „Art\|Typ“ plus `Split` (`grenzen.md` · Parameter) |
| „Wert beim Export setzen“, „Schalter im PDF“ | geht nicht | harte Grenze 5; es gilt die Vorgabe; ein ungültiger Parameter leert im Fenster den ganzen Report (`grenzen.md` · Bedienung) |

## Daten

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „mehrere Auswertungen in einem Report“ | geht | eine breite Abfrage, Themen per Filter auf `@OBJ@` (`daten.md`) |
| „zwei verschiedene Abfragen in einem Report“ | geht nicht | zwei Reports; auch ein Unterbericht führt keine eigene Abfrage aus (harte Grenze 1) |
| „Projektname, Nummer, Bauherr im Kopf“ | geht | Standardparameter und Spalten der Modellabfrage (`daten.md` · Projekt- und Deckblattdaten) |
| „Planliste, Projektliste, Bauwerksstruktur“ | geht | Planliste: Report Master Planliste (K090, D200, M090, T130, T140); alle: `projektlisten.md`; als PDF oder DOCX, nicht als XLSX |
| „Liste aller Teilbilder des Projekts“ | geht nicht verlässlich | `DOCUMENT` liefert je Abfrage 172, 76 oder 38 Zeilen; Teilbilder je Plan über `LAYOUT` plus `LAYOUT_DRAWINGS` (`projektlisten.md`) |
| „Stab- und Mattenliste, Gewicht je Durchmesser“ | geht mit Kniff | Report Master Bewehrung (K080, U050, D170 bis D190, T090 bis T120); Stab-kg aus Gesamtlänge × kg je m, nie aus dem Feld Gewicht (Allplan fasst Zeilen zusammen); `bewehrung.md` |
| „Preise oder Notizen aus einer Excel-Liste dazu“ | geht mit Kniff | CSV im Code lesen, absoluter Pfad (`codes.md`) |
| „Layer, Stift, U-Wert auswerten“ | geht nicht | harte Grenze 12; Attribut erst am Bauteil setzen |
| „Report über tausende Bauteile mit Bildern“ | geht mit Kniff | Bildspalte weglassen oder Abfrage einschränken (`grenzen.md` · Tempo) |

## Sprache

| Wunsch des Kunden | Urteil | Womit |
|---|---|---|
| „auch auf Englisch“, „Zahlen und Datum in der Sprache des Lesers“ | geht | `python master/sprache.py --en`; englisch rendern und ansehen (`sprache.md`); `<Language>` am Report, nicht am Textfeld |
| „Raumnamen, Materialien übersetzen“ | geht nicht | Daten aus dem Modell bleiben; Materialgruppen werden an Wortstämmen erkannt (`sprache.md`) |
| „sieht im Fenster genauso aus wie im PDF“ | geht, wenn nichts überlappt (F) | mindestens 0,05 cm Abstand zwischen Geschwistern; Hintergrund als Eltern-Rectangle, Strich als Rahmen (`fallen.md` · Text und Zeichen); Warnung W28 „Elemente überlappen sich“ beachten |
