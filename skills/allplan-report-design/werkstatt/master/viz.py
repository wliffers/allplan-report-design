# -*- coding: utf-8 -*-
"""Diagramm- und Messanzeigen-Bausteine (RDL 2016) fuer den Master-Report.

Stand des Labors labor/viz2016/rdl.py, hier als Bibliothek: nur die Element-Bauer (chart, S, axis,
area, legend, dlabel, gauge ...). Das Report-Geruest baut core.py."""
import re
from xml.sax.saxutils import escape


def esc(s):
    return escape(str(s))


# ------------------------------------------------------------------ Textbox / Style
def st(**kw):
    """Style-Baustein aus Schluesselwoertern (Tags in Originalschreibweise)."""
    return "<Style>" + "".join("<%s>%s</%s>" % (k, esc(v) if not str(v).startswith("<") else v, k) for k, v in kw.items()) + "</Style>"


def border(color="#D0D5DD", style="Solid", width="0.5pt"):
    return "<Border><Color>%s</Color><Style>%s</Style><Width>%s</Width></Border>" % (esc(color), style, width)


def textbox(name, text, top, left, w, h, size="10pt", bold=False, color="#1F2937", align=None, valign=None,
            bg=None, italic=False, font="Segoe UI", border_xml="", wrap_expr=False):
    s = "<FontFamily>%s</FontFamily><FontSize>%s</FontSize>" % (font, size)
    if bold:
        s += "<FontWeight>Bold</FontWeight>"
    if italic:
        s += "<FontStyle>Italic</FontStyle>"
    s += "<Color>%s</Color>" % color
    pstyle = "<Style>%s</Style>" % (("<TextAlign>%s</TextAlign>" % align) if align else "")
    tb_style = ""
    if bg:
        tb_style += "<BackgroundColor>%s</BackgroundColor>" % bg
    if valign:
        tb_style += "<VerticalAlign>%s</VerticalAlign>" % valign
    tb_style += border_xml
    tb_style += "<PaddingLeft>2pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>1pt</PaddingTop><PaddingBottom>1pt</PaddingBottom>"
    return ('<Textbox Name="%s"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether><Paragraphs><Paragraph><TextRuns>'
            "<TextRun><Value>%s</Value><Style>%s</Style></TextRun></TextRuns>%s</Paragraph></Paragraphs>"
            "<Top>%scm</Top><Left>%scm</Left><Height>%scm</Height><Width>%scm</Width><Style>%s</Style></Textbox>"
            % (name, esc(text), s, pstyle, top, left, h, w, tb_style))


def rect(name, top, left, w, h, inner="", bg=None, border_xml=""):
    s = ("<BackgroundColor>%s</BackgroundColor>" % bg if bg else "") + border_xml
    return ('<Rectangle Name="%s"><ReportItems>%s</ReportItems><KeepTogether>true</KeepTogether><Top>%scm</Top><Left>%scm</Left>'
            "<Height>%scm</Height><Width>%scm</Width><Style>%s</Style></Rectangle>" % (name, inner, top, left, h, w, s))


# ------------------------------------------------------------------ Chart
FONT = "Segoe UI"
GRID = "#E5E7EB"
TXT = "#4B5563"


def fstyle(size="8pt", color=TXT, bold=False, fmt=None, font=FONT, extra=""):
    s = "<FontFamily>%s</FontFamily><FontSize>%s</FontSize><Color>%s</Color>" % (font, size, color)
    if bold:
        s += "<FontWeight>Bold</FontWeight>"
    if fmt:
        s += "<Format>%s</Format>" % esc(fmt)
    return "<Style>" + s + extra + "</Style>"


