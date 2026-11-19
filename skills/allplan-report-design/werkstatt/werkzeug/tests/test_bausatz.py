# -*- coding: utf-8 -*-
"""Pruefungen des Bausatzes master/core.py - ohne Renderer und ohne Allplan.

    python -m pytest werkzeug/tests/test_bausatz.py -q

Drei Gruppen: (1) alte Aufrufe liefern unveraendertes XML (SHA-256 aus dem Stand VOR der Erweiterung), (2) die neuen Argumente
erzeugen das erwartete XML, (3) abgelehnte Vorgaben werfen ValueError mit der Meldung, die der Nutzer lesen soll.
"""
import hashlib
import os
import re
import subprocess
import sys
import xml.dom.minidom

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "master"))

import core as c  # noqa: E402


def sha(text):
    return hashlib.sha256(re.sub(r"<rd:ReportID>[^<]*</rd:ReportID>", "", text).encode()).hexdigest()


def wohlgeformt(text):
    xml.dom.minidom.parseString(text.encode("utf-8"))


DS = [c.dataset("AllplanReport", "SELECT 1", [("A", "String")])]
ZEILEN = [("kopf", 0.5, ["<a/>", "<b/>"]), ("daten", 0.5, ["<c/>", "<d/>"]), ("fuss", 0.5, ["<e/>", "<f/>"])]


# ---------------------------------------------------------------- 1. alte Aufrufe: unveraendertes XML
ALT = {
    "rect": ("fbc8265b90d3bdf6a2ec41e537d29129b110304d3a8a494526b466e11ba9081b",
             lambda: c.rect("R", 1, 2, 3, 4, "<X/>", bg="#fff", page_break=True, hidden="=1", keep=False, label="L")),
    "rect_schlicht": ("a8fcf77c9c82092372185498e8c65689395620295c66e96157d81c4d58f1fda6", lambda: c.rect("R", None, 0, 0, 0)),
    "parameter": ("f89116d9bbde739f3d7f1f4e0e0221a2268463d9adf8884f92c445a4a93e604a",
                  lambda: c.parameter("P", "Float", "1.5", "Preis", [("a", "A"), ("b", "B")])),
    "tablix_gruppe": ("ac5d4a29c74af11c553ad5544f884fc38c1a78de0200ef8461e243f01531076d",
                      lambda: c.tablix("T", 0, 0, [2, 3], ZEILEN, group="=Fields!X.Value", sort="=1", filter_expr="True")),
    "tablix_detail": ("6f25a763c3f284ba3bae2a07815925324dd0d39cd47a1309080157c99b39fb64",
                      lambda: c.tablix("T", 0, 0, [2], [("kopf", 0.5, ["<a/>"]), ("daten", 0.5, ["<c/>"])])),
    "report": ("29129f9e25fed1c7500861787dc91ef8bfe11acad9fda835fe0781c4e4161aff",
               lambda: c.report(["<i/>", "<j/>"], DS, extra_params=c.parameter("P", "String", "x", "p"), code="Public x",
                                footer_xml="<f/>", labels=["a", "b"], embedded_xml="<EmbeddedImages/>")),
    "report_ohne_fuss": ("c7ee6074ec526292a548c0ad570cf81e1be0c639214f136f5fb3b04961ae4eed", lambda: c.report(["<i/>"], DS)),
    "bild": ("bbd3a236e18f46453538261ec9d694d3177fc55ce29377c37aa9f32abb5baeb6", lambda: c.image("I", 0, 0, 1, 1, "v", action="Marke")),
    "text": ("7711e94c5aaafd554d95385c5d37af137e11b8c82c9b3a691f6775b9fe940e49",
             lambda: c.text("T", 1, 2, 3, 4, [c.para([c.run("x", 9)])], align="Right", valign="Middle", bg="#fff", pad=(1, 2, 3, 4),
                            border_xml=c.edge(["Bottom"]), grow=True, hidden="=1", bg_expr="=x", rotate="Rotate270")),
    "zelle": ("c5177d5ac17dab3874b529b14c3d8f8d39e69b67bfac758818e6ac3c48ed2917", lambda: c.cell("Z", c.run("x"), "Right")),
    "linie": ("cf5db67fa571377b664e2645cc158512699368072ba722ac2f4e077c30e67097", lambda: c.line("L", 1, 2, 3)),
    "filters": ("21f0a3c71d22e108c6543478b92230bea067980af924c2a1fc26e53f1ce5841a", lambda: c.filters("a<b")),
    "topn": ("29eef7d34258d7aa32a8621eb13b695c0ab51d3eadf4613db89ccf29a1625975", lambda: c.topn("Sum(x)", 3, True)),
    "tablix_sortiert": ("cd639c8ee5d38ca9a9ef96eefa780a82df6cd9502559d134d4c3de5b15ebd884",
                        lambda: c.tablix("T", 0, 0, [2], [("kopf", 0.5, ["<a/>"]), ("daten", 0.5, ["<c/>"])], group="=Fields!X.Value",
                                         sort="=Sum(1)", sort_desc=True, repeat_header=False)),
    "tablix_fuss_ohne_gruppe": ("698e6451772ecf1c4952c5510dbad1c82b1336b83f950ef3c42b45782ef77220",
                                lambda: c.tablix("T", 1, 2, [2, 3], [("kopf", 0.5, ["<a/>", "<b/>"]), ("daten", 0.5, ["<c/>", "<d/>"]),
                                                                    ("fuss", 0.5, ["<e/>", "<f/>"])], sort="=Fields!X.Value", filter_expr="x>1")),
    "dataset": ("d8e7e68f26917fd478c67cde0d67d4a9578257ce05c77d2d75cf3e0a6bda9530",
                lambda: c.dataset("D", "SELECT 1", [("A", "String"), ("B", "Double")])),
}


