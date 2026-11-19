# Gestaltungsregeln des Master-Reports

Maßstab ist Seite 1 (`seiten/s01_uebersicht.py`, Bild `aus/live/Report_Master_S1.png`).
Jede weitere Seite muss daneben liegen können, ohne dass man einen Stilbruch sieht.

## Blatt und Raster

- A4 hoch, randlos: Blatt 21 × 29,7 cm, Seitenränder 0. Inhalt von `c.INSET` (1,5 cm) bis 19,5 cm,
  also 18 cm breit (`c.CONTENT_W`). Nutzbare Höhe je Seite 28,5 cm; darunter steht der Fuß.
- Eine Seite = ein Blatt. Nach dem Rendern muss `OK Seiten=1` stehen (bei `--nur=N`).
- Kopf der Folgeseiten: `seitenkopf(nr, titel, untertitel)`, 2,5 cm hoch. Inhalt beginnt bei 3,3 cm.
- Abschnitt: `overline(name, top, left, w, etikett, titel)` belegt 1,2 cm; der Inhalt folgt bei `top + 1,45`.
- Zwei Spalten: 8,8 + 0,4 + 8,8 cm. Drei Spalten: 5,73 + 0,4 + 5,73 + 0,4 + 5,74 cm.
- Zwischen zwei Abschnitten untereinander 0,7–0,9 cm Luft. Lieber ein Schaustück weniger als gedrängt.

## Farbe

- Nur die Werte aus `core.py`. Keine neuen Hex-Werte in den Seiten.
- `c.INK` für Überschriften und große Zahlen, `c.TEXT` für Werte, `c.MUTED` für Beschriftungen,
  `c.FAINT` für Einheiten und Fußnoten, `c.HAIR` für Linien, `c.SURFACE` für Flächen.
- Leitfarbe `c.BLUE`. Akzent `c.ORANGE` höchstens einmal je Seite, für das eine, worauf der Blick soll.
- Materialfarben (`c.MATERIAL`, Ausdruck `MAT_FARBE`) nur dort, wo wirklich Material dargestellt ist.
- Geordnete Kategorien bekommen Blaustufen: `=Code.Stufe(<Name>)` (größte = dunkelste, überall dieselbe Farbe).
- `c.GREEN`, `c.AMBER`, `c.RED` nur für Bewertung (gut / Achtung / schlecht), nie als Schmuck.

## Schrift

- Segoe UI. Große Zahlen in `c.F_LIGHT`, Überschriften und Hervorhebungen in `c.F_SEMI`, sonst `c.F`.
- Größen: Seitentitel 19, Abschnittstitel 13, große Zahl 17–30, Tabellenwert 9–9,5, Beschriftung 7–8,5,
  Tabellenkopf 7 in Großbuchstaben, Etikett 6,5.
- Einheiten kleiner und heller als die Zahl (eigener `c.run` in derselben Textbox).

## Diagramme

- Kein Rahmen, kein Hintergrund, kein 3D, keine Schatten, kein Farbverlauf.
- Achslinien aus. Gitter höchstens als helle Linien an der Werteachse (`gridcolor="#EEF2F6"`).
  Wo die Werte direkt am Balken stehen, entfällt die Werteachse ganz (`visible=False`).
- Achsbeschriftung mit fester Schriftgröße: `extra="<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"`.
- Legende nur, wenn Direktbeschriftung nicht geht; dann lieber eine eigene kleine Tabelle wie auf Seite 1.
- Höchstens sechs Farben in einem Diagramm. Sortiert nach Größe, nicht nach Alphabet.
- Jedes Diagramm filtert seine Zeilen selbst: `extra=c.filters(<Bedingung>)`.

## Technik, die das Layout hält

- Eine wachsende Tabelle schiebt alles darunter nach unten und alles rechts davon nach rechts.
  Darum steht jede Tabelle in einem `c.rect(...)` mit reservierter Höhe und Breite (Lage der Tabelle darin 0/0).
- Zahlen in Ausdrücken immer `CDbl(Fields!X.Value)`; Bedingungen über `ist(...)`, `ROHBAU`, `RAUM` …;
  Anteile über `quote(zaehler, nenner)`; Summen über `summe(feld, bedingung)`.
- Elementnamen sind im ganzen Report eindeutig: jede Seite setzt ihr Kürzel davor (`S3_…`).
- Unter jedem Schaustück ein `etikett(...)`: Kennung (z. B. `D050`) und in einem Satz die Technik.

## Prüfen

```
python build_master.py --nur=3 --render        # baut out/_Seite3.rdlc, rendert nach aus/png/_Seite3_S1.png
```

