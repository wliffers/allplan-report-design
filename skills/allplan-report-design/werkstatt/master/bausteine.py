# -*- coding: utf-8 -*-
"""Daten und wiederverwendbare Gestaltungs-Bausteine des Master-Reports.

Jede Seite (seiten/sNN_*.py) setzt sich aus diesen Bausteinen zusammen. Wer einen neuen Baustein
braucht, der auf mehreren Seiten vorkommt, legt ihn hier an; Einmaliges bleibt in der Seite.
"""
import os
import re
import sys

import core as c
import viz as v

# ---------------------------------------------------------------- Daten
QUERY = """SELECT
       @498@[Name=Objekt],
       [Name=ObjNr|f=@OBJ@],
       @507@[Name=Bezeichnung],
       @506@[Name=Funktion],
       @508@[Name=Material],
       @209@[Name=Gewerk],
       @220@[Name=Laenge],
       @221@[Name=Dicke],
       @222@[Name=Hoehe],
       @229@[Name=Flaeche],
       @223@[Name=Volumen],
       @10@[Name=Nr],
       @205@[Name=Bild|Projection=9|Width=60|Height=40|Hidden=5|GText=HD_CENTERMIDDLE]
FROM [MODEL_DATA, Filter=@OBJ@.eq.1.or.@OBJ@.eq.3.or.@OBJ@.eq.4.or.@OBJ@.eq.6.or.@OBJ@.eq.704.or.@OBJ@.eq.61.or.@OBJ@.eq.991.or.@OBJ@.eq.992]
"""
FIELDS = [("Objekt", "String"), ("ObjNr", "String"), ("Bezeichnung", "String"), ("Funktion", "String"),
          ("Material", "String"), ("Gewerk", "String"), ("Laenge", "Double"), ("Dicke", "Double"),
          ("Hoehe", "Double"), ("Flaeche", "Double"), ("Volumen", "Double"), ("Nr", "String"), ("Bild", "Byte[]")]


def ist(*nummern):
    """Bedingung: Zeile gehoert zu einer der Objektnummern (@OBJ@)."""
    return "(" + " Or ".join("Val(Fields!ObjNr.Value)=%d" % n for n in nummern) + ")"


ROHBAU = ist(1, 3, 4, 6, 704)
WAND, RAUM, FENSTER, TUER = ist(1), ist(61), ist(991), ist(992)
MIT_MATERIAL = '(%s And Fields!Material.Value <> "")' % ROHBAU


def summe(feld, bedingung, scope=None):
    return "Sum(IIf(%s, CDbl(Fields!%s.Value), 0.0)%s)" % (bedingung, feld, ', "%s"' % scope if scope else "")


def anzahl(bedingung, scope=None):
    return "Sum(IIf(%s, 1, 0)%s)" % (bedingung, ', "%s"' % scope if scope else "")


def raw(expr):
    """Ausdruck, der bereits XML-Entitaeten enthaelt, vor doppeltem Maskieren schuetzen."""
    return expr.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


# Datenfest: Diese Ausdruecke haengen nicht an den Namen eines bestimmten Projekts.
MATGRUPPE = "Code.MatArt(Fields!Material.Value)"          # Materialgruppe am Wortstamm: Beton, Mauerwerk, Daemmung ...
MAT_FARBE = "=Code.MatFarbe(Fields!Material.Value)"       # Farbe der Materialgruppe (c.MATERIALGRUPPE)
ART = "Code.Art(Fields!ObjNr.Value)"                      # Bauteilart aus der Objektnummer: Wand, Stuetze, Decke ...
IST_BETON = '(Code.MatArt(Fields!Material.Value) = "Beton")'
IST_VERKEHR = "Code.IstVerkehr(Fields!Funktion.Value)"    # Flur, Diele, Treppe, Gang, Foyer ...


def in_cell(xml):
    """Lageangaben entfernen: Inhalt einer Tabellenzelle traegt keine Position."""
    return re.sub(r"<Top>[\d.]+cm</Top><Left>[\d.]+cm</Left><Height>[\d.]+cm</Height><Width>[\d.]+cm</Width>", "", xml)


