# Baut bin\RenderRdlc.exe gegen die ReportViewer-DLLs der Allplan-Installation.
# Die DLLs werden nach bin\ kopiert (nicht eingecheckt): der Ausdrucks-Host des
# ReportViewers laedt sie aus dem Programmordner der EXE, nicht ueber AssemblyResolve.
#   powershell -ExecutionPolicy Bypass -File build.ps1
# Liegt Allplan 2027 an anderer Stelle:  ... -File build.ps1 -Prg "D:\Allplan\Allplan 2027\Prg"
param([string]$Prg = "C:\Program Files\Allplan\Allplan 2027\Prg")
$ErrorActionPreference = "Stop"
if (-not (Test-Path (Join-Path $Prg "Microsoft.ReportViewer.WinForms.dll"))) {
    Write-Output "FEHLER: Allplan 2027 nicht gefunden unter $Prg. Den Programmordner angeben: -Prg `"<Laufwerk>:\...\Allplan 2027\Prg`""
    exit 2
}
$csc = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) {
    Write-Output "FEHLER: Der C#-Compiler von Windows fehlt ($csc). Er gehoert zum .NET Framework 4.8."
    exit 2
}
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$bin = Join-Path $here "bin"
New-Item -ItemType Directory -Force $bin | Out-Null
foreach ($f in "Microsoft.ReportViewer.Common.dll", "Microsoft.ReportViewer.DataVisualization.dll",
               "Microsoft.ReportViewer.Design.dll", "Microsoft.ReportViewer.ProcessingObjectModel.dll",
               "Microsoft.ReportViewer.WinForms.dll", "Microsoft.SqlServer.Types.dll", "SqlServerSpatial170.dll") {
    Copy-Item (Join-Path $Prg $f) $bin -Force
}
$config = @'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <runtime>
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <dependentAssembly>
        <assemblyIdentity name="Microsoft.SqlServer.Types" publicKeyToken="89845dcd8080cc91" culture="neutral" />
        <bindingRedirect oldVersion="0.0.0.0-17.0.0.0" newVersion="17.0.0.0" />
      </dependentAssembly>
    </assemblyBinding>
  </runtime>
</configuration>
'@
[IO.File]::WriteAllText((Join-Path $bin "RenderRdlc.exe.config"), $config, (New-Object Text.UTF8Encoding($false)))
$out = Join-Path $bin "RenderRdlc.exe"
& $csc /nologo /platform:x64 /target:exe "/out:$out" `
    "/r:$bin\Microsoft.ReportViewer.WinForms.dll" `
    "/r:$bin\Microsoft.ReportViewer.Common.dll" `
    /r:System.Web.Extensions.dll /r:System.Data.dll /r:System.Xml.dll `
    (Join-Path $here "RenderRdlc.cs")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Output "gebaut: $out"
