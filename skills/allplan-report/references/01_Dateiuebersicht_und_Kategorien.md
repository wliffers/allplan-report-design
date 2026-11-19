# Dateiübersicht und Kategorien

Die Vorlagen sind die Allplan‑2027‑Bibliothek `<RDLC>` (`C:\ProgramData\Nemetschek\Allplan\2027\Etc\Reports`, nur lesen) (551 Dateien). Die Einzeltabellen unten stammen aus dem älteren flachen Bestand (520 Dateien) und nennen nur Dateinamen; den Ordner einer Datei liefert `RelativePath` in `<SKILL>/rdlc-index.json`.

## 0. Allplan 2027: Ordnerstruktur und Abweichungen zum Altbestand

- **Baum statt flach:** `deu/<Kategorie>/…` (292 Dateien, 31 Kategorien), `eng/<Category>/…` (251), `Template_*.rdlc` (8) an der Wurzel. Kategorien mit Unterordnern, z. B. `deu/Räume, Flächen, Geschosse/DIN 277/`. Im Index: Felder `Language`, `Category`, `SubCategory`.
- **Deutsche Kategorien 2027:** Allplan BCM, Ausbau, Bewehrung, Deckensystem, Einbauteile, Facility Management, Fassade, Fertigteile, Geländer, Gewerke, Grundbau, Intelligente Verlegungen, Kanalisation/Leitungsbau, LCA, Lageplan, Landschaftsplanung, Leitungskataster, NEVARIS, Objekte, Positionsplan, Rohbau, Räume/Flächen/Geschosse, Schalung, Skelettbau, SmartParts, Städtebau, Tragwerksobjekte, Treppe, Umbauplanung, Verwaltung, Wärmeschutz.
- **Neu gegenüber dem Altbestand** (u. a.): Fertigteil‑Reihe `001`–`006` und `050_Stapelliste` (DE/EN), `BillOfMaterial Articles`, `Baugrube Bediener Übersicht`, `Layout list with documents (PL-TB/TB-PL)`, `Custom-components`, `Slab Foundations`.
- **Nicht mehr ausgeliefert:** 13 Dateien, u. a. die englischen DIN‑277‑Reports (`Net floor area…`, `Net room areas…`, `Gross …`).
- **Inhaltlich geändert:** rund 100 gleichnamige Dateien unterscheiden sich vom Altbestand (z. B. alle `Gewerke/Betonarbeiten/*` mit neuen Topologie‑Attributen `@521@ @522@ @524@ @528@`). Bei Abweichung gilt die 2027‑Datei.

## 1. Wichtigste Grundfakten

- **Sprachen**: Jede fachliche Vorlage existiert doppelt – einmal mit deutschem Dateinamen (`Wände.rdlc`) und einmal mit englischem (`Walls.rdlc`). Inhaltlich praktisch identisch, nur Überschriften und Labels unterschiedlich.
- **Schema‑Versionen**: Drei RDL‑Generationen, erkennbar am Namespace des Wurzelelements (nicht am Dateinamen – das Suffix `_2005` tragen nur die vier `Template_*_2005.rdlc`):
  - `…/reporting/2005/01/reportdefinition` → RDL 2005, `<Table>`/`<Matrix>`, Seitenmaße direkt unter `<Report>` (493 Dateien in 2027, der Normalfall).
  - `…/reporting/2010/01/reportdefinition` → RDL 2010, `<Tablix>`, `<ReportSections>` (10 Kanal‑Reports).
  - `…/reporting/2016/01/reportdefinition` → RDL 2016, `<Tablix>`, `<ReportSections>`, `<Page>` (48 Dateien).
- **Nummerierte Reports** (z. B. `002 General`, `031 List of starter bars`, `040 FF reinforcement cages`, `047 Bars + stirrups`, `060 MWS reinforcement group`, `062 FF reinforcement cages with fixtures`) gehören zu den **Fertigteil‑Produktions‑Reports** und sind deutsch/englisch gedoppelt (`040_FF-Bewehrungskörbe - A4.rdlc` ↔ `040  FF reinforcement cages - A4.rdlc`).
- **DataProvider**: Immer `ALLPLAN` (keine echte SQL‑Datenbank). Die Query‑Syntax ist Allplan‑spezifisch.
- **Autor**: Meist `Allplan GmbH`. Einige Schweizer Reports: `Allplan Schweiz AG`.

