"""Kontaktbogen: je PDF die erste Seite (oder einen Ausschnitt) verkleinert in ein Raster setzen.

    python kontaktbogen.py <ziel.png> <pdf1> <pdf2> ... [--spalten=4] [--dpi=45] [--ausschnitt=l,o,r,u]
Ausschnitt in Anteilen der Seite (0..1), z. B. 0,0.12,1,0.6 fuer den oberen Tabellenteil.
"""
import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("FEHLER: Dieses Werkzeug braucht das Paket PyMuPDF. Es fehlt im Python von Allplan. Abhilfe: ein eigenes "
             "Python 3.10 oder neuer nehmen und einmal ausfuehren: python -m pip install pymupdf pillow")
from PIL import Image, ImageDraw


def main(argv):
    opts = dict(a[2:].split("=", 1) for a in argv if a.startswith("--"))
    files = [a for a in argv if not a.startswith("--")]
    if len(files) < 2:
        sys.exit("Aufruf: python kontaktbogen.py <ziel.png> <pdf1> <pdf2> ... [--spalten=4] [--dpi=45] [--ausschnitt=l,o,r,u]")
    ziel, pdfs = files[0], files[1:]
    spalten = int(opts.get("spalten", "4"))
    dpi = int(opts.get("dpi", "45"))
    crop = [float(x) for x in opts["ausschnitt"].split(",")] if "ausschnitt" in opts else None
    bilder = []
    for pdf in pdfs:
        page = pymupdf.open(pdf)[0]
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if crop:
            w, h = img.size
            img = img.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
        bilder.append((os.path.splitext(os.path.basename(pdf))[0], img))
    w = max(i.size[0] for _n, i in bilder)
    h = max(i.size[1] for _n, i in bilder) + 14
    zeilen = (len(bilder) + spalten - 1) // spalten
    bogen = Image.new("RGB", (w * spalten, h * zeilen), "white")
    draw = ImageDraw.Draw(bogen)
    for k, (name, img) in enumerate(bilder):
        x, y = (k % spalten) * w, (k // spalten) * h
        bogen.paste(img, (x, y + 14))
        draw.text((x + 3, y + 1), name, fill="red")
        draw.rectangle((x, y, x + w - 1, y + h - 1), outline="#bbbbbb")
    bogen.save(ziel)
    print(ziel, bogen.size)


if __name__ == "__main__":
    main(sys.argv[1:])
