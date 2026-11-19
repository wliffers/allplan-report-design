"""Gemeinsame Bausteine fuer die RDLC-Werkzeuge der Report-Werkstatt.

Allplan-RDLC ist Microsoft-RDL-XML mit Allplan-eigener Query-Sprache im
``<CommandText>``. Drei Schema-Generationen kommen im Allplan-2027-Bestand vor:

* 2005 - ``<Table>``/``<Matrix>``, Seitenmasse direkt unter ``<Report>``
* 2010 - ``<Tablix>``, ``ReportSections/ReportSection/Page`` (Kanal-Reports)
* 2016 - ``<Tablix>``, ``ReportSections/ReportSection/Page``

Das Schema wird am Namespace des Wurzelelements erkannt - nie am Dateinamen:
nur die acht ``Template_*_2005.rdlc`` tragen das Suffix ``_2005``.

Alle Zugriffe laufen ueber den lokalen Elementnamen, weil ``rd:``-Elemente
(ReportID, DataSourceID, TypeName) in einem zweiten Namespace liegen.
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# Ordner ueber scripts/: im Entwicklungs-Workspace projects/Reports, im
# ausgelieferten Paket der Skill-Ordner. Beide haben dasselbe Layout
# (scripts/, data/attributes_2027.json, rdlc-index.json).
BASE_DIR = Path(__file__).resolve().parents[1]
ALLPLAN_2027_REPORTS = Path(r"C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports")


def default_library() -> Path:
    """Vorlagenbibliothek: ALLPLAN_REPORTS, sonst <BASE>/rdlc, sonst Allplan-2027-Etc."""
    override = os.environ.get("ALLPLAN_REPORTS")
    if override:
        return Path(override)
    local_copy = BASE_DIR / "rdlc"
    return local_copy if local_copy.is_dir() else ALLPLAN_2027_REPORTS

NAMESPACE_YEARS = {
    "http://schemas.microsoft.com/sqlserver/reporting/2005/01/reportdefinition": "2005",
    "http://schemas.microsoft.com/sqlserver/reporting/2008/01/reportdefinition": "2008",
    "http://schemas.microsoft.com/sqlserver/reporting/2010/01/reportdefinition": "2010",
    "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition": "2016",
}

STANDARD_DATASOURCE_ID = "58c077ef-da67-445a-8cc2-60008c49a79b"
# Alle 551 Vorlagen der Allplan-2027-Bibliothek tragen diese ReportID.
ALLPLAN_STANDARD_REPORT_ID = "2cdc5b66-aa6c-4050-9ab9-72a8741b687e"

# In 484 von 521 Bestandsvorlagen vorhanden; dazu meist "Note" (383) oder
# "Fileset_Name" (13). Nur Vorhandensein zaehlt, die Reihenfolge variiert.
STANDARD_PARAMETERS = (
    "Project_Name", "Edited_By", "Company_Name", "Company_Address", "Date", "Time",
    "PageNo_1", "Company_Logo", "Telephone_Number", "E_Mail", "Display_Logo",
)
VARIABLE_STANDARD_PARAMETERS = ("Note", "Fileset_Name")

# Komma ausgeschlossen: 'Deckenbuch.rdlc' (Etc 2027) schreibt '[Name=Station,' ohne ']'.
QUERY_FIELD_RE = re.compile(r"\[\s*Name\s*=\s*([^|\]\s,]+)")
FIELD_REF_RE = re.compile(r"Fields!([A-Za-z_À-ſ][\wÀ-ſ]*)")
PARAM_REF_RE = re.compile(r"Parameters!([A-Za-z_À-ſ][\wÀ-ſ]*)")
FROM_RE = re.compile(r"\bFROM\s*\[([^\]]*)\]", re.IGNORECASE)
LENGTH_RE = re.compile(r"^\s*(-?[0-9]+(?:[.,][0-9]+)?)\s*(cm|mm|in|pt|pc)\s*$", re.IGNORECASE)
LENGTH_TO_CM = {"cm": 1.0, "mm": 0.1, "in": 2.54, "pt": 2.54 / 72.0, "pc": 2.54 / 6.0}


def configure_stdout() -> None:
    """Umlaute in Dateinamen (Raeume, Flaechen, ...) sicher ausgeben."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass


