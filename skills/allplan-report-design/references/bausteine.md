# Bausteinverzeichnis

Erzeugt von `master/build_master.py` aus den Anmeldungen (`@b.baustein`) - nicht von Hand ändern.
Die Kennung steht im Report klein unter dem Schaustück und auf Seite 10 des Masters.
Bauplan = die genannte Funktion in der Datei unter `master/`; sie nimmt `(top, left, w)` und liefert das XML des Blocks.
Gemeinsame Teile (Kachel, Abschnittskopf, Kennwert-Balken, Bildkarten, Klick ins Modell) in `master/bausteine.py`.

## K - Kennzahlen und Kernaussagen

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| K010 | Kernaussage | Master Seite 1 | `seiten/s01_uebersicht.py` · `k010` | Satz aus Ausdrücken (Sum, IIf, Format); Halbsätze ohne Grundlage entfallen, Beton über die Materialgruppe |
| K020 | Kennzahl-Kacheln | Master Seite 1 | `seiten/s01_uebersicht.py` · `k020` | fünf Kacheln; die Zahl schrumpft mit der Stellenzahl, ab 100 ohne Nachkommastelle |
| K030 | Kennzahl-Kacheln | Master Seite 4 | `seiten/s04_messanzeigen.py` · `k030` | Kachel hell (wie Seite 1), dunkel, mit Vergleichszeile in Bewertungsfarbe, mit Mini-Diagramm (höchstens 8 Säulen) |
| K040 | Kernaussage | Master Seite 7 | `seiten/s07_bedienen.py` · `k040` | Satz aus Ausdrücken (Switch, Format, Max): größte Materialgruppe, Fensteranteil gegen den Parameter Ziel, Zahl der Hinweise |
| K050 | Kennzahl-Kacheln | Begleit-Report Grundriss | `grundriss/build_grundriss.py` · `k050` |  |
| K060 | Kennzahl-Kacheln | Begleit-Report Wandbelag | `abwicklung/build_wandbelag.py` · `k060` |  |
| K070 | Kennzahl-Kacheln Abwicklung | Begleit-Report Abwicklung | `abwicklung/build_abwicklung.py` · `k070` |  |
| K080 | Kennzahl-Kacheln Stahl | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `k080` |  |
| K090 | Kennzahl-Kacheln Planliste | Begleit-Report Planliste | `projektlisten/build_planliste.py` · `k090` |  |
| K100 | Kernaussage Listen | Begleit-Report Listen | `listen/build_listen.py` · `k100` |  |
| K110 | Kennzahl-Kacheln Listen | Begleit-Report Listen | `listen/build_listen.py` · `k110` |  |

