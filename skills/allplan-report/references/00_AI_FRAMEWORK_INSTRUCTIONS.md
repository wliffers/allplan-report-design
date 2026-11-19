# Rahmenanweisung für KI‑Systeme – Allplan Report Knowledge Base

Diese Knowledge Base bündelt das Wissen aus 520 Allplan RDLC‑Reportvorlagen. Sie dient jeder KI als verbindliche Arbeitsgrundlage, um neue Allplan‑Reports zu **erstellen, zu erweitern oder zu korrigieren**.

Allplan‑RDLC‑Dateien sind **kein reines Microsoft‑RDL**. Sie nutzen das Microsoft‑RDL‑Schema als Container, transportieren darin aber eine **Allplan‑eigene Abfrage‑ und Attribut‑Syntax** (FROM‑Tabellen wie `[MODEL_DATA]`, Platzhalter `@XXX@`, Filter‑Sprache mit `.eq. .and. ELE(…)`). Ohne dieses Wissen lassen sich Reports weder lesen noch neu schreiben.

**Pfad‑Platzhalter** in allen Dateien: `<SKILL>` ist der Ordner des Skills `allplan-report` (mit `scripts/` und `references/`); `<RDLC>` ist die Vorlagenbibliothek der Allplan-2027-Installation `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports` (nur lesen; die Umgebungsvariable `ALLPLAN_REPORTS` geht vor). Dieses Repo liefert keine Allplan-Vorlagen mit. Den Katalog der Vorbilder (`rdlc-index.json`) einmal selbst erzeugen: `python scripts/build_report_index.py`.

## 1. Aufbau der Knowledge Base

| Datei | Inhalt / Zweck |
|-------|----------------|
| `00_AI_FRAMEWORK_INSTRUCTIONS.md` | Diese Rahmenanweisung – immer zuerst lesen |
| `01_Dateiuebersicht_und_Kategorien.md` | Alle 520 Vorlagen gruppiert nach Thema, Sprache, Normen |
| `02_RDLC_Grundstruktur.md` | XML‑Grundgerüst, RDL 2005 vs 2016, DataSource, DataSet, Body |
| `03_Standardparameter_und_Layout.md` | 12 Pflicht‑Parameter, Header‑/Footer‑Aufbau, A4/A3, Ränder |
| `04_Allplan_Query_Syntax.md` | `SELECT @XXX@[…] FROM [Tabelle,Filter=…]`, alle FROM‑Tabellen, Filter‑Sprache |
| `05_Attribute_Referenz.md` | Referenz der wichtigsten `@XXX@`‑IDs (Objekte, Geometrie, Bewehrung, Räume, Projekt) |
| `06_Expressions_und_Aggregate.md` | RDL‑Ausdrücke (`=Sum`, `=IIF`, `=Switch`), Parameter‑Bindung, Einheiten |
| `07_Gruppierung_und_Tabellen.md` | Table/Tablix, ein‑ und mehrstufige `TableGroups`, Matrix, Sort‑Expressions |
| `08_Grafiken_und_Bilder.md` | `@205@`, Projektionen, Bewehrungs‑Biegeformen, `@87@` SVG‑Map, Logo |
| `09_Muster_Bauteile_Abbruch_Neubau.md` | Wände, Decken, Stützen, Fenster, Türen – inkl. `@49@` Abbruch/Neubau |
| `10_Muster_Bewehrung.md` | Stabliste, Mattenliste, Länderstandards (ISO/BS/SANS/CH), FF‑ und MSA‑Körbe |
| `11_Muster_Flaechen_Raeume.md` | Wohnflächen WoFlV, DIN277, Raumbuch, BGF/BRI, Ausbauflächen |
| `12_Muster_Spezial_Kanal_Schalung_Einbauteile.md` | Schalung (`CASING_AREA`), Kanal (Pipework_Macro), Baugrube, PythonPart‑UUIDs |
| `13_Anleitung_Neuer_Report.md` | Schritt‑für‑Schritt‑Vorgehen beim Erstellen einer neuen Vorlage |
| `14_Qualitaet_und_typische_Fehler.md` | Prüfcheckliste, häufigste Fehler, Verifikation |
| `15_Referenz_Beispiele.md` | 10 reale, zusammengefasste Report‑Snippets als Copy‑and‑Adapt‑Vorlagen |

## 2. Wo steht welches Wissen?

