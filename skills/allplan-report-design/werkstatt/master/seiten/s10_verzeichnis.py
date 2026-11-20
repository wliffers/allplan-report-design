# -*- coding: utf-8 -*-
"""Seite 10 - Verzeichnis der Bausteine. Entsteht beim Bauen aus dem Register (b.REGISTER): jede mit
@b.baustein angemeldete Funktion erscheint mit Kennung, Name und Seite. Wer einen Report bestellt, nennt
die Kennungen - Anwender, Agent und Skill reden ueber dasselbe."""
import importlib
import os
import sys

import bausteine as b
import core as c

TITEL = "Verzeichnis der Bausteine"

GRUPPEN = [("K", "Kennzahlen und Kernaussagen"), ("D", "Diagramme"), ("M", "Messanzeigen"), ("T", "Tabellen"),
           ("B", "Bilder"), ("U", "Bedienung"), ("X", "Text, Symbole, Flächen")]
ZEILE_MAX, ZEILE_MIN = 0.40, 0.34   # Zeilenabstand in cm: so locker wie moeglich, nie enger als 8 pt lesbar
KOPF = 0.58          # Hoehe einer Gruppenueberschrift
LUFT = 0.3           # Abstand vor einer Gruppenueberschrift
ANFANG = 4.95        # Oberkante des Verzeichnisses (unter dem Einleitungssatz)
BESTELL_H = 4.0      # Hoehe des Blocks "So bestellen" (Abschnittskopf + Karten)
PRO_ZEILE = 5        # Kennungen je Zeile in der kompakten Begleit-Report-Zeile


def _register_fuellen():
    """Bei einem Einzelbau (--nur=10) sind die anderen Seiten noch nicht gelaufen: dann hier anmelden lassen."""
    hier = os.path.dirname(os.path.abspath(__file__))
    for datei in sorted(os.listdir(hier)):
        if datei[:1] == "s" and datei[1:3].isdigit() and datei.endswith(".py") and not datei.startswith("s10"):
            importlib.import_module(datei[:-3])
    for ordner, modul in (("grundriss", "build_grundriss"), ("abwicklung", "build_abwicklung"), ("abwicklung", "build_wandbelag"),
                          ("bewehrung", "build_bewehrung"), ("projektlisten", "build_planliste"), ("listen", "build_listen")):
        pfad = os.path.normpath(os.path.join(hier, "..", ordner))
        if os.path.isfile(os.path.join(pfad, modul + ".py")):
            if pfad not in sys.path:
                sys.path.insert(0, pfad)
            try:
                importlib.import_module(modul)
            except Exception:  # pylint: disable=broad-except
                pass   # ein Begleit-Report ist ein eigenes Bauskript; fehlt er, fehlen nur seine Zeilen


def _ort(modul):
    """Wo der Baustein zu sehen ist: Seitennummer des Masters oder der Begleit-Report."""
    if modul[:1] == "s" and modul[1:3].isdigit():
        return "Seite %d" % int(modul[1:3])
    return "Begleit-Report"


def eintraege():
    _register_fuellen()
    nach_gruppe = {}
    for kennung, (name, modul, _funktion) in sorted(b.REGISTER.items()):
        nach_gruppe.setdefault(kennung[:1], []).append((kennung, name, _ort(modul), modul))
    return nach_gruppe


def _posten(bloecke):
    """Flache Liste (Art, Inhalt, Gruppentitel, Zeilen): Gruppenkopf, dann je Eintrag eine Zeile."""
    posten = []
    for titel, zeilen in bloecke:
        posten.append(("kopf", titel, titel, 0))
        posten += [(art, inhalt, titel, n) for art, inhalt, n in zeilen]
    return posten


def _hoehe(teil, p):
    """Hoehe eines Spaltenstuecks bei Zeilenabstand p; vor einer Gruppenueberschrift (ausser oben) steht LUFT."""
    h = 0.0
    for nr, (art, _inhalt, _titel, n) in enumerate(teil):
        h += KOPF + (LUFT if nr else 0) if art in ("kopf", "forts") else p * n
    return h