def axis(name="Primary", visible=True, title=None, fmt=None, grid=False, gridcolor=GRID, minimum=None, maximum=None,
         interval=None, reverse=False, log=False, angle=None, hide_labels=False, strips="", line=True, size="8pt",
         extra="", margin=None, rot=None, tick=False, scalebreak=None, title_size="8pt", crossat=None, location=None,
         labelinterval=None, includezero=None):
    x = '<ChartAxis Name="%s">' % name
    line_xml = border("#9CA3AF", "Solid", "0.75pt") if line else border("#FFFFFF", "None", "0.5pt")
    x += fstyle(size, TXT, fmt=fmt, extra=line_xml)
    if title:
        x += "<ChartAxisTitle><Caption>%s</Caption>%s</ChartAxisTitle>" % (esc(title), fstyle(title_size, TXT))
    else:
        x += "<ChartAxisTitle><Caption/></ChartAxisTitle>"
    gl = (border(gridcolor, "Solid", "0.5pt")) if grid else ""
    x += "<ChartMajorGridLines><Enabled>%s</Enabled><Style>%s</Style>%s</ChartMajorGridLines>" % (
        "True" if grid else "False", gl, ("<Interval>%s</Interval>" % interval) if interval and grid else "")
    x = x.replace("<Style><Border>", "<Style><Border>", 1)
    x += "<ChartMinorGridLines><Enabled>False</Enabled><Style>%s</Style></ChartMinorGridLines>" % border(gridcolor, "Dotted", "0.5pt")
    x += "<ChartMajorTickMarks><Enabled>%s</Enabled></ChartMajorTickMarks>" % ("True" if tick else "False")
    x += "<ChartMinorTickMarks><Enabled>False</Enabled></ChartMinorTickMarks>"
    if interval:
        x += "<Interval>%s</Interval>" % interval
    if labelinterval:
        x += "<LabelInterval>%s</LabelInterval>" % labelinterval
    if reverse:
        x += "<Reverse>true</Reverse>"
    if crossat is not None:
        x += "<CrossAt>%s</CrossAt>" % crossat
    if location:
        x += "<Location>%s</Location>" % location
    if strips:
        x += "<ChartStripLines>%s</ChartStripLines>" % strips
    if minimum is not None:
        x += "<Minimum>%s</Minimum>" % esc(minimum)
    if maximum is not None:
        x += "<Maximum>%s</Maximum>" % esc(maximum)
    if log:
        x += "<LogScale>true</LogScale>"
    if hide_labels:
        x += "<HideLabels>true</HideLabels>"
    if angle is not None:
        x += "<Angle>%s</Angle>" % angle
    if rot:
        x += "<AllowLabelRotation>%s</AllowLabelRotation>" % rot
    if includezero:
        x += "<IncludeZero>%s</IncludeZero>" % includezero
    if margin is not None:
        x += "<Margin>%s</Margin>" % margin
    x += "<Visible>%s</Visible>" % ("True" if visible else "False")
    if scalebreak:
        x += scalebreak
    x += extra + "</ChartAxis>"
    return x


def strip(offset, width="0.6", color="#C0392B", title=None, interval="0"):
    t = "<Title>%s</Title>" % esc(title) if title else ""
    return ("<ChartStripLine><Style><BackgroundColor>%s</BackgroundColor></Style>%s<Interval>%s</Interval>"
            "<IntervalOffset>%s</IntervalOffset><StripWidth>%s</StripWidth></ChartStripLine>"
            % (color, t, interval, offset, width))


def area(name="Default", cat_axes=None, val_axes=None, extra="", style="", pos=None, inner=None):
    cat_axes = cat_axes or [axis("Primary")]
    val_axes = val_axes or [axis("Primary", grid=True, line=False)]
    p = ""
    if pos:
        p += "<ChartElementPosition><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width></ChartElementPosition>" % pos
    if inner:
        p += "<ChartInnerPlotPosition><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width></ChartInnerPlotPosition>" % inner
    return ('<ChartArea Name="%s"><ChartCategoryAxes>%s</ChartCategoryAxes><ChartValueAxes>%s</ChartValueAxes>%s%s<Style>%s</Style></ChartArea>'
            % (name, "".join(cat_axes), "".join(val_axes), extra, p, style or "<BackgroundColor>White</BackgroundColor>"))