def local(tag: str) -> str:
    """Lokaler Elementname ohne Namespace."""
    return tag.rsplit("}", 1)[-1]


def kids(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if local(child.tag) == name]


def kid(element: ET.Element | None, name: str) -> ET.Element | None:
    if element is None:
        return None
    for child in element:
        if local(child.tag) == name:
            return child
    return None


def walk(element: ET.Element | None, *names: str) -> ET.Element | None:
    """Pfad aus lokalen Namen entlanggehen, erstes Kind je Stufe."""
    current = element
    for name in names:
        current = kid(current, name)
        if current is None:
            return None
    return current


def descendants(element: ET.Element, name: str) -> list[ET.Element]:
    return [node for node in element.iter() if local(node.tag) == name]


def text_of(element: ET.Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""


def detect_encoding(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf8-bom"
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return "utf16"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return "unbekannt"
    return "utf8"


def parse_length_cm(value: str) -> float | None:
    match = LENGTH_RE.match(value or "")
    if not match:
        return None
    return float(match.group(1).replace(",", ".")) * LENGTH_TO_CM[match.group(2).lower()]


def line_of(text: str, needle: str) -> int | None:
    index = text.find(needle)
    return text.count("\n", 0, index) + 1 if index >= 0 else None


@dataclass
class DataSet:
    name: str
    command_text: str
    fields: dict[str, str]            # Field Name -> DataField (leer bei berechneten Feldern)
    type_names: dict[str, str]        # Field Name -> rd:TypeName


@dataclass
class PageMetrics:
    body_width: float | None
    page_width: float | None
    left_margin: float
    right_margin: float
    column_width_sum: float | None


@dataclass
class Rdlc:
    path: Path
    raw: bytes
    text: str
    encoding: str
    root: ET.Element | None = None
    parse_error: str = ""
    namespace: str = ""
    year: str = "unbekannt"
    datasets: list[DataSet] = field(default_factory=list)

    # ------------------------------------------------------------------ Aufbau
    @classmethod
    def load(cls, path: Path) -> Rdlc:
        raw = path.read_bytes()
        encoding = detect_encoding(raw)
        text = raw.decode("utf-8-sig", errors="replace") if encoding != "utf16" else raw.decode("utf-16")
        doc = cls(path=path, raw=raw, text=text, encoding=encoding)
        try:
            doc.root = ET.fromstring(raw)
        except ET.ParseError as error:
            doc.parse_error = str(error)
            return doc
        if doc.root.tag.startswith("{"):
            doc.namespace = doc.root.tag[1:].split("}", 1)[0]
        doc.year = NAMESPACE_YEARS.get(doc.namespace, "unbekannt")
        doc.datasets = doc._read_datasets()
        return doc

    def _read_datasets(self) -> list[DataSet]:
        result = []
        for node in descendants(self.root, "DataSet"):
            command = walk(node, "Query", "CommandText")
            fields: dict[str, str] = {}
            types: dict[str, str] = {}
            for field_node in descendants(node, "Field"):
                name = field_node.get("Name", "")
                fields[name] = text_of(kid(field_node, "DataField"))
                types[name] = text_of(kid(field_node, "TypeName"))
            result.append(DataSet(node.get("Name", ""), text_of(command), fields, types))
        return result

    # -------------------------------------------------------------- Abfragen
    @property
    def has_tablix(self) -> bool:
        return bool(self.root is not None and descendants(self.root, "Tablix"))

    @property
    def has_table(self) -> bool:
        return bool(self.root is not None and descendants(self.root, "Table"))

    @property
    def has_matrix(self) -> bool:
        return bool(self.root is not None and descendants(self.root, "Matrix"))

    def main_dataset(self) -> DataSet | None:
        """Erstes DataSet 'AllplanReport*', sonst das erste mit CommandText."""
        for dataset in self.datasets:
            if dataset.name.startswith("AllplanReport"):
                return dataset
        for dataset in self.datasets:
            if dataset.command_text:
                return dataset
        return None

    def expressions(self) -> list[str]:
        """Alle RDL-Ausdruecke (Elementtexte, die mit '=' beginnen).

        Ein 'Fields!X' in einem <Prompt> ist blosser Text und kein Ausdruck
        (Staedtebau-Reports der Etc-Bibliothek).
        """
        if self.root is None:
            return []
        return [text for text in (text_of(node) for node in self.root.iter()) if text.startswith("=")]

    def report_id(self) -> str:
        return text_of(kid(self.root, "ReportID")) if self.root is not None else ""

    def author(self) -> str:
        return text_of(kid(self.root, "Author")) if self.root is not None else ""

    def data_providers(self) -> list[str]:
        if self.root is None:
            return []
        return [text_of(node) for node in descendants(self.root, "DataProvider")]

    def datasource_names(self) -> list[str]:
        sources = walk(self.root, "DataSources")
        return [node.get("Name", "") for node in kids(sources, "DataSource")] if sources is not None else []

    def datasource_ids(self) -> list[str]:
        if self.root is None:
            return []
        return [text_of(node) for node in descendants(self.root, "DataSourceID")]

    def report_parameters(self) -> list[str]:
        block = kid(self.root, "ReportParameters")
        return [node.get("Name", "") for node in kids(block, "ReportParameter")] if block is not None else []

    def _section(self) -> ET.Element | None:
        """Traeger von Body/Width/Page: Report (2005) bzw. ReportSection (2010/2016)."""
        if self.root is None:
            return None
        section = walk(self.root, "ReportSections", "ReportSection")
        return section if section is not None else self.root

    def page_metrics(self) -> PageMetrics:
        section = self._section()
        page = kid(section, "Page") if self.year in ("2010", "2016") else section
        if page is None:
            page = section

        def length(parent: ET.Element | None, name: str) -> float | None:
            return parse_length_cm(text_of(kid(parent, name)))

        return PageMetrics(
            body_width=length(section, "Width"),
            page_width=length(page, "PageWidth"),
            left_margin=length(page, "LeftMargin") or 0.0,
            right_margin=length(page, "RightMargin") or 0.0,
            column_width_sum=self._widest_table_cm(),
        )

    def _widest_table_cm(self) -> float | None:
        """Groesste Summe aus eigenen Spaltenbreiten plus linker Position je Tabelle.

        Nur die direkten Spalten der Tabelle - verschachtelte Tabellen zaehlen
        in ihrer eigenen Zelle, nicht obendrauf.
        """
        if self.root is None:
            return None
        widest = None
        for table in descendants(self.root, "Table") + descendants(self.root, "Tablix"):
            holder = kid(table, "TableColumns") if local(table.tag) == "Table" else walk(table, "TablixBody", "TablixColumns")
            columns = kids(holder, "TableColumn") + kids(holder, "TablixColumn") if holder is not None else []
            widths = [parse_length_cm(text_of(kid(column, "Width"))) for column in columns]
            if not widths or any(width is None for width in widths):
                continue
            left = parse_length_cm(text_of(kid(table, "Left"))) or 0.0
            total = left + sum(widths)  # type: ignore[arg-type]
            widest = total if widest is None else max(widest, total)
        return widest

    def detail_value_texts(self) -> list[str]:
        """Ausdruecke, die je Datensatz ausgewertet werden (Detailzeilen)."""
        if self.root is None:
            return []
        values: list[str] = []
        for table in descendants(self.root, "Table"):
            details = kid(table, "Details")
            if details is not None:
                values += [text_of(node) for node in descendants(details, "Value")]
        for tablix in descendants(self.root, "Tablix"):
            values += _tablix_detail_values(tablix)
        return [value for value in values if value]


def _tablix_detail_values(tablix: ET.Element) -> list[str]:
    """Zeilen der Tablix, deren Zeilenmitglied in einer Detailgruppe liegt.

    Die Blaetter der Zeilenhierarchie entsprechen in Dokumentreihenfolge den
    ``TablixRow``-Eintraegen. Detail heisst: das Blatt oder ein Vorfahr hat
    eine ``Group`` ohne ``GroupExpressions``.
    """
    rows = descendants(walk(tablix, "TablixBody", "TablixRows") or ET.Element("x"), "TablixRow")
    hierarchy = walk(tablix, "TablixRowHierarchy", "TablixMembers")
    if hierarchy is None or not rows:
        return []

    leaves: list[bool] = []

    def visit(members: ET.Element, in_details: bool) -> None:
        for member in kids(members, "TablixMember"):
            group = kid(member, "Group")
            details_here = in_details or (group is not None and kid(group, "GroupExpressions") is None)
            children = kid(member, "TablixMembers")
            if children is not None and kids(children, "TablixMember"):
                visit(children, details_here)
            else:
                leaves.append(details_here)

    visit(hierarchy, False)
    values: list[str] = []
    for is_detail, row in zip(leaves, rows):
        if is_detail:
            values += [text_of(node) for node in descendants(row, "Value")]
    return values


# ---------------------------------------------------------------- Query-Teil
def query_field_names(command_text: str) -> list[str]:
    return QUERY_FIELD_RE.findall(command_text)


def from_tables(command_text: str) -> list[str]:
    """Tabellen der FROM-Klauseln: benannte (MODEL_DATA, ...) und 'Type=N'."""
    tables: list[str] = []
    for clause in FROM_RE.findall(command_text):
        for token in (part.strip() for part in clause.split(",")):
            if not token:
                continue
            if "=" not in token:
                tables.append(token)
            elif re.match(r"^Type\s*=\s*\d+$", token):
                tables.append(re.sub(r"\s+", "", token))
    return list(dict.fromkeys(tables))


def _filter_values(command_text: str, attribute: str) -> list[int]:
    escaped = re.escape(attribute)
    values = re.findall(rf"{escaped}\.eq\.(-?\d+)", command_text)
    values += re.findall(rf"{escaped}\s*=\s*(-?\d+)", command_text)
    for listing in re.findall(rf"ELE\(\s*{escaped}\s*;([^)]*)\)", command_text):
        values += [item.strip() for item in listing.split(";") if item.strip().lstrip("-").isdigit()]
    return sorted({int(value) for value in values})


def query_metadata(command_text: str) -> dict:
    dotted = bool(re.search(r"\.(eq|ne|lt|le|gt|ge|and|or)\.", command_text))
    legacy = bool(re.search(r"@\w+@\s*=\s*[-\w\"]", command_text))
    dialect = "mixed" if dotted and legacy else "dotted" if dotted else "legacy" if legacy else ""
    return {
        "FieldNames": query_field_names(command_text),
        "FromTables": from_tables(command_text),
        "ObjectFilters": _filter_values(command_text, "@OBJ@"),
        "StatusFilters": _filter_values(command_text, "@49@"),
        "TradeFilters": _filter_values(command_text, "@GW@"),
        "FilterDialect": dialect,
        "HasGraphics205": "@205@" in command_text,
        "HasSvg87": "@87@" in command_text,
        "HasParent": "PARENT(" in command_text,
    }


def iter_rdlc(paths: list[Path], recursive: bool = True, skip_dirs: tuple[str, ...] = ()) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            pattern = "**/*.rdlc" if recursive else "*.rdlc"
            found += [
                item for item in path.glob(pattern)
                if item.is_file() and not set(skip_dirs).intersection(item.relative_to(path).parts)
            ]
    return sorted(set(found), key=lambda item: str(item).lower())
