# -*- coding: utf-8 -*-
"""Seite 2 - Diagramme: Vergleichen. Saeulen, Balken-Rangliste, gestapelte Saeulen, 100-%-Balken,
Pareto mit zweiter Achse und gruppierte Saeulen - sechs Schaustuecke im Zwei-Spalten-Raster."""
import re

import core as c
import viz as v
import bausteine as b
from bausteine import (WAND, FENSTER, TUER, MIT_MATERIAL, MAT_FARBE, MATGRUPPE, ART, raw, overline, etikett,
                       seitenkopf)

FEST = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"
VOL = "Sum(CDbl(Fields!Volumen.Value))"
# Datenfest: Bauteilart ueber die Objektnummer, Material ueber die Materialgruppe (kein Projektname im Ausdruck).
ART_LABEL = '=Replace(Code.Art(First(Fields!ObjNr.Value)), "Bodenplatte", "Boden-" & Chr(10) & "platte")'
MATGRUPPE_ERSTE = "Code.MatArt(First(Fields!Material.Value))"
WAND_MIT_MATERIAL = '(%s And Fields!Material.Value <> "")' % WAND
# Gruppen mit dunkler Farbe: Beschriftung im Segment weiss, sonst dunkel
TEXT_AUF_GRUPPE = ('=IIf(InStr("|Beton|Mauerwerk|Holz|Stahl|Naturstein|", "|" & %s & "|") > 0, "%s", "%s")'
                   % (MATGRUPPE_ERSTE, c.WHITE, c.INK))
MAX_GRUPPEN = 5   # Deckel fuer Materialgruppen in Stapeln und Legenden
D02_NAME = 32     # laengster Name in der Rangliste D040 (Zeichen); der Rest bekommt "…"


# ---------------------------------------------------------------- Hilfen dieser Seite
def kategorie_achse(**kw):
    """Kategorieachse mit feiner Grundlinie in Faint statt der Standardlinie."""
    return v.axis("Primary", extra=FEST, **kw).replace("#9CA3AF", c.HAIR, 1)


def wert_achse(maximum):
    return v.axis("Primary", visible=False, line=False, minimum="0", maximum=maximum)


def gruppe_filter(chart_xml, filter_xml):
    """Filter an die (einzige) Kategoriegruppe eines Diagramms haengen, z. B. Top-N."""
    return chart_xml.replace("</GroupExpressions></Group>", "</GroupExpressions>" + filter_xml + "</Group>", 1)


def kategorie_label(chart_xml, alt, neu):
    """Beschriftung der Kategoriegruppe durch einen eigenen Ausdruck ersetzen."""
    return chart_xml.replace("<Label>%s</Label>" % c.esc(alt), "<Label>%s</Label>" % c.esc(neu), 1)


def zahl(ausdruck, ab=100):
    """Zahl als Text: ab 100 ohne Nachkommastelle (31.540), darunter mit einer (92,7)."""
    return 'Format(%s, IIf(%s >= %d, "N0", "N1"))' % (ausdruck, ausdruck, ab)


def serien_nach_material(chart_xml, name, n=MAX_GRUPPEN, summe=False):
    """Serien dynamisch nach Materialgruppe (groesste zuerst = unten), hoechstens n; optional statische Serie "Summe"."""
    wert = c.esc("=" + VOL)
    neu = ('<ChartSeriesHierarchy><ChartMembers><ChartMember><Group Name="%s_Ser"><GroupExpressions><GroupExpression>=%s'
           '</GroupExpression></GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>%s</Value>'
           '<Direction>Descending</Direction></SortExpression></SortExpressions><Label>=%s</Label></ChartMember>%s'
           '</ChartMembers></ChartSeriesHierarchy>'
           % (name, c.esc(MATGRUPPE), c.topn(VOL, n), wert, c.esc(MATGRUPPE),
              "<ChartMember><Label>Summe</Label></ChartMember>" if summe else ""))
    return re.sub(r"<ChartSeriesHierarchy>.*?</ChartSeriesHierarchy>", lambda m: neu, chart_xml, count=1, flags=re.S)


