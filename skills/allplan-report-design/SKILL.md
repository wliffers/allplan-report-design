---
name: allplan-report-design
description: 'Auslöser: "Report gestalten", "Report schoener", "Dashboard", "Diagramm im Report", "Bild im Report", "Kennzahlen-Report", "Report-Design", "Report UX", "Master-Report", "Raum-Abwicklung", "englischer Report", "Report uebersetzen" oder eine Baustein-Kennung wie "D040", "T020", "K010". Gestaltet Allplan-2027-Reports (.rdlc) als Auswertung zum Hinsehen und Bedienen - Diagramme, Messanzeigen, Kennzahl-Kacheln, Tabellen mit Grafik, Bauteilbilder und Grundrisse aus dem Modell, Klick ins Modell, Stellschrauben - deutsch und englisch, und führt zum Beweis in Allplan. Reine Listen ohne Gestaltung: Skill allplan-report, falls installiert.'
---

# Allplan-Reports gestalten

Allplan zeigt Reports mit dem Microsoft ReportViewer 15. Der kann weit mehr, als Allplans 551 Vorlagen nutzen:
dort gibt es kein einziges Diagramm. Was davon in Allplan wirklich läuft, wurde gemessen und steckt als Bausatz
und als Master-Report in der Werkstatt.

`<SKILL>` = Ordner dieser Datei. `<REPORT>` = die Werkstatt: der Ordner mit `master/` (Bausatz), `werkzeug/`, `vorlagen/`, `out/`.

**Werkstatt anlegen (beim Kunden, einmal):** `python <SKILL>/werkstatt_anlegen.py <ziel>` kopiert `<SKILL>/werkstatt/` nach `<ziel>`
und bricht ab, wenn `<ziel>` nicht leer ist. Gearbeitet wird nur in der Kopie. Kante: `<REPORT>/master/build_master.py` und `<REPORT>/out/` sind da.
`--aktualisieren` bringt eine vorhandene Werkstatt auf den Stand des Pakets: ersetzt nur Dateien in `master/` und `werkzeug/`, die der Anwender nicht
verändert hat (neue Paketdateien kommen dazu); veränderte bleiben, die neue Fassung liegt daneben als `.neu`. `out/`, `aus/`, eigene Daten, eigene
Seiten und `vorlagen/` bleiben unberührt.
Voraussetzungen: Python 3.10 oder neuer; für den Renderer Allplan 2027 (DLLs aus `Allplan 2027\Prg`). Ist `python` nicht im Suchpfad, das Python von
Allplan nehmen: `"C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe"` (Pillow ist dort enthalten). Damit laufen Bauen, Rendern, Sprache, Prüfen und
die Abwicklungs-Vorschau. Nur `pdf_zu_png.py` und `kontaktbogen.py` (PyMuPDF) und die Tests (pytest) brauchen ein eigenes Python mit diesen Paketen.
Der Renderer wird einmal je Werkstatt gebaut: `powershell -ExecutionPolicy Bypass -File werkzeug/render/build.ps1` (vorher den Nutzer fragen);
liegt Allplan nicht unter `C:\Program Files\Allplan\Allplan 2027\Prg`, den Ordner mit `-Prg "<Pfad>"` angeben.

**Vor dem ersten eigenen Report:** `VERFASSER` in `<REPORT>/master/core.py` auf den eigenen Namen setzen; er steht als `<Author>` in jeder erzeugten Datei.

Die statische Prüfung R1 macht das mitgelieferte Skript `<REPORT>/werkzeug/pruefen/validate_rdlc.py`; Attribut-Nummern schlägt
`<REPORT>/werkzeug/pruefen/lookup_attribute.py` nach (`references/daten.md`). Jede Attribut-Nummer und jedes Konstrukt braucht ein Vorbild:
einen Baustein des Master-Reports, der in `references/grenzen.md` die Belegstufe A trägt, oder eine Vorlage aus Allplans Bibliothek
(`Etc\Reports` der Installation). Das Fachwissen zur Abfragesprache und zu Attributen trägt der Grundskill `allplan-report` (im selben Repo,
Ordner `skills/allplan-report`), falls er installiert ist.