# ---------------------------------------------------------------- Aufruf der Bauskripte
def aufruf_pruefen(doc, schalter):
    """Erste Zeile von `if __name__ == "__main__":` in jedem Bauskript. -h / --help zeigt den Aufruftext (die erste Zeile der
    Moduldoku und die Aufrufliste "python ...") und beendet das Skript, ohne etwas zu bauen; ein unbekannter
    Schalter wird gemeldet (Abbruch mit Meldung) statt still ignoriert. schalter: erlaubte Namen ohne Wert, z. B. {"--render", "--daten"}
    (--daten=<name> und --nur=<n> sind damit gemeint)."""
    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        zeilen = (doc or "").strip().split("\n")
        aufruf = []
        lesen = False
        for zeile in zeilen[1:]:
            if zeile.lstrip().startswith("python "):
                lesen = True
            elif lesen and not zeile.strip():
                break
            if lesen:
                aufruf.append(zeile.rstrip())
        print("\n".join([zeilen[0], ""] + aufruf))
        sys.exit(0)
    for a in argv:
        if a.startswith("-") and a.split("=", 1)[0] not in schalter:
            sys.exit("Unbekannter Schalter %s. Aufruf zeigt: %s --help" % (a, sys.argv[0]))


# ---------------------------------------------------------------- Bausteine
def overline(name, top, left, w, label, title, titel_w=None):
    """Abschnittskopf: Etikett in Versalien (halbfett, leise), darunter die Ueberschrift, darunter eine Haarlinie.
    titel_w: Breite der Ueberschrift, wenn rechts neben ihr ein weiteres Feld steht (Felder duerfen sich nicht ueberlappen)."""
    return (c.text(name + "_o", top, left, w, 0.35, c.run(label.upper(), 7, c.MUTED, c.F_SEMI))
            + c.text(name + "_t", top + 0.4, left, titel_w or w, 0.7, c.run(title, 13, c.INK, c.F_SEMI))
            + c.line(name + "_l", top + 1.18, left, w))


def rang_titel(gruppen, deckel, vor, nach, einzahl, ohne):
    """Ausdruck fuer die Ueberschrift einer Liste mit Deckel: nennt die Zahl der tatsaechlich gezeigten Zeilen (hoechstens
    der Deckel), nicht eine feste Zahl. gruppen: Ausdruck mit der Zahl der Gruppen, z. B. CountDistinct(IIf(<Bedingung>, <Feld>, Nothing));
    ergibt "<vor><n><nach>", bei einer Gruppe <einzahl>, bei keiner <ohne>."""
    return ('=IIf(%s = 1, "%s", IIf(%s = 0, "%s", "%s" & IIf(%s < %d, %s, %d) & "%s"))'
            % (gruppen, einzahl, gruppen, ohne, vor, gruppen, deckel, gruppen, deckel, nach))


def kpi(name, top, left, w, value_expr, fmt, unit, label, note):
    """Kennzahl-Kachel: grosse Zahl, Einheit, Beschriftung, Fussnote."""
    inner = (c.rect(name + "_a", 0, 0, w, 0.09, bg=c.BLUE)
             + c.text(name + "_v", 0.42, 0.32, w - 0.4, 1.05,
                      c.para([c.run("=" + value_expr, 22, c.INK, c.F_ZAHL, fmt=fmt),
                              c.run(" " + unit if unit else "", 10, c.MUTED, c.F)]), valign="Bottom")
             + c.text(name + "_l", 1.5, 0.32, w - 0.4, 0.37, c.run(label.upper(), 7, c.TEXT, c.F_SEMI))
             + c.text(name + "_n", 1.92, 0.32, w - 0.4, 0.4, c.run(note, 7, c.MUTED, c.F)))
    return c.rect(name, top, left, w, 2.55, inner, bg=c.SURFACE)


def quote(zaehler, nenner):
    """Anteil 0..1, sicher gegen Division durch null."""
    return "IIf(%s = 0, 0.0, %s / IIf(%s = 0, 1.0, %s))" % (nenner, zaehler, nenner, nenner)


