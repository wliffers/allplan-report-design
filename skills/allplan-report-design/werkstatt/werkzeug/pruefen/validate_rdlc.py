"""Statische Pruefung von Allplan-RDLC-Reportvorlagen (Report-Gate, Stufe R1).

Aufruf (Pfad des Skripts: scripts/ im Skill- bzw. Projektordner):
    python scripts/validate_rdlc.py <datei|ordner> [...]
        [--no-recursive] [--bibliothek] [--bom-error] [--strict]
        [--json [DATEI]] [--quiet]

Ordner werden rekursiv durchsucht. ``--bibliothek`` prueft einen Bestand wie
die Allplan-Etc-Bibliothek nur auf Struktur und laesst die Konventionen fuer
eigene Reports weg (Standardparameter, eigene ReportID, BOM, ...).

Kalibriert an den 551 Vorlagen von Allplan 2027: was dort vorkommt und laeuft,
ist hoechstens eine Warnung. Fehler sind nur Befunde, an denen ein Report
sicher scheitert.

Kennungen (Bedeutung und Fix: 14_Qualitaet_und_typische_Fehler.md, Abschnitt 3):
    E01 XML nicht wohlgeformt            W01 UTF-8-BOM
    E02 Namespace unbekannt              W02 DummyDataSource fehlt
    E03 Schema-Mix Table/Tablix          W03 rd:DataSourceID nicht Standard
    E04 kein DataProvider ALLPLAN        W04 kein DataSet 'AllplanReport*'
    E05 kein DataSet mit CommandText     W05 Standardparameter fehlen
    E06 Fields!X nicht deklariert        W06 Breite nicht pruefbar
    E07 SQL-Wort in der FROM-Klausel     W07 Body breiter als Seite
    E08 Encoding UTF-16/unlesbar         W08 Tabelle breiter als Body
    E09 Vorgabe=Ausdruck (Int/Float/Datum) W09 RepeatOnNewPage=true fehlt (nur bei Kopfzeile)
    E10 DataSetReference in Parameter    W10 Aggregat ohne Scope in Detailzeile
    E11 Ausdruck in ValidValues          W11 @205@/@87@ mit falschem Datentyp
    E12 DateTime-Vorgabe nicht ISO       W12 rd:ReportID fehlt
    E13 Integer/Float ohne Vorgabe       W13 ReportID = Allplan-Standard-GUID
    E14 RowSpan>1 im Tabellenkoerper     W14 ReportID doppelt im Pruefsatz
    E15 Unterbericht/Tabelle in Kopf/Fuss W15 Sortierung nach Story statt StoryIndex
    E16 konstante Division durch 0       W16 Query-Feld ohne <Field>
                                         W17 Parameters!X nicht deklariert
                                         W18 String-Vorgabe als Ausdruck
                                         W19 Hyperlink ohne Schema
                                         W20 mehr als eine ReportSection
                                         W21 RepeatWith
                                         W22 Filter Like mit %
                                         W23 Unterbericht (Hinweis)
                                         W24 Unterbericht: Felder fehlen im Hauptreport
                                         W25 Unterbericht: Parameter ohne Prompt
                                         W26 BookmarkLink auf Bookmark
                                         W27 BreakLocation End + Start (leere Seite)
                                         W28 Geschwister-Elemente ueberlappen sich (Report-Fenster)

Exit-Codes: 0 kein Fehler (mit --strict auch keine Warnung), 1 Fehler,
2 Pfad fehlt oder keine .rdlc gefunden. Letzte Zeile ist immer die Ampel.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rdlc_common as rc  # noqa: E402

# Konventionen fuer eigene Reports - im Bibliotheksmodus unterdrueckt.
CONVENTION_CODES = {"W01", "W02", "W03", "W04", "W05", "W09", "W10", "W12", "W13", "W14", "W15"}
TOLERANCE_CM = 0.01
AGGREGATE_RE = re.compile(r"(?<![\w.])(Sum|Count|Avg|Min|Max|CountDistinct)\s*\(")
SQL_WORD_RE = re.compile(r"\b(JOIN|ORDER\s+BY|TOP|LIKE)\b")
# Seitenkopf/-fuss: Unterberichte und Datenregionen sind dort ungueltig.
DATA_REGIONS = ("Subreport", "Tablix", "Table", "Matrix", "List", "Chart")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
# Allplan nimmt DateTime-Vorgaben in ISO-Schreibweise und US-Schreibweise (gemessen); '19.11.2026' nicht.
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$")
US_DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}( \d{1,2}:\d{2}(:\d{2})?( ?[AaPp][Mm])?)?$")
ALLPLAN_PROMPT_RE = re.compile(r"@\w+@")
# Ueberlappung: Schnitt unter OVERLAP_TOLERANCE_CM zaehlt nicht (Beruehrung, Rundungsreste bis 0,005 cm);
# gemessen verschiebt das Report-Fenster schon bei 0,02 cm.
OVERLAP_TOLERANCE_CM = 0.01
OVERLAP_MAX_FINDINGS = 15
STRIPE_MAX_CM = 0.05   # kleineres Schnittmass bis hierher heisst "Streifen"
# Allplans eigene Standard-Elemente in PageHeader/PageFooter, abgeleitet aus den Startvorlagen
# Template_Grouping0/1/2(_2005) und Template_empty(_2005) von Allplan 2027. Paare, bei denen BEIDE Elemente
# in dieser Liste stehen, melden kein W28: In den ausgelieferten Vorlagen vorhanden und laeuft (z. B.
# Footer1/Footer2 um 0,05 cm, in 503 von 551 Etc-Vorlagen); die Verschiebung hat dort keine sichtbare Wirkung.
# Ein fremdes Element, das ein Standard-Element schneidet, meldet weiter.
STANDARD_PAGE_ELEMENTS = {
    "PageHeader": frozenset({"Heading1", "Line1", "Line2", "Text1", "Text2", "Text3", "Text4", "Project", "Created",
                             "Date", "Note", "LogoPlaceholder", "Logo"}),
    "PageFooter": frozenset({"PageNumber", "Line6", "Footer1", "Footer2", "Footer3"}),
}
# Zahl / Null-Konstante, Operatoren ohne Leerraum (siehe constant_zero_divisions).
CONST_ZERO_DIV_RE = re.compile(r"(?<![\w.!)\]*/\\^])\d+(?:\.\d+)?[/\\]0+(?:\.0*)?(?![\w.])")


@dataclass
class Finding:
    code: str
    message: str
    line: int | None = None

    @property
    def severity(self) -> str:
        return "ERROR" if self.code.startswith("E") else "WARN"

    def render(self) -> str:
        where = f" (Zeile {self.line})" if self.line else ""
        return f"  {self.severity:<5} {self.code}: {self.message}{where}"


@dataclass
class FileResult:
    path: str
    namespace_year: str = "unbekannt"
    encoding: str = ""
    has_tablix: bool = False
    has_table: bool = False
    report_id: str = ""
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)   # Hinweise ohne Kennung: zaehlen nicht in der Ampel

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "ERROR"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "WARN"]

    @property
    def status(self) -> str:
        return "ERROR" if self.errors else "WARN" if self.warnings else "OK"


# --------------------------------------------------------------- Einzelchecks
def unscoped_aggregates(expression: str) -> list[str]:
    """Aggregataufrufe ohne Scope-Argument (ein Argument = Scope der Zeile)."""
    found = []
    for match in AGGREGATE_RE.finditer(expression):
        depth, index, top_level_comma, in_string = 1, match.end(), False, False
        while index < len(expression) and depth:
            char = expression[index]
            if char == '"':
                in_string = not in_string
            elif not in_string:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                elif char == "," and depth == 1:
                    top_level_comma = True
            index += 1
        if not top_level_comma:
            found.append(match.group(1))
    return found


def sql_words_in_from(command_text: str) -> list[str]:
    words = []
    for clause in rc.FROM_RE.findall(command_text):
        unquoted = re.sub(r'"[^"]*"', '""', clause)
        words += [re.sub(r"\s+", " ", word) for word in SQL_WORD_RE.findall(unquoted)]
    return words


def has_header_row(doc: rc.Rdlc) -> bool:
    """Gibt es eine Tabelle mit Kopfzeile? (2005: <Header>; Tablix: statisches Blatt vor einer Gruppe.)"""
    if doc.root is None:
        return False
    if any(rc.kid(table, "Header") is not None for table in rc.descendants(doc.root, "Table")):
        return True
    for tablix in rc.descendants(doc.root, "Tablix"):
        hierarchy = rc.walk(tablix, "TablixRowHierarchy")
        for members in rc.descendants(hierarchy, "TablixMembers") if hierarchy is not None else []:
            seen_static_leaf = False
            for member in rc.kids(members, "TablixMember"):
                has_group = bool(rc.descendants(member, "Group"))
                if has_group and seen_static_leaf:
                    return True
                if not has_group and rc.kid(member, "TablixMembers") is None:
                    seen_static_leaf = True
    return False


def constant_zero_divisions(expression: str) -> list[str]:
    """Division einer Zahl durch eine Null-Konstante ('1/0', '5 \\ 0'): bricht beim Uebersetzen ab."""
    text = re.sub(r'"(?:[^"]|"")*"', '""', expression)
    text = re.sub(r"\s*([/\\*^+\-&(),])\s*", r"\1", text)
    return [match.group(0) for match in CONST_ZERO_DIV_RE.finditer(text)]


@lru_cache(maxsize=None)
def _subreport_names_in(directory: Path) -> frozenset[str]:
    """Namen (ohne Pfad und Endung, klein), auf die <ReportName> der .rdlc-Dateien in 'directory' zeigt."""
    names: set[str] = set()
    for path in directory.glob("*.rdlc"):
        try:
            text = path.read_bytes().decode("utf-8-sig", errors="replace")
        except OSError:
            continue
        for value in re.findall(r"<ReportName>([^<]*)</ReportName>", text):
            # Ausdruecke (=IIF(..., "Sub\A", "Sub\B")): die Textliterale zaehlen
            for name in re.findall(r'"([^"]*)"', value) if value.startswith("=") else [value]:
                stem = name.replace("\\", "/").rsplit("/", 1)[-1]
                names.add(re.sub(r"\.rdlc$", "", stem, flags=re.IGNORECASE).strip().lower())
    return frozenset(names)


def is_subreport_target(path: Path) -> bool:
    """Wird die Datei von einem Unterbericht im selben oder uebergeordneten Ordner aufgerufen?

    Dort gibt der Hauptreport die Parameter vor (Etc: Sub/MattenQuerschnitte.rdlc, PrimaryKey).
    """
    folder = path.resolve().parent
    return folder.name.lower() == "sub" or path.stem.lower() in _subreport_names_in(folder) | _subreport_names_in(folder.parent)


def _default_values(parameter: ET.Element) -> list[str]:
    values = rc.walk(parameter, "DefaultValue", "Values")
    return [rc.text_of(node) for node in rc.kids(values, "Value")] if values is not None else []


def _valid_value_texts(parameter: ET.Element) -> list[str]:
    block = rc.walk(parameter, "ValidValues", "ParameterValues")
    if block is None:
        return []
    return [rc.text_of(rc.kid(item, "Value")) for item in rc.kids(block, "ParameterValue")]


def _check_parameters(doc: rc.Rdlc, result: FileResult) -> None:
    """Parameter-Vorgaben und -Listen: was Allplan bei der Ausgabe nicht annimmt (Messung 2026-11-19)."""
    add = result.findings.append
    block = rc.kid(doc.root, "ReportParameters")
    target = is_subreport_target(doc.path)
    for parameter in rc.kids(block, "ReportParameter") if block is not None else []:
        name = parameter.get("Name", "")
        data_type = rc.text_of(rc.kid(parameter, "DataType"))
        defaults = _default_values(parameter)
        where = rc.line_of(doc.text, f'Name="{name}"')

        for container in ("DefaultValue", "ValidValues"):
            if rc.kid(rc.kid(parameter, container), "DataSetReference") is not None:
                add(Finding("E10", f"Parameter '{name}': DataSetReference in {container} - Allplan meldet 'Parameter nicht "
                                   f"angegeben', keine Datei. Abhilfe: feste Liste oder <Prompt>Distinct(Fields!X.Value)</Prompt>",
                            where))

        for value in _valid_value_texts(parameter):
            if value.startswith("="):
                add(Finding("E11", f"Parameter '{name}': Ausdruck in ValidValues/ParameterValue/Value - Allplan meldet "
                                   f"'Parameter nicht angegeben', keine Datei. Abhilfe: feste Werte, abhaengige Liste als "
                                   f"Kombi-Liste mit Split", where))
                break

        expressions = [value for value in defaults if value.startswith("=")]
        if expressions and data_type in ("Integer", "Float", "DateTime"):
            add(Finding("E09", f"Parameter '{name}' ({data_type}): Vorgabe ist ein Ausdruck - Allplan wertet ihn nicht aus, "
                               f"Typfehler, keine Datei. Abhilfe: feste Vorgabe; Datum per Prompt @401@ oder als "
                               f"String-Parameter mit CDate", where))
        elif expressions and data_type == "String":
            add(Finding("W18", f"Parameter '{name}' (String): Vorgabe ist ein Ausdruck - in Allplan bleibt der Wert leer. "
                               f"Abhilfe: feste Vorgabe", where))

        if data_type == "DateTime":
            for value in defaults:
                if value and not value.startswith("=") and not ISO_DATE_RE.match(value) and not US_DATE_RE.match(value):
                    add(Finding("E12", f"Parameter '{name}': DateTime-Vorgabe '{value}' nicht in ISO-Schreibweise - "
                                       f"Allplan: Definition ungueltig, keine Datei. Abhilfe: 2026-11-19", where))
                    break

        if data_type in ("Integer", "Float") and not any(defaults):
            nullable = rc.text_of(rc.kid(parameter, "Nullable")).lower() == "true"
            filled_by_allplan = bool(ALLPLAN_PROMPT_RE.search(rc.text_of(rc.kid(parameter, "Prompt"))))
            if not nullable and not filled_by_allplan and not target and rc.kid(parameter, "DefaultValue") is None:
                add(Finding("E13", f"Parameter '{name}' ({data_type}): ohne Vorgabe und ohne Nullable - Allplan meldet "
                                   f"Typfehler, keine Datei. Abhilfe: feste Vorgabe oder <Nullable>true</Nullable>", where))


def _top_cm(item: ET.Element) -> float:
    return rc.parse_length_cm(rc.text_of(rc.kid(item, "Top"))) or 0.0


def _check_items(doc: rc.Rdlc, result: FileResult) -> None:
    """Berichtselemente: Seitenkopf/-fuss, Zellen, Unterberichte, Links, Umbrueche, Filter."""
    add = result.findings.append
    root = doc.root

    sections = rc.kids(rc.kid(root, "ReportSections"), "ReportSection") if rc.kid(root, "ReportSections") is not None else []
    if len(sections) > 1:
        add(Finding("W20", f"{len(sections)} <ReportSection> - Allplan gibt allen Seiten die Groesse der ersten Sektion, "
                           f"breitere Sektionen laufen ueber. Abhilfe: je Seitengroesse ein eigener Report"))

    for edge in ("PageHeader", "PageFooter"):
        for holder in rc.descendants(root, edge):
            bad = sorted({rc.local(node.tag) for name in DATA_REGIONS for node in rc.descendants(holder, name)})
            if bad:
                add(Finding("E15", f"{', '.join(bad)} in {edge} - Allplan: Dokument ungueltig, keine Datei. "
                                   f"Abhilfe: Unterbericht und Tabellen in den Body, im Kopf nur Textboxen/Bilder",
                            rc.line_of(doc.text, f"<{bad[0]}")))
                break

    for expression in doc.expressions():
        found = constant_zero_divisions(expression)
        if found:
            add(Finding("E16", f"Konstante Division durch 0 ('{found[0]}') - Allplan bricht den ganzen Report beim "
                               f"Uebersetzen ab. Abhilfe: Nenner aus Feld oder Variable", rc.line_of(doc.text, expression[:40])))
            break

    for node in rc.descendants(root, "RepeatWith"):
        add(Finding("W21", "<RepeatWith> ist in Allplan wirkungslos - das Element erscheint nur auf Seite 1. "
                           "Abhilfe: RepeatOnNewPage an der Kopfzeile oder PageHeader", rc.line_of(doc.text, "<RepeatWith")))
        break

    for tablix in rc.descendants(root, "Tablix"):
        for cell in rc.descendants(rc.walk(tablix, "TablixBody") or ET.Element("x"), "TablixCell"):
            span = rc.text_of(rc.walk(cell, "CellContents", "RowSpan"))
            if span.isdigit() and int(span) > 1:
                add(Finding("E14", f"RowSpan {span} in einer Zelle des Tabellenkoerpers (Tablix '{tablix.get('Name', '')}') - "
                                   f"Allplan: 'The TablixCell can only span one row', keine Datei. Abhilfe: senkrecht "
                                   f"verbinden mit dem TablixHeader der aeusseren Gruppe; RowSpan nur in der Matrix-Ecke",
                            rc.line_of(doc.text, "<RowSpan")))
                break
        else:
            continue
        break

    for node in rc.descendants(root, "Hyperlink"):
        target = rc.text_of(node)
        if target and not target.startswith("=") and not URL_SCHEME_RE.match(target):
            add(Finding("W19", f"<Hyperlink> '{target[:40]}' ohne Schema - Allplan setzt keinen Link ins PDF. "
                               f"Abhilfe: https://... oder mailto:...", rc.line_of(doc.text, f"<Hyperlink>{target}")))
            break

    for node in rc.descendants(root, "BookmarkLink"):
        target = rc.text_of(node)
        if not re.search(r"\b(Zoom|Edit):", target, re.IGNORECASE):
            add(Finding("W26", "BookmarkLink auf <Bookmark> - im PDF entsteht kein Sprung. Abhilfe: Lesezeichen "
                               "(DocumentMapLabel) statt Sprungmarke", rc.line_of(doc.text, "<BookmarkLink")))
            break

    for filter_node in rc.descendants(root, "Filter"):
        if rc.text_of(rc.kid(filter_node, "Operator")).lower() != "like":
            continue
        for value in rc.descendants(filter_node, "FilterValue"):
            text = rc.text_of(value)
            literal = re.fullmatch(r'="((?:[^"]|"")*)"', text)
            fixed = literal.group(1) if literal else "" if text.startswith("=") else text
            if "%" in fixed:
                add(Finding("W22", f"Filter Like mit '%' im Vergleichswert '{fixed[:30]}' - der Platzhalter in Allplan ist "
                                   f"'*', '%' trifft nichts. Abhilfe: \"*text*\"", rc.line_of(doc.text, "<Operator>Like")))
                break
        else:
            continue
        break

    _check_page_breaks(doc, result)
    _check_subreports(doc, result)


def _check_page_breaks(doc: rc.Rdlc, result: FileResult) -> None:
    for holder in rc.descendants(doc.root, "ReportItems"):
        items = sorted(rc.kids(holder, "Rectangle") + rc.kids(holder, "Tablix") + rc.kids(holder, "Table")
                       + rc.kids(holder, "Textbox") + rc.kids(holder, "Subreport") + rc.kids(holder, "List")
                       + rc.kids(holder, "Image") + rc.kids(holder, "Chart"), key=_top_cm)
        for first, second in zip(items, items[1:]):
            end = rc.text_of(rc.walk(first, "PageBreak", "BreakLocation"))
            start = rc.text_of(rc.walk(second, "PageBreak", "BreakLocation"))
            if end in ("End", "StartAndEnd") and start in ("Start", "StartAndEnd"):
                result.findings.append(Finding(
                    "W27", f"BreakLocation End an '{first.get('Name', '')}' und Start am folgenden '{second.get('Name', '')}' - "
                           f"dazwischen entsteht eine LEERE Seite. Abhilfe: nur eines von beiden setzen",
                    rc.line_of(doc.text, f'Name="{first.get("Name", "")}"')))
                return


def _check_subreports(doc: rc.Rdlc, result: FileResult) -> None:
    add = result.findings.append
    main_fields: set[str] = set()
    for dataset in doc.datasets:
        main_fields |= set(dataset.fields) | set(dataset.fields.values())
    for node in rc.descendants(doc.root, "Subreport"):
        name = node.get("Name", "")
        target_name = rc.text_of(rc.kid(node, "ReportName"))
        where = rc.line_of(doc.text, f'<Subreport Name="{name}"')
        add(Finding("W23", f"Unterbericht '{name}' -> '{target_name}': Allplan gibt dem Unterbericht die Zeilen des "
                           f"Hauptreports und fuehrt seine eigene Abfrage nicht aus; gefuellt sind nur Felder, die im "
                           f"Hauptreport gleich heissen", where))
        if not target_name or target_name.startswith("="):
            continue
        relative = Path(target_name.replace("\\", "/"))
        target_path = doc.path.parent / (relative if relative.suffix.lower() == ".rdlc" else relative.with_name(relative.name + ".rdlc"))
        if not target_path.is_file():
            continue
        target = rc.Rdlc.load(target_path)
        if target.root is None:
            continue
        missing = sorted({field for dataset in target.datasets for field in dataset.fields} - main_fields)
        if missing:
            add(Finding("W24", f"Unterbericht '{target_name}': Felder {', '.join(missing[:8])}"
                               f"{' ...' if len(missing) > 8 else ''} gibt es im Hauptreport nicht - in Allplan leer. "
                               f"Abhilfe: Feldnamen des Hauptreports verwenden", where))
        block = rc.kid(target.root, "ReportParameters")
        no_prompt = [p.get("Name", "") for p in rc.kids(block, "ReportParameter")
                     if not rc.text_of(rc.kid(p, "Prompt"))] if block is not None else []
        if no_prompt:
            add(Finding("W25", f"Unterbericht '{target_name}': Parameter ohne <Prompt>: {', '.join(no_prompt)} - Allplan "
                               f"fordert den Unterbericht nicht an. Abhilfe: <Prompt> an jedem Parameter des Ziels", where))


class _OverlapTuple(NamedTuple):
    container: str
    element_a: str
    element_b: str
    dx: float
    dy: float


class Overlap(_OverlapTuple):
    """Zwei Geschwister-Elemente eines Containers, die sich ueberlappen (Mass in cm).

    Als Tupel (container, element_a, element_b, dx, dy); zusaetzlich ``expression_a``/``expression_b``:
    traegt das Element einen Sichtbarkeits-Ausdruck (<Visibility><Hidden>=...). Siehe ``is_alternative``.
    """

    def __new__(cls, container: str, element_a: str, element_b: str, dx: float, dy: float,
                expression_a: bool = False, expression_b: bool = False):
        self = super().__new__(cls, container, element_a, element_b, dx, dy)
        self.expression_a, self.expression_b = expression_a, expression_b
        return self


def has_visibility_expression(item: ET.Element) -> bool:
    """Eigener Sichtbarkeits-Ausdruck: <Visibility><Hidden> beginnt mit '='; festes true/false zaehlt nicht."""
    return rc.text_of(rc.walk(item, "Visibility", "Hidden")).startswith("=")


def is_alternative(item: Overlap) -> bool:
    """Entweder-oder-Paar: BEIDE Elemente haben einen Sichtbarkeits-Ausdruck - nie zugleich sichtbar gebaut."""
    return item.expression_a and item.expression_b


def _extent(item: ET.Element) -> tuple[float, float, float, float] | None:
    """(links, oben, rechts, unten) in cm; fehlendes Top/Left = 0, unbekannte Breite/Hoehe = None."""
    def length(name: str) -> float | None:
        return rc.parse_length_cm(rc.text_of(rc.kid(item, name)))

    width, height = length("Width"), length("Height")
    if width is None and rc.local(item.tag) in ("Table", "Tablix"):
        widths = [rc.parse_length_cm(rc.text_of(rc.kid(col, "Width")))
                  for col in rc.descendants(item, "TableColumn") + rc.descendants(item, "TablixColumn")]
        width = sum(widths) if widths and None not in widths else None
    if height is None and rc.local(item.tag) in ("Table", "Tablix"):
        heights = [rc.parse_length_cm(rc.text_of(rc.kid(row, "Height")))
                   for row in rc.descendants(item, "TableRow") + rc.descendants(item, "TablixRow")]
        height = sum(heights) if heights and None not in heights else None
    if width is None or height is None:
        return None
    left, top = length("Left") or 0.0, length("Top") or 0.0
    return (min(left, left + width), min(top, top + height), max(left, left + width), max(top, top + height))


def _overlap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> tuple[float, float] | None:
    """Schnittmass (dx, dy) in cm oder None. Linien (Breite oder Hoehe 0) zaehlen nur, wenn sie durch die Flaeche laufen."""
    tol = OVERLAP_TOLERANCE_CM
    dx = min(first[2], second[2]) - max(first[0], second[0])
    dy = min(first[3], second[3]) - max(first[1], second[1])
    thin = [rect for rect in (first, second) if rect[2] - rect[0] <= 1e-9 or rect[3] - rect[1] <= 1e-9]
    if len(thin) == 2:
        return None  # Linie gegen Linie hat keine Flaeche
    if thin:
        line, area = (first, second) if thin[0] is first else (second, first)
        if line[2] - line[0] <= 1e-9:   # senkrecht: muss innerhalb der Flaeche liegen, nicht auf ihrem Rand
            inside = area[0] + tol < line[0] < area[2] - tol
            return (0.0, dy) if inside and dy > tol else None
        inside = area[1] + tol < line[1] < area[3] - tol
        return (dx, 0.0) if inside and dx > tol else None
    return (dx, dy) if dx > tol and dy > tol else None


def find_overlaps(source: Path | str | bytes | ET.Element | rc.Rdlc) -> list[Overlap]:
    """Ueberlappende Geschwister je Container (Body, Rectangle, Seitenkopf/-fuss, Zelle).

    ``source``: Pfad zur .rdlc, XML-Text/-Bytes, ein ElementTree-Element oder ein ``rc.Rdlc``.
    Elemente verschiedener Container werden nie verglichen. Rueckgabe: Liste von
    ``Overlap(container, element_a, element_b, dx, dy)`` (cm), in Dokumentreihenfolge.
    Das Report-Fenster verschiebt bei jeder Ueberlappung eines der beiden Elemente - das PDF nicht.
    """
    if isinstance(source, rc.Rdlc):
        root = source.root
    elif isinstance(source, ET.Element):
        root = source
    elif isinstance(source, bytes) or (isinstance(source, str) and source.lstrip().startswith("<")):
        root = ET.fromstring(source)
    else:
        root = rc.Rdlc.load(Path(source)).root
    found: list[Overlap] = []
    if root is None:
        return found
    parents = {child: parent for parent in root.iter() for child in parent}
    for holder in rc.descendants(root, "ReportItems"):
        container = parents.get(holder)
        label = (container.get("Name") or rc.local(container.tag)) if container is not None else ""
        items = []
        for index, item in enumerate(holder):
            extent = _extent(item)
            if extent is not None:
                items.append((item.get("Name") or f"{rc.local(item.tag)}#{index + 1}", extent,
                              has_visibility_expression(item)))
        standard = STANDARD_PAGE_ELEMENTS.get(rc.local(container.tag), frozenset()) if container is not None else frozenset()
        for position, (name_a, rect_a, expr_a) in enumerate(items):
            for name_b, rect_b, expr_b in items[position + 1:]:
                if name_a in standard and name_b in standard:
                    continue
                shared = _overlap(rect_a, rect_b)
                if shared:
                    found.append(Overlap(label, name_a, name_b, shared[0], shared[1], expr_a, expr_b))
    return found


def is_stripe(item: Overlap) -> bool:
    """Duenner Streifen: kleineres Schnittmass <= 0,05 cm. Eine Linie durch die Flaeche (Mass 0) ist keiner."""
    return 0 < min(item.dx, item.dy) <= STRIPE_MAX_CM + 1e-9


def _check_overlaps(doc: rc.Rdlc, result: FileResult) -> None:
    found = find_overlaps(doc)
    alternatives = [item for item in found if is_alternative(item)]
    if alternatives:
        result.notes.append(f"{len(alternatives)} Entweder-oder-Paare mit Sichtbarkeits-Ausdruck uebersprungen "
                            f"(W28 gilt fuer sie nicht)")
    # Groesste Schnittflaeche zuerst, damit die Einzelmeldungen die wichtigen sind (Linien: Laenge mal Toleranz).
    overlaps = sorted((item for item in found if not is_alternative(item)),
                      key=lambda item: -(item.dx * item.dy or max(item.dx, item.dy) * OVERLAP_TOLERANCE_CM))
    for item in overlaps[:OVERLAP_MAX_FINDINGS]:
        dx, dy = (f"{value:.2f}".replace(".", ",") for value in (item.dx, item.dy))
        kind = ("Streifen", " (kritisch in Feldern fester Hoehe)") if is_stripe(item) else ("Ueberlappung", "")
        one_sided = (" (eines hat einen Sichtbarkeits-Ausdruck: als Alternative bauen - auch das andere mit dem "
                     "Gegen-Ausdruck ausblenden)" if item.expression_a or item.expression_b else "")
        result.findings.append(Finding(
            "W28", f"{kind[0]}: '{item.element_a}' und '{item.element_b}' ueberlappen sich in '{item.container}' um "
                   f"{dx} x {dy} cm{kind[1]} - im Report-Fenster wird eines verschoben; Abstand >= 0,05 cm lassen"
                   f"{one_sided}",
            rc.line_of(doc.text, f'Name="{item.element_a}"')))
    rest = overlaps[OVERLAP_MAX_FINDINGS:]
    if rest:
        stripes = sum(1 for item in rest if is_stripe(item))
        result.findings.append(Finding(
            "W28", f"... und {len(rest)} weitere: {len(rest) - stripes} Ueberlappungen, {stripes} Streifen"))

def _check_structure(doc: rc.Rdlc, result: FileResult) -> None:
    add = result.findings.append
    if doc.year == "unbekannt":
        add(Finding("E02", f"unbekannter Namespace '{doc.namespace}'"))
    elif doc.year == "2005" and doc.has_tablix:
        add(Finding("E03", "RDL-2005-Datei enthaelt <Tablix>", rc.line_of(doc.text, "<Tablix")))
    elif doc.year in ("2010", "2016") and result.has_table:
        add(Finding("E03", f"RDL-{doc.year}-Datei enthaelt <Table>/<Matrix>"))

    if "ALLPLAN" not in doc.data_providers():
        add(Finding("E04", "kein DataSource mit DataProvider ALLPLAN"))
    if "DummyDataSource" not in doc.datasource_names():
        add(Finding("W02", "kein DataSource 'DummyDataSource'"))
    if rc.STANDARD_DATASOURCE_ID not in doc.datasource_ids():
        add(Finding("W03", f"rd:DataSourceID nicht {rc.STANDARD_DATASOURCE_ID}"))

    main = doc.main_dataset()
    if main is None or not main.command_text:
        add(Finding("E05", "kein DataSet mit CommandText"))
    if not any(dataset.name.startswith("AllplanReport") for dataset in doc.datasets):
        add(Finding("W04", "kein DataSet 'AllplanReport*' (Konvention; 141 Etc-Vorlagen weichen ab)"))


def _check_fields_and_parameters(doc: rc.Rdlc, result: FileResult) -> None:
    add = result.findings.append
    declared_fields: set[str] = set()
    for dataset in doc.datasets:
        declared_fields |= set(dataset.fields)
        known = set(dataset.fields) | set(dataset.fields.values())
        for name in dict.fromkeys(rc.query_field_names(dataset.command_text)):
            if name not in known:
                add(Finding("W16", f"DataSet '{dataset.name}': Query-Feld '{name}' ohne <Field> - Spalte ungenutzt",
                            rc.line_of(doc.text, f"Name={name}")))
        for word in sql_words_in_from(dataset.command_text):
            add(Finding("E07", f"DataSet '{dataset.name}': '{word}' in der FROM-Klausel - gibt es in Allplan nicht"))

    expressions = doc.expressions()
    joined = "\n".join(expressions)
    for name in dict.fromkeys(rc.FIELD_REF_RE.findall(joined)):
        if name not in declared_fields:
            add(Finding("E06", f"Fields!{name} ist in keinem DataSet deklariert",
                        rc.line_of(doc.text, f"Fields!{name}")))

    parameters = doc.report_parameters()
    for name in dict.fromkeys(rc.PARAM_REF_RE.findall(joined)):
        if name not in parameters:
            add(Finding("W17", f"Parameters!{name} nicht deklariert - geht nur, wenn Allplan ihn selbst liefert",
                        rc.line_of(doc.text, f"Parameters!{name}")))

    missing = [name for name in rc.STANDARD_PARAMETERS if name not in parameters]
    if missing:
        add(Finding("W05", f"Standardparameter fehlen: {', '.join(missing)}"))
    if not any(name in parameters for name in rc.VARIABLE_STANDARD_PARAMETERS):
        add(Finding("W05", "weder 'Note' noch 'Fileset_Name' als zwoelfter Standardparameter"))

    for dataset in doc.datasets:
        for attribute, expected in (("205", "System.Byte[]"), ("87", "System.String")):
            for name in re.findall(rf"@{attribute}@\[\s*Name\s*=\s*([^|\]\s,]+)", dataset.command_text):
                actual = dataset.type_names.get(name, "")
                if actual and actual != expected:
                    add(Finding("W11", f"Feld '{name}' (@{attribute}@) hat {actual}, erwartet {expected}"))

    for expression in doc.detail_value_texts():
        aggregates = unscoped_aggregates(expression)
        if aggregates:
            add(Finding("W10", f"Aggregat ohne Scope in einer Detailzeile ({', '.join(aggregates)}): "
                               f"wirkt nur auf die eine Zeile", rc.line_of(doc.text, expression[:40])))
            break


def _check_layout(doc: rc.Rdlc, result: FileResult) -> None:
    add = result.findings.append
    metrics = doc.page_metrics()
    if metrics.body_width is None or metrics.page_width is None:
        add(Finding("W06", "Body- oder Seitenbreite fehlt; Breite nicht pruefbar"))
    else:
        usable = metrics.page_width - metrics.left_margin - metrics.right_margin
        if metrics.body_width > usable + TOLERANCE_CM:
            add(Finding("W07", f"Body-Breite {metrics.body_width:.2f} cm > nutzbare Seitenbreite {usable:.2f} cm "
                               f"- leere Zwischenseiten moeglich"))
        if metrics.column_width_sum is not None and metrics.column_width_sum > metrics.body_width + TOLERANCE_CM:
            add(Finding("W08", f"Tabelle {metrics.column_width_sum:.2f} cm breiter als Body "
                               f"{metrics.body_width:.2f} cm"))

    if has_header_row(doc):
        repeat = [rc.text_of(node).lower() for node in rc.descendants(doc.root, "RepeatOnNewPage")]
        if "true" not in repeat:
            add(Finding("W09", "RepeatOnNewPage=true fehlt; Spaltenkoepfe fehlen ab Seite 2"))

    for node in rc.descendants(doc.root, "SortExpression"):
        if "Fields!Story.Value" in rc.text_of(node):
            add(Finding("W15", "Sortierung nach Fields!Story statt StoryIndex",
                        rc.line_of(doc.text, "Fields!Story.Value")))
            break


def check_file(path: Path, bom_error: bool = False) -> FileResult:
    doc = rc.Rdlc.load(path)
    result = FileResult(path=str(path), encoding=doc.encoding)
    add = result.findings.append

    if doc.encoding in ("utf16", "unbekannt"):
        add(Finding("E08", f"Encoding {doc.encoding}; Allplan-Vorlagen sind UTF-8"))
    elif doc.encoding == "utf8-bom":
        add(Finding("E08" if bom_error else "W01", "UTF-8 mit BOM; neue Dateien ohne BOM speichern"))

    if doc.root is None:
        add(Finding("E01", f"XML nicht wohlgeformt: {doc.parse_error}"))
        return result

    result.namespace_year = doc.year
    result.has_tablix = doc.has_tablix
    result.has_table = doc.has_table or doc.has_matrix
    result.report_id = doc.report_id()

    _check_structure(doc, result)
    _check_fields_and_parameters(doc, result)
    _check_layout(doc, result)
    _check_parameters(doc, result)
    _check_items(doc, result)
    _check_overlaps(doc, result)

    if not result.report_id:
        add(Finding("W12", "rd:ReportID fehlt"))
    elif result.report_id == rc.ALLPLAN_STANDARD_REPORT_ID:
        add(Finding("W13", "rd:ReportID ist die Allplan-Standard-GUID; eigene Reports mit frischer GUID"))
    return result


def mark_duplicate_ids(results: list[FileResult]) -> None:
    by_id: dict[str, list[FileResult]] = {}
    for result in results:
        if result.report_id and result.report_id != rc.ALLPLAN_STANDARD_REPORT_ID:
            by_id.setdefault(result.report_id, []).append(result)
    for report_id, group in by_id.items():
        if len(group) < 2:
            continue
        for result in group:
            others = ", ".join(Path(other.path).name for other in group if other is not result)
            result.findings.append(Finding("W14", f"rd:ReportID {report_id} auch in: {others}"))


# ------------------------------------------------------------------ Ausgabe
def ampel(files: int, errors: int, warnings: int, missing: bool = False) -> str:
    colour = "ROT" if errors or missing else "ORANGE" if warnings else "GRUEN"
    detail = "Pfad fehlt oder keine .rdlc gefunden" if missing else \
        f"{files} Dateien, {errors} Fehler, {warnings} Warnungen"
    return f"AMPEL: {colour} | validate_rdlc | {detail}"


def main(argv: list[str] | None = None) -> int:
    rc.configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--bibliothek", action="store_true",
                        help="Bestand pruefen: nur Struktur, keine Konventionen fuer eigene Reports")
    parser.add_argument("--bom-error", action="store_true", help="BOM als Fehler werten")
    parser.add_argument("--strict", action="store_true", help="Warnungen lassen die Pruefung scheitern")
    parser.add_argument("--json", nargs="?", const="-", metavar="DATEI", help="Ergebnis als JSON")
    parser.add_argument("--quiet", action="store_true", help="nur Dateien mit Befund ausgeben")
    args = parser.parse_args(argv)

    files = rc.iter_rdlc(args.paths, recursive=not args.no_recursive)
    if not files:
        print(ampel(0, 0, 0, missing=True))
        return 2

    results = [check_file(path, args.bom_error) for path in files]
    mark_duplicate_ids(results)
    if args.bibliothek:
        for result in results:
            result.findings = [item for item in result.findings if item.code not in CONVENTION_CODES]

    if args.json:
        payload = [
            {**{key: value for key, value in asdict(result).items() if key != "findings"},
             "status": result.status,
             "errors": [asdict(item) for item in result.errors],
             "warnings": [asdict(item) for item in result.warnings]}
            for result in results
        ]
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        if args.json == "-":
            print(text)
        else:
            Path(args.json).write_text(text + "\n", encoding="utf-8")
    if args.json != "-":
        for result in results:
            if args.quiet and result.status == "OK":
                continue
            print(f"[{result.status}] {result.path}")
            for finding in result.findings:
                print(finding.render())
            for note in result.notes:
                print(f"  Hinweis: {note}")

    errors = sum(len(result.errors) for result in results)
    warnings = sum(len(result.warnings) for result in results)
    print(ampel(len(results), errors, warnings))
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
