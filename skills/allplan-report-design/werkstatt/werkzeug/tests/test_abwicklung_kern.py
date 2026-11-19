# -*- coding: utf-8 -*-
"""Pruefungen des Rechenkerns der Raum-Abwicklung - ohne Allplan.

    python -m pytest werkzeug/tests/test_abwicklung_kern.py
    python werkzeug/tests/test_abwicklung_kern.py <ordner>      schreibt zusaetzlich faelle.json fuer die Vorschau
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import abwicklung_kern as kern  # noqa: E402


def koerper(a, b, von, bis, tiefe, unten, oben, aussen_links=True):
    """Oeffnungskoerper in der Wand hinter der Kante a->b: von/bis laengs, 'tiefe' nach aussen."""
    lang = math.hypot(b[0] - a[0], b[1] - a[1])
    u = ((b[0] - a[0]) / lang, (b[1] - a[1]) / lang)
    n = (-u[1], u[0]) if aussen_links else (u[1], -u[0])
    return [(a[0] + u[0] * s + n[0] * q, a[1] + u[1] * s + n[1] * q, z)
            for z in (unten, oben) for s in (von, bis) for q in (0.0, tiefe)]


# L-Raum (gegen den Uhrzeigersinn gezeichnet: aussen ist RECHTS der Zeichenrichtung)
L_PUNKTE = [(0, 0), (6, 0), (6, 2.5), (3.5, 2.5), (3.5, 5), (0, 5)]
L_RAUM = {"id": "L", "nr": "0001Rau0000000001", "name": "L-Raum", "punkte": L_PUNKTE, "z0": 0.0, "hoehe": 2.6}
L_OEFFNUNGEN = [
    {"art": "tuer", "ecken": koerper((0, 0), (6, 0), 1.0, 1.9, 0.24, 0.0, 2.1, aussen_links=False)},
    {"art": "fenster", "ecken": koerper((0, 5), (0, 0), 1.5, 3.0, 0.36, 0.9, 2.2, aussen_links=False)},
    {"art": "tuer", "ecken": koerper((6, 2.5), (3.5, 2.5), 0.4, 1.3, 0.24, 0.0, 2.1, aussen_links=False)},
    {"art": "fenster", "ecken": koerper((6, 0), (6, 2.5), 0.4, 0.9, 0.36, 1.0, 2.0, aussen_links=False)},
]
# Raum mit zwei schraegen Waenden
S_PUNKTE = [(0, 0), (5, 0), (6.5, 3), (2, 4.2), (0, 3.2)]
S_RAUM = {"id": "S", "nr": "0001Rau0000000002", "name": "Schräger Raum", "punkte": S_PUNKTE, "z0": 0.1, "hoehe": 2.75}
S_OEFFNUNGEN = [
    {"art": "tuer", "ecken": koerper((5, 0), (6.5, 3), 1.0, 1.9, 0.30, 0.1, 2.2, aussen_links=False)},
    {"art": "fenster", "ecken": koerper((6.5, 3), (2, 4.2), 1.2, 3.2, 0.36, 1.0, 2.35, aussen_links=False)},
]
# Langer Flur, Tueren dicht an dicht (Abschnitte von 0,20 m)
F_PUNKTE = [(0, 0), (22, 0), (22, 1.6), (0, 1.6)]
F_RAUM = {"id": "F", "nr": "0001Rau0000000003", "name": "Langer Flur", "punkte": F_PUNKTE, "z0": 0.0, "hoehe": 2.5}
F_OEFFNUNGEN = ([{"art": "tuer", "ecken": koerper((0, 0), (22, 0), 0.3 + i * 1.085, 1.185 + i * 1.085, 0.2, 0.0, 2.01,
                                                  aussen_links=False)} for i in range(8)]
                + [{"art": "tuer", "ecken": koerper((22, 0), (22, 1.6), 0.2, 1.4, 0.2, 0.0, 2.1, aussen_links=False)}])
FAELLE = [(L_RAUM, L_OEFFNUNGEN), (S_RAUM, S_OEFFNUNGEN), (F_RAUM, F_OEFFNUNGEN)]


def test_band_ist_so_lang_wie_der_umfang():
    for raum, oeffnungen in FAELLE:
        info = kern.abwicklung(raum, oeffnungen)["info"]
        punkte = raum["punkte"]
        umfang = sum(math.dist(punkte[i], punkte[(i + 1) % len(punkte)]) for i in range(len(punkte)))
        assert abs(info["umfang_m"] - umfang) < 0.001, raum["name"]       # info ist auf mm gerundet
        assert abs(sum(info["waende_m"]) - umfang) < 0.005


def test_umlauf_im_uhrzeigersinn_start_an_laengster_wand():
    for punkte in (L_PUNKTE, list(reversed(L_PUNKTE)), S_PUNKTE):
        umriss = kern.ring(punkte)
        assert kern._flaeche(umriss) < 0                                   # pylint: disable=protected-access
        laengen = [k["laenge"] for k in kern.waende(umriss)]
        assert abs(laengen[0] - max(laengen)) < 1e-9


def test_jede_oeffnung_landet_in_genau_einer_wand():
    for raum, oeffnungen in FAELLE:
        info = kern.abwicklung(raum, oeffnungen)["info"]
        assert info["tueren"] + info["fenster"] == len(oeffnungen), raum["name"]


def test_schraege_wand_traegt_ihre_tuer_in_wahrer_laenge():
    kanten = kern.waende(kern.ring(S_PUNKTE))
    kern.oeffnungen_zuordnen(kanten, S_OEFFNUNGEN, 0.1, 2.75)
    schraeg = [k for k in kanten if abs(k["laenge"] - math.dist((5, 0), (6.5, 3))) < 1e-6][0]
    assert len(schraeg["oeffnungen"]) == 1
    tuer = schraeg["oeffnungen"][0]
    assert abs((tuer["rechts"] - tuer["links"]) - 0.9) < 1e-6
    assert abs(tuer["unten"]) < 1e-9 and abs(tuer["oben"] - 2.1) < 1e-6


def test_jeder_abschnitt_hat_eine_zahl_und_keine_beruehrt_die_andere():
    for raum, oeffnungen in FAELLE:
        bild = kern.abwicklung(raum, oeffnungen)
        k = bild["info"]["k"]
        zahlen = [t for t in bild["texte"] if t["ausrichtung"] == "mitte_oben" and t["farbe"] == kern.TEXT_GRAU]
        assert len(zahlen) == bild["info"]["abschnitte"], raum["name"]
        kaesten = []
        for t in zahlen:
            halb = len(t["text"]) * kern.ZEICHEN * t["hoehe_m"] / 2
            kaesten.append((t["x"] - halb, t["x"] + halb, t["y"] - t["hoehe_m"], t["y"]))
        for i, a in enumerate(kaesten):
            for b in kaesten[i + 1:]:
                ueberlappt = a[0] < b[1] - 1e-9 and b[0] < a[1] - 1e-9 and a[2] < b[3] - 1e-9 and b[2] < a[3] - 1e-9
                assert not ueberlappt, (raum["name"], a, b, k)


def test_alles_liegt_im_rahmen():
    for raum, oeffnungen in FAELLE:
        bild = kern.abwicklung(raum, oeffnungen, 10.0, -5.0)
        r = bild["rahmen"]
        for li in bild["linien"]:
            for i in range(0, len(li["punkte"]), 2):
                assert r["x"] - 1e-6 <= li["punkte"][i] <= r["x"] + r["laenge"] + 1e-6, raum["name"]
                assert r["y"] - 1e-6 <= li["punkte"][i + 1] <= r["y"] + r["breite"] + 1e-6, raum["name"]


def test_englisch_hat_punkt_und_englische_worte():
    bild = kern.abwicklung(L_RAUM, L_OEFFNUNGEN, sprache="en")
    texte = " ".join(t["text"] for t in bild["texte"])
    import re
    assert "Wall 1" in texte and "Door" in texte and "Window" in texte
    assert re.search(r"\d\.\d\d", texte) and not re.search(r"\d,\d", texte)


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(ziel, exist_ok=True)
    raeume, oeffnungen = [], []
    for nr, (raum, liste) in enumerate(FAELLE):                 # nebeneinander legen: die Faelle teilen sich sonst den Ursprung
        dx = nr * 30.0
        raeume.append(dict(raum, punkte=[(x + dx, y) for x, y in raum["punkte"]]))
        oeffnungen += [dict(o, ecken=[(x + dx, y, z) for x, y, z in o["ecken"]]) for o in liste]
    with open(os.path.join(ziel, "faelle.json"), "w", encoding="utf-8") as handle:
        json.dump({"raeume": raeume, "oeffnungen": oeffnungen}, handle, ensure_ascii=False)
    print(os.path.join(ziel, "faelle.json"))


def test_netto_wandflaeche_stimmt_mit_allplan_ueberein():
    """Echte Daten des eigenen Master-Gebaeudes (9 Raeume, gelesen 2026-11-18): Allplan rechnet die Netto-Wandflaeche
    selbst (Attribut 295 am Raum). Der Kern muss auf dasselbe kommen - das beweist, dass jede Oeffnung in der
    richtigen Wand landet. Ein Raum weicht um 0,2 m2 ab (Stuetze im Raum), daher die Toleranz."""
    import abwicklung_zeichnen as zeichnen

    pfad = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daten", "master_elemente.json")
    with open(pfad, encoding="utf-8") as handle:
        elemente = json.load(handle)["elements"]
    raeume, oeffnungen, _ecke = zeichnen.aus_elementliste(elemente)
    allplan = {e["id"]: dict((nr, wert) for nr, wert in e["attribute"])[295] for e in elemente if e["typ"] == "raum"}
    assert len(raeume) == 9
    for raum in raeume:
        netto = kern.abwicklung(raum, oeffnungen)["info"]["wandflaeche_netto_m2"]
        assert abs(netto - allplan[raum["id"]]) < 0.25, (raum["name"], netto, allplan[raum["id"]])
