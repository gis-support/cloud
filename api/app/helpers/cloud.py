#!/usr/bin/python
# -*- coding: utf-8 -*-

from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs


DB_RESTRICTED_USERS = (
    'docker',  # Superadmin from docker-compose.yml
    'replicator',
    'postgres'
)


class Cloud:
    def __init__(self, options):
        # Username
        self.user = options['user']
        # App context
        self.app = options['app']
        # Postgres context
        self.db = self.app._db
        # Hashids context
        self.hashids = self.app._hashids
        # Redis context
        self.redis = self.app._redis

    # Hash layer name
    def hash_name(self, name):
        return self.hashids.encode(int(name.encode('utf-8').hex(), 16))

    # Unhash layer name
    def unhash_name(self, lid):
        try:
            return bytes.fromhex(hex(self.hashids.decode(lid)[0])[2:]).decode('utf-8')
        except:
            raise ValueError("invalid layer id")

    # Execute SQL queries
    def execute(self, *args, **kwargs):
        return self.db.execute_sql(*args, **kwargs)

    # Get permissions for layers
    def get_permissions(self):
        cursor = self.execute("""
            SELECT A.rolname, B.table_name, B.privilege_type
            FROM pg_roles as A
            FULL OUTER JOIN information_schema.role_table_grants as B
            ON B.grantee = A.rolname
            WHERE A.rolname NOT IN %s
            AND A.rolcanlogin = true
            AND (B.privilege_type IN %s OR B.privilege_type IS NULL)
            AND (B.grantor = %s OR B.grantor IS NULL)
        """, (DB_RESTRICTED_USERS, ('SELECT', 'INSERT'), self.user))
        users = {}
        layers = []
        for row in cursor.fetchall():
            if not users.get(row[0]):
                users[row[0]] = {}
            if row[1] == None:
                continue
            layers.append(row[1])
            if not users[row[0]].get(row[1]):
                users[row[0]][row[1]] = 'read'
            else:
                users[row[0]][row[1]] = 'write'
        permissions = []
        for layer in set(layers):
            perm = {
                "name": layer,
                "id": self.hash_name(layer),
                "users": {}
            }
            for user in users:
                if not users[user].get(layer):
                    perm['users'][user] = {}
                else:
                    perm['users'][user] = users[user]
            permissions.append(perm)
        return permissions

    # Layers list
    def get_layers(self):
        cursor = self.execute("""
            SELECT DISTINCT table_name FROM information_schema.role_table_grants WHERE grantee = %s
        """, (self.user,))
        return [{
            "name": row[0],
            "id": self.hash_name(row[0])
        } for row in cursor.fetchall()]

    # Check if layer exists by layer name
    def layer_exists(self, layer):
        cursor = self.execute("""
            SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s
        """, (layer,))
        return cursor.fetchone() != None

    # Create new layer by name and fields
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
