# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Wandbelag" (RDL 2016) nach out/Report_Master_Wandbelag.rdlc.

Wandflaechen je Raum aus den Seitenflaechen des Raumausbaus (@OBJ@ = 62). Eine Zeile = ein Belag (Innenputz,
Anstrich ...) einer Raum-Seitenflaeche. Raeume ohne Ausbau liefern keine Zeile.

    python build_wandbelag.py              schreibt out/Report_Master_Wandbelag.rdlc
    python build_wandbelag.py --render     rendert zusaetzlich kopflos nach abwicklung/aus/png_wandbelag_bsp (daten/wandbelag_bsp.json)
    python build_wandbelag.py --render --daten=viel         anderer Datensatz (daten/<name>.json, aus/png_<name>): 40 Raeume mit 3-4 Belaegen,
                                                            lange Namen, grosse Flaechen

Ausgeliefert wird der Beispieldatensatz wandbelag_bsp (9 Raeume des eigenen Testgebaeudes, erzeugt von daten/make_wandbelag_bsp.py).
Eigene Datensaetze: --daten=<name> nimmt die Datei daten/<name>.json.

Bausteine (angemeldet mit @b.baustein): K060 Kennzahl-Kacheln, D160 Balken Wandflaeche je Raum,
T080 Wandflaechen je Raum (Kreuztabelle mit Zellenbalken). Elementnamen beginnen mit "W_". Eine Seite.
Datenfest: Belaege hoechstens 3 (die flaechengroessten), Tabelle 14 Raeume, Diagramm 8.

Allplans Aufmassskizze (@205@ mit Projection=10) wird abgefragt, aber NICHT gezeigt: der Anwender hat sie am
2026-11-18 als unlesbar verworfen (Wandstuecke kreuz und quer, Zahlen uebereinander, auch vergroessert). Die Spalte
bleibt in der Abfrage, weil die Abfrage nur in dieser Form in Allplan belegt ist.

Wandflaeche eines Raums = die groesste Belagsflaeche des Raums (Putz und Anstrich liegen auf derselben Wand und
duerfen nicht addiert werden). Die Leibung steht an jedem Belag derselben Seitenflaeche; sie wird nur an der
ersten Schicht (Nr endet auf "/01") gezaehlt.
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
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "wandbelag_bsp")
JSON = os.environ.get("WANDBELAG_JSON", os.path.join(HERE, "daten", DATEN + ".json"))
AUS = os.environ.get("WANDBELAG_AUS", os.path.join(HERE, "aus", "png_" + DATEN))

MAX_BELAEGE = 3        # Spalten der Kreuztabelle und Kacheln
MAX_TABELLE = 14       # Raeume in der Tabelle
MAX_DIAGRAMM = 8       # Balken im Diagramm

# ---------------------------------------------------------------- Daten
# Die QT-Spalte (Flaeche) muss VOR dem Bild stehen, sonst liefert Allplan weder Skizze noch Rechenansatz (gemessen).
QUERY = """SELECT
       @10@[Name=Nr],
       @209@[Name=Gewerk],
       @508@[Name=Material],
       [Name=Raum|f=PARENT(@507@)],
       [Name=Funktion|f=PARENT(@506@)],
       [Name=RaumNr|f=PARENT(@10@)],
       [Name=Flaeche|Fmt=G12.0|f=QT(@295@;;;;@205@213@)],
       @205@[Name=Bild|Projection=10|Width=120|Height=60|GText=HD],
       @225@[Name=Abmessungen],
       @211@[Name=Dicke],
       @213@[Name=Leibung]
FROM [Type=0,Filter=@OBJ@.eq.62]
"""
FIELDS = [("Nr", "String"), ("Gewerk", "String"), ("Material", "String"), ("Raum", "String"), ("Funktion", "String"),
          ("RaumNr", "String"), ("Flaeche", "Double"), ("Bild", "Byte[]"), ("Abmessungen", "String"),
          ("Dicke", "Double"), ("Leibung", "Double")]

