# -*- coding: utf-8 -*-
"""Geruest und Gestaltungssystem des Master-Reports (RDL 2016).

core.py baut den Report-Rahmen (Datenquelle, DataSets, Parameter, Seiten, Kopf/Fuss) und die
Grundbausteine Text, Flaeche, Linie, Bild, Tabelle. Diagramme liefert viz.py.
Datenquelle und Standardparameter stammen woertlich aus Allplans Template_Grouping0.rdlc.
"""
import os
import re
import subprocess
import sys
import uuid
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design  # noqa: E402  (liegt neben core.py)

HERE = os.path.dirname(os.path.abspath(__file__))
# Datenquelle und Standardparameter, die jeder Allplan-Report tragen muss (Project_Name, Date ...): die zwei
# Bloecke aus Allplans Startvorlage Template_Grouping0.rdlc, unveraendert.
TEMPLATE = os.path.join(HERE, "rahmen.xml")
VERFASSER = "W. Liffers"     # steht als <Author> in jeder erzeugten Datei; fuer eigene Reports hier aendern
NS = "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"
RENDER = os.path.normpath(os.path.join(HERE, "..", "werkzeug", "render", "bin", "RenderRdlc.exe"))

# ---------------------------------------------------------------- Gestaltungssystem
# Farben und Schrift kommen aus design.py: Hausdesign oder Kundendesign (festgelegt in <Werkstatt>/design.json).
# Hier stehen nur die Namen, unter denen Seiten und Bausteine sie benutzen - nie ein Hex-Wert in einer Seite.
DESIGN = design.laden()
_f = DESIGN.farben
INK = _f["tinte"]                   # Ueberschriften, grosse Zahlen
TEXT = _f["text"]                   # Fliesstext, Tabellenwerte
MUTED = _f["leise"]                 # Beschriftungen, Achsen
FAINT = _f["fussnote"]              # Einheiten, Fussnoten
HAIR = _f["linie"]                  # Haarlinien, Rahmen
HAIR_STARK = _f["linie_stark"]      # starke Trenner
SURFACE = _f["flaeche"]             # Kachelflaechen
MIST = _f["flaeche_blau"]           # Hinweis- und Bandflaechen
TINT = _f["flaeche_tint"]           # Hervorhebung in Listen, Rand von Hinweisen
NAVY = _f["dunkel"]                 # Titelband, dunkle Flaechen
BLUE = _f["leit"]                   # Leitfarbe: Balken, Links, hervorgehobene Zahl auf Weiss
AKZENT = _f["akzent"]               # Akzent: auf Weiss NUR als Flaeche oder Linie (im Hausdesign Tuerkis - als Schrift unlesbar)
AKZENT_TEXT = DESIGN.akzent_text    # hervorgehobene Schrift auf Weiss (Akzent, wenn lesbar - sonst Leitfarbe)
AUF_AKZENT = DESIGN.auf_akzent      # Schrift auf einer Akzentflaeche
AKZENT_DUNKEL = DESIGN.akzent_auf_dunkel    # Akzent als Schrift oder Marke auf dunklem Grund
AUF_NAVY = DESIGN.auf_dunkel        # zweitrangige Schrift auf dunklem Grund (Weiss 70 %)
AUF_NAVY_LEISE = DESIGN.auf_dunkel_leise    # leise Schrift auf dunklem Grund (Weiss 60 %)
NAVY_LINIE = DESIGN.dunkel_linie    # Linie auf dunklem Grund (Weiss 15 %)
NAVY_FLAECHE = DESIGN.dunkel_flaeche        # Kachel auf dunklem Grund (Weiss 8 %)
GREEN = _f["gut"]                   # Bewertung als Flaeche, Punkt, Balken
RED = _f["schlecht"]
AMBER = _f["achtung"]
GREEN_TEXT = DESIGN.gut_text        # Bewertung als Schrift auf Weiss (abgedunkelt, bis sie lesbar ist)
RED_TEXT = DESIGN.schlecht_text
AMBER_TEXT = DESIGN.achtung_text
WHITE = _f["weiss"]

F = DESIGN.schrift["normal"]
F_LIGHT = DESIGN.schrift["leicht"]
F_SEMI = DESIGN.schrift["halbfett"]
F_ZAHL = DESIGN.schrift["zahl"]     # grosse Kennzahlen

# Farben mit Bedeutung: jede Materialgruppe hat im ganzen Report dieselbe Farbe - in jedem Design (Beton grau, Mauerwerk
# ziegelrot). Die Gruppe erkennt der Report am Wortstamm des Materialnamens (Code.MatArt), nicht am genauen Namen:
# "StB C45", "Beton bewehrt" und "Beton" sind alle "Beton".
MATERIALGRUPPE = design.MATERIALGRUPPE
# Die vier Materialien des Master-Teilbilds (Name im Modell, Farbe) - fuer feste Legenden.
MATERIAL = [("Beton bewehrt", "#475569"), ("Mauerwerk", "#C2410C"), ("Dämmung", "#EAB308"),
            ("Gipskarton", "#94A3B8")]
# Ein Farbton in Stufen: fuer geordnete Kategorien (groesste = dunkelste).
RAMP = list(_f["stufen"])
SERIE = list(_f["serie"])

PAGE_W, PAGE_H = 21.0, 29.7
INSET = 1.5                      # Abstand des Inhalts vom Blattrand
CONTENT_W = PAGE_W - 2 * INSET   # 18 cm
FOOT_H = 1.2
PAGE_BODY_H = PAGE_H - FOOT_H    # nutzbare Hoehe je Seite


def esc(value):
    return escape(str(value))


def cm(value):
    return "%scm" % round(value, 3)


# ---------------------------------------------------------------- Text
def run(value, size=9, color=TEXT, font=F, bold=False, italic=False, fmt=None):
    """Ein Textstueck; mehrere davon ergeben gemischte Formate in einer Textbox."""
    style = "<FontFamily>%s</FontFamily><FontSize>%spt</FontSize>" % (font, size)
    if bold:
        style += "<FontWeight>Bold</FontWeight>"
    if italic:
        style += "<FontStyle>Italic</FontStyle>"
    if fmt:
        style += "<Format>%s</Format>" % esc(fmt)
    style += "<Color>%s</Color>" % esc(color)
    return "<TextRun><Value>%s</Value><Style>%s</Style></TextRun>" % (esc(value), style)


