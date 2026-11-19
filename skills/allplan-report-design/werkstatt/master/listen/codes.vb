' ============================================================================================================
' codes.vb - Strichcode 128, Strichcode 39 und QR-Code als Bild aus dem <Code>-Block (nur Systembibliotheken)
' Beleg in Allplan 2027 (PDF-Ausgabe, mit zxing-cpp dekodiert): p_strichcode (9 von 9 Codes) und p_qr (8 von 8 Codes)
'
' EINBAU
'   1. Diesen Text (ab der Zeile "Private Const T39") in den <Code>-Block des Reports setzen. In der .rdlc muss er XML-maskiert
'      sein (& < > "); der Bausatz (core.report -> esc) tut das selbst. Namen kollidieren nicht mit master/bausteine.CODE.
'   2. Im Report (nach <Language>, vor </Report>) das CodeModule eintragen, sonst findet der Code System.Drawing nicht:
'        <CodeModules><CodeModule>System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a</CodeModule></CodeModules>
'      (Bausatz: c.report(..., codemodules=["System.Drawing, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a"]).) NICHT "System" als CodeModule eintragen.
'   3. Ein Image mit Source Database, MIMEType image/png, Sizing FitProportional und dem Wert:
'        =Code.QrPng(Fields!Nr.Value, 5)          QR-Code, 5 Pixel je Modul
'        =Code.Strichcode128(Fields!Nr.Value)     Code 128 Satz B, 2 Pixel je Modul, 50 Pixel hoch
'        =Code.Strichcode39(Fields!Nr.Value)      Code 39, 2 Pixel je Modul, 50 Pixel hoch
'      Feste Texte gehen genauso: =Code.QrPng("BT-0042", 5). Je Tabellenzeile geht es (gemessen mit 5 bis 6 Zeilen je Probe).
'
' GRENZEN (gemessen)
'   Strichcode 128: nur ASCII 32..126 (Gross- und Kleinbuchstaben, Ziffern, Leerzeichen, Satzzeichen); andere Zeichen ergeben ein
'                   leeres Bild. Keine Laengengrenze ausser der Seitenbreite (17 Zeichen = rund 450 x 50 Pixel).
'   Strichcode 39:  nur 0-9 A-Z - . Leerzeichen $ / + %; Kleinbuchstaben werden zu Grossbuchstaben (Gross/Klein geht verloren);
'                   / + $ % lesen Decoder als Zeichenpaar (Full-ASCII) und liefern ein anderes Zeichen: in IDs meiden.
'                   Start/Stopp * kommt von selbst dazu. 6 Zeichen = 294 x 50 Pixel.
'   QR-Code:        Version 1-5, Byte-Modus (UTF-8), Fehlerkorrektur L, feste Maske 0; hoechstens 106 Byte
'                   (Version 1: 17, 2: 32, 3: 53, 4: 78, 5: 106). Laenger = leeres Bild ohne Fehler. Bildgroesse (17+4*Version+8)*px,
'                   bei px = 5: 145 bis 225 Pixel im Quadrat. Immer unter 300 x 300 Pixel bleiben (ein 1600-Pixel-Bild per Code
'                   fiel in Allplan zeitlich mit einem Absturz zusammen).
'   Zeitbedarf: Seiten mit 3.000 Datenzeilen und je 5 Bildern kopflos rund 1 bis 2 Sekunden laenger; in Allplan nicht eigens gemessen.
' ============================================================================================================

Private Const T39 As String = "0nnnwwnwnn1wnnwnnnnw2nnwwnnnnw3wnwwnnnnn4nnnwwnnnw5wnnwwnnnn6nnwwwnnnn7nnnwnnwnw8wnnwnnwnn9nnwwnnwnnAwnnnnwnnwBnnwnnwnnwCwnwnnwnnnDnnnnwwnnwEwnnnwwnnnFnnwnwwnnnGnnnnnwwnwHwnnnnwwnnInnwnnwwnnJnnnnwwwnnKwnnnnnnwwLnnwnnnnwwMwnwnnnnwnNnnnnwnnwwOwnnnwnnwnPnnwnwnnwnQnnnnnnwwwRwnnnnnwwnSnnwnnnwwnTnnnnwnwwnUwwnnnnnnwVnwwnnnnnwWwwwnnnnnnXnwnnwnnnwYwwnnwnnnnZnwwnwnnnn-nwnnnnwnw.wwnnnnwnn nwwnnnwnn*nwnnwnwnn$nwnwnwnnn/nwnwnnnwn+nwnnnwnwn%nnnwnwnwn"

