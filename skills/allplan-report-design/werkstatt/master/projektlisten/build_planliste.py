# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Planliste" (RDL 2016) nach out/Report_Master_Planliste.rdlc.

Eine Abfrage auf die Projekttabelle LAYOUT (Plaene) mit LAYOUT_DRAWINGS (Teilbilder je Plan) als Untertabelle. Der
Report hat keine Bauteildaten und keine Bilder; er zeigt, was an den Plaenen des Projekts fehlt und wie die Planliste aussieht.

    python build_planliste.py              schreibt out/Report_Master_Planliste.rdlc
    python build_planliste.py --render     rendert zusaetzlich kopflos nach projektlisten/aus/png_planliste (daten/planliste.json)
    python build_planliste.py --render --daten=planliste_gross    anderer Datensatz (daten/<name>.json, aus/png_<name>):
                                                                  180 Plaene, 12 Monate, 5 Ersteller, viele Luecken
    python build_planliste.py --render --daten=planliste_klein    drei Plaene

Datenform (gemessen in Allplan 2027 am 2026-11-19, labor/projektlisten/wissen.md): eine Zeile je Plan UND Teilbild, die
Plan-Spalten stehen auf jeder dieser Zeilen; ein Plan ohne Teilbild ist EINE Zeile mit leerem Teilbild. Teilbildnamen
kommen mit Leerzeichen aufgefuellt (Trim). Blattgroesse @758@/@222@ in Millimetern (Katalog sagt "m", gemessen 1189 / 841).

Seiten: 1 Ueberblick (Kacheln, Plaene je Monat, Plankopf-Vollstaendigkeit, Hinweisliste "was fehlt"), ab 2 die vollstaendige
Planliste mit den Teilbildern je Plan - ohne Deckel, als letztes Element des Reports, Tabellenkopf wiederholt sich.
Bausteine (angemeldet mit @b.baustein): K090 Kennzahl-Kacheln, D200 Saeulen Plaene je Monat, M090 Vollstaendigkeit
des Plankopfs, T130 Hinweisliste, T140 Planliste mit Teilbildern. Elementnamen beginnen mit "PL_". Kein Klick ins Modell
(Plaene sind keine Modellelemente).
Leere Felder zeigt der Report als "keine Angabe" (Planname) bzw. "–" (alle schmalen Spalten der Liste); Datumsfelder liest er mit Code.D (leer, Nothing und
Jahr <= 1900 zaehlen als nicht gesetzt).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MASTER)

import bausteine as b  # noqa: E402
import core as c  # noqa: E402
import viz as v  # noqa: E402

OUT_DIR = os.path.normpath(os.path.join(MASTER, "..", "out"))
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "planliste")
JSON = os.environ.get("PLANLISTE_JSON", os.path.join(HERE, "daten", DATEN + ".json"))
AUS = os.environ.get("PLANLISTE_AUS", os.path.join(HERE, "aus", "png_" + DATEN))

MAX_MONATE = 12        # Saeulen im Diagramm (die juengsten Monate mit Plaenen)
MAX_HINWEISE = 10      # Zeilen der Hinweisliste

# ---------------------------------------------------------------- Daten
# Beide Tabellen in EINEM DataSet (zwei SELECT, wie Allplans Planliste mit Dokumenten). Jede Spalte ist in Allplan 2027 gemessen
# (labor/projektlisten/wissen.md, Abschnitt "Gemessen in Allplan 2026-11-19"); @389@ (Planindex) kam leer zurueck.
QUERY = """SELECT
       @446@[Name=Plannummer],
       @445@[Name=Planname],
       @389@[Name=Planindex],
       @432@[Name=Erstellt],
       @433@[Name=Geaendert],
       @481@[Name=Ersteller],
       @395@[Name=Pruefer],
       @443@[Name=Freigabe],
       @375@[Name=Planformat],
       @758@[Name=Breite],
       @222@[Name=Hoehe]
FROM [LAYOUT]
SELECT
       @512@[Name=Teilbildnummer],
       @425@[Name=Teilbildname]
FROM [LAYOUT_DRAWINGS]
"""
FIELDS = [("Plannummer", "Int32"), ("Planname", "String"), ("Planindex", "String"), ("Erstellt", "DateTime"),
          ("Geaendert", "DateTime"), ("Ersteller", "String"), ("Pruefer", "String"), ("Freigabe", "DateTime"),
          ("Planformat", "String"), ("Breite", "Double"), ("Hoehe", "Double"), ("Teilbildnummer", "Int32"),
          ("Teilbildname", "String")]