def _teilen(bloecke, p):
    """Zwei Spalten mit moeglichst gleicher Hoehe. Die Trennung darf mitten in einer Gruppe liegen; die Gruppe
    bekommt oben in der rechten Spalte dann eine Fortsetzungs-Ueberschrift. Liefert (links, rechts, Hoehe)."""
    posten = _posten(bloecke)
    beste = None
    for s in range(1, len(posten)):
        if posten[s - 1][0] == "kopf":
            continue                                   # eine Ueberschrift nie allein am Spaltenende
        rechts = posten[s:] if posten[s][0] == "kopf" else [("forts", posten[s][2], posten[s][2], 0)] + posten[s:]
        hoehe = max(_hoehe(posten[:s], p), _hoehe(rechts, p))
        if beste is None or hoehe < beste[2]:
            beste = (posten[:s], rechts, hoehe)
    return beste


def _spalte(prefix, left, w, posten, p):
    """Eine Spalte des Verzeichnisses: Gruppenueberschrift, darunter die Zeilen Kennung | Name | Ort."""
    gross, klein = (8.5, 7.5) if p >= 0.38 else (8, 7)
    xml, top = "", 0.0
    for nr, (art, inhalt, titel, n) in enumerate(posten):
        q = "%s%d" % (prefix, nr)
        if art in ("kopf", "forts"):
            top += LUFT if nr else 0
            kopf = c.run(titel.upper(), 7, c.MUTED, c.F_SEMI)
            if art == "forts":
                kopf += c.run("  · fortgesetzt", 7, c.MUTED, c.F)
            xml += c.text(q + "_h", top, left, w, KOPF - 0.1, c.para([kopf]) if art == "forts" else kopf, valign="Bottom",
                          border_xml=c.edge(["Bottom"], c.INK, "1pt"), pad=(0, 0, 0, 2))
            top += KOPF
            continue
        linie = c.edge(["Bottom"], c.HAIR, "0.5pt")
        if art == "kompakt":                            # Begleit-Report: eine Zeile "Name | K050 · B080 · ..."
            name, kennungen = inhalt
            xml += c.text(q + "_n", top, left, 2.4, p * n, c.run(name, gross, c.INK, c.F_SEMI), valign="Middle", border_xml=linie)
            xml += c.text(q + "_k", top, left + 2.4, w - 2.4, p * n, c.run("\u00a0·  ".join(kennungen), gross, c.BLUE, c.F_SEMI),
                          valign="Middle", border_xml=linie)
        else:
            kennung, name, ort = inhalt
            xml += c.text(q + "_k", top, left, 1.2, p, c.run(kennung, gross, c.BLUE, c.F_SEMI), valign="Middle", border_xml=linie)
            name_w, groesse = w - 3.2, gross
            while groesse > 7 and b.textbreite(name, groesse) * 1.1 > name_w:     # langer Name: Schrift kleiner statt Umbruch
                groesse -= 0.5
            xml += c.text(q + "_n", top, left + 1.2, name_w, p, c.run(name, groesse, c.INK), valign="Middle", border_xml=linie)
            xml += c.text(q + "_o", top, left + w - 2.0, 2.0, p, c.run(ort, klein, c.MUTED), align="Right", valign="Middle",
                          border_xml=linie)
        top += p * n
    return xml


def _passend(bloecke, frei):
    """Groesster Zeilenabstand (ZEILE_MAX ... ZEILE_MIN), bei dem das Verzeichnis in die freie Hoehe passt, sonst None."""
    for hundert in range(int(round(ZEILE_MAX * 100)), int(round(ZEILE_MIN * 100)) - 1, -1):
        links, rechts, hoehe = _teilen(bloecke, hundert / 100)
        if hoehe <= frei:
            return links, rechts, hoehe, hundert / 100
    return None


