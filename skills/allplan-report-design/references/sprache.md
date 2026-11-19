# Sprache: deutsch bauen, englisch erzeugen

Reports werden **deutsch gebaut**. Die englische Fassung entsteht danach mit `master/sprache.py` aus Tabellen – nichts wird doppelt gebaut.
Berichtssprache im Report: `<Language>de-DE</Language>` bzw. `en-US`; Zahlen- und Datumsformat folgen ihr (`1.234,57` ↔ `1,234.57`).
In Allplan ausgegeben (2026-11-18): Master 10 Seiten, Grundriss 2, Abwicklung 5, Auswahl 1 – jeweils auch englisch.

## Befehle (in `<REPORT>`)

| Zweck | Befehl |
|---|---|
| Englische Fassung aller Reports in `out/` erzeugen (Name beginnt nicht mit `_`) | `python master/sprache.py --en` → `out/eng/` (eine Datei mit fehlenden Texten wird ausgelassen und als `AUSGELASSEN …` gemeldet; Rückgabe 1) |
| Eine Datei, auch ein eigener Report | `python master/sprache.py --en out/<Datei>.rdlc` → `out/eng/<Datei>.rdlc` |
| Eine Datei, fehlende Texte bleiben deutsch (nur Vorschau) | `python master/sprache.py --en out/_Seite3.rdlc --lax` |
| Zeigen, was noch nicht übersetzt ist | `python master/sprache.py --offen` (alle) bzw. `--offen out/<Datei>.rdlc` (eine Datei) |
| Neue Texte in die Tabellen eintragen (Übersetzung `null` = offen) | `python master/sprache.py --sammeln` (Master) bzw. `--sammeln out/<Datei>.rdlc` (eigener Report) |

Die Tabellen liegen in `master/sprache/en/*.json`: `00_gemeinsam` (Texte aus zwei oder mehr Quellen), `s01` … `s10`, `grundriss`,
`abwicklung`, `wandbelag`, `auswahl`. Form: `{ "deutscher Text": "english text" }`. `--sammeln` liest `out/_Seite1.rdlc` … `_Seite10.rdlc`
(erzeugt mit `build_master.py --nur=N`), die drei Begleit-Reports und `out/Report_Auswahl_Beispiel.rdlc`. Ist eine dieser Quellen nicht gebaut,
bleiben ihre Einträge unverändert (Zeile `Hinweis: nicht gebaut …`); neu geordnet wird nur, was gebaut ist. `bausatz.json` enthält Texte des
Bausatzes, die in keinem Beispiel stehen (Standardtitel von `build_auswahl.py`); `eigene.json` die Texte eigener Reports. Beide fasst `--sammeln` nicht an.
**In einer frischen Werkstatt genügt für jede Änderung der Weg „Eigener Report“ unten** – auch für eine geänderte Master-Seite
(`--sammeln out/Report_Master.rdlc`).

## Regeln der Tabellen (Kopf von `sprache.py`)

- `"="` heißt „bleibt, wie es ist“ (Wortstämme zum Erkennen von Modelldaten, Einheiten, technische Namen). `null` heißt „noch offen“.
- Dieselbe Zeichenkette wird überall gleich ersetzt, im festen Text, im Ausdruck und im VB-Code: „Beton“ in `Code.MatArt` und im Vergleich
  eines Ausdrucks werden beide zu „Concrete“.
- Ein **geschütztes Leerzeichen (U+00A0) am Wortende** macht aus demselben deutschen Wort einen eigenen Schlüssel: für die Mehrzahl
  („Fenster“ = Window, „Fenster“ + U+00A0 = Windows) oder eine Kurzform nur fürs Englische („Beton“ + U+00A0 = Concr.).
- **Bereichsnamen von Summenfunktionen bleiben stehen** (`Sum(x, "S3_TbTorte")`): Namen von Tabellen und Gruppen werden nicht übersetzt.
- Nicht übersetzt wird, was aus dem Modell kommt (Raumnamen, Materialien, Bauteilnamen). Der VB-Code erkennt Materialgruppen an deutschen
  und englischen Wortstämmen (`Code.MatArt`, `Code.IstVerkehr` in `bausteine.py`), darum laufen englische Modelle ohne Umbau.

## Ablauf bei neuen oder geänderten Texten

1. Deutsch bauen (`build_master.py`, Begleit-Reports, `build_auswahl.py`). Kante: die `.rdlc` liegen in `out/`.
2. `python master/sprache.py --sammeln`; die neuen Einträge stehen auf `null`. Tabellen füllen. Kante: `python master/sprache.py --offen` meldet überall 0 offen.
3. `python master/sprache.py --en`. Kante: `out/eng/` enthält jede Datei, keine Zeile `AUSGELASSEN`, Rückgabe 0.
4. **Englisch rendern und ansehen**, weil englische Texte anders lang sind (Abschneiden, Umbrüche):
   `python master/build_master.py --render --daten=master_en` rendert die deutsche Fassung mit englischen Materialnamen; die englische `.rdlc` rendert man
   mit `werkzeug\render\bin\RenderRdlc.exe out\eng\Report_Master.rdlc master\daten\master_en.json <ordner>`. Kante: `OK Seiten=n` mit derselben Zahl wie
   deutsch, jedes PNG angesehen.
5. R1 (`pruefstrecke.md`, Abschnitt (e)) auch auf die englische Datei.

## Eigener Report (nicht Teil des Masters)

1. Deutsch bauen; die `.rdlc` liegt in `out/`.
2. `python master/sprache.py --sammeln out/<Datei>.rdlc` trägt die neuen Texte des Reports in `master/sprache/en/eigene.json` ein (Wert `null`).
3. Die KI füllt die Einträge englisch. Kante: `python master/sprache.py --offen out/<Datei>.rdlc` zeigt 0.
4. `python master/sprache.py --en out/<Datei>.rdlc` erzeugt `out/eng/<Datei>.rdlc`. Dann englisch rendern und ansehen wie oben (Schritt 4 und 5).

Beispieldatensatz mit englischen Materialnamen: `master/daten/master_en.json` (Concrete, Masonry, Insulation, Plasterboard).
Die Abwicklungs-Zeichnung hat ihre eigene Sprachwahl: `abwicklung_zeichnen.py --sprache=de|en` (`bilder.md`).
