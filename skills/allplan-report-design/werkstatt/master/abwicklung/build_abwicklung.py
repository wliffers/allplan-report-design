# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Raum-Abwicklung" (RDL 2016) nach out/Report_Master_Abwicklung.rdlc.

Je Raum eine gezeichnete Abwicklung: Das Werkzeug werkzeug/abwicklung_zeichnen.py legt im Teilbild je Raum eine
2D-Zeichnung der abgewickelten Waende (Tueren/Fenster farbig, Masse, Lageskizze) an und darunter eine duenne Decke als
RAHMEN. Der Report holt das Bild als Planausschnitt dieses Rahmens (@205@ mit Image=true, 170 x 90 mm).

    python build_abwicklung.py              schreibt out/Report_Master_Abwicklung.rdlc
    python build_abwicklung.py --render     rendert zusaetzlich kopflos nach abwicklung/aus/png_master_abw (daten/master_abw.json)
    python build_abwicklung.py --render --daten=viel_abw     24 Raeume + 24 Rahmen, lange Namen, Rahmen ohne Raum, Raum ohne Rahmen

Eine Abfrage, ein DataSet, zwei Zeilenarten (beide ObjNr 4 bzw. 61):
  RAHMEN  ObjNr 4 UND Material "Abwicklung". Bez = Bauteil-ID des Raums, Bild = Abwicklungs-Zeichnung.
  RAUM    ObjNr 61. Nr = Bauteil-ID; Name = Bez (wenn gefuellt) sonst Funktion; Seitenflaeche = Wandflaeche NETTO.
Die Raumwerte zum Rahmen holt Lookup(Bez, Nr, <Feld>, "AllplanReport"). Lookup steht nie in Filter- oder
Sortierausdruecken: gefiltert wird nur ueber ObjNr/Material, sortiert ueber Bez.

Bausteine (angemeldet mit @b.baustein): K070 Kennzahl-Kacheln Abwicklung, B100 Abwicklung je Raum. Elementnamen "AW_".

Seitenregel: Blatt 1 = Titelband, Kacheln und Karte 1. Ab Blatt 2 je zwei Karten. Hoechstens 8 Karten (sortiert nach Bez):
Blaetter = 1 + aufrunden((n - 1) / 2) mit n = Zahl der Karten (1 bis 8); ohne Rahmen 1 Blatt. Der Seitenwechsel
kommt aus der Tablix-Gruppe Int(RowNumber / 2) mit PageBreak "Between": Zeile 1 -> Gruppe 0, Zeilen 2+3 -> Gruppe 1 usw.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MASTER)

import bausteine as b  # noqa: E402
import core as c  # noqa: E402

OUT_DIR = os.path.normpath(os.path.join(MASTER, "..", "out"))
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "master_abw")
JSON = os.environ.get("ABWICKLUNG_JSON", os.path.join(HERE, "daten", DATEN + ".json"))
AUS = os.environ.get("ABWICKLUNG_AUS", os.path.join(HERE, "aus", "png_" + DATEN))

MAX_KARTEN = 8         # Deckel fuer die Abwicklungskarten (sortiert nach Bez)
ALLE = "AllplanReport"

# ---------------------------------------------------------------- Daten
# ObjNr 4 = Decke (hier: der Rahmen unter der Zeichnung), ObjNr 61 = Raum. Eine Bildgroesse gilt fuer alle Zeilen.
QUERY = """SELECT
       @10@[Name=Nr],
       [Name=ObjNr|f=@OBJ@],
       @507@[Name=Bez],
       @506@[Name=Funktion],
       @508@[Name=Material],
       @229@[Name=Flaeche],
       @228@[Name=Umfang],
       @222@[Name=Hoehe],
       @295@[Name=Seitenflaeche],
       @205@[Name=Bild|Image=true|Width=170|Height=90|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.4.or.@OBJ@.eq.61]
"""
FIELDS = [("Nr", "String"), ("ObjNr", "String"), ("Bez", "String"), ("Funktion", "String"), ("Material", "String"),
          ("Flaeche", "Double"), ("Umfang", "Double"), ("Hoehe", "Double"), ("Seitenflaeche", "Double"), ("Bild", "Byte[]")]