def legend(name="Default", position="BottomCenter", layout="Row", title=None, size="8pt", hidden=False, extra=""):
    t = ""
    if title:
        t = "<ChartLegendTitle><Caption>%s</Caption>%s</ChartLegendTitle>" % (esc(title), fstyle(size, TXT, bold=True))
    return ('<ChartLegend Name="%s"><Hidden>%s</Hidden>%s<Position>%s</Position><Layout>%s</Layout>%s%s</ChartLegend>'
            % (name, "true" if hidden else "false", fstyle(size, TXT), position, layout, t, extra))


def title(text, size="11pt", name="Default", color="#111827", position="TopCenter", bold=True, extra=""):
    return ('<ChartTitle Name="%s"><Caption>%s</Caption><Style><FontFamily>%s</FontFamily><FontSize>%s</FontSize>'
            "<FontWeight>%s</FontWeight><Color>%s</Color></Style><Position>%s</Position>%s</ChartTitle>"
            % (name, esc(text), FONT, size, "Bold" if bold else "Normal", color, position, extra))


def dlabel(position=None, fmt="N0", size="8pt", color="#374151", label=None, visible=True, bold=False, rotation=None):
    x = "<ChartDataLabel>%s" % fstyle(size, color, bold=bold, fmt=fmt)
    if visible:
        x += "<UseValueAsLabel>%s</UseValueAsLabel>" % ("false" if label else "true")
    if label:
        x += "<Label>%s</Label>" % esc(label)
    if position:
        x += "<Position>%s</Position>" % position
    if rotation is not None:
        x += "<Rotation>%s</Rotation>" % rotation
    x += "<Visible>%s</Visible></ChartDataLabel>" % ("true" if visible else "false")
    return x


def marker(mtype="Circle", size="6pt", color=None, bordercolor="#FFFFFF"):
    s = ""
    if color:
        s += "<BackgroundColor>%s</BackgroundColor>" % color
    s += border(bordercolor, "Solid", "1pt")
    return "<ChartMarker><Type>%s</Type><Size>%s</Size><Style>%s</Style></ChartMarker>" % (mtype, size, s)


def custom(**kw):
    if not kw:
        return ""
    return "<CustomProperties>" + "".join(
        "<CustomProperty><Name>%s</Name><Value>%s</Value></CustomProperty>" % (k, esc(v)) for k, v in kw.items()) + "</CustomProperties>"


def S(name, vals, typ="Column", sub="Plain", color=None, label=None, mark=None, area_name=None, vaxis=None,
      caxis=None, style_extra="", pstyle="", custom_xml="", legend_name=None, tooltip=None, axislabel=None,
      line_w=None, hidden=False, legend_item=None, empty=None, smart=None, grad=None, gradend=None, transp=None):
    """Eine Serie. vals: dict Tag->Ausdruck (Y, X, Size, High, Low, Start, End)."""
    v = "".join("<%s>%s</%s>" % (k, esc(e), k) for k, e in vals.items())
    s = ""
    if color:
        s += "<Color>%s</Color>" % color
    if grad:
        s += "<BackgroundGradientType>%s</BackgroundGradientType>" % grad
        if gradend:
            s += "<BackgroundGradientEndColor>%s</BackgroundGradientEndColor>" % gradend
    if line_w:
        s += border(color or "#2563EB", "Solid", line_w)
    s += style_extra
    pstyle = s + pstyle
    s = ""
    pt = "<ChartDataPoint><ChartDataPointValues>%s</ChartDataPointValues>" % v
    if label:
        pt += label
    if axislabel:
        pt += "<AxisLabel>%s</AxisLabel>" % esc(axislabel)
    if tooltip:
        pt += "<ToolTip>%s</ToolTip>" % esc(tooltip)
    if pstyle:
        pt += "<Style>%s</Style>" % pstyle
    else:
        pt += "<Style/>"
    if mark:
        pt += mark
    pt += "</ChartDataPoint>"
    x = '<ChartSeries Name="%s">' % name
    if hidden:
        x += "<Hidden>true</Hidden>"
    x += "<ChartDataPoints>%s</ChartDataPoints><Type>%s</Type><Subtype>%s</Subtype>" % (pt, typ, sub)
    x += "<Style>%s</Style>" % s if s else "<Style/>"
    if empty:
        x += empty
    if custom_xml:
        x += custom_xml
    if legend_name:
        x += "<LegendName>%s</LegendName>" % legend_name
    if legend_item:
        x += legend_item
    if area_name:
        x += "<ChartAreaName>%s</ChartAreaName>" % area_name
    if vaxis:
        x += "<ValueAxisName>%s</ValueAxisName>" % vaxis
    if caxis:
        x += "<CategoryAxisName>%s</CategoryAxisName>" % caxis
    if smart:
        x += smart
    x += "</ChartSeries>"
    return x