def gruppenlegende(name, top, left, w, bedingung, n=MAX_GRUPPEN):
    """Legende aus den tatsaechlich vorkommenden Materialgruppen (groesste zuerst, hoechstens n): je Gruppe eine Spalte."""
    spalte = 1.7
    zelle = c.cell(name + "_z", c.para([c.run("■ ", 8, MAT_FARBE),
                                        c.run("=" + MATGRUPPE_ERSTE, 7.5, c.MUTED)]), valign="Top", pad=(0, 0, 0, 0))
    xml = ('<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
           "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
           "</TablixCells></TablixRow></TablixRows></TablixBody>" % (name + "_t", c.cm(spalte), c.cm(0.42), zelle))
    xml += ('<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="%s_G"><GroupExpressions><GroupExpression>=%s'
            "</GroupExpression></GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>=%s</Value>"
            "<Direction>Descending</Direction></SortExpression></SortExpressions></TablixMember></TablixMembers>"
            "</TablixColumnHierarchy>" % (name + "_t", c.esc(MATGRUPPE), c.topn(VOL, n), c.esc(VOL)))
    xml += "<TablixRowHierarchy><TablixMembers><TablixMember><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember></TablixMembers></TablixRowHierarchy>"
    xml += "<DataSetName>AllplanReport</DataSetName>" + c.filters(bedingung)
    xml += "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>" % (
        c.cm(0.42), c.cm(spalte * n))
    return c.rect(name, top, left, w, 0.42, xml)


def legende(name, top, left, w, eintraege):
    """Eigene Mini-Legende: farbiges Quadrat + Name je Eintrag, rechtsbuendig in einer Textbox."""
    runs = []
    for i, (farbe, text) in enumerate(eintraege):
        runs.append(c.run("■ ", 8, farbe))
        runs.append(c.run(text + ("      " if i < len(eintraege) - 1 else ""), 7.5, c.MUTED))
    return c.text(name, top, left, w, 0.42, c.para(runs, "Right"))


def statische_kategorien(chart_xml, namen):
    """Kategorieachse aus festen Eintraegen statt aus einer Datengruppe (je Serie ein Punkt je Eintrag)."""
    alt = "<ChartCategoryHierarchy><ChartMembers><ChartMember><Label>1</Label></ChartMember></ChartMembers></ChartCategoryHierarchy>"
    neu = "<ChartCategoryHierarchy><ChartMembers>%s</ChartMembers></ChartCategoryHierarchy>" % "".join(
        "<ChartMember><Label>%s</Label></ChartMember>" % c.esc(n) for n in namen)
    return chart_xml.replace(alt, neu, 1)


def serie_mit_punkten(name, punkte, **kw):
    """Eine Serie mit mehreren Datenpunkten. punkte: Liste (y_ausdruck, label_xml)."""
    teile = [v.S(name, {"Y": y}, label=lab, **kw) for y, lab in punkte]
    alle = "".join(re.search(r"<ChartDataPoint>.*?</ChartDataPoint>", t, re.S).group(0) for t in teile[1:])
    return teile[0].replace("</ChartDataPoints>", alle + "</ChartDataPoints>", 1)


