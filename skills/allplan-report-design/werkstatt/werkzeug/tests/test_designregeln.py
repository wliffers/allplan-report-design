# -*- coding: utf-8 -*-
"""Designregeln des Master-Reports und der Begleit-Reports - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_designregeln.py -q

Alles, was gebaut wird, entsteht in einem TEMP-ORDNER (tmp_path_factory), nie in out/, vorlagen/ oder in den Sprachtabellen:
ein Testlauf darf den Report eines Kunden nicht ueberschreiben. Die Regeln rechnen mit dem geladenen Design (c.DESIGN), nicht mit
festen Hauswerten; conftest.py setzt REPORT_DESIGN=haus, damit der Lauf ohne Design-Sperre durchkommt.

Geprueft werden
  Quelltext   master/viz.py, bausteine.py, seiten/*.py, build_master.py, build_auswahl.py, masse.py und die Bauskripte der
              Begleit-Reports (grundriss, abwicklung, bewehrung, listen, projektlisten, bauordnung): kein Hex-Wert, keine alten
              Namen (c.SKY, c.ORANGE, c.F_LIGHT), keine feste Schrift ausser der Symbolschrift (b.SYMBOL)
  Reports     der gebaute Master und die sechs Begleit-Reports (Bauordnung nur als Quelltext, ihr Bau ist langsam):
              Schriftrollen 0/2/3 plus Symbolschrift, jede feste Farbe aus dem System (Farbnamen nur "Transparent"), kein
              FontWeight Bold, keine Akzentschrift (Text, Diagrammbeschriftung, Messfeld) auf hellem Grund, kleinste Schrift
              7 pt (Etikett 6,5), fester Text bricht nicht um (nur Master)
  Vorlagen    die ausgelieferten vorlagen/deu und vorlagen/eng: Funktion Schrift, keine alte Palette, keine feste Schrift

Was die Tests NICHT fangen: eine Farbe, die erst zur Laufzeit aus einem Ausdruck entsteht (Farbskalen, IIf), ein Hintergrund aus
einem Ausdruck, eine Linie oder ein Rand ohne gesetzte Farbe (Standard ist Schwarz - das zeigt nur das Bild, siehe die Pixelzaehlung
in GESTALTUNG.md), und Text, der erst durch die Daten zu lang wird (dafuer sind die Bilder mit master, master_en und gross da).
"""
import glob
import importlib
import os
import re
import sys
import xml.etree.ElementTree as ET

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
WERKSTATT = os.path.normpath(os.path.join(HERE, "..", ".."))
MASTER = os.path.join(WERKSTATT, "master")
BEGLEIT = [("Grundriss", "grundriss", "build_grundriss"), ("Abwicklung", "abwicklung", "build_abwicklung"),
           ("Wandbelag", "abwicklung", "build_wandbelag"), ("Bewehrung", "bewehrung", "build_bewehrung"),
           ("Listen", "listen", "build_listen"), ("Planliste", "projektlisten", "build_planliste")]
for _pfad in [MASTER, os.path.join(MASTER, "seiten")] + [os.path.join(MASTER, ordner) for _n, ordner, _m in BEGLEIT]:
    sys.path.insert(0, _pfad)

import core as c  # noqa: E402
import design  # noqa: E402

NS = "{http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition}"
SYMBOLSCHRIFT = "Segoe UI Symbol"
SYMBOLZEICHEN = set("■●▲▼✓✕○★→█ ")       # was in der Symbolschrift stehen darf (Roboto hat diese Zeichen nicht)
ERLAUBTE_FAMILIEN = {"=Code.Schrift(0)", "=Code.Schrift(2)", "=Code.Schrift(3)"}      # normal, halbfett, Zahl - nie 1 (leicht)
FARBNAMEN = {"Transparent"}
QUELLEN = ([os.path.join(MASTER, n) for n in ("viz.py", "bausteine.py", "build_master.py", "build_auswahl.py", "masse.py")]
           + [os.path.join(MASTER, "seiten", n) for n in sorted(os.listdir(os.path.join(MASTER, "seiten"))) if n.endswith(".py")]
           + [os.path.join(MASTER, ordner, modul + ".py") for _n, ordner, modul in BEGLEIT]
           + [os.path.join(MASTER, "bauordnung", "build_bauordnung.py")])