## D - Diagramme

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| D010 | Balken Volumen nach Materialgruppe | Master Seite 1 | `seiten/s01_uebersicht.py` · `d010` | Balken je Materialgruppe (Code.MatArt), Farbe über Code.MatFarbe, höchstens 9 Gruppen |
| D020 | Ring mit Legende | Master Seite 1 | `seiten/s01_uebersicht.py` · `d020` | TopN 7 in Ring und Legende, Rest als Zeile |
| D030 | Fläche je Bauteilart | Master Seite 2 | `seiten/s02_vergleichen.py` · `d030` | Säulen mit Direktbeschriftung, Art aus der Objektnummer, Werteachse entfällt |
| D040 | Die 8 größten Bauteile | Master Seite 2 | `seiten/s02_vergleichen.py` · `d040` | Balken-Rangliste Top 8 (Filter TopN), Materialfarbe, Wert am Balken |
| D050 | Volumen je Bauteilart | Master Seite 2 | `seiten/s02_vergleichen.py` · `d050` | Gestapelte Säulen, Serien = Materialgruppen (höchstens 5), Summe als Linie |
| D060 | Materialanteile der Wandschichten | Master Seite 2 | `seiten/s02_vergleichen.py` · `d060` | 100-%-Stapelbalken, Serien = Materialgruppen, Anteil im Segment |
| D070 | Die 8 größten Wandaufbauten | Master Seite 2 | `seiten/s02_vergleichen.py` · `d070` | Pareto Top 8: eigene Achsen, Linie kumuliert zur Gesamtsumme aller Schichten |
| D080 | Fenster und Türen nach Breite | Master Seite 2 | `seiten/s02_vergleichen.py` · `d080` | Gruppierte Säulen, vier Breitenklassen, zwei Serien |
| D090 | Volumen nach Bauteilart | Master Seite 3 | `seiten/s03_anteile.py` · `d090` | Ring mit Zahl in der Mitte, eigene Legende mit Wert und Anteil |
| D100 | Fläche nach Typ | Master Seite 3 | `seiten/s03_anteile.py` · `d100` | Torte Top 5 Typen, Legende: Anteil an den 5 gezeigten (= 100 %) |
| D110 | Volumen nach Material | Master Seite 3 | `seiten/s03_anteile.py` · `d110` | Pyramide Top 6 Materialgruppen, Fläche = Volumen, Materialfarben |
| D120 | Volumen nach Bauteil und Material | Master Seite 3 | `seiten/s03_anteile.py` · `d120` | TreeMap Top 10 Felder (Bauteil + Material), Fläche = Volumen |
| D130 | Fläche gegen Volumen | Master Seite 3 | `seiten/s03_anteile.py` · `d130` | Punktwolke je Bauteil, Farbe nach Materialgruppe, Achsen logarithmisch |
| D140 | Öffnungen: Breite, Höhe, Anzahl | Master Seite 3 | `seiten/s03_anteile.py` · `d140` | Blasen je Format (12 häufigste), Größe = Anzahl, ohne Beschriftung |
| D150 | Ring Fläche nach Nutzung mit Legende | Begleit-Report Grundriss | `grundriss/build_grundriss.py` · `d150` |  |
| D160 | Balken Wandfläche je Raum | Begleit-Report Wandbelag | `abwicklung/build_wandbelag.py` · `d160` |  |
| D170 | Balken Rundstahl nach Durchmesser | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `d170` |  |
| D180 | Ring Stab / Matte | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `d180` |  |
| D190 | Ring gerade / gebogen | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `d190` |  |
| D200 | Säulen Pläne je Monat | Begleit-Report Planliste | `projektlisten/build_planliste.py` · `d200` |  |

## M - Messanzeigen

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| M010 | Kennwert-Balken | Master Seite 1 | `seiten/s01_uebersicht.py` · `m010` | Prozent mit Balken; ohne Grundlage steht – |
| M020 | Tacho-Reihe | Master Seite 4 | `seiten/s04_messanzeigen.py` · `m020` | RadialGauge Halbkreis, Bewertungsfarben; Ziele sind Annahmen. Außenwand = Wandschicht aus Beton oder Mauerwerk ab 20 cm Dicke |
| M030 | Fortschrittsringe | Master Seite 4 | `seiten/s04_messanzeigen.py` · `m030` | RadialGauge 270°, RadialPointer Typ Bar auf heller Spur |
| M040 | Zielbalken (Bullet-Graph) | Master Seite 4 | `seiten/s04_messanzeigen.py` · `m040` | Balkendiagramm: Bänder gestapelt, Ist auf 2. Achse, Ziele angenommen |
| M050 | Fortschrittsbalken | Master Seite 4 | `seiten/s04_messanzeigen.py` · `m050` | Baustein fortschritt, Zielbereich als Linie, zwei Farben gestapelt |
| M060 | Ampel mit Schwellen | Master Seite 4 | `seiten/s04_messanzeigen.py` · `m060` | StateIndicator mit Schwellen (ohne Grundlage grau); Textsymbol per Ausdruck |
| M080 | Kennwert-Balken | Begleit-Report Grundriss | `grundriss/build_grundriss.py` · `m080` |  |
| M090 | Vollständigkeit des Plankopfs | Begleit-Report Planliste | `projektlisten/build_planliste.py` · `m090` |  |