ALLE = "AllplanReport"
FL = "CDbl(Fields!Flaeche.Value)"
ERSTE_SCHICHT = 'Right(Fields!Nr.Value, 3) = "/01"'
LEIBUNG = "Sum(IIf(%s, CDbl(Fields!Leibung.Value), 0.0)%s)"
LEIBUNG_ALLE = LEIBUNG % (ERSTE_SCHICHT, ', "%s"' % ALLE)
RAUM_ANZAHL = 'CountDistinct(Fields!RaumNr.Value, "%s")' % ALLE
# Rang eines Raums (Gruppen-Bereich): groesste Belagsflaeche, Raum-ID als eindeutiger Nachrang (TopN nimmt gleiche Werte sonst alle mit)
RAUM_RANG = "Max(%s) + Val(Right(Max(Fields!RaumNr.Value), 8)) / 1000000000000" % FL
MAT_RANG = ("Sum(%s) + CDbl(Asc(Left(Min(Fields!Material.Value) & \"   \", 1))) * 0.000001"
            " + CDbl(Asc(Mid(Min(Fields!Material.Value) & \"   \", 2, 1))) * 0.000000001" % FL)

HEAD = c.edge(["Bottom"], c.INK, "1pt")
ROW = c.edge(["Bottom"], c.HAIR, "0.75pt")
SUMLINE = c.edge(["Top"], c.INK, "1pt")
RAHMEN = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR
ZOOM_RAUM = '="Zoom:" + First(Fields!RaumNr.Value) + ",Mark:" + First(Fields!RaumNr.Value)'