## 2. Template‑Dateien (Ausgangspunkt für neue Reports)

| Template | Inhalt | Einsatz |
|----------|--------|---------|
| `Template_empty_2005.rdlc` | Minimal‑Report, leerer Body, Standard‑Header/Footer | Neue Vorlagen ohne Tabellenstruktur |
| `Template_empty.rdlc` | Dasselbe, aber RDL 2016 | Nur wenn Tablix‑Features zwingend sind |
| `Template_Grouping0_2005.rdlc` | Tabelle ohne Gruppierung + Bild‑Spalte | Einfache Liste mit Vorschaubild |
| `Template_Grouping1_2005.rdlc` | Ein Gruppierungs‑Level | Gliederung z. B. nach Geschoss |
| `Template_Grouping2_2005.rdlc` | Zwei Gruppierungs‑Level (ohne Bild) | Gliederung Geschoss → Material etc. |
| `Template_Grouping0/1/2.rdlc` | 2016‑Varianten | Dito, Tablix‑basiert |

## 3. Thematische Hauptkategorien

### 3.1 Bewehrung (Reinforcement)

Stab-, Matten- und Biegeformlisten nach verschiedenen Ländernormen.

| Vorlage | Standard / Zweck |
|---------|------------------|
| `Stabliste Biegeformen.rdlc` | Deutsche Biegeform‑Liste (DIN, ISO 3766) |
| `Stabliste ISO 3766.rdlc` | ISO 3766 |
| `Stabliste British Standard.rdlc`, `Stabliste BS8666 2020.rdlc` | BS / BS8666:2020 |
| `Stabliste SANS 282.rdlc` | Südafrika |
| `Stabliste Schweiz.rdlc` | Schweiz (mit Zusatzkopf) |
| `Stabliste Benennung.rdlc` | Benennungs‑Form (nur Kurzbeschreibung) |
| `Stabliste Biegeformen, Zusammenfassung.rdlc` | Biegeform‑Summary |
| `Mattenstahlliste.rdlc`, `Mesh reinforcement.rdlc` | Mattenliste |
| `MattenQuerschnitte.rdlc`, `Mesh cross-sections.rdlc` | Matten‑Querschnitte |
| `Mattenschneideskizze.rdlc`, `Mattenschneideskizze Schweiz.rdlc`, `Mesh cutting diagram.rdlc` | Ganzseitige Schneideskizze |
| `Listenmattenübersicht.rdlc`, `Custom mesh overview.rdlc` | Listenmatten |
| `SubEinzelmatte.rdlc`, `SubordinateMesh.rdlc` | Einzelmatten |
| `Übersicht Bewehrung.rdlc`, `Reinforcement - overview.rdlc` | Aggregierte Bewehrung |
| `Metrische Stahlstückliste.rdlc`, `Metric steel BOM.rdlc`, `Imperiale Stahlstückliste.rdlc`, `Imperial-Steel-BOM.rdlc` | Stahlbau BOM |
| `StahlQuerschnitte.rdlc`, `Steel cross-sections.rdlc` | Stahl‑Profile |
| `Verbindungsplan-metrisch.rdlc`, `Verbindungsplan-imperial.rdlc`, `ConnectionSchedule-Metric.rdlc`, `ConnectionSchedule-Imperial.rdlc` | Stahlbau Verbindungen |

### 3.2 Bewehrungs‑ und Fertigteil‑Körbe (nummeriert)

| Vorlage | Inhalt |
|---------|--------|
| `031 List of starter bars.rdlc` / `031_Stückliste_AnsBew.rdlc` | Anschlussbewehrung (AB) |
| `032 List of starter bars, shape.rdlc` / `032_Stückliste_AnsBew_Form.rdlc` | AB mit Biegeform |
| `033 List of starter bars, details.rdlc` / `033_Stückliste_AnsBew_Detail.rdlc` | AB detailliert |
| `040 FF reinforcement cages - A4.rdlc` / `040_FF-Bewehrungskörbe - A4.rdlc` | FF‑Bewehrungskörbe A4 |
| `041 FF reinforcement cages - A3.rdlc` / `041_FF-Bewehrungskörbe - A3.rdlc` | FF‑Bewehrungskörbe A3 |
| `045 Stirrup cages (from stock).rdlc` / `045_Bauseitige_BK_(Lagerware).rdlc` | Bauseitige Bügelkörbe Lager |
| `046 Stirrup cages (special reinforcement).rdlc` / `046_Bauseitige_BK_(Spezialbewehrung).rdlc` | Bauseitige Bügelkörbe Spezial |
| `047 Bars + stirrups.rdlc` / `047_Stabstahl+Bügel_bauseitig.rdlc` | Bauseitig Stäbe + Bügel |
| `060/061 MWS reinforcement group` / `_MSA_Bewehrungsgruppe` | MSA‑Bewehrungsgruppe A4/A3 |
| `062/063 FF reinforcement cages with fixtures` / `_FF-BewehrungskörbeMitEbt` | FF‑Körbe **mit** Einbauteilen |

