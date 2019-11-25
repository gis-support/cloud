#!/usr/bin/python
# -*- coding: utf-8 -*-

from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs


class Cloud:
    def __init__(self, options):
        # Nazwa użytkownika
        self.user = options['user']
        # Kontekst aplikacji
        self.app = options['app']
        # Kontekst Postgresa
        self.db = self.app._db
        # Kontekst Hashids
        self.hashids = self.app._hashids
        # Kontekst Redisa
        self.redis = self.app._redis
    # Zahaszowanie nazwy warstwy

    def hash_name(self, name):
        return self.hashids.encode(int(name.encode('utf-8').hex(), 16))
    # Odhaszowanie nazwy warstwy

    def unhash_name(self, lid):
        try:
            return bytes.fromhex(hex(self.hashids.decode(lid)[0])[2:]).decode('utf-8')
        except:
            raise ValueError("invalid layer id")
    # Wykonywanie zapytań, zwraca kursor

    def execute(self, *args, **kwargs):
        return self.db.execute_sql(*args, **kwargs)
    # Lista warstw

    def get_layers(self):
        cursor = self.execute("""
            SELECT DISTINCT table_name FROM information_schema.role_table_grants WHERE grantee = %s
        """, (self.user,))
        return [{
            "name": row[0],
            "id": self.hash_name(row[0])
        } for row in cursor.fetchall()]
    # Czy warstwa istnieje

    def layer_exists(self, layer):
        cursor = self.execute("""
            SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s
        """, (layer,))
        return cursor.fetchone() != None
    # Tworzenie warstwy

    def create_layer(self, name, fields):
        columns = ["id"] + [f["name"] for f in fields]
        types = [AsIs(f) for f in ["serial"] + [f["type"] for f in fields]]
        table_string = SQL("""
            CREATE TABLE {} ({})
        """).format(
            Identifier(name),
            SQL(', ').join(map(lambda c: SQL("{} %s").format(Identifier(c)), columns))
        )
        self.execute(table_string, *[types])
        self.execute(SQL("""
            GRANT ALL PRIVILEGES ON TABLE {} TO {};
        """).format(Identifier(name), Identifier(self.user)))
        self.execute(SQL("""
            ALTER TABLE {} OWNER TO {};
        """).format(Identifier(name), Identifier(self.user)))