# ---------------------------------------------------------------- Schaustuecke
def _d01(top, x, w, h):
    """Saeulen mit Direktbeschriftung: Flaeche je Bauteilart (Art aus der Objektnummer, hoechstens 6)."""
    flaeche = "Sum(CDbl(Fields!Flaeche.Value))"
    xml = v.chart(
        "S2_D01", top, x, w, h,
        [v.S("Flaeche", {"Y": "=" + flaeche}, typ="Column", sub="Plain", color=c.BLUE,
             label=v.dlabel(fmt="#,##0 m²", size="8.5pt", color=c.TEXT),
             custom_xml=v.custom(PointWidth="0.55", BarLabelStyle="Outside"))],
        [("=" + ART, "=" + flaeche, "Descending")],
        areas=v.area(cat_axes=[kategorie_achse(interval="1", size="7.5pt")],
                     val_axes=[wert_achse('=Max(Sum(CDbl(Fields!Flaeche.Value), "S2_D01_Cat1"), "S2_D01") * 1.2')],
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    xml = gruppe_filter(xml, c.topn(flaeche, 6))
    return kategorie_label(xml, "=" + ART, ART_LABEL)


def _d02(top, x, w, h, n=8):
    """Balken-Rangliste: die n groessten Bauteile nach Volumen, Wert am Balken."""
    voll = ('Code.Art(First(Fields!ObjNr.Value)) & " · " & %s & '
            'IIf(Val(First(Fields!ObjNr.Value)) = 1, " · " & Format(CDbl(First(Fields!Laenge.Value)), "N1") & " m", '
            '" · " & Format(CDbl(First(Fields!Flaeche.Value)), "N0") & " m²")' % MATGRUPPE_ERSTE)
    label = '=IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (voll, D02_NAME, voll, D02_NAME - 1, voll)   # lange Namen mit "…" kuerzen
    xml = v.chart(
        "S2_D02", top, x, w, h,
        [v.S("Volumen", {"Y": "=" + VOL}, typ="Bar", sub="Plain", pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE),
             label=v.dlabel(size="8pt", color=c.TEXT, label='=%s & " m³"' % zahl(VOL, 100)),
             custom_xml=v.custom(PointWidth="0.6", BarLabelStyle="Outside"))],
        [("=Fields!Nr.Value", "=" + VOL, None)],
        areas=v.area(cat_axes=[kategorie_achse(interval="1", size="8pt")],
                     val_axes=[wert_achse('=Max(Sum(CDbl(Fields!Volumen.Value), "S2_D02_Cat1"), "S2_D02") * 1.7')],   # Reserve: der Wert steht immer rechts ausserhalb
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    return kategorie_label(gruppe_filter(xml, c.topn(VOL, n)), "=Fields!Nr.Value", label)


def _d03(top, x, w, h):
    """Gestapelte Saeulen in Materialfarben, Summe ueber der Saeule: Volumen je Bauteilart.
    Serien = Materialgruppen, wie sie im Projekt vorkommen (hoechstens 5)."""
    anteil = 'IIf(%s / Max(Sum(CDbl(Fields!Volumen.Value), "S2_D03_Cat1"), "S2_D03") < 0.07, "", %s)'
    lab = v.dlabel("Center", fmt="N0", size="7.5pt", color=c.esc(TEXT_AUF_GRUPPE),
                   label="=" + anteil % (VOL, 'Format(%s, "N0")' % VOL))
    summe = v.dlabel("Top", fmt="N1", size="8pt", color=c.INK, bold=True,
                     label='=%s & " m³"' % zahl(VOL))
    serien = [v.S("Material", {"Y": "=" + VOL}, typ="Column", sub="Stacked", pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE),
                  label=lab, custom_xml=v.custom(PointWidth="0.55")),
              v.S("Summe", {"Y": "=" + VOL}, typ="Line", sub="Plain", label=summe,
                  pstyle="<Border><Style>None</Style></Border>")]
    xml = v.chart(
        "S2_D03", top, x, w, h, serien,
        [("=" + ART, "=" + VOL, "Descending")], names=["Material", "Summe"],
        areas=v.area(cat_axes=[kategorie_achse(interval="1", size="7.5pt")],
                     val_axes=[wert_achse('=Max(Sum(CDbl(Fields!Volumen.Value), "S2_D03_Cat1"), "S2_D03") * 1.2')],
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw(MIT_MATERIAL)))
    xml = serien_nach_material(xml, "S2_D03", summe=True)
    xml = gruppe_filter(xml, c.topn(VOL, 6))
    return kategorie_label(xml, "=" + ART, ART_LABEL)


def _d04(top, x, w, h):
    """100-%-Stapelbalken: Materialanteile der Wandschichten nach Anzahl, Laenge, Flaeche und Volumen (Materialgruppen)."""
    masse = [("Anzahl", "1"), ("Länge", "CDbl(Fields!Laenge.Value)"), ("Fläche", "CDbl(Fields!Flaeche.Value)"),
             ("Volumen", "CDbl(Fields!Volumen.Value)")]
    punkte = []
    for _, m in masse:
        y = "Sum(%s)" % m
        gesamt = 'Sum(%s, "S2_D04")' % m
        lab = v.dlabel("Center", fmt="0 %", size="7.5pt", color=c.esc(TEXT_AUF_GRUPPE),
                       label='=IIf(%s / %s < 0.06, "", Format(%s / %s, "0 %%"))' % (y, gesamt, y, gesamt))
        punkte.append(("=" + y, lab))
    serie = serie_mit_punkten("Material", punkte, typ="Bar", sub="PercentStacked",
                              pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE), custom_xml=v.custom(PointWidth="0.62"))
    xml = v.chart(
        "S2_D04", top, x, w, h, [serie], [], nomember=True, names=["Material"],
        areas=v.area(cat_axes=[kategorie_achse(reverse=True, size="8pt", interval="1")],
                     val_axes=[v.axis("Primary", visible=False, line=False)], pos=(0, 0, 100, 100)),
        extra=c.filters(raw(WAND_MIT_MATERIAL)))
    xml = serien_nach_material(xml, "S2_D04")
    return statische_kategorien(xml, [n for n, _ in masse])


def _d05(top, x, w, h, n=8):
    """Pareto: die n groessten Wandaufbauten (Materialgruppe + Dicke) nach Volumen, Saeule + kumulierter Anteil an der
    Gesamtsumme aller Wandschichten auf zweiter Achse, 80-%-Marke. Die Saeulen haben eine eigene Achse bis zur groessten
    Saeule (sie belegen das untere Drittel), die Linie steht auf der Prozent-Achse darueber: bei vielen kleinen Aufbauten
    (je 1 %) bleiben die Saeulen lesbar, und die Linie liegt nie auf den Saeulen."""
    gruppe = '=%s & "|" & CStr(Round(CDbl(Fields!Dicke.Value) * 1000))' % MATGRUPPE
    # "Beton" + geschuetztes Leerzeichen: im Deutschen unsichtbar, im Englischen ein eigener Schluessel fuer die Kurzform
    kurz = ('Replace(Replace(Replace(Replace(Replace(%s, "Mauerwerk", "Mauer"), "Dämmung", "Dämm."), "Gipskarton", "Gipsk."), '
            '"Naturstein", "Naturst."), "Beton", "Beton ")' % MATGRUPPE_ERSTE)
    label = ('=%s & Chr(10) & Format(CDbl(First(Fields!Dicke.Value)) * 100, "0.#") & " cm" & Chr(10) & %s & " m³"'
             % (kurz, zahl(VOL)))
    gesamt = 'Sum(CDbl(Fields!Volumen.Value), "S2_D05")'
    kumuliert = '=RunningValue(%s, Sum, "S2_D05") / %s' % (VOL, gesamt)
    marke = v.strip("=0.8", width="=0.008", color=c.HAIR)                  # 80-%-Marke auf der Prozent-Achse
    groesste = 'Max(Sum(CDbl(Fields!Volumen.Value), "S2_D05_Cat1"), "S2_D05")'
    xml = v.chart(
        "S2_D05", top, x, w, h,
        [v.S("Volumen", {"Y": "=" + VOL}, typ="Column", sub="Plain", color=c.BLUE, custom_xml=v.custom(PointWidth="0.55")),
         v.S("Kumuliert", {"Y": kumuliert}, typ="Line", sub="Plain", color=c.ORANGE, line_w="2pt", vaxis="Secondary",
             mark=v.marker("Circle", "6pt", c.ORANGE),
             label=v.dlabel("Top", fmt="0 %", size="8pt", color=c.TEXT, bold=True))],
        [(gruppe, "=" + VOL, "Descending")], names=["Volumen", "Kumuliert"],
        areas=v.area(cat_axes=[kategorie_achse(interval="1", size="7pt")],
                     val_axes=[v.axis("Primary", visible=True, line=False, hide_labels=True, minimum="0",
                                      maximum="=%s * 3.6" % groesste),
                               v.axis("Secondary", visible=True, hide_labels=True, line=False, minimum="=-0.6", maximum="=1.2",
                                      location="Opposite", strips=marke)],
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw(WAND_MIT_MATERIAL)))
    return kategorie_label(gruppe_filter(xml, c.topn(VOL, n)), gruppe, label)


BREITENKLASSEN = ["< 90 cm", "90–100 cm", "101–125 cm", "> 125 cm"]


def breitenklasse(breite):
    """Ausdruck: Breitenklasse 1..4 (in ganzen cm: <90, 90-100, 101-125, >125)."""
    cm = "Round(%s * 100)" % breite
    return "IIf(%s < 90, 1, IIf(%s <= 100, 2, IIf(%s <= 125, 3, 4)))" % (cm, cm, cm)


def _d06(top, x, w, h):
    """Gruppierte Saeulen: Fenster und Tueren nebeneinander je Breitenklasse (vier Klassen statt jeder Einzelbreite)."""
    klasse = breitenklasse("CDbl(Fields!Laenge.Value)")
    serien = []
    for kurz, bed, farbe in (("Fenster", FENSTER, c.BLUE), ("Tueren", TUER, c.SKY)):
        y = "Sum(IIf(%s, 1, 0))" % bed
        serien.append(v.S(kurz, {"Y": "=" + y}, typ="Column", sub="Plain", color=farbe,
                          label=v.dlabel(fmt="N0", size="8.5pt", color=c.TEXT, label='=IIf(%s = 0, "", Format(%s, "N0"))' % (y, y)),
                          custom_xml=v.custom(PointWidth="0.8", BarLabelStyle="Outside")))
    xml = v.chart(
        "S2_D06", top, x, w, h, serien, [("=" + klasse, None, None)], names=["Fenster", "Tueren"],
        areas=v.area(cat_axes=[kategorie_achse(interval="1", size="8pt")],
                     val_axes=[wert_achse('=Max(Sum(IIf(%s Or %s, 1, 0), "S2_D06_Cat1"), "S2_D06") * 1.18' % (FENSTER, TUER))],
                     pos=(0, 0, 100, 100)),
        extra=c.filters(raw("((%s Or %s) And CDbl(Fields!Laenge.Value) > 0)" % (FENSTER, TUER))))
    namen = ", ".join('"%s"' % k for k in BREITENKLASSEN)
    return kategorie_label(xml, "=" + klasse,
                           "=Choose(%s, %s)" % (breitenklasse("CDbl(First(Fields!Laenge.Value))"), namen))


# ---------------------------------------------------------------- Bausteine (Kopf + Diagramm + Etikett)
H = 5.6   # Hoehe des Diagramms (mit Legende 0,35 weniger)


def block(kennung, top, left, w, kopf, titel, diagramm, technik, legende_xml=None):
    """Ein Baustein: Abschnittskopf, optional Legende, Diagramm, Etikett."""
    nm = "S2_" + kennung.replace("-", "")
    items = overline(nm, top, left, w, kopf, titel)
    ct, ch = top + 1.45, H
    if legende_xml is not None:
        items += legende_xml(nm + "_leg", top + 1.32, left, w)
        ct, ch = top + 1.8, H - 0.35
    items += diagramm(ct, left, w, ch)
    return items + etikett(nm + "_e", top + 1.45 + H + 0.05, left, w, kennung, technik)


def _mat_legende(bedingung):
    return lambda nm, top, left, w: gruppenlegende(nm, top, left, w, bedingung)


@b.baustein("D030", "Fläche je Bauteilart")
def d030(top, left, w):
    return block("D030", top, left, w, "Bauteile", "Fläche je Bauteilart", _d01,
                 "Säulen mit Direktbeschriftung, Art aus der Objektnummer, Werteachse entfällt")


@b.baustein("D040", "Die 8 größten Bauteile")
def d040(top, left, w):
    bauteile = "CountDistinct(IIf(%s, Fields!Nr.Value, Nothing))" % raw(MIT_MATERIAL)
    return block("D040", top, left, w, "Rangliste",
                 b.rang_titel(bauteile, 8, "Die ", " größten Bauteile", "Das größte Bauteil", "Die größten Bauteile"), _d02,
                 "Balken-Rangliste Top 8 (Filter TopN), Materialfarbe, Wert am Balken")


@b.baustein("D050", "Volumen je Bauteilart")
def d050(top, left, w):
    return block("D050", top, left, w, "Bauteile", "Volumen je Bauteilart", _d03,
                 "Gestapelte Säulen, Serien = Materialgruppen (höchstens 5), Summe als Linie",
                 _mat_legende(MIT_MATERIAL))


@b.baustein("D060", "Materialanteile der Wandschichten")
def d060(top, left, w):
    return block("D060", top, left, w, "Wandaufbau", "Materialanteile der Wandschichten", _d04,
                 "100-%-Stapelbalken, Serien = Materialgruppen, Anteil im Segment",
                 _mat_legende(WAND_MIT_MATERIAL))


@b.baustein("D070", "Die 8 größten Wandaufbauten")
def d070(top, left, w):
    aufbauten = 'CountDistinct(IIf(%s, %s & "|" & CStr(Round(CDbl(Fields!Dicke.Value) * 1000)), Nothing))' % (WAND_MIT_MATERIAL, MATGRUPPE)
    return block("D070", top, left, w, "Wandaufbau",
                 b.rang_titel(aufbauten, 8, "Die ", " größten Wandaufbauten", "Der größte Wandaufbau", "Die größten Wandaufbauten"), _d05,
                 "Pareto Top 8: eigene Achsen, Linie kumuliert zur Gesamtsumme aller Schichten")


@b.baustein("D080", "Fenster und Türen nach Breite")
def d080(top, left, w):
    return block("D080", top, left, w, "Öffnungen", "Fenster und Türen nach Breite", _d06,
                 "Gruppierte Säulen, vier Breitenklassen, zwei Serien",
                 lambda nm, t, x, bw: legende(nm, t, x, bw, [(c.BLUE, "Fenster "), (c.SKY, "Türen")]))   # Mehrzahl: eigener Schluessel


# ---------------------------------------------------------------- Seite
TITEL = "Diagramme: Vergleichen"   # Name der Seite in der Dokumentstruktur (PDF-Lesezeichen)


def seite():
    x0, w = c.INSET, 8.8
    xr = x0 + w + 0.4
    items = seitenkopf(2, "Diagramme: Vergleichen", "Säulen, Balken, Stapel, Kombination")
    for top, links, rechts in ((3.3, d030, d040), (11.75, d050, d060), (20.2, d070, d080)):
        items += links(top, x0, w) + rechts(top, xr, w)
    return items
