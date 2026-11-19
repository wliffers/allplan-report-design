# -*- coding: utf-8 -*-
"""Beispieldaten fuer den Wandbelag-Report aus dem eigenen Testgebaeude: master_abw.json -> wandbelag_bsp.json.

    python make_wandbelag_bsp.py

Quelle sind die 9 Raeume des eigenen Testgebaeudes in master_abw.json (Nr, Funktion, Umfang, Hoehe, Seitenflaeche).
Je Raum entstehen zwei Zeilen in der Feldform, die die Abfrage von build_wandbelag.py liefert:
  /01  Innenputz (Putz- und Stuckarbeiten), Flaeche = Seitenflaeche des Raums, Dicke 15 mm
  /02  Anstrich (Maler- und Lackierarbeiten), Flaeche = 97 % der Seitenflaeche, Dicke 0 mm
Die Leibung (Laibungsflaeche der Oeffnungen, 0 bis 6 m) ist ein fester, erfundener Wert je Raum: das Testgebaeude hat
keine Raumausbau-Seitenflaechen (@OBJ@ = 62), aus denen Allplan sie liefern koennte.
Das Feld Bild bleibt leer (null): der Report zeigt die Aufmassskizze nicht (siehe build_wandbelag.py), er braucht kein Bild.
Der Datensatz enthaelt keine Angaben aus fremden Projekten; derselbe Aufruf ergibt dieselbe Datei.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HERE, "master_abw.json")
ZIEL = os.path.join(HERE, "wandbelag_bsp.json")

TYPEN = {"Nr": "String", "Gewerk": "String", "Material": "String", "Raum": "String", "Funktion": "String",
         "RaumNr": "String", "Flaeche": "Double", "Bild": "Bytes", "Abmessungen": "String", "Dicke": "Double",
         "Leibung": "Double"}
BELAEGE = [("/01", "Putz- und Stuckarbeiten", "Innenputz", 1.0, 15.0), ("/02", "Maler- und Lackierarbeiten", "Anstrich", 0.97, 0.0)]


def main():
    with open(QUELLE, encoding="utf-8") as handle:
        raeume = [z for z in json.load(handle)["rows"] if z["ObjNr"] == "61"]
    zeilen = []
    for i, raum in enumerate(sorted(raeume, key=lambda z: z["Nr"])):
        raum_nr = raum["Nr"]
        sfl_nr = raum_nr.replace("Rau", "Sfl")                    # "0540Rau0000002353" -> "0540Sfl0000002353"
        brutto = raum["Umfang"] * raum["Hoehe"]
        abmessung = "%.3f*%.3f-%.3f" % (raum["Umfang"], raum["Hoehe"], brutto - raum["Seitenflaeche"])   # Umfang x Hoehe - Oeffnungen
        leibung = round((i * 1.9) % 6.0, 3)
        for endung, gewerk, material, faktor, dicke in BELAEGE:
            zeilen.append({"Nr": sfl_nr + endung, "Gewerk": gewerk, "Material": material, "Raum": "0.%02d" % (i + 1),
                           "Funktion": raum["Funktion"], "RaumNr": raum_nr, "Flaeche": round(raum["Seitenflaeche"] * faktor, 3),
                           "Bild": None, "Abmessungen": abmessung, "Dicke": dicke, "Leibung": leibung})
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"types": TYPEN, "rows": zeilen}, handle, ensure_ascii=False, indent=1)
    print(len(zeilen), "Zeilen aus", len(raeume), "Raeumen")


if __name__ == "__main__":
    main()
