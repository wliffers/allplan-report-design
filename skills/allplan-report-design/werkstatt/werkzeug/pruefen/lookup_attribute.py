"""Allplan-Attribut-IDs (@Ifnr@) im Attributkatalog von Allplan 2027 nachschlagen.

Aufruf (Pfad des Skripts: scripts/ im Skill- bzw. Projektordner):
    python scripts/lookup_attribute.py 220 507 205
    python scripts/lookup_attribute.py --suche Volumen
    python scripts/lookup_attribute.py --export
    ... [--lang de|en] [--json] [--etc DIR]

Quelle der Wahrheit sind die Kataloge der Installation:
``<Etc>/Xml/*AttributeDefinitionCollection*_{de,en}.xml`` (Allplan, Allplan2,
_08, Precast, Bridge, PassiveHouse, BSDD). ``--etc`` oder die Umgebungsvariable
``ALLPLAN_ETC`` ueberschreiben den Pfad. Ohne Installation dient der
mitgelieferte Export ``data/attributes_2027.json`` (neben ``scripts/``) als Rueckfall.

Die Spalte ``TypeName`` nennt den passenden ``<rd:TypeName>`` fuer das
``<Field>`` im Report. Ein ``?`` heisst: fuer diesen Datentyp gibt es keinen
Beleg - an einer Vorlage der Allplan-Bibliothek pruefen.

Exit-Codes: 0 Treffer, 1 kein Treffer, 2 keine Quelle.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rdlc_common as rc  # noqa: E402

DEFAULT_ETC = Path(r"C:\ProgramData\Nemetschek\Allplan\2027\Etc")
SNAPSHOT = rc.BASE_DIR / "data" / "attributes_2027.json"

# Datatype-Code des Katalogs -> rd:TypeName im RDLC-Field. Gezaehlt an allen
# Query-Feldern der Etc-2027-Bibliothek (2026-09-29): C String 3351/3574,
# R Double 1614/1662, I Int32 951/1061, B Byte[] 315/315, E String 112/112,
# D je 17x String und DateTime. S ist unbelegt (Textliste -> String angenommen),
# P und Y kommen in keiner Vorlage vor.
TYPE_NAMES = {
    "C": "System.String",
    "S": "System.String",
    "R": "System.Double",
    "I": "System.Int32",
    "D": "System.DateTime",
    "B": "System.Byte[]",
    "E": "System.String",
}
DATATYPE_LABELS = {
    "C": "Text", "S": "Textliste", "R": "Zahl (reell)", "I": "Ganzzahl", "D": "Datum",
    "B": "Grafik/Binaer", "E": "Aufzaehlung", "P": "?", "Y": "?",
}


def _catalog_files(etc: Path) -> dict[str, dict[str, Path]]:
    """Stamm -> {'de': Pfad, 'en': Pfad, '': Pfad} fuer alle Kataloge."""
    catalogs: dict[str, dict[str, Path]] = {}
    for path in sorted((etc / "Xml").glob("*AttributeDefinitionCollection*.xml")):
        match = re.match(r"^(.*?)(?:_(de|en))?$", path.stem)
        stem, lang = match.group(1), match.group(2) or ""
        catalogs.setdefault(stem, {})[lang] = path
    return catalogs


def _read_catalog(path: Path) -> dict[int, dict]:
    entries: dict[int, dict] = {}
    for node in ET.parse(path).getroot().iter("AttributeDefinition"):
        ifnr = (node.findtext("Ifnr") or "").strip()
        if not ifnr.isdigit():
            continue
        entries[int(ifnr)] = {
            "text": (node.findtext("Text") or "").strip(),
            "datatype": (node.findtext("Datatype") or "").strip(),
            "unit": (node.findtext("Unit") or "").strip(),
            "comment": (node.findtext("Comment") or "").strip(),
        }
    return entries


def load_from_etc(etc: Path) -> list[dict]:
    result: dict[int, dict] = {}
    for stem, by_lang in _catalog_files(etc).items():
        german = _read_catalog(by_lang.get("de") or by_lang.get(""))
        english = _read_catalog(by_lang["en"]) if "en" in by_lang else {}
        source = (by_lang.get("de") or by_lang.get("")).name
        for ifnr, entry in german.items():
            if ifnr in result:
                continue
            result[ifnr] = {
                "ifnr": ifnr,
                "text_de": entry["text"],
                "text_en": english.get(ifnr, {}).get("text", ""),
                "datatype": entry["datatype"],
                "type_name": TYPE_NAMES.get(entry["datatype"], "?"),
                "unit": entry["unit"],
                "comment_de": entry["comment"],
                "source": source,
            }
    return [result[key] for key in sorted(result)]


def load(etc: Path | None) -> tuple[list[dict], str]:
    candidates = [etc] if etc else [Path(os.environ["ALLPLAN_ETC"])] if os.environ.get("ALLPLAN_ETC") else []
    candidates.append(DEFAULT_ETC)
    for candidate in candidates:
        if candidate and (candidate / "Xml").is_dir() and _catalog_files(candidate):
            return load_from_etc(candidate), str(candidate / "Xml")
    if SNAPSHOT.is_file():
        return json.loads(SNAPSHOT.read_text(encoding="utf-8")), str(SNAPSHOT)
    return [], ""


def render(entry: dict, lang: str) -> str:
    text = entry["text_de"] if lang == "de" else entry["text_en"] or entry["text_de"]
    other = entry["text_en"] if lang == "de" else entry["text_de"]
    unit = f"  Einheit={entry['unit']}" if entry["unit"] else ""
    label = DATATYPE_LABELS.get(entry["datatype"], "?")
    return (f"@{entry['ifnr']}@  {text}" + (f" | {other}" if other else "")
            + f"  Datatype={entry['datatype']} ({label}) -> {entry['type_name']}{unit}  [{entry['source']}]")


def main(argv: list[str] | None = None) -> int:
    rc.configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="*", help="Attributnummern, auch in der Form @220@")
    parser.add_argument("--suche", help="Teiltext in Name oder Kommentar (DE und EN)")
    parser.add_argument("--lang", choices=("de", "en"), default="de")
    parser.add_argument("--json", action="store_true", help="Treffer als JSON")
    parser.add_argument("--export", nargs="?", const=str(SNAPSHOT), metavar="DATEI",
                        help="kompletten Katalog als JSON schreiben (Rueckfall ohne Allplan)")
    parser.add_argument("--etc", type=Path, help="Allplan-Etc-Ordner (Vorgabe 2027)")
    args = parser.parse_args(argv)

    entries, source = load(args.etc)
    if not entries:
        print("Kein Attributkatalog gefunden (weder Allplan-Etc noch Export).")
        return 2

    if args.export:
        target = Path(args.export)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((json.dumps(entries, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
        print(f"{len(entries)} Attribute exportiert nach {target} (Quelle {source})")
        return 0

    by_id = {entry["ifnr"]: entry for entry in entries}
    hits: list[dict] = []
    misses: list[str] = []
    for raw in args.ids:
        number = raw.strip("@")
        if number.isdigit() and int(number) in by_id:
            hits.append(by_id[int(number)])
        else:
            misses.append(raw)
    if args.suche:
        needle = args.suche.lower()
        hits += [entry for entry in entries
                 if needle in entry["text_de"].lower() or needle in entry["text_en"].lower()
                 or needle in entry["comment_de"].lower()][:50]

    if args.json:
        print(json.dumps(hits, indent=2, ensure_ascii=False))
    else:
        for entry in hits:
            print(render(entry, args.lang))
        for raw in misses:
            print(f"{raw}: nicht im Katalog - Vorbild in der Allplan-Bibliothek suchen, nicht raten")
        print(f"Quelle: {source}")
    return 0 if hits and not misses else 1


if __name__ == "__main__":
    raise SystemExit(main())