### 3.3 Räume, Flächen, Gebäude

| Vorlage (DE) | EN‑Äquivalent | Zweck |
|--------------|---------------|-------|
| `Raumbuch.rdlc` | – (nur DE) | Vollständiges Raumbuch |
| `Raumgeometrie.rdlc` | `Room geometry.rdlc` | Raum mit Abmessungen |
| `Raumgruppen.rdlc` | `Room groups.rdlc` | Apartments / Raumgruppen |
| `Raumvolumen mit Ansatz.rdlc` | `Room volume incl. calculation.rdlc` | Nettovolumen mit Rechenweg |
| `Wohnflächen.rdlc` | `Living space.rdlc` | WoFlV |
| `Wohnflächen (Rundung einstellbar).rdlc` | `Living space (rounding adjustable).rdlc` | WoFlV mit Parameter |
| `Netto-Grundflächen.rdlc` | `Net floor area.rdlc` | NGF |
| `Netto-Raumflächen.rdlc` | `Net room areas.rdlc` | NRF |
| `Brutto-Grundflächen Abmessungen.rdlc` | `Gross floor area, dimensions.rdlc` | BGF |
| `Brutto-Rauminhalte Abmessungen.rdlc` | `Gross cubic content, dimensions.rdlc` | BRI |
| `Grundfläche Geschossfläche mit GRZ GFZ.rdlc` | `Base area, floor area and ratio, site occupancy index.rdlc` | GRZ/GFZ |
| `Baumasse mit Baumassenzahl.rdlc` | `Building volume and ratio.rdlc` | BMZ |
| `BMZ - Grundstück.rdlc`, `BMZ - PlanzV.rdlc` | – | BauNVO‑Auswertungen |
| `Ausbau Bodenflächen/Deckenflächen/Seitenflächen.rdlc` | `Finish floors/ceilings/vertical surfaces.rdlc` | Ausbauflächen |
| `Ausbauflächen Material.rdlc`, `Ausbauflächen Übersicht.rdlc` | `Finishing surfaces, material/overview.rdlc` | Ausbau‑Mengen |
| `Flächenübersicht (Kennwerte).rdlc` | `Area overview (characteristics).rdlc` | Kennwert‑Matrix |
| `Übersicht Netto-Grundflächen.rdlc` | `Net floor areas - overview.rdlc` | NGF‑Aggregat |
| `Übersicht Gebäude.rdlc` | `Buildings - overview.rdlc` | Gebäude‑Übersicht |
| `Übersicht Raumgruppen.rdlc` | `Room groups - overview.rdlc` | Raumgruppen‑Übersicht |
| `FM-Raum Grundfläche.rdlc`, `FM-Räume und Nutzungsart.rdlc`, `FM-Räume und Kostenstellen.rdlc` | `FM room - base area.rdlc` etc. | Facility Management |
| `Exposé Raumgruppen.rdlc` | `Concept, room groups.rdlc` | Exposé |

### 3.4 Bauteile (Architektur)

