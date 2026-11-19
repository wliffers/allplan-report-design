# -*- coding: utf-8 -*-
"""Seite 1 - Uebersicht: Titelband, Kennzahl-Kacheln, zwei Diagramme, Tabelle mit Zellenbalken,
Kennwert-Balken und Bildkarten aus dem Modell. Diese Seite ist der Gestaltungs-Massstab.

Datenfest: jede Liste hat einen Deckel (TopN), keine Projektnamen in Ausdruecken (Materialgruppe statt
Materialname), Anteile ohne Grundlage zeigen "-" statt einer Scheinaussage. Jeder Block ist eine eigene
Funktion mit fester Kennung (K010 ... B010)."""
import re

import core as c
import viz as v
import bausteine as b
from bausteine import (ROHBAU, WAND, RAUM, FENSTER, TUER, MIT_MATERIAL, MAT_FARBE, MATGRUPPE, IST_BETON, IST_VERKEHR,
                       summe, anzahl, raw, in_cell, quote, overline, kennwert, karten, etikett, fortschritt)


TITEL = "Übersicht"   # Name der Seite in der Dokumentstruktur (PDF-Lesezeichen)

# ---------------------------------------------------------------- Zahlen (Ausdruecke), projektunabhaengig
MAX_NUTZUNGEN = 7      # Ring und Legende zeigen hoechstens so viele Raumnutzungen
MAX_GRUPPEN = 5        # Tabelle "Bauteile nach Material": Materialgruppen
MAX_KARTEN = 5         # Bildkarten nebeneinander
BETON_ROHBAU = "(%s And %s)" % (ROHBAU, IST_BETON)
ROHBAU_VOL = summe("Volumen", MIT_MATERIAL)
BETON_VOL = summe("Volumen", BETON_ROHBAU)
AUSSEN = summe("Flaeche", "(%s And %s)" % (WAND, IST_BETON))      # Aussenwand = Wandschichten aus Beton (Materialgruppe)
FENSTER_FL = summe("Flaeche", FENSTER)
FENSTER_OK = "(%s > 0 And %s > 0)" % (AUSSEN, FENSTER_FL)       # ohne Fenster oder Betonwand keine Anteilsaussage
ANTEIL = quote(FENSTER_FL, AUSSEN)
RAUM_FL = summe("Flaeche", RAUM)
N_RAUM = anzahl(RAUM)
ZIEL = "Parameters!Ziel_Fensteranteil.Value / 100"
FLAECHE = "Sum(CDbl(Fields!Flaeche.Value))"
VOLUMEN = "Sum(CDbl(Fields!Volumen.Value))"
# eindeutiger Nachrang: gleiche Werte am Deckelrand sollen nicht alle mitzaehlen
NACHRANG = "Min(Val(Right(Fields!Nr.Value, 6))) / 1000000000.0"


def deckel(xml, gruppe, ausdruck, n):
    """Haengt an die Gruppe einen "nur die n groessten"-Filter (Chart-Kategorie, Tablix-Zeilengruppe, Spaltengruppe)."""
    f = c.topn(ausdruck, n)
    return re.sub(r'(<Group Name="%s"><GroupExpressions>.*?</GroupExpressions>)' % re.escape(gruppe),
                  lambda m: m.group(1) + f, xml, count=1, flags=re.S)


def fm(x, grenze=100):
    """Zahl mit Tausenderpunkt; ab der Grenze ohne Nachkommastelle."""
    return 'Format(%s, IIf(Abs(%s) >= %d, "N0", "N1"))' % (x, x, grenze)


