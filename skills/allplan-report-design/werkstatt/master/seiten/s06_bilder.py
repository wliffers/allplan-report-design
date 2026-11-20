# -*- coding: utf-8 -*-
"""Seite 6 - Bilder: aus dem Modell und aus der Datei.

B020 Steckbrief-Karten (Bauteilbild aus Allplan, Werte, Klick ins Modell), B030 Bildleiste (ein Bild je Bauteilart),
B040 Piktogramm-Tabelle (eingebettete Icons, Auswahl per Ausdruck), B050 Materialmuster als Kachel-Hintergrund,
B060 Firmenlogo aus Parameter (Bild aus Dateipfad), B070 Hinweistafel zu den Bildarten.

Jeder Baustein ist eine eigene, mit @b.baustein angemeldete Funktion (b020 ... b070): Abschnittskopf, Inhalt und Etikett
in einem Block. seite() legt sie nur noch an die Stelle; die Blockhoehen stehen in den Konstanten H_P01 ... darunter.
"""
import bausteine as b
import core as c
from bausteine import (ist, WAND, RAUM, FENSTER, TUER, MIT_MATERIAL, ICON, MATGRUPPE, MAT_FARBE, ART, summe, raw, overline,
                       seitenkopf, etikett, bild_eingebettet)

TITEL = "Bilder: aus dem Modell und aus der Datei"

RAHMEN = c.edge(["Top", "Bottom", "Left", "Right"], c.HAIR, "0.75pt")
HAIRLINE = c.edge(["Bottom"], c.HAIR, "0.75pt")
HEAD = c.edge(["Bottom"], c.INK, "1pt")
FLAECHE = "Sum(CDbl(Fields!Flaeche.Value))"
VOLUMEN = "Sum(CDbl(Fields!Volumen.Value))"
# Kein Bild von Allplan (Raum, leeres Feld): Bedingung fuer das Ersatz-Piktogramm
OHNE_BILD = "(IsNothing(First(Fields!Bild.Value)) OrElse First(Fields!Bild.Value).Length = 0)"
MIT_BILD = "=Not " + OHNE_BILD
ZOOM = '="Zoom:" + First(Fields!Nr.Value) + ",Mark:" + First(Fields!Nr.Value)'


# Muster nach Materialgruppe (nicht nach dem Projekt-Materialnamen); Gruppen ohne Muster bleiben bei der Gruppenfarbe
MUSTER_GRUPPEN = [("Beton", "beton"), ("Mauerwerk", "mauerwerk"), ("Dämmung", "daemmung"), ("Gipskarton", "gipskarton")]
MUSTER_NAME = ("=Switch(" + ", ".join('%s="%s", "muster_%s"' % (MATGRUPPE, g, n) for g, n in MUSTER_GRUPPEN) + ', True, "muster_beton")')
HAT_MUSTER = "(" + " Or ".join('%s="%s"' % (MATGRUPPE, g) for g, _ in MUSTER_GRUPPEN) + ")"


def leer_stil(text):
    """Ruhiger Leertext statt leerer Flaeche, wenn eine Datenregion keine Zeilen hat."""
    return ("<NoRowsMessage>%s</NoRowsMessage>" % c.esc(text),
            "<Style><Border><Style>None</Style></Border><FontFamily>%s</FontFamily><FontSize>8pt</FontSize>"
            "<Color>%s</Color></Style>" % (c.F, c.FAINT))