| Vorlage | Bauteil |
|---------|---------|
| `Wände.rdlc` / `Walls.rdlc`, `Wände nach Abrechnungsart.rdlc` / `Walls by calculation mode.rdlc` | Wand |
| `Decken.rdlc` / `Slabs.rdlc`, `Deckenbuch.rdlc`, `Deckensystem.rdlc` / `Ceiling System.rdlc` | Decke |
| `Stützen.rdlc` / `Columns.rdlc` | Stütze |
| `Unterzüge.rdlc` / `Downstand beams.rdlc` | Unter-/Überzug |
| `Stürze.rdlc` / `Lintels, headers.rdlc` | Stürze |
| `Fundamente.rdlc`, `Fundamente Übersicht.rdlc` / `Foundation(.overview).rdlc` | Fundament |
| `Schornstein.rdlc` / `Chimney.rdlc` | Schornstein |
| `Treppe.rdlc` / `Stair.rdlc`, `Treppe - komplette auswertung.rdlc` / `Stair - full analyses.rdlc` | Treppe |
| `Fenster*.rdlc` / `Windows*.rdlc` (mehrere Detailstufen inkl. Preise) | Fenster |
| `Türen*.rdlc` / `Doors*.rdlc` (mehrere Detailstufen, Qualitäten, Übergaben) | Tür |
| `Öffnungen.rdlc` / `Openings.rdlc`, `Türöffnungen.rdlc` / `Door openings.rdlc`, `Fensteröffnungen.rdlc` / `Window openings.rdlc` | Öffnungen |
| `Fensterbänke.rdlc` / `Window sills.rdlc`, `Rollladen.rdlc` / `Roller shutters.rdlc`, `Rolladenkasten.rdlc`, `Sonnenschutz.rdlc` / `Shading.rdlc`, `Lichtband.rdlc` / `Row of lights.rdlc`, `Lichtkuppeln.rdlc` / `Skylights.rdlc`, `Dachflächenfenster.rdlc` / `Domed roof-lights.rdlc` | Sonderbauteile |
| `Dachhaut.rdlc` / `Roof covering.rdlc`, `Dachobjekte.rdlc` / `Roof objects.rdlc` | Dach |
| `Ausstattung.rdlc` / `Equipment.rdlc`, `Sanitär.rdlc` / `Sanitary facilities.rdlc`, `Einbauteile.rdlc` / `Fixtures.rdlc`, `Ausstattungen der FM-Räume.rdlc` / `FM rooms - equipment.rdlc` | Ausstattung |
| `Geländer Übersicht.rdlc` / `Railing - overview.rdlc`, `Fassade*.rdlc` / `Facade*.rdlc`, `Wärmedämm - Verbundsysteme.rdlc` / `Exterior insulation finish system.rdlc` | Fassade/Geländer |
| `User-defined archit. elements.rdlc` | Architekt. Eigen‑Bauteile |
| `SmartParts Übersicht.rdlc` / `SmartParts - overview.rdlc`, `SmartParts Einzeldarstellung.rdlc` / `SmartParts - individual representation.rdlc`, `Smart symbols.rdlc` / `Makros.rdlc` | SmartParts/Makros |

### 3.5 Abbruch ↔ Neubau (Spiegelpaare)

Immer **identischer** Aufbau; einziger Unterschied: Filter `@49@.eq.0` (Neubau) vs `@49@.eq.2` (Abbruch).

| Paar |
|------|
| `Abbruch Wände.rdlc` / `Demolition - walls.rdlc` ↔ `Neubau Wände.rdlc` / `New building - walls.rdlc` |
| `Abbruch Decke.rdlc` ↔ `Neubau Decke.rdlc` |
| `Abbruch Fenster.rdlc` ↔ `Neubau Fenster.rdlc` |
| `Abbruch Türen.rdlc` ↔ `Neubau Türen.rdlc` |
| `Abbruch Fundamente.rdlc` ↔ `Neubau Fundamente.rdlc` |
| `Abbruch Stütze.rdlc` ↔ `Neubau Stütze.rdlc` |
| `Abbruch Schornstein.rdlc` ↔ `Neubau Schornstein.rdlc` |
| `Abbruch Dachhaut.rdlc` ↔ `Neubau Dachhaut.rdlc` |
| `Abbruch Unter- Überzüge.rdlc` ↔ `Neubau Unter- Überzüge.rdlc` |
| `Abbruch Elektro Heizung Sanitär.rdlc` ↔ `Neubau Elektro Heizung Sanitär.rdlc` |
| `Abbruch Fenstermakros Türmakros.rdlc` ↔ `Neubau Fenstermakros Türmakros.rdlc` |
| `Abbruch Abbruchkörper.rdlc` ↔ `Neubau Neubaukörper.rdlc` |
| `Abbruch Wände Größer 2,5.rdlc` ↔ `Neubau Wände Größer 2,5.rdlc` |
| `Building alteration - rooms.rdlc` / `Umbau Räume.rdlc` | Umbau‑Räume |