Private Const T128 As String = "212222 222122 222221 121223 121322 131222 122213 122312 132212 221213 221312 231212 112232 122132 122231 113222 123122 123221 223211 221132 221231 213212 223112 312131 311222 321122 321221 312212 322112 322211 212123 212321 232121 111323 131123 131321 112313 132113 132311 211313 231113 231311 112133 112331 132131 113123 113321 133121 313121 211331 231131 213113 213311 213131 311123 311321 331121 312113 312311 332111 314111 221411 431111 111224 111422 121124 121421 141122 141221 112214 112412 122114 122411 142112 142211 241211 221114 413111 241112 134111 111242 121142 121241 114212 124112 124211 411212 421112 421211 212141 214121 412121 111143 111341 131141 114113 114311 411113 411311 113141 114131 311141 411131 211412 211214 211232 2331112"

' Code 39 als Modulfolge: "1" = Balken, "0" = Luecke; schmal = 1 Modul, breit = 3 Module. Start und Stopp "*" kommen dazu.
Public Function Modul39(ByVal text As Object) As String
    Dim s As String = "*" & text.ToString().ToUpper() & "*"
    Dim r As New System.Text.StringBuilder()
    Dim k, j, e, p, w As Integer
    For k = 0 To s.Length - 1
        p = -1
        For j = 0 To T39.Length - 10 Step 10
            If T39(j) = s(k) Then
                p = j
                Exit For
            End If
        Next
        If p < 0 Then Return ""
        For e = 1 To 9
            w = 1
            If T39(p + e) = "w"c Then w = 3
            If e Mod 2 = 1 Then
                r.Append("1"c, w)
            Else
                r.Append("0"c, w)
            End If
        Next
        If k < s.Length - 1 Then r.Append("0"c)
    Next
    Return r.ToString()
End Function

' Code 128 Satz B (ASCII 32..126) als Modulfolge, mit Pruefzeichen.
Public Function Modul128(ByVal text As Object) As String
    Dim s As String = text.ToString()
    Dim muster() As String = T128.Split(" "c)
    Dim werte As New System.Collections.Generic.List(Of Integer)
    Dim i, v, summe As Integer
    werte.Add(104)
    summe = 104
    For i = 0 To s.Length - 1
        v = Asc(s(i)) - 32
        If v < 0 OrElse v > 94 Then Return ""
        werte.Add(v)
        summe = summe + v * (i + 1)
    Next
    werte.Add(summe Mod 103)
    werte.Add(106)
    Dim r As New System.Text.StringBuilder()
    Dim d, n As Integer
    Dim balken As Boolean
    For i = 0 To werte.Count - 1
        balken = True
        For d = 0 To muster(werte(i)).Length - 1
            n = Asc(muster(werte(i))(d)) - 48
            If balken Then
                r.Append("1"c, n)
            Else
                r.Append("0"c, n)
            End If
            balken = Not balken
        Next
    Next
    Return r.ToString()
End Function

' Modulfolge als PNG: px Pixel je Modul, hoch Pixel Hoehe, ruhe Module Ruhezone links und rechts.
Public Function ModulPng(ByVal m As String, ByVal px As Integer, ByVal hoch As Integer, ByVal ruhe As Integer) As Byte()
    If m.Length = 0 Then Return Nothing
    Dim bmp As New System.Drawing.Bitmap((m.Length + 2 * ruhe) * px, hoch)
    Dim g As System.Drawing.Graphics = System.Drawing.Graphics.FromImage(bmp)
    g.Clear(System.Drawing.Color.White)
    Dim i As Integer
    For i = 0 To m.Length - 1
        If m(i) = "1"c Then g.FillRectangle(System.Drawing.Brushes.Black, (i + ruhe) * px, 0, px, hoch)
    Next
    g.Dispose()
    Dim ms As New System.IO.MemoryStream()
    bmp.Save(ms, System.Drawing.Imaging.ImageFormat.Png)
    bmp.Dispose()
    Return ms.ToArray()
End Function

Public Function Strichcode39(ByVal text As Object) As Byte()
    Return ModulPng(Modul39(text), 2, 50, 10)
End Function

Public Function Strichcode128(ByVal text As Object) As Byte()
    Return ModulPng(Modul128(text), 2, 50, 10)
End Function

' ---------------------------------------------------------------- QR-Code
Private gfExp(511) As Integer
Private gfLog(255) As Integer
Private gfFertig As Boolean = False