ALLE = "AllplanReport"

CODE_PLANLISTE = """
' ---- Planliste: leere Felder, Datum, Blattgroesse, Luecken (Allplan liefert leere Felder als Nothing oder Leerzeichen)
Public Function Leer(ByVal x As Object) As Boolean
    If x Is Nothing Then Return True
    If IsDBNull(x) Then Return True
    Return x.ToString().Trim() = ""
End Function

Public Function DatumDa(ByVal d As Object) As Boolean
    If d Is Nothing Then Return False
    If IsDBNull(d) Then Return False
    Try
        Return CDate(d).Year > 1900
    Catch
        Return False
    End Try
End Function

Public Function D(ByVal x As Object) As Date
    If DatumDa(x) Then Return CDate(x)
    Return DateSerial(1900, 1, 1)
End Function

Public Function DatumText(ByVal x As Object, ByVal leer As String) As String
    If Not DatumDa(x) Then Return leer
    Return CDate(x).ToString("dd.MM.yyyy")
End Function

Public Function MonKey(ByVal x As Object) As Integer
    If Not DatumDa(x) Then Return 0
    Return CDate(x).Year * 100 + CDate(x).Month
End Function

Public Function MonText(ByVal k As Object) As String
    Dim n As Integer = CInt(Val(k))
    Return (n Mod 100).ToString("00") & "." & (n \\ 100).ToString()
End Function

Public Function Papier(ByVal b As Object, ByVal h As Object, ByVal fmt As Object) As String
    If Not Leer(fmt) Then Return fmt.ToString().Trim()
    Dim x As Double = Val(b)
    Dim y As Double = Val(h)
    If x <= 0 OrElse y <= 0 Then Return "–"
    Dim l As Double = Math.Max(x, y)
    Dim k As Double = Math.Min(x, y)
    Dim ll() As Double = {1189, 841, 594, 420, 297}
    Dim kk() As Double = {841, 594, 420, 297, 210}
    For i As Integer = 0 To 4
        If Math.Abs(l - ll(i)) <= 3 AndAlso Math.Abs(k - kk(i)) <= 3 Then Return "A" & i.ToString()
    Next
    Return Math.Round(l / 10).ToString() & "×" & Math.Round(k / 10).ToString()
End Function

Public Function FehltAnz(ByVal name As Object, ByVal ersteller As Object, ByVal pruefer As Object, ByVal freigabe As Object, ByVal tb As Object) As Integer
    Dim n As Integer = 0
    If Leer(name) Then n += 1
    If Leer(ersteller) Then n += 1
    If Leer(pruefer) Then n += 1
    If Not DatumDa(freigabe) Then n += 1
    If Val(tb) <= 0 Then n += 1
    Return n
End Function

Public Function FehltText(ByVal name As Object, ByVal ersteller As Object, ByVal pruefer As Object, ByVal freigabe As Object, ByVal tb As Object) As String
    Dim s As String = ""
    If Leer(name) Then s = s & "Name, "
    If Leer(ersteller) Then s = s & "Ersteller, "
    If Leer(pruefer) Then s = s & "Prüfer, "
    If Not DatumDa(freigabe) Then s = s & "Freigabe, "
    If Val(tb) <= 0 Then s = s & "Teilbild, "
    If s.Length > 2 Then s = s.Substring(0, s.Length - 2)
    Return s
End Function
"""

# ---------------------------------------------------------------- Ausdruecke
PLAN = "Fields!Plannummer.Value"
PLAENE = "CountDistinct(%s)" % PLAN
TB_DA = "Val(Fields!Teilbildnummer.Value) > 0"
NAME_DA = "Not Code.Leer(Fields!Planname.Value)"
ERSTELLER_DA = "Not Code.Leer(Fields!Ersteller.Value)"
PRUEFER_DA = "Not Code.Leer(Fields!Pruefer.Value)"
FREIGABE_DA = "Code.DatumDa(Fields!Freigabe.Value)"
FA = ("Code.FehltAnz(Fields!Planname.Value, Fields!Ersteller.Value, Fields!Pruefer.Value, Fields!Freigabe.Value, "
      "Fields!Teilbildnummer.Value)")
FT = ("Code.FehltText(Fields!Planname.Value, Fields!Ersteller.Value, Fields!Pruefer.Value, Fields!Freigabe.Value, "
      "Fields!Teilbildnummer.Value)")
