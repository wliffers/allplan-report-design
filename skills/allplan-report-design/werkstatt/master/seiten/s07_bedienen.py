# -*- coding: utf-8 -*-
"""Seite 7 - Bedienen: der Report als Werkzeug.

Was ein Report ueber das Aussehen hinaus fuer den Anwender TUN kann: Auffaelligkeiten zuerst zeigen,
per Klick ins Modell springen, Details aufklappen, per Klick sortieren, mit Stellschrauben rechnen.
Alle Werte kommen aus den Report-Parametern (bausteine.PARAMS) und dem einen DataSet "AllplanReport".

Datenfest: jede Liste hat einen Deckel (Hinweise 5 Zeilen, Kosten 5 Materialgruppen, Aufklapptabelle 5 Gruppen,
je Gruppe 5 Einzelzeilen), Material wird ueber die Materialgruppe erkannt (bausteine.MATGRUPPE), Preise gibt es nur
fuer vier Gruppen. Jeder Block ist eine eigene Funktion mit fester Kennung (U020 ... U010)."""
import re

import core as c
import viz as v
import bausteine as b
from bausteine import (ROHBAU, WAND, RAUM, FENSTER, TUER, MIT_MATERIAL, MAT_FARBE, MATGRUPPE, IST_BETON, PREIS, ZOOM,
                       summe, anzahl, quote, overline, etikett, klick, sortierbar)

TITEL = "Bedienen: der Report als Werkzeug"
DS = "AllplanReport"
MAX_TUEREN = 3          # bis zu so vielen Tuer-Zeilen; sind es mehr, zeigt die Liste eine weniger und "und n weitere" (Platz ist reserviert)
MAX_GRUPPEN = 5         # Materialgruppen in Kostentabelle und Aufklapptabelle
MAX_EINZEL = 5          # Einzelzeilen je Gruppe, wenn aufgeklappt
PREIS_GRUPPEN = ["Beton", "Mauerwerk", "Dämmung", "Gipskarton"]   # Gruppen, fuer die bausteine.PREIS einen Preis kennt

# ---------------------------------------------------------------- Regeln und Zahlen (Ausdruecke)
T_COND = "(%s And CDbl(Fields!Laenge.Value) < Parameters!Tuer_Mindestbreite.Value)" % TUER
R_COND = '(%s And Len(Trim(CStr(Fields!Bezeichnung.Value & ""))) = 0)' % RAUM
N_T = anzahl(T_COND, DS)
N_R = anzahl(R_COND, DS)
N_RAUM = anzahl(RAUM, DS)
# Bauteile ohne Materialangabe: stehen nicht in den Mengen, der Hinweis sagt es
O_COND = '(%s And Fields!Material.Value = "")' % ROHBAU
N_O = anzahl(O_COND, DS)
VOL_O = summe("Volumen", O_COND, DS)
N_FENSTER = anzahl(FENSTER, DS)
AUSSENWAND = summe("Flaeche", "(%s And %s)" % (WAND, IST_BETON), DS)   # Wandschichten aus Beton (Materialgruppe, nicht Name)
ANTEIL = quote(summe("Flaeche", FENSTER, DS), AUSSENWAND)             # Fensterflaechenanteil 0..1
FENSTER_OK = "(%s > 0 And %s > 0)" % (AUSSENWAND, N_FENSTER)           # ohne Fenster oder Betonwand keine Anteilsaussage
F_FLAG = "(%s And (%s) * 100 < Parameters!Ziel_Fensteranteil.Value)" % (FENSTER_OK, ANTEIL)
N = "(%s + IIf(%s > 0, 1, 0) + IIf(%s, 1, 0) + IIf(%s > 0, 1, 0))" % (N_T, N_R, F_FLAG, N_O)    # Anzahl der Hinweise
KEINE = "(%s = 0)" % N
# schmalste zuerst; die Nr als Winziges dazu, damit gleich breite Tueren eine feste Reihenfolge haben (BottomN zaehlt sonst Gleiche mit)
TUER_REIHENFOLGE = "=CDbl(Fields!Laenge.Value) + Val(Right(Fields!Nr.Value, 6)) / 1000000000.0"
NACHRANG = "Val(Right(Fields!Nr.Value, 6)) / 1000000000.0"
VOLUMEN = "Sum(CDbl(Fields!Volumen.Value))"
IST_PREIS = "(%s)" % " Or ".join('%s = "%s"' % (MATGRUPPE, g) for g in PREIS_GRUPPEN)


