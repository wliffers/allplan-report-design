# Design: Farben und Schrift

Auslöser: der Anwender nennt Hausfarben, Hausschrift, ein Logo, ein CI-Handbuch oder „soll aussehen wie …“; oder ein Bauskript hält mit Code 3 an („DESIGN: OFFEN“).
Farben und Schrift liegen an einer Stelle: `master/design.py`. `master/core.py` legt daraus seine Namen an; Seiten benutzen nur diese Namen (SKILL.md, Regel 15).

## Befehle (in `<REPORT>`)

| Befehl | Wirkung |
|---|---|
| `python master/design.py` | Stand in einer Zeile: `DESIGN: OFFEN`, `HAUS` oder `KUNDE` (Rückgabewert 3 bei OFFEN) |
| `--fragen` | die drei Fragen an den Anwender (Stil, Farben, Schrift) |
| `--haus --antwort "<Wortlaut>"` | Hausdesign festlegen, erst nach der Antwort des Anwenders; ohne `--antwort` lehnt der Befehl ab (Rückgabewert 2); die Antwort steht in `design.json` |
| `--vorlage [datei]` | Formular `design_kunde.json` schreiben (überschreibt nichts) |
| `--kunde <datei> [--antwort "<Wortlaut>"]` | prüfen und festlegen; bei einem Fehler wird nichts festgelegt; die Antwort ist hier wahlfrei |
| `--pruefen [datei]` | nur prüfen (Kontraste, Schrift); ohne Datei das geltende Design |
| `--tabelle` | alle Farben und Schriften des geltenden Designs |

Das festgelegte Design steht in `design.json` der Werkstatt, das Formular in `design_kunde.json`; beide gehören dem Anwender und gehen nie ins Paket.
Ist `design.json` unlesbar, kein Objekt, nennt sie weder `haus` noch `kunde` oder enthält sie ein fehlerhaftes Kundendesign, gilt der Stand OFFEN mit dem Grund in der `DESIGN`-Zeile; nie still das Hausdesign.
Nur Tests und der Sammelbau der ausgelieferten Vorlagen setzen `REPORT_DESIGN=haus` oder `=<datei>`; die Variable geht `design.json` vor und lässt nichts anhalten. Eine Datei wird geprüft, bei Fehlern bricht der Lauf ab. Für den Report eines Anwenders ist sie kein Weg an der Frage vorbei.

## Rollen: Formular → Name in `core.py` → wofür

| `design_kunde.json` | `core.py` | Wofür |
|---|---|---|
| `tinte` (Pflicht) | `INK` | Überschriften, große Zahlen; nie reines Schwarz |
| `text` | `TEXT` | Fließtext, Tabellenwerte (Vorgabe: `tinte`) |
| `leise`, `fussnote` | `MUTED`, `FAINT` | Beschriftungen, Achsen; Einheiten, Fußnoten |
| `linie`, `linie_stark` | `HAIR`, `HAIR_STARK` | Haarlinien und Rahmen; starke Trenner |
| `flaeche`, `flaeche_blau`, `flaeche_tint` | `SURFACE`, `MIST`, `TINT` | gedämpfte Kachel; Hinweis- und Bandfläche; Hervorhebung in Listen |
| `dunkel` (Pflicht) | `NAVY` | Titelband, dunkle Flächen; trägt weiße Schrift |
| `leit` (Pflicht) | `BLUE` | Balken, Links, hervorgehobene Zahl auf Weiß |
| `akzent` (Pflicht) | `AKZENT` | eine Markierung je Seite; auf Weiß nur als Fläche oder Linie |
| `gut`, `achtung`, `schlecht` | `GREEN`, `AMBER`, `RED` | Bewertung als Fläche, Punkt, Balken |
| `stufen`, `serie` (je 8) | `RAMP`, `SERIE` | geordnete Kategorien; Reihenfolge der Diagrammfarben |
| `schrift`: `normal`, `leicht`, `halbfett`, `zahl` | `F`, `F_LIGHT`, `F_SEMI`, `F_ZAHL` | Text; dünne Schrift; Kopfzeilen und Betonung; große Kennzahlen |