Danach die Datei `../out/_Seite3.rdlc` mit dem Prüfskript des Skills allplan-report (`validate_rdlc.py`) prüfen.
Das Bild ansehen, mit Seite 1 vergleichen, nachbessern. Zum Schluss der Beweis aus Allplan
(als PDF ausgeben und ansehen, `references/pruefstrecke.md`) – kopflos ist nur die Vorschau.

## Lesbarkeit: nichts überlappt, nichts ist zu klein

Abnahmebedingung des Anwenders (2026-11-18, an Torte und Blasendiagramm eines großen Projekts gesehen):
Beschriftungen und Führungslinien lagen übereinander und waren nicht zu lesen.

- Keine Beschriftung überlappt eine andere, eine Führungslinie oder eine Achse – mit keinem der Datensätze (master, master_en, gross).
- Kleinste Schrift 7 pt, in Diagrammen wie in Tabellen. Etiketten 6,5 pt sind die einzige Ausnahme.
- Torte und Ring: höchstens 5–6 Segmente, der Rest als „Übrige“ oder gar nicht. Außenbeschriftung nur, wenn alle
  Texte Platz haben; sonst eine eigene Legenden-Tabelle daneben (Name, Wert, Anteil).
- Punkt- und Blasendiagramme: Punkte dürfen sich überdecken, Texte nicht. Höchstens die fünf wichtigsten beschriften
  oder ganz ohne Beschriftung arbeiten.
- Flächenkacheln (TreeMap): Text nur in Feldern, in die er ganz passt; Schriftfarbe mit Kontrast zum Feld.
- Achsbeschriftung nie gestapelt, gedreht oder buchstabenweise umbrochen: Kategorien deckeln und Namen kürzen.
- Geprüft wird am vergrößerten Einzeldiagramm, nicht an der verkleinerten Seite.

## Datenfest: die Seite muss mit jedem Projekt halten

Gemessen am 2026-11-18: Der Report sah auf dem Master-Teilbild (51 Zeilen) perfekt aus und zerfiel auf
echten Projekten – 13 statt 7 Seiten beim Wohnhaus (101 Zeilen, 13 Raumnutzungen, 6 Materialien),
20 Seiten bei einem großen Projekt (3.545 Zeilen, 36 Raumnutzungen, Materialnamen als Kürzel). Seitdem gilt:

**Prüfpflicht.** Jede Seite ergibt mit allen Datensätzen genau ein Blatt und sieht gut aus. Ausgeliefert werden
`master` (Master-Teilbild), `master_en` (dasselbe auf Englisch) und `gross` (künstlicher Prüfdatensatz mit 3.000 Zeilen:
40 Raumnutzungen mit langen Namen, viele Materialschreibweisen, je 15 Tür- und 20 Fenstertypen):

```
python build_master.py --nur=3 --render                    # Master-Teilbild      -> aus/png/_Seite3_S1.png
python build_master.py --nur=3 --render --daten=master_en  # englische Daten      -> aus/png_master_en/_Seite3_S1.png
python build_master.py --nur=3 --render --daten=gross      # Prüfdatensatz        -> aus/png_gross/_Seite3_S1.png
```

Eigene Datensätze aus echten Projekten legst du als `daten/<name>.json` dazu und prüfst mit `--daten=<name>`.

**Regeln.**

- **Jede Liste hat einen Deckel.** Feste Höchstzahl an Zeilen (`c.topn(ausdruck, n)` an Tabelle oder Gruppe),
  passend zur reservierten Höhe. Wird gekürzt, sagt eine Zeile, wie viel fehlt („… und 303 weitere“) oder
  die Überschrift nennt es („Die 8 größten“). Nie eine Einzelliste aller Bauteile ohne Deckel.
- **Jedes Diagramm hat einen Deckel.** Höchstens 6–8 Kategorien (TopN an der Kategoriegruppe). Punktwolken
  vertragen viele Punkte, Balken und Torten nicht.
- **Karten nebeneinander** (Spaltengruppe) höchstens so viele, wie in die Breite passen (TopN).
- **Keine Projektnamen im Ausdruck.** Nie `Fields!Material.Value="Beton bewehrt"` oder
  `Fields!Funktion.Value="Verkehrsfläche"`. Stattdessen:
  - Materialgruppe `b.MATGRUPPE` (Beton, Mauerwerk, Dämmung, Gipskarton, Holz, Stahl, Glas, Naturstein,
    Sonstiges, ohne Angabe) – erkennt „StB C45“, „MW“, „Gipskarton + Dämmung“ am Wortstamm; `b.IST_BETON`.
  - Farbe `b.MAT_FARBE` (Farbe der Materialgruppe aus `c.MATERIALGRUPPE`).
  - Bauteilart `b.ART` aus der Objektnummer (Wand, Stütze, Decke, Unterzug, Bodenplatte, Raum, Fenster, Tür) –
    Projekte nennen ihre Objekte „Wand_Fass“, „Stuetze“, „Traeger“.
  - Verkehrsfläche `b.IST_VERKEHR` (Flur, Diele, Treppe, Gang, Foyer …).
  - Diagramme und Legenden über Material gruppieren nach `b.MATGRUPPE`, nicht nach dem rohen Namen;
    feste Legenden aus `c.MATERIALGRUPPE` nur für Gruppen zeigen, die vorkommen, oder die Legende weglassen
    und direkt beschriften.