def fortschritt(name, top, left, w, anteil, farbe=c.BLUE, h=0.2):
    """Schmaler Fortschrittsbalken 0..100 %: gefuellter Teil in Farbe, Rest als helle Spur."""
    achse = v.axis("Primary", visible=False, minimum="0", maximum="1")
    return v.chart(
        name, top, left, w, h,
        [v.S(name + "a", {"Y": "=" + anteil}, typ="Bar", sub="Stacked", color=farbe, custom_xml=v.custom(PointWidth="1")),
         v.S(name + "b", {"Y": "=1 - (%s)" % anteil}, typ="Bar", sub="Stacked", color=c.HAIR, custom_xml=v.custom(PointWidth="1"))],
        [], nomember=True, names=["a", "b"],
        areas=v.area(cat_axes=[v.axis("Primary", visible=False)], val_axes=[achse], pos=(0, 0, 100, 100), inner=(0, 0, 100, 100)))


def kennwert(name, top, left, w, label, note, anteil, farbe=c.BLUE):
    """Kennwert-Zeile: Beschriftung links, Prozentzahl rechts, Fortschrittsbalken darunter."""
    return (c.text(name + "_l", top, left, w - 2.2, 0.42, c.run(label, 9.5, c.INK, c.F_SEMI))
            + c.text(name + "_n", top + 0.47, left, w - 2.2, 0.36, c.run(note, 7.5, c.MUTED))
            + c.text(name + "_v", top, left + w - 2.2, 2.2, 0.83, c.run("=" + anteil, 17, c.INK, c.F_ZAHL, fmt="0 %"),
                     align="Right", valign="Bottom")
            + fortschritt(name + "_b", top + 0.95, left, w, anteil, farbe))


def karten(name, top, left, breite, karte_w, luecke, bedingung, gruppe, typ_expr, sortierung=None):
    """Bildkarten nebeneinander: je Gruppe eine Karte mit Bauteilbild aus Allplan, Name und Anzahl.
    sortierung: Ausdruck, nach dem die Karten absteigend stehen (ohne Angabe: alphabetisch nach Gruppenname)."""
    rahmen = "<Border><Color>%s</Color><Style>Solid</Style><Width>0.75pt</Width></Border>" % c.HAIR
    bild = ('<Image Name="%s_Bild"><Source>Database</Source><Value>=First(Fields!Bild.Value)</Value><MIMEType>image/jpeg</MIMEType>'
            "<Sizing>FitProportional</Sizing><ActionInfo><Actions><Action><BookmarkLink>=\"Zoom:\" + First(Fields!Nr.Value) + \",Mark:\" + First(Fields!Nr.Value)</BookmarkLink></Action></Actions></ActionInfo>"
            "<ToolTip>Klick: in Allplan auf ein Bauteil dieses Typs zoomen</ToolTip>"
            "<Style>%s<PaddingLeft>6pt</PaddingLeft><PaddingRight>6pt</PaddingRight>"
            "<PaddingTop>6pt</PaddingTop><PaddingBottom>6pt</PaddingBottom></Style></Image>" % (name, rahmen))
    zeilen = [
        (1.75, bild, c.cell(name + "_x1", c.run("", 6))),
        (0.85, c.cell(name + "_Name", c.run("=" + gruppe, 7.5, c.INK, c.F_SEMI), valign="Top", pad=(1, 4, 1, 0)),
         c.cell(name + "_x2", c.run("", 6))),
        (0.42, c.cell(name + "_Anz", c.para([c.run("=CountRows()", 8, c.BLUE, c.F_SEMI), c.run(' =" × " & %s' % typ_expr, 8, c.MUTED)]),
                      valign="Top", pad=(1, 0, 1, 0)),
         c.cell(name + "_x3", c.run("", 6))),
    ]
    xml = '<Tablix Name="%s"><TablixBody><TablixColumns><TablixColumn><Width>%s</Width></TablixColumn><TablixColumn><Width>%s</Width></TablixColumn></TablixColumns><TablixRows>' % (
        name, c.cm(karte_w), c.cm(luecke))
    for hoehe, a, b in zeilen:
        xml += ("<TablixRow><Height>%s</Height><TablixCells><TablixCell><CellContents>%s</CellContents></TablixCell>"
                "<TablixCell><CellContents>%s</CellContents></TablixCell></TablixCells></TablixRow>" % (c.cm(hoehe), a, b))
    xml += "</TablixRows></TablixBody>"
    xml += ('<TablixColumnHierarchy><TablixMembers><TablixMember><Group Name="%s_G"><GroupExpressions><GroupExpression>=%s</GroupExpression>'
            "</GroupExpressions></Group><SortExpressions><SortExpression><Value>=%s</Value>%s</SortExpression></SortExpressions>"
            "<TablixMembers><TablixMember/><TablixMember/></TablixMembers></TablixMember></TablixMembers></TablixColumnHierarchy>"
            % (name, c.esc(gruppe), c.esc(sortierung or gruppe), "<Direction>Descending</Direction>" if sortierung else ""))
    xml += "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>" % ("<TablixMember/>" * len(zeilen))
    xml += "<DataSetName>AllplanReport</DataSetName>" + c.filters(bedingung)
    hoehe = sum(z[0] for z in zeilen)
    xml += "<Top>0cm</Top><Left>0cm</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>" % (
        c.cm(hoehe), c.cm(karte_w + luecke))
    return c.rect(name + "_Feld", top, left, breite, hoehe + 0.1, xml)


