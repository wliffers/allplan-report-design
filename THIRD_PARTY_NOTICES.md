# Third-party notices / Hinweise zu Fremdem

*Deutsch und English*

## Allplan

Allplan ist eine Marke ihres Inhabers. Die Reportvorlagen in `vorlagen\` und die Beispiele in `beispiel\` sind eigene Arbeiten. Sie enthalten die Standard-Datenquelle und die Standardparameter, die jeder Allplan-Report tragen muss, damit Allplan ihn öffnet. Die Vorlagenbibliothek von Allplan 2027 (551 Vorlagen) und der Attributkatalog sind **nicht** Teil dieses Repos. Der Skill liest sie aus der Allplan-Installation. Die Fachtexte des Skills `allplan-report` zitieren kurze Ausschnitte daraus (einzelne Abfragen und XML-Zeilen), um die Schreibweise zu erklären; ganze Vorlagen sind nicht enthalten.

*Allplan is a trademark of its owner. The report templates in `vorlagen\` and the examples in `beispiel\` are our own work. They contain the standard data source and the standard parameters that every Allplan report must carry for Allplan to open it. The template library of Allplan 2027 (551 templates) and the attribute catalog are **not** part of this repo. The skill reads them from the Allplan installation. The reference texts of the skill `allplan-report` quote short excerpts from them (single queries and XML lines) to explain the notation; no complete templates are included.*

## Microsoft ReportViewer

Allplan zeigt Reports mit dem Microsoft ReportViewer. Er wird **nicht mitgeliefert**. Der Vorschau-Renderer des Skills nutzt die Programmdateien (DLLs) der Allplan-Installation und kopiert sie nur auf deinem Rechner in den Arbeitsordner.

*Allplan shows reports with the Microsoft ReportViewer. It is **not included**. The preview renderer of the skill uses the program files (DLLs) of the Allplan installation and copies them only on your computer, into the working folder.*

## Roboto

Das Hausdesign der Reports verwendet die Schrift Roboto (Lizenz: Apache License 2.0). Sie ist **nicht enthalten** und muss nicht installiert sein. Fehlt sie auf dem Rechner, der den Report öffnet, zeigt der Report Segoe UI. Wer sie nutzen will, installiert sie selbst.

*The house design of the reports uses the font Roboto (license: Apache License 2.0). It is **not included** and does not have to be installed. If it is missing on the computer that opens the report, the report shows Segoe UI. If you want to use it, you install it yourself.*

## Segoe UI

Segoe UI ist die Ersatzschrift der Reports, wenn die Schrift des Designs fehlt. Sie ist eine Windows-Systemschrift und **nicht enthalten**.

*Segoe UI is the fallback font of the reports when the font of the design is missing. It is a Windows system font and is **not included**.*

## Python-Pakete / Python packages

Pillow und PyMuPDF werden optional für die Vorschau der Abwicklungs-Zeichnung und für PDF-Bilder verwendet. Sie sind **nicht enthalten**; sie haben eigene Lizenzen und werden von dir selbst installiert.

*Pillow and PyMuPDF are optionally used for the preview of the elevation drawing and for PDF images. They are **not included**; they have their own licenses and you install them yourself.*
