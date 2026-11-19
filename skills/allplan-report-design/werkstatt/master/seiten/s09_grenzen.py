# -*- coding: utf-8 -*-
"""Seite 9 - Grenzen: was geht, was nicht. Reiner Text, keine Daten aus dem Modell: die Seite sieht mit jedem
Datensatz gleich aus. Inhalt ausschliesslich aus skill/allplan-report-design/references/grenzen.md."""
import core as c
import bausteine as b
from bausteine import etikett, overline, seitenkopf

TITEL = "Grenzen: was geht, was nicht"

SYM = "Segoe UI Symbol"

# (Zeichen, Ueberschrift, Farbe, [(Stichwort, Halbsatz)]) - Stichwort hoechstens 4 Woerter
SPALTEN = [
    ("✓", "Geht", c.GREEN, [
        ("Säulen, Torten, Ringe", "auch TreeMap und Pareto"),
        ("Tacho und Ampel-Zeichen", "Messanzeigen, Seite 4"),
        ("Gruppen und Summen", "auch Kreuztabelle mit Farbskala"),
        ("Bauteilbilder in 3D", "Strichzeichnung je Bauteil, Seite 6"),
        ("Planausschnitt als Bild", "wie im Teilbild, mit Schraffur"),
        ("Segoe UI in drei Schnitten", "im PDF eingebettet"),
        ("Zahlen nach de-DE", "Sprache am Report wählbar"),
        ("PDF und DOCX", "mit allen Bildern"),
        ("Farbflächen und Linien", "randlos bis zum Blattrand"),
        ("Parameter als Stellschraube", "Preise, Ziele, Schalter"),
    ]),
    ("▲", "Geht mit Kniff", c.AMBER, [
        ("Symbole wie Häkchen", "Schrift Segoe UI Symbol nehmen"),
        ("Wachsende Tabellen", "Platz fest reservieren"),
        ("Grundriss ganzes Geschoss", "Bild an der Decke abfragen"),
        ("Raumbilder", "nur im Planmodus"),
        ("Bauteilbild in Farbe", "über einen Bildparameter"),
        ("Tausende Bauteilbilder", "Bildspalte weglassen oder einengen"),
        ("Maße im Grundriss", "nur innerhalb der Deckenkante"),
        ("Raum-Abwicklung", "2D-Zeichnung plus Rahmen im Teilbild"),
        ("Deckblattdaten", "Projektattribute als Spalten"),
        ("XLSX-Export", "nur Rohdaten, ohne Layout"),
    ]),
    ("✕", "Geht nicht", c.RED, [
        ("Trendlinie im Diagramm", "kennt das Report-Format nicht"),
        ("Karte, Lageplan", "nur Polygon-Text, kein Kartenbild"),
        ("3D-Bild des Gebäudes", "zeigt nur die graue Decke"),
        ("Farbverlauf, Transparenz", "flach bzw. Fehler; hell mischen"),
        ("SVG- und TIFF-Bilder", "rotes Kreuz; PNG oder JPG nehmen"),
        ("Allplan-Ansicht als Bild", "nur Titel und Maß, Inhalt fehlt"),
        ("Sunburst-Diagramm", "unlesbar; TreeMap nehmen"),
        ("Ausgeblendete Elemente", "geben ihren Platz nicht frei"),
        ("Seitenzahl im Textteil", "nur im Fuß, sonst Abbruch"),
        ("Layer, Stiftnummer", "Wert immer leer"),
    ]),
]

GRENZEN = [
    ("Nur die erste Abfrage wird gefüllt.",
     "Jede weitere hat 0 Zeilen: Ein Report braucht eine breite Abfrage, die Themen trennt der Filter im Report."),
    ("Je Report nur eine Bildart aus dem Modell.",
     "Die erste Bildspalte bestimmt alle Bilder; Ausnahme ist eine Untertabelle mit eigenem Bildfeld."),
    ("Bedienung wirkt nur im Allplan-Fenster.",
     "Klicksprung, Aufklappen und Parameter fehlen im PDF, DOCX und XLSX; beim Export lässt sich kein Parameter setzen."),
    ("Eine leere Abfrage ergibt keinen Report.",
     "Liefert die erste Abfrage keine Zeile, öffnet Allplan ein Meldungsfenster und schreibt keine Datei."),
    ("Jedes Bauteilbild kostet Rechenzeit.",
     "Auch wenn es nirgends gezeigt wird: 3.545 Zeilen brauchten 3 bis 7 Minuten, Allplan „reagiert nicht“."),
]

KOPF_H = 0.95        # Spaltenkopf
ZEILE_H = 1.05       # eine Zeile Stichwort + Halbsatz
BAND_ZEILE_H = 1.2   # eine der fünf harten Grenzen