RAHMEN_ZEILE = '(%s And Fields!Material.Value = "Abwicklung")' % b.ist(4)
ANZ_RAHMEN = "Sum(IIf(%s, 1, 0))" % RAHMEN_ZEILE
ANZ_RAHMEN_DS = 'Sum(IIf(%s, 1, 0), "%s")' % (RAHMEN_ZEILE, ALLE)
# Rang fuer den Deckel: Nicht-Rahmen bekommen eine riesige Zahl (BottomN nimmt die kleinsten) - egal, in welcher Reihenfolge die Filter laufen
RANG = "IIf(%s, Code.Rang(Fields!Bez.Value), 1.0E+18)" % RAHMEN_ZEILE

RAND = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR
ZOOM_RAUM = '="Zoom:" + Fields!Bez.Value + ",Mark:" + Fields!Bez.Value'


def raum(feld):
    """Wert eines Feldes aus der RAUM-Zeile, deren Nr der Bez des Rahmens entspricht (Nothing ohne Raum)."""
    return 'Lookup(Fields!Bez.Value, Fields!Nr.Value, Fields!%s.Value, "%s")' % (feld, ALLE)


NETTO = raum("Seitenflaeche")
UMFANG = raum("Umfang")
HOEHE = raum("Hoehe")
GRUND = raum("Flaeche")
BRUTTO = "Code.Brutto(%s, %s)" % (UMFANG, HOEHE)
OEFFNUNG = "Code.Diff(%s, %s)" % (BRUTTO, NETTO)
NAME = "Code.RName(%s, %s)" % (raum("Bez"), raum("Funktion"))

# Summen der Kacheln: ueber ALLE Raeume (ObjNr 61). Ein Lookup innerhalb einer Summe (Sum(Lookup(...))) liefert im ReportViewer
# nichts - "nur Raeume mit Rahmen" ist per Ausdruck nicht sauber zu summieren, die Kacheln heissen deshalb "alle Raeume".
SUM_NETTO = b.summe("Seitenflaeche", b.ist(61))
SUM_BRUTTO = "Sum(IIf(%s, CDbl(Fields!Umfang.Value) * CDbl(Fields!Hoehe.Value), 0.0))" % b.ist(61)

# Zusatz zum gemeinsamen Code des Masters: Zahlenformat mit Strich bei fehlendem Raum, Rechnen mit Nothing, Kuerzen, Rang aus der ID
CODE_AW = """
Public Function Zahl(ByVal x As Object, ByVal dez As Integer) As String
    If x Is Nothing Then Return "–"
    If IsDBNull(x) Then Return "–"
    Return Format(CDbl(x), "N" & dez)
End Function

Public Function Einheit(ByVal x As Object, ByVal e As String) As String
    If x Is Nothing Then Return ""
    If IsDBNull(x) Then Return ""
    Return e
End Function

Public Function Brutto(ByVal umfang As Object, ByVal hoehe As Object) As Object
    If umfang Is Nothing OrElse hoehe Is Nothing Then Return Nothing
    Return CDbl(umfang) * CDbl(hoehe)
End Function

Public Function Diff(ByVal a As Object, ByVal b As Object) As Object
    If a Is Nothing OrElse b Is Nothing Then Return Nothing
    Return CDbl(a) - CDbl(b)
End Function

' Name des Raums: Bezeichnung, sonst Funktion, sonst Strich; lange Namen werden gekuerzt (die Zelle waechst nicht).
Public Function RName(ByVal bez As Object, ByVal fkt As Object) As String
    Dim s As String = ""
    If Not bez Is Nothing Then s = bez.ToString().Trim()
    If s = "" AndAlso Not fkt Is Nothing Then s = fkt.ToString().Trim()
    If s = "" Then Return "–"
    If s.Length > 56 Then Return s.Substring(0, 55) & "…"
    Return s
End Function

Public Function Kurz(ByVal x As Object, ByVal n As Integer) As String
    Dim s As String = ""
    If Not x Is Nothing Then s = x.ToString()
    If s.Length > n Then Return s.Substring(0, n - 1) & "…"
    Return s
End Function

' Rang eines Rahmens aus der Raum-ID (Bez): die Ziffern der ID als Zahl, kleinste zuerst (entspricht der Sortierung nach Bez).
Public Function Rang(ByVal id As Object) As Double
    Dim s As String = ""
    If Not id Is Nothing Then s = id.ToString()
    Dim z As String = ""
    For Each ch As Char In s
        If Char.IsDigit(ch) Then z = z & ch
    Next
    If z.Length > 15 Then z = z.Substring(z.Length - 15)
    If z = "" Then Return 0.0
    Return Double.Parse(z, System.Globalization.CultureInfo.InvariantCulture)
End Function
"""


