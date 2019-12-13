DEFAULT_POINT_STYLE = """
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" minScale="1e+8" simplifyDrawingTol="1" styleCategories="AllStyleCategories" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" maxScale="0" simplifyDrawingHints="1" simplifyAlgorithm="0" version="cloud" simplifyLocal="1" simplifyMaxScale="1">
 <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0" type="singleSymbol">
  <symbols>
   <symbol clip_to_extent="1" alpha="1" type="marker" name="0" force_rhr="0">
    <layer locked="0" enabled="1" class="SimpleMarker" pass="0">
     <prop v="{}" k="color"/>
     <prop v="{}" k="outline_color"/>
     <prop v="{}" k="outline_width"/>
     <prop v="Pixel" k="outline_width_unit"/>
    </layer>
   </symbol>
  </symbols>
 </renderer-v2>
</qgis>
"""

DEFAULT_LINESTRING_STYLE = """
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" minScale="1e+8" simplifyDrawingTol="1" styleCategories="AllStyleCategories" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" maxScale="0" simplifyDrawingHints="1" simplifyAlgorithm="0" version="cloud" simplifyLocal="1" simplifyMaxScale="1">
 <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0" type="singleSymbol">
  <symbols>
   <symbol clip_to_extent="1" alpha="1" type="line" name="0" force_rhr="0">
    <layer locked="0" enabled="1" class="SimpleLine" pass="0">
     <prop v="{}" k="line_color"/>
     <prop v="{}" k="line_width"/>
     <prop v="Pixel" k="line_width_unit"/>
    </layer>
   </symbol>
  </symbols>
 </renderer-v2>
</qgis>
"""

DEFAULT_POLYGON_STYLE = """
<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" minScale="1e+8" simplifyDrawingTol="1" styleCategories="AllStyleCategories" labelsEnabled="0" hasScaleBasedVisibilityFlag="0" maxScale="0" simplifyDrawingHints="1" simplifyAlgorithm="0" version="cloud" simplifyLocal="1" simplifyMaxScale="1">
 <renderer-v2 symbollevels="0" forceraster="0" enableorderby="0" type="singleSymbol">
  <symbols>
   <symbol force_rhr="0" name="0" alpha="1" clip_to_extent="1" type="fill">
    <layer locked="0" pass="0" class="SimpleFill" enabled="1">
     <prop v="{}" k="color"/>
     <prop v="{}" k="outline_color"/>
     <prop v="{}" k="outline_width"/>
     <prop v="Pixel" k="outline_width_unit"/>
    </layer>
   </symbol>
  </symbols>
 </renderer-v2>
</qgis>
"""

QML_TO_OL = {
    "marker": {
        "color": "fill-color",
        "outline_color": "stroke-color",
        "outline_width": "stroke-width"
    },
    "line": {
        "line_color": "stroke-color",
        "line_width": "stroke-width"
    },
    "fill": {
        "color": "fill-color",
        "outline_color": "stroke-color",
        "outline_width": "stroke-width"
    }
}


def create_qml(geom_type, style={}):
    fill_color = style.get('fill-color', '255,255,255,0.4')
    stroke_color = style.get('stroke-color', '51,153,204,255')
    stroke_width = style.get('stroke-width', '2')

    if 'point' in geom_type.lower():
        return DEFAULT_POINT_STYLE.format(fill_color, stroke_color, stroke_width)
    elif 'line' in geom_type.lower():
        return DEFAULT_LINESTRING_STYLE.format(stroke_color, stroke_width)
    else:
        return DEFAULT_POLYGON_STYLE.format(fill_color, stroke_color, stroke_width)
