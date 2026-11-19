"""PDF-Seiten als PNG ablegen (PyMuPDF), damit ein exportierter Report angesehen werden kann.

    python pdf_zu_png.py <datei.pdf> [<ausgabeordner>] [--dpi=110] [--seiten=1-3]
"""
import os
import sys

try:
    import pymupdf as fitz
except ImportError:
    sys.exit("FEHLER: Dieses Werkzeug braucht das Paket PyMuPDF. Es fehlt im Python von Allplan. Abhilfe: ein eigenes "
             "Python 3.10 oder neuer nehmen und einmal ausfuehren: python -m pip install pymupdf pillow")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        sys.exit("Aufruf: python pdf_zu_png.py <datei.pdf> [<ausgabeordner>] [--dpi=110] [--seiten=1-3]")
    opts = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    pdf = args[0]
    out = args[1] if len(args) > 1 else os.path.dirname(os.path.abspath(pdf))
    dpi = int(opts.get("dpi", "110"))
    os.makedirs(out, exist_ok=True)
    doc = fitz.open(pdf)
    first, last = 1, doc.page_count
    if "seiten" in opts:
        teile = opts["seiten"].split("-")
        first, last = int(teile[0]), int(teile[-1])
    base = os.path.splitext(os.path.basename(pdf))[0]
    for nr in range(first, min(last, doc.page_count) + 1):
        ziel = os.path.join(out, "%s_S%d.png" % (base, nr))
        doc[nr - 1].get_pixmap(dpi=dpi).save(ziel)
        print(ziel)
    print("Seiten gesamt:", doc.page_count)


if __name__ == "__main__":
    main(sys.argv[1:])
