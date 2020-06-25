#!/usr/bin/python
# -*- coding: utf-8 -*-
import uuid
from typing import Iterable, Callable, List, Any

from app.blueprints.layers.dicts.dict import Dict
from app.blueprints.layers.utils import ATTACHMENTS_COLUMN_NAME
from app.db import enumerators
from app.helpers.cloud import Cloud
from app.helpers.style import QML_TO_OL, LayerStyle, generate_categories
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs
from xml.dom import minidom
from datetime import datetime
from dateutil.parser import parse
import dateutil
import json

PERMISSIONS = {
    "read": "GRANT SELECT ON {} TO {};",
    "write": "GRANT SELECT, UPDATE, INSERT ON {} TO {};",
    "": "REVOKE ALL ON {} FROM {}"
}

RESTRICTED_COLUMNS = (
    "id",
    "geometry"
)

TYPES = {
    'character varying': str,
    'real': (int, float),
    'integer': int,
    'timestamp without time zone': (int, float, datetime),
    "dict": str
}


class Layer(Cloud):
    def __init__(self, options):
        super().__init__(options)
        if options.get('name'):
            # New object
            self.name = options['name']
            self.lid = self.hash_name(self.name)
        else:
            # Existing object
            self.lid = options['lid']
            self.name = self.unhash_name(self.lid)
        self.validate()

    # Check existence and permissions
    def validate(self):
        cursor = self.execute(
            "SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s", (self.name,))
        if cursor.fetchone() == None:
            raise ValueError("layer not exists")
        if self.name not in [l['name'] for l in self.get_layers()]:
            raise PermissionError("access denied")

    # Check ownerhsip
    def check_owner(self):
        cursor = self.execute(
            "SELECT tableowner FROM pg_tables WHERE tablename = %s", (self.name,))
        if cursor.fetchone()[0] != self.user:
            raise PermissionError("access denied, not an owner")

    # Check write permission
    def check_write(self):
        cursor = self.execute(
            "SELECT * FROM information_schema.role_table_grants WHERE grantee = %s", (self.user,))
        if len(cursor.fetchall()) < 2:
            raise PermissionError("access denied, read only permission")

    def geom_type(self):
        cursor = self.execute(SQL("""
            SELECT GeometryType(geometry) FROM {} LIMIT 1
        """).format(Identifier(self.name)))
        geom = cursor.fetchone()[0]
        if 'point' in geom.lower():
            geom = 'point'
        elif 'line' in geom.lower():
            geom = 'line'
        else:
            geom = 'polygon'
        return geom

    def bounding_box(self):
        cursor = self.execute(SQL("""
            SELECT ST_AsGeoJSON(ST_Extent(geometry)) FROM {};
        """).format(Identifier(self.name)))
        return json.loads(cursor.fetchone()[0])

    def set_style(self, data):
        # TODO: self.syncQML()
        style = LayerStyle(data, self.geom_type(), self.columns()).style
        self.execute("""
            UPDATE system.layer_styles SET stylejson=%s WHERE f_table_name = %s
        """, (json.dumps(style), self.name,))
        return style

    def syncQML(self):
        return None

    def get_style(self):
        cursor = self.execute("""
            SELECT stylejson FROM system.layer_styles WHERE f_table_name = %s
        """, (self.name,))
        return cursor.fetchone()[0]

    # Change layer name
    def change_name(self, layer_name, callbacks: Iterable[Callable[[str, str], None]] = None):
        callbacks = [] or callbacks
        if self.layer_exists(layer_name):
            raise ValueError("layer exists")
        old_lid = self.lid
        old_name = self.name
        self.name = layer_name
        self.execute(
            SQL("ALTER TABLE {} RENAME TO {}").format(Identifier(old_name), Identifier(self.name)))
        self.execute("""
            UPDATE system.layer_styles SET f_table_name = %s WHERE f_table_name = %s
        """, (self.name, old_name,))
        self.lid = self.hash_name(self.name)
        for callback in callbacks:
            callback(old_lid, self.lid)


    # Layer columns
    def settings(self):
        cursor = self.execute(
            "SELECT t1.column_name, t1.data_type, t1.udt_name, t2.typcategory "
            "FROM information_schema.columns t1 "
            "JOIN pg_catalog.pg_type t2 "
            "ON (t1.udt_name = t2.typname )"
            "WHERE t1.table_name = %s AND t1.column_name != 'geometry'", (self.name,))
        settings = {
            "id": self.lid,
            "name": self.name,
            "geometry_type": self.geom_type(),
            "bbox": self.bounding_box(),
            "columns": {}
        }
        for row in cursor.fetchall():
            name = row[0]
            type_ = row[1]

            if type_ == "USER-DEFINED":
                dict = Dict.get_or_none(column_name=name)
                if dict is not None:
                    type_ = "dict"

            if name == ATTACHMENTS_COLUMN_NAME:
                type_ = "attachments"

            settings['columns'][name] = type_
        return settings

    def categories(self, attr):
        cursor = self.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s;
        """, (self.name, attr,))
        if cursor.fetchone()[0] == None:
            raise ValueError("attribute not exists")
        cursor = self.execute(SQL("""
            SELECT DISTINCT {}
            FROM {} LIMIT 20
        """).format(Identifier(attr), Identifier(self.name)))
        return generate_categories([c[0] for c in cursor.fetchall()], self.geom_type())

    # Add column to layer
    def add_column(self, column_name, column_type):
        if self.column_exists(column_name):
            raise ValueError("column exists")
        if column_type not in list(TYPES.keys()):
            raise ValueError("invalid column type")
        self.execute(
            SQL("ALTER TABLE {} ADD COLUMN {} %s").format(Identifier(self.name), Identifier(column_name)), (AsIs(column_type),))

    def add_dict_column(self, column_name: str, values: List[Any] = None):
        if self.column_exists(column_name):
            raise ValueError("column exists")

        values = [] or values

        with self.db.atomic():
            enumerator_name = f"{column_name}_{uuid.uuid4()}"
            enumerator_name = enumerator_name.replace("-", "_")
            enumerators.create_enumerator(enumerator_name, values)

            sql = SQL("ALTER TABLE {} ADD COLUMN {} {};").format(Identifier(self.name), Identifier(column_name),
                                                                SQL(enumerator_name))

            Dict.create(layer_id=self.lid, column_name=column_name, enumerator_name=enumerator_name)

            self.execute(sql)

    # Remove layer column
    def remove_column(self, column_name):
        if not self.column_exists(column_name):
            raise ValueError("column not exists")

        with self.db.atomic():
            self.execute(
                SQL("ALTER TABLE {} DROP COLUMN {}").format(Identifier(self.name), Identifier(column_name)))

            if (dict_ := Dict.get_or_none(layer_id=self.lid, column_name=column_name)) is not None:
                enumerators.drop_enumerator(dict_.enumerator_name)
                dict_.delete_instance()

    # Check existence of column
    def column_exists(self, column_name):
        if not column_name:
            raise ValueError("column_name required")
        if column_name in RESTRICTED_COLUMNS:
            raise ValueError("column restricted")
        return column_name in self.columns()

    # Grant user with permission
    def grant(self, user, permission):
        self.execute(SQL(PERMISSIONS[""]).format(
            Identifier(self.name), Identifier(user)))
        if permission:
            self.execute(SQL(PERMISSIONS[permission]).format(
                Identifier(self.name), Identifier(user)))

    # Column lists
    def columns(self, with_types=False):
        cursor = self.execute(SQL("""
            SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s AND column_name NOT IN %s
        """), (self.name, RESTRICTED_COLUMNS,))
        if with_types:
            names = {}
            for c in cursor.fetchall():
                name = c[0]
                type_ = c[1]
                if type_ == "USER-DEFINED":
                    if Dict.select().where(Dict.layer_id == self.lid, Dict.column_name == name).exists():
                        type_ = "dict"

                names[name] = type_
            return names
        return [c[0] for c in cursor.fetchall()]

    # Count features
    def count(self):
        cursor = self.execute(SQL("""
            SELECT count(*) FROM {}
        """).format(Identifier(self.name)))
        return cursor.fetchone()[0]

    # Delete layer
    def delete(self):
        self.execute(SQL("""
            DROP TABLE {} CASCADE
        """).format(Identifier(self.name)))
        self.execute("""
            DELETE FROM system.layer_styles WHERE f_table_name=%s;
        """, (self.name,))

    # Convert layer to GeoJSON
    def as_geojson(self):
        cursor = self.execute(SQL("""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )
            FROM (SELECT * from {}) as t;
        """).format(Identifier(self.name)))
        feature_collection = cursor.fetchone()[0]
        if not feature_collection['features']:
            feature_collection['features'] = []
        return feature_collection

    # Convert feature to GeoJSON
    def as_geojson_by_fid(self, fid):
        cursor = self.execute(SQL("""
            SELECT ST_AsGeoJSON(t.*)
            FROM (SELECT * from {} WHERE id=%s) AS t;
        """).format(Identifier(self.name)), (fid,))
        feature = cursor.fetchone()
        if not feature:
            raise ValueError("feature not exists")
        return json.loads(feature[0])

    # Add new feature
    def add_feature(self, columns, values, columns_with_types):
        # Validation
        error = False
        for i in range(1, len(columns)):
            value = values[i]
            column_name = columns[i]

            if isinstance(values[i], type(None)):
                continue

            if columns_with_types[column_name] == "dict":
                dict_ = Dict.get(layer_id=self.lid, column_name=column_name)
                allowed_values = dict_.get_values()
                if value not in allowed_values:
                    error = f"value '{value}' is not allowed for dict-column '{column_name}'. allowed values: '{allowed_values}'"

            elif not isinstance(value, TYPES[columns_with_types[column_name]]):
                error = f"value '{values[i]}' invalid type of column '{column_name}' ({columns_with_types[column_name]})"
                break

            elif columns_with_types[column_name] == 'timestamp without time zone':
                values[i] = datetime.fromtimestamp(value)

        if error:
            raise ValueError(error)
        query_string = SQL("INSERT INTO {} ({}) values ({})  RETURNING id;").format(
            Identifier(self.name),
            SQL(', ').join(map(lambda c: Identifier(c), columns)),
            SQL(', ').join(Placeholder() * len(columns))
        )
        cursor = self.execute(query_string, *[values])
        return self.as_geojson_by_fid(cursor.fetchone()[0])

    # Edit existing feature

    def edit_feature(self, fid, columns, values, columns_with_types):
        # Validation
        error = False
        for i in range(1, len(columns)):
            value = values[i]
            column_name = columns[i]

            if isinstance(value, type(None)):
                continue

            if columns_with_types[column_name] == "dict":
                dict_ = Dict.get(layer_id=self.lid, column_name=column_name)
                allowed_values = dict_.get_values()
                if value not in allowed_values:
                    error = f"value '{value}' is not allowed for dict-column '{column_name}'. allowed values: '{allowed_values}'"

            elif not isinstance(value, TYPES[columns_with_types[column_name]]):
                error = f"value '{value}' invalid type of column '{column_name}' ({columns_with_types[column_name]})"
                break

            elif columns_with_types[column_name] == 'timestamp without time zone':
                values[i] = datetime.fromtimestamp(value)

        if error:
            raise ValueError(error)

        query_string = SQL("UPDATE {} SET {} WHERE id=%s").format(
            Identifier(self.name),
            SQL(', ').join(
                map(lambda c: SQL("{} = %s").format(Identifier(c)), columns))
        )
        self.execute(query_string, *[values + [fid]])

        return self.as_geojson_by_fid(fid)

    # Delete feature
    def delete_feature(self, fid):
        query_string = SQL("DELETE FROM {} WHERE id=%s;").format(
            Identifier(self.name))
        self.execute(query_string, (fid,))

    # Export fo GeoJSON file
    def export_geojson(self, filter_ids=None):
        if not filter_ids:
            query = """
                SELECT json_build_object(
                    'type', 'FeatureCollection',
                    'features', json_agg(ST_AsGeoJSON(t.*)::json)
                )
                FROM (SELECT * from {}) as t;
            """
            cursor = self.execute(SQL(query).format(Identifier(self.name)))
        else:
            query = """
                SELECT json_build_object(
                    'type', 'FeatureCollection',
                    'features', json_agg(ST_AsGeoJSON(t.*)::json)
                )
                FROM (SELECT * from {} WHERE id = ANY (%s) ) as t;
            """
            cursor = self.execute(SQL(query).format(
                Identifier(self.name)), (filter_ids,))
        feature_collection = cursor.fetchone()[0]
        if not feature_collection['features']:
            feature_collection['features'] = []
        return feature_collection

    def get_distances(self, fid, buffer=0):
        result = {
            'pn': [],
            'pk': []
        }
        cursor = self.execute(SQL("""
            SELECT pn, pk FROM settings
        """))
        names = cursor.fetchone()
        if not names:
            raise ValueError("empty analysis settings settings")
        try:
            pn_layer_name = self.unhash_name(names[0])
        except ValueError:
            raise ValueError("invalid pn layer in settings")
        try:
            pk_layer_name = self.unhash_name(names[1])
        except ValueError:
            raise ValueError("invalid pk layer in settings")
        # Parki narodowe
        pn_cursor = self.execute(SQL("""
            SELECT b.nazwa, ST_Distance(ST_Transform(a.geometry, 2180), ST_Transform(b.geometry, 2180))
            FROM (SELECT geometry FROM {} WHERE id=%s) a, {} b
            WHERE ST_DWithin(
                ST_Transform(a.geometry, 2180),
                ST_Transform(b.geometry, 2180),
                %s
            )
            ORDER BY 1
        """).format(Identifier(self.name), Identifier(pn_layer_name)), (fid, buffer,))
        for row in pn_cursor.fetchall():
            result['pn'].append({
                'name': row[0],
                'distance': row[1]
            })
        # Parki krajobrazowe
        pk_cursor = self.execute(SQL("""
            SELECT b.nazwa, ST_Distance(ST_Transform(a.geometry, 2180), ST_Transform(b.geometry, 2180))
            FROM (SELECT geometry FROM {} WHERE id=%s) a, {} b
            WHERE ST_DWithin(
                ST_Transform(a.geometry, 2180),
                ST_Transform(b.geometry, 2180),
                %s
            )
            ORDER BY 1
        """).format(Identifier(self.name), Identifier(pk_layer_name)), (fid, buffer,))
        for row in pk_cursor.fetchall():
            result['pk'].append({
                'name': row[0],
                'distance': row[1]
            })
        return result