def test_dataset_unterscheidet_gross_und_klein():
    """Ohne <CaseSensitivity>True</CaseSensitivity> gruppiert der ReportViewer "Flur" und "FLUR" zusammen, CountDistinct zaehlt
    aber zwei (in Allplan gemessen): Rest-Zeile doppelt, Seite laenger. Abgesehen von dieser Angabe ist das XML der alte Stand
    (die drei Pruefsummen dataset, report, report_ohne_fuss sind deshalb neu; ohne die Angabe ergaben sie die alten)."""
    x = c.dataset("D", "SELECT 1", [("A", "String")])
    assert x.count("<CaseSensitivity>True</CaseSensitivity>") == 1
    assert x.index("</Fields>") < x.index("<CaseSensitivity>") < x.index("<rd:DataSetInfo>")


@pytest.mark.parametrize("name", sorted(ALT))
def test_alte_aufrufe_liefern_unveraendertes_xml(name):
    erwartet, bauen = ALT[name]
    assert sha(bauen()) == erwartet


def test_render_argumente_alt_unveraendert(monkeypatch):
    monkeypatch.setattr(c, "RENDER", os.path.abspath(__file__))
    assert c.render_argumente("a.rdlc", "d.json", "aus") == [os.path.abspath(__file__), "a.rdlc", "d.json", "aus", "--dpi=110",
                                                            "Project_Name=Musterprojekt"]


# ---------------------------------------------------------------- 2. neue Argumente: erwartetes XML
def test_parameter_arten():
    x = c.parameter("M", "String", ["Beton", "Holz"], "Material", werte=[("Beton", "Beton"), ("Holz", "Holz")], multi=True)
    assert "<DefaultValue><Values><Value>Beton</Value><Value>Holz</Value></Values></DefaultValue>" in x
    assert "<MultiValue>true</MultiValue>" in x and "<ValidValues>" in x
    assert x.index("<Prompt>") < x.index("<MultiValue>") < x.index("<ValidValues>")      # Reihenfolge wie in Allplans Vorlagen
    n = c.parameter("N", "String", None, "x", nullable=True)
    assert "<Nullable>true</Nullable>" in n and "<DefaultValue>" not in n
    assert "<AllowBlank>true</AllowBlank>" in c.parameter("B", "String", None, "x", allowblank=True)
    assert "<Hidden>true</Hidden>" in c.parameter("H", "String", "geheim", "x", hidden=True)
    for teil in (x, n):
        wohlgeformt("<r>%s</r>" % teil)