def kurz(expr, n):
    """Name auf n Zeichen kuerzen, mit "…" am Ende: sonst laeuft er ueber das Titelfeld der Karte (drei Zeilen passen nicht)."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (expr, n, expr, n - 1, expr)


def zahl(expr):
    """Zahl mit Tausenderpunkt; unter 100 eine Nachkommastelle, sonst keine (grosse Projekte: 31.540 m2)."""
    return 'Format(%s, IIf(Math.Abs(%s) >= 100, "#,##0", "#,##0.0"))' % (expr, expr)


# ---------------------------------------------------------------- Bausteine dieser Seite
def foto(name, top, left, w, h, tip="Klick: in Allplan auf dieses Bauteil zoomen"):
    """Bauteilbild aus Allplan (Feld Bild): FitProportional, anklickbar. Ein anders proportioniertes Bild bleibt im Kasten.
    Sichtbar nur, wenn Allplan ein Bild liefert - das Ersatz-Piktogramm (passepartout) ist genau dann ausgeblendet: die beiden
    schliessen sich gegenseitig aus, nie stehen zwei Felder gleichzeitig auf derselben Stelle."""
    act = "<ActionInfo><Actions><Action><BookmarkLink>%s</BookmarkLink></Action></Actions></ActionInfo>" % c.esc(ZOOM)
    return ('<Image Name="%s"><Source>Database</Source><Value>=First(Fields!Bild.Value)</Value><MIMEType>image/jpeg</MIMEType>'
            "<Sizing>FitProportional</Sizing>%s<ToolTip>%s</ToolTip><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>"
            "<Visibility><Hidden>=%s</Hidden></Visibility><Style><Border><Style>None</Style></Border></Style></Image>"
            % (name, act, c.esc(tip), c.cm(top), c.cm(left), c.cm(h), c.cm(w), c.esc(OHNE_BILD)))


def passepartout(name, top, left, w, h, ersatz_w=0.9):
    """Weisse Bildflaeche mit Haarrand als Behaelter (Kinder liegen sicher ueber dem Weiss). Darin hinten das Piktogramm
    der Bauteilart (nur sichtbar, wenn Allplan kein Bild liefert), davor das Bauteilbild. Leeres Feld = ruhiges
    Piktogramm statt Loch."""
    ersatz = c.image(name + "_Ersatz", (h - ersatz_w) / 2, (w - ersatz_w) / 2, ersatz_w, ersatz_w, ICON,
                     source="Embedded", hidden=MIT_BILD)
    return c.rect(name, top, left, w, h, ersatz + foto(name + "_Bild", 0.05, 0.05, w - 0.1, h - 0.1),
                  bg=c.WHITE, border_xml=RAHMEN)


def tablix_eins(name, top, left, w, h, zelle, gruppe, rang, bedingung, leer, anzahl=1):
    """Eine Karte je Gruppe, nur die 'anzahl' ersten nach 'rang' (c.topn an der Gruppe). Feld mit reservierter Groesse;
    ohne Treffer steht der Leertext 'leer' im Feld."""
    meldung, stil = leer_stil(leer)
    xml = ('<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
           "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
           "</TablixCells></TablixRow></TablixRows></TablixBody>"
           "<TablixColumnHierarchy><TablixMembers><TablixMember/></TablixMembers></TablixColumnHierarchy>"
           '<TablixRowHierarchy><TablixMembers><TablixMember><Group Name="%s_G"><GroupExpressions><GroupExpression>%s'
           "</GroupExpression></GroupExpressions>%s</Group></TablixMember></TablixMembers></TablixRowHierarchy>"
           "<DataSetName>AllplanReport</DataSetName>%s%s<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>%s</Tablix>"
           % (name, c.cm(w), c.cm(h), zelle, name, c.esc(gruppe), c.topn(rang, anzahl), c.filters(raw(bedingung)), meldung,
              c.cm(h), c.cm(w), stil))
    return c.rect(name + "_Feld", top, left, w, h, xml)


# ---------------------------------------------------------------- B020 Steckbrief-Karten
KARTE_H = 3.4


def steckbrief(name, top, left, w, art, titel, werte, gruppe, rang, bedingung, leer):
    """Datenblatt: links das Bauteilbild gross, rechts Art, Titel und vier Wertepaare (Beschriftung klein, Wert gross)."""
    bw, bh = 4.6, KARTE_H - 0.5
    tx = 0.25 + bw + 0.3
    tw = w - tx - 0.25
    inner = (passepartout(name + "_P", 0.25, 0.25, bw, bh, 1.2)
             + c.text(name + "_Art", 0.27, tx, tw, 0.3, c.run(art.upper(), 7, c.MUTED, c.F_SEMI))
             + c.text(name + "_Titel", 0.6, tx, tw, 0.95, c.run(titel, 9.5, c.INK, c.F_SEMI), valign="Top"))
    spalte = tw / 2
    for i, (label, expr, fmt, unit) in enumerate(werte):
        x = tx + (i % 2) * spalte
        y = 1.72 + (i // 2) * 0.78
        inner += c.text("%s_L%d" % (name, i), y, x, spalte - 0.05, 0.3, c.run(label.upper(), 7, c.MUTED, c.F_SEMI))
        inner += c.text("%s_W%d" % (name, i), y + 0.33, x, spalte - 0.05, 0.42,
                        c.para([c.run("=" + expr, 9.5, c.INK, c.F_SEMI, fmt=fmt), c.run(" " + unit, 7.5, c.FAINT)]))
    zelle = c.rect(name + "_K", None, 0, 0, 0, inner, bg=c.SURFACE)
    return tablix_eins(name, top, left, w, KARTE_H, zelle, gruppe, rang, bedingung, leer)


def first_d(feld):
    return "CDbl(First(Fields!%s.Value))" % feld


@b.baustein("B020", "Steckbriefe aus dem Modell")
def b020(top, left, w):
    items = overline("S6_A1", top, left, w, "Datenblatt je Bauteil", "Steckbriefe aus dem Modell")
    half = 8.8
    y1, y2 = top + 1.45, top + 1.45 + KARTE_H + 0.25
    xr = left + half + 0.4
    typ = "=Fields!Bezeichnung.Value & \"|\" & Fields!Laenge.Value & \"|\" & Fields!Hoehe.Value"
    # Rang eindeutig machen: Nachrang ueber die Bauteil-ID, sonst nimmt TopN gleiche Werte alle mit (mehrere Karten in einem Feld)
    nachrang = " + Val(Right(Max(Fields!Nr.Value), 8)) / 1000000000000"
    haeufig = "Count(Fields!Nr.Value) + Max(CDbl(Fields!Flaeche.Value)) / 1000" + nachrang
    groesste = "Max(CDbl(Fields!Volumen.Value))" + nachrang
    art_mat = '=Code.Art(First(Fields!ObjNr.Value)) & "  ·  " & Code.MatArt(First(Fields!Material.Value))'
    items += steckbrief(
        "S6_K1", y1, left, half, "Wandschicht", art_mat,
        [("Länge", first_d("Laenge"), "N2", "m"), ("Dicke", first_d("Dicke") + " * 100", "N1", "cm"),
         ("Fläche", first_d("Flaeche"), "N1", "m²"), ("Volumen", first_d("Volumen"), "N2", "m³")],
        "=Fields!Nr.Value", groesste, WAND, "Keine Wand im Modell")
    items += steckbrief(
        "S6_K2", y1, xr, half, "Fenster", "=" + kurz("First(Fields!Bezeichnung.Value)", 38),
        [("Breite", first_d("Laenge"), "N2", "m"), ("Höhe", first_d("Hoehe"), "N2", "m"),
         ("Fläche", first_d("Flaeche"), "N2", "m²"), ("Anzahl", "CountRows()", "N0", "×")],
        typ, haeufig, FENSTER, "Kein Fenster im Modell")
    items += steckbrief(
        "S6_K3", y2, left, half, "Tür", "=" + kurz("First(Fields!Bezeichnung.Value)", 38),
        [("Breite", first_d("Laenge"), "N2", "m"), ("Höhe", first_d("Hoehe"), "N2", "m"),
         ("Fläche", first_d("Flaeche"), "N2", "m²"), ("Anzahl", "CountRows()", "N0", "×")],
        typ, haeufig, TUER, "Keine Tür im Modell")
    items += steckbrief(
        "S6_K4", y2, xr, half, "Unterzug", art_mat,
        [("Länge", first_d("Laenge"), "N2", "m"), ("Breite", first_d("Dicke") + " * 100", "N0", "cm"),
         ("Höhe", first_d("Hoehe") + " * 100", "N0", "cm"), ("Volumen", first_d("Volumen"), "N2", "m³")],
        "=Fields!Nr.Value", groesste, ist(6), "Kein Unterzug im Modell")
    ey = y2 + KARTE_H + 0.1
    items += etikett("S6_K_E", ey, left, w, "B020",
                     "Steckbrief: Karte je Typ (Gruppe mit Deckel c.topn: häufigster Typ bzw. größtes Bauteil), Bild =First(Bild), Klick zoomt")
    return items


# ---------------------------------------------------------------- B030 Bildleiste
@b.baustein("B030", "Bildleiste Bauteile")
def b030(top, left, w):
    items = overline("S6_A2", top, left, w, "Galerie", "Bauteile in Bildern")
    n, luecke = 8, 0.2
    kw = (w - (n - 1) * luecke) / n
    bild_h, name_h, sub_h, menge_h = 1.4, 0.42, 0.32, 0.4

    inner = passepartout("S6_G", 0, 0, kw, bild_h, 0.8)
    bild = c.rect("S6_G_Zelle", None, 0, 0, 0, inner)
    key = "=%s & \"|\" & %s" % (ART, MATGRUPPE)
    mat_gr = "Code.MatArt(First(Fields!Material.Value))"
    vol = VOLUMEN
    zeilen = [
        (bild_h, bild),
        (name_h, c.cell("S6_G_Name", c.run("=Code.Art(First(Fields!ObjNr.Value))", 7.5, c.INK, c.F_SEMI), valign="Top",
                        pad=(1, 3, 1, 0))),
        (sub_h, c.cell("S6_G_Mat", c.run('=IIf(%s = "ohne Angabe", "", %s)' % (mat_gr, mat_gr), 7, c.MUTED), valign="Top",
                       pad=(1, 0, 1, 0))),
        (menge_h, c.cell("S6_G_Menge", c.para([c.run('=Format(CountRows(), "#,##0")', 7.5, c.BLUE, c.F_SEMI),
                                               c.run('="  ×  " & %s & " m³"' % zahl(vol), 7, c.MUTED)]),
                         valign="Top", pad=(1, 0, 0, 0))),
    ]
    meldung, stil = leer_stil("Keine Bauteile mit Material im Modell")
    xml = ('<Tablix Name="S6_Galerie"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn>'
           "<TablixColumn><Width>%s</Width></TablixColumn></TablixColumns><TablixRows>" % (c.cm(kw), c.cm(luecke)))
    for i, (h, a) in enumerate(zeilen):
        xml += ("<TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow>"
                % (c.cm(h), a, c.cell("S6_G_x%d" % i, c.run("", 6))))
    xml += "</TablixRows></TablixBody>"
    # groesste Menge zuerst; hoechstens acht Bauteilarten (Deckel), damit die Leiste nie ueber den Rand waechst
    rang = vol + " + Val(Right(Max(Fields!Nr.Value), 8)) / 1000000000000"
    xml += ('<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="S6_Galerie_G"><GroupExpressions>'
            "<GroupExpression>%s</GroupExpression></GroupExpressions>%s</Group>"
            "<SortExpressions><SortExpression><Value>=-%s</Value></SortExpression></SortExpressions>"
            "<TablixMembers><TablixMember/><TablixMember/></TablixMembers></TablixMember></TablixMembers></TablixColumnHierarchy>"
            % (c.esc(key), c.topn(rang, n), c.esc(vol)))
    xml += "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>" % ("<TablixMember/>" * len(zeilen))
    hoehe = sum(z[0] for z in zeilen)
    xml += ("<DataSetName>AllplanReport</DataSetName>%s%s<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>%s</Tablix>"
            % (c.filters(raw(MIT_MATERIAL)), meldung, c.cm(hoehe), c.cm(n * (kw + luecke)), stil))
    items += c.rect("S6_G_Feld", top + 1.45, left, w, hoehe + 0.05, xml)
    ey = top + 1.45 + hoehe + 0.1
    items += etikett("S6_G_E", ey, left, w, "B030",
                     "Bildleiste: Spaltengruppe je Bauteilart und Materialgruppe, Deckel 8, =First(Bild); ohne Bild erscheint das Piktogramm")
    return items


# ---------------------------------------------------------------- B040 Piktogramm-Tabelle
@b.baustein("B040", "Bauteilarten mit Piktogramm")
def b040(top, left, w):
    items = overline("S6_A3", top, left, w, "Eingebettet", "Bauteilarten mit Piktogramm")

    def kopf(name, label, align=None):
        return c.cell(name, c.run(label.upper(), 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=HEAD, pad=(4, 2, 4, 4))

    # Fenster und Tueren haben kein Bauteilvolumen: dort steht "-" (auch wenn Allplan eines liefert)
    ohne_vol = "(%s = 0 Or Val(First(Fields!ObjNr.Value)) = 991 Or Val(First(Fields!ObjNr.Value)) = 992)" % VOLUMEN
    rows = [
        ("kopf", 0.5, [kopf("S6_T3_H1", ""), kopf("S6_T3_H2", "Bauteilart"), kopf("S6_T3_H3", "Anzahl", "Right"),
                       kopf("S6_T3_H4", "Fläche", "Right"), kopf("S6_T3_H5", "Volumen", "Right")]),
        ("daten", 0.62, [
            c.rect("S6_T3_D1", None, 0, 0, 0, bild_eingebettet("S6_T3_Icon", 0.05, 0.1, 0.62, 0.5, ICON), border_xml=HAIRLINE),
            c.cell("S6_T3_D2", c.run("=Code.Art(First(Fields!ObjNr.Value))", 9, c.INK, c.F_SEMI), border_xml=HAIRLINE),
            c.cell("S6_T3_D3", c.run('=Format(CountRows(), "#,##0")', 9, c.TEXT), "Right", border_xml=HAIRLINE),
            c.cell("S6_T3_D4", c.para([c.run("=" + zahl(FLAECHE), 9, c.TEXT), c.run(" m²", 7.5, c.FAINT)]),
                   "Right", border_xml=HAIRLINE, pad=(2, 2, 4, 2)),
            c.cell("S6_T3_D5", c.para([c.run('=IIf(%s, "–", %s)' % (ohne_vol, zahl(VOLUMEN)), 9, c.INK, c.F_SEMI),
                                       c.run('=IIf(%s, "", " m³")' % ohne_vol, 7.5, c.FAINT)]), "Right", border_xml=HAIRLINE,
                   pad=(2, 2, 4, 2)),
        ])]
    reihenfolge = ("=Switch(Val(Fields!ObjNr.Value)=1, 1, Val(Fields!ObjNr.Value)=4, 2, Val(Fields!ObjNr.Value)=704, 3, "
                   "Val(Fields!ObjNr.Value)=3, 4, Val(Fields!ObjNr.Value)=6, 5, Val(Fields!ObjNr.Value)=61, 6, "
                   "Val(Fields!ObjNr.Value)=991, 7, True, 8)")
    # Deckel: die Abfrage liefert nur acht Objektnummern, also hoechstens acht Gruppen; die Tabelle steht im Feld fester Hoehe.
    # Bauteile zaehlen nur mit Materialangabe (wie auf allen Seiten); Raeume, Fenster, Tueren brauchen keine.
    tab = c.tablix("S6_T3", 0, 0, [0.9, 2.3, 1.5, 2.0, 2.1], rows, group="=Fields!ObjNr.Value", sort=reihenfolge,
                  filter_expr="(%s Or %s Or %s Or %s)" % (MIT_MATERIAL, RAUM, FENSTER, TUER))
    hoehe = 0.5 + 8 * 0.62
    items += c.rect("S6_T3_Feld", top + 1.45, left, w, hoehe + 0.1, tab)
    ey = top + 1.45 + hoehe + 0.2
    items += etikett("S6_T3_E", ey, left, w, "B040", "Eingebettete Piktogramme: Bild per Ausdruck nach Objektart")
    return items


# ---------------------------------------------------------------- B050 Materialmuster
@b.baustein("B050", "Materialien als Muster")
def b050(top, left, w):
    items = overline("S6_A4", top, left, w, "Eingebettet", "Materialien als Muster")
    n, luecke = 4, 0.267
    kw = (w - (n - 1) * luecke) / n
    kachel_h, name_h, wert_h = 1.6, 0.45, 0.8
    muster = ('<Rectangle Name="S6_P4_Muster"><Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>'
              "<Visibility><Hidden>=Not %s</Hidden></Visibility><Style><Border><Style>None</Style></Border>"
              "<BackgroundImage><Source>Embedded</Source><Value>%s</Value><BackgroundRepeat>Repeat</BackgroundRepeat>"
              "</BackgroundImage></Style></Rectangle>" % (c.cm(kachel_h - 0.1), c.cm(kw), c.esc(HAT_MUSTER), c.esc(MUSTER_NAME)))
    # Gruppen ohne eigenes Muster zeigen ihre Gruppenfarbe; der leere Anker haelt die Kachel, auch wenn das Muster ausgeblendet ist.
    # Anker und Muster ueberlappen sich nicht: das Muster endet 0,1 cm vor dem Kachelrand, der Anker liegt im Streifen darunter.
    anker = c.text("S6_P4_Anker", kachel_h - 0.05, 0, kw, 0.05, c.run("", 6))
    kachel = c.rect("S6_P4_Kachel", None, 0, 0, 0, anker + muster, bg=MAT_FARBE, border_xml=RAHMEN)
    gesamt = summe("Volumen", MIT_MATERIAL, "AllplanReport")
    gruppe = "Code.MatArt(First(Fields!Material.Value))"
    zeilen = [
        (kachel_h, kachel),
        (name_h, c.cell("S6_P4_Name", c.run("=" + gruppe, 7.5, c.INK, c.F_SEMI), valign="Top", pad=(1, 3, 1, 0))),
        (wert_h, c.cell("S6_P4_Wert", [
            c.para([c.run("=" + zahl(VOLUMEN), 8.5, c.TEXT), c.run(" m³", 7, c.FAINT)]),
            c.para([c.run('=Format(IIf(%s = 0, 0.0, %s / %s), "0 %%")' % (gesamt, VOLUMEN, gesamt), 8.5, c.BLUE, c.F_SEMI),
                    c.run("  Anteil", 7, c.FAINT)])], valign="Top", pad=(1, 0, 0, 0))),
    ]
    meldung, stil = leer_stil("Keine Materialien im Modell")
    xml = ('<Tablix Name="S6_Muster"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn>'
           "<TablixColumn><Width>%s</Width></TablixColumn></TablixColumns><TablixRows>" % (c.cm(kw), c.cm(luecke)))
    for i, (h, a) in enumerate(zeilen):
        xml += ("<TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow>"
                % (c.cm(h), a, c.cell("S6_P4_x%d" % i, c.run("", 6))))
    xml += "</TablixRows></TablixBody>"
    # Deckel: die vier groessten Materialgruppen (Nachrang ueber den Namen haelt die Zahl bei gleichem Volumen fest)
    rang = VOLUMEN + " + Len(Max(Fields!Material.Value)) / 1000000"
    xml += ('<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="S6_Muster_G"><GroupExpressions>'
            "<GroupExpression>=%s</GroupExpression></GroupExpressions>%s</Group>"
            "<SortExpressions><SortExpression><Value>=-%s</Value></SortExpression></SortExpressions>"
            "<TablixMembers><TablixMember/><TablixMember/></TablixMembers></TablixMember></TablixMembers></TablixColumnHierarchy>"
            % (c.esc(MATGRUPPE), c.topn(rang, n), c.esc(VOLUMEN)))
    xml += "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>" % ("<TablixMember/>" * len(zeilen))
    hoehe = sum(z[0] for z in zeilen)
    xml += ("<DataSetName>AllplanReport</DataSetName>%s%s<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>%s</Tablix>"
            % (c.filters(raw(MIT_MATERIAL)), meldung, c.cm(hoehe), c.cm(n * (kw + luecke)), stil))
    items += c.rect("S6_P4_Feld", top + 1.45, left, w, hoehe + 0.05, xml)
    ey = top + 1.45 + hoehe + 0.1
    items += etikett("S6_P4_E", ey, left, w, "B050", "Muster als Kachel-Hintergrund (Repeat), nach Materialgruppe, Deckel 4")
    return items


# ---------------------------------------------------------------- B060 Firmenlogo aus Parameter
@b.baustein("B060", "Firmenlogo aus Parameter")
def b060(top, left, w, h=2.0):
    kein_logo = "Len(Parameters!Company_Logo.Value) = 0"
    versteckt = "=Parameters!Display_Logo.Value = False Or %s" % kein_logo
    # Logo, Leertext und Anker liegen untereinander, nichts ueberlappt (das Report-Fenster schiebt Ueberlappendes weg):
    # Logo oben, darunter die Meldung (nur ohne Logo sichtbar), ganz unten der leere Anker, der die Flaeche haelt.
    inner = (c.text("S6_P5_Anker", h - 0.55, 0.0, 3.0, 0.05, c.run("", 6), valign="Middle")
             + c.image("S6_P5_Logo", 0.15, 0.15, 2.7, h - 1.2, '="file:///" & Parameters!Company_Logo.Value', source="External",
                     hidden=versteckt)
             + c.text("S6_P5_Leer", h - 1.0, 0.0, 3.0, 0.4, c.run('=IIf(Parameters!Display_Logo.Value = False, "Logo ausgeblendet", "kein Logo übergeben")', 7, c.FAINT),
                      align="Center", valign="Middle",
                      hidden="=Parameters!Display_Logo.Value = True And Len(Parameters!Company_Logo.Value) > 0"))
    box = c.rect("S6_P5_Weiss", 0.25, 0.25, 3.0, h - 0.5, inner, bg=c.WHITE, border_xml=RAHMEN)
    tx = 3.6
    text = (c.text("S6_P5_Art", 0.27, tx, w - tx - 0.25, 0.35, c.run("FIRMENLOGO AUS PARAMETER", 7, c.MUTED, c.F_SEMI))
            + c.text("S6_P5_Titel", 0.62, tx, w - tx - 0.25, 0.5, c.run("Bild aus Dateipfad", 11, c.INK, c.F_SEMI))
            + c.text("S6_P5_Text", 1.12, tx, w - tx - 0.25, 0.75,
                     c.run("Der Pfad kommt aus einem Parameter oder aus einem Datenfeld je Zeile.", 8, c.TEXT, c.F),
                     valign="Top"))
    items = c.rect("S6_P5", top, left, w, h, box + text, bg=c.SURFACE)
    items += etikett("S6_P5_E", top + h + 0.1, left, w, "B060", "Externes Bild: file:/// & Company_Logo, Sichtbarkeit Display_Logo")
    return items


# ---------------------------------------------------------------- B070 Hinweistafel
@b.baustein("B070", "Hinweistafel Bildarten")
def b070(top, left, w, h=1.85):
    spalten = [("3D-Bild, farbig", "Bauteilbild je Zeile. So kommt es in diesem Report vor."),
               ("Grundriss, Raumplan", "Ausschnitt, ganzes Geschoss, Raum: im Begleit-Report „Report Master Grundriss“."),
               ("Je Report eine Bildart", "Entweder 3D-Bilder oder Grundriss-Ausschnitte, nie beides in einem Report.")]
    cw = (w - 0.5 - 2 * 0.3) / 3
    inner = c.text("S6_P6_Kopf", 0.25, 0.3, w - 0.6, 0.3, c.run("WAS ALLPLAN AN BILDERN LIEFERT", 7, c.MUTED, c.F_SEMI))
    for i, (kopf, text) in enumerate(spalten):
        x = 0.3 + i * (cw + 0.3)
        inner += c.text("S6_P6_T%d" % i, 0.58, x, cw, 0.45, c.run(kopf, 9, c.INK, c.F_SEMI), valign="Top")
        inner += c.text("S6_P6_B%d" % i, 1.05, x, cw, h - 1.1, c.run(text, 7.5, c.TEXT, c.F), valign="Top")
    items = c.rect("S6_P6", top, left, w, h, inner, bg=c.SURFACE)
    items += etikett("S6_P6_E", top + h + 0.1, left, w, "B070", "Hinweistafel: Textfläche auf c.SURFACE, drei Spalten")
    return items


# ---------------------------------------------------------------- Seite
# Hoehe der Bloecke samt Abschnittskopf und Etikett (cm); davon haengt die Lage des naechsten Bausteins ab.
H_P01 = 1.45 + 2 * KARTE_H + 0.25 + 0.1 + 0.4
H_P02 = 1.45 + 2.54 + 0.1 + 0.4
H_P03 = 1.45 + 0.5 + 8 * 0.62 + 0.2 + 0.4
H_P04 = 1.45 + 2.85 + 0.1 + 0.4


def seite():
    x0, w = c.INSET, c.CONTENT_W
    half = 8.8
    xr = x0 + half + 0.4
    items = seitenkopf(6, TITEL, "Steckbrief, Piktogramm, Muster, Logo")
    top1 = 3.3
    items += b020(top1, x0, w)
    top2 = top1 + H_P01 + 0.6
    items += b030(top2, x0, w)
    y3 = top2 + H_P02 + 0.6
    items += b040(y3, x0, half)
    items += b050(y3, xr, half)
    ende_l, ende_r = y3 + H_P03, y3 + H_P04
    top5 = ende_r + 0.25
    h5 = max(2.0, ende_l - 0.5 - top5)       # Etikett von B060 steht auf einer Linie mit dem von B040
    items += b060(top5, xr, half, h5)
    items += b070(max(ende_l, top5 + h5 + 0.5) + 0.35, x0, w, 1.85)
    return items
