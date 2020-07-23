import json

from peewee import SQL, Field
from shapely import wkb
from shapely.geometry import shape


class GeometryBareField(Field):
    """Pole Peewee odpowiadające typowi `geometry` w Postgresie, bez definiowania SRIDu i typu geometrii"""

    field_type = "geometry"
    db_field = "geometry"

    def db_value(self, value):
        epsg = value.get("crs", {}).get("properties", {}).get("name", "EPSG:4326")
        srid = int(epsg.split(":")[1])
        if type(value) is dict:
            return wkb.dumps(shape(value), hex=True, srid=srid)
        else:
            return value

    def python_value(self, value):
        """
            Konwersja WKB -> GeoJSON z użyciem Shapely
        """
        try:
            return wkb.loads(value, hex=True).__geo_interface__
        except:
            return value

class GeometryField(GeometryBareField):
    """ Pole Peewee odpowiadające typowi `geometry` w Postgresie, ze zdefiniowanym SRIDem i typem geometrii"""

    def __init__(self, geometry_type: str, srid: int, *args, **kwargs):
        self.geometry_type = geometry_type
        self.srid = srid
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        epsg = value.get("crs", {}).get("properties", {}).get("name", f"EPSG:{self.srid}")
        srid = int(epsg.split(":")[1])
        if type(value) is dict:
            return wkb.dumps(shape(value), hex=True, srid=srid)
        else:
            return value

    def ddl_datatype(self, ctx):
        ddl = SQL("{}({}, {})".format(self.field_type, self.geometry_type, self.srid))
        return ddl
