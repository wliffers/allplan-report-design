# -*- coding: utf-8 -*-
"""Erzeugt den grossen, kuenstlichen Pruefdatensatz gross.json aus dem eigenen Master-Datensatz master.json.

    python make_gross.py

Gross = rund 3.000 Zeilen, durch Vervielfachen und Abwandeln der Zeilen von master.json (eigenes Testgebaeude,
kein fremdes Projekt): 40 Raumnutzungen mit teils sehr langen Namen, je Materialgruppe 8 Schreibweisen
(deutsch und englisch gemischt, dazu Bauteile ohne Material), 15 Tuer- und 20 Fenstertypen mit verschiedenen
Breiten, sehr grosse und sehr kleine Zahlen. Die Bildfelder sind wie in master.json (file:bilder/<ObjNr>.png).
Feste Zufallszahlen: derselbe Aufruf ergibt dieselbe Datei.

Der Datensatz prueft, ob eine Seite mit vielen Zeilen, langen Namen und unbekannten Schreibweisen haelt
(Deckel, Abschneiden, Materialerkennung am Wortstamm). Er ersetzt in ausgelieferten Unterlagen
Datensaetze aus echten Projekten; die werden nicht ausgeliefert.
"""
import copy
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HERE, "master.json")
ZIEL = os.path.join(HERE, "gross.json")

# Zeilen je Objektnummer (Summe 3000)
ANZAHL = {"704": 3, "4": 14, "3": 280, "6": 150, "1": 1500, "61": 260, "991": 420, "992": 373}
# Reihenfolge der Objektnamen wie im Allplan-Export (aufsteigend nach der ersten Spalte)
OBJEKT_ORDNUNG = ["Bodenplatte", "Decke", "Fenstermakro, -SmartPart", "Raum", "Stütze", "Türmakro, -SmartPart", "Unterzug", "Wand"]
GESCHOSSE = ["0536", "0537", "0538", "0539", "0540", "0541", "0542", "0543"]   # Teilbildnummern als Kopf der Bauteil-ID
KUERZEL = {"704": "PFu", "4": "De ", "3": "St ", "6": "Unz", "1": "Wa ", "61": "Rau", "991": "Mak", "992": "Mak"}

# Materialgruppe -> (Gewerk, acht Schreibweisen). Jede Schreibweise muss Code.MatArt in bausteine.py der Gruppe zuordnen.
MATERIAL = {
    "Beton": ("Betonarbeiten", ["Beton bewehrt", "StB C30/37", "Stahlbeton", "Concrete C25/30", "Ortbeton WU",
                                "Reinforced concrete", "Beton C20/25", "Sichtbeton SB3"]),
    "Mauerwerk": ("Mauerarbeiten", ["Mauerwerk", "MW", "MW 17,5", "KS 20", "Kalksandstein", "Ziegelmauerwerk",
                                    "Masonry", "Brick wall"]),
    "Dämmung": ("Wärmedämm-Verbundsysteme", ["Dämmung", "WDVS", "Wärmedämmung EPS 035", "Daemmung", "Insulation",
                                             "Mineralwolle Isolierung", "ETICS", "XPS Dämmplatte"]),
    "Gipskarton": ("Trockenbauarbeiten", ["Gipskarton", "Trockenbauwand", "Gipskartonplatte", "Gypsum board",
                                          "Plasterboard", "Drywall", "Gipsfaser", "Gips-Ständerwand"]),
    "Holz": ("Zimmererarbeiten", ["Holz", "Wood", "Timber C24", "Brettschichtholz GL24h", "Massivholz Fichte",
                                  "Holzrahmen", "Holzbalkendecke", "Timber frame"]),
    "Stahl": ("Stahlbauarbeiten", ["Stahl", "Steel", "Baustahl S355", "Stahl S235", "Edelstahl", "Structural steel S355",
                                   "Stahlprofil HEB", "Steel plate"]),
    "Naturstein": ("Natursteinarbeiten", ["Naturstein", "Natural stone", "Granit Stein", "Sandstein", "Stone cladding",
                                          "Muschelkalk Stein", "Kalkstein", "Basalt Stein"]),
}
# Schreibweisen, die keiner Gruppe angehoeren ("Sonstiges")
SONSTIGES = ("Estrich", "Putz")