@b.baustein("X080", "Übersicht Geht / Kniff / Geht nicht")
def x080(top, left, w):
    """Drei Spalten mit farbigem Kopfzeichen; je Zeile ein Stichwort und darunter ein Halbsatz."""
    luecke = 0.4
    sw = (w - 2 * luecke) / 3
    xml = ""
    for nr, (zeichen, titel, farbe, zeilen) in enumerate(SPALTEN):
        p = "S9_C%d" % nr
        x = left + nr * (sw + luecke)
        xml += c.text(p + "_z", top, x, 0.8, KOPF_H - 0.1, c.run(zeichen, 17, farbe, SYM), valign="Middle")
        xml += c.text(p + "_t", top, x + 0.85, sw - 0.85, KOPF_H - 0.1, c.run(titel, 13, c.INK, c.F_SEMI), valign="Middle")
        xml += c.line(p + "_l", top + KOPF_H - 0.05, x, sw, color=farbe, width="1.5pt")
        for i, (stichwort, halbsatz) in enumerate(zeilen):
            q = "%s_%d" % (p, i)
            y = top + KOPF_H + i * ZEILE_H
            xml += c.text(q + "_k", y + 0.15, x, sw, 0.42, c.run(stichwort, 9, c.INK, c.F_SEMI), valign="Middle")
            xml += c.text(q + "_h", y + 0.58, x, sw, 0.38, c.run(halbsatz, 8, c.MUTED), valign="Top")
            xml += c.line(q + "_r", y + ZEILE_H, x, sw)
    ende = top + KOPF_H + len(SPALTEN[0][3]) * ZEILE_H
    xml += etikett("S9_X08", ende + 0.1, left, w, "X080",
                   "Drei Spalten aus Textboxen; Kopfzeichen in Segoe UI Symbol, je Zeile Stichwort und Halbsatz")
    return xml


@b.baustein("X090", "Die harten Grenzen")
def x090(top, left, w):
    """Fünf nummerierte Zeilen auf heller Fläche: große Ziffer, ein Satz fett, darunter die Folge."""
    xml = overline("S9_G", top, left, w, "Die fünf harten Grenzen", "Was Allplan-Reports nicht leisten")
    y0 = top + 1.45
    inner = ""
    for i, (satz, folge) in enumerate(GRENZEN):
        y = i * BAND_ZEILE_H
        inner += c.text("S9_G%d_n" % i, y, 0.3, 1.0, BAND_ZEILE_H, c.run(str(i + 1), 24, c.BLUE, c.F_LIGHT), valign="Middle")
        inner += c.text("S9_G%d_t" % i, y, 1.5, w - 1.8, BAND_ZEILE_H,
                        [c.para([c.run(satz, 10, c.INK, c.F_SEMI)]), c.para([c.run(folge, 8.5, c.TEXT)])], valign="Middle")
        if i:
            inner += c.line("S9_G%d_r" % i, y, 0.3, w - 0.6, color=c.WHITE, width="1.5pt")
    xml += c.rect("S9_GBand", y0, left, w, len(GRENZEN) * BAND_ZEILE_H, inner, bg=c.SURFACE)
    xml += etikett("S9_X09", y0 + len(GRENZEN) * BAND_ZEILE_H + 0.1, left, w, "X090",
                   "Fünf Zeilen auf heller Fläche, große Ziffer in Segoe UI Light, Satz und Folge in einer Textbox")
    return xml


def seite():
    x0, w = c.INSET, c.CONTENT_W
    items = seitenkopf(9, TITEL, "gemessen in Allplan 2027")

    befund = c.para([
        c.run("Allplans Report-Maschine kann weit mehr, als die mitgelieferten Vorlagen zeigen: ", 14, c.TEXT, c.F_LIGHT),
        c.run("keine der 551", 14, c.INK, c.F_SEMI),
        c.run(" enthält ein Diagramm oder eine Messanzeige. Die Grenzen liegen vor allem bei den ", 14, c.TEXT, c.F_LIGHT),
        c.run("Daten und Bildern", 14, c.INK, c.F_SEMI),
        c.run(", die Allplan je Report liefert.", 14, c.TEXT, c.F_LIGHT)])
    items += c.rect("S9_BefundBalken", 3.3, x0, 0.1, 2.3, bg=c.BLUE)
    items += c.text("S9_Befund", 3.3, x0 + 0.4, w - 0.4, 2.3, befund, valign="Middle")

    items += x080(6.3, x0, w)
    items += x090(18.85, x0, w)

    items += c.line("S9_FussLinie", 27.2, x0, w)
    items += c.text("S9_Beleg", 27.3, x0, w, 0.7,
                    c.run("Belegt in Allplan 2027 am PDF-Export; einzelne Urteile nur kopflos gerendert oder aus Allplans Vorlagen "
                          "übernommen. Bedienung im Report-Fenster nicht selbst ausgelöst.", 7, c.FAINT))
    return items
