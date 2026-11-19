# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Listen" (RDL 2016) nach out/Report_Master_Listen.rdlc.

Ein FLIESSENDER Report: die Listen laufen ueber so viele Seiten, wie die Daten brauchen. Er zeigt die heute in Allplan
gemessenen Techniken als fertige, bestellbare Bausteine (Messbefunde: labor/luecken/A, B, C; Bausatz: master/core.py).

    python build_listen.py                     schreibt out/Report_Master_Listen.rdlc
    python build_listen.py --render            rendert zusaetzlich kopflos nach listen/aus/png (Datensatz master)
    python build_listen.py --render --pdf      dazu das PDF (Lesezeichen, Seitenzaehlung pruefen)
    python build_listen.py --render --daten=master_en | gross      anderer Datensatz (master/daten/<name>.json, aus/png_<name>)
    python build_listen.py --render --eng      die englische Fassung (out/eng/, vorher: python master/sprache.py --en) mit master_en.json -> aus/png_eng
    python build_listen.py --render --param=Auswertung_Gruppe=Material --param=Auswertung_Zeilen=3 --param=Material=Mauerwerk|Holz
                                               Stellschrauben beim kopflosen Rendern setzen (nur Werkstatt; in Allplan gilt die Vorgabe)
    python build_listen.py --render --param=Etiketten_Art=1 --param=Etiketten_Anzahl=16
                                               Etiketten nur fuer Waende (Objektnummer; 0 = alle Arten), 16 Stueck auf 2 Seiten
    python build_listen.py --render --daten=master --nur-bauteile=7     kleiner Pruefdatensatz (nur die ersten 7 Bauteile, keine
                                               Raeume): zeigt, dass die letzte Reihe kein leeres Etikett malt

Bausteine (angemeldet mit @b.baustein): K100 Kernaussage, K110 Kennzahl-Kacheln, U060 Auswertung nach Wahl, U070 Auswahl aus den
Daten, T150 Bauteilliste je Art, B110 Etiketten mit QR-Code (zum Ausschneiden), B120 Strichcode 128 (auf jedem Etikett).
Elementnamen beginnen mit "LT_".

Daten: die Abfrage des Masters (bausteine.QUERY, FIELDS, CODE) OHNE die @205@-Bildspalte; sie wird im Code aus der Master-Abfrage
herausgenommen, nicht abgeschrieben - aendert sich die Master-Abfrage, folgt der Listen-Report. Warum: jede Zeile mit Bildspalte kostet
Rechenzeit, auch wenn das Bild nirgends gezeigt wird (3.545 Zeilen rund 3 Minuten); die Listen zeigen keine Bilder. Menge = Volumen (m3) der Rohbauteile,
Flaeche (m2) bei Fenstern und Tueren.

Seitenfolge: Deckseite (feste Hoehe, 1 Seite) - Bauteilliste je Art (ein Abschnitt je Objektart, Umbruch dazwischen, eigene
Seitenzaehlung) - Etiketten (eigener Abschnitt, eigene Zaehlung, 8 je Seite, Anzahl per Stellschraube). Kopf (ab Seite 2) und Fuss
tragen den Gruppennamen.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MASTER)

import bausteine as b  # noqa: E402
import core as c  # noqa: E402
import viz as v  # noqa: E402

OUT_DIR = os.path.normpath(os.path.join(MASTER, "..", "out"))
ENG = "--eng" in sys.argv
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "master_en" if ENG else "master")
JSON = os.environ.get("LISTEN_JSON", os.path.join(MASTER, "daten", DATEN + ".json"))
AUS = os.environ.get("LISTEN_AUS", os.path.join(HERE, "aus", "png_eng" if ENG else ("png" if DATEN == "master" else "png_" + DATEN)))
CODES_VB = os.path.join(HERE, "codes.vb")

MAX_AUSWAHL = 3        # Zeilen der Tabelle "Auswahl aus den Daten" (Rest: "... und n weitere")
MAX_ZEILEN = 20        # groesste waehlbare Zeilenzahl der "Auswertung nach Wahl" (reserviert die Hoehe auf der Deckseite)
SEITE_NUTZ_H = 27.1    # Seitenhoehe 29,7 minus Kopf 1,3 minus Fuss 1,2 (der Platz ist auf jeder Seite reserviert, auch auf der Deckseite)

DS = "AllplanReport"
X0, W = c.INSET, c.CONTENT_W

# ---------------------------------------------------------------- Abfrage: die des Masters ohne Bildspalte
def abfrage_ohne_bild():
    """(QUERY, FIELDS) des Masters ohne die @205@-Zeile und das Bildfeld. Die Zeile davor verliert ihr Komma."""
    zeilen = b.QUERY.splitlines()
    nr = [i for i, z in enumerate(zeilen) if "@205@" in z]
    if len(nr) != 1 or not zeilen[nr[0] - 1].rstrip().endswith(","):
        sys.exit("FEHLER: die Master-Abfrage hat sich geaendert - abfrage_ohne_bild() erwartet genau eine @205@-Zeile nach einer Spalte mit Komma")
    zeilen[nr[0] - 1] = zeilen[nr[0] - 1].rstrip()[:-1]
    del zeilen[nr[0]]
    return chr(10).join(zeilen) + chr(10), [f for f in b.FIELDS if f[1] != "Byte[]"]


QUERY, FIELDS = abfrage_ohne_bild()

# ---------------------------------------------------------------- Parameter (Stellschrauben, Benutzerinteraktion)
GRUPPEN_WERTE = [("Objektart", "Objektart"), ("Material", "Material"), ("Teilbild", "Teilbild")]
SORT_WERTE = [("Menge", "Menge (größte zuerst)"), ("Name", "Name (A bis Z)")]
ZEILEN_WERTE = [("3", "3 Gruppen"), ("5", "5 Gruppen"), ("10", "10 Gruppen"), ("20", "20 Gruppen")]
# Etiketten: Wert = Objektnummer der Bauteilart ("0" = alle Arten); Anzahl in ganzen Seiten zu 8 Etiketten
ETIKETT_ARTEN = [("0", "Alle Bauteile"), ("1", "Wand"), ("3", "Stütze"), ("4", "Decke"), ("6", "Unterzug"),
                 ("704", "Bodenplatte"), ("991", "Fenster"), ("992", "Tür")]
ETIKETT_ZAHL = [("8", "8 Etiketten (1 Seite)"), ("16", "16 Etiketten (2 Seiten)"), ("32", "32 Etiketten (4 Seiten)"),
                ("96", "96 Etiketten (12 Seiten)")]
PARAMS = (c.parameter("Auswertung_Gruppe", "String", "Objektart", "Auswertung nach Wahl: Gruppieren nach", werte=GRUPPEN_WERTE)
          + c.parameter("Auswertung_Sortierung", "String", "Menge", "Auswertung nach Wahl: Sortieren nach", werte=SORT_WERTE)
          + c.parameter("Auswertung_Zeilen", "String", "10", "Auswertung nach Wahl: Wie viele Gruppen zeigen (die größten)",
                        werte=ZEILEN_WERTE)
          + c.parameter("Etiketten_Art", "String", "0", "Etiketten: Für welche Bauteile", werte=ETIKETT_ARTEN)
          + c.parameter("Etiketten_Anzahl", "String", "8", "Etiketten: Wie viele (die größten nach Menge)", werte=ETIKETT_ZAHL)
          # Name wie in Allplans Vorlagen (Ausbau Bodenflaechen: Parameter "Material"); die Liste kommt aus den Daten (Distinct),
          # ohne Auswahl liefert Allplan alle Werte
          + c.parameter("Material", "String", None, "wird ersetzt", multi=True, allowblank=True, distinct="Material"))