def test_parameter_distinct_ersetzt_den_prompt():
    x = c.parameter("L", "String", None, "wird ersetzt", multi=True, allowblank=True, distinct="Material")
    assert "<Prompt>Distinct(Fields!Material.Value)</Prompt>" in x
    assert "wird ersetzt" not in x and "<DefaultValue>" not in x


@pytest.mark.parametrize("datum", ["2026-11-19", "2026-11-19T00:00:00"])
def test_datetime_iso_wird_angenommen(datum):
    assert "<Value>%s</Value>" % datum in c.parameter("D", "DateTime", datum, "Datum")


def test_report_variablen_codemodules_classes():
    x = c.report(["<i/>"], DS, variablen=[("V_Ges", 'Sum(Fields!A.Value, "AllplanReport")'), ("V_Zwei", "=Variables!V_Ges.Value * 2")],
                 codemodules=["System.Drawing", "System.Windows.Forms"], classes=[("Hilfe.Zaehler", "Zaehler")])
    wohlgeformt(x)
    assert ('<Variables><Variable Name="V_Ges"><Value>=Sum(Fields!A.Value, "AllplanReport")</Value></Variable>'
            '<Variable Name="V_Zwei"><Value>=Variables!V_Ges.Value * 2</Value></Variable></Variables>') in x
    assert x.index("<Variables>") < x.index("<Language>")                                 # Variablen direkt unter <Report>
    assert ("<CodeModules><CodeModule>System.Drawing</CodeModule><CodeModule>System.Windows.Forms</CodeModule></CodeModules>"
            "<Classes><Class><ClassName>Hilfe.Zaehler</ClassName><InstanceName>Zaehler</InstanceName></Class></Classes>") in x
    assert x.index("<ConsumeContainerWhitespace>") < x.index("<CodeModules>") < x.index("<rd:ReportUnitType>")


def test_report_fliessend_hat_keine_seitenrechtecke():
    x = c.report("<Textbox Name=\"T\"/>", DS, fliessend=True, fliess_h=4.7)
    wohlgeformt(x)
    assert '<Body><ReportItems><Textbox Name="T"/></ReportItems><Height>4.7cm</Height>' in x
    assert "<Rectangle" not in x and "<PageBreak>" not in x
    zwei = c.report(["<a/>", "<b/>"], DS, fliessend=True)                                  # Liste von Teilen wird zusammengesetzt
    assert "<ReportItems><a/><b/></ReportItems>" in zwei and "<Rectangle" not in zwei


def test_report_kopf_und_fuss_schalter():
    x = c.report(["<i/>"], DS, footer_xml="<f/>", footer_first=False, footer_last=False, header_xml="<h/>", header_h=1.0,
                 header_first=False)
    assert ("<PageHeader><Height>1.0cm</Height><PrintOnFirstPage>false</PrintOnFirstPage><PrintOnLastPage>true</PrintOnLastPage>"
            "<ReportItems><h/></ReportItems><Style/></PageHeader>") in x
    assert ("<PageFooter><Height>1.2cm</Height><PrintOnFirstPage>false</PrintOnFirstPage><PrintOnLastPage>false</PrintOnLastPage>"
            "<ReportItems><f/></ReportItems><Style/></PageFooter>") in x
    assert x.index("<PageHeader>") < x.index("<PageFooter>")


def test_report_ohne_standardparameter_und_breite():
    ziel = c.report("<a/>", DS, fliessend=True, standardparameter=False, body_breite=17.8,
                    extra_params=c.parameter("Marke", "String", "x", "Marke"))
    assert "Project_Name" not in ziel and 'ReportParameter Name="Marke"' in ziel
    assert "<Width>17.8cm</Width>" in ziel
    assert "<ReportParameters>" not in c.report("<a/>", DS, fliessend=True, standardparameter=False)


