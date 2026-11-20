# -*- coding: utf-8 -*-
"""Zeichnet die eingebetteten Bilder des Master-Reports: Piktogramme je Bauteilart und Musterflaechen
je Material. Eingebettet heisst: die Bilder stecken in der .rdlc, der Report braucht keine Dateien.

    python make_bilder.py      -> schreibt die PNG neben dieses Skript
Gezeichnet wird vierfach vergroessert und dann verkleinert (glatte Kanten).
"""
import os
import random
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import core as c  # noqa: E402  (Farben des Gestaltungssystems; Materialmuster behalten ihre Materialfarben)


def rgba(hexfarbe):
    return tuple(int(hexfarbe[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


INK = rgba(c.INK)        # Piktogramme in der Tintenfarbe des Designs
BLUE = rgba(c.BLUE)      # Akzentstellen der Piktogramme in der Leitfarbe
S = 4          # Ueberabtastung
N = 96         # Kantenlaenge der fertigen Bilder


def canvas():
    img = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def save(img, name):
    img.resize((N, N), Image.LANCZOS).save(os.path.join(HERE, name + ".png"))


def p(*werte):
    return [w * S for w in werte]


def icon_wand():
    img, d = canvas()
    d.rectangle(p(10, 34, 86, 62), outline=INK, width=3 * S)
    for x in (29, 48, 67):
        d.line(p(x, 34, x, 62), fill=INK, width=2 * S)
    save(img, "icon_wand")


def icon_stuetze():
    img, d = canvas()
    d.rectangle(p(36, 12, 60, 84), outline=INK, width=3 * S)
    d.line(p(26, 84, 70, 84), fill=INK, width=3 * S)
    d.line(p(26, 12, 70, 12), fill=INK, width=3 * S)
    save(img, "icon_stuetze")


def icon_decke():
    img, d = canvas()
    d.polygon(p(10, 52, 48, 34, 86, 52, 48, 70), outline=INK, width=3 * S)
    d.line(p(10, 52, 10, 60, 48, 78, 86, 60, 86, 52), fill=INK, width=3 * S, joint="curve")
    d.line(p(48, 70, 48, 78), fill=INK, width=3 * S)
    save(img, "icon_decke")


def icon_unterzug():
    img, d = canvas()
    d.rectangle(p(10, 38, 86, 54), outline=INK, width=3 * S)
    d.rectangle(p(16, 54, 28, 84), outline=INK, width=3 * S)
    d.rectangle(p(68, 54, 80, 84), outline=INK, width=3 * S)
    save(img, "icon_unterzug")


def icon_bodenplatte():
    img, d = canvas()
    d.rectangle(p(8, 56, 88, 70), outline=INK, width=3 * S)
    for x in range(14, 88, 12):
        d.line(p(x, 78, x - 6, 86), fill=INK, width=2 * S)
    d.line(p(8, 78, 88, 78), fill=INK, width=2 * S)
    save(img, "icon_bodenplatte")


def icon_raum():
    img, d = canvas()
    d.line(p(14, 82, 14, 14, 82, 14, 82, 82, 52, 82), fill=INK, width=3 * S, joint="curve")
    d.line(p(14, 82, 26, 82), fill=INK, width=3 * S)
    d.arc(p(26 - 26, 82 - 26, 26 + 26, 82 + 26), 270, 360, fill=BLUE, width=2 * S)
    d.line(p(26, 82, 26, 56), fill=BLUE, width=2 * S)
    save(img, "icon_raum")


def icon_fenster():
    img, d = canvas()
    d.rectangle(p(18, 14, 78, 82), outline=INK, width=3 * S)
    d.line(p(48, 14, 48, 82), fill=INK, width=2 * S)
    d.line(p(18, 48, 78, 48), fill=INK, width=2 * S)
    save(img, "icon_fenster")


def icon_tuer():
    img, d = canvas()
    d.rectangle(p(28, 10, 68, 86), outline=INK, width=3 * S)
    d.ellipse(p(57, 46, 63, 52), fill=BLUE)
    save(img, "icon_tuer")


def muster_beton():
    random.seed(7)
    img, d = canvas()
    d.rectangle(p(0, 0, N, N), fill=(71, 85, 105, 255))
    for _ in range(170):
        x, y, r = random.uniform(0, N), random.uniform(0, N), random.uniform(0.5, 1.8)
        ton = random.choice([(100, 116, 139, 255), (51, 65, 85, 255), (148, 163, 184, 255)])
        d.ellipse(p(x - r, y - r, x + r, y + r), fill=ton)
    save(img, "muster_beton")


def muster_mauerwerk():
    img, d = canvas()
    d.rectangle(p(0, 0, N, N), fill=(194, 65, 12, 255))
    fuge = (254, 215, 170, 255)
    for i, y in enumerate(range(0, N + 1, 16)):
        d.line(p(0, y, N, y), fill=fuge, width=2 * S)
        for x in range(-16 if i % 2 else 0, N + 1, 32):
            d.line(p(x, y, x, y + 16), fill=fuge, width=2 * S)
    save(img, "muster_mauerwerk")


def muster_daemmung():
    img, d = canvas()
    d.rectangle(p(0, 0, N, N), fill=(234, 179, 8, 255))
    hell = (254, 240, 138, 255)
    for y in range(-8, N + 16, 16):
        punkte = []
        for k, x in enumerate(range(0, N + 13, 12)):
            punkte += [x, y + (8 if k % 2 else 0)]
        d.line(p(*punkte), fill=hell, width=2 * S, joint="curve")
    save(img, "muster_daemmung")


def muster_gipskarton():
    img, d = canvas()
    d.rectangle(p(0, 0, N, N), fill=(148, 163, 184, 255))
    hell = (203, 213, 225, 255)
    for x in (32, 64):
        d.line(p(x, 0, x, N), fill=hell, width=2 * S)
    for x in (16, 48, 80):
        for y in range(10, N, 20):
            d.ellipse(p(x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=hell)
    save(img, "muster_gipskarton")


if __name__ == "__main__":
    for fn in (icon_wand, icon_stuetze, icon_decke, icon_unterzug, icon_bodenplatte, icon_raum, icon_fenster, icon_tuer,
               muster_beton, muster_mauerwerk, muster_daemmung, muster_gipskarton):
        fn()
    namen = sorted(f for f in os.listdir(HERE) if f.endswith(".png") and not f.startswith("_"))
    bogen = Image.new("RGBA", (N * len(namen) + 8 * (len(namen) + 1), N + 16), (255, 255, 255, 255))
    for i, f in enumerate(namen):
        bild = Image.open(os.path.join(HERE, f))
        bogen.paste(bild, (8 + i * (N + 8), 8), bild)
    bogen.save(os.path.join(HERE, "_alle.png"))
    print(len(namen), "Bilder")
