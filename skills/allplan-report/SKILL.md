---
name: allplan-report
description: >
  Allplan-2027-RDLC-Reportvorlagen (.rdlc) erstellen, aendern, uebersetzen,
  pruefen und nachschlagen - Microsoft-RDL-XML mit Allplan-Query
  (@id@[Name=...] FROM [MODEL_DATA, Filter=...]). Auto-activate bei
  "Allplan Report", "RDLC", "Reportvorlage", "Stueckliste", "Mengenliste",
  "Auswertung", "Report-Designer", "Attribut-ID", "@OBJ@", "CommandText".
  English: create, edit, translate, review or validate an Allplan RDLC report
  template or bill of materials, look up an Allplan attribute id or query
  filter. Nicht fuer PythonPart-Code (.py/.pyp).
---

# Allplan-RDLC-Reports

Eine `.rdlc` ist Microsoft-RDL-XML, dessen `<CommandText>` keine SQL-Abfrage
enthaelt, sondern Allplans eigene Query-Sprache. Attribut-IDs, FROM-Tabellen
und Filterwerte stehen in keinem Trainingsmaterial: **jede ID und jedes
Konstrukt wird belegt**, am Attributkatalog oder an einer Vorlage der Bibliothek.

## Platzhalter

- `<SKILL>` = der Ordner dieser `SKILL.md`, z. B. `.claude/skills/allplan-report`,
  `.github/skills/allplan-report` oder `.agents/skills/allplan-report`.
- `<RDLC>` = die Vorlagenbibliothek der Allplan-2027-Installation
  (`C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports`, nur lesen). Die Umgebungsvariable
  `ALLPLAN_REPORTS` geht vor. Dieses Repo liefert keine Allplan-Vorlagen mit.

