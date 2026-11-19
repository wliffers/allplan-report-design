# -*- coding: utf-8 -*-
"""Seite 8 - Text, Symbole und Flaechen: Schriftprobe, Fliesstext mit Auszeichnung, Farbpalette,
Zeichen ohne Bilddatei, Balken aus Schriftzeichen und eine Farbskala aus Text. Kein Diagramm-Element."""
import core as c
import bausteine as b
from bausteine import (ROHBAU, WAND, RAUM, FENSTER, MIT_MATERIAL, MATGRUPPE, IST_BETON, summe, anzahl, quote,
                       overline, etikett, seitenkopf)

TITEL = "Text, Symbole und Flächen"

SYM = "Segoe UI Symbol"
MONO = "Consolas"
RAHMEN_HELL = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR


def hell(hex_farbe):
    """True, wenn die Farbe so hell ist, dass sie auf Weiss einen Rand braucht."""
    r, g, b = (int(hex_farbe[i:i + 2], 16) for i in (1, 3, 5))
    return (0.299 * r + 0.587 * g + 0.114 * b) > 215


def fliess(runs, zeile=14):
    """Absatz mit fester Zeilenhoehe in pt (LineHeight in pt geht, in Prozent nicht)."""
    return ("<Paragraph><TextRuns>%s</TextRuns><Style><LineHeight>%spt</LineHeight></Style></Paragraph>"
            % ("".join(runs), zeile))


def zahl(expr, fmt, farbe=c.BLUE, size=9.5):
    """Zahl im Satz: halbfett, in Farbe, Ausdruck mit Format."""
    return c.run("=" + expr, size, farbe, c.F_SEMI, fmt=fmt)   # fmt=None: der Ausdruck liefert schon Text


GROESSE = [30, 22, 13, 9.5, 7, 6.5]      # Schriftgroessen der sechs Stufen (fuer den Basislinienausgleich)

# ---------------------------------------------------------------- Datenfest: Deckel, Namen, Zahlen
N_RANG = 9          # Rangliste und Kacheln: die 9 groessten Nutzungen
N_ANW = 6           # Anwendungstabelle: die 6 haeufigsten Schichtarten


def zf(expr):
    """Zahl als Text: ab 100 ohne Nachkommastellen (31.540), darunter eine (18,5)."""
    return 'IIf(Abs(%s) >= 100, Format(%s, "N0"), Format(%s, "N1"))' % (expr, expr, expr)


def zi(expr):
    """Ganzzahl als Text mit Tausenderpunkt (2.342)."""
    return 'Format(%s, "N0")' % expr


def kurz(expr, n):
    """Name auf n Zeichen kuerzen (Zellen wachsen nicht); leer wird "ohne Nutzung"."""
    return 'IIf(Len(%s) = 0, "ohne Nutzung", IIf(Len(%s) > %d, Left(%s, %d) & "…", %s))' % (expr, expr, n, expr, n - 1, expr)


NUTZUNG = 'Fields!Funktion.Value & ""'

FLAECHE_N = "Sum(IIf(%s, CDbl(Fields!Flaeche.Value), 0.0))" % RAUM
# Rangschluessel einer Nutzung: Flaechensumme auf 0,01 gerundet, bei Gleichstand entscheiden die ersten
# zwei Buchstaben - so ergibt TopN immer genau n Gruppen.
RANG = ('Round(%s, 2) - (Max(AscW(Mid(Fields!Funktion.Value & "  ", 1, 1))) * 65536.0 '
        '+ Max(AscW(Mid(Fields!Funktion.Value & "  ", 2, 1)))) / 1.0E13' % FLAECHE_N)
N_NUTZUNGEN = 'CountDistinct(IIf(%s, Fields!Funktion.Value & "", Nothing))' % RAUM
SCHICHTART = '%s & "|" & CStr(Round(CDbl(Fields!Dicke.Value) * 100, 1))' % MATGRUPPE
N_SCHICHTARTEN = "CountDistinct(IIf(%s, %s, Nothing))" % (WAND, SCHICHTART)
BETON_VOL = "Sum(IIf(%s And %s, CDbl(Fields!Volumen.Value), 0.0))" % (ROHBAU, IST_BETON)