def deckel(xml, gruppe, ausdruck, n):
    """Haengt an die benannte Gruppe einen "nur die n groessten"-Filter."""
    f = c.topn(ausdruck, n)
    return re.sub(r'(<Group Name="%s">(?:<GroupExpressions>.*?</GroupExpressions>)?)' % re.escape(gruppe),
                  lambda m: m.group(1) + f, xml, count=1, flags=re.S)


def kurz(x, n):
    """Name auf n Zeichen kuerzen, mit "…" am Ende (Ausdruck): sonst schneidet die Zelle mitten im Wort ab."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (x, n, x, n - 1, x)


def eur(x):
    """Betrag mit Tausenderpunkt; ab einer Million als "1,2 Mio." (passt in jede Zelle)."""
    return 'IIf(%s >= 1000000, Format((%s) / 1000000, "0.0") & " Mio.", Format(%s, "N0"))' % (x, x, x)


def fm(x, grenze=1000):
    return 'Format(%s, IIf(Abs(%s) >= %d, "N0", "N1"))' % (x, x, grenze)


def erster(bedingung):
    """Bauteil-ID des ersten Treffers (Ziel fuer den Klick bei zusammengefassten Hinweisen)."""
    return 'Min(IIf(%s, Fields!Nr.Value, "~"), "%s")' % (bedingung, DS)


def zoom_auf(bedingung):
    return '="Zoom:" & %s & ",Mark:" & %s' % (erster(bedingung), erster(bedingung))


# Kernaussage: groesste Materialgruppe am Bauteilvolumen (Gruppen aus core.MATERIALGRUPPE, keine Projektnamen)
GRUPPEN = [g for g, _f in c.MATERIALGRUPPE]
VOL = {g: summe("Volumen", '(%s And %s = "%s")' % (MIT_MATERIAL, MATGRUPPE, g), DS) for g in GRUPPEN}
MAXV = VOL[GRUPPEN[-1]]
for _g in reversed(GRUPPEN[:-1]):
    MAXV = "System.Math.Max(%s, %s)" % (VOL[_g], MAXV)
GROESSTES = "Switch(%s, True, \"\")" % ", ".join('%s = %s, "%s"' % (VOL[g], MAXV, g) for g in GRUPPEN)
ROHBAU_VOL = summe("Volumen", MIT_MATERIAL, DS)
KOSTEN_ZEILE = "CDbl(Fields!Volumen.Value) * " + PREIS


def symbol(name, text_, farbe, size=9):
    """Farbiges Zeichen in der Symbolschrift (in Roboto fehlen ▲ ● ✓ ■)."""
    return c.cell(name, c.run(text_, size, farbe, b.SYMBOL), "Center", pad=(0, 0, 0, 0),
                  border_xml=c.edge(["Bottom"], c.HAIR, "0.5pt"))


def zeile(h, zellen):
    return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (
        c.cm(h), "".join("<TablixCell><CellContents>%s</CellContents></TablixCell>" % z for z in zellen))


def tablix_raw(name, breiten, zeilen, hierarchie, hoehe, extra=""):
    return ('<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s</TablixRows></TablixBody>'
            "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>"
            "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>%s"
            "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>"
            % (name, "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(x) for x in breiten),
               "".join(zeilen), "<TablixMember/>" * len(breiten), hierarchie, extra, c.cm(hoehe), c.cm(sum(breiten))))


def seite():
    x0, w = c.INSET, c.CONTENT_W
    from bausteine import seitenkopf
    items = seitenkopf(7, "Bedienen: der Report als Werkzeug", "Hinweise, Klick ins Modell, Aufklappen, Was-wäre-wenn")
    items += u010(2.95, x0, w)
    items += k040(4.85, x0, w)
    items += u020(8.85, x0, w)
    items += u030(16.2, x0, w)
    items += u040(23.05, x0, w)
    return items


# ---------------------------------------------------------------- U010 Bedien-Legende (oben: erst erklaeren)
@b.baustein("U010", "Bedien-Legende")
def u010(top, left, w):
    items = ""
    gap = 0.3
    kw = (w - 3 * gap) / 4
    kacheln = [("Klick", "zoomt in Allplan zum Bauteil"), ("Plus-Zeichen", "klappt die Einzelbauteile auf"),
               ("Spaltenkopf", "sortiert die Tabelle"), ("Parameter", "ändern, der Report rechnet neu")]
    reihe = ""
    for i, (kopf, satz) in enumerate(kacheln):
        inner = (c.rect("S7_B05k%d_a" % i, 0, 0, 0.08, 1.4, bg=c.BLUE)
                 + c.text("S7_B05k%d_t" % i, 0.15, 0.4, kw - 0.5, 0.3, c.run(kopf.upper(), 7, c.MUTED, c.F_SEMI))
                 + c.text("S7_B05k%d_s" % i, 0.5, 0.4, kw - 0.5, 0.85, c.run(satz, 8, c.TEXT)))
        reihe += c.rect("S7_B05k%d" % i, 0, i * (kw + gap), kw, 1.4, inner, bg=c.SURFACE)
    # Die Reihe liegt in einem EIGENEN Behaelter (gemessen im Report-Fenster): liegen die vier Kacheln direkt auf der Seite,
    # verschieben ausgeblendete Felder weiter unten (die Haken-Zeile von U020) Kachel 3 und 4 nach links.
    items += c.rect("S7_B05r", top, left, w, 1.4, reihe)
    items += etikett("S7_B05_e", top + 1.45, left, w, "U010", "Bedien-Legende: vier Kacheln, reiner Text - sagt dem Anwender, dass dieser Report bedienbar ist")
    return items


# ---------------------------------------------------------------- K040 Kernaussage
@b.baustein("K040", "Kernaussage")
def k040(top, left, w):
    items = overline("S7_B04", top, left, w, "Kernaussage", "Das Wichtigste in drei Sätzen")
    fl, sb = c.F, c.F_SEMI
    gross = 13

    def r(expr, fett=False, cond=None):
        """Textstueck; mit cond entfaellt es ganz, wenn die Grundlage fehlt."""
        if cond:
            inner = expr[1:] if expr.startswith("=") else '"%s"' % expr
            return c.run('=IIf(%s, %s, "")' % (cond, inner), gross, c.INK if fett else c.TEXT, sb if fett else fl)
        wert = expr
        return c.run(wert, gross, c.INK if fett else c.TEXT, sb if fett else fl)

    ziel = "Parameters!Ziel_Fensteranteil.Value"
    ok_m, ok_f = "%s > 0" % ROHBAU_VOL, FENSTER_OK
    lage = 'Switch((%s) * 100 < %s, "unter", (%s) * 100 > %s, "über", True, "auf")' % (ANTEIL, ziel, ANTEIL, ziel)
    hinweise = ('IIf(%s, "Es gibt keine Auffälligkeiten.", "Es gibt " & IIf(%s = 1, "einen Hinweis", %s & " Hinweise") '
                '& ", die Sie prüfen sollten.")' % (KEINE, N, N))
    satz = c.para([
        r("=" + GROESSTES, True, ok_m), r(" macht ", cond=ok_m), r('=Format(%s, "0 %%")' % quote(MAXV, ROHBAU_VOL), True, ok_m),
        r(" des Bauteilvolumens aus. ", cond=ok_m),
        r("Der Fensterflächenanteil liegt mit ", cond=ok_f), r('=Format(%s, "0 %%")' % ANTEIL, True, ok_f),
        r("=\" \" & %s & \" dem Ziel von \"" % lage, cond=ok_f), r('=Format(%s / 100, "0 %%")' % ziel, True, ok_f),
        r(". ", cond=ok_f), r("=" + hinweise)])
    # Hinweisband: Flaeche MIST, linker Rand 3 pt Akzent, Schrift INK
    inner = c.rect("S7_B04_bar", 0, 0, 0.106, 1.7, bg=c.AKZENT) + c.text("S7_B04_s", 0, 0.5, w - 0.6, 1.7, satz, valign="Middle")
    items += c.rect("S7_B04_feld", top + 1.45, left, w, 1.7, inner, bg=c.MIST)
    items += etikett("S7_B04_e", top + 3.25, left, w, "K040", "Satz aus Ausdrücken (Switch, Format, Max): größte Materialgruppe, Fensteranteil gegen den Parameter Ziel, Zahl der Hinweise")
    return items


# ---------------------------------------------------------------- U020 Bitte pruefen
@b.baustein("U020", "Hinweisliste")
def u020(top, left, w):
    items = overline("S7_B01", top, left, w, "Hinweise", "Bitte prüfen")
    y = top + 1.45

    # Kopfband: grosse Zahl + Satz; ohne Treffer ein ruhiges Haekchen
    teile = ('Mid(IIf(%s > 0, " · " & IIf(%s = 1, "1 Tür zu schmal", %s & " Türen zu schmal"), "")'
             ' & IIf(%s > 0, " · " & IIf(%s = 1, "1 Raum ohne Bezeichnung", %s & " Räume ohne Bezeichnung"), "")'
             ' & IIf(%s, " · Fensteranteil unter Ziel", "")'
             ' & IIf(%s > 0, " · Bauteile ohne Material", ""), 4)' % (N_T, N_T, N_T, N_R, N_R, N_R, F_FLAG, N_O))
    # Zahl der Hinweise und Haken sind EINE Textbox mit zwei Textstuecken (eines davon jeweils leer): zwei Felder auf
    # derselben Stelle ueberlappen sich, und das Report-Fenster schiebt eines weg.
    band = (c.text("S7_B01_n", 0, 0, 1.3, 1.1,
                   c.para([c.run('=IIf(%s, "", Format(%s, "N0"))' % (KEINE, N), 28, c.AKZENT_TEXT, c.F_ZAHL).replace(
                               "<FontSize>28pt</FontSize>", "<FontSize>=%s</FontSize>" % c.esc('IIf(%s >= 100, "16pt", IIf(%s >= 10, "24pt", "28pt"))' % (N, N))),
                           c.run('=IIf(%s, "✓", "")' % KEINE, 22, c.GREEN_TEXT, b.SYMBOL)], "Center"), valign="Middle")
            + c.text("S7_B01_bt", 0.08, 1.34, w - 2.0, 0.55,
                     c.run('=IIf(%s, "Keine Auffälligkeiten", IIf(%s = 1, "Hinweis", "Hinweise") & " aus der Prüfung des Modells")' % (KEINE, N),
                           10.5, c.INK, c.F_SEMI))
            + c.text("S7_B01_bu", 0.66, 1.34, w - 2.0, 0.4,
                     c.run('=IIf(%s, "Türbreite, Raumbezeichnung und Fensteranteil erfüllen die Vorgaben.", %s)' % (KEINE, teile), 8, c.MUTED)))
    items += c.rect("S7_B01_band", y, left, w, 1.1, band, bg=c.SURFACE)

    # Liste: Tuerhinweise je Tuer (Gruppenfilter), Raeume und Fenster als je eine zusammengefasste Zeile
    ly = y + 1.2
    head = c.edge(["Bottom"], c.INK, "1pt")
    row = c.edge(["Bottom"], c.HAIR, "0.5pt")

    def kopfzelle(name, label, align=None):
        return c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=head, pad=(4, 2, 4, 3))

    def zelle(name, runs, align=None, ziel=ZOOM, tip=None):
        x = c.cell(name, runs, align, border_xml=row, pad=(4, 2, 4, 2))
        return klick(x, ziel, tip) if tip is not False else x

    link = lambda n, ziel: zelle(n, c.run("im Modell zeigen ›", 8, c.BLUE, c.F_SEMI), "Right", ziel)
    zoom_tip = "Klick: in Allplan auf das erste betroffene Bauteil zoomen"
    z_raum, z_fenster, z_ohne = zoom_auf(R_COND), zoom_auf(FENSTER), zoom_auf(O_COND)

    kopf = [kopfzelle("S7_LH1", ""), kopfzelle("S7_LH2", "Hinweis"), kopfzelle("S7_LH3", "Bauteil"),
            kopfzelle("S7_LH4", "Wert", "Right"), kopfzelle("S7_LH5", "")]
    tuer = [symbol("S7_LT1", "▲", c.RED_TEXT),
            zelle("S7_LT2", c.run('="Tür unter der Mindestbreite von " & Format(Parameters!Tuer_Mindestbreite.Value, "0.00") & " m"', 9, c.INK, c.F_SEMI)),
            zelle("S7_LT3", c.run("=" + kurz("Fields!Bezeichnung.Value", 20), 9, c.MUTED)),
            zelle("S7_LT4", c.run('=Format(CDbl(Fields!Laenge.Value), "0.0##") & " m"', 9, c.INK, c.F_SEMI), "Right"),
            link("S7_LT5", ZOOM)]
    raum = [symbol("S7_LR1", "●", c.AMBER_TEXT, 8),
            zelle("S7_LR2", c.run('=%s & IIf(%s = 1, " Raum", " Räume") & " ohne Bezeichnung"' % (N_R, N_R), 9, c.INK, c.F_SEMI), ziel=z_raum, tip=zoom_tip),
            zelle("S7_LR3", c.run("Räume", 9, c.MUTED), ziel=z_raum, tip=zoom_tip),
            zelle("S7_LR4", c.run('=%s & " von " & %s' % (N_R, N_RAUM), 9, c.INK, c.F_SEMI), "Right", z_raum, zoom_tip),
            zelle("S7_LR5", c.run("im Modell zeigen ›", 8, c.BLUE, c.F_SEMI), "Right", z_raum, zoom_tip)]
    fenster = [symbol("S7_LF1", "●", c.AMBER_TEXT, 8),
               zelle("S7_LF2", c.run('="Fensterflächenanteil unter dem Ziel von " & Format(Parameters!Ziel_Fensteranteil.Value / 100, "0 %")',
                                     9, c.INK, c.F_SEMI), ziel=z_fenster, tip=zoom_tip),
               zelle("S7_LF3", c.run('=%s & " Fenster"' % N_FENSTER, 9, c.MUTED), ziel=z_fenster, tip=zoom_tip),
               zelle("S7_LF4", c.run('=Format(%s, "0 %%")' % ANTEIL, 9, c.INK, c.F_SEMI), "Right", z_fenster, zoom_tip),
               zelle("S7_LF5", c.run("im Modell zeigen ›", 8, c.BLUE, c.F_SEMI), "Right", z_fenster, zoom_tip)]
    ohne = [symbol("S7_LO1", "●", c.AMBER_TEXT, 8),
            zelle("S7_LO2", c.run('=%s & IIf(%s = 1, " Bauteil", " Bauteile") & " ohne Material · " & %s & " m³ – nicht in den Mengen enthalten"'
                                  % (N_O, N_O, fm(VOL_O, 100)), 9, c.INK, c.F_SEMI), ziel=z_ohne, tip=zoom_tip),
            zelle("S7_LO5", c.run("im Modell zeigen ›", 8, c.BLUE, c.F_SEMI), "Right", z_ohne, zoom_tip)]
    erlaubt = "=IIf(%s <= %d, %d, %d)" % (N_T, MAX_TUEREN, MAX_TUEREN, MAX_TUEREN - 1)
    filter_xml = c.filters(T_COND).replace("</Filters>", (
        "<Filter><FilterExpression>%s</FilterExpression><Operator>BottomN</Operator>"
        "<FilterValues><FilterValue>%s</FilterValue></FilterValues></Filter></Filters>") % (c.esc(TUER_REIHENFOLGE), c.esc(erlaubt)))
    gruppe = ('<TablixMember><Group Name="S7_HT"><GroupExpressions><GroupExpression>=Fields!Nr.Value</GroupExpression></GroupExpressions>%s</Group>'
              "<SortExpressions><SortExpression><Value>%s</Value></SortExpression></SortExpressions></TablixMember>"
              % (filter_xml, c.esc(TUER_REIHENFOLGE)))
    mehr = [c.cell("S7_LM1", c.run("", 8), border_xml=row),
            c.cell("S7_LM2", c.run('="… und " & (%s - %d) & " weitere Türen unter der Mindestbreite"' % (N_T, MAX_TUEREN - 1), 9, c.MUTED),
                   border_xml=row, pad=(4, 2, 4, 2)),
            c.cell("S7_LM5", c.run("", 8), border_xml=row)]
    # "und n weitere": Text ueber drei Spalten (ColSpan), damit er auch in der schmaleren Hinweis-Spalte ganz steht
    zeile_mehr = ("<TablixRow><Height>" + c.cm(0.56) + "</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                  "<TablixCell><CellContents>%s<ColSpan>3</ColSpan></CellContents></TablixCell><TablixCell/><TablixCell/>"
                  "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow>" % tuple(mehr))
    statisch = "<TablixMember><Visibility><Hidden>%s</Hidden></Visibility></TablixMember>"
    hier = ("<TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>" + gruppe
            + statisch % c.esc("=%s <= %d" % (N_T, MAX_TUEREN)) + statisch % c.esc("=%s = 0" % N_R) + statisch % c.esc("=Not %s" % F_FLAG)
            + statisch % c.esc("=%s = 0" % N_O))
    # Zeile "ohne Material": Text ueber drei Spalten (ColSpan), Platz fuer sechs Zeilen im Feld von 3,9 cm
    zeile_ohne = ("<TablixRow><Height>" + c.cm(0.56) + "</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                  "<TablixCell><CellContents>%s<ColSpan>3</ColSpan></CellContents></TablixCell><TablixCell/><TablixCell/>"
                  "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow>" % tuple(ohne))
    tab = tablix_raw("S7_TbHinweis", [1.2, 6.9, 3.5, 2.9, 3.5],   # Wert-Spalte breit genug fuer "260 von 260" in einer Zeile (schmaler bricht die Zahl um)
                     [zeile(0.5, kopf), zeile(0.56, tuer), zeile_mehr] + [zeile(0.56, z) for z in (raum, fenster)] + [zeile_ohne],
                     hier, 3.86, extra="<DataSetName>%s</DataSetName>" % DS)
    items += c.rect("S7_B01_liste", ly, left, w, 3.9, tab, hidden="=" + KEINE)

    # ohne Treffer: drei ruhige Haken statt der Liste
    breite = (w - 2 * 0.3) / 3
    regeln = [c.run("Alle Türen breit genug", 9, c.TEXT), c.run("Alle Räume benannt", 9, c.TEXT),
              c.run('=IIf(%s, "Fensteranteil erreicht das Ziel", "Keine Fenster zum Vergleichen")' % FENSTER_OK, 9, c.TEXT)]
    haken = ""
    for i, regel in enumerate(regeln):
        haken += c.text("S7_B01_g%d" % i, 0, i * (breite + 0.3), breite, 0.7,
                        c.para([c.run("✓  ", 10, c.GREEN_TEXT, b.SYMBOL), regel]), valign="Middle",
                        border_xml=c.edge(["Bottom"], c.HAIR, "0.5pt"))
    # EIN Behaelter mit der Sichtbarkeit (gemessen im Report-Fenster): drei einzeln ausgeblendete Felder direkt auf der Seite
    # verschieben fremde Elemente derselben Seite, die nicht auf ihren Kanten liegen.
    items += c.rect("S7_B01_haken", ly + 0.2, left, w, 0.7, haken, hidden="=Not " + KEINE)
    items += etikett("S7_B01_e", ly + 3.95, left, w, "U020",
                     "Tablix mit Gruppenfilter (Türen) und per Ausdruck sichtbaren Zeilen, BookmarkLink Zoom/Mark je Zeile, Tooltip; ohne Treffer Haken-Zeile")
    return items


# ---------------------------------------------------------------- U030 Was-waere-wenn: Kostenschaetzung
@b.baustein("U030", "Kostenschätzung")
def u030(top, left, w):
    items = overline("S7_B03", top, left, w, "Was wäre wenn", "Kostenschätzung Material")
    y = top + 1.45
    head = c.edge(["Bottom"], c.INK, "1pt")
    row = c.edge(["Bottom"], c.HAIR, "0.5pt")
    tw = 11.0

    def kopf(name, label, align=None):
        return c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=head, pad=(4, 2, 4, 4))

    kosten = "Sum(%s)" % KOSTEN_ZEILE
    gesamt = 'Sum(%s, "S7_TbKosten")' % KOSTEN_ZEILE
    preis_sonst = lambda ausdruck: '=IIf(%s, %s, "–")' % (IST_PREIS, ausdruck)
    schluessel = "%s + %s / 1000000.0" % (kosten, VOLUMEN)       # Gruppen mit Preis zuerst, dann nach Volumen
    cdn = 'CountDistinct(%s, "S7_TbKosten")' % MATGRUPPE
    rows = [
        ("kopf", 0.65, [kopf("S7_KH1", "Material"), kopf("S7_KH2", "Volumen", "Right"), kopf("S7_KH3", "Preis €/m³", "Right"),
                        kopf("S7_KH4", "Kosten", "Right"), kopf("S7_KH5", "Anteil", "Right")]),
        ("daten", 0.6, [
            c.cell("S7_KD1", c.para([c.run("■ ", 9, MAT_FARBE, b.SYMBOL), c.run("=" + MATGRUPPE, 9.5, c.INK, c.F_SEMI)]), border_xml=row),
            c.cell("S7_KD2", c.para([c.run("=" + fm(VOLUMEN), 9.5, c.TEXT), c.run(" m³", 8, c.FAINT)]),
                   "Right", border_xml=row),
            c.cell("S7_KD3", c.run(preis_sonst('Format(%s, "N0")' % PREIS), 9.5, c.BLUE, c.F_SEMI), "Right", border_xml=row),
            c.cell("S7_KD4", c.para([c.run(preis_sonst('%s & " €"' % eur(kosten)), 9.5, c.INK, c.F_SEMI)]), "Right", border_xml=row),
            c.cell("S7_KD5", c.run(preis_sonst('Format(%s, "0 %%")' % quote(kosten, gesamt)), 9.5, c.TEXT), "Right", border_xml=row),
        ]),
        ("fuss", 1.0, [
            c.cell("S7_KF1", c.run('=IIf(%s > %d, "Summe (+" & (%s - %d) & " ohne Preis)", "Summe")' % (cdn, MAX_GRUPPEN, cdn, MAX_GRUPPEN), 9.5, c.INK, c.F_SEMI),
                   valign="Bottom", pad=(4, 0, 4, 0)),            # zwei Zeilen (englisch immer) passen ohne Innenabstand in die Zeile
            c.cell("S7_KF2", c.para([c.run("=" + fm(summe("Volumen", "(%s And %s)" % (MIT_MATERIAL, IST_PREIS))), 9.5, c.INK, c.F_SEMI),
                                     c.run(" m³", 8, c.FAINT)]), "Right", valign="Bottom"),
            c.cell("S7_KF3", c.run("", 9)),
            c.cell("S7_KF4", c.para([c.run("=" + eur(kosten), 15, c.INK, c.F_SEMI), c.run(" €", 9, c.MUTED)]), "Right", valign="Bottom"),
            c.cell("S7_KF5", c.run("100 %", 9.5, c.INK, c.F_SEMI), "Right", valign="Bottom"),
        ]),
    ]
    tabelle = c.tablix("S7_TbKosten", 0, 0, [3.3, 2.0, 1.6, 2.7, 1.4], rows, group="=" + MATGRUPPE,
                       sort="=" + schluessel, sort_desc=True, filter_expr=MIT_MATERIAL)
    tabelle = deckel(tabelle, "S7_TbKosten_G", schluessel, MAX_GRUPPEN)
    items += c.rect("S7_B03_tab", y, left, tw, 4.65, tabelle)

    # Ring der Kostenanteile in Materialfarben, Summe in der Mitte
    rx = left + tw + 0.5
    ring = v.chart(
        "S7_ChKosten", y - 0.1, rx + 0.5, 3.4, 3.1,
        [v.S("Kosten", {"Y": "=" + kosten}, typ="Shape", sub="Doughnut",
             custom_xml=v.custom(DoughnutRadius="30", PieLabelStyle="Disabled", PieStartAngle="270"),
             pstyle="<Color>%s</Color>" % c.esc(MAT_FARBE) + v.border(c.WHITE, "Solid", "1.5pt"))],
        [("=" + MATGRUPPE, "=" + schluessel, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        titles=(v.title('=%s & " €"' % eur(kosten),
                        size='=IIf(Len(%s) &gt;= 7, "8pt", IIf(Len(%s) &gt;= 6, "10pt", "11pt"))' % (eur(kosten).replace("&", "&amp;").replace(">", "&gt;"), eur(kosten).replace("&", "&amp;").replace(">", "&gt;")), color=c.INK,
                        extra="<ChartElementPosition><Top>38</Top><Left>4</Left><Height>14</Height><Width>92</Width></ChartElementPosition>")
                + v.title("Materialkosten", size="7pt", name="Unter", color=c.MUTED, bold=False,
                          extra="<ChartElementPosition><Top>52</Top><Left>8</Left><Height>9</Height><Width>84</Width></ChartElementPosition>")),
        extra=c.filters(MIT_MATERIAL))
    items += deckel(ring, "S7_ChKosten_Cat1", schluessel, 6)
    # Hinweis zur Stellschraube und zur Preisgrundlage
    notiz = (c.rect("S7_B03_na", 0, 0, 0.08, 1.4, bg=c.BLUE)
             + c.text("S7_B03_nt", 0.03, 0.35, 6.0, 1.34,
                      c.para([c.run("Preise links im Report-Fenster ändern – der Report rechnet neu. ", 7, c.TEXT),
                              c.run("Preise nur für Beton, Mauerwerk, Dämmung, Gipskarton; andere zeigen – und zählen nicht.",
                                    7, c.MUTED)]),
                      valign="Middle"))
    items += c.rect("S7_B03_n", y + 3.15, rx, 6.5, 1.4, notiz, bg=c.SURFACE)
    items += etikett("S7_B03_e", y + 4.7, left, w, "U030",
                     "Preise als Report-Parameter (Switch je Materialgruppe), Kosten = Volumen × Preis, TopN 5, Ring in Materialfarben; rechnet bei jeder Parameteränderung neu")
    return items


# ---------------------------------------------------------------- U040 aufklappbar, sortierbar, anklickbar
@b.baustein("U040", "Aufklappbare Tabelle")
def u040(top, left, w):
    items = overline("S7_B02", top, left, w, "Details", "Bauteile zum Aufklappen", titel_w=5.7)
    gruppen_n = "CountDistinct(IIf(%s, %s, Nothing), \"%s\")" % (MIT_MATERIAL, MATGRUPPE, DS)
    hinweis = ('=IIf(%s > %d, "Die %d größten von " & %s & " Gruppen · ", "") & "+ klappt auf · Spaltenkopf sortiert · Klick zoomt in Allplan"'
               % (gruppen_n, MAX_GRUPPEN, MAX_GRUPPEN, gruppen_n))
    items += c.text("S7_B02_h", top + 0.5, left + 5.8, w - 5.8, 0.5, c.run(hinweis, 7.5, c.MUTED), "Right", "Bottom")
    head = c.edge(["Bottom"], c.INK, "1pt")
    row = c.edge(["Bottom"], c.HAIR, "0.5pt")
    cols = [5.0, 4.2, 2.8, 3.0, 3.0]
    sort_tip = "Klick: nach dieser Spalte sortieren"

    def kopf(name, label, ausdruck, align=None):
        x = c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=head, pad=(4, 2, 4, 4))
        return c.plus(sortierbar(x, ausdruck, "S7_Mat"), "<ToolTip>%s</ToolTip>" % sort_tip)

    def einheit(runs_expr, unit, fmt, fett, groesse=9):
        return c.para([c.run("=" + runs_expr, groesse, c.INK if fett else c.TEXT, c.F_SEMI if fett else c.F, fmt=fmt),
                       c.run(" " + unit, 8, c.FAINT)])

    kopfzeile = [kopf("S7_TH1", "Material / Bauteil", MATGRUPPE),
                 c.cell("S7_TH2", c.run("BAUTEIL-ID", 7, c.MUTED, c.F_SEMI), None, "Bottom", border_xml=head, pad=(4, 2, 4, 4)),
                 kopf("S7_TH3", "Länge", "Sum(CDbl(Fields!Laenge.Value))", "Right"),
                 kopf("S7_TH4", "Fläche", "Sum(CDbl(Fields!Flaeche.Value))", "Right"),
                 kopf("S7_TH5", "Volumen", VOLUMEN, "Right")]
    g = dict(bg=c.SURFACE, border_xml=row, pad=(14, 1, 4, 1))
    gp = dict(bg=c.SURFACE, border_xml=row, pad=(4, 1, 4, 1))
    gruppenzeile = [
        c.cell("S7_G1", c.para([c.run("■ ", 9, MAT_FARBE, b.SYMBOL), c.run("=" + MATGRUPPE, 9.5, c.INK, c.F_SEMI)]), **g),
        c.cell("S7_G2", c.run('=Format(CountRows(), "N0") & " Bauteile"', 8, c.MUTED), **gp),
        c.cell("S7_G3", einheit("Sum(CDbl(Fields!Laenge.Value))", "m", "N1", False), "Right", **gp),
        c.cell("S7_G4", einheit("Sum(CDbl(Fields!Flaeche.Value))", "m²", "N1", False), "Right", **gp),
        c.cell("S7_G5", einheit(VOLUMEN, "m³", "N1", True), "Right", **gp)]

    def d(name, runs, align=None, pad=(4, 1, 4, 1)):
        return klick(c.cell(name, runs, align, border_xml=row, pad=pad))

    einzel = [d("S7_D1", c.run("=" + kurz("Fields!Objekt.Value", 22), 9, c.BLUE), pad=(28, 1, 4, 1)),
              d("S7_D2", c.run("=Fields!Nr.Value", 8, c.MUTED)),
              d("S7_D3", einheit("CDbl(Fields!Laenge.Value)", "m", "N2", False), "Right"),
              d("S7_D4", einheit("CDbl(Fields!Flaeche.Value)", "m²", "N2", False), "Right"),
              d("S7_D5", einheit("CDbl(Fields!Volumen.Value)", "m³", "N2", False), "Right")]

    einzel_wert = "CDbl(Fields!Volumen.Value) + " + NACHRANG
    gruppen_filter = c.topn(VOLUMEN, MAX_GRUPPEN)
    einzel_filter = c.topn(einzel_wert, MAX_EINZEL)
    hier = ("<TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>"
            '<TablixMember><Group Name="S7_Mat"><GroupExpressions><GroupExpression>=%s</GroupExpression></GroupExpressions>%s'
            "<DocumentMapLabel>=%s</DocumentMapLabel></Group>"
            "<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression></SortExpressions>"
            "<TablixMembers><TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>"
            '<TablixMember><Group Name="S7_Det">%s</Group>'
            "<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression></SortExpressions>"
            "<Visibility><Hidden>=Not Parameters!Zeige_Details.Value</Hidden>"
            "<ToggleItem>S7_G1</ToggleItem></Visibility></TablixMember>"
            "</TablixMembers></TablixMember>"
            % (c.esc(MATGRUPPE), gruppen_filter, c.esc(MATGRUPPE), c.esc(VOLUMEN), einzel_filter, c.esc(einzel_wert)))
    tab = tablix_raw("S7_TbAuf", cols, [zeile(0.55, kopfzeile), zeile(0.55, gruppenzeile), zeile(0.5, einzel)], hier, 1.6,
                     extra="<NoRowsMessage>Keine Bauteile mit Material im Teilbild.</NoRowsMessage><DataSetName>%s</DataSetName>%s" % (DS, c.filters(MIT_MATERIAL)))
    items += c.rect("S7_B02_tab", top + 1.45, left, w, 3.4, tab)
    items += etikett("S7_B02_e", top + 4.85, left, w, "U040",
                     "Tablix mit ToggleItem (Startzustand aus Parameter Zeige_Details), UserSort am Spaltenkopf, TopN 5 Gruppen, 5 Zeilen je Gruppe, BookmarkLink Zoom/Mark")
    return items
