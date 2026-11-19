// Kopfloser Report-Test mit Allplans eigenem ReportViewer 15 (Microsoft.ReportViewer.WinForms).
// Rendert eine .rdlc mit Beispieldaten (JSON) als PNG je Seite, auf Wunsch zusaetzlich als PDF.
// Allplans Query-Verarbeitung laeuft NICHT mit: die Daten kommen aus der JSON-Datei.
// Die ReportViewer-DLLs werden zur Laufzeit aus dem Allplan-Programmordner geladen.
//
//   RenderRdlc.exe <rdlc> <daten.json> <ausgabeordner> [--pdf] [--format=xlsx|docx] [--dpi=120] [--prg=<Allplan\Prg>]
//                  [--vollzugriff] [--info] [Name=Wert ...]
//
// Parameter: Name=Wert setzt einen Parameter; bei Zahl-Parametern (Float) gehen 0.95 und 0,95 beide. Hat der Parameter MEHRERE Werte (MultiValue), werden die Werte mit | getrennt:
//   Material=Beton|Mauerwerk. Name=~null setzt Nothing (Nullable). Ein Name, den der Report nicht kennt, wird gemeldet.
// Unterberichte: werden wie in Allplan bedient - das Ziel (<ReportName>, im Ordner des aufrufenden Reports, auch verschachtelt)
//   wird geladen und bekommt die Daten des HAUPTreports (Allplan fuehrt die Abfrage des Ziels nicht aus).
// --vollzugriff: der Code des Reports laeuft mit vollen Rechten (Allplan tut das auch): er kann Dateien lesen und schreiben.
//   Nur setzen, wenn der Report Dateien lesen soll; ohne den Schalter laeuft der Code im Sandkasten (SecurityException).
// --format=xlsx|docx: zusaetzlich als Excel- bzw. Word-Datei (auch pdf); --info: Parameter des Reports auflisten.
//
// JSON: { "types": { "Feld": "String|Double|Int|Bool|Bytes" }, "rows": [ { "Feld": Wert } ] }
//   oder { "datasets": { "AllplanReport": { "types": ..., "rows": ... }, ... } }
//   Bytes-Wert: "file:<Pfad zu Bilddatei>" oder Base64.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Web.Script.Serialization;
using System.Xml;
using Microsoft.Reporting.WinForms;

public static class RenderRdlc
{
    static string prg = @"C:\Program Files\Allplan\Allplan 2027\Prg";
    static bool info = false, vollzugriff = false;
    static string format = null;

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool SetDllDirectory(string path);

    static Assembly Resolve(object sender, ResolveEventArgs e)
    {
        string name = new AssemblyName(e.Name).Name;
        if (name.EndsWith(".resources")) return null;
        if (name != "Microsoft.SqlServer.Types" && !name.StartsWith("Microsoft.ReportViewer.")) return null;
        foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
            if (a.GetName().Name == name) return a;
        string path = Path.Combine(prg, name + ".dll");
        return File.Exists(path) ? Assembly.LoadFrom(path) : null;
    }

    public static int Main(string[] args)
    {
        var rest = new List<string>();
        bool pdf = false; int dpi = 120;
        foreach (string a in args)
        {
            if (a == "--pdf") pdf = true;
            else if (a.StartsWith("--dpi=")) dpi = int.Parse(a.Substring(6));
            else if (a.StartsWith("--prg=")) prg = a.Substring(6);
            else if (a == "--info") info = true;
            else if (a == "--vollzugriff" || a == "--fulltrust") vollzugriff = true;
            else if (a.StartsWith("--format=")) format = a.Substring(9);
            else rest.Add(a);
        }
        if (rest.Count < 3)
        {
            Console.WriteLine("Aufruf: RenderRdlc <rdlc> <json> <ordner> [--pdf] [--format=xlsx|docx] [--dpi=120] [--prg=<Prg>] [--vollzugriff] [--info] [Name=Wert ...]");
            Console.WriteLine("  Mehrere Werte: Name=Wert1|Wert2 (nur bei Parametern mit MultiValue); Name=~null setzt Nothing.");
            Console.WriteLine("  Unterberichte werden wie in Allplan bedient: Ziel aus dem Ordner des Reports, Daten des Hauptreports.");
            Console.WriteLine("  --vollzugriff: der Code des Reports laeuft mit vollen Rechten und kann Dateien lesen und schreiben (wie in Allplan).");
            return 1;
        }
        AppDomain.CurrentDomain.AssemblyResolve += Resolve;
        SetDllDirectory(prg);
        try { return Run(rest, pdf, dpi); }
        catch (Exception e)
        {
            for (Exception x = e; x != null; x = x.InnerException)
                Console.WriteLine("FEHLER: " + x.GetType().Name + ": " + x.Message);
            return 2;
        }
    }