def rang_nr(tablix):
    """Platz der aktuellen Nutzung (1, 2, 3 ...) - RowNumber zaehlt Datenzeilen, nicht Gruppen."""
    return 'RunningValue(%s, CountDistinct, "%s")' % (NUTZUNG, tablix)


def mit_deckel(tablix_xml, schluessel, n):
    """TopN-Filter in die Gruppe der Tabelle setzen (Aggregate im Schluessel gelten je Gruppe)."""
    return tablix_xml.replace("</GroupExpressions></Group>", "</GroupExpressions>%s</Group>" % c.topn(schluessel, n), 1)


def etikett_x(name, top, left, w, kennung, ausdruck, katalog):
    """Etikett mit Ausdruck im Text (Anzahlen aus den Daten); katalog = Text fuers Bausteinverzeichnis."""
    b.KATALOG.append((b.SEITE_AKTUELL[0], kennung, katalog))
    return c.text(name, top, left, w, 0.4,
                  c.para([c.run(kennung + "  ", 6.5, c.BLUE, c.F_SEMI), c.run("=" + ausdruck, 6.5, c.FAINT)]))


# ---------------------------------------------------------------- X010 Typo-Skala
def typo_skala(x0, top, w):
    stufen = [
        ("Titel", "30 pt  ·  Light", 1.2,
         c.para([c.run("Bauteile", 30, c.INK, c.F_LIGHT)])),
        ("Zahl", "22 pt  ·  Light", 0.92,
         c.para([c.run("=" + zf(BETON_VOL), 22, c.INK, c.F_LIGHT), c.run(" m³", 10, c.MUTED)])),
        ("Abschnitt", "13 pt  ·  Semibold", 0.75,
         c.para([c.run("Wandaufbau", 13, c.INK, c.F_SEMI)])),
        ("Wert", "9,5 pt  ·  Regular", 0.6,
         c.para([c.run("=" + zi(anzahl(WAND)), 9.5, c.INK, c.F_SEMI),
                 c.run(" Schichten · ", 9.5, c.TEXT),
                 c.run("=" + zf(summe("Flaeche", WAND)), 9.5, c.TEXT), c.run(" m²", 8, c.FAINT)])),
        ("Beschriftung", "7 pt  ·  Semibold", 0.52,
         c.para([c.run("WANDFLÄCHE  ·  FENSTER", 7, c.MUTED, c.F_SEMI)])),
        ("Etikett", "6,5 pt  ·  Semibold", 0.48,
         c.para([c.run("D090  ", 6.5, c.BLUE, c.F_SEMI), c.run("Ring mit Zahl", 6.5, c.FAINT)])),
    ]
    c_name, c_spec = 1.95, 2.05
    sx = x0 + c_name + c_spec
    sw = w - c_name - c_spec
    xml = ""
    y = top
    for i, (name, spec, h, sample) in enumerate(stufen):
        n = "S8_T%d" % i
        luft = round(max(0.0, (GROESSE[i] - 7) * 0.26), 1)     # Unterlaenge der Beispielschrift ausgleichen
        xml += c.text(n + "n", y, x0, c_name, h, c.run(name.upper(), 7, c.TEXT, c.F_SEMI), valign="Bottom", pad=(0, 0, 0, luft))
        xml += c.text(n + "s", y, x0 + c_name, c_spec, h, c.run(spec, 6.5, c.FAINT), valign="Bottom", pad=(0, 0, 0, luft))
        xml += c.text(n + "p", y, sx, sw, h, sample, valign="Bottom", pad=(0, 0, 0, 0))
        y += h
        xml += c.line(n + "l", y, x0, w)
    # drei Schnitte
    y += 0.25
    cw = w / 3
    for i, (fam, name) in enumerate([(c.F_LIGHT, "Light"), (c.F, "Regular"), (c.F_SEMI, "Semibold")]):
        xml += c.text("S8_Sch%d" % i, y, x0 + i * cw, 0.8, 0.85,
                      [c.para([c.run("Aa", 17, c.INK, fam)]),
                       ],
                      valign="Bottom")
        xml += c.text("S8_SchN%d" % i, y, x0 + i * cw + 0.85, cw - 0.9, 0.85,
                      [c.para([c.run(name.upper(), 7, c.TEXT, c.F_SEMI)]),
                       c.para([c.run(fam, 6.5, c.FAINT)])], valign="Bottom", pad=(0, 0, 0, 4))
    return xml, y + 0.85


