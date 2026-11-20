# -*- coding: utf-8 -*-
"""Sprachschalter: macht aus einem fertig gebauten deutschen Report (.rdlc) die englische Fassung.

    python sprache.py --sammeln             alle Texte der gebauten Master-Reports in die Tabellen sprache/en/*.json
                                            eintragen (vorhandene Uebersetzungen bleiben; neue stehen auf null).
                                            Ist eine Quelle nicht gebaut, bleiben ihre Eintraege unveraendert.
    python sprache.py --sammeln out/Mein.rdlc    die Texte eines EIGENEN Reports, die noch in keiner Tabelle stehen,
                                            nach sprache/en/eigene.json eintragen (null = noch zu uebersetzen)
    python sprache.py --en                  jeder Report in out/, dessen Name nicht mit "_" beginnt -> out/eng/
                                            (eine Datei mit fehlenden Texten wird ausgelassen und gemeldet; Rueckgabe 1)
    python sprache.py --en out/_Seite3.rdlc --lax     einzelne Datei; fehlende Texte bleiben deutsch (nur fuer die Vorschau)
    python sprache.py --offen               zeigt, was noch nicht uebersetzt ist

Wie es arbeitet: Uebersetzt wird das fertige XML, nicht der Bausatz - so gilt der Schalter fuer jeden Report, auch
fuer einen per build_auswahl.py gestapelten. Erfasst werden (a) feste Texte in <Value>, <Caption>, <Prompt>, <Label>,
<ToolTip>, <DocumentMapLabel>, <NoRowsMessage> und (b) jede Zeichenkette "..." in einem Ausdruck (=...) oder im VB-Code. Dieselbe
Zeichenkette wird ueberall gleich ersetzt: "Beton" im VB-Code (Code.MatArt) und "Beton" im Vergleich eines Ausdrucks
werden beide zu "Concrete" - Schluessel und Anzeige bleiben dadurch gleich.

Zwei Kniffe im Bausatz: Ein geschuetztes Leerzeichen (U+00A0) am Ende macht aus demselben deutschen Wort einen
eigenen Schluessel - fuer die Mehrzahl ("Fenster" = Window, "Fenster" + U+00A0 = Windows) oder eine Kurzform, die
nur das Englische braucht ("Beton" + U+00A0 = Concr.). Namen von Tabellen und Gruppen bleiben stehen, wo sie Bereich
einer Summenfunktion sind (Sum(x, "S3_TbTorte")).

Tabellen: { "deutscher Text": "english text" }. Sonderwerte: "=" heisst "bleibt, wie es ist" (Wortstaemme zum
Erkennen von Modelldaten, Einheiten, technische Namen), null heisst "noch offen". Zahlen- und Datumsformat folgen
der Report-Sprache (<Language>): de-DE bzw. en-US.

Was NICHT uebersetzt wird: alles, was aus dem Modell kommt (Raumnamen, Materialien, Bauteilnamen).
"""
import glob
import html
import json
import os
import re
import sys
import uuid
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "out"))
TABELLEN = os.path.join(HERE, "sprache", "en")
TEXT_TAGS = {"Value", "Caption", "Prompt", "Label", "ToolTip", "DocumentMapLabel", "NoRowsMessage"}
AUSGELASSEN = ("DataSets", "DataSources", "EmbeddedImages")       # Abfrage, Verbindung, Bilddaten: nie anfassen
BLATT = re.compile(r"<([A-Za-z:]+)>([^<]+)</\1>")
LITERAL = re.compile(r'"((?:[^"]|"")*)"')
BUCHSTABE = re.compile(r"[A-Za-zÄÖÜäöüß]")
FARBE = re.compile(r"#[0-9A-Fa-f]{6}(?![0-9A-Fa-f])")
SCHRIFTLISTE = re.compile(r"Dim (?:soll|ersatz)\(\) As String = \{([^}]*)\}")     # design.schrift_zur_laufzeit
# Zeichenketten, die technisch sind und nie uebersetzt werden (Formate, Stilwerte, Schriften)
TECHNISCH = re.compile(r"^(#[0-9A-Fa-f]{6,8}|[NFPCDEG]\d?|\d+(\.\d+)?(pt|cm|mm|in)|Segoe UI( Light| Semibold| Symbol)?|"
                       r"Bold|Normal|Italic|Solid|None|Transparent|True|False|Left|Right|Center|Top|Middle|Bottom|Default|"
                       r"Light|Semibold|White|Black|Zoom:|,Mark:|AllplanReport)$")
