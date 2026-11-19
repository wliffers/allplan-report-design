# -*- coding: utf-8 -*-
"""Seite 4 - Messanzeigen und Kennwerte: Halbkreis-Tachos, Fortschrittsringe, Zielbalken (Bullet-Graph),
Fortschrittsbalken mit Zielbereich, Ampeln (StateIndicator und Textsymbol) und Kennzahl-Kacheln.

Das Ziel fuer den Fensterflaechenanteil ist der Report-Parameter Ziel_Fensteranteil (wie auf Seite 1 und 7); die uebrigen
Zielwerte sind feste Annahmen."""
import re

import bausteine as b
import core as c
import viz as v
from bausteine import (WAND, RAUM, FENSTER, TUER, MIT_MATERIAL, IST_BETON, IST_VERKEHR, MATGRUPPE, summe, anzahl, raw,
                       quote, ist, overline, etikett, seitenkopf, fortschritt)

# ---------------------------------------------------------------- Annahmen (Zielwerte)
ZIEL_P = "Parameters!Ziel_Fensteranteil.Value"                    # Report-Parameter, Prozent (Vorgabe 20): Ziel = mindestens so viel
ZIEL_F = "Math.Min(39.0, Math.Max(1.0, %s))" % ZIEL_P             # fuer die Skala 0..40 begrenzt
ZIEL_TXT = 'Format(%s / 100, "0 %%")' % ZIEL_P                    # "20 %", wie auf Seite 1 und 7
ZIEL_RAUM = 25              # mittlere Raumflaeche in m2, Untergrenze
AUSSEN_DICKE = 0.2          # Aussenwand: Wandschicht aus Beton oder Mauerwerk ab dieser Dicke (m)
LEER = "–"                  # Anzeige, wenn die Grundlage fehlt

TACHO_R = 64                 # Radius des Halbkreises in Prozent der Panelhoehe
TACHO_PIVOT = 70             # Lage des Drehpunkts in Prozent der Panelhoehe

# ---------------------------------------------------------------- Kennwerte als Ausdruck (Bruch 0..1 bzw. Zahl)
# Keine Projektnamen: Materialgruppe (IST_BETON), Bauteilart (Objektnummer) und Nutzungswort (IST_VERKEHR).
AUSSENWAND = ('(%s And (%s Or %s = "Mauerwerk") And CDbl(Fields!Dicke.Value) >= %s)'
              % (WAND, IST_BETON, MATGRUPPE, AUSSEN_DICKE))
BETON = summe("Volumen", "(%s And %s)" % (MIT_MATERIAL, IST_BETON))
AUSSEN = summe("Flaeche", AUSSENWAND)
AUSSEN_L = summe("Laenge", AUSSENWAND)
RAUM_FL = summe("Flaeche", RAUM)
VERKEHR = summe("Flaeche", "(%s And %s)" % (RAUM, IST_VERKEHR))
Q_FENSTER = quote(summe("Flaeche", FENSTER), AUSSEN)
Q_VERKEHR = quote(VERKEHR, RAUM_FL)
Q_BETON = quote(BETON, summe("Volumen", MIT_MATERIAL))
Q_EFF = quote(RAUM_FL, summe("Flaeche", ist(4, 704)))
RAUM_MITTEL = quote(RAUM_FL, anzahl(RAUM))
OEFFNUNG = "(10 * %s)" % quote("(%s + %s)" % (anzahl(FENSTER), anzahl(TUER)), AUSSEN_L)

# Grundlage je Kennwert: ohne sie zeigt die Anzeige "-" und einen leeren Bogen statt 0 % mit roter Ampel.
B_FENSTER = "(%s > 0 And %s > 0)" % (AUSSEN, summe("Flaeche", FENSTER))
B_RAUM = "(%s > 0)" % RAUM_FL
B_BETON = "(%s > 0)" % summe("Volumen", MIT_MATERIAL)
B_EFF = "(%s > 0 And %s > 0)" % (RAUM_FL, summe("Flaeche", ist(4, 704)))
B_OEFF = "(%s > 0 And %s + %s > 0)" % (AUSSEN_L, anzahl(FENSTER), anzahl(TUER))
Q_NUTZ = "IIf(%s, 1 - %s, 0.0)" % (B_RAUM, Q_VERKEHR)





def pct(q):
    """Bruch in Prozent (Zahl 0..100)."""
    return "(%s * 100)" % q


def lim(wert, hi):
    """Wert auf 0..hi begrenzen: ueber dem Skalenende bleibt der Zeiger am Anschlag (die Zahl daneben bleibt richtig)."""
    return "Math.Min(%s, Math.Max(0.0, %s))" % (float(hi), wert)


def mit(basis, wert, sonst="0.0"):
    return "IIf(%s, %s, %s)" % (basis, wert, sonst)