_SCHRIFTEN = {}
# Schriftdatei je Familienname des Designs (Windows-Schriftordner); unbekannte Familie: schaetzen
_DATEIEN = {"Roboto": "Roboto-Regular.ttf", "Roboto Light": "Roboto-Light.ttf", "Roboto Medium": "Roboto-Medium.ttf",
            "Roboto Black": "Roboto-Black.ttf", "Segoe UI": "segoeui.ttf", "Segoe UI Light": "segoeuil.ttf",
            "Segoe UI Semibold": "seguisb.ttf"}


def _schrift(datei):
    """Die Hausschrift aus dem Windows-Schriftordner (PIL), sonst None: dann schaetzt textbreite()."""
    if datei not in _SCHRIFTEN:
        try:
            from PIL import ImageFont
            _SCHRIFTEN[datei] = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", datei), 1000)
        except (ImportError, OSError):
            _SCHRIFTEN[datei] = None
    return _SCHRIFTEN[datei]


def textbreite(text, pt, leicht=False):
    """Breite eines Textes in cm in der Hausschrift (Regular; mit leicht=True die leichte Schrift des Designs, nur fuer Altlasten). Gemessen mit der Schrift, wenn sie da ist
    (PIL, Windows), sonst geschaetzt aus schmalen, normalen, grossen und breiten Zeichen (liegt bei Titeln rund 5 % darueber)."""
    schrift = _schrift(_DATEIEN.get(c.DESIGN.schrift["leicht" if leicht else "normal"], ""))
    if schrift is not None:
        return schrift.getlength(text) / 1000.0 * pt / 72 * 2.54
    em = 0.0
    for ch in text:
        if ch in " ilj.,:;'!|tfI-":
            em += 0.27
        elif ch in "mwMW":
            em += 0.85
        elif ch.isupper():
            em += 0.62
        else:
            em += 0.52
    return em * pt / 72 * 2.54


def titelbreite(titel, untertitel, breite):
    """Breite des Titelfelds im Folgekopf (19 pt). Der Titel bekommt 15 % Reserve (ein uebersetzter Titel darf etwas
    laenger sein), der Untertitel (8,5 pt, rechtsbuendig) den Rest der Zeile - nie weniger, als er selbst braucht plus 5 %
    Reserve (gemessen: so kleine Schrift setzt das Report-Fenster bis 3 % BREITER als das PDF, sonst bricht er um). Die
    englischen Untertitel sind teils 40 % laenger als die deutschen: darum bekommt der Untertitel alles, was der Titel
    nicht braucht. Ohne festen Untertitel (ein Ausdruck) bekommt der Titel seine Breite plus 2 cm."""
    roh = textbreite(titel, 19)
    if untertitel is None:
        return round(min(roh * 1.03 + 2.15, breite - 4.0), 2)
    return round(min(roh * 1.15 + 0.3, breite - 0.1 - textbreite(untertitel, 8.5) * 1.05), 2)