# Lesezeichen und Seitenlabels mehrseitiger Reports (build_auswahl.py): "<Titel> - Seite 2". Eigener Tabelleneintrag je Seite
# waere eine Schleife ohne Ende; darum zaehlt nur <Titel>, "- Seite n" wird zu "- page n".
SEITENLABEL = re.compile(r"^(.+) - Seite (\d+)$", re.S)
SPRACHE_DE, SPRACHE_EN = "<Language>de-DE</Language>", "<Language>en-US</Language>"


AGGREGAT = {"Sum", "Count", "CountDistinct", "CountRows", "First", "Last", "Max", "Min", "Avg", "RunningValue",
            "RowNumber", "Lookup", "LookupSet", "MultiLookup", "InScope", "Previous", "Aggregate", "StDev", "Var"}


def _namen(xml):
    """Namen von Elementen, Gruppen, Bildern: als Bereichsangabe einer Summenfunktion bleiben sie stehen."""
    return set(re.findall(r'\bName="([^"]+)"', xml))


def _bleibt(text, im_code=False):
    if not BUCHSTABE.search(text) or TECHNISCH.match(text.strip()):
        return True
    return im_code and text == text.lower()          # im VB-Code: Wortstaemme zum Erkennen von Modelldaten


def _mit_farben(de, woerter):
    """Uebersetzung fuer einen Text, der einen Farbwert des Designs traegt (<font color='#...'>): die Tabelle kennt ihn mit den
    Farben des Hausdesigns. Verglichen wird ohne die Farbwerte; die Uebersetzung bekommt die Farben des Reports zurueck."""
    farben = FARBE.findall(de)
    if not farben:
        return None
    muster = FARBE.sub("#", de)
    for schluessel, en in woerter.items():
        if "#" in schluessel and FARBE.sub("#", schluessel) == muster:
            if en in (None, "="):
                return en
            rest = list(farben)
            return FARBE.sub(lambda m: rest.pop(0) if rest else m.group(0), en)
    return None


def _ist_bereich(ausdruck, treffer, namen):
    """True, wenn die Zeichenkette das letzte Argument einer Summenfunktion ist und ein Elementname:
    Sum(x, "S3_TbTorte"). Dieselbe Zeichenkette als angezeigter Text (IIf(a, b, "Summe")) wird uebersetzt."""
    if treffer.group(1) not in namen or not ausdruck[treffer.end():].lstrip().startswith(")"):
        return False
    tiefe = 0
    for pos in range(treffer.start() - 1, -1, -1):
        zeichen = ausdruck[pos]
        if zeichen == ")":
            tiefe += 1
        elif zeichen == "(":
            if tiefe == 0:
                davor = re.search(r"([A-Za-z_.]+)\s*$", ausdruck[:pos])
                return bool(davor) and davor.group(1).split(".")[-1] in AGGREGAT
            tiefe -= 1
    return False


def _teile(xml):
    """Zerlegt das XML in (Art, Text)-Stuecke. Art: 'roh' (unveraendert), 'fest', 'ausdruck', 'code'."""
    sperre = re.compile("|".join(r"<%s>.*?</%s>" % (t, t) for t in AUSGELASSEN), re.S)
    pos = 0
    for block in sperre.finditer(xml):
        yield from _teile_offen(xml[pos:block.start()])
        yield "roh", block.group(0)
        pos = block.end()
    yield from _teile_offen(xml[pos:])


def _teile_offen(stueck):
    pos = 0
    for treffer in BLATT.finditer(stueck):
        tag, inhalt = treffer.group(1), treffer.group(2)
        klar = html.unescape(inhalt)
        if tag == "Code":
            art = "code"
        elif klar.lstrip().startswith("="):
            art = "ausdruck"
        elif tag in TEXT_TAGS:
            art = "fest"
        else:
            continue
        yield "roh", stueck[pos:treffer.start(2)]
        yield art, inhalt
        pos = treffer.end(2)
    yield "roh", stueck[pos:]


def _ohne_seite(wort, woerter):
    """'<X> - Seite <n>' ohne eigenen Tabelleneintrag: (X, n); sonst (wort, None)."""
    treffer = SEITENLABEL.match(wort)
    if treffer and wort not in woerter:
        return treffer.group(1), treffer.group(2)
    return wort, None


def texte(xml, woerter=None):
    """Alle uebersetzbaren Zeichenketten eines Reports, in der Reihenfolge des ersten Auftretens.
    Ein Seitenlabel '<X> - Seite <n>' ohne eigenen Eintrag zaehlt als X (ein Eintrag statt n)."""
    namen, gefunden = _namen(xml), {}
    woerter = tabelle() if woerter is None else woerter
    for art, inhalt in _teile(xml):
        if art == "roh":
            continue
        klar = html.unescape(inhalt)
        if art == "fest":
            klar = _ohne_seite(klar, woerter)[0]
            if not _bleibt(klar):
                gefunden.setdefault(klar, None)
        else:
            for treffer in LITERAL.finditer(klar):
                wort = _ohne_seite(treffer.group(1).replace('""', '"'), woerter)[0]
                if not _bleibt(wort, im_code=(art == "code")) and not _ist_bereich(klar, treffer, namen):
                    gefunden.setdefault(wort, None)
    return list(gefunden)