- **Lange Namen** („Wärme- und Kältedämmarbeiten“, „Innentür_2flg_klein“): Zellen wachsen nicht
  (`grow=False` ist Vorgabe), Text wird abgeschnitten; Spalten breit genug für 25 Zeichen, sonst kleinere Schrift.
- **Große Zahlen**: 31.540 m² statt 513 m² – Platz für sieben Ziffern, Format `#,##0`, Nachkommastellen nur unter 100.
- **Leere und Null**: Division über `b.quote()`; fehlt eine Art ganz (keine Fenster), zeigt der Baustein
  „–“ oder einen ruhigen Leertext, nie `#Error`, `NaN` oder ein leeres Diagramm mit Achsen.
- **Kernaussagen** dürfen nichts behaupten, was die Erkennung nicht trägt: lieber „Beton (StB C45, StB C30 …)“
  über die Materialgruppe als ein genauer Name.

## Keine Überlappung: auch nicht um 0,02 cm

Gemessen im echten Allplan-Report-Fenster (2026-11-19): Überlappen sich zwei Elemente im selben
Container auch nur um 0,02 cm – auch ein leeres Feld –, schiebt das Fenster eines davon weg (abgeschnittener Text, verrutschte
Blöcke, längere Seiten). PDF und kopflose Vorschau lassen beide an ihrem Platz und verraten es nicht.

- Zwischen Geschwistern (Body, Rectangle, Zellen-Rectangle, Kopf, Fuß) mindestens 0,05 cm Luft; Berührung (0 cm) ist erlaubt.
- Titel und rechtsbündiger Untertitel stehen nebeneinander mit getrennten Breiten (`b.folgekopf`, `overline(..., titel_w=)`), nie beide über die volle Breite.
- Hintergrundflächen und Rahmen mit Inhalt sind das ELTERN-Rectangle (Kinder im Rectangle sind richtig), nicht ein leeres Geschwister darunter.
- Leertexte sind `NoRowsMessage` der Tabelle, kein zweites Feld über dem Bild; Strich bei fehlendem Wert ist ein zweiter Textlauf im selben Feld.
- Zwei Etiketten untereinander: `etikett(..., h=0.3)` und 0,35 cm Abstand.
- Zwei Felder auf derselben Stelle sind nur dann erlaubt, wenn sie sich GEGENSEITIG ausschalten: JEDES trägt einen eigenen
  Sichtbarkeits-Ausdruck (`<Hidden>`), und die Ausdrücke schließen einander aus (nie beide sichtbar, nie beide weg). Beispiele:
  Foto `=OHNE_BILD` gegen Ersatzbild `=Not OHNE_BILD`; Hinweisliste `=KEINE` gegen Haken `=Not KEINE`; vier Säulenvarianten mit
  Monatsbereichen 0–1, 2–3, 4–6, 7 und mehr. Trägt nur eines einen Ausdruck, ist das ein Fund.
  Das Prüfskript führt solche Paare einzeln als `[Alternative]` auf und zählt sie getrennt; ob sich die Ausdrücke ausschließen,
  prüft man von Hand und rendert beide Zustände.
- Ein Feld mit Sichtbarkeits-Ausdruck liegt nie lose neben fremden Bausteinen: es kommt in EIN Rectangle über die volle Breite, das
  den Ausdruck trägt (`S7_B01_haken`, `PL_D200_n_Feld`). Gemessen im Report-Fenster: lose ausgeblendete
  Felder mit eigenen Kanten schoben im Fenster die Kacheln von U010 bis 2,4 cm nach links, obwohl nichts überlappte.
- Reihen aus mehreren Kacheln liegen in einem eigenen Rectangle (`S7_B05r`).
- Text bis 8,5 pt bekommt 10 % Breitenreserve: das Fenster setzt ihn 3 bis 8 % breiter als das PDF (ab 9 pt 0,5 bis 3 % schmaler).

Prüfen: das Prüfskript `validate_rdlc.py` meldet jede Überlappung als Warnung W28 mit Container und beiden Elementnamen
(Aufruf in `references/pruefstrecke.md`, Abschnitt R1); Entweder-oder-Paare nennt es als Hinweis.