# ---------------------------------------------------------------- X020 Fliesstext
def fliesstext(x0, top, w):
    """Absatz in einer Textbox: Zahlen aus den Daten stehen halbfett und farbig im Satz.
    Darunter dieselbe Idee mit HTML-Auszeichnung (b, i, font, ul/li). Keine festen Namen: Beton ueber die
    Materialgruppe, Halbsaetze entfallen, wenn die Art im Projekt fehlt."""
    xml = ""
    # senkrechte Randmarke (Rotate270) mit Haarlinie
    xml += c.text("S8_Rand", top, x0, 0.42, 2.75, c.run("BERICHT IN WORTEN", 6.5, c.BLUE, c.F_SEMI),
                  valign="Middle", rotate="Rotate270", align="Left")
    xml += c.line("S8_RandL", top, x0 + 0.5, 0, c.HAIR, "0.75pt", h=2.75)
    n_raum, n_fenster = anzahl(RAUM), anzahl(FENSTER)
    runs = [
        c.run("Das Gebäude besteht aus ", 9.5, c.TEXT),
        zahl(zi(anzahl(MIT_MATERIAL)), None, c.INK), c.run(" Bauteilen mit zusammen ", 9.5, c.TEXT),
        zahl(zf(summe("Volumen", MIT_MATERIAL)), None, c.INK), c.run(" m³ Volumen. ", 9.5, c.TEXT),
        zahl(quote(BETON_VOL, summe("Volumen", MIT_MATERIAL)), "0 %", c.BLUE),
        c.run(" davon sind Beton. ", 9.5, c.TEXT),
        c.run('=IIf(%s = 0, "", "Auf ")' % n_raum, 9.5, c.TEXT),
        zahl('IIf(%s = 0, "", %s)' % (n_raum, zf(summe("Flaeche", RAUM))), None, c.BLUE),
        c.run('=IIf(%s = 0, "", " m² Raumfläche verteilen sich ")' % n_raum, 9.5, c.TEXT),
        zahl('IIf(%s = 0, "", %s)' % (n_raum, zi(n_raum)), None, c.BLUE),
        c.run('=IIf(%s = 0, "", " Räume")' % n_raum, 9.5, c.TEXT),
        c.run('=IIf(%s = 0, "", IIf(%s = 0, ".", "; Licht kommt durch "))' % (n_raum, n_fenster), 9.5, c.TEXT),
        zahl('IIf(%s = 0, "", %s)' % (n_fenster, zi(n_fenster)), None, c.BLUE),
        c.run('=IIf(%s = 0, "", " Fenster.")' % n_fenster, 9.5, c.TEXT),
    ]
    xml += c.text("S8_Fliess", top, x0 + 0.8, w - 0.8, 2.75, [fliess(runs, 14.5)], valign="Top")

    # HTML-Variante: groesste Materialgruppe der Bauteile aus den Daten
    hy = top + 3.0
    stil = ("<Style><FontFamily>%s</FontFamily><FontSize>9pt</FontSize><Color>%s</Color></Style>" % (c.F, c.TEXT))
    gruppen = [g for g, _ in c.MATERIALGRUPPE]
    vol = ['Sum(IIf(%s And %s = "%s", CDbl(Fields!Volumen.Value), 0.0))' % (MIT_MATERIAL, MATGRUPPE, g) for g in gruppen]
    groesste = vol[-1]
    for ausdruck in reversed(vol[:-1]):
        groesste = "Math.Max(%s, %s)" % (ausdruck, groesste)
    name = 'Switch(%s, True, "–")' % ", ".join('%s = %s, "%s"' % (a, groesste, g) for a, g in zip(vol, gruppen))
    k_gruppen = 'CountDistinct(IIf(%s, %s, Nothing))' % (MIT_MATERIAL, MATGRUPPE)
    html = ('="Größte Materialgruppe: <font color=\'%s\'><b>" & %s & "</b></font> mit " & %s & " m³'
            '<ul><li><b>" & Format(%s, "0 %%") & "</b> des Bauteilvolumens</li>'
            '<li><i>" & %s & "</i> Materialgruppen bei den <b>Bauteilen</b></li></ul>"'
            % (c.BLUE, name, zf(groesste), quote(groesste, summe("Volumen", MIT_MATERIAL)), k_gruppen))
    para_html = ("<Paragraph><TextRuns><TextRun><Value>%s</Value><MarkupType>HTML</MarkupType>%s</TextRun></TextRuns>"
                 "<Style/></Paragraph>" % (c.esc(html), stil))
    xml += c.text("S8_Html", hy, x0 + 0.8, w - 0.8, 1.55, [para_html], valign="Top")
    xml += c.text("S8_HtmlK", hy, x0, 0.42, 1.55, c.run("HTML", 6.5, c.BLUE, c.F_SEMI),
                  valign="Middle", rotate="Rotate270", align="Left")
    xml += c.line("S8_HtmlL", hy, x0 + 0.5, 0, c.HAIR, "0.75pt", h=1.55)
    return xml, hy + 1.55