def _kompakt(daten):
    """Notloesung bei sehr vielen Kennungen: die Begleit-Reports (eigene Abfrage, nicht stapelbar) schrumpfen je Report auf
    eine Zeile 'Report | Kennungen'. Liefert die Bloecke ohne Begleit-Eintraege plus den Block der Begleit-Reports."""
    bloecke = [(titel, [("zeile", (k, n, o), 1) for k, n, o, m in daten[buchstabe] if o != "Begleit-Report"])
               for buchstabe, titel in GRUPPEN if daten.get(buchstabe)]
    nach_report = {}
    for liste in daten.values():
        for kennung, _name, ort, modul in liste:
            if ort == "Begleit-Report":
                nach_report.setdefault(modul[6:] if modul.startswith("build_") else modul, []).append(kennung)
    bloecke = [(t, z) for t, z in bloecke if z]
    bloecke.append(("Begleit-Reports (eigene Abfrage)", [
        ("kompakt", (name.capitalize(), sorted(kennungen)), -(-len(kennungen) // PRO_ZEILE))
        for name, kennungen in sorted(nach_report.items())]))
    return bloecke


def seite():
    x0, w = c.INSET, c.CONTENT_W
    items = b.seitenkopf(10, TITEL, "Kennung nennen genügt")
    satz = c.para([
        c.run("Jeder Baustein dieses Reports trägt eine Kennung – sie steht klein unter dem Schaustück. ", 11, c.TEXT, c.F),
        c.run("Wer einen Report bestellt, nennt die Kennungen: ", 11, c.TEXT, c.F),
        c.run("„K020, D030 und T040 – nach Geschoss statt nach Material“", 11, c.INK, c.F_SEMI),
        c.run(". Der Bauplan zu jeder Kennung liegt im Skill allplan-report-design.", 11, c.TEXT, c.F)])
    items += c.text("S10_Satz", 3.2, x0, w, 1.55, satz)

    daten = eintraege()
    bloecke = [(titel, [("zeile", (k, n, o), 1) for k, n, o, _m in daten[buchstabe]])
               for buchstabe, titel in GRUPPEN if daten.get(buchstabe)]
    sonst = [e for buchstabe, liste in sorted(daten.items()) if buchstabe not in dict(GRUPPEN) for e in liste]
    if sonst:
        bloecke.append(("Weitere", [("zeile", (k, n, o), 1) for k, n, o, _m in sonst]))
    # So viel Platz bleibt dem Verzeichnis, damit "So bestellen" immer auf die Seite passt
    frei = c.PAGE_BODY_H - 0.3 - BESTELL_H - 0.4 - ANFANG
    plan = _passend(bloecke, frei)
    if plan is None:                       # mehr Kennungen, als eine Zeile je Baustein hergibt: Begleit-Reports kompakt
        bloecke = _kompakt(daten)
        plan = _passend(bloecke, frei) or (*_teilen(bloecke, ZEILE_MIN), ZEILE_MIN)
    links, rechts, hoch, p = plan
    sw = 8.8
    items += c.rect("S10_Feld", ANFANG, x0, w, hoch, _spalte("S10_L", 0, sw, links, p) + _spalte("S10_R", sw + 0.4, sw, rechts, p))
    # Bestell-Beispiele: so klingt ein Auftrag mit Kennungen
    by = ANFANG + hoch + 0.4
    items += b.overline("S10_B", by, x0, w, "So bestellen", "Drei Beispiele")
    beispiele = [
        ("Ein Blatt für die Bauherrin", "„K010 als Einleitung, darunter K020 und D020, unten T010.“"),
        ("Baustein mit anderem Inhalt", "„D040, aber die 10 größten Räume statt Bauteile.“"),
        ("Aus zwei mach eins", "„T040 mit den Farben aus D050, dazu die Hinweisliste U020.“"),
    ]
    bw = (w - 0.8) / 3
    for i, (kopf, auftrag) in enumerate(beispiele):
        inner = (c.text("S10_B%d_k" % i, 0.25, 0.35, bw - 0.6, 0.45, c.run(kopf.upper(), 7, c.MUTED, c.F_SEMI))
                 + c.text("S10_B%d_s" % i, 0.75, 0.35, bw - 0.6, 1.7, c.run(auftrag, 10, c.INK, c.F)))
        items += c.rect("S10_B%d" % i, by + 1.4, x0 + i * (bw + 0.4), bw, BESTELL_H - 1.4, inner, bg=c.SURFACE,
                        border_xml=c.edge(["Left"], c.BLUE, "2pt"))
    return items