def derived(name, source, formula, params=None, typ="Line", color="#C0392B", w="1.5pt", area_name=None):
    p = ""
    if params:
        p = "<ChartFormulaParameters>" + "".join(
            '<ChartFormulaParameter Name="%s"><Value>%s</Value></ChartFormulaParameter>' % (k, v) for k, v in params.items()
        ) + "</ChartFormulaParameters>"
    an = "<ChartAreaName>%s</ChartAreaName>" % area_name if area_name else ""
    ser = ('<ChartSeries Name="%s"><Type>%s</Type><Subtype>Plain</Subtype><Style>%s</Style>%s</ChartSeries>'
           % (name, typ, border(color, "Solid", w), an))
    return ("<ChartDerivedSeries>%s<SourceChartSeriesName>%s</SourceChartSeriesName><DerivedSeriesFormula>%s</DerivedSeriesFormula>%s</ChartDerivedSeries>"
            % (ser, source, formula, p))


def cat_hier(groups, nomember=False, pre="C"):
    """groups: Liste (Ausdruck, Sortierausdruck|None, Richtung). Verschachtelt von aussen nach innen."""
    if nomember or not groups:
        return "<ChartCategoryHierarchy><ChartMembers><ChartMember><Label>1</Label></ChartMember></ChartMembers></ChartCategoryHierarchy>"
    inner = ""
    for i, (expr, sort, direction) in reversed(list(enumerate(groups))):
        srt = ""
        if sort is not False:
            srt = ("<SortExpressions><SortExpression><Value>%s</Value>%s</SortExpression></SortExpressions>"
                   % (esc(sort or expr), "<Direction>%s</Direction>" % direction if direction else ""))
        inner = ('<ChartMembers><ChartMember><Group Name="%s_Cat%d"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions></Group>'
                 "%s%s<Label>%s</Label></ChartMember></ChartMembers>" % (pre, i + 1, esc(expr), srt, inner, esc(expr)))
    return "<ChartCategoryHierarchy>%s</ChartCategoryHierarchy>" % inner


def ser_hier(names=None, group=None, pre="C"):
    """names: statische Serien (Reihenfolge = Reihenfolge der ChartSeries); group: Ausdruck fuer dynamische Serien."""
    if group:
        return ('<ChartSeriesHierarchy><ChartMembers><ChartMember><Group Name="%s_Ser"><GroupExpressions><GroupExpression>%s</GroupExpression>'
                "</GroupExpressions></Group><SortExpressions><SortExpression><Value>%s</Value></SortExpression></SortExpressions>"
                "<Label>%s</Label></ChartMember></ChartMembers></ChartSeriesHierarchy>" % (pre, esc(group), esc(group), esc(group)))
    return "<ChartSeriesHierarchy><ChartMembers>%s</ChartMembers></ChartSeriesHierarchy>" % "".join(
        "<ChartMember><Label>%s</Label></ChartMember>" % esc(n) for n in names)


