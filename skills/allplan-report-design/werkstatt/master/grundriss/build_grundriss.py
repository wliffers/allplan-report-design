# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Grundriss" (RDL 2016) nach out/Report_Master_Grundriss.rdlc.

Allplan liefert je Report nur EINE Bildart (die erste @205@-Spalte bestimmt alle Bilder). Der Master-Report nutzt
farbige 3D-Bauteilbilder; dieser Report zeigt die zweite Bildart, den Planmodus (Image=true):
der Geschoss-Grundriss (Bild der Decke) und je Raum eine Karte mit Raumplan.

    python build_grundriss.py              schreibt out/Report_Master_Grundriss.rdlc
    python build_grundriss.py --render     rendert zusaetzlich kopflos nach grundriss/aus/png (daten/grundriss.json)
    python build_grundriss.py --render --daten=<name>    anderer Datensatz (daten/<name>.json, aus/png_<name>)
Ausgeliefert wird der Datensatz grundriss; eigene legst du als daten/<name>.json dazu.

Jeder Block ist ein angemeldeter Baustein (@b.baustein): B080 Geschoss-Grundriss, B090 Raumkarten, K050 Kennzahl-Kacheln,
D150 Ring Flaeche nach Nutzung mit Legende, M080 Kennwert-Balken. seite1()/seite2() legen sie nur an ihre Stelle.
Datenfest: Legende und Ring hoechstens 7 Nutzungen, Raumkarten hoechstens 9; der Report bleibt bei zwei Seiten.
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
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "grundriss")
JSON = os.environ.get("GRUNDRISS_JSON", os.path.join(HERE, "daten", DATEN + ".json"))
AUS = os.environ.get("GRUNDRISS_AUS", os.path.join(HERE, "aus", "png" if DATEN == "grundriss" else "png_" + DATEN))

MAX_NUTZUNGEN = 7      # Deckel fuer Ring und Legende
MAX_RAEUME = 9         # Deckel fuer die Raumkarten (3 Reihen a 3)

# ---------------------------------------------------------------- Daten
# ObjNr 4 = Decke (ihr Planbild ist der ganze Grundriss des Teilbilds), ObjNr 61 = Raum (Grundriss dieses Raums).
# Eine Bildgroesse gilt fuer alle Zeilen; die Raumkarten zeigen das Bild verkleinert (FitProportional).
QUERY = """SELECT
       @498@[Name=Objekt],
       [Name=ObjNr|f=@OBJ@],
       @507@[Name=Bezeichnung],
       @506@[Name=Funktion],
       @220@[Name=Laenge],
       @221@[Name=Dicke],
       @222@[Name=Hoehe],
       @229@[Name=Flaeche],
       @223@[Name=Volumen],
       @10@[Name=Nr],
       @205@[Name=Bild|Image=true|Width=180|Height=120|GText=HD]
FROM [MODEL_DATA, Filter=@OBJ@.eq.4.or.@OBJ@.eq.61]
"""
FIELDS = [("Objekt", "String"), ("ObjNr", "String"), ("Bezeichnung", "String"), ("Funktion", "String"),
          ("Laenge", "Double"), ("Dicke", "Double"), ("Hoehe", "Double"), ("Flaeche", "Double"),
          ("Volumen", "Double"), ("Nr", "String"), ("Bild", "Byte[]")]

DECKE, RAUM = b.ist(4), b.ist(61)
FLAECHE = "CDbl(Fields!Flaeche.Value)"
RAUM_SUMME = b.summe("Flaeche", RAUM)
RAUM_MAX = "Max(IIf(%s, %s, 0.0))" % (RAUM, FLAECHE)
DECKE_SUMME = b.summe("Flaeche", DECKE)       # alle Decken (ObjNr 4) zusammen; einzelne Decken koennen winzige Platten sein
# Name eines Raums: Nutzung (@506@), sonst Bezeichnung (@507@), sonst "Raum"
NAME = ('IIf(Len(Fields!Funktion.Value) > 0, Fields!Funktion.Value, '
        'IIf(Len(Fields!Bezeichnung.Value) > 0, Fields!Bezeichnung.Value, "Raum"))')