def zahltext(wert, basis, fmt="0.0", deckel=None):
    """Zahl als Text oder "-", wenn die Grundlage fehlt; ueber dem Deckel steht ">999" statt einer zu breiten Zahl."""
    z = 'Format(%s, "%s")' % (wert, fmt)
    if deckel:
        z = 'IIf(%s > %s, ">%s", %s)' % (wert, deckel, deckel, z)
    return 'IIf(%s, %s, "%s")' % (basis, z, LEER)


def gross(wert):
    """Ganze Zahl mit Tausenderpunkt."""
    return 'Format(%s, "#,##0")' % wert


# ---------------------------------------------------------------- Helfer dieser Seite (Kandidaten fuer bausteine.py)
def _clean(xml):
    """Gauge-Standardgrau durch die Farben des Systems ersetzen, Rahmenlinie des Gauges ausschalten."""
    xml = xml.replace(v.border("#D1D5DB", "Solid", "0.75pt"), v.border(c.WHITE, "None", "0.5pt"))
    xml = re.sub(r"(<ScaleRange Name=\"[^\"]*\"><Style><BackgroundColor>[^<]*</BackgroundColor>)</Style>",
                 lambda m: m.group(1) + "<Border><Style>None</Style></Border></Style>", xml)
    xml = xml.replace("</EndWidth><DistanceFromScale>", "</EndWidth><BackgroundGradientType>None</BackgroundGradientType><DistanceFromScale>")
    return xml.replace("#374151", c.MUTED).replace("#6B7280", c.FAINT).replace("#9CA3AF", c.FAINT)


def ausgeblendet(xml, bedingung):
    """Skalenbereich per Ausdruck ausblenden (Bedingung ohne fuehrendes =)."""
    return xml.replace("</ScaleRange>", "<Hidden>=%s</Hidden></ScaleRange>" % c.esc(bedingung))


def glabel(name, text, top, left, h, w, size, color, font=c.F_LIGHT, align="Center"):
    """Text im Gauge (GaugeLabel, Lage in Prozent des Panels). Liegt im Gauge selbst und ueberlagert keine Textbox."""
    return ('<GaugeLabel Name="%s"><Style><FontFamily>%s</FontFamily><FontSize>%spt</FontSize><Color>%s</Color>'
            "<TextAlign>%s</TextAlign><VerticalAlign>Middle</VerticalAlign></Style><Text>%s</Text><Top>%s</Top><Left>%s</Left>"
            "<Height>%s</Height><Width>%s</Width><ResizeMode>None</ResizeMode></GaugeLabel>"
            % (name, font, size, color, align, c.esc(text), round(top, 2), round(left, 2), round(h, 2), round(w, 2)))


def zahl_label(name, text_expr, basis, einheit, top, h, size, mitte=54.0, breite=36.0):
    """Grosse Zahl und kleinere Einheit als zwei GaugeLabels: Zahl rechtsbuendig bis zur Mitte, Einheit ab der Mitte.
    Fehlt die Grundlage, steht nur "-" da."""
    return (glabel(name + "_z", "=" + text_expr, top, mitte - breite, h, breite, size, c.INK, c.F_LIGHT, "Right")
            + glabel(name + "_u", '=IIf(%s, "%s", "")' % (basis, einheit), top, mitte - 0.2, h, 16, size * 0.5, c.MUTED, c.F, "Left"))


def tacho(name, top, left, w, h, value_expr, vmax, baender, labels, basis, farbe_zeiger=c.INK):
    """Schlanker Halbkreis-Tacho: duenne Farbbaender, schmale Nadel; ohne Rahmen, ohne Ticks.
    Ohne Grundlage: nur eine helle Spur, keine Nadel."""
    rg = "".join(ausgeblendet(v.srange("%s_b%d" % (name, i), a, b_, col, "6", "2", "Inside"), "Not " + basis)
                 for i, (a, b_, col) in enumerate(baender))
    rg += ausgeblendet(v.srange(name + "_leer", 0, vmax, c.HAIR, "6", "2", "Inside"), basis)
    r = _clean(v.radial(name + "_r", "=" + mit(basis, lim(value_expr, vmax)), 0, vmax, ranges=rg, start=90, sweep=180, ticks=False,
                        labels=False, top=0, left=0, h=100, w=100, pivot=(50, TACHO_PIVOT), radius=TACHO_R, needle="Tapered",
                        color=farbe_zeiger, pwidth="7", dist="-4", scale_w="1", cap=True, fstyle_="None", frame="Rectangular"))
    r = r.replace("<Type>Needle</Type>", "<Type>Needle</Type><Hidden>=%s</Hidden>" % c.esc("Not " + basis), 1)
    return v.gauge(name, top, left, w, h, radials=r, labels=labels, autolayout="false")