def test_rect_umbruch_seitenname_bookmark_label():
    x = c.rect("R", 0, 0, 1, 1, umbruch="Start", seitenname="Blatt", bookmark="Anfang", label="Deckblatt")
    wohlgeformt(x)
    assert "<PageBreak><BreakLocation>Start</BreakLocation></PageBreak>" in x
    assert "<DocumentMapLabel>Deckblatt</DocumentMapLabel><Bookmark>Anfang</Bookmark><PageName>Blatt</PageName>" in x
    assert "<BreakLocation>End</BreakLocation>" in c.rect("R", 0, 0, 1, 1, umbruch="End")
    assert "<BreakLocation>End</BreakLocation>" in c.rect("R", 0, 0, 1, 1, page_break=True)       # alt bleibt


def test_marke_haengt_an_beliebiges_element():
    t = c.marke(c.text("T", 0, 0, 1, 1, "x"), bookmark="B1", label="Eintrag")
    wohlgeformt(t)
    assert t.endswith("<Bookmark>B1</Bookmark><DocumentMapLabel>Eintrag</DocumentMapLabel></Textbox>")
    tab = c.marke(c.tablix("T", 0, 0, [2], [("kopf", 0.5, ["<a/>"]), ("daten", 0.5, ["<c/>"])]), label="Liste")
    assert tab.endswith("<DocumentMapLabel>Liste</DocumentMapLabel></Tablix>")


def test_tablix_keep_together_und_gruppenumbruch():
    x = c.tablix("T", 0, 0, [2, 3], ZEILEN, group="=Fields!X.Value", keep_together=True, gruppen_umbruch=True,
                 seitenzaehlung_neu=True, gruppen_seitenname="=Fields!X.Value", gruppen_label="=Fields!X.Value")
    assert "<KeepTogether>true</KeepTogether>" in x
    assert ("</GroupExpressions><PageBreak><BreakLocation>Between</BreakLocation><ResetPageNumber>true</ResetPageNumber></PageBreak>"
            "<PageName>=Fields!X.Value</PageName><DocumentMapLabel>=Fields!X.Value</DocumentMapLabel></Group>") in x
    assert "<KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage>" in x         # feste Vorgabe bleibt
    ohne = c.tablix("T", 0, 0, [2, 3], ZEILEN, group="=Fields!X.Value", gruppen_umbruch=True)
    assert "<PageBreak><BreakLocation>Between</BreakLocation></PageBreak>" in ohne and "ResetPageNumber" not in ohne


def test_aktionen():
    assert c.hyperlink("https://www.allplan.com") == (
        "<ActionInfo><Actions><Action><Hyperlink>https://www.allplan.com</Hyperlink></Action></Actions></ActionInfo>")
    assert "mailto:a@b.de" in c.hyperlink("mailto:a@b.de") and "file:///C:/x.txt" in c.hyperlink("file:///C:/x.txt")
    ausdruck = c.hyperlink('="https://www.allplan.com/?n=" & CountRows()')
    assert "<Hyperlink>=&quot;" not in ausdruck and "&amp;" in ausdruck                            # Ausdruck wird maskiert
    assert "<BookmarkLink>Ziel</BookmarkLink>" in c.bookmark_link("Ziel")
    d = c.drillthrough("Ziel", [("Objektart", "Wand"), ("Nr", "=Fields!Nr.Value")])
    assert ("<Drillthrough><ReportName>Ziel</ReportName><Parameters><Parameter Name=\"Objektart\"><Value>Wand</Value></Parameter>"
            "<Parameter Name=\"Nr\"><Value>=Fields!Nr.Value</Value></Parameter></Parameters></Drillthrough>") in d
    assert "<Parameters>" not in c.drillthrough("Ziel")
    for teil in (c.hyperlink("https://a.de"), ausdruck, d):
        wohlgeformt(teil)