def chart(name, top, left, w, h, series, cats, areas=None, legends=None, titles="", palette="Default",
          custom_palette=None, names=None, sergroup=None, nodata=None, dataset=True, derived_xml="", skin="None",
          style=None, tooltip=None, extra="", nomember=False, sort_cats=True):
    """series: Liste von S(...)-XML; cats: Liste (Ausdruck, Sort, Richtung)."""
    x = '<Chart Name="%s">' % name
    x += ser_hier(names=names or [], group=sergroup, pre=name) if (names or sergroup) else "<ChartSeriesHierarchy><ChartMembers><ChartMember><Label/></ChartMember></ChartMembers></ChartSeriesHierarchy>"
    x += cat_hier(cats, nomember=nomember, pre=name)
    x += "<ChartData><ChartSeriesCollection>%s</ChartSeriesCollection>%s</ChartData>" % (
        "".join(series), ("<ChartDerivedSeriesCollection>%s</ChartDerivedSeriesCollection>" % derived_xml) if derived_xml else "")
    x += "<ChartAreas>%s</ChartAreas>" % (areas or area())
    x += "<ChartLegends>%s</ChartLegends>" % (legends if legends is not None else legend(hidden=True))
    if titles:
        x += "<ChartTitles>%s</ChartTitles>" % titles
    x += "<Palette>%s</Palette>" % palette
    if custom_palette:
        x += "<ChartCustomPaletteColors>%s</ChartCustomPaletteColors>" % "".join(
            "<ChartCustomPaletteColor>%s</ChartCustomPaletteColor>" % c for c in custom_palette)
    x += "<ChartBorderSkin><ChartBorderSkinType>%s</ChartBorderSkinType></ChartBorderSkin>" % skin
    if nodata:
        x += ('<ChartNoDataMessage Name="NoDataMessage"><Caption>%s</Caption><Style><FontFamily>%s</FontFamily><FontSize>10pt</FontSize>'
              "<Color>#6B7280</Color></Style></ChartNoDataMessage>" % (esc(nodata), FONT))
    if dataset:
        x += "<DataSetName>AllplanReport</DataSetName>"
    if tooltip:
        x += "<ToolTip>%s</ToolTip>" % esc(tooltip)
    x += extra
    x += "<Top>%scm</Top><Left>%scm</Left><Height>%scm</Height><Width>%scm</Width>" % (top, left, h, w)
    x += style or "<Style><Border><Color>#E5E7EB</Color><Style>None</Style></Border><BackgroundColor>White</BackgroundColor></Style>"
    x += "</Chart>"
    return x


# Standard-Kategorie: Geschoss, nach GeschossIndex sortiert
GESCH = ("=Fields!Geschoss.Value", "=Min(Fields!GeschossIndex.Value)", None)
SUMV = "=Sum(Fields!Volumen.Value)"


# ------------------------------------------------------------------ Gauge
def gin(value):
    return "<GaugeInputValue><Value>%s</Value></GaugeInputValue>" % esc(value)


def gval(tag, value):
    return "<%s><Value>%s</Value></%s>" % (tag, esc(value), tag)


def srange(name, start, end, color, w="8", dist="0", placement="Inside", sw=None, ew=None):
    return ('<ScaleRange Name="%s"><Style><BackgroundColor>%s</BackgroundColor></Style>%s%s<StartWidth>%s</StartWidth><EndWidth>%s</EndWidth>'
            "<DistanceFromScale>%s</DistanceFromScale><Placement>%s</Placement></ScaleRange>"
            % (name, color, gval("StartValue", start), gval("EndValue", end), sw or w, ew or w, dist, placement))


