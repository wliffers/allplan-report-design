"""Datenprobe: baut aus einer Allplan-Abfrage einen schlichten Tabellen-Report (RDL 2005).

Zweck: nachsehen, was Allplan fuer eine Abfrage wirklich liefert - Zeilenzahl, Werte,
Schreibweisen, Einheiten. Den Report in Allplan als .xlsx exportieren (allplan_export.py),
dann liegen die Rohdaten als Tabelle vor.

    python datenprobe.py <ziel.rdlc> --from "[MODEL_DATA]" "@498@:Objekt" "@508@:Material" "@223@:Volumen:Double"

Jede Spalte: <Attribut mit Optionen>:<Feldname>[:<Typ>]  (Typ String | Double | Int32 | Bild, Vorgabe String).
Typ Bild = Bauteilgrafik (@205@ ...): Feld als System.Byte[], Zelle mit <Image>, Zeilen 3 cm hoch.
Optionen eines Attributs mit '|' anhaengen: "@221@|Dim=1:Dicke:Double".
Geruest (Datenquelle, Parameter, Kopf, Fuss) stammt aus Allplans Template_Grouping0_2005.rdlc.
"""
import argparse
import os
import re
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
VORLAGE = "Template_Grouping0_2005.rdlc"


def _startvorlage():
    """Allplans Startvorlage aus der Installation (die Umgebungsvariable ALLPLAN_REPORTS geht vor).
    Die Datei gehoert zu Allplan und wird nicht mitgeliefert."""
    orte = [os.environ.get("ALLPLAN_REPORTS", ""),
            os.path.join("C:" + os.sep, "ProgramData", "Nemetschek", "Allplan", "2027", "Etc", "Reports")]
    for ort in orte:
        if ort and os.path.isfile(os.path.join(ort, VORLAGE)):
            return os.path.normpath(os.path.join(ort, VORLAGE))
    raise SystemExit("Startvorlage %s nicht gefunden. Gesucht in: %s. Abhilfe: ALLPLAN_REPORTS auf den Ordner "
                     "Etc/Reports der Allplan-Installation setzen." % (VORLAGE, "; ".join(o for o in orte if o)))


TEMPLATE = _startvorlage()

CELL = """                <TableCell>
                  <ReportItems>
                    <Textbox Name="{name}">
                      <Style>{border}
                        <FontSize>7pt</FontSize>{weight}
                        <VerticalAlign>Bottom</VerticalAlign>
                        <PaddingLeft>2pt</PaddingLeft>
                        <PaddingRight>2pt</PaddingRight>
                        <PaddingTop>1pt</PaddingTop>
                        <PaddingBottom>1pt</PaddingBottom>
                      </Style>
                      <CanGrow>true</CanGrow>
                      <Value>{value}</Value>
                    </Textbox>
                  </ReportItems>
                </TableCell>
"""


IMAGE_CELL = """                <TableCell>
                  <ReportItems>
                    <Image Name="{name}">
                      <Sizing>FitProportional</Sizing>
                      <Source>Database</Source>
                      <MIMEType>image/png</MIMEType>
                      <Value>{value}</Value>
                    </Image>
                  </ReportItems>
                </TableCell>
"""


def build(columns, from_clause, title):
    """columns: Liste (attribut, feldname, typ). Liefert den RDLC-Text."""
    with open(TEMPLATE, encoding="utf-8-sig") as handle:
        text = handle.read()
    fields = "".join(
        '        <Field Name="{0}">\n          <DataField>{0}</DataField>\n'
        '          <rd:TypeName>System.{1}</rd:TypeName>\n        </Field>\n'.format(
            name, "Byte[]" if typ == "Bild" else typ)
        for _attr, name, typ in columns)
    text = re.sub(r"<Fields>.*?</Fields>", lambda _m: "<Fields>\n" + fields + "      </Fields>", text, flags=re.S)
    select = ",\n".join("       {0}[Name={1}{2}]".format(
        attr.split("|")[0], name, "".join("|" + o for o in attr.split("|")[1:])) for attr, name, _t in columns)
    query = "SELECT\n" + select + "\nFROM " + from_clause + "\n"
    text = re.sub(r"<CommandText>.*?</CommandText>", lambda _m: "<CommandText>" + query + "</CommandText>", text, flags=re.S)
    width = round(17.9 / len(columns), 3)
    details = "".join((IMAGE_CELL if typ == "Bild" else CELL).format(
        name="D_" + name, border="", weight="", value="=Fields!%s.Value" % name) for _a, name, typ in columns)
    row_height = "3cm" if any(typ == "Bild" for _a, _n, typ in columns) else "0.4cm"
    header = "".join(CELL.format(
        name="H_" + name, weight="\n                        <FontWeight>700</FontWeight>",
        border="\n                        <BorderStyle>\n                          <Bottom>Solid</Bottom>\n"
               "                        </BorderStyle>",
        value="%s %s" % (name, attr.split("|")[0])) for attr, name, _t in columns)
    footer = CELL.format(name="F_Count", border="", weight="\n                        <FontWeight>700</FontWeight>",
                         value='="Zeilen: " &amp; CountRows("AllplanReport")')
    footer += "".join(CELL.format(name="F_" + name, border="", weight="", value="") for _a, name, _t in columns[1:])
    table = """      <Table Name="Table">
        <Top>0.2cm</Top>
        <Width>{total}cm</Width>
        <Details>
          <TableRows>
            <TableRow>
              <TableCells>
{details}              </TableCells>
              <Height>{row_height}</Height>
            </TableRow>
          </TableRows>
        </Details>
        <Header>
          <RepeatOnNewPage>true</RepeatOnNewPage>
          <TableRows>
            <TableRow>
              <TableCells>
{header}              </TableCells>
              <Height>0.6cm</Height>
            </TableRow>
          </TableRows>
        </Header>
        <Footer>
          <TableRows>
            <TableRow>
              <TableCells>
{footer}              </TableCells>
              <Height>0.5cm</Height>
            </TableRow>
          </TableRows>
        </Footer>
        <TableColumns>
{cols}        </TableColumns>
        <Height>1.5cm</Height>
        <Left>0pt</Left>
      </Table>
""".format(row_height=row_height, total=round(width * len(columns), 3), details=details, header=header, footer=footer,
           cols="          <TableColumn>\n            <Width>%scm</Width>\n          </TableColumn>\n" % width * len(columns))
    text = re.sub(r"      <Table Name=\"Table\">.*?</Table>\n", lambda _m: table, text, flags=re.S)
    text = text.replace("<Value>Heading1</Value>", "<Value>%s</Value>" % title)
    text = re.sub(r"<rd:ReportID>.*?</rd:ReportID>", "<rd:ReportID>%s</rd:ReportID>" % uuid.uuid4(), text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ziel")
    parser.add_argument("spalten", nargs="+")
    parser.add_argument("--from", dest="from_clause", default="[MODEL_DATA]")
    parser.add_argument("--titel", default="Datenprobe")
    args = parser.parse_args()
    columns = []
    for spec in args.spalten:
        parts = spec.split(":")
        columns.append((parts[0], parts[1], parts[2] if len(parts) > 2 else "String"))
    text = build(columns, args.from_clause, args.titel)
    with open(args.ziel, "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write(text)
    print(args.ziel, len(columns), "Spalten")


if __name__ == "__main__":
    main()
