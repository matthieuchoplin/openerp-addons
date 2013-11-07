<?xml version="1.0"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:x="urn:schemas-microsoft-com:office:excel"
xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
xmlns:html="http://www.w3.org/TR/REC-html40">
<DocumentProperties xmlns="urn:schemas-microsoft-com:office:office">
<Title>${title}</Title>
</DocumentProperties>
<Styles>
<Style ss:ID="ssH">
<Alignment ss:Horizontal="Center" ss:Vertical="Center" ss:WrapText="1"/>
<Font ss:Bold="1" />
<Borders>
  <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" />
</Borders>
</Style>
<Style ss:ID="ssBorder">
<Alignment ss:Vertical="Center" ss:WrapText="1"/>
<Borders>
  <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" />
  <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" />
</Borders>
</Style>
<Style ss:ID="sShortDate">
    <NumberFormat ss:Format="Short Date"/>
    <Alignment ss:Vertical="Center" ss:WrapText="1"/>
    <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" />
    </Borders>
</Style>
<Style ss:ID="sDate">
    <NumberFormat ss:Format="General Date"/>
    <Alignment ss:Vertical="Center" ss:WrapText="1"/>
    <Borders>
    <Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Left" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1" />
    <Border ss:Position="Top" ss:LineStyle="Continuous" ss:Weight="1" />
    </Borders>
</Style>
</Styles>
<Worksheet ss:Name="Sheet">
<Table ss:ExpandedColumnCount="${len(headers)}" ss:ExpandedRowCount="${len(objects)+1}" x:FullColumns="1"
x:FullRows="1">
% for x in headers:
<Column ss:AutoFitWidth="1" ss:Width="70" />
% endfor
<Row>
% for header in headers:
<Cell ss:StyleID="ssH"><Data ss:Type="String">${header[0]}</Data></Cell>
% endfor
</Row>
% for row in objects:
<Row>
  % for index, h in enumerate(headers):
    <% result=row[index] %>
    % if h[1] == 'date' and result and result != 'False':
        <Cell ss:StyleID="sShortDate">
            <Data ss:Type="DateTime">${result|n}T00:00:00.000</Data>
        </Cell>
    % elif h[1] == 'datetime' and result and result != 'False':
        <Cell ss:StyleID="sDate">
            <Data ss:Type="DateTime">${("%s.000"%result.replace(' ','T'))|n}</Data>
        </Cell>
    % else:
        <Cell ss:StyleID="ssBorder">
            % if h[1] == 'bool':
                <Data ss:Type="Boolean">${result=='True' and '1' or '0'}</Data>
            % elif h[1] in ('number', 'int', 'float'):
                % if not isinstance(result, bool): 
                    <Data ss:Type="Number">${result}</Data>
                % else:
                    <Data ss:Type="String"></Data>
                % endif
            % else:
                <Data ss:Type="String">${(result or "")|x}</Data>
            % endif
        </Cell>
    % endif
  % endfor
</Row>
% endfor
</Table>
<AutoFilter x:Range="R1C1:R1C${len(headers)}" xmlns="urn:schemas-microsoft-com:office:excel">
</AutoFilter>
</Worksheet>
</Workbook>