# ---------------------------------------------------------------- Ausdruecke
BAUTEIL = b.ist(1, 3, 4, 6, 704, 991, 992)     # Wand, Stuetze, Decke, Unterzug, Bodenplatte, Fenster, Tuer (kein Raum)
ROHBAU = b.ROHBAU
OEFF = b.ist(991, 992)                         # Fenster und Tueren: Menge in m2, alles andere in m3
FL = "CDbl(Fields!Flaeche.Value)"
VOL = "CDbl(Fields!Volumen.Value)"
MENGE = "IIf(%s, %s, %s)" % (OEFF, FL, VOL)
EINHEIT = 'IIf(%s, "m²", "m³")' % OEFF
NACHRANG = "Val(Right(Fields!Nr.Value, 8)) / 1000000000000"      # eindeutiger Rang je Zeile (TopN zaehlt Gleiche sonst alle mit)
NACHRANG_G = "Val(Right(Min(Fields!Nr.Value), 8)) / 1000000000000"
NAME = "IIf(Len(Fields!Bezeichnung.Value) > 0, Fields!Bezeichnung.Value, Fields!Objekt.Value)"
MAT = 'IIf(Len(Fields!Material.Value) = 0, "(ohne Angabe)", Fields!Material.Value)'
ART = "Code.Art(Fields!ObjNr.Value)"
KARTEN_NAME = "Etiketten"                      # Seitenname des Etiketten-Abschnitts (steht im Fuss und im Seitenkopf)

# Zahlen, einmal als Report-Variable gerechnet und in Kopf, Fuss und Body benutzt
VARIABLEN = [("V_Anz", b.anzahl(BAUTEIL, DS)),
             ("V_Vol", b.summe("Volumen", ROHBAU, DS)),
             ("V_Arten", 'CountDistinct(IIf(%s, Fields!ObjNr.Value, Nothing), "%s")' % (BAUTEIL, DS))]
V_ANZ, V_VOL, V_ARTEN = "Variables!V_Anz.Value", "Variables!V_Vol.Value", "Variables!V_Arten.Value"

ROW = c.edge(["Bottom"], c.HAIR, "0.5pt")
HEAD = c.edge(["Bottom"], c.INK, "1pt")
SUMLINE = c.edge(["Top"], c.INK, "1pt")
RAHMEN = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR


def fm(x):
    """Menge mit Tausenderpunkt und zwei Nachkommastellen (jede Spalte gleich, damit die Kommas untereinander stehen)."""
    return 'Format(%s, "#,##0.00")' % x


def prozent(q):
    """Anteil 0..1 als Prozent mit einer Stelle; ein Anteil unter 0,05 % steht als '< 0,1 %' (nicht als 0,0 %)."""
    return 'IIf(%s > 0 And %s < 0.0005, "< " & Format(0.001, "0.0 %%"), Format(%s, "0.0 %%"))' % (q, q, q)