## T - Tabellen

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| T010 | Tabelle mit Zellenbalken | Master Seite 1 | `seiten/s01_uebersicht.py` · `t010` | Tablix je Materialgruppe, TopN 5, Balken-Diagramm in der Zelle; die Summe zählt alle Gruppen |
| T020 | Rangliste mit Zellenbalken | Master Seite 5 | `seiten/s05_tabellen.py` · `t020` | Zellenbalken je Zeile, Akzent am größten Wert; Deckel 9, Summe über alle |
| T030 | Statussymbole (Türtypen) | Master Seite 5 | `seiten/s05_tabellen.py` · `t030` | Türen je Typ und Breite (Deckel 9); Symbol und Farbe nach Schwelle |
| T040 | Kreuztabelle mit Farbskala | Master Seite 5 | `seiten/s05_tabellen.py` · `t040` | Zeilen = Bauteilart, Spalten = Materialgruppe (die 5 größten); Farbskala per Hintergrundausdruck, voll ab 25 % des Gesamtvolumens |
| T050 | Stapelbalken in der Tabellenzelle | Master Seite 5 | `seiten/s05_tabellen.py` · `t040` | 100-%-Stapelbalken in der Zelle: Diagramm je Zeile, Farbe der Materialgruppe, Segmente ab 14 % beschriftet |
| T060 | Gruppierte Tabelle mit Zwischensummen | Master Seite 5 | `seiten/s05_tabellen.py` · `t060` | Zeilengruppen Materialgruppe (höchstens 6) und Bauteilart; Einzelzeilen und Zwischensumme nur für die größte Gruppe, alle anderen eine Zeile |
| T070 | Mini-Säulen im Gruppenkopf | Master Seite 5 | `seiten/s05_tabellen.py` · `t060` | Mini-Säulen im Gruppenkopf: die 12 größten Einzelbauteile je Gruppe, absteigend nach Volumen |
| T080 | Wandflächen je Raum (Kreuztabelle) | Begleit-Report Wandbelag | `abwicklung/build_wandbelag.py` · `t080` |  |
| T090 | Matten nach Typ | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `t090` |  |
| T100 | Rundstahl nach Stahlgüte | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `t100` |  |
| T110 | Stabliste | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `t110` |  |
| T120 | Mattenliste | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `t120` |  |
| T130 | Hinweisliste: was fehlt | Begleit-Report Planliste | `projektlisten/build_planliste.py` · `t130` |  |
| T140 | Planliste mit Teilbildern | Begleit-Report Planliste | `projektlisten/build_planliste.py` · `t140` |  |
| T150 | Bauteilliste je Art | Begleit-Report Listen | `listen/build_listen.py` · `t150` |  |

## B - Bilder

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| B010 | Bildkarten | Master Seite 1 | `seiten/s01_uebersicht.py` · `b010` | Karte je Typ mit Bild aus Allplan, TopN 5 nach Häufigkeit (häufigster zuerst), Klick zoomt aufs Bauteil |
| B020 | Steckbriefe aus dem Modell | Master Seite 6 | `seiten/s06_bilder.py` · `b020` | Steckbrief: Karte je Typ (Gruppe mit Deckel c.topn: häufigster Typ bzw. größtes Bauteil), Bild =First(Bild), Klick zoomt |
| B030 | Bildleiste Bauteile | Master Seite 6 | `seiten/s06_bilder.py` · `b030` | Bildleiste: Spaltengruppe je Bauteilart und Materialgruppe, Deckel 8, =First(Bild); ohne Bild erscheint das Piktogramm |
| B040 | Bauteilarten mit Piktogramm | Master Seite 6 | `seiten/s06_bilder.py` · `b040` | Eingebettete Piktogramme: Bild per Ausdruck nach Objektart, ohne Dateipfad |
| B050 | Materialien als Muster | Master Seite 6 | `seiten/s06_bilder.py` · `b050` | Muster als Kachel-Hintergrund (Repeat), nach Materialgruppe, Deckel 4 |
| B060 | Firmenlogo aus Parameter | Master Seite 6 | `seiten/s06_bilder.py` · `b060` | Externes Bild: file:/// & Company_Logo, Sichtbarkeit Display_Logo |
| B070 | Hinweistafel Bildarten | Master Seite 6 | `seiten/s06_bilder.py` · `b070` | Hinweistafel: Textfläche auf c.SURFACE, drei Spalten |
| B080 | Geschoss-Grundriss | Begleit-Report Grundriss | `grundriss/build_grundriss.py` · `b080` |  |
| B090 | Raumkarten | Begleit-Report Grundriss | `grundriss/build_grundriss.py` · `b090` |  |
| B100 | Abwicklung je Raum | Begleit-Report Abwicklung | `abwicklung/build_abwicklung.py` · `b100` |  |
| B110 | Etiketten mit QR-Code | Begleit-Report Listen | `listen/build_listen.py` · `b110` |  |
| B120 | Strichcode 128 | Begleit-Report Listen | `listen/build_listen.py` · `b120` |  |

