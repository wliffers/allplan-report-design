# -*- coding: utf-8 -*-
"""Pruefungen von master/design.py: Stand, Sperre, Pruefung, Ableitung, Schrift, Befehle - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_design.py -q

Die echte design.json der Werkstatt bleibt unberuehrt: jeder Test legt sie ueber die Fixture `werkstatt` in einen Temp-Ordner um.
Die Schriften des Rechners sind ebenfalls ersetzt, damit die Ergebnisse nicht davon abhaengen, was installiert ist.
"""
import json
import os
import re
import sys
from xml.sax.saxutils import escape as esc_xml

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "master"))

import design  # noqa: E402

ECHTE_SCHRIFTEN = design.installierte_schriften
SCHRIFTEN = {"roboto", "roboto light", "roboto medium", "roboto black", "arial", "segoe ui", "segoe ui light", "segoe ui semibold"}


@pytest.fixture
def werkstatt(tmp_path, monkeypatch):
    """Leere Werkstatt: kein design.json, keine Umgebungsvariable, feste Schriftliste."""
    monkeypatch.delenv(design.UMGEBUNG, raising=False)
    monkeypatch.setattr(design, "WERKSTATT", str(tmp_path))
    monkeypatch.setattr(design, "DATEI", str(tmp_path / "design.json"))
    monkeypatch.setattr(design, "installierte_schriften", lambda: set(SCHRIFTEN))
    return tmp_path


def kunde(**aenderungen):
    """Ein gueltiges Kundendesign: die vier Pflichtfarben und eine Schrift; `aenderungen` ueberschreiben Farben (None = streichen)."""
    farben = {"tinte": "#1A1A1A", "dunkel": "#1F3A5F", "leit": "#1F5FAF", "akzent": "#E87722"}
    for name, wert in aenderungen.items():
        if wert is None:
            farben.pop(name, None)
        else:
            farben[name] = wert
    return {"name": "Testbuero", "stil": "ruhig", "farben": farben, "schrift": dict(design.HAUS["schrift"])}


def haus_festlegen(antwort="nimm den Standard"):
    """Hausdesign festlegen, wie der Agent es nach der Antwort des Anwenders tut."""
    return design.main(["--haus", "--antwort", antwort])


def schreibe(pfad, inhalt):
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False), encoding="utf-8")
    return str(pfad)


def stufen(befunde, stufe):
    return [text for s, text in befunde if s == stufe]


# ---------------------------------------------------------------- Stand: offen, haus, kunde
def test_stand_offen(werkstatt, capsys):
    d = design.laden()
    assert d.quelle == "offen"
    assert d.zeile().startswith("DESIGN: OFFEN")
    assert design.main([]) == 3
    assert capsys.readouterr().out.startswith("DESIGN: OFFEN")


def test_stand_haus(werkstatt, capsys):
    assert design.main(["--haus", "--antwort", "nimm den Standard"]) == 0
    assert json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))["quelle"] == "haus"
    d = design.laden()
    assert d.quelle == "haus" and d.schrift["normal"] == "Roboto"
    assert d.zeile().startswith("DESIGN: HAUS | %s | Schrift Roboto | festgelegt " % design.HAUS["name"])
    capsys.readouterr()
    assert design.main([]) == 0
    assert capsys.readouterr().out.startswith("DESIGN: HAUS")


def test_stand_kunde(werkstatt):
    schreibe(werkstatt / "design.json", {"quelle": "kunde", "design": kunde(), "festgelegt": "2026-01-02"})
    d = design.laden()
    assert d.quelle == "kunde"
    assert d.farben["dunkel"] == "#1F3A5F" and d.farben["akzent"] == "#E87722"
    assert d.zeile() == "DESIGN: KUNDE | Testbuero | Schrift Roboto | festgelegt 2026-01-02"


def test_umgebungsvariable_geht_vor(werkstatt, monkeypatch):
    schreibe(werkstatt / "design.json", {"quelle": "kunde", "design": kunde(), "festgelegt": "2026-01-02"})
    monkeypatch.setenv(design.UMGEBUNG, "HAUS")                      # Gross und Klein egal
    d = design.laden()
    assert d.quelle == "haus" and d.festgelegt == "automatischer Lauf"
    datei = schreibe(werkstatt / "anderes.json", kunde(tinte="#101010"))
    schreibe(werkstatt / "design.json", {"quelle": "haus"})
    monkeypatch.setenv(design.UMGEBUNG, datei)
    d = design.laden()
    assert d.quelle == "kunde" and d.farben["tinte"] == "#101010" and d.festgelegt == "automatischer Lauf"


def test_umgebungsvariable_haus_ohne_design_json(werkstatt, monkeypatch):
    monkeypatch.setenv(design.UMGEBUNG, "haus")
    assert design.laden().quelle == "haus"                           # kein "offen": automatische Laeufe halten nirgends an


# ---------------------------------------------------------------- Sperre
def test_sperre_offen_endet_mit_code_3_und_nennt_die_fragen(werkstatt, capsys):
    with pytest.raises(SystemExit) as ende:
        design.sperre(design.laden())
    assert ende.value.code == 3
    fehler = capsys.readouterr().err
    assert "DESIGN: OFFEN" in fehler
    for frage in ("Stil", "Farben", "Schrift"):
        assert frage in fehler
    assert "--haus" in fehler and "--vorlage" in fehler


def test_sperre_laesst_festgelegtes_design_durch(werkstatt):
    haus_festlegen()
    design.sperre(design.laden())