def para(runs, align=None):
    style = "<Style>%s</Style>" % ("<TextAlign>%s</TextAlign>" % align if align else "")
    return "<Paragraph><TextRuns>%s</TextRuns>%s</Paragraph>" % ("".join(runs), style)


def edge(sides, color=HAIR, width="0.75pt"):
    """Rahmen nur an den genannten Seiten, z. B. edge(['Bottom'])."""
    out = "<Border><Style>None</Style></Border>"
    for side in sides:
        out += "<%sBorder><Color>%s</Color><Style>Solid</Style><Width>%s</Width></%sBorder>" % (side, color, width, side)
    return out


def box_style(bg=None, valign=None, pad=(0, 0, 0, 0), border_xml="", bg_expr=None):
    style = border_xml
    if bg or bg_expr:
        style += "<BackgroundColor>%s</BackgroundColor>" % esc(bg_expr or bg)
    if valign:
        style += "<VerticalAlign>%s</VerticalAlign>" % valign
    style += ("<PaddingLeft>%spt</PaddingLeft><PaddingRight>%spt</PaddingRight><PaddingTop>%spt</PaddingTop>"
              "<PaddingBottom>%spt</PaddingBottom>" % (pad[0], pad[2], pad[1], pad[3]))
    return style


def text(name, top, left, w, h, content, align=None, valign=None, bg=None, pad=(0, 0, 0, 0), border_xml="",
         grow=False, hidden=None, bg_expr=None, rotate=None):
    """Textbox. content: Zeichenkette aus run()/para() oder eine Liste von para()."""
    if isinstance(content, (list, tuple)):
        paragraphs = "".join(content)
    elif content.startswith("<Paragraph>"):
        paragraphs = content
    else:
        paragraphs = para([content], align)
    if align and "<TextAlign>" not in paragraphs:
        paragraphs = paragraphs.replace("<Style></Style>", "<Style><TextAlign>%s</TextAlign></Style>" % align)
    vis = "<Visibility><Hidden>%s</Hidden></Visibility>" % esc(hidden) if hidden else ""
    style = box_style(bg, valign, pad, border_xml, bg_expr)
    if rotate:
        style += "<WritingMode>%s</WritingMode>" % rotate
    pos = ""
    if top is not None:
        pos = "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (cm(top), cm(left), cm(h), cm(w))
    return ('<Textbox Name="%s"><CanGrow>%s</CanGrow><KeepTogether>true</KeepTogether><Paragraphs>%s</Paragraphs>'
            "%s%s<Style>%s</Style></Textbox>" % (name, "true" if grow else "false", paragraphs, pos, vis, style))


def cell(name, content, align=None, valign="Middle", bg=None, pad=(4, 2, 4, 2), border_xml="", bg_expr=None):
    """Textbox fuer eine Tabellenzelle (ohne Lage)."""
    return text(name, None, 0, 0, 0, content, align, valign, bg, pad, border_xml, bg_expr=bg_expr)


def plus(textbox_xml, extra):
    """Zusatz-XML (Aktion, Tooltip, Sortierung, Lesezeichen) in eine Textbox einsetzen."""
    return textbox_xml.replace("</Paragraphs>", "</Paragraphs>" + extra, 1)


def marke(element_xml, bookmark=None, label=None):
    """Sprungziel (Bookmark) und/oder Eintrag der Dokumentstruktur (DocumentMapLabel) an ein fertiges Element haengen
    (Textbox, Bild, Rechteck, Tabelle). In Allplan gemessen: Das Label wird im PDF zum Lesezeichen; ein BookmarkLink auf
    ein Bookmark ergibt im PDF KEINEN Link (nur Hyperlink tut das)."""
    extra = ""
    if bookmark:
        extra += "<Bookmark>%s</Bookmark>" % esc(bookmark)
    if label:
        extra += "<DocumentMapLabel>%s</DocumentMapLabel>" % esc(label)
    ende = element_xml.rfind("</")
    return element_xml[:ende] + extra + element_xml[ende:]


# ---------------------------------------------------------------- Aktionen (Klick auf Textbox oder Bild)
_LINK_SCHEMA = ("https://", "mailto:", "file:///")


def aktion(inner):
    """ActionInfo-Huelle um eine Aktion; mit plus(textbox, ...) an eine Textbox, mit image(..., action=...) an ein Bild."""
    return "<ActionInfo><Actions><Action>%s</Action></Actions></ActionInfo>" % inner


def hyperlink(url):
    """Aktion Hyperlink. In Allplan gemessen (PDF): https://, mailto: und file:/// kommen als Link an, ein Ausdruck
    (="https://..." & Wert) ebenso; ein Link OHNE Schema (www.allplan.com) wird gestrichen - darum hier ValueError."""
    ziel = url.strip()
    if ziel.startswith("="):
        anfang = re.match(r'=\s*"(.*)', ziel, re.S)
        if not anfang or not anfang.group(1).lower().startswith(_LINK_SCHEMA):
            raise ValueError('Hyperlink-Ausdruck muss mit einem Text-Schema beginnen: ="https://..." & ... (gefunden: %r)' % url)
    elif not ziel.lower().startswith(_LINK_SCHEMA):
        raise ValueError("Hyperlink nur mit https://, mailto: oder file:/// - ohne Schema streicht Allplan den Link (gefunden: %r)" % url)
    return aktion("<Hyperlink>%s</Hyperlink>" % esc(ziel))


def bookmark_link(name):
    """Aktion BookmarkLink (Sprung zu einem Bookmark, z. B. gesetzt mit marke()/rect(bookmark=...)). In Allplan als
    PDF gemessen: erzeugt KEINEN Link; ob der Klick im Report-Fenster springt, ist nicht gemessen."""
    return aktion("<BookmarkLink>%s</BookmarkLink>" % esc(name))


def drillthrough(ziel, parameter=()):
    """Aktion Drillthrough (Sprung in einen zweiten Report). ziel: Dateiname OHNE Endung, im selben Ordner (oder ="Sub\\..."
    als Ausdruck); parameter: Liste (Name, Wert oder Ausdruck). In Allplan gemessen: Quelle und Ziel werden als PDF
    fehlerfrei ausgegeben; der Klick im Report-Fenster ist nicht gemessen."""
    if ziel.lower().endswith((".rdlc", ".rdl")):
        raise ValueError("Drillthrough-Ziel ohne Endung angeben (gefunden: %r)" % ziel)
    liste = "".join('<Parameter Name="%s"><Value>%s</Value></Parameter>' % (n, esc(w)) for n, w in parameter)
    return aktion("<Drillthrough><ReportName>%s</ReportName>%s</Drillthrough>"
                  % (esc(ziel), "<Parameters>%s</Parameters>" % liste if liste else ""))