| Suchst du… | → Dann lies… |
|------------|--------------|
| Technisches XML‑Grundgerüst / RDL‑Version | `02_RDLC_Grundstruktur.md` |
| Welche Parameter müssen rein? | `03_Standardparameter_und_Layout.md` |
| Wie lautet der SQL‑Ausdruck für „alle Wände"? | `04_Allplan_Query_Syntax.md` + `09_Muster_Bauteile_Abbruch_Neubau.md` |
| Was bedeutet `@507@` oder `@205@`? | `05_Attribute_Referenz.md` |
| Wie summiere ich eine Spalte? | `06_Expressions_und_Aggregate.md` |
| Wie gruppiere ich nach Geschoss + Material? | `07_Gruppierung_und_Tabellen.md` |
| Wie zeige ich eine 3D‑Vorschau? | `08_Grafiken_und_Bilder.md` |
| Wie baue ich einen Abbruchreport? | `09_Muster_Bauteile_Abbruch_Neubau.md` |
| Wie baue ich eine Biegeliste? | `10_Muster_Bewehrung.md` |
| Wie rechne ich Wohnfläche? | `11_Muster_Flaechen_Raeume.md` |
| Wie baue ich einen Schalungs‑ oder Kanalreport? | `12_Muster_Spezial_Kanal_Schalung_Einbauteile.md` |
| Wie fange ich konkret an? | `13_Anleitung_Neuer_Report.md` |
| Woran erkenne ich einen Fehler? | `14_Qualitaet_und_typische_Fehler.md` |
| Wie sieht ein echtes Beispiel aus? | `15_Referenz_Beispiele.md` |

## 3. Pflichtvorgehen bei neuen Reports (Kurzfassung)

Die KI folgt **immer** diesen Schritten – detailliert in `13_Anleitung_Neuer_Report.md`:

1. **Zielklärung**: Welche Allplan‑Objekte (Wand? Raum? Bewehrungsstab? Schacht?) sollen ausgewertet werden? Welche Spalten? Welche Gruppierung? Welches Blattformat?
2. **Referenzvorlage suchen**: Die passende bestehende Vorlage aus `01_Dateiuebersicht_und_Kategorien.md` identifizieren. **Nie von Null starten** – immer auf einer existierenden Vorlage aufsetzen.
3. **FROM‑Klausel planen**: Aus `04_Allplan_Query_Syntax.md` die korrekte Tabelle (`[MODEL_DATA]`, `[ENGINEERING]`, `[Type=0]`, `[FLOOR_AREA_ARCHITECTURE]`, `[CASING_AREA]` etc.) plus passenden `Filter=@OBJ@.eq.…` bestimmen.
4. **Spalten zusammenstellen**: `@XXX@[Name=...|Fmt=…|Dim=…|Projection=…]` laut `05_Attribute_Referenz.md` und den Muster‑Dateien.
5. **Template wählen**: `Template_empty_2005.rdlc` oder `Template_Grouping0/1/2_2005.rdlc` je nach gewünschter Gruppentiefe. 2005‑Variante nutzen, solange keine Tablix‑Features zwingend nötig sind.
6. **Standardparameter übernehmen** (Abschnitt `ReportParameters` unverändert einbauen).
7. **Query einsetzen** (nur `CommandText` ändern, `DataSourceName="DummyDataSource"` lassen).
8. **Body/Table aufbauen** nach `07_Gruppierung_und_Tabellen.md`, Felder an `Fields!<Name>.Value` binden.
9. **Summen/Expressions** gemäß `06_Expressions_und_Aggregate.md` einfügen.
10. **Qualitätsprüfung** gemäß `14_Qualitaet_und_typische_Fehler.md`.

## 4. Wie prüft eine KI einen vorhandenen Report?

1. XML‑Wohlgeformtheit (Parser darf nicht abbrechen).
2. `<DataProvider>ALLPLAN</DataProvider>` vorhanden?
3. Genau **ein** `<DataSet Name="AllplanReport">` mit gültiger FROM‑Klausel?
4. Jedes `Fields!<Name>.Value` im Body hat ein korrespondierendes `<Field>` im DataSet, das exakt denselben `Name=` aus der Query trägt?
5. Alle in Expressions referenzierten Parameter sind unter `<ReportParameters>` deklariert?
6. Page‑Header/Footer und Margins matchen das Zielpapierformat (A4=21×29.7 cm, A3=29.7×42 cm)?
7. Gruppierungs‑Expressions referenzieren vorhandene Feldnamen, nicht freie Strings?
8. Sum‑/Count‑Aggregate stehen **ausserhalb** der Detail‑Row oder in einem Footer‑Group‑Scope?

