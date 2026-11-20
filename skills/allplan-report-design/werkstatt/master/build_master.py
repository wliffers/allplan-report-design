# -*- coding: utf-8 -*-
"""Erzeugt den Master-Report (RDL 2016) nach out/Report_Master.rdlc.

    python build_master.py                 schreibt die .rdlc mit allen Seiten
    python build_master.py --render        rendert zusaetzlich kopflos nach aus/png (Beispieldaten daten/master.json)
    python build_master.py --nur=3 --render   nur Seite 3 bauen -> out/_Seite3.rdlc und rendern
    python build_master.py --nur=3 --render --daten=master_en  mit den englischen Beispieldaten (daten/master_en.json)
    python build_master.py --nur=3 --render --daten=gross      mit dem grossen Pruefdatensatz (daten/gross.json, 3.000 Zeilen, kuenstlich)

Ausgeliefert werden die Datensaetze master, master_en und gross (--daten=<name> nimmt jede Datei daten/<name>.json).
Jede Seite muss mit allen diesen Datensaetzen genau eine Seite ergeben.
Bilder landen in aus/png (master) bzw. aus/png_<daten>.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "seiten"))

import bausteine as b  # noqa: E402
import core as c  # noqa: E402

OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "out"))

# Jede Datei seiten/sNN_*.py ist eine Seite; die Nummer bestimmt die Reihenfolge.
SEITEN = sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "seiten")) if f[:1] == "s" and f[1:3].isdigit() and f.endswith(".py"))


def build(nur=None):
    module = SEITEN if nur is None else [m for m in SEITEN if m.startswith("s%02d_" % nur)]
    pages = []
    for m in module:
        b.SEITE_AKTUELL[0] = m
        pages.append(importlib.import_module(m).seite())
    datasets = [c.dataset("AllplanReport", b.QUERY, b.FIELDS)]
    labels = [getattr(importlib.import_module(m), "TITEL", m) for m in module]
    xml = c.report(pages, datasets, extra_params=b.PARAMS, footer_xml=b.fuss(), code=b.CODE, labels=labels,
                   embedded_xml=c.embedded(os.path.join(HERE, "bilder")))
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master.rdlc" if nur is None else "_Seite%d.rdlc" % nur)
    c.save(ziel, xml)
    if nur is None:
        katalog(module)
    return ziel


def katalog(module):
    """Bausteinverzeichnis fuer den Skill: je Kennung Name, Fundort, Datei und Funktion, Technik.
    Quelle sind die Anmeldungen (b.REGISTER) und die Etiketten (b.KATALOG) - auch die der Begleit-Reports."""
    ziel = os.path.normpath(os.path.join(HERE, "..", "out", "bausteine.md"))
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    technik = {k: t for _s, k, t in b.KATALOG}
    gruppen = [("K", "Kennzahlen und Kernaussagen"), ("D", "Diagramme"), ("M", "Messanzeigen"), ("T", "Tabellen"),
               ("B", "Bilder"), ("U", "Bedienung"), ("X", "Text, Symbole, Flächen")]
    begleit = {"build_grundriss": ("Begleit-Report Grundriss", "grundriss/build_grundriss.py"),
               "build_abwicklung": ("Begleit-Report Abwicklung", "abwicklung/build_abwicklung.py"),
               "build_wandbelag": ("Begleit-Report Wandbelag", "abwicklung/build_wandbelag.py"),
               "build_bewehrung": ("Begleit-Report Bewehrung", "bewehrung/build_bewehrung.py"),
               "build_planliste": ("Begleit-Report Planliste", "projektlisten/build_planliste.py"),
               "build_listen": ("Begleit-Report Listen", "listen/build_listen.py")}

    def ort(modul):
        if modul[:1] == "s" and modul[1:3].isdigit():
            return "Master Seite %d" % int(modul[1:3]), "seiten/%s.py" % modul
        return begleit.get(modul, (modul, modul + ".py"))

    zeilen = ["# Bausteinverzeichnis", "",
              "Erzeugt von `master/build_master.py` aus den Anmeldungen (`@b.baustein`) - nicht von Hand ändern.",
              "Die Kennung steht im Report klein unter dem Schaustück und auf Seite 10 des Masters.",
              "Bauplan = die genannte Funktion in der Datei unter `master/`; sie nimmt `(top, left, w)` und liefert das XML des Blocks.",
              "Gemeinsame Teile (Kachel, Abschnittskopf, Kennwert-Balken, Bildkarten, Klick ins Modell) in `master/bausteine.py`.", ""]
    for buchstabe, titel in gruppen:
        eintraege = sorted((k, v) for k, v in b.REGISTER.items() if k[:1] == buchstabe)
        if not eintraege:
            continue
        zeilen += ["## %s - %s" % (buchstabe, titel), "", "| Kennung | Name | Zu sehen | Datei · Funktion | Technik |", "|---|---|---|---|---|"]
        for kennung, (name, modul, funktion) in eintraege:
            wo, datei = ort(modul)
            zeilen.append("| %s | %s | %s | `%s` · `%s` | %s |" % (kennung, name, wo, datei, funktion,
                                                                 technik.get(kennung, "").replace("|", "/")))
        zeilen.append("")
    with open(ziel, "w", encoding="utf-8", newline=chr(10)) as handle:
        handle.write(chr(10).join(zeilen))


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--nur", "--daten"})
    nur = next((int(a[6:]) for a in sys.argv if a.startswith("--nur=")), None)
    ziel = build(nur)
    print(ziel)
    daten = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "master")
    if "--render" in sys.argv:
        c.rendern(ziel, os.path.join(HERE, "daten", daten + ".json"),
                  os.path.join(HERE, "aus", "png" if daten == "master" else "png_" + daten),
                  vollzugriff=True)      # volle Rechte: Code.Schrift liest die installierten Schriften (sonst Ersatzschrift Segoe UI)