# Raumnutzung -> (kleinste, groesste Flaeche in m2, Raumhoehe in m); 40 Nutzungen, teils sehr lange Namen
NUTZUNGEN = {
    "Büro": (12, 30, 2.78), "Großraumbüro": (80, 320, 3.1), "Besprechung": (12, 40, 2.78),
    "Besprechungsraum für Projektteams und Auftraggebergespräche mit Videokonferenzanlage": (30, 60, 2.9),
    "Empfang": (15, 45, 3.2), "Küche": (8, 25, 2.78), "Teeküche": (4, 10, 2.78), "Lager": (6, 80, 2.78),
    "Archiv": (10, 120, 2.6), "Sanitär": (6, 24, 2.6), "WC Damen": (6, 14, 2.6), "WC Herren": (6, 14, 2.6),
    "Behinderten-WC": (4, 6, 2.6), "Technik": (5, 40, 2.78), "Serverraum": (8, 30, 2.8), "Verkehrsfläche": (20, 140, 2.78),
    "Flur": (8, 90, 2.78), "Treppenhaus": (14, 36, 2.78), "Aufzugsvorraum": (3, 9, 2.78), "Foyer": (40, 220, 4.5),
    "Kantine": (90, 260, 3.4), "Pausenraum": (12, 36, 2.78), "Schulungsraum": (28, 70, 2.9), "Labor": (20, 90, 3.0),
    "Werkstatt": (40, 400, 4.2), "Technische Gebäudeausrüstung - Lüftungszentrale und Kälteerzeugung im Untergeschoss": (60, 180, 3.6),
    "Putzmittelraum": (2, 5, 2.6), "Umkleide": (8, 30, 2.6), "Dusche": (3, 8, 2.6), "Fahrradabstellraum": (15, 60, 2.6),
    "Müllraum": (6, 20, 2.6), "Elektro-Hauptverteilung": (10, 40, 2.8), "Heizungsraum": (12, 45, 2.8),
    "Tiefgarage Stellplätze mit Rangierfläche": (600, 1850, 2.4), "Ausstellungsfläche": (120, 650, 5.5),
    "Veranstaltungssaal / Event Hall": (150, 640, 6.5), "Wartebereich": (10, 40, 2.78),
    "Sozialraum für Reinigungs- und Haustechnikpersonal einschließlich Spinde und Umkleidebänke": (14, 40, 2.6),
    "Corridor": (12, 60, 2.78), "Atrium / Lichthof": (80, 300, 9.0),
}