Die Schriftrolle `normal` ist Pflicht, sobald `schrift` Angaben enthält; fehlen `halbfett` und `zahl`, nehmen sie die Normalschrift (dann fehlt das Gewicht; fette Schnitte sind eigene Familien).
Abgeleitet, nicht im Formular: `AKZENT_TEXT` (Akzent als Schrift auf Weiß, sonst die Leitfarbe), `AUF_AKZENT`, `AKZENT_DUNKEL`, `AUF_NAVY`, `AUF_NAVY_LEISE`, `NAVY_LINIE`, `NAVY_FLAECHE`,
`GREEN_TEXT`, `AMBER_TEXT`, `RED_TEXT`. Materialfarben (`MATERIALGRUPPE`: Beton grau, Mauerwerk ziegelrot) gelten in jedem Design.

## Aus Kundenangaben die vier Pflichtfarben gewinnen

1. **Dunkle Fläche** (`dunkel`): die dunkelste Hausfarbe, die weiße Schrift trägt (Kontrast mindestens 4,5).
2. **Leitfarbe** (`leit`): die kräftige Hausfarbe, die auf Weiß als Schrift lesbar ist (mindestens 4,5).
3. **Akzent** (`akzent`): die auffälligste Farbe; ist sie auf Weiß zu hell, ist das erlaubt.
4. **Tinte** (`tinte`): die Textfarbe; fehlt sie, die dunkle Fläche. Kein reines Schwarz im Hausdesign.

Quelle der Werte: Farbwerte des Kunden, sonst CI-Handbuch, Website, Logo oder Beispiel-PDF. Nur `#RRGGBB`. Ein Wert, der geraten ist, wird dem Anwender als geraten genannt.
Daraus rechnet der Bausatz alles andere: Linien und Flächen als Mischung von Tinte und Leitfarbe mit Weiß, 8 Stufen und 8 Serienfarben aus der Leitfarbe, `leise` und `fussnote` abgedunkelt bis Kontrast 4,5, Schrift auf Dunkel als Weiß mit 70 und 60 %.
Bewertungsfarben nimmt der Bausatz aus dem Hausdesign, wenn das Formular sie nicht nennt.

## Regeln

- Der Akzent steht auf Weiß nur als Fläche oder Linie, wenn er zu hell ist (Türkis des Hausdesigns: Kontrast 1,3); hervorgehobene Schrift nimmt die Leitfarbe (`AKZENT_TEXT`).
- Bewertungsfarben als Schrift stehen abgedunkelt (`GREEN_TEXT` …); die reine Farbe bleibt für Flächen und Punkte.
- Höchstens drei Schriftgewichte je Seite; `zahl` nur für große Kennzahlen.
- Kleine Schrift braucht Kontrast mindestens 4,5, große Schrift und Linien 3.
- `--kunde` und `--pruefen` melden FEHLER bei:
  - fehlender Pflichtfarbe, unbekanntem Namen, Wert mit Durchsicht (`#RRGGBBAA`, `rgba(…)`);
  - zu schwacher Schrift und zu heller dunkler Fläche;
  - Bewertungsfarbe mit Kontrast unter 1,5 auf Weiß;
  - `stufen` oder `serie` mit weniger als 6 verschiedenen Farben, einer der ersten fünf mit Kontrast unter 1,3 auf Weiß, oder einer ersten Stufe mit Kontrast unter 3;
  - Schrift, die kein nicht-leerer Text ist oder `< > & "` enthält, und fehlender Rolle `normal`.
- HINWEIS bei zu hellem Akzent, bei `leit` oder `akzent` nahe einer Bewertungsfarbe (Verwechslungsgefahr), bei fehlenden Rollen `halbfett` oder `zahl` und bei Schrift, die auf diesem Rechner fehlt.
- Eine Farbe steht höchstens einmal in `serie`: ein Duplikat (z. B. Akzent gleich Leitfarbe) rechnet der Bausatz auf eine Mischung aus Tinte und Weiß um.

## Schrift