NR_NACHRANG = "Val(Right(Fields!Nr.Value, 8)) / 1000000000000"          # macht den Rang je Raum eindeutig (TopN nimmt gleiche Werte sonst alle mit)
RAUM_ANZAHL = b.anzahl(RAUM, "AllplanReport")
RAUM_FLAECHE = b.summe("Flaeche", RAUM, "AllplanReport")
RAHMEN = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR


def sortiert(tablix_xml, *ausdruecke):
    """Sortierung der ganzen Datenregion (vor dem Gruppieren). Steht im Tablix nach den Filtern."""
    srt = "<SortExpressions>%s</SortExpressions>" % "".join(
        "<SortExpression><Value>%s</Value>%s</SortExpression>" % (c.esc(e), "<Direction>Descending</Direction>" if d else "")
        for e, d in ausdruecke)
    pos = tablix_xml.rfind("<Top>")
    return tablix_xml[:pos] + srt + tablix_xml[pos:]


def tooltip(xml, text):
    """ToolTip in ein Image einsetzen (steht vor dem Style)."""
    return xml.replace("<Style>", "<ToolTip>%s</ToolTip><Style>" % c.esc(text), 1)


def filter_beide(*xmls):
    """Mehrere <Filters>-Bloecke zu einem zusammenfassen (Tablix erlaubt nur einen)."""
    return "<Filters>" + "".join(f for x in xmls for f in re.findall(r"<Filter>.*?</Filter>", x, re.S)) + "</Filters>"


def mini(name, top, left, w, h, inhalt, bedingung):
    """Ein-Zellen-Tabelle ueber die nach Flaeche absteigend sortierten Zeilen: First() liefert den groessten Raum."""
    xml = c.tablix(name, top, left, [w], [("daten", h, [inhalt])], group="=1", filter_expr=bedingung)
    return sortiert(xml, ("=" + FLAECHE, True))


# ---------------------------------------------------------------- Bausteine
def kopf2():
    """Kopf der zweiten Seite: wie seitenkopf(), aber fuer den Begleit-Report."""
    return b.folgekopf("G_P2Kopf", "G_P2", "REPORT MASTER  ·  BEGLEIT-REPORT  ·  SEITE 2", "Raumpläne",
                       c.run("Grundriss je Raum, nach Fläche", 8.5, "#CBD5E1"), untertitel_text="Grundriss je Raum, nach Fläche")


