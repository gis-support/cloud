from copy import copy
from random import randint

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
    stroke_color = style.get('stroke-color', '51,153,204,1')
    stroke_width = style.get('stroke-width', '2')

    if 'point' in geom_type.lower():
        return DEFAULT_POINT_STYLE.format(fill_color, stroke_color, stroke_width)
    elif 'line' in geom_type.lower():
        return DEFAULT_LINESTRING_STYLE.format(stroke_color, stroke_width)
    else:
        return DEFAULT_POLYGON_STYLE.format(fill_color, stroke_color, stroke_width)


def create_stylejson(geom_type):
    if 'point' in geom_type.lower():
        return {
            'labels': [],
            'renderer': 'single',
            'type': 'point',
            'fill-color': '255,255,255,0.4',
            'stroke-color': '51,153,204,1',
            'stroke-width': '1',
            'width': '2'
        }
    elif 'line' in geom_type.lower():
        return {
            'labels': [],
            'renderer': 'single',
            'type': 'line',
            'stroke-color': '51,153,204,1',
            'stroke-width': '2'
        }
    else:
        return {
            'labels': [],
            'renderer': 'single',
            'type': 'polygon',
            'fill-color': '255,255,255,0.4',
            'stroke-color': '51,153,204,1',
            'stroke-width': '2'
        }


def generate_categories(values, geom_type):
    categories = []
    schema = {
        'type': geom_type,
        'fill-color': '255,255,255,0.4',
        'stroke-color': '51,153,204,1',
        'stroke-width': '1',
        'width': '2'
    }
    if geom_type == 'line':
        del schema['fill-color']
        del schema['width']
    elif geom_type == 'polygon':
        del schema['width']
    for value in values:
        schema_copy = copy(schema)
        schema_copy['value'] = value
        schema_copy['stroke-color'] = f'{randint(0,255)},{randint(0,255)},{randint(0,255)},1'
        categories.append(schema_copy)
    return categories


class LayerStyle:

    def __init__(self, data, geom_type, columns):
        self.data = data
        self.geom_type = geom_type
        self.columns = columns
        self.check_existence('renderer', self.data)
        self.check_contains('renderer', self.data['renderer'], [
                            'single', 'categorized'])
        self.renderer = data['renderer']
        self.style = {}
        self.style['renderer'] = self.renderer
        if self.renderer == 'single':
            self.validate_single()
        elif self.renderer == 'categorized':
            self.validate_categorized()
        self.validate_labels()

    def check_existence(self, value, data):
        if value not in data:
            raise ValueError(f"{value} required")

    def check_contains(self, key, value, data):
        if value not in data:
            raise ValueError(f"invalid {key}")

    def check_color(self, color):
        splitted = color.split(',')
        if len(splitted) != 4:
            raise ValueError("invalid number of color arguments")
        for value in splitted[:2]:
            try:
                val = int(value)
            except:
                raise ValueError("invalid value for color")
            if val < 0 or val > 255:
                raise ValueError("invalid value for color")
        try:
            opacity = float(splitted[3])
        except:
            raise ValueError("invalid value for opacity")
        if opacity < 0 or opacity > 1:
            raise ValueError("invalid value for opacity")

    def check_width(self, width):
        try:
            val = int(width)
        except:
            raise ValueError("invalid value for width")
        if val < 1 or val > 10:
            raise ValueError("invalid value for width (1-10)")

    def check_point(self, data):
        self.check_contains('type', data['type'], [
                            'point', 'triangle', 'square'])
        for color in ['fill-color', 'stroke-color']:
            self.check_existence(color, data)
            self.check_color(data[color])
        for width in ['stroke-width', 'width']:
            self.check_existence(width, data)
            self.check_width(data[width])

    def check_line(self, data):
        self.check_contains('type', data['type'], [
                            'line', 'dashed', 'dotted'])
        self.check_existence('stroke-color', data)
        self.check_color(data['stroke-color'])
        self.check_existence('stroke-width', data)
        self.check_width(data['stroke-width'])

    def check_polygon(self, data):
        self.check_contains('type', data['type'], ['polygon'])
        for color in ['fill-color', 'stroke-color']:
            self.check_existence(color, data)
            self.check_color(data[color])
        self.check_existence('stroke-width', data)
        self.check_width(data['stroke-width'])

    def validate_labels(self):
        self.check_existence('labels', self.data)
        if not isinstance(self.data['labels'], list):
            raise ValueError(f"invalid labels type")
        for column in self.data['labels']:
            self.check_contains(
                f'labels - column {column} not exists', column, self.columns)
        self.style['labels'] = self.data['labels']

    def validate_single(self):
        self.check_existence('type', self.data)
        if self.geom_type == 'point':
            self.check_point(self.data)
            self.style['type'] = self.data['type']
            self.style['fill-color'] = self.data['fill-color']
            self.style['stroke-color'] = self.data['stroke-color']
            self.style['stroke-width'] = self.data['stroke-width']
            self.style['width'] = self.data['width']
        elif self.geom_type == 'line':
            self.check_line(self.data)
            self.style['type'] = self.data['type']
            self.style['stroke-color'] = self.data['stroke-color']
            self.style['stroke-width'] = self.data['stroke-width']
        else:
            self.check_polygon(self.data)
            self.style['type'] = self.data['type']
            self.style['fill-color'] = self.data['fill-color']
            self.style['stroke-color'] = self.data['stroke-color']
            self.style['stroke-width'] = self.data['stroke-width']

    def validate_categorized(self):
        self.check_existence('attribute', self.data)
        self.check_existence('categories', self.data)
        if not isinstance(self.data['categories'], list):
            raise ValueError("invalid categories")
        self.style['categories'] = []
        self.style['attribute'] = self.data['attribute']
        for category in self.data['categories']:
            self.check_existence('value', category)
            validated_category = {
                'value': category['value']
            }
            if self.geom_type == 'point':
                self.check_point(category)
                validated_category['type'] = category['type']
                validated_category['fill-color'] = category['fill-color']
                validated_category['stroke-color'] = category['stroke-color']
                validated_category['stroke-width'] = category['stroke-width']
                validated_category['width'] = category['width']
            elif self.geom_type == 'line':
                self.check_line(category)
                validated_category['type'] = category['type']
                validated_category['stroke-color'] = category['stroke-color']
                validated_category['stroke-width'] = category['stroke-width']
            else:
                self.check_polygon(category)
                validated_category['type'] = category['type']
                validated_category['fill-color'] = category['fill-color']
                validated_category['stroke-color'] = category['stroke-color']
                validated_category['stroke-width'] = category['stroke-width']
            self.style['categories'].append(validated_category)
