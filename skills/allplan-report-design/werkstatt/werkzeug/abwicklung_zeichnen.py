# -*- coding: utf-8 -*-
"""Rechnet die Raum-Abwicklung aus einer Datendatei und schreibt die Zeichenauftraege - ohne Allplan.

    python abwicklung_zeichnen.py <elemente.json> <auftrag.json> [--scale=100] [--sprache=de|en]

Eingabe ist entweder
  (a) die eigene Form des Kerns: {"raeume": [{"id","nr","name","punkte":[[x,y],...],"z0","hoehe"}],
      "oeffnungen": [{"art":"tuer"|"fenster","ecken":[[x,y,z],...]}]}  (Meter), oder
  (b) eine Elementliste {"elements": [...]} mit Raeumen (bbox_m, attribute), Waenden (achse_m, dicke_m) und
      Oeffnungen (oeffnung: wand_id, mitte_m, breite_m, unterkante_m, oberkante_m) - Beispiel: tests/daten/.
      Diese Form kennt keinen Raumumriss - Raeume werden dann als Rechteck ihrer Umgrenzung gerechnet.
Dieses Paket enthaelt kein Werkzeug, das die Zeichnung in Allplan ablegt; der Kern liefert die Geometrie.

Ausgabe: {"teilbild_massstab", "flaechen", "linien", "texte", "rahmen", "raeume"} - Meter; Texthoehe in Papier-mm
fuer den genannten Teilbildmassstab. abwicklung_vorschau.py zeichnet daraus Bilder.
"""
import json
import math
import sys

import abwicklung_kern as kern

ABSTAND_RAEUME = 3.0             # m zwischen zwei Rahmen
ABSTAND_GEBAEUDE = 15.0          # m zwischen Gebaeude und erstem Rahmen


def _attribut(element, nummer, vorgabe=None):
    for nr, wert in element.get("attribute", []):
        if nr == nummer:
            return wert
    return vorgabe