def test_aktion_an_textbox_und_bild():
    t = c.plus(c.text("T", 0, 0, 1, 1, "x"), c.hyperlink("https://a.de"))
    assert "</Paragraphs><ActionInfo>" in t
    assert "<Hyperlink>https://a.de</Hyperlink>" in c.image("I", 0, 0, 1, 1, "v", action=c.hyperlink("https://a.de"))
    assert "<BookmarkLink>Marke</BookmarkLink>" in c.image("I", 0, 0, 1, 1, "v", action="Marke")


def test_subreport():
    x = c.subreport("UB", 3.9, 1.5, 17.8, 4.3, "ziel", [("Marke", '="a" & Parameters!P.Value')], keine_zeilen="leer", rahmen=c.RED)
    wohlgeformt(x)
    assert x.startswith('<Subreport Name="UB"><ReportName>ziel</ReportName><Parameters>')
    assert '<Parameter Name="Marke"><Value>="a" &amp; Parameters!P.Value</Value></Parameter>' in x
    assert "<NoRowsMessage>leer</NoRowsMessage>" in x and "<Top>3.9cm</Top>" in x
    assert "<Style><Border><Color>%s</Color><Style>Solid</Style><Width>1pt</Width></Border></Style></Subreport>" % c.RED in x
    zelle = c.subreport("UB", None, 0, 0, 0, "ziel")
    assert "<Top>" not in zelle and "<Parameters>" not in zelle and zelle.endswith("<Style><Border><Style>None</Style></Border></Style></Subreport>")


def test_render_argumente_neu(monkeypatch):
    monkeypatch.setattr(c, "RENDER", "R.exe")
    monkeypatch.setattr(c.os.path, "isfile", lambda pfad: True)
    a = c.render_argumente("a", "d", "o", parameter={"Material": ["Beton", "Holz"], "Leer": None, "Zahl": 3}, pdf=True,
                           datei_format="xlsx", vollzugriff=True, dpi=80)
    assert a == ["R.exe", "a", "d", "o", "--dpi=80", "--pdf", "--format=xlsx", "--vollzugriff", "Project_Name=Musterprojekt",
                 "Material=Beton|Holz", "Leer=~null", "Zahl=3"]
    b = c.render_argumente("a", "d", "o", parameter=[("Project_Name", "Echt")])
    assert b[-2:] == ["Project_Name=Musterprojekt", "Project_Name=Echt"]                             # der spaetere Wert gilt


def test_fuss_titel_ist_wahlfrei():
    import bausteine as b
    assert "Report Master   ·   " in b.fuss() and b.fuss("Mein Titel").count("Mein Titel   ·   ") == 1
    assert 'Aber ""Zitat""' in b.fuss('Aber "Zitat"')


# ---------------------------------------------------------------- 3. abgelehnte Vorgaben
def test_ausdruck_als_vorgabe_wird_abgelehnt():
    for datentyp, vorgabe in (("String", '="A" & "B"'), ("Integer", "=1+1"), ("DateTime", "=Today()")):
        with pytest.raises(ValueError, match="Allplan wertet Ausdrücke in Parameter-Vorgaben nicht aus – festen Wert setzen"):
            c.parameter("X", datentyp, vorgabe, "x")
    with pytest.raises(ValueError, match="festen Wert setzen"):
        c.parameter("X", "String", ["a", "=b"], "x", multi=True)


def test_dataset_reference_wird_abgelehnt():
    with pytest.raises(ValueError, match="Auswahlliste aus zweiter Abfrage geht in Allplan nicht – Distinct-Prompt nehmen"):
        c.parameter("X", "String", None, "x", dataset_ref=("Zweit", "Wert", "Text"))


def test_liste_als_ausdruck_wird_abgelehnt():
    with pytest.raises(ValueError, match="Auswahllisten"):
        c.parameter("X", "String", "a", "x", werte=[("=Parameters!Y.Value", "dynamisch")])


@pytest.mark.parametrize("datum", ["19.11.2026", "11/19/2026", "2026-1-9", "heute"])
def test_datetime_nur_iso(datum):
    with pytest.raises(ValueError, match="ISO"):
        c.parameter("D", "DateTime", datum, "Datum")


