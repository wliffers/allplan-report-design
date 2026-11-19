# Maße der Bausteine

Erzeugt von `master/masse.py --md` - nicht von Hand ändern.
Höhe = Platz samt Abschnittskopf und Etikett (mit kleiner Reserve). Breite = die Breite, für die der Baustein gebaut ist;
zwei Bausteine, die zusammen eine Zeile füllen (halb + halb, breit + schmal, drittel + zweidrittel), stehen nebeneinander.
„braucht“ = Report-Parameter, die der Baustein im Ausdruck benutzt (Project_Name und Date liefert Allplan immer).
Report aus Kennungen bauen: `python master/build_auswahl.py --bausteine=K010,D040,T020 [--titel="…"] [--ohne-etikett] [--render]`.

| Kennung | Name | Höhe cm | Breite | braucht | Hinweis |
|---|---|---|---|---|---|
| B010 | Bildkarten | 5,70 | zweidrittel (10,8 cm) | – | steht auf der Master-Seite 1 neben M010 |
| B020 | Steckbriefe aus dem Modell | 9,10 | voll (18 cm) | – |  |
| B030 | Bildleiste Bauteile | 4,60 | voll (18 cm) | – |  |
| B040 | Bauteilarten mit Piktogramm | 7,65 | halb (8,8 cm) | – |  |
| B050 | Materialien als Muster | 4,90 | halb (8,8 cm) | – |  |
| B060 | Firmenlogo aus Parameter | 2,60 | halb (8,8 cm) | `Company_Logo`, `Display_Logo` | Logo kommt aus Allplans Parametern Company_Logo und Display_Logo; ohne Logo steht ein Hinweis |
| B070 | Hinweistafel Bildarten | 2,45 | voll (18 cm) | – |  |
| D010 | Balken Volumen nach Materialgruppe | 5,70 | breit (10,4 cm) | – | steht auf der Master-Seite 1 neben D020 |
| D020 | Ring mit Legende | 5,70 | schmal (7,2 cm) | – | steht auf der Master-Seite 1 neben D010 |
| D030 | Fläche je Bauteilart | 7,60 | halb (8,8 cm) | – |  |
| D040 | Die 8 größten Bauteile | 7,60 | halb (8,8 cm) | – |  |
| D050 | Volumen je Bauteilart | 7,60 | halb (8,8 cm) | – |  |
| D060 | Materialanteile der Wandschichten | 7,60 | halb (8,8 cm) | – |  |
| D070 | Die 8 größten Wandaufbauten | 7,60 | halb (8,8 cm) | – |  |
| D080 | Fenster und Türen nach Breite | 7,60 | halb (8,8 cm) | – |  |
| D090 | Volumen nach Bauteilart | 7,75 | halb (8,8 cm) | – |  |
| D100 | Fläche nach Typ | 7,75 | halb (8,8 cm) | – |  |
| D110 | Volumen nach Material | 7,75 | halb (8,8 cm) | – |  |
| D120 | Volumen nach Bauteil und Material | 7,75 | halb (8,8 cm) | – |  |
| D130 | Fläche gegen Volumen | 7,75 | halb (8,8 cm) | – |  |
| D140 | Öffnungen: Breite, Höhe, Anzahl | 7,75 | halb (8,8 cm) | – |  |
| K010 | Kernaussage | 1,80 | voll (18 cm) | `Ziel_Fensteranteil` |  |
| K020 | Kennzahl-Kacheln | 3,10 | voll (18 cm) | – |  |
| K030 | Kennzahl-Kacheln | 4,60 | voll (18 cm) | `Ziel_Fensteranteil` |  |
| K040 | Kernaussage | 3,75 | voll (18 cm) | `Tuer_Mindestbreite`, `Ziel_Fensteranteil` |  |
| M010 | Kennwert-Balken | 5,70 | drittel (6,6 cm) | – | steht auf der Master-Seite 1 neben B010 |
| M020 | Tacho-Reihe | 6,15 | voll (18 cm) | `Ziel_Fensteranteil` |  |
| M030 | Fortschrittsringe | 5,95 | halb (8,8 cm) | – |  |
| M040 | Zielbalken (Bullet-Graph) | 5,95 | halb (8,8 cm) | `Ziel_Fensteranteil` |  |
| M050 | Fortschrittsbalken | 6,80 | halb (8,8 cm) | `Ziel_Fensteranteil` |  |
| M060 | Ampel mit Schwellen | 6,80 | halb (8,8 cm) | `Ziel_Fensteranteil` |  |
| T010 | Tabelle mit Zellenbalken | 6,70 | voll (18 cm) | – |  |
| T020 | Rangliste mit Zellenbalken | 7,85 | halb (8,8 cm) | – |  |
| T030 | Statussymbole (Türtypen) | 8,15 | halb (8,8 cm) | – |  |
| T040 | Kreuztabelle mit Farbskala | 7,10 | voll (18 cm) | – |  |
| T050 | Stapelbalken in der Tabellenzelle | 7,10 | voll (18 cm) | – | Teil von T040 (gleiche Funktion, nicht zusammen mit T040 wählbar) |
| T060 | Gruppierte Tabelle mit Zwischensummen | 9,30 | voll (18 cm) | – |  |
| T070 | Mini-Säulen im Gruppenkopf | 9,30 | voll (18 cm) | – | Teil von T060 (gleiche Funktion, nicht zusammen mit T060 wählbar) |
| U010 | Bedien-Legende | 1,65 | voll (18 cm) | – |  |
| U020 | Hinweisliste | 7,10 | voll (18 cm) | `Tuer_Mindestbreite`, `Ziel_Fensteranteil` |  |
| U030 | Kostenschätzung | 6,65 | voll (18 cm) | `Preis_Beton`, `Preis_Daemmung`, `Preis_Gipskarton`, `Preis_Mauerwerk` |  |
| U040 | Aufklappbare Tabelle | 5,35 | voll (18 cm) | `Zeige_Details` |  |
| X010 | Schriftstufen | 7,65 | halb (8,8 cm) | – |  |
| X020 | Bericht in Worten | 7,65 | halb (8,8 cm) | – |  |
| X030 | Farbpalette | 5,25 | voll (18 cm) | – |  |
| X040 | Zeichen und Schichtarten | 6,15 | voll (18 cm) | – |  |
| X050 | Rangliste aus Zeichen | 5,50 | halb (8,8 cm) | – |  |
| X060 | Farbskala-Kacheln | 5,50 | halb (8,8 cm) | – |  |
| X080 | Übersicht Geht / Kniff / Geht nicht | 12,05 | voll (18 cm) | – | über ein halbes Blatt hoch |
| X090 | Die harten Grenzen | 8,05 | voll (18 cm) | – |  |