# 20 Fenstertypen: (Bezeichnung, moegliche Breiten, moegliche Hoehen) in m
FENSTER = [
    ("1flg Holz", (0.76, 0.885, 1.01, 1.26), (0.76, 1.385)), ("1flg Weiß", (0.76, 1.01, 1.26), (1.01, 1.385)),
    ("2flg Weiß", (1.51, 1.76, 2.01), (1.385, 1.51)), ("2flg Kunststoff Dreh-Kipp", (1.26, 1.51), (1.26, 1.51)),
    ("3flg Alu", (2.26, 2.51, 3.01), (1.385, 2.01)), ("Festverglasung", (0.5, 1.0, 2.0, 3.5), (0.5, 2.5)),
    ("Oberlicht", (0.5, 0.6, 1.0), (0.5, 0.6)), ("Fensterband Alu", (6.0, 8.0, 12.5), (0.9, 1.2)),
    ("Dachflächenfenster", (0.78, 1.14), (1.18, 1.40)), ("Kellerfenster klein", (0.5, 0.6), (0.4, 0.5)),
    ("Schaufenster", (3.0, 4.5, 6.0), (2.4, 3.0)), ("Bodentief 1flg", (0.885, 1.01), (2.135, 2.26)),
    ("Bodentief 2flg Schiebe", (2.0, 2.4, 3.0), (2.135, 2.26)), ("Lüftungsflügel", (0.4, 0.5), (0.3, 0.4)),
    ("Rundfenster", (0.6, 0.9), (0.6, 0.9)), ("Brandschutzverglasung EI30", (1.0, 1.5, 2.0), (1.0, 2.1)),
    ("Holz-Alu Sprosse", (1.01, 1.26), (1.385, 1.51)), ("Stahlfenster Fabrik", (1.8, 2.4), (2.0, 3.0)),
    ("Kastenfenster", (1.01, 1.26), (1.51, 1.76)), ("Glasbaustein-Feld", (0.9, 1.2), (0.9, 1.2)),
]
# 15 Tuertypen
TUEREN = [
    ("1flg Holz Glasauschn.", (0.885, 1.01), (2.01, 2.135)), ("1flg Weiß Blockzarge", (0.885, 1.01), (2.135,)),
    ("1flg Weiß 1 Seitenteil", (1.26, 1.385), (2.135,)), ("2flg Holz", (1.51, 1.76, 2.01), (2.135, 2.26)),
    ("2flg Stahl T30", (1.76, 2.01), (2.135,)), ("Stahltür T90", (1.01, 1.26), (2.135,)),
    ("Schiebetür Glas", (1.26, 1.51, 2.0), (2.135, 2.26)), ("Drehflügeltür Glas ganz", (0.885, 1.01), (2.135, 2.5)),
    ("Haustür Alu", (1.01, 1.26), (2.135, 2.26)), ("Karusselltür", (2.2, 2.6), (2.4, 2.6)),
    ("Schiebetor Industrie", (3.0, 4.0, 5.0), (3.0, 4.0)), ("Brandschutztor", (2.5, 3.5), (2.5, 3.0)),
    ("Kellertür einfach", (0.76, 0.885), (1.885, 2.01)), ("Pendeltür 2flg", (1.5, 1.8), (2.135,)),
    ("Technikraumtür Lüftung", (0.9, 1.1), (2.0, 2.135)),
]


def gerundet(wert):
    return round(wert, 3)


def vorlagen_nach_objnr(zeilen):
    """Erste Zeile je Objektnummer aus master.json: sie liefert Feldreihenfolge, Objektname und Bildverweis."""
    vorlagen = {}
    for zeile in zeilen:
        vorlagen.setdefault(zeile["ObjNr"], zeile)
    return vorlagen


def neue_zeile(vorlage, rng, objnr, zaehler):
    zeile = copy.deepcopy(vorlage)
    geschoss = GESCHOSSE[(zaehler[objnr] * 7 + rng.randrange(3)) % len(GESCHOSSE)]
    zaehler[objnr] += 1
    zaehler["lfd"] += rng.randrange(1, 40)                     # laufende Nummer: die Bauteil-ID ist so immer eindeutig
    zeile["Nr"] = "%s%s%010d" % (geschoss, KUERZEL[objnr], zaehler["lfd"])
    zeile["Bezeichnung"] = ""
    zeile["Funktion"] = ""
    zeile["Material"] = ""
    zeile["Gewerk"] = ""
    return zeile


def material_setzen(zeile, gruppe, rng, ohne_anteil=0.0):
    """Schreibweise der Gruppe waehlen; ein Anteil der Bauteile bekommt gar kein Material, wenige 'Sonstiges'."""
    wurf = rng.random()
    if wurf < ohne_anteil:
        return
    if wurf < ohne_anteil + 0.02:
        zeile["Material"], zeile["Gewerk"] = rng.choice(SONSTIGES), "Estricharbeiten"
        return
    gewerk, schreibweisen = MATERIAL[gruppe]
    zeile["Material"], zeile["Gewerk"] = rng.choice(schreibweisen), gewerk


def bodenplatten(vorlage, rng, zaehler):
    zeilen = []
    for laenge, breite, staerke in ((88.4, 61.2, 0.6), (24.5, 18.2, 0.3), (6.2, 4.8, 0.2)):
        z = neue_zeile(vorlage, rng, "704", zaehler)
        material_setzen(z, "Beton", rng)
        flaeche = laenge * breite
        z.update(Laenge=laenge, Dicke=breite, Hoehe=staerke, Flaeche=gerundet(flaeche), Volumen=gerundet(flaeche * staerke))
        zeilen.append(z)
    return zeilen