def test_core_save_haelt_an_solange_das_design_offen_ist(werkstatt, tmp_path, monkeypatch):
    import core                                                      # liegt neben design.py; conftest.py setzt REPORT_DESIGN=haus
    monkeypatch.setattr(core, "DESIGN", design.laden())
    ziel = tmp_path / "x.rdlc"
    with pytest.raises(SystemExit) as ende:
        core.save(str(ziel), "<Report/>")
    assert ende.value.code == 3 and not ziel.exists()
    haus_festlegen()
    monkeypatch.setattr(core, "DESIGN", design.laden())
    core.save(str(ziel), "<Report/>")
    assert ziel.exists()


# ---------------------------------------------------------------- pruefen
def test_pruefen_gueltiges_design_hat_keinen_fehler():
    assert stufen(design.pruefen(kunde()), "FEHLER") == []


def test_pruefen_hausdesign_hat_nur_den_akzent_hinweis(werkstatt):
    befunde = design.pruefen({"farben": design.HAUS["farben"], "schrift": design.HAUS["schrift"]})
    assert stufen(befunde, "FEHLER") == []
    assert len(stufen(befunde, "HINWEIS")) == 1 and "Akzent" in stufen(befunde, "HINWEIS")[0]


@pytest.mark.parametrize("name", design.PFLICHT_FARBEN)
def test_pruefen_fehlende_pflichtfarbe(name):
    fehler = stufen(design.pruefen(kunde(**{name: None})), "FEHLER")
    assert any("'%s' fehlt" % name in text for text in fehler)


def test_pruefen_abschnitt_farben_fehlt():
    assert design.pruefen({"schrift": {}}) == [("FEHLER", "Abschnitt 'farben' fehlt.")]


def test_pruefen_unbekannter_farbname():
    fehler = stufen(design.pruefen(kunde(magenta="#FF00FF")), "FEHLER")
    assert any("'magenta'" in text and "kennt der Bausatz nicht" in text for text in fehler)


@pytest.mark.parametrize("wert", ["#E87722CC", "rgba(232,119,34,0.5)", "Transparent", "#E87", "E87722", 12])
def test_pruefen_wert_mit_durchsicht_oder_falscher_form(wert):
    fehler = stufen(design.pruefen(kunde(akzent=wert)), "FEHLER")
    assert any("'akzent'" in text and "#RRGGBB" in text for text in fehler)


def test_pruefen_text_zu_schwach():
    fehler = stufen(design.pruefen(kunde(text="#CCCCCC")), "FEHLER")
    assert any("'text'" in text and "zu schwach" in text for text in fehler)


def test_pruefen_leitfarbe_zu_schwach():
    fehler = stufen(design.pruefen(kunde(leit="#99BBEE")), "FEHLER")
    assert any("'leit'" in text and "zu schwach" in text for text in fehler)


def test_pruefen_dunkel_zu_hell():
    fehler = stufen(design.pruefen(kunde(dunkel="#DDDDDD")), "FEHLER")
    assert any("'dunkel'" in text and "zu hell" in text for text in fehler)


def test_pruefen_heller_akzent_ist_nur_hinweis():
    befunde = design.pruefen(kunde(akzent="#00FBC8"))
    assert stufen(befunde, "FEHLER") == []
    hinweise = stufen(befunde, "HINWEIS")
    assert len(hinweise) == 1 and "traegt auf Weiss keine Schrift" in hinweise[0]


def test_pruefen_akzent_kaum_vom_dunklen_grund_unterscheidbar():
    befunde = design.pruefen(kunde(akzent="#233F66"))
    assert stufen(befunde, "FEHLER") == []
    assert any("hebt sich vom dunklen Grund" in text for text in stufen(befunde, "HINWEIS"))


@pytest.mark.parametrize("name", ["stufen", "serie"])
def test_pruefen_listen_brauchen_acht_farben(name):
    fehler = stufen(design.pruefen(kunde(**{name: ["#112233"] * 7})), "FEHLER")
    assert any("genau 8" in text for text in fehler)


def test_pruefen_unbekannte_schriftrolle():
    roh = kunde()
    roh["schrift"] = {"fett": "Arial"}
    assert any("nur die Rollen" in text for text in stufen(design.pruefen(roh), "FEHLER"))


def test_pruefen_fehlende_schrift_ist_hinweis(werkstatt, monkeypatch):
    monkeypatch.setattr(design, "installierte_schriften", lambda: {"segoe ui"})
    roh = kunde()
    roh["schrift"] = {"normal": "Hausschrift XY"}
    befunde = design.pruefen(roh)
    assert stufen(befunde, "FEHLER") == []
    assert any("Hausschrift XY" in text and "Segoe UI" in text for text in stufen(befunde, "HINWEIS"))


# ---------------------------------------------------------------- ableiten
VIER_FARBEN = [
    {"tinte": "#1A1A1A", "dunkel": "#1F3A5F", "leit": "#1F5FAF", "akzent": "#E87722"},
    {"tinte": "#062246", "dunkel": "#062246", "leit": "#0F54AC", "akzent": "#00FBC8"},
    {"tinte": "#222222", "dunkel": "#7A1020", "leit": "#B3122E", "akzent": "#FFD100"},
    {"tinte": "#0B3D2E", "dunkel": "#0B3D2E", "leit": "#1B7F4F", "akzent": "#9BE564"},
]