def folgekopf(rect_name, p, over, titel, sub_run, top=0, label=None, untertitel_text=None):
    """Schmales randloses Band mit Kapitelzeile, Titel und rechtsbuendigem Untertitel (Folgeseiten und Begleit-Reports).
    Titel und Untertitel stehen nebeneinander mit getrennten Breiten (das Report-Fenster schiebt Felder weg, die sich
    ueberlappen): der Titel bekommt, was er braucht, der Untertitel den Rest der Zeile. p: Namensvorsatz der Felder
    (p + "Akzent", "Over", "Titel", "Sub"); sub_run: der Textlauf (c.run) des Untertitels; untertitel_text: sein
    Text (feste Texte), damit der Titel die Breite bekommt, die der Untertitel uebrig laesst."""
    x0, w = c.INSET, c.CONTENT_W
    titel_w = titelbreite(titel, untertitel_text, w)
    sub_x = round(titel_w + 0.1, 2)
    # Roboto laeuft breiter als die bisherige Schrift: reicht der Platz nicht fuer 19 pt plus 5 % Reserve, schrumpft der Titel
    roh = textbreite(titel, 19)
    groesse = 19 if roh * 1.05 <= titel_w else round(max(16.0, 19 * titel_w / (roh * 1.05)), 1)
    inner = (c.rect(p + "Akzent", 0.62, x0, 0.9, 0.08, bg=c.AKZENT)
             + c.text(p + "Over", 0.8, x0, 12, 0.3, c.run(over, 7, c.AKZENT_DUNKEL, c.F_SEMI))
             + c.text(p + "Titel", 1.15, x0, titel_w, 0.95, c.run(titel, groesse, c.WHITE, c.F))
             + c.text(p + "Sub", 1.3, x0 + sub_x, w - sub_x, 0.6, sub_run, align="Right", valign="Bottom"))
    return c.rect(rect_name, top, 0, c.PAGE_W, 2.5, inner, bg=c.NAVY, label=label)


def seitenkopf(nr, titel, untertitel):
    """Kopf der Folgeseiten: schmales randloses Band mit Kapitelnummer, Titel und Untertitel."""
    p = "S%dKopf" % nr
    return folgekopf(p, p, "REPORT MASTER  ·  KAPITEL %d" % nr, titel, c.run(untertitel, 8.5, c.AUF_NAVY), untertitel_text=untertitel)


# Symbolschrift: Roboto hat ■ ● ▲ ▼ ✓ nicht (kein Zeichen im Bild). Nur fuer diese Zeichen, nie fuer Text.
SYMBOL = "Segoe UI Symbol"

KATALOG = []          # (Seite, Kennung, Technik) - fuellt sich beim Bauen, daraus entsteht das Bausteinverzeichnis
SEITE_AKTUELL = [""]  # setzt build_master.py vor jeder Seite
REGISTER = {}         # Kennung -> (Name, Modul, Funktion): jeder Baustein ist eine eigene Funktion


def baustein(kennung, name):
    """Meldet eine Funktion als Baustein an. Die Kennung (z. B. "D030") ist der Name, unter dem Anwender,
    Agent und Skill ueber den Baustein reden; sie steht sichtbar im Etikett unter dem Schaustueck.

        @b.baustein("D030", "Fläche je Bauteilart")
        def d030(top, left, w):
            ...Abschnittskopf, Inhalt, Etikett...
            return xml

    Die Funktion nimmt mindestens (top, left, w) und liefert das XML des ganzen Blocks."""
    def anmelden(funktion):
        REGISTER[kennung] = (name, funktion.__module__, funktion.__name__)
        return funktion
    return anmelden


ETIKETT_AN = [True]   # build_auswahl.py --ohne-etikett schaltet die Unterzeilen fuer Kunden-Reports ab


def etikett(name, top, left, w, kennung, text, h=0.4):
    """Kleine Unterzeile unter einem Schaustueck: Kennung des Bausteins und die Technik dahinter.
    h: Hoehe; stehen zwei Etiketten untereinander, 0.3 und 0.35 Abstand (sie duerfen sich nicht ueberlappen)."""
    KATALOG.append((SEITE_AKTUELL[0], kennung.strip(), text))
    if not ETIKETT_AN[0]:
        return ""
    return c.text(name, top, left, w, h,
                  c.para([c.run(kennung + "  ", 6.5, c.BLUE, c.F_SEMI), c.run(text, 6.5, c.FAINT)]))