def decken(vorlage, rng, zaehler):
    zeilen = []
    for i in range(ANZAHL["4"]):
        z = neue_zeile(vorlage, rng, "4", zaehler)
        material_setzen(z, "Holz" if i == 13 else "Beton", rng)
        laenge, breite = (65.0, 50.2) if i == 0 else (round(rng.uniform(6, 48), 2), round(rng.uniform(5, 40), 2))
        staerke = rng.choice((0.18, 0.2, 0.22, 0.25, 0.3))
        flaeche = laenge * breite
        z.update(Laenge=laenge, Dicke=breite, Hoehe=staerke, Flaeche=gerundet(flaeche), Volumen=gerundet(flaeche * staerke))
        zeilen.append(z)
    return zeilen


def stuetzen(vorlage, rng, zaehler):
    zeilen = []
    for _ in range(ANZAHL["3"]):
        z = neue_zeile(vorlage, rng, "3", zaehler)
        material_setzen(z, rng.choices(("Beton", "Stahl", "Holz"), weights=(80, 14, 6))[0], rng, ohne_anteil=0.03)
        breite = rng.choice((0.2, 0.25, 0.3, 0.3, 0.4, 0.5, 0.6))
        tiefe = breite if rng.random() < 0.7 else rng.choice((0.2, 0.3, 0.5, 0.8))
        hoehe = round(rng.uniform(2.4, 4.4), 2)
        z.update(Laenge=breite, Dicke=tiefe, Hoehe=hoehe, Flaeche=gerundet(2 * (breite + tiefe) * hoehe),
                 Volumen=gerundet(breite * tiefe * hoehe))
        zeilen.append(z)
    return zeilen


def unterzuege(vorlage, rng, zaehler):
    zeilen = []
    for _ in range(ANZAHL["6"]):
        z = neue_zeile(vorlage, rng, "6", zaehler)
        material_setzen(z, rng.choices(("Beton", "Stahl", "Holz"), weights=(70, 18, 12))[0], rng, ohne_anteil=0.04)
        laenge, breite, hoehe = round(rng.uniform(1.8, 14.5), 2), rng.choice((0.2, 0.25, 0.3, 0.4)), rng.choice((0.3, 0.4, 0.5, 0.65, 0.9))
        z.update(Laenge=laenge, Dicke=breite, Hoehe=hoehe, Flaeche=gerundet(laenge * (breite + 2 * hoehe)),
                 Volumen=gerundet(laenge * breite * hoehe))
        zeilen.append(z)
    return zeilen


AUFBAUTEN = [  # Schichten einer Wand von aussen nach innen: (Gruppe, kleinste Dicke, groesste Dicke)
    (("Beton", 0.2, 0.4),), (("Beton", 0.2, 0.3), ("Dämmung", 0.1, 0.24)),
    (("Mauerwerk", 0.115, 0.365), ("Gipskarton", 0.0125, 0.1)), (("Mauerwerk", 0.175, 0.3), ("Dämmung", 0.08, 0.2)),
    (("Gipskarton", 0.0125, 0.125),), (("Holz", 0.06, 0.2), ("Dämmung", 0.06, 0.16)), (("Naturstein", 0.03, 0.1), ("Beton", 0.2, 0.3)),
    (("Stahl", 0.01, 0.05),),
]