def ring(name, top, left, w, h, value_expr, farbe, labels, basis, vmax=100):
    """Fortschrittsring: heller Bogen als Spur, Fuellbogen (RadialPointer Bar) in Farbe, 270 Grad."""
    track = v.srange(name + "_t", 0, vmax, c.HAIR, "9", "0", "Cross")
    r = _clean(v.radial(name + "_r", "=" + mit(basis, lim(value_expr, vmax)), 0, vmax, ranges=track, start=135, sweep=270, ticks=False,
                        labels=False, top=0, left=0, h=100, w=100, pivot=(50, 50), radius=40, ptype="Bar", color=farbe, pwidth="9",
                        dist="0", scale_w="1", cap=False, fstyle_="None", frame="Circular"))
    r = r.replace("<Placement>Inside</Placement>", "<Placement>Cross</Placement>")
    r = r.replace("<Type>Bar</Type>", "<Type>Bar</Type><Hidden>=%s</Hidden>" % c.esc("Not " + basis), 1)
    return v.gauge(name, top, left, w, h, radials=r, labels=labels, autolayout="false")


def _zahl(x):
    return isinstance(x, (int, float))


def _minus(a, b):
    """a - b: Zahl, wenn beide Zahlen sind, sonst VB-Ausdruck."""
    return round(a - b, 4) if _zahl(a) and _zahl(b) else "(%s) - (%s)" % (a, b)


def bullet(name, top, left, w, h, value_expr, vmax, baender, ziel_nach, ziel, basis, farbe=c.NAVY):
    """Zielbalken (Bullet-Graph) als Balkendiagramm: Bereiche gestapelt im Hintergrund, Ist als schmaler Balken auf der
    zweiten Achse, Zielmarke als Strip Line. (Der Bereichs-Streifen des LinearGauge bleibt in kleinen Panels zu duenn.)
    Ohne Grundlage fehlt der Ist-Balken.
    baender: (von, bis, Farbe), Grenzen als Zahl oder VB-Ausdruck ohne "="; die Zielmarke steht an der Grenze zwischen
    Band ziel_nach und dem naechsten Band, ziel ist deren Lage (Zahl oder Ausdruck)."""
    d = vmax * 0.005
    teile = []                               # Breite je Stueck; die Zielmarke selbst ist ein dunkles Stueck zwischen zwei Baendern
    for i, (a, e, col) in enumerate(baender):
        breite = _minus(e, a)
        if i in (ziel_nach, ziel_nach + 1):
            breite = _minus(breite, d)
        teile.append((breite, col))
        if i == ziel_nach:
            teile.append((2 * d, c.INK))
    namen = ["t%d" % i for i in range(len(teile))] + ["ist"]
    serien = [v.S("%s_t%d" % (name, i), {"Y": "=%s" % br}, typ="Bar", sub="Stacked", color=f,
                  custom_xml=v.custom(PointWidth="1")) for i, (br, f) in enumerate(teile)]
    serien.append(v.S(name + "_ist", {"Y": "=" + mit(basis, lim(value_expr, vmax))}, typ="Bar", sub="Plain", color=farbe,
                      vaxis="Secondary", custom_xml=v.custom(PointWidth="0.3")))
    marke = v.strip(_minus(ziel, d) if _zahl(ziel) else "=" + c.esc(_minus(ziel, d)), width=2 * d, color=c.INK)
    return v.chart(
        name, top, left, w, h, serien, [], nomember=True, names=namen,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False, line=False)],
                     val_axes=[v.axis("Primary", visible=True, hide_labels=True, line=False, minimum="0", maximum=str(vmax), strips=marke),
                               v.axis("Secondary", visible=False, line=False, minimum="0", maximum=str(vmax), location="Opposite")],
                     pos=(0, 0, 100, 100), inner=(0, 0, 100, 100)))


def ampel(name, top, left, size, value_expr, states, basis):
    """StateIndicator mit eigenen Schwellen. states: Liste (Name, von, bis, Farbe, Stil).
    Ohne Grundlage (Wert -1) zeigt er einen ruhigen grauen Kreis statt einer roten Ampel."""
    stufen = [("Grau", -1, -0.5, c.HAIR, "Circle")] + list(states)
    s = v.stateind(name + "_s", "=" + mit(basis, lim(value_expr, 100), "-1.0"), -1, 100, stufen, style="Circle", top=8, left=8, h=84, w=84)
    return v.gauge(name, top, left, size, size, states=s, autolayout="false")


