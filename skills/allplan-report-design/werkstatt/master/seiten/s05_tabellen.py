# -*- coding: utf-8 -*-
"""Seite 5 - Tabellen, die zeigen statt zaehlen (datenfest: jede Tabelle hat einen Deckel, die Seite bleibt ein Blatt).

T020 Rangliste mit Zellenbalken (Raeume, die 9 groessten Nutzungen), T030 Statussymbole (Tuertypen nach Anzahl),
T040 Kreuztabelle mit Farbskala (Bauteilart x Materialgruppe) mit T050 100-%-Stapelbalken in der Zelle,
T060 gruppierte Tabelle mit Zwischensummen und T070 Mini-Saeulen im Gruppenkopf.
Summen und Anteile rechnen ueber ALLE Zeilen (Datensatz-Bereich), auch wenn die Tabelle nur die groessten zeigt.
"""
import bausteine as b
import core as c
import viz as v
from bausteine import (RAUM, TUER, MIT_MATERIAL, MATGRUPPE, ART, MAT_FARBE, raw, summe, anzahl, in_cell, overline, etikett,
                       seitenkopf)

TITEL = "Tabellen, die zeigen statt zählen"   # Name der Seite in der Dokumentstruktur (PDF-Lesezeichen)

ALLE = "AllplanReport"          # Bereich "alle Zeilen des Datensatzes", unabhaengig von Tabellenfiltern
FLAECHE = "Sum(CDbl(Fields!Flaeche.Value))"
VOLUMEN = "Sum(CDbl(Fields!Volumen.Value))"
HEAD = c.edge(["Bottom"], c.INK, "1pt")
ROW = c.edge(["Bottom"], c.HAIR, "0.75pt")
SUMLINE = c.edge(["Top"], c.INK, "1pt")
SPALTE_W = 8.8                  # Breite eines Bausteins in der Zweispaltenanordnung

# feste Reihenfolge der Materialgruppen im ganzen Abschnitt (wie auf Seite 1: groesster Anteil zuerst)
GRUPPEN = ["Beton", "Dämmung", "Mauerwerk", "Gipskarton", "Holz", "Stahl", "Glas", "Naturstein", "Sonstiges"]
GRUPPENFARBE = dict(c.MATERIALGRUPPE)
ORDNUNG = "Switch(%s, True, 99)" % ", ".join('%s="%s", %d' % (MATGRUPPE, g, i + 1) for i, g in enumerate(GRUPPEN))
HELLE_GRUPPEN = "Dämmung Gipskarton Glas Sonstiges"      # helle Segmente bekommen dunkle Schrift

T01_ZEILEN, T04_ZEILEN, T02_SPALTEN, T03_GRUPPEN, T03_SAEULEN = 9, 9, 5, 6, 12
T03_ARTEN = 5                    # Bauteilarten im Rohbau (Wand, Stuetze, Decke, Unterzug, Bodenplatte): mehr Einzelzeilen gibt es nie
LEGENDE_MAX = 3                  # hoechstens so viele Gruppen in der Legende, danach "…" (sonst bricht die Zeile um)
STAPEL_MIN = 0.14                # Segment erst ab diesem Anteil beschriften (schmaler: der Text passt nicht hinein)


# ---------------------------------------------------------------- Hilfen
def kopf(name, label, align=None):
    return c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=HEAD, pad=(4, 2, 4, 4))


def ganz(expr):
    """Anzahl als ganze Zahl mit Tausenderpunkt."""
    return 'Format(%s, "#,##0")' % expr


def kurz(expr, n):
    """Name auf n Zeichen kuerzen, mit "…" am Ende (n darf ein Ausdruck sein): sonst schneidet die Zelle mitten im Wort ab."""
    return 'IIf(Len(%s) > %s, Left(%s, %s - 1) & "…", %s)' % (expr, n, expr, n, expr)


def fm(expr):
    """Zahlenformat: ab 1.000 ohne Nachkommastelle (19.478 statt 19.478,3), darunter eine Stelle."""
    return 'Format(%s, IIf(%s >= 1000, "#,##0", "#,##0.0"))' % (expr, expr)


def zahl(name, expr, unit, align="Right", font=c.F, color=c.TEXT, border_xml=ROW, size=9.5, bg=None):
    """Zahl mit heller Einheit. Kein Innenabstand oben/unten: sonst schneidet die Zelle in niedrigen Zeilen den Fuss des
    Kommas ab und es sieht wie ein Punkt aus."""
    runs = [c.run("=" + fm(expr), size, color, font)]
    if unit:
        runs.append(c.run(" " + unit, 8, c.FAINT))
    return c.cell(name, c.para(runs), align, border_xml=border_xml, bg=bg, pad=(4, 0, 4, 0))


def _rgb(hexfarbe):
    return tuple(int(hexfarbe[i:i + 2], 16) for i in (1, 3, 5))


def heat(t):
    """Farbausdruck: stufenlos von Weiss nach c.BLUE, t = Ausdruck 0..1."""
    def kanal(ziel):
        return 'Right("0" & Hex(CInt(255 + (%d - 255) * (%s))), 2)' % (ziel, t)
    r, g, bl = _rgb(c.BLUE)
    return '="#" & %s & %s & %s' % (kanal(r), kanal(g), kanal(bl))


