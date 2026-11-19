# -*- coding: utf-8 -*-
"""Masse der Bausteine des Masters: Hoehe und Breite, damit build_auswahl.py Bausteine frei stapeln kann.

    python masse.py          Selbsttest: Tabelle gegen das Register und gegen das gebaute XML
    python masse.py --md     schreibt zusaetzlich out/masse.md

MASSE[kennung] = (hoehe_cm, breitenklasse). Die Hoehe ist der Platz, den der Baustein samt Abschnittskopf und
Etikett belegt, mit kleiner Reserve; der Zwischenraum zum naechsten Baustein kommt beim Stapeln dazu.
Die Breite ist die, mit der die Seitendatei den Baustein ruft - die Bausteine sind darauf gebaut.
Stimmt eine Hoehe nicht mehr (Seitendatei wurde geaendert), meldet der Selbsttest es mit der gemessenen Zahl.
"""
import importlib
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SEITEN = os.path.join(HERE, "seiten")
sys.path.insert(0, HERE)
sys.path.insert(0, SEITEN)

import bausteine as b  # noqa: E402
import core as c  # noqa: E402

MD_ZIEL = os.path.normpath(os.path.join(HERE, "..", "out", "masse.md"))

# Breitenklassen in cm. Zwei Bausteine stehen nebeneinander, wenn ihre Klassen zusammen eine Zeile fuellen.
BREITEN = {"voll": c.CONTENT_W, "halb": 8.8, "breit": 10.4, "zweidrittel": 10.8, "schmal": 7.2, "drittel": 6.6}

MASSE = {
    "B010": (5.70, "zweidrittel"),
    "B020": (9.10, "voll"),
    "B030": (4.60, "voll"),
    "B040": (7.65, "halb"),
    "B050": (4.90, "halb"),
    "B060": (2.60, "halb"),
    "B070": (2.45, "voll"),
    "D010": (5.70, "breit"),
    "D020": (5.70, "schmal"),
    "D030": (7.60, "halb"),
    "D040": (7.60, "halb"),
    "D050": (7.60, "halb"),
    "D060": (7.60, "halb"),
    "D070": (7.60, "halb"),
    "D080": (7.60, "halb"),
    "D090": (7.75, "halb"),
    "D100": (7.75, "halb"),
    "D110": (7.75, "halb"),
    "D120": (7.75, "halb"),
    "D130": (7.75, "halb"),
    "D140": (7.75, "halb"),
    "K010": (1.80, "voll"),
    "K020": (3.10, "voll"),
    "K030": (4.60, "voll"),
    "K040": (3.75, "voll"),
    "M010": (5.70, "drittel"),
    "M020": (6.15, "voll"),
    "M030": (6.05, "halb"),
    "M040": (5.95, "halb"),
    "M050": (6.80, "halb"),
    "M060": (6.80, "halb"),
    "T010": (6.70, "voll"),
    "T020": (7.85, "halb"),
    "T030": (8.15, "halb"),
    "T040": (7.10, "voll"),
    "T050": (7.10, "voll"),
    "T060": (9.30, "voll"),
    "T070": (9.30, "voll"),
    "U010": (1.95, "voll"),
    "U020": (7.10, "voll"),
    "U030": (6.65, "voll"),
    "U040": (5.35, "voll"),
    "X010": (7.65, "halb"),
    "X020": (7.65, "halb"),
    "X030": (5.25, "voll"),
    "X040": (6.15, "voll"),
    "X050": (5.50, "halb"),
    "X060": (5.50, "halb"),
    "X080": (12.05, "voll"),
    "X090": (8.05, "voll"),
}

# Zweite Anmeldungen derselben Funktion: die Kennung steht im Register, gebaut wird aber dieselbe Funktion.
TEIL_VON = {"T050": "T040", "T070": "T060"}

# Bausteine mit Besonderheiten beim Stapeln (Text fuer das Verzeichnis).
VERMERK = {
    "T050": "Teil von T040 (gleiche Funktion, nicht zusammen mit T040 wählbar)",
    "T070": "Teil von T060 (gleiche Funktion, nicht zusammen mit T060 wählbar)",
    "B060": "Logo kommt aus Allplans Parametern Company_Logo und Display_Logo; ohne Logo steht ein Hinweis",
    "X080": "über ein halbes Blatt hoch",
    "D010": "steht auf der Master-Seite 1 neben D020",
    "D020": "steht auf der Master-Seite 1 neben D010",
    "M010": "steht auf der Master-Seite 1 neben B010",
    "B010": "steht auf der Master-Seite 1 neben M010",
}

STANDARD_PARAMETER = {"Project_Name", "Date"}   # liefert Allplan immer; kein Grund, sie je Baustein zu nennen


def register():
    """Alle Bausteine der Master-Seiten (ohne Seite 10, ohne Begleit-Reports): Kennung -> (Name, Modul, Funktion)."""
    for datei in sorted(os.listdir(SEITEN)):
        if re.fullmatch(r"s\d\d_.*\.py", datei) and not datei.startswith("s10"):
            importlib.import_module(datei[:-3])
    return {k: v for k, v in b.REGISTER.items() if re.fullmatch(r"s\d\d_.*", v[1]) and not v[1].startswith("s10")}


