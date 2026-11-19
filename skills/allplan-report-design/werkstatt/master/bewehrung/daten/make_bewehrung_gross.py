# -*- coding: utf-8 -*-
"""Beispieldaten fuer den Begleit-Report "Report Master Bewehrung" - reproduzierbar, ohne Allplan.

    python make_bewehrung_gross.py

Schreibt neben dieses Skript:
  bilder/bf_<Form>.png        gezeichnete Biegeform-Platzhalter (69 x 25 mm wie Allplans @205@-Bild, zehn Pixel je mm)
  bewehrung_gross.json        Pruefdatensatz: rund 300 Positionen (270 Staebe, 30 Matten), 9 Durchmesser, 3 Stahlguete,
                              6 Mattentypen, 7 Bauteile (zwei mit sehr langem Namen), 5 Geschosse, 15 Ueberlaengen
                              (Stablaenge ueber 12 m), einzelne Positionen mit mehreren Ausfuehrungen, eine sehr schwere Position,
                              4 Positionen Meterware (Form 99, LfdM 1), Stab-Positionen in mehreren Zeilen derselben Nr (ein Teil
                              davon von Allplan zusammengefasst: Einzellaenge vervielfacht, Gewicht nur einer Zeile), Matten-Positionen
                              mit mehreren verlegten Matten (je Matte eine Zeile und eine Nr)
  bewehrung_klein.json        kleinster Fall: zwei Stab-Positionen, keine Matte, keine Ueberlaenge
und ergaenzt bewehrung.json (die in Allplan gemessenen 17 Zeilen) um das Bildfeld und entfernt dort die Spalte Art:
Stab oder Matte steht im Report nie als Text in den Daten, sondern folgt der ObjId (366 und 368 = Matte).

Die Feldform ist die der Abfrage in build_bewehrung.py, auch in ihren Eigenheiten - so, wie Allplan sie liefert (gemessen in
Allplan 2027, Kopf von build_bewehrung.py): Fasst Allplan gleiche Zeilen einer Position zusammen, addiert es Anzahl, Gesamtlaenge und
Einzellaenge, das Gewicht nicht; Meterware kommt mit Anzahl 2, doppelter Einzellaenge und dem Gewicht einer Haelfte. Der Report
rechnet darum Stab-kg aus Gesamtlaenge x kg/m und die Stablaenge aus Gesamtlaenge / Anzahl. Alle Werte gelten fuer EINE
Ausfuehrung; Seite 1 multipliziert mit den Ausfuehrungen (so rechnet Allplans "Uebersicht Bewehrung").
"""
import json
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BILDER = os.path.join(HERE, "bilder")
BREITE, HOEHE = 690, 250          # 69 x 25 mm bei zehn Pixeln je Millimeter

TYPEN = {"Bauteil": "String", "Teilbild": "String", "Geschoss": "String", "Nr": "String", "ObjId": "Int", "Gebogen": "Int",
         "Position": "Int", "Anzahl": "Int", "Ausfuehrungen": "Int", "Durchmesser": "Double", "Bezeichnung": "String",
         "Stahlguete": "String", "Gesamtlaenge": "Double", "Einzellaenge": "Double", "Gewicht": "Double", "KgJeM": "Double",
         "Biegeform": "String", "Mattenname": "String", "MattenBreite": "Double", "LfdM": "String", "Bild": "Bytes"}

# Durchmesser (mm) -> kg je m (Stahl 7,85 kg/dm3, auf drei Stellen)
KG_JE_M = {6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 14: 1.21, 16: 1.58, 20: 2.47, 25: 3.85, 28: 4.83}
# Mattentyp -> kg je m2
MATTEN = {"Q188A": 3.022, "Q257A": 4.116, "Q335A": 5.431, "Q424A": 6.72, "R188A": 2.38, "R257A": 3.2}
GUETEN = ["B500B", "B500B", "B500B", "B500A", "B500C"]
FORMEN = ["00", "00", "00", "11", "21", "51"]           # 00 = gerade; die anderen sind gebogen
GESCHOSSE = ["Untergeschoss", "Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss", "Dachgeschoss"]
BAUTEILE = ["Bodenplatte", "Außenwand Treppenhaus Achse A/3-4 mit großer Öffnung", "Decke über EG", "Stütze S1", "Unterzug UZ3",
            "Treppenlauf", "Fundamentbalken F1 Achse B zwischen Achse 1 und Achse 7"]