def heat_fest(t):
    """Dieselbe Farbskala als feste Farbe (fuer die Legende); gerechnet aus c.BLUE, kein eigener Farbwert."""
    r, g, bl = _rgb(c.BLUE)
    return "#%02X%02X%02X" % tuple(int(round(255 + (z - 255) * t)) for z in (r, g, bl))


def tabellenfeld(name, top, left, w, h, xml):
    """Wachsende Tabelle in Rechteck mit reservierter Hoehe (haelt das Seitenlayout)."""
    return c.rect(name, top, left, w, h, xml)


def zelle(z):
    """Tabellenzelle: Inhalt, (Inhalt, Spaltenzahl) fuer verbundene Zellen oder None fuer eine verdeckte Zelle."""
    if z is None:
        return "<TablixCell/>"
    if isinstance(z, tuple):
        return "<TablixCell><CellContents>%s<ColSpan>%d</ColSpan></CellContents></TablixCell>" % z
    return "<TablixCell><CellContents>%s</CellContents></TablixCell>" % z


def zeile(h, zellen):
    return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (c.cm(h), "".join(zelle(z) for z in zellen))


def versteckt(bedingung):
    return "<Visibility><Hidden>=%s</Hidden></Visibility>" % c.esc(bedingung)


def tablix(name, cols, rows, member_xml, filter_expr=None):
    """Tabelle mit eigener Zeilenhierarchie. rows: Liste (Hoehe, Zellen); member_xml: Inhalt von TablixRowHierarchy."""
    hoehe = sum(r[0] for r in rows)
    return ('<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s</TablixRows></TablixBody>'
            "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>"
            "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>"
            "<DataSetName>AllplanReport</DataSetName>%s<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>"
            "<Style><Border><Style>None</Style></Border></Style></Tablix>") % (
        name, "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(w) for w in cols),
        "".join(zeile(h, z) for h, z in rows), "<TablixMember/>" * len(cols), member_xml,
        c.filters(filter_expr) if filter_expr else "", c.cm(hoehe), c.cm(sum(cols)))


KOPFZEILE = "<TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember>"
FUSSZEILE = "<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>"


def gruppe(name, ausdruck, sortierung, desc=False, deckel=None):
    """Zeilengruppe (eine Datenzeile je Gruppe) mit Sortierung und optionalem TopN-Deckel."""
    return ('<TablixMember><Group Name="%s"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions>%s</Group>'
            "<SortExpressions><SortExpression><Value>%s</Value>%s</SortExpression></SortExpressions></TablixMember>"
            % (name, c.esc(ausdruck), deckel or "", c.esc(sortierung), "<Direction>Descending</Direction>" if desc else ""))


def rest_zeile(hidden):
    """Zeile "... und n weitere", die nur erscheint, wenn die Tabelle gekuerzt wurde."""
    return "<TablixMember>%s<KeepWithGroup>Before</KeepWithGroup></TablixMember>" % versteckt(hidden)


