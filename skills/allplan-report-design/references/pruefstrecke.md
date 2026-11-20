# Prüfen: kopflos und im echten Allplan

Kopflos ist nur die Vorschau (Layout, Diagramme; Allplans Abfrage läuft nicht mit). **Beweis ist Allplan.**
`<REPORT>` = die Werkstatt (angelegt mit `werkstatt_anlegen.py`), Werkzeuge in `<REPORT>/werkzeug/`.
Befehle laufen in `<REPORT>`.

## Der Prüfweg

Es gibt genau einen Prüfweg: (a) Renderer bauen, (c) kopflos rendern und ansehen, (d) Datenfest-Lauf, (e) statische Prüfung R1, dann (f) der Anwender
öffnet den Report in Allplan und meldet zurück (R2). Bis zu dieser Rückmeldung ist R2 „nicht geprüft“.

## (a) Renderer bauen (einmalig)

```
powershell -ExecutionPolicy Bypass -File werkzeug\render\build.ps1
```
Kopiert die ReportViewer-DLLs aus `C:\Program Files\Allplan\Allplan 2027\Prg` und baut `werkzeug\render\bin\RenderRdlc.exe`
(Parameter `-Prg` für einen anderen Ordner). In der angelegten Werkstatt durchgespielt: danach liegt die EXE samt DLLs in `bin\`.

## (b) Datenprobe: was liefert Allplan wirklich?

```
python werkzeug\datenprobe.py <ziel.rdlc> --from "[MODEL_DATA]" "@498@:Objekt" "@508@:Material" "@223@:Volumen:Double"
```
Spalte = `<Attribut mit Optionen>:<Feldname>[:<Typ>]`, Typ `String|Double|Int32|Bild` (Vorgabe String), Optionen mit `|` (`"@221@|Dim=1:Dicke:Double"`).
Zahlen als **String** typen, dann kommen sie im XLSX ungerundet (Double: 3 Stellen). Den Probe-Report gibt der Anwender in Allplan als `.xlsx` aus
(Ausgabe als Excel). Danach:
```
python werkzeug\xlsx_lesen.py <datei.xlsx> [--zeilen=15] [--gruppe=Spaltenname ...]
python werkzeug\xlsx_zu_json.py <probe.rdlc> <probe.xlsx> <ziel.json>
```
`xlsx_zu_json` nimmt Feldnamen/Typen aus der `.rdlc` (Spaltenzahl muss passen); Ergebnis `{"types": {Feld: "String|Double|Int|Bool|Bytes"}, "rows": […]}`.
XLSX hat keine Bilder: `Bild`-Felder als `Bytes` mit `"file:bilder/x.png"` oder Base64 ergänzen.

## (c) Kopflos rendern und ansehen

```
werkzeug\render\bin\RenderRdlc.exe <rdlc> <daten.json> <ausgabeordner> [Schalter] [Name=Wert ...]
```
Schalter: `--pdf` zusätzlich PDF; `--format=xlsx` oder `--format=docx` zusätzlich Excel bzw. Word; `--dpi=120`; `--prg=<Allplan\Prg>` anderer Programmordner; `--info` listet die Parameter des Reports.
`--vollzugriff` (auch `--fulltrust`): der Code des Reports läuft mit vollen Rechten und darf Dateien lesen und schreiben, wie in Allplan; nur setzen, wenn der Report das braucht (CSV, Ordner lesen), sonst bleibt der Dateizugriff gesperrt.
Mehrere Werte bei Mehrfachauswahl: `Name=a|b`; `Name=~null` setzt „Nothing“. Ein Name, den der Report nicht kennt, wird gemeldet. Unterberichte bedient das Programm wie Allplan: das Ziel (`<ReportName>.rdlc` im Ordner des aufrufenden Reports, auch verschachtelt) bekommt die Daten des Hauptreports.
Ausgabe `<ausgabeordner>\<Name>_S<n>.png` (höchstens 60 Seiten). **Das PNG ansehen.**
- Meldet: `Seite n: …`, `WARNUNG: …` (nur Seite 1), `FEHLER: <Typ>: <Text>` (Exit 2), zum Schluss `OK Seiten=n`. Seitenzahl prüfen.
- Meldet **nicht**: Fehler im Diagramm (stehen nur als Text im Bild), Ausdrucksfehler (`#Error` in Zellen, darf nie vorkommen).
- Dezimalzahlen mit **Punkt oder Komma** übergeben (`Tuer_Mindestbreite=0.8` und `=0,8` gehen beide; bei Zahl-Parametern wandelt der Renderer das Zeichen um). Standardparameter sind vorbelegt.
- Zahl als Text in Achsen-`Minimum`/`Maximum` liest die deutsche Kultur falsch: als Ausdruck `"=1.14"` schreiben.
- `build_master.py --render` und `build_auswahl.py --render` übergeben `Project_Name=Musterprojekt`: dieser Name steht dann in Titel
  und Fuß der gerenderten Bilder (nicht im Report selbst; in Allplan kommt der echte Projektname).

