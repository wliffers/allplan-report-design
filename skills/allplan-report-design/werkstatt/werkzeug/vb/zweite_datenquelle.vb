' ============================================================================================================
' zweite_datenquelle.vb - CSV-Datei im <Code>-Block lesen und je Zeile per Schluessel nachschlagen
' Beleg in Allplan 2027 (PDF-Ausgabe): p_code (CSV mit 51 Zeilen gelesen, Treffer ueber Bauteil-ID und ueber Zeilennummer,
' Spalten Preis und Notiz kamen in der Tabelle an)
'
' EINBAU
'   1. Text in den <Code>-Block setzen (XML-maskieren; der Bausatz tut das selbst). Kein CodeModule noetig.
'   2. Parameter fuer den Pfad (String, feste Vorgabe, ABSOLUTER Pfad - das Arbeitsverzeichnis ist der Allplan-Programmordner
'      C:\Program Files\Allplan\Allplan 2027, ein Pfad "neben dem Report" wird nicht gefunden):
'        <ReportParameter Name="Zusatz_Datei"><DataType>String</DataType><DefaultValue><Values><Value>C:\Daten\zusatz.csv</Value></Values></DefaultValue><Prompt>CSV-Datei</Prompt></ReportParameter>
'   3. In einer Tabellenzelle:
'        =Code.CsvWert(Parameters!Zusatz_Datei.Value, Fields!Nr.Value, 2)          Spalte 2 (0-basiert) zur Bauteil-ID @10@
'        =Code.CsvWert(Parameters!Zusatz_Datei.Value, "Z" & RowNumber(Nothing), 2)  Spalte 2 zur Zeilennummer
'        =Code.CsvAnzahl(Parameters!Zusatz_Datei.Value)                             Kontrollzeile: "51 Datenzeilen gelesen" oder "FEHLER ..."
'      Zahlen kommen als Text (mit Komma, wie in der Datei): im Report CDbl(...) und Format(x, "N2") (Kultur de-DE).
'
' DATEIFORMAT (gemessen): UTF-8 mit oder ohne BOM, Trennzeichen Semikolon, erste Zeile Kopf (wird uebersprungen), mindestens vier
' Spalten; Schluessel Spalte 1 (Bauteil-ID) und Spalte 0 mit Praefix Z (Zeilennummer). Andere Spalten als Schluessel: Zeile
' "csvZeilen(t(1)) = t" in CsvLaden aendern.
'
' GRENZEN
'   Gelesen wird einmal je Reportlauf und der Pfad des ERSTEN Aufrufs gilt fuer alle (Zwischenspeicher). Fehlt die Datei oder
'   ist sie gesperrt, steht in jeder Zelle "FEHLER <Ausnahme>: <Text>" statt eines Werts; fehlt der Schluessel, "(kein Treffer)".
'   Allplan gibt dem Code Vollzugriff auf Dateien; das ist kein Sicherheitsmerkmal des Reports: eine CSV-Datei auf dem
'   Rechner des Anwenders ist Teil des Reports und muss bei der Weitergabe mitgehen. Kopflos (eingeschraenkte Rechte des Renderers) ist der
'   Zugriff gesperrt: dort den Renderer mit Vollzugriff starten (Option --fulltrust).
' ============================================================================================================

' Zweite Datenquelle: CSV (Zeile;Nr;Preis;Notiz), einmal gelesen und im Hashtable gehalten (Schluessel Nr bzw. Zeilennummer)
Private csvZeilen As System.Collections.Hashtable = Nothing
Private csvFehler As String = ""

Private Sub CsvLaden(ByVal pfad As String)
    If Not csvZeilen Is Nothing Then Return
    csvZeilen = New System.Collections.Hashtable()
    Try
        Dim zeilen() As String = System.IO.File.ReadAllLines(pfad, System.Text.Encoding.UTF8)
        Dim i As Integer
        For i = 1 To zeilen.Length - 1
            Dim t() As String = zeilen(i).Split(";"c)
            If t.Length >= 4 Then
                csvZeilen(t(1)) = t
                csvZeilen("Z" & t(0)) = t
            End If
        Next
    Catch ex As System.Exception
        csvFehler = ex.GetType().Name & ": " & ex.Message
    End Try
End Sub

Public Function CsvWert(ByVal pfad As String, ByVal schluessel As String, ByVal spalte As Integer) As String
    CsvLaden(pfad)
    If csvFehler <> "" Then Return "FEHLER " & csvFehler
    If Not csvZeilen.ContainsKey(schluessel) Then Return "(kein Treffer)"
    Return CType(csvZeilen(schluessel), String())(spalte)
End Function

Public Function CsvAnzahl(ByVal pfad As String) As String
    CsvLaden(pfad)
    If csvFehler <> "" Then Return "FEHLER " & csvFehler
    Return (csvZeilen.Count \ 2).ToString() & " Datenzeilen gelesen"
End Function