def band():
    x0 = c.INSET
    inner = (c.rect("G_BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.ORANGE)
             + c.text("G_BandOver", 1.4, x0, 12, 0.4, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.SKY, c.F_SEMI))
             + c.text("G_BandTitel", 1.85, x0, 13, 1.45, c.run("Grundriss und Räume", 30, c.WHITE, c.F_LIGHT))
             + c.text("G_BandSub", 3.3, x0, 13, 0.55,
                      c.run('=Parameters!Project_Name.Value & "   ·   Geschossgrundriss   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, "#CBD5E1", c.F))
             + c.text("G_BandRechts", 1.4, x0 + 13, 5, 0.4, c.run("Geschossfläche", 8, c.SKY, c.F_SEMI), align="Right")
             + c.text("G_BandRechts2", 1.85, x0 + 13, 5, 1.45,
                      c.para([c.run("=" + DECKE_SUMME, 30, c.WHITE, c.F_LIGHT, fmt="N0"), c.run(" m²", 12, c.SKY, c.F)], "Right"))
             + c.text("G_BandRechts3", 3.3, x0 + 13, 5, 0.55, c.run("Decken, brutto", 9, "#CBD5E1", c.F), align="Right"))
    return c.rect("G_Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


def kachel_gross(name, top, left, w):
    """Kennzahl-Kachel 'Groesster Raum': Zahl und Name kommen aus der absteigend sortierten Datenregion."""
    zahl = c.cell(name + "_vc", c.para([c.run("=First(%s)" % FLAECHE, 22, c.INK, c.F_LIGHT, fmt="N1"),
                                        c.run(" m²", 10, c.MUTED, c.F)]), valign="Bottom", pad=(0, 0, 0, 0))
    notiz = c.cell(name + "_nc", c.run("=First(%s)" % NAME, 7, c.MUTED, c.F), valign="Top", pad=(0, 0, 0, 0))
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + mini(name + "_v", 0.42, 0.32, w - 0.4, 1.05, zahl, RAUM)
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run("GRÖSSTER RAUM", 7, c.TEXT, c.F_SEMI))
             + mini(name + "_n", 1.92, 0.32, w - 0.4, 0.4, notiz, RAUM))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


def grundriss(name, top, left, w, h):
    """Geschoss-Grundriss: das Bild der GROESSTEN Decke (Region nach Flaeche absteigend, First). Das Planbild zeigt den
    Ausschnitt um das gewaehlte Objekt - eine kleine Platte waere nur ein Eckchen. Ohne Decke steht ein ruhiger Leertext."""
    bild = c.image(name + "_Bild", None, 0, 0, 0, "=First(Fields!Bild.Value)", mime="image/jpeg", sizing="FitProportional")
    tb = c.tablix(name + "_Tb", 0, 0, [w], [("daten", h, [bild])], group="=1", filter_expr=DECKE)
    tb = sortiert(tb, ("=" + FLAECHE, True))
    # Der Leertext ist die NoRowsMessage der Tabelle, kein zweites Feld ueber dem Bild (zwei Felder auf derselben Stelle
    # ueberlappen sich, und das Report-Fenster schiebt eines weg).
    tb = tb.replace("<Top>", "<NoRowsMessage>Keine Decke im Teilbild: kein Geschossgrundriss</NoRowsMessage><Top>", 1)
    tb = tb.replace("<Style><Border><Style>None</Style></Border></Style></Tablix>",
                    "<Style><Border><Style>None</Style></Border><FontFamily>Segoe UI</FontFamily><FontSize>8pt</FontSize>"
                    "<Color>%s</Color><TextAlign>Center</TextAlign><VerticalAlign>Middle</VerticalAlign></Style></Tablix>" % c.FAINT)
    return c.rect(name, top, left, w, h, tb)


def raumkarten(name, top, left, pitch, karte_w, karte_h, zeile_h, reihen):
    """Raster 3 je Reihe: Zeile = (RowNumber-1) \\ 3, Spalte = (RowNumber-1) Mod 3, nach Flaeche absteigend.
    Deckel: hoechstens MAX_RAEUME Karten (die groessten), TopN an der Datenregion."""
    # Nicht-Raeume bekommen -1: sie nehmen den groessten keinen Platz weg, egal in welcher Reihenfolge die Filter laufen
    rang = "IIf(%s, %s + %s, -1.0)" % (RAUM, FLAECHE, NR_NACHRANG)
    bw = karte_w - 0.3
    ih = 4.4                                   # Hoehe des Bildfelds; darunter Kennung, Name, Flaeche, Masse
    bild = tooltip(c.image(name + "_Bild", 0.15, 0.15, bw, ih, "=Fields!Bild.Value", mime="image/jpeg",
                           sizing="FitProportional", action=b.ZOOM),
                   "Klick: in Allplan auf diesen Raum zoomen")
    nummer = c.text(name + "_Nr", ih + 0.3, 0.3, bw, 0.35,
                    c.run('="RAUM " & Format(RowNumber(Nothing), "00")', 6.5, c.BLUE, c.F_SEMI))
    titel = b.klick(c.text(name + "_Name", ih + 0.7, 0.3, bw, 0.5, c.run("=" + NAME, 10.5, c.INK, c.F_SEMI)))
    zahl = c.text(name + "_Fl", ih + 1.25, 0.3, bw, 0.8,
                  c.para([c.run("=" + FLAECHE, 18, c.INK, c.F_LIGHT, fmt="N1"), c.run(" m²", 9, c.MUTED, c.F)]), valign="Top")
    masse = c.text(name + "_Ma", ih + 2.1, 0.3, bw, 0.4,
                   c.para([c.run('=Format(CDbl(Fields!Laenge.Value), "N2") & " × " & Format(CDbl(Fields!Dicke.Value), "N2") & " m"',
                                 7.5, c.MUTED, c.F),
                           c.run('="   ·   H " & Format(CDbl(Fields!Hoehe.Value), "N2") & " m"', 7.5, c.FAINT, c.F)]))
    # In der letzten Reihe erzeugt die Matrix auch fuer fehlende Raeume eine Zelle: ohne Datensatz (Nr leer) ausblenden.
    karte = c.rect(name + "_Zelle", None, 0, 0, 0,
                   c.rect(name + "_Rahmen", 0, 0, karte_w, karte_h, bild + nummer + titel + zahl + masse, border_xml=RAHMEN),
                   hidden='=Len(Fields!Nr.Value & "") = 0')
    xml = ('<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
           "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
           "</TablixCells></TablixRow></TablixRows></TablixBody>"
           '<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="%s_c"><GroupExpressions><GroupExpression>'
           "=(RowNumber(Nothing) - 1) Mod 3</GroupExpression></GroupExpressions></Group></TablixMember></TablixMembers>"
           "</TablixColumnHierarchy>"
           '<TablixRowHierarchy><TablixMembers><TablixMember><Group Name="%s_r"><GroupExpressions><GroupExpression>'
           "=(RowNumber(Nothing) - 1) \\ 3</GroupExpression></GroupExpressions></Group></TablixMember></TablixMembers>"
           "</TablixRowHierarchy><DataSetName>AllplanReport</DataSetName>%s"
           "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>"
           "<Style><Border><Style>None</Style></Border></Style></Tablix>"
           % (name + "_Tb", c.cm(pitch), c.cm(zeile_h), karte, name, name,
              filter_beide(c.filters(RAUM), c.topn(rang, MAX_RAEUME)), c.cm(zeile_h), c.cm(pitch)))
    xml = sortiert(xml, ("=" + FLAECHE, True), ("=Fields!Nr.Value", False))
    return c.rect(name, top, left, 3 * pitch, reihen * zeile_h, xml)


# ---------------------------------------------------------------- Bausteine dieser Seiten
@b.baustein("K050", "Kennzahl-Kacheln")
def k050(top, left, w):
    """Drei Kacheln: Raumflaeche gesamt, Anzahl Raeume, groesster Raum."""
    gap = 0.3
    kw = (w - 2 * gap) / 3
    items = b.kpi("G_K1", top, left, kw, RAUM_SUMME, "N1", "m²", "Raumfläche gesamt", "Summe aller Räume im Teilbild")
    items += b.kpi("G_K2", top, left + kw + gap, kw, b.anzahl(RAUM), "N0", "", "Anzahl Räume",
                   '=Format(%s, "N1") & " m² je Raum im Mittel"' % (b.quote(RAUM_SUMME, b.anzahl(RAUM)),))
    items += kachel_gross("G_K3", top, left + 2 * (kw + gap), kw)
    items += b.etikett("G_E3", top + 2.65, left, w, "K050",
                       "Kennzahl-Kacheln: Summe und Anzahl der Raumzeilen, größter Raum als First() der nach Fläche sortierten Zeilen")
    return items


@b.baustein("B080", "Geschoss-Grundriss")
def b080(top, left, w, h=11.9):
    """Planbild der Decke: ein Bild fuer das ganze Geschoss, auch bei mehreren Decken im Teilbild."""
    items = b.overline("G_A1", top, left, w, "Grundriss", "Geschoss im Überblick")
    items += grundriss("G_Plan", top + 1.45, left, w, h)
    items += b.etikett("G_E1", top + 1.45 + h + 0.05, left, w, "B080",
                       "Planbild der Decke (@205@ mit Image=true), ganzer Grundriss des Teilbilds")
    return items


@b.baustein("D150", "Ring Fläche nach Nutzung mit Legende")
def d150(top, left, w):
    """Ring und Legende der Raumflaeche je Nutzung: hoechstens MAX_NUTZUNGEN, der Rest steht als Zeile 'weitere'."""
    items = b.overline("G_A2", top, left, w, "Räume", "Fläche nach Nutzung")
    flaeche = "Sum(CDbl(Fields!Flaeche.Value))"
    rang = flaeche + " + " + NR_NACHRANG.replace("Fields!Nr.Value", "Max(Fields!Nr.Value)")
    deckel = c.topn(rang, MAX_NUTZUNGEN)
    ring = v.chart(
        "G_ChRaum", top + 1.4, left - 0.1, 3.9, 3.9,
        [v.S("Flaeche", {"Y": "=" + flaeche}, typ="Shape", sub="Doughnut",
             custom_xml=v.custom(DoughnutRadius="30", PieLabelStyle="Disabled", PieStartAngle="270"),
             pstyle="<Color>=Code.Stufe(Fields!Funktion.Value)</Color>" + v.border("#FFFFFF", "Solid", "1.5pt"))],
        [("=Fields!Funktion.Value", "=" + flaeche, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        titles=(v.title('=Format(%s, "N0") & " m²"' % RAUM_FLAECHE, size='=IIf(%s >= 1000, "12pt", "15pt")' % RAUM_FLAECHE,
                        color=c.INK, bold=False,
                        extra="<ChartElementPosition><Top>38</Top><Left>20</Left><Height>14</Height><Width>60</Width></ChartElementPosition>")
                + v.title("Raumfläche", size="7.5pt", name="Unter", color=c.MUTED, bold=False,
                          extra="<ChartElementPosition><Top>52</Top><Left>20</Left><Height>9</Height><Width>60</Width></ChartElementPosition>")),
        extra=c.filters(RAUM))
    ring = ring.replace("</GroupExpressions></Group>", "</GroupExpressions>" + deckel + "</Group>", 1)
    lrow = c.edge(["Bottom"], c.HAIR, "0.5pt")
    kopf = c.edge(["Bottom"], c.INK, "1pt")
    nutzung = 'IIf(Len(Fields!Funktion.Value) = 0, "ohne Nutzung", Fields!Funktion.Value)'
    # Der Deckel wirkt nicht auf die Fusszeile (sie sieht alle Gruppen): angezeigt werden genau MAX_NUTZUNGEN, der Rest ist die Differenz
    rest_n = '(CountDistinct(IIf(%s, Fields!Funktion.Value, Nothing), "AllplanReport") - %d)' % (RAUM, MAX_NUTZUNGEN)
    zeile_h = 0.44        # 8-pt-Text braucht mit Innenabstand 0,41 cm; bei 0,40 wurde die Zeile unten angeschnitten
    legende = c.tablix("G_TbRaum", 0, 0, [0.4, 3.6, 1.2], [
        ("kopf", 0.45, [
            c.cell("G_LK1", c.run("", 7), border_xml=kopf, pad=(0, 0, 0, 3)),
            c.cell("G_LK2", c.run("NUTZUNG", 7, c.MUTED, c.F_SEMI), valign="Bottom", border_xml=kopf, pad=(0, 0, 2, 3)),
            c.cell("G_LK3", c.run("M²", 7, c.MUTED, c.F_SEMI), "Right", valign="Bottom", border_xml=kopf, pad=(0, 0, 0, 3)),
        ]),
        ("daten", zeile_h, [
            c.cell("G_L1", c.run("■", 9, "=Code.Stufe(Fields!Funktion.Value)"), "Left", pad=(0, 0, 0, 0), border_xml=lrow),
            c.cell("G_L2", c.run("=" + nutzung, 8, c.TEXT), pad=(0, 1, 2, 1), border_xml=lrow),
            c.cell("G_L3", c.run("=" + flaeche, 8, c.INK, c.F_SEMI, fmt="N1"), "Right", pad=(0, 1, 0, 1), border_xml=lrow),
        ]),
        ("fuss", zeile_h, [
            c.cell("G_LF1", c.run("", 8), pad=(0, 0, 0, 0)),
            c.cell("G_LF2", c.run('=IIf(%s > 0, "+ " & %s & " weitere", "")' % (rest_n, rest_n), 8, c.MUTED), pad=(0, 1, 2, 1)),
            c.cell("G_LF3", c.run("", 8), "Right", pad=(0, 1, 0, 1)),
        ])], group="=Fields!Funktion.Value", sort="=" + flaeche, sort_desc=True, filter_expr=RAUM)
    legende = legende.replace("</GroupExpressions></Group>", "</GroupExpressions>" + deckel + "</Group>", 1)
    items += ring + c.rect("G_FeldRaum", top + 1.4, left + 3.9, 5.2, 0.45 + (MAX_NUTZUNGEN + 1) * zeile_h, legende)
    items += b.etikett("G_E4", top + 1.4 + 4.0, left, w, "D150",
                       "Ring mit Legende: Fläche je Nutzung, Deckel 7 (c.topn), Rest als „weitere“")
    return items


def kennwert_gueltig(name, top, left, w, label, note, anteil, farbe):
    """Wie b.kennwert, aber die Prozentzahl erscheint nur zwischen 0 und 100 %; sonst steht ein Strich und der Balken ist leer."""
    ok = "(%s > 0 And %s <= 1)" % (anteil, anteil)
    return (c.text(name + "_l", top, left, w - 2.2, 0.42, c.run(label, 9.5, c.INK, c.F_SEMI))
            + c.text(name + "_n", top + 0.47, left, w - 2.2, 0.36, c.run(note, 7.5, c.MUTED))
            + c.text(name + "_v", top, left + w - 2.2, 2.2, 0.83,
                     c.run('=IIf(%s, Format(%s, "0 %%"), "–")' % (ok, anteil), 17, c.INK, c.F_LIGHT), align="Right", valign="Bottom")
            + b.fortschritt(name + "_b", top + 0.95, left, w, "IIf(%s, %s, 0.0)" % (ok, anteil), farbe))


@b.baustein("M080", "Kennwert-Balken")
def m080(top, left, w):
    """Zwei Kennwerte als Prozentzahl mit Balken. Anteile ueber b.quote() (sicher bei null); ausserhalb 0-100 % steht ein Strich."""
    def gekappt(q):
        return "IIf(%s > 1.0, 1.0, %s)" % (q, q)

    items = b.overline("G_A3", top, left, w, "Kennwerte", "Anteile am Geschoss")
    # Bezug: die Summe aller Decken des Teilbilds (eine einzelne kleine Decke ergab 2920 %)
    items += kennwert_gueltig("G_W1", top + 1.45, left, w, "Nettoraumfläche", "Raumfläche zu Geschossfläche",
                              b.quote(RAUM_SUMME, DECKE_SUMME), c.BLUE)
    items += b.kennwert("G_W2", top + 2.95, left, w, "Größter Raum", "Anteil an der gesamten Raumfläche",
                        gekappt(b.quote(RAUM_MAX, RAUM_SUMME)), c.MUTED)
    items += b.etikett("G_E5", top + 4.45, left, w, "M080",
                       "Kennwert-Balken: Anteil als b.quote(), nur zwischen 0 und 100 %")
    return items


@b.baustein("B090", "Raumkarten")
def b090(top, left, w):
    """Raumkarten im Raster 3 je Reihe, die MAX_RAEUME groessten; darunter der Hinweis auf die uebrigen Raeume."""
    items = b.overline("G_B1", top, left, w, "Räume", "Raumpläne nach Fläche")
    luecke = 0.4
    pitch = (w + luecke) / 3
    karte_w, karte_h = pitch - luecke, 7.05
    zeile_h = karte_h + luecke
    items += raumkarten("G_Karte", top + 1.45, left, pitch, karte_w, karte_h, zeile_h, 3)
    ey = top + 1.45 + 3 * zeile_h + 0.05      # unter dem Raster (dessen Hoehe schliesst die letzte Luecke ein)
    rest = "%s - %d" % (RAUM_ANZAHL, MAX_RAEUME)
    items += c.text("G_KarteRest", ey, left, w, 0.4,
                    c.run('=IIf(%s > 0, "… und " & Format(%s, "#,##0") & " weitere Räume", "")' % (rest, rest), 8, c.MUTED, c.F))
    items += b.etikett("G_E2", ey + 0.5, left, w, "B090",
                       "Raster 3 je Reihe, die 9 größten nach Fläche (TopN), Klick zoomt (Feld Nr); Raumbild zeigt die Raumbeschriftung des Teilbilds, wenn gezeichnet")
    return items


# ---------------------------------------------------------------- Seiten
def seite1():
    x0, w = c.INSET, c.CONTENT_W
    items = band()
    items += k050(5.05, x0, w)
    items += b080(8.4, x0, w)
    t2 = 22.6                      # D150 endet mit seinem Etikett bei 28,4 cm; nutzbar sind 28,5
    lw = 9.4
    items += d150(t2, x0, lw)
    items += m080(t2, x0 + lw + 0.8, w - lw - 0.8)
    return items


def seite2():
    return kopf2() + b090(3.3, c.INSET, c.CONTENT_W)


SEITEN = [("Grundriss und Räume", seite1), ("Raumpläne", seite2)]


def build():
    pages = [fn() for _t, fn in SEITEN]
    xml = c.report(pages, [c.dataset("AllplanReport", QUERY, FIELDS)], footer_xml=b.fuss(), code=b.CODE,
                   labels=[t for t, _f in SEITEN])
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Grundriss.rdlc")
    c.save(ziel, xml)
    return ziel


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--daten"})
    ziel = build()
    print(ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        c.rendern(ziel, JSON, AUS)
