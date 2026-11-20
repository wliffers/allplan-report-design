# -*- coding: utf-8 -*-
"""Rechenregeln des Begleit-Reports Bewehrung (master/bewehrung/build_bewehrung.py) - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_bewehrung.py -q

Eine kleine Python-Nachrechnung derselben Formeln, die der Report als VB-Ausdruck rechnet, gegen die Sollwerte aus Allplans
eigenen Listen (Stabliste Biegeformen, Mattenstahlliste, Uebersicht Bewehrung): Probemodell (bewehrung.json),
Fall A (bewehrung_fall_a.json = echtes Teilbild, neutralisiert) und Fall B (bewehrung_fall_b.json = zweites echtes
Teilbild, Ausfuehrungen auf 2 gesetzt).
Dazu: die VB-Ausdruecke selbst sind festgeschrieben - wer die Formel im Report aendert, muss diese Datei
mitaendern und die Sollwerte in Allplan neu belegen.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.normpath(os.path.join(HERE, "..", ".."))
DATEN = os.path.join(REPORT, "master", "bewehrung", "daten")
sys.path.insert(0, os.path.join(REPORT, "master", "bewehrung"))
sys.path.insert(0, os.path.join(REPORT, "master"))

import build_bewehrung as bw  # noqa: E402


# ---------------------------------------------------------------- Nachrechnung (dieselben Regeln wie die VB-Ausdruecke)
def ist_matte(z):
    return int(z["ObjId"]) in (366, 368)


def ausf(z):
    return max(1.0, float(z["Ausfuehrungen"] or 0))


def ist_lfdm(z):
    return float(z.get("LfdM") or 0) >= 1


def kg1(z):
    """kg je Ausfuehrung: Matte = Feld Gewicht auf 2 Stellen, Stab = Gesamtlaenge x kg/m (nie das Feld Gewicht)."""
    return round(z["Gewicht"], 2) if ist_matte(z) else z["Gesamtlaenge"] * z["KgJeM"]


def einzel(z):
    """Stablaenge einzeln = Gesamtlaenge / Anzahl (nie das Feld Einzellaenge)."""
    return z["Gesamtlaenge"] / max(1.0, float(z["Anzahl"]))


def nachrechnen(zeilen, lager=12.0):
    stab = [z for z in zeilen if not ist_matte(z)]
    matte = [z for z in zeilen if ist_matte(z)]
    stabliste = {}                                   # je Nr (= eine Position)
    for z in stab:
        stabliste.setdefault(z["Nr"], []).append(z)
    zeilen_stab = {}
    for zs in stabliste.values():
        lf = any(ist_lfdm(z) for z in zs)
        anzahl = sum(z["Anzahl"] for z in zs)
        gesamt = sum(z["Gesamtlaenge"] for z in zs)
        zeilen_stab[zs[0]["Position"]] = (1 if lf else anzahl, "lfdm" if lf else round(gesamt / max(1, anzahl), 2),
                                          gesamt, sum(kg1(z) for z in zs))
    mattenliste = {}                                 # je Teilbild/Bauteil/Position/Typ/Mass
    for z in matte:
        k = (z["Teilbild"], z["Bauteil"], z["Position"], z["Mattenname"], round(z["Einzellaenge"], 3), round(z["MattenBreite"], 3))
        mattenliste.setdefault(k, []).append(z)
    zeilen_matte = {k[2]: (sum(z["Anzahl"] for z in zs), sum(kg1(z) for z in zs)) for k, zs in mattenliste.items()}
    rund = sum(kg1(z) * ausf(z) for z in stab)
    mat = sum(kg1(z) * ausf(z) for z in matte)
    return {
        "stabliste": zeilen_stab, "mattenliste": zeilen_matte,
        "stab_stueck": sum(0 if ist_lfdm(z) else z["Anzahl"] for z in stab) + len({z["Nr"] for z in stab if ist_lfdm(z)}),
        "stab_laenge": sum(z["Gesamtlaenge"] for z in stab),
        "stab_kg1": sum(kg1(z) for z in stab), "matte_kg1": sum(kg1(z) for z in matte),
        "rund": rund, "matten": mat, "gesamt": round(rund, 1) + round(mat, 1),
        "n_stab": len(stabliste), "n_matte": len({(z["Teilbild"], z["Bauteil"], z["Position"]) for z in matte}),
        "gebogen": sum(kg1(z) * ausf(z) for z in stab if int(z["Gebogen"]) == 1),
        "mittel_d": sum(z["Durchmesser"] * kg1(z) * ausf(z) for z in stab) / rund if rund else 0.0,
        "ueber": len({z["Nr"] for z in stab if not ist_lfdm(z) and einzel(z) > lager}),
    }


def lade(name):
    with open(os.path.join(DATEN, name + ".json"), encoding="utf-8") as handle:
        return json.load(handle)["rows"]


# ---------------------------------------------------------------- Sollwerte aus Allplans eigenen Listen (Allplan 2027, PDF-Ausgabe)
# Stabliste Biegeformen: Position -> (Stueck, Einzellaenge, Gesamtlaenge, Gewicht); Mattenstahlliste: Position -> (Stueck, Gewicht)
SOLL = {
    "bewehrung": {
        "ausf": 1,
        "stabliste": {1: (25, 5.00, 125.00, 111.00), 2: (30, 4.00, 120.00, 106.56), 3: (25, 5.16, 129.00, 79.59),
                      4: (40, 1.41, 56.40, 34.80), 5: (30, 1.84, 55.20, 21.80), 6: (20, 1.20, 24.00, 9.48),
                      7: (8, 6.00, 48.00, 75.84), 8: (6, 7.50, 45.00, 111.15), 9: (12, 2.22, 26.64, 42.09),
                      10: (4, 13.00, 52.00, 200.20), 11: (16, 1.71, 27.36, 33.11), 12: (2, 9.00, 18.00, 86.94)},
        "mattenliste": {20: (1, 34.75), 21: (1, 34.75), 22: (1, 34.75), 30: (1, 56.80), 31: (1, 56.80)},
        "stab_summe": 912.56, "matte_summe": 217.85, "uebersicht": (912.6, 217.9, 1130.5),
        "gebogen": 31.3 + 114.4 + 33.1 + 42.1, "n_stab": 12, "n_matte": 5, "ueber": 1,
    },
    "bewehrung_fall_a": {
        "ausf": 1,
        "stabliste": {1: (152, 2.62, 398.24, 245.71), 2: (8, 6.32, 50.56, 61.18), 3: (4, 6.32, 25.28, 22.45),
                      4: (1, "lfdm", 105.08, 127.15), 5: (1, "lfdm", 52.54, 46.66), 6: (225, 3.18, 715.50, 441.46)},
        "mattenliste": {1: (5, 88.25), 2: (1, 3.38), 3: (3, 125.10), 4: (2, 41.70), 5: (2, 45.94), 6: (1, 14.41), 7: (1, 15.88),
                        8: (2, 113.60), 9: (1, 56.61), 10: (1, 28.40), 11: (1, 31.43), 12: (1, 51.74), 13: (1, 51.56)},
        "stab_summe": 944.61, "matte_summe": 668.00, "uebersicht": (944.6, 668.0, 1612.6),
        "gebogen": 687.2, "n_stab": 6, "n_matte": 13, "ueber": 0,
    },
    "bewehrung_fall_b": {
        "ausf": 2,
        "stabliste": {1: (168, 2.62, 440.16, 271.58), 2: (4, 7.32, 29.28, 35.43), 3: (2, 7.31, 14.62, 12.98),
                      4: (1, "lfdm", 105.08, 127.15), 5: (1, "lfdm", 52.54, 46.66), 6: (239, 3.18, 760.02, 468.93),
                      7: (4, 7.31, 29.24, 35.38), 8: (2, 7.31, 14.62, 12.98)},
        "mattenliste": {1: (5, 88.25), 2: (1, 3.38), 3: (3, 125.10), 4: (2, 41.70), 6: (1, 14.41), 8: (2, 113.60), 9: (1, 56.61),
                        10: (1, 28.40), 11: (1, 31.43), 12: (1, 51.74), 13: (1, 51.56), 20: (3, 27.21), 21: (2, 59.84),
                        22: (1, 20.68)},
        # Allplans Listen je Ausfuehrung (gemessen, Ausfuehrungen 1); "Gesamtgewicht = Summe x Ausfuehrungen" (Allplans Regel)
        "stab_summe": 1011.09, "matte_summe": 713.91, "uebersicht": (2 * 1011.09, 2 * 713.91, 2 * 1011.1 + 2 * 713.9),
        "gebogen": 2 * 740.5, "n_stab": 8, "n_matte": 14, "ueber": 0,
    },
}


@pytest.mark.parametrize("name", sorted(SOLL))
def test_stabliste_zeilen_und_summe(name):
    soll, ist = SOLL[name], nachrechnen(lade(name))
    assert set(ist["stabliste"]) == set(soll["stabliste"])
    for pos, (stueck, laenge, gesamt, kg) in soll["stabliste"].items():
        i_stueck, i_laenge, i_gesamt, i_kg = ist["stabliste"][pos]
        assert i_stueck == stueck, (name, pos)
        assert i_laenge == laenge, (name, pos)
        assert i_gesamt == pytest.approx(gesamt, abs=0.006), (name, pos)
        assert i_kg == pytest.approx(kg, abs=0.006), (name, pos)
    assert ist["stab_kg1"] == pytest.approx(soll["stab_summe"], abs=0.006)
    # Zeilen und Summe aus EINER Formel: die Summenzeile ist die Summe der gezeigten Zeilen
    assert ist["stab_kg1"] == pytest.approx(sum(r[3] for r in ist["stabliste"].values()))
    assert ist["stab_stueck"] == sum(r[0] for r in ist["stabliste"].values())
    assert ist["stab_laenge"] == pytest.approx(sum(r[2] for r in ist["stabliste"].values()))


@pytest.mark.parametrize("name", sorted(SOLL))
def test_mattenliste_eine_zeile_je_position(name):
    soll, ist = SOLL[name], nachrechnen(lade(name))
    assert set(ist["mattenliste"]) == set(soll["mattenliste"])
    for pos, (stueck, kg) in soll["mattenliste"].items():
        assert ist["mattenliste"][pos][0] == stueck, (name, pos)
        assert ist["mattenliste"][pos][1] == pytest.approx(kg, abs=0.006), (name, pos)
    assert ist["matte_kg1"] == pytest.approx(soll["matte_summe"], abs=0.006)


@pytest.mark.parametrize("name", sorted(SOLL))
def test_kacheln_wie_allplans_uebersicht(name):
    soll, ist = SOLL[name], nachrechnen(lade(name))
    rund, matten, gesamt = soll["uebersicht"]
    assert round(ist["rund"], 1) == pytest.approx(rund, abs=0.051)
    assert round(ist["matten"], 1) == pytest.approx(matten, abs=0.051)
    assert ist["gesamt"] == pytest.approx(gesamt, abs=0.051)
    assert ist["rund"] == pytest.approx(soll["ausf"] * soll["stab_summe"], abs=0.01)
    assert ist["gebogen"] == pytest.approx(soll["gebogen"], abs=0.15)
    assert (ist["n_stab"], ist["n_matte"], ist["ueber"]) == (soll["n_stab"], soll["n_matte"], soll["ueber"])


def test_alte_formel_haette_die_fehler_gezeigt():
    """Gegenprobe am echten Teilbild: das Feld Gewicht und das Feld Einzellaenge sind bei zusammengefassten Zeilen falsch."""
    zeilen = lade("bewehrung_fall_a")
    stab = [z for z in zeilen if not ist_matte(z)]
    assert sum(z["Gewicht"] for z in stab) == pytest.approx(683.14, abs=0.01)           # die falsche Kachel 683,1 kg
    assert sum(1 for z in stab if z["Einzellaenge"] > 12) == 4                          # die falschen 4 Ueberlaengen
    assert sum(z["Anzahl"] for z in stab) == 393                                        # die alte Summenzeile


def test_mittlerer_durchmesser():
    assert nachrechnen(lade("bewehrung_fall_a"))["mittel_d"] == pytest.approx(10.94, abs=0.01)
    assert nachrechnen(lade("bewehrung"))["mittel_d"] == pytest.approx(17.55, abs=0.01)


# ---------------------------------------------------------------- die VB-Ausdruecke des Reports sind die nachgerechneten
def test_vb_formeln_festgeschrieben():
    assert bw.LFDM == "(Val(Fields!LfdM.Value) >= 1)"
    assert bw.KG1 == ("IIf(%s, Round(CDbl(Fields!Gewicht.Value), 2), CDbl(Fields!Gesamtlaenge.Value) * CDbl(Fields!KgJeM.Value))"
                      % bw.MATTE)
    assert bw.EINZEL == "(CDbl(Fields!Gesamtlaenge.Value) / IIf(CDbl(Fields!Anzahl.Value) < 1, 1.0, CDbl(Fields!Anzahl.Value)))"
    assert bw.KG == "(%s) * %s" % (bw.KG1, bw.AUSF)
    assert bw.UEBER == "(%s And Not %s And %s > Parameters!Lagerlaenge.Value)" % (bw.STAB, bw.LFDM, bw.EINZEL)
    assert bw.MATTE == "(CInt(Fields!ObjId.Value) = 366 Or CInt(Fields!ObjId.Value) = 368)"


def test_abfrage_hat_lfdm_und_bild_zuletzt():
    q = bw.QUERY
    assert "@794@[Name=LfdM]" in q
    assert q.count("@205@") == 1 and q.index("@794@") < q.index("@205@")
    assert q.strip().splitlines()[-2].strip().startswith("@205@")
    assert ("LfdM", "String") in bw.FIELDS and bw.FIELDS[-1] == ("Bild", "Byte[]")


@pytest.mark.parametrize("name", ["bewehrung", "bewehrung_klein", "bewehrung_gross", "bewehrung_fall_a", "bewehrung_fall_b"])
def test_datensaetze_haben_alle_felder(name):
    with open(os.path.join(DATEN, name + ".json"), encoding="utf-8") as handle:
        daten = json.load(handle)
    felder = [f for f, _t in bw.FIELDS]
    assert list(daten["types"]) == felder
    assert all(set(z) == set(felder) for z in daten["rows"])


def test_gross_enthaelt_die_schwierigen_faelle():
    zeilen = lade("bewehrung_gross")
    stab = [z for z in zeilen if not ist_matte(z)]
    assert sum(1 for z in stab if ist_lfdm(z)) >= 3                                      # Meterware
    assert any(ausf(z) > 1 for z in zeilen)                                              # Ausfuehrungen > 1
    nr = [z["Nr"] for z in stab]
    assert len(nr) > len(set(nr))                                                        # Positionen in mehreren Zeilen
    assert any(z["Einzellaenge"] > einzel(z) + 0.01 for z in stab if not ist_lfdm(z))    # zusammengefasste Zeilen
    matte = {}
    for z in zeilen:
        if ist_matte(z):
            matte.setdefault(z["Position"], set()).add(z["Nr"])
    assert any(len(n) > 1 for n in matte.values())                                       # mehrfach verlegte Mattenposition


# ---------------------------------------------------------------- Zahlenformat im gebauten deutschen XML
def gebautes_xml(monkeypatch, tmp_path):
    gespeichert = {}
    monkeypatch.setattr(bw, "OUT_DIR", str(tmp_path))
    monkeypatch.setattr(bw.c, "save", lambda pfad, xml: gespeichert.setdefault("xml", xml))
    bw.build()
    return gespeichert["xml"]


def test_kein_abgeschnittenes_komma(monkeypatch, tmp_path):
    """Ursache des Befunds "27.6 statt 27,6" im deutschen PDF: nicht die Formatierung (der PDF-Text hat das Komma), sondern
    Zeilen bis 0,6 cm mit 2 pt Innenabstand oben/unten - der Fuss des Kommas wird abgeschnitten. Darum: jede Zahl, die per
    Format(...) in einer Zeile oder einem Feld bis 0,6 cm Hoehe steht, hat oben und unten 0 pt Innenabstand. Dazu: jede Zahl
    laeuft ueber Format() oder die Format-Eigenschaft (folgen der Report-Sprache), nie ueber CStr/ToString/Str."""
    import re
    xml = gebautes_xml(monkeypatch, tmp_path)
    assert "<Language>de-DE</Language>" in xml
    ausdruecke = re.sub(r"<Code>.*?</Code>", "", xml, flags=re.S)       # der gemeinsame VB-Code formatiert nur Texte
    # Schriftfamilien stehen als Ausdruck =Code.Schrift(n) im Report (core.report()); sie sind keine Zahlenausdruecke
    ausdruecke = re.sub(r"Code\.Schrift\(\d\)", "", ausdruecke)         # auch im Ausdruck der Haken-Zeile: IIf(n > 0, Code.Schrift(3), Symbolschrift)
    for verboten in (".ToString(", "CStr(Sum", "CStr(CDbl", "Str(Sum", "FormatNumber(", "Code."):
        assert verboten not in ausdruecke, verboten

    def cm(wert):
        return float(wert[:-2]) if wert.endswith("cm") else 99.0

    def pruefe(textbox, hoehe, wo):
        if "Format(" not in textbox or hoehe > 0.6:
            return
        oben = re.search(r"<PaddingTop>([\d.]+)pt</PaddingTop>", textbox)
        unten = re.search(r"<PaddingBottom>([\d.]+)pt</PaddingBottom>", textbox)
        name = re.search(r'Name="([^"]+)"', textbox).group(1)
        assert oben and unten and float(oben.group(1)) == 0 and float(unten.group(1)) == 0, (wo, name, hoehe)

    for zeile in re.finditer(r"<TablixRow><Height>([^<]+)</Height>(.*?)</TablixRow>", xml, re.S):
        for zelle in re.finditer(r"<TablixCell><CellContents>(<Textbox .*?</Textbox>)", zeile.group(2), re.S):
            pruefe(zelle.group(1), cm(zeile.group(1)), "Tabellenzeile")
    for tb in re.finditer(r"<Textbox (?:(?!</Textbox>).)*?</Paragraphs>(?:(?!</Textbox>).)*?<Height>([^<]+)</Height>.*?</Textbox>", xml, re.S):
        pruefe(tb.group(0), cm(tb.group(1)), "Feld")
