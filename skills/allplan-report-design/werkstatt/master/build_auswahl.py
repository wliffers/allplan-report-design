# -*- coding: utf-8 -*-
"""Baut einen Report aus Baustein-Kennungen nach out/<name>.rdlc: "K010, D040 und T020 auf ein Blatt".

    python build_auswahl.py --bausteine=K010,D040,T020
    python build_auswahl.py --bausteine=K020,D020,T010 --titel="Für die Bauherrin" --name=Mein_Report
    python build_auswahl.py --bausteine=D090,D100,M020 --ohne-etikett     ohne die Kennung-Unterzeilen (Kunden-Report)
    python build_auswahl.py --bausteine=B020,X020 --render --daten=gross  rendert kopflos nach aus/auswahl/<daten>/

Die Bausteine stehen in der genannten Reihenfolge untereinander. Zwei Bausteine, die zusammen eine Zeile
fuellen (z. B. halb + halb), stehen nebeneinander. Passt der naechste nicht mehr aufs Blatt, beginnt eine neue Seite.
Hoehe und Breite je Baustein stehen in masse.py; Abfrage, Felder, Parameter, Code, Fuss und Bilder sind die des Masters.
"""
import argparse
import difflib
import glob
import importlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "seiten"))

import bausteine as b  # noqa: E402
import core as c  # noqa: E402
import masse  # noqa: E402

OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "out"))

KOPF_H = 2.0                    # schmales Titelband auf jeder Seite
START = KOPF_H + 0.6            # erste Zeile unter dem Band
ABSTAND = 0.5                   # Zwischenraum zwischen zwei Zeilen
RAND_UNTEN = 0.1                # so nah darf der letzte Baustein an das Seitenende
LUECKE = 0.4                    # Zwischenraum zwischen zwei Bausteinen nebeneinander
NAMEN = re.compile(r'<(?:Textbox|Rectangle|Line|Image|Tablix|Chart|Subreport|GaugePanel|Group|List|Map)\s+Name="([^"]+)"')


def fehler(text):
    sys.exit("FEHLER: " + text)


def begleit_report(kennung):
    """Begleit-Report (eigene Abfrage), der die Kennung anmeldet: (Name, Ordner, Skriptname) oder None.
    Die Bausteine der Begleit-Reports stehen in master/<ordner>/build_<name>.py; sie melden sich beim Import im Register an."""
    skripte = {}
    for pfad in sorted(glob.glob(os.path.join(HERE, "*", "build_*.py"))):
        ordner, modul = os.path.dirname(pfad), os.path.basename(pfad)[:-3]
        if ordner not in sys.path:
            sys.path.insert(0, ordner)
        try:
            importlib.import_module(modul)
        except Exception:  # pylint: disable=broad-except
            continue       # ein Begleit-Report ist ein eigenes Bauskript; fehlt er, fehlen nur seine Kennungen
        skripte[modul] = os.path.basename(ordner)
    eintrag = b.REGISTER.get(kennung)
    if eintrag and eintrag[1] in skripte:
        return eintrag[1][len("build_"):].capitalize(), skripte[eintrag[1]], eintrag[1]
    return None


def kennungen_pruefen(roh):
    """Liste der Kennungen: gross geschrieben, bekannt, ohne Doppelte (auch nicht ueber zweite Anmeldungen)."""
    gueltig = masse.register()
    ergebnis, funktion_von = [], {}
    for kennung in (k.strip().upper() for k in roh.split(",") if k.strip()):
        if kennung not in gueltig:
            begleit = begleit_report(kennung)
            if begleit:
                fehler("%s gehört zum Begleit-Report %s (eigene Abfrage, nicht stapelbar) - mit `python master\\%s\\%s.py` bauen."
                       % (kennung, begleit[0], begleit[1], begleit[2]))
            nah = sorted((k for k in gueltig if k[0] == kennung[:1]), key=lambda k: abs(int(k[1:]) - int(re.sub(r"\D", "", kennung) or 0)))[:4]
            nah += [k for k in difflib.get_close_matches(kennung, gueltig, n=3) if k not in nah]
            fehler("Unbekannte Kennung %s. Nächstliegende gültige: %s. Alle gültigen stehen in references/masse.md." % (kennung, ", ".join(nah)))
        schluessel = gueltig[kennung][1:]
        if schluessel in funktion_von:
            fehler("%s kommt doppelt vor (%s ist dieselbe Funktion) - Elementnamen müssen im Report eindeutig sein."
                   % (kennung, funktion_von[schluessel]))
        funktion_von[schluessel] = kennung
        ergebnis.append(kennung)
    if not ergebnis:
        fehler("Keine Kennung angegeben, z. B. --bausteine=K010,D040,T020")
    return ergebnis