# ---------------------------------------------------------------- T020 Rangliste mit Zellenbalken
@b.baustein("T020", "Rangliste mit Zellenbalken")
def t020(top, left, w):
    nutzungen = 'CountDistinct(IIf(%s, Fields!Funktion.Value, Nothing))' % RAUM
    items = overline("S5_A1", top, left, w, "Rangliste", b.rang_titel(nutzungen, T01_ZEILEN, "Die ", " größten Nutzungen",
                                                                      "Die größte Nutzung", "Die größten Nutzungen"))
    maxwert = 'Max(Sum(CDbl(Fields!Flaeche.Value), "S5_T1_G"), "S5_T1")'
    bar = in_cell(v.chart(
        "S5_ZBalken", 0, 0, 1, 1,
        [v.S("V", {"Y": "=" + FLAECHE}, typ="Bar", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc('=IIf(%s = %s, "%s", "%s")' % (FLAECHE, maxwert, c.BLUE, c.RAMP[3])),
             custom_xml=v.custom(PointWidth="0.42"))],
        [], nomember=True, dataset=False,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)],
                     val_axes=[v.axis("Primary", visible=False, minimum="0", maximum="=" + maxwert)],
                     pos=(0, 0, 100, 100), inner=(4, 0, 90, 100))))
    alle = summe("Flaeche", RAUM, ALLE)                               # Fläche aller Räume, auch der nicht gelisteten
    n_alle = 'CountDistinct(IIf(%s, Fields!Funktion.Value, Nothing), "%s")' % (RAUM, ALLE)
    zeigt = 'Sum(Sum(CDbl(Fields!Flaeche.Value), "S5_T1_G"), "S5_T1")'      # Summe der gelisteten Gruppen
    rest_n = "(%s - %d)" % (n_alle, T01_ZEILEN)
    rest_f = "(%s - %s)" % (alle, zeigt)
    anteil = "IIf(%s = 0, 0.0, %s / %s)" % (alle, FLAECHE, alle)
    erstes = 'Min(Fields!Funktion.Value) & "   "'
    # eindeutiger Nachrang (erste Zeichen des Namens), damit TopN bei gleicher Flaeche nicht mehr als 9 Zeilen liefert
    eindeutig = ("%s + CDbl(Asc(Left(%s, 1))) * 0.000001 + CDbl(Asc(Mid(%s, 2, 1))) * 0.000000001 + CDbl(Asc(Mid(%s, 3, 1))) * 0.000000000001"
                 % (FLAECHE, erstes, erstes, erstes))
    rows = [
        (0.5, [kopf("S5_T1_H1", "Nr", "Right"), kopf("S5_T1_H2", "Nutzung"), kopf("S5_T1_H3", "Fläche", "Right"),
               kopf("S5_T1_H4", ""), kopf("S5_T1_H5", "Anteil", "Right")]),
        (0.48, [
            c.cell("S5_T1_D1", c.run('=Format(RunningValue(Fields!Funktion.Value, CountDistinct, Nothing), "00")', 8, c.FAINT, c.F_SEMI),
                   "Right", border_xml=ROW, pad=(0, 1, 6, 1)),
            c.cell("S5_T1_D2", c.para([c.run("=" + kurz("First(Fields!Funktion.Value)", "IIf(CountRows() > 1, 16 - Len(CStr(CountRows())), 20)"), 8.5, c.INK, c.F_SEMI),
                                      c.run('=IIf(CountRows() > 1, " ×" & CountRows(), "")', 7, c.FAINT)]),
                   border_xml=ROW, pad=(4, 0, 4, 0)),
            zahl("S5_T1_D3", FLAECHE, "m²"),
            c.rect("S5_T1_D4", None, 0, 0, 0, bar, border_xml=ROW),
            c.cell("S5_T1_D5", c.run("=" + anteil, 9.5, c.TEXT, fmt="0 %"), "Right", border_xml=ROW, pad=(4, 0, 4, 0)),
        ]),
        (0.46, [
            c.cell("S5_T1_R0", c.run("", 7), border_xml=ROW),
            (c.cell("S5_T1_R1", c.run('="… und " & %s & " weitere Nutzungen · " & %s & " m²"' % (rest_n, fm(rest_f)), 7.5, c.MUTED),
                    border_xml=ROW, pad=(4, 0, 4, 0)), 3),
            None, None,
            c.cell("S5_T1_R5", c.run("=IIf(%s = 0, 0.0, %s / %s)" % (alle, rest_f, alle), 8, c.MUTED, fmt="0 %"), "Right",
                   border_xml=ROW, pad=(4, 0, 4, 0)),
        ]),
        (0.5, [
            c.cell("S5_T1_F1", c.run("", 9), border_xml=SUMLINE),
            c.cell("S5_T1_F2", c.run("Summe alle", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 0, 4, 0)),
            zahl("S5_T1_F3", alle, "m²", font=c.F_SEMI, color=c.INK, border_xml=SUMLINE),
            c.cell("S5_T1_F4", c.run("", 9), border_xml=SUMLINE),
            c.cell("S5_T1_F5", c.run("100 %", 9.5, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
        ]),
    ]
    members = (KOPFZEILE
               + gruppe("S5_T1_G", "=Fields!Funktion.Value", "=" + eindeutig, True, c.topn(eindeutig, T01_ZEILEN))
               + rest_zeile("%s <= 0" % rest_n) + FUSSZEILE)
    tab = tablix("S5_T1", [0.7, 3.2, 1.9, 1.7, 1.3], rows, members, raw(RAUM))
    items += tabellenfeld("S5_T1_Feld", top + 1.45, left, w, 5.85, tab)
    items += etikett("S5_T1_E", top + 7.35, left, w, "T020", "Zellenbalken je Zeile, Akzent am größten Wert; Deckel 9, Summe über alle")
    return items


# ---------------------------------------------------------------- T030 Statussymbole
@b.baustein("T030", "Statussymbole (Türtypen)")
def t030(top, left, w):
    items = overline("S5_A4", top, left, w, "Status", "Türen nach Typ und Breite")
    breite = "CDbl(Min(Fields!Laenge.Value))"
    farbe = '=IIf(%s >= 0.9, "%s", IIf(%s >= 0.8, "%s", "%s"))' % (breite, c.GREEN_TEXT, breite, c.AMBER_TEXT, c.RED_TEXT)
    zeichen = '=IIf(%s >= 0.9, "✓", IIf(%s >= 0.8, "▲", "✕"))' % (breite, breite)
    text = '=IIf(%s >= 0.9, "barrierefrei", IIf(%s >= 0.8, "knapp", "zu schmal"))' % (breite, breite)
    typ_key = 'Fields!Bezeichnung.Value & "|" & Format(CDbl(Fields!Laenge.Value), "0.00")'
    erstes = 'Min(Fields!Bezeichnung.Value) & "  "'
    # Anzahl zuerst, dann schmalere Tuer zuerst; Zeichen des Namens als eindeutiger Nachrang
    eindeutig = ("CountRows() + CDbl(Min(CDbl(Fields!Laenge.Value))) / 1000.0 + CDbl(Asc(Left(%s, 1))) * 0.00000001 "
                 "+ CDbl(Asc(Mid(%s, 2, 1))) * 0.00000000001" % (erstes, erstes))
    n_alle = 'CountDistinct(IIf(%s, %s, Nothing), "%s")' % (TUER, typ_key, ALLE)
    summe_t = anzahl(TUER, ALLE)
    zeigt = 'Sum(Sum(1, "S5_T4_G"), "S5_T4")'
    rest_n = "(%s - %d)" % (n_alle, T04_ZEILEN)
    rest_t = "(%s - %s)" % (summe_t, zeigt)
    name_ausdruck = '=IIf(First(Fields!Bezeichnung.Value) = "", "(ohne Bezeichnung)", %s)' % kurz("First(Fields!Bezeichnung.Value)", 21)
    rows = [
        (0.5, [kopf("S5_T4_H1", "Typ"), kopf("S5_T4_H2", "Anzahl", "Right"), kopf("S5_T4_H3", "Breite", "Right"),
               kopf("S5_T4_H4", "", "Center"), kopf("S5_T4_H5", "Status")]),
        (0.48, [
            c.cell("S5_T4_D1", c.run(name_ausdruck, 8, c.INK, c.F_SEMI), border_xml=ROW, pad=(4, 0, 4, 0)),
            c.cell("S5_T4_D2", c.run("=CountRows()", 9.5, c.TEXT, fmt="N0"), "Right", border_xml=ROW, pad=(4, 0, 4, 0)),
            c.cell("S5_T4_D3", c.para([c.run("=" + breite, 9.5, c.INK, c.F_SEMI, fmt="N2"), c.run(" m", 8, c.FAINT)]),
                   "Right", border_xml=ROW, pad=(4, 0, 4, 0)),
            c.cell("S5_T4_D4", c.run(zeichen, 11, farbe, b.SYMBOL), "Center", border_xml=ROW, pad=(0, 0, 0, 0)),
            c.cell("S5_T4_D5", c.run(text, 8, c.MUTED), border_xml=ROW, pad=(2, 0, 2, 0)),
        ]),
        (0.46, [
            (c.cell("S5_T4_R1", c.run('="… und " & %s & " weitere Türtypen · " & %s & " Türen"' % (rest_n, ganz(rest_t)), 7.5, c.MUTED),
                    border_xml=ROW, pad=(4, 0, 4, 0)), 5),
            None, None, None, None,
        ]),
        (0.5, [
            c.cell("S5_T4_F1", c.run("Summe alle", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 0, 4, 0)),
            c.cell("S5_T4_F2", c.run("=" + ganz(summe_t), 9.5, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
            c.cell("S5_T4_F3", c.run("", 9), border_xml=SUMLINE), c.cell("S5_T4_F4", c.run("", 9), border_xml=SUMLINE),
            c.cell("S5_T4_F5", c.run("", 9), border_xml=SUMLINE),
        ]),
    ]
    members = (KOPFZEILE + gruppe("S5_T4_G", "=" + typ_key, "=" + eindeutig, True, c.topn(eindeutig, T04_ZEILEN))
               + rest_zeile("%s <= 0" % rest_n) + FUSSZEILE)
    tab = tablix("S5_T4", [3.2, 1.4, 1.5, 0.7, 2.0], rows, members, raw(TUER))
    items += tabellenfeld("S5_T4_Feld", top + 1.45, left, w, 5.85, tab)
    items += etikett("S5_T4_E", top + 7.35, left, w, "T030", "Türen je Typ und Breite (Deckel 9); Symbol und Farbe nach Schwelle", h=0.3)
    items += c.text("S5_T4_E2", top + 7.7, left, w, 0.3,
                    c.run("Schwelle frei gewählt: ab 0,90 m barrierefrei, ab 0,80 m knapp (Modellmaß).", 7, c.FAINT))
    return items


# ---------------------------------------------------------------- T040 Kreuztabelle mit Farbskala + T050 Stapelbalken
def stapel(name, scope, linie=False):
    """100-%-Stapelbalken in der Zelle: Anteile der Materialgruppen im Bereich 'scope', Segmente ab 14 % beschriftet."""
    anteil = '%s / %s' % (VOLUMEN, 'Sum(CDbl(Fields!Volumen.Value), "%s")' % scope)
    farbe = c.esc('=IIf(InStr("%s", %s) > 0, "%s", "%s")' % (HELLE_GRUPPEN, MATGRUPPE, c.INK, c.WHITE))
    label = v.dlabel(position="Center", size="7pt", color=farbe, label='=IIf(%s > %s, Format(%s, "0 %%"), "")' % (anteil, STAPEL_MIN, anteil))
    gruppe_expr = "=" + MATGRUPPE
    xml = in_cell(v.chart(
        name, 0, 0, 1, 1,
        [v.S("V", {"Y": "=" + VOLUMEN}, typ="Bar", sub="PercentStacked",
             pstyle="<Color>%s</Color>%s" % (c.esc(MAT_FARBE), v.border(c.WHITE, "Solid", "1pt")),
             label=label, custom_xml=v.custom(PointWidth="1.5"))],
        [], nomember=True, dataset=False, sergroup=gruppe_expr,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False, line=False)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0", maximum="100")],
                     pos=(0, 0, 100, 100), inner=(4, 8, 94, 84)),
        style=("<Style><Border><Style>None</Style></Border><TopBorder><Color>%s</Color><Style>Solid</Style><Width>1pt</Width></TopBorder>"
               "<BackgroundColor>%s</BackgroundColor></Style>" % (c.INK, c.WHITE)) if linie else None))
    # Reihenfolge der Segmente fest (wie die Spalten), nicht alphabetisch
    return xml.replace("<Value>%s</Value></SortExpression></SortExpressions><Label>" % c.esc(gruppe_expr),
                       "<Value>=%s</Value></SortExpression></SortExpressions><Label>" % c.esc(ORDNUNG), 1)


def legende():
    """Legende der Materialgruppen, die im Modell vorkommen (jede Gruppe erscheint nur, wenn es sie gibt), einzeilig:
    hoechstens LEGENDE_MAX Gruppen in der festen Reihenfolge, bei mehr steht "…" am Ende. Kaestchen und Name haengen
    an derselben Bedingung und stehen darum nie getrennt. Bei drei Gruppen passt die Zeile auch mit den laengsten Namen
    und dem "…" in das Feld (bei vier brach das "…" in eine zweite Zeile). Kein geschuetztes Leerzeichen am Namensende:
    das ist im Sprachschalter der Schluessel fuer die Kurzform ("Beton" + U+00A0 = Concr.)."""
    teile = []
    for i, g in enumerate(GRUPPEN):
        da = 'Sum(IIf(%s And %s = "%s", 1, 0), "%s") > 0' % (MIT_MATERIAL, MATGRUPPE, g, ALLE)
        # Anzahl der vorhandenen Gruppen bis einschliesslich dieser (in der festen Reihenfolge)
        bis_hier = 'CountDistinct(IIf(%s And %s <= %d, %s, Nothing), "%s")' % (MIT_MATERIAL, ORDNUNG, i + 1, MATGRUPPE, ALLE)
        zeigen = "%s And %s <= %d" % (da, bis_hier, LEGENDE_MAX)
        teile.append(c.run('=IIf(%s, "■ ", "")' % zeigen, 7, GRUPPENFARBE[g], b.SYMBOL))
        teile.append(c.run('=IIf(%s, "%s ", "")' % (zeigen, g), 7, c.MUTED, c.F_SEMI))
    mehr = 'CountDistinct(IIf(%s, %s, Nothing), "%s") > %d' % (MIT_MATERIAL, MATGRUPPE, ALLE, LEGENDE_MAX)
    teile.append(c.run('=IIf(%s, "…", "")' % mehr, 7, c.MUTED, c.F_SEMI))
    return teile


@b.baustein("T050", "Stapelbalken in der Tabellenzelle")
@b.baustein("T040", "Kreuztabelle mit Farbskala")
def t040(top, left, w):
    items = overline("S5_A2", top, left, w, "Kreuztabelle", "Volumen nach Bauteilart und Materialgruppe", titel_w=w - 5.2)
    # Legende der Farbskala rechts neben der Ueberschrift
    stufen = [c.run("m³ · weniger  ", 7, c.FAINT)] + [c.run("■", 11, heat_fest(t), b.SYMBOL) for t in (0.12, 0.3, 0.5, 0.72, 0.95)] \
        + [c.run("  mehr", 7, c.FAINT)]
    items += c.text("S5_A2_Leg", top + 0.42, left + w - 5.0, 5.0, 0.6, c.para(stufen, "Right"), valign="Middle")

    gesamt = summe("Volumen", MIT_MATERIAL, ALLE)
    t = "IIf(%s = 0, 0.0, IIf(%s / %s * 4 > 1, 1.0, %s / %s * 4))" % (gesamt, VOLUMEN, gesamt, VOLUMEN, gesamt)
    kachel = ("<Border><Style>Solid</Style><Color>%s</Color><Width>2pt</Width></Border>" % c.WHITE)
    wert = '=IIf(%s = 0, "–", %s)' % (VOLUMEN, fm(VOLUMEN))
    wfarbe = '=IIf(%s = 0, "%s", IIf(%s > 0.55, "%s", "%s"))' % (VOLUMEN, c.FAINT, t, c.WHITE, c.INK)
    kopf_h, zeile_h = 0.85, 0.65
    sp_w, rk_w, sum_w, stapel_w = 1.8, 2.1, 1.6, 5.3

    def tc(inner):
        return "<TablixCell><CellContents>%s</CellContents></TablixCell>" % inner

    def summe_zelle(name, rand=""):
        return c.cell(name, c.run("=" + fm(VOLUMEN), 9, c.INK, c.F_SEMI), "Right", border_xml=rand, pad=(4, 2, 6, 2))

    heat_zelle = c.cell("S5_T2_Z", c.run(wert, 9, wfarbe), "Right", border_xml=kachel, bg_expr=heat(t), pad=(4, 2, 8, 2))
    body = ("<TablixBody><TablixColumns>"
            "<TablixColumn><Width>%s</Width></TablixColumn><TablixColumn><Width>%s</Width></TablixColumn>"
            "<TablixColumn><Width>%s</Width></TablixColumn></TablixColumns><TablixRows>"
            "<TablixRow><Height>%s</Height><TablixCells>%s%s%s</TablixCells></TablixRow>"
            "<TablixRow><Height>%s</Height><TablixCells>%s%s%s</TablixCells></TablixRow>"
            "</TablixRows></TablixBody>") % (
        c.cm(sp_w), c.cm(sum_w), c.cm(stapel_w),
        c.cm(zeile_h), tc(heat_zelle), tc(summe_zelle("S5_T2_ZS")), tc(stapel("S5_StapelZ", "S5_T2_Obj")),
        c.cm(zeile_h), tc(summe_zelle("S5_T2_SZ", SUMLINE)), tc(summe_zelle("S5_T2_SS", SUMLINE)),
        tc(stapel("S5_StapelS", "S5_T2", linie=True)))

    def kh(size, inner):
        return "<TablixHeader><Size>%s</Size><CellContents>%s</CellContents></TablixHeader>" % (c.cm(size), inner)

    mat_kopf = c.cell("S5_T2_HM", c.run("=UCase(%s)" % MATGRUPPE, 7, c.MUTED, c.F_SEMI), "Right", "Bottom", border_xml=HEAD,
                      pad=(0, 2, 3, 4))
    # die 5 volumenstaerksten Gruppen als Spalten, in der festen Reihenfolge der Gruppen
    spalten = c.topn(VOLUMEN, T02_SPALTEN)
    col_h = ("<TablixColumnHierarchy><TablixMembers>"
             '<TablixMember><Group Name="S5_T2_Mat"><GroupExpressions><GroupExpression>=%s</GroupExpression>'
             "</GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>=%s</Value></SortExpression></SortExpressions>%s</TablixMember>"
             "<TablixMember>%s</TablixMember><TablixMember>%s</TablixMember></TablixMembers></TablixColumnHierarchy>") % (
        c.esc(MATGRUPPE), spalten, c.esc(ORDNUNG), kh(kopf_h, mat_kopf),
        kh(kopf_h, kopf("S5_T2_HS", "Summe", "Right").replace("<PaddingRight>4pt", "<PaddingRight>8pt")),
        kh(kopf_h, c.cell("S5_T2_HP", c.para(legende()), None, "Bottom", border_xml=HEAD, pad=(8, 2, 0, 4))))
    zeilen_h = ("<TablixRowHierarchy><TablixMembers>"
                '<TablixMember><Group Name="S5_T2_Obj"><GroupExpressions><GroupExpression>=%s</GroupExpression>'
                "</GroupExpressions></Group><SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction>"
                "</SortExpression></SortExpressions>%s</TablixMember><TablixMember>%s</TablixMember></TablixMembers></TablixRowHierarchy>") % (
        c.esc(ART), c.esc(VOLUMEN), kh(rk_w, c.cell("S5_T2_RH", c.run("=" + ART, 8.5, c.INK, c.F_SEMI), pad=(4, 2, 4, 2))),
        kh(rk_w, c.cell("S5_T2_RS", c.run("Summe", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 2, 4, 2))))
    ecke = ("<TablixCorner><TablixCornerRows><TablixCornerRow><TablixCornerCell><CellContents>%s</CellContents></TablixCornerCell>"
            "</TablixCornerRow></TablixCornerRows></TablixCorner>") % kopf("S5_T2_Ecke", "Bauteilart")
    hoehe = kopf_h + 2 * zeile_h
    tab = ('<Tablix Name="S5_T2">%s%s%s%s<DataSetName>AllplanReport</DataSetName>%s'
           "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>") % (
        ecke, body, col_h, zeilen_h, c.filters(raw(MIT_MATERIAL)), c.cm(hoehe), c.cm(rk_w + sp_w * T02_SPALTEN + sum_w + stapel_w))
    items += tabellenfeld("S5_T2_Feld", top + 1.45, left, w, 4.8, tab)
    items += etikett("S5_T2_E", top + 6.3, left, w, "T040",
                     "Zeilen = Bauteilart, Spalten = Materialgruppe (die 5 größten); Farbskala per Hintergrundausdruck, voll ab 25 % des Gesamtvolumens", h=0.3)
    items += etikett("S5_T2_E2", top + 6.65, left, w, "T050",
                     "100-%-Stapelbalken in der Zelle: Diagramm je Zeile, Farbe der Materialgruppe, Segmente ab 14 % beschriftet", h=0.3)
    return items


# ---------------------------------------------------------------- T060 gruppierte Tabelle + T070 Mini-Saeulen
@b.baustein("T070", "Mini-Säulen im Gruppenkopf")
@b.baustein("T060", "Gruppierte Tabelle mit Zwischensummen")
def t060(top, left, w):
    items = overline("S5_A3", top, left, w, "Gruppiert", "Bauteile nach Materialgruppe und Bauteilart")
    gesamt = summe("Volumen", MIT_MATERIAL, ALLE)
    # Feste Hoehe: nur die groesste Materialgruppe (Rang 1 nach Volumen) zeigt Einzelzeilen und Zwischensumme, alle anderen
    # Gruppen sind eine Zeile. Der Nachrang (feste Reihenfolge der Gruppen, winzig) macht den Rang auch bei gleichem Volumen eindeutig.
    schluessel = 'Sum(CDbl(Fields!Volumen.Value), "S5_T3_Mat") - CDbl(Min(%s, "S5_T3_Mat")) * 0.000001' % ORDNUNG
    groesste = '%s >= Max(%s, "S5_T3")' % (schluessel, schluessel)
    einzeln = '(CountDistinct(%s) = 1 Or Not (%s))' % (ART, groesste)       # Gruppe ist eine Zeile (eine Art oder nicht die groesste)
    n_gruppen = 'CountDistinct(IIf(%s, %s, Nothing), "%s")' % (MIT_MATERIAL, MATGRUPPE, ALLE)
    nr_zahl = ("(Val(Left(Min(Fields!Nr.Value), 4)) * 10000000000.0 + Val(Right(Min(Fields!Nr.Value), 10))) * 0.000000000000000001")
    eindeutig = "%s + %s" % (VOLUMEN, nr_zahl)               # eindeutiger Nachrang je Bauteil (Nr), damit TopN genau 12 liefert

    def spark(name):
        xml = in_cell(v.chart(
            name, 0, 0, 1, 1,
            [v.S("V", {"Y": "=" + VOLUMEN}, typ="Column", sub="Plain",
                 pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE), custom_xml=v.custom(PointWidth="0.85"))],
            [("=Fields!Nr.Value", "=" + eindeutig, "Descending")], names=["V"], dataset=False,
            areas=v.area(cat_axes=[v.axis("Primary", visible=False, line=False)],
                         val_axes=[v.axis("Primary", visible=False, line=False, minimum="0")],
                         pos=(0, 0, 100, 100), inner=(4, 14, 92, 72), style="<BackgroundColor>%s</BackgroundColor>" % c.SURFACE),
            style="<Style><Border><Style>None</Style></Border><BackgroundColor>%s</BackgroundColor></Style>" % c.SURFACE))
        return xml.replace("</GroupExpressions></Group>", "</GroupExpressions>" + c.topn(eindeutig, T03_SAEULEN) + "</Group>", 1)

    cols = [5.2, 1.6, 2.6, 2.6, 3.8, 2.2]
    # Hoechsthoehe = Kopf + groesste Gruppe (Band, 5 Arten, Zwischensumme) + 5 weitere Gruppen + "und n weitere" + Summe
    kopf_h, band_h, det_h, sub_h, rest_h, tot_h = 0.5, 0.5, 0.42, 0.42, 0.42, 0.55
    feld_h = 7.0
    hoechst = kopf_h + band_h + T03_ARTEN * det_h + sub_h + (T03_GRUPPEN - 1) * band_h + rest_h + tot_h     # 6,99 cm
    assert hoechst <= feld_h, "T060: Hoechsthoehe %.2f cm passt nicht in das Feld von %.2f cm" % (hoechst, feld_h)

    def bandzahl(name, expr, unit, fmt=None):
        """Wert im Gruppenkopf: nur wenn die Gruppe eine Zeile ist (eine Bauteilart oder nicht die groesste Gruppe)."""
        wert = fm(expr) if fmt is None else 'Format(%s, "%s")' % (expr, fmt)
        runs = [c.run('=IIf(%s, %s, "")' % (einzeln, wert), 9.5, c.INK, c.F_SEMI)]
        if unit:
            runs.append(c.run('=IIf(%s, " %s", "")' % (einzeln, unit), 8, c.FAINT))
        return c.cell(name, c.para(runs), "Right", bg=c.SURFACE, pad=(4, 1, 4, 1))

    anteil = "IIf(%s = 0, 0.0, %s / %s)" % (gesamt, VOLUMEN, gesamt)
    zeigt_g = 'Sum(IIf(%s, 1, 0), "S5_T3")' % MIT_MATERIAL
    rows = [
        (kopf_h, [kopf("S5_T3_H1", "Bauteil"), kopf("S5_T3_H2", "Anzahl", "Right"), kopf("S5_T3_H3", "Fläche", "Right"),
                  kopf("S5_T3_H4", "Volumen", "Right"), kopf("S5_T3_H5", "Einzelbauteile"), kopf("S5_T3_H6", "Anteil", "Right")]),
        (band_h, [
            c.cell("S5_T3_B1", c.para([c.run("■  ", 8, MAT_FARBE, b.SYMBOL), c.run("=" + MATGRUPPE, 9.5, c.INK, c.F_SEMI),
                                       c.run('="   " & IIf(CountDistinct(%s) = 1, Code.Art(First(Fields!ObjNr.Value)), CountDistinct(%s) & " Bauteilarten")'
                                             % (ART, ART), 8, c.MUTED)]),
                   bg=c.SURFACE, pad=(8, 1, 4, 1)),
            bandzahl("S5_T3_B2", "CountRows()", "", "N0"),
            bandzahl("S5_T3_B3", FLAECHE, "m²"),
            bandzahl("S5_T3_B4", VOLUMEN, "m³"),
            c.rect("S5_T3_B5", None, 0, 0, 0, spark("S5_Spark"), bg=c.SURFACE),
            c.cell("S5_T3_B6", c.run('=IIf(%s, Format(%s, "0.0 %%"), "")' % (einzeln, anteil), 9.5, c.INK, c.F_SEMI), "Right",
                   bg=c.SURFACE, pad=(4, 1, 4, 1))]),
        (det_h, [
            c.cell("S5_T3_D1", c.run("=" + ART, 9, c.TEXT), border_xml=ROW, pad=(20, 0, 4, 0)),
            c.cell("S5_T3_D2", c.run("=CountRows()", 9.5, c.TEXT, fmt="N0"), "Right", border_xml=ROW, pad=(4, 0, 4, 0)),
            zahl("S5_T3_D3", FLAECHE, "m²"),
            zahl("S5_T3_D4", VOLUMEN, "m³", font=c.F_SEMI, color=c.INK),
            c.cell("S5_T3_D5", c.run("", 9), border_xml=ROW),
            c.cell("S5_T3_D6", c.run("=" + anteil, 9.5, c.TEXT, fmt="0.0 %"), "Right", border_xml=ROW, pad=(4, 0, 4, 0))]),
        (sub_h, [
            c.cell("S5_T3_S1", c.run("Zwischensumme", 8, c.MUTED, c.F_SEMI), border_xml=ROW, pad=(20, 0, 4, 0)),
            c.cell("S5_T3_S2", c.run("=CountRows()", 9.5, c.INK, c.F_SEMI, fmt="N0"), "Right", border_xml=ROW, pad=(4, 0, 4, 0)),
            zahl("S5_T3_S3", FLAECHE, "m²", font=c.F_SEMI, color=c.INK),
            zahl("S5_T3_S4", VOLUMEN, "m³", font=c.F_SEMI, color=c.INK),
            c.cell("S5_T3_S5", c.run("", 9), border_xml=ROW),
            c.cell("S5_T3_S6", c.run("=" + anteil, 9.5, c.INK, c.F_SEMI, fmt="0.0 %"), "Right", border_xml=ROW, pad=(4, 0, 4, 0))]),
        (rest_h, [
            c.cell("S5_T3_R0", c.run("", 7), border_xml=ROW),
            (c.cell("S5_T3_R1", c.run('="… und " & (%s - %d) & " weitere Materialgruppen"' % (n_gruppen, T03_GRUPPEN), 7.5, c.MUTED),
                    border_xml=ROW, pad=(4, 0, 4, 0)), 5),
            None, None, None, None]),
        (tot_h, [
            c.cell("S5_T3_G1", c.run("Gesamtsumme", 9.5, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(8, 2, 4, 2)),
            c.cell("S5_T3_G2", c.run("=" + ganz(anzahl(MIT_MATERIAL, ALLE)), 9.5, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE),
            zahl("S5_T3_G3", summe("Flaeche", MIT_MATERIAL, ALLE), "m²", font=c.F_SEMI, color=c.INK, border_xml=SUMLINE),
            zahl("S5_T3_G4", gesamt, "m³", font=c.F_SEMI, color=c.INK, border_xml=SUMLINE),
            c.cell("S5_T3_G5", c.run("", 9), border_xml=SUMLINE),
            c.cell("S5_T3_G6", c.run("100 %", 9.5, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE)]),
    ]
    ausblenden = versteckt('CountDistinct(%s, "S5_T3_Mat") = 1 Or Not (%s)' % (ART, groesste))
    members = (
        KOPFZEILE
        + '<TablixMember><Group Name="S5_T3_Mat"><GroupExpressions><GroupExpression>=%s</GroupExpression></GroupExpressions>%s</Group>'
          "<SortExpressions><SortExpression><Value>=%s</Value></SortExpression></SortExpressions>"
          "<TablixMembers>"
          "<TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>"
          '<TablixMember><Group Name="S5_T3_Obj"><GroupExpressions><GroupExpression>=%s</GroupExpression></GroupExpressions></Group>'
          "<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression></SortExpressions>%s</TablixMember>"
          "<TablixMember>%s<KeepWithGroup>Before</KeepWithGroup></TablixMember>"
          "</TablixMembers></TablixMember>"
        % (c.esc(MATGRUPPE), c.topn(VOLUMEN, T03_GRUPPEN), c.esc(ORDNUNG), c.esc(ART), c.esc(VOLUMEN), ausblenden, ausblenden)
        + rest_zeile("%s <= %d" % (n_gruppen, T03_GRUPPEN)) + FUSSZEILE)
    tab = tablix("S5_T3", cols, rows, members, raw(MIT_MATERIAL))
    items += tabellenfeld("S5_T3_Feld", top + 1.45, left, w, feld_h, tab)
    items += etikett("S5_T3_E", top + 8.5, left, w, "T060",
                     "Zeilengruppen Materialgruppe (höchstens 6) und Bauteilart; Einzelzeilen und Zwischensumme nur für die größte Gruppe, alle anderen eine Zeile", h=0.3)
    items += etikett("S5_T3_E2", top + 8.85, left, w, "T070",
                     "Mini-Säulen im Gruppenkopf: die 12 größten Einzelbauteile je Gruppe, absteigend nach Volumen", h=0.3)
    return items


# ---------------------------------------------------------------- Seite
def seite():
    x0, w = c.INSET, c.CONTENT_W
    items = seitenkopf(5, "Tabellen, die zeigen statt zählen", "Zellenbalken, Farbskala, Symbole, Zwischensummen")
    items += t020(3.3, x0, SPALTE_W)
    items += t030(3.3, x0 + SPALTE_W + 0.4, SPALTE_W)
    items += t040(11.6, x0, w)
    items += t060(18.9, x0, w)
    return items