    static Type ColumnType(string t)
    {
        switch (t)
        {
            case "Double": return typeof(double);
            case "Int": return typeof(int);
            case "Bool": return typeof(bool);
            case "Bytes": return typeof(byte[]);
            default: return typeof(string);
        }
    }

    static object Cell(Type t, object v, string baseDir)
    {
        if (v == null) return DBNull.Value;
        if (t == typeof(double)) return Convert.ToDouble(v, System.Globalization.CultureInfo.InvariantCulture);
        if (t == typeof(int)) return Convert.ToInt32(v, System.Globalization.CultureInfo.InvariantCulture);
        if (t == typeof(bool)) return Convert.ToBoolean(v);
        if (t == typeof(byte[]))
        {
            string s = Convert.ToString(v);
            if (s.StartsWith("file:"))
            {
                string p = s.Substring(5);
                if (!Path.IsPathRooted(p)) p = Path.Combine(baseDir, p);
                return File.ReadAllBytes(p);
            }
            return Convert.FromBase64String(s);
        }
        return Convert.ToString(v, System.Globalization.CultureInfo.InvariantCulture);
    }

    static DataTable Table(string name, Dictionary<string, object> def, string baseDir)
    {
        var types = (Dictionary<string, object>)def["types"];
        var table = new DataTable(name);
        foreach (var kv in types) table.Columns.Add(kv.Key, ColumnType((string)kv.Value));
        foreach (object rowObj in (IEnumerable)def["rows"])
        {
            var src = (Dictionary<string, object>)rowObj;
            DataRow row = table.NewRow();
            foreach (var kv in src)
                if (table.Columns.Contains(kv.Key))
                    row[kv.Key] = Cell(table.Columns[kv.Key].DataType, kv.Value, baseDir);
            table.Rows.Add(row);
        }
        return table;
    }

    // Unterberichte wie Allplan bedienen: jedes <Subreport><ReportName> (auch in geladenen Zielen, verschachtelt) aus dem Ordner des
    // aufrufenden Reports laden. ReportName ohne Endung; Ausdruecke (=...) lassen sich nicht vorab laden und werden gemeldet.
    static void LoadSubreports(LocalReport report, string rdlcPath, HashSet<string> loaded)
    {
        var doc = new XmlDocument();
        doc.Load(rdlcPath);
        string dir = Path.GetDirectoryName(rdlcPath);
        foreach (XmlNode n in doc.GetElementsByTagName("ReportName"))
        {
            if (n.ParentNode == null || n.ParentNode.LocalName != "Subreport") continue;
            string name = n.InnerText.Trim();
            if (name.StartsWith("="))
            {
                Console.WriteLine("WARNUNG: Unterbericht mit Ausdruck als Ziel (" + name + ") wird nicht vorab geladen.");
                continue;
            }
            if (!loaded.Add(name)) continue;
            string file = Path.Combine(dir, name + ".rdlc");
            if (!File.Exists(file)) file = Path.Combine(dir, name + ".rdl");
            if (!File.Exists(file))
            {
                Console.WriteLine("WARNUNG: Unterbericht-Datei fehlt: " + Path.Combine(dir, name + ".rdlc"));
                continue;
            }
            using (var rd = new StreamReader(file)) report.LoadSubreportDefinition(name, rd);
            Console.WriteLine("Unterbericht geladen: " + name);
            LoadSubreports(report, file, loaded);
        }
    }

    static string FormatName(string f)
    {
        switch (f.ToLowerInvariant())
        {
            case "xlsx": return "EXCELOPENXML";
            case "docx": return "WORDOPENXML";
            case "pdf": return "PDF";
            default: return f;
        }
    }