Ein Report bettet keine Schrift ein. Der Report wählt sie beim Öffnen selbst: sind alle Familien des Designs auf dem öffnenden Rechner installiert, gelten sie, sonst Segoe UI, Segoe UI Light, Segoe UI Semibold.
Roboto muss also nicht installiert sein; ohne sie zeigt derselbe Report Segoe UI, mit ihr ist er schöner. Gemessen am 2026-11-20 in Allplan 2027 (PDF und Report-Fenster): mit Roboto steht Roboto im PDF, mit einer nicht installierten Familie stehen Segoe UI, Light und Semibold.
Ohne diesen Ersatz setzt Windows alles in „Microsoft Sans Serif“, Gewichte fehlen und einzelne Zeichen erscheinen als leere Kästchen.
Fette Schnitte sind eigene Familien (`Arial Black`). Fehlt die Schrift auf dem Rechner, der baut, steht das in der `DESIGN`-Zeile („Reports zeigen hier Segoe UI“); gebaut wird trotzdem mit der Soll-Schrift.
Symbolschriften (Segoe UI Symbol, Consolas) bleiben fest (`fallen.md` · Text und Zeichen). Die Fenster-Messungen in diesen Referenzen (das Report-Fenster setzt kleine Schrift breiter) stammen von Segoe UI; die Passkontrolle der Seiten rechnet mit den Breiten von Roboto.
Gemessen in Allplan (2026-11-20, PDF): ein Satz in 14 pt Roboto brach in vier statt in drei Zeilen wie in der kopflosen Vorschau um. Hinweisbänder brauchen eine ganze Zeile Luft.

## Was eine RDLC vom Design nicht kann

| Wunsch | Geht nicht, weil | Stattdessen |
|---|---|---|
| runde Ecken | Textbox und Rechteck kennen keinen Radius | flache Fläche; runde Ecken nur als PNG (`grenzen.md` · Flächen und Linien) |
| Schatten | kein Schattenattribut | Haarlinie (`HAIR`) und Fläche (`SURFACE`) |
| Durchsicht („Weiß 10 %“) | harter Fehler bei `#AARRGGBB`, `rgba()`, `Transparent` | vorab auf den Grund mischen (`design.mischen`); der Bausatz tut das für dunkle Flächen |
| Farbverlauf | flach in der Startfarbe | Stufen aus `RAMP` |
| Laufweite der Schrift | kein Attribut | schmale Leerzeichen U+2009 oder U+200A (`grenzen.md` · Text und Schrift) |
| Webschrift, Schrift einbetten | der Report bettet nichts ein | installierte Schrift; sonst greift der Ersatz |
| Hover, Mausreaktion | keine Zustände in einer RDLC | Wert am Balken beschriften, Farbe immer sichtbar |
| Hintergrundfarbe der Seite | Rand bleibt weiß | Farbband als Rechteck in Seitenbreite |

## Stil-Wunsch

Wünsche zum Stil (dunkles Titelband oder heller Kopf, Logo im Kopf, kräftig oder ruhig) trägt `stil` in `design_kunde.json` und die Antwort an den Anwender. Dafür gibt es keinen Schalter:
die Seiten in `master/seiten/` werden von Hand angepasst (Titelband = `NAVY`-Fläche, heller Kopf = `MIST` oder Weiß mit `HAIR`-Linie), danach den Master rendern und ansehen.

## Hausdesign (Werte aus `python master/design.py --tabelle`)

| Rolle | Wert | Rolle | Wert |
|---|---|---|---|
| `tinte`, `text`, `dunkel` | `#062246` | `flaeche` | `#F6F6F6` |
| `leit` | `#0F54AC` | `flaeche_blau` | `#E9F1FB` |
| `akzent` (Türkis) | `#00FBC8` | `flaeche_tint` | `#D3E4F6` |
| `leise`, `fussnote` | `#575757` | `gut`, `achtung`, `schlecht` | `#10B981`, `#F59E0B`, `#EF4444` |
| `linie`, `linie_stark` | `#E7E7E7`, `#D3D3D3` | Schrift | Roboto, Light, Medium, Black |

Stil: dunkles Titelband, heller Inhalt, ruhige Typografie, Akzent nur als Markierung. Ersatzschrift: Segoe UI, Segoe UI Light, Segoe UI Semibold.