def test_integer_ohne_vorgabe_wird_abgelehnt():
    with pytest.raises(ValueError, match="Integer ohne Vorgabe"):
        c.parameter("I", "Integer", None, "x")
    assert "<Nullable>true</Nullable>" in c.parameter("I", "Integer", None, "x", nullable=True)        # mit nullable geht es


def test_mehrere_vorgaben_nur_mit_multi():
    with pytest.raises(ValueError, match="multi=True"):
        c.parameter("X", "String", ["a", "b"], "x")


@pytest.mark.parametrize("url", ["www.allplan.com", "http://www.allplan.com", "ftp://x", "C:/datei.txt", '="www." & Parameters!P.Value'])
def test_hyperlink_ohne_erlaubtes_schema_wird_abgelehnt(url):
    with pytest.raises(ValueError, match="Hyperlink"):
        c.hyperlink(url)


@pytest.mark.parametrize("ziel", ["Ziel.rdlc", "Sub/Ziel.RDL"])
def test_drillthrough_und_unterbericht_ziel_ohne_endung(ziel):
    with pytest.raises(ValueError, match="ohne Endung"):
        c.drillthrough(ziel)
    with pytest.raises(ValueError, match="ohne Endung"):
        c.subreport("UB", 0, 0, 1, 1, ziel)


def test_rect_umbruch_nur_start_oder_ende():
    with pytest.raises(ValueError, match="Start"):
        c.rect("R", 0, 0, 1, 1, umbruch="Between")


def test_gruppen_umbruch_braucht_gruppe():
    with pytest.raises(ValueError, match="group"):
        c.tablix("T", 0, 0, [2], [("kopf", 0.5, ["<a/>"]), ("daten", 0.5, ["<c/>"])], gruppen_umbruch=True)
    with pytest.raises(ValueError, match="gruppen_umbruch"):
        c.tablix("T", 0, 0, [2], ZEILEN[:2], group="=Fields!X.Value", seitenzaehlung_neu=True)


# ---------------------------------------------------------------- 4. Runde 2: Umbruch mit Zaehler, Filter, Sortierung, ColSpan, verschachtelte Gruppen
def test_rect_seitenzaehlung_neu_start_und_end():
    for ort in ("Start", "End"):
        x = c.rect("R", 0, 0, 1, 1, "<i/>", umbruch=ort, seitenzaehlung_neu=True)
        assert "<PageBreak><BreakLocation>%s</BreakLocation><ResetPageNumber>true</ResetPageNumber></PageBreak>" % ort in x
    assert "<ResetPageNumber>" in c.rect("R", 0, 0, 1, 1, page_break=True, seitenzaehlung_neu=True)
    with pytest.raises(ValueError, match="Seitenumbruch"):
        c.rect("R", 0, 0, 1, 1, seitenzaehlung_neu=True)


def test_filter_bausteine():
    assert c.filter_in("Fields!M.Value", "Mat") == (
        "<Filter><FilterExpression>=Fields!M.Value</FilterExpression><Operator>In</Operator><FilterValues>"
        "<FilterValue>=Parameters!Mat.Value</FilterValue></FilterValues></Filter>")
    assert "<Operator>TopN</Operator><FilterValues><FilterValue>=5</FilterValue>" in c.filter_topn("Sum(x)", 5)
    assert "<Operator>BottomN</Operator>" in c.filter_topn("Sum(x)", "CInt(Parameters!N.Value)", unten=True)
    assert "<FilterValue>=CInt(Parameters!N.Value)</FilterValue>" in c.filter_topn("Sum(x)", "CInt(Parameters!N.Value)")
    assert "IIf(a &lt; b" in c.filter_j("a < b")
    liste = c.filter_liste(c.filter_j("x"), c.filter_in("y", "P"))
    assert liste.startswith("<Filters><Filter>") and liste.count("<Filter>") == 2 and liste.endswith("</Filter></Filters>")