Projektregeln (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`) haben Vorrang.

## Quellen

| Was | Wo |
|---|---|
| Fachwissen (Deutsch, 00-15) | `<SKILL>/references/` |
| Vorbilder: 551 Vorlagen | `<RDLC>/deu/<Kategorie>/`, `<RDLC>/eng/<Category>/`, `<RDLC>/Template_*.rdlc` |
| Katalog aller Vorbilder (Felder, Filter, Query; Pfade relativ zu `<RDLC>`) | `<SKILL>/rdlc-index.json` (einmal selbst erzeugen: `python scripts/build_report_index.py`) |
| Attribut-ID nachschlagen | `python "<SKILL>/scripts/lookup_attribute.py" 220 507 --suche Volumen` |
| Pruefen (Datei oder Ordner) | `python "<SKILL>/scripts/validate_rdlc.py" <pfad>` |
| Katalog neu bauen (nach einem Allplan-Update) | `python "<SKILL>/scripts/build_report_index.py"` |
| Ergebnisse | Ordner `out/` im Projekt (bei Bedarf anlegen), sofern die Projektregeln nichts anderes sagen |

Die Skripte brauchen nur Python 3.10+ ohne Zusatzpakete; Allplans eigenes Python
(`C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe`) genuegt.
`<RDLC>` wird nie geaendert.

## Zuerst

1. `<SKILL>/references/00_AI_FRAMEWORK_INSTRUCTIONS.md` und
   `14_Qualitaet_und_typische_Fehler.md` lesen.
2. Die Anfrage einem Modus zuordnen: **create**, **modify**, **translate**, **review**, **lookup**.
   Ist er nicht eindeutig, eine Frage stellen.
3. Weitere Referenzen nur nach Bedarf (Themenkarte in `00`, Abschnitt 2).

## create

1. Klaeren, bevor XML entsteht: Zielobjekt (`@OBJ@`), Status (`@49@`), Gewerk (`@GW@`),
   Spalten, Gruppierung, Vorschaubild, Blattformat, Laenderstandard, Summen, Sprachen.
   Eindeutiges annehmen und nennen, Entscheidungen des Nutzers erfragen.
2. Vorbild finden: im Katalog nach `ObjectFilters`, `Category`, `FieldNames` filtern,
   1-3 Kandidaten nennen, das beste **ganz** lesen.
3. Basis kopieren: das Vorbild oder `<RDLC>/Template_Grouping0|1|2_2005.rdlc`.
   RDL 2005 (`<Table>`) ist die Vorgabe; Tablix nur, wenn das Vorbild es hat.
4. Frische GUID in `<rd:ReportID>` je Datei (die Bibliothek teilt eine einzige GUID).
5. Query bauen: jede ID per `lookup_attribute.py` belegen; `Datatype -> TypeName`
   aus dessen Ausgabe in `<rd:TypeName>` uebernehmen.
6. Konsistenz-Dreieck: Query `[Name=X]` = `<Field Name="X">` = `Fields!X.Value`, case-exakt.
7. Standardparameter des Vorbilds unveraendert lassen, eigene dahinter anhaengen.
8. DE und EN anlegen, wenn nicht anders gewuenscht: gleiche Query und Struktur,
   nur Beschriftungen und `Heading1` uebersetzt.
9. Nach `out/` schreiben, UTF-8 ohne BOM, dann Report-Gate.

## modify und translate

1. Die Datei ganz lesen; bei DE/EN-Paaren beide.
2. Query, `<Fields>` und Body immer gemeinsam aendern.
3. Den Filter-Dialekt der Datei beibehalten (`.eq./.and.` oder alt `@OBJ@=1031&@49@=2`).
4. `DataProvider`, `DummyDataSource`, `rd:DataSourceID` und Standardparameter bleiben, wie sie sind.
5. Ergebnis nach `out/`, ausser der Nutzer verlangt ausdruecklich eine andere Stelle.
   Eine Vorlage in `<RDLC>` wird nie ueberschrieben.

## review

1. `validate_rdlc.py <pfad>` ausfuehren; Befunde ueber ihre Kennung (E01..., W01...)
   in `references/14_Qualitaet_und_typische_Fehler.md`, Abschnitt 3 einordnen.
2. Von Hand: Aggregat-Scope, DE/EN-Gleichheit, Konstrukte ohne Vorbild (Regel unten).
3. Befunde priorisiert melden: Fundstelle (Datei:Zeile), Wirkung, Fix.

## lookup

- Attribut: `lookup_attribute.py` liest den Katalog der Allplan-Installation. Ohne
  Allplan auf dem Rechner gibt es keinen Attributkatalog.
  Kein Treffer = am Vorbild suchen, nicht raten.
- FROM-Tabellen und Filter: `references/04_Allplan_Query_Syntax.md`; reale
  Beispiele: `FromTables` im Katalog.
- Vorlage zu einem Thema: Katalog nach `Category`/`ObjectFilters`, dann `references/01`.

## Regeln

- **Vorbild vor Konstrukt.** Jedes RDL-Element und jede Query-Funktion, die neu in
  eine Datei kommt, hat einen Treffer in `<RDLC>` (Textsuche nach dem Konstrukt).
  Ohne Vorbild bleibt der Report im Report-Manager weiss.
- `Dim=` nur dort, wo das Vorbild es setzt; viele Attribute liefern schon m bzw. m³.
- Geschosse nach `StoryIndex` sortieren, `Story` nur anzeigen.
- Summen in Gruppen- oder Tabellenfuss, nicht in der Detailzeile.
- Body-Breite = Seitenbreite minus Raender (A4 hoch: 21 - 2 - 1 = 18 cm).
- Kein `JOIN`, `ORDER BY`, `TOP`, `LIKE` in der FROM-Klausel - gibt es in Allplan nicht.

## Report-Gate (vor jeder Uebergabe)

- **Stufe R1:** `python "<SKILL>/scripts/validate_rdlc.py" out/<Datei>`.
  Die letzte Zeile (`AMPEL: ...`) wird woertlich weitergegeben. Fertig heisst:
  0 Fehler; jede Warnung ist erklaert oder behoben.
- **Stufe R2:** Sichtpruefung in Allplan 2027 durch den Nutzer - Datei in den
  Bueroordner `<Datenpfad>\Std\Reports\deu\<Kategorie>\` kopieren (Standard:
  `C:\allplandaten\2027\Std\...`), Report oeffnen, Zeilenzahl und Summen am Modell
  pruefen. Bis zur Rueckmeldung ist R2 **GRAU** (nicht geprueft).

## Helfer

Suche nach Vorbildern und Pruefung macht die KI mit den Schritten oben selbst.

## Uebergabe

Hoechstens 30 Zeilen: Datei(en) in `out/`, Vorbild, FROM mit Filter, Gruppierung,
Papierformat, getroffene Annahmen, Ampel-Zeile von R1, was fuer R2 zu pruefen ist.