def tabelle():
    """Alle Tabellen zusammen. Derselbe Schluessel mit zwei verschiedenen Uebersetzungen ist ein Fehler."""
    gesamt, quelle = {}, {}
    for pfad in sorted(glob.glob(os.path.join(TABELLEN, "*.json"))):
        with open(pfad, encoding="utf-8") as handle:
            for de, en in json.load(handle).items():
                if de in gesamt and en is not None and gesamt[de] is not None and gesamt[de] != en:
                    raise SystemExit("Widerspruch: %r steht in %s als %r und in %s als %r" % (
                        de, quelle[de], gesamt[de], os.path.basename(pfad), en))
                if gesamt.get(de) is None:
                    gesamt[de], quelle[de] = en, os.path.basename(pfad)
    return gesamt


def uebersetzen(xml, woerter):
    """Liefert (englisches XML, Liste der fehlenden Texte)."""
    namen, fehlend, teile = _namen(xml), [], []
    # Schriftnamen des Designs (Hausschrift oder die des Kunden) stehen in der Funktion Schrift und bleiben, wie sie sind
    schriften = set()
    for liste in SCHRIFTLISTE.findall(html.unescape(xml)):
        schriften.update(name.replace('""', '"') for name in LITERAL.findall(liste))

    def englisch(de, im_code=False):
        if _bleibt(de, im_code) or de in schriften:
            return de
        kopf, nummer = _ohne_seite(de, woerter)
        if nummer is not None:
            return "%s - page %s" % (englisch(kopf, im_code), nummer)
        en = woerter.get(de)
        if en is None:
            en = _mit_farben(de, woerter)
        if en is None:
            fehlend.append(de)
            return de
        return de if en == "=" else en

    for art, inhalt in _teile(xml):
        if art == "roh":
            teile.append(inhalt)
        elif art == "fest":
            teile.append(escape(englisch(html.unescape(inhalt))))
        else:
            klar = html.unescape(inhalt)
            neu = LITERAL.sub(lambda m, ausdruck=klar, code=(art == "code"): m.group(0) if _ist_bereich(ausdruck, m, namen)
                              else '"%s"' % englisch(m.group(1).replace('""', '"'), code).replace('"', '""'), klar)
            teile.append(escape(neu))
    ergebnis = "".join(teile)
    if SPRACHE_DE in ergebnis:
        ergebnis = ergebnis.replace(SPRACHE_DE, SPRACHE_EN)
    # Jede Datei braucht ihre eigene Kennung: die englische bekommt eine feste, aus der deutschen abgeleitete
    kennung = re.search(r"<rd:ReportID>([^<]+)</rd:ReportID>", ergebnis)
    if kennung:
        try:
            neu = uuid.uuid5(uuid.UUID(kennung.group(1)), "en")
        except ValueError:
            neu = uuid.uuid5(uuid.NAMESPACE_URL, kennung.group(1) + "/en")
        ergebnis = ergebnis.replace(kennung.group(0), "<rd:ReportID>%s</rd:ReportID>" % neu)
    return ergebnis, sorted(set(fehlend))


def _lesen(pfad):
    with open(pfad, encoding="utf-8", newline="") as handle:
        return handle.read()


def _gruppen():
    """Quelle je Tabelle: Einzelseiten des Masters und die Begleit-Reports. Liefert (gebaute Quellen, Namen der fehlenden)."""
    quellen = [("s%02d" % n, os.path.join(OUT, "_Seite%d.rdlc" % n)) for n in range(1, 11)]
    quellen += [(name, os.path.join(OUT, datei)) for name, datei in (
        ("grundriss", "Report_Master_Grundriss.rdlc"), ("abwicklung", "Report_Master_Abwicklung.rdlc"),
        ("wandbelag", "Report_Master_Wandbelag.rdlc"), ("bewehrung", "Report_Master_Bewehrung.rdlc"),
        ("planliste", "Report_Master_Planliste.rdlc"), ("listen", "Report_Master_Listen.rdlc"),
        ("auswahl", "Report_Auswahl_Beispiel.rdlc"))]
    return ([(name, pfad) for name, pfad in quellen if os.path.isfile(pfad)],
            [name for name, pfad in quellen if not os.path.isfile(pfad)])


