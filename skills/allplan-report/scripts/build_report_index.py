"""Katalog aller Referenzvorlagen als JSON erzeugen (rdlc-index.json).

Aufruf (Pfade relativ zum Ordner ueber scripts/):
    python scripts/build_report_index.py [--source DIR] [--output DATEI] [--mit-legacy]

Vorgabe-Quelle: Umgebungsvariable ``ALLPLAN_REPORTS``, sonst ``rdlc/`` neben
``scripts/`` (Entwicklungs-Workspace), sonst die installierte Bibliothek
``C:\\ProgramData\\Nemetschek\\Allplan\\2027\\Etc\\Reports``.
Vorgabe-Ziel: ``rdlc-index.json`` neben ``scripts/``. Der Ordner
``_nicht_in_2027`` wird nur mit ``--mit-legacy`` aufgenommen.

Die Ausgabe ist deterministisch: nach ``RelativePath`` sortiert, UTF-8 ohne
BOM, LF - ein zweiter Lauf auf demselben Bestand erzeugt dieselben Bytes.

Suchbeispiele (Python, weil Dateinamen Umlaute tragen):
    Vorlagen fuer Waende (@OBJ@=1):   Eintraege mit 1 in "ObjectFilters"
    Abbruch-Reports:                   2 in "StatusFilters"
    Kategorie:                         "Category": "Gewerke", "Language": "deu"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rdlc_common as rc  # noqa: E402

DEFAULT_OUTPUT = rc.BASE_DIR / "rdlc-index.json"
LEGACY_DIR = "_nicht_in_2027"


def classify(relative: Path) -> tuple[str, str, str]:
    """Sprache, Kategorie und Unterkategorie aus dem Pfad (deu/<Kategorie>/<Unter>/...)."""
    parts = relative.parts[:-1]
    if parts and parts[0] == LEGACY_DIR:
        return "", LEGACY_DIR, ""
    language = parts[0] if parts and parts[0] in ("deu", "eng") else ""
    rest = parts[1:] if language else parts
    category = rest[0] if rest else ""
    sub_category = "/".join(rest[1:]) if len(rest) > 1 else ""
    return language, category, sub_category


def index_entry(path: Path, source: Path) -> dict:
    relative = path.relative_to(source)
    language, category, sub_category = classify(relative)
    doc = rc.Rdlc.load(path)
    entry: dict = {
        "FileName": path.name,
        "RelativePath": relative.as_posix(),
        "Language": language,
        "Category": category,
        "SubCategory": sub_category,
        "RdlNamespace": doc.year,
        "Encoding": doc.encoding,
    }
    if doc.root is None:
        entry["ParseError"] = doc.parse_error
        return entry

    main = doc.main_dataset()
    main_meta = rc.query_metadata(main.command_text if main else "")
    parameters = doc.report_parameters()
    metrics = doc.page_metrics()
    entry.update({
        "HasTablix": doc.has_tablix,
        "HasTable": doc.has_table,
        "HasMatrix": doc.has_matrix,
        "ReportID": doc.report_id(),
        "Author": doc.author(),
        "PageWidthCm": round(metrics.page_width, 3) if metrics.page_width is not None else None,
        "BodyWidthCm": round(metrics.body_width, 3) if metrics.body_width is not None else None,
        "ReportParameters": parameters,
        "ExtraParameters": [name for name in parameters if name not in rc.STANDARD_PARAMETERS
                            and name not in rc.VARIABLE_STANDARD_PARAMETERS],
        "MainDataSet": main.name if main else "",
        "DataSets": [
            {"Name": dataset.name,
             "FieldNames": rc.query_field_names(dataset.command_text),
             "FromTables": rc.from_tables(dataset.command_text),
             "CommandText": dataset.command_text}
            for dataset in doc.datasets
        ],
        "FieldCount": len(main_meta["FieldNames"]),
        **main_meta,
        "ParseError": None,
    })
    return entry


def build(source: Path, with_legacy: bool) -> list[dict]:
    skip = () if with_legacy else (LEGACY_DIR,)
    files = rc.iter_rdlc([source], recursive=True, skip_dirs=skip)
    entries = [index_entry(path, source) for path in files]
    return sorted(entries, key=lambda item: item["RelativePath"])


def main(argv: list[str] | None = None) -> int:
    rc.configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, default=None, help="Vorlagenbibliothek (Vorgabe s. oben)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mit-legacy", action="store_true", help=f"Ordner {LEGACY_DIR} mitindexieren")
    args = parser.parse_args(argv)
    args.source = args.source or rc.default_library()

    if not args.source.is_dir():
        print(f"Quelle nicht gefunden: {args.source}")
        print("AMPEL: ROT | build_report_index | Quelle fehlt")
        return 2

    entries = build(args.source, args.mit_legacy)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    args.output.write_bytes(text.encode("utf-8"))

    parse_errors = sum(1 for entry in entries if entry.get("ParseError"))
    colour = "GRUEN" if entries and not parse_errors else "ROT"
    print(f"Index geschrieben: {args.output}")
    print(f"AMPEL: {colour} | build_report_index | {len(entries)} Dateien, {parse_errors} Parse-Fehler")
    return 0 if colour == "GRUEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
