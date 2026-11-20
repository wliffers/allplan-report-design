# -*- coding: utf-8 -*-
"""Begleit-Report "Report Master Bewehrung" (RDL 2016) nach out/Report_Master_Bewehrung.rdlc.

Stahl im Teilbild: Rundstahl und Matten aus EINER Abfrage (Tabelle ENGINEERING). Seite 1 ist der Ueberblick fuer
Tragwerksplaner und Baustelle, ab Seite 2 folgen die vollstaendigen Listen.

    python build_bewehrung.py              schreibt out/Report_Master_Bewehrung.rdlc
    python build_bewehrung.py --render     rendert zusaetzlich kopflos nach bewehrung/aus/png (daten/bewehrung.json)
    python build_bewehrung.py --render --daten=bewehrung_gross     anderer Datensatz (daten/<name>.json, aus/png_<name>)
                                                                   bewehrung_gross: 300 Positionen, bewehrung_klein: 2 Staebe, keine Matte
                                                                   bewehrung_fall_a / _fall_b: zwei echte Teilbilder, neutralisiert
                                                                   (Meterware, zusammengefasste Zeilen, mehrfach verlegte Matten;
                                                                   Fall B mit Ausfuehrungen = 2)
Beispieldaten und ihr Erzeuger: daten/make_bewehrung_gross.py (die 17 Zeilen von bewehrung.json stammen aus Allplan, ebenso die
Zeilen der beiden Fall-Datensaetze). Die Rechenregeln prueft werkzeug/tests/test_bewehrung.py gegen Allplans eigene Listen.

Bausteine (angemeldet mit @b.baustein): K080 Kennzahl-Kacheln, U050 Hinweis Ueberlaengen, D170 Balken Rundstahl nach Durchmesser,
D180 Ring Stab / Matte, D190 Ring gerade / gebogen, T090 Matten nach Typ, T100 Rundstahl nach Stahlguete,
T110 Stabliste, T120 Mattenliste. Elementnamen beginnen mit "RB_".

Stab oder Matte wird NIE ueber einen Text aus der Abfrage entschieden, sondern ueber die ObjId (366 und 368 = Matte): nur so
stimmt die englische Fassung, weil der Sprachschalter jede Zeichenkette im Ausdruck uebersetzt, Werte aus der Abfrage aber nicht.

Rechenregeln (an zwei echten Teilbildern und am Probemodell gegen Allplans Stabliste, Mattenstahlliste und Uebersicht
nachgerechnet, Sollwerte in werkzeug/tests/test_bewehrung.py). Allplan fasst gleiche Zeilen einer Position zusammen und addiert dabei Anzahl, Gesamtlaenge
und Einzellaenge, das Gewicht aber NICHT. Darum:
  - Stab-Gewicht = Gesamtlaenge x KgJeM (wie Allplans "Stabliste Biegeformen, Zusammenfassung"), nie das Feld Gewicht;
    Matten-Gewicht = Feld Gewicht, je Matte auf 2 Stellen gerundet (wie Allplans Mattenstahlliste, F14.2).
  - Stablaenge einzeln = Gesamtlaenge / Anzahl, nie das Feld Einzellaenge (das ist bei zusammengefassten Zeilen ein Vielfaches).
  - Meterware (Feld LfdM = @794@ = 1): Stueck 1, Laenge "lfdm", nie Ueberlaenge - wie Allplans Stabliste.
  - Zeilen und Summen beider Listen gelten fuer EINE Ausfuehrung (wie Allplans Listen); die Summenzeile nennt bei
    Ausfuehrungen > 1 zusaetzlich das Gesamtgewicht. Seite 1 (Kacheln, Diagramme, kleine Tabellen) rechnet mit den
    Ausfuehrungen (Feld Ausfuehrungen, leer oder 0 zaehlt als 1) - so rechnet Allplans "Uebersicht Bewehrung".

Datenfest: Seite 1 hat Deckel (Durchmesser 10, Mattentypen 5, Stahlgueten 5, Ueberlaengen 4 Karten) und bleibt immer eine Seite;
Stabliste und Mattenliste sind vollstaendig (ohne Deckel), fliessen ueber Seiten, die Kopfzeile wiederholt sich.
Die Stabliste steht zuletzt: die Mattenliste darueber waechst und schiebt sie nach unten.
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
DATEN = next((a[8:] for a in sys.argv if a.startswith("--daten=")), "bewehrung")
JSON = os.environ.get("BEWEHRUNG_JSON", os.path.join(HERE, "daten", DATEN + ".json"))
AUS = os.environ.get("BEWEHRUNG_AUS", os.path.join(HERE, "aus", "png" if DATEN == "bewehrung" else "png_" + DATEN))

MAX_DURCHMESSER = 10   # Balken im Durchmesser-Diagramm
MAX_TYPEN = 5          # Zeilen "Matten nach Typ"
MAX_GUETEN = 5         # Zeilen "Rundstahl nach Stahlguete"
MAX_UEBER = 4          # Karten im Ueberlaengen-Hinweis

# ---------------------------------------------------------------- Daten
# Bild (@205@) steht zuletzt und ist die erste und einzige @205@-Spalte: die Biegeform in ihrer Ebene (Projection=0).
QUERY = """SELECT
       @419@[Name=Bauteil],
       @425@[Name=Teilbild],
       @452@[Name=Geschoss],
       @10@[Name=Nr],
       [Name=ObjId|f=@OBJ@],
       @799@[Name=Gebogen],
       @767@[Name=Position],
       @766@[Name=Anzahl],
       @423@[Name=Ausfuehrungen],
       @759@[Name=Durchmesser],
       @785@[Name=Bezeichnung],
       @422@[Name=Stahlguete],
       @760@[Name=Gesamtlaenge|Dim=3],
       @757@[Name=Einzellaenge|Dim=3],
       @765@[Name=Gewicht],
       @756@[Name=KgJeM],
       @763@[Name=Biegeform],
       @751@[Name=Mattenname],
       @758@[Name=MattenBreite|Dim=3],
       @794@[Name=LfdM],
       @205@[Name=Bild|Projection=0|Width=69|Height=25|GText=HD_CENTERMIDDLE|CanSave=true]
