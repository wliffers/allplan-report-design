# -*- coding: utf-8 -*-
"""Seite 3 - Diagramme: Anteile und Zusammenhaenge.

Sechs Schaustuecke im Zwei-Spalten-Raster: Ring mit Zahl in der Mitte, Torte mit Fuehrungslinien,
Trichter, TreeMap, Punktwolke und Blasendiagramm.

Datenfest: Bauteilart ueber die Objektnummer (b.ART), Material ueber die Materialgruppe (b.MATGRUPPE, Farbe
b.MAT_FARBE), jedes Diagramm mit Deckel (TopN) und Legenden aus den tatsaechlich vorkommenden Gruppen."""
import core as c
import viz as v
import bausteine as b
from bausteine import (FENSTER, TUER, MIT_MATERIAL, MAT_FARBE, MATGRUPPE, ART, ist, raw, overline, seitenkopf,
                       etikett)
from s02_vergleichen import gruppenlegende, gruppe_filter, zahl, MATGRUPPE_ERSTE, TEXT_AUF_GRUPPE

FEST = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"
VOL = "Sum(CDbl(Fields!Volumen.Value))"
FLAE = "Sum(CDbl(Fields!Flaeche.Value))"
OEFFNUNG = "(%s Or %s)" % (FENSTER, TUER)
OEFFNUNG_MASS = "(%s And CDbl(Fields!Laenge.Value) > 0 And CDbl(Fields!Hoehe.Value) > 0)" % OEFFNUNG
OEFF_ART = 'IIf(%s, "Fenster", "Tür")' % ist(991)
DY = 1.45       # Inhalt unter dem Abschnittskopf
DH = 5.7        # Hoehe des Diagramms
DE = 7.25       # Etikett unter dem Schaustueck


def stufe(n=5):
    """Blaustufe nach Rang der Bauteilart (Zeile 1 = dunkelste). Passt zur benutzerdefinierten Palette des Rings."""
    rang = "RunningValue(%s, CountDistinct, Nothing)" % ART
    return "=Choose(%s, %s)" % (rang, ", ".join('"%s"' % f for f in c.RAMP[:n]))


def titel_mitte(name, gross, klein, ziffern=None):
    """Zahl in der Mitte des Rings; ziffern: Ausdruck der Zahl als Text - ab fuenf Zeichen wird die Schrift kleiner, damit sie ins Loch passt."""
    groesse = "15pt" if ziffern is None else ('=IIf(Len(%s) &gt;= 8, "9pt", IIf(Len(%s) &gt;= 5, "11pt", "15pt"))' % (ziffern, ziffern))
    return (v.title(gross, size=groesse, color=c.INK, font=c.F_ZAHL, name=name,
                    extra="<ChartElementPosition><Top>38</Top><Left>20</Left><Height>14</Height><Width>60</Width></ChartElementPosition>")
            + v.title(klein, size="7.5pt", name=name + "u", color=c.MUTED, bold=False,
                      extra="<ChartElementPosition><Top>52</Top><Left>20</Left><Height>9</Height><Width>60</Width></ChartElementPosition>"))


