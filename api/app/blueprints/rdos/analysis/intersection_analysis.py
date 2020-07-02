import json
from typing import List

from psycopg2 import sql as psysql

from app.db.database import database
from app.helpers.layer import Layer


def get_intersecting_features_ids(layer: Layer, json_geometry: dict, srid: int) -> List[int]:
    geometry_str = json.dumps(json_geometry)

    sql = psysql.SQL("""SELECT id FROM public.{} WHERE ST_Intersects(geometry, ST_SetSRID(ST_GeomFromGeoJSON({}), {}));""").format(
        psysql.Identifier(layer.name),
        psysql.Literal(geometry_str),
        psysql.Literal(srid)
    )

    cursor = database.execute_sql(sql)

    result = []
    while (row := cursor.fetchone()) is not None:
        result.append(row[0])

    return result