@pytest.mark.parametrize("vier", VIER_FARBEN)
def test_ableiten_fuellt_alles_aus_vier_farben(vier):
    f = design.ableiten(vier)
    for name in design.EINZELFARBEN:
        assert design._HEX.match(f[name]), name
    assert len(f["stufen"]) == 8 and len(f["serie"]) == 8
    assert all(design._HEX.match(w) for w in f["stufen"] + f["serie"])
    assert f["stufen"][0] == f["dunkel"] and f["stufen"][1] == f["leit"]
    assert f["serie"][4] == f["akzent"]
    for name in vier:                                               # genannte Farben bleiben unveraendert
        assert f[name] == vier[name]


@pytest.mark.parametrize("vier", VIER_FARBEN)
def test_ableiten_aendert_die_eingabe_nicht(vier):
    vorher = dict(vier)
    design.ableiten(vier)
    assert vier == vorher


def test_ableiten_nennt_der_kunde_eine_farbe_bleibt_sie():
    f = design.ableiten(dict(VIER_FARBEN[0], leise="#444444", stufen=["#000000"] * 8))
    assert f["leise"] == "#444444" and f["fussnote"] == "#444444" and f["stufen"] == ["#000000"] * 8


@pytest.mark.parametrize("vier", VIER_FARBEN)
def test_abgeleitete_schriftfarben_erreichen_4_5_auf_weiss(werkstatt, vier):
    d = design.Design("kunde", {"farben": vier, "schrift": {"normal": "Roboto"}})
    for name in ("leise", "fussnote"):
        assert design.kontrast(d.farben[name], d.farben["weiss"]) >= 4.5, name
    for farbe in (d.gut_text, d.achtung_text, d.schlecht_text, d.akzent_text):
        assert design.kontrast(farbe, d.farben["weiss"]) >= 4.5, farbe
    # was auf dunklem Grund steht, ist dort lesbar
    assert design.kontrast(d.auf_dunkel, d.farben["dunkel"]) >= 4.5
    assert design.kontrast(d.akzent_auf_dunkel, d.farben["dunkel"]) >= 4.5


def test_akzent_text_ist_der_akzent_nur_wenn_er_lesbar_ist(werkstatt):
    hell = design.Design("kunde", kunde(akzent="#00FBC8"))
    dunkel = design.Design("kunde", kunde(akzent="#8A1538"))
    assert hell.akzent_text == hell.farben["leit"]
    assert dunkel.akzent_text == "#8A1538"


def test_hausdesign_bewertungsschrift_ist_abgedunkelt(werkstatt):
    d = design.Design("haus", design.HAUS)
    assert d.gut_text != design.HAUS["farben"]["gut"]               # #10B981 allein ist als Schrift zu schwach
    assert design.kontrast(d.gut_text, "#FFFFFF") >= 4.5
    assert d.farben["gut"] == design.HAUS["farben"]["gut"]          # die reine Farbe bleibt fuer Flaechen


