# -*- coding: utf-8 -*-
"""Pruefungen des Sprachschalters master/sprache.py - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_sprache.py -q

Zwei Gruppen: (1) Seitenlabels '<Titel> - Seite <n>' werden ohne Tabelleneintrag je Seite uebersetzt, (2) feste Leermeldungen
(NoRowsMessage) werden uebersetzt.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "master"))

import sprache  # noqa: E402


def bericht(*labels):
    return "<Report>%s</Report>" % "".join("<DocumentMapLabel>%s</DocumentMapLabel>" % text for text in labels)


# ---------------------------------------------------------------- 1. Seitenlabels
def test_seitenlabel_wird_ohne_eintrag_je_seite_uebersetzt():
    xml = bericht("Mein Report - Seite 1", "Mein Report - Seite 2", "Mein Report - Seite 10")
    englisch, fehlend = sprache.uebersetzen(xml, {"Mein Report": "My report"})
    assert fehlend == []
    for erwartet in ("My report - page 1", "My report - page 2", "My report - page 10"):
        assert "<DocumentMapLabel>%s</DocumentMapLabel>" % erwartet in englisch


def test_fehlender_titel_wird_einmal_gemeldet():
    xml = bericht("Mein Report - Seite 1", "Mein Report - Seite 2", "Mein Report - Seite 3")
    assert sprache.uebersetzen(xml, {})[1] == ["Mein Report"]
    assert sprache.texte(xml, {}) == ["Mein Report"]


def test_texte_sammelt_den_titel_nicht_das_label():
    xml = bericht("Mein Report - Seite 1", "Mein Report - Seite 2", "Etwas anderes")
    assert sprache.texte(xml, {}) == ["Mein Report", "Etwas anderes"]


def test_eigener_eintrag_gewinnt():
    xml = bericht("Mein Report - Seite 2")
    englisch, fehlend = sprache.uebersetzen(xml, {"Mein Report - Seite 2": "Sonderfall", "Mein Report": "My report"})
    assert fehlend == []
    assert "<DocumentMapLabel>Sonderfall</DocumentMapLabel>" in englisch
    assert sprache.texte(xml, {"Mein Report - Seite 2": "Sonderfall"}) == ["Mein Report - Seite 2"]


def test_unverwandte_texte_bleiben_unveraendert():
    xml = bericht("Seite 3", "Etwas - Seite", "Etwas - Seite x", "Titel Seite 2")
    englisch, fehlend = sprache.uebersetzen(xml, {"Seite 3": "Page 3"})
    assert "<DocumentMapLabel>Page 3</DocumentMapLabel>" in englisch
    assert fehlend == ["Etwas - Seite", "Etwas - Seite x", "Titel Seite 2"]
    for text in fehlend:
        assert "<DocumentMapLabel>%s</DocumentMapLabel>" % text in englisch


def test_seitenlabel_im_ausdruck():
    xml = "<Report><Value>=IIf(Fields!A.Value, \"Mein Report - Seite 2\", \"\")</Value></Report>"
    englisch, fehlend = sprache.uebersetzen(xml, {"Mein Report": "My report"})
    assert fehlend == []
    assert "My report - page 2" in englisch


# ---------------------------------------------------------------- 2. Leermeldung
def test_feste_leermeldung_wird_uebersetzt():
    xml = "<Report><NoRowsMessage>Keine Wand im Modell</NoRowsMessage></Report>"
    assert sprache.texte(xml, {}) == ["Keine Wand im Modell"]
    englisch, fehlend = sprache.uebersetzen(xml, {"Keine Wand im Modell": "No wall in the model"})
    assert fehlend == []
    assert "<NoRowsMessage>No wall in the model</NoRowsMessage>" in englisch


# ---------------------------------------------------------------- Farbwert des Designs im Text
def test_text_mit_farbe_des_kundendesigns_findet_den_eintrag_des_hausdesigns():
    tabelle = {"Größte Gruppe: <font color='#0F54AC'><b>": "Largest group: <font color='#0F54AC'><b>"}
    xml = "<Report><Value>=\"Größte Gruppe: &lt;font color='#2E7D32'&gt;&lt;b&gt;\" &amp; Fields!a.Value</Value></Report>"
    englisch, fehlend = sprache.uebersetzen(xml, tabelle)
    assert fehlend == []
    assert "Largest group: &lt;font color='#2E7D32'&gt;" in englisch and "#0F54AC" not in englisch


def test_text_mit_farbe_ohne_passenden_eintrag_bleibt_gemeldet():
    xml = "<Report><Value>=\"Kleinste Gruppe: &lt;font color='#2E7D32'&gt;\"</Value></Report>"
    assert sprache.uebersetzen(xml, {"Größte Gruppe: <font color='#0F54AC'>": "x"})[1] == ["Kleinste Gruppe: <font color='#2E7D32'>"]