Private Sub GfStart()
    If gfFertig Then Return
    Dim x, i As Integer
    x = 1
    For i = 0 To 254
        gfExp(i) = x
        gfLog(x) = i
        x = x * 2
        If x >= 256 Then x = x Xor 285
    Next
    For i = 255 To 511
        gfExp(i) = gfExp(i - 255)
    Next
    gfFertig = True
End Sub

Private Function GfMul(ByVal a As Integer, ByVal b As Integer) As Integer
    If a = 0 OrElse b = 0 Then Return 0
    Return gfExp(gfLog(a) + gfLog(b))
End Function

' Fehlerkorrektur-Codewoerter (Reed-Solomon) zu den Datenwoertern
Private Function RsRest(ByVal daten() As Integer, ByVal ec As Integer) As Integer()
    GfStart()
    Dim gen(ec) As Integer
    Dim nxt(ec) As Integer
    Dim i, j As Integer
    gen(0) = 1
    For i = 0 To ec - 1
        For j = 0 To ec
            nxt(j) = 0
        Next
        For j = 0 To i
            nxt(j) = nxt(j) Xor gen(j)
            nxt(j + 1) = nxt(j + 1) Xor GfMul(gen(j), gfExp(i))
        Next
        For j = 0 To ec
            gen(j) = nxt(j)
        Next
    Next
    Dim rest(ec - 1) As Integer
    Dim f As Integer
    For i = 0 To daten.Length - 1
        f = daten(i) Xor rest(0)
        For j = 0 To ec - 2
            rest(j) = rest(j + 1)
        Next
        rest(ec - 1) = 0
        For j = 0 To ec - 1
            rest(j) = rest(j) Xor GfMul(gen(j + 1), f)
        Next
    Next
    Return rest
End Function

Private Sub QrSetze(ByVal m(,) As Boolean, ByVal fn(,) As Boolean, ByVal x As Integer, ByVal y As Integer, ByVal v As Boolean)
    m(y, x) = v
    fn(y, x) = True
End Sub