def kurz(x, n):
    """Text auf n Zeichen kuerzen, Auslassung als Punkte (Zellen wachsen nicht, abgeschnitten wirkt kaputt)."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (x, n, x, n - 1, x)


def gross_zahl(txt_expr):
    """Grosse Zahl; die Schriftgroesse schrumpft mit der Ziffernzahl, damit nichts umbricht."""
    groesse = 'IIf(Len(%s) >= 8, "12pt", IIf(Len(%s) >= 6, "15pt", "17pt"))' % (txt_expr, txt_expr)
    return ("<TextRun><Value>=%s</Value><Style><FontFamily>%s</FontFamily><FontSize>=%s</FontSize><Color>%s</Color></Style></TextRun>"
            % (c.esc(txt_expr), c.F_LIGHT, c.esc(groesse), c.INK))


# ---------------------------------------------------------------- VB-Code: Bausatz-Code, Strichcode/QR, Hilfe fuer die Auswahl
CODE_AUSWAHL = '''
' Die Auswahl einer Mehrfach-Stellschraube als Text: nur gesetzte Werte, hoechstens grenze Zeichen.
Public Function WahlListe(ByVal v As Object, ByVal grenze As Integer) As String
    Dim s As String = ""
    If v Is Nothing Then Return ""
    If TypeOf v Is Object() Then
        Dim a() As Object = CType(v, Object())
        Dim i As Integer
        For i = 0 To a.Length - 1
            If Not a(i) Is Nothing Then
                If a(i).ToString().Length > 0 Then
                    If s.Length > 0 Then s = s & ", "
                    s = s & a(i).ToString()
                End If
            End If
        Next
    Else
        s = v.ToString()
    End If
    If s.Length > grenze Then s = s.Substring(0, grenze - 1) & "…"
    Return s
End Function
'''


CODE_INWAHL = '''
' Ist wert einer der in einer Mehrfach-Stellschraube gewaehlten Werte?
Public Function InWahl(ByVal v As Object, ByVal wert As Object) As Boolean
    If v Is Nothing Then Return False
    Dim s As String = ""
    If Not wert Is Nothing Then s = wert.ToString()
    If TypeOf v Is Object() Then
        Dim a() As Object = CType(v, Object())
        Dim i As Integer
        For i = 0 To a.Length - 1
            If Not a(i) Is Nothing Then
                If a(i).ToString() = s Then Return True
            End If
        Next
        Return False
    End If
    Return v.ToString() = s
End Function
'''


CODE_ETIKETT = '''
' Nicht leere Teile mit Komma verbinden (die Masse eines Etiketts).
Public Function Verbinde(ByVal a As String, ByVal b As String, ByVal c As String) As String
    Dim s As String = ""
    Dim t As String
    For Each t In New String() {a, b, c}
        If Not t Is Nothing Then
            If t.Trim().Length > 0 Then
                If s.Length > 0 Then s = s & ", "
                s = s & t.Trim()
            End If
        End If
    Next
    Return s
End Function

' Text fuer den QR-Code eines Etiketts, hoechstens grenze Byte in UTF-8 (QrPng liefert sonst ein leeres Bild ohne Fehler).
' Zeilen: kopf (wird gekuerzt, bis es passt), zusatz (faellt weg, wenn er nicht ganz passt), masse, id.
' Reicht der Platz nicht einmal fuer masse und id, bleibt die id allein.
Public Function EtikettText(ByVal kopf As String, ByVal zusatz As String, ByVal masse As String, ByVal id As String, ByVal grenze As Integer) As String
    Dim nl As String = ChrW(10)
    Dim u As System.Text.Encoding = System.Text.Encoding.UTF8
    Dim fest As String = masse & nl & id
    If u.GetByteCount(fest) > grenze Then Return id
    Dim k As String = "" & kopf
    Do While k.Length > 0 AndAlso u.GetByteCount(k & nl & fest) > grenze
        k = k.Substring(0, k.Length - 1)
    Loop
    k = k.TrimEnd()
    If k.Length = 0 Then Return fest
    If Len(zusatz) > 0 AndAlso u.GetByteCount(k & nl & zusatz & nl & fest) <= grenze Then Return k & nl & zusatz & nl & fest
    Return k & nl & fest
End Function
'''


def code():
    with open(CODES_VB, encoding="utf-8") as handle:
        vb = handle.read()
    return b.CODE + CODE_AUSWAHL + CODE_INWAHL + CODE_ETIKETT + "\n" + vb[vb.index("Private Const T39 As"):]


CODEMODULES = ["System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a"]


# ---------------------------------------------------------------- Tabellen-Bausteine (Hilfen kommen aus core.py: tablix_gruppen, gruppe_mitglied, filter_*)
def kopfzelle(name, label, align=None, unter=None):
    """Tabellenkopf: Name in Grossbuchstaben, optional eine zweite Zeile (Einheit) heller darunter."""
    inhalt = [c.para([c.run(label.upper(), 7, c.MUTED, c.F_SEMI)], align)]
    if unter:
        inhalt.append(c.para([c.run(unter, 7, c.FAINT)], align))
    return c.cell(name, inhalt, align, "Bottom", border_xml=HEAD, pad=(4, 2, 4, 4))


def balken_zelle(name, farbe, y, maximum, hoehe_anteil="0.42"):
    """Zellenbalken: Massstab ist der groesste Wert der Gruppe (Ausdruck maximum)."""
    return b.in_cell(v.chart(
        name, 0, 0, 1, 1,
        [v.S("V", {"Y": "=" + y}, typ="Bar", sub="Plain", pstyle="<Color>%s</Color>" % c.esc(farbe),
             custom_xml=v.custom(PointWidth=hoehe_anteil))],
        [], nomember=True, dataset=False,
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)],
                     val_axes=[v.axis("Primary", visible=False, minimum="0", maximum="=" + maximum)],
                     pos=(0, 0, 100, 100), inner=(4, 4, 90, 92))))


def etikett_zeile(name, kennung, technik, span):
    """Etikett als letzte Tabellenzeile: es haengt so immer direkt unter der Tabelle, egal wie lang sie wird."""
    b.KATALOG.append((b.SEITE_AKTUELL[0], kennung, technik))
    inner = c.para([c.run(kennung + "  ", 6.5, c.BLUE, c.F_SEMI), c.run(technik, 6.5, c.FAINT)]) if b.ETIKETT_AN[0] else c.para([c.run("", 6.5)])
    return c.zeile(0.45, [c.zelle(c.cell(name, inner, valign="Top", pad=(4, 4, 0, 0)), span)])


def zahlenzelle(name, ausdruck, einheit=None, groesse=9, farbe=c.TEXT, font=c.F, border=ROW):
    """Zahl rechtsbuendig, Einheit kleiner und heller dahinter."""
    runs = [c.run("=" + ausdruck, groesse, farbe, font)]
    if einheit:
        runs.append(c.run("=" + einheit if einheit.startswith(("IIf", "Code")) else einheit, 7, c.FAINT))
    return c.cell(name, c.para(runs), "Right", border_xml=border, pad=(4, 1, 4, 1))


# ---------------------------------------------------------------- Kopf, Fuss, Deckseitenband
def kopf_xml():
    """Schmaler Seitenkopf ab Seite 2: Reportname links, Gruppenname (Seitenname) rechts, darunter die Gesamtzahlen aus den Variablen.
    Die Marineflaeche ist die Fuellung des Rechtecks, die Texte sind seine Kinder: nichts im Kopf ueberlappt (im Report-Fenster
    verschiebt Allplan sonst Elemente). Auf der Deckseite steht kein Kopf (header_first=False):
    ein Kopf in Marine ueber dem Titelband liesse an der Naht einen hellen Haarstrich (Kantenglaettung zweier aneinander stossender Flaechen
    bei Bruchteilen eines Pixels; die Geometrie im PDF ist luckenlos, ein Ueberdecken geht nicht: Top darf nicht negativ sein, Linien am
    Rand werden abgeschnitten, ausgeblendete Kinder verkuerzen das Rechteck). Darum bleiben die 1,3 cm oben weiss."""
    inner = (c.rect("LT_KopfAkzent", 0.14, X0, 0.7, 0.06, bg=c.ORANGE)
             + c.text("LT_KopfOver", 0.26, X0, 8.0, 0.38, c.run("REPORT MASTER  ·  LISTEN", 7, c.SKY, c.F_SEMI))
             + c.text("LT_KopfTitel", 0.7, X0, 8.0, 0.5, c.run("Bauteile im Teilbild", 11, c.WHITE, c.F_LIGHT), valign="Middle")
             + c.text("LT_KopfGruppe", 0.18, X0 + 8.1, W - 8.1, 0.56, c.run("=Globals!PageName", 12, c.WHITE, c.F_SEMI), align="Right", valign="Middle")
             + c.text("LT_KopfSumme", 0.79, X0 + 8.1, W - 8.1, 0.4,
                      c.run('=Format(%s, "N0") & " Bauteile  ·  " & Format(%s, "N1") & " m³ Rohbau gesamt"' % (V_ANZ, V_VOL), 7.5, "#CBD5E1"),
                      align="Right", valign="Middle"))
    return c.rect("LT_Kopf", 0, 0, c.PAGE_W, 1.3, inner, bg=c.NAVY)


def fuss_xml():
    """Fuss: Linie, links Report und Projekt (gekuerzt: ein langer Name braeche um und wuerde abgeschnitten), Mitte Gruppenname und Rohbau gesamt, rechts Seite je Gruppe und gesamt (OverallPageNumber).
    Keine Ueberlappung: die Felder liegen nebeneinander (x) bzw. mit 0,05 cm Luft untereinander (y)."""
    return (c.line("LT_FussLinie", 0.15, X0, W)
            + c.text("LT_FussLinks", 0.3, X0, 6.9, 0.45,
                     c.run('="Listen   ·   " & ' + kurz("Parameters!Project_Name.Value", 34), 7.5, c.MUTED))
            + c.text("LT_FussMitte", 0.27, X0 + 7.0, 4.9, 0.4, c.run("=Globals!PageName", 8, c.INK, c.F_SEMI), align="Center")
            + c.text("LT_FussSumme", 0.72, X0 + 7.0, 4.9, 0.4,
                     c.run('="Rohbau gesamt " & Format(%s, "N1") & " m³"' % V_VOL, 7, c.FAINT), align="Center")
            + c.text("LT_FussRechts", 0.3, X0 + W - 6.0, 6.0, 0.45,
                     c.run('="Seite " & Globals!PageNumber & " / " & Globals!TotalPages & "   ·   gesamt " & Globals!OverallPageNumber '
                           '& " / " & Globals!OverallTotalPages', 7.5, c.MUTED), align="Right"))


def band():
    inner = (c.rect("LT_BandAkzent", 0.1, X0, 1.3, 0.1, bg=c.ORANGE)
             + c.text("LT_BandOver", 0.35, X0, 12, 0.4, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.SKY, c.F_SEMI))
             + c.text("LT_BandTitel", 0.8, X0, 12.9, 1.4, c.run("Listen", 30, c.WHITE, c.F_LIGHT))
             + c.text("LT_BandSub", 2.3, X0, 12.9, 0.5,
                      c.run('=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")', 9, "#CBD5E1", c.F))
             + c.text("LT_BandRechts", 0.35, X0 + 13, 5, 0.4, c.run("Vollständige Listen", 8, c.SKY, c.F_SEMI), align="Right")
             + c.text("LT_BandRechts2", 0.8, X0 + 13, 5, 1.4,
                      c.para([c.run('=Format(%s, "N0")' % V_ANZ, 30, c.WHITE, c.F_LIGHT)], "Right"))
             + c.text("LT_BandRechts3", 2.3, X0 + 13, 5, 0.5, c.run("Bauteile im Teilbild", 9, "#CBD5E1", c.F), align="Right"))
    return c.rect("LT_Band", 0, 0, c.PAGE_W, 3.3, inner, bg=c.NAVY)


# ---------------------------------------------------------------- Abschnittskopf ohne Ueberlappung
def abschnitt(name, top, left, w, label, title, hinweis=None):
    """Abschnittskopf: kleine Zeile in Leitfarbe, Ueberschrift, Haarlinie, rechts optional ein Hinweis. Wie bausteine.overline(), aber ohne
    ueberlappende Felder (overline legt Zeile und Ueberschrift um 0,02 cm uebereinander; im Report-Fenster schiebt Allplan dann eines weg):
    die Ueberschrift ist nur 7,5 cm breit, der Hinweis steht rechts daneben. Belegt 1,2 cm."""
    items = (c.text(name + "_o", top, left, w, 0.38, c.run(label.upper(), 7, c.BLUE, c.F_SEMI))
             + c.text(name + "_t", top + 0.43, left, 7.5, 0.7, c.run(title, 13, c.INK, c.F_SEMI))
             + c.line(name + "_l", top + 1.18, left, w))
    if hinweis:
        items += c.text(name + "_h", top + 0.5, left + 7.6, w - 7.6, 0.5, c.run(hinweis, 7.5, c.MUTED), "Right", "Bottom")
    return items


# ---------------------------------------------------------------- K100 Kernaussage
@b.baustein("K100", "Kernaussage Listen")
def k100(top, left, w):
    """Ein Satz, der sagt, was der Report zeigt; die Zahlen kommen aus den Report-Variablen."""
    def zahl(ausdruck, fmt=None):
        return c.run("=" + ausdruck, 12.5, c.INK, c.F_SEMI, fmt=fmt)
    leicht = lambda t: c.run(t, 12.5, c.TEXT, c.F_LIGHT)  # noqa: E731
    inhalt = c.para([leicht("Das Teilbild enthält "), zahl(V_ANZ, "N0"), leicht(" Bauteile in "), zahl(V_ARTEN, "N0"),
                     leicht(" Arten, zusammen "), zahl(V_VOL, "N1"), leicht(" m³ Rohbau. Die Liste je Art ist vollständig, "
                                                                           "die Etiketten am Ende tragen QR-Code und Strichcode.")])
    items = c.text("LT_K100", top, left, w, 1.1, inhalt, valign="Top")
    items += b.etikett("LT_K100_e", top + 1.15, left, w, "K100", "ein Satz aus Report-Variablen (einmal gerechnet, überall benutzt)")
    return items


# ---------------------------------------------------------------- K110 Kennzahl-Kacheln
def kachel(name, top, left, w, wert, einheit, label, note):
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.3, 0.3, w - 0.35, 0.95,
                      c.para([gross_zahl(wert), c.run("=" + einheit if einheit else "", 9, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.32, 0.3, w - 0.35, 0.4, c.run(label, 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.8, 0.3, w - 0.35, 0.4, c.run(note, 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.2, inner, bg=c.SURFACE)


@b.baustein("K110", "Kennzahl-Kacheln Listen")
def k110(top, left, w):
    """Fuenf Kacheln: Bauteile, Arten, Rohbauvolumen, Raeume, Materialien (Namen laut Modell)."""
    gap = 0.25
    kw = (w - 4 * gap) / 5
    raeume = b.anzahl(b.RAUM, DS)
    raum_fl = b.summe("Flaeche", b.RAUM, DS)
    materialien = 'CountDistinct(IIf(%s And Len(Fields!Material.Value) > 0, Fields!Material.Value, Nothing), "%s")' % (ROHBAU, DS)
    kacheln = [
        ("LT_K1", 'Format(%s, "N0")' % V_ANZ, None, "BAUTEILE", "Rohbau, Fenster, Türen"),
        ("LT_K2", 'Format(%s, "N0")' % V_ARTEN, None, "ARTEN", "Wand, Decke, Stütze …"),
        ("LT_K3", 'Format(%s, IIf(%s >= 1000, "N0", "N1"))' % (V_VOL, V_VOL), '" m³"', "ROHBAUVOLUMEN", "alle Rohbauteile"),
        ("LT_K4", 'Format(%s, "N0")' % raeume, None, "RÄUME", '=Format(%s, "N0") & " m² Grundfläche"' % raum_fl),
        ("LT_K5", 'Format(%s, "N0")' % materialien, None, "MATERIALIEN", "Namen laut Modell"),
    ]
    items = ""
    for i, (name, wert, einheit, label, note) in enumerate(kacheln):
        items += kachel(name, top, left + i * (kw + gap), kw, wert, einheit, label, note)
    items += b.etikett("LT_K_e", top + 2.28, left, w, "K110",
                       "fünf Kacheln aus Report-Variablen und Summen über die Objektnummer")
    return items


# ---------------------------------------------------------------- Tabellen der Deckseite
def tabellen_block(name, top, left, w, spalten, zeilen_h, kopf, daten, summe, rest_zeile, gruppe, gruppen_sort, deckel_xml, filter_xml,
                   rest_zahl, rest_hidden, leer_text, kennung, technik):
    """Gruppierte Tabelle (Kopf, Datenzeile je Gruppe, Rest-Hinweis, Summe, Etikett). Liefert das XML des Tablix; die Hoehe ist die deklarierte."""
    n = len(spalten)
    z_kopf = c.zeile(zeilen_h[0], [c.zelle(z) for z in kopf])
    z_daten = c.zeile(zeilen_h[1], [c.zelle(z) for z in daten])
    z_rest = c.zeile(zeilen_h[2], [c.zelle(rest_zeile, n)])
    z_summe = c.zeile(zeilen_h[3], [c.zelle(z) for z in summe])
    z_eti = etikett_zeile(name + "_E", kennung, technik, n)
    mitglieder = [c.kopf_mitglied(), c.gruppe_mitglied(name + "_G", gruppe, gruppen_sort, deckel_xml),
                  c.fuss_mitglied(rest_hidden), c.fuss_mitglied(), c.fuss_mitglied()]
    hoehe = sum(zeilen_h) + 0.45                 # jede Zeile einmal, dazu die Etikettzeile
    return c.tablix_gruppen(name, 0, 0, spalten, [z_kopf, z_daten, z_rest, z_summe, z_eti], mitglieder, hoehe, filter_xml=filter_xml,
                            keine_zeilen=leer_text), hoehe


# Gruppierung der "Auswertung nach Wahl": die Zeichenketten sind Schluessel der festen Liste (Parameter Auswertung_Gruppe)
GRUPPE_AUSWERTUNG = ('Switch(Parameters!Auswertung_Gruppe.Value = "Objektart", Code.Art(Fields!ObjNr.Value), '
                     'Parameters!Auswertung_Gruppe.Value = "Material", %s, True, "Teilbild " & Left(Fields!Nr.Value, 4))' % MAT)
N_ZEILEN = "CInt(Parameters!Auswertung_Zeilen.Value)"
ROHBAU_VOL_DS = b.summe("Volumen", ROHBAU, DS)


@b.baustein("U060", "Auswertung nach Wahl")
def u060(top, left, w):
    """Tabelle, deren Gruppierung, Sortierung und Zeilenzahl drei Stellschrauben bestimmen (feste Listen mit Beschriftung, feste Vorgaben).
    Rohbauteile; die n groessten Gruppen nach Volumen, dann nach Wahl sortiert; der Rest steht als Zeile 'und n weitere', die Summe zaehlt alle."""
    items = abschnitt("LT_U6", top, left, w, "Stellschrauben", "Auswertung nach Wahl",
                      '="Rohbau nach " & Parameters!Auswertung_Gruppe.Label & "  ·  " & Parameters!Auswertung_Sortierung.Label '
                      '& "  ·  die " & Parameters!Auswertung_Zeilen.Value & " größten"')
    name = "LT_Aus"
    spalten = [6.2, 1.8, 2.3, 2.3, 1.7, 3.7]
    vol = "Sum(%s)" % VOL
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (VOL, name, name)
    rang = vol + " + " + NACHRANG_G
    sortwert = 'Switch(Parameters!Auswertung_Sortierung.Value = "Menge", %s, True, 0.0)' % vol
    rest_zahl = 'CountDistinct(IIf(%s, %s, Nothing), "%s")' % (ROHBAU, GRUPPE_AUSWERTUNG, DS)
    zh = (0.55, 0.46, 0.45, 0.6)
    kopf = [kopfzelle(name + "_H1", "Gruppe"), kopfzelle(name + "_H2", "Bauteile", "Right"), kopfzelle(name + "_H3", "Fläche", "Right", "m²"),
            kopfzelle(name + "_H4", "Volumen", "Right", "m³"), kopfzelle(name + "_H5", "Anteil", "Right"), kopfzelle(name + "_H6", "")]
    pad = (4, 1, 4, 1)
    daten = [c.cell(name + "_D1", c.run("=" + kurz("First(%s)" % GRUPPE_AUSWERTUNG, 34), 9, c.INK, c.F_SEMI), border_xml=ROW, pad=pad),
             zahlenzelle(name + "_D2", "CountRows()", groesse=9),
             zahlenzelle(name + "_D3", fm("Sum(%s)" % FL), groesse=9),
             zahlenzelle(name + "_D4", fm(vol), groesse=9, farbe=c.INK, font=c.F_SEMI),
             zahlenzelle(name + "_D5", prozent(b.quote(vol, V_VOL)), groesse=9),
             c.rect(name + "_D6", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, vol, maxi), border_xml=ROW)]
    sp = (4, 0, 4, 0)
    summe = [c.cell(name + "_S1", c.run("Summe aller Rohbauteile", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S2", c.run('=Format(%s, "N0")' % b.anzahl(ROHBAU, DS), 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S3", c.run("=" + fm(b.summe("Flaeche", ROHBAU, DS)), 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S4", c.run("=" + fm(V_VOL), 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S5", c.run('=IIf(%s > 0, Format(1, "0.0 %%"), "–")' % V_VOL, 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S6", c.run("", 9), border_xml=SUMLINE)]
    rest = c.cell(name + "_Rest", c.run('=IIf(%s - %s = 1, "… und 1 weitere Gruppe", "… und " & (%s - %s) & " weitere Gruppen")'
                                        % (rest_zahl, N_ZEILEN, rest_zahl, N_ZEILEN), 7.5, c.MUTED), pad=(4, 0, 4, 0))
    xml, hoehe = tabellen_block(
        name, top, left, w, spalten, zh, kopf, daten, summe, rest, "=" + GRUPPE_AUSWERTUNG,
        [("=" + sortwert, True), ("=" + GRUPPE_AUSWERTUNG, False)], c.filter_liste(c.filter_topn(rang, N_ZEILEN)), c.filter_liste(c.filter_j(ROHBAU)),
        rest_zahl, "=%s <= %s" % (rest_zahl, N_ZEILEN), "Keine Rohbauteile im Teilbild.", "U060",
        "Parameter-Listen; die N größten Gruppen, dann sortiert; Teilbild = Nr. aus der Bauteil-ID")
    # Die Tabelle steht in einem Feld fester Groesse: sie waechst mit der Zeilenzahl, die Deckseite bleibt eine Seite
    voll = zh[0] + MAX_ZEILEN * zh[1] + zh[2] + zh[3] + 0.45
    return items + c.rect("LT_Aus_Feld", top + 1.45, left, w, voll, xml)


U060_H = 1.45 + 0.55 + MAX_ZEILEN * 0.46 + 0.45 + 0.6 + 0.45


@b.baustein("U070", "Auswahl aus den Daten")
def u070(top, left, w):
    """Mehrfach-Stellschraube Material, deren Liste aus den Daten kommt (Distinct) und die per In-Filter wirkt; ohne Auswahl zeigt Allplan alle.
    Ein Satz nennt, was gewaehlt ist; die Tabelle zeigt die gewaehlten Materialien des Rohbaus."""
    items = abschnitt("LT_U7", top, left, w, "Stellschraube", "Auswahl aus den Daten")
    n_alle = 'CountDistinct(Fields!Material.Value, "%s")' % DS          # alle Werte der Liste, auch der leere (Raeume, Fenster ohne Material)
    n_namen = 'CountDistinct(IIf(Len(Fields!Material.Value) > 0, Fields!Material.Value, Nothing), "%s")' % DS
    gewaehlt = ('=IIf(Parameters!Material.Count >= %s, "Alle " & %s & " Materialien im Teilbild (keine Auswahl getroffen)", '
                '"Gewählt: " & Code.WahlListe(Parameters!Material.Value, 95))' % (n_alle, n_namen))
    items += c.text("LT_U7_h", top + 1.4, left, w, 0.5, c.run(gewaehlt, 8.5, c.INK, c.F_SEMI), valign="Middle")
    name = "LT_Wahl"
    spalten = [7.2, 2.0, 2.5, 2.5, 3.8]
    vol = "Sum(%s)" % VOL
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (VOL, name, name)
    rang = vol + " + " + NACHRANG_G
    # Rest nur unter den GEWAEHLTEN Materialien zaehlen (der In-Filter der Tabelle wirkt nicht auf Aggregate im Bereich des Datensatzes)
    rest_zahl = ('CountDistinct(IIf(%s And Code.InWahl(Parameters!Material.Value, Fields!Material.Value), Fields!Material.Value, Nothing), "%s")'
                 % (ROHBAU, DS))
    zh = (0.55, 0.5, 0.45, 0.6)
    kopf = [kopfzelle(name + "_H1", "Material"), kopfzelle(name + "_H2", "Bauteile", "Right"), kopfzelle(name + "_H3", "Volumen", "Right", "m³"),
            kopfzelle(name + "_H4", "Anteil", "Right"), kopfzelle(name + "_H5", "")]
    pad = (4, 1, 4, 1)
    daten = [c.cell(name + "_D1", c.run("=" + kurz(MAT.replace("Fields!Material.Value", "First(Fields!Material.Value)"), 40), 9, c.INK, c.F_SEMI),
                    border_xml=ROW, pad=pad),
             zahlenzelle(name + "_D2", "CountRows()"),
             zahlenzelle(name + "_D3", fm(vol), groesse=9, farbe=c.INK, font=c.F_SEMI),
             zahlenzelle(name + "_D4", prozent(b.quote(vol, V_VOL))),
             c.rect(name + "_D5", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, vol, maxi), border_xml=ROW)]
    sp = (4, 0, 4, 0)
    summe = [c.cell(name + "_S1", c.run("Summe der Auswahl", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S2", c.run('=Format(CountRows(), "N0")', 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S3", c.run("=" + fm(vol.replace("Sum(%s)" % VOL, 'Sum(%s, "%s")' % (VOL, name))), 9, c.INK, c.F_SEMI), "Right",
                    border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S4", c.run('=Format(%s, "0.0 %%")' % b.quote('Sum(%s, "%s")' % (VOL, name), V_VOL), 9, c.INK, c.F_SEMI), "Right",
                    border_xml=SUMLINE, pad=sp),
             c.cell(name + "_S5", c.run("", 9), border_xml=SUMLINE)]
    rest = c.cell(name + "_Rest", c.run('=IIf(%s - %d = 1, "… und 1 weiteres Material", "… und " & (%s - %d) & " weitere Materialien")'
                                        % (rest_zahl, MAX_AUSWAHL, rest_zahl, MAX_AUSWAHL), 7.5, c.MUTED), pad=(4, 0, 4, 0))
    xml, hoehe = tabellen_block(
        name, top, left, w, spalten, zh, kopf, daten, summe, rest, "=Fields!Material.Value", [("=" + vol, True)],
        c.filter_liste(c.filter_topn(rang, MAX_AUSWAHL)), c.filter_liste(c.filter_j(ROHBAU), c.filter_in("Fields!Material.Value", "Material")),
        rest_zahl, "=%s <= %d" % (rest_zahl, MAX_AUSWAHL), "Kein Rohbauteil mit dem gewählten Material.", "U070",
        "Mehrfachliste aus den Daten (Prompt Distinct), Filter In; ohne Auswahl alle Werte")
    voll = zh[0] + MAX_AUSWAHL * zh[1] + zh[2] + zh[3] + 0.45
    return items + c.rect("LT_Wahl_Feld", top + 1.95, left, w, voll, xml)


U070_H = 1.95 + 0.55 + MAX_AUSWAHL * 0.5 + 0.45 + 0.6 + 0.45


def deckseite():
    """Deckseite: feste Hoehe (eine Seite), danach beginnt die Liste. Auswertung nach Wahl steht zuletzt: sie waechst mit der Zeilenzahl."""
    inner = band()
    y = 3.55
    inner += k100(y, X0, W)
    y += 1.65
    inner += k110(y, X0, W)
    y += 2.8
    inner += u070(y, X0, W)
    y += U070_H + 0.35
    inner += u060(y, X0, W)
    ende = y + U060_H
    if ende > SEITE_NUTZ_H:
        sys.exit("FEHLER: die Deckseite ist %.2f cm hoch, nutzbar sind %.2f cm" % (ende, SEITE_NUTZ_H))
    return c.rect("LT_Deckseite", 0, 0, c.PAGE_W, SEITE_NUTZ_H, inner, umbruch="End", seitenzaehlung_neu=True, label='="Deckseite"',
                  bookmark="Anfang", seitenname='="Deckseite"'), ende


# ---------------------------------------------------------------- T150 Bauteilliste je Art
LISTE_SPALTEN = [4.9, 4.0, 2.4, 1.7, 2.1, 2.9]
LISTE_Z = (0.9, 0.85, 0.85, 0.7, 0.7, 0.45)      # Abschnittstitel, Spaltenkopf, Bauteilzeile, Summe der Art, Gesamt, Etikett
LISTE_H = sum(LISTE_Z)


@b.baustein("T150", "Bauteilliste je Art")
def t150(top, left, w):
    """Alle Bauteile (ohne Deckel), je Objektart ein Abschnitt: Seitenumbruch zwischen den Arten, Seitenzaehlung je Art neu, Art als
    Seitenname und PDF-Lesezeichen, Abschnittstitel und Spaltenkopf wiederholen sich auf jeder Folgeseite. Anteil an der Art, kumuliert
    (RunningValue), Datenbalken; Klick auf die Zeile zoomt aufs Bauteil."""
    name = "LT_Liste"
    art_g, pos_g = name + "_Art", name + "_Pos"
    kopf_h = LISTE_Z
    art = "Code.Art(Fields!ObjNr.Value)"
    summe_art = "Sum(%s)" % MENGE
    summe_art_gruppe = 'Sum(%s, "%s")' % (MENGE, art_g)
    maxi = 'Max(Sum(%s, "%s"), "%s")' % (MENGE, pos_g, art_g)
    anteil = b.quote("Sum(%s)" % MENGE, summe_art_gruppe)
    kumuliert = b.quote('RunningValue(%s, Sum, "%s")' % (MENGE, art_g), summe_art_gruppe)
    # Zeile 1: Abschnittstitel (Art, Anzahl, Menge); Zeile 2: Spaltenkopf; beide wiederholen sich mit der Gruppe auf der Folgeseite
    titel = c.para([c.run("ART   ", 7, c.BLUE, c.F_SEMI), c.run("=" + art, 12, c.INK, c.F_SEMI),
                    c.run('="     " & Format(CountRows(), "N0") & IIf(CountRows() = 1, " Bauteil", " Bauteile") & "  ·  " & %s & " " & %s'
                          % (fm(summe_art), EINHEIT.replace("Fields!ObjNr.Value", "First(Fields!ObjNr.Value)")), 8, c.MUTED)])
    z_titel = c.zeile(kopf_h[0], [c.zelle(c.cell(name + "_T", titel, valign="Bottom", border_xml=c.edge(["Bottom"], c.HAIR, "0.75pt"),
                                              pad=(0, 0, 0, 3)), len(LISTE_SPALTEN))])
    einheit_kopf = '=' + EINHEIT.replace("Fields!ObjNr.Value", "First(Fields!ObjNr.Value)")
    kopf = [kopfzelle(name + "_H1", "Bezeichnung", None, "Nr"), kopfzelle(name + "_H2", "Material"),
            kopfzelle(name + "_H3", "Menge", "Right", einheit_kopf), kopfzelle(name + "_H4", "Anteil", "Right", "an der Art"),
            kopfzelle(name + "_H5", "Kumuliert", "Right", "an der Art"), kopfzelle(name + "_H6", "")]
    z_kopf = c.zeile(kopf_h[1], [c.zelle(z) for z in kopf])
    pad = (4, 1, 4, 1)
    name_zelle = c.text(name + "_D1", None, 0, 0, 0, [
        c.para([c.run("=" + kurz(NAME, 30), 9, c.INK, c.F_SEMI)]),
        c.para([c.run("=Fields!Nr.Value", 7, c.FAINT)])], valign="Middle", border_xml=ROW, pad=pad)
    kl = lambda z: b.klick(z)  # noqa: E731
    daten = [kl(name_zelle),
             kl(c.cell(name + "_D2", c.run("=" + kurz(MAT, 26), 8.5, c.MUTED), border_xml=ROW, pad=pad)),
             kl(zahlenzelle(name + "_D3", fm(MENGE), EINHEIT, groesse=9, farbe=c.INK, font=c.F_SEMI)),
             kl(zahlenzelle(name + "_D4", prozent(anteil))),
             kl(zahlenzelle(name + "_D5", prozent(kumuliert), farbe=c.MUTED)),
             c.rect(name + "_D6", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, "Sum(%s)" % MENGE, maxi), border_xml=ROW)]
    z_daten = c.zeile(kopf_h[2], [c.zelle(z) for z in daten])
    sp = (4, 0, 4, 0)
    summe_zellen = [c.cell(name + "_S1", c.run('="Summe " & ' + art, 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=sp),
                    c.cell(name + "_S2", c.run('=Format(CountRows(), "N0") & IIf(CountRows() = 1, " Bauteil", " Bauteile")', 8.5, c.MUTED),
                           border_xml=SUMLINE, pad=sp),
                    c.cell(name + "_S3", c.para([c.run("=" + fm(summe_art), 9, c.INK, c.F_SEMI),
                                                 c.run("=" + EINHEIT.replace("Fields!ObjNr.Value", "First(Fields!ObjNr.Value)"), 7, c.FAINT)]),
                           "Right", border_xml=SUMLINE, pad=sp),
                    c.cell(name + "_S4", c.run('=IIf(%s > 0, Format(1, "0.0 %%"), "–")' % summe_art_gruppe, 9, c.INK, c.F_SEMI), "Right",
                           border_xml=SUMLINE, pad=sp),
                    c.cell(name + "_S5", c.run("", 9), border_xml=SUMLINE, pad=sp), c.cell(name + "_S6", c.run("", 9), border_xml=SUMLINE, pad=sp)]
    z_summe = c.zeile(kopf_h[3], [c.zelle(z) for z in summe_zellen])
    gesamt = c.para([c.run("Gesamt aller Arten   ", 9, c.INK, c.F_SEMI),
                     c.run('=Format(%s, "N0") & " Bauteile in " & Format(%s, "N0") & " Arten  ·  Rohbau " & %s & " m³"'
                           % (V_ANZ, V_ARTEN, 'Format(%s, "#,##0.0")' % V_VOL), 8.5, c.MUTED)])
    z_gesamt = c.zeile(kopf_h[4], [c.zelle(c.cell(name + "_G", gesamt, border_xml=c.edge(["Top"], c.HAIR, "0.75pt"), pad=(4, 4, 4, 0)),
                                       len(LISTE_SPALTEN))])
    z_eti = etikett_zeile(name + "_E", "T150", "Umbruch und Zählung je Art, RunningValue, Datenbalken, Klick; ohne Bildspalte (jede Zeile mit Bild kostet Zeit)",
                          len(LISTE_SPALTEN))
    innen = (c.kopf_mitglied() + c.kopf_mitglied()
             + c.gruppe_mitglied(pos_g, "=Fields!Nr.Value", [("=" + MENGE, True), ("=Fields!Nr.Value", False)])
             + c.fuss_mitglied())
    mitglieder = [c.gruppe_mitglied(art_g, "=Fields!ObjNr.Value", [("=Val(Fields!ObjNr.Value)", False)], kinder=innen,
                                  umbruch=True, seitenzaehlung_neu=True, seitenname="=" + art, label='="Bauteilliste " & ' + art),
                  c.fuss_mitglied(), c.fuss_mitglied()]
    return c.tablix_gruppen(name, top, left, LISTE_SPALTEN, [z_titel, z_kopf, z_daten, z_summe, z_gesamt, z_eti], mitglieder, LISTE_H,
                            filter_xml=c.filter_liste(c.filter_j(BAUTEIL)), keine_zeilen="Keine Bauteile im Teilbild.")


# ---------------------------------------------------------------- B110 Etiketten zum Ausschneiden (QR-Code), B120 Strichcode 128
# Ein Etikett je Bauteil, 2 je Reihe, 4 Reihen je Seite; die Tabelle fliesst ueber so viele Seiten, wie die Stellschraube erlaubt.
ETIKETT_W, ETIKETT_PITCH, ETIKETT_H, ETIKETT_ZEILE = 8.85, 9.0, 5.8, 6.0
ETIKETT_REIHEN = 4          # Reihen je Seite: 4 x 6,0 cm passen unter den Abschnittstitel (1,85 cm) in die 27,1 cm Nutzhoehe
SCHNITT = "<Border><Color>%s</Color><Style>Dashed</Style><Width>0.75pt</Width></Border>" % c.FAINT       # Schnittlinie

LAE, DCK, HOE = "CDbl(Fields!Laenge.Value)", "CDbl(Fields!Dicke.Value)", "CDbl(Fields!Hoehe.Value)"
# Masse je Bauteilart: (Objektnummern, [(Name, Ausdruck, Format, Einheit) ...]) - hoechstens drei je Etikett. Decke und Bodenplatte
# zeigen Flaeche und Dicke (Laenge und Breite waeren bei schiefen Platten nur die Umrissmasse); die Menge steht eigens darunter.
MASSE = [((1,), [("Länge", LAE, "N2", "m"), ("Dicke", DCK + " * 100", "0.#", "cm"), ("Höhe", HOE, "N2", "m")]),
         ((3,), [("Breite", LAE + " * 100", "0.#", "cm"), ("Tiefe", DCK + " * 100", "0.#", "cm"), ("Höhe", HOE, "N2", "m")]),
         ((6,), [("Länge", LAE, "N2", "m"), ("Breite", DCK + " * 100", "0.#", "cm"), ("Höhe", HOE + " * 100", "0.#", "cm")]),
         ((4, 704), [("Fläche", FL, "N1", "m²"), ("Dicke", HOE + " * 100", "0.#", "cm")]),
         ((991, 992), [("Breite", LAE, "N2", "m"), ("Höhe", HOE, "N2", "m")])]


def mass(i, teil):
    """Das i-te Mass des Bauteils, je nach Bauteilart: Name (teil 0), Wert als Text (1) oder Einheit (2); ohne Mass ein leerer Text."""
    glieder = []
    for nummern, liste in MASSE:
        if i < len(liste):
            name, ausdruck, fmt, einheit = liste[i]
            glieder.append("%s, %s" % (b.ist(*nummern), ['"%s"' % name, 'Format(%s, "%s")' % (ausdruck, fmt), '"%s"' % einheit][teil]))
    return 'Switch(%s, True, "")' % ", ".join(glieder)


# Was auf die Etiketten kommt: Bauteile der gewaehlten Art (Stellschraube; "0" = alle Arten), die groessten nach Menge
TREFFER = ('(%s And (Parameters!Etiketten_Art.Value = "0" Or Val(Fields!ObjNr.Value) = Val(Parameters!Etiketten_Art.Value)))' % BAUTEIL)
N_ETIKETTEN = "CInt(Parameters!Etiketten_Anzahl.Value)"
# Text im QR-Code: Art und Name, Material, Masse und Menge, Bauteil-ID - je eine Zeile; Code.EtikettText haelt die 106 Byte ein
# Name auf dem Etikett: die Bezeichnung des Bauteils, sonst die Bauteilart (nicht der Objektname aus dem Modell - der bliebe in der
# englischen Fassung deutsch: "WALL / Wand")
BEZ = '("" & Fields!Bezeichnung.Value)'
ETIKETT_NAME = "IIf(Len(%s) > 0, %s, %s)" % (BEZ, BEZ, ART)
QR_KOPF = 'IIf(Len(%s) > 0, %s & ": " & %s, %s)' % (BEZ, ART, BEZ, ART)
QR_MASSE = ('Code.Verbinde(%s) & ChrW(10) & "Menge " & %s & " " & %s'
            % (", ".join('%s & " " & %s & " " & %s' % (mass(i, 0), mass(i, 1), mass(i, 2)) for i in range(3)), fm(MENGE), EINHEIT))
QR_TEXT = 'Code.EtikettText(%s, "" & Fields!Material.Value, %s, "ID " & Fields!Nr.Value, 106)' % (QR_KOPF, QR_MASSE)


@b.baustein("B120", "Strichcode 128")
def b120(top, left, w):
    """Der Streifen unten auf jedem Etikett: Code 128 der Bauteil-ID (fuer Handscanner) und die ID als Text darunter. Teil von B110."""
    return (c.image("LT_Et_SC", top, left, w, 0.9, "=Code.Strichcode128(Fields!Nr.Value)", mime="image/png")
            + c.text("LT_Et_Nr", top + 1.0, left, w, 0.4, c.run('="ID " & Fields!Nr.Value', 7.5, c.MUTED), valign="Middle"))


def etikett_karte():
    """Ein Etikett: Art, Name, Material, bis zu drei Masse, Menge, Teilbild, QR-Code (Klartext zum Scannen mit dem Telefon) und der
    Strichcode-Streifen (B120). Klick auf Name, Menge und QR-Code zoomt aufs Bauteil. Der gestrichelte Rahmen ist die Schnittlinie;
    die Felder sind Kinder des Rechtecks und ueberlappen sich nicht."""
    n = "LT_Et"
    x, lw = 0.35, 5.3                                     # linker Block; rechts daneben der QR-Code
    art = c.text(n + "_Art", 0.25, x, lw, 0.32, c.run("=UCase(%s)" % ART, 7, c.BLUE, c.F_SEMI))
    name = b.klick(c.text(n + "_Name", 0.62, x, lw, 0.55, c.run("=" + kurz(ETIKETT_NAME, 24), 12, c.INK, c.F_SEMI), valign="Middle"))
    # Material nur, wenn das Bauteil eines hat (Fenster und Tueren haben keines); 28 Zeichen: kleine Schrift ist im Fenster bis 8 % breiter
    material = c.text(n + "_Mat", 1.22, x, lw, 0.42, c.run("=" + kurz('("" & Fields!Material.Value)', 28), 8, c.MUTED), valign="Middle")
    masse = "".join(
        c.text("%s_M%d" % (n, i + 1), 1.85, x + i * 1.8, 1.7, 0.9,
               [c.para([c.run("=UCase(%s)" % mass(i, 0), 6.5, c.MUTED, c.F_SEMI)]),
                c.para([c.run("=" + mass(i, 1), 10.5, c.INK, c.F_SEMI), c.run('=" " & ' + mass(i, 2), 7, c.MUTED)])], valign="Top")
        for i in range(3))
    menge = b.klick(c.text(n + "_Menge", 2.95, x, 4.0, 0.8,
                           c.para([c.run("=" + fm(MENGE), 16, c.INK, c.F_LIGHT), c.run("=" + EINHEIT, 9, c.MUTED)]), valign="Bottom"))
    teilbild = c.text(n + "_TB", 3.25, x + 4.1, ETIKETT_W - 2 * x - 4.1, 0.5,
                      c.run('="Teilbild " & Format(Val(Left(Fields!Nr.Value, 4)), "0")', 8, c.MUTED), align="Right", valign="Bottom")
    qr = c.image(n + "_QR", 0.25, ETIKETT_W - x - 2.6, 2.6, 2.6, "=Code.QrPng(%s, 5)" % QR_TEXT, mime="image/png", action=b.ZOOM)
    streifen = b120(3.9, x, ETIKETT_W - 2 * x)
    # 0,2 cm Luft UEBER jedem Etikett: auf den Folgeseiten stuende die Schnittlinie sonst direkt am Seitenkopf
    karte_ = c.rect(n + "_Karte", ETIKETT_ZEILE - ETIKETT_H, 0, ETIKETT_W, ETIKETT_H, art + name + material + masse + menge + teilbild + qr + streifen,
                    border_xml=SCHNITT)
    # In der letzten Reihe legt die Matrix auch fuer ein fehlendes Etikett eine Zelle an: ohne Datensatz (Nr leer) ausblenden.
    return c.rect(n + "_Zelle", None, 0, 0, 0, karte_, hidden='=Len(Fields!Nr.Value & "") = 0')


def etiketten_raster(name, top, left):
    """Raster 2 je Reihe: Zeile = (RowNumber-1) \\ 2, Spalte = (RowNumber-1) Mod 2, nach Menge absteigend (bei gleicher Menge
    nach Teilbild und Elementnummer); Deckel = Stellschraube.
    Das umschliessende Rechteck haelt nicht zusammen (keep=False): ab der 5. Reihe laeuft die Tabelle auf die naechste Seite."""
    # Rang als Text fester Breite: Menge (auf 4 Stellen), dann Teilbild und Elementnummer umgekehrt (kleinere zuerst), dann das Kuerzel.
    # Eine Zahl reicht dafuer nicht: gleiche Bauteile in kopierten Teilbildern haben dieselbe Menge UND dieselbe Elementnummer; TopN
    # naehme dann alle Gleichen mit (9 statt 8 Etiketten). Sortiert wird nach demselben Text - die 8 sind so der Anfang der 16.
    rang = ('IIf(%s, Format(CLng(%s * 10000), "000000000000000") & Format(9999 - Val(Left(Fields!Nr.Value, 4)), "0000") & '
            'Format(9999999999 - Val(Right(Fields!Nr.Value, 10)), "0000000000") & Mid(Fields!Nr.Value, 5, 3), "")' % (TREFFER, MENGE))
    xml = ('<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>'
           "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
           "</TablixCells></TablixRow></TablixRows></TablixBody>"
           '<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="%s_c"><GroupExpressions><GroupExpression>'
           "=(RowNumber(Nothing) - 1) Mod 2</GroupExpression></GroupExpressions></Group></TablixMember></TablixMembers>"
           "</TablixColumnHierarchy>"
           '<TablixRowHierarchy><TablixMembers><TablixMember><Group Name="%s_r"><GroupExpressions><GroupExpression>'
           "=(RowNumber(Nothing) - 1) \\ 2</GroupExpression></GroupExpressions></Group></TablixMember></TablixMembers>"
           "</TablixRowHierarchy><DataSetName>%s</DataSetName>%s%s"
           "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>"
           "<Style><Border><Style>None</Style></Border></Style></Tablix>"
           % (name + "_Tb", c.cm(ETIKETT_PITCH), c.cm(ETIKETT_ZEILE), etikett_karte(), name, name, DS,
              c.filter_liste(c.filter_j(TREFFER), c.filter_topn(rang, N_ETIKETTEN)),
              c.sortierung(("=" + rang, True)), c.cm(ETIKETT_ZEILE), c.cm(ETIKETT_PITCH)))
    return c.rect(name, top, left, 2 * ETIKETT_PITCH, ETIKETT_REIHEN * ETIKETT_ZEILE, xml, keep=False)


@b.baustein("B110", "Etiketten mit QR-Code")
def b110(top, left, w):
    """Etiketten zum Ausschneiden: je Bauteil eines mit Name, Art, Material, Massen, Menge, QR-Code und Strichcode (B120). 2 je Reihe
    (Spaltengruppe), 8 je Seite; Bauteilart und Anzahl waehlt der Anwender (Stellschrauben Etiketten_Art, Etiketten_Anzahl)."""
    n = b.anzahl(TREFFER, DS)
    hinweis = ('=Parameters!Etiketten_Art.Label & "  ·  " & IIf(%s = 0, "kein Bauteil im Teilbild", IIf(%s > %s, %s & " von " & '
               'Format(%s, "N0") & ", die größten nach Menge", "alle " & Format(%s, "N0") & ", die größten zuerst"))'
               % (n, n, N_ETIKETTEN, N_ETIKETTEN, n, n))
    items = abschnitt("LT_B11", top, left, w, "Baustelle", "Etiketten zum Ausschneiden", hinweis)
    items += etiketten_raster("LT_Etiketten", top + 1.45, left)
    ende = top + 1.45 + ETIKETT_REIHEN * ETIKETT_ZEILE
    items += b.etikett("LT_B11_e", ende + 0.05, left, w, "B110",
                       "Spalten- und Zeilengruppe (Mod 2), fließt über Seiten; QR-Code mit Klartext (höchstens 106 Byte); "
                       "Art und Anzahl als Stellschrauben")
    items += b.etikett("LT_B12_e", ende + 0.5, left, w, "B120",
                       "Code 128 der Bauteil-ID als Bild aus VB (Code.Strichcode128), Zeichenvorrat ASCII 32 bis 126")
    return items


KARTEN_ABSTAND = 0.4        # Luft zwischen Seitenkopf und Abschnittstitel
KARTEN_H = KARTEN_ABSTAND + 1.45 + ETIKETT_REIHEN * ETIKETT_ZEILE + 0.95


def karten_abschnitt(top):
    """Etiketten-Abschnitt: eigener Seitenabschnitt (Umbruch davor, Seitenzaehlung neu, Seitenname, Lesezeichen) mit Raster und Etiketten.
    Er haelt nicht zusammen (keep=False), weil er mit mehr als 8 Etiketten ueber mehrere Seiten laeuft."""
    return c.rect("LT_Karten_Abschnitt", top, X0, W, KARTEN_H, b110(KARTEN_ABSTAND, 0, W), keep=False, umbruch="Start",
                  seitenzaehlung_neu=True, seitenname='="%s"' % KARTEN_NAME, label='="%s"' % KARTEN_NAME), KARTEN_H


# ---------------------------------------------------------------- Zusammenbau
def build():
    b.SEITE_AKTUELL[0] = "build_listen"
    deck, _ende = deckseite()
    liste_top = SEITE_NUTZ_H + 0.1
    liste = t150(liste_top, X0, W)
    karten, karten_h = karten_abschnitt(liste_top + LISTE_H + 0.4)
    inhalt = deck + liste + karten
    nenn_h = liste_top + LISTE_H + 0.4 + karten_h
    xml = c.report(inhalt, [c.dataset(DS, QUERY, FIELDS)], extra_params=PARAMS,
                   code=code(), footer_xml=fuss_xml(), header_xml=kopf_xml(), header_h=1.3, header_first=False, footer_first=False,
                   fliessend=True, fliess_h=nenn_h, variablen=VARIABLEN, codemodules=CODEMODULES)
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Listen.rdlc")
    c.save(ziel, xml)
    return ziel


def parameter_aus_aufruf():
    """--param=Name=Wert (mehrere Werte mit |). Ohne Angabe bekommt die Mehrfachliste Material ALLE Werte des Datensatzes - so verhaelt sich
    Allplan ohne Auswahl; der kopflose Renderer kennt den Distinct-Prompt nicht."""
    werte = {}
    for a in sys.argv:
        if a.startswith("--param="):
            name, _, wert = a[8:].partition("=")
            werte[name] = wert.split("|") if name == "Material" else wert
    if "Material" not in werte:
        with open(JSON, encoding="utf-8") as handle:
            zeilen = json.load(handle)["rows"]
        werte["Material"] = sorted({r.get("Material") or "" for r in zeilen})
    return werte


def daten_klein(n):
    """Pruefdatensatz: nur die ersten n Bauteile (keine Raeume) - zeigt, dass die letzte Reihe kein leeres Etikett malt."""
    with open(JSON, encoding="utf-8") as handle:
        d = json.load(handle)
    d["rows"] = [r for r in d["rows"] if r["ObjNr"] != "61"][:n]
    pfad = os.path.join(os.path.dirname(JSON), "_klein.json")        # neben dem Datensatz: die Bildplatzhalter sind relativ dazu
    with open(pfad, "w", encoding="utf-8") as handle:
        json.dump(d, handle, ensure_ascii=False)
    return pfad


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--pdf", "--daten", "--eng", "--param", "--nur-bauteile"})
    ziel = build()
    print(ziel)
    if ENG:
        ziel = os.path.join(OUT_DIR, "eng", "Report_Master_Listen.rdlc")
        if not os.path.isfile(ziel):
            sys.exit("FEHLER: %s fehlt - erst python master/sprache.py --en" % ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        klein = next((int(a[15:]) for a in sys.argv if a.startswith("--nur-bauteile=")), None)
        daten_json = daten_klein(klein) if klein else JSON
        try:
            c.rendern(ziel, daten_json, AUS, parameter=parameter_aus_aufruf(), pdf="--pdf" in sys.argv, vollzugriff=True)
        finally:
            if klein and os.path.isfile(daten_json):
                os.remove(daten_json)
