# -*- coding: utf-8 -*-
"""Rechenkern der Raum-Abwicklung - reines Python, ohne Allplan.

Aus Raumumriss, Raumhoehe und den Koerpern der Oeffnungen entsteht je Raum EINE zusammenhaengende Abwicklung:
die Waende im Uhrzeigersinn als durchlaufendes Band (von innen gesehen links nach rechts), Ecken als Knicklinien,
Tueren und Fenster farbig mit Kuerzel, eine durchlaufende Masslinie mit JEDEM Abschnitt (enge Zahlen ruecken in
eine tiefere Zeile und bekommen einen Hinweisstrich), eine Lageskizze mit den Wandnummern und eine Legende.

Alle Masse der Zeichnung stehen in "Report-Millimetern": das Bildfeld im Report ist FELD_B x FELD_H mm gross, der
Rahmen hat dasselbe Seitenverhaeltnis, und k (Modellmeter je Report-Millimeter) wird je Raum so gewaehlt, dass die
Zeichnung das Feld fuellt. Dadurch ist die Schrift in jedem Raum gleich gross, egal wie lang die Waende sind.

Eingabe (Meter):
    raum      = {"id", "nr", "name", "punkte": [(x, y), ...], "z0": Fussboden, "hoehe": lichte Hoehe}
    oeffnung  = {"art": "tuer" | "fenster", "ecken": [(x, y, z), ...]}     Eckpunkte des Oeffnungskoerpers
Ausgabe je Raum: {"flaechen", "linien", "texte", "rahmen", "info"} - Zeichenelemente in Metern, Texthoehe in Report-mm
mal k (Modellmeter); der Aufrufer rechnet sie mit dem Teilbildmassstab in Papier-mm um.
"""
import math

KERN_VERSION = 2

FELD_B, FELD_H = 170.0, 90.0     # Bildfeld im Report in mm
RAND = 4.0
KOPF = 6.0                       # Zeile mit den Wandnummern ueber dem Band
ZEILE = 5.0                      # Luft zwischen zwei Bandreihen
LEGENDE = 2.5                    # Luft ueber der Legende; dazu je Zeile T_KLEIN + 1,4
LEGENDE_ZEILEN_MAX = 3
HOEHENMASS = 9.0                 # Platz links fuer das Hoehenmass
T_GROSS, T_KLEIN = 2.7, 2.3      # Schrifthoehen in Report-mm (rund 7,5 und 6,5 pt)
ZEICHEN = 0.62                   # mittlere Zeichenbreite je Schrifthoehe
BAHN = T_KLEIN + 1.5             # Hoehe einer Zeile der Masszahlen
K_EINE_REIHE = 0.30              # bis 1:300 bleibt die Abwicklung in EINER Reihe
BAHNEN_MAX = 5
FARBE_WAND, FARBE_FENSTER, FARBE_TUER = "#F1F5F9", "#BFDBFE", "#FED7AA"
TEXT_DUNKEL, TEXT_GRAU = "#0F172A", "#64748B"
EPS = 1e-6

TEXTE = {
    "de": {"wand": "Wand", "tuer": "Tür", "fenster": "Fenster", "bruestung": "Brüstung", "ohne": "ohne Öffnungen",
           "lage": "Lage im Grundriss · Start an der Marke, im Uhrzeigersinn", "komma": ","},
    "en": {"wand": "Wall", "tuer": "Door", "fenster": "Window", "bruestung": "sill", "ohne": "no openings",
           "lage": "Key plan · start at the mark, clockwise", "komma": "."},
}


class AbwicklungFehler(ValueError):
    """Der Raum laesst sich nicht abwickeln (Meldung in Alltagssprache)."""


# ---------------------------------------------------------------- Raumumriss
def _flaeche(punkte):
    return 0.5 * sum(punkte[i][0] * punkte[(i + 1) % len(punkte)][1] - punkte[(i + 1) % len(punkte)][0] * punkte[i][1]
                     for i in range(len(punkte)))