def radial(name, value, vmin, vmax, ranges="", start=None, sweep=None, needle="Tapered", ptype="Needle", color="#111827",
           top=0, left=0, h=100, w=100, pivot=(50, 50), radius=38, interval=None, labels=True, frame="Default",
           fstyle_="None", fill="White", scale_w="3", cap=True, label_size="8pt", frame_bg=None, pwidth="14", dist="0", ticks=True,
           barstart="ScaleStart", extra_scale="", aspect="Fixed"):
    sc = '<RadialScale Name="%s_Scale">' % name
    sc += "<Style><Border><Color>#9CA3AF</Color></Border></Style>" if False else ""
    sc += '<GaugePointers><RadialPointer Name="%s_Ptr">%s<Type>%s</Type>' % (name, gin(value), ptype)
    sc += "<Style><BackgroundColor>%s</BackgroundColor></Style>" % color
    if ptype == "Needle":
        sc += "<NeedleStyle>%s</NeedleStyle>" % needle
        if cap:
            sc += "<PointerCap><Style><BackgroundColor>%s</BackgroundColor></Style><CapStyle>Rounded</CapStyle><Width>20</Width></PointerCap>" % color
    sc += "<Width>%s</Width><DistanceFromScale>%s</DistanceFromScale>" % (pwidth, dist)
    if ptype == "Bar":
        sc += "<BarStart>%s</BarStart>" % barstart
    sc += "</RadialPointer></GaugePointers>"
    if ranges:
        sc += "<ScaleRanges>%s</ScaleRanges>" % ranges
    sc += "<ScaleLabels>%s<Interval>%s</Interval><Hidden>%s</Hidden></ScaleLabels>" % (
        fstyle(label_size, "#374151"), interval or "NaN", "false" if labels else "true")
    sc += ("<GaugeMajorTickMarks><Style>%s</Style><Length>8</Length><Width>1</Width><Hidden>%s</Hidden></GaugeMajorTickMarks>"
           % (border("#6B7280", "Solid", "0.5pt").replace("<Border>", "<Border>"), "false" if ticks else "true"))
    sc += "<GaugeMinorTickMarks><Hidden>true</Hidden></GaugeMinorTickMarks>"
    sc += gval("MaximumValue", vmax) + gval("MinimumValue", vmin)
    if interval:
        sc += "<Interval>%s</Interval>" % interval
    sc += "<Width>%s</Width>" % scale_w
    sc += "<Radius>%s</Radius>" % radius
    if start is not None:
        sc += "<StartAngle>%s</StartAngle>" % start
    if sweep is not None:
        sc += "<SweepAngle>%s</SweepAngle>" % sweep
    sc += extra_scale + "</RadialScale>"
    bf = ("<BackFrame><Style><BackgroundColor>%s</BackgroundColor>%s</Style><FrameStyle>%s</FrameStyle><FrameShape>%s</FrameShape>"
          "<FrameBackground><Style><BackgroundColor>%s</BackgroundColor></Style></FrameBackground><GlassEffect>None</GlassEffect></BackFrame>"
          % (fill, border("#D1D5DB", "Solid", "0.75pt"), fstyle_, frame, frame_bg or fill))
    return ('<RadialGauge Name="%s"><BackFrame/>' % name).replace("<BackFrame/>", bf) + "<GaugeScales>%s</GaugeScales>" % sc + \
        "<PivotX>%s</PivotX><PivotY>%s</PivotY><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (
            pivot[0], pivot[1], top, left, h, w) + "<AspectRatio>%s</AspectRatio>" % ("1" if aspect == "Fixed" else aspect) + "</RadialGauge>"


def linear(name, value, vmin, vmax, ranges="", ptype="Bar", orient="Horizontal", color="#2563EB", top=0, left=0, h=100, w=100,
           pos=50, scale_w="6", interval=None, labels=True, marker_style="Triangle", fill="White", barstart="ScaleStart",
           pwidth="10", extra_ptr="", thermo="", labelsize="8pt", ticks=True, extra_scale="", dist="0", mlen="12", frame="Rectangular",
           second_ptr=""):
    sc = '<LinearScale Name="%s_Scale">' % name
    sc += '<GaugePointers><LinearPointer Name="%s_Ptr">%s<Type>%s</Type>' % (name, gin(value), ptype)
    sc += "<Style><BackgroundColor>%s</BackgroundColor>%s</Style>" % (color, border("#FFFFFF", "None", "0.5pt"))
    sc += "<Placement>Inside</Placement>"
    sc += "<DistanceFromScale>%s</DistanceFromScale>" % dist
    if ptype == "Marker":
        sc += "<MarkerLength>%s</MarkerLength><MarkerStyle>%s</MarkerStyle>" % (mlen, marker_style)
    if ptype == "Bar":
        sc += "<BarStart>%s</BarStart>" % barstart
    sc += "<Width>%s</Width>" % pwidth
    if ptype == "Thermometer":
        sc += thermo
    sc += extra_ptr + "</LinearPointer>%s</GaugePointers>" % second_ptr
    if ranges:
        sc += "<ScaleRanges>%s</ScaleRanges>" % ranges
    sc += "<ScaleLabels>%s<Interval>%s</Interval><Hidden>%s</Hidden></ScaleLabels>" % (
        fstyle(labelsize, "#374151"), interval or "NaN", "false" if labels else "true")
    sc += "<GaugeMajorTickMarks><Style>%s</Style><Length>5</Length><Width>1</Width><Hidden>%s</Hidden></GaugeMajorTickMarks>" % (
        border("#6B7280", "Solid", "0.5pt"), "false" if ticks else "true")
    sc += "<GaugeMinorTickMarks><Hidden>true</Hidden></GaugeMinorTickMarks>"
    sc += gval("MaximumValue", vmax) + gval("MinimumValue", vmin)
    if interval:
        sc += "<Interval>%s</Interval>" % interval
    sc += "<Width>%s</Width><Position>%s</Position>" % (scale_w, pos)
    sc += extra_scale + "</LinearScale>"
    bf = ("<BackFrame><Style><BackgroundColor>%s</BackgroundColor>%s</Style><FrameStyle>None</FrameStyle><FrameShape>%s</FrameShape>"
          "<GlassEffect>None</GlassEffect></BackFrame>" % (fill, border("#D1D5DB", "Solid", "0.75pt"), frame))
    return ('<LinearGauge Name="%s">' % name) + bf + "<GaugeScales>%s</GaugeScales>" % sc + \
        "<Orientation>%s</Orientation><Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width>" % (orient, top, left, h, w) + \
        "</LinearGauge>"