BERICHTE = ["Master"] + [n for n, _o, _m in BEGLEIT]


def _quelle(pfad):
    with open(pfad, encoding="utf-8") as handle:
        return handle.read()


# ---------------------------------------------------------------- die gebauten Reports (Temp-Ordner, einmal je Testlauf)
@pytest.fixture(scope="module")
def baeume(tmp_path_factory):
    """Name -> (Wurzel, Elternabbildung) fuer den Master und die sechs Begleit-Reports. Gebaut wird nur nach tmp, nie nach out/."""
    ordner = str(tmp_path_factory.mktemp("designregeln"))
    mp = pytest.MonkeyPatch()
    ergebnis = {}
    try:
        import build_master as bm
        mp.setattr(bm, "OUT_DIR", ordner)
        mp.setattr(bm, "katalog", lambda module: None)       # schriebe sonst skill/.../bausteine.md
        ergebnis["Master"] = bm.build()
        for name, _o, modul in BEGLEIT:
            m = importlib.import_module(modul)
            mp.setattr(m, "OUT_DIR", ordner)
            ergebnis[name] = m.build()
    finally:
        mp.undo()
    for ziel in ergebnis.values():
        assert os.path.normpath(os.path.dirname(ziel)) == os.path.normpath(ordner), "gebaut ausserhalb des Temp-Ordners: %s" % ziel
    baeume = {}
    for name, ziel in ergebnis.items():
        wurzel = ET.parse(ziel).getroot()
        baeume[name] = (wurzel, {kind: parent for parent in wurzel.iter() for kind in parent})
    return baeume


def _text(element, name):
    kind = element.find(NS + name)
    return kind.text if kind is not None else None


def _schrift_stile(wurzel):
    """Jeder Style mit FontFamily (Textlauf, Diagrammbeschriftung, Messfeld): (Style, Wert oder None, Familie, Groesse, Farbe)."""
    for stil in wurzel.iter(NS + "Style"):
        familie = _text(stil, "FontFamily")
        if familie is None:
            continue
        groesse = _text(stil, "FontSize")
        yield (stil, None, familie, float(groesse[:-2]) if groesse and re.fullmatch(r"[\d.]+pt", groesse) else None,
               _text(stil, "Color"))


def _lauf_stile(wurzel):
    """Jedes TextRun mit Wert und Stil: (Element, Wert, Familie, Groesse in pt oder None, Farbe)."""
    for run in wurzel.iter(NS + "TextRun"):
        stil = run.find(NS + "Style")
        wert = _text(run, "Value") or ""
        familie = _text(stil, "FontFamily") if stil is not None else None
        groesse = _text(stil, "FontSize") if stil is not None else None
        farbe = _text(stil, "Color") if stil is not None else None
        yield run, wert, familie, float(groesse[:-2]) if groesse and re.fullmatch(r"[\d.]+pt", groesse) else None, farbe


# ---------------------------------------------------------------- 1. Quelltext
@pytest.mark.parametrize("pfad", QUELLEN, ids=lambda p: os.path.relpath(p, MASTER))
def test_kein_hex_wert_im_quelltext(pfad):
    funde = [(n + 1, z.strip()) for n, z in enumerate(_quelle(pfad).splitlines()) if re.search(r"#[0-9A-Fa-f]{6}\b", z)]
    assert not funde, "Hex-Wert statt c.<Name>: %s" % funde