# ---------------------------------------------------------------- X030 Farbpalette
def palette(x0, top, w):
    spalten = 13
    pitch = w / spalten
    chip_w = pitch - 0.1
    chip_h = 0.46

    reihen = [
        [("MARKE", [("Nachtblau", c.NAVY), ("Leitfarbe", c.BLUE), ("Himmel", c.SKY), ("Akzent", c.ORANGE)]),
         ("NEUTRAL", [("Tinte", c.INK), ("Text", c.TEXT), ("Gedämpft", c.MUTED), ("Blass", c.FAINT),
                      ("Haarlinie", c.HAIR), ("Fläche", c.SURFACE)]),
         ("BEWERTUNG", [("Gut", c.GREEN), ("Achtung", c.AMBER), ("Schlecht", c.RED)])],
        [("BLAUSTUFEN  ·  GRÖSSTE = DUNKELSTE", [("Stufe %d" % (i + 1), f) for i, f in enumerate(c.RAMP)]),
         ("MATERIAL", [(n.replace(" bewehrt", ""), f) for n, f in c.MATERIAL])],
    ]
    xml = ""
    y = top
    for r, gruppen in enumerate(reihen):
        i = 0
        for g, (titel, chips) in enumerate(gruppen):
            gx = x0 + i * pitch
            gw = len(chips) * pitch - 0.1
            n = "S8_P%d_%d" % (r, g)
            xml += c.line(n + "l", y, gx, gw, c.INK, "0.75pt")
            xml += c.text(n + "t", y + 0.07, gx, gw, 0.32, c.run(titel, 6.5, c.MUTED, c.F_SEMI))
            for k, (name, farbe) in enumerate(chips):
                cx = x0 + (i + k) * pitch
                m = "%s_%d" % (n, k)
                xml += c.rect(m, y + 0.42, cx, chip_w, chip_h, "", bg=farbe, border_xml=RAHMEN_HELL if hell(farbe) else "")
                xml += c.text(m + "n", y + 0.42 + chip_h + 0.06, cx, pitch, 0.3, c.run(name, 7, c.INK, c.F_SEMI))
                xml += c.text(m + "h", y + 0.42 + chip_h + 0.41, cx, pitch, 0.25, c.run(farbe.upper(), 6.5, c.FAINT))
            i += len(chips)
        y += 0.42 + chip_h + 0.6 + 0.22
    return xml, y - 0.22


