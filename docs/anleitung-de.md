# Allplan Report Design – Anleitung

*Deutsch · [English](guide-en.md)*

Diese Anleitung zeigt Schritt für Schritt, wie du den Skill einrichtest, deine Werkstatt anlegst, einen ersten eigenen Report bauen lässt, ihn prüfst und in Allplan öffnest. Du brauchst dafür keine Programmierkenntnisse. Die Kurzfassung steht in der [README](../README.md).

## 1. Überblick

Der Skill macht deine KI zum Helfer für gestaltete Allplan-Reports. Er enthält:

- **allplan-report-design**: das Wissen zum Gestalten (was in Allplan-Reports geht und was nicht), einen Bausatz mit dem Master-Report und sechs Begleit-Reports (zusammen sieben Vorlagen je Sprache, 81 Bausteine) und die Werkzeuge zum Bauen und Ansehen.
- **allplan-report**: die Grundlagen für jeden Allplan-Report: wie Abfragen aufgebaut sind, wie du Attribute nachschlägst und wie ein Report geprüft wird.

**Was du brauchst**

| | |
|---|---|
| Allplan 2027 | zum Öffnen der fertigen Reports und für die Vorschau am Rechner |
| Eine KI mit Dateizugriff | GitHub Copilot in VS Code (Agent-Modus), Claude Code oder Codex. Sie muss Dateien lesen und Befehle ausführen dürfen. |
| Python 3.10 oder neuer | Für Bauen und Prüfen genügt das Python von Allplan 2027, es ist schon da: `C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe` |
| Nur für zwei Nebenwerkzeuge: ein eigenes Python 3.10 oder neuer | PDF-Seiten als Bilder ablegen (`python -m pip install pymupdf pillow`) und die mitgelieferten Tests (`python -m pip install pytest`). Im Python von Allplan fehlen PyMuPDF und pytest; Pillow ist dort vorhanden. Bauen, Vorschau, englische Fassung und Prüfen brauchen sie nicht. |

**Begriffe**

- **Skill**: eine Anleitung samt Werkzeugen, die deine KI liest, bevor sie arbeitet.
- **Projektordner**: der Ordner, den du in VS Code oder im Terminal öffnest. Dort liegt der Skill.
- **Werkstatt**: ein eigener Arbeitsordner mit dem Bausatz für Reports. Die fertigen Reports liegen im Unterordner `out`.
- **Baustein**: ein fertiger Abschnitt eines Reports, zum Beispiel ein Diagramm. Jeder hat eine Kennung wie `D040`. Es gibt 81 Bausteine: 50 im Master, 31 in den sechs Begleit-Reports.
- **Teilbild**: die Zeichnungsdatei in Allplan, in der dein Modell liegt.

## 2. Skill einrichten

### 2.1 Repo ablegen

Lade das Repo herunter oder kopiere es an eine Stelle mit kurzem Pfad, zum Beispiel `C:\Allplan-Tools\allplan-report-design`. Es bleibt dort als Vorlage liegen. In deinen Projektordner kommen Kopien.

### 2.2 Projektordner anlegen

Lege einen leeren Ordner mit kurzem Pfad an, zum Beispiel `C:\Projekte\Reports`. Das ist dein Projektordner.

### 2.3 Wohin welche Ordner gehören

Kopiere den **Inhalt** des Repo-Ordners `skills\` in den Skill-Ordner deines Werkzeugs. Das sind die zwei Ordner `allplan-report-design` und `allplan-report`.

| Werkzeug | Zielordner im Projektordner |
|---|---|
| GitHub Copilot in VS Code | `.github\skills\` |
| Claude Code | `.claude\skills\` |
| Codex (Programmier-Werkzeug von OpenAI) | `.agents\skills\` |

Am Beispiel **GitHub Copilot** sieht der Projektordner danach so aus:

```
C:\Projekte\Reports\
└── .github\
    └── skills\
        ├── allplan-report-design\     ← mit SKILL.md und weiteren Dateien
        └── allplan-report\            ← mit SKILL.md, references, scripts