## 5. Typische Fehler, die eine KI unbedingt vermeiden muss

Ausführlich in `14_Qualitaet_und_typische_Fehler.md`. Die sieben häufigsten:

1. **Tippfehler in `@XXX@`‑IDs** – jede falsche Zahl produziert leere Spalten, ohne Fehlermeldung.
2. **Falsche FROM‑Klausel** – z. B. `[Type=0]` ohne `Filter=@OBJ@.eq.…` liefert *alle* Modellobjekte, nicht nur Wände.
3. **Feldname in Query ≠ Feldname in `<Fields>`‑Block** – das DataSet kennt das Feld, der Body findet es nicht.
4. **Verwechslung `@231@` Region vs `@232@` AreaType** bei DIN277‑Reports – produziert falsche BGF/BRI.
5. **Abbruch‑Report ohne `@49@.eq.2`** – zeigt auch Neubauteile.
6. **Falsche Schema‑Version** – `<Tablix>` in einer RDL‑2005‑Datei (Namespace `…/2005/01/reportdefinition`) → ungültig. 2005 kennt nur `<Table>`/`<Matrix>`.
7. **Margins + Page‑Width nicht konsistent** – `LeftMargin=2cm + Width=18cm + RightMargin=1cm` muss zusammen die `PageWidth=21cm` ergeben.

## 6. Nicht‑Veränderungsregeln

- **Sprache**: Deutsche und englische Varianten existieren parallel (z. B. `Wände.rdlc` / `Walls.rdlc`). Beide müssen synchron bleiben, wenn der Inhalt identisch ist. Dateiname ≠ Titel – der Titel steht im `Heading1`‑Textbox des PageHeaders.
- **Author‑Feld**: `<Author>Allplan GmbH</Author>` für offizielle Reports. `Allplan Schweiz AG` nur bei CH‑spezifischen.
- **Standardparameter**: Die Standard‑Parameter der Ausgangsvorlage werden **nie umbenannt oder entfernt**. Neue Parameter werden nur ergänzt. (Genauer Bestand: `03_Standardparameter_und_Layout.md`.)
- **DataSource**: `DummyDataSource` mit DataProvider `ALLPLAN` – Konvention für neue Reports. Im 2027‑Bestand weichen 26 Vorlagen beim Namen und 6 bei der `rd:DataSourceID` ab; das Prüfskript meldet das als Warnung, nicht als Fehler.

## 7. Ausgangsverzeichnis

Stand Allplan 2027 (Abgleich 2026-09-29): Die Quellvorlagen sind die Allplan‑2027‑Bibliothek `<RDLC>` (unveränderte Kopie von `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports`) mit **551** Vorlagen im Baum `deu/<Kategorie>/…`, `eng/<Category>/…` und den acht `Template_*.rdlc` an der Wurzel. Die Zahl „520" in dieser Knowledge Base bezieht sich auf den älteren flachen Bestand; die Aussagen gelten weiter, die Zählungen sind Näherungen.

Die Knowledge Base ersetzt dieses Verzeichnis nicht – sie abstrahiert es. Wenn eine KI ein Detail braucht, das hier nicht dokumentiert ist, liest sie die passende Referenzvorlage direkt; welche passt, zeigt der Katalog `<SKILL>/rdlc-index.json`.

**Schema-Erkennung:** Die RDL-Version steht im Namespace des Wurzelelements `<Report xmlns=…>`, nicht im Dateinamen. Im Bestand kommen drei vor: 2005 (`<Table>`/`<Matrix>`), 2010 und 2016 (beide `<Tablix>`). Nur die acht Templates tragen das Suffix `_2005`.

## 8. Werkzeuge (`<SKILL>` = Ordner des Skills `allplan-report`)

| Zweck | Befehl |
|-------|--------|
| Attribut-ID nachschlagen (Name, Datentyp, `rd:TypeName`, Einheit) | `python <SKILL>/scripts/lookup_attribute.py 220 --suche Volumen` |
| Report prüfen (Report-Gate R1, Kennungen siehe `14`, §3) | `python <SKILL>/scripts/validate_rdlc.py <datei oder ordner>` |
| Katalog der Vorlagen neu erzeugen | `python <SKILL>/scripts/build_report_index.py` |

Der Attributkatalog von Allplan 2027 (`Etc\Xml\*AttributeDefinitionCollection*.xml`) enthält jede ID, die im Vorlagenbestand vorkommt. Er ist die Quelle der Wahrheit für IDs – vor den Tabellen in `05_Attribute_Referenz.md`.