def rect(name, top, left, w, h, inner="", bg=None, border_xml="", page_break=False, hidden=None, keep=True, label=None,
         umbruch=None, seitenname=None, bookmark=None, seitenzaehlung_neu=False):
    """Rechteck. page_break=True: Seitenumbruch NACH dem Rechteck; umbruch='Start' | 'End' setzt ihn davor bzw. danach
    (gemessen in Allplan: beides geht; End des einen plus Start des naechsten ergibt eine LEERE Seite - nur eines setzen).
    seitenzaehlung_neu=True: Globals!PageNumber zaehlt ab diesem Umbruch wieder ab 1 (ResetPageNumber; braucht umbruch oder
    page_break; in Allplan ausgegeben - der Zaehlerstand der ersten Gruppe stimmt nur, wenn die Deckseite mit End UND
    ResetPageNumber schliesst; je Gruppe an der Tabelle ist es ebenfalls in Allplan gemessen).
    seitenname: Ausdruck fuer Globals!PageName ab dieser Seite; bookmark: Sprungziel; label: Eintrag der Dokumentstruktur
    (im PDF ein Lesezeichen, bis 3 Ebenen verschachtelt - gemessen in Allplan)."""
    style = (("<BackgroundColor>%s</BackgroundColor>" % bg) if bg else "") + (border_xml or "<Border><Style>None</Style></Border>")
    if umbruch is not None and umbruch not in ("Start", "End"):
        raise ValueError("Seitenumbruch am Rechteck: nur 'Start' oder 'End' (gemessen), nicht %r" % (umbruch,))
    ort = umbruch or ("End" if page_break else None)
    if seitenzaehlung_neu and not ort:
        raise ValueError("seitenzaehlung_neu braucht einen Seitenumbruch am Rechteck: umbruch='Start' oder 'End' setzen")
    brk = ("<PageBreak><BreakLocation>%s</BreakLocation>%s</PageBreak>"
           % (ort, "<ResetPageNumber>true</ResetPageNumber>" if seitenzaehlung_neu else "")) if ort else ""
    vis = "<Visibility><Hidden>%s</Hidden></Visibility>" % esc(hidden) if hidden else ""
    items = "<ReportItems>%s</ReportItems>" % inner if inner else ""
    pos = ""
    if top is not None:
        pos = "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (cm(top), cm(left), cm(h), cm(w))
    lab = "<DocumentMapLabel>%s</DocumentMapLabel>" % esc(label) if label else ""
    if bookmark:
        lab += "<Bookmark>%s</Bookmark>" % esc(bookmark)
    if seitenname:
        lab += "<PageName>%s</PageName>" % esc(seitenname)
    return ('<Rectangle Name="%s">%s%s<KeepTogether>%s</KeepTogether>%s%s%s<Style>%s</Style></Rectangle>'
            % (name, items, brk, "true" if keep else "false", lab, pos, vis, style))


def line(name, top, left, w, color=HAIR, width="0.75pt", h=0):
    return ('<Line Name="%s"><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>'
            "<Style><Border><Color>%s</Color><Style>Solid</Style><Width>%s</Width></Border></Style></Line>"
            % (name, cm(top), cm(left), cm(h), cm(w), color, width))


def image(name, top, left, w, h, value, source="Database", sizing="FitProportional", mime="image/png", hidden=None,
          action=None):
    pos = ""
    if top is not None:
        pos = "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (cm(top), cm(left), cm(h), cm(w))
    vis = "<Visibility><Hidden>%s</Hidden></Visibility>" % esc(hidden) if hidden else ""
    mime_xml = "<MIMEType>%s</MIMEType>" % mime if source == "Database" else ""
    if action and action.startswith("<ActionInfo>"):       # fertige Aktion aus hyperlink() / drillthrough() / bookmark_link()
        act = action
    else:
        act = "<ActionInfo><Actions><Action><BookmarkLink>%s</BookmarkLink></Action></Actions></ActionInfo>" % esc(action) if action else ""
    return ('<Image Name="%s"><Source>%s</Source><Value>%s</Value>%s<Sizing>%s</Sizing>%s%s%s'
            "<Style><Border><Style>None</Style></Border></Style></Image>"
            % (name, source, esc(value), mime_xml, sizing, act, pos, vis))


def subreport(name, top, left, w, h, ziel, parameter=(), keine_zeilen=None, rahmen=None, rahmen_breite="1pt"):
    """Unterbericht (<Subreport>): zweite .rdlc im selben Ordner, ziel = Dateiname OHNE Endung.
    parameter: Liste (Name, Wert oder Ausdruck); top=None setzt ihn ohne Lage in eine Tabellenzelle (je Zeile einer).
    rahmen: Farbe des Rahmens; er sitzt als Style/Border am Subreport selbst - ein Rechteck dahinter verdeckt den Inhalt.

    In Allplan 2027 gemessen: Allplan gibt dem Unterbericht die ZEILEN DES HAUPTREPORTS und fuehrt die Abfrage des Ziels
    NICHT aus (keine eigene Abfrage, keine andere Tabelle, keine andere Bildart). Gefuellt sind nur die Felder des Ziels,
    die im Hauptreport gleich HEISSEN (Zuordnung nach Namen); das Ziel waehlt seine Zeilen per Tablix-Filter ueber einen
    Parameter und deckelt jede Tabelle mit TopN, sonst waechst es und schiebt alles darunter weg. JEDER Parameter des
    Ziels braucht <Prompt>, sonst wird der Unterbericht nicht angefordert. Nicht im Seitenkopf oder -fuss (Dokument
    ungueltig). Parameter uebergeben, zweite Ebene und Unterbericht in der Tabellenzelle gehen."""
    if ziel.lower().endswith((".rdlc", ".rdl")):
        raise ValueError("Unterbericht-Ziel ohne Endung angeben (gefunden: %r)" % ziel)
    xml = '<Subreport Name="%s"><ReportName>%s</ReportName>' % (name, esc(ziel))
    if parameter:
        xml += "<Parameters>%s</Parameters>" % "".join(
            '<Parameter Name="%s"><Value>%s</Value></Parameter>' % (n, esc(w)) for n, w in parameter)
    if keine_zeilen:
        xml += "<NoRowsMessage>%s</NoRowsMessage>" % esc(keine_zeilen)
    if top is not None:
        xml += "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (cm(top), cm(left), cm(h), cm(w))
    rand = ("<Border><Color>%s</Color><Style>Solid</Style><Width>%s</Width></Border>" % (rahmen, rahmen_breite)
            if rahmen else "<Border><Style>None</Style></Border>")
    return xml + "<Style>%s</Style></Subreport>" % rand