# ---------------------------------------------------------------- Farbrechnung, lesbar, auf
def test_mischen_und_kontrast():
    assert design.mischen("#FFFFFF", "#000000", 0.5) == "#808080"
    assert design.mischen("#123456", "#FFFFFF", 1.0) == "#123456"
    assert design.mischen("#123456", "#FFFFFF", 0.0) == "#FFFFFF"
    assert design.kontrast("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert design.kontrast("#336699", "#336699") == pytest.approx(1.0)


@pytest.mark.parametrize("farbe", ["#00FBC8", "#F59E0B", "#10B981", "#9BA7B5", "#FFFF00"])
def test_lesbar_auf_hellem_grund(farbe):
    ergebnis = design.lesbar(farbe, "#FFFFFF")
    assert design.kontrast(ergebnis, "#FFFFFF") >= 4.5


@pytest.mark.parametrize("farbe", ["#062246", "#0F54AC", "#365F94", "#444444"])
def test_lesbar_auf_dunklem_grund(farbe):
    ergebnis = design.lesbar(farbe, "#062246")
    assert design.kontrast(ergebnis, "#062246") >= 4.5
    assert design.helligkeit(ergebnis) > design.helligkeit(farbe) or ergebnis == farbe   # dunkler Grund: aufgehellt, nie abgedunkelt


def test_lesbar_laesst_eine_ausreichende_farbe_unveraendert():
    assert design.lesbar("#062246", "#FFFFFF") == "#062246"
    assert design.lesbar("#FFFFFF", "#062246") == "#FFFFFF"


def test_lesbar_ziel_3_ist_weniger_streng_als_4_5():
    assert design.kontrast(design.lesbar("#00FBC8", "#FFFFFF", ziel=3.0), "#FFFFFF") >= 3.0
    assert design.helligkeit(design.lesbar("#00FBC8", "#FFFFFF", ziel=3.0)) > design.helligkeit(design.lesbar("#00FBC8", "#FFFFFF"))


def test_auf_waehlt_die_lesbarere_schriftfarbe():
    assert design.auf("#062246") == "#FFFFFF"
    assert design.auf("#FFFFFF") == "#000000"
    assert design.auf("#00FBC8", "#FFFFFF", "#062246") == "#062246"


# ---------------------------------------------------------------- Schrift
def test_schrift_da_namensformen():
    assert design.schrift_da("Roboto", {"roboto"})
    assert design.schrift_da("Roboto", {"roboto regular"})
    assert design.schrift_da("ROBOTO", {"roboto"})                   # Gross und Klein egal
    assert design.schrift_da("  Roboto ", {"roboto"})
    assert design.schrift_da("Roboto Medium", {"roboto medium"})
    assert not design.schrift_da("Roboto", {"roboto medium", "roboto light"})   # Familie 'Roboto' ist mehr als ein Schnitt
    assert not design.schrift_da("Roboto", {"arial"})


def test_schrift_da_sammeleintrag_mit_und_zeichen():
    sammel = {"segoe ui & segoe ui light & segoe ui semilight", "arial"}
    assert design.schrift_da("Segoe UI", sammel)
    assert design.schrift_da("Segoe UI Light", sammel)
    assert not design.schrift_da("Segoe UI Semibold", sammel)


def test_schrift_da_unlesbare_liste_heisst_vorhanden():
    assert design.schrift_da("Irgendwas", None)


def test_installierte_schriften_liefert_namen_ohne_klammerzusatz():
    namen = ECHTE_SCHRIFTEN()                                         # die echte Funktion, nicht die der Fixture
    assert namen is None or (namen and all(n == n.lower() and not n.endswith(")") for n in namen))


def test_fehlende_schrift_wird_gemeldet_der_report_waehlt_beim_oeffnen(werkstatt, monkeypatch):
    monkeypatch.setattr(design, "installierte_schriften", lambda: {"segoe ui", "segoe ui light", "segoe ui semibold"})
    schreibe(werkstatt / "design.json", {"quelle": "kunde", "festgelegt": "2026-01-02",
                                         "design": dict(kunde(), schrift={"normal": "Hausschrift XY"})})
    d = design.laden()
    assert d.schrift == d.schrift_soll                                # gebaut wird mit der Soll-Schrift, den Ersatz waehlt der Report beim Oeffnen
    assert d.schrift["normal"] == "Hausschrift XY"
    assert set(d.schrift_fehlt) == {"Hausschrift XY"}
    zeile = d.zeile()
    assert "Schrift Hausschrift XY" in zeile
    assert "Schrift fehlt auf diesem Rechner: Hausschrift XY -> Reports zeigen hier Segoe UI" in zeile


def test_hausschrift_fehlt_dann_meldung_und_ersatz_nennt_segoe(werkstatt, monkeypatch):
    monkeypatch.setattr(design, "installierte_schriften", lambda: {"segoe ui"})
    d = design.Design("haus", design.HAUS)
    assert d.schrift == design.HAUS["schrift"]
    assert "Roboto" in d.zeile() and "Reports zeigen hier Segoe UI" in d.zeile()


def test_vorhandene_schrift_wird_nicht_ersetzt(werkstatt):
    d = design.Design("haus", design.HAUS)
    assert d.schrift_fehlt == [] and "Schrift fehlt" not in d.zeile()
    assert d.schrift == design.HAUS["schrift"]


def test_kundendesign_ohne_schriftangabe_nimmt_die_hausschrift(werkstatt):
    roh = kunde()
    del roh["schrift"]
    d = design.Design("kunde", roh)
    assert d.schrift_soll["normal"] == design.HAUS["schrift"]["normal"]
    assert set(d.schrift) == set(design.ROLLEN)


def test_kundendesign_mit_einer_schrift_gilt_fuer_alle_rollen(werkstatt):
    roh = kunde()
    roh["schrift"] = {"normal": "Arial"}
    d = design.Design("kunde", roh)
    assert [d.schrift[r] for r in design.ROLLEN] == ["Arial"] * 4


# ---------------------------------------------------------------- Befehle
def test_vorlage_dann_kunde_ist_ein_rundlauf(werkstatt, capsys):
    formular = werkstatt / "design_kunde.json"
    assert design.main(["--vorlage"]) == 0
    assert formular.is_file()
    inhalt = json.loads(formular.read_text(encoding="utf-8"))
    assert set(inhalt["farben"]) == set(design.PFLICHT_FARBEN)
    assert inhalt["schrift"] == design.HAUS["schrift"] and "_hilfe" in inhalt
    inhalt["name"] = "Buero Beispiel"
    inhalt["farben"]["akzent"] = "#E87722"
    formular.write_text(json.dumps(inhalt, ensure_ascii=False), encoding="utf-8")
    capsys.readouterr()
    assert design.main(["--kunde", str(formular)]) == 0
    ausgabe = capsys.readouterr().out
    assert "AMPEL:" in ausgabe and "DESIGN: KUNDE | Buero Beispiel | Schrift Roboto" in ausgabe
    stand = json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))
    assert stand["quelle"] == "kunde" and stand["design"]["name"] == "Buero Beispiel"
    assert "_hilfe" not in stand["design"]                          # Formularhilfe wird nicht festgelegt
    assert design.laden().quelle == "kunde" and design.laden().farben["akzent"] == "#E87722"


def test_vorlage_ueberschreibt_nichts(werkstatt, capsys):
    ziel = werkstatt / "mein.json"
    ziel.write_text("{}", encoding="utf-8")
    assert design.main(["--vorlage", str(ziel)]) == 2
    assert ziel.read_text(encoding="utf-8") == "{}"
    assert "nichts ueberschrieben" in capsys.readouterr().out


def test_kunde_mit_fehler_legt_nichts_fest(werkstatt, capsys):
    datei = schreibe(werkstatt / "kaputt.json", kunde(akzent="#E87722CC"))
    assert design.main(["--kunde", datei]) == 1
    assert not (werkstatt / "design.json").exists()
    assert "AMPEL: ROT | design | 1 Fehler" in capsys.readouterr().out