def sammeln():
    """Traegt jeden Text in genau eine Tabelle ein: Texte aus zwei oder mehr Quellen nach 00_gemeinsam.json.
    Solange Quellen fehlen, geht nichts verloren: Eintraege, die in keiner gebauten Quelle stehen, bleiben, wo sie sind."""
    os.makedirs(TABELLEN, exist_ok=True)
    bekannt = tabelle()
    gebaut, fehlt = _gruppen()
    je_quelle = {name: texte(_lesen(pfad), bekannt) for name, pfad in gebaut}
    anzahl = {}
    for liste in je_quelle.values():
        for wort in liste:
            anzahl[wort] = anzahl.get(wort, 0) + 1
    ziel = {"00_gemeinsam": [w for w in anzahl if anzahl[w] > 1]}
    for name, liste in je_quelle.items():
        ziel[name] = [w for w in liste if anzahl[w] == 1]
    for name, liste in ziel.items():
        pfad = os.path.join(TABELLEN, name + ".json")
        eintraege = {w: bekannt.get(w) for w in liste}
        if fehlt and os.path.isfile(pfad):
            with open(pfad, encoding="utf-8") as handle:
                for wort, en in json.load(handle).items():
                    if wort not in anzahl:
                        eintraege[wort] = en
        with open(pfad, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(eintraege, handle, ensure_ascii=False, indent=1)
        offen = sum(1 for en in eintraege.values() if en is None)
        print("%-16s %4d Texte, %4d offen" % (name, len(eintraege), offen))
    if fehlt:
        print("Hinweis: nicht gebaut, Eintraege deshalb unveraendert: %s" % ", ".join(fehlt))


def sammeln_eigene(dateien):
    """Texte eigener Reports, die noch in keiner Tabelle stehen, nach eigene.json (vorhandene Eintraege bleiben)."""
    os.makedirs(TABELLEN, exist_ok=True)
    pfad = os.path.join(TABELLEN, "eigene.json")
    eigene = {}
    if os.path.isfile(pfad):
        with open(pfad, encoding="utf-8") as handle:
            eigene = json.load(handle)
    bekannt = tabelle()
    neu = 0
    for datei in dateien:
        for wort in texte(_lesen(datei), bekannt):
            if wort not in bekannt and wort not in eigene:
                eigene[wort] = None
                neu += 1
    with open(pfad, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(eigene, handle, ensure_ascii=False, indent=1)
    offen = sum(1 for wert in eigene.values() if wert is None)
    print("%s: %d neue Texte, %d offen (null durch die englische Fassung ersetzen)" % (pfad, neu, offen))


def main():
    dateien = [a for a in sys.argv[1:] if not a.startswith("--")]
    fehlt = [a for a in dateien if not os.path.isfile(a)]
    if fehlt:
        sys.exit("FEHLER: Datei nicht gefunden: %s" % ", ".join(fehlt))
    if "--sammeln" in sys.argv:
        return sammeln_eigene(dateien) if dateien else sammeln()
    woerter = tabelle()
    dateien = dateien or sorted(p for p in glob.glob(os.path.join(OUT, "*.rdlc")) if not os.path.basename(p).startswith("_"))
    if "--offen" in sys.argv:
        for pfad in dateien:
            fehlend = uebersetzen(_lesen(pfad), woerter)[1]
            print("%-40s %d offen" % (os.path.basename(pfad), len(fehlend)))
            for wort in fehlend:
                print("    %r" % wort)
        return None
    if "--en" in sys.argv:
        os.makedirs(os.path.join(OUT, "eng"), exist_ok=True)
        ausgelassen = []
        for pfad in dateien:
            xml, fehlend = uebersetzen(_lesen(pfad), woerter)
            if fehlend and "--lax" not in sys.argv:
                ausgelassen.append(os.path.basename(pfad))
                print("AUSGELASSEN %s: %d Texte ohne Uebersetzung, z. B.: %s" % (
                    os.path.basename(pfad), len(fehlend), "; ".join(fehlend[:8])))
                continue
            ziel = os.path.join(OUT, "eng", os.path.basename(pfad))
            with open(ziel, "w", encoding="utf-8", newline="") as handle:
                handle.write(xml)
            print(ziel, "(%d Texte noch deutsch)" % len(fehlend) if fehlend else "")
        if ausgelassen:
            sys.exit("FEHLER: %d von %d Dateien nicht uebersetzt (%s). Je Datei: python master/sprache.py --sammeln out/<Datei>.rdlc, "
                     "die Eintraege in master/sprache/en/eigene.json englisch fuellen, dann --en wiederholen."
                     % (len(ausgelassen), len(dateien), ", ".join(ausgelassen)))
        return None
    print(__doc__)
    return None


if __name__ == "__main__":
    main()