# ---------------------------------------------------------------- Tabelle
_SEITENUMBRUCH = ("Between", "Start", "End", "StartAndEnd")


def _zellen(zellen):
    """TablixCell-XML aus Zellinhalten. Ein Eintrag (inhalt, span) laeuft ueber span Spalten (ColSpan); die Folgezellen
    der Zeile entfallen dann in der Liste und werden hier als leere Zellen angehaengt."""
    xml = ""
    for z in zellen:
        if isinstance(z, tuple):
            inhalt, span = z
            xml += ("<TablixCell><CellContents>%s<ColSpan>%d</ColSpan></CellContents></TablixCell>%s"
                    % (inhalt, span, "<TablixCell/>" * (span - 1)))
        else:
            xml += "<TablixCell><CellContents>%s</CellContents></TablixCell>" % z
    return xml


def sortierung(*ausdruecke):
    """SortExpressions aus Paaren (Ausdruck, absteigend); mehrere Paare ergeben eine zweite, dritte ... Sortierung.
    Sortieren nach einem Aggregat der Gruppe (z. B. =Sum(...)) ist in Allplan ausgegeben (labor/luecken/B/befund.md)."""
    if not ausdruecke:
        return ""
    return "<SortExpressions>%s</SortExpressions>" % "".join(
        "<SortExpression><Value>%s</Value>%s</SortExpression>" % (esc(e), "<Direction>Descending</Direction>" if d else "")
        for e, d in ausdruecke)


def _sortierung_aus(sort, sort_desc):
    """sort: ein Ausdruck (mit sort_desc) oder eine Liste von Paaren (Ausdruck, absteigend)."""
    if not sort:
        return ""
    return sortierung(*(sort if isinstance(sort, (list, tuple)) else [(sort, sort_desc)]))


def _umbruch_xml(ort, neu, seitenname, label):
    """Umbruch, Seitenname und Dokumentstruktur-Eintrag am Gruppenband (Inhalt von <Group>)."""
    xml = ""
    if ort:
        if ort is True:
            ort = "Between"
        if ort not in _SEITENUMBRUCH:
            raise ValueError("Seitenumbruch je Gruppe: True oder einer von %s, nicht %r" % (", ".join(_SEITENUMBRUCH), ort))
        xml += "<PageBreak><BreakLocation>%s</BreakLocation>%s</PageBreak>" % (ort, "<ResetPageNumber>true</ResetPageNumber>" if neu else "")
    if seitenname:
        xml += "<PageName>%s</PageName>" % esc(seitenname)
    if label:
        xml += "<DocumentMapLabel>%s</DocumentMapLabel>" % esc(label)
    return xml