def test_kunde_ohne_datei_oder_mit_unlesbarer_datei(werkstatt, capsys):
    assert design.main(["--kunde"]) == 2
    assert design.main(["--kunde", str(werkstatt / "gibt_es_nicht.json")]) == 2
    (werkstatt / "kein_json.json").write_text("{nicht json", encoding="utf-8")
    assert design.main(["--kunde", str(werkstatt / "kein_json.json")]) == 2
    assert not (werkstatt / "design.json").exists()
    assert capsys.readouterr().out.count("FEHLER:") == 3


def test_kunde_mit_json_das_kein_objekt_ist_meldet_fehler_statt_abzustuerzen(werkstatt, capsys):
    (werkstatt / "liste.json").write_text("[]", encoding="utf-8")
    assert design.main(["--kunde", str(werkstatt / "liste.json")]) == 2
    assert "enthaelt kein Design" in capsys.readouterr().out
    assert not (werkstatt / "design.json").exists()


def test_pruefen_ohne_datei_prueft_das_geltende_design_und_legt_nichts_fest(werkstatt, capsys):
    assert design.main(["--pruefen"]) == 0
    assert "AMPEL: ORANGE | design | 0 Fehler, 1 Hinweise" in capsys.readouterr().out     # Hausdesign: nur der Akzent-Hinweis
    assert not (werkstatt / "design.json").exists()


def test_pruefen_mit_datei_legt_nichts_fest(werkstatt, capsys):
    assert design.main(["--pruefen", schreibe(werkstatt / "k.json", kunde())]) == 0
    assert not (werkstatt / "design.json").exists()


def test_haus_ueberschreibt_ein_kundendesign(werkstatt):
    schreibe(werkstatt / "design.json", {"quelle": "kunde", "design": kunde()})
    assert design.main(["--haus", "--antwort", "nimm den Standard"]) == 0
    assert design.laden().quelle == "haus"


def test_fragen_nennen_stil_farben_schrift_und_die_empfehlung(capsys):
    assert design.main(["--fragen"]) == 0
    ausgabe = capsys.readouterr().out
    for wort in ("1  Stil", "2  Farben", "3  Schrift", "--haus", "--vorlage", "--kunde"):
        assert wort in ausgabe


def test_tabelle_nennt_alle_farben_und_schriften(werkstatt, capsys):
    haus_festlegen()
    capsys.readouterr()
    assert design.main(["--tabelle"]) == 0
    ausgabe = capsys.readouterr().out
    for name in design.EINZELFARBEN + ("stufen", "serie", "auf_dunkel", "akzent_text", "gut_text"):
        assert name in ausgabe
    for rolle in design.ROLLEN:
        assert "schrift %-10s" % rolle in ausgabe
    assert ausgabe.rstrip().splitlines()[-1].startswith("DESIGN: HAUS")


# ---------------------------------------------------------------- Schrift zur Laufzeit
def runde(familie):
    return "<TextRun><Value>x</Value><Style><FontFamily>%s</FontFamily></Style></TextRun>" % familie


def report_xml(*familien):
    return "<Report>%s<Code>Public Function Alt()\nEnd Function</Code></Report>" % "".join(runde(f) for f in familien)


def vb_listen(xml):
    """Die beiden Listen (soll, ersatz) aus dem angehaengten VB-Code."""
    from xml.sax.saxutils import unescape
    code = unescape(xml[xml.index("<Code>"):xml.index("</Code>")])
    liste = lambda name: re.search(r"Dim %s\(\) As String = \{([^}]*)\}" % name, code).group(1).replace('"', "").split(", ")
    return liste("soll"), liste("ersatz")


def haus_design(werkstatt):
    return design.Design("haus", design.HAUS)


def test_laufzeit_ersetzt_jede_sollfamilie_durch_den_ausdruck(werkstatt):
    d = haus_design(werkstatt)
    xml = design.schrift_zur_laufzeit(report_xml("Roboto", "Roboto Light", "Roboto Medium", "Roboto Black"), d, esc_xml)
    assert "<FontFamily>Roboto" not in xml
    assert [xml.count("<FontFamily>=Code.Schrift(%d)</FontFamily>" % i) for i in range(4)] == [1, 1, 1, 1]


def test_laufzeit_nennt_soll_und_ersatz_gleich_lang_und_in_gleicher_reihenfolge(werkstatt):
    d = haus_design(werkstatt)
    xml = design.schrift_zur_laufzeit(report_xml("Roboto Medium", "Roboto"), d, esc_xml)
    soll, ersatz = vb_listen(xml)
    assert len(soll) == len(ersatz) == 4
    assert soll == ["Roboto", "Roboto Light", "Roboto Medium", "Roboto Black"]
    assert ersatz == ["Segoe UI", "Segoe UI Light", "Segoe UI Semibold", "Segoe UI Semibold"]
    # der Ausdruck zeigt auf die Stelle der Familie in der Liste: Medium = 2, Normal = 0
    assert "<FontFamily>=Code.Schrift(2)</FontFamily>" in xml and "<FontFamily>=Code.Schrift(0)</FontFamily>" in xml


def test_laufzeit_laesst_fremde_feste_namen_stehen(werkstatt):
    d = haus_design(werkstatt)
    xml = design.schrift_zur_laufzeit(report_xml("Roboto", "Segoe UI Symbol", "Consolas", "Segoe UI"), d, esc_xml)
    for fest in ("Segoe UI Symbol", "Consolas", "Segoe UI"):
        assert "<FontFamily>%s</FontFamily>" % fest in xml
    assert xml.count("=Code.Schrift(") == 1