def kachel_hell(name, top, left, w, wert, basis, einheit, label, note_expr):
    """Helle Kennzahl-Kachel (wie Seite 1): grosse Zahl, Einheit nur wenn es eine Zahl gibt, Beschriftung, Fussnote."""
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, w - 0.4, 1.05,
                      c.para([c.run("=" + zahltext(wert, basis, "N1"), 22, c.INK, c.F_LIGHT),
                              c.run('=IIf(%s, " %s", "")' % (basis, einheit), 10, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run(label.upper(), 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4, c.run(note_expr, 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


def kachel_dunkel(name, top, left, w, wert, basis, label, note):
    """Dunkle Kennzahl-Kachel: weisse Zahl auf Marine, Beschriftung und Fussnote in hellem Blau."""
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.SKY)
             + c.text(name + "_v", 0.42, 0.32, w - 0.4, 1.05,
                      c.para([c.run("=" + zahltext(wert, basis, "N1"), 22, c.WHITE, c.F_LIGHT)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run(label.upper(), 7, c.WHITE, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4, c.run(note, 7, c.SKY, c.F)))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.NAVY)


def kachel_vergleich(name, top, left, w, wert_q, basis, label, ziel, hoeher_ist_besser, ziel_text):
    """Kachel mit Vergleichszeile: ' 3,3 %-Pkt. unter Ziel 20 %' in Bewertungsfarbe (Gruen = erfuellt, Amber = Achtung).
    ziel: Zielwert in Prozent (Zahl oder VB-Ausdruck), ziel_text: VB-Ausdruck fuer den Text "Ziel 20 %".
    Ohne Grundlage: "-" und eine ruhige graue Zeile."""
    d = "(%s - %s)" % (pct(wert_q), ziel)
    ok = "%s >= 0" % d if hoeher_ist_besser else "%s <= 0" % d
    farbe = '=IIf(%s, IIf(%s, "%s", "%s"), "%s")' % (basis, ok, c.GREEN, c.AMBER, c.FAINT)
    zeile = ('=IIf(%s, IIf(%s >= 0, "▲ ", "▼ ") & Format(Abs(%s), "0.0") & " %%-Pkt. " & IIf(%s >= 0, "über", "unter") & " " & %s,'
             ' "keine Fenster oder Außenwand")' % (basis, d, d, d, ziel_text))
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, w - 0.4, 1.05,
                      c.para([c.run("=" + zahltext(wert_q, basis, "0 %"), 22, c.INK, c.F_LIGHT)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run(label.upper(), 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4,
                      c.para([c.run(zeile, 7.5, farbe, "Segoe UI Semibold")])))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


MINI_SAEULEN = 8        # Deckel der Mini-Saeulen in der Kachel


def kachel_spark(name, top, left, w):
    """Kachel mit Mini-Diagramm: Raumflaeche je Nutzung als Saeulen ohne Achsen (hoechstens 8, groesste zuerst), Zahl links.
    Ab 1.000 bzw. 10.000 m2 wird die Zahl kleiner gesetzt, damit sie neben die Saeulen passt."""
    flaeche = "Sum(CDbl(Fields!Flaeche.Value))"
    erstes = 'Min(Fields!Funktion.Value) & "   "'
    eindeutig = ("%s + CDbl(Asc(Left(%s, 1))) * 0.000001 + CDbl(Asc(Mid(%s, 2, 1))) * 0.000000001 + CDbl(Asc(Mid(%s, 3, 1))) * 0.000000000001"
                 % (flaeche, erstes, erstes, erstes))
    mini = v.chart(
        name + "_c", 0.5, w - 1.65, 1.5, 0.95,
        [v.S("F", {"Y": "=" + flaeche}, typ="Column", sub="Plain", color=c.BLUE, custom_xml=v.custom(PointWidth="0.55"))],
        [("=Fields!Funktion.Value", "=" + eindeutig, "Descending")],
        areas=v.area(cat_axes=[v.axis("Primary", visible=False, line=False)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0")],
                     pos=(0, 0, 100, 100), inner=(0, 0, 100, 100), style="<BackgroundColor>%s</BackgroundColor>" % c.SURFACE),
        style="<Style><Border><Style>None</Style></Border><BackgroundColor>%s</BackgroundColor></Style>" % c.SURFACE,
        extra=c.filters(raw(RAUM)))
    mini = mini.replace("</GroupExpressions></Group>", "</GroupExpressions>" + c.topn(eindeutig, MINI_SAEULEN) + "</Group>", 1)
    zahl_run = c.run("=" + gross(RAUM_FL), 22, c.INK, c.F_LIGHT).replace(
        "<FontSize>22pt</FontSize>", "<FontSize>=%s</FontSize>" % c.esc('IIf(%s >= 10000, "13pt", IIf(%s >= 1000, "16pt", "22pt"))' % (RAUM_FL, RAUM_FL)))
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, w - 2.0, 1.05,
                      c.para([zahl_run, c.run(" m²", 10, c.MUTED, c.F)]), valign="Bottom")
             + mini
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run("RAUMFLÄCHE NACH NUTZUNG", 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4,
                      c.run(b.rang_titel('CountDistinct(IIf(%s, Fields!Funktion.Value, Nothing))' % RAUM, MINI_SAEULEN, "die ",
                                         " größten, größte zuerst", "die größte Nutzung", "die größten, größte zuerst"), 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


def status_symbol(wert, basis, ok, warn, hoeher_ist_besser):
    """Ausdruecke fuer Textsymbol, Farbe und Wort. wert in Prozent bzw. Einheit; ok/warn sind die beiden Schwellen.
    Haken = im Ziel; Pfeil nach unten/oben = Abweichung in die jeweilige Richtung. Ohne Grundlage: Strich, graue Schrift."""
    if hoeher_ist_besser:
        gut, mittel, pfeil = "%s >= %s" % (wert, ok), "%s >= %s" % (wert, warn), "▼"
    else:
        gut, mittel, pfeil = "%s <= %s" % (wert, ok), "%s <= %s" % (wert, warn), "▲"
    sym = '=IIf(%s, IIf(%s, "✓", "%s"), "%s")' % (basis, gut, pfeil, LEER)
    farbe = '=IIf(%s, IIf(%s, "%s", IIf(%s, "%s", "%s")), "%s")' % (basis, gut, c.GREEN, mittel, c.AMBER, c.RED, c.FAINT)
    wort = '=IIf(%s, IIf(%s, "im Ziel", IIf(%s, "knapp", "verfehlt")), "ohne Daten")' % (basis, gut, mittel)
    return sym, farbe, wort


SYMBOL = "Segoe UI Symbol"
SPALTE_W = 8.8          # Breite eines Bausteins in der Zweispaltenanordnung


# ---------------------------------------------------------------- Bausteine (je ein Block: Abschnittskopf, Inhalt, Etikett)
@b.baustein("M020", "Tacho-Reihe")
def m020(top, left, w):
    items = overline("S4_A1", top, left, w, "Messanzeigen", "Kennwerte im Zielbereich")
    cw, gap = 5.73, 0.4
    gy, g_h = top + 1.4, 3.3
    tachos = [
        ("S4_T1", Q_FENSTER, B_FENSTER, 40,
         [(0, "=%s / 2" % ZIEL_F, c.RED), ("=%s / 2" % ZIEL_F, "=" + ZIEL_F, c.AMBER), ("=" + ZIEL_F, 40, c.GREEN)],
         "Fensterflächenanteil", '="Ziel ab " & %s & "  ·  Glasfläche zu Außenwand"' % ZIEL_TXT),
        ("S4_T2", Q_VERKEHR, B_RAUM, 40, [(0, 20, c.GREEN), (20, 25, c.AMBER), (25, 40, c.RED)],
         "Verkehrsfläche", "Ziel höchstens 20 %  ·  Flure zu Raumfläche"),
        ("S4_T3", Q_BETON, B_BETON, 100, [(0, 40, c.RED), (40, 60, c.AMBER), (60, 100, c.GREEN)],
         "Betonanteil", "Ziel mindestens 60 %  ·  am Bauteilvolumen"),
    ]
    r_cm = TACHO_R / 100.0 * g_h
    for i, (n, q, basis, vmax, baender, titel, sub) in enumerate(tachos):
        lx = left + i * (cw + gap)
        ende = 100.0 * (cw / 2 - r_cm + 0.4) / cw                      # Mitte der Skalenenden in Prozent der Breite
        labels = (zahl_label(n, zahltext(pct(q), basis, "0", 999), basis, "%", TACHO_PIVOT + 5, 25, 22)
                  + glabel(n + "_0", "0", TACHO_PIVOT + 2, ende - 7, 10, 14, 6.5, c.FAINT, c.F)
                  + glabel(n + "_m", "%d %%" % vmax, TACHO_PIVOT + 2, 100 - ende - 7, 10, 14, 6.5, c.FAINT, c.F))
        items += tacho(n, gy, lx, cw, g_h, pct(q), vmax, baender, labels, basis)
        items += c.text(n + "_n", gy + 3.35, lx, cw - 0.05, 0.42, c.run(titel, 9.5, c.INK, c.F_SEMI), align="Center")
        items += c.text(n + "_s", gy + 3.82, lx, cw - 0.05, 0.38, c.run(sub, 7, c.MUTED), align="Center")
    items += etikett("S4_E1", gy + 4.25, left, w, "M020",
                     "RadialGauge Halbkreis, Bewertungsfarben; Ziele sind Annahmen. Außenwand = Wandschicht aus Beton oder "
                     "Mauerwerk ab 20 cm Dicke")
    return items


@b.baustein("M030", "Fortschrittsringe")
def m030(top, left, w):
    ry = top + 1.45
    items = overline("S4_A2", top, left, w, "Fortschritt", "Flächen im Verhältnis")
    ringe = [("S4_R1", Q_NUTZ, B_RAUM, c.BLUE, "Nutzfläche", "Raumfläche ohne Flure"),
             ("S4_R2", Q_EFF, B_EFF, c.NAVY, "Flächeneffizienz", "Raumfläche zu Deckenfläche")]
    for i, (n, q, basis, col, titel, sub) in enumerate(ringe):
        lx = left + i * 4.4
        items += ring(n, ry, lx, 4.3, 3.1, pct(q), col,
                      zahl_label(n, zahltext(pct(q), basis, "0", 999), basis, "%", 30, 40, 22, 54.0, 54.0), basis)
        items += c.text(n + "_n", ry + 3.15, lx, 4.3, 0.42, c.run(titel, 9.5, c.INK, c.F_SEMI), align="Center")
        items += c.text(n + "_s", ry + 3.62, lx, 4.3, 0.38, c.run(sub, 7, c.MUTED), align="Center")
    items += etikett("S4_E2", ry + 4.1, left, w, "M030", "RadialGauge 270°, RadialPointer Typ Bar auf heller Spur")
    return items


@b.baustein("M040", "Zielbalken (Bullet-Graph)")
def m040(top, left, w):
    ry = top + 1.45
    items = overline("S4_A3", top, left, w, "Ziel", "Ist gegen Ziel")
    dunkel, mittel, hell = c.RAMP[6], c.RAMP[7], c.SURFACE       # dunkel = schlecht, hell = gut
    zeilen = [
        ("S4_B1", "Fensterflächenanteil", '="Ziel ab " & ' + ZIEL_TXT, pct(Q_FENSTER), B_FENSTER, 40, 1, ZIEL_F, "0.0", "%",
         [(0, "%s / 2" % ZIEL_F, dunkel), ("%s / 2" % ZIEL_F, ZIEL_F, mittel), (ZIEL_F, 40, hell)]),
        ("S4_B2", "Verkehrsfläche", "Ziel bis 20 %", pct(Q_VERKEHR), B_RAUM, 40, 0, 20, "0.0", "%",
         [(0, 20, hell), (20, 25, mittel), (25, 40, dunkel)]),
        ("S4_B3", "Betonanteil", "Ziel ab 60 %", pct(Q_BETON), B_BETON, 100, 1, 60, "0", "%",
         [(0, 40, dunkel), (40, 60, mittel), (60, 100, hell)]),
        ("S4_B4", "Raumfläche je Raum", "Ziel ab %d m²" % ZIEL_RAUM, RAUM_MITTEL, B_RAUM, 30, 1, ZIEL_RAUM, "0.0", "m²",
         [(0, 20, dunkel), (20, ZIEL_RAUM, mittel), (ZIEL_RAUM, 30, hell)]),
    ]
    zh = 1.0
    for i, (n, titel, sub, wert, basis, vmax, ziel_nach, ziel, fmt, einheit, baender) in enumerate(zeilen):
        zy = ry + i * zh
        items += c.text(n + "_l", zy, left, 3.0, 0.5, c.run(titel, 8.5, c.INK, c.F_SEMI), valign="Bottom")
        items += c.text(n + "_n", zy + 0.5, left, 3.0, 0.4, c.run(sub, 7, c.MUTED), valign="Top")
        items += bullet(n, zy, left + 3.1, 4.2, 0.9, wert, vmax, baender, ziel_nach, ziel, basis)
        items += c.text(n + "_v", zy, left + 7.3, 1.5, 0.9,
                        c.para([c.run("=" + zahltext(wert, basis, fmt, 999), 12, c.INK, c.F_LIGHT),
                                c.run('=IIf(%s, " %s", "")' % (basis, einheit), 8, c.MUTED, c.F)], "Right"), valign="Middle")
    items += etikett("S4_E3", ry + 4.0, left, w, "M040",
                     "Balkendiagramm: Bänder gestapelt, Ist auf 2. Achse, Ziele angenommen")
    return items


@b.baustein("M050", "Fortschrittsbalken")
def m050(top, left, w):
    by = top + 1.45
    items = overline("S4_A4", top, left, w, "Anteile", "Fortschrittsbalken")

    def kopf(n, y, titel, sub, q, basis, fmt="0 %"):
        return (c.text(n + "_l", y, left, 6.0, 0.42, c.run(titel, 9.5, c.INK, c.F_SEMI))
                + c.text(n + "_n", y + 0.47, left, 6.0, 0.36, c.run(sub, 7.5, c.MUTED))
                + c.text(n + "_v", y, left + w - 2.2, 2.2, 0.83, c.run("=" + zahltext(q, basis, fmt), 17, c.INK, c.F_LIGHT),
                         align="Right", valign="Bottom"))

    # a: einfach (Baustein fortschritt)
    items += kopf("S4_P1", by, "Betonanteil", "am Bauteilvolumen", Q_BETON, B_BETON)
    items += fortschritt("S4_P1_b", by + 0.95, left, w, mit(B_BETON, lim(Q_BETON, 1)), c.MATERIAL[0][1], 0.2)
    # b: mit Ziel (Klammer unter dem Balken von der Zielmarke bis zum Skalenende, Lage folgt dem Parameter)
    b2 = by + 1.4
    items += kopf("S4_P2", b2, "Fensterflächenanteil", "Skala 0 bis 40 %", Q_FENSTER, B_FENSTER)
    items += fortschritt("S4_P2_b", b2 + 0.95, left, w, mit(B_FENSTER, lim("(%s) / 0.4" % Q_FENSTER, 1)), c.BLUE, 0.2)
    dk = 0.09                                                     # halbe Breite der Endstriche in Skalenwerten (ca. 0,04 cm)
    leer = "Transparent"
    enden = (v.strip("=" + c.esc("%s - %s" % (ZIEL_F, dk)), width=2 * dk, color=c.INK)       # Endstrich an der Zielmarke
             + v.strip(40 - 2 * dk, width=2 * dk, color=c.INK))                              # Endstrich am Skalenende
    klammer = v.chart(
        "S4_P2_k", b2 + 1.23, left, w, 0.2,
        [v.S("S4_P2_k0", {"Y": "=" + ZIEL_F}, typ="Bar", sub="Stacked", color=leer, custom_xml=v.custom(PointWidth="0.2")),
         v.S("S4_P2_k1", {"Y": "=40 - " + ZIEL_F}, typ="Bar", sub="Stacked", color=c.INK, custom_xml=v.custom(PointWidth="0.2"))],
        [], nomember=True, names=["k0", "k1"],
        areas=v.area(cat_axes=[v.axis("Primary", visible=False, line=False)],
                     val_axes=[v.axis("Primary", visible=True, hide_labels=True, line=False, minimum="0", maximum="40", strips=enden)],
                     pos=(0, 0, 100, 100), inner=(0, 0, 100, 100)),
        style="<Style><Border><Style>None</Style></Border><BackgroundColor>Transparent</BackgroundColor></Style>")
    items += (klammer
              + c.text("S4_P2_t", b2 + 1.45, left + w - 3.0, 3.0, 0.3, c.run('="Ziel ab " & ' + ZIEL_TXT, 7, c.MUTED), align="Right"))
    # c: zweifarbig
    b3 = b2 + 1.75
    achse = v.axis("Primary", visible=False, minimum="0", maximum="1")
    items += (c.text("S4_P3_l", b3, left, 6.0, 0.42, c.run("Raumfläche", 9.5, c.INK, c.F_SEMI))
              + c.text("S4_P3_n", b3 + 0.47, left, 6.0, 0.36, c.run("Verkehr und Nutzfläche, zusammen 100 %", 7.5, c.MUTED)))
    items += v.chart(
        "S4_P3_b", b3 + 0.95, left, w, 0.2,
        [v.S("S4_P3_a", {"Y": "=" + mit(B_RAUM, Q_VERKEHR)}, typ="Bar", sub="Stacked", color=c.RAMP[0], custom_xml=v.custom(PointWidth="1")),
         v.S("S4_P3_c", {"Y": "=" + Q_NUTZ}, typ="Bar", sub="Stacked", color=c.RAMP[4], custom_xml=v.custom(PointWidth="1")),
         v.S("S4_P3_d", {"Y": "=" + mit(B_RAUM, "0.0", "1.0")}, typ="Bar", sub="Stacked", color=c.HAIR, custom_xml=v.custom(PointWidth="1"))],
        [], nomember=True, names=["a", "b", "c"],
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)], val_axes=[achse], pos=(0, 0, 100, 100), inner=(0, 0, 100, 100)))
    items += (c.text("S4_P3_v1", b3 + 1.22, left, 4.0, 0.4,
                     c.para([c.run("■ ", 7, c.RAMP[0], SYMBOL), c.run("Verkehr ", 7.5, c.MUTED),
                             c.run("=" + zahltext(Q_VERKEHR, B_RAUM, "0 %"), 7.5, c.INK, c.F_SEMI)]))
              + c.text("S4_P3_v2", b3 + 1.22, left + w - 4.0, 4.0, 0.4,
                       c.para([c.run("■ ", 7, c.RAMP[4], SYMBOL), c.run("Nutzfläche ", 7.5, c.MUTED),
                               c.run("=" + zahltext(Q_NUTZ, B_RAUM, "0 %"), 7.5, c.INK, c.F_SEMI)], "Right")))
    items += etikett("S4_E4", b3 + 1.7, left, w, "M050", "Baustein fortschritt, Zielbereich als Linie, zwei Farben gestapelt")
    return items


@b.baustein("M060", "Ampel mit Schwellen")
def m060(top, left, w):
    ay = top + 1.4
    items = overline("S4_A5", top, left, w, "Status", "Ampel mit Schwellen")
    sp = [("Kennwert", 0, 2.9, None), ("Ist", 2.9, 1.3, "Right"), ("Ziel", 4.2, 1.5, None), ("Anzeige", 5.7, 1.1, None),
          ("Text", 6.8, 2.0, None)]
    for i, (head, ox, cwid, al) in enumerate(sp):
        items += c.text("S4_AH%d" % i, ay, left + ox, cwid, 0.4, c.run(head.upper(), 6.5, c.MUTED, c.F_SEMI), align=al,
                        pad=(10 if head == "Ziel" else 0, 0, 0, 0), valign="Bottom")
    items += c.line("S4_AHL", ay + 0.45, left, w, c.INK, "1pt")
    rot, gel, gru = c.RED, c.AMBER, c.GREEN

    def drei(a, b_, hoch):
        if hoch:
            return [("Rot", 0, a, rot, "ThreeSymbolCross"), ("Gelb", a, b_, gel, "ThreeSymbolExclamation"),
                    ("Gruen", b_, 100, gru, "ThreeSymbolCheck")]
        return [("Gruen", 0, a, gru, "ThreeSymbolCheck"), ("Gelb", a, b_, gel, "ThreeSymbolExclamation"),
                ("Rot", b_, 100, rot, "ThreeSymbolCross")]

    ampeln = [
        ("S4_M1", "Fensterflächenanteil", pct(Q_FENSTER), B_FENSTER, "0.0", "%", '="≥ " & ' + ZIEL_TXT, True, ZIEL_P,
         "(%s / 2)" % ZIEL_P, drei("=%s / 2" % ZIEL_P, "=" + ZIEL_P, True)),
        ("S4_M2", "Verkehrsfläche", pct(Q_VERKEHR), B_RAUM, "0.0", "%", "≤ 20 %", False, 20, 25, drei(20, 25, False)),
        ("S4_M3", "Betonanteil", pct(Q_BETON), B_BETON, "0", "%", "≥ 60 %", True, 60, 40, drei(40, 60, True)),
        ("S4_M4", "Raumfläche je Raum", RAUM_MITTEL, B_RAUM, "0.0", "m²", "≥ %d m²" % ZIEL_RAUM, True, ZIEL_RAUM, 20,
         drei(20, ZIEL_RAUM, True)),
    ]
    rh = 0.95
    for i, (n, titel, wert, basis, fmt, einheit, ziel, hoch, ok, warn, states) in enumerate(ampeln):
        yy = ay + 0.55 + i * rh
        sym, farbe, wort = status_symbol(wert, basis, ok, warn, hoch)
        items += c.text(n + "_l", yy, left, 2.9, rh - 0.05, c.run(titel, 8.5, c.INK, c.F_SEMI), valign="Middle")
        items += c.text(n + "_i", yy, left + 2.9, 1.3, rh - 0.05,
                        c.para([c.run("=" + zahltext(wert, basis, fmt, 999), 9, c.TEXT),
                                c.run('=IIf(%s, " %s", "")' % (basis, einheit), 7, c.FAINT)], "Right"), valign="Middle")
        items += c.text(n + "_z", yy, left + 4.2, 1.5, rh - 0.05, c.run(ziel, 8, c.MUTED), valign="Middle", pad=(10, 0, 0, 0))
        items += ampel(n + "_g", yy + 0.12, left + 5.8, 0.7, wert, states, basis)
        items += c.text(n + "_t", yy, left + 6.8, 0.5, rh - 0.05, c.run(sym, 10, farbe, SYMBOL), valign="Middle")
        items += c.text(n + "_w", yy, left + 7.3, 1.5, rh - 0.05, c.run(wort, 7.5, c.MUTED), valign="Middle")
        items += c.line(n + "_x", yy + rh - 0.02, left, w)
    items += etikett("S4_E5", top + 6.3, left, w, "M060", "StateIndicator mit Schwellen (ohne Grundlage grau); Textsymbol per Ausdruck")
    return items


@b.baustein("K030", "Kennzahl-Kacheln")
def k030(top, left, w):
    items = overline("S4_A6", top, left, w, "Kennzahlen", "Kacheln in vier Ausführungen")
    ky = top + 1.45
    kg = 0.4
    kw = (w - 3 * kg) / 4
    items += kachel_hell("S4_K1", ky, left, kw, RAUM_MITTEL, B_RAUM, "m²", "Ø Raumfläche", '=%s & " Räume im Modell"' % anzahl(RAUM))
    items += kachel_dunkel("S4_K2", ky, left + (kw + kg), kw, OEFFNUNG, B_OEFF, "Öffnungen je 10 m", "Fenster und Türen, Außenwand")
    items += kachel_vergleich("S4_K3", ky, left + 2 * (kw + kg), kw, Q_FENSTER, B_FENSTER, "Fensterflächenanteil", ZIEL_P, True,
                              '"Ziel " & ' + ZIEL_TXT)
    items += kachel_spark("S4_K4", ky, left + 3 * (kw + kg), kw)
    items += etikett("S4_E6", ky + 2.65, left, w, "K030",
                     "Kachel hell (wie Seite 1), dunkel, mit Vergleichszeile in Bewertungsfarbe, mit Mini-Diagramm (höchstens 8 Säulen)")
    return items


# ---------------------------------------------------------------- Seite
def seite():
    x0, w = c.INSET, c.CONTENT_W
    rx = x0 + SPALTE_W + 0.4
    items = seitenkopf(4, "Messanzeigen und Kennwerte", "Tacho, Zielbalken, Ampel, Kachel")
    items += m020(3.3, x0, w)
    items += m030(9.8, x0, SPALTE_W)
    items += m040(9.8, rx, SPALTE_W)
    items += m050(16.2, x0, SPALTE_W)
    items += m060(16.2, rx, SPALTE_W)
    items += k030(23.4, x0, w)
    return items