' QR-Matrix: Version 1-5, Byte-Modus, Fehlerkorrektur L, Maske 0. Nothing, wenn der Text nicht passt (hoechstens 106 Bytes).
Public Function QrMatrix(ByVal text As Object) As Boolean(,)
    Dim roh() As Byte = System.Text.Encoding.UTF8.GetBytes(text.ToString())
    Dim dcwTab() As Integer = {19, 34, 55, 80, 108}
    Dim ecwTab() As Integer = {7, 10, 15, 20, 26}
    Dim ver As Integer = 0
    Dim i, j, x, y As Integer
    For i = 1 To 5
        If roh.Length <= dcwTab(i - 1) - 2 Then
            ver = i
            Exit For
        End If
    Next
    If ver = 0 Then Return Nothing
    Dim dcw As Integer = dcwTab(ver - 1)
    Dim ecw As Integer = ecwTab(ver - 1)
    Dim bits As New System.Text.StringBuilder()
    bits.Append("0100")
    bits.Append(Convert.ToString(roh.Length, 2).PadLeft(8, "0"c))
    For i = 0 To roh.Length - 1
        bits.Append(Convert.ToString(CInt(roh(i)), 2).PadLeft(8, "0"c))
    Next
    j = dcw * 8 - bits.Length
    If j > 4 Then j = 4
    bits.Append("0"c, j)
    While bits.Length Mod 8 <> 0
        bits.Append("0"c)
    End While
    Dim daten(dcw - 1) As Integer
    For i = 0 To bits.Length \ 8 - 1
        daten(i) = Convert.ToInt32(bits.ToString(i * 8, 8), 2)
    Next
    For i = bits.Length \ 8 To dcw - 1
        If (i - bits.Length \ 8) Mod 2 = 0 Then
            daten(i) = 236
        Else
            daten(i) = 17
        End If
    Next
    Dim rest() As Integer = RsRest(daten, ecw)
    Dim alle(dcw + ecw - 1) As Integer
    For i = 0 To dcw - 1
        alle(i) = daten(i)
    Next
    For i = 0 To ecw - 1
        alle(dcw + i) = rest(i)
    Next
    Dim n As Integer = 17 + 4 * ver
    Dim m(n - 1, n - 1) As Boolean
    Dim fn(n - 1, n - 1) As Boolean
    For i = 0 To n - 1
        QrSetze(m, fn, 6, i, i Mod 2 = 0)
        QrSetze(m, fn, i, 6, i Mod 2 = 0)
    Next
    Dim ecken() As Integer = {3, 3, n - 4, 3, 3, n - 4}
    Dim dx, dy, d, k As Integer
    For k = 0 To 2
        For dy = -4 To 4
            For dx = -4 To 4
                x = ecken(2 * k) + dx
                y = ecken(2 * k + 1) + dy
                If x >= 0 AndAlso x < n AndAlso y >= 0 AndAlso y < n Then
                    d = System.Math.Max(System.Math.Abs(dx), System.Math.Abs(dy))
                    QrSetze(m, fn, x, y, d <> 2 AndAlso d <> 4)
                End If
            Next
        Next
    Next
    If ver >= 2 Then
        Dim a As Integer = 10 + 4 * ver
        For dy = -2 To 2
            For dx = -2 To 2
                QrSetze(m, fn, a + dx, a + dy, System.Math.Max(System.Math.Abs(dx), System.Math.Abs(dy)) <> 1)
            Next
        Next
    End If
    ' Formatinfo: Stufe L (01), Maske 0, BCH-Rest, Maskierung 0x5412
    Dim rem1 As Integer = 8
    For i = 1 To 10
        rem1 = (rem1 * 2) Xor ((rem1 \ 512) * 1335)
    Next
    Dim fb As Integer = ((8 * 1024) Or rem1) Xor 21522
    For i = 0 To 5
        QrSetze(m, fn, 8, i, (fb \ (2 ^ i)) Mod 2 = 1)
    Next
    QrSetze(m, fn, 8, 7, (fb \ 64) Mod 2 = 1)
    QrSetze(m, fn, 8, 8, (fb \ 128) Mod 2 = 1)
    QrSetze(m, fn, 7, 8, (fb \ 256) Mod 2 = 1)
    For i = 9 To 14
        QrSetze(m, fn, 14 - i, 8, (fb \ (2 ^ i)) Mod 2 = 1)
    Next
    For i = 0 To 7
        QrSetze(m, fn, n - 1 - i, 8, (fb \ (2 ^ i)) Mod 2 = 1)
    Next
    For i = 8 To 14
        QrSetze(m, fn, 8, n - 15 + i, (fb \ (2 ^ i)) Mod 2 = 1)
    Next
    QrSetze(m, fn, 8, n - 8, True)
    ' Daten im Zickzack von rechts unten
    Dim bit As Integer = 0
    Dim rechts As Integer = n - 1
    Dim vert, jj As Integer
    Dim auf As Boolean
    While rechts >= 1
        If rechts = 6 Then rechts = 5
        For vert = 0 To n - 1
            For jj = 0 To 1
                x = rechts - jj
                auf = ((rechts + 1) And 2) = 0
                If auf Then
                    y = n - 1 - vert
                Else
                    y = vert
                End If
                If Not fn(y, x) AndAlso bit < alle.Length * 8 Then
                    m(y, x) = ((alle(bit \ 8) \ (2 ^ (7 - (bit Mod 8)))) Mod 2) = 1
                    bit = bit + 1
                End If
            Next
        Next
        rechts = rechts - 2
    End While
    For y = 0 To n - 1
        For x = 0 To n - 1
            If Not fn(y, x) AndAlso (x + y) Mod 2 = 0 Then m(y, x) = Not m(y, x)
        Next
    Next
    Return m
End Function

' QR-Code als PNG: px Pixel je Modul, Ruhezone 4 Module.
Public Function QrPng(ByVal text As Object, ByVal px As Integer) As Byte()
    Dim m(,) As Boolean = QrMatrix(text)
    If m Is Nothing Then Return Nothing
    Dim n As Integer = m.GetLength(0)
    Dim bmp As New System.Drawing.Bitmap((n + 8) * px, (n + 8) * px)
    Dim g As System.Drawing.Graphics = System.Drawing.Graphics.FromImage(bmp)
    g.Clear(System.Drawing.Color.White)
    Dim x, y As Integer
    For y = 0 To n - 1
        For x = 0 To n - 1
            If m(y, x) Then g.FillRectangle(System.Drawing.Brushes.Black, (x + 4) * px, (y + 4) * px, px, px)
        Next
    Next
    g.Dispose()
    Dim ms As New System.IO.MemoryStream()
    bmp.Save(ms, System.Drawing.Imaging.ImageFormat.Png)
    bmp.Dispose()
    Return ms.ToArray()
End Function