def test_laufzeit_kundenlayout_mit_festem_segoe_bleibt_unveraendert_und_ohne_funktion(werkstatt):
    d = haus_design(werkstatt)
    vorher = report_xml("Segoe UI", "Segoe UI Light", "Segoe UI Semibold")
    nachher = design.schrift_zur_laufzeit(vorher, d, esc_xml)
    assert nachher == vorher and "Function Schrift" not in nachher


def test_laufzeit_design_dessen_schrift_schon_der_ersatz_ist_ergibt_keinen_ausdruck(werkstatt):
    roh = kunde()
    roh["schrift"] = dict(design.SCHRIFT_ERSATZ)
    d = design.Design("kunde", roh)
    vorher = report_xml("Segoe UI", "Segoe UI Light", "Segoe UI Semibold")
    assert design.schrift_zur_laufzeit(vorher, d, esc_xml) == vorher


def test_laufzeit_haengt_die_funktion_genau_einmal_an(werkstatt):
    d = haus_design(werkstatt)
    xml = design.schrift_zur_laufzeit(report_xml("Roboto", "Roboto", "Roboto Light"), d, esc_xml)
    assert xml.count("Public Function Schrift(") == 1
    assert "Public Function Alt()" in xml                              # der vorhandene Code bleibt
    zweimal = design.schrift_zur_laufzeit(xml, d, esc_xml)             # nichts mehr zu ersetzen: kein zweites Anhaengen
    assert zweimal == xml


def test_laufzeit_ohne_treffer_bleibt_alles_wie_es_ist(werkstatt):
    d = haus_design(werkstatt)
    vorher = report_xml("Consolas")
    assert design.schrift_zur_laufzeit(vorher, d, esc_xml) == vorher


@pytest.mark.parametrize("rahmen", ["<Report><X/></Report>", "<Report><Code /></Report>"])
def test_laufzeit_legt_den_code_block_an_wenn_er_fehlt(werkstatt, rahmen):
    d = haus_design(werkstatt)
    xml = design.schrift_zur_laufzeit(rahmen.replace("<X/>", runde("Roboto")).replace("<Code />", runde("Roboto") + "<Code />"), d, esc_xml)
    assert xml.count("<Code>") == 1 and xml.count("Public Function Schrift(") == 1


def test_laufzeit_kundenfamilie_wird_ebenfalls_zum_ausdruck(werkstatt):
    roh = kunde()
    roh["schrift"] = {"normal": "Arial", "zahl": "Arial Black"}
    d = design.Design("kunde", roh)
    xml = design.schrift_zur_laufzeit(report_xml("Arial", "Arial Black"), d, esc_xml)
    soll, ersatz = vb_listen(xml)
    assert soll == ["Arial", "Arial Black"] and ersatz == ["Segoe UI", "Segoe UI Semibold"]


def test_laufzeit_maskiert_den_namen_im_xml(werkstatt):
    roh = kunde()
    roh["schrift"] = {"normal": "Muster & Sohn"}
    d = design.Design("kunde", roh)
    xml = design.schrift_zur_laufzeit(report_xml("Muster &amp; Sohn"), d, esc_xml)
    assert "=Code.Schrift(0)" in xml and "Muster &amp; Sohn" not in xml.split("<Code>")[0]


# ---------------------------------------------------------------- --haus verlangt die Antwort des Anwenders
def test_haus_ohne_antwort_wird_abgelehnt(werkstatt, capsys):
    assert design.main(["--haus"]) == 2
    assert not (werkstatt / "design.json").exists()
    ausgabe = capsys.readouterr().out
    assert "FEHLER" in ausgabe and "--antwort" in ausgabe and "--fragen" in ausgabe


@pytest.mark.parametrize("argumente", [["--haus", "--antwort"], ["--haus", "--antwort", ""], ["--haus", "--antwort", "   "],
                                       ["--haus", "--antwort="]])
def test_haus_mit_leerer_antwort_wird_abgelehnt(werkstatt, argumente):
    assert design.main(argumente) == 2
    assert not (werkstatt / "design.json").exists()


def test_haus_mit_antwort_schreibt_den_wortlaut_in_design_json(werkstatt):
    assert design.main(["--haus", "--antwort", "  nimm den Standard  "]) == 0
    stand = json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))
    assert stand["quelle"] == "haus" and stand["antwort"] == "nimm den Standard"
    assert design.laden().quelle == "haus"


def test_antwort_mit_gleichheitszeichen_geht_auch(werkstatt):
    assert design.main(["--haus", "--antwort=Standard bitte"]) == 0
    assert json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))["antwort"] == "Standard bitte"


def test_antwort_vor_dem_schalter_geht_auch(werkstatt):
    assert design.main(["--antwort", "Standard", "--haus"]) == 0
    assert json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))["antwort"] == "Standard"


def test_kunde_mit_antwort_wird_vermerkt_ohne_antwort_geht_es_auch(werkstatt):
    datei = schreibe(werkstatt / "k.json", kunde())
    assert design.main(["--kunde", datei]) == 0
    assert "antwort" not in json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))
    assert design.main(["--kunde", datei, "--antwort", "unsere Farben stehen im CI-Handbuch"]) == 0
    stand = json.loads((werkstatt / "design.json").read_text(encoding="utf-8"))
    assert stand["quelle"] == "kunde" and stand["antwort"] == "unsere Farben stehen im CI-Handbuch"


