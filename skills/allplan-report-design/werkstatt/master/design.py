# -*- coding: utf-8 -*-
"""Design der Reports: Farben und Schrift an EINER Stelle - und die Sperre, die das Design vor dem ersten Report klaert.

Zwei Quellen:
  haus   das Hausdesign (Navy und Tuerkis, Roboto) - gilt, wenn der Anwender nichts anderes vorgibt
  kunde  das Design des Kunden aus einer ausgefuellten design_kunde.json (Stil, Farben, Schrift)

Welche gilt, steht in <Werkstatt>/design.json. Fehlt die Datei, ist das Design OFFEN: core.save() bricht dann ab und
nennt die Fragen an den Anwender. So entsteht kein Report, ohne dass das Design einmal geklaert wurde.

    python master/design.py                      Stand in einer Zeile (DESIGN: OFFEN | HAUS | KUNDE)
    python master/design.py --fragen             die Fragen an den Anwender (Stil, Farben, Schrift)
    python master/design.py --haus --antwort "<Wortlaut des Anwenders>"
                                                 Hausdesign festlegen - erst NACH seiner Antwort auf die Fragen
    python master/design.py --vorlage [datei]    Formular design_kunde.json zum Ausfuellen schreiben
    python master/design.py --kunde <datei>      Kundendesign pruefen und festlegen
    python master/design.py --pruefen [datei]    nur pruefen (Kontraste, Schrift), nichts festlegen
    python master/design.py --tabelle            alle Farben und Schriften des geltenden Designs

Nur automatische Laeufe (Tests, Sammelbau der ausgelieferten Vorlagen) setzen die Umgebungsvariable REPORT_DESIGN=haus
oder =<datei>; dann fragt nichts. Fuer den Report eines Anwenders ist die Variable kein Weg an der Frage vorbei.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WERKSTATT = os.path.normpath(os.path.join(HERE, ".."))
DATEI = os.path.join(WERKSTATT, "design.json")
UMGEBUNG = "REPORT_DESIGN"

# ---------------------------------------------------------------- Hausdesign
# Farben aus der Markenpalette. Auf dunklem Grund gibt es in einer RDLC keine Durchsicht: die Werte "auf_dunkel" sind
# Weiss mit 70 / 60 / 15 / 8 % Deckung, fest auf das Navy gerechnet.
HAUS = {
    "name": "Hausdesign",
    "stil": "Navy traegt, Tuerkis zeigt: dunkles Titelband, heller Inhalt, ruhige Typografie, Tuerkis nur als Markierung.",
    "farben": {
        "tinte": "#062246",             # Ueberschriften, grosse Zahlen (nie reines Schwarz)
        "text": "#062246",              # Fliesstext, Tabellenwerte
        "leise": "#575757",             # Beschriftungen, Achsen
        "fussnote": "#575757",          # Einheiten, Fussnoten
        "linie": "#E7E7E7",             # Haarlinien, Rahmen
        "linie_stark": "#D3D3D3",       # starke Trenner
        "flaeche": "#F6F6F6",           # gedaempfte Flaeche (Kacheln)
        "flaeche_blau": "#E9F1FB",      # Hinweis- und Bandflaeche
        "flaeche_tint": "#D3E4F6",      # Hervorhebung in Listen, Rand von Hinweisen
        "dunkel": "#062246",            # Titelband, dunkle Flaechen
        "leit": "#0F54AC",              # Leitfarbe: Balken, Links, hervorgehobene Zahl auf Weiss
        "akzent": "#00FBC8",            # Tuerkis: auf Dunkel als Text, auf Weiss nur als Flaeche oder Linie
        "gut": "#10B981",
        "achtung": "#F59E0B",
        "schlecht": "#EF4444",
        "weiss": "#FFFFFF",
        "stufen": ["#062246", "#0F54AC", "#365F94", "#7597C2", "#A4BEDC", "#D3E4F6", "#E9F1FB", "#E7E7E7"],
        "serie": ["#062246", "#0F54AC", "#365F94", "#7597C2", "#00FBC8", "#D3E4F6", "#575757", "#D3D3D3"],
    },
    "schrift": {"normal": "Roboto", "leicht": "Roboto Light", "halbfett": "Roboto Medium", "zahl": "Roboto Black"},
}
# Ersatz, wenn eine Schrift auf dem Rechner fehlt, der den Report baut (Segoe UI gehoert zu jedem Windows).
SCHRIFT_ERSATZ = {"normal": "Segoe UI", "leicht": "Segoe UI Light", "halbfett": "Segoe UI Semibold", "zahl": "Segoe UI Semibold"}
# Farben mit Bedeutung (Material) gehoeren nicht zur Marke: Beton ist grau, Mauerwerk ziegelrot - in jedem Design.
MATERIALGRUPPE = [("Beton", "#475569"), ("Mauerwerk", "#C2410C"), ("Dämmung", "#EAB308"), ("Gipskarton", "#94A3B8"),
                  ("Holz", "#A16207"), ("Stahl", "#0E7490"), ("Glas", "#93C5FD"), ("Naturstein", "#78716C"),
                  ("Sonstiges", "#CBD5E1")]

PFLICHT_FARBEN = ("tinte", "dunkel", "leit", "akzent")          # das Mindeste, was ein Kundendesign nennen muss
EINZELFARBEN = ("tinte", "text", "leise", "fussnote", "linie", "linie_stark", "flaeche", "flaeche_blau", "flaeche_tint", "dunkel",
                "leit", "akzent", "gut", "achtung", "schlecht", "weiss")
ROLLEN = ("normal", "leicht", "halbfett", "zahl")
_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

FRAGEN = """Design fuer die Reports - einmal je Werkstatt mit dem Anwender klaeren:

1  Stil       Wie sollen die Reports wirken? (ruhig und sachlich / kraeftig / wie ein vorhandenes Dokument: bitte Beispiel)
              Dunkles Titelband oder heller Kopf? Gibt es ein Logo fuer den Kopf?
2  Farben     Gibt es Hausfarben (CI-Handbuch, Website, Briefbogen)? Gebraucht werden mindestens:
              Textfarbe, dunkle Flaeche (Titelband), Leitfarbe (Balken, Hervorhebung), Akzent (eine Markierung je Seite).
3  Schrift    Welche Schrift ist Hausschrift - und ist sie auf den Rechnern installiert, die den Report oeffnen?
              (Ein Report bettet keine Schrift ein; fehlt sie, nimmt Windows eine andere.)

Erst fragen, dann festlegen. Antwortet der Anwender "nimm den Standard" oder nennt er keine Vorgaben, gilt das
Hausdesign (Navy und Tuerkis, Schrift %s):  python master/design.py --haus --antwort "<sein Wortlaut>"
Mit Vorgaben:  python master/design.py --vorlage   ->  design_kunde.json ausfuellen  ->  python master/design.py --kunde design_kunde.json
""" % HAUS["schrift"]["normal"]


# ---------------------------------------------------------------- Farbrechnung
def _rgb(farbe):
    return tuple(int(farbe[i:i + 2], 16) for i in (1, 3, 5))


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(x)))) for x in rgb)


def mischen(vorn, hinten, deckung):
    """Farbe 'vorn' mit der Deckung 0..1 ueber 'hinten' (eine RDLC kennt keine Durchsicht: der Wert wird fest gerechnet)."""
    return _hex(a * deckung + b * (1 - deckung) for a, b in zip(_rgb(vorn), _rgb(hinten)))


def helligkeit(farbe):
    def kanal(x):
        x /= 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (kanal(x) for x in _rgb(farbe))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def kontrast(a, b):
    """Kontrastverhaeltnis nach WCAG 2 (1 bis 21); 4,5 reicht fuer kleine Schrift, 3 fuer grosse Schrift und Linien."""
    x, y = sorted((helligkeit(a), helligkeit(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def lesbar(farbe, grund="#FFFFFF", ziel=4.5):
    """Dieselbe Farbe, so weit abgedunkelt (auf dunklem Grund: aufgehellt), dass sie als Schrift auf 'grund' das Ziel erreicht."""
    pol = "#000000" if helligkeit(grund) > 0.5 else "#FFFFFF"
    for schritt in range(0, 101, 2):
        kandidat = mischen(pol, farbe, schritt / 100.0)
        if kontrast(kandidat, grund) >= ziel:
            return kandidat
    return pol


def auf(grund, hell="#FFFFFF", dunkel="#000000"):
    """Schriftfarbe auf einer Flaeche: die der beiden mit dem groesseren Kontrast."""
    return hell if kontrast(hell, grund) >= kontrast(dunkel, grund) else dunkel


# ---------------------------------------------------------------- Schrift
def installierte_schriften():
    """Namen der in Windows eingetragenen Schriften (klein geschrieben); None, wenn sie sich nicht lesen lassen."""
    try:
        import winreg
    except ImportError:
        return None
    namen = set()
    for wurzel in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(wurzel, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts") as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    namen.add(re.sub(r"\s*\(.*\)\s*$", "", winreg.EnumValue(key, i)[0]).strip().lower())
        except OSError:
            pass
    return namen or None


def schrift_da(familie, namen):
    """Ist die Familie installiert? 'Roboto Medium' steht als eigener Eintrag, 'Roboto' als 'Roboto' oder 'Roboto Regular';
    Sammeldateien nennen mehrere Namen mit '&' ('Segoe UI & Segoe UI Light ...')."""
    if namen is None:
        return True
    f = familie.strip().lower()
    for eintrag in namen:
        for teil in eintrag.split("&"):
            teil = teil.strip()
            if teil == f or teil in (f + " regular", f + " bold", f + " variable"):
                return True
    return False


# ---------------------------------------------------------------- Laden und Ableiten
def ableiten(farben):
    """Ergaenzt ein Kundendesign: aus den Pflichtfarben folgt alles, was nicht genannt ist (Flaechen, Stufen, Serie)."""
    f = dict(farben)
    weiss = f.setdefault("weiss", "#FFFFFF")
    f.setdefault("text", f["tinte"])
    f.setdefault("leise", lesbar(mischen(f["tinte"], weiss, 0.6), weiss))
    f.setdefault("fussnote", f["leise"])
    f.setdefault("linie", mischen(f["tinte"], weiss, 0.10))
    f.setdefault("linie_stark", mischen(f["tinte"], weiss, 0.20))
    f.setdefault("flaeche", mischen(f["tinte"], weiss, 0.04))
    f.setdefault("flaeche_blau", mischen(f["leit"], weiss, 0.10))
    f.setdefault("flaeche_tint", mischen(f["leit"], weiss, 0.20))
    for name, wert in (("gut", HAUS["farben"]["gut"]), ("achtung", HAUS["farben"]["achtung"]), ("schlecht", HAUS["farben"]["schlecht"])):
        f.setdefault(name, wert)
    f.setdefault("stufen", [f["dunkel"], f["leit"]] + [mischen(f["leit"], weiss, d) for d in (0.75, 0.55, 0.40, 0.25, 0.14, 0.08)])
    f.setdefault("serie", [f["dunkel"], f["leit"], mischen(f["leit"], weiss, 0.75), mischen(f["leit"], weiss, 0.5), f["akzent"],
                           mischen(f["leit"], weiss, 0.2), f["leise"], f["linie_stark"]])
    # keine Farbe zweimal (Akzent = Leitfarbe, Tinte = dunkel ...): die Dublette weicht auf eine Mischung aus Tinte und Weiss aus
    serie, ersatz = [], [mischen(f["tinte"], weiss, d) for d in (0.5, 0.3, 0.7, 0.15, 0.85, 0.4, 0.6, 0.2)]
    for farbe in f["serie"]:
        while farbe.upper() in (x.upper() for x in serie) and ersatz:
            farbe = ersatz.pop(0)
        serie.append(farbe)
    f["serie"] = serie
    return f


class Design(object):
    """Das geltende Design, fertig gerechnet. core.py legt daraus seine Konstanten an."""

    def __init__(self, quelle, roh, festgelegt="", hinweis=""):
        self.quelle = quelle                      # "haus" | "kunde" | "offen"
        self.hinweis = hinweis                    # warum offen, wenn es eine design.json gibt (unlesbar, ungueltig)
        self.name = roh.get("name") or ("Hausdesign" if quelle != "kunde" else "Kundendesign")
        self.stil = roh.get("stil", "")
        self.festgelegt = festgelegt
        self.farben = ableiten(roh["farben"])
        f = self.farben
        # Abgeleitete Farben: Schrift auf dunklem Grund (Weiss mit 70 / 60 %), Linie und Flaeche auf Dunkel (15 / 8 %)
        self.auf_dunkel = mischen(f["weiss"], f["dunkel"], 0.70)
        self.auf_dunkel_leise = mischen(f["weiss"], f["dunkel"], 0.60)
        self.dunkel_linie = mischen(f["weiss"], f["dunkel"], 0.15)
        self.dunkel_flaeche = mischen(f["weiss"], f["dunkel"], 0.08)
        # Akzent als Schrift auf Weiss: nur wenn er lesbar ist (Tuerkis ist es nicht) - sonst traegt die Leitfarbe die Schrift
        self.akzent_text = f["akzent"] if kontrast(f["akzent"], f["weiss"]) >= 4.5 else f["leit"]
        self.auf_akzent = auf(f["akzent"], f["weiss"], f["tinte"])
        self.akzent_auf_dunkel = f["akzent"] if kontrast(f["akzent"], f["dunkel"]) >= 4.5 else f["weiss"]
        # Bewertungsfarben als Schrift auf Weiss: abgedunkelt, bis sie lesbar sind (die reine Farbe bleibt fuer Flaechen und Punkte)
        self.gut_text, self.achtung_text, self.schlecht_text = (lesbar(f[k], f["weiss"]) for k in ("gut", "achtung", "schlecht"))
        self.schrift_soll = dict(HAUS["schrift"] if quelle != "kunde" else {}, **roh.get("schrift", {}))
        for rolle in ROLLEN:
            self.schrift_soll.setdefault(rolle, self.schrift_soll.get("normal", HAUS["schrift"]["normal"]))
        # Im Report steht die Soll-Schrift als Ausdruck (schrift_zur_laufzeit): der Rechner, der den Report OEFFNET, waehlt sie -
        # oder, wenn ihm eine der Familien fehlt, den Ersatz. schrift_fehlt nennt nur, was DIESEM Rechner fehlt (fuer die Meldung).
        namen = installierte_schriften()
        self.schrift = dict(self.schrift_soll)
        self.schrift_fehlt = [self.schrift_soll[r] for r in ROLLEN if not schrift_da(self.schrift_soll[r], namen)]

    def zeile(self):
        """Der Stand in einer Zeile - geht woertlich an den Anwender."""
        if self.quelle == "offen":
            return "DESIGN: OFFEN | %s | python master/design.py --fragen" % (self.hinweis or "noch nicht festgelegt")
        art = "HAUS" if self.quelle == "haus" else "KUNDE"
        ersatz = "" if not self.schrift_fehlt else " | Schrift fehlt auf diesem Rechner: %s -> Reports zeigen hier %s" % (
            ", ".join(sorted(set(self.schrift_fehlt))), SCHRIFT_ERSATZ["normal"])
        return "DESIGN: %s | %s | Schrift %s | festgelegt %s%s" % (art, self.name, self.schrift_soll["normal"], self.festgelegt or "-", ersatz)


def pruefen(roh):
    """Befunde zu einem Design als Liste (Stufe, Text); Stufe 'FEHLER' verhindert das Festlegen, 'HINWEIS' nicht."""
    befunde = []
    farben = roh.get("farben")
    if not isinstance(farben, dict):
        return [("FEHLER", "Abschnitt 'farben' fehlt.")]
    for name in PFLICHT_FARBEN:
        if name not in farben:
            befunde.append(("FEHLER", "Farbe '%s' fehlt (Pflicht: %s)." % (name, ", ".join(PFLICHT_FARBEN))))
    for name, wert in farben.items():
        werte = wert if isinstance(wert, list) else [wert]
        if name not in EINZELFARBEN + ("stufen", "serie"):
            befunde.append(("FEHLER", "Farbe '%s' kennt der Bausatz nicht (bekannt: %s, stufen, serie)." % (name, ", ".join(EINZELFARBEN))))
        elif not all(isinstance(w, str) and _HEX.match(w) for w in werte):
            befunde.append(("FEHLER", "Farbe '%s': nur Werte der Form #RRGGBB (ohne Durchsicht) - gefunden %r." % (name, wert)))
        elif name in ("stufen", "serie") and len(werte) != 8:
            befunde.append(("FEHLER", "'%s' braucht genau 8 Farben, gefunden %d." % (name, len(werte))))
    if any(stufe == "FEHLER" for stufe, _ in befunde):
        return befunde
    f = ableiten(farben)
    weiss = f["weiss"]
    for name, mindestens in (("tinte", 4.5), ("text", 4.5), ("leise", 4.5), ("fussnote", 4.5), ("leit", 4.5)):
        k = kontrast(f[name], weiss)
        if k < mindestens:
            befunde.append(("FEHLER", "'%s' %s ist als Schrift auf Weiss zu schwach (Kontrast %.1f, noetig %.1f)." % (name, f[name], k, mindestens)))
    if kontrast(weiss, f["dunkel"]) < 4.5:
        befunde.append(("FEHLER", "'dunkel' %s ist zu hell fuer weisse Schrift (Kontrast %.1f, noetig 4.5)." % (f["dunkel"], kontrast(weiss, f["dunkel"]))))
    k = kontrast(f["akzent"], weiss)
    if k < 4.5:
        befunde.append(("HINWEIS", "Akzent %s traegt auf Weiss keine Schrift (Kontrast %.1f): er erscheint dort nur als Flaeche oder Linie, "
                                   "hervorgehobene Schrift nimmt die Leitfarbe." % (f["akzent"], k)))
    if kontrast(f["akzent"], f["dunkel"]) < 4.5:
        befunde.append(("HINWEIS", "Akzent %s hebt sich vom dunklen Grund %s kaum ab (Kontrast %.1f): auf dem Titelband steht dann Weiss."
                        % (f["akzent"], f["dunkel"], kontrast(f["akzent"], f["dunkel"]))))
    for name in ("gut", "achtung", "schlecht"):
        if kontrast(f[name], weiss) < 1.5:
            befunde.append(("FEHLER", "Bewertungsfarbe '%s' %s ist auf Weiss nicht zu sehen (Kontrast %.1f, noetig 1.5)." % (name, f[name], kontrast(f[name], weiss))))
    for name in ("stufen", "serie"):
        verschieden = len(set(x.upper() for x in f[name]))
        if verschieden < 6:
            befunde.append(("FEHLER", "'%s' braucht mindestens 6 verschiedene Farben, gefunden %d." % (name, verschieden)))
        blass = [x for x in f[name][:5] if kontrast(x, weiss) < 1.3]
        if blass:
            befunde.append(("FEHLER", "'%s': %s ist auf Weiss nicht zu sehen (die ersten fuenf Farben tragen die Diagramme)." % (name, ", ".join(blass))))
    if kontrast(f["stufen"][0], weiss) < 3:
        befunde.append(("FEHLER", "'stufen': die erste Stufe %s ist zu hell (groesste = dunkelste; Kontrast %.1f, noetig 3)." % (f["stufen"][0], kontrast(f["stufen"][0], weiss))))
    for marke in ("leit", "akzent"):
        for name in ("gut", "achtung", "schlecht"):
            if sum((a - b) ** 2 for a, b in zip(_rgb(f[marke]), _rgb(f[name]))) ** 0.5 < 70:
                befunde.append(("HINWEIS", "'%s' %s aehnelt der Bewertungsfarbe '%s' %s: der Leser kann Marke und Bewertung verwechseln - "
                                           "Bewertung steht deshalb nie ohne Wort oder Zeichen; bei Bedarf '%s' im Formular anders setzen."
                                % (marke, f[marke], name, f[name], name)))
    schrift = roh.get("schrift", {})
    if not isinstance(schrift, dict) or any(r not in ROLLEN for r in schrift):
        befunde.append(("FEHLER", "Abschnitt 'schrift': nur die Rollen %s." % ", ".join(ROLLEN)))
    elif any(not isinstance(v, str) or not v.strip() or any(z in v for z in '<>&"') for v in schrift.values()):
        befunde.append(("FEHLER", "Abschnitt 'schrift': je Rolle ein Familienname als Text, nicht leer und ohne die Zeichen < > & \"."))
    else:
        if schrift and "normal" not in schrift:
            befunde.append(("FEHLER", "Abschnitt 'schrift': die Rolle 'normal' fehlt."))
        fehlend = [r for r in ("halbfett", "zahl") if schrift and r not in schrift]
        if fehlend:
            befunde.append(("HINWEIS", "Schrift: ohne eigene Familie fuer %s gilt dort die Normalschrift - Ueberschriften und Kennzahlen "
                                       "verlieren ihr Gewicht. Fette Schnitte sind eigene Familien (z. B. 'Arial Black')." % " und ".join(fehlend)))
        namen = installierte_schriften()
        for rolle, familie in schrift.items():
            if not schrift_da(familie, namen):
                befunde.append(("HINWEIS", "Schrift '%s' (%s) ist auf diesem Rechner nicht installiert: Reports zeigen hier '%s'."
                                % (familie, rolle, SCHRIFT_ERSATZ[rolle])))
    return befunde


# ---------------------------------------------------------------- Schrift zur Laufzeit
# In Allplan gemessen (2026-11-20, PDF und Report-Fenster): <FontFamily> darf ein Ausdruck sein. Der Report fragt beim Oeffnen
# die in Windows eingetragenen Schriften ab (Registry, braucht keine Zusatz-Bibliothek) und nimmt die Soll-Familien nur, wenn
# ALLE da sind - sonst den Ersatz (auch wenn sich die Liste nicht lesen laesst: den Ersatz gibt es auf jedem Windows). Ohne das setzt Windows bei fehlender Schrift alles in "Microsoft Sans Serif" (gemessen:
# Gewichte weg, einzelne Zeichen als leere Kaestchen).
_VB_SCHRIFT = r'''
Private rd_schrift() As String = Nothing
Public Function Schrift(ByVal rolle As Integer) As String
    If rd_schrift Is Nothing Then
        Dim soll() As String = {%s}
        Dim ersatz() As String = {%s}
        Dim namen As String = "|"
        Try
            For Each wurzel As Microsoft.Win32.RegistryKey In New Microsoft.Win32.RegistryKey() {Microsoft.Win32.Registry.LocalMachine, Microsoft.Win32.Registry.CurrentUser}
                Dim k As Microsoft.Win32.RegistryKey = wurzel.OpenSubKey("SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
                If Not k Is Nothing Then
                    For Each n As String In k.GetValueNames()
                        Dim p As Integer = n.IndexOf(" (")
                        If p > 0 Then n = n.Substring(0, p)
                        For Each teil As String In n.Split("&"c)
                            namen &= teil.Trim().ToLowerInvariant() & "|"
                        Next
                    Next
                    k.Close()
                End If
            Next
        Catch
            namen = ""
        End Try
        Dim alle As Boolean = (namen <> "")
        For i As Integer = 0 To soll.Length - 1
            Dim f As String = soll(i).ToLowerInvariant()
            If Not (namen.Contains("|" & f & "|") OrElse namen.Contains("|" & f & " regular|") OrElse namen.Contains("|" & f & " bold|") OrElse namen.Contains("|" & f & " variable|")) Then alle = False
        Next
        If alle Then rd_schrift = soll Else rd_schrift = ersatz
    End If
    Return rd_schrift(rolle)
End Function
'''


def schrift_zur_laufzeit(xml, design, esc):
    """Ersetzt im fertigen Report jede Soll-Familie durch den Ausdruck =Code.Schrift(n) und haengt die Funktion an den Code.
    Familien, die schon der Ersatz sind (oder fremde wie in einem Kundenlayout), bleiben fest stehen."""
    rollen = [r for r in ROLLEN if design.schrift_soll[r] != SCHRIFT_ERSATZ[r]]
    familien = []
    for r in rollen:
        if design.schrift_soll[r] not in familien:
            familien.append(design.schrift_soll[r])
    treffer = 0
    for i, familie in enumerate(familien):
        alt = "<FontFamily>%s</FontFamily>" % esc(familie)
        treffer += xml.count(alt)
        xml = xml.replace(alt, "<FontFamily>=Code.Schrift(%d)</FontFamily>" % i)
    if not treffer:
        return xml
    ersatz = [SCHRIFT_ERSATZ[next(r for r in rollen if design.schrift_soll[r] == f)] for f in familien]
    vb = esc(_VB_SCHRIFT % (", ".join('"%s"' % f.replace('"', '""') for f in familien), ", ".join('"%s"' % f for f in ersatz)))
    if "</Code>" in xml:
        return xml.replace("</Code>", vb + "</Code>", 1)
    return xml.replace("<Code />", "<Code>%s</Code>" % vb, 1) if "<Code />" in xml else xml.replace("</Report>", "<Code>%s</Code></Report>" % vb, 1)


def _lies(pfad):
    with open(pfad, encoding="utf-8-sig") as handle:
        return json.load(handle)


def _gueltig(roh):
    """Fehlertext, wenn das Kundendesign nicht brauchbar ist - sonst ''."""
    if not isinstance(roh, dict):
        return "kein Design (erwartet: ein Objekt mit 'farben')"
    fehler = [text for stufe, text in pruefen({k: v for k, v in roh.items() if not k.startswith("_")}) if stufe == "FEHLER"]
    return fehler[0] if fehler else ""


def laden():
    """Das geltende Design: Umgebungsvariable vor design.json; ohne beides das Hausdesign mit dem Vermerk 'offen'.
    Eine design.json, die sich nicht lesen laesst oder keine gueltige Quelle nennt, zaehlt als OFFEN (mit Grund) - nie still als Haus."""
    wahl = os.environ.get(UMGEBUNG, "").strip()
    if wahl.lower() == "haus":
        return Design("haus", HAUS, "automatischer Lauf")
    if wahl:
        try:
            roh = _lies(wahl)
        except (OSError, ValueError) as fehler:
            raise SystemExit("FEHLER: %s=%s laesst sich nicht lesen (%s)." % (UMGEBUNG, wahl, fehler))
        grund = _gueltig(roh)
        if grund:
            raise SystemExit("FEHLER: %s=%s ist kein gueltiges Design: %s" % (UMGEBUNG, wahl, grund))
        return Design("kunde", {k: v for k, v in roh.items() if not k.startswith("_")}, "automatischer Lauf")
    if not os.path.isfile(DATEI):
        return Design("offen", HAUS)
    try:
        stand = _lies(DATEI)
    except (OSError, ValueError) as fehler:
        return Design("offen", HAUS, hinweis="design.json laesst sich nicht lesen (%s)" % fehler)
    quelle = str(stand.get("quelle", "")).strip().lower() if isinstance(stand, dict) else ""
    if quelle == "haus":
        return Design("haus", HAUS, str(stand.get("festgelegt", "")))
    if quelle == "kunde":
        grund = _gueltig(stand.get("design"))
        if grund:
            return Design("offen", HAUS, hinweis="design.json: Kundendesign ungueltig - %s" % grund)
        return Design("kunde", stand["design"], str(stand.get("festgelegt", "")))
    return Design("offen", HAUS, hinweis="design.json nennt keine gueltige Quelle (haus oder kunde)")


def sperre(design):
    """Bricht ab, solange das Design offen ist. core.save() ruft das vor jedem Schreiben eines Reports."""
    if design.quelle == "offen":
        sys.stderr.write("\n" + design.zeile() + "\n\n" + FRAGEN + "\n")
        raise SystemExit(3)


# ---------------------------------------------------------------- Befehle
def _festlegen(stand):
    stand["festgelegt"] = datetime.date.today().isoformat()
    with open(DATEI, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(stand, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _melde(befunde):
    for stufe, text in befunde:
        print("%s: %s" % (stufe, text))
    fehler = sum(1 for stufe, _ in befunde if stufe == "FEHLER")
    hinweise = len(befunde) - fehler
    print("AMPEL: %s | design | %d Fehler, %d Hinweise" % ("ROT" if fehler else ("ORANGE" if hinweise else "GRUEN"), fehler, hinweise))
    return fehler


def vorlage():
    """Formular fuer ein Kundendesign: die vier Pflichtfarben und die Schrift; alles Weitere rechnet der Bausatz daraus."""
    f = HAUS["farben"]
    return {"name": "<Name des Bueros>",
            "stil": "<ein Satz: wie sollen die Reports wirken?>",
            "farben": {k: f[k] for k in PFLICHT_FARBEN},
            "schrift": dict(HAUS["schrift"]),
            "_hilfe": {"farben": "Pflicht: %s. Moeglich ausserdem: %s, stufen und serie (je 8 Farben). Nur #RRGGBB."
                                 % (", ".join(PFLICHT_FARBEN), ", ".join(k for k in EINZELFARBEN if k not in PFLICHT_FARBEN)),
                       "schrift": "Familienname je Rolle, wie Windows ihn nennt (z. B. 'Arial', 'Arial Black'). Fette Schnitte sind eigene Familien.",
                       "akzent": "Ist der Akzent auf Weiss zu hell fuer Schrift, zeigt der Bausatz ihn dort nur als Flaeche oder Linie."}}


def tabelle(design):
    zeilen = ["%-18s %s" % (k, v if isinstance(v, str) else " ".join(v)) for k, v in design.farben.items()]
    zeilen += ["%-18s %s" % (k, getattr(design, k)) for k in ("auf_dunkel", "auf_dunkel_leise", "dunkel_linie", "dunkel_flaeche", "akzent_text",
                                                             "auf_akzent", "akzent_auf_dunkel", "gut_text", "achtung_text", "schlecht_text")]
    zeilen += ["schrift %-10s %s" % (r, design.schrift[r]) for r in ROLLEN]
    return "\n".join(zeilen)


def main(argumente):
    if "--fragen" in argumente:
        print(FRAGEN)
        return 0
    antwort = next((a[10:] for a in argumente if a.startswith("--antwort=")), None)
    if antwort is None and "--antwort" in argumente[:-1]:
        antwort = argumente[argumente.index("--antwort") + 1]
        argumente = [a for i, a in enumerate(argumente) if i not in (argumente.index("--antwort"), argumente.index("--antwort") + 1)]
    if "--haus" in argumente:
        if not (antwort or "").strip():
            print("FEHLER: --haus braucht die Antwort des Anwenders auf die Design-Fragen:\n"
                  "  python master/design.py --haus --antwort \"<sein Wortlaut, z. B. nimm den Standard>\"\n"
                  "Noch nicht gefragt? Erst fragen:  python master/design.py --fragen")
            return 2
        _festlegen({"quelle": "haus", "name": HAUS["name"], "antwort": antwort.strip()})
        print(laden().zeile())
        return 0
    if "--vorlage" in argumente:
        rest = [a for a in argumente if not a.startswith("--")]
        ziel = rest[0] if rest else os.path.join(WERKSTATT, "design_kunde.json")
        if os.path.exists(ziel):
            print("FEHLER: %s gibt es schon - nichts ueberschrieben." % ziel)
            return 2
        with open(ziel, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(vorlage(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("Formular geschrieben: %s" % ziel)
        return 0
    for schalter in ("--kunde", "--pruefen"):
        if schalter in argumente:
            rest = [a for a in argumente if not a.startswith("--")]
            if not rest and schalter == "--pruefen":
                roh = laden()
                roh = {"farben": roh.farben, "schrift": dict(roh.schrift_soll)}
            elif not rest:
                print("FEHLER: Datei fehlt -  python master/design.py --kunde design_kunde.json")
                return 2
            else:
                try:
                    roh = _lies(rest[0])
                except (OSError, ValueError) as fehler:
                    print("FEHLER: %s laesst sich nicht lesen (%s)." % (rest[0], fehler))
                    return 2
                if not isinstance(roh, dict):
                    print("FEHLER: %s enthaelt kein Design (erwartet: ein Objekt mit 'farben', siehe --vorlage)." % rest[0])
                    return 2
            roh = {k: v for k, v in roh.items() if not k.startswith("_")}
            if _melde(pruefen(roh)):
                return 1
            if schalter == "--kunde":
                _festlegen(dict({"quelle": "kunde", "design": roh}, **({"antwort": antwort.strip()} if (antwort or "").strip() else {})))
                print(laden().zeile())
            return 0
    design = laden()
    if "--tabelle" in argumente:
        print(tabelle(design))
    print(design.zeile())
    return 3 if design.quelle == "offen" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