def bild_zeichnen(form, pfad):
    """Biegeform als duenne Linienzeichnung mit kleinen Massen, so wie Allplan sie liefert (nur ein Platzhalter)."""
    img = Image.new("RGB", (BREITE, HOEHE), "white")
    d = ImageDraw.Draw(img)
    try:
        schrift = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        schrift = ImageFont.load_default()
    dunkel, mass, w = "#222222", "#777777", 4
    if form == "00":                                   # gerader Stab
        d.line([(40, 110), (650, 110)], fill=dunkel, width=w)
        d.line([(40, 90), (40, 130)], fill=mass, width=2)
        d.line([(650, 90), (650, 130)], fill=mass, width=2)
        d.text((330, 140), "500", fill=mass, font=schrift)
    elif form == "11":                                 # geschlossener Buegel
        d.rectangle([(230, 50), (470, 190)], outline=dunkel, width=w)
        d.text((330, 200), "25", fill=mass, font=schrift)
        d.text((490, 110), "14", fill=mass, font=schrift)
    elif form == "21":                                 # Stab mit einer Abbiegung
        d.line([(110, 200), (560, 200), (560, 45)], fill=dunkel, width=w)
        d.text((310, 210), "430", fill=mass, font=schrift)
        d.text((580, 110), "85", fill=mass, font=schrift)
    elif form == "51":                                 # Buegel mit Haken
        d.rectangle([(260, 50), (440, 190)], outline=dunkel, width=w)
        d.line([(260, 50), (300, 90)], fill=dunkel, width=w)
        d.text((330, 200), "24", fill=mass, font=schrift)
        d.text((455, 110), "18", fill=mass, font=schrift)
    elif form == "99":                                 # freie Form / Meterware: Polygonzug
        d.line([(40, 170), (250, 170), (330, 80), (650, 80)], fill=dunkel, width=w)
        d.text((300, 190), "lfdm", fill=mass, font=schrift)
    elif form == "51q":                                # Matte, abgekantet
        d.rectangle([(150, 60), (470, 210)], outline=dunkel, width=w)
        d.line([(470, 60), (560, 30), (560, 180), (470, 210)], fill=dunkel, width=w)
        for x in range(200, 470, 50):
            d.line([(x, 60), (x, 210)], fill=mass, width=2)
    elif form == "00q":                                # Matte
        d.rectangle([(150, 30), (540, 210)], outline=dunkel, width=w)
        for x in range(200, 540, 50):
            d.line([(x, 30), (x, 210)], fill=mass, width=2)
        for y in range(70, 210, 40):
            d.line([(150, y), (540, y)], fill=mass, width=2)
    img.save(pfad)


def bilder_schreiben():
    os.makedirs(BILDER, exist_ok=True)
    for form in ("00", "11", "21", "51", "99", "00q", "51q"):
        bild_zeichnen(form, os.path.join(BILDER, "bf_%s.png" % form))


def bild_von(form):
    return "file:bilder/bf_%s.png" % form


def stab(nr, pos, bauteil, geschoss, form, d, anzahl, einzel, guete, ausf=1, zusammen=1):
    """Eine Stab-Zeile. zusammen=k: k gleiche Zeilen, die Allplan zu einer zusammenfasst (Anzahl, Gesamtlaenge und
    Einzellaenge mal k, Gewicht nur einer Zeile - so liefert es Allplan, gemessen)."""
    gesamt = round(einzel * anzahl, 3)
    return {"Bauteil": bauteil, "Teilbild": "Report Master Bewehrung", "Geschoss": geschoss, "Nr": "0544RuB%010d" % nr,
            "ObjId": 257, "Gebogen": 0 if form in ("00", "99") else 1, "Position": pos, "Anzahl": anzahl * zusammen,
            "Ausfuehrungen": ausf, "Durchmesser": float(d), "Bezeichnung": str(d), "Stahlguete": guete,
            "Gesamtlaenge": round(gesamt * zusammen, 3), "Einzellaenge": round(einzel * zusammen, 3),
            "Gewicht": round(gesamt * KG_JE_M[d], 3), "KgJeM": KG_JE_M[d], "Biegeform": form, "Mattenname": str(d),
            "MattenBreite": 0.0, "LfdM": "0", "Bild": bild_von(form)}