@pytest.mark.parametrize("pfad", QUELLEN, ids=lambda p: os.path.relpath(p, MASTER))
def test_keine_veralteten_namen_im_quelltext(pfad):
    funde = [(n + 1, z.strip()) for n, z in enumerate(_quelle(pfad).splitlines()) if re.search(r"\b(c\.)?(SKY|ORANGE|F_LIGHT)\b", z)]
    assert not funde, "veralteter Name (c.SKY, c.ORANGE, c.F_LIGHT): %s" % funde


@pytest.mark.parametrize("pfad", QUELLEN, ids=lambda p: os.path.relpath(p, MASTER))
def test_keine_feste_schrift_im_quelltext(pfad):
    """Schriftnamen stehen nur in design.py; hier nur c.F, c.F_SEMI, c.F_ZAHL und b.SYMBOL (Segoe UI Symbol). Als Wort in einem
    Erklaertext ("Schrift Segoe UI Symbol nehmen") ist der Name erlaubt - gesucht wird der Name als Schriftangabe."""
    funde = []
    for n, zeile in enumerate(_quelle(pfad).splitlines()):
        if zeile.lstrip().startswith("#") or '"""' in zeile:
            continue
        if os.path.basename(pfad) != "bausteine.py" and re.search(
                r"""["'](Segoe UI|Consolas|Arial|Calibri|Roboto[^"']*)["']|<FontFamily>[A-Za-z]""", zeile):
            funde.append((n + 1, zeile.strip()[:100]))
        if re.search(r"<FontWeight>\s*Bold", zeile):
            funde.append((n + 1, zeile.strip()[:100]))
    assert not funde, "feste Schrift oder FontWeight Bold: %s" % funde


def test_jede_master_seite_hat_einen_titel():
    """TITEL steht in der Dokumentstruktur (PDF-Lesezeichen); ohne ihn steht dort der Dateiname ("s04_messanzeigen")."""
    fehlt = [n for n in sorted(os.listdir(os.path.join(MASTER, "seiten"))) if re.fullmatch(r"s\d\d_.*\.py", n)
             and not re.search(r"^TITEL\s*=", _quelle(os.path.join(MASTER, "seiten", n)), re.M)]
    assert not fehlt, fehlt


# ---------------------------------------------------------------- 2. Reports: Schrift
def _familie_ausdruck_ok(familie):
    """Ein Ausdruck als Schriftfamilie (Haken oder Zahl je nach Wert) darf nur Code.Schrift(0|2|3) und die Symbolschrift nennen."""
    if not familie.startswith("="):
        return False
    if re.search(r"Roboto|Segoe UI(?! Symbol)|Arial|Calibri|Consolas|Schrift\((?![023]\))", familie):
        return False
    return "Code.Schrift(" in familie
@pytest.mark.parametrize("name", BERICHTE)
def test_hoechstens_drei_schriftrollen_und_die_symbolschrift(baeume, name):
    wurzel, _ = baeume[name]
    familien = {t.text for t in wurzel.iter(NS + "FontFamily")}
    fremd = {f for f in familien - ERLAUBTE_FAMILIEN - {SYMBOLSCHRIFT} if not _familie_ausdruck_ok(f)}
    assert not fremd, "feste oder leichte Schrift im Report: %s" % sorted(fremd)
    assert len({f for f in familien if not f.startswith("=IIf") and f != SYMBOLSCHRIFT}) <= 3


@pytest.mark.parametrize("name", BERICHTE)
def test_kein_fettschnitt_bold(baeume, name):
    """Halbfett ist c.F_SEMI (Roboto Medium); <FontWeight>Bold wuerde Roboto Bold laden (ein viertes Gewicht)."""
    wurzel, _ = baeume[name]
    bold = {t.text for t in wurzel.iter(NS + "FontWeight") if (t.text or "").strip() not in ("Normal", "")}
    assert not bold, "FontWeight %s" % sorted(bold)