## U - Bedienung

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| U010 | Bedien-Legende | Master Seite 7 | `seiten/s07_bedienen.py` · `u010` | Bedien-Legende: vier Kacheln, reiner Text - sagt dem Anwender, dass dieser Report bedienbar ist |
| U020 | Hinweisliste | Master Seite 7 | `seiten/s07_bedienen.py` · `u020` | Tablix mit Gruppenfilter (Türen) und per Ausdruck sichtbaren Zeilen, BookmarkLink Zoom/Mark je Zeile, Tooltip; ohne Treffer Haken-Zeile |
| U030 | Kostenschätzung | Master Seite 7 | `seiten/s07_bedienen.py` · `u030` | Preise als Report-Parameter (Switch je Materialgruppe), Kosten = Volumen × Preis, TopN 5, Ring in Materialfarben; rechnet bei jeder Parameteränderung neu |
| U040 | Aufklappbare Tabelle | Master Seite 7 | `seiten/s07_bedienen.py` · `u040` | Tablix mit ToggleItem (Startzustand aus Parameter Zeige_Details), UserSort am Spaltenkopf, TopN 5 Gruppen und 5 Zeilen je Gruppe, BookmarkLink Zoom/Mark |
| U050 | Hinweis Überlängen | Begleit-Report Bewehrung | `bewehrung/build_bewehrung.py` · `u050` |  |
| U060 | Auswertung nach Wahl | Begleit-Report Listen | `listen/build_listen.py` · `u060` |  |
| U070 | Auswahl aus den Daten | Begleit-Report Listen | `listen/build_listen.py` · `u070` |  |

## X - Text, Symbole, Flächen

| Kennung | Name | Zu sehen | Datei · Funktion | Technik |
|---|---|---|---|---|
| X010 | Schriftstufen | Master Seite 8 | `seiten/s08_text.py` · `x010` | Typo-Skala, drei Schnitte der Segoe UI |
| X020 | Bericht in Worten | Master Seite 8 | `seiten/s08_text.py` · `x020` | TextRuns mit Ausdruck, darunter HTML |
| X030 | Farbpalette | Master Seite 8 | `seiten/s08_text.py` · `x030` | Rechtecke mit Hintergrundfarbe, Werte aus core.py, kein Verlauf, keine Transparenz |
| X040 | Zeichen und Schichtarten | Master Seite 8 | `seiten/s08_text.py` · `x040` | Segoe UI Symbol, Zeichen und Farbe per Ausdruck (IIf), je Materialgruppe und Dicke eine Zeile |
| X050 | Rangliste aus Zeichen | Master Seite 8 | `seiten/s08_text.py` · `x050` | Balken aus Zeichen (StrDup, Consolas), die größten Nutzungen |
| X060 | Farbskala-Kacheln | Master Seite 8 | `seiten/s08_text.py` · `x060` | Tonwert = √(Fläche ÷ größte Nutzung), per Hex() |
| X080 | Übersicht Geht / Kniff / Geht nicht | Master Seite 9 | `seiten/s09_grenzen.py` · `x080` | Drei Spalten aus Textboxen; Kopfzeichen in Segoe UI Symbol, je Zeile Stichwort und Halbsatz |
| X090 | Die harten Grenzen | Master Seite 9 | `seiten/s09_grenzen.py` · `x090` | Fünf Zeilen auf heller Fläche, große Ziffer in Segoe UI Light, Satz und Folge in einer Textbox |