def breite(kennung):
    return BREITEN[MASSE[kennung][1]]


def bau(kennung, top, left):
    """XML des Bausteins mit seiner Breite an der Stelle (top, left)."""
    _name, modul, funktion = b.REGISTER[kennung]
    return getattr(importlib.import_module(modul), funktion)(top, left, breite(kennung))


def gemessene_hoehe(kennung):
    """Unterkante des tiefsten Elements, wenn der Baustein bei top=0 gebaut wird (Etikett eingeschaltet)."""
    aus = b.ETIKETT_AN[0]
    b.ETIKETT_AN[0] = True
    try:
        xml = bau(kennung, 0.0, 0.0)
    finally:
        b.ETIKETT_AN[0] = aus
    ns = "{http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition}"
    wurzel = ET.fromstring("<r xmlns='%s' xmlns:rd='urn:rd'>%s</r>" % (ns[1:-1], xml))
    unten = 0.0
    for el in wurzel:
        top, hoehe = el.find(ns + "Top"), el.find(ns + "Height")
        if top is not None and hoehe is not None:
            unten = max(unten, float(top.text[:-2]) + float(hoehe.text[:-2]))
    return unten


def braucht(kennung):
    """Report-Parameter, die der Baustein im Ausdruck benutzt (Textsuche im erzeugten XML)."""
    namen = set(re.findall(r"Parameters!(\w+)\.Value", bau(kennung, 0.0, 0.0))) - STANDARD_PARAMETER
    return sorted(namen)


def selbsttest():
    """Meldet fehlende und ueberzaehlige Kennungen und Hoehen, die kleiner sind als das gebaute XML."""
    im_register = register()
    fehler = ["FEHLT in masse.py: %s" % k for k in sorted(set(im_register) - set(MASSE))]
    fehler += ["UEBERZAEHLIG in masse.py (nicht im Register): %s" % k for k in sorted(set(MASSE) - set(im_register))]
    hinweise = []
    for kennung in sorted(set(MASSE) & set(im_register)):
        if kennung in TEIL_VON and TEIL_VON[kennung] not in MASSE:
            fehler.append("%s ist Teil von %s, das fehlt" % (kennung, TEIL_VON[kennung]))
        gemessen = gemessene_hoehe(kennung)
        hoehe = MASSE[kennung][0]
        if gemessen > hoehe:
            fehler.append("ZU NIEDRIG %s: Tabelle %.2f cm, gemessen %.2f cm" % (kennung, hoehe, gemessen))
        elif hoehe - gemessen > 0.4:
            hinweise.append("%s: Tabelle %.2f cm, gemessen %.2f cm (grosszuegig)" % (kennung, hoehe, gemessen))
    for zeile in fehler + hinweise:
        print(zeile)
    print("%s: %d Kennungen im Register, %d in der Tabelle, %d Fehler, %d Hinweise"
          % ("OK" if not fehler else "FEHLER", len(im_register), len(MASSE), len(fehler), len(hinweise)))
    return not fehler


def tabelle_md():
    """Markdown-Tabelle Kennung | Name | Höhe cm | Breite | braucht | Hinweis; braucht entsteht beim Aufruf aus dem XML."""
    zeilen = ["| Kennung | Name | Höhe cm | Breite | braucht | Hinweis |", "|---|---|---|---|---|---|"]
    for kennung in sorted(MASSE):
        hoehe, klasse = MASSE[kennung]
        name = b.REGISTER[kennung][0]
        brauche = ", ".join("`%s`" % p for p in braucht(kennung)) or "–"
        zeilen.append("| %s | %s | %s | %s (%s cm) | %s | %s |" % (
            kennung, name, ("%.2f" % hoehe).replace(".", ","), klasse, ("%g" % BREITEN[klasse]).replace(".", ","), brauche,
            VERMERK.get(kennung, "")))
    return chr(10).join(zeilen)


def schreibe_md():
    kopf = ["# Maße der Bausteine", "",
            "Erzeugt von `master/masse.py --md` - nicht von Hand ändern.",
            "Höhe = Platz samt Abschnittskopf und Etikett (mit kleiner Reserve). Breite = die Breite, für die der Baustein gebaut ist;",
            "zwei Bausteine, die zusammen eine Zeile füllen (halb + halb, breit + schmal, drittel + zweidrittel), stehen nebeneinander.",
            "„braucht“ = Report-Parameter, die der Baustein im Ausdruck benutzt (Project_Name und Date liefert Allplan immer).",
            "Report aus Kennungen bauen: `python master/build_auswahl.py --bausteine=K010,D040,T020 [--titel=\"…\"] [--ohne-etikett] [--render]`.", ""]
    os.makedirs(os.path.dirname(MD_ZIEL), exist_ok=True)
    with open(MD_ZIEL, "w", encoding="utf-8", newline=chr(10)) as handle:
        handle.write(chr(10).join(kopf) + chr(10) + tabelle_md() + chr(10))
    return MD_ZIEL


if __name__ == "__main__":
    gut = selbsttest()
    if "--md" in sys.argv:
        print(schreibe_md())
    sys.exit(0 if gut else 1)
