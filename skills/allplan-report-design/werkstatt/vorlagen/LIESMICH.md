# Report-Vorlagen für Allplan 2027

Sieben gestaltete Auswertungen mit Diagrammen, Kennzahlen, Tabellen und
Bauteilbildern aus deinem Modell, auf Deutsch (`deu`) und Englisch (`eng`).

## Die sieben Vorlagen

- **Report Master** – 10 Seiten Auswertung aus Wänden, Decken, Stützen,
  Unterzügen, Bodenplatte, Räumen sowie Fenster- und Tür-SmartParts.
- **Report Master Grundriss** – Geschossgrundriss und Raumkarten.
- **Report Master Raum-Abwicklung** – je Raum die Wandflächen und die
  gezeichnete Abwicklung.
- **Report Master Wandbeläge** – Putz, Anstrich, Leibung je Raum.
- **Report Master Bewehrung** – Stabliste, Mattenliste, Überlängen.
- **Report Master Planliste** – Pläne des Projekts: Überblick, Planliste.
- **Report Master Listen** – vollständige Bauteilliste je Art, Etiketten mit QR-Code zum Ausschneiden.

## Einrichten

1. Kopiere die Dateien eines Sprachordners in einen eigenen Ordner
   bei den Büro-Reports von Allplan 2027, zum Beispiel
   `C:\allplandaten\2027\Std\Reports\deu\Meine Reports\`
   (englisch: `...\Reports\eng\Meine Reports\`).
   *Annahme:* Standardpfad; wo deine Daten liegen, zeigen die Pfadeinstellungen.
2. Report-Dialog öffnen, Vorlage in deiner Kategorie auswählen.

## Was jede Vorlage braucht

- **Master, Grundriss, Wandbeläge, Bewehrung, Listen:** Teilbild; **Planliste:** Projekt.
- **Wandbeläge:** nur Räume, die einen Ausbau haben.
- **Raum-Abwicklung:** zusätzlich ein Teilbild mit der Abwicklungs-
  Zeichnung je Raum, jeweils mit einem Rahmen (dünne Decke, Material
  „Abwicklung“, Bezeichnung = Bauteil-ID des Raums). Der Report zeichnet
  nicht selbst, er zeigt nur, was im Teilbild liegt. Ohne solche
  Zeichnung bleibt der Abschnitt leer.

## Bedienung im Report-Fenster

Im Allplan-Fenster sind vorgesehen: Klick aufs Bauteil, Aufklappen,
Sortieren und die Stellschrauben links (Preise, Ziel Fensteranteil,
Mindestbreite Tür, Details zeigen). Im PDF wirkt das nicht.
Im Allplan-Fenster ausprobiert: Stellschrauben, Aufklappen und Sortieren
wirken. Der Klick aufs Bauteil (Zoom ins Modell) ist eingebaut, aber
nicht gesichert: im Testfenster blieb er ohne Wirkung.

## Englische Vorlagen

Die Texte sind englisch, Zahlen im Format en-US. Namen aus dem Modell
(Räume, Materialien) bleiben, wie sie im Projekt stehen. Materialgruppen
werden an deutschen und englischen Wörtern erkannt (concrete, masonry,
insulation, plasterboard, timber, steel, glass, stone).

## Kennungen

Jeder Baustein trägt eine Kennung (K010, D040 …), Verzeichnis auf Seite
10 des Masters. Damit lässt sich ein eigener Report bestellen.

## Grenzen

- Allplan füllt je Report nur das erste Datenpaket.
- Große Projekte brauchen Minuten (gemessen: 3.545 Bauteile, der Master mit
  10 Seiten 3 bis 7 Minuten; Allplan meldet solange „reagiert nicht“).
- Raum-Abwicklung: höchstens 8 Räume je Report; weitere nennt eine Zeile.
- Das Prüfskript meldet bei Wandbeläge und Raum-Abwicklung je einen Hinweis,
  mit Absicht (erklärt in der Anleitung, Abschnitt Prüfen).