FEHLT_PLAENE = "CountDistinct(IIf(%s > 0, %s, Nothing))" % (FA, PLAN)
KEINE = "keine Angabe"

HEAD = c.edge(["Bottom"], c.INK, "1pt")
ROW = c.edge(["Top"], c.HAIR, "0.75pt")
FEST = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"


def mit(bedingung):
    """Anzahl Plaene, fuer die die Bedingung (zeilenweise) zutrifft."""
    return "CountDistinct(IIf(%s, %s, Nothing))" % (bedingung, PLAN)


def kurz(x, n):
    """Text auf n Zeichen kuerzen, Auslassung als Punkte (Zellen wachsen nicht, abgeschnitten wirkt kaputt)."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (x, n, x, n - 1, x)


def kopfzelle(name, label, align=None):
    return c.cell(name, c.run(label, 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=HEAD, pad=(3, 2, 3, 4))


def tc(inner, extra=""):
    return "<TablixCell><CellContents>%s%s</CellContents></TablixCell>" % (inner, extra)


def wert(name, ausdruck, leer_bed, leer_text, align=None, size=8, fett=False, rand=ROW, pad=(3, 0, 3, 0)):
    """Tabellenzelle: Wert oder - wenn leer_bed zutrifft - der Leertext in blasser Farbe."""
    run = c.run('=IIf(%s, "%s", %s)' % (leer_bed, leer_text, ausdruck), size,
                '=IIf(%s, "%s", "%s")' % (leer_bed, c.FAINT, c.INK if fett else c.TEXT), c.F_SEMI if fett else c.F)
    return c.cell(name, run, align, "Middle", border_xml=rand, pad=pad)


def gruppe_filter(chart_xml, filter_xml):
    return chart_xml.replace("</GroupExpressions></Group>", "</GroupExpressions>" + filter_xml + "</Group>", 1)


def kategorie_label(chart_xml, alt, neu):
    return chart_xml.replace("<Label>%s</Label>" % c.esc(alt), "<Label>%s</Label>" % c.esc(neu), 1)


# ---------------------------------------------------------------- Kopfband Seite 1
def band():
    x0 = c.INSET
    letzte = "Code.DatumText(Max(Code.D(Fields!Geaendert.Value)), \"–\")"
    inner = (c.rect("PL_BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.AKZENT)
             + c.text("PL_BandOver", 1.4, x0, 10.5, 0.4, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.AKZENT_DUNKEL, c.F_SEMI))
             + c.text("PL_BandTitel", 1.85, x0, 10.5, 1.45, c.run("Planliste", 30, c.WHITE, c.F))
             + c.text("PL_BandSub", 3.3, x0, 10.5, 0.55,
                      c.run('=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, c.AUF_NAVY, c.F))
             + c.text("PL_BandRechts", 1.4, x0 + 11, 7, 0.4, c.run("Zuletzt geändert", 8, c.AUF_NAVY, c.F_SEMI), align="Right")
             + c.text("PL_BandRechts2", 1.85, x0 + 11, 7, 1.45, c.para([c.run("=" + letzte, 24, c.WHITE, c.F_ZAHL)], "Right"))
             + c.text("PL_BandRechts3", 3.3, x0 + 11, 7, 0.55, c.run("letzte Änderung an einem Plan", 9, c.AUF_NAVY, c.F), align="Right"))
    return c.rect("PL_Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


# ---------------------------------------------------------------- K090 Kacheln
@b.baustein("K090", "Kennzahl-Kacheln Planliste")
def k090(top, left, w):
    """Vier Kacheln: Plaene, Teilbilder auf Plaenen, Plaene ohne Namen, Plaene ohne Teilbild."""
    gap = 0.3
    kw = (w - 3 * gap) / 4
    teilbilder = "CountDistinct(IIf(%s, Fields!Teilbildnummer.Value, Nothing))" % TB_DA
    kacheln = [
        ("PL_K1", PLAENE, "Pläne", "im Projekt"),
        ("PL_K2", teilbilder, "Teilbilder auf Plänen", "jedes nur einmal gezählt"),
        ("PL_K3", "%s - %s" % (PLAENE, mit(NAME_DA)), "Pläne ohne Namen", "Planname leer"),
        ("PL_K4", "%s - %s" % (PLAENE, mit(TB_DA)), "Pläne ohne Teilbild", "noch nichts auf dem Plan"),
    ]
    items = ""
    for i, (name, ausdruck, label, note) in enumerate(kacheln):
        items += b.kpi(name, top, left + i * (kw + gap), kw, ausdruck, "#,##0", "", label, note)
    items += b.etikett("PL_E1", top + 2.65, left, w, "K090", "Vier Kacheln: Zähler als CountDistinct über die Plannummer, "
                                                            "Plan-Spalten stehen auf jeder Teilbild-Zeile")
    return items


# ---------------------------------------------------------------- D200 Saeulen je Monat
# Ein Diagramm hat feste Breite; bei einem Monat wuerde die Saeule 9 cm breit. Darum vier Varianten, von denen je nach Zahl
# der Monate genau eine sichtbar ist (die anderen sind ausgeblendet und fallen weg), mittig im Feld: 1, 2-3, 4-6, 7-12 Monate.
MONATE = "CountDistinct(IIf(Code.MonKey(Fields!Erstellt.Value) > 0, Code.MonKey(Fields!Erstellt.Value), Nothing), \"%s\")" % ALLE
MONATE_N = "IIf(%s > %d, %d, %s)" % (MONATE, MAX_MONATE, MAX_MONATE, MONATE)
D200_BREITEN = [(4.0, "%s > 1" % MONATE_N), (7.0, "(%s < 2) Or (%s > 3)" % (MONATE_N, MONATE_N)),
                (11.0, "(%s < 4) Or (%s > 6)" % (MONATE_N, MONATE_N)), (c.CONTENT_W, "%s < 7" % MONATE_N)]   # (Breite, versteckt wenn)


def d200_diagramm(name, top, left, w, h):
    key = "Code.MonKey(Fields!Erstellt.Value)"
    zahl = "CountDistinct(%s)" % PLAN
    neuester = '=IIf(Max(%s) = Max(Max(%s, "%s_Cat1"), "%s"), "%s", "%s")' % (key, key, name, name, c.BLUE, c.RAMP[3])
    chart = v.chart(
        name, top, left, w, h,
        [v.S("Plaene", {"Y": "=" + zahl}, typ="Column", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc(neuester),
             label=v.dlabel(fmt="#,##0", size="8.5pt", color=c.TEXT),
             custom_xml=v.custom(PointWidth="0.55", BarLabelStyle="Outside"))],
        [("=" + key, None, None)],
        areas=v.area(cat_axes=[v.axis("Primary", interval="1", size="7.5pt", extra=FEST)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0",
                                      maximum='=Max(CountDistinct(%s, "%s_Cat1"), "%s") * 1.25' % (PLAN, name, name))],
                     pos=(0, 0, 100, 100)),
        nodata="Keine Pläne mit Erstellungsdatum",
        extra=c.filters("%s > 0" % key))
    chart = gruppe_filter(chart, c.topn("Max(%s)" % key, MAX_MONATE))
    return kategorie_label(chart, "=" + key, "=Code.MonText(Max(%s))" % key)


@b.baustein("D200", "Säulen Pläne je Monat")
def d200(top, left, w, h=5.5):
    items = b.overline("PL_A2", top, left, w, "Zeitverlauf", "Pläne je Monat der Erstellung")
    for i, (breite, versteckt) in enumerate(D200_BREITEN):
        name = "PL_D200_%d" % (i + 1)
        # jede Variante in einem Behaelter ueber die VOLLE Breite (gemessen im Report-Fenster: ein ausgeblendetes Feld, dessen
        # Kanten nicht auf denen der Nachbarn liegen, verschiebt sichtbare Elemente desselben Behaelters)
        items += c.rect(name + "_Feld", top + 1.45, left, w, h,
                        d200_diagramm(name, 0, (w - breite) / 2, breite, h), hidden="=" + versteckt)
    items += b.etikett("PL_E2", top + 1.45 + h + 0.05, left, w, "D200",
                       "Säulen: Pläne je Erstellungsmonat, Deckel 12 (die jüngsten), Breite nach Zahl der Monate (4 Varianten), neuester Monat in Leitfarbe, übrige heller")
    return items


# ---------------------------------------------------------------- M090 Vollstaendigkeit
@b.baustein("M090", "Vollständigkeit des Plankopfs")
def m090(top, left, w):
    items = b.overline("PL_A3", top, left, w, "Plankopf", "Was ist ausgefüllt?")
    zeilen = [("Pläne mit Namen", "Planname gesetzt", NAME_DA),
              ("Pläne mit Ersteller", "Plan-Ersteller gesetzt", ERSTELLER_DA),
              ("Pläne mit Prüfer", "Planprüfer gesetzt", PRUEFER_DA),
              ("Pläne mit Freigabe", "Freigabedatum gesetzt", FREIGABE_DA),
              ("Pläne mit Teilbild", "mindestens ein Teilbild auf dem Plan", TB_DA)]
    y = top + 1.45
    for i, (label, note, bed) in enumerate(zeilen):
        items += b.kennwert("PL_M%d" % (i + 1), y, left, w, label, note, b.quote(mit(bed), PLAENE))
        y += 1.3
    items += b.etikett("PL_E3", y + 0.05, left, w, "M090",
                       "Kennwert-Balken: Anteil der Pläne mit gesetztem Feld")
    return items


# ---------------------------------------------------------------- T130 Hinweisliste
HW_KOPF, HW_ZEILE, HW_REST = 0.55, 0.55, 0.5
HW_HOEHE = HW_KOPF + MAX_HINWEISE * HW_ZEILE + HW_REST


@b.baustein("T130", "Hinweisliste: was fehlt")
def t130(top, left, w):
    items = b.overline("PL_A4", top, left, w, "Hinweise", "Was an den Plänen fehlt")
    cols = [0.9, 2.5, w - 3.4]
    rang = "Max(%s) * 10000000.0 + (9999999 - Min(%s))" % (FA, PLAN)
    rest = "(%s - %d)" % (FEHLT_PLAENE, MAX_HINWEISE)
    kopf = [kopfzelle("PL_T1_H1", "NR"), kopfzelle("PL_T1_H2", "PLAN"), kopfzelle("PL_T1_H3", "FEHLT")]
    daten = [
        c.cell("PL_T1_D1", c.run("=First(%s)" % PLAN, 8, c.INK, c.F_SEMI), border_xml=ROW, pad=(3, 0, 3, 0)),
        wert("PL_T1_D2", kurz("Trim(First(Fields!Planname.Value))", 14), "Code.Leer(First(Fields!Planname.Value))", KEINE),
        c.cell("PL_T1_D3", c.run("=First(%s)" % FT, 7, c.TEXT), border_xml=ROW, pad=(3, 0, 3, 0)),
    ]
    zu = [c.cell("PL_T1_R1", c.run('="… und " & %s & " weitere Pläne mit Lücken"' % rest, 7.5, c.MUTED), pad=(3, 0, 3, 0)),
          "@@LEER@@", "@@LEER@@"]
    xml = c.tablix("PL_T1", 0, 0, cols, [("kopf", HW_KOPF, kopf), ("daten", HW_ZEILE, daten), ("fuss", HW_REST, zu)],
                   dataset=ALLE, group="=" + PLAN, sort="=" + rang, sort_desc=True)
    filter_xml = ("<Filters><Filter><FilterExpression>=%s</FilterExpression><Operator>TopN</Operator><FilterValues>"
                  "<FilterValue>=%d</FilterValue></FilterValues></Filter><Filter><FilterExpression>=Max(%s)</FilterExpression>"
                  '<Operator>GreaterThan</Operator><FilterValues><FilterValue DataType="Integer">0</FilterValue></FilterValues>'
                  "</Filter></Filters>") % (c.esc(rang), MAX_HINWEISE, c.esc(FA))
    xml = xml.replace("</GroupExpressions></Group>", "</GroupExpressions>" + filter_xml + "</Group>", 1)
    # Hinweiszeile ueber alle drei Spalten (ColSpan): erste Zelle verbreitern, die beiden Folgezellen leeren
    xml = xml.replace("<TablixCell><CellContents>@@LEER@@</CellContents></TablixCell>", "<TablixCell/>")
    xml = re.sub(r'(<Textbox Name="PL_T1_R1">.*?</Textbox>)</CellContents>', r"\1<ColSpan>3</ColSpan></CellContents>", xml, count=1, flags=re.S)
    xml = xml.replace("<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>",
                      "<TablixMember><KeepWithGroup>Before</KeepWithGroup><Visibility><Hidden>%s</Hidden></Visibility></TablixMember>"
                      % c.esc("=%s <= 0" % rest), 1)
    items += c.rect("PL_T1_Feld", top + 1.45, left, w, HW_HOEHE + 0.05, xml)
    items += b.etikett("PL_E4", top + 1.45 + HW_HOEHE + 0.1, left, w, "T130",
                       "Gruppe je Plan, Deckel 10 (meiste Lücken zuerst)")
    return items


# ---------------------------------------------------------------- T140 Planliste mit Teilbildern
# Allplan zeichnet Text rund 10-15 % breiter als die kopflose Vorschau (gemessen 2026-11-19): jede Spalte hat Reserve,
# lange Werte werden mit kurz() gekuerzt, leere Felder der schmalen Spalten sind ein "–" (ein Zeichen kann nicht umbrechen).
SPALTEN = [0.9, 4.2, 1.1, 1.9, 1.9, 1.5, 1.8, 1.8, 1.9, 1.0]    # Summe 18,0
ZEILE_PLAN, ZEILE_TB, ZEILE_KOPF = 0.55, 0.45, 0.65
assert abs(sum(SPALTEN) - c.CONTENT_W) < 1e-9


def planliste_tablix(top, left):
    f = lambda feld: "First(Fields!%s.Value)" % feld        # Wert eines Plans im Gruppenbereich
    kopf = [kopfzelle("PL_T2_H1", "NR"), kopfzelle("PL_T2_H2", "PLAN"), kopfzelle("PL_T2_H3", "INDEX"),
            kopfzelle("PL_T2_H4", "ERSTELLT"), kopfzelle("PL_T2_H5", "GEÄNDERT"), kopfzelle("PL_T2_H6", "FORMAT"),
            kopfzelle("PL_T2_H7", "ERSTELLER"), kopfzelle("PL_T2_H8", "PRÜFER"), kopfzelle("PL_T2_H9", "FREIGABE"),
            kopfzelle("PL_T2_H10", "TB", "Right")]
    tb_zahl = "CountDistinct(IIf(%s, Fields!Teilbildnummer.Value, Nothing))" % TB_DA
    datum = lambda name, feld: wert(name, "Code.DatumText(%s, \"–\")" % f(feld), "Not Code.DatumDa(%s)" % f(feld), "–")
    plan = [
        c.cell("PL_T2_P1", c.run("=" + f("Plannummer"), 8, c.INK, c.F_SEMI), border_xml=ROW, pad=(3, 0, 3, 0)),
        wert("PL_T2_P2", kurz("Trim(%s)" % f("Planname"), 26), "Code.Leer(%s)" % f("Planname"), KEINE, fett=True),
        wert("PL_T2_P3", "Trim(%s)" % f("Planindex"), "Code.Leer(%s)" % f("Planindex"), "–"),
        datum("PL_T2_P4", "Erstellt"), datum("PL_T2_P5", "Geaendert"),
        wert("PL_T2_P6", kurz("Code.Papier(%s, %s, %s)" % (f("Breite"), f("Hoehe"), f("Planformat")), 7), "false", "–"),
        wert("PL_T2_P7", kurz("Trim(%s)" % f("Ersteller"), 11), "Code.Leer(%s)" % f("Ersteller"), "–"),
        wert("PL_T2_P8", kurz("Trim(%s)" % f("Pruefer"), 11), "Code.Leer(%s)" % f("Pruefer"), "–"),
        wert("PL_T2_P9", "Code.DatumText(%s, \"\")" % f("Freigabe"), "Not Code.DatumDa(%s)" % f("Freigabe"), "–"),
        wert("PL_T2_P10", tb_zahl, "%s = 0" % tb_zahl, "–", align="Right"),
    ]
    tb_text = ('"TB " & First(Fields!Teilbildnummer.Value) & IIf(Code.Leer(First(Fields!Teilbildname.Value)), "", "   ·   " & %s)'
               % kurz("Trim(First(Fields!Teilbildname.Value))", 100))
    detail = [c.cell("PL_T2_T1", c.run("", 7), pad=(3, 0, 3, 0)),
              c.cell("PL_T2_T2", c.run("=" + tb_text, 7.5, c.MUTED), pad=(3, 0, 3, 0))]
    detail_cells = tc(detail[0]) + tc(detail[1], "<ColSpan>9</ColSpan>") + "<TablixCell/>" * 8

    def zeile(hoehe, zellen):
        return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (c.cm(hoehe), zellen)

    body = ("<TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s%s%s</TablixRows></TablixBody>" % (
        "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(x) for x in SPALTEN),
        zeile(ZEILE_KOPF, "".join(tc(z) for z in kopf)), zeile(ZEILE_PLAN, "".join(tc(z) for z in plan)),
        zeile(ZEILE_TB, detail_cells)))
    spalten_h = "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>" % ("<TablixMember/>" * len(SPALTEN))
    zeilen_h = (
        "<TablixRowHierarchy><TablixMembers>"
        "<TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember>"
        '<TablixMember><Group Name="PL_T2_Plan"><GroupExpressions><GroupExpression>=%s</GroupExpression></GroupExpressions></Group>'
        "<SortExpressions><SortExpression><Value>=%s</Value></SortExpression></SortExpressions><TablixMembers>"
        "<TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>"
        '<TablixMember><Group Name="PL_T2_TB"><GroupExpressions><GroupExpression>=Fields!Teilbildnummer.Value</GroupExpression>'
        "</GroupExpressions></Group><SortExpressions><SortExpression><Value>=Fields!Teilbildnummer.Value</Value></SortExpression>"
        "</SortExpressions><Visibility><Hidden>%s</Hidden></Visibility></TablixMember>"
        "</TablixMembers></TablixMember></TablixMembers></TablixRowHierarchy>") % (
        PLAN, "Min(%s)" % PLAN, c.esc("=Val(First(Fields!Teilbildnummer.Value)) <= 0"))
    return ("<Tablix Name=\"PL_T2\">%s%s%s<DataSetName>%s</DataSetName><Top>%s</Top><Left>%s</Left><Height>%s</Height>"
            "<Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>") % (
        body, spalten_h, zeilen_h, ALLE, c.cm(top), c.cm(left), c.cm(ZEILE_KOPF + ZEILE_PLAN + ZEILE_TB), c.cm(c.CONTENT_W))


@b.baustein("T140", "Planliste mit Teilbildern")
def t140(top, left):
    """Alle Plaene, je Plan eine Zeile und darunter die Teilbilder. Ohne Deckel: gehoert ans Ende des Reports."""
    return planliste_tablix(top, left)


# ---------------------------------------------------------------- Seiten
def seite1():
    x0, w = c.INSET, c.CONTENT_W
    sp = 8.8
    xr = x0 + sp + 0.4
    items = band()
    items += k090(5.05, x0, w)
    items += d200(8.6, x0, w)
    items += m090(16.8, x0, sp)
    items += t130(16.8, xr, sp)
    return items


def kopf_seite2():
    """Kopf der Planliste: Band wie die Folgeseiten des Masters (steht nur auf der ersten Seite der Liste;
    die Tabelle wiederholt ihren eigenen Kopf)."""
    return b.folgekopf("PL_Kopf2", "PL_K2", "REPORT MASTER  ·  PLANLISTE", "Alle Pläne",
                       c.run('=%s & " Pläne  ·  " & CountDistinct(IIf(%s, Fields!Teilbildnummer.Value, Nothing)) & " Teilbilder"'
                             % (PLAENE, TB_DA), 8.5, c.AUF_NAVY), top=c.PAGE_BODY_H, label="Planliste")


def build():
    """Seite 1 ist ein Rechteck mit Seitenumbruch danach; die Planliste folgt als fliessender Teil (core.report(fliessend=True)):
    Kopfband, dann die Tabelle, die mit den Daten ueber beliebig viele Seiten waechst."""
    liste_top = c.PAGE_BODY_H + 2.9
    seite1_rect = c.rect("Seite1", 0, 0, c.PAGE_W, c.PAGE_BODY_H, seite1(), umbruch="End", label="Überblick")
    b.KATALOG.append(("Planliste", "T140", "Tabelle mit Gruppe je Plan und je Teilbild, ohne Deckel, Kopf wiederholt, letztes Element"))
    inhalt = seite1_rect + kopf_seite2() + planliste_tablix(liste_top, c.INSET)
    xml = c.report(inhalt, [c.dataset(ALLE, QUERY, FIELDS)], footer_xml=b.fuss(), code=b.CODE + CODE_PLANLISTE,
                   fliessend=True, fliess_h=liste_top + 1.5)
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Planliste.rdlc")
    c.save(ziel, xml)
    return ziel


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--daten"})
    ziel = build()
    print(ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        c.rendern(ziel, JSON, AUS, vollzugriff=True)   # volle Rechte: Code.Schrift liest die installierten Schriften (sonst Ersatzschrift Segoe UI)