## Bestellen per Kennung

Jeder Baustein hat eine feste Kennung: ein Buchstabe für die Art, drei Ziffern.
K Kennzahl/Kernaussage · D Diagramm · M Messanzeige · T Tabelle · B Bild · U Bedienung · X Text/Symbol/Fläche.
Sie steht im Report klein unter dem Schaustück, gesammelt auf Seite 10 des Masters und mit Bauplan in `references/bausteine.md`
(Kennung → Datei und Funktion). Nennt der Anwender Kennungen („K010, D040 und T020, aber nach Geschoss“), ist das der Auftrag: die Funktionen
aus `bausteine.md` aufrufen bzw. kopieren und nur das Genannte ändern. Ein neuer Baustein bekommt die nächste freie Zehnerzahl seiner Art
und wird mit `@b.baustein("<Kennung>", "<Name>")` angemeldet – dann erscheint er von selbst im Verzeichnis.

Der schnelle Weg für vorhandene Bausteine: `python master/build_auswahl.py --bausteine=K010,D040,T020 --titel="…" --name=<Datei> [--ohne-etikett] --render`
stapelt sie in der genannten Reihenfolge zu `out/<Datei>.rdlc` (schmale nebeneinander, Seitenwechsel von selbst). Höhe, Breite und Parameter
je Baustein: `references/masse.md`. `--ohne-etikett` nimmt die Kennungs-Unterzeilen heraus (Kunden-Report). Verlangt der Auftrag anderen Inhalt
(„D040, aber Räume“), wird die Funktion kopiert und geändert; die Master-Abfrage kennt kein Geschoss-Feld – dann die Abfrage erweitern und
Beispieldaten neu holen (Ablauf Schritt 2).
Fertige Vorlagen zum Kopieren in Allplan: `<REPORT>/vorlagen/` (deu, eng, `LIESMICH.md`).

## Die Reports

| Report | Bildart | Bauskript | Ergebnis in `<REPORT>/out/` |
|---|---|---|---|
| Master (10 Seiten: alles, was geht) | 3D-Bauteilbild | `master/build_master.py` | `Report_Master.rdlc` |
| Begleit-Report Grundriss | Planausschnitt (Grundriss, Raumplan mit m² und Maßen) | `master/grundriss/build_grundriss.py` | `Report_Master_Grundriss.rdlc` |
| Begleit-Report Raum-Abwicklung | gezeichnete Abwicklung je Raum | `master/abwicklung/build_abwicklung.py` | `Report_Master_Abwicklung.rdlc` |
| Begleit-Report Wandbeläge | keine (Zahlen aus dem Raumausbau; Beispielsatz `wandbelag_bsp`) | `master/abwicklung/build_wandbelag.py` | `Report_Master_Wandbelag.rdlc` |
| Begleit-Report Bewehrung (Abfrage `ENGINEERING`, Stäbe und Matten; K080, U050, D170 bis D190, T090 bis T120) | Biegeform-Bild (`Projection=0`) | `master/bewehrung/build_bewehrung.py` | `Report_Master_Bewehrung.rdlc` |
| Begleit-Report Planliste (Abfrage `LAYOUT` plus `LAYOUT_DRAWINGS`; K090, D200, M090, T130, T140) | keine | `master/projektlisten/build_planliste.py` | `Report_Master_Planliste.rdlc` |
| Begleit-Report Listen (fließend; eigene Abfrage = Master-Abfrage ohne Bildspalte; K100, K110, U060, U070, T150, B110, B120) | keine (QR- und Strichcode-Bilder aus dem Code) | `master/listen/build_listen.py` | `Report_Master_Listen.rdlc` |
| Auswahl per Kennung | wie Master | `master/build_auswahl.py` | frei wählbar |