### 3.6 Schalung & Ortbeton

| Vorlage | Zweck |
|---------|-------|
| `Schalung Wände, Stützen, Wandpfeiler.rdlc` / `Formwork - walls, columns, flush piers.rdlc` | Schalung Vertikalbauteile |
| `Schalung Decken (Untersicht).rdlc` / `Formwork - slabs (soffit).rdlc` | Deckenschalung |
| `Schalung Unterzüge.rdlc` / `Formwork - downstand, upstand beams.rdlc` | Unterzug‑Schalung |
| `Schalung Öffnungen (Decken).rdlc` / `Formwork - openings (slabs).rdlc` | Deckenöffnungen |
| `Schalung Öffnungen (Wände).rdlc` / `Formwork - openings (walls).rdlc` | Wandöffnungen |
| `Randschalung Decken.rdlc` / `Edge formwork - slabs.rdlc` | Randschalung Decke |
| `Randschalung Fundamente.rdlc` / `Edge formwork - foundations.rdlc` | Randschalung Fundament |
| `Formbau_Schalungselemente.rdlc` / `Formwork - formwork elements.rdlc` | Formbau‑Schalelemente |
| `Formbau_Schalungselemente_Bemasst.rdlc` / `Formwork - formwork elements, with dimensions.rdlc` | Dito, bemasst |
| `Formbau_Elementliste.rdlc` / `Formwork elements list.rdlc` | Elementliste |
| `Formbau_Elementauszug_A4.rdlc` / `Formwork - elements - A4.rdlc` und `_bemasst` Variante | Elementauszug |
| `Stückliste Schalungselemente.rdlc` | Stückliste Schalung |
| `Betonarbeiten.rdlc` / `Concreting work.rdlc`, `Betonarbeiten - Ortbeton.rdlc` / `Concreting work - in-situ concrete.rdlc` | Betonmenge |

### 3.7 Gewerke / Bauleistungen

| Vorlage | Gewerk |
|---------|--------|
| `Mauerarbeiten.rdlc` / `Masonry work.rdlc` | Mauerwerk |
| `Putz- und Stuckarbeiten.rdlc` + `(detailliert)` / `Plaster and stucco work(.details).rdlc` | Putz |
| `Maler- und Lackierarbeiten.rdlc` / `Painting work.rdlc` | Maler |
| `Fliesen- und Plattenarbeiten.rdlc` / `Tiling work.rdlc` | Fliesen |
| `Bodenbelagsarbeiten.rdlc` / `Floor covering work.rdlc` | Bodenbelag |
| `Estricharbeiten.rdlc` / `Screeding work.rdlc` | Estrich |
| `Trockenbauarbeiten.rdlc` + `(Montagewände)` + `(Ausbauflächen)` / `Dry construction work*.rdlc` | Trockenbau |
| `Übersicht Gewerke.rdlc` / `Trades - overview.rdlc` | Gewerke‑Übersicht |
| `Baukosten.rdlc` / `Building cost.rdlc` | Kosten |

### 3.8 Mengenauswertung / 3D

| Vorlage | Zweck |
|---------|-------|
| `Mengen.rdlc`, `Mengen (Grafik).rdlc`, `Mengen (SVG Map).rdlc` | Mengen normal / mit Bild / mit SVG |
| `Mengenübersicht.rdlc`, `Quantities - overview.rdlc` | Mengen aggregiert |
| `Mengenliste Ö-Norm.rdlc`, `Quantities - Austrian standard.rdlc` | ÖNORM |
| `Mengenkörper.rdlc` | Volumen 3D‑Körper |
| `Mengen IBD.rdlc` | IBD‑Mengen |
| `Auswertung 3D Körper und Flächen.rdlc` | 3D‑Körper Multi‑Select |
| `Ergebnisliste.rdlc`, `Result list.rdlc` | Ergebnis |

### 3.9 Kanal / Leitungen / Tiefbau