```

Bei Claude Code heißt der obere Ordner `.claude`, bei Codex `.agents`.

### 2.4 Schritt für Schritt im Windows-Explorer

Beispiel GitHub Copilot, Repo unter `C:\Allplan-Tools\allplan-report-design`, Projektordner `C:\Projekte\Reports`:

1. Im Projektordner einen neuen Ordner `.github` anlegen. Lässt der Explorer den Namen mit Punkt am Anfang nicht zu, gib `.github.` ein (mit Punkt am Ende). Windows entfernt den Punkt am Ende selbst.
2. In `.github` einen Ordner `skills` anlegen.
3. Aus dem Repo-Ordner `skills` die zwei Ordner `allplan-report-design` und `allplan-report` nach `.github\skills\` kopieren.

Für Claude Code und Codex genauso, nur mit dem Zielordner aus 2.3.

### 2.5 Alternativ in PowerShell

Zuerst die zwei Pfade anpassen, dann nur den Block für dein Werkzeug ausführen:

```powershell
$repo    = "C:\Allplan-Tools\allplan-report-design"
$projekt = "C:\Projekte\Reports"

# GitHub Copilot
New-Item -ItemType Directory -Force "$projekt\.github\skills" | Out-Null
Copy-Item "$repo\skills\*" "$projekt\.github\skills\" -Recurse -Force

# Claude Code
New-Item -ItemType Directory -Force "$projekt\.claude\skills" | Out-Null
Copy-Item "$repo\skills\*" "$projekt\.claude\skills\" -Recurse -Force