Mehrere Reports statt einem, weil Allplan je Report nur eine Abfrage füllt und nur eine Bildart liefert (Regeln 2, 3). In Allplan ausgegeben: Bewehrung am Probemodell und an einem echten Projekt (Summen wie Allplans „Übersicht Bewehrung“, Rechenregeln: `references/bewehrung.md`),
Planliste deutsch und englisch (nach Korrektur erneut, sauber), Wandbeläge an einem echten Haus (deutsch und englisch), Listen am Probemodell (9 Seiten, deutsch und englisch) und an einem echten Haus (11 Seiten); auf dem Etikettenblatt alle 8 QR- und 8 Strichcodes je PDF aus dem Allplan-PDF zurückgelesen, Etikettenseite im Report-Fenster wie im PDF.

## Zuerst lesen

1. Neuer Wunsch des Kunden: `references/rezepte.md` – Wunsch → geht / Kniff / geht nicht → womit (Kennung, Bausatz-Funktion, Abschnitt); die Bausatz-Funktionen stehen in `references/bausatz.md`.
2. `references/grenzen.md` – was geht, was nur mit Kniff, was nicht.
3. `<REPORT>/master/GESTALTUNG.md` – Raster, Farben, Schrift, Regeln für Diagramme, Abschnitt „Datenfest“.
4. Den Master rendern (`python master/build_master.py --render`) und die zehn Bilder ansehen: `master/aus/png/Report_Master_S1.png` … `_S10.png`.
   Sie sind der Maßstab; eine neue Seite muss daneben bestehen.

Nach Bedarf: `references/bausteine.md`, `masse.md`, `fallen.md`, `bilder.md`, `daten.md`, `sprache.md`, `pruefstrecke.md`; je Thema `bewehrung.md`, `projektlisten.md`, `codes.md` (Strichcode, QR, CSV).

## Regeln, die gemessen sind

1. **Schema 2016.** Gestaltete Reports entstehen im RDL-2016-Schema über den Bausatz (`master/core.py`, `viz.py`, `bausteine.py`), nicht als Hand-XML.
2. **Eine Abfrage für alles.** Allplan füllt nur das erste DataSet. Mehrere Themen kommen aus EINER breiten Abfrage; Tabellen und Diagramme
   trennen per Filter über die Objektnummer (`@OBJ@`). Ein Unterbericht führt keine eigene Abfrage aus: er bekommt die Zeilen des Hauptreports.
3. **Eine Bildart je Report.** Die erste `@205@`-Spalte bestimmt alle Bilder: 3D-Bauteilbild (`Projection`, farbig mit `Hidden=5`) oder
   Planausschnitt (`Image=true`: Grundriss, Raumplan). Braucht der Auftrag beides, entstehen zwei Reports (Vorbild `master/grundriss/`).
   Im Planbild erscheint, was im Teilbild liegt und innerhalb der Deckenkante; Maßketten außerhalb werden abgeschnitten (`references/bilder.md`).
4. **Jede wachsende Tabelle steht in einem Feld fester Größe** (`c.rect`). Sonst schiebt sie den Rest der Seite auf Folgeblätter.
5. **Datenfest.** Jede Liste, Legende und Kartenreihe hat einen Deckel (`c.topn`), kein Ausdruck enthält Namen eines bestimmten Projekts
   (Materialgruppe `b.MATGRUPPE`, Bauteilart `b.ART`). Die Seite besteht mit den drei ausgelieferten Datensätzen `master`, `master_en`
   (englische Materialnamen) und `gross` (3.000 künstliche Zeilen).
6. **Der Beweis ist Allplan.** Kopflos gerendert ist Vorschau. Fertig ist eine Seite erst, wenn Allplan sie ausgegeben hat und das Bild
   angesehen wurde – bis dahin ist sie nicht bewiesen (Ablauf Schritt 7).
7. **Lesbarkeit ist Abnahmebedingung.** Nichts überlappt, kleinste Schrift 7 pt (Etikett 6,5), Torte und Ring höchstens 5–7 Segmente mit
   eigener Legende statt Randbeschriftung. Geprüft wird am großen Datensatz (`gross`), das Einzeldiagramm vergrößert – am kleinen Master sieht
   fast alles gut aus.