# ------------------------------------------------------------ D090 Ring mit Zahl in der Mitte + Legende
@b.baustein("D090", "Volumen nach Bauteilart")
def d090(top, left, w):
    # Die Bauteile kennen genau fuenf Bauteilarten (Wand, Stuetze, Decke, Unterzug, Bodenplatte): der Deckel ergibt sich daraus.
    items = overline("S3_A1", top, left, w, "Anteile", "Volumen nach Bauteilart")
    ring = v.chart(
        "S3_ChRing", top + DY + 0.7, left - 0.1, 4.5, 4.5,
        [v.S("Vol", {"Y": "=" + VOL}, typ="Shape", sub="Doughnut",
             custom_xml=v.custom(DoughnutRadius="32", PieLabelStyle="Disabled", PieStartAngle="270"),
             pstyle=v.border(c.WHITE, "Solid", "1.5pt"))],
        [("=" + ART, "=" + VOL, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        titles=titel_mitte("Mitte", '=Format(%s, "N0") & " m³"' % VOL, "Bauteilvolumen", 'Format(%s, "N0")' % VOL),
        palette="Custom", custom_palette=c.RAMP[:5], extra=c.filters(raw(MIT_MATERIAL)))
    lrow = c.edge(["Bottom"], c.HAIR, "0.5pt")
    gesamt = 'Sum(CDbl(Fields!Volumen.Value), "S3_TbRing")'
    kopf = c.edge(["Bottom"], c.INK, "0.75pt")
    legende = c.tablix("S3_TbRing", 0, 0, [0.45, 1.95, 1.0, 1.0], [
        ("kopf", 0.5, [
            c.cell("S3_LH1", c.run("", 7), border_xml=kopf),
            c.cell("S3_LH2", c.run("ART", 7, c.MUTED, c.F_SEMI), pad=(0, 1, 2, 1), border_xml=kopf),
            c.cell("S3_LH3", c.run("M³", 7, c.MUTED, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=kopf),
            c.cell("S3_LH4", c.run("ANTEIL", 7, c.MUTED, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=kopf),
        ]),
        ("daten", 0.62, [
            c.cell("S3_L1", c.run("■", 10, stufe(), b.SYMBOL), "Left", pad=(0, 0, 0, 0), border_xml=lrow),
            c.cell("S3_L2", c.run("=" + ART, 8.5, c.TEXT), pad=(0, 1, 2, 1), border_xml=lrow),
            c.cell("S3_L3", c.run("=" + zahl(VOL), 8.5, c.INK, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=lrow),
            c.cell("S3_L4", c.run("=%s / %s" % (VOL, gesamt), 8.5, c.TEXT, fmt="0 %"), "Right", pad=(0, 1, 0, 1), border_xml=lrow),
        ])], group="=" + ART, sort="=" + VOL, sort_desc=True, filter_expr=raw(MIT_MATERIAL))
    items += ring
    items += c.rect("S3_FeldRing", top + DY + 1.1, left + 4.5, 4.4, 3.9, legende)
    return items + etikett("S3_E1", top + DE, left, w, "D090", "Ring mit Zahl in der Mitte, eigene Legende mit Wert und Anteil")


# ------------------------------------------------------------ D100 Torte mit eigener Legende
@b.baustein("D100", "Fläche nach Typ")
def d100(top, left, w):
    name = '%s & " " & Replace(Fields!Bezeichnung.Value, "1flg ", "")' % OEFF_ART
    typen = "CountDistinct(IIf(%s, %s, Nothing))" % (OEFFNUNG, name)
    items = overline("S3_A2", top, left, w, "Öffnungen", b.rang_titel(typen, 5, "Fläche der ", " größten Typen", "Fläche des größten Typs",
                                                                      "Fläche der größten Typen"))
    torte = v.chart(
        "S3_ChTorte", top + DY + 0.7, left - 0.1, 4.3, 4.3,
        [v.S("Flaeche", {"Y": "=" + FLAE}, typ="Shape", sub="Pie",
             custom_xml=v.custom(PieLabelStyle="Disabled", PieStartAngle="250"),
             pstyle=v.border(c.WHITE, "Solid", "1.5pt"))],
        [("=" + name, "=" + FLAE, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        palette="Custom", custom_palette=c.RAMP[:5], extra=c.filters(raw(OEFFNUNG)))
    torte = gruppe_filter(torte, c.topn(FLAE, 5))
    # Legende statt Beschriftung am Rand: nichts kann sich ueberlappen; Anteil bezieht sich auf die 5 gezeigten Typen (wie die Torte)
    lrow = c.edge(["Bottom"], c.HAIR, "0.5pt")
    kopf = c.edge(["Bottom"], c.INK, "0.75pt")
    fest = name.replace('" "', "Chr(160)")   # Art und Typ nicht am Leerzeichen umbrechen
    kurz = 'IIf(Len(%s) > 16, Left(%s, 15) & "…", %s)' % (fest, fest, fest)   # 16 Zeichen passen sicher in eine Zeile
    gesamt = 'Sum(Sum(CDbl(Fields!Flaeche.Value), "S3_TbTorte_G"), "S3_TbTorte")'
    farbe = '=Choose(RunningValue(%s, CountDistinct, "S3_TbTorte"), %s)' % (
        name, ", ".join('"%s"' % f for f in c.RAMP[:5]))
    legende = c.tablix("S3_TbTorte", 0, 0, [0.3, 2.4, 0.9, 1.0], [
        ("kopf", 0.5, [
            c.cell("S3_TH1", c.run("", 7), border_xml=kopf),
            c.cell("S3_TH2", c.run("TYP", 7, c.MUTED, c.F_SEMI), pad=(0, 1, 2, 1), border_xml=kopf),
            c.cell("S3_TH3", c.run("M²", 7, c.MUTED, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=kopf),
            c.cell("S3_TH4", c.run("ANTEIL", 7, c.MUTED, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=kopf),
        ]),
        ("daten", 0.62, [
            c.cell("S3_T1", c.run("■", 10, farbe, b.SYMBOL), "Left", pad=(0, 0, 0, 0), border_xml=lrow),
            c.cell("S3_T2", c.run("=" + kurz, 7, c.TEXT), pad=(3, 1, 2, 1), border_xml=lrow),
            c.cell("S3_T3", c.run("=" + zahl(FLAE), 7, c.INK, c.F_SEMI), "Right", pad=(0, 1, 0, 1), border_xml=lrow),
            c.cell("S3_T4", c.run("=%s / %s" % (FLAE, gesamt), 7, c.TEXT, fmt="0 %"), "Right", pad=(0, 1, 0, 1),
                   border_xml=lrow),
        ])], group="=" + name, sort="=" + FLAE, sort_desc=True, filter_expr=raw(OEFFNUNG))
    items += torte
    items += c.rect("S3_FeldTorte", top + DY + 1.1, left + 4.2, 4.6, 3.9, gruppe_filter(legende, c.topn(FLAE, 5)))
    return items + etikett("S3_E2", top + DE, left, w, "D100", "Torte Top 5 Typen, Legende: Anteil an den 5 gezeigten (= 100 %)")


# ------------------------------------------------------------ D110 Trichter
@b.baustein("D110", "Volumen nach Material")
def d110(top, left, w):
    items = overline("S3_A3", top, left, w, "Rangfolge", "Volumen nach Material")
    trichter = v.chart(
        "S3_ChTrichter", top + DY, left, w, DH,
        [v.S("Vol", {"Y": "=" + VOL}, typ="Shape", sub="Pyramid",
             label=v.dlabel(position="Auto", fmt="N1", size="8pt", color=c.TEXT,
                            label='=%s & "   " & %s & " m³"' % (MATGRUPPE_ERSTE, zahl(VOL))),
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE) + v.border(c.WHITE, "Solid", "1.5pt"),
             custom_xml=v.custom(PyramidLabelStyle="OutsideInColumn", PyramidPointGap="1", PyramidMinPointHeight="3",
                                 Pyramid3DRotationAngle="0", PyramidValueType="Surface",
                                 CalloutLineColor=c.HAIR_STARK))],
        [("=" + MATGRUPPE, "=" + VOL, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    items += gruppe_filter(trichter, c.topn(VOL, 6))
    return items + etikett("S3_E3", top + DE, left, w, "D110", "Pyramide Top 6 Materialgruppen, Fläche = Volumen, Materialfarben")


# ------------------------------------------------------------ D120 TreeMap
@b.baustein("D120", "Volumen nach Bauteil und Material")
def d120(top, left, w):
    items = overline("S3_A4", top, left, w, "Gliederung", "Volumen nach Bauteil und Material")
    feld = '%s & "|" & %s' % (ART, MATGRUPPE)
    anteil = '%s / Sum(CDbl(Fields!Volumen.Value), "S3_ChSun")' % VOL
    text = ('=IIf(%s < 0.07, "", Code.Art(First(Fields!ObjNr.Value)) & Chr(10) & %s & Chr(10) & %s & " m³")'
            % (anteil, MATGRUPPE_ERSTE, zahl(VOL)))
    items += gruppenlegende("S3_SunLeg", top + 1.3, left, w, MIT_MATERIAL)
    sun = v.chart(
        "S3_ChSun", top + 1.8, left, w, 5.2,
        [v.S("Vol", {"Y": "=" + VOL}, typ="Shape", sub="TreeMap",
             label=v.dlabel(fmt="N0", size="7.5pt", color=c.esc(TEXT_AUF_GRUPPE), label=text),
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE) + v.border(c.WHITE, "Solid", "1pt"))],
        [("=" + feld, "=" + VOL, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    items += gruppe_filter(sun, c.topn(VOL, 10))
    return items + etikett("S3_E4", top + DE, left, w, "D120", "TreeMap Top 10 Felder (Bauteil + Material), Fläche = Volumen")


# ------------------------------------------------------------ D130 Punktwolke
@b.baustein("D130", "Fläche gegen Volumen")
def d130(top, left, w):
    items = overline("S3_A5", top, left, w, "Zusammenhang", "Fläche gegen Volumen")
    items += gruppenlegende("S3_PktLeg", top + 1.3, left, w, MIT_MATERIAL)
    bedingung = "(%s And CDbl(Fields!Flaeche.Value) > 0 And CDbl(Fields!Volumen.Value) > 0)" % MIT_MATERIAL
    pt = v.chart(
        "S3_ChPunkte", top + 1.8, left, w, 5.2,
        [v.S("Punkte", {"X": "=" + FLAE, "Y": "=" + VOL}, typ="Scatter", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE),
             mark=v.marker("Circle", "5pt", c.esc(MAT_FARBE), c.WHITE))],
        [("=Fields!Nr.Value", "=Fields!Nr.Value", None)],
        areas=v.area(
            cat_axes=[v.axis("Primary", line=True, size="7.5pt", fmt="#,##0.##", grid=True, gridcolor=c.HAIR,
                             extra=FEST, log=True, title="Fläche in m²", title_size="7.5pt")],
            val_axes=[v.axis("Primary", line=False, size="7.5pt", fmt="#,##0.##", grid=True, gridcolor=c.HAIR, extra=FEST,
                             log=True, title="Volumen in m³", title_size="7.5pt")],
            pos=(0, 0, 100, 100)),
        extra=c.filters(raw(bedingung)))
    items += pt
    return items + etikett("S3_E5", top + DE, left, w, "D130", "Punktwolke je Bauteil, Farbe nach Materialgruppe, Achsen logarithmisch")


# ------------------------------------------------------------ D140 Blasendiagramm
@b.baustein("D140", "Öffnungen: Breite, Höhe, Anzahl")
def d140(top, left, w):
    items = overline("S3_A6", top, left, w, "Formate", "Öffnungen: Breite, Höhe, Anzahl")
    items += c.text("S3_BlLeg", top + 1.3, left, w, 0.42,
                    c.para([c.run("■ ", 9, c.BLUE, b.SYMBOL), c.run("Fenster      ", 7.5, c.MUTED),
                            c.run("■ ", 9, c.SERIE[3], b.SYMBOL), c.run("Tür      ", 7.5, c.MUTED),
                            c.run("Größe der Blase = Anzahl", 7.5, c.FAINT)]))
    # Format = Art + Breite + Hoehe in ganzen cm; die 12 haeufigsten. Keine Beschriftung an den Blasen:
    # Blasen duerfen sich ueberdecken, Texte nie - die Anzahl steht in der Blasengroesse.
    format_ = '%s & "|" & CStr(Round(CDbl(Fields!Laenge.Value) * 100)) & "|" & CStr(Round(CDbl(Fields!Hoehe.Value) * 100))' % OEFF_ART
    anzahl = "Count(Fields!Nr.Value)"
    bubbles = v.chart(
        "S3_ChBlasen", top + 1.8, left, w, 5.2,
        [v.S("Blasen", {"X": "=Max(CDbl(Fields!Laenge.Value))", "Y": "=Max(CDbl(Fields!Hoehe.Value))", "Size": "=" + anzahl},
             typ="Scatter", sub="Bubble",
             label=v.dlabel(visible=False),
             pstyle="<Color>=IIf(Val(Max(Fields!ObjNr.Value))=991, \"%s\", \"%s\")</Color>" % (c.BLUE, c.SERIE[3]),
             mark=v.marker("Circle", "10pt", None, c.WHITE),
             custom_xml=v.custom(BubbleMaxSize="14"))],
        [("=" + format_, "=" + anzahl, "Descending")],
        areas=v.area(
            cat_axes=[v.axis("Primary", size="7.5pt", fmt="0.0", extra=FEST, minimum="=0",
                             title="Breite in m", title_size="7.5pt")],
            val_axes=[v.axis("Primary", line=False, size="7.5pt", fmt="0.0", grid=True, gridcolor=c.HAIR, extra=FEST,
                             minimum="=0", title="Höhe in m", title_size="7.5pt")],
            pos=(0, 0, 100, 100)),
        extra=c.filters(raw(OEFFNUNG_MASS)))
    items += gruppe_filter(bubbles, c.topn(anzahl, 12))
    return items + etikett("S3_E6", top + DE, left, w, "D140", "Blasen je Format (12 häufigste), Größe = Anzahl, ohne Beschriftung")


TITEL = "Diagramme: Anteile und Zusammenhänge"   # Name der Seite in der Dokumentstruktur (PDF-Lesezeichen)


def seite():
    x0, w = c.INSET, 8.8
    xr = x0 + w + 0.4
    items = seitenkopf(3, "Diagramme: Anteile und Zusammenhänge", "Ring, Torte, Pyramide, Kacheln, Punkte")
    for top, links, rechts in ((3.3, d090, d100), (11.8, d110, d120), (20.3, d130, d140)):
        items += links(top, x0, w) + rechts(top, xr, w)
    return items