def test_tablix_filter_xml_und_gruppenfilter_und_sortierung():
    f = c.filter_liste(c.filter_in("Fields!M.Value", "Mat"), c.filter_j("x > 1"))
    x = c.tablix("T", 0, 0, [2], ZEILEN[:2], group="=Fields!X.Value", filter_xml=f,
                 gruppen_filter=c.filter_liste(c.filter_topn("Sum(1)", 3)), sort=[("=Sum(1)", True), ("=Fields!X.Value", False)])
    wohlgeformt(x)
    assert x.count("<Filters>") == 2                                                    # einer an der Gruppe, einer an der Tabelle
    assert x.index("</GroupExpressions><Filters>") < x.index("<DataSetName>") < x.index(f)
    assert ("<SortExpressions><SortExpression><Value>=Sum(1)</Value><Direction>Descending</Direction></SortExpression>"
            "<SortExpression><Value>=Fields!X.Value</Value></SortExpression></SortExpressions>") in x
    detail = c.tablix("T", 0, 0, [2], ZEILEN[:2], sort=[("=Fields!A.Value", False), ("=Fields!B.Value", True)])
    assert detail.count("<SortExpression>") == 2 and '<Group Name="T_D"/><SortExpressions>' in detail


def test_tablix_gruppenband_start_und_end():
    for ort in ("Start", "End", "StartAndEnd", "Between"):
        x = c.tablix("T", 0, 0, [2], ZEILEN[:2], group="=Fields!X.Value", gruppen_umbruch=ort, seitenzaehlung_neu=True)
        assert "<PageBreak><BreakLocation>%s</BreakLocation><ResetPageNumber>true</ResetPageNumber></PageBreak>" % ort in x
    with pytest.raises(ValueError, match="Seitenumbruch je Gruppe"):
        c.tablix("T", 0, 0, [2], ZEILEN[:2], group="=Fields!X.Value", gruppen_umbruch="Mitten")


def test_tablix_filter_expr_und_filter_xml_schliessen_sich_aus():
    with pytest.raises(ValueError, match="filter_liste"):
        c.tablix("T", 0, 0, [2], ZEILEN[:2], filter_expr="x", filter_xml=c.filter_liste(c.filter_j("y")))
    with pytest.raises(ValueError, match="group"):
        c.tablix("T", 0, 0, [2], ZEILEN[:2], gruppen_filter=c.filter_liste(c.filter_topn("x", 3)))


def test_colspan_in_tablix_zeile_und_zelle():
    x = c.tablix("T", 0, 0, [2, 3, 4], [("kopf", 0.5, ["<a/>", "<b/>", "<c/>"]), ("daten", 0.5, [("<hinweis/>", 3)])])
    assert "<TablixCell><CellContents><hinweis/><ColSpan>3</ColSpan></CellContents></TablixCell><TablixCell/><TablixCell/>" in x
    assert c.zelle("<x/>") == "<TablixCell><CellContents><x/></CellContents></TablixCell>"
    assert c.zelle("<x/>", 2) == "<TablixCell><CellContents><x/><ColSpan>2</ColSpan></CellContents></TablixCell><TablixCell/>"
    wohlgeformt(x)