| Vorlage | Inhalt |
|---------|--------|
| `Kanalisation Übersicht.rdlc` / `Overview sewer system.rdlc`, `Kanalisation Übersicht_Grafik.rdlc` | Kanal Gesamtübersicht |
| `Kanal Schächte.rdlc` / `Drain Shafts.rdlc` | Schächte |
| `Kanal Rohre.rdlc` / `Drain Pipes.rdlc` | Rohre |
| `Kanal Formteile.rdlc` / `Drain Mouldings.rdlc` | Formteile |
| `Kanal Schachtkoordinaten.rdlc`, `Kanal Schachtkoordinaten Excel.rdlc` / `Drain Shaft Coordinates(.Excel).rdlc` | Koordinaten (+Excel‑Export) |
| `Schacht Detailliste.rdlc`, `Schachtliste Geo405.rdlc`, `Schachtschäden.rdlc`, `Kanalschäden.rdlc`, `Kanalliste.rdlc`, `Kanalliste Geo405.rdlc`, `Haltung.rdlc` | Kanal‑Sonderlisten |
| `Leitungen.rdlc`, `Leitungen Geo405.rdlc`, `Leitungspunkte.rdlc`, `Leitungspunkte Geo405.rdlc`, `Leitungspunktliste Geo405.rdlc` | Leitungen |
| `Kanal eBKP-T.rdlc` / `Drain eBKP-T.rdlc` | Schweiz eBKP‑T |
| `Anlagen.rdlc`, `Anlagen Geo405.rdlc`, `Einbauten Geo 405.rdlc` | Geo‑Anlagen |
| `Abwasserknoten.rdlc`, `Einzugsgebiet.rdlc`, `Spezial Bauwerk Geo 405.rdlc` | Geo |
| `Baugrube Übersicht.rdlc` / `Excavation Pit Overview.rdlc`, `Erdbau Auftrag Abtrag.rdlc` / `Eearthwork Cut Fill.rdlc` | Baugrube / Erdbau |
| `Bohrpfahlwand.rdlc` / `Bored pile wall.rdlc`, `Spundwand.rdlc` / `Sheet pile wall.rdlc`, `Trägerbohlwand.rdlc` / `Soldier pile wall.rdlc`, `Bodenanker.rdlc` / `Ground anchor.rdlc` | Spezialtiefbau (PythonParts) |

### 3.10 Einbauteile / Hersteller‑Stücklisten

| Vorlage | Hersteller |
|---------|-----------|
| `Stückliste Leviat.rdlc` / `Bill of material Leviat.rdlc` | Leviat / HALFEN / DEHA |
| `Stückliste Leviat Deutschland.rdlc` | Leviat DE |
| `Stückliste PEIKKO - Einbauteile.rdlc` / `List of PEIKKO fixtures.rdlc` | PEIKKO |
| `Stückliste PHILIPP - Einbauteile.rdlc` / `List of PHILIPP fixtures.rdlc` | PHILIPP |
| `Stückliste Schöck - Einbauteile.rdlc` / `Parts list of Schöck fixtures.rdlc`, `CH - Bestell-Liste Schöck Einbauteile.rdlc` | Schöck |
| `Stückliste Einbauteile.rdlc` / `List of fixtures.rdlc`, `Stückliste Einbauteile (detailliert).rdlc` / `List of fixtures (details).rdlc` | Generisch |
| `Muffen, Muttern, Gewinde.rdlc` / `Couplers, nuts, threads.rdlc` | Bewehrungszubehör |
| `Bodenanker.rdlc` | Verankerungen |

### 3.11 Projekt / Layout / Metadaten

| Vorlage | Inhalt |
|---------|--------|
| `Projektattribute.rdlc` / `Project attributes.rdlc` | Projektattribute |
| `Projektdetails.rdlc` / `Project details.rdlc` | Dokumentenliste |
| `Projektübersicht.rdlc` / `Project overview.rdlc` | Projekt‑Metadaten |
| `Bauwerksstruktur.rdlc` / `Building structure.rdlc` | BWS (Bauwerkstruktur) |
| `Planliste mit Dokumenten.rdlc` / `Layout list with documents.rdlc` | Planliste |
| `Planübersicht mit Planstruktur.rdlc` / `Layout overview with layout structure.rdlc` | Planübersicht |
| `Filesets.rdlc` | Teilbildsätze |
| `Zeichnungen.rdlc` | Zeichnungen |
| `Koordinatenliste.rdlc` / `Coordinate list.rdlc` | DGM‑Punkte |
| `Querschnittsreihen.rdlc` / `Cross-section catalogs.rdlc` | Querschnittskatalog |
| `Prismenliste.rdlc` / `Prism list.rdlc` | Prismen |
| `Allgemeine Objektattribute.rdlc` / `General object attributes.rdlc` | Alle Objekte, frei |
| `002 General.rdlc` / `002_Allgemein.rdlc` | „Allgemeiner" Standard‑Bauteilreport |
| `Key plan.rdlc` / `Positionsplan.rdlc` | Positionsplan |
| `Symbols.rdlc` / `Symbole.rdlc` | Symbole |