8. **Jedes Bild ansehen.** Fehler in Diagrammen und Ausdrücken stehen nur als Text im Bild (`#Error`, schwarzer Fehlertext); kein Werkzeug meldet sie.
9. **Erst die Aussage, dann die Zahl.** Eine Seite beginnt mit dem, was der Leser wissen will: Kernaussage als Satz, Auffälligkeiten vor Listen.
   Diagramme sortiert nach Größe, Wert am Balken, höchstens sechs Farben.
10. **Parameter sind feste Werte.** Vorgaben und Listen als Ausdruck oder aus einem DataSet wertet Allplan nicht aus; Integer braucht eine Vorgabe (`c.parameter` prüft das, Regeltabelle in `grenzen.md`).
11. **Projekttabellen** (Pläne, Teilbilder, Projekt, Struktur) als erste Abfrage, ausgegeben als PDF oder DOCX, nie als XLSX; Bauteildaten daneben gibt es nicht (`projektlisten.md`).
12. **Bewehrung:** eine Abfrage `ENGINEERING`, Stab oder Matte über die Objektnummer, nie über einen Text aus der Abfrage; Stab-kg aus Gesamtlänge × kg je m, nie aus dem Feld Gewicht, weil Allplan gleiche Zeilen zusammenfasst (`bewehrung.md`).
13. **Code hat Vollzugriff.** Strichcode, QR und CSV laufen als VB-Code (`werkzeug/vb/`); eine CSV braucht einen absoluten Pfad (`codes.md`).
14. **Keine Überlappung.** Kein Element darf ein Nachbarelement im selben Container überlappen – mindestens 0,05 cm Abstand. Sonst verschiebt das Report-Fenster eines davon (PDF und Vorschau zeigen es nicht):
    Text rutscht unter den Nachbarn, wird in festen Rahmen abgeschnitten, Blöcke rücken nach unten. Hintergrundflächen als Eltern-Rectangle bauen, Striche als Rahmen, Titel und Untertitel nebeneinander;
    unsichtbare Ankerfelder zählen mit. Das Prüfskript meldet Überlappungen als Warnung W28 „Elemente überlappen sich“ (`validate_rdlc.py`); Text ab 9 pt ist im Fenster 0,5 bis 3 % schmaler als im PDF, Text bis 8,5 pt dagegen 3 bis 8 % BREITER (gemessen: 8,5 pt +3 %, 8 pt +8 %, 6,5 pt +5 %) – kleinem Text 10 % Breitenreserve geben (`fallen.md`).
    Ausgeblendete Felder (`Hidden`-Ausdruck) verschieben im Fenster sichtbare Elemente im selben Behälter, wenn ihre Kanten nicht auf deren Kanten liegen (gemessen bis 2,4 cm, auch bei 8 cm Abstand); ein eigener Behälter (Rectangle über die volle Breite, Sichtbarkeit am Behälter) behebt es.

## Ablauf

Jeder Schritt endet an der genannten Kante. R1 = statische Prüfung (`werkzeug/pruefen/validate_rdlc.py`), R2 = Beweis in Allplan.
Es gibt genau einen Prüfweg: kopflos rendern und ansehen (Schritte 4 und 5), statische Prüfung R1 (Schritt 6), dann öffnet der Anwender den
Report in Allplan und meldet zurück (R2, Schritt 7). Bis zu seiner Rückmeldung ist R2 „nicht geprüft“.

1. **Auftrag fassen.** Leser, die Frage, die der Report beantwortet, Objektarten, Bildart. Kante: ein Satz „Der Report zeigt <wem> <was>“ und
   die Liste der Bausteine nach Kennung.
2. **Daten holen.** Abfrage nach `references/daten.md` (Muster: `QUERY` in `bausteine.py`), jede Attribut-Nummer mit
   `werkzeug/pruefen/lookup_attribute.py` belegt. Der Anwender gibt den Probe-Report (`werkzeug/datenprobe.py`) in Allplan als Excel aus,
   `werkzeug/xlsx_zu_json.py` macht daraus JSON. Bis echte Daten da sind, wird mit `master.json` und `gross.json` gebaut.
   Kante: JSON mit echten Zeilen und genannter Zeilenzahl – oder der Satz „gebaut mit master.json und gross.json“.