def test_fragen_nennen_haus_nur_mit_antwort(capsys):
    design.main(["--fragen"])
    assert "--haus --antwort" in capsys.readouterr().out


# ---------------------------------------------------------------- laden(): nie still Hausdesign
@pytest.mark.parametrize("inhalt,grund", [
    ("{}", "keine gueltige Quelle"),
    ("[]", "keine gueltige Quelle"),
    ('"haus"', "keine gueltige Quelle"),
    ('{"quelle": "irgendwas"}', "keine gueltige Quelle"),
    ('{"quelle": 5}', "keine gueltige Quelle"),
    ("{nicht json", "laesst sich nicht lesen"),
    ("", "laesst sich nicht lesen"),
    ('{"quelle": "Kunde"}', "Kundendesign ungueltig"),
    ('{"quelle": "kunde", "design": []}', "Kundendesign ungueltig"),
])
def test_unbrauchbare_design_json_ist_offen_mit_grund(werkstatt, capsys, inhalt, grund):
    (werkstatt / "design.json").write_text(inhalt, encoding="utf-8")
    d = design.laden()
    assert d.quelle == "offen" and grund in d.hinweis
    assert d.zeile().startswith("DESIGN: OFFEN | ") and grund in d.zeile()
    with pytest.raises(SystemExit) as ende:
        design.sperre(d)
    assert ende.value.code == 3 and grund in capsys.readouterr().err
    assert design.main([]) == 3


def test_kundendesign_mit_fehler_in_design_json_ist_offen_mit_dem_ersten_fehler(werkstatt):
    schreibe(werkstatt / "design.json", {"quelle": "kunde", "design": kunde(akzent=None)})
    d = design.laden()
    assert d.quelle == "offen" and "Kundendesign ungueltig" in d.hinweis and "'akzent' fehlt" in d.hinweis


def test_quelle_gross_geschrieben_gilt(werkstatt):
    schreibe(werkstatt / "design.json", {"quelle": "HAUS"})
    assert design.laden().quelle == "haus"
    schreibe(werkstatt / "design.json", {"quelle": " Kunde ", "design": kunde()})
    assert design.laden().quelle == "kunde"


def test_offen_ohne_design_json_hat_keinen_grund_ausser_noch_nicht_festgelegt(werkstatt):
    d = design.laden()
    assert d.hinweis == "" and "noch nicht festgelegt" in d.zeile()


# ---------------------------------------------------------------- REPORT_DESIGN=<datei> wird geprueft
def test_umgebungsvariable_mit_komplett_weissem_design_bricht_ab(werkstatt, monkeypatch):
    weiss = kunde(tinte="#FFFFFF", dunkel="#FFFFFF", leit="#FFFFFF", akzent="#FFFFFF")
    monkeypatch.setenv(design.UMGEBUNG, schreibe(werkstatt / "weiss.json", weiss))
    with pytest.raises(SystemExit) as ende:
        design.laden()
    assert "kein gueltiges Design" in str(ende.value) and "zu schwach" in str(ende.value)


@pytest.mark.parametrize("inhalt,text", [("{nicht json", "laesst sich nicht lesen"), ("[]", "kein gueltiges Design"),
                                         ('{"farben": {}}', "kein gueltiges Design")])
def test_umgebungsvariable_mit_kaputter_datei_bricht_ab(werkstatt, monkeypatch, inhalt, text):
    (werkstatt / "e.json").write_text(inhalt, encoding="utf-8")
    monkeypatch.setenv(design.UMGEBUNG, str(werkstatt / "e.json"))
    with pytest.raises(SystemExit) as ende:
        design.laden()
    assert text in str(ende.value)


def test_umgebungsvariable_mit_fehlender_datei_bricht_ab(werkstatt, monkeypatch):
    monkeypatch.setenv(design.UMGEBUNG, str(werkstatt / "gibt_es_nicht.json"))
    with pytest.raises(SystemExit) as ende:
        design.laden()
    assert "laesst sich nicht lesen" in str(ende.value)


# ---------------------------------------------------------------- pruefen: neue Regeln
def test_pruefen_bewertungsfarbe_auf_weiss_unsichtbar():
    fehler = stufen(design.pruefen(kunde(gut="#FAFAFA")), "FEHLER")
    assert any("Bewertungsfarbe 'gut'" in text and "nicht zu sehen" in text for text in fehler)


def test_pruefen_bewertungsfarben_des_hausdesigns_sind_sichtbar():
    assert not [t for t in stufen(design.pruefen(kunde()), "FEHLER") if "Bewertungsfarbe" in t]


def test_pruefen_stufen_mit_zu_wenig_verschiedenen_farben():
    fehler = stufen(design.pruefen(kunde(stufen=["#112233"] * 4 + ["#223344"] * 4)), "FEHLER")
    assert any("'stufen'" in text and "mindestens 6 verschiedene" in text and "gefunden 2" in text for text in fehler)


def test_pruefen_stufen_gross_klein_zaehlt_als_dieselbe_farbe():
    fehler = stufen(design.pruefen(kunde(stufen=["#112233", "#aabbcc"] * 4)), "FEHLER")
    assert any("mindestens 6 verschiedene" in text for text in fehler)