    // Float-Parameter: der ReportViewer liest den Wert in der Kultur des Rechners (auch bei englischem Report; gemessen). Mit genau EINEM
    // Trennzeichen ('.' oder ',') wird es zum Dezimaltrenner dieser Kultur, so dass 0.95 und 0,95 dasselbe ergeben (sonst wird 0.95 zu 95).
    // Mehrdeutiges (beide Zeichen oder mehrere Trennzeichen) bleibt unveraendert und wird gemeldet.
    static string Dezimal(string name, string wert)
    {
        string ziel = System.Globalization.CultureInfo.CurrentCulture.NumberFormat.NumberDecimalSeparator;
        int punkte = 0, kommas = 0;
        foreach (char c in wert) { if (c == '.') punkte++; else if (c == ',') kommas++; }
        if (punkte + kommas == 0) return wert;
        if (punkte + kommas > 1)
        {
            Console.WriteLine("WARNUNG: Der Wert '" + wert + "' von Parameter '" + name + "' hat mehrere Trennzeichen und wird unveraendert uebergeben (Dezimaltrenner des Rechners: '" + ziel + "').");
            return wert;
        }
        return wert.Replace(punkte == 1 ? "." : ",", ziel);
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    static int Run(List<string> rest, bool pdf, int dpi)
    {
        string jsonPath = Path.GetFullPath(rest[1]);
        var ser = new JavaScriptSerializer(); ser.MaxJsonLength = int.MaxValue;
        var json = (Dictionary<string, object>)ser.DeserializeObject(File.ReadAllText(jsonPath));
        string baseDir = Path.GetDirectoryName(jsonPath);

        var report = new LocalReport();
        report.ReportPath = Path.GetFullPath(rest[0]);
        report.EnableExternalImages = true;
        report.EnableHyperlinks = true;
        if (vollzugriff)
        {
            report.SetBasePermissionsForSandboxAppDomain(new System.Security.PermissionSet(System.Security.Permissions.PermissionState.Unrestricted));
            Console.WriteLine("HINWEIS: --vollzugriff: Der Code des Reports laeuft mit vollen Rechten und kann Dateien lesen und schreiben (wie in Allplan).");
        }
        var tables = new Dictionary<string, DataTable>();
        if (json.ContainsKey("datasets"))
            foreach (var kv in (Dictionary<string, object>)json["datasets"])
                tables[kv.Key] = Table(kv.Key, (Dictionary<string, object>)kv.Value, baseDir);
        else
            tables["AllplanReport"] = Table("AllplanReport", json, baseDir);
        DataTable firstTable = null;
        foreach (var kv in tables)
        {
            report.DataSources.Add(new ReportDataSource(kv.Key, kv.Value));
            if (firstTable == null) firstTable = kv.Value;
        }

        // Unterberichte: Ziel laden, dem Ziel die Daten des HAUPTreports geben (so macht es Allplan, gemessen).
        LoadSubreports(report, Path.GetFullPath(rest[0]), new HashSet<string>());
        report.SubreportProcessing += (sender, ev) =>
        {
            Console.WriteLine("Unterbericht angefordert: " + ev.ReportPath + " (Daten des Hauptreports)");
            foreach (string dn in ev.DataSourceNames)
                ev.DataSources.Add(new ReportDataSource(dn, tables.ContainsKey(dn) ? tables[dn] : firstTable));
        };

        var values = new Dictionary<string, string> {
            {"Project_Name", "Testprojekt"}, {"Edited_By", "Test"}, {"Company_Name", "Musterbuero"}, {"Company_Address", "Musterstrasse 1"},
            {"Date", DateTime.Today.ToString("yyyy-MM-dd")}, {"Time", "12:00"}, {"Company_Logo", ""},
            {"Telephone_Number", ""}, {"E_Mail", ""}, {"Display_Logo", "False"}, {"Note", ""}};
        var standard = new HashSet<string>(values.Keys);
        for (int i = 3; i < rest.Count; i++)
        {
            int eq = rest[i].IndexOf('=');
            if (eq > 0) values[rest[i].Substring(0, eq)] = rest[i].Substring(eq + 1);
        }
        var declared = new Dictionary<string, ReportParameterInfo>();
        foreach (ReportParameterInfo pi in report.GetParameters()) declared[pi.Name] = pi;
        var list = new List<ReportParameter>();
        foreach (var kv in values)
        {
            if (!declared.ContainsKey(kv.Key))
            {
                // Vorbelegte Standardwerte duerfen fehlen; ein vom Aufrufer genannter Name, den der Report nicht kennt, wird gemeldet.
                if (!standard.Contains(kv.Key)) Console.WriteLine("WARNUNG: Der Report kennt keinen Parameter '" + kv.Key + "' (Wert ignoriert).");
                continue;
            }
            bool zahl = declared[kv.Key].DataType == ParameterDataType.Float;
            if (kv.Value == "~null") list.Add(new ReportParameter(kv.Key, (string)null));
            else if (declared[kv.Key].MultiValue)
            {
                string[] teile = kv.Value.Split('|');
                if (zahl) for (int t = 0; t < teile.Length; t++) teile[t] = Dezimal(kv.Key, teile[t]);
                list.Add(new ReportParameter(kv.Key, teile));
            }
            else list.Add(new ReportParameter(kv.Key, zahl ? Dezimal(kv.Key, kv.Value) : kv.Value));
        }
        report.SetParameters(list);
        foreach (ReportParameterInfo pi in report.GetParameters())
        {
            if (info)
            {
                var vals = new List<string>(); if (pi.Values != null) foreach (string v in pi.Values) vals.Add(v == null ? "<null>" : v);
                var valid = new List<string>(); if (pi.ValidValues != null) foreach (ValidValue vv in pi.ValidValues) valid.Add(vv.Value + "=" + vv.Label);
                Console.WriteLine("PARAM " + pi.Name + " state=" + pi.State + " multi=" + pi.MultiValue + " nullable=" + pi.Nullable +
                    " type=" + pi.DataType + " prompt=" + pi.Prompt + " vals=[" + string.Join(";", vals.ToArray()) + "] valid=[" + string.Join(";", valid.ToArray()) + "]");
            }
            if (pi.State != ParameterState.HasValidValue)
                Console.WriteLine("FEHLER: Parameter '" + pi.Name + "' hat keinen gueltigen Wert (Zustand " + pi.State +
                    "): mit " + pi.Name + "=Wert setzen (mehrere Werte: " + pi.Name + "=Wert1|Wert2; Nothing: " + pi.Name + "=~null).");
        }

        Directory.CreateDirectory(rest[2]);
        string baseName = Path.GetFileNameWithoutExtension(rest[0]);
        string mime, enc, ext; string[] streams; Warning[] warnings;
        int pages = 0;
        var gemeldet = new HashSet<string>();
        for (int page = 1; page <= 60; page++)
        {
            string deviceInfo = "<DeviceInfo><OutputFormat>PNG</OutputFormat><StartPage>" + page +
                                "</StartPage><DpiX>" + dpi + "</DpiX><DpiY>" + dpi + "</DpiY></DeviceInfo>";
            byte[] bytes;
            try { bytes = report.Render("IMAGE", deviceInfo, out mime, out enc, out ext, out streams, out warnings); }
            catch (Exception) { if (page == 1) throw; break; }
            if (bytes == null || bytes.Length < 200) break;
            string file = Path.Combine(rest[2], baseName + "_S" + page + ".png");
            File.WriteAllBytes(file, bytes);
            pages = page;
            Console.WriteLine("Seite " + page + ": " + file + " (" + bytes.Length + " Bytes)");
            // Warnungen aller Seiten (je Meldung einmal, mit der Seite, auf der sie zuerst auftrat)
            foreach (Warning w in warnings)
            {
                string meldung = w.Severity + " " + w.Code + " [" + w.ObjectType + " " + w.ObjectName + "]: " + w.Message;
                if (gemeldet.Add(meldung)) Console.WriteLine("WARNUNG: " + meldung + (page > 1 ? " (ab Seite " + page + ")" : ""));
            }
        }
        if (pdf)
        {
            byte[] bytes = report.Render("PDF", null, out mime, out enc, out ext, out streams, out warnings);
            string file = Path.Combine(rest[2], baseName + ".pdf");
            File.WriteAllBytes(file, bytes);
            Console.WriteLine("PDF: " + file + " (" + bytes.Length + " Bytes)");
        }
        if (format != null)
        {
            byte[] bytes = report.Render(FormatName(format), null, out mime, out enc, out ext, out streams, out warnings);
            string file = Path.Combine(rest[2], baseName + "." + ext);
            File.WriteAllBytes(file, bytes);
            Console.WriteLine("FORMAT " + FormatName(format) + ": " + file + " (" + bytes.Length + " Bytes)");
        }
        Console.WriteLine("OK Seiten=" + pages);
        return 0;
    }
}