@pytest.mark.parametrize("name", BERICHTE)
def test_symbolschrift_nur_fuer_symbole(baeume, name):
    wurzel, _ = baeume[name]
    falsch = [wert for _r, wert, familie, _g, _f in _lauf_stile(wurzel)
              if familie == SYMBOLSCHRIFT and not wert.startswith("=") and not set(wert) <= SYMBOLZEICHEN]
    assert not falsch, "Text in der Symbolschrift: %s" % falsch[:5]


@pytest.mark.parametrize("name", BERICHTE)
def test_kleinste_schrift_7_pt_etikett_6_5(baeume, name):
    """Unter 7 pt nur Etiketten (erster Textlauf = Kennung wie "D040  ") und leere Platzhalter; nie unter 6,5 pt."""
    wurzel, eltern = baeume[name]
    zu_klein = []
    for run, wert, _fam, groesse, _farbe in _lauf_stile(wurzel):
        if groesse is None or groesse >= 7 or not wert.strip() or _text(run.find(NS + "Style"), "Format") == ";;;":
            continue                      # (Format ;;; = unsichtbarer Hilfslauf)
        absatz = eltern[eltern[run]]
        erster = (_text(absatz.find(NS + "TextRuns")[0], "Value") or "")
        ist_etikett = re.fullmatch(r"[A-Z]\d{3}\s*", erster) is not None and groesse >= 6.5
        if not ist_etikett:
            zu_klein.append((groesse, wert[:50]))
    assert not zu_klein, zu_klein[:8]