def stateind(name, value, vmin, vmax, states, style="Circle", top=0, left=0, h=100, w=100, transform="None", scale="1"):
    s = '<StateIndicator Name="%s">%s' % (name, gin(value))
    s += "<TransformationType>%s</TransformationType>" % transform
    s += gval("MinimumValue", vmin) + gval("MaximumValue", vmax)
    s += "<IndicatorStyle>%s</IndicatorStyle>" % style
    s += "<IndicatorStates>%s</IndicatorStates>" % "".join(
        '<IndicatorState Name="%s"><Color>%s</Color>%s%s<ScaleFactor>1</ScaleFactor><IndicatorStyle>%s</IndicatorStyle></IndicatorState>'
        % (n, c, gval("StartValue", a), gval("EndValue", b), ist) for (n, a, b, c, ist) in states)
    s += "<ResizeMode>AutoFit</ResizeMode><ScaleFactor>%s</ScaleFactor>" % scale
    s += "<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width></StateIndicator>" % (top, left, h, w)
    return s


def numind(name, value, style="Digital7Segment", top=0, left=0, h=100, w=100, digits="6", decimals="1", color="#1F2937"):
    return ('<NumericIndicator Name="%s">%s<IndicatorStyle>%s</IndicatorStyle><Digits>%s</Digits><DecimalDigits>%s</DecimalDigits>'
            "<DigitColor>%s</DigitColor><DecimalDigitColor>#6B7280</DecimalDigitColor><ShowDecimalPoint>True</ShowDecimalPoint>"
            "%s%s<Top>%s</Top><Left>%s</Left><Height>%s</Height><Width>%s</Width></NumericIndicator>"
            % (name, gin(value), style, digits, decimals, color, gval("MinimumValue", "0"), gval("MaximumValue", "99999"), top, left, h, w))


def gaugelabel(name, text, top, left, h, w, size="14pt", color="#111827", bold=True, align="Center"):
    return ('<GaugeLabel Name="%s"><Style><FontFamily>%s</FontFamily><FontSize>%s</FontSize><FontWeight>%s</FontWeight><Color>%s</Color>'
            "<TextAlign>%s</TextAlign><VerticalAlign>Middle</VerticalAlign></Style><Text>%s</Text><Top>%s</Top><Left>%s</Left><Height>%s</Height>"
            "<Width>%s</Width><ResizeMode>AutoFit</ResizeMode></GaugeLabel>" % (name, FONT, size, "Bold" if bold else "Normal", color, align, esc(text), top, left, h, w))