def tablix(name, top, left, cols, rows, dataset="AllplanReport", group=None, sort=None, sort_desc=False,
           filter_expr=None, detail=True, repeat_header=True, keep_together=False, gruppen_umbruch=False,
           seitenzaehlung_neu=False, gruppen_seitenname=None, gruppen_label=None, filter_xml="", gruppen_filter=""):
    """Tabelle mit Kopf-, Daten- und Fusszeilen.

    cols: Spaltenbreiten in cm. rows: Liste (art, hoehe_cm, [zellen-xml]) mit art 'kopf' | 'daten' | 'fuss'.
    Eine Zelle darf ein Paar (zellen-xml, span) sein: ColSpan ueber span Spalten, die Folgezellen der Zeile lässt man weg
    (ColSpan im statischen Raster und im Gruppenband: in Allplan ausgegeben, labor/luecken/B/befund.md).
    group: Ausdruck -> je Gruppe eine Datenzeile (Aggregate); ohne group und detail=True: je Datensatz eine Zeile.
    filter_expr: Ausdruck, der fuer die gewuenschten Zeilen "j" liefert. filter_xml: stattdessen fertige <Filters> aus
    filter_liste(filter_in(...), filter_j(...), ...) - mehrere Filter und andere Arten (In mit Mehrfach-Parameter, Between ...);
    gruppen_filter: ebenso, aber an der Gruppe (z. B. filter_liste(filter_topn(...)) fuer "nur die n groessten Gruppen").
    sort: ein Ausdruck (mit sort_desc) oder eine Liste (Ausdruck, absteigend) - die zweite Sortierung der Gruppe bzw. die
    Sortierung der Detailzeilen; TopN, BottomN, In, Sortieren nach Aggregat sind in Allplan ausgegeben (B/befund.md).
    Die Kopfzeile bleibt mit der ersten Datenzeile zusammen (KeepWithGroup After) und wiederholt sich auf Folgeseiten.
    keep_together: Tabelle beginnt ganz auf der Folgeseite, wenn sie nicht mehr passt (in Allplan gemessen; die Luecke bleibt).
    Nur mit group: gruppen_umbruch=True setzt vor jede weitere Gruppe einen Seitenumbruch (Between; auch 'Start', 'End',
    'StartAndEnd' am Gruppenband - nur kopflos gemessen; 'Start' bricht auch vor der ERSTEN Gruppe, die Kopfzeile steht dann
    allein auf Seite 1 - fuer "je Gruppe eine Seite" bleibt Between die Wahl), mit
    seitenzaehlung_neu=True zaehlt Globals!PageNumber je Gruppe wieder ab 1 (gemessen: Fuss "Seite 1 / 1", dazu
    OverallPageNumber und OverallTotalPages); gruppen_seitenname / gruppen_label sind Ausdruecke fuer Globals!PageName
    bzw. den Eintrag der Dokumentstruktur (PDF-Lesezeichen) je Gruppe. Verschachtelte Gruppen: tablix_gruppen().
    """
    if (gruppen_umbruch or seitenzaehlung_neu or gruppen_seitenname or gruppen_label or gruppen_filter) and not group:
        raise ValueError("Umbruch, Seitenzaehlung, Seitenname, Label und Filter je Gruppe brauchen group=<Ausdruck>")
    if seitenzaehlung_neu and not gruppen_umbruch:
        raise ValueError("seitenzaehlung_neu gehoert zum Seitenumbruch je Gruppe: gruppen_umbruch=True setzen")
    if filter_expr and filter_xml:
        raise ValueError("filter_expr und filter_xml schliessen sich aus: alle Filter in filter_liste(...) sammeln")

    xml = '<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>' % (
        name, "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % cm(c) for c in cols))
    members = ""
    for art, hoehe, zellen in rows:
        xml += "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (cm(hoehe), _zellen(zellen))
        if art == "kopf":
            members += ("<TablixMember><KeepWithGroup>After</KeepWithGroup>%s</TablixMember>"
                        % ("<RepeatOnNewPage>true</RepeatOnNewPage>" if repeat_header else ""))
        elif art == "fuss":
            members += "<TablixMember><KeepWithGroup>Before</KeepWithGroup></TablixMember>"
        else:
            srt = _sortierung_aus(sort, sort_desc)
            if group:
                gruppe = _umbruch_xml(gruppen_umbruch, seitenzaehlung_neu, gruppen_seitenname, gruppen_label)
                members += ('<TablixMember><Group Name="%s_G"><GroupExpressions><GroupExpression>%s</GroupExpression>'
                            "</GroupExpressions>%s%s</Group>%s</TablixMember>" % (name, esc(group), gruppen_filter, gruppe, srt))
            else:
                members += '<TablixMember><Group Name="%s_D"/>%s</TablixMember>' % (name, srt)
    xml += "</TablixRows></TablixBody>"
    xml += "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>" % ("<TablixMember/>" * len(cols))
    xml += "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>" % members
    xml += "<DataSetName>%s</DataSetName>" % dataset
    if filter_expr:
        xml += filters(filter_expr)
    xml += filter_xml
    if keep_together:
        xml += "<KeepTogether>true</KeepTogether>"
    xml += "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border></Style></Tablix>" % (
        cm(top), cm(left), cm(sum(r[1] for r in rows)), cm(sum(cols)))
    return xml


def filters(expr):
    """Filter fuer Tabelle/Diagramm/Gruppe: behaelt Zeilen, fuer die der Ausdruck wahr ist."""
    return ('<Filters><Filter><FilterExpression>=IIf(%s, "j", "n")</FilterExpression><Operator>Equal</Operator>'
            "<FilterValues><FilterValue>j</FilterValue></FilterValues></Filter></Filters>" % esc(expr))


def topn(ausdruck, n, unten=False):
    """Filter "nur die n groessten" (unten=True: die n kleinsten) - an Tabelle, Diagramm oder Gruppe.
    Gleiche Werte am Rand zaehlen alle mit; fuer eine feste Zeilenzahl einen eindeutigen Nachrang in den
    Ausdruck rechnen."""
    return ("<Filters><Filter><FilterExpression>=%s</FilterExpression><Operator>%s</Operator>"
            "<FilterValues><FilterValue>=%d</FilterValue></FilterValues></Filter></Filters>"
            % (esc(ausdruck), "BottomN" if unten else "TopN", n))


# ---------------------------------------------------------------- Filter und verschachtelte Gruppen (Bausteine fuer tablix_gruppen)
def filter_j(bedingung):
    """Ein <Filter>: behaelt Zeilen, fuer die der Ausdruck wahr ist (IIf j/n wie filters())."""
    return ('<Filter><FilterExpression>=IIf(%s, "j", "n")</FilterExpression><Operator>Equal</Operator>'
            "<FilterValues><FilterValue>j</FilterValue></FilterValues></Filter>" % esc(bedingung))


def filter_in(ausdruck, parameter):
    """Ein <Filter> 'Ausdruck In Parameter': der Parameter ist eine Mehrfachauswahl (=Parameters!X.Value; Muster der Allplan-
    Vorlagen). In Allplan ausgegeben (labor/luecken/B/befund.md, C/befund.md). ausdruck ohne fuehrendes '='."""
    return ("<Filter><FilterExpression>=%s</FilterExpression><Operator>In</Operator><FilterValues><FilterValue>=Parameters!%s.Value"
            "</FilterValue></FilterValues></Filter>" % (esc(ausdruck), parameter))


def filter_topn(ausdruck, n, unten=False):
    """Ein <Filter> 'nur die n groessten' (unten=True: die n kleinsten); n eine Zahl oder ein Ausdruck ohne '='
    (z. B. CInt(Parameters!N.Value)). An der Gruppe gesetzt (gruppen_filter / gruppe_mitglied). TopN, BottomN in Allplan
    ausgegeben (labor/luecken/B/befund.md). ausdruck ohne fuehrendes '='."""
    return ("<Filter><FilterExpression>=%s</FilterExpression><Operator>%s</Operator><FilterValues><FilterValue>=%s</FilterValue>"
            "</FilterValues></Filter>" % (esc(ausdruck), "BottomN" if unten else "TopN", esc(str(n))))


def filter_liste(*filter_xml):
    """<Filters> aus mehreren <Filter> (filter_j, filter_in, filter_topn)."""
    return "<Filters>%s</Filters>" % "".join(filter_xml)


def zelle(inhalt, span=None):
    """Fertige Tabellenzelle fuer zeile(); mit span ueber mehrere Spalten (ColSpan), die Folgezellen werden leer angehaengt."""
    return _zellen([(inhalt, span) if span else inhalt])


def zeile(hoehe, zellen):
    """Tabellenzeile aus fertigen Zellen (zelle())."""
    return "<TablixRow><Height>%s</Height><TablixCells>%s</TablixCells></TablixRow>" % (cm(hoehe), "".join(zellen))


def kopf_mitglied(wiederholen=True):
    """Kopfzeile (Zeilenhierarchie): bleibt mit der naechsten Zeile zusammen, wiederholt sich auf Folgeseiten."""
    return "<TablixMember><KeepWithGroup>After</KeepWithGroup>%s</TablixMember>" % ("<RepeatOnNewPage>true</RepeatOnNewPage>" if wiederholen else "")


def fuss_mitglied(versteckt=None):
    """Fusszeile (Summe, Etikett): bleibt mit der Zeile davor zusammen; versteckt: Ausdruck fuer Visibility/Hidden."""
    vis = "<Visibility><Hidden>%s</Hidden></Visibility>" % esc(versteckt) if versteckt else ""
    return "<TablixMember><KeepWithGroup>Before</KeepWithGroup>%s</TablixMember>" % vis


def gruppe_mitglied(name, ausdruck, sortiert=(), gruppen_filter="", kinder="", umbruch=None, seitenzaehlung_neu=False,
                    seitenname=None, label=None):
    """Zeilengruppe der Zeilenhierarchie. ausdruck mit fuehrendem '='; sortiert: Liste (Ausdruck, absteigend);
    gruppen_filter: filter_liste(filter_topn(...)); kinder: Mitglieder INNERHALB der Gruppe (kopf_mitglied(), eine innere
    gruppe_mitglied(), fuss_mitglied()) - so entsteht die aeussere Gruppe mit Kopfzeile je Gruppe und inneren Detailzeilen.
    umbruch: True/'Between' | 'Start' | 'End' | 'StartAndEnd' (Between mit Zaehler neu je Gruppe: in Allplan ausgegeben, A/befund.md;
    Start am Gruppenband nur kopflos); seitenzaehlung_neu, seitenname, label wie bei tablix()."""
    return ('<TablixMember><Group Name="%s"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions>%s%s</Group>%s%s</TablixMember>'
            % (name, esc(ausdruck), gruppen_filter, _umbruch_xml(umbruch, seitenzaehlung_neu, seitenname, label), sortierung(*sortiert),
               "<TablixMembers>%s</TablixMembers>" % kinder if kinder else ""))


def tablix_gruppen(name, top, left, cols, zeilen, mitglieder, hoehe, dataset="AllplanReport", filter_xml="", keine_zeilen=None,
                   stil="", keep_together=False):
    """Tabelle mit freier Zeilenhierarchie - fuer verschachtelte Gruppen und Kopf-/Fusszeilen je Gruppe, die tablix() nicht kann.
    zeilen: Liste aus zeile(); mitglieder: die Zeilen-Mitglieder der obersten Ebene in der Reihenfolge der Zeilen (kopf_mitglied(),
    gruppe_mitglied(..., kinder=...), fuss_mitglied()); hoehe: Nennhoehe in cm; filter_xml: filter_liste(...) an der Tabelle;
    keine_zeilen: Text, der statt der leeren Tabelle steht; stil: weiteres Style-XML (z. B. Schrift). Verschachtelte Datenregionen,
    Gruppenvariablen und Filter an Gruppen: in Allplan ausgegeben (labor/luecken/B/befund.md)."""
    extra = ""
    if keine_zeilen:
        extra += "<NoRowsMessage>=%s</NoRowsMessage>" % esc('"%s"' % keine_zeilen.replace('"', '""'))
        stil += "<FontFamily>%s</FontFamily><FontSize>9pt</FontSize><Color>%s</Color>" % (F, MUTED)
    extra += "<DataSetName>%s</DataSetName>%s%s" % (dataset, filter_xml, "<KeepTogether>true</KeepTogether>" if keep_together else "")
    return ('<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>%s</TablixRows></TablixBody>'
            "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>"
            "<TablixRowHierarchy><TablixMembers>%s</TablixMembers></TablixRowHierarchy>%s"
            "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width><Style><Border><Style>None</Style></Border>%s</Style></Tablix>"
            % (name, "".join("<TablixColumn><Width>%s</Width></TablixColumn>" % cm(x) for x in cols), "".join(zeilen),
               "<TablixMember/>" * len(cols), "".join(mitglieder), extra, cm(top), cm(left), cm(hoehe), cm(sum(cols)), stil))


# ---------------------------------------------------------------- Report-Rahmen
def dataset(name, query, fields):
    """fields: Liste (Name, Typ) mit Typ String | Double | Int32 | Byte[].

    <CaseSensitivity>True</CaseSensitivity> steht fest im DataSet (in Allplan 2027 gemessen, laeuft): ohne die Angabe fasst eine
    Gruppe "Flur" und "FLUR" zu EINER Zeile zusammen, CountDistinct zaehlt sie aber als ZWEI - Rang, "+ n weitere" und TopN
    laufen dann auseinander (Rest-Zeile doppelt, Seite laenger). Mit der Angabe sind es ueberall zwei Werte."""
    felder = "".join('<Field Name="%s"><DataField>%s</DataField><rd:TypeName>System.%s</rd:TypeName></Field>' % (n, n, t)
                     for n, t in fields)
    return ('<DataSet Name="%s"><Query><DataSourceName>DummyDataSource</DataSourceName><CommandText>%s</CommandText></Query>'
            "<Fields>%s</Fields><CaseSensitivity>True</CaseSensitivity>"
            "<rd:DataSetInfo><rd:DataSetName>%s</rd:DataSetName><rd:TableName>AllplanTable</rd:TableName>"
            "</rd:DataSetInfo></DataSet>" % (name, esc(query), felder, name))


def parameter(name, datatype, default, prompt, werte=None, multi=False, nullable=False, allowblank=False, hidden=False,
              distinct=None, dataset_ref=None):
    """Eigener Parameter: erscheint im Allplan-Report-Fenster links unter "Benutzerinteraktion".
    datatype Boolean | String | Integer | Float | DateTime; werte: Liste (Wert, Anzeigetext) ergibt eine Auswahlliste
    (ValidValues; Parameters!x.Label liefert den Anzeigetext).
    default: fester Wert, bei multi eine Liste fester Werte, None = keine Vorgabe.
    multi: Mehrfachauswahl (MultiValue; mit Liste und ohne Vorgabe liefert Allplan nur den ERSTEN Listenwert - Vorgaben nennen).
    nullable: ohne Vorgabe ergibt Nothing; allowblank: ohne Vorgabe ergibt leeren Text; hidden: Wert gilt, aber das
    Report-Fenster IGNORIERT Hidden - der Parameter steht dort sichtbar und aenderbar (im Fenster gemessen).
    distinct: Feldname -> Auswahlliste aus den DATEN ueber <Prompt>Distinct(Fields!X.Value)</Prompt> (der prompt-Text entfaellt);
    ohne Auswahl liefert Allplan ALLE Werte, den leeren zuerst - "keine Auswahl = alle" ergibt sich von selbst.
    In Allplan 2027 gemessen (PDF-Ausgabe und Report-Fenster; im Fenster wirken Haken, Zahl und Liste sofort, ein einziger
    ungueltiger Parameter laesst dort den ganzen Report leer): Allplan nimmt feste Werte und eigene Hilfen (Prompt @Nr@,
    Distinct); Ausdruecke in Vorgaben und Listen wertet es NICHT aus, darum hier ValueError: Vorgabe mit "=" am Anfang,
    Listenwert mit "=", DataSetReference (dataset_ref). DateTime-Vorgabe nur ISO (JJJJ-MM-TT, auch mit THH:MM:SS);
    deutsche Schreibweise macht die Definition ungueltig. Integer ohne Vorgabe scheitert (Typfehler, keine Datei)."""
    if dataset_ref:
        raise ValueError("Auswahlliste aus zweiter Abfrage geht in Allplan nicht – Distinct-Prompt nehmen "
                         "(parameter(..., distinct='Feld')); gemessen: DataSetReference ergibt 'Parameter nicht angegeben', keine Datei")
    vorgaben = list(default) if isinstance(default, (list, tuple)) else ([] if default is None else [default])
    if len(vorgaben) > 1 and not multi:
        raise ValueError("Mehrere Vorgaben nur mit multi=True (Parameter %s)" % name)
    for wert in vorgaben:
        if str(wert).lstrip().startswith("="):
            raise ValueError("Allplan wertet Ausdrücke in Parameter-Vorgaben nicht aus – festen Wert setzen "
                             "(Parameter %s: %r)" % (name, wert))
        if datatype == "DateTime" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?", str(wert)):
            raise ValueError("DateTime-Vorgabe nur ISO (JJJJ-MM-TT), deutsche Schreibweise macht die Definition ungueltig "
                             "(Parameter %s: %r)" % (name, wert))
    if datatype == "Integer" and not vorgaben and not nullable:
        raise ValueError("Integer ohne Vorgabe scheitert in Allplan (Typfehler, keine Datei) - Vorgabe setzen oder nullable=True "
                         "(Parameter %s)" % name)
    for wert, _ in (werte or ()):
        if str(wert).lstrip().startswith("="):
            raise ValueError("Allplan wertet Ausdruecke in Auswahllisten nicht aus - feste Werte nennen (Parameter %s: %r)" % (name, wert))
    liste = ""
    if werte:
        liste = "<ValidValues><ParameterValues>%s</ParameterValues></ValidValues>" % "".join(
            "<ParameterValue><Value>%s</Value><Label>%s</Label></ParameterValue>" % (esc(w), esc(l)) for w, l in werte)
    if distinct:
        prompt = "Distinct(Fields!%s.Value)" % distinct
    xml = "<DataType>%s</DataType>" % datatype
    if nullable:
        xml += "<Nullable>true</Nullable>"
    if vorgaben:
        xml += "<DefaultValue><Values>%s</Values></DefaultValue>" % "".join("<Value>%s</Value>" % esc(w) for w in vorgaben)
    if allowblank:
        xml += "<AllowBlank>true</AllowBlank>"
    xml += "<Prompt>%s</Prompt>" % esc(prompt)
    if hidden:
        xml += "<Hidden>true</Hidden>"
    if multi:
        xml += "<MultiValue>true</MultiValue>"
    return '<ReportParameter Name="%s">%s%s</ReportParameter>' % (name, xml, liste)


def embedded(ordner):
    """Alle PNG eines Ordners als eingebettete Bilder (Name = Dateiname ohne Endung, '_'-Dateien ausgenommen)."""
    import base64
    teile = ""
    for datei in sorted(os.listdir(ordner)):
        if datei.endswith(".png") and not datei.startswith("_"):
            with open(os.path.join(ordner, datei), "rb") as handle:
                daten = base64.b64encode(handle.read()).decode("ascii")
            teile += ('<EmbeddedImage Name="%s"><MIMEType>image/png</MIMEType><ImageData>%s</ImageData></EmbeddedImage>'
                      % (datei[:-4], daten))
    return "<EmbeddedImages>%s</EmbeddedImages>" % teile if teile else ""


def report(pages, datasets, extra_params="", code="", footer_xml="", page_body_h=PAGE_BODY_H, foot_h=FOOT_H, labels=None,
           embedded_xml="", variablen=None, codemodules=None, classes=None, fliessend=False, fliess_h=None,
           footer_first=True, footer_last=True, header_xml="", header_h=1.2, header_first=True, header_last=True,
           standardparameter=True, body_breite=None):
    """pages: Liste von Seiten-Inhalten (ReportItems-XML, Lage relativ zur Seite). Jede Seite wird ein
    Rectangle in voller Seitenhoehe mit Seitenumbruch danach. labels: je Seite ein Titel fuer die
    Dokumentstruktur (im PDF als Lesezeichen).

    variablen: Liste (Name, Ausdruck) -> <Variables> am Report: einmal gerechnet, im Body und im Seitenfuss gleich
        (in Allplan gemessen; Variable aus Variable geht: Variables!V_Ges.Value). Gruppenvariablen sitzen in der Gruppe.
    codemodules: Liste von Assembly-Namen (z. B. System.Drawing, System.Windows.Forms; "System" selbst NICHT eintragen);
        classes: Liste (Klasse, Instanzname). Beides lief in Allplan (gemessen).
    fliessend=True: pages ist EIN ReportItems-Text (oder eine Liste davon) ohne Seiten fester Hoehe - die Elemente duerfen
        ueber Seiten laufen (Listen-Reports: Tabelle waechst mit den Daten); fliess_h ist die Nennhoehe des Bodys.
    footer_first/footer_last, header_xml/header_h/header_first/header_last: ob Fuss bzw. Kopf auf der ersten/letzten
        Seite stehen (False geht in Allplan, gemessen). Ein Kopfelement nur auf Seite 1 oder erst ab Seite 2 gelingt mit
        hidden="=Globals!PageNumber > 1" am Element.
    standardparameter=False: ohne die Allplan-Standardparameter (Project_Name ...) - fuer das Ziel eines Unterberichts,
        in dem nur eigene Parameter stehen (jeder mit <Prompt>). body_breite: Breite des Inhalts in cm (Vorgabe Blattbreite);
        ein Unterbericht-Ziel nimmt die Breite seines <Subreport>-Feldes."""
    with open(TEMPLATE, encoding="utf-8-sig") as handle:
        tpl = handle.read()
    sources = re.search(r"<DataSources>.*?</DataSources>", tpl, re.S).group(0)
    if standardparameter:
        params = re.search(r"<ReportParameters>.*?</ReportParameters>", tpl, re.S).group(0)
        params = params.replace("</ReportParameters>", extra_params + "</ReportParameters>")
    else:
        params = "<ReportParameters>%s</ReportParameters>" % extra_params if extra_params else ""
    if fliessend:
        inhalt = pages if isinstance(pages, str) else "".join(pages)
        body = "<Body><ReportItems>%s</ReportItems><Height>%s</Height><Style/></Body>" % (
            inhalt, cm(fliess_h if fliess_h is not None else page_body_h))
    else:
        items = ""
        for nr, inner in enumerate(pages):
            items += rect("Seite%d" % (nr + 1), nr * page_body_h, 0, PAGE_W, page_body_h, inner,
                          page_break=nr < len(pages) - 1, keep=True, label=labels[nr] if labels else None)
        body = "<Body><ReportItems>%s</ReportItems><Height>%s</Height><Style/></Body>" % (items, cm(len(pages) * page_body_h))
    footer = ("<PageFooter><Height>%s</Height><PrintOnFirstPage>%s</PrintOnFirstPage><PrintOnLastPage>%s</PrintOnLastPage>"
              "<ReportItems>%s</ReportItems><Style/></PageFooter>"
              % (cm(foot_h), "true" if footer_first else "false", "true" if footer_last else "false", footer_xml)) if footer_xml else ""
    header = ("<PageHeader><Height>%s</Height><PrintOnFirstPage>%s</PrintOnFirstPage><PrintOnLastPage>%s</PrintOnLastPage>"
              "<ReportItems>%s</ReportItems><Style/></PageHeader>"
              % (cm(header_h), "true" if header_first else "false", "true" if header_last else "false", header_xml)) if header_xml else ""
    page = ("<Page>%s%s<PageHeight>%s</PageHeight><PageWidth>%s</PageWidth><LeftMargin>0cm</LeftMargin><RightMargin>0cm</RightMargin>"
            "<TopMargin>0cm</TopMargin><BottomMargin>0cm</BottomMargin><Style/></Page>" % (header, footer, cm(PAGE_H), cm(PAGE_W)))
    code_xml = "<Code>%s</Code>" % esc(code or "' Bausatz")     # immer vorhanden: die Schriftwahl haengt ihre Funktion an
    if variablen:
        embedded_xml += "<Variables>%s</Variables>" % "".join(
            '<Variable Name="%s"><Value>%s</Value></Variable>' % (n, esc(a if a.startswith("=") else "=" + a)) for n, a in variablen)
    zusatz = ""
    if codemodules:
        zusatz += "<CodeModules>%s</CodeModules>" % "".join("<CodeModule>%s</CodeModule>" % esc(m) for m in codemodules)
    if classes:
        zusatz += "<Classes>%s</Classes>" % "".join(
            "<Class><ClassName>%s</ClassName><InstanceName>%s</InstanceName></Class>" % (esc(k), esc(i)) for k, i in classes)
    xml = ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<Report xmlns="%s" xmlns:rd="http://schemas.microsoft.com/SQLServer/reporting/reportdesigner">'
            "<Author>%s</Author><AutoRefresh>0</AutoRefresh>%s<DataSets>%s</DataSets>"
            "<ReportSections><ReportSection>%s<Width>%s</Width>%s</ReportSection></ReportSections>%s%s%s"
            "<Language>de-DE</Language>"   # Zahlen- und Datumsformat fest; sprache.py setzt fuer Englisch en-US
            "<ConsumeContainerWhitespace>true</ConsumeContainerWhitespace>%s<rd:ReportUnitType>Cm</rd:ReportUnitType>"
            "<rd:ReportID>%s</rd:ReportID></Report>"
            % (NS, esc(VERFASSER), sources, "".join(datasets), body, cm(body_breite or PAGE_W), page, params, code_xml, embedded_xml, zusatz,
               uuid.uuid4()))
    # Schrift: der Report waehlt beim Oeffnen die Soll-Schrift des Designs oder, wenn sie dem Rechner fehlt, den Ersatz
    return design.schrift_zur_laufzeit(xml, DESIGN, esc)