def test_tablix_gruppen_verschachtelt():
    innen = c.kopf_mitglied() + c.gruppe_mitglied("T_Pos", "=Fields!Nr.Value", [("=Sum(1)", True)]) + c.fuss_mitglied()
    aussen = c.gruppe_mitglied("T_Art", "=Fields!Objekt.Value", [("=Fields!Objekt.Value", False)], kinder=innen, umbruch=True,
                               seitenzaehlung_neu=True, seitenname="=Fields!Objekt.Value", label="=Fields!Objekt.Value",
                               gruppen_filter=c.filter_liste(c.filter_topn("Sum(1)", 4)))
    zeilen = [c.zeile(0.6, [c.zelle("<titel/>", 2)]), c.zeile(0.5, [c.zelle("<a/>"), c.zelle("<b/>")]), c.zeile(0.5, [c.zelle("<s/>", 2)])]
    x = c.tablix_gruppen("T", 1, 2, [3, 4], zeilen, [aussen, c.fuss_mitglied("=x")], 1.6, filter_xml=c.filter_liste(c.filter_j("y")),
                         keine_zeilen='Keine "Bauteile".', keep_together=True)
    wohlgeformt(x)
    assert '<TablixMember><Group Name="T_Art"><GroupExpressions><GroupExpression>=Fields!Objekt.Value</GroupExpression></GroupExpressions>' in x
    assert x.index("<TablixMembers><TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>") < x.index('Group Name="T_Pos"')
    assert ("<PageBreak><BreakLocation>Between</BreakLocation><ResetPageNumber>true</ResetPageNumber></PageBreak>"
            "<PageName>=Fields!Objekt.Value</PageName><DocumentMapLabel>=Fields!Objekt.Value</DocumentMapLabel></Group>") in x
    assert '<NoRowsMessage>="Keine ""Bauteile""."</NoRowsMessage><DataSetName>AllplanReport</DataSetName>' in x
    assert "<Height>1.6cm</Height><Width>7cm</Width>" in x and x.count("<TablixRow>") == 3
    assert x.count("<KeepTogether>true</KeepTogether>") == 1 and "<Visibility><Hidden>=x</Hidden></Visibility>" in x


# ---------------------------------------------------------------- 4. Float-Parameter im Anzeigeprogramm (nur mit gebautem Programm)
def parameterwerte(tmp_path, *werte):
    """Rendert einen kleinen Report mit Float-, Float-Mehrfach-, Ganzzahl- und Textparameter und liest die Werte per --info zurueck."""
    rdlc = tmp_path / "Mini.rdlc"
    params = (c.parameter("Zahl", "Float", "0.9", "Zahl") + c.parameter("Zahlen", "Float", ["0.1", "0.2"], "Zahlen", multi=True) +
              c.parameter("Ganz", "Integer", "1", "Ganz") + c.parameter("Wort", "String", "x", "Wort"))
    c.save(str(rdlc), c.report([""], [c.dataset("AllplanReport", "SELECT 1", [("A", "String")])], extra_params=params))
    daten = tmp_path / "d.json"
    daten.write_text('{"types": {"A": "String"}, "rows": [{"A": "x"}]}', encoding="utf-8")
    ausgabe = subprocess.run([c.RENDER, str(rdlc), str(daten), str(tmp_path / "aus"), "--info"] + list(werte), capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=120).stdout
    return {m.group(1): m.group(2) for m in re.finditer(r"PARAM (\w+) .* vals=\[([^\]]*)\]", ausgabe)}, ausgabe


@pytest.mark.skipif(not os.path.isfile(c.RENDER), reason="Anzeigeprogramm nicht gebaut (werkzeug/render/build.ps1)")
def test_float_parameter_punkt_und_komma_gleich(tmp_path):
    zahl = lambda text: float(text.replace(",", "."))  # noqa: E731 - der Renderer zeigt den Wert im Dezimalformat des Rechners
    punkt, _ = parameterwerte(tmp_path, "Zahl=0.95", "Zahlen=0.1|1,2", "Ganz=3", "Wort=a.b,c")
    komma, aus = parameterwerte(tmp_path, "Zahl=0,95", "Zahlen=0,1|1.2", "Ganz=3", "Wort=a.b,c")
    assert zahl(punkt["Zahl"]) == zahl(komma["Zahl"]) == 0.95
    assert [zahl(t) for t in punkt["Zahlen"].split(";")] == [zahl(t) for t in komma["Zahlen"].split(";")] == [0.1, 1.2]
    assert punkt["Ganz"] == komma["Ganz"] == "3" and punkt["Wort"] == komma["Wort"] == "a.b,c"
    mehrdeutig, aus = parameterwerte(tmp_path, "Zahl=1.234,5")
    assert "WARNUNG: Der Wert '1.234,5' von Parameter 'Zahl' hat mehrere Trennzeichen" in aus
