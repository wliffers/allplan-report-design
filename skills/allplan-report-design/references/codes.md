# Strichcode, QR-Code und zweite Datenquelle (CSV)

Beides läuft als VB-Code im `<Code>`-Block des Reports; der Code selbst steht in zwei Dateien der Werkstatt, nicht hier:

| Datei | Funktionen |
|---|---|
| `werkzeug/vb/codes.vb` | `Strichcode128(text)`, `Strichcode39(text)`, `QrPng(text, px)` – liefern ein PNG als `Byte()` |
| `werkzeug/vb/zweite_datenquelle.vb` | `CsvWert(pfad, schluessel, spalte)`, `CsvAnzahl(pfad)` |

Belege: in Allplan 2027 als PDF ausgegeben (A) und mit einem Decoder gelesen (Strichcodes, QR) bzw. die Tabelle mit den Werten verglichen (CSV). Das Report-Fenster ist nicht gemessen.
Die Dateien enthalten Einbau und Grenzen als Kopfkommentar; ab der Zeile `Private Const T39` (codes.vb) bzw. `Private csvZeilen` (zweite_datenquelle.vb) beginnt der Code.

## Strichcode und QR-Code einbauen

1. Code ab `Private Const T39` in den Code-Block setzen. Der Bausatz maskiert das XML selbst:
   ```
   vb = open("werkzeug/vb/codes.vb", encoding="utf-8").read()
   vb = vb[vb.index("Private Const T39"):]
   xml = c.report(pages, datasets, extra_params=b.PARAMS, code=b.CODE + "\n" + vb,
                  codemodules=["System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a"])
   ```
   `System.Drawing` als `CodeModule` ist Pflicht (sonst findet der Code die Zeichenklassen nicht). `System` selbst nie eintragen (BC2000).
2. Ein Bildfeld mit Quelle `Database`, `image/png`, `FitProportional` und dem Ausdruck als Wert:
   ```
   c.image("Etikett_QR", top, left, 3.0, 3.0, '=Code.QrPng(Fields!Nr.Value, 5)')
   c.image("Etikett_128", top, left, 5.0, 1.0, '=Code.Strichcode128(Fields!Nr.Value)')
   c.image("Etikett_39", top, left, 5.0, 1.0, '=Code.Strichcode39(Fields!Nr.Value)')
   ```
   Feste Texte gehen genauso: `=Code.QrPng("BT-0042", 5)`. Je Tabellenzeile geht es (5 bis 6 Zeilen je Probe gemessen); `@10@` (Bauteil-ID) als `Nr` in die Abfrage nehmen.
3. Das Bild ansehen und mit einem Handscanner oder Decoder gegenlesen: ein leeres Bild meldet keinen Fehler.

## Grenzen (gemessen, A)

| Code | Zeichenvorrat | Größe |
|---|---|---|
| Code 128 (Satz B) | ASCII 32 bis 126; andere Zeichen ergeben ein leeres Bild | keine Längengrenze außer der Seitenbreite; 17 Zeichen rund 450 × 50 Pixel (2 Pixel je Modul, 50 Pixel hoch) |
| Code 39 | `0-9 A-Z - .` und Leerzeichen; Kleinbuchstaben werden zu Großbuchstaben, `/ + $ %` liest ein Decoder als Zeichenpaar und liefert ein anderes Zeichen: in IDs meiden | 6 Zeichen 294 × 50 Pixel; Start und Stopp `*` kommen von selbst |
| QR-Code | Byte-Modus (UTF-8), Version 1 bis 5, Fehlerkorrektur L, feste Maske 0 | höchstens 106 Byte (Version 1: 17, 2: 32, 3: 53, 4: 78, 5: 106), länger ergibt ein leeres Bild ohne Fehler; Bild (17 + 4 × Version + 8) × `px` Pixel im Quadrat, bei `px` = 5: 145 bis 225 |

- Bild per Code immer unter 300 × 300 Pixel halten: ein 1600-Pixel-Bild fiel in Allplan zeitlich mit einem Absturz zusammen (`grenzen.md`, Bilder aus Dateien).
- QR-Text über 106 Byte: kürzen (Vorbild `EtikettText`, siehe unten) oder eine Verweis-ID statt Klartext verschlüsseln.
- Code 39 aus Tabellenzellen (fester Text) geht auch, braucht aber 127 Zellen für 6 Zeichen (120 KB); das VB-Bild ist kleiner.
- Zeitbedarf: kopflos rund 1 bis 2 Sekunden mehr bei 3.000 Zeilen mit je 5 Bildern; in Allplan nicht gemessen.
- Nicht geprüft: EAN, Data Matrix, Code 93; QR über Version 5.

## QR-Code mit Klartext (Etiketten)

Ein QR-Code kann statt einer ID auch Text tragen, den ein Telefon beim Scannen anzeigt (Vorbild: B110 Etiketten, `master/listen/build_listen.py`, `CODE_ETIKETT`). Das Etikett zeigt Art und Name, Material, Maße, Menge und Bauteil-ID, je eine Zeile.