# ---------------------------------------------------------------- Hilfen
def kurz(x, n):
    """Text auf n Zeichen kuerzen, Auslassung als Punkte (Zellen wachsen nicht, abgeschnitten wirkt kaputt)."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (x, n, x, n - 1, x)


def fm(x):
    """Flaeche: ab 1.000 ganze Zahl, sonst eine Nachkommastelle."""
    return 'Format(%s, IIf(%s >= 1000, "#,##0", "#,##0.0"))' % (x, x)


RAUM_T = "First(Fields!Raum.Value)"
FKT_T = "First(Fields!Funktion.Value)"
# Anzeigename eines Raums (Gruppen-Bereich): Nummer + Nutzung; ohne Nutzung nur die Nummer bzw. der Text aus Raum
NAME_RAUM = kurz(RAUM_T, 18)
NAME_FKT = 'IIf(Len(%s) > 0, "   " & %s, "")' % (FKT_T, kurz(FKT_T, 20))


def sortiert(tablix_xml, *ausdruecke):
    """Sortierung der ganzen Datenregion (vor dem Gruppieren): bestimmt, welche Zeile First() einer Gruppe liefert."""
    srt = "<SortExpressions>%s</SortExpressions>" % "".join(
        "<SortExpression><Value>%s</Value>%s</SortExpression>" % (c.esc(e), "<Direction>Descending</Direction>" if d else "")
        for e, d in ausdruecke)
    pos = tablix_xml.rfind("<Top>")
    return tablix_xml[:pos] + srt + tablix_xml[pos:]


def deckel(xml, gruppe, ausdruck, n):
    """Haengt an die Gruppe einen "nur die n groessten"-Filter (Diagramm-Kategorie, Tablix-Gruppe)."""
    f = c.topn(ausdruck, n)
    return re.sub(r'(<Group Name="%s"><GroupExpressions>.*?</GroupExpressions>)' % re.escape(gruppe),
                  lambda m: m.group(1) + f, xml, count=1, flags=re.S)


def kopfzelle(name, label, align=None):
    return c.cell(name, c.run(label, 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=HEAD, pad=(4, 2, 4, 4))


def kh(size, inner):
    return "<TablixHeader><Size>%s</Size><CellContents>%s</CellContents></TablixHeader>" % (c.cm(size), inner)


def tc(inner):
    return "<TablixCell><CellContents>%s</CellContents></TablixCell>" % inner


# ---------------------------------------------------------------- Kopfband
def band():
    x0 = c.INSET
    inner = (c.rect("W_BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.ORANGE)
             + c.text("W_BandOver", 1.4, x0, 12, 0.4, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.SKY, c.F_SEMI))
             + c.text("W_BandTitel", 1.85, x0, 13, 1.45, c.run("Wandbeläge je Raum", 30, c.WHITE, c.F_LIGHT))
             + c.text("W_BandSub", 3.3, x0, 13, 0.55,
                      c.run('=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, "#CBD5E1", c.F))
             + c.text("W_BandRechts", 1.4, x0 + 13, 5, 0.4, c.run("Räume", 8, c.SKY, c.F_SEMI), align="Right")
             + c.text("W_BandRechts2", 1.85, x0 + 13, 5, 1.45,
                      c.para([c.run("=Format(%s, \"N0\")" % RAUM_ANZAHL, 30, c.WHITE, c.F_LIGHT)], "Right"))
             + c.text("W_BandRechts3", 3.3, x0 + 13, 5, 0.55, c.run("mit Raumausbau", 9, "#CBD5E1", c.F), align="Right"))
    return c.rect("W_Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


def kachel(name, kw, wert, einheit, label, note):
    """Kennzahl-Kachel als Tabellenzelle (ohne Lage): grosse Zahl, Einheit, Beschriftung, Fussnote (alles Ausdruecke)."""
    inner = (c.rect(name + "_a", 0, 0, kw, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, kw - 0.4, 1.05,
                      c.para([c.run("=" + wert, 22, c.INK, c.F_LIGHT), c.run(einheit, 10, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, kw - 0.4, 0.37, c.run(label, 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, kw - 0.4, 0.4, c.run(note, 7, c.MUTED, c.F)))
    return c.rect(name, None, 0, 0, 0, inner, bg=c.SURFACE)


def kacheln(name, top, left, kw, gap):
    """Eine Tablix, vier Kacheln: die flaechengroessten Belaege (Spaltengruppe Material, TopN 3), danach - ohne Luecke,
    auch wenn es weniger Belaege gibt - die Leibung als feste letzte Spalte."""
    s = "Sum(%s)" % FL
    mat = 'IIf(Len(Fields!Material.Value) = 0, "ohne Angabe", Fields!Material.Value)'
    n = "CountDistinct(Fields!RaumNr.Value)"
    belag = kachel(name + "_B", kw, 'Format(%s, IIf(%s >= 100, "#,##0", "N1"))' % (s, s), " m²", "=UCase(%s)" % kurz(mat, 24),
                   '=%s & IIf(%s = 1, " Raum", " Räume")' % (n, n))
    leib = kachel(name + "_L", kw, 'Format(%s, "N1")' % (LEIBUNG % (ERSTE_SCHICHT, "")), " m", "LEIBUNG GESAMT", "Länge aller Leibungen")
    luecke = c.text(name + "_Luecke", None, 0, 0, 0, c.run("", 6))
    xml = ('<Tablix Name="%s_Tb"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn>'
           "<TablixColumn><Width>%s</Width></TablixColumn><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>"
           "<TablixRows><TablixRow><Height>2.55cm</Height><TablixCells>%s%s%s</TablixCells></TablixRow></TablixRows></TablixBody>"
           '<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="%s_G"><GroupExpressions>'
           "<GroupExpression>=Fields!Material.Value</GroupExpression></GroupExpressions>%s</Group>"
           "<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression></SortExpressions>"
           "<TablixMembers><TablixMember/><TablixMember/></TablixMembers></TablixMember><TablixMember/></TablixMembers></TablixColumnHierarchy>"
           "<TablixRowHierarchy><TablixMembers><TablixMember/></TablixMembers></TablixRowHierarchy>"
           "<DataSetName>%s</DataSetName><Top>0cm</Top><Left>0cm</Left><Height>2.55cm</Height><Width>%s</Width>"
           "<Style><Border><Style>None</Style></Border></Style></Tablix>"
           % (name, c.cm(kw), c.cm(gap), c.cm(kw), tc(belag), tc(luecke), tc(leib), name, c.topn(MAT_RANG, MAX_BELAEGE),
              c.esc(MAT_RANG), ALLE, c.cm(2 * kw + gap)))
    return c.rect(name, top, left, MAX_BELAEGE * (kw + gap) + kw, 2.55, xml)


@b.baustein("K060", "Kennzahl-Kacheln")
def k060(top, left, w):
    """Wandflaeche je Belag (die 3 flaechengroessten) und Leibungslaenge gesamt."""
    gap = 0.3
    kw = (w - 3 * gap) / 4
    items = kacheln("W_K", top, left, kw, gap)
    items += b.etikett("W_E1", top + 2.65, left, w, "K060",
                       "Kachel je Belag: Spaltengruppe Material, Deckel 3 (c.topn); Leibung je Seitenfläche einmal (Schicht /01)")
    return items


# ---------------------------------------------------------------- T080 Kreuztabelle
def balken_zelle(name):
    """Zellenbalken: groesste Belagsflaeche des Raums, Massstab = groesster Raum; der groesste Balken in Akzentfarbe."""
    wert = "Max(%s)" % FL
    maxwert = 'Max(%s, "%s")' % (FL, ALLE)
    return b.in_cell(v.chart(
        name, 0, 0, 1, 1,
        [v.S("V", {"Y": "=" + wert}, typ="Bar", sub="Plain",
             pstyle="<Color>%s</Color>" % c.esc('=IIf(%s = %s, "%s", "%s")' % (wert, maxwert, c.ORANGE, c.BLUE)),
             custom_xml=v.custom(PointWidth="0.42"))],
        [], nomember=True, dataset=False,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)],
                     val_axes=[v.axis("Primary", visible=False, minimum="0", maximum="=" + maxwert)],
                     pos=(0, 0, 100, 100), inner=(4, 4, 90, 92))))


RAUM_W, MAT_W, LEIB_W = 4.8, 2.3, 1.8
KOPF_H, ZEILE_H, REST_H, SUM_H, ETI_H = 0.85, 0.55, 0.5, 0.6, 0.45
TABELLE_H = KOPF_H + MAX_TABELLE * ZEILE_H + REST_H + SUM_H + ETI_H      # Kopf + Raumzeilen + "... und n" + Summe + Etikett
# Anzahl der Belag-Spalten, die wirklich erscheinen (die Spaltengruppe hat den Deckel 3)
N_BELAEGE = 'IIf(CountDistinct(Fields!Material.Value, "%s") > %d, %d, CountDistinct(Fields!Material.Value, "%s"))' % (
    ALLE, MAX_BELAEGE, MAX_BELAEGE, ALLE)


@b.baustein("T080", "Wandflächen je Raum (Kreuztabelle)")
def t080(top, left, w):
    items = b.overline("W_A2", top, left, w, "Wandflächen", "Wandflächen je Raum")
    mat_wert = "Sum(%s)" % FL
    leib_wert = LEIBUNG % (ERSTE_SCHICHT, "")
    rest_n = "(%s - %d)" % (RAUM_ANZAHL, MAX_TABELLE)
    # Der Zellenbalken fuellt den Rest der Breite: je nach Zahl der Belag-Spalten (3, 2, 1) erscheint genau eine von drei
    # Spalten-Varianten, die anderen sind ausgeblendet und fallen weg - so endet die Tabelle immer buendig bei 18 cm.
    breite = [c.CONTENT_W - RAUM_W - (MAX_BELAEGE - k) * MAT_W - LEIB_W for k in range(MAX_BELAEGE)]    # fuer 3, 2, 1 Belag-Spalten
    bal_breiten = [(breite[0], "%s < %d" % (N_BELAEGE, MAX_BELAEGE)),
                   (breite[1], "%s <> %d" % (N_BELAEGE, MAX_BELAEGE - 1)),
                   (breite[2], "%s > 1" % N_BELAEGE)]

    mat_zelle = c.cell("W_T2_Z", c.para([c.run('=IIf(%s = 0, "–", %s)' % (mat_wert, fm(mat_wert)), 9.5, c.TEXT),
                                        c.run('=IIf(%s = 0, "", " m²")' % mat_wert, 7, c.FAINT)]),
                       "Right", border_xml=ROW, pad=(4, 0, 6, 0))
    leib_zelle = c.cell("W_T2_L", c.para([c.run('=IIf(%s = 0, "–", Format(%s, "N1"))' % (leib_wert, leib_wert), 9, c.MUTED),
                                         c.run('=IIf(%s = 0, "", " m")' % leib_wert, 7, c.FAINT)]),
                        "Right", border_xml=ROW, pad=(4, 0, 6, 0))
    sum_mat = c.cell("W_T2_SM", c.para([c.run("=" + fm(mat_wert), 9.5, c.INK, c.F_SEMI), c.run(" m²", 7, c.FAINT)]),
                     "Right", border_xml=SUMLINE, pad=(4, 0, 6, 0))
    sum_leib = c.cell("W_T2_SL", c.para([c.run('=Format(%s, "N1")' % LEIBUNG_ALLE.replace(', "%s"' % ALLE, ""), 9, c.INK, c.F_SEMI),
                                        c.run(" m", 7, c.FAINT)]), "Right", border_xml=SUMLINE, pad=(4, 0, 6, 0))

    def leer(name, rand=""):
        return tc(c.cell(name, c.run("", 7), border_xml=rand))

    nb = len(bal_breiten)
    # Spalten: Belag (dynamisch), Leibung, Balken-Varianten
    spalten = "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(x)
                      for x in [MAT_W, LEIB_W] + [bw for bw, _h in bal_breiten])
    zeile_daten = tc(mat_zelle) + tc(leib_zelle) + "".join(
        tc(c.rect("W_T2_B%d" % i, None, 0, 0, 0, balken_zelle("W_ZBalken%d" % i), border_xml=ROW)) for i in range(nb))
    zeile_rest = "".join(leer("W_T2_R%d" % i) for i in range(2 + nb))
    zeile_sum = tc(sum_mat) + tc(sum_leib) + "".join(leer("W_T2_S%d" % i, SUMLINE) for i in range(nb))
    zeile_eti = "".join(leer("W_T2_E%d" % i) for i in range(2 + nb))
    body = ("<TablixBody><TablixColumns>%s</TablixColumns><TablixRows>"
            "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>"
            "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>"
            "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>"
            "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>"
            "</TablixRows></TablixBody>") % (
        spalten, c.cm(ZEILE_H), zeile_daten, c.cm(REST_H), zeile_rest, c.cm(SUM_H), zeile_sum, c.cm(ETI_H), zeile_eti)

    mat_kopf = c.cell("W_T2_HM", c.run('=UCase(%s)' % kurz('IIf(Len(Fields!Material.Value) = 0, "ohne Angabe", Fields!Material.Value)', 16),
                                       7, c.MUTED, c.F_SEMI), "Right", "Bottom", border_xml=HEAD, pad=(2, 2, 6, 4))
    bal_koepfe = "".join(
        "<TablixMember><Visibility><Hidden>%s</Hidden></Visibility>%s</TablixMember>"
        % (c.esc("=" + hid), kh(KOPF_H, kopfzelle("W_T2_HB%d" % i, "GRÖSSTER BELAG"))) for i, (_bw, hid) in enumerate(bal_breiten))
    col_h = ("<TablixColumnHierarchy><TablixMembers>"
             '<TablixMember><Group Name="W_T2_Mat"><GroupExpressions><GroupExpression>=Fields!Material.Value</GroupExpression>'
             "</GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>=Sum(%s)</Value><Direction>Descending</Direction>"
             "</SortExpression></SortExpressions>%s</TablixMember>"
             "<TablixMember>%s</TablixMember>%s</TablixMembers></TablixColumnHierarchy>") % (
        c.topn(MAT_RANG, MAX_BELAEGE), c.esc(FL), kh(KOPF_H, mat_kopf),
        kh(KOPF_H, kopfzelle("W_T2_HL", "LEIBUNG", "Right").replace("<PaddingRight>4pt", "<PaddingRight>6pt")), bal_koepfe)

    raum_zelle = c.cell("W_T2_RH", c.para([c.run("=" + NAME_RAUM, 9.5, c.INK, c.F_SEMI), c.run("=" + NAME_FKT, 8.5, c.TEXT)]),
                        border_xml=ROW, pad=(4, 0, 4, 0))
    rest_zelle = c.cell("W_T2_RR", c.run('="… und " & %s & " weitere Räume"' % rest_n, 7.5, c.MUTED), pad=(4, 0, 4, 0))
    sum_zelle = c.cell("W_T2_RS", c.run("Summe alle Räume", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 0, 4, 0))
    # Das Etikett steht als letzte Tabellenzeile: es haengt so immer direkt unter der Tabelle, egal wie viele Raeume sie hat.
    b.KATALOG.append((b.SEITE_AKTUELL[0], "T080", "Kreuztabelle Raum × Belag (Spaltengruppe, Deckel 3), Zellenbalken je Raum, "
                                                  "Deckel 14 Räume, Summe über alle"))
    eti_zelle = c.cell("W_T2_RE", c.para([c.run("T080  ", 6.5, c.BLUE, c.F_SEMI), c.run("Kreuztabelle, Deckel 14 Räume", 6.5, c.FAINT)]),
                       valign="Top", pad=(4, 4, 0, 0))
    zeilen_h = ("<TablixRowHierarchy><TablixMembers>"
                '<TablixMember><Group Name="W_T2_Raum"><GroupExpressions><GroupExpression>=Fields!RaumNr.Value</GroupExpression>'
                "</GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>=Min(Fields!Raum.Value)</Value></SortExpression>"
                "</SortExpressions>%s</TablixMember>"
                "<TablixMember><Visibility><Hidden>%s</Hidden></Visibility>%s</TablixMember>"
                "<TablixMember>%s</TablixMember><TablixMember>%s</TablixMember></TablixMembers></TablixRowHierarchy>") % (
        c.topn(RAUM_RANG, MAX_TABELLE), kh(RAUM_W, raum_zelle), c.esc("=%s <= 0" % rest_n),
        kh(RAUM_W, rest_zelle), kh(RAUM_W, sum_zelle), kh(RAUM_W, eti_zelle))
    ecke = ("<TablixCorner><TablixCornerRows><TablixCornerRow><TablixCornerCell><CellContents>%s</CellContents></TablixCornerCell>"
            "</TablixCornerRow></TablixCornerRows></TablixCorner>") % kopfzelle("W_T2_Ecke", "RAUM")
    tab = ('<Tablix Name="W_T2">%s%s%s%s<DataSetName>%s</DataSetName>'
           "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>") % (
        ecke, body, col_h, zeilen_h, ALLE, c.cm(TABELLE_H), c.cm(c.CONTENT_W))
    items += c.rect("W_T2_Feld", top + 1.45, left, w, TABELLE_H + 0.05, tab)
    return items


# ---------------------------------------------------------------- D160 Balken
@b.baustein("D160", "Balken Wandfläche je Raum")
def d160(top, left, w, h=5.4):
    items = b.overline("W_A3", top, left, w, "Wandfläche je Raum", "Die 8 größten Wandflächen")
    fest = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"
    wert = "Max(%s)" % FL
    achse = "=Max(Max(%s, \"W_Ch_Cat1\"), \"W_Ch\") * 1.25" % FL
    label_x = '%s & IIf(Len(First(Fields!Funktion.Value)) > 0, "  " & %s, "")' % (kurz("First(Fields!Raum.Value)", 14),
                                                                                   kurz("First(Fields!Funktion.Value)", 16))
    bars = v.chart(
        "W_Ch", top + 1.45, left, w, h,
        [v.S("V", {"Y": "=" + wert}, typ="Bar", sub="Plain", color=c.BLUE,
             axislabel="=" + label_x,
             label=v.dlabel(fmt="#,##0.0 m²", size="8.5pt", color=c.TEXT),
             custom_xml=v.custom(PointWidth="0.55", BarLabelStyle="Outside"))],
        [("=Fields!RaumNr.Value", "=" + RAUM_RANG, None)],
        areas=v.area(cat_axes=[v.axis("Primary", interval="1", line=False, size="8.5pt", extra=fest)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0", maximum=achse)],
                     pos=(0, 0, 100, 100)))
    items += deckel(bars, "W_Ch_Cat1", RAUM_RANG, MAX_DIAGRAMM)
    items += b.etikett("W_E3", top + 1.45 + h + 0.05, left, w, "D160",
                       "Balken: größte Belagsfläche je Raum, Deckel 8 (TopN an der Kategorie), Wert am Balken")
    return items


# ---------------------------------------------------------------- B100 Skizzenkarten
# ---------------------------------------------------------------- Seiten
def seite1():
    x0, w = c.INSET, c.CONTENT_W
    items = band()
    items += k060(5.05, x0, w)
    items += d160(8.4, x0, w)
    items += t080(16.35, x0, w)
    return items


SEITEN = [("Wandbeläge je Raum", seite1)]


def build():
    pages = [fn() for _t, fn in SEITEN]
    xml = c.report(pages, [c.dataset(ALLE, QUERY, FIELDS)], footer_xml=b.fuss(), code=b.CODE, labels=[t for t, _f in SEITEN])
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Wandbelag.rdlc")
    c.save(ziel, xml)
    return ziel


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--daten"})
    ziel = build()
    print(ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        c.rendern(ziel, JSON, AUS)