def meterware(nr, pos, bauteil, geschoss, d, laenge, guete):
    """Meterware (Form 99, LfdM 1) so, wie Allplan sie liefert (gemessen): zwei gleiche Haelften zu einer Zeile zusammengefasst,
    Anzahl 2, Gesamtlaenge = laenge, Einzellaenge = 2 x laenge, Gewicht einer Haelfte. Richtig: 1 Stueck, laenge lfdm."""
    z = stab(nr, pos, bauteil, geschoss, "99", d, 1, laenge, guete)
    z.update({"Anzahl": 2, "Gesamtlaenge": laenge, "Einzellaenge": round(2 * laenge, 3),
              "Gewicht": round(laenge / 2 * KG_JE_M[d], 3), "LfdM": "1"})
    return z


def matte(nr, pos, bauteil, geschoss, typ, anzahl, laenge, breite, ausf=1):
    return {"Bauteil": bauteil, "Teilbild": "Report Master Bewehrung", "Geschoss": geschoss, "Nr": "0544MaB%010d" % nr,
            "ObjId": 368, "Gebogen": 1, "Position": pos, "Anzahl": anzahl, "Ausfuehrungen": ausf, "Durchmesser": 0.0,
            "Bezeichnung": typ, "Stahlguete": "B500A", "Gesamtlaenge": round(laenge * anzahl, 3), "Einzellaenge": laenge,
            "Gewicht": round(laenge * breite * anzahl * MATTEN[typ], 3), "KgJeM": MATTEN[typ], "Biegeform": "00q",
            "Mattenname": typ, "MattenBreite": breite, "LfdM": "0", "Bild": bild_von("00q")}


def gross():
    """Rund 300 Positionen mit fester Zufallsfolge (Startwert 2027): zwei Laeufe ergeben dieselbe Datei."""
    zufall = random.Random(2027)
    zeilen, nr, pos = [], 100, 0
    durchmesser = sorted(KG_JE_M)
    for i in range(270):
        pos += 1
        nr += 3
        d = durchmesser[(i * 5 + zufall.randrange(3)) % len(durchmesser)]
        form = zufall.choice(FORMEN)
        if form == "00":
            einzel = round(zufall.uniform(1.2, 11.9), 2)
        else:
            einzel = round(zufall.uniform(0.6, 4.8), 2)
        anzahl = zufall.choice([2, 4, 6, 8, 10, 12, 16, 20, 24, 30, 40, 60, 80, 120])
        zeilen.append(stab(nr, pos, zufall.choice(BAUTEILE), zufall.choice(GESCHOSSE), form, d, anzahl, einzel,
                           zufall.choice(GUETEN), ausf=zufall.choice([1, 1, 1, 1, 1, 1, 1, 2, 3])))
    # 15 Ueberlaengen (Einzellaenge ueber 12 m, die laengste 18 m), gerade Staebe
    for k, einzel in enumerate([12.3, 12.5, 12.5, 13.0, 13.0, 13.5, 14.0, 14.5, 15.0, 15.0, 16.0, 16.5, 17.0, 17.5, 18.0]):
        idx = 20 + k * 17
        z = zeilen[idx]
        zeilen[idx] = stab(int(z["Nr"][-10:]), z["Position"], z["Bauteil"], z["Geschoss"], "00", [16, 20, 25, 28][k % 4],
                           zufall.choice([2, 4, 6, 8]), einzel, z["Stahlguete"])
    # eine sehr schwere Position (Zahlen mit vielen Stellen) und eine mit Ausfuehrungen = 0 (zaehlt als 1)
    zeilen[7] = stab(int(zeilen[7]["Nr"][-10:]), zeilen[7]["Position"], BAUTEILE[6], GESCHOSSE[0], "00", 28, 200, 9.0, "B500B")
    zeilen[9]["Ausfuehrungen"] = 0
    # 4 Positionen Meterware (Einzellaenge ueber 12 m - darf nie als Ueberlaenge zaehlen)
    for idx, d, laenge in ((30, 14, 105.08), (95, 12, 52.54), (160, 16, 236.4), (230, 10, 48.9)):
        z = zeilen[idx]
        zeilen[idx] = meterware(int(z["Nr"][-10:]), z["Position"], z["Bauteil"], z["Geschoss"], d, laenge, z["Stahlguete"])
    # Stab-Positionen in mehreren Zeilen derselben Nr (mehrere Verlegungen); jede zweite mit von Allplan zusammengefassten
    # Zeilen (zusammen=2 oder 3: Einzellaenge vervielfacht, Gewicht einer Zeile)
    weitere = []
    for k in range(20):
        z = zeilen[40 + k * 11]
        if z["LfdM"] == "1" or z["Einzellaenge"] > 12:
            continue
        for j in range(1 + k % 3):
            weitere.append(stab(int(z["Nr"][-10:]), z["Position"], z["Bauteil"], z["Geschoss"], z["Biegeform"], int(z["Durchmesser"]),
                                zufall.choice([3, 6, 18, 36]), z["Einzellaenge"], z["Stahlguete"], z["Ausfuehrungen"],
                                zusammen=(2 + j % 2) if k % 2 == 0 else 1))
    zeilen += weitere
    # 30 Matten-Positionen; die Haelfte als einzeln verlegte Matten (je Matte eine Zeile, eigene Nr, Anzahl 1)
    for k in range(30):
        pos += 1
        typ = list(MATTEN)[(k * 7 + zufall.randrange(2)) % len(MATTEN)]
        bauteil, geschoss = zufall.choice(BAUTEILE), zufall.choice(GESCHOSSE)
        laenge, breite = zufall.choice([5.0, 6.0]), zufall.choice([2.15, 2.3])
        if k % 2 == 0:
            for _ in range(zufall.choice([2, 3, 5])):
                nr += 3
                zeilen.append(matte(nr, pos, bauteil, geschoss, typ, 1, laenge, breite))
        else:
            nr += 3
            zeilen.append(matte(nr, pos, bauteil, geschoss, typ, zufall.choice([1, 1, 2, 3, 4, 6]), laenge, breite))
    zeilen.sort(key=lambda z: z["Position"])
    return {"types": dict(TYPEN), "rows": zeilen}


