# Changelog

## 1.0.1 – 2026-11-20

Neues Hausdesign und Design-Abfrage. / New house design and design question.

- Alle Reports, Vorlagen und Beispiele im neuen Hausdesign: dunkles Marineblau trägt Titelband und Schrift, Türkis markiert nur (nie als Schrift auf Weiß, nie als Balken), eine Schrift in drei Gewichten. Materialfarben bleiben, weil sie Bedeutung tragen.
- Design: Farben und Schrift an einer Stelle (`master/design.py`). Hausdesign als Vorgabe (dunkles Marineblau, kräftiges Blau, Türkis als Akzent, Roboto), eigenes Design aus einer ausgefüllten `design_kunde.json` (vier Pflichtfarben und Schrift; alles Weitere rechnet der Bausatz, Kontraste werden geprüft). Der Skill fragt das Design vor dem ersten Report einmal ab; bis es festgelegt ist, bricht jedes Bauskript ab (Sperre). Die Schrift wählt der Report beim Öffnen: sind alle Familien des Designs installiert, gelten sie, sonst Segoe UI. Neue Testdateien: `test_design.py` (Befehle, Prüfregeln, Sperre, Schrift im Report) und `test_designregeln.py` (die Seiten benutzen nur Namen aus dem Design); `conftest.py` setzt für alle Tests das Hausdesign.
- Das Hausdesign wird nur mit der Antwort des Anwenders festgelegt (`design.py --haus --antwort "…"`); eine unlesbare oder ungültige `design.json` zählt als offen. Ein Kundendesign wird geprüft: Kontraste, sichtbare Bewertungsfarben, Schriftrollen.
- Die Vorschau läuft mit vollen Rechten wie in Allplan, damit sie dieselbe Schrift zeigt wie der Report in Allplan.
- Tests bauen nur noch in einen Zwischenordner und überschreiben keinen Report in `out/`.
- README im Hausdesign: Kopfbild, Abzeichen in den Hausfarben, im Abschnitt „Design“ die Farbtafel und derselbe Report in zwei Designs (Vorschau mit Beispieldaten, nicht aus Allplan).
- Behoben: Mit einem eigenen Design ließ der Sprachschalter die englische Fassung aus („Texte ohne Übersetzung“). Er lässt die Schriftnamen des Designs jetzt stehen und findet Texte mit eingebauter Farbe auch in anderen Farben.

## 1.0.0 – 2026-11-19

Erste Fassung. / First release.

- Skill `allplan-report-design`: Wissen zum Gestalten von Allplan-2027-Reports mit rund 100 gemessenen Techniken (Urteil „geht / geht mit Kniff / geht nicht“), Liste „Wunsch → Weg“ (60 Einträge), Nachschlagedateien zu Bewehrung, Projektlisten und Strichcode/QR/CSV, Bausatz, Werkzeuge.
- Skill `allplan-report`: Grundlagen für Abfragen, Attribute und die Prüfung von Reports (ohne die Allplan-Vorlagenbibliothek, sie wird aus der Allplan-Installation gelesen). Das Prüfskript hat 44 Regeln (16 Fehler E01–E16, 28 Warnungen W01–W28); 19 davon stammen aus Messungen in Allplan (E09–E16, W18–W28; W28 meldet überlappende Elemente). Zwei weitere Fenster-Regeln stehen im Skill, ohne Prüfregel: ein ausgeblendetes Feld gehört in einen eigenen Behälter über die volle Breite; kleine Schrift braucht 10 % Breitenreserve.
- Sieben Vorlagen je Sprache: Report Master (10 Seiten) und sechs Begleit-Reports (Grundriss, Raum-Abwicklung, Wandbeläge, Bewehrung, Planliste, Listen).
- 81 Bausteine mit fester Kennung (K, D, M, T, B, U, X): 50 im Master, 31 in den Begleit-Reports; Verzeichnis auf Seite 10 des Masters.
- Report aus Kennungen mit einem Befehl (`build_auswahl.py`) für die 50 Master-Bausteine; die Bausteine der Begleit-Reports werden mit ihrem Report gebaut.
- Bewehrung: Stahlmengen, Überlängen, Stab- und Mattenliste mit Biegeform. Planliste: was an den Plänen fehlt. Listen: Bauteillisten über viele Seiten, Etikettenblatt zum Ausschneiden (QR-Code mit Klartext, Strichcode; Bauteilart und Anzahl einstellbar) und Auswertung nach Wahl.
- Bausatz mit geprüften Funktionen für fließende Reports, Gruppen mit Umbruch und Zählung, Filter, mehrere Sortierungen, Zellen verbinden, Parameter-Arten, Links, Unterbericht und Variablen; 100 Tests. Die Unterscheidung von Groß- und Kleinschreibung wird beim Gruppieren festgelegt (behebt eine doppelte „+ n weitere“-Zeile, wenn dieselbe Raumnutzung als „Flur“ und „FLUR“ im Modell steht).
- Vorschauprogramm mit PDF-, Word- und Excel-Ausgabe, Parameterliste, mehreren Werten je Parameter und Unterberichten wie in Allplan; Zahlen für Stellschrauben gehen mit Punkt oder Komma.
- Deutsch und Englisch: Übersetzungstabellen (1186 Einträge in 19 Dateien), Zahlen und Datum en-US in der englischen Fassung.
- Fertige Vorlagen (`vorlagen\deu`, `vorlagen\eng`) und Beispiele als PDF (`beispiel\deu`, `beispiel\eng`); die PDFs zu Planliste und Wandbeläge sind Vorschauen mit Beispieldaten, nicht aus Allplan.
- Anleitung auf Deutsch und Englisch (`docs`).

Checked in Allplan 2027 / in Allplan 2027 geprüft: Bedienung im Report-Fenster (Stellschrauben, Aufklappen, Sortieren, Sprung in einen zweiten Report, Gliederungsleiste, fixierter Tabellenkopf, Unterbericht); PDF-Ausgabe aller sieben Vorlagen, deutsch und englisch; Fenster und PDF Seite für Seite verglichen (sitzt wie im PDF); der Master an einem echten Wohnhaus (10 Seiten, deutsch und englisch).

Not yet checked / noch nicht geprüft: Klick ins Modell (nicht gesichert); Tooltips, Hyperlinks, Export aus dem Fenster; Wandbeläge und Teile des englischen Masters im Report-Fenster; ein echtes englischsprachiges Projekt; Raum-Abwicklung für L-förmige Räume und schräge Wände im Modell; Bewehrung mit „Ausführungen“ größer 1; Einrichten in den KI-Werkzeugen an einem fremden Rechner.
