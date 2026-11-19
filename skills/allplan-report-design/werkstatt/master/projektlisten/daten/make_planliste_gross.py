# -*- coding: utf-8 -*-
"""Kuenstlicher Pruefdatensatz fuer den Planlisten-Report: planliste_gross.json (rund 180 Plaene).

    python make_planliste_gross.py

Feldform wie die Abfrage von build_planliste.py (eine Zeile je Plan und Teilbild, Plan-Spalten auf jeder Zeile,
ein Plan ohne Teilbild = eine Zeile mit leerem Teilbild - so hat Allplan es am 2026-11-19 geliefert).
Erfunden, nichts aus einem echten Projekt: 12 Monate (2025-12 bis 2026-11), 5 Ersteller, rund ein Fuenftel ohne Namen,
viele ohne Index, Pruefer und Freigabe, lange Namen, 0 bis 3 Teilbilder je Plan, Blattgroessen A0 bis A4 und ein Sonderformat.
Derselbe Aufruf ergibt dieselbe Datei.
"""
import datetime
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HERE, "planliste_gross.json")
TYPEN = {"Plannummer": "Int", "Planname": "String", "Planindex": "String", "Erstellt": "String", "Geaendert": "String",
         "Ersteller": "String", "Pruefer": "String", "Freigabe": "String", "Planformat": "String", "Breite": "Double",
         "Hoehe": "Double", "Teilbildnummer": "Int", "Teilbildname": "String"}
ERSTELLER = ["Berger", "Lindner", "Okafor", "Vogel", "Hartmann"]
PRUEFER = ["Dr. Winter", "Kessler"]
ARTEN = ["Grundriss", "Schnitt", "Ansicht", "Detail", "Schalplan", "Bewehrungsplan", "Lageplan", "Fassadenschnitt", "Dachaufsicht",
         "Entwässerungsplan", "Fluchtwegplan Gebäudeteil", "Montageplan Treppenhaus"]
ORTE = ["Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss", "Untergeschoss", "Dachgeschoss", "Achse A-A", "Süd", "Nord", "West",
        "Treppenhaus 2 und Aufzugskern", "Hauptgebäude und Verbindungsbau Ost"]
BLAETTER = [(1189, 841), (841, 594), (594, 420), (420, 297), (297, 210), (420, 297), (594, 420), (1500, 1000)]
TBNAMEN = ["Grundriss", "Schnitt", "Ansicht", "Detail", "Decke", "Lageplan", "Achse 1-4", "Treppe"]
N_PLAENE = 180


def main():
    zufall = random.Random(2026)
    zeilen = []
    start = datetime.date(2025, 12, 1)
    tb = 100
    for i in range(N_PLAENE):
        nr = 1 + i + (i // 40) * 10                        # Luecken in der Nummerierung
        erstellt = min(start + datetime.timedelta(days=int(i * 350 / N_PLAENE) + zufall.randint(0, 6)), datetime.date(2026, 11, 19))
        geaendert = min(erstellt + datetime.timedelta(days=zufall.randint(0, 40)), datetime.date(2026, 11, 19))
        name = "" if zufall.random() < 0.2 else "%s %s" % (zufall.choice(ARTEN), zufall.choice(ORTE))
        index = "" if zufall.random() < 0.35 else chr(65 + zufall.randint(0, 5))
        ersteller = "" if zufall.random() < 0.15 else zufall.choice(ERSTELLER)
        pruefer = "" if zufall.random() < 0.6 else zufall.choice(PRUEFER)
        freigabe = None if (not pruefer or zufall.random() < 0.5) else min(geaendert + datetime.timedelta(days=3), datetime.date(2026, 11, 19)).isoformat()
        breite, hoehe = zufall.choice(BLAETTER)
        format_ = "" if zufall.random() < 0.7 else "A%d Sonder" % zufall.randint(0, 4)
        anzahl = zufall.choice([0, 0, 1, 1, 1, 2, 2, 3])
        basis = {"Plannummer": nr, "Planname": name, "Planindex": index, "Erstellt": erstellt.isoformat(),
                 "Geaendert": geaendert.isoformat(), "Ersteller": ersteller, "Pruefer": pruefer, "Freigabe": freigabe,
                 "Planformat": format_, "Breite": float(breite), "Hoehe": float(hoehe)}
        if anzahl == 0:
            zeilen.append(dict(basis, Teilbildnummer=None, Teilbildname=""))
        for _ in range(anzahl):
            tb += zufall.randint(1, 4)
            tbname = "" if zufall.random() < 0.3 else "%s %s" % (zufall.choice(TBNAMEN), zufall.choice(ORTE)[:30])
            zeilen.append(dict(basis, Teilbildnummer=tb, Teilbildname=tbname + " " * zufall.randint(0, 3)))   # Allplan liefert Leerzeichen mit
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"types": TYPEN, "rows": zeilen}, handle, ensure_ascii=False, indent=1)
    print(len(zeilen), "Zeilen,", N_PLAENE, "Plaene")


if __name__ == "__main__":
    main()
