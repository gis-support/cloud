#!/usr/bin/python
# -*- coding: utf-8 -*-
from app.helpers.cloud import Cloud
from psycopg2.sql import SQL, Identifier, Placeholder
import json

PERMISSIONS = {
    "read": "GRANT SELECT ON {} TO {};",
    "write": "GRANT SELECT, UPDATE, INSERT ON {} TO {};",
    "": "REVOKE ALL ON {} FROM {}"
}


class Layer(Cloud):
    def __init__(self, options):
        super().__init__(options)
        # Nowy obiekt
        if options.get('name'):
            self.name = options['name']
            self.lid = self.hash_name(self.name)
        else:
            # Zahaszowane ID warstwy
            self.lid = options['lid']
            # Nazwa warstwy
            self.name = self.unhash_name(self.lid)
        self.validate()

    # Sprawdzenie czy warstwa istnieje + uprawnienia
    def validate(self):
        cursor = self.execute(
            "SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s", (self.name,))
        if cursor.fetchone() == None:
            raise ValueError("layer not exists")
        if self.name not in [l['name'] for l in self.get_layers()]:
            raise PermissionError("access denied")

    # Sprawdzenie czy użytkownik jest właścicielem warstwy
    def check_owner(self):
        cursor = self.execute(
            "SELECT tableowner FROM pg_tables WHERE tablename = %s", (self.name,))
        if cursor.fetchone()[0] != self.user:
            raise PermissionError("access denied, not an owner")

    # Sprawdzenie czy użytkownik ma prawa edycji
    def check_write(self):
        cursor = self.execute(
            "SELECT * FROM information_schema.role_table_grants WHERE grantee = %s", (self.user,))
        if len(cursor.fetchall()) < 2:
            raise PermissionError("access denied, read only permission")

    def grant(self, user, permission):
        self.execute(SQL(PERMISSIONS[""]).format(
            Identifier(self.name), Identifier(user)))
        if permission:
            self.execute(SQL(PERMISSIONS[permission]).format(
                Identifier(self.name), Identifier(user)))

    # Lista kolumn
    def columns(self):
        cursor = self.execute(SQL("""
            SELECT * FROM {} LIMIT 0
        """).format(Identifier(self.name)))
        return [description[0] for description in cursor.description if description[0] not in ['id', 'geometry']]
    # Liczba features

    def count(self):
        cursor = self.execute(SQL("""
            SELECT count(*) FROM {}
        """).format(Identifier(self.name)))
        return cursor.fetchone()[0]
    # Usunięcie warstwy

    def delete(self):
        self.execute(SQL("""
            DROP TABLE {} CASCADE
        """).format(Identifier(self.name)))
    # Wyświetlenie warstwy za pomocą GeoJSONa

    def as_geojson(self):
        cursor = self.execute(SQL("""
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )
            FROM (SELECT * from {}) as t;
        """).format(Identifier(self.name)))
        return cursor.fetchone()[0]
    # Wyświetlenie pojedynczego feature

    def as_geojson_by_fid(self, fid):
        cursor = self.execute(SQL("""
            SELECT ST_AsGeoJSON(t.*)
            FROM (SELECT * from {} WHERE id=%s) AS t;
        """).format(Identifier(self.name)), (fid,))
        return json.loads(cursor.fetchone()[0])
    # Dodanie nowego feature

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
    # Edycja feature

    def edit_feature(self, fid, columns, values):
        query_string = SQL("UPDATE {} SET {} WHERE id=%s").format(
            Identifier(self.name),
            SQL(', ').join(
                map(lambda c: SQL("{} = %s").format(Identifier(c)), columns))
        )
        self.execute(query_string, *[values + [fid]])
    # Usunięcie feature

    def delete_feature(self, fid):
        query_string = SQL("DELETE FROM {} WHERE id=%s;").format(
            Identifier(self.name))
        self.execute(query_string, (fid,))