### 3.12 Außenanlagen / Grundstück / Städtebau

| Vorlage | Inhalt |
|---------|--------|
| `Außenanlagen.rdlc` / `Outdoor facilities.rdlc` | Außenanlagen |
| `Pflanzen.rdlc`, `Pflanzen (Allplan BCM).rdlc` / `Plants*.rdlc` | Pflanzen |
| `Baumbestandsplan.rdlc` / `Tree plan.rdlc` | Baumbestand |
| `Wegeflächen nach Abrechnungsart.rdlc` / `Paths by calculation mode.rdlc`, `Wegeflächen Schichtaufbauten.rdlc` / `Paths by layer structure.rdlc` | Wegeflächen |
| `Straßendetails` → `Road details.rdlc` | Straße |
| `BMZ Übersicht Vergleich.rdlc`, `BMZ - Grundstück.rdlc`, `BMZ - PlanzV.rdlc` | BMZ Nachweise |
| `GFZ-GRZ - Grundstück.rdlc`, `GFZ-GRZ - PlanzV.rdlc`, `FAR-SOI - plot.rdlc` / `FAR-SOI - drawing symbol regulations.rdlc` | GFZ/GRZ, FAR/SOI |
| `SAR - drawing symbol regulations.rdlc`, `SAR - overview of comparison.rdlc`, `SAR - plot.rdlc` | SAR |
| `PlanzV - Flächen.rdlc`, `Drawing symbol regulations - areas.rdlc` | PlanzV |
| `Bauzonen.rdlc` | Bauzonen |
| `Anteilige Fensterflächen.rdlc` / `Proportionate window area.rdlc`, `Anteilige Glasflächen.rdlc` / `Proportionate glazing area.rdlc` | Anteile |
| `Übersicht Hüllflächen.rdlc` / `Envelope surfaces - overview.rdlc`, `Übersicht Hüllflächen Abmessungen.rdlc` / `Dimensions of envelope surfaces - overview.rdlc` | Hüllflächen |

### 3.13 Sonstiges

| Vorlage | Inhalt |
|---------|--------|
| `Kranbahn.rdlc` / `Crane runway.rdlc` | Kranbahn |
| `OneClick LCA.rdlc` | Ökobilanz‑Export |
| `Reparatur.rdlc` | Reparatur |
| `Objects - overview.rdlc` / `Übersicht Objekte.rdlc`, `Objects grouped - overview.rdlc` / `Übersicht Objekte gruppiert.rdlc` | Objekt‑Übersichten |
| `Sparrenkonstruktion - Ansichten.rdlc`, `Sparrenkonstruktion - Querschnitte.rdlc` / `Rafter design - views/cross-sections.rdlc` | Dachstuhl |
| `Verlegung - Einzelteile.rdlc` / `Placement - elements.rdlc`, `Verlegung - Gestaltung.rdlc` / `Placement - arrangement.rdlc` | Verlegung Flächen |

## 4. Nicht lesbar / unklar

Alle 520 Dateien sind gültige XML‑RDLC. Keine beschädigten Dateien gefunden. Alle Autoren eingetragen. Einige Reports haben eine leicht fehlerhafte Filter‑Syntax im CommandText (überzählige Klammern, siehe z. B. `Kanalisation Übersicht.rdlc`), dies ist jedoch durch Allplan tolerantes Parsing offenbar akzeptiert – nicht „automatisch" korrigieren, nur analog übernehmen.

## 5. Paar‑Logik (DE ↔ EN)

Wenn eine KI einen der beiden Dateinamen findet, existiert fast immer ein Sprach‑Gegenstück mit identischer Struktur. Strukturänderungen müssen **in beiden Dateien** nachgezogen werden. Maßgebend ist die inhaltlich jüngere Datei (neueres `ModificationDate`).