# ---------------------------------------------------------------- X040 Zeichen
def zeichen(x0, top, w):
    gw = 8.8
    zeilen = [
        ("✓", c.GREEN, "Anforderung erfüllt"),
        ("✕", c.RED, "Anforderung verfehlt"),
        ("▲", c.GREEN, "Wert über Soll, steigend"),
        ("▼", c.RED, "Wert unter Soll, fallend"),
        ("●", c.AMBER, "Achtung, bitte prüfen"),
        ("○", c.MUTED, "nicht bewertet"),
        ("■", c.BLUE, "Legendenschlüssel"),
        ("★", c.AMBER, "Spitzenwert, Rang 1"),
        ("→", c.BLUE, "Verweis, Übergang"),
    ]
    rh = 0.4
    xml = ""
    kopf = c.edge(["Bottom"], c.INK, "1pt")
    c1, c2 = 1.1, 3.0
    xml += c.text("S8_ZH1", top, x0, c1, 0.5, c.run("ZEICHEN", 7, c.MUTED, c.F_SEMI), align="Center", valign="Bottom",
                  border_xml=kopf, pad=(0, 0, 0, 4))
    xml += c.text("S8_ZH2", top, x0 + c1, c2, 0.5, c.run("SCHRIFT", 7, c.MUTED, c.F_SEMI), valign="Bottom",
                  border_xml=kopf, pad=(4, 0, 0, 4))
    xml += c.text("S8_ZH3", top, x0 + c1 + c2, gw - c1 - c2, 0.5, c.run("EINSATZ", 7, c.MUTED, c.F_SEMI), valign="Bottom",
                  border_xml=kopf, pad=(4, 0, 0, 4))
    y = top + 0.5
    rowb = c.edge(["Bottom"], c.HAIR, "0.5pt")
    for i, (g, farbe, einsatz) in enumerate(zeilen):
        n = "S8_Z%d" % i
        xml += c.text(n + "g", y, x0, c1, rh, c.run(g, 8 if g in "●○" else 10, farbe, SYM), align="Center", valign="Middle", border_xml=rowb)
        xml += c.text(n + "f", y, x0 + c1, c2, rh, c.run(SYM, 7.5, c.FAINT), valign="Middle", border_xml=rowb, pad=(4, 0, 0, 0))
        xml += c.text(n + "e", y, x0 + c1 + c2, gw - c1 - c2, rh, c.run(einsatz, 8, c.TEXT), valign="Middle",
                      border_xml=rowb, pad=(4, 0, 0, 0))
        y += rh
    return xml, y


def anwendung(x0, top, w):
    """Echte Zeilen aus den Daten: je Materialgruppe und Dicke eine Zeile, die haeufigsten N_ANW, nach Dicke."""
    dicke = "Round(CDbl(First(Fields!Dicke.Value)) * 100, 1)"
    ok = "%s >= 17.5" % dicke
    kopf = c.edge(["Bottom"], c.INK, "1pt")
    rowb = c.edge(["Bottom"], c.HAIR, "0.5pt")

    def h(name, label, align=None):
        return c.cell(name, c.run(label, 7, c.MUTED, c.F_SEMI), align, "Bottom", border_xml=kopf, pad=(4, 0, 4, 4))

    rows = [
        ("kopf", 0.5, [h("S8_AH1", ""), h("S8_AH2", "SCHICHT"), h("S8_AH3", "DICKE", "Right"), h("S8_AH4", "ANZAHL", "Right"),
                       h("S8_AH5", "BEFUND")]),
        ("daten", 0.4, [
            c.cell("S8_AD1", c.run('=IIf(%s, "✓", "○")' % ok, 9.5, '=IIf(%s, "%s", "%s")' % (ok, c.GREEN, c.FAINT), SYM),
                   "Center", border_xml=rowb, pad=(0, 0, 0, 0)),
            c.cell("S8_AD2", c.run("=" + kurz("Code.MatArt(First(Fields!Material.Value))", 14), 8.5, c.INK, c.F_SEMI),
                   border_xml=rowb, pad=(4, 0, 2, 0)),
            c.cell("S8_AD3", c.para([c.run("=" + dicke, 8.5, c.TEXT, fmt="N1"), c.run(" cm", 7, c.FAINT)]), "Right",
                   border_xml=rowb, pad=(4, 0, 4, 0)),
            c.cell("S8_AD4", c.para([c.run("=" + zi("CountRows()"), 8.5, c.TEXT), c.run(" ×", 7, c.FAINT)]), "Right",
                   border_xml=rowb, pad=(4, 0, 4, 0)),
            c.cell("S8_AD5", c.run('=IIf(%s, "tragfähig", "schlank")' % ok, 8.5, '=IIf(%s, "%s", "%s")' % (ok, c.GREEN, c.MUTED)),
                   border_xml=rowb, pad=(8, 0, 0, 0)),
        ]),
    ]
    # Deckel: die haeufigsten Schichtarten (Anzahl, bei Gleichstand dicker/Gruppenname), angezeigt nach Dicke
    schluessel = ('Count(Fields!ObjNr.Value) + Max(Round(CDbl(Fields!Dicke.Value) * 100, 1)) / 100000.0 '
                  '- Max(AscW(Mid(%s & " ", 1, 1))) / 1.0E12' % MATGRUPPE)
    tb = c.tablix("S8_TbAnw", 0, 0, [0.8, 2.9, 1.8, 1.6, 1.7], rows,
                  group="=" + SCHICHTART,
                  sort="=Max(CDbl(Fields!Dicke.Value))", sort_desc=True, filter_expr=WAND)
    tb = mit_deckel(tb, schluessel, N_ANW)
    xml = c.rect("S8_FeldAnw", top, x0, w, 0.5 + N_ANW * 0.4 + 0.05, tb)
    ky = top + 0.5 + N_ANW * 0.4 + 0.25
    gut = "Sum(IIf(%s And Round(CDbl(Fields!Dicke.Value) * 100, 1) >= 17.5, 1, 0))" % WAND
    xml += c.text("S8_AnwZ", ky, x0, w, 0.9,
                  c.para([c.run("=" + gut, 22, c.INK, c.F_LIGHT, fmt="#,##0"),
                          c.run(" von ", 10, c.MUTED), c.run("=" + anzahl(WAND), 10, c.MUTED, fmt="#,##0"),
                          c.run(" Wandschichten ab 17,5 cm", 10, c.MUTED)]), valign="Bottom")
    return xml, ky + 0.9