def waende(vorlage, rng, zaehler):
    """Wandaufbauten: Allplan liefert je Wandschicht eine Zeile, alle Schichten einer Wand haben dieselbe Laenge."""
    zeilen = []
    while len(zeilen) < ANZAHL["1"]:
        laenge = rng.choice((round(rng.uniform(0.6, 12.0), 3), round(rng.uniform(3.0, 85.0), 2), 0.05, 0.35))
        hoehe = round(rng.uniform(2.4, 4.6), 2)
        for gruppe, klein, gross in rng.choice(AUFBAUTEN):
            z = neue_zeile(vorlage, rng, "1", zaehler)
            material_setzen(z, gruppe, rng, ohne_anteil=0.04)
            dicke = round(rng.uniform(klein, gross), 4)
            flaeche = laenge * hoehe
            z.update(Laenge=laenge, Dicke=dicke, Hoehe=hoehe, Flaeche=gerundet(flaeche), Volumen=gerundet(flaeche * dicke))
            zeilen.append(z)
    return zeilen[:ANZAHL["1"]]


def raeume(vorlage, rng, zaehler):
    namen = list(NUTZUNGEN)
    wahl = namen + [rng.choice(namen) for _ in range(ANZAHL["61"] - len(namen))]   # jede Nutzung mindestens einmal
    zeilen = []
    for name in wahl:
        z = neue_zeile(vorlage, rng, "61", zaehler)
        klein, gross, hoehe = NUTZUNGEN[name]
        flaeche = rng.uniform(klein, gross)
        laenge = flaeche ** 0.5 * rng.uniform(0.8, 1.9)
        breite = flaeche / laenge
        flaeche = laenge * breite
        z["Funktion"] = name
        z.update(Laenge=gerundet(laenge), Dicke=gerundet(breite), Hoehe=hoehe, Flaeche=gerundet(flaeche), Volumen=gerundet(flaeche * hoehe))
        zeilen.append(z)
    return zeilen


def oeffnungen(vorlage, rng, zaehler, objnr, typen):
    zeilen = []
    for i in range(ANZAHL[objnr]):
        name, breiten, hoehen = typen[i % len(typen)] if i < 3 * len(typen) else rng.choice(typen)   # jeder Typ mehrfach
        z = neue_zeile(vorlage, rng, objnr, zaehler)
        breite, hoehe = rng.choice(breiten), rng.choice(hoehen)
        z["Bezeichnung"] = name
        z.update(Laenge=breite, Dicke=0.08, Hoehe=hoehe, Flaeche=gerundet(breite * hoehe), Volumen=0.0)
        zeilen.append(z)
    return zeilen


def sortieren(zeilen):
    """Wie der Allplan-Export: aufsteigend nach den Spalten in Abfragereihenfolge."""
    spalten = ("Objekt", "ObjNr", "Bezeichnung", "Funktion", "Material", "Gewerk", "Laenge", "Dicke", "Hoehe", "Flaeche", "Volumen", "Nr")
    rang = {name: i for i, name in enumerate(OBJEKT_ORDNUNG)}
    return sorted(zeilen, key=lambda z: (rang[z["Objekt"]],) + tuple(str(z[s]).lower() if isinstance(z[s], str) else z[s] for s in spalten[1:]))


def main():
    with open(QUELLE, encoding="utf-8") as handle:
        master = json.load(handle)
    vorlagen = vorlagen_nach_objnr(master["rows"])
    fehlt = [nr for nr in ANZAHL if nr not in vorlagen]
    if fehlt:
        raise SystemExit("master.json hat keine Zeile mit ObjNr %s" % ", ".join(fehlt))
    rng = random.Random(2027)
    zaehler = dict.fromkeys(ANZAHL, 0)
    zaehler["lfd"] = 1000
    zeilen = (bodenplatten(vorlagen["704"], rng, zaehler) + decken(vorlagen["4"], rng, zaehler)
              + stuetzen(vorlagen["3"], rng, zaehler) + unterzuege(vorlagen["6"], rng, zaehler)
              + waende(vorlagen["1"], rng, zaehler) + raeume(vorlagen["61"], rng, zaehler)
              + oeffnungen(vorlagen["991"], rng, zaehler, "991", FENSTER) + oeffnungen(vorlagen["992"], rng, zaehler, "992", TUEREN))
    ergebnis = {"types": master["types"], "rows": sortieren(zeilen)}
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(ergebnis, handle, ensure_ascii=False, indent=1)
    print("%d Zeilen -> %s" % (len(ergebnis["rows"]), ZIEL))


if __name__ == "__main__":
    main()