3. **Seite bauen.** Eine Datei je Seite nach dem Muster `master/seiten/sNN_*.py`; Bausteine aus `bausteine.py`, Einmaliges in der Seite. Ein eigener
   Report bekommt ein eigenes Bauskript (Muster `master/grundriss/build_grundriss.py`). Kante: kopflos „OK Seiten=n“ mit der geplanten Seitenzahl.
4. **Ansehen und nachbessern.** Bild gegen Seite 1 halten: Fluchten, Abstände, Abgeschnittenes, Ruhe. Kante: drei Runden, in der letzten nichts mehr gefunden.
5. **Datenfest prüfen.** Dieselbe Seite mit `--daten=master`, `--daten=master_en`, `--daten=gross`. Kante: dreimal die geplante Seitenzahl, alle drei Bilder angesehen.
6. **R1.** `python werkzeug/pruefen/validate_rdlc.py out/<Datei>.rdlc`; die Zeile `AMPEL: …` geht wörtlich an den Nutzer. Kante: GRUEN – ORANGE nur, wenn jeder Hinweis erklärt ist (`references/pruefstrecke.md`) – und 0 Überlappungen (Warnung W28 „Elemente überlappen sich“) in allem, was im Fenster benutzt wird.
7. **R2, Beweis in Allplan** (`references/pruefstrecke.md`): der Anwender öffnet den Report in Allplan, bedient ihn im Fenster (dort zeigen sich Überlappungen) und meldet zurück: Bild oder Fehlermeldung.
   Bis zu seiner Rückmeldung ist R2 **GRAU („nicht geprüft“)** und wird nie als bestanden gemeldet. Kante: Rückmeldung des Anwenders liegt vor.
8. **Übergabe.** Siehe unten.

## Sprache

Reports werden deutsch gebaut; `python master/sprache.py --en` erzeugt die englische Fassung nach `out/eng/` aus den Tabellen `master/sprache/en/*.json`.
Neue Texte: `--sammeln`, Tabellen füllen, `--offen` meldet 0; dann englisch rendern und ansehen, weil englische Texte anders lang sind.
Berichtssprache `<Language>` de-DE bzw. en-US; der VB-Code erkennt Materialgruppen an deutschen und englischen Wortstämmen. Regeln und Befehle: `references/sprache.md`.

## Raum-Abwicklung

Je Raum EIN zusammenhängendes Band (Wände im Uhrzeigersinn ab der längsten, jede Wand in wahrer Länge, L-Räume und schräge Wände gehen),
eine durchlaufende Maßlinie, Kürzel T1/F1, Legende, Lageskizze; ab 1:300 zweite Reihe. **Der Report zeichnet nicht selbst:** er zeigt nur, was im
Teilbild liegt – die Zeichnung muss vorher dorthin.
- **Dieses Paket legt keine Zeichnung in Allplan ab.** Es liefert den Rechenkern (`werkzeug/abwicklung_kern.py`, rechnet die Geometrie), den Zeichenauftrag
  (`werkzeug/abwicklung_zeichnen.py`) und die Vorschau ohne Allplan (`werkzeug/abwicklung_vorschau.py`). Die Zeichnung im Beispiel wurde eigens
  angelegt; sie zeigt, was geht, wenn eine Zeichnung im Teilbild liegt. Ohne eigene Zeichnung im Teilbild bleibt
  die Vorlage „Report Master Raum-Abwicklung“ leer. Das dem Anwender vor der Übergabe sagen.
Einzelheiten, gemessene Datenquellen und die drei erprobten Wege: `references/bilder.md`.

## Werkzeuge