# ---------------------------------------------------------------- 2. Reports: Farbe
def _erlaubte_farben():
    """Alle festen Farben des Gestaltungssystems (Namen in core.py, Materialfarben, Rampen)."""
    ok = set()
    for wert in vars(c).values():
        if isinstance(wert, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", wert):
            ok.add(wert.upper())
        if isinstance(wert, (list, tuple)):
            for teil in wert:
                for x in (teil if isinstance(teil, (list, tuple)) else (teil,)):
                    if isinstance(x, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", x):
                        ok.add(x.upper())
    ok |= {f.upper() for _g, f in c.MATERIALGRUPPE}
    import s05_tabellen                                        # die fuenf Stufen der Farbskala-Legende: c.BLUE nach Weiss gemischt
    ok |= {s05_tabellen.heat_fest(t).upper() for t in (0.12, 0.3, 0.5, 0.72, 0.95)}
    return ok


def _farb_elemente(wurzel):
    """Alle Elemente, deren Tag auf Color endet (Color, BackgroundColor, DigitColor, ...) mit festem Text (kein Ausdruck)."""
    for e in wurzel.iter():
        if e.tag.endswith("Color") and e.text and e.text.strip() and not e.text.startswith("="):
            yield e


@pytest.mark.parametrize("name", BERICHTE)
def test_jede_feste_farbe_kommt_aus_dem_gestaltungssystem(baeume, name):
    wurzel, _ = baeume[name]
    ok = _erlaubte_farben()
    fremd = set()
    for e in _farb_elemente(wurzel):
        wert = e.text.strip()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", wert):
            if wert.upper() not in ok:
                fremd.add(wert)
        elif wert not in FARBNAMEN:
            fremd.add(wert)
    assert not fremd, "Farbe ausserhalb des Systems (Hex nicht im System oder ein Farbname wie Black/Red/White): %s" % sorted(fremd)


def _grund_ist_dunkel(element, eltern):
    """Hintergrund des Elements oder des naechsten Behaelters darueber (Textbox, Rechteck, Diagramm, Messfeld; fester Wert);
    ohne Angabe Weiss. Dunkel = Kontrast zu Weiss >= 3. None bei einem Hintergrund aus einem Ausdruck."""
    knoten = element
    while knoten is not None:
        if knoten.tag in (NS + "Textbox", NS + "Rectangle", NS + "Chart", NS + "GaugePanel"):
            stil = knoten.find(NS + "Style")
            grund = _text(stil, "BackgroundColor") if stil is not None else None
            if grund and re.fullmatch(r"#[0-9A-Fa-f]{6}", grund):
                return design.kontrast(grund, c.WHITE) >= 3
            if grund and grund.startswith("="):
                return None
        knoten = eltern.get(knoten)
    return False


@pytest.mark.parametrize("name", BERICHTE)
def test_keine_akzentschrift_auf_hellem_grund(baeume, name):
    """Text, Diagrammbeschriftung, Messfeld-Text: der Akzent (im Hausdesign Tuerkis) ist auf Weiss nie Schrift."""
    wurzel, eltern = baeume[name]
    akzent = c.AKZENT.upper()
    auf_weiss = []
    for stil, _w, _fam, _g, farbe in _schrift_stile(wurzel):
        if not farbe or akzent not in farbe.upper():
            continue
        if _grund_ist_dunkel(stil, eltern) is False:
            auf_weiss.append((farbe[:30], eltern[stil].tag.replace(NS, "")))
    assert not auf_weiss, "Akzentfarbe als Schrift auf hellem Grund: %s" % auf_weiss[:5]


def test_gegenprobe_akzent_in_diagrammbeschriftung_wird_gefangen(baeume):
    """Die Regel muss anschlagen, wenn jemand v.dlabel(color=c.AKZENT) auf Weiss setzt (der Fund bliebe sonst unbemerkt)."""
    import viz as v
    chart = v.chart("Probe", 0, 0, 5, 5, [v.S("S", {"Y": "=1"}, label=v.dlabel(color=c.AKZENT))], [], nomember=True)
    wurzel = ET.fromstring("<r xmlns='%s'>%s</r>" % (NS[1:-1], chart))
    eltern = {kind: parent for parent in wurzel.iter() for kind in parent}
    gefunden = [s for s, _w, _f, _g, farbe in _schrift_stile(wurzel) if farbe == c.AKZENT and _grund_ist_dunkel(s, eltern) is False]
    assert gefunden


def test_gegenprobe_farbname_wird_gefangen():
    wurzel = ET.fromstring("<r xmlns='%s'><Style><Color>Black</Color><BackgroundColor>Transparent</BackgroundColor></Style></r>" % NS[1:-1])
    assert [e.text for e in _farb_elemente(wurzel) if e.text not in FARBNAMEN and not e.text.startswith("#")] == ["Black"]


def test_akzent_auf_dunkel_ist_der_akzent_des_designs(baeume):
    """Auf dem Titelband steht der Akzent als c.AKZENT_DUNKEL (im Hausdesign dieselbe Farbe wie c.AKZENT)."""
    wurzel, _ = baeume["Master"]
    farben = {farbe.upper() for _r, wert, _f, _g, farbe in _lauf_stile(wurzel) if farbe and re.fullmatch(r"#[0-9A-Fa-f]{6}", farbe)}
    assert c.AKZENT_DUNKEL.upper() in farben


@pytest.mark.parametrize("name", BERICHTE)
def test_hoechstens_zwei_akzente_je_seite_im_titelband(baeume, name):
    """Titelband: der Akzent als Strich (Flaeche), als Etikett und als Kennzahl - zusammen hoechstens zwei Schriftstellen."""
    wurzel, eltern = baeume[name]
    akzent = c.AKZENT_DUNKEL.upper()
    texte = [wert for _r, wert, _f, _g, farbe in _lauf_stile(wurzel) if farbe and farbe.upper() == akzent and wert.strip()]
    # je Seite (Kopfband) ein Etikett und hoechstens eine Kennzahl; Kachelstriche sind Flaechen, keine Schrift
    assert len(texte) <= 2 * 10, texte[:20]


# ---------------------------------------------------------------- 2. Reports: nichts bricht um (nur Master)
def _schriftdatei(familie):
    m = re.search(r"Schrift\((\d)\)", familie or "")
    return {"0": "Roboto-Regular.ttf", "2": "Roboto-Medium.ttf", "3": "Roboto-Black.ttf"}[m.group(1)] if m else "seguisym.ttf"


def test_fester_text_passt_in_sein_feld(baeume):
    """Fester Text (ohne Ausdruck) hoechstens 97 % der Feldbreite je Zeile, gemessen mit der Schrift (PIL gemessen ist rund 2 %
    pessimistisch). Kein Fenster-Aufschlag: der steht in den Bildern und in GESTALTUNG.md (10 % bei Text bis 8,5 pt)."""
    pil = pytest.importorskip("PIL.ImageFont")
    fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    geladen = {}
    wurzel, _ = baeume["Master"]
    zu_breit = []
    for tb in wurzel.iter(NS + "Textbox"):
        breite, hoehe = _text(tb, "Width"), _text(tb, "Height")
        if not breite or not breite.endswith("cm"):
            continue
        stil = tb.find(NS + "Style")
        luft = sum(float(_text(stil, k)[:-2]) for k in ("PaddingLeft", "PaddingRight") if stil is not None and _text(stil, k)) / 72 * 2.54
        nutz = float(breite[:-2]) - luft
        for absatz in tb.iter(NS + "Paragraph"):
            summe, groesste, fest = 0.0, 0.0, True
            for _r, wert, fam, groesse, _f in _lauf_stile(absatz):
                if wert.startswith("=") or groesse is None:
                    fest = False
                    break
                datei = _schriftdatei(fam)
                if datei not in geladen:
                    try:
                        geladen[datei] = pil.truetype(os.path.join(fonts, datei), 1000)
                    except OSError:
                        pytest.skip("Schrift %s fehlt" % datei)
                summe += geladen[datei].getlength(wert) / 1000.0 * groesse / 72 * 2.54
                groesste = max(groesste, groesse)
            if not fest or not groesste:
                continue
            zeilen = max(1, int(float(hoehe[:-2]) * 72 / 2.54 // (groesste * 1.25)))
            if summe > nutz * 0.97 * zeilen:
                zu_breit.append((tb.get("Name"), round(summe, 2), round(nutz * zeilen, 2)))
    assert not zu_breit, zu_breit[:8]


# ---------------------------------------------------------------- 3. Die ausgelieferten Vorlagen
VORLAGEN = sorted(glob.glob(os.path.join(WERKSTATT, "vorlagen", "deu", "*.rdlc")) + glob.glob(os.path.join(WERKSTATT, "vorlagen", "eng", "*.rdlc")))
ALTE_PALETTE = ("#2563EB", "#F97316", "#0F172A", "#334155", "#64748B", "#0B1F3A")


@pytest.mark.skipif(not VORLAGEN, reason="vorlagen/deu und vorlagen/eng fehlen")
@pytest.mark.parametrize("pfad", VORLAGEN, ids=lambda p: os.path.relpath(p, os.path.join(WERKSTATT, "vorlagen")))
def test_vorlage_hat_schriftfunktion_keine_alte_palette_keine_feste_schrift(pfad):
    text = _quelle(pfad)
    assert "Function Schrift(" in text or "Function Schrift (" in text, "die Funktion Schrift fehlt im Code-Block"
    alt = [p for p in ALTE_PALETTE if p.lower() in text.lower()]
    assert not alt, "alter Palettenwert: %s" % alt
    familien = set(re.findall(r"<FontFamily>([^<]*)</FontFamily>", text))
    fremd = {f for f in familien - ERLAUBTE_FAMILIEN - {SYMBOLSCHRIFT} if not _familie_ausdruck_ok(f.replace("&lt;", "<").replace("&gt;", ">"))}
    assert not fremd, "feste Schriftfamilie: %s" % sorted(fremd)