def klein():
    """Kleinster Fall: zwei Stab-Positionen, keine Matte."""
    return {"types": dict(TYPEN), "rows": [
        stab(2, 1, "Stütze S1", "Erdgeschoss", "00", 12, 10, 4.0, "B500B"),
        stab(6, 2, "Stütze S1", "Erdgeschoss", "51", 8, 20, 1.2, "B500B")]}


def basis_ergaenzen():
    """bewehrung.json (aus Allplan): Spalte Art entfernen, Bildfeld ergaenzen. Mehrfach ausfuehrbar."""
    pfad = os.path.join(HERE, "bewehrung.json")
    with open(pfad, encoding="utf-8") as handle:
        daten = json.load(handle)
    daten["types"].pop("Art", None)
    daten["types"].pop("Bild", None)
    daten["types"]["LfdM"] = "String"           # das Probemodell hat keine Meterware (Allplans Stabliste: alle 12 mit Laenge)
    daten["types"]["Bild"] = "Bytes"
    for zeile in daten["rows"]:
        zeile.pop("Art", None)
        bild = zeile.pop("Bild", None)
        zeile.setdefault("LfdM", "0")
        zeile["Bild"] = bild or bild_von(zeile["Biegeform"])
    schreiben(pfad, daten)
    return daten


def schreiben(pfad, daten):
    with open(pfad, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(daten, handle, ensure_ascii=False, indent=1)


def kennzahlen(name, daten):
    """Kennzahlen nach den Rechenregeln des Reports (Stab-kg = Gesamtlaenge x kg/m, Matten-kg je Matte auf 2 Stellen)."""
    zeilen = daten["rows"]
    stab_kg = sum(z["Gesamtlaenge"] * z["KgJeM"] * max(1, z["Ausfuehrungen"]) for z in zeilen if z["ObjId"] not in (366, 368))
    matte_kg = sum(round(z["Gewicht"], 2) * max(1, z["Ausfuehrungen"]) for z in zeilen if z["ObjId"] in (366, 368))
    ueber = len({z["Nr"] for z in zeilen if z["ObjId"] not in (366, 368) and z.get("LfdM") != "1"
                 and z["Gesamtlaenge"] / max(1, z["Anzahl"]) > 12})
    print("%-18s %3d Zeilen  Rundstahl %10.1f kg  Matten %9.1f kg  gesamt %10.1f kg  Ueberlaengen %d"
          % (name, len(zeilen), stab_kg, matte_kg, stab_kg + matte_kg, ueber))


if __name__ == "__main__":
    bilder_schreiben()
    for dateiname, quelle in (("bewehrung_gross.json", gross()), ("bewehrung_klein.json", klein()), ("bewehrung.json", None)):
        if quelle is None:
            quelle = basis_ergaenzen()
        else:
            schreiben(os.path.join(HERE, dateiname), quelle)
        kennzahlen(dateiname, quelle)