def render_argumente(rdlc, daten_json, ausgabe, parameter=None, pdf=False, datei_format=None, vollzugriff=True, dpi=110):
    """Aufruf des Anzeigeprogramms; bricht mit klarer Meldung ab, solange es nicht gebaut ist.
    parameter: weitere Parameterwerte als dict oder Liste (Name, Wert) - Wert eine Zeichenkette, bei Parametern mit mehreren
        Werten eine Liste (der Renderer bekommt Name=Wert1|Wert2), None setzt Nothing (Name=~null); Project_Name=Musterprojekt
        ist vorbelegt und laesst sich hier ueberschreiben.
    pdf: zusaetzlich <name>.pdf; datei_format: 'xlsx' | 'docx' zusaetzlich als Datei (der Renderer kennt auch 'pdf').
    vollzugriff: der Code des Reports laeuft mit vollen Rechten wie in Allplan (Vorgabe). Noetig, seit jeder Report beim Oeffnen
    die installierten Schriften abfragt (design.schrift_zur_laufzeit): ohne volle Rechte zeigt die Vorschau die Ersatzschrift."""
    if not os.path.isfile(RENDER):
        sys.exit("FEHLER: Das Anzeigeprogramm fehlt (%s). Einmal bauen: "
                 "powershell -ExecutionPolicy Bypass -File werkzeug\render\build.ps1" % RENDER)
    args = [RENDER, rdlc, daten_json, ausgabe, "--dpi=%d" % dpi]
    if pdf:
        args.append("--pdf")
    if datei_format:
        args.append("--format=%s" % datei_format)
    if vollzugriff:
        args.append("--vollzugriff")
    args.append("Project_Name=Musterprojekt")
    for name, wert in (parameter.items() if isinstance(parameter, dict) else (parameter or ())):
        if wert is None:
            wert = "~null"
        elif isinstance(wert, (list, tuple)):
            wert = "|".join(str(w) for w in wert)
        args.append("%s=%s" % (name, wert))
    return args


def rendern(rdlc, daten_json, ausgabe, **optionen):
    """Rendert kopflos nach <ausgabe>; ein Fehler des Anzeigeprogramms beendet das Skript mit Code 1.
    optionen wie bei render_argumente (parameter, pdf, datei_format, vollzugriff, dpi)."""
    sys.stdout.flush()
    code = subprocess.call(render_argumente(rdlc, daten_json, ausgabe, **optionen))
    if code != 0:
        sys.exit("FEHLER: Rendern fehlgeschlagen (Code %d)." % code)


def save(path, xml):
    design.sperre(DESIGN)       # kein Report, solange das Design nicht geklaert ist (python master/design.py --fragen)
    with open(path, "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write(xml)
