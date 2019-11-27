#!/usr/bin/python
# -*- coding: utf-8 -*-
from app.helpers.cloud import Cloud
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs
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

TYPES = (
    'character varying',
    'real',
    'integer',
    'timestamp without time zone'
)


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

    # Layer columns
    def settings(self):
        cursor = self.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s AND column_name != 'geometry'", (self.name,))
        settings = {
            "id": self.lid,
            "name": self.name,
            "columns": {}
        }
        for row in cursor.fetchall():
            settings['columns'][row[0]] = row[1]
        return settings

    # Add column to layer
    def add_column(self, column_name, column_type):
        if self.column_exists(column_name):
            raise ValueError("column exists")
        if column_type not in TYPES:
            raise ValueError("invalid column type")
        self.execute(
            SQL("ALTER TABLE {} ADD COLUMN {} %s").format(Identifier(self.name), Identifier(column_name)), (AsIs(column_type),))

    # Remove layer column
    def remove_column(self, column_name):
        if not self.column_exists(column_name):
            raise ValueError("column not exists")
        self.execute(
            SQL("ALTER TABLE {} DROP COLUMN {}").format(Identifier(self.name), Identifier(column_name)))

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
    def columns(self):
        cursor = self.execute(SQL("""
            SELECT * FROM {} LIMIT 0
        """).format(Identifier(self.name)))
        return [description[0] for description in cursor.description if description[0] not in RESTRICTED_COLUMNS]

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

    # Convert layer to GeoJSON
    def as_geojson(self):
        cursor = self.execute(SQL("""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )
            FROM (SELECT * from {}) as t;
        """).format(Identifier(self.name)))
        return cursor.fetchone()[0]

    # Convert feature to GeoJSON
    def as_geojson_by_fid(self, fid):
        cursor = self.execute(SQL("""
            SELECT ST_AsGeoJSON(t.*)
            FROM (SELECT * from {} WHERE id=%s) AS t;
        """).format(Identifier(self.name)), (fid,))
        return json.loads(cursor.fetchone()[0])

    # Add new feature
    def add_feature(self, columns, values):
        query_string = SQL("INSERT INTO {} ({}) values ({})").format(
            Identifier(self.name),
            SQL(', ').join(map(lambda c: Identifier(c), columns)),
            SQL(', ').join(Placeholder() * len(columns))
        )
        self.execute(query_string, *[values])
        cursor = self.execute(
            SQL("SELECT count(*) FROM {}").format(Identifier(self.name)))
        return cursor.fetchone()[0]

    # Edit existing feature
    def edit_feature(self, fid, columns, values):
        query_string = SQL("UPDATE {} SET {} WHERE id=%s").format(
            Identifier(self.name),
            SQL(', ').join(
                map(lambda c: SQL("{} = %s").format(Identifier(c)), columns))
        )
        self.execute(query_string, *[values + [fid]])

    # Delete feature
    def delete_feature(self, fid):
        query_string = SQL("DELETE FROM {} WHERE id=%s;").format(
            Identifier(self.name))
        self.execute(query_string, (fid,))