def kopf(nr, titel):
    """Schmales Titelband im Stil der Master-Folgeseiten: Akzent, Reportname, Titel, rechts Projekt und Datum."""
    x0, p = c.INSET, "AuswahlKopf%d" % nr
    sub = '=Parameters!Project_Name.Value & "   ·   " & Format(Parameters!Date.Value, "dd.MM.yyyy")'
    # Titel und Untertitel nebeneinander mit getrennten Breiten (Felder duerfen sich nicht ueberlappen)
    titel_w = round(min(b.textbreite(titel, 19, leicht=True) * 1.03 + 0.5, c.CONTENT_W - 6.5), 2)
    inner = (c.rect(p + "Akzent", 0.5, x0, 0.9, 0.08, bg=c.ORANGE)
             + c.text(p + "Over", 0.66, x0, 12, 0.3, c.run("REPORT  ·  ALLPLAN 2027", 7, c.SKY, c.F_SEMI))
             + c.text(p + "Titel", 0.98, x0, titel_w, 0.85, c.run(titel, 19, c.WHITE, c.F_LIGHT))
             + c.text(p + "Sub", 1.1, x0 + titel_w + 0.1, c.CONTENT_W - titel_w - 0.1, 0.65, c.run(sub, 8.5, "#CBD5E1"),
                      align="Right", valign="Bottom"))
    return c.rect(p, 0, 0, c.PAGE_W, KOPF_H, inner, bg=c.NAVY)


def reihen_bilden(kennungen):
    """Zwei aufeinanderfolgende Bausteine stehen nebeneinander, wenn sie zusammen eine Zeile (fast) fuellen."""
    reihen, i = [], 0
    while i < len(kennungen):
        if i + 1 < len(kennungen):
            summe = masse.breite(kennungen[i]) + masse.breite(kennungen[i + 1])
            if c.CONTENT_W - 0.8 <= summe <= c.CONTENT_W - LUECKE + 1e-6:
                reihen.append(kennungen[i:i + 2])
                i += 2
                continue
        reihen.append(kennungen[i:i + 1])
        i += 1
    return reihen


def namen_pruefen(teile):
    """teile: Liste (Herkunft, XML). Elementnamen muessen im ganzen Report eindeutig sein (Gross/Klein zaehlt nicht)."""
    gesehen, doppelt = {}, []
    for herkunft, xml in teile:
        for name in set(NAMEN.findall(xml)):
            if name.lower() in gesehen and gesehen[name.lower()] != herkunft:
                doppelt.append("%s (%s und %s)" % (name, gesehen[name.lower()], herkunft))
            gesehen.setdefault(name.lower(), herkunft)
    if doppelt:
        fehler("Elementnamen doppelt - die Bausteine lassen sich so nicht mischen: " + "; ".join(sorted(doppelt)))