def test_pruefen_serie_mit_unsichtbaren_ersten_fuenf_farben():
    serie = ["#FEFEFE", "#FDFDFD", "#FCFCFC", "#FBFBFB", "#FAFAFA", "#222222", "#333333", "#444444"]
    fehler = stufen(design.pruefen(kunde(serie=serie)), "FEHLER")
    assert any("'serie'" in text and "nicht zu sehen" in text for text in fehler)


def test_pruefen_blasse_farbe_ab_der_sechsten_stelle_ist_erlaubt():
    serie = ["#222222", "#333333", "#444444", "#555555", "#666666", "#FEFEFE", "#FDFDFD", "#FCFCFC"]
    assert stufen(design.pruefen(kunde(serie=serie)), "FEHLER") == []


def test_pruefen_erste_stufe_zu_hell():
    hell = ["#CCCCCC", "#1F5FAF", "#333333", "#444444", "#555555", "#666666", "#777777", "#888888"]
    fehler = stufen(design.pruefen(kunde(stufen=hell)), "FEHLER")
    assert any("erste Stufe" in text and "zu hell" in text for text in fehler)


@pytest.mark.parametrize("wert", ["", "   ", "Muster<Schrift", "Muster & Sohn", 'Muster "Sans"', 5, None, ["Arial"]])
def test_pruefen_schriftname_muss_brauchbarer_text_sein(wert):
    roh = kunde()
    roh["schrift"] = dict(design.HAUS["schrift"], normal=wert)
    fehler = stufen(design.pruefen(roh), "FEHLER")
    assert any("Familienname als Text" in text for text in fehler)


def test_pruefen_rolle_normal_fehlt():
    roh = kunde()
    roh["schrift"] = {"leicht": "Arial", "halbfett": "Arial Black", "zahl": "Arial Black"}
    assert any("'normal' fehlt" in text for text in stufen(design.pruefen(roh), "FEHLER"))


def test_pruefen_fehlende_halbfett_und_zahl_sind_ein_hinweis(werkstatt):
    roh = kunde()
    roh["schrift"] = {"normal": "Arial"}
    befunde = design.pruefen(roh)
    assert stufen(befunde, "FEHLER") == []
    assert any("halbfett" in text and "zahl" in text and "Normalschrift" in text for text in stufen(befunde, "HINWEIS"))


def test_pruefen_vollstaendige_schrift_hat_keinen_schrifthinweis(werkstatt):
    assert not [t for t in stufen(design.pruefen(kunde()), "HINWEIS") if "Normalschrift" in t]


def test_pruefen_leere_schriftangabe_ist_kein_fehler():
    roh = kunde()
    roh["schrift"] = {}
    assert stufen(design.pruefen(roh), "FEHLER") == []


def test_pruefen_akzent_aehnlich_einer_bewertungsfarbe_ist_ein_hinweis():
    befunde = design.pruefen(kunde(akzent="#EE4040"))
    assert stufen(befunde, "FEHLER") == []
    assert any("'akzent'" in text and "'schlecht'" in text and "verwechseln" in text for text in stufen(befunde, "HINWEIS"))


def test_pruefen_leitfarbe_aehnlich_einer_bewertungsfarbe_ist_ein_hinweis():
    befunde = design.pruefen(kunde(gut="#1F5FB0"))
    assert any("'leit'" in text and "'gut'" in text for text in stufen(befunde, "HINWEIS"))


def test_pruefen_unaehnliche_marke_hat_keinen_verwechslungshinweis():
    assert not [t for t in stufen(design.pruefen(kunde(akzent="#6A1B9A")), "HINWEIS") if "verwechseln" in t]


# ---------------------------------------------------------------- ableiten: keine Farbe zweimal in der Serie
def test_ableiten_serie_hat_keine_farbe_zweimal():
    f = design.ableiten({"tinte": "#062246", "dunkel": "#062246", "leit": "#0F54AC", "akzent": "#0F54AC"})
    assert len({x.upper() for x in f["serie"]}) == 8
    assert f["serie"][0] == "#062246" and f["serie"][1] == "#0F54AC"      # die ersten bleiben, die Dublette weicht aus


def test_ableiten_serie_dublette_gross_klein():
    f = design.ableiten({"tinte": "#062246", "dunkel": "#062246", "leit": "#0F54AC", "akzent": "#0f54ac"})
    assert len({x.upper() for x in f["serie"]}) == 8


def test_ableiten_serie_des_hausdesigns_bleibt_wie_sie_ist(werkstatt):
    assert design.ableiten(design.HAUS["farben"])["serie"] == design.HAUS["farben"]["serie"]


# ---------------------------------------------------------------- VB-Funktion
def vb_code(xml):
    from xml.sax.saxutils import unescape
    return unescape(xml[xml.index("<Code>"):xml.index("</Code>")])


def test_laufzeit_anfuehrungszeichen_im_namen_werden_verdoppelt(werkstatt):
    roh = kunde()
    roh["schrift"] = {"normal": 'Mu"ster'}
    d = design.Design("kunde", roh)
    xml = design.schrift_zur_laufzeit(report_xml('Mu"ster'), d, esc_xml)
    assert '"Mu""ster"' in vb_code(xml)


def test_laufzeit_ersatz_gilt_wenn_die_schriftliste_nicht_lesbar_ist(werkstatt):
    code = vb_code(design.schrift_zur_laufzeit(report_xml("Roboto"), haus_design(werkstatt), esc_xml))
    assert "Catch" in code and 'namen = ""' in code                       # Lesefehler -> leere Liste
    assert 'Dim alle As Boolean = (namen <> "")' in code                  # leere Liste -> nie "alle da"