# ---------------------------------------------------------------- Eingebettete Bilder
# Die PNG aus master/bilder stecken in der .rdlc (kein Dateizugriff noetig). Auswahl per Ausdruck (Muster: s06_bilder.MUSTER_NAME):
ICON = ("=Switch(" + ", ".join('Val(Fields!ObjNr.Value)=%d, "icon_%s"' % (nr, name) for nr, name in [
    (1, "wand"), (3, "stuetze"), (4, "decke"), (6, "unterzug"), (704, "bodenplatte"), (61, "raum"), (991, "fenster"),
    (992, "tuer")]) + ', True, "icon_wand")')


def bild_eingebettet(name, top, left, w, h, ausdruck_oder_name, sizing="FitProportional"):
    """Eingebettetes Bild: fester Name ("icon_wand") oder Ausdruck (ICON)."""
    return c.image(name, top, left, w, h, ausdruck_oder_name, source="Embedded", sizing=sizing)


# ---------------------------------------------------------------- Bedienung
# Stellschrauben des Anwenders (Allplan-Report-Fenster, Gruppe "Benutzerinteraktion").
PREISE = [("Beton bewehrt", "Preis_Beton", 185), ("Mauerwerk", "Preis_Mauerwerk", 140),
          ("Dämmung", "Preis_Daemmung", 95), ("Gipskarton", "Preis_Gipskarton", 60)]
PARAMS = ("".join(c.parameter(name, "Float", wert, "Einheitspreis %s in EUR je m³" % material) for material, name, wert in PREISE)
          + c.parameter("Tuer_Mindestbreite", "Float", "0.9", "Mindestbreite Tür in m (barrierefrei)")
          + c.parameter("Ziel_Fensteranteil", "Float", "20", "Zielwert Fensterflächenanteil in Prozent")
          + c.parameter("Zeige_Details", "Boolean", "false", "Einzelbauteile aufgeklappt zeigen"))
# Preis je m3 nach Materialgruppe (nicht nach genauem Namen); unbekannte Gruppen kosten 0.
PREIS = ("Switch(" + ", ".join('%s="%s", Parameters!%s.Value' % (MATGRUPPE, g, n) for g, n in [
    ("Beton", "Preis_Beton"), ("Mauerwerk", "Preis_Mauerwerk"), ("Dämmung", "Preis_Daemmung"), ("Gipskarton", "Preis_Gipskarton")])
         + ", True, 0.0)")

# Klick im Allplan-Report-Fenster: zoomt auf das Bauteil der Zeile und markiert es (Feld Nr = @10@).
ZOOM = '="Zoom:" + Fields!Nr.Value + ",Mark:" + Fields!Nr.Value'


def klick(textbox_xml, ziel=ZOOM, tooltip="Klick: in Allplan auf dieses Bauteil zoomen"):
    """Macht eine Textbox anklickbar (Allplan zoomt aufs Bauteil) und gibt ihr einen Tooltip."""
    extra = "<ActionInfo><Actions><Action><BookmarkLink>%s</BookmarkLink></Action></Actions></ActionInfo>" % c.esc(ziel)
    if tooltip:
        extra += "<ToolTip>%s</ToolTip>" % c.esc(tooltip)
    return c.plus(textbox_xml, extra)


def sortierbar(textbox_xml, ausdruck, gruppe=None):
    """Spaltenkopf, der per Klick sortiert. Bei Aggregaten die Gruppe nennen, auf die sortiert wird."""
    scope = "<SortExpressionScope>%s</SortExpressionScope>" % gruppe if gruppe else ""
    return c.plus(textbox_xml, "<UserSort><SortExpression>=%s</SortExpression>%s</UserSort>" % (c.esc(ausdruck), scope))


def fuss(titel="Report Master"):
    """Fusszeile: Linie, links Titel und Projektname, rechts "Seite n / m". titel: der Text vor dem Projektnamen."""
    x0, w = c.INSET, c.CONTENT_W
    return (c.line("FussLinie", 0.15, x0, w)
            + c.text("FussLinks", 0.3, x0, 12, 0.45,
                     c.run('="%s   ·   " & Parameters!Project_Name.Value' % titel.replace('"', '""'), 7.5, c.MUTED))
            + c.text("FussRechts", 0.3, x0 + w - 5, 5, 0.45,
                     c.run('="Seite " & Globals!PageNumber & " / " & Globals!TotalPages', 7.5, c.MUTED), align="Right"))