def seiten_bauen(kennungen, titel):
    """Gibt (Seiten-XML-Liste, Teile fuer die Namenspruefung) zurueck."""
    x0 = c.INSET
    seiten, teile = [], []
    inhalt, y = "", START
    for reihe in reihen_bilden(kennungen):
        hoehe = max(masse.MASSE[k][0] for k in reihe)
        if inhalt and y + hoehe > c.PAGE_BODY_H - RAND_UNTEN:
            seiten.append(inhalt)
            inhalt, y = "", START
        if not inhalt:
            inhalt = kopf(len(seiten) + 1, titel)
            teile.append(("Kopf%d" % (len(seiten) + 1), inhalt))
        for i, kennung in enumerate(reihe):
            links = x0 if i == 0 else x0 + c.CONTENT_W - masse.breite(kennung)
            xml = masse.bau(kennung, y, links)
            teile.append((kennung, xml))
            inhalt += xml
        y += hoehe + ABSTAND
    seiten.append(inhalt)
    return seiten, teile


def build(kennungen, titel, name, ohne_etikett):
    b.ETIKETT_AN[0] = not ohne_etikett
    seiten, teile = seiten_bauen(kennungen, titel)
    fuss = b.fuss()
    namen_pruefen(teile + [("Fuss", fuss)])
    labels = ["%s - Seite %d" % (titel, n + 1) if len(seiten) > 1 else titel for n in range(len(seiten))]
    xml = c.report(seiten, [c.dataset("AllplanReport", b.QUERY, b.FIELDS)], extra_params=b.PARAMS, footer_xml=fuss, code=b.CODE,
                   labels=labels, embedded_xml=c.embedded(os.path.join(HERE, "bilder")))
    os.makedirs(OUT_DIR, exist_ok=True)
    ziel = os.path.join(OUT_DIR, name + ".rdlc")
    c.save(ziel, xml)
    return ziel, len(seiten)


def rendern(ziel, name, daten):
    """Rendert kopflos wie build_master; die PNG liegen in aus/auswahl/<daten>/<name>_S<n>.png."""
    json_datei = os.path.join(HERE, "daten", daten + ".json")
    if not os.path.isfile(json_datei):
        fehler("Datensatz %s fehlt: %s" % (daten, json_datei))
    ausgabe = os.path.join(HERE, "aus", "auswahl", daten)
    os.makedirs(ausgabe, exist_ok=True)
    for alt in glob.glob(os.path.join(ausgabe, name + "_S*.png")):
        os.remove(alt)     # sonst bleiben Seiten eines frueheren, laengeren Laufs liegen
    lauf = subprocess.run(c.render_argumente(ziel, json_datei, ausgabe), capture_output=True, check=False)
    # Das Anzeigeprogramm schreibt in der Konsolen-Codepage; Pfade mit Umlauten duerfen das Lesen nicht abbrechen.
    ausgabe_text = lauf.stdout.decode("oem", errors="replace").strip()
    print(ausgabe_text)
    if lauf.returncode != 0:
        fehler("Rendern fehlgeschlagen (Code %d): %s" % (lauf.returncode, lauf.stderr.decode("oem", errors="replace").strip()))
    if "OK Seiten=" not in ausgabe_text:
        fehler("Rendern ohne Ergebnis: das Anzeigeprogramm hat keine Seite gemeldet.")
    return ausgabe


def main():
    arg = argparse.ArgumentParser(description="Report aus Baustein-Kennungen bauen")
    arg.add_argument("--bausteine", required=True, help="Kennungen in Reihenfolge, z. B. K010,D040,T020")
    arg.add_argument("--titel", default="Auswahl")
    arg.add_argument("--name", default="Report_Auswahl")
    arg.add_argument("--ohne-etikett", action="store_true", help="keine Kennung-Unterzeilen")
    arg.add_argument("--render", action="store_true")
    arg.add_argument("--daten", default="master", help="master | master_en | gross - Datensatz fürs Rendern (Datei daten/<name>.json)")
    opt = arg.parse_args()
    ziel, seiten = build(kennungen_pruefen(opt.bausteine), opt.titel, opt.name, opt.ohne_etikett)
    print(ziel)
    print("Seiten=%d" % seiten)
    if opt.render:
        print(rendern(ziel, opt.name, opt.daten))


if __name__ == "__main__":
    main()
