# Bausatz: die Funktionen in `master/core.py`

Übersicht für die KI: welche Funktion wofür da ist und wie weit sie in Allplan gemessen ist (A = in Allplan 2027 ausgegeben, K = nur kopflos; Belegstufen: `grenzen.md`).
Quelle sind die Docstrings in `master/core.py`. Genaue Signatur und Beispiel: `python -c "import sys; sys.path.insert(0,'master'); import core; help(core.tablix)"`
und die Bauskripte der Begleit-Reports als Vorbild: `master/listen/build_listen.py` (fließende Listen), `master/bewehrung/build_bewehrung.py` (vollständige Tabellen mit Bild),
`master/projektlisten/build_planliste.py` (Projekttabellen). In den Bauskripten heißt das Modul `c`.

## Grundbausteine

| Funktion | Wofür | Stand |
|---|---|---|
| `run`, `para` | Textstück und Absatz; mehrere `run` ergeben gemischte Formate in einer Textbox | A (nur Schema 2016) |
| `text` | Textbox mit Lage; `content` aus `run`/`para` oder Liste von `para` | A |
| `cell` | Textbox für eine Tabellenzelle (ohne Lage) | A |
| `edge`, `box_style` | Rahmen nur an genannten Seiten, Fläche und Innenabstand | A |
| `rect` | Rechteck als Rahmen oder Seitenfeld; Seitenumbruch (`page_break`, `umbruch` Start oder End), `hidden`, `label`, `seitenname`, `bookmark`, `seitenzaehlung_neu` | A; Start plus End hintereinander ergibt eine leere Seite; `seitenzaehlung_neu` am Rectangle in Allplan ausgegeben |
| `line` | Linie | K |
| `image` | Bild aus Datenbank, Datei oder eingebettet; `sizing`, `mime`, `action` | A; nur PNG, JPG, GIF, BMP |
| `embedded` | alle PNG eines Ordners als eingebettete Bilder | A |
| `dataset` | DataSet mit Abfrage und Feldliste (Typ String, Double, Int32, Byte[]); setzt `<CaseSensitivity>True</CaseSensitivity>`, damit Gruppen und `CountDistinct` Texte gleich unterscheiden | A; nur das erste DataSet wird gefüllt |
| `plus` | Zusatz-XML (Aktion, Tooltip, Sortierung, Lesezeichen) in eine Textbox einsetzen | A |

## Tabellen

| Funktion | Wofür | Stand |
|---|---|---|
| `tablix` | Tabelle mit Kopf-, Daten- und Fußzeilen; `group`, `sort`/`sort_desc` (auch Liste von Paaren), `filter_expr`, `filter_xml`, `gruppen_filter`, `detail`, `keep_together`, `gruppen_umbruch`, `seitenzaehlung_neu`, `gruppen_seitenname`, `gruppen_label`; Zelle als Paar (xml, span) für `ColSpan` | A; Kopf bleibt mit erster Zeile zusammen und wiederholt sich; `keep_together` lässt eine Lücke; `Start`, `End`, `StartAndEnd` am Gruppenband nur kopflos |
| `tablix_gruppen` | Tabelle mit freier Zeilenhierarchie: verschachtelte Gruppen, Kopf und Fuß je Gruppe; `keine_zeilen`, `stil`, `keep_together` | A (verschachtelte Datenregionen, Gruppenvariablen, Filter an Gruppen) |
| `zeile`, `zelle` | fertige Tabellenzeile aus Zellen; Zelle mit `span` über mehrere Spalten | A |
| `kopf_mitglied` | Kopfzeile der Zeilenhierarchie, wiederholt sich auf Folgeseiten | A |
| `fuss_mitglied` | Fußzeile (Summe, Etikett), bleibt mit der Zeile davor zusammen; `versteckt` als Ausdruck | A |
| `gruppe_mitglied` | Zeilengruppe: `ausdruck`, `sortiert`, `gruppen_filter`, `kinder`, `umbruch` (Between, Start, End, StartAndEnd), `seitenzaehlung_neu`, `seitenname`, `label` | A für Between mit Zähler neu je Gruppe; Start am Gruppenband nur kopflos |
| `sortierung` | SortExpressions aus Paaren (Ausdruck, absteigend), mehrere Paare ergeben mehrere Sortierungen | A, auch nach Aggregat der Gruppe |
| `filters`, `topn` | Filter „Ausdruck wahr“ und „nur die n größten“ an Tabelle, Diagramm, Gruppe | A; gleiche Werte am Rand zählen mit: eindeutigen Nachrang einrechnen |
| `filter_j`, `filter_in`, `filter_topn`, `filter_liste` | einzelne Filter und ihre Zusammenfassung; `filter_in` für Mehrfach-Parameter, `filter_topn` mit Zahl oder Ausdruck als n | A (TopN, BottomN, In) |