# ---------------------------------------------------------------- X050 Rangliste aus Zeichen
def rangliste(x0, top, w, rh=0.38):
    """Die N_RANG groessten Nutzungen (je Funktion die Summe der Raumflaechen); der Balken misst gegen die groesste."""
    summe_n = FLAECHE_N
    mx = 'Max(Sum(IIf(%s, CDbl(Fields!Flaeche.Value), 0.0), "S8_TbRang_G"), "S8_TbRang")' % RAUM
    nmax = 29
    n = "CInt(%d * %s)" % (nmax, quote(summe_n, mx))
    rowb = c.edge(["Bottom"], c.HAIR, "0.5pt")
    rows = [("daten", rh, [
        c.cell("S8_RD1", c.run("=" + rang_nr("S8_TbRang"), 7, c.FAINT, c.F_SEMI, fmt="00"), border_xml=rowb, pad=(0, 0, 0, 0)),
        c.cell("S8_RD2", c.run("=" + kurz("First(" + NUTZUNG + ")", 17), 8, c.INK, c.F_SEMI), border_xml=rowb, pad=(2, 0, 2, 0)),
        c.cell("S8_RD3", c.para([c.run('=StrDup(%s, "█")' % n, 6.5, c.BLUE, MONO),
                                 c.run('=StrDup(%d - %s, "█")' % (nmax, n), 6.5, c.HAIR, MONO)]),
               border_xml=rowb, pad=(0, 0, 0, 0)),
        c.cell("S8_RD4", c.para([c.run("=" + zf(summe_n), 8.5, c.INK, c.F_SEMI), c.run(" m²", 7, c.FAINT)]), "Right",
               border_xml=rowb, pad=(0, 0, 0, 0)),
    ])]
    tb = c.tablix("S8_TbRang", 0, 0, [0.6, 2.7, 3.7, 1.8], rows, group="=" + NUTZUNG, sort="=" + RANG, sort_desc=True,
                  filter_expr=RAUM, repeat_header=False)
    tb = mit_deckel(tb, RANG, N_RANG)
    return c.rect("S8_FeldRang", top, x0, w, N_RANG * rh + 0.1, tb), top + N_RANG * rh