| Zweck | Befehl (in `<REPORT>`) |
|---|---|
| Renderer bauen (einmalig) | `powershell -ExecutionPolicy Bypass -File werkzeug/render/build.ps1` |
| Master bauen und kopflos rendern | `python master/build_master.py --render [--nur=N] [--daten=master\|master_en\|gross]` |
| Begleit-Reports bauen | `python master/grundriss/build_grundriss.py --render` · `python master/abwicklung/build_abwicklung.py --render` · `python master/abwicklung/build_wandbelag.py --render` · `python master/bewehrung/build_bewehrung.py --render` · `python master/projektlisten/build_planliste.py --render` · `python master/listen/build_listen.py --render` |
| Report aus Kennungen | `python master/build_auswahl.py --bausteine=K010,D040,T020 --render` |
| Englische Fassung | `python master/sprache.py --en` (Tabellen: `references/sprache.md`) |
| Maße der Bausteine prüfen / neu schreiben | `python master/masse.py` · `python master/masse.py --md` (schreibt in der Werkstatt nach `out/masse.md`) |
| Abwicklung rechnen und ansehen (ohne Allplan) | `python werkzeug/abwicklung_zeichnen.py <elemente.json> <auftrag.json> [--sprache=de\|en]` · `python werkzeug/abwicklung_vorschau.py <auftrag.json> <ordner>` |
| Abfrage ausprobieren | `python werkzeug/datenprobe.py <ziel.rdlc> --from "[MODEL_DATA]" "@498@:Objekt" …` |
| Excel-Export zu Beispieldaten | `python werkzeug/xlsx_lesen.py <datei.xlsx>` · `python werkzeug/xlsx_zu_json.py <probe.rdlc> <probe.xlsx> <ziel.json>` |
| Beispieldaten neu | `python master/daten/make_gross.py` · `python master/abwicklung/daten/make_wandbelag_bsp.py` |
| PDF ansehen | `python werkzeug/pdf_zu_png.py <datei.pdf>` · `python werkzeug/kontaktbogen.py …` |
| Tests | `python -m pytest werkzeug/tests -q` |
| VB-Code für Strichcode, QR und CSV | `werkzeug/vb/codes.vb`, `werkzeug/vb/zweite_datenquelle.vb` (Einbau: `references/codes.md`) |
| Report statisch prüfen (R1) | `python werkzeug/pruefen/validate_rdlc.py out/<Datei>.rdlc` (auch ein ganzer Ordner) |
| Attribut-Nummer nachschlagen | `python werkzeug/pruefen/lookup_attribute.py 220 507 --suche Volumen` (braucht den Attributkatalog der Allplan-Installation, siehe `references/daten.md`) |

## Offen (nicht belegt) und Prüfregel

- Prüfregel: `--daten=gross` ergibt ohne `--nur` wie `master` 10 Seiten. Die empfindliche Stelle ist Seite 5 (Baustein T060 „Bauteile nach
  Materialgruppe und Bauteilart“): sie darf bei mehreren Materialgruppen mit mehreren Bauteilarten nicht auf eine weitere Seite umbrechen.
- OFFEN: Klick ins Modell (`Zoom:`, `Edit:`) in einem Report, den Allplans Befehl „Reports“ öffnet (im Testfenster ohne Wirkung), Tooltips, angeklickte Hyperlinks, Export aus dem Fenster, Auswahl im Mehrfach-Dialog.
  Aufklappen, Sortieren, Stellschrauben (Haken, Zahl, Liste), Drillthrough, Dokumentstruktur und fixierter Kopf sind im Fenster bedient (`references/grenzen.md`, Abschnitt „Bedienung“).
- OFFEN: Ursache der leeren Projekttabellen `LAYOUT_HISTORY`, `ATTRIBUTES` und `FILESET` mit Filter (`references/grenzen.md`, Abschnitt „Nicht geprüft“).
- Dauer: ein großes Projekt mit 3.545 Bauteilen, 10-Seiten-Master 3 bis 7 Minuten – Anwender vorwarnen.

## Übergabe

Höchstens 30 Zeilen: Datei(en) in `out/`; die Frage, die der Report beantwortet; Bausteine nach Kennung; Abfrage mit Filter; Bildart; Ergebnis der drei
Datensätze; die `AMPEL`-Zeile von R1; R2 (Bild aus Allplan mit Pfad – oder GRAU „nicht geprüft“, bis der Anwender zurückmeldet); was im Allplan-Fenster nicht
selbst geprüft wurde (Klick ins Modell, Tooltips, Hyperlinks; ohne Fensterprüfung die ganze Bedienung); Sprachen (deutsch, englisch).