- `Code.EtikettText(kopf, zusatz, masse, id, 106)` hält die Grenze von 106 Byte (UTF-8) ein: Es kürzt die Kopfzeile, lässt notfalls das Material (`zusatz`) weg, im äußersten Fall bleibt nur die ID. Ohne diese Kürzung gäbe ein zu langer Text ein leeres Bild ohne Fehlermeldung.
- `Code.Verbinde(a, b, c)` verbindet die nicht leeren Teile mit Komma (die Maße).
- Beide Funktionen stehen im Bausatz des Listen-Reports, nicht in `codes.vb`; der Aufruf: `=Code.QrPng(Code.EtikettText(…, 106), 5)`.
- Umlaute gehen (UTF-8); aus dem Allplan-PDF mit einem Decoder zurückgelesen, auch mit Umlauten und bei genau 106 Byte.
- Der Strichcode braucht Breite: 17 Zeichen sind auf rund 7 cm gut lesbar, auf 5 cm zu fein.
- Gemessen (A): Etikettenblatt an zwei Projekten als PDF ausgegeben, deutsch und englisch, alle 8 QR- und 8 Strichcodes je PDF zurückgelesen; im Report-Fenster sitzt die Seite wie im PDF, und die Stellschrauben für Bauteilart und Anzahl wirken (16 Etiketten auf zwei Seiten). Kopflos zusätzlich 96 Etiketten auf 12 Seiten, alle Codes gelesen.
- Auswahl mit Deckel (`TopN`) braucht einen eindeutigen Rang: gleiche Bauteile in kopierten Teilbildern haben dieselbe Menge und dieselbe Elementnummer, `TopN` nimmt dann alle Gleichen mit (9 statt 8). Vorbild: Rang als Text fester Breite aus Menge, Teilbild und Elementnummer, nach demselben Text sortiert (`etiketten_raster`).

## CSV als zweite Datenquelle

Allplan füllt nur EINE Abfrage (`grenzen.md`); Zusatzdaten wie Preise oder Notizen kommen aus einer CSV-Datei, die der Code liest und je Zeile nachschlägt.

1. Code ab `Private csvZeilen` in den Code-Block setzen (kein `CodeModule` nötig):
   ```
   vb = open("werkzeug/vb/zweite_datenquelle.vb", encoding="utf-8").read()
   vb = vb[vb.index("Private csvZeilen"):]
   xml = c.report(pages, datasets, extra_params=b.PARAMS + pfad_parameter, code=b.CODE + "\n" + vb)
   ```
2. Pfad als Parameter mit fester Vorgabe, **absoluter Pfad**: `pfad_parameter = c.parameter("Zusatz_Datei", "String", r"C:\Daten\zusatz.csv", "CSV-Datei")`.
   Das Arbeitsverzeichnis von Allplan ist der Programmordner `C:\Program Files\Allplan\Allplan 2027`; ein Pfad „neben dem Report“ wird nicht gefunden.
3. In einer Tabellenzelle:
   - `=Code.CsvWert(Parameters!Zusatz_Datei.Value, Fields!Nr.Value, 2)` Spalte 2 (von 0 an gezählt) zur Bauteil-ID `@10@`
   - `=Code.CsvWert(Parameters!Zusatz_Datei.Value, "Z" & RowNumber(Nothing), 2)` Spalte 2 zur Zeilennummer
   - `=Code.CsvAnzahl(Parameters!Zusatz_Datei.Value)` Kontrollzeile: „51 Datenzeilen gelesen“ oder „FEHLER …“
4. Zahlen kommen als Text mit Komma, wie in der Datei: im Report `CDbl(…)` und `Format(x, "N2")` (Kultur de-DE).

Dateiformat (gemessen): UTF-8 mit oder ohne BOM, Trennzeichen Semikolon, erste Zeile Kopf (wird übersprungen), mindestens vier Spalten (`Zeile;Nr;Preis;Notiz`);
Schlüssel ist Spalte 1 (Bauteil-ID) und Spalte 0 mit Vorsatz `Z` (Zeilennummer).

Grenzen:
- Gelesen wird einmal je Reportlauf; der Pfad des ERSTEN Aufrufs gilt für alle.
- Fehlt die Datei oder ist sie gesperrt, steht in jeder Zelle „FEHLER <Ausnahme>: <Text>“; fehlt der Schlüssel, „(kein Treffer)“. Immer die Kontrollzeile `CsvAnzahl` mit ausgeben.
- Die Verbindung hängt am Schlüssel: Bauteil-ID `@10@` ist stabil, die Zeilennummer ändert sich mit der Abfrage.
- **Der Code läuft mit vollen Rechten:** Allplan gibt ihm Zugriff auf Dateien, Ordner, Umgebungsvariablen, Registry (lesen) und zum Schreiben von Dateien (A). Das ist kein Sicherheitsmerkmal des Reports;
  die CSV-Datei ist Teil des Reports und muss bei der Weitergabe mitgehen. Empfehlung (keine Messung): Reports Dritter vor dem Öffnen im Code-Block lesen.
- Kopflos (eingeschränkte Rechte des Renderers) ist der Dateizugriff gesperrt (`SecurityException`): dort den Renderer mit `--fulltrust` starten oder in Allplan prüfen.
- Nicht geprüft: CSV mit anderem Trennzeichen als Semikolon.