## (d) Datenfest-Lauf mit drei Datensätzen

```
python master\build_master.py --nur=3 --render                    (master, 51 Zeilen  -> master\aus\png\_Seite3_S1.png)
python master\build_master.py --nur=3 --render --daten=master_en  (englische Materialnamen -> aus\png_master_en\)
python master\build_master.py --nur=3 --render --daten=gross      (3.000 Zeilen -> aus\png_gross\)
```
Jede Seite muss mit allen drei genau `OK Seiten=1` ergeben und gut aussehen. Ohne `--nur` entsteht `out\Report_Master.rdlc` (10 Seiten).
Regel: `--daten=gross` ohne `--nur` ergibt wie `master` 10 Seiten.
Zweite Bildart: `python master\grundriss\build_grundriss.py [--render]` (Standarddatensatz `grundriss`).
Großen Prüfdatensatz neu: `python master\daten\make_gross.py` (aus `master.json`).

## (e) R1: statische Prüfung

```
python werkzeug\pruefen\validate_rdlc.py out\Report_Master.rdlc
```
Auch ein ganzer Ordner geht. Fehler E01–E16 scheitern sicher; Warnungen W01–W28 sind Hinweise (die Kennungen stehen im Kopf des Skripts).
Die letzte Zeile ist die Ampel `AMPEL: <FARBE> | …` und geht wörtlich an den Anwender; Exit-Code 0 heißt „kein Fehler“.

Zwei mitgelieferte Reports melden je einen Hinweis (ORANGE), beide mit Absicht – dem Anwender so erklären, nicht „beheben“:

| Report | Hinweis | Warum er bleibt |
|---|---|---|
| Wandbeläge | W08 „Tabelle breiter als Body“ | Die Balkenspalte gibt es in drei Breiten (für 1, 2, 3 Belag-Spalten); sichtbar ist immer genau eine. Das Prüfskript zählt alle drei mit. |
| Raum-Abwicklung | W09 „RepeatOnNewPage fehlt“ | Die erste Zeile ist die Überschrift des Blocks, kein Spaltenkopf; sie soll nur auf Blatt 1 stehen. |


## (f) Der Prüfweg: R2 in Allplan

1. **Renderer einmal bauen** (a). Kante: `werkzeug\render\bin\RenderRdlc.exe` vorhanden.
2. **Kopflos rendern und ansehen** (c), Datenfest-Lauf (d). Kante: `OK Seiten=n` mit der geplanten Zahl, jedes PNG angesehen.
3. **R1** (e). Kante: `AMPEL: GRUEN`.
4. **R2: der Anwender öffnet den Report in Allplan.** Die `.rdlc` aus `out\` in den Büro-Reports-Ordner kopieren lassen
   (`vorlagen\LIESMICH.md`, Abschnitt Einrichten), Report-Dialog öffnen, Teilbild mit dem Modell wählen, PDF oder Fenster ansehen und
   zurückmelden: Bild oder Fehlermeldung. **Bis zu dieser Rückmeldung ist R2 GRAU („nicht geprüft“) und wird nie als bestanden gemeldet.**
   Kante: Rückmeldung des Anwenders liegt vor und ist benannt.

Beispieldaten: Der Anwender gibt den Probe-Report aus `datenprobe.py` in Allplan als Excel aus; daraus macht `xlsx_zu_json.py` die JSON-Datei (b).
Bis dahin wird mit `master.json` und `gross.json` gebaut.

Meldet der Anwender ein Fenster, erklärt die Tabelle bei (g), was es bedeutet.


## (g) Meldungsfenster

Fenster, die das Öffnen oder die Ausgabe eines Reports blockieren – die Tabelle hilft beim Lesen der Rückmeldung des Anwenders:

| Fenster | Auslöser |
|---|---|
| „Allplan“ – „Es wurden keine Bauteile gefunden …“ | Abfrage ohne Treffer: Filter prüfen |
| „Einstellungen für Ausgabedatei“ – „Zugriff auf diesen Pfad nicht möglich“ (`#32770`) | Pfad mit Schrägstrichen oder Ordner nicht beschreibbar |
| Titel `Microsoft.ReportViewer…DefinitionInvalidException` | Report-Definition ungültig; Titel nennt Element und Fehler (Dialog „Fehler bei der lokalen Berichtsverarbeitung“) |
| „Report“ (Allplan-Betrachter) | Projekttabelle (`CURRENT_PROJECT` …) als XLSX ausgegeben; blockiert bis zum Schließen |