# Codex
New-Item -ItemType Directory -Force "$projekt\.agents\skills" | Out-Null
Copy-Item "$repo\skills\*" "$projekt\.agents\skills\" -Recurse -Force
```

### 2.6 Projektordner im Werkzeug öffnen

- **VS Code mit GitHub Copilot:** *Datei → Ordner öffnen…* und den Projektordner wählen. Wurden die Ordner bei offenem VS Code angelegt, einmal neu laden: `Strg+Umschalt+P`, dann *Developer: Reload Window*. Im Copilot-Chat den **Agent-Modus** wählen.
- **Claude Code:** im Terminal in den Projektordner wechseln und starten:
  ```powershell
  cd C:\Projekte\Reports
  claude
  ```
- **Codex:** im Terminal in den Projektordner wechseln und `codex` starten.

### 2.7 Mehrere Werkzeuge im selben Projektordner

Das geht. GitHub Copilot liest Skills auch aus `.claude\skills` und `.agents\skills`. Wer Copilot zusammen mit Claude Code oder Codex nutzt, lässt deshalb `.github\skills` weg, sonst sieht Copilot den Skill doppelt.

### 2.8 ChatGPT im Chatfenster

Das reine Chatfenster kann keine Dateien in deinem Ordner lesen und keine Befehle ausführen. Der Skill ist für eine KI gedacht, die das kann. Im Chatfenster kannst du `SKILL.md` und den Ordner `references\` als Wissen hochladen und dir Bauskripte schreiben lassen, die du selbst ausführst. **Das ist nicht erprobt.**

> **Nicht erprobt:** Das Einrichten in Copilot, Codex und Claude Code mit genau diesem Skill wurde nicht an einem fremden Rechner ausprobiert. Die Ordner sind die, an denen diese Werkzeuge Skills erwarten. Stimmt bei dir etwas nicht, melde es über die [Issues](../../../issues).

## 3. Prüfen, ob die KI den Skill sieht

Stelle einfach eine Frage, die der Skill beantworten kann:

> „Was geht in einem Allplan-Report an Diagrammen, und was geht nicht?"

Die KI sollte sich auf den Skill `allplan-report-design` beziehen und eine Tabelle oder Liste aus dessen Wissen wiedergeben. Antwortet sie nur allgemein, prüfe den Ordnernamen (er muss genau `allplan-report-design` heißen und direkt die Datei `SKILL.md` enthalten) und starte eine neue Sitzung.

## 4. Werkstatt anlegen

Die Werkstatt ist dein Arbeitsordner für Reports. Du kannst die KI bitten:

> „Lege die Werkstatt im Ordner reports an und zeig mir den Master."

Oder du führst es selbst aus, hier für Copilot im Projektordner:

```powershell
python .github\skills\allplan-report-design\werkstatt_anlegen.py reports
```

Der Befehl kopiert Bausatz, Werkzeuge und Vorlagen aus dem Skill in den Ordner `reports` und legt dort den leeren Ordner `out` an. Er bricht ab, wenn `reports` schon Dateien enthält. Gearbeitet wird nur in dieser Kopie, der Skill selbst bleibt unverändert.

In `master\core.py` steht `VERFASSER = "W. Liffers"`. Ändere das vor deinem ersten eigenen Report auf deinen Namen (oder sag es der KI). Sonst trägt jede erzeugte Datei diesen Namen.

Das Anzeigeprogramm für die Vorschau baut die KI beim ersten Mal selbst. Es nutzt dafür die Programmdateien von Allplan 2027. Dazu startet sie ein PowerShell-Skript mit dem Schalter `-ExecutionPolicy Bypass`. Die KI fragt vorher nach. Das ist erwartet und betrifft nur dieses eine Skript. Danach zeigt sie dir die zehn Seiten des Masters als Bilder.

## 5. Dein erster eigener Report

### 5.1 Auftrag formulieren

Beschreibe den Report so, wie du ihn einer Kollegin beschreiben würdest. Am einfachsten ist die Bestellung per Kennung (siehe README, Abschnitt „Bestellen per Kennung“):

> „Baue mir einen einseitigen Report mit K010, D040 und T020, Titel ‚Rohbau-Übersicht', ohne Kennungs-Zeilen."

Du kannst auch ohne Kennungen sagen, was du sehen willst: „Ein Diagramm der größten Bauteile und eine Kennzahl für das Gesamtvolumen." Die KI sucht passende Bausteine im Master und nennt dir ihre Kennungen.

Das Stapeln per Kennung gilt für die 50 Master-Bausteine. Die 31 Bausteine der Begleit-Reports haben eine eigene Abfrage und werden mit ihrem Report gebaut. Nennst du so eine Kennung beim Stapeln, sagt dir `build_auswahl.py` das mit Namen.

Für die Begleit-Reports Bewehrung, Planliste und Listen genügen Sätze in Alltagssprache:

> „Baue mir eine Bewehrungs-Übersicht für dieses Teilbild."
>
> „Ich brauche eine Bauteilliste je Art, jede Art auf eigener Seite, mit QR-Code."
>
> „Zeig mir, was an meinen Plänen noch fehlt."

Bei einem neuen Wunsch sieht die KI zuerst in ihrer Liste „Wunsch → Weg“ nach (60 Einträge mit dem Urteil „geht“, „geht mit Kniff“ oder „geht nicht“ und dem Weg dorthin). Geht etwas nicht, sagt sie dir das ehrlich.

### 5.2 Rückfragen beantworten

Die KI fragt nur, was sie nicht sicher annehmen kann: zum Beispiel, ob Abbruchbauteile mitzählen oder welche Größen du sehen willst. Antworte kurz. Alles, was sie annimmt, nennt sie dir am Ende.

### 5.3 Ergebnis ansehen

Nach dem Bauen liegt die Datei in `out\`. Die KI zeigt dir ein Vorschaubild. Es entsteht ohne Allplan aus Beispieldaten und zeigt Aufbau und Diagramme. Die Zahlen sind daher Beispielzahlen, nicht die deines Modells. Schau dir das Bild genau an und sag, was anders sein soll, zum Beispiel „Die Überschrift ist zu lang" oder „Nimm noch D030 dazu".

### 5.4 Änderungen und andere Sprache

| Vorhaben | Beispiel |
|---|---|
| Baustein ändern | „Ich brauche D040, aber mit den zehn größten Räumen statt Bauteilen." |
| Baustein ergänzen | „Nimm noch M020 dazu." |
| Englische Fassung | „Mach daraus die englische Fassung." (Datei in `out\eng\`) |

Braucht eine Änderung Daten, die der Report noch nicht abfragt, erweitert die KI die Abfrage. Sie bittet dich dann vielleicht, in Allplan einen kleinen Probe-Report als Excel-Datei auszugeben. Daraus macht sie neue Beispieldaten.

**Englische Fassung eines eigenen Reports.** Die KI trägt die neuen Texte des Reports mit `python master\sprache.py --sammeln out\<Datei>.rdlc` in die Tabelle `master\sprache\en\eigene.json` ein (jeweils mit dem Wert `null`) und füllt sie englisch. `python master\sprache.py --offen out\<Datei>.rdlc` muss dann 0 zeigen. Danach erzeugt `python master\sprache.py --en out\<Datei>.rdlc` die Datei in `out\eng\`. Ohne Dateiangabe übersetzt `--en` alle Reports in `out\`, deren Name nicht mit `_` beginnt.

## 6. Prüfen

### 6.1 Die Prüfzeile

Sag der KI: „Prüfe den Report und sag mir, was ich in Allplan ansehen soll." Sie prüft die Datei mit dem Skill `allplan-report` und gibt dir die Prüfzeile im Wortlaut:

```
AMPEL: GRUEN | validate_rdlc | 1 Dateien, 0 Fehler, 0 Warnungen
```

- **GRUEN**: keine Befunde.
- **ORANGE**: nur Hinweise. Die KI erklärt jeden. Der Report ist nutzbar. Zwei Vorlagen melden mit Absicht je einen Hinweis: Wandbeläge „Tabelle breiter als Body“ (von drei Spaltenbreiten ist immer nur eine sichtbar) und Raum-Abwicklung „RepeatOnNewPage fehlt“ (die erste Zeile ist eine Überschrift, kein Spaltenkopf).
- **ROT**: Fehler. Die KI behebt sie, bevor sie dir die Datei gibt.

Das Prüfen am Rechner kennt Allplan nicht. Es findet Fehler im Aufbau der Datei, aber nicht, ob die Zahlen zu deinem Modell passen. Zu den Regeln gehört, dass sich Elemente nicht überlappen dürfen: Im Allplan-Report-Fenster würde sonst eines verschoben (Warnung W28). PDF und Vorschau zeigen das nicht. Zwei weitere Fenster-Regeln stehen im Skill, ohne Prüfregel: Ein ausgeblendetes Feld gehört in einen eigenen Behälter über die volle Breite, und kleine Schrift braucht 10 % Breitenreserve, weil das Fenster sie 3 bis 8 % breiter setzt als das PDF.

### 6.2 Die Liste für Allplan

Dazu bekommst du eine Liste dessen, was du in Allplan ansehen sollst, zum Beispiel:

- Stimmt die Zahl der Zeilen mit dem, was du im Modell siehst?
- Stimmen die Summen?
- Erscheinen Bilder und Umlaute richtig?
- Bei bedienbaren Reports: Stellschrauben, Aufklappen und Sortieren im Report-Fenster wurden selbst geprüft und wirken. Der Klick ins Modell (Zoom auf das Bauteil) ist **nicht gesichert**: In dem Fenster, das zum Testen geöffnet wurde, hatte er keine Wirkung, und über Allplans Befehl „Reports“ ist er nicht geprüft. Verlass dich nicht darauf.

Bis du zurückmeldest, was du gesehen hast, gilt der Report als **nicht in Allplan geprüft**.

## 7. In Allplan öffnen

1. Kopiere die Datei aus `out\` in den Büroordner von Allplan, in einen eigenen Ordner: `C:\allplandaten\2027\Std\Reports\deu\Meine Reports\`. Englische Reports gehören nach `...\Reports\eng\Meine Reports\`. Das ist der Standardpfad; bei einem anderen Datenpfad entsprechend.
2. In Allplan die Funktion **Reports** aufrufen und die Vorlage wählen.
3. Den Report auf das Projekt anwenden und prüfen (Liste aus 6.2).
4. Weicht etwas ab, schreibe der KI genau das, zum Beispiel „Im 1. OG fehlen zwei Stützen".

Die Vorlagen unter `C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports` gehören Allplan. Lege dort nichts ab und ändere nichts.

Bei großen Projekten dauert die Ausgabe Minuten. Warte ab, auch wenn Allplan zwischendurch „reagiert nicht" meldet. Im Report-Fenster braucht der Master 22 bis 24 Sekunden bis zur ersten Seite, weitere Seiten 5 bis 15 Sekunden.

## 8. Die fertigen Vorlagen ohne KI

Die Ordner `vorlagen\deu` und `vorlagen\eng` enthalten die fertigen Reports. Kopiere die Dateien eines Sprachordners wie in Abschnitt 7 in den Büroordner. Was die einzelnen Vorlagen brauchen, steht in `vorlagen\LIESMICH.md` und in der README.

Die sieben Vorlagen je Sprache (deutsch / englisch) und was jede braucht:

| Vorlage | Braucht |
|---|---|
| Report Master / Report Master | ein Teilbild mit den Bauteilen |
| Report Master Grundriss / … Floor plan | ein Teilbild mit Bauteilen und Räumen |
| Report Master Raum-Abwicklung / … Room elevations | Räume **und** ein Teilbild mit der Abwicklungs-Zeichnung, beide zusammen; ohne das Teilbild mit den Räumen bleiben die Raumkarten leer |
| Report Master Wandbeläge / … Wall finishes | Räume mit Raumausbau |
| Report Master Bewehrung / … Reinforcement | ein Teilbild mit Bewehrung |
| Report Master Planliste / … Layout list | ein Projekt mit Plänen (kein Teilbild) |
| Report Master Listen / … Lists | ein Teilbild mit den Bauteilen |

Beispiel-PDFs liegen in `beispiel\deu` und `beispiel\eng`. Die PDFs zu Planliste und Wandbeläge sind **Vorschau mit Beispieldaten, nicht aus Allplan**; in Allplan wurden beide an echten Projekten ausgegeben und angesehen. In `beispiel\deu` liegt außerdem `Uebersicht_Master.pdf` (in `beispiel\eng`: `Overview_Master.pdf`) mit allen zehn Master-Seiten auf einem Blatt.

## 9. Aktualisieren und entfernen

- **Neue Fassung des Skills:** den Ordner `allplan-report-design` im Skill-Ordner löschen und aus dem neuen Repo-Stand neu kopieren. Deine Reports in `reports\out\` bleiben unberührt. Die Werkstatt selbst bringst du mit dem Befehl `python <Skill-Ordner>\werkstatt_anlegen.py reports --aktualisieren` (`<Skill-Ordner>` ist `allplan-report-design` im Skill-Ordner deines Werkzeugs) auf den neuen Stand. Er ersetzt nur Dateien, die du nicht selbst verändert hast; veränderte Dateien bleiben, die neue Fassung liegt daneben als `.neu`.
- **Entfernen:** die Ordner `allplan-report-design` und `allplan-report` im Skill-Ordner löschen. Die Werkstatt ist ein normaler Ordner und kann einfach gelöscht werden.

## 10. Häufige Probleme

| Problem | Lösung |
|---|---|
| Die KI kennt den Skill nicht | Ordnernamen mit Abschnitt 2.3 vergleichen. Der Ordner muss `allplan-report-design` heißen und direkt die `SKILL.md` enthalten. VS Code neu laden oder eine neue Sitzung starten. In Copilot muss der **Agent-Modus** aktiv sein. |
| Explorer lässt den Ordner `.github` nicht anlegen | Als Namen `.github.` eingeben (Punkt am Ende) oder PowerShell nutzen (Abschnitt 2.5). |
| `python` wird nicht gefunden | Der KI sagen, sie soll das Python von Allplan verwenden: `C:\Program Files\Allplan\Allplan 2027\Prg\Python\python.exe`. |
| Die Vorschau lässt sich nicht erzeugen | Das Anzeigeprogramm braucht die Programmdateien von Allplan 2027. Ist Allplan an einem anderen Ort installiert, nennst du der KI den Ordner. |
| `werkstatt_anlegen.py` bricht ab | Der Zielordner ist nicht leer. Nimm einen neuen Ordner oder, für eine vorhandene Werkstatt, die Option `--aktualisieren`. |
| Ampel ist ROT | Die KI bitten, die Befunde zu beheben. |
| Report bleibt in Allplan leer | Die abgefragten Attribute sind im Modell nicht gefüllt, oder der Filter passt nicht zu den Bauteilen. Der KI beschreiben, welche Bauteile erscheinen sollten. Liefert die Abfrage keine einzige Zeile, entsteht in Allplan gar kein Report. |
| Report bleibt in Allplan weiß | Die Vorlage enthält etwas, das Allplan nicht versteht. Die KI bitten, die Datei mit dem Skill `allplan-report` zu prüfen. |
| Report bleibt im Report-Fenster leer | Ein Parameter hat eine ungültige Vorgabe. Allplan nimmt nur feste Vorgaben und feste Listen. Die KI bitten, die Parameter zu prüfen. |
| Text im Report-Fenster ist abgeschnitten oder Blöcke sind verrutscht | Elemente im Report überlappen sich, und das Fenster schiebt eines weg. PDF und Vorschau zeigen das nicht. Das Prüfskript meldet es als Warnung W28; die KI bitten, die Überlappung zu beheben. |
| Die Excel-Ausgabe einer Planliste öffnet das Fenster statt einer Datei | Pläne und Projektdaten lassen sich als Report nur als PDF oder Word ausgeben, nicht als Excel. Gib den Report als PDF oder Word aus. |
| Die Raum-Abwicklung zeigt nichts | Der Report zeichnet nicht selbst. Die Zeichnung muss im Teilbild liegen (siehe README, Abschnitt „Raum-Abwicklung“). |
| Umlaute erscheinen als „?" | Die Datei wurde nicht als UTF-8 gespeichert. Die KI bitten, sie als UTF-8 ohne BOM neu zu schreiben. |
