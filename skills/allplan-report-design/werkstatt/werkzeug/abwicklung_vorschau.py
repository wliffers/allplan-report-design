# -*- coding: utf-8 -*-
"""Vorschau der gerechneten Raum-Abwicklung ohne Allplan: zeichnet je Rahmen ein PNG in Report-Groesse.

    python abwicklung_vorschau.py <auftrag.json> <ausgabeordner> [--dpi=150]

Dient nur dem schnellen Blick auf Aufteilung und Ueberlappungen; Beweis bleibt der Report aus Allplan.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ANKER = {"links_unten": "ls", "mitte_unten": "ms", "rechts_unten": "rs", "links_mitte": "lm", "mitte": "mm",
         "rechts_mitte": "rm", "links_oben": "lt", "mitte_oben": "mt", "rechts_oben": "rt"}


def main():
    if len([a for a in sys.argv[1:] if not a.startswith("--")]) != 2:
        sys.exit("Aufruf: python abwicklung_vorschau.py <auftrag.json> <ausgabeordner> [--dpi=150]")
    quelle, ordner = sys.argv[1], sys.argv[2]
    dpi = next((float(a[6:]) for a in sys.argv if a.startswith("--dpi=")), 150.0)
    with open(quelle, encoding="utf-8") as handle:
        auftrag = json.load(handle)
    os.makedirs(ordner, exist_ok=True)
    scale = auftrag["teilbild_massstab"]
    for nr, (rahmen, raum) in enumerate(zip(auftrag["rahmen"], auftrag["raeume"]), 1):
        x0, y0, b, h = rahmen["x"], rahmen["y"], rahmen["length"], rahmen["width"]
        px = 170.0 / 25.4 * dpi / b                              # Pixel je Modellmeter (Feld 170 mm breit)
        bild = Image.new("RGB", (int(b * px), int(h * px)), "white")
        zeichner = ImageDraw.Draw(bild)

        def punkt(x, y):
            return (x - x0) * px, (y0 + h - y) * px

        def innen(x, y):
            return x0 - 1e-6 <= x <= x0 + b + 1e-6 and y0 - 1e-6 <= y <= y0 + h + 1e-6

        for f in auftrag["flaechen"]:
            p = f["punkte"]
            if innen(p[0], p[1]):
                zeichner.polygon([punkt(p[i], p[i + 1]) for i in range(0, len(p), 2)], fill=f["fuellfarbe"])
        for li in auftrag["linien"]:
            p = li["punkte"]
            if innen(p[0], p[1]):
                zug = [punkt(p[i], p[i + 1]) for i in range(0, len(p), 3)]
                if li.get("geschlossen"):
                    zug.append(zug[0])
                zeichner.line(zug, fill="black", width=1)
        for t in auftrag["texte"]:
            if not innen(t["x"], t["y"]):
                continue
            hoehe_m = t["texthoehe"] * scale / 1000.0
            schrift = ImageFont.truetype("arial.ttf", max(4, int(round(hoehe_m * px * 1.35))))
            if t.get("angle"):
                breite = int(zeichner.textlength(t["text"], font=schrift)) + 4
                kachel = Image.new("RGBA", (breite, schrift.size + 6), (255, 255, 255, 0))
                ImageDraw.Draw(kachel).text((2, 2), t["text"], font=schrift, fill=t.get("textfarbe") or "black")
                kachel = kachel.rotate(t["angle"], expand=True)
                cx, cy = punkt(t["x"], t["y"])
                bild.paste(kachel, (int(cx - kachel.width), int(cy - kachel.height / 2)), kachel)
            else:
                zeichner.text(punkt(t["x"], t["y"]), t["text"], font=schrift, fill=t.get("textfarbe") or "black",
                              anchor=ANKER[t["ausrichtung"]])
        zeichner.rectangle([0, 0, bild.width - 1, bild.height - 1], outline="#94A3B8")
        ziel = os.path.join(ordner, "abwicklung_%02d.png" % nr)
        bild.save(ziel)
        print(ziel, raum["name"], "1:%d" % raum["massstab_1_zu"])


if __name__ == "__main__":
    main()