# ---------------------------------------------------------------- Kopfband (Seitenrahmen, kein Baustein)
def band():
    x0 = c.INSET
    inner = (c.rect("BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.ORANGE)
             + c.text("BandOver", 1.4, x0, 12, 0.4, c.run("REPORT MASTER  ·  ALLPLAN 2027", 8, c.SKY, c.F_SEMI))
             + c.text("BandTitel", 1.85, x0, 13, 1.45, c.run("Gebäudeauswertung", 30, c.WHITE, c.F_LIGHT))
             + c.text("BandSub", 3.3, x0, 13, 0.55,
                      c.run('=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, "#CBD5E1", c.F))
             + c.text("BandRechts", 1.4, x0 + 13, 5, 0.4, c.run("Übersicht", 8, c.SKY, c.F_SEMI), align="Right")
             + c.text("BandRechts2", 1.85, x0 + 13, 5, 1.45,
                      c.para([c.run("=" + anzahl(MIT_MATERIAL), 30, c.WHITE, c.F_LIGHT, fmt="N0")], "Right"))
             + c.text("BandRechts3", 3.3, x0 + 13, 5, 0.55, c.run("Bauteile im Modell", 9, "#CBD5E1", c.F), align="Right"))
    return c.rect("Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


# ---------------------------------------------------------------- K010 Kernaussage
@b.baustein("K010", "Kernaussage")
def k010(top, left, w):
    """Ein Satz, der sagt, was die Zahlen bedeuten. Halbsaetze ohne Grundlage (keine Raeume, keine Fenster) entfallen."""
    ok_r = "%s > 0" % N_RAUM
    ok_f = FENSTER_OK

    def s(txt, cond=None):
        if cond:
            return c.run('=IIf(%s, "%s", "")' % (cond, txt), 11.5, c.TEXT, c.F_LIGHT)
        return c.run(txt, 11.5, c.TEXT, c.F_LIGHT)

    def z(expr, fmt, einheit="", cond=None):
        wert = 'Format(%s, "%s")' % (expr, fmt) + (' & "%s"' % einheit if einheit else "")
        return c.run("=" + ('IIf(%s, %s, "")' % (cond, wert) if cond else wert), 11.5, c.INK, c.F_SEMI)

    farbe = '=IIf(%s < %s, "%s", "%s")' % (ANTEIL, ZIEL, c.ORANGE, c.GREEN)
    items = c.text("Aussage", top, left, w, 1.25, c.para([
        s("Die Bauteile umfassen "), z(ROHBAU_VOL, "#,##0", " m³"), s(", davon "), z(quote(BETON_VOL, ROHBAU_VOL), "0 %"), s(" Beton."),
        s(" ", ok_r), z(N_RAUM, "0", "", ok_r), s(" Räume mit zusammen ", ok_r), z(RAUM_FL, "#,##0", " m²", ok_r), s(".", ok_r),
        s(" Der Fensterflächenanteil liegt mit ", ok_f), z(ANTEIL, "0 %", "", ok_f),
        c.run('=IIf(%s, IIf(%s < %s, " unter", " über"), "")' % (ok_f, ANTEIL, ZIEL), 11.5, farbe, c.F_SEMI),
        s(" dem Ziel von ", ok_f), z(ZIEL, "0 %", "", ok_f), s(".", ok_f)]), grow=False)
    items += etikett("E01_e", top + 1.3, left, w, "K010",
                     "Satz aus Ausdrücken (Sum, IIf, Format); Halbsätze ohne Grundlage entfallen, Beton über die Materialgruppe")
    return items


# ---------------------------------------------------------------- K020 Kennzahl-Kacheln
def _gross(txt_expr, farbe=c.INK):
    """Grosse Zahl; die Schriftgroesse schrumpft mit der Ziffernzahl, damit nichts umbricht."""
    groesse = 'IIf(Len(%s) >= 8, "14pt", IIf(Len(%s) >= 6, "18pt", "22pt"))' % (txt_expr, txt_expr)
    return ("<TextRun><Value>=%s</Value><Style><FontFamily>%s</FontFamily><FontSize>=%s</FontSize><Color>%s</Color></Style></TextRun>"
            % (c.esc(txt_expr), c.F_LIGHT, c.esc(groesse), farbe))


def _kachel(name, top, left, w, wert, einheit, label, note):
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, w - 0.4, 1.05,
                      c.para([_gross(wert), c.run(" " + einheit if einheit else "", 10, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run(label.upper(), 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4, c.run(note, 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


@b.baustein("K020", "Kennzahl-Kacheln")
def k020(top, left, w):
    gap = 0.3
    kw = (w - 4 * gap) / 5
    tiles = [
        ("K1", 'Format(%s, "N0")' % summe("Flaeche", WAND), "m²", "Wandfläche", "alle Schichten"),
        ("K2", fm(BETON_VOL), "m³", "Beton", "alle Bauteile aus Beton"),
        ("K3", 'Format(%s, "N0")' % RAUM_FL, "m²", "Raumfläche", '=%s & " Räume"' % N_RAUM),
        ("K4", 'Format(%s, "N0")' % anzahl(FENSTER), "", "Fenster", '=%s & " m² Glasfläche"' % fm(FENSTER_FL, 1000)),
        ("K5", 'Format(%s, "N0")' % anzahl(TUER), "", "Türen", '=%s & " m² Öffnung"' % fm(summe("Flaeche", TUER), 1000)),
    ]
    items = ""
    for i, (name, wert, einheit, label, note) in enumerate(tiles):
        items += _kachel(name, top, left + i * (kw + gap), kw, wert, einheit, label, raw(note))
    items += etikett("E02_e", top + 2.6, left, w, "K020",
                     "fünf Kacheln; die Zahl schrumpft mit der Stellenzahl, ab 100 ohne Nachkommastelle")
    return items


# ---------------------------------------------------------------- D010 Balken Volumen nach Materialgruppe
@b.baustein("D010", "Balken Volumen nach Materialgruppe")
def d010(top, left, w):
    items = overline("A1", top, left, w, "Mengen", "Volumen nach Material")
    fest = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"
    bars = v.chart(
        "ChMaterial", top + 1.35, left, w, 3.8,
        [v.S("Volumen", {"Y": "=" + VOLUMEN}, typ="Bar", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE),
             label=v.dlabel(fmt="#,##0.0 m³", size="8.5pt", color=c.TEXT),
             custom_xml=v.custom(PointWidth="0.5", BarLabelStyle="Outside"))],
        [("=" + MATGRUPPE, "=" + VOLUMEN, None)],
        areas=v.area(cat_axes=[v.axis("Primary", interval="1", line=False, size="9pt", extra=fest)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0",
                                      maximum='=Max(Sum(CDbl(Fields!Volumen.Value), "ChMaterial_Cat1"), "ChMaterial") * 1.3')],
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    items += deckel(bars, "ChMaterial_Cat1", VOLUMEN, 9)
    items += etikett("E03_e", top + 5.2, left, w, "D010",
                     "Balken je Materialgruppe (Code.MatArt), Farbe über Code.MatFarbe, höchstens 9 Gruppen")
    return items


# ---------------------------------------------------------------- D020 Ring mit Legende
@b.baustein("D020", "Ring mit Legende")
def d020(top, left, w):
    items = overline("A2", top, left, w, "Räume", "Fläche nach Nutzung")
    schluessel = "%s + %s" % (FLAECHE, NACHRANG)        # gleiche Rangfolge in Ring und Legende
    ring = v.chart(
        "ChRaum", top + 1.35, left - 0.1, 3.8, 3.8,
        [v.S("Flaeche", {"Y": "=" + FLAECHE}, typ="Shape", sub="Doughnut",
             custom_xml=v.custom(DoughnutRadius="30", PieLabelStyle="Disabled", PieStartAngle="270"),
             pstyle="<Color>=Code.Stufe(Fields!Funktion.Value)</Color>" + v.border("#FFFFFF", "Solid", "1.5pt"))],
        [("=Fields!Funktion.Value", "=" + FLAECHE, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        titles=(v.title('=Format(%s, "N0") & " m²"' % FLAECHE,
                        size='=IIf(Len(Format(%s, "N0")) &gt;= 5, "9.5pt", "14pt")' % FLAECHE.replace("&", "&amp;"), color=c.INK, bold=False,
                        extra="<ChartElementPosition><Top>38</Top><Left>10</Left><Height>14</Height><Width>80</Width></ChartElementPosition>")
                + v.title("Raumfläche", size="7.5pt", name="Unter", color=c.MUTED, bold=False,
                          extra="<ChartElementPosition><Top>52</Top><Left>20</Left><Height>9</Height><Width>60</Width></ChartElementPosition>")),
        extra=c.filters(raw(RAUM)))
    ring = deckel(ring, "ChRaum_Cat1", schluessel, MAX_NUTZUNGEN)

    lrow = c.edge(["Bottom"], c.HAIR, "0.5pt")
    name = ('=IIf(Len(CStr(Fields!Funktion.Value & "")) = 0, "ohne Angabe", IIf(Len(Fields!Funktion.Value) > 13, '
            'Left(Fields!Funktion.Value, 12) & "…", Fields!Funktion.Value))')
    cdn = 'CountDistinct(Fields!Funktion.Value, "TbRaum")'
    rest = ('="+ " & (%s - %d) & " weitere · " & %s & " m²"' % (cdn, MAX_NUTZUNGEN, fm(
                'Sum(CDbl(Fields!Flaeche.Value), "TbRaum") - RunningValue(Sum(CDbl(Fields!Flaeche.Value)), Sum, "TbRaum")')))
    cols = [0.35, 1.95, 1.0]
    daten = [c.cell("L1", c.run("■", 9, "=Code.Stufe(Fields!Funktion.Value)"), "Left", pad=(0, 0, 0, 0), border_xml=lrow),
             c.cell("L2", c.run(name, 8, c.TEXT), pad=(0, 1, 2, 1), border_xml=lrow),
             c.cell("L3", c.run("=" + fm(FLAECHE), 8, c.INK, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=lrow)]
    fuss = c.cell("L4", c.run(rest, 7.5, c.MUTED), pad=(0, 1, 0, 1))

    def zeile(h, zellen):
        return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (c.cm(h), zellen)

    z_daten = "".join("<TablixCell><CellContents>%s</CellContents></TablixCell>" % z for z in daten)
    z_fuss = ("<TablixCell><CellContents>%s<ColSpan>3</ColSpan></CellContents></TablixCell><TablixCell/><TablixCell/>" % fuss)
    versteckt = ('=(%s <= %d) Or (RunningValue(Fields!Funktion.Value, CountDistinct, "TbRaum") < %d)'
                 % (cdn, MAX_NUTZUNGEN, MAX_NUTZUNGEN))
    gruppe = ('<TablixMember><Group Name="TbRaum_G"><GroupExpressions><GroupExpression>=Fields!Funktion.Value</GroupExpression></GroupExpressions>%s</Group>'
              "<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression></SortExpressions>"
              "<TablixMembers><TablixMember/><TablixMember><Visibility><Hidden>%s</Hidden></Visibility></TablixMember></TablixMembers></TablixMember>"
              % (c.topn(schluessel, MAX_NUTZUNGEN), c.esc(schluessel), c.esc(versteckt)))
    legende = ('<Tablix Name="TbRaum"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s%s</TablixRows></TablixBody>'
               "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>"
               "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy><DataSetName>AllplanReport</DataSetName>%s"
               "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>"
               % ("".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(x) for x in cols),
                  zeile(0.46, z_daten), zeile(0.42, z_fuss), "<TablixMember/>" * len(cols), gruppe,
                  c.filters(raw(RAUM)), c.cm(0.88), c.cm(sum(cols))))
    items += ring
    items += c.rect("FeldRaum", top + 1.35, left + 3.9, w - 3.9, 3.8, legende)
    items += etikett("E04_e", top + 5.2, left, w, "D020",
                     "TopN 7 in Ring und Legende, Rest als Zeile")
    return items


# ---------------------------------------------------------------- T010 Tabelle mit Zellenbalken
@b.baustein("T010", "Tabelle mit Zellenbalken")
def t010(top, left, w):
    items = overline("A3", top, left, w, "Bauteile", "Bauteile nach Material")
    head = c.edge(["Bottom"], c.INK, "1pt")
    rowb = c.edge(["Bottom"], c.HAIR, "0.75pt")

    def h(name, label, align=None):
        return c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=head, pad=(4, 2, 4, 4))

    gesamt = "Sum(CDbl(Fields!Volumen.Value), \"TbMaterial\")"
    bar = in_cell(v.chart(
        "ChZelle", 0, 0, 1, 1,
        [v.S("V", {"Y": "=" + VOLUMEN}, typ="Bar", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE), custom_xml=v.custom(PointWidth="0.42"))],
        [], nomember=True, dataset=False,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)],
                     val_axes=[v.axis("Primary", visible=False, minimum="0",
                                      maximum="=Max(Sum(CDbl(Fields!Volumen.Value), \"TbMaterial_G\"), \"TbMaterial\")")],
                     pos=(0, 0, 100, 100), inner=(8, 0, 84, 100))))
    cdn = 'CountDistinct(%s, "TbMaterial")' % MATGRUPPE
    mehr = '=IIf(%s > %d, "inkl. " & (%s - %d) & " weitere Materialgruppen", "")' % (cdn, MAX_GRUPPEN, cdn, MAX_GRUPPEN)
    rows = [
        ("kopf", 0.7, [h("H1", "Material"), h("H2", "Gewerk"), h("H3", "Bauteile", "Right"), h("H4", "Fläche", "Right"),
                       h("H5", "Volumen", "Right"), h("H6", ""), h("H7", "Anteil", "Right")]),
        ("daten", 0.68, [
            c.cell("D1", c.run("=" + MATGRUPPE, 9.5, c.INK, c.F_SEMI), border_xml=rowb),
            c.cell("D2", c.run("=Left(First(Fields!Gewerk.Value), 32)", 9, c.MUTED), border_xml=rowb),
            c.cell("D3", c.run("=CountRows()", 9.5, c.TEXT, fmt="N0"), "Right", border_xml=rowb),
            c.cell("D4", c.para([c.run("=" + FLAECHE, 9.5, c.TEXT, fmt="#,##0.0"), c.run(" m²", 8, c.FAINT)]),
                   "Right", border_xml=rowb),
            c.cell("D5", c.para([c.run("=" + VOLUMEN, 9.5, c.INK, c.F_SEMI, fmt="#,##0.0"),
                                 c.run(" m³", 8, c.FAINT)]), "Right", border_xml=rowb),
            c.rect("D6", None, 0, 0, 0, bar, border_xml=rowb),
            c.cell("D7", c.run("=%s / %s" % (VOLUMEN, gesamt), 9.5, c.TEXT, fmt="0 %"), "Right",
                   border_xml=rowb),
        ]),
        ("fuss", 0.75, [
            c.cell("F1", c.run("Summe", 9.5, c.INK, c.F_SEMI)), c.cell("F2", c.run(mehr, 8, c.MUTED)),
            c.cell("F3", c.run("=CountRows()", 9.5, c.INK, c.F_SEMI, fmt="N0"), "Right"),
            c.cell("F4", c.para([c.run("=" + FLAECHE, 9.5, c.INK, c.F_SEMI, fmt="#,##0.0"),
                                 c.run(" m²", 8, c.FAINT)]), "Right"),
            c.cell("F5", c.para([c.run("=" + VOLUMEN, 9.5, c.INK, c.F_SEMI, fmt="#,##0.0"),
                                 c.run(" m³", 8, c.FAINT)]), "Right"),
            c.cell("F6", c.run("", 9)), c.cell("F7", c.run("100 %", 9.5, c.INK, c.F_SEMI), "Right"),
        ]),
    ]
    tabelle = c.tablix("TbMaterial", 0, 0, [3.4, 5.2, 1.6, 2.2, 2.2, 2.2, 1.2], rows,
                       group="=" + MATGRUPPE, sort="=" + VOLUMEN, sort_desc=True,
                       filter_expr=raw(MIT_MATERIAL))
    tabelle = deckel(tabelle, "TbMaterial_G", VOLUMEN, MAX_GRUPPEN)
    items += c.rect("FeldMaterial", top + 1.3, left, w, 4.85, tabelle)
    items += etikett("E05_e", top + 6.2, left, w, "T010",
                     "Tablix je Materialgruppe, TopN 5, Balken-Diagramm in der Zelle; die Summe zählt alle Gruppen")
    return items


# ---------------------------------------------------------------- M010 Kennwert-Balken
def _kennwert(name, top, left, w, label, note, anteil, gueltig, farbe):
    """Wie bausteine.kennwert, aber ohne Grundlage (gueltig falsch) steht "-" statt einer Scheinzahl."""
    wert = 'IIf(%s, Format(%s, "0 %%"), "–")' % (gueltig, anteil)
    return (c.text(name + "_l", top, left, w - 2.2, 0.42, c.run(label, 9.5, c.INK, c.F_SEMI))
            + c.text(name + "_n", top + 0.47, left, w - 2.2, 0.36, c.run(note, 7.5, c.MUTED))
            + c.text(name + "_v", top, left + w - 2.2, 2.2, 0.83, c.run("=" + wert, 17, c.INK, c.F_LIGHT),
                     align="Right", valign="Bottom")
            + fortschritt(name + "_b", top + 0.95, left, w, "IIf(%s, %s, 0.0)" % (gueltig, anteil), farbe))


@b.baustein("M010", "Kennwert-Balken")
def m010(top, left, w):
    items = overline("A4", top, left, w, "Kennwerte", "Anteile im Gebäude")
    verkehr = summe("Flaeche", "(%s And %s)" % (RAUM, IST_VERKEHR))
    y = top + 1.4
    items += _kennwert("W1", y, left, w, "Fensterflächenanteil", "Glasfläche zu Außenwandfläche", ANTEIL, FENSTER_OK, c.BLUE)
    items += _kennwert("W2", y + 1.3, left, w, "Verkehrsfläche", "Flure zu gesamter Raumfläche",
                       quote(verkehr, RAUM_FL), "%s > 0" % RAUM_FL, c.ORANGE)
    items += _kennwert("W3", y + 2.6, left, w, "Betonanteil", "am Bauteilvolumen",
                       quote(BETON_VOL, ROHBAU_VOL), "%s > 0" % ROHBAU_VOL, "#475569")
    items += etikett("E06_e", top + 5.2, left, w, "M010",
                     "Prozent mit Balken; ohne Grundlage steht –")
    return items


# ---------------------------------------------------------------- B010 Bildkarten
@b.baustein("B010", "Bildkarten")
def b010(top, left, w):
    bedingung = raw("(%s Or %s)" % (FENSTER, TUER))
    typen = 'CountDistinct(IIf(%s, Fields!Bezeichnung.Value, Nothing))' % bedingung
    items = overline("A5", top, left, w, "Aus dem Modell", "Fenster und Türen")
    items = items.replace("<Value>Fenster und Türen</Value>",
                          '<Value>=IIf(%s > %d, "Die %d häufigsten Typen", "Fenster und Türen")</Value>' % (c.esc(typen), MAX_KARTEN, MAX_KARTEN), 1)
    haeufigkeit = "Count(Fields!Nr.Value) + " + NACHRANG      # Karten nach Anzahl absteigend, gleiche Anzahl: kleinere Nr zuerst
    kk = karten("Karten", top + 1.4, left, w, 2.0, 0.2, bedingung, "Fields!Bezeichnung.Value",
                'IIf(%s, "Fenster", "Tür")' % ("Val(First(Fields!ObjNr.Value))=991"), sortierung=haeufigkeit)
    kk = kk.replace("<Value>=Fields!Bezeichnung.Value</Value>",
                    "<Value>=IIf(InStr(Fields!Bezeichnung.Value, \" \") = 0, IIf(Len(Fields!Bezeichnung.Value) &gt; 13, Left(Fields!Bezeichnung.Value, 12) &amp; \"…\", Fields!Bezeichnung.Value), "
                    "IIf(Len(Fields!Bezeichnung.Value) &gt; 24, Left(Fields!Bezeichnung.Value, 23) &amp; \"…\", Fields!Bezeichnung.Value))</Value>", 1)
    kk = deckel(kk, "Karten_G", haeufigkeit, MAX_KARTEN)
    items += kk
    items += etikett("E07_e", top + 5.2, left, w, "B010",
                     "Karte je Typ mit Bild aus Allplan, TopN 5 nach Häufigkeit (häufigster zuerst), Klick zoomt aufs Bauteil")
    return items


# ---------------------------------------------------------------- Seite
def seite():
    x0, w = c.INSET, c.CONTENT_W
    items = band()
    items += k010(4.7, x0, w)
    items += k020(6.55, x0, w)
    lw, rw = 10.4, 7.2
    items += d010(9.85, x0, lw)
    items += d020(9.85, x0 + lw + 0.4, rw)
    items += t010(15.75, x0, w)
    kwid = 6.6
    items += m010(22.65, x0, kwid)
    items += b010(22.65, x0 + kwid + 0.6, w - kwid - 0.6)
    return items
