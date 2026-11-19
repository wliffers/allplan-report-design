# -*- coding: utf-8 -*-
"""Etikettenblatt des Begleit-Reports Listen (master/listen/build_listen.py, B110/B120) - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_listen.py -q

Geprueft wird, was am Etikett still schiefgehen kann: ein QR-Text ueber 106 Byte ergibt ein leeres Bild ohne Fehler, eine
Reihe zu viel schiebt die Etiketten ueber den Seitenrand, eine Bauteilart ohne Masse bekommt ein leeres Etikett.
Die Kuerzung selbst laeuft im Report als VB (Code.EtikettText); hier steht dieselbe Regel in Python nachgerechnet, und der
VB-Text ist festgeschrieben - wer ihn aendert, aendert diese Datei mit.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPORT, "master", "listen"))
sys.path.insert(0, os.path.join(REPORT, "master"))

import build_listen as li  # noqa: E402


def etikett_text(kopf, zusatz, masse, kennung, grenze=106):
    """Dieselbe Regel wie Code.EtikettText: Kopf kuerzen, Zusatz nur ganz, sonst weglassen; zuletzt bleibt die ID."""
    nbytes = lambda t: len(t.encode("utf-8"))  # noqa: E731
    fest = masse + "\n" + kennung
    if nbytes(fest) > grenze:
        return kennung
    while kopf and nbytes(kopf + "\n" + fest) > grenze:
        kopf = kopf[:-1]
    kopf = kopf.rstrip()
    if not kopf:
        return fest
    if zusatz and nbytes(kopf + "\n" + zusatz + "\n" + fest) <= grenze:
        return kopf + "\n" + zusatz + "\n" + fest
    return kopf + "\n" + fest


MASSE_WAND = "Länge 17,84 m, Dicke 24 cm, Höhe 2,78 m\nMenge 11,90 m³"
ID = "ID 0540Wa 0000000015"


def test_qr_text_bleibt_unter_106_byte():
    kurz = etikett_text("Wand", "Beton bewehrt", MASSE_WAND, ID)
    assert kurz.split("\n") == ["Wand", "Beton bewehrt", "Länge 17,84 m, Dicke 24 cm, Höhe 2,78 m", "Menge 11,90 m³", ID]
    lang = etikett_text("Wand: Außenwand tragend mit Wärmedämmverbundsystem und Sichtbetonoberfläche", "Beton bewehrt", MASSE_WAND, ID)
    assert len(lang.encode("utf-8")) <= 106
    assert lang.endswith(MASSE_WAND + "\n" + ID)                  # Masse und ID bleiben ganz
    assert "Beton bewehrt" not in lang                            # der Zusatz faellt weg, wenn er nicht ganz passt
    assert not lang.split("\n")[0].endswith(" ")                  # kein Leerzeichen am gekuerzten Ende
    assert etikett_text("Wand", "", "x" * 120, ID) == ID          # reicht es nicht einmal fuer die Masse, bleibt die ID


def test_vb_kuerzung_festgeschrieben():
    vb = li.CODE_ETIKETT
    assert "Public Function EtikettText(ByVal kopf As String, ByVal zusatz As String, ByVal masse As String, ByVal id As String, " \
           "ByVal grenze As Integer) As String" in vb
    assert "If u.GetByteCount(fest) > grenze Then Return id" in vb
    assert "Do While k.Length > 0 AndAlso u.GetByteCount(k & nl & fest) > grenze" in vb
    assert "k = k.TrimEnd()" in vb
    assert li.QR_TEXT.startswith("Code.EtikettText(") and li.QR_TEXT.endswith(", 106)")
    assert "Code.QrPng(%s, 5)" % li.QR_TEXT in li.etikett_karte().replace("&amp;", "&").replace("&quot;", '"').replace("&gt;", ">")


def test_stellschrauben_der_etiketten():
    art = re.search(r'<ReportParameter Name="Etiketten_Art">.*?</ReportParameter>', li.PARAMS, re.S).group(0)
    zahl = re.search(r'<ReportParameter Name="Etiketten_Anzahl">.*?</ReportParameter>', li.PARAMS, re.S).group(0)
    assert re.findall(r"<Value>(\d+)</Value>", art.split("<ValidValues>")[1]) == ["0", "1", "3", "4", "6", "704", "991", "992"]
    assert "<DefaultValue><Values><Value>0</Value>" in art and "<DefaultValue><Values><Value>8</Value>" in zahl
    mengen = [int(w) for w, _ in li.ETIKETT_ZAHL]
    je_seite = 2 * li.ETIKETT_REIHEN
    assert mengen == sorted(mengen) and all(m % je_seite == 0 for m in mengen)      # nur ganze Seiten


def test_etiketten_passen_auf_die_seite():
    kopf = li.KARTEN_ABSTAND + 1.45                                 # Luft und Abschnittstitel ueber der ersten Reihe
    assert 2 * li.ETIKETT_PITCH <= li.W                             # zwei Spalten in der Inhaltsbreite
    assert li.ETIKETT_W <= li.ETIKETT_PITCH and li.ETIKETT_H <= li.ETIKETT_ZEILE
    assert kopf + li.ETIKETT_REIHEN * li.ETIKETT_ZEILE <= li.SEITE_NUTZ_H < kopf + (li.ETIKETT_REIHEN + 1) * li.ETIKETT_ZEILE
    assert li.KARTEN_H <= li.SEITE_NUTZ_H                           # mit den zwei Etikettzeilen darunter
    assert (li.ETIKETT_REIHEN + 1) * li.ETIKETT_ZEILE > li.SEITE_NUTZ_H   # Folgeseiten: auch dort genau ETIKETT_REIHEN Reihen


def test_jede_bauteilart_hat_masse():
    arten = sorted(int(n) for n in re.findall(r"Val\(Fields!ObjNr\.Value\)=(\d+)", li.BAUTEIL))
    belegt = sorted(n for nummern, _liste in li.MASSE for n in nummern)
    assert belegt == arten                                          # jede Art genau einmal
    assert all(1 <= len(liste) <= 3 for _nummern, liste in li.MASSE)
    assert sorted(int(w) for w, _ in li.ETIKETT_ARTEN if w != "0") == arten     # die Stellschraube nennt dieselben Arten