# ---------------------------------------------------------------- X060 Farbskala-Kacheln
def kacheln(x0, top, w, rh=1.14):
    """3 x 3 Kacheln: die N_RANG groessten Nutzungen, Rang 1 links oben, zeilenweise absteigend.
    Drei Tabellen (je eine Spalte der Matrix) zeigen jede dritte Gruppe; die uebrigen Zeilen sind unsichtbar,
    fehlende Nutzungen ergeben keine Kachel. Tonwert = Wurzel aus Flaeche / groesste Nutzung."""
    spalte = w / 3
    a = [int(c.SURFACE[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c.BLUE[i:i + 2], 16) for i in (1, 3, 5)]
    weiss = "<Border><Color>%s</Color><Style>Solid</Style><Width>3pt</Width></Border>" % c.WHITE
    inner = ""
    for k in range(3):
        tb = "S8_Heat%d" % k
        mx = 'Max(Sum(IIf(%s, CDbl(Fields!Flaeche.Value), 0.0), "%s_G"), "%s")' % (RAUM, tb, tb)
        t = "Math.Sqrt(%s / IIf(%s = 0, 1.0, %s))" % (FLAECHE_N, mx, mx)
        farbe = '="#" & ' + " & ".join('Right("0" & Hex(CInt(%d + (%d) * %s)), 2)' % (a[i], b[i] - a[i], t) for i in range(3))
        schrift = '=IIf(%s > 0.8, "%s", "%s")' % (t, c.WHITE, c.INK)
        schrift2 = '=IIf(%s > 0.8, "%s", "%s")' % (t, c.SKY, c.MUTED)
        inhalt = c.cell("S8_KH%d" % k, [
            c.para([c.run("=" + kurz("First(" + NUTZUNG + ")", 16), 7.5, schrift, c.F_SEMI)]),
            c.para([c.run("=" + zf(FLAECHE_N), 13, schrift, c.F_LIGHT), c.run(" m²", 8, schrift2)]),
        ], valign="Middle", pad=(9, 2, 4, 2), border_xml=weiss, bg_expr=farbe)
        gruppe = ("<Group Name=\"%s_G\"><GroupExpressions><GroupExpression>=%s</GroupExpression></GroupExpressions>%s</Group>"
                  % (tb, c.esc(NUTZUNG), c.topn(RANG, N_RANG)))
        sortierung = ("<SortExpressions><SortExpression><Value>=%s</Value><Direction>Descending</Direction></SortExpression>"
                      "</SortExpressions>" % c.esc(RANG))
        sichtbar = "<Visibility><Hidden>=(%s - 1) Mod 3 &lt;&gt; %d</Hidden></Visibility>" % (c.esc(rang_nr(tb)), k)
        inner += ('<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
                  "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                  "</TablixCells></TablixRow></TablixRows></TablixBody>"
                  "<TablixColumnHierarchy><TablixMembers><TablixMember/></TablixMembers></TablixColumnHierarchy>"
                  "<TablixRowHierarchy><TablixMembers><TablixMember>%s%s%s</TablixMember></TablixMembers></TablixRowHierarchy>"
                  "<DataSetName>AllplanReport</DataSetName>%s"
                  "<Top>0cm</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>"
                  "<Style><Border><Style>None</Style></Border></Style></Tablix>"
                  % (tb, c.cm(spalte), c.cm(rh), inhalt, gruppe, sortierung, sichtbar, c.filters(RAUM),
                     c.cm(k * spalte), c.cm(rh), c.cm(spalte)))
    return c.rect("S8_FeldHeat", top, x0, w, 3 * rh + 0.1, inner), top + 3 * rh


# ---------------------------------------------------------------- Bausteine
# Hoehe des Inhalts (ab Blockanfang, ohne Etikett); zwei Bausteine nebeneinander teilen sich die groessere.
KOPF = 1.45                      # Abschnittskopf: Inhalt beginnt bei top + 1,45
H_R1 = KOPF + 5.57               # X010 (die Typo-Skala ist hoeher als der Bericht)
H_R2 = KOPF + 3.18
H_R3 = KOPF + 4.1                # X040: die Zeichentabelle ist hoeher als die Anwendung
H_R4 = KOPF + 3 * 1.14           # X050/X060


@b.baustein("X010", "Schriftstufen")
def x010(top, left, w):
    xml = overline("S8_X01", top, left, w, "Schrift", "Schriftstufen des Reports")
    inhalt, _ = typo_skala(left, top + KOPF, w)
    return xml + inhalt + etikett("S8_E01", top + H_R1 + 0.1, left, w, "X010", "Typo-Skala, drei Schnitte der Segoe UI")


@b.baustein("X020", "Bericht in Worten")
def x020(top, left, w):
    xml = overline("S8_X02", top, left, w, "Auszeichnung", "Bericht in Worten")
    inhalt, _ = fliesstext(left, top + KOPF, w)
    return xml + inhalt + etikett("S8_E02", top + H_R1 + 0.1, left, w, "X020", "TextRuns mit Ausdruck, darunter HTML")


@b.baustein("X030", "Farbpalette")
def x030(top, left, w):
    xml = overline("S8_X03", top, left, w, "Farbe", "Die Palette des Reports")
    inhalt, _ = palette(left, top + KOPF, w)
    return xml + inhalt + etikett("S8_E03", top + H_R2 + 0.15, left, w, "X030",
                                  "Rechtecke mit Hintergrundfarbe, Werte aus core.py, kein Verlauf, keine Transparenz")


@b.baustein("X040", "Zeichen und Schichtarten")
def x040(top, left, w):
    lw = 8.8
    rw = w - lw - 0.4
    rx = left + lw + 0.4
    xml = overline("S8_X04", top, left, lw, "Zeichen", "Symbole ohne Bilddatei")
    xml += zeichen(left, top + KOPF, lw)[0]
    xml += overline("S8_X04b", top, rx, rw, "Anwendung", "Häufigste Schichtarten mit Befund")
    xml += anwendung(rx, top + KOPF, rw)[0]
    return xml + etikett_x("S8_E04", top + H_R3 + 0.1, left, w, "X040",
                           '"Segoe UI Symbol, Zeichen und Farbe per Ausdruck (IIf), je Materialgruppe und Dicke eine Zeile" & '
                           'IIf(%s > %d, " · die %d häufigsten von " & %s & " Schichtarten", "")'
                           % (N_SCHICHTARTEN, N_ANW, N_ANW, N_SCHICHTARTEN),
                           "Segoe UI Symbol, Zeichen und Farbe per Ausdruck (IIf), je Materialgruppe und Dicke eine Zeile")


@b.baustein("X050", "Rangliste aus Zeichen")
def x050(top, left, w):
    xml = overline("S8_X05", top, left, w, "Rangfolge", "Nutzungen nach Fläche")
    inhalt, _ = rangliste(left, top + KOPF, w)
    return xml + inhalt + etikett_x("S8_E05", top + H_R4 + 0.1, left, w, "X050",
                                    '"Balken aus Zeichen (StrDup, Consolas)" & IIf(%s > %d, " · die %d größten von " & %s & " Nutzungen", "")'
                                    % (N_NUTZUNGEN, N_RANG, N_RANG, N_NUTZUNGEN),
                                    "Balken aus Zeichen (StrDup, Consolas), die größten Nutzungen")


@b.baustein("X060", "Farbskala-Kacheln")
def x060(top, left, w):
    xml = overline("S8_X06", top, left, w, "Farbskala", "Fläche als Tonwert")
    inhalt, _ = kacheln(left, top + KOPF, w)
    return xml + inhalt + etikett("S8_E06", top + H_R4 + 0.1, left, w, "X060", "Tonwert = √(Fläche ÷ größte Nutzung), per Hex()")


# ---------------------------------------------------------------- Seite
def seite():
    x0, w = c.INSET, c.CONTENT_W
    lw = 8.8
    rw = w - lw - 0.4
    rx = x0 + lw + 0.4
    items = seitenkopf(8, "Text, Symbole und Flächen", "Schrift, Auszeichnung, Zeichen, Farbskala")
    t1 = 3.3
    items += x010(t1, x0, lw) + x020(t1, rx, rw)
    t2 = t1 + H_R1 + 0.8
    items += x030(t2, x0, w)
    t3 = t2 + H_R2 + 0.8
    items += x040(t3, x0, w)
    t4 = t3 + H_R3 + 0.8
    items += x050(t4, x0, lw) + x060(t4, rx, rw)
    return items
