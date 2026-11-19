"""Macht aus dem Excel-Export einer Datenprobe die Beispieldaten fuer den kopflosen Renderer.

    python xlsx_zu_json.py <probe.rdlc> <probe.xlsx> <ziel.json>
Feldnamen und Typen kommen aus der .rdlc (Reihenfolge der <Field>-Eintraege = Spaltenfolge).
"""
import json
import re
import sys

from xlsx_lesen import lade

TYP = {"System.String": "String", "System.Double": "Double", "System.Int32": "Int"}


def main(rdlc, xlsx, ziel):
    text = open(rdlc, encoding="utf-8-sig").read()
    felder = re.findall(r'<Field Name="([^"]+)">.*?<rd:TypeName>([^<]+)</rd:TypeName>', text, re.S)
    kopf, daten = lade(xlsx)
    if len(kopf) != len(felder):
        raise SystemExit("Spaltenzahl passt nicht: %d im Excel, %d Felder" % (len(kopf), len(felder)))
    rows = []
    for zeile in daten:
        werte = [zeile[k] for k in kopf]
        if isinstance(werte[0], str) and werte[0].startswith("Zeilen:"):
            continue
        row = {}
        for (name, typ), wert in zip(felder, werte):
            t = TYP.get(typ, "String")
            if wert is None:
                row[name] = 0 if t != "String" else ""
            elif t == "Double":
                row[name] = float(wert)
            elif t == "Int":
                row[name] = int(float(wert))
            else:
                row[name] = str(int(wert)) if isinstance(wert, float) and wert == int(wert) else str(wert)
        rows.append(row)
    types = {name: TYP.get(typ, "String") for name, typ in felder}
    with open(ziel, "w", encoding="utf-8") as handle:
        json.dump({"types": types, "rows": rows}, handle, ensure_ascii=False, indent=1)
    print(ziel, len(rows), "Zeilen")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Aufruf: python xlsx_zu_json.py <probe.rdlc> <probe.xlsx> <ziel.json>")
    main(*sys.argv[1:4])