def ring(punkte, toleranz=0.001):
    """Umriss aufraeumen: doppelte und auf einer Geraden liegende Punkte weg, Umlauf im Uhrzeigersinn
    (Raum rechts der Laufrichtung), Start an der laengsten Wand."""
    sauber = []
    for p in punkte:
        p = (float(p[0]), float(p[1]))
        if not sauber or math.hypot(p[0] - sauber[-1][0], p[1] - sauber[-1][1]) > toleranz:
            sauber.append(p)
    if len(sauber) > 1 and math.hypot(sauber[0][0] - sauber[-1][0], sauber[0][1] - sauber[-1][1]) <= toleranz:
        sauber.pop()
    geaendert = True
    while geaendert and len(sauber) > 3:
        geaendert = False
        for i in range(len(sauber)):
            a, b, c = sauber[i - 1], sauber[i], sauber[(i + 1) % len(sauber)]
            lang = math.hypot(c[0] - a[0], c[1] - a[1])
            abstand = abs((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / lang if lang > EPS else 0.0
            if abstand <= toleranz:
                del sauber[i]
                geaendert = True
                break
    if len(sauber) < 3 or abs(_flaeche(sauber)) < 1e-4:
        raise AbwicklungFehler("Der Raum hat keinen Umriss mit mindestens drei Ecken.")
    if _flaeche(sauber) > 0:
        sauber.reverse()
    start = max(range(len(sauber)), key=lambda i: (round(_laenge(sauber, i), 4), -i))
    return sauber[start:] + sauber[:start]


def _laenge(punkte, i):
    a, b = punkte[i], punkte[(i + 1) % len(punkte)]
    return math.hypot(b[0] - a[0], b[1] - a[1])


def waende(ring_cw):
    kanten = []
    for i, a in enumerate(ring_cw):
        b = ring_cw[(i + 1) % len(ring_cw)]
        lang = math.hypot(b[0] - a[0], b[1] - a[1])
        u = ((b[0] - a[0]) / lang, (b[1] - a[1]) / lang)
        kanten.append({"nr": i + 1, "a": a, "b": b, "u": u, "aussen": (-u[1], u[0]), "laenge": lang, "oeffnungen": []})
    return kanten


# ---------------------------------------------------------------- Oeffnungen
def oeffnungen_zuordnen(kanten, oeffnungen, z0, hoehe, toleranz=0.05):
    """Eine Oeffnung gehoert zu der Wand, an deren Innenflaeche ihr Koerper anliegt und nach aussen reicht."""
    for o in oeffnungen:
        ecken = o["ecken"]
        if not ecken:
            continue
        zmin, zmax = min(p[2] for p in ecken), max(p[2] for p in ecken)
        unten, oben = max(0.0, zmin - z0), min(hoehe, zmax - z0)
        if oben - unten < 0.05:
            continue
        for kante in kanten:
            a, u, n = kante["a"], kante["u"], kante["aussen"]
            laengs = [(p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1] for p in ecken]
            quer = [(p[0] - a[0]) * n[0] + (p[1] - a[1]) * n[1] for p in ecken]
            if min(quer) < -toleranz or min(quer) > toleranz or max(quer) < 0.03 or max(quer) > 1.5:
                continue
            links, rechts = max(0.0, min(laengs)), min(kante["laenge"], max(laengs))
            breite = max(laengs) - min(laengs)
            if rechts - links < 0.05 or rechts - links < 0.6 * breite:
                continue
            kante["oeffnungen"].append({"art": o["art"], "links": links, "rechts": rechts, "unten": unten, "oben": oben,
                                        "breite": breite, "hoehe": zmax - zmin, "bruestung": unten})
    for kante in kanten:
        kante["oeffnungen"].sort(key=lambda o: o["links"])


# ---------------------------------------------------------------- Aufteilung
def _reihen(kanten, anzahl):
    """Kanten in 'anzahl' aufeinanderfolgende Reihen teilen - getrennt wird nur an Ecken."""
    if anzahl <= 1:
        return [kanten]
    gesamt = sum(k["laenge"] for k in kanten)
    grenzen, lauf, ecken = [], 0.0, []
    for i, k in enumerate(kanten[:-1]):
        lauf += k["laenge"]
        ecken.append((lauf, i + 1))
    for j in range(1, anzahl):
        ziel = gesamt * j / anzahl
        grenzen.append(min(ecken, key=lambda e: abs(e[0] - ziel))[1])
    reihen, start = [], 0
    for g in sorted(set(grenzen)):
        if g > start:
            reihen.append(kanten[start:g])
            start = g
    reihen.append(kanten[start:])
    return reihen


def _massstab(reihen, hoehe, bahnen, kuerzelzeile, legende_mm):
    mass = 3.0 + bahnen * BAHN + (T_KLEIN + 1.5 if kuerzelzeile else 0.0)
    n = len(reihen)
    breite = max(sum(k["laenge"] for k in r) for r in reihen) / (FELD_B - 2 * RAND - HOEHENMASS)
    frei = FELD_H - 2 * RAND - legende_mm - n * (KOPF + mass) - ZEILE * (n - 1)
    if frei <= 5.0:
        return float("inf"), mass
    return max(breite, n * hoehe / frei), mass


def _bahnen(eintraege, luft):
    """Jede Zahl in die oberste Zeile, in der sie ihren Nachbarn nicht beruehrt. eintraege: [(mitte, breite)]."""
    belegt, ergebnis = [], []
    for mitte, breite in eintraege:
        links, rechts = mitte - breite / 2 - luft, mitte + breite / 2 + luft
        for nr, zeile in enumerate(belegt):
            if all(rechts <= l or links >= r for l, r in zeile):
                zeile.append((links, rechts))
                ergebnis.append(nr)
                break
        else:
            belegt.append([(links, rechts)])
            ergebnis.append(len(belegt) - 1)
    return ergebnis


def _cm(wert):
    """Auf ganze Zentimeter - 0,885 wird 0,89, auch wenn die Zahl als 0,88499999 ankommt."""
    return math.floor(wert * 100 + 0.5 + 1e-6) / 100.0


def _rechteck(x, y, b, h):
    return [x, y, x + b, y, x + b, y + h, x, y + h]


# ---------------------------------------------------------------- Zeichnung
def abwicklung(raum, oeffnungen, x0=0.0, y_oben=0.0, sprache="de"):
    """Zeichnung eines Raums. x0/y_oben: linke obere Ecke des Rahmens im Modell (Meter)."""
    worte = TEXTE[sprache]

    def zahl(wert, stellen=2):
        return ("%.*f" % (stellen, _cm(wert) if stellen == 2 else wert)).replace(".", worte["komma"])

    umriss = ring(raum["punkte"])
    kanten = waende(umriss)
    hoehe, z0 = float(raum["hoehe"]), float(raum["z0"])
    if hoehe <= 0.05:
        raise AbwicklungFehler("Der Raum hat keine Höhe.")
    oeffnungen_zuordnen(kanten, oeffnungen, z0, hoehe)

    # Oeffnungsarten und Legende stehen fest, bevor der Massstab gewaehlt wird (die Legende braucht ihren Platz)
    arten = {}
    for kante in kanten:
        for o in kante["oeffnungen"]:
            schluessel = (o["art"], _cm(o["breite"]), _cm(o["hoehe"]), _cm(o["bruestung"]))
            if schluessel not in arten:
                arten[schluessel] = ("T" if o["art"] == "tuer" else "F") + str(1 + sum(1 for s in arten if s[0] == o["art"]))
            o["kuerzel"] = arten[schluessel]
    eintraege = []
    for (art, breite, hoch, bruestung), kuerzel in arten.items():
        eintrag = "%s  %s %s × %s" % (kuerzel, worte["tuer"] if art == "tuer" else worte["fenster"], zahl(breite), zahl(hoch))
        if art != "tuer" and bruestung > 0.005:
            eintrag += ", %s %s" % (worte["bruestung"], zahl(bruestung))
        eintraege.append(eintrag)
    platz = int((FELD_B - 2 * RAND) / (ZEICHEN * T_KLEIN))
    legende = [""]
    for eintrag in eintraege or [worte["ohne"]]:
        if legende[-1] and len(legende[-1]) + 6 + len(eintrag) > platz:
            legende.append("")
        legende[-1] += ("      " if legende[-1] else "") + eintrag
    if len(legende) > LEGENDE_ZEILEN_MAX:
        legende = legende[:LEGENDE_ZEILEN_MAX]
        legende[-1] = legende[-1][:platz - 2] + " …"
    legende_mm = LEGENDE + len(legende) * (T_KLEIN + 1.4)

    bahnen, kuerzelzeile = 1, False
    for _versuch in range(6):
        wahl = None
        for anzahl in range(1, 5):
            reihen = _reihen(kanten, anzahl)
            k, mass = _massstab(reihen, hoehe, bahnen, kuerzelzeile, legende_mm)
            if wahl is None or k < wahl[0] * 0.85:           # mehr Reihen nur, wenn es deutlich groesser wird
                wahl = (k, mass, reihen)
            if anzahl == 1 and k <= K_EINE_REIHE:
                break
        k, mass, reihen = wahl
        if not math.isfinite(k):
            raise AbwicklungFehler("Der Raum ist zu hoch für das Bildfeld.")
        plan = _reihen_planen(reihen, k, zahl)
        noetig = min(BAHNEN_MAX, max(p["bahnen"] for p in plan))
        braucht_kuerzel = any(p["kuerzel_unten"] for p in plan)
        if noetig <= bahnen and braucht_kuerzel == kuerzelzeile:
            break
        bahnen, kuerzelzeile = max(bahnen, noetig), braucht_kuerzel

    bild = {"flaechen": [], "linien": [], "texte": []}

    def text(inhalt, x, y, mm, ausrichtung, farbe=TEXT_DUNKEL, winkel=0.0):
        bild["texte"].append({"text": inhalt, "x": round(x, 4), "y": round(y, 4), "hoehe_m": round(mm * k, 5),
                              "ausrichtung": ausrichtung, "farbe": farbe, "winkel": winkel})

    def linie(punkte, geschlossen=False):
        bild["linien"].append({"punkte": [round(p, 4) for p in punkte], "geschlossen": geschlossen})

    def flaeche(punkte, farbe, reihenfolge):
        bild["flaechen"].append({"punkte": [round(p, 4) for p in punkte], "farbe": farbe, "reihenfolge": reihenfolge})

    y_reihe = y_oben - RAND * k
    for reihe, p in zip(reihen, plan):
        boden = y_reihe - KOPF * k - hoehe
        x_band = x0 + (RAND + HOEHENMASS) * k
        lang = sum(kante["laenge"] for kante in reihe)
        # Hoehenmass links
        xm = x_band - 4.0 * k
        linie([xm, boden, xm, boden + hoehe])
        for yy in (boden, boden + hoehe):
            linie([xm - 0.9 * k, yy, xm + 0.9 * k, yy])
        text(zahl(hoehe), xm - 1.0 * k, boden + hoehe / 2, T_KLEIN, "mitte_unten", TEXT_GRAU, 90.0)
        # das Band: eine Flaeche, ein Umriss, Knicklinien an den Ecken
        flaeche(_rechteck(x_band, boden, lang, hoehe), FARBE_WAND, 2)
        linie(_rechteck(x_band, boden, lang, hoehe), True)
        x = x_band
        for nr, kante in enumerate(reihe):
            if nr:
                linie([x, boden, x, boden + hoehe + 1.6 * k])
            name = "%s %d" % (worte["wand"], kante["nr"])
            if kante["laenge"] < (len(name) * ZEICHEN * T_GROSS + 1.0) * k:
                name = str(kante["nr"])
            if kante["laenge"] >= (len(name) * ZEICHEN * T_GROSS + 0.4) * k:
                text(name, x + kante["laenge"] / 2, boden + hoehe + 1.6 * k, T_GROSS, "mitte_unten")
            for o in kante["oeffnungen"]:
                breite, hoch = o["rechts"] - o["links"], o["oben"] - o["unten"]
                farbe = FARBE_TUER if o["art"] == "tuer" else FARBE_FENSTER
                flaeche(_rechteck(x + o["links"], boden + o["unten"], breite, hoch), farbe, 4)
                linie(_rechteck(x + o["links"], boden + o["unten"], breite, hoch), True)
                kuerzel, mitte = o["kuerzel"], x + o["links"] + breite / 2
                for mm in (T_GROSS, T_KLEIN):
                    if breite >= (len(kuerzel) * ZEICHEN * mm + 0.5) * k and hoch >= (mm + 1.0) * k:
                        text(kuerzel, mitte, boden + o["unten"] + hoch / 2, mm, "mitte")
                        break
                else:
                    text(kuerzel, mitte, boden - 0.9 * k, T_KLEIN, "mitte_oben")      # Kuerzelzeile unter dem Band
            x += kante["laenge"]
        # Masslinie: durchlaufend, JEDER Abschnitt bekommt seine Zahl
        ym = boden - (2.0 + (T_KLEIN + 1.5 if kuerzelzeile else 0.0)) * k
        linie([x_band, ym, x_band + lang, ym])
        for s, ecke in p["marken"]:
            linie([x_band + s, ym - (1.4 if ecke else 0.9) * k, x_band + s, ym + (1.4 if ecke else 0.9) * k])
        for (links, rechts, beschriftung), bahn in zip(p["abschnitte"], p["bahn"]):
            mitte = x_band + (links + rechts) / 2
            y_text = ym - (1.2 + bahn * BAHN) * k
            if bahn:
                linie([mitte, ym, mitte, y_text + 0.3 * k])
            text(beschriftung, mitte, y_text, T_KLEIN, "mitte_oben", TEXT_GRAU)
        y_reihe = boden - mass * k - ZEILE * k
    # Legende am unteren Rand, Zeile fuer Zeile von unten nach oben
    unten_frei = y_oben - (FELD_H - RAND - legende_mm) * k
    for nr, zeile in enumerate(reversed(legende)):
        text(zeile, x0 + RAND * k, y_oben - (FELD_H - RAND - nr * (T_KLEIN + 1.4)) * k, T_KLEIN, "links_unten", TEXT_GRAU)
    _lageskizze(umriss, kanten, x0 + (RAND + HOEHENMASS + 6.0) * k, y_reihe + ZEILE * k - 2.0 * k, unten_frei, k, worte,
                text, linie, flaeche)

    brutto = sum(kante["laenge"] for kante in kanten) * hoehe
    abzug = sum((o["rechts"] - o["links"]) * (o["oben"] - o["unten"]) for kante in kanten for o in kante["oeffnungen"])
    bild["rahmen"] = {"x": round(x0, 4), "y": round(y_oben - FELD_H * k, 4), "laenge": round(FELD_B * k, 4),
                      "breite": round(FELD_H * k, 4)}
    bild["info"] = {
        "raum_id": raum.get("id"), "raum_nr": raum.get("nr"), "name": raum.get("name") or "", "k": k,
        "massstab_1_zu": round(k * 1000), "reihen": len(reihen), "bahnen": bahnen, "waende": len(kanten),
        "waende_m": [round(kante["laenge"], 3) for kante in kanten], "umfang_m": round(sum(kante["laenge"] for kante in kanten), 3),
        "hoehe_m": round(hoehe, 3), "wandflaeche_brutto_m2": round(brutto, 3), "oeffnungen_m2": round(abzug, 3),
        "wandflaeche_netto_m2": round(brutto - abzug, 3),
        "tueren": sum(1 for kante in kanten for o in kante["oeffnungen"] if o["art"] == "tuer"),
        "fenster": sum(1 for kante in kanten for o in kante["oeffnungen"] if o["art"] != "tuer"),
        "abschnitte": sum(len(p["abschnitte"]) for p in plan)}
    return bild


def _reihen_planen(reihen, k, zahl):
    """Je Reihe: Masspunkte, Abschnitte mit Zahl, Zeile jeder Zahl, und ob Kuerzel unter das Band muessen."""
    plan = []
    for reihe in reihen:
        marken, lauf, kuerzel_unten = [(0.0, True)], 0.0, False
        for kante in reihe:
            for o in kante["oeffnungen"]:
                marken += [(lauf + o["links"], False), (lauf + o["rechts"], False)]
                breite, hoch = o["rechts"] - o["links"], o["oben"] - o["unten"]
                if not (breite >= (2 * ZEICHEN * T_KLEIN + 0.5) * k and hoch >= (T_KLEIN + 1.0) * k):
                    kuerzel_unten = True
            lauf += kante["laenge"]
            marken.append((lauf, True))
        eindeutig = {}
        for s, ecke in marken:
            s = round(s, 4)
            eindeutig[s] = eindeutig.get(s, False) or ecke
        punkte = sorted(eindeutig)
        abschnitte = [(a, b, zahl(b - a)) for a, b in zip(punkte, punkte[1:]) if b - a > 0.004]
        bahn = _bahnen([((a + b) / 2, len(t) * ZEICHEN * T_KLEIN * k) for a, b, t in abschnitte], 0.5 * k)
        plan.append({"marken": [(s, eindeutig[s]) for s in punkte], "abschnitte": abschnitte, "bahn": bahn,
                     "bahnen": 1 + max(bahn or [0]), "kuerzel_unten": kuerzel_unten})
    return plan


def _lageskizze(umriss, kanten, x_links, y_oben, y_unten, k, worte, text, linie, flaeche):
    """Kleiner Grundriss des Raums mit Wandnummern, Oeffnungen und Startmarke - nur wenn Platz bleibt."""
    rand = (T_KLEIN + 2.4) * k
    titel = (T_KLEIN + 1.5) * k
    platz = y_oben - y_unten - 2 * rand - titel
    if platz < 12.0 * k:
        return
    text(worte["lage"], x_links, y_oben, T_KLEIN, "links_oben", TEXT_GRAU)
    y_oben -= titel
    xs, ys = [p[0] for p in umriss], [p[1] for p in umriss]
    s = min(110.0 * k / max(max(xs) - min(xs), EPS), platz / max(max(ys) - min(ys), EPS))
    breite, hoch = (max(xs) - min(xs)) * s, (max(ys) - min(ys)) * s
    x_links += rand
    unten = y_oben - rand - hoch

    def lage(p):
        return x_links + (p[0] - min(xs)) * s, unten + (p[1] - min(ys)) * s

    flach = []
    for p in umriss:
        flach += list(lage(p))
    flaeche(flach, FARBE_WAND, 2)
    linie(flach, True)
    dicke = 0.8 * k
    for kante in kanten:
        n, u = kante["aussen"], kante["u"]
        mitte = lage((kante["a"][0] + u[0] * kante["laenge"] / 2, kante["a"][1] + u[1] * kante["laenge"] / 2))
        if kante["laenge"] * s >= 2.6 * k:
            weg = (3.6 if kante["oeffnungen"] else 2.4) * k            # an Oeffnungsmarken vorbei
            text(str(kante["nr"]), mitte[0] + n[0] * weg, mitte[1] + n[1] * weg, T_KLEIN, "mitte")
        for o in kante["oeffnungen"]:
            a = lage((kante["a"][0] + u[0] * o["links"], kante["a"][1] + u[1] * o["links"]))
            b = lage((kante["a"][0] + u[0] * o["rechts"], kante["a"][1] + u[1] * o["rechts"]))
            ecke = [a[0] - n[0] * dicke, a[1] - n[1] * dicke, b[0] - n[0] * dicke, b[1] - n[1] * dicke,
                    b[0] + n[0] * dicke, b[1] + n[1] * dicke, a[0] + n[0] * dicke, a[1] + n[1] * dicke]
            flaeche(ecke, FARBE_TUER if o["art"] == "tuer" else FARBE_FENSTER, 4)
            linie(ecke, True)
    # Startmarke: kleines Dreieck an der ersten Ecke, Spitze in Laufrichtung
    start, u, n = lage(kanten[0]["a"]), kanten[0]["u"], kanten[0]["aussen"]
    g = 1.6 * k
    dreieck = [start[0] + n[0] * 0.4 * g, start[1] + n[1] * 0.4 * g, start[0] + n[0] * 1.6 * g, start[1] + n[1] * 1.6 * g,
               start[0] + u[0] * 1.3 * g + n[0] * g, start[1] + u[1] * 1.3 * g + n[1] * g]
    flaeche(dreieck, TEXT_DUNKEL, 6)


# ---------------------------------------------------------------- mehrere Raeume
def alle(raeume, oeffnungen, x_links=0.0, y_oben=0.0, abstand=3.0, sprache="de"):
    """Alle Raeume untereinander. Liefert (Liste der Zeichnungen, Liste der Raeume, die nicht gingen)."""
    bilder, fehler, y = [], [], y_oben
    for raum in raeume:
        try:
            bild = abwicklung(raum, oeffnungen, x_links, y, sprache)
        except AbwicklungFehler as grund:
            fehler.append({"raum": raum.get("name") or raum.get("nr") or raum.get("id"), "grund": str(grund)})
            continue
        bilder.append(bild)
        y -= bild["rahmen"]["breite"] + abstand
    return bilder, fehler
