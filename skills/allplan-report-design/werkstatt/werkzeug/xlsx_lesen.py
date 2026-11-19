"""Liest einen von Allplan exportierten Report (.xlsx) als Tabelle und fasst ihn zusammen.

    python xlsx_lesen.py <datei.xlsx> [--zeilen=15] [--gruppe=Spaltenname ...]
Kopfzeile = erste Zeile, in der mindestens drei Zellen gefuellt sind.
"""
import collections
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def _spalte(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def _zeilen(pfad):
    """Erstes Tabellenblatt als Liste von Zeilen (nur Standardbibliothek)."""
    with zipfile.ZipFile(pfad) as z:
        texte = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si"):
                texte.append("".join(t.text or "" for t in si.iter(NS + "t")))
        blatt = sorted(n for n in z.namelist() if n.startswith("xl/worksheets/sheet"))[0]
        rows = []
        for row in ET.fromstring(z.read(blatt)).iter(NS + "row"):
            werte = {}
            for c in row.iter(NS + "c"):
                v = c.find(NS + "v")
                if c.get("t") == "inlineStr":
                    wert = "".join(t.text or "" for t in c.iter(NS + "t"))
                elif v is None:
                    continue
                elif c.get("t") == "s":
                    wert = texte[int(v.text)]
                elif c.get("t") in ("str", "b"):
                    wert = v.text
                else:
                    try:
                        wert = float(v.text)
                    except ValueError:
                        wert = v.text
                werte[_spalte(c.get("r"))] = wert
            rows.append([werte.get(i) for i in range(max(werte) + 1)] if werte else [])
        return rows


def lade(pfad):
    rows = _zeilen(pfad)
    if not rows:
        raise SystemExit("Keine Zeilen in %s" % pfad)
    # Kopfzeile: bei einer Datenprobe die erste Zeile mit "Name @Nr@", sonst die erste Zeile mit mindestens drei Zellen
    # (bei schmalen Tabellen: so vielen Zellen, wie die breiteste Zeile hat)
    belegt = [sum(v is not None for v in r) for r in rows]
    probe = [i for i, r in enumerate(rows) if any(isinstance(v, str) and " @" in v for v in r)]
    start = probe[0] if probe else next(i for i, n in enumerate(belegt) if n >= min(3, max(belegt)))
    kopf_roh = rows[start]
    spalten = [i for i, v in enumerate(kopf_roh) if v is not None]
    kopf = [str(kopf_roh[i]).split(" @")[0] for i in spalten]
    daten = []
    for r in rows[start + 1:]:
        werte = [r[i] if i < len(r) else None for i in spalten]
        if any(v is not None for v in werte):
            daten.append(dict(zip(kopf, werte)))
    return kopf, daten


def main(argv):
    pfade = [a for a in argv if not a.startswith("--")]
    if len(pfade) != 1:
        sys.exit("Aufruf: python xlsx_lesen.py <datei.xlsx> [--zeilen=15] [--gruppe=Spaltenname ...]")
    pfad = pfade[0]
    zeilen = 15
    gruppen = []
    for a in argv:
        if a.startswith("--zeilen="):
            zeilen = int(a[9:])
        if a.startswith("--gruppe="):
            gruppen.append(a[9:])
    kopf, daten = lade(pfad)
    print("Spalten:", kopf)
    print("Zeilen:", len(daten))
    for d in daten[:zeilen]:
        print(" | ".join("" if d[k] is None else str(d[k]) for k in kopf))
    for g in gruppen:
        print("-- Werte in", g, ":", dict(collections.Counter(str(d.get(g)) for d in daten).most_common(40)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