CODE = """
Private zuordnung As New System.Collections.Hashtable()
Private stufen() As String = {%s}

' Farbe einer Kategorie: die erste gesehene bekommt den dunkelsten Ton, jede weitere den naechsten.
' Gleicher Name = gleiche Farbe, in jedem Diagramm und jeder Tabelle des Reports.
Public Function Stufe(ByVal name As Object) As String
    Dim key As String = ""
    If Not name Is Nothing Then key = name.ToString()
    If Not zuordnung.ContainsKey(key) Then
        zuordnung(key) = stufen(zuordnung.Count Mod stufen.Length)
    End If
    Return CStr(zuordnung(key))
End Function

' Materialgruppe am Wortstamm erkennen - Projekte benennen dasselbe Material verschieden
' ("Beton bewehrt", "StB C45", "Beton"; "Mauerwerk", "MW", "KS 20").
Public Function MatArt(ByVal name As Object) As String
    Dim s As String = ""
    If Not name Is Nothing Then s = name.ToString().Trim().ToLower()
    If s = "" Then Return "ohne Angabe"
    If s.Contains("gips") OrElse s.Contains("trockenbau") OrElse s.Contains("gypsum") OrElse s.Contains("plasterboard") OrElse s.Contains("drywall") Then Return "Gipskarton"
    If s.Contains("dämm") OrElse s.Contains("daemm") OrElse s.Contains("wdvs") OrElse s.Contains("isolier") OrElse s.Contains("insulat") OrElse s.Contains("etics") Then Return "Dämmung"
    If s.Contains("mauer") OrElse s = "mw" OrElse s.StartsWith("mw ") OrElse s.Contains("ziegel") OrElse s.Contains("kalksand") OrElse s.Contains("porenbeton") OrElse s.StartsWith("ks ") OrElse s.Contains("masonry") OrElse s.Contains("brick") OrElse s.Contains("blockwork") Then Return "Mauerwerk"
    If s.Contains("beton") OrElse s.StartsWith("stb") OrElse s.Contains("concrete") Then Return "Beton"
    If s.Contains("holz") OrElse s.Contains("wood") OrElse s.Contains("timber") Then Return "Holz"
    If s.Contains("stahl") OrElse s.Contains("steel") Then Return "Stahl"
    If s.Contains("glas") Then Return "Glas"   ' trifft auch "glass"
    If s.Contains("stein") OrElse s.Contains("stone") Then Return "Naturstein"
    Return "Sonstiges"
End Function

Public Function MatFarbe(ByVal name As Object) As String
    Select Case MatArt(name)
%s        Case Else : Return "%s"
    End Select
End Function

' Bauteilart aus der Allplan-Objektnummer (@OBJ@) - unabhaengig davon, wie das Projekt seine Objekte nennt.
Public Function Art(ByVal nr As Object) As String
    Select Case CInt(Val(nr))
        Case 1 : Return "Wand"
        Case 3 : Return "Stütze"
        Case 4 : Return "Decke"
        Case 6 : Return "Unterzug"
        Case 704 : Return "Bodenplatte"
        Case 61 : Return "Raum"
        Case 991 : Return "Fenster"
        Case 992 : Return "Tür"
        Case Else : Return "Sonstiges"
    End Select
End Function

' Verkehrsflaeche an der Raumnutzung erkennen.
Public Function IstVerkehr(ByVal funktion As Object) As Boolean
    Dim s As String = ""
    If Not funktion Is Nothing Then s = funktion.ToString().ToLower()
    Return s.Contains("flur") OrElse s.Contains("diele") OrElse s.Contains("gang") OrElse s.Contains("treppe") _
        OrElse s.Contains("verkehr") OrElse s.Contains("foyer") OrElse s.Contains("windfang") OrElse s.Contains("aufzug") _
        OrElse s.Contains("corridor") OrElse s.Contains("hallway") OrElse s.Contains("circulation") OrElse s.Contains("stair") _
        OrElse s.Contains("lobby") OrElse s.Contains("lift") OrElse s.Contains("elevator")
End Function
""" % (", ".join('"%s"' % f for f in c.RAMP),
       "".join('        Case "%s" : Return "%s"' % (g, f) + chr(10) for g, f in c.MATERIALGRUPPE),
       c.MATERIALGRUPPE[-1][1])