def gauge(name, top, left, w, h, radials="", linears="", states="", nums="", labels="", dataset=True, bg="White", nrows=None,
          extra="", autolayout="False"):
    x = '<GaugePanel Name="%s">' % name
    if radials:
        x += "<RadialGauges>%s</RadialGauges>" % radials
    if linears:
        x += "<LinearGauges>%s</LinearGauges>" % linears
    if nums:
        x += "<NumericIndicators>%s</NumericIndicators>" % nums
    if states:
        x += "<StateIndicators>%s</StateIndicators>" % states
    if labels:
        x += "<GaugeLabels>%s</GaugeLabels>" % labels
    x += "<AntiAliasing>All</AntiAliasing><TextAntiAliasingQuality>High</TextAntiAliasingQuality><ShadowIntensity>0</ShadowIntensity>"
    x += "<AutoLayout>%s</AutoLayout>" % autolayout
    if dataset:
        x += "<DataSetName>AllplanReport</DataSetName>"
    x += extra
    x += "<Top>%scm</Top><Left>%scm</Left><Height>%scm</Height><Width>%scm</Width>" % (top, left, h, w)
    x += "<Style><Border><Color>#E5E7EB</Color><Style>None</Style></Border><BackgroundColor>%s</BackgroundColor></Style></GaugePanel>" % bg
    return x


# ------------------------------------------------------------------ Tablix
def tablix(name, top, left, cols, header_cells, detail_cells, group_expr=None, sort_expr=None, row_h=0.9, head_h=0.7,
           group_header=None, details=False):
    """cols: Breiten in cm; header_cells/detail_cells: Liste von CellContents-XML.
    Mit group_expr: eine Zeilengruppe, detail_cells = Zeile der Gruppe (Aggregate je Gruppe)."""
    def cell(inner):
        return "<TablixCell><CellContents>%s</CellContents></TablixCell>" % inner
    xml = '<Tablix Name="%s"><TablixBody><TablixColumns>%s</TablixColumns><TablixRows>' % (
        name, "".join("<TablixColumn><Width>%scm</Width></TablixColumn>" % c for c in cols))
    xml += "<TablixRow><Height>%scm</Height><TablixCells>%s</TablixCells></TablixRow>" % (head_h, "".join(cell(c) for c in header_cells))
    xml += "<TablixRow><Height>%scm</Height><TablixCells>%s</TablixCells></TablixRow>" % (row_h, "".join(cell(c) for c in detail_cells))
    xml += "</TablixRows></TablixBody>"
    xml += "<TablixColumnHierarchy><TablixMembers>%s</TablixMembers></TablixColumnHierarchy>" % ("<TablixMember/>" * len(cols))
    if group_expr:
        srt = "<SortExpressions><SortExpression><Value>%s</Value></SortExpression></SortExpressions>" % esc(sort_expr or group_expr)
        xml += ('<TablixRowHierarchy><TablixMembers><TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>'
                '<TablixMember><Group Name="%s_Grp"><GroupExpressions><GroupExpression>%s</GroupExpression></GroupExpressions></Group>%s'
                "</TablixMember></TablixMembers></TablixRowHierarchy>" % (name, esc(group_expr), srt))
    else:
        xml += ('<TablixRowHierarchy><TablixMembers><TablixMember><KeepWithGroup>After</KeepWithGroup></TablixMember>'
                '<TablixMember><Group Name="%s_Details"/></TablixMember></TablixMembers></TablixRowHierarchy>' % name)
    xml += "<DataSetName>AllplanReport</DataSetName>"
    xml += "<Top>%scm</Top><Left>%scm</Left><Height>%scm</Height><Width>%scm</Width><Style/></Tablix>" % (
        top, left, head_h + row_h, sum(cols))
    return xml


def tb(name, text, size="9pt", bold=False, align=None, color="#1F2937", bg=None, border_xml="", valign="Middle"):
    """Textbox fuer Tablix-Zelle (ohne Position)."""
    t = textbox(name, text, 0, 0, 1, 1, size=size, bold=bold, color=color, align=align, valign=valign, bg=bg, border_xml=border_xml)
    return re.sub(r"<Top>.*?</Width>", "", t)