def aus_elementliste(elemente):
    """Elementliste (Form b) in die Form des Kerns bringen."""
    waende = {e["id"]: e for e in elemente if e["typ"] == "wand" and "achse_m" in e}
    raeume = []
    for e in sorted((e for e in elemente if e["typ"] == "raum"), key=lambda e: str(_attribut(e, 10))):
        (x0, y0, z0), (x1, y1, z1) = e["bbox_m"]
        raeume.append({"id": e["id"], "nr": _attribut(e, 10), "name": _attribut(e, 507) or _attribut(e, 506) or "",
                       "punkte": [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "z0": z0, "hoehe": z1 - z0})
    raumkanten = [kante for raum in raeume for kante in kern.waende(kern.ring(raum["punkte"]))]
    oeffnungen = []
    for e in elemente:
        daten = e.get("oeffnung")
        wand = waende.get(daten.get("wand_id")) if daten else None
        if wand is None:
            continue
        von, nach = wand["achse_m"]["von"], wand["achse_m"]["nach"]
        lang = math.hypot(nach[0] - von[0], nach[1] - von[1])
        if lang < 1e-6:
            continue
        u = ((nach[0] - von[0]) / lang, (nach[1] - von[1]) / lang)
        n = (-u[1], u[0])
        halb, mitte = daten["breite_m"] / 2, daten["mitte_m"]
        dicke = wand.get("dicke_m", daten.get("wanddicke_m", 0.4))
        quer = [_wandflaeche(mitte, u, n, seite, dicke, halb, raumkanten) for seite in (1.0, -1.0)]
        ecken = [(mitte[0] + u[0] * s + n[0] * q, mitte[1] + u[1] * s + n[1] * q, z)
                 for z in (daten["unterkante_m"], daten["oberkante_m"]) for s in (-halb, halb) for q in quer]
        oeffnungen.append({"art": "tuer" if daten["art"] == "tuer" else "fenster", "ecken": ecken})
    kaesten = [e["bbox_m"] for e in elemente if "bbox_m" in e]
    return raeume, oeffnungen, (min(k[0][0] for k in kaesten), min(k[0][1] for k in kaesten))


def _wandflaeche(mitte, u, n, seite, dicke, halb, raumkanten):
    """Abstand der Wandflaeche von der Achse auf einer Seite: die naechste parallele Raumkante, sonst die halbe Dicke.
    Die Achse liegt nicht immer in Wandmitte - der Koerper der Oeffnung muss die Raumflaeche genau erreichen."""
    bester = None
    for kante in raumkanten:
        if abs(kante["u"][0] * u[1] - kante["u"][1] * u[0]) > 0.05:
            continue
        ax, ay = kante["a"][0] - mitte[0], kante["a"][1] - mitte[1]
        q = ax * n[0] + ay * n[1]
        laengs = -(ax * kante["u"][0] + ay * kante["u"][1])
        if q * seite < -1e-6 or abs(q) > dicke + 0.05 or laengs < -halb or laengs > kante["laenge"] + halb:
            continue
        if bester is None or abs(q) < abs(bester):
            bester = q
    return bester if bester is not None else seite * dicke / 2


def auftrag(raeume, oeffnungen, x_links, y_oben, scale, sprache="de"):
    bilder, fehler = kern.alle(raeume, oeffnungen, x_links, y_oben, ABSTAND_RAEUME, sprache)
    papier = 1000.0 / scale
    ergebnis = {"teilbild_massstab": scale, "sprache": sprache, "kern": kern.KERN_VERSION, "flaechen": [], "linien": [],
                "texte": [], "rahmen": [], "raeume": [], "nicht_abgewickelt": fehler}
    for bild in bilder:
        for f in bild["flaechen"]:
            ergebnis["flaechen"].append({"typ": "flaeche", "punkte": f["punkte"], "fuellfarbe": f["farbe"],
                                         "reihenfolge": f["reihenfolge"]})
        for li in bild["linien"]:
            flach = []
            for i in range(0, len(li["punkte"]), 2):
                flach += [li["punkte"][i], li["punkte"][i + 1], 0.0]
            ergebnis["linien"].append({"typ": "linie", "punkte": flach, "geschlossen": 1 if li["geschlossen"] else 0,
                                       "reihenfolge": 10})
        for t in bild["texte"]:
            ergebnis["texte"].append({"typ": "text", "text": t["text"], "x": t["x"], "y": t["y"],
                                      "texthoehe": round(t["hoehe_m"] * papier, 2), "ausrichtung": t["ausrichtung"],
                                      "textfarbe": t["farbe"], "angle": t["winkel"], "reihenfolge": 12})
        r = bild["rahmen"]
        ergebnis["rahmen"].append({"typ": "decke", "x": r["x"], "y": r["y"], "z": -1.0, "length": r["laenge"],
                                   "width": r["breite"], "thickness": 0.01, "material": "Abwicklung"})
        ergebnis["raeume"].append(bild["info"])
    return ergebnis


def main():
    if len([a for a in sys.argv[1:] if not a.startswith("--")]) != 2:
        sys.exit("Aufruf: python abwicklung_zeichnen.py <elemente.json> <auftrag.json> [--scale=100] [--sprache=de|en]")
    quelle, ziel = sys.argv[1], sys.argv[2]
    scale = next((float(a[8:]) for a in sys.argv if a.startswith("--scale=")), 100.0)
    sprache = next((a[10:] for a in sys.argv if a.startswith("--sprache=")), "de")
    with open(quelle, encoding="utf-8") as handle:
        daten = json.load(handle)
    if "raeume" in daten:
        raeume, oeffnungen = daten["raeume"], daten["oeffnungen"]
        x_links = min(p[0] for r in raeume for p in r["punkte"])
        y_unten = min(p[1] for r in raeume for p in r["punkte"])
    else:
        raeume, oeffnungen, (x_links, y_unten) = aus_elementliste(daten["elements"])
    ergebnis = auftrag(raeume, oeffnungen, x_links, y_unten - ABSTAND_GEBAEUDE, scale, sprache)
    with open(ziel, "w", encoding="utf-8") as handle:
        json.dump(ergebnis, handle, ensure_ascii=False, indent=1)
    print("Raeume %d | Flaechen %d | Linien %d | Texte %d | nicht abgewickelt %d" % (
        len(ergebnis["raeume"]), len(ergebnis["flaechen"]), len(ergebnis["linien"]), len(ergebnis["texte"]),
        len(ergebnis["nicht_abgewickelt"])))
    for r in ergebnis["raeume"]:
        print("  %-16s 1:%-4d Reihen %d Zeilen %d  Waende %d  Tueren %d Fenster %d  netto %.2f m2" % (
            r["name"][:16], r["massstab_1_zu"], r["reihen"], r["bahnen"], r["waende"], r["tueren"], r["fenster"],
            r["wandflaeche_netto_m2"]))
    for f in ergebnis["nicht_abgewickelt"]:
        print("  NICHT: %s - %s" % (f["raum"], f["grund"]))


if __name__ == "__main__":
    main()