## Seite, Aktionen, Unterbericht

| Funktion | Wofür | Stand |
|---|---|---|
| `report` | ganzer Report: `pages`, `datasets`, `extra_params`, `code`, `footer_xml`, `labels` (Lesezeichen je Seite), `variablen`, `codemodules`, `classes`, `fliessend`, `fliess_h`, `header_xml`, `header_first`, `header_last`, `footer_first`, `footer_last`, `standardparameter`, `body_breite` | A; `variablen` einmal gerechnet, in Body und Fuß gleich; `codemodules` ohne `System`; Kopf oder Fuß nicht auf erster oder letzter Seite geht; `fliessend` ohne Seiten fester Höhe, Elemente laufen über Seiten |
| `marke` | Sprungziel (Bookmark) und oder Eintrag der Dokumentstruktur (`DocumentMapLabel`) an ein fertiges Element | Label wird im PDF zum Lesezeichen (A); `BookmarkLink` auf ein Bookmark ergibt im PDF keinen Link |
| `aktion` | Hülle `ActionInfo` um eine Aktion (mit `plus` an eine Textbox, mit `image(..., action=...)` an ein Bild) | A |
| `hyperlink` | Link; `https://`, `mailto:`, `file:///` oder Ausdruck | A; Link ohne Schema (`www.…`) wird gestrichen, darum `ValueError` |
| `bookmark_link` | Sprung zu einem Bookmark | im PDF kein Link; im Fenster springt er mit vorherigem Meldungsfenster (F) |
| `drillthrough` | Sprung in einen zweiten Report; `ziel` ohne Endung im selben Ordner, `parameter` als Liste | A als PDF, im Fenster F; Zurück-Knopf erst nach dem Sprung |
| `subreport` | Unterbericht (zweite .rdlc im selben Ordner); `parameter`, `top=None` für die Tabellenzelle, `keine_zeilen`, `rahmen` | A; bekommt die Zeilen des Hauptreports, keine eigene Abfrage; Parameter des Ziels brauchen `<Prompt>`; nicht in Kopf oder Fuß |

## Parameter und Anzeigeprogramm

| Funktion | Wofür | Stand |
|---|---|---|
| `parameter` | Parameter links im Fenster: `werte` (Auswahlliste mit Anzeigetext), `multi`, `nullable`, `allowblank`, `hidden`, `distinct` (Liste aus den Daten), `default` | A; wirft `ValueError` bei Ausdruck als Vorgabe oder Listenwert, bei `DataSetReference`, bei deutschem Datum und bei Integer ohne Vorgabe; `hidden` wird im Fenster ignoriert (F) |
| `render_argumente`, `rendern` | Aufruf des Anzeigeprogramms: `parameter` (dict oder Liste; Mehrfachwerte als Liste, `None` setzt Nothing), `pdf`, `datei_format` (`xlsx`, `docx`), `vollzugriff`, `dpi` | K; `Project_Name=Musterprojekt` ist vorbelegt; Schalter: `pruefstrecke.md` (c) |
| `esc`, `cm`, `save` | XML maskieren, cm-Angabe, Datei schreiben | – |

Nicht im Bausatz, aber im Report möglich: Diagramme und Messanzeigen in `master/viz.py` (`chart`, `radial`, `linear`, `stateind`, `gauge`), Bausteine in `master/bausteine.py` (`kpi`, `kennwert`, `fortschritt`, `karten`, `klick`, `sortierbar`).
