# -*- coding: utf-8 -*-
"""Legt die Werkstatt des Skills allplan-report-design in einem Ordner des Anwenders an.

    python werkstatt_anlegen.py <ziel>                   neue Werkstatt; bricht ab, wenn <ziel> nicht leer ist
    python werkstatt_anlegen.py <ziel> --aktualisieren   vorhandene Werkstatt auf den Stand dieses Pakets bringen

Der Skill-Ordner bleibt unveraendert: gearbeitet wird nur in <ziel>. Die Werkstatt ist die Kopie von
werkstatt/ neben diesem Skript (Bausatz master/, Werkzeuge werkzeug/, Vorlagen vorlagen/). Im Ziel entstehen
ausserdem der leere Ordner out/ (dort landen die fertigen .rdlc) und die Merkdatei .werkstatt_stand.json
(Pruefsumme jeder kopierten Datei - sie erkennt, was der Anwender selbst veraendert hat).

--aktualisieren ueberschreibt, und nur das:
  - Dateien unter master/ und werkzeug/, die es im Paket gibt und die der Anwender seit dem Kopieren NICHT
    veraendert hat (Pruefsumme gleich der Merkdatei). Neue Dateien des Pakets in diesen Ordnern kommen dazu.
  - Hat der Anwender eine Paketdatei veraendert (oder fehlt die Merkdatei), bleibt seine Datei stehen; die
    neue Fassung liegt daneben als <name>.neu und wird gemeldet.
Unangetastet bleiben: out/ und aus/, eigene Datensaetze, eigene Seiten und alles andere, was es im Paket nicht
gibt, sowie vorlagen/ und der gebaute Renderer werkzeug/render/bin. Geloescht wird nie etwas.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
PAKET = HIER / "werkstatt"
MERKDATEI = ".werkstatt_stand.json"
AKTUALISIERT = ("master", "werkzeug")                 # nur diese Ordner ersetzt --aktualisieren


def pruefsumme(pfad):
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def paketdateien():
    return sorted(p for p in PAKET.rglob("*") if p.is_file())


def neu_anlegen(ziel):
    if ziel.exists() and any(ziel.iterdir()):
        sys.exit("FEHLER: %s ist nicht leer. Anderen Ordner nehmen oder --aktualisieren benutzen "
                 "(das ersetzt nur master/ und werkzeug/, siehe Kopf dieser Datei)." % ziel)
    stand = {}
    for quelle in paketdateien():
        rel = quelle.relative_to(PAKET)
        (ziel / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(quelle, ziel / rel)
        stand[rel.as_posix()] = pruefsumme(quelle)
    (ziel / "out").mkdir(exist_ok=True)
    (ziel / MERKDATEI).write_text(json.dumps(stand, indent=1), encoding="utf-8")
    print("Werkstatt angelegt: %s (%d Dateien)" % (ziel, len(stand)))
    print("Renderer bauen (einmalig): powershell -ExecutionPolicy Bypass -File werkzeug\\render\\build.ps1")


def aktualisieren(ziel):
    merk = ziel / MERKDATEI
    if not (ziel / "master").is_dir() or not (ziel / "werkzeug").is_dir():
        sys.exit("FEHLER: %s ist keine Werkstatt (master/ oder werkzeug/ fehlt)." % ziel)
    stand = json.loads(merk.read_text(encoding="utf-8")) if merk.is_file() else {}
    gezaehlt = {"neu": [], "ersetzt": [], "gleich": 0, "behalten": []}
    for quelle in paketdateien():
        rel = quelle.relative_to(PAKET)
        if rel.parts[0] not in AKTUALISIERT:
            continue
        ziel_datei = ziel / rel
        schluessel = rel.as_posix()
        neu = pruefsumme(quelle)
        if not ziel_datei.is_file():
            ziel_datei.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(quelle, ziel_datei)
            gezaehlt["neu"].append(schluessel)
        elif pruefsumme(ziel_datei) == neu:
            gezaehlt["gleich"] += 1
        elif stand.get(schluessel) == pruefsumme(ziel_datei):          # vom Anwender nicht veraendert
            shutil.copyfile(quelle, ziel_datei)
            gezaehlt["ersetzt"].append(schluessel)
        else:                                                           # vom Anwender veraendert: nichts ueberschreiben
            shutil.copyfile(quelle, ziel_datei.with_name(ziel_datei.name + ".neu"))
            gezaehlt["behalten"].append(schluessel)
            continue
        stand[schluessel] = neu
    (ziel / "out").mkdir(exist_ok=True)
    merk.write_text(json.dumps(stand, indent=1), encoding="utf-8")
    print("Aktualisiert: %s" % ziel)
    print("  neu hinzugekommen: %d; ersetzt: %d; schon gleich: %d; vom Anwender veraendert, Datei bleibt: %d"
          % (len(gezaehlt["neu"]), len(gezaehlt["ersetzt"]), gezaehlt["gleich"], len(gezaehlt["behalten"])))
    for schluessel in gezaehlt["behalten"]:
        print("  BEHALTEN %s - neue Fassung daneben als %s.neu" % (schluessel, Path(schluessel).name))
    if not (ziel / "werkzeug" / "render" / "bin" / "RenderRdlc.exe").is_file():
        print("  Hinweis: der Renderer ist noch nicht gebaut: powershell -ExecutionPolicy Bypass -File werkzeug\\render\\build.ps1")


def main(argumente):
    ordner = [a for a in argumente if not a.startswith("--")]
    if len(ordner) != 1 or not PAKET.is_dir():
        sys.exit(__doc__ if len(ordner) != 1 else "FEHLER: %s fehlt - das Paket ist unvollstaendig." % PAKET)
    ziel = Path(ordner[0]).resolve()
    if PAKET == ziel or PAKET in ziel.parents:
        sys.exit("FEHLER: Das Ziel liegt im Skill-Ordner. Die Werkstatt gehoert in einen eigenen Ordner.")
    if "--aktualisieren" in argumente:
        aktualisieren(ziel)
    else:
        neu_anlegen(ziel)


if __name__ == "__main__":
    main(sys.argv[1:])