FROM [ENGINEERING,Filter=@793@|@792@|@1210@]
"""
FIELDS = [("Bauteil", "String"), ("Teilbild", "String"), ("Geschoss", "String"), ("Nr", "String"), ("ObjId", "Int32"),
          ("Gebogen", "Int32"), ("Position", "Int32"), ("Anzahl", "Int32"), ("Ausfuehrungen", "Int32"),
          ("Durchmesser", "Double"), ("Bezeichnung", "String"), ("Stahlguete", "String"), ("Gesamtlaenge", "Double"),
          ("Einzellaenge", "Double"), ("Gewicht", "Double"), ("KgJeM", "Double"), ("Biegeform", "String"),
          ("Mattenname", "String"), ("MattenBreite", "Double"), ("LfdM", "String"), ("Bild", "Byte[]")]
# LfdM als String wie in Allplans Stabliste Biegeformen (Feld LfdM, Vergleich "= 1"); in der Probe q_eng gemessen: "0" / "1"

# Stellschraube: Lagerlaenge der Staebe (m); laengere Positionen sind Ueberlaengen
PARAMS = c.parameter("Lagerlaenge", "Float", "12", "Lagerlänge [m]")

DS = "AllplanReport"
MATTE = "(CInt(Fields!ObjId.Value) = 366 Or CInt(Fields!ObjId.Value) = 368)"
STAB = "(CInt(Fields!ObjId.Value) <> 366 And CInt(Fields!ObjId.Value) <> 368)"
GEBOGEN = "(CInt(Fields!Gebogen.Value) = 1)"
STAB_GEBOGEN = "(%s And %s)" % (STAB, GEBOGEN)
LFDM = "(Val(Fields!LfdM.Value) >= 1)"                               # Meterware (@794@ = 1)
AUSF = "IIf(CDbl(Fields!Ausfuehrungen.Value) < 1, 1.0, CDbl(Fields!Ausfuehrungen.Value))"
ANZ = "CDbl(Fields!Anzahl.Value)"
GESL = "CDbl(Fields!Gesamtlaenge.Value)"
# EINE Formel fuer jede Zeile, Summe und Kachel (Herleitung oben im Kopf):
KG1 = "IIf(%s, Round(CDbl(Fields!Gewicht.Value), 2), %s * CDbl(Fields!KgJeM.Value))" % (MATTE, GESL)   # kg je Ausfuehrung
EINZEL = "(%s / IIf(%s < 1, 1.0, %s))" % (GESL, ANZ, ANZ)            # Stablaenge einzeln (m), nicht das Feld Einzellaenge
FLAECHE1 = "CDbl(Fields!Einzellaenge.Value) * CDbl(Fields!MattenBreite.Value) * " + ANZ   # Matten-m2 je Ausfuehrung
KG = "(%s) * %s" % (KG1, AUSF)                                       # Seite 1: mal Ausfuehrungen
STUECK = "%s * %s" % (ANZ, AUSF)
FLAECHE = "%s * %s" % (FLAECHE1, AUSF)
UEBER = "(%s And Not %s And %s > Parameters!Lagerlaenge.Value)" % (STAB, LFDM, EINZEL)
DM = "CDbl(Fields!Durchmesser.Value)"
NACHRANG = "Val(Right(Min(Fields!Nr.Value), 8)) / 1000000000000"      # eindeutiger Rang je Gruppe (TopN zaehlt Gleiche sonst alle mit)

ROW = c.edge(["Bottom"], c.HAIR, "0.5pt")
# Zellen in Zeilen bis 0,6 cm: oben und unten 0 pt Innenabstand. Mit 2 pt schneidet die Zeile den Fuss des Kommas ab, und
# "27,6" sieht im PDF wie "27.6" aus (der PDF-Text hat das Komma; gemessen 2026-11-19, references/fallen.md)
P0 = (4, 0, 4, 0)
HEAD = c.edge(["Bottom"], c.INK, "1pt")
SUMLINE = c.edge(["Top"], c.INK, "1pt")
C_STAB, C_MATTE = c.RAMP[0], c.SERIE[1]          # Ring Stab / Matte
C_GERADE, C_GEBOGEN, C_UEBER = c.FAINT, c.BLUE, c.AMBER     # Form und Bewertung, in Ringen wie in der Stabliste gleich


def S(ausdruck, bedingung="True", scope=None):
    """Summe ueber die Zeilen, die die Bedingung erfuellen (Ausdruecke nur mit Fields!, ohne Zeilen-Kontext)."""
    return "Sum(IIf(%s, %s, 0.0)%s)" % (bedingung, ausdruck, ', "%s"' % scope if scope else "")


def kurz(x, n):
    """Text auf n Zeichen kuerzen, Auslassung als Punkte (Zellen wachsen nicht, abgeschnitten wirkt kaputt)."""
    return 'IIf(Len(%s) > %d, Left(%s, %d) & "…", %s)' % (x, n, x, n - 1, x)


def gewicht(x):
    """kg mit Tausenderpunkt; ab 1.000 kg ganze Zahl."""
    return 'Format(%s, IIf(%s >= 1000, "#,##0", "#,##0.0"))' % (x, x)


def kgt_wert(x):
    """Kachelzahl: unter 1.000 kg in kg mit einer Stelle, darueber in t mit zwei Stellen."""
    return 'IIf(%s >= 1000, Format(%s / 1000, "N2"), Format(%s, "N1"))' % (x, x, x)


def kgt_einheit(x):
    return 'IIf(%s >= 1000, " t", " kg")' % x


RUND = S(KG, STAB)
MATTEN = S(KG, MATTE)
# Gesamtsumme aus den gerundeten Teilen: so addieren sich die Zahlen auf dem Blatt (912,6 + 217,9 = 1.130,5), wie in Allplans Uebersicht
GES = '(CDbl(Format(%s, "0.0")) + CDbl(Format(%s, "0.0")))' % (RUND, MATTEN)
RUND_D = S(KG, STAB, DS)           # Summen im Bereich des ganzen Datensatzes (fuer Anteile in Tabellen und Ringen)
GES_D = S(KG, "True", DS)

# Positionen, nicht Zeilen: eine Stab-Position ist eine Nr (@10@, mehrere Verlegungen = mehrere Zeilen mit derselben Nr),
# eine Matten-Position ist Teilbild + Bauteil + Positionsnummer (jede verlegte Matte hat ihre eigene Nr)
MATTE_POS = 'Fields!Teilbild.Value & "|" & Fields!Bauteil.Value & "|" & CStr(Fields!Position.Value)'


def pos_zahl(bedingung, schluessel, scope=None):
    return "CountDistinct(IIf(%s, %s, Nothing)%s)" % (bedingung, schluessel, ', "%s"' % scope if scope else "")


N_STAB, N_MATTE = pos_zahl(STAB, "Fields!Nr.Value"), pos_zahl(MATTE, MATTE_POS)
N_UEBER_D = pos_zahl(UEBER, "Fields!Nr.Value", DS)
MAX_EINZEL = "Max(IIf(%s And Not %s, %s, 0.0))" % (STAB, LFDM, EINZEL)


# ---------------------------------------------------------------- Hilfen
def deckel(xml, gruppe, ausdruck, n):
    """Haengt an die Gruppe einen "nur die n groessten"-Filter (Diagramm-Kategorie, Tablix-Gruppe)."""
    f = c.topn(ausdruck, n)
    return re.sub(r'(<Group Name="%s"><GroupExpressions>.*?</GroupExpressions>)' % re.escape(gruppe),
                  lambda m: m.group(1) + f, xml, count=1, flags=re.S)


def zelle(inner, span=None):
    """Tabellenzelle; mit span ueber mehrere Spalten (die Folgezellen bleiben leer)."""
    cols = "<ColSpan>%d</ColSpan>" % span if span else ""
    return "<TablixCell><CellContents>%s%s</CellContents></TablixCell>%s" % (inner, cols, "<TablixCell/>" * ((span or 1) - 1))


def zeile(h, zellen):
    return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (c.cm(h), "".join(zellen))


def tablix(name, breiten, zeilen, mitglieder, hoehe, extra="", stil="", top=0, left=0):
    """Tablix aus fertigen Zeilen und Zeilen-Mitgliedern. extra steht vor dem Datensatznamen (NoRows), stil im Style."""
    return ('<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s</TablixRows></TablixBody>'
            "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>"
            "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>%s"
            "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border>%s</Style></Tablix>"
            % (name, "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % c.cm(x) for x in breiten), "".join(zeilen),
               "<TablixMember/>" * len(breiten), "".join(mitglieder), extra, c.cm(top), c.cm(left), c.cm(hoehe), c.cm(sum(breiten)), stil))


def kopf_mitglied():
    return "<TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember>"


def fuss_mitglied(versteckt=None):
    vis = "<Visibility><Hidden>%s</Hidden></Visibility>" % c.esc(versteckt) if versteckt else ""
    return "<TablixMember><KeepWithGroup>Before</KeepWithGroup>%s</TablixMember>" % vis


def gruppe_mitglied(name, ausdruck, sortierung, absteigend=False, deckel_xml=""):
    return ('<TablixMember><Group Name="%s"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions>%s</Group>'
            "<SortExpressions><SortExpression><Value>%s</Value>%s</SortExpression></SortExpressions></TablixMember>"
            % (name, c.esc(ausdruck), deckel_xml, c.esc(sortierung), "<Direction>Descending</Direction>" if absteigend else ""))


def keine_zeilen(text):
    """Meldung, wenn die Tabelle keine Zeile hat (steht statt der Tabelle) samt Schrift dazu."""
    stil = "<FontFamily>%s</FontFamily><FontSize>9pt</FontSize><Color>%s</Color>" % (c.F, c.MUTED)
    # als Ausdruck ("=...") geschrieben: nur so uebersetzt der Sprachschalter den Text (NoRowsMessage steht nicht in seinen Textfeldern)
    return "<NoRowsMessage>=%s</NoRowsMessage>" % c.esc('"%s"' % text), stil


def kopfzelle(name, label, align=None, unter=None):
    """Tabellenkopf: Name in Grossbuchstaben, optional eine zweite Zeile (Einheit) heller darunter."""
    inhalt = [c.para([c.run(label.upper(), 7, c.MUTED, c.F_SEMI)], align)]
    if unter:
        inhalt.append(c.para([c.run(unter, 7, c.FAINT)], align))
    return c.cell(name, inhalt, align, "Bottom", border_xml=HEAD, pad=(4, 2, 4, 4))


def balken_zelle(name, farbe, y, maximum, hoehe_anteil="0.42"):
    """Zellenbalken: Massstab ist der groesste Wert der Tabelle (Ausdruck maximum)."""
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
    return zeile(0.45, [zelle(c.cell(name, inner, valign="Top", pad=(4, 4, 0, 0)), span)])


def abschnitt(name, top, left, w, label, titel, rechts=None):
    """Abschnittskopf wie b.overline (kleiner Name in Leitfarbe, Titel, Haarlinie), aber mit 0,05 cm Luft zwischen den Feldern:
    ueberlappen sich Geschwister auch nur um 0,02 cm, verschiebt Allplans Report-Fenster eines davon. rechts: optionaler Hinweis
    rechtsbuendig in der Zeile des kleinen Namens (eigenes Feld daneben, nicht darueber)."""
    breite_o = 3.2 if rechts else w
    xml = (c.text(name + "_o", top, left, breite_o, 0.38, c.run(label.upper(), 7, c.MUTED, c.F_SEMI))
           + c.text(name + "_t", top + 0.43, left, w, 0.7, c.run(titel, 13, c.INK, c.F_SEMI))
           + c.line(name + "_l", top + 1.18, left, w))
    if rechts:
        xml += c.text(name + "_h", top, left + breite_o + 0.1, w - breite_o - 0.1, 0.38, rechts, "Right", "Bottom")
    return xml


# ---------------------------------------------------------------- Seitenrahmen
def band():
    x0 = c.INSET
    inner = (c.rect("RB_BandAkzent", 1.15, x0, 1.3, 0.1, bg=c.AKZENT)
             + c.text("RB_BandOver", 1.4, x0, 12.9, 0.45, c.run("REPORT MASTER  ·  BEGLEIT-REPORT", 8, c.AKZENT_DUNKEL, c.F_SEMI))
             + c.text("RB_BandTitel", 1.9, x0, 12.9, 1.45, c.run("Bewehrung", 30, c.WHITE, c.F))
             + c.text("RB_BandSub", 3.4, x0, 12.9, 0.55,
                      c.run('=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")',
                            9, c.AUF_NAVY, c.F))
             + c.text("RB_BandRechts", 1.4, x0 + 13.05, 4.95, 0.45, c.run("Bewehrte Bauteile", 8, c.AUF_NAVY, c.F_SEMI), align="Right")
             + c.text("RB_BandRechts2", 1.9, x0 + 13.05, 4.95, 1.45,
                      c.para([c.run('=Format(CountDistinct(Fields!Bauteil.Value), "N0")', 30, c.WHITE, c.F_ZAHL)], "Right"))
             + c.text("RB_BandRechts3", 3.4, x0 + 13.05, 4.95, 0.55, c.run("Stab und Matte im Teilbild", 9, c.AUF_NAVY, c.F), align="Right"))
    return c.rect("RB_Band", 0, 0, c.PAGE_W, 4.5, inner, bg=c.NAVY)


def kopf2():
    """Kopf der zweiten Seite: wie seitenkopf(), aber fuer den Begleit-Report."""
    x0 = c.INSET
    inner = (c.rect("RB_P2Akzent", 0.62, x0, 0.9, 0.08, bg=c.AKZENT)
             + c.text("RB_P2Over", 0.8, x0, 12, 0.45, c.run("REPORT MASTER  ·  BEGLEIT-REPORT  ·  SEITE 2", 7, c.AKZENT_DUNKEL, c.F_SEMI))
             + c.text("RB_P2Titel", 1.3, x0, 8.8, 0.95, c.run("Listen", 19, c.WHITE, c.F))
             + c.text("RB_P2Sub", 1.3, x0 + 9, 9, 0.6, c.run("Mattenliste und vollständige Stabliste", 8.5, c.AUF_NAVY),
                      align="Right", valign="Bottom"))
    return c.rect("RB_P2Kopf", 0, 0, c.PAGE_W, 2.5, inner, bg=c.NAVY)


# ---------------------------------------------------------------- K080 Kennzahl-Kacheln
def gross_zahl(txt_expr):
    """Grosse Zahl; die Schriftgroesse schrumpft mit der Ziffernzahl, damit nichts umbricht."""
    groesse = 'IIf(Len(%s) >= 8, "12pt", IIf(Len(%s) >= 6, "15pt", "17pt"))' % (txt_expr, txt_expr)
    return ("<TextRun><Value>=%s</Value><Style><FontFamily>%s</FontFamily><FontSize>=%s</FontSize><Color>%s</Color></Style></TextRun>"
            % (c.esc(txt_expr), c.F_ZAHL, c.esc(groesse), c.INK))


def kachel(name, top, left, w, wert, einheit, label, note):
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.3, 0.3, w - 0.35, 0.95,
                      c.para([gross_zahl(wert), c.run("=" + einheit if einheit else "", 9, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.3, 0.3, w - 0.35, 0.38, c.run(label, 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.73, 0.3, w - 0.35, 0.4, c.run(note, 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.2, inner, bg=c.SURFACE)


def pos_text(n):
    return '%s & IIf(%s = 1, " Position", " Positionen")' % (n, n)


@b.baustein("K080", "Kennzahl-Kacheln Stahl")
def k080(top, left, w):
    """Sechs Kacheln: Stahl gesamt, Rundstahl, Matten, Positionen, Anteil gebogen, mittlerer Durchmesser (nach Gewicht)."""
    gap = 0.25
    kw = (w - 5 * gap) / 6
    anteil = b.quote(S(KG, STAB_GEBOGEN), RUND)
    mittel = b.quote(S(DM + " * " + KG, STAB), RUND)
    kacheln = [
        ("RB_K1", kgt_wert(GES), kgt_einheit(GES), "STAHL GESAMT", '=IIf(%s >= 1000, Format(%s, "N1") & " kg", "Rundstahl + Matten")' % (GES, GES)),
        ("RB_K2", kgt_wert(RUND), kgt_einheit(RUND), "RUNDSTAHL", "=" + pos_text(N_STAB)),
        ("RB_K3", kgt_wert(MATTEN), kgt_einheit(MATTEN), "MATTEN", "=" + pos_text(N_MATTE)),
        ("RB_K4", 'Format(%s + %s, "N0")' % (N_STAB, N_MATTE), None, "POSITIONEN",
         '=%s & IIf(%s = 1, " Stab", " Stäbe") & " · " & %s & IIf(%s = 1, " Matte", " Matten")' % (N_STAB, N_STAB, N_MATTE, N_MATTE)),
        ("RB_K5", 'IIf(%s > 0, Format(%s * 100, "N0"), "–")' % (RUND, anteil), 'IIf(%s > 0, " %%", "")' % RUND,
         "ANTEIL GEBOGEN", "des Rundstahls"),
        ("RB_K6", 'IIf(%s > 0, Format(%s, "N1"), "–")' % (RUND, mittel), 'IIf(%s > 0, " mm", "")' % RUND,
         "MITTLERER Ø", "nach Gewicht"),
    ]
    items = ""
    for i, (name, wert, einheit, label, note) in enumerate(kacheln):
        items += kachel(name, top, left + i * (kw + gap), kw, wert, einheit, label, note)
    items += b.etikett("RB_K_e", top + 2.28, left, w, "K080",
                       "sechs Kacheln, Stab/Matte über die ObjId; Stab-kg = Gesamtlänge × kg/m, mal Ausführungen")
    return items


# ---------------------------------------------------------------- U050 Hinweis Ueberlaengen
def karte(name, kw, kh):
    """Eine Karte je Ueberlaenge (Gruppe je Nr): Position und Stablaenge gross, darunter Durchmesser, Stueck, Gewicht je Ausfuehrung.
    Klick zoomt aufs Bauteil."""
    l1 = b.klick(c.text(name + "_1", 0.08, 0.3, kw - 0.4, 0.45,
                        c.para([c.run('="Pos " & Fields!Position.Value', 9.5, c.INK, c.F_SEMI),
                                c.run('="   " & Format(Max(%s), "N2") & " m"' % EINZEL, 9.5, c.AMBER_TEXT, c.F_SEMI)]),
                        valign="Middle"))
    l2 = b.klick(c.text(name + "_2", 0.6, 0.3, kw - 0.4, 0.4,
                        c.run('="Ø " & Format(%s, "0.##") & " · " & Format(Sum(%s), "N0") & " Stk. · " & Format(Sum(%s), "N0") & " kg"'
                              % (DM, ANZ, KG1), 7, c.MUTED), valign="Middle"))
    return c.rect(name + "_z", None, 0, 0, 0, c.rect(name + "_b", 0, 0, 0.07, kh, "", bg=c.AMBER) + l1 + l2, bg=c.SURFACE)


def zahl_oder_haken(n):
    """Ein Feld fuer beides: die Zahl der Ueberlaengen oder - bei 0 - ein Haken (Schrift, Groesse, Farbe als Ausdruck)."""
    return c.para(["<TextRun><Value>=%s</Value><Style><FontFamily>=%s</FontFamily><FontSize>=%s</FontSize><Color>=%s</Color></Style></TextRun>"
                   % (c.esc('IIf(%s > 0, Format(%s, "N0"), "✓")' % (n, n)), c.esc('IIf(%s > 0, Code.Schrift(3), "%s")' % (n, b.SYMBOL)),
                      c.esc('IIf(%s > 0, "24pt", "20pt")' % n), c.esc('IIf(%s > 0, "%s", "%s")' % (n, c.AMBER_TEXT, c.GREEN_TEXT)))], "Center")


@b.baustein("U050", "Hinweis Überlängen")
def u050(top, left, w):
    """Positionen mit Einzellaenge ueber der Lagerlaenge (Stellschraube): Anzahl, laengster Stab, die laengsten als Karten."""
    items = ""
    kb = 1.2                                                      # Hoehe des Hinweisbands
    n = N_UEBER_D
    farbe = c.esc('=IIf(%s > 0, "%s", "%s")' % (n, c.AMBER, c.GREEN))
    band_ = (c.rect("RB_U_akzent", 0, 0, 0.08, kb, bg=farbe)
             + c.text("RB_U_n", 0.1, 0.35, 1.4, kb - 0.2, zahl_oder_haken(n), "Center", "Middle")
             + c.text("RB_U_t", 0.1, 1.9, w - 7.2, 0.5,
                      c.run('=IIf(%s = 0, "Keine Überlängen", IIf(%s = 1, "Position länger als die Lagerlänge", "Positionen länger als die Lagerlänge"))'
                            % (n, n), 10.5, c.INK, c.F_SEMI), valign="Middle")
             + c.text("RB_U_s", 0.66, 1.9, w - 2.0, 0.45,
                      c.run('="Lagerlänge " & Format(Parameters!Lagerlaenge.Value, "0.0#") & " m (links im Report-Fenster änderbar)'
                            '  ·  längster Stab " & Format(%s, "0.00") & " m"' % MAX_EINZEL, 8, c.MUTED), valign="Middle")
             + c.text("RB_U_m", 0.1, w - 5.2, 5.0, 0.5,
                      c.run('=IIf(%s > %d, "… und " & (%s - %d) & " weitere", "")' % (n, MAX_UEBER, n, MAX_UEBER), 8, c.MUTED),
                      "Right", "Middle"))
    items += c.rect("RB_U_band", top, left, w, kb, band_, bg=c.SURFACE)
    # Karten: die laengsten Ueberlaengen nebeneinander (Spaltengruppe, TopN), Rang = Einzellaenge mit eindeutigem Nachrang
    kw, luecke, kh = 4.15, 0.3, 1.05
    rang = "Max(%s) + %s" % (EINZEL, NACHRANG)
    inhalt = karte("RB_U_k", kw, kh)
    xml = ('<Tablix Name="RB_U_Tb"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn>'
           "<TablixColumn><Width>%s</Width></TablixColumn></TablixColumns>"
           "<TablixRows><TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
           "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow></TablixRows></TablixBody>"
           '<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="RB_U_G"><GroupExpressions><GroupExpression>=Fields!Nr.Value'
           "</GroupExpression></GroupExpressions>%s</Group><SortExpressions><SortExpression><Value>=%s</Value>"
           "<Direction>Descending</Direction></SortExpression></SortExpressions>"
           "<TablixMembers><TablixMember/><TablixMember/></TablixMembers></TablixMember></TablixMembers></TablixColumnHierarchy>"
           "<TablixRowHierarchy><TablixMembers><TablixMember/></TablixMembers></TablixRowHierarchy>"
           "<DataSetName>%s</DataSetName>%s<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width>"
           "<Style><Border><Style>None</Style></Border></Style></Tablix>"
           % (c.cm(kw), c.cm(luecke), c.cm(kh), inhalt, c.cell("RB_U_x", c.run("", 6)),
              c.topn(rang, MAX_UEBER), c.esc(rang), DS, c.filters(UEBER), c.cm(kh), c.cm(kw + luecke)))
    items += c.rect("RB_U_karten", top + kb + 0.2, left, w, kh + 0.05, xml)
    items += b.etikett("RB_U_e", top + kb + 0.2 + kh + 0.1, left, w, "U050",
                       "Stablänge = Gesamtlänge / Stück über der Lagerlänge (Parameter), ohne Meterware; Deckel 4 Karten (TopN)")
    return items


# ---------------------------------------------------------------- D170 Balken Rundstahl nach Durchmesser
@b.baustein("D170", "Balken Rundstahl nach Durchmesser")
def d170(top, left, w, h=7.3):
    n = 'CountDistinct(IIf(%s, Fields!Durchmesser.Value, Nothing), "%s")' % (STAB, DS)
    items = abschnitt("RB_A1", top, left, w, "Rundstahl", "Rundstahl nach Durchmesser",
                      c.run('=IIf(%s > %d, "Die %d schwersten von " & %s & " Durchmessern", "")' % (n, MAX_DURCHMESSER, MAX_DURCHMESSER, n),
                            7.5, c.MUTED))
    fest = "<LabelsAutoFitDisabled>true</LabelsAutoFitDisabled>"
    kg = "Sum(%s)" % KG
    bars = v.chart(
        "RB_ChD", top + 1.45, left, w, h,
        [v.S("Gewicht", {"Y": "=" + kg}, typ="Bar", sub="Plain", color=c.BLUE,
             axislabel='="Ø " & Format(Min(Fields!Durchmesser.Value), "0.##")',
             label=v.dlabel(fmt="#,##0 kg", size="8.5pt", color=c.TEXT),
             custom_xml=v.custom(PointWidth="0.45", BarLabelStyle="Outside"))],
        [("=Fields!Durchmesser.Value", "=Fields!Durchmesser.Value", "Descending")],
        areas=v.area(cat_axes=[v.axis("Primary", interval="1", line=False, size="9pt", extra=fest)],
                     val_axes=[v.axis("Primary", visible=False, line=False, minimum="0",
                                      maximum='=Max(%s, "RB_ChD") * 1.35' % ('Sum(%s, "RB_ChD_Cat1")' % KG))],
                     pos=(0, 0, 100, 100)),
        nodata="Kein Rundstahl im Teilbild", extra=c.filters(STAB))
    items += deckel(bars, "RB_ChD_Cat1", kg, MAX_DURCHMESSER)
    items += b.etikett("RB_A1_e", top + 1.45 + h + 0.05, left, w, "D170",
                       "Balken je Ø, Wert am Balken, Deckel 10 (TopN)")
    return items


# ---------------------------------------------------------------- D180 / D190 Ringe mit Legende
def ring_block(praefix, kennung, top, left, w, label, titel, gruppe, farbe, bedingung, mitte, mitte_text, namen, technik):
    """Ring mit Zahl in der Mitte und Legende rechts daneben. gruppe/farbe/namen sind Ausdruecke ueber die Zeilen der Gruppe."""
    items = abschnitt(praefix, top, left, w, label, titel)
    kg = "Sum(%s)" % KG
    ring = v.chart(
        praefix + "_Ch", top + 1.4, left - 0.1, 2.7, 2.7,
        [v.S("Gewicht", {"Y": "=" + kg}, typ="Shape", sub="Doughnut",
             custom_xml=v.custom(DoughnutRadius="30", PieLabelStyle="Disabled", PieStartAngle="270"),
             pstyle="<Color>=%s</Color>" % c.esc(farbe) + v.border(c.WHITE, "Solid", "1.5pt"))],
        [("=" + gruppe, "=" + kg, "Descending")],
        areas=v.area(pos=(0, 0, 100, 100)),
        titles=(v.title("=" + mitte, size="12pt", color=c.INK, font=c.F_ZAHL,
                        extra="<ChartElementPosition><Top>28</Top><Left>20</Left><Height>22</Height><Width>60</Width></ChartElementPosition>")
                + v.title(mitte_text, size="7pt", name="Unter", color=c.MUTED, bold=False,
                          extra="<ChartElementPosition><Top>51</Top><Left>20</Left><Height>14</Height><Width>60</Width></ChartElementPosition>")),
        nodata="Keine Daten", extra=c.filters(bedingung))
    items += ring
    cols = [0.45, 2.5, 1.85, 1.1]
    zelle_h = 0.5
    inhalt = [c.cell(praefix + "_L1", c.run("■", 10, "=" + farbe, b.SYMBOL), "Left", pad=(0, 0, 0, 0), border_xml=ROW),
              c.cell(praefix + "_L2", c.run("=" + namen, 8.5, c.TEXT), pad=(0, 0, 2, 0), border_xml=ROW),
              c.cell(praefix + "_L3", c.para([c.run("=" + gewicht(kg), 8.5, c.INK, c.F_SEMI), c.run(" kg", 7, c.FAINT)]), "Right",
                     pad=(0, 0, 2, 0), border_xml=ROW),
              c.cell(praefix + "_L4", c.run('=Format(%s, "0 %%")' % b.quote(kg, GES_D if bedingung == "True" else RUND_D), 8.5, c.INK, c.F_SEMI),
                     "Right", pad=(0, 0, 0, 0), border_xml=ROW)]
    legende = tablix(praefix + "_Tb", cols, [zeile(zelle_h, [zelle(z) for z in inhalt])],
                     [gruppe_mitglied(praefix + "_G", "=" + gruppe, "=" + kg, True)], zelle_h,
                     extra="<DataSetName>%s</DataSetName>%s" % (DS, c.filters(bedingung)))
    items += c.rect(praefix + "_Feld", top + 1.4 + 0.8, left + 2.7, w - 2.7, 1.1, legende)
    items += b.etikett(praefix + "_e", top + 1.4 + 2.75, left, w, kennung, technik)
    return items


@b.baustein("D180", "Ring Stab / Matte")
def d180(top, left, w):
    ist_matte = "Max(IIf(%s, 1, 0)) = 1" % MATTE
    return ring_block("RB_R1", "D180", top, left, w, "Anteil", "Stab und Matte",
                      'IIf(%s, "Matten", "Rundstahl")' % MATTE, 'IIf(%s, "%s", "%s")' % (ist_matte, C_MATTE, C_STAB), "True",
                      'Format(%s, "0 %%")' % b.quote(RUND_D, GES_D), "Rundstahl ",  # mit geschuetztem Leerzeichen: eigene (kurze) englische Uebersetzung fuer die enge Ringmitte
                      'IIf(%s, "Matten", "Rundstahl")' % ist_matte,
                      "Ring nach Gewicht (ObjId), Zahl = Anteil Rundstahl")


@b.baustein("D190", "Ring gerade / gebogen")
def d190(top, left, w):
    gebogen = "Max(IIf(%s, 1, 0)) = 1" % GEBOGEN
    return ring_block("RB_R2", "D190", top, left, w, "Form", "Gerade und gebogen",
                      'IIf(%s, "gebogen", "gerade")' % GEBOGEN, 'IIf(%s, "%s", "%s")' % (gebogen, C_GEBOGEN, C_GERADE), STAB,
                      'Format(%s, "0 %%")' % b.quote(S(KG, STAB_GEBOGEN, DS), RUND_D), "gebogen",
                      'IIf(%s, "gebogen", "gerade")' % gebogen,
                      "Ring nach Gewicht (Feld Gebogen), Zahl = Anteil gebogen")


# ---------------------------------------------------------------- T090 / T100 kleine Tabellen mit Zellenbalken
def gruppentabelle(name, kennung, top, left, w, label, titel, spalten, gruppe, bedingung, deckel_n, rest_text, rest_zahl, summe_zellen,
                   daten_zellen, kopf_zellen, technik, leer_text):
    """Tabelle je Gruppe, nach kg absteigend, Deckel deckel_n mit Zeile "... und n weitere", Summe ueber alle, Etikett als letzte Zeile."""
    items = abschnitt(name + "_A", top, left, w, label, titel)
    kg = "Sum(%s)" % KG
    rang = kg + " + " + NACHRANG
    zeilen_h = (0.85, 0.5, 0.45, 0.6, 0.45)
    n = len(spalten)
    hidden_rest = "=%s <= %d" % (rest_zahl, deckel_n)
    z_kopf = zeile(zeilen_h[0], [zelle(z) for z in kopf_zellen])
    z_daten = zeile(zeilen_h[1], [zelle(z) for z in daten_zellen])
    z_rest = zeile(zeilen_h[2], [zelle(c.cell(name + "_Rest", c.run(rest_text, 7.5, c.MUTED), pad=(4, 0, 4, 0)), n)])
    z_summe = zeile(zeilen_h[3], [zelle(z) for z in summe_zellen])
    z_eti = etikett_zeile(name + "_E", kennung, technik, n)
    mitglieder = [kopf_mitglied(), gruppe_mitglied(name + "_G", gruppe, "=" + kg, True, c.topn(rang, deckel_n)),
                  fuss_mitglied(hidden_rest), fuss_mitglied(), fuss_mitglied()]
    norows, stil = keine_zeilen(leer_text)
    extra = "%s<DataSetName>%s</DataSetName>%s" % (norows, DS, c.filters(bedingung))
    voll = zeilen_h[0] + deckel_n * zeilen_h[1] + sum(zeilen_h[2:])          # Platz fuer Kopf, alle Zeilen, Rest, Summe, Etikett
    tab = tablix(name, spalten, [z_kopf, z_daten, z_rest, z_summe, z_eti], mitglieder, voll, extra=extra, stil=stil)
    items += c.rect(name + "_Feld", top + 1.45, left, w, voll + 0.05, tab)
    return items


@b.baustein("T090", "Matten nach Typ")
def t090(top, left, w):
    name = "RB_TbTyp"
    spalten = [1.9, 1.2, 1.6, 1.9, 2.2]
    kg = "Sum(%s)" % KG
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (KG, name, name)
    rest_zahl = 'CountDistinct(IIf(%s, Fields!Mattenname.Value, Nothing), "%s")' % (MATTE, DS)
    kopf = [kopfzelle(name + "_H1", "Typ"), kopfzelle(name + "_H2", "Stück", "Right"), kopfzelle(name + "_H3", "Fläche", "Right", "m²"),
            kopfzelle(name + "_H4", "Gewicht", "Right", "kg"), kopfzelle(name + "_H5", "")]
    daten = [c.cell(name + "_D1", c.run("=" + kurz("First(Fields!Mattenname.Value)", 10), 9.5, c.INK, c.F_SEMI), border_xml=ROW, pad=P0),
             c.cell(name + "_D2", c.run('=Format(Sum(%s), "N0")' % STUECK, 9.5, c.TEXT), "Right", border_xml=ROW, pad=P0),
             c.cell(name + "_D3", c.run('=Format(Sum(%s), "#,##0.0")' % FLAECHE, 9.5, c.TEXT), "Right", border_xml=ROW, pad=P0),
             c.cell(name + "_D4", c.run("=" + gewicht(kg), 9.5, c.INK, c.F_SEMI), "Right", border_xml=ROW, pad=P0),
             c.rect(name + "_D5", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, kg, maxi), border_xml=ROW)]
    summe = [c.cell(name + "_S1", c.run("Summe", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S2", c.run('=Format(Sum(%s), "N0")' % STUECK, 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S3", c.run('=Format(Sum(%s), "#,##0.0")' % FLAECHE, 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S4", c.run("=" + gewicht("Sum(%s)" % KG), 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S5", c.run("", 9), border_xml=SUMLINE)]
    rest = '=IIf(%s - %d = 1, "… und 1 weiterer Typ", "… und " & (%s - %d) & " weitere Typen")' % (rest_zahl, MAX_TYPEN, rest_zahl, MAX_TYPEN)
    return gruppentabelle(name, "T090", top, left, w, "Matten", "Matten nach Typ", spalten, "=Fields!Mattenname.Value", MATTE, MAX_TYPEN,
                          rest, rest_zahl, summe, daten, kopf,
                          "Tablix je Mattentyp, Deckel 5 (TopN), Zellenbalken", "Keine Matten im Teilbild.")


@b.baustein("T100", "Rundstahl nach Stahlgüte")
def t100(top, left, w):
    name = "RB_TbGuete"
    spalten = [1.8, 1.1, 2.2, 1.5, 2.2]          # Anteil 1,5 cm: "100 %" mit Reserve (1,2 cm schnitt im Fenster das % ab)
    kg = "Sum(%s)" % KG
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (KG, name, name)
    rest_zahl = 'CountDistinct(IIf(%s, Fields!Stahlguete.Value, Nothing), "%s")' % (STAB, DS)
    kopf = [kopfzelle(name + "_H1", "Güte"), kopfzelle(name + "_H2", "Pos.", "Right"), kopfzelle(name + "_H3", "Gewicht", "Right", "kg"),
            kopfzelle(name + "_H4", "Anteil", "Right"), kopfzelle(name + "_H5", "")]
    guete = 'IIf(Len(First(Fields!Stahlguete.Value)) = 0, "ohne Angabe", First(Fields!Stahlguete.Value))'
    daten = [c.cell(name + "_D1", c.run("=" + kurz(guete, 9), 9.5, c.INK, c.F_SEMI), border_xml=ROW, pad=P0),
             c.cell(name + "_D2", c.run('=Format(CountDistinct(Fields!Nr.Value), "N0")', 9.5, c.TEXT), "Right", border_xml=ROW, pad=P0),
             c.cell(name + "_D3", c.run("=" + gewicht(kg), 9.5, c.INK, c.F_SEMI), "Right", border_xml=ROW, pad=P0),
             c.cell(name + "_D4", c.run('=Format(%s, "0 %%")' % b.quote(kg, RUND_D), 9.5, c.TEXT), "Right", border_xml=ROW, pad=P0),
             c.rect(name + "_D5", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, kg, maxi), border_xml=ROW)]
    summe = [c.cell(name + "_S1", c.run("Summe", 9, c.INK, c.F_SEMI), border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S2", c.run('=Format(CountDistinct(Fields!Nr.Value), "N0")', 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S3", c.run("=" + gewicht("Sum(%s)" % KG), 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S4", c.run('=IIf(Sum(%s) > 0, "100 %%", "–")' % KG, 9, c.INK, c.F_SEMI), "Right", border_xml=SUMLINE, pad=(4, 0, 4, 0)),
             c.cell(name + "_S5", c.run("", 9), border_xml=SUMLINE)]
    rest = '=IIf(%s - %d = 1, "… und 1 weitere Güte", "… und " & (%s - %d) & " weitere Güten")' % (rest_zahl, MAX_GUETEN, rest_zahl, MAX_GUETEN)
    return gruppentabelle(name, "T100", top, left, w, "Rundstahl", "Rundstahl nach Stahlgüte", spalten, "=Fields!Stahlguete.Value", STAB,
                          MAX_GUETEN, rest, rest_zahl, summe, daten, kopf,
                          "Tablix je Stahlgüte, Deckel 5 (TopN), Zellenbalken", "Kein Rundstahl im Teilbild.")


# ---------------------------------------------------------------- T110 Stabliste, T120 Mattenliste (vollstaendig, fliessen ueber Seiten)
def titel_zeilen(name, label, titel, cols, legende=None, legende_ab=7):
    """Abschnittstitel als erste Zeile der Tabelle (statt freier Textboxen): er bleibt mit der ersten Datenzeile zusammen und steht nie
    allein am Seitenende. Er wiederholt sich mit den Spaltenkoepfen auf jeder Folgeseite (Allplan-Tablix: alle Kopfzeilen vor der
    Gruppe wiederholen oder keine). Liefert (Zeilen, Mitglieder)."""
    n = len(cols)
    linie = c.edge(["Bottom"], c.HAIR, "0.75pt")
    inhalt = c.para([c.run(label.upper() + "   ", 7, c.MUTED, c.F_SEMI), c.run(titel, 12, c.INK, c.F_SEMI)])
    titel_zelle = c.cell(name + "_T", inhalt, valign="Bottom", border_xml=linie, pad=(0, 0, 0, 3))
    if legende:
        z1 = zeile(0.8, [zelle(titel_zelle, legende_ab),
                         zelle(c.cell(name + "_Leg", legende, "Right", "Bottom", border_xml=linie, pad=(0, 0, 0, 4)), n - legende_ab)])
    else:
        z1 = zeile(0.8, [zelle(titel_zelle, n)])
    return [z1], [kopf_mitglied()]


def kl(zelle_xml, tooltip="Klick: in Allplan auf dieses Bauteil zoomen"):
    """Zelle anklickbar machen: Allplan zoomt aufs Bauteil der Zeile (Feld Nr)."""
    return b.klick(zelle_xml, tooltip=tooltip)


SUMME_H = 1.25      # Summenzeile der Listen: 0,6 Summen + zwei Zeilen Etikett
SORTIER = "(CDbl(Fields!Position.Value) + Val(Right(Fields!Nr.Value, 8)) / 1000000000000)"   # je Zeile eindeutig, nach Position


def summen_zeile(name, tab, cols, werte, kennung, technik):
    """Summenzeile der Listen als EIN Rechteck ueber alle Spalten: oben die Summen an ihren Spalten, darunter das Etikett und -
    nur bei Ausfuehrungen > 1 - das Gesamtgewicht. Die Zeile steht IN der Gruppe und ist nur bei der letzten Position sichtbar
    (gruppe_mit_summe): so haengt sie immer an der letzten Datenzeile. Als eigene Fusszeile (KeepWithGroup) rutschte sie im
    Test allein auf eine Folgeseite, das Etikett darunter in Allplan ebenso. Alle Summen tragen darum den Bereich der Tabelle (tab).
    werte: {Spaltenindex: (Inhalt, Ausrichtung, Anzahl Spalten)}."""
    b.KATALOG.append((b.SEITE_AKTUELL[0], kennung, technik))
    links = [sum(cols[:i]) for i in range(len(cols))]
    breite = sum(cols)
    inner = ""
    for i, (inhalt, align, span) in sorted(werte.items()):
        inner += c.text("%s_%d" % (name, i + 1), 0, links[i], sum(cols[i:i + span]) - 0.05, 0.6, inhalt, align, "Middle",
                        pad=(4, 0, 4, 0))
    mi, ma = 'Min(%s, "%s")' % (AUSF, tab), 'Max(%s, "%s")' % (AUSF, tab)
    eins = "%s = 1 And %s = 1" % (mi, ma)
    ausf_text = '=IIf(%s = %s, "× " & Format(%s, "N0") & " Ausführungen", "mit den Ausführungen je Position")' % (mi, ma, ma)
    gesamt_kg = 'Sum(%s, "%s")' % (KG, tab)
    inner += c.text(name + "_Ausf", 0.66, breite - 7.0, 7.0, 0.42,
                    c.para([c.run(ausf_text, 7.5, c.MUTED), c.run('="  =  " & ' + gewicht(gesamt_kg) + ' & " kg"', 8, c.INK, c.F_SEMI)],
                           "Right"), "Right", "Top", pad=P0, hidden="=" + eins)
    if b.ETIKETT_AN[0]:
        inner += c.text(name + "_E", 0.66, 0, breite - 7.2, 0.4,
                        c.para([c.run(kennung + "  ", 6.5, c.BLUE, c.F_SEMI), c.run(technik, 6.5, c.FAINT)]), valign="Top", pad=(4, 2, 0, 0))
    return zeile(SUMME_H, [zelle(c.rect(name, None, 0, 0, 0, inner, border_xml=SUMLINE), len(cols))])


def gruppe_mit_summe(name, tab, ausdruck, schluessel):
    """Gruppe der Listen mit zwei Zeilen je Gruppe: Datenzeile und Summenzeile. Die Summenzeile ist nur bei der letzten Gruppe
    sichtbar (groesster Sortierschluessel); KeepTogether haelt Datenzeile und Summe auf einer Seite. schluessel: je Zeile
    eindeutig steigender Sortierwert, die Gruppe sortiert nach seinem Kleinsten."""
    rang = "Min(%s)" % schluessel
    letzte = '=%s < Max(Min(%s, "%s"), "%s")' % (rang, schluessel, name, tab)
    return ('<TablixMember><Group Name="%s"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions></Group>'
            "<SortExpressions><SortExpression><Value>=%s</Value></SortExpression></SortExpressions>"
            "<TablixMembers><TablixMember/><TablixMember><Visibility><Hidden>%s</Hidden></Visibility></TablixMember></TablixMembers>"
            "<KeepTogether>true</KeepTogether></TablixMember>" % (name, c.esc(ausdruck), c.esc(rang), c.esc(letzte)))


@b.baustein("T110", "Stabliste")
def t110(top, left, w):
    """Alle Rundstahl-Positionen (je Nr eine Zeile, auch wenn Allplan sie in mehreren Zeilen liefert): Pos, Stueck, Durchmesser,
    Guete, Laengen, kg, Form, Biegeform-Bild, Datenbalken kg. Werte je Ausfuehrung wie Allplans Stabliste. Ohne Deckel."""
    name = "RB_TbStab"
    cols = [2.8, 1.5, 0.8, 1.2, 1.6, 0.4, 1.9, 1.9, 1.15, 3.0, 1.75]
    legende = c.para([c.run("■ ", 8, C_GERADE, b.SYMBOL), c.run("gerade   ", 7.5, c.MUTED),
                      c.run("■ ", 8, C_GEBOGEN, b.SYMBOL), c.run("gebogen   ", 7.5, c.MUTED),
                      c.run("■ ", 8, C_UEBER, b.SYMBOL), c.run("Überlänge", 7.5, c.MUTED)], "Right")
    titel_z, titel_m = titel_zeilen(name, "Stabliste", "Alle Rundstahl-Positionen", cols, legende, 7)
    lfdm_g = "Max(IIf(%s, 1, 0)) = 1" % LFDM                                # die Position ist Meterware
    ueber_z = "Max(IIf(%s, 1, 0)) = 1" % UEBER
    gebogen_z = "Max(CInt(Fields!Gebogen.Value)) = 1"
    stueck_g = "IIf(%s, 1.0, Sum(%s))" % (lfdm_g, ANZ)                       # Meterware: 1 wie in Allplans Stabliste
    einzel_g = 'IIf(%s, "lfdm", Format(Sum(%s) / IIf(Sum(%s) < 1, 1.0, Sum(%s)), "N2"))' % (lfdm_g, GESL, ANZ, ANZ)
    stueck_s = 'Sum(IIf(%s, 0.0, %s), "%s") + %s' % (LFDM, ANZ, name, pos_zahl(LFDM, "Fields!Nr.Value", name))
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (KG1, name, name)
    farbe = '=IIf(%s, "%s", IIf(%s, "%s", "%s"))' % (ueber_z, C_UEBER, gebogen_z, C_GEBOGEN, C_GERADE)
    kopf = [kopfzelle(name + "_H1", "Pos", None, "Bauteil"), kopfzelle(name + "_H2", "Stück", "Right"),
            kopfzelle(name + "_H3", "Ø", "Right", "mm"), kopfzelle(name + "_H4", "Güte"),
            kopfzelle(name + "_H5", "Länge", "Right", "einzeln m"), kopfzelle(name + "_H6", ""),
            kopfzelle(name + "_H7", "Länge", "Right", "gesamt m"), kopfzelle(name + "_H8", "Gewicht", "Right", "kg"),
            kopfzelle(name + "_H9", "Form", "Center", "ISO"), kopfzelle(name + "_H10", "Biegeform"), kopfzelle(name + "_H11", "")]
    pos = c.text(name + "_D1", None, 0, 0, 0, [
        c.para([c.run("=Fields!Position.Value", 9.5, c.INK, c.F_SEMI)]),
        c.para([c.run("=" + kurz("Fields!Bauteil.Value", 18), 7, c.MUTED)])], valign="Middle", border_xml=ROW, pad=(4, 1, 2, 1))
    zelle_d = lambda nr, inh, al=None: kl(c.cell(name + "_D%d" % nr, inh, al, border_xml=ROW, pad=(4, 1, 4, 1)))
    bild = c.rect(name + "_D10", None, 0, 0, 0,
                  c.image(name + "_Bild", 0.06, 0.1, 2.8, 0.98, "=Fields!Bild.Value", mime="image/jpeg", sizing="FitProportional",
                          action=b.ZOOM), border_xml=ROW)
    daten = [kl(pos),
             zelle_d(2, c.run('=Format(%s, "N0")' % stueck_g, 9, c.TEXT), "Right"),
             zelle_d(3, c.run('=Format(%s, "0.##")' % DM, 9, c.TEXT), "Right"),
             zelle_d(4, c.run("=" + kurz("Fields!Stahlguete.Value", 7), 8.5, c.MUTED)),
             zelle_d(5, c.run("=" + einzel_g, 9, c.TEXT), "Right"),
             c.cell(name + "_D6", c.run('=IIf(%s, "▲", "")' % ueber_z, 8, c.AMBER_TEXT, b.SYMBOL), "Left", border_xml=ROW, pad=(2, 1, 0, 1)),
             zelle_d(7, c.run('=Format(Sum(%s), "#,##0.0")' % GESL, 9, c.TEXT), "Right"),
             zelle_d(8, c.run('=Format(Sum(%s), "#,##0.0")' % KG1, 9, c.INK, c.F_SEMI), "Right"),
             zelle_d(9, c.run("=Fields!Biegeform.Value", 8.5, '=IIf(%s, "%s", "%s")' % (GEBOGEN, c.BLUE, c.FAINT), c.F_SEMI), "Center"),
             bild,
             c.rect(name + "_D11", None, 0, 0, 0, balken_zelle(name + "_Ch", farbe, "Sum(%s)" % KG1, maxi), border_xml=ROW)]
    summe = summen_zeile(name + "_S", name, cols, {
        0: (c.run("Summe", 9, c.INK, c.F_SEMI), None, 1),
        1: (c.run('=Format(%s, "N0")' % stueck_s, 9, c.INK, c.F_SEMI), "Right", 1),
        6: (c.run('=Format(Sum(%s, "%s"), "#,##0.0")' % (GESL, name), 9, c.INK, c.F_SEMI), "Right", 1),
        7: (c.run('=Format(Sum(%s, "%s"), "#,##0.0")' % (KG1, name), 9, c.INK, c.F_SEMI), "Right", 1)},
        "T110", "Zeile je Nr; kg = Gesamtlänge × kg/m; Meterware als lfdm; ohne Deckel")
    mitglieder = titel_m + [kopf_mitglied(), gruppe_mit_summe(name + "_G", name, "=Fields!Nr.Value", SORTIER)]
    norows, stil = keine_zeilen("Stabliste: keine Rundstahl-Positionen im Teilbild.")
    hoehe = 0.8 + 0.9 + 1.1 + SUMME_H
    zeilen = titel_z + [zeile(0.9, [zelle(z) for z in kopf]), zeile(1.1, [zelle(z) for z in daten]), summe]
    extra = "%s<DataSetName>%s</DataSetName>%s" % (norows, DS, c.filters(STAB))
    items = tablix(name, cols, zeilen, mitglieder, hoehe, extra=extra, stil=stil, top=top, left=left)
    return items


T120_H = 0.8 + 0.85 + 0.6 + SUMME_H     # Summe der deklarierten Zeilen: wachsen die Matten, schiebt das Wachstum die Stabliste nach unten
# (eine kleinere deklarierte Hoehe schiebt nicht: die Listen ueberlappen dann - ausprobiert)
# Eine Zeile je Position, Mattentyp und Mass (wie Allplans Mattenstahlliste): jede verlegte Matte hat ihre eigene Nr
MATTE_ZEILE = ('%s & "|" & Fields!Mattenname.Value & "|" & Format(CDbl(Fields!Einzellaenge.Value), "0.000") & "|" & '
               'Format(CDbl(Fields!MattenBreite.Value), "0.000")' % MATTE_POS)


@b.baustein("T120", "Mattenliste")
def t120(top, left, w):
    """Alle Matten-Positionen, je Position/Typ/Mass eine Zeile mit summierter Stueckzahl: Pos, Typ, Bauteil, Stueck,
    Laenge x Breite, m2, kg, Datenbalken. Werte je Ausfuehrung wie Allplans Mattenstahlliste. Ohne Deckel; die Stabliste steht darunter."""
    name = "RB_TbMatte"
    cols = [1.2, 2.3, 3.7, 1.3, 3.2, 1.8, 2.0, 2.5]
    titel_z, titel_m = titel_zeilen(name, "Mattenliste", "Alle Matten-Positionen", cols)
    maxi = 'Max(Sum(%s, "%s_G"), "%s")' % (KG1, name, name)
    kopf = [kopfzelle(name + "_H1", "Pos"), kopfzelle(name + "_H2", "Typ"), kopfzelle(name + "_H3", "Bauteil"),
            kopfzelle(name + "_H4", "Stück", "Right"), kopfzelle(name + "_H5", "Länge × Breite", "Right", "m"),
            kopfzelle(name + "_H6", "Fläche", "Right", "m²"), kopfzelle(name + "_H7", "Gewicht", "Right", "kg"), kopfzelle(name + "_H8", "")]
    zelle_d = lambda nr, inh, al=None: kl(c.cell(name + "_D%d" % nr, inh, al, border_xml=ROW, pad=P0))
    daten = [zelle_d(1, c.run("=Fields!Position.Value", 9, c.INK, c.F_SEMI), "Left"),
             zelle_d(2, c.run("=" + kurz("Fields!Mattenname.Value", 10), 9, c.INK)),
             zelle_d(3, c.run("=" + kurz("Fields!Bauteil.Value", 22), 7.5, c.MUTED)),
             zelle_d(4, c.run('=Format(Sum(%s), "N0")' % ANZ, 9, c.TEXT), "Right"),
             zelle_d(5, c.run('=Format(CDbl(Fields!Einzellaenge.Value), "N2") & " × " & Format(CDbl(Fields!MattenBreite.Value), "N2")', 9, c.TEXT),
                     "Right"),
             zelle_d(6, c.run('=Format(Sum(%s), "#,##0.0")' % FLAECHE1, 9, c.TEXT), "Right"),
             zelle_d(7, c.run('=Format(Sum(%s), "#,##0.0")' % KG1, 9, c.INK, c.F_SEMI), "Right"),
             c.rect(name + "_D8", None, 0, 0, 0, balken_zelle(name + "_Ch", c.BLUE, "Sum(%s)" % KG1, maxi), border_xml=ROW)]
    summe = summen_zeile(name + "_S", name, cols, {
        0: (c.run("Summe", 9, c.INK, c.F_SEMI), None, 2),
        3: (c.run('=Format(Sum(%s, "%s"), "N0")' % (ANZ, name), 9, c.INK, c.F_SEMI), "Right", 1),
        5: (c.run('=Format(Sum(%s, "%s"), "#,##0.0")' % (FLAECHE1, name), 9, c.INK, c.F_SEMI), "Right", 1),
        6: (c.run('=Format(Sum(%s, "%s"), "#,##0.0")' % (KG1, name), 9, c.INK, c.F_SEMI), "Right", 1)},
        "T120", "Zeile je Position, Typ und Maß; Stück summiert; ohne Deckel")
    mitglieder = titel_m + [kopf_mitglied(), gruppe_mit_summe(name + "_G", name, "=" + MATTE_ZEILE, SORTIER)]
    norows, stil = keine_zeilen("Mattenliste: keine Matten im Teilbild.")
    zeilen = titel_z + [zeile(0.85, [zelle(z) for z in kopf]), zeile(0.6, [zelle(z) for z in daten]), summe]
    extra = "%s<DataSetName>%s</DataSetName>%s" % (norows, DS, c.filters(MATTE))
    items = tablix(name, cols, zeilen, mitglieder, T120_H, extra=extra, stil=stil, top=top, left=left)
    return items


# ---------------------------------------------------------------- Seiten
def seite1():
    x0, w = c.INSET, c.CONTENT_W
    items = band()
    items += k080(4.95, x0, w)
    items += u050(7.85, x0, w)
    hw = 8.8
    items += d170(11.2, x0, hw)
    items += d180(11.2, x0 + hw + 0.4, hw)
    items += d190(15.95, x0 + hw + 0.4, hw)
    items += t090(21.0, x0, hw)
    items += t100(21.0, x0 + hw + 0.4, hw)
    return items


def seite2():
    return kopf2() + t120(3.3, c.INSET, c.CONTENT_W) + t110(3.3 + T120_H + 0.4, c.INSET, c.CONTENT_W)


SEITEN = [("Bewehrung im Überblick", seite1), ("Matten- und Stabliste", seite2)]


def build():
    b.SEITE_AKTUELL[0] = "build_bewehrung"
    pages = [fn() for _t, fn in SEITEN]
    xml = c.report(pages, [c.dataset(DS, QUERY, FIELDS)], extra_params=PARAMS, footer_xml=b.fuss(), code=b.CODE,
                   labels=[t for t, _f in SEITEN])
    # Die letzte Seite traegt die Listen und darf ueber Seiten laufen: ihr Blatt darf nicht zusammengehalten werden
    ende = "</ReportItems><KeepTogether>true</KeepTogether><DocumentMapLabel>%s</DocumentMapLabel>" % c.esc(SEITEN[-1][0])
    if xml.count(ende) != 1:
        sys.exit("FEHLER: die letzte Seite wurde im XML nicht gefunden")
    xml = xml.replace(ende, ende.replace("<KeepTogether>true", "<KeepTogether>false"))
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, "Report_Master_Bewehrung.rdlc")
    c.save(ziel, xml)
    return ziel


if __name__ == "__main__":
    b.aufruf_pruefen(__doc__, {"--render", "--daten"})
    ziel = build()
    print(ziel)
    if "--render" in sys.argv:
        os.makedirs(AUS, exist_ok=True)
        c.rendern(ziel, JSON, AUS, vollzugriff=True)   # volle Rechte: Code.Schrift liest die installierten Schriften (sonst Ersatzschrift Segoe UI)