## (h) PDF als Bild ansehen

```
python werkzeug\pdf_zu_png.py <datei.pdf> [<ausgabeordner>] [--dpi=110] [--seiten=1-3]
python werkzeug\kontaktbogen.py <ziel.png> <pdf1> <pdf2> ... [--spalten=4] [--dpi=45] [--ausschnitt=l,o,r,u]
```
`pdf_zu_png` schreibt `<name>_S<n>.png` und `Seiten gesamt: n`; `kontaktbogen` setzt je PDF die erste Seite in ein Raster (Ausschnitt als Seitenanteile 0..1).
Beide brauchen PyMuPDF (`pymupdf`) und Pillow; PyMuPDF fehlt im Python von Allplan, dafür ein eigenes Python nehmen. Jedes Bild ansehen, auch Diagramme: Fehler stehen nur dort.
Das PDF liefert der Anwender aus Allplan.


## (i) Nicht selbst prüfbar

Der Anwender prüft die Bedienung im Report-Fenster: Report in Allplan öffnen, bedienen, zurückmelden. Erfahrungsgemäß geht im Fenster:
- Aufklappen (Klick aufs Plus), Sortieren (Pfeil am Spaltenkopf), Haken umschalten, Zahl eingeben (erst das Wertfeld anklicken, dann tippen, Enter), Liste wählen (Knopf rechts im Wertfeld).
- Sprung in einen zweiten Report; der Zurück-Knopf erscheint erst nach dem Sprung.
- Dokumentstruktur-Leiste links, Unterbericht, fixierter Tabellenkopf (sichtbar, wenn die Seite höher ist als das Fenster).
- Nach jedem Klick, der neu rechnet, 5 bis 15 s Pause; der Master braucht bis zur ersten Seite rund 25 s, jede weitere Seite beim ersten Aufruf 5 bis 15 s.

Worauf er achten soll:
- Text rutscht unter einen Nachbarn, bricht anders um oder wird abgeschnitten, Blöcke rücken nach unten: zwei Elemente überlappen sich (das PDF zeigt das nicht).
- Elemente einer Reihe rücken zusammen oder nach links, ohne dass etwas überlappt: weiter unten im selben Behälter liegt ein ausgeblendetes Feld mit anderen Kanten – es in einen eigenen Behälter über die volle Breite legen (Sichtbarkeit am Behälter).
- Kleiner Text (bis 8,5 pt) bricht im Fenster um, im PDF nicht: er ist dort 3 bis 8 % breiter; 10 % Breitenreserve geben. Text ab 9 pt ist im Fenster 0,5 bis 3 % schmaler. Gemessen mit Segoe UI; die Passkontrolle der Seiten rechnet mit den Breiten von Roboto.
- Parameterleiste leer und auf der Fläche „Im Project_Name-Parameter fehlt ein Wert.“: ein Parameter ist ungültig (Ausdruck als Vorgabe, abhängige Liste); die Meldung nennt den falschen Parameter.
- Ein `Hidden`-Parameter steht sichtbar da; ein interner Sprung zeigt vorher ein Meldungsfenster.
- Klick ins Modell (`Zoom:`) wirkte im Testfenster nicht: ausprobieren, nicht versprechen. Hyperlinks, Tooltips und Export aus dem Fenster sind nicht geprüft.

Ehrlich melden:
„Kopflos gerendert; Klick/Aufklappen/Sortieren im Report-Fenster vom Anwender zu prüfen“ – nie als bestanden ausgeben.
Das ist der Normalfall: R2 bleibt GRAU, bis der Anwender zurückmeldet.


