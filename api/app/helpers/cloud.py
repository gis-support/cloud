#!/usr/bin/python
# -*- coding: utf-8 -*-

from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs
from app.helpers.style import create_qml


DB_RESTRICTED_USERS = (
    'docker',  # Superadmin from docker-compose.yml
    'replicator',  # Docker Kartoza user for slave
    'postgres'  # Superadmin default
)

DB_RESTRICTED_TABLES = (
    'spatial_ref_sys',  # Postgis dependency
    'layer_styles'  # QGIS styles source
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
            SELECT t1.rolname, t2.table_name, t2.privilege_type
            FROM pg_roles AS t1
            LEFT JOIN information_schema.role_table_grants as t2
            ON t1.rolname = t2.grantee
            WHERE t1.rolcanlogin = true
            AND t1.rolname NOT IN %s
            AND (t2.privilege_type IN %s OR t2.privilege_type IS NULL)
            AND (t2.grantor = %s OR t2.grantor IS NULL)
            AND (t2.table_name NOT IN %s OR t2.table_name IS NULL)
        """, (DB_RESTRICTED_USERS, ('SELECT', 'INSERT'), self.user, DB_RESTRICTED_TABLES))
        users = {}
        layers = []
        for row in cursor.fetchall():
            if not users.get(row[0]):
                users[row[0]] = {}
            if row[1] == None:
                continue
            if row[1] not in layers:
                layers.append(row[1])
            if not users[row[0]].get(row[1]):
                users[row[0]][row[1]] = 'read'
            else:
                users[row[0]][row[1]] = 'write'
        permissions = []
        for layer in layers:
            perm = {
                "name": layer,
                "id": self.hash_name(layer),
                "users": {}
            }
            for user in users:
                perm['users'][user] = users[user].get(layer, "")
            permissions.append(perm)
        return {
            'permissions': permissions,
            'users': list(users.keys())
        }

    # Get user groups
    def get_groups(self):
        groups = []
        cursor = self.execute(
            """SELECT groname FROM pg_group WHERE groname NOT LIKE 'pg_%%';""")
        for row in cursor.fetchall():
            groups.append(row[0])
        return groups

    def get_user_group(self):
        cursor = self.execute("""
            SELECT rolname FROM pg_user
            JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
            JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
            WHERE
            pg_user.usename = %s;
        """, (self.user,))
        return cursor.fetchone()[0]

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
    def create_layer(self, name, fields, geom_type):
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
        self.execute("""
            INSERT INTO layer_styles (
                f_table_catalog,
                f_table_schema,
                f_table_name,
                f_geometry_column,
                stylename,
                styleqml,
                useasdefault
            )
            VALUES (
                'cloud',
                'public',
                %s,
                'geometry',
                'default',
                %s,
                True
            );
        """, (name, create_qml(geom_type)))