def tc(inner):
    return "<TablixCell><CellContents>%s</CellContents></TablixCell>" % inner


def sortiert(tablix_xml, *ausdruecke):
    """Sortierung der ganzen Datenregion (vor dem Gruppieren). Steht im Tablix nach den Filtern."""
    srt = "<SortExpressions>%s</SortExpressions>" % "".join(
        "<SortExpression><Value>%s</Value>%s</SortExpression>" % (c.esc(e), "<Direction>Descending</Direction>" if d else "")
        for e, d in ausdruecke)
    pos = tablix_xml.rfind("<Top>")
    return tablix_xml[:pos] + srt + tablix_xml[pos:]


def filter_beide(*xmls):
    """Mehrere <Filters>-Bloecke zu einem zusammenfassen (Tablix erlaubt nur einen)."""
    return "<Filters>" + "".join(f for x in xmls for f in re.findall(r"<Filter>.*?</Filter>", x, re.S)) + "</Filters>"


def tooltip(xml, text):
    """ToolTip in ein Image einsetzen (steht vor dem Style)."""
    return xml.replace("<Style>", "<ToolTip>%s</ToolTip><Style>" % c.esc(text), 1)


# ---------------------------------------------------------------- Kopfband
def band():
    x0 = c.INSET
    inner = (c.rect("AW_BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.ORANGE)
             + c.text("AW_BandOver", 1.4, x0, 12, 0.4, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.SKY, c.F_SEMI))
             + c.text("AW_BandTitel", 1.85, x0, 13, 1.45, c.run("Raum-Abwicklung", 30, c.WHITE, c.F_LIGHT))
             + c.text("AW_BandSub", 3.3, x0, 12.5, 0.55,
                      c.run('=Code.Kurz(Parameters!Project_Name.Value, 56) & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, "#CBD5E1", c.F))
             + c.text("AW_BandRechts", 1.4, x0 + 13, 5, 0.4, c.run("Räume", 8, c.SKY, c.F_SEMI), align="Right")
             + c.text("AW_BandRechts2", 1.85, x0 + 13, 5, 1.45,
                      c.para([c.run('=Format(%s, "N0")' % ANZ_RAHMEN, 30, c.WHITE, c.F_LIGHT)], "Right"))
             + c.text("AW_BandRechts3", 3.3, x0 + 13, 5, 0.55, c.run("mit Abwicklung", 9, "#CBD5E1", c.F), align="Right"))
    return c.rect("AW_Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


# ---------------------------------------------------------------- K070 Kennzahl-Kacheln
def flaeche(x):
    """Flaeche: ab 1.000 ganze Zahl, sonst eine Nachkommastelle (deutsch formatiert)."""
    return 'Format(%s, IIf(%s >= 1000, "#,##0", "#,##0.0"))' % (x, x)


@b.baustein("K070", "Kennzahl-Kacheln Abwicklung")
def k070(top, left, w):
    """Vier Kacheln: Raeume mit Abwicklung, Wandflaeche netto, brutto, Oeffnungen (brutto - netto)."""
    gap = 0.3
    kw = (w - 3 * gap) / 4
    items = b.kpi("AW_K1", top, left, kw, 'Format(%s, "N0")' % ANZ_RAHMEN, None, "", "Räume mit Abwicklung", "Rahmen im Teilbild")
    items += b.kpi("AW_K2", top, left + (kw + gap), kw, flaeche(SUM_NETTO), None, "m²", "Wandfläche netto",
                   "alle Räume, ohne Öffnungen")
    items += b.kpi("AW_K3", top, left + 2 * (kw + gap), kw, flaeche(SUM_BRUTTO), None, "m²", "Wandfläche brutto", "alle Räume, Umfang × Höhe")
    items += b.kpi("AW_K4", top, left + 3 * (kw + gap), kw, flaeche("(%s - %s)" % (SUM_BRUTTO, SUM_NETTO)), None, "m²",
                   "Öffnungen", "alle Räume, brutto − netto")
    items += b.etikett("AW_E1", top + 2.65, left, w, "K070",
                       "Kennzahl-Kacheln: Zahl der Rahmen; Wandflächen als Summe über alle Räume (Lookup in Summen geht nicht)")
    return items


# ---------------------------------------------------------------- B100 Abwicklung je Raum
KARTE_H = 11.95        # Karte: Kopf 1,0 + Zahlen 1,65 + Bild 9,0 + Luft
LUFT = 0.7             # Abstand ueber jeder Karte (Blatt 1: unter dem Abschnittskopf)
BILD_W, BILD_H = 17.0, 9.0                    # Seitenverhaeltnis 170 : 90 wie die Abfrage


def zahl_feld(name, top, left, w, label, wert, einheit, dez, gross=False):
    """Beschriftung (7 pt) und Zahl mit Einheit; die Zahlen stehen auf einer Grundlinie (valign Bottom)."""
    kopf = c.text(name + "_l", top, left, w, 0.35, c.run(label, 7, c.MUTED, c.F_SEMI), valign="Top")
    einh = '=Code.Einheit(%s, " %s")' % (wert, einheit)
    if gross:
        # Die grosse Zahl ist ein BLANKES Lookup (ganzer Ausdruck, Format ueber die Textlaufeigenschaft): Gemessen im
        # ReportViewer liefern die uebrigen Lookup-Ausdruecke der Karte (Format, CDbl, Code.*) ab Karte 2 nur dann Werte,
        # wenn mindestens ein blankes Lookup in der Karte steht, sonst #Error. Ohne Raum bleibt die Zahl leer, ein
        # Strich im selben Feld (zweiter Textlauf) springt ein - kein zweites Feld darueber (Ueberlappung).
        inhalt = c.para([c.run("=" + wert, 17, c.INK, c.F_LIGHT, fmt="N%d" % dez),
                         c.run('=IIf(IsNothing(%s), "–", "")' % wert, 17, c.INK, c.F_LIGHT), c.run(einh, 9, c.MUTED, c.F)])
    else:
        inhalt = c.para([c.run("=Code.Zahl(%s, %d)" % (wert, dez), 11, c.TEXT, c.F), c.run(einh, 7, c.FAINT, c.F)])
    return kopf + c.text(name + "_v", top + 0.35, left, w, 0.95, inhalt, valign="Bottom")


def karte(name, w):
    """Eine Karte (Inhalt einer Tablix-Zelle, ohne Lage): Kopfzeile, Zahlenzeile, Abwicklungsbild. Der Rahmen ist das
    Eltern-Rechteck der Karte: alles steht IN ihm (ein leerer Rahmen als Geschwister unter dem Inhalt ueberlappt ihn)."""
    t0 = 0.0
    items = ""
    # Kopfzeile: Raumname (Semibold), klein die Bauteil-ID
    # Der Name ist ein verschachtelter Lookup (Code.RName). Steht vor ihm in der Karte kein BLANKES Lookup, meldet der
    # ReportViewer ab Seite 2 "rsRuntimeErrorInExpression" (das Bild stimmt trotzdem): darum steht davor ein blankes Lookup,
    # das wegen des Formats ;;; nichts anzeigt.
    vor = c.run("=" + GRUND, 1, c.INK, c.F, fmt=";;;")
    items += b.klick(c.text(name + "_Name", t0, 0, 13.0, 1.0, c.para([vor, c.run("=" + NAME, 12, c.INK, c.F_SEMI)]), valign="Middle",
                            bg=c.SURFACE, pad=(14, 0, 0, 0)), ZOOM_RAUM, "Klick: in Allplan auf diesen Raum zoomen")
    items += c.text(name + "_Id", t0, 13.0, w - 13.0, 1.0, c.para([c.run("=Fields!Bez.Value", 7, c.MUTED, c.F)], "Right"),
                    valign="Middle", bg=c.SURFACE, pad=(0, 0, 14, 0))
    # Zahlenzeile
    spalten = [4.3, 2.8, 2.8, 2.4, 2.2, 2.5]
    x = 0.5
    zy = t0 + 1.15
    felder = [("WANDFLÄCHE NETTO", NETTO, "m²", 1, True), ("BRUTTO", BRUTTO, "m²", 1, False),
              ("ÖFFNUNGEN", OEFFNUNG, "m²", 1, False), ("UMFANG", UMFANG, "m", 1, False),
              ("HÖHE", HOEHE, "m", 2, False), ("GRUNDFLÄCHE", GRUND, "m²", 1, False)]
    for i, ((label, wert, einheit, dez, gross), bw) in enumerate(zip(felder, spalten)):
        items += zahl_feld("%s_Z%d" % (name, i), zy, x, bw, label, wert, einheit, dez, gross)
        x += bw
    # Bild 17,0 x 9,0 cm: weiss, Haarrand, anklickbar
    bild = tooltip(c.image(name + "_Bild", 0.02, 0.02, BILD_W - 0.04, BILD_H - 0.04, "=Fields!Bild.Value", mime="image/jpeg",
                           sizing="FitProportional", action=ZOOM_RAUM), "Klick: in Allplan auf diesen Raum zoomen")
    items += c.rect(name + "_BildFeld", t0 + 2.65, 0.5, BILD_W, BILD_H, bild, bg=c.WHITE, border_xml=RAND)
    return c.rect(name, None, 0, 0, 0, c.rect(name + "_Rahmen", LUFT, 0, w, KARTE_H, items, border_xml=RAND))


@b.baustein("B100", "Abwicklung je Raum")
def b100(top, left, w):
    """Karten mit Abwicklungsbild, hoechstens MAX_KARTEN, nach Bez sortiert; Blatt 1 eine Karte, danach zwei je Blatt.
    Liefert EINE Tablix (Kopf, Karten, Rest-Zeile, Hinweis, Etikett), die in den Berichtskoerper gehoert und waechst."""
    kopf = c.rect("AW_Kopf", None, 0, 0, 0, b.overline("AW_A", 0, 0, w, "Abwicklung", "Abwicklung je Raum"))
    rest = ANZ_RAHMEN_DS
    rest_text = c.cell("AW_Rest", c.run('=IIf(%s = 0, "Keine Abwicklung im Teilbild (Rahmen mit Material Abwicklung fehlen).", '
                                        'IIf(%s > %d, "… und " & Format(%s - %d, "#,##0") & IIf(%s - %d = 1, " weiterer Raum", " weitere Räume"), ""))'
                                        % (rest, rest, MAX_KARTEN, rest, MAX_KARTEN, rest, MAX_KARTEN), 8, c.MUTED, c.F), valign="Middle", pad=(0, 0, 0, 0))
    hinweis = c.cell("AW_Hinweis", c.run("Die Zeichnung erzeugt das Werkzeug werkzeug/abwicklung_zeichnen.py aus dem Modell "
                                         "(Räume als Rechteck). Flächen und Maße der Kopfzeile kommen live aus Allplan.", 7, c.MUTED, c.F),
                     valign="Top", pad=(0, 4, 0, 0))
    eti = b.in_cell(b.etikett("AW_E2", 0, 0, w, "B100",
                              "Karte je Rahmen (ObjNr 4, Material Abwicklung), Raumwerte per Lookup, Deckel 8; Blatt 1 eine Karte, danach zwei"))
    heights = [1.25, LUFT + KARTE_H, 0.5, 0.85, 0.45]
    zellen = [kopf, karte("AW_Karte", w), rest_text, hinweis, eti]
    rows = "".join("<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (c.cm(h), tc(z))
                   for h, z in zip(heights, zellen))
    blatt = "=Int(RowNumber(Nothing) / 2)"
    zeilen_h = ('<TablixRowHierarchy><TablixMembers>'
                "<TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>"
                '<TablixMember><Group Name="AW_Blatt"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions>'
                "<PageBreak><BreakLocation>Between</BreakLocation></PageBreak></Group>"
                '<TablixMembers><TablixMember><Group Name="AW_KarteG"/></TablixMember></TablixMembers></TablixMember>'
                "<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>"
                "<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>"
                "<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>"
                "</TablixMembers></TablixRowHierarchy>") % c.esc(blatt)
    xml = ('<Tablix Name="AW_Tb"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
           "<TablixRows>%s</TablixRows></TablixBody>"
           "<TablixColumnHierarchy><TablixMembers><TablixMember/></TablixMembers></TablixColumnHierarchy>%s"
           "<DataSetName>%s</DataSetName>%s<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>"
           "<Style><Border><Style>None</Style></Border></Style></Tablix>"
           % (c.cm(w), rows, zeilen_h, ALLE, filter_beide(c.filters(RAHMEN_ZEILE), c.topn(RANG, MAX_KARTEN, unten=True)),
              c.cm(top), c.cm(left), c.cm(sum(heights)), c.cm(w)))
    return sortiert(xml, ("=Fields!Bez.Value", False))


# ---------------------------------------------------------------- Bericht
KOPF_H = 8.4            # Hoehe des festen Kopfbereichs auf Blatt 1 (Band, Kacheln); darunter beginnt die wachsende Tablix


def seite_kopf():
    x0, w = c.INSET, c.CONTENT_W
    return band() + k070(5.05, x0, w)


def build():
    x0, w = c.INSET, c.CONTENT_W
    xml = c.report([seite_kopf()], [c.dataset(ALLE, QUERY, FIELDS)], footer_xml=b.fuss(), code=b.CODE + CODE_AW,
                   page_body_h=KOPF_H, labels=["Raum-Abwicklung"])
    tab = b100(KOPF_H, x0, w)
    # Die Tablix steht direkt im Berichtskoerper (nicht im Seiten-Rechteck), damit sie ueber Blatt 1 hinaus wachsen
    # und umbrechen darf. Der Koerper behaelt eine Mindesthoehe von Kopfbereich + Kopfzeile + einer Karte.
    marke = "</ReportItems><Height>%s</Height><Style/></Body>" % c.cm(KOPF_H)
    assert xml.count(marke) == 1
    xml = xml.replace(marke, tab + "</ReportItems><Height>%s</Height><Style/></Body>" % c.cm(KOPF_H + 1.25 + LUFT + KARTE_H))
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Abwicklung.rdlc")
    c.save(ziel, xml)
    return ziel


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--daten"})
    ziel = build()
    print(ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        c.rendern(ziel, JSON, AUS)
