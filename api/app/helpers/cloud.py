#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import wraps

import psycopg2
from flask import current_app, request
from psycopg2.sql import SQL, Identifier
from psycopg2.extensions import AsIs

from app.blueprints.layers.tags.models import LayerTag
from app.helpers.style import create_qml, create_stylejson
import os
import json


ADMIN_GROUP = os.environ.get('ADMIN_GROUP')


DB_RESTRICTED_USERS = (
    'docker',  # Superadmin from docker-compose.yml
    'replicator',  # Docker Kartoza user for slave
    'postgres'  # Superadmin default
)

DB_RESTRICTED_TABLES = (
    'spatial_ref_sys',  # Postgis dependency
    'layer_styles',  # QGIS styles source
    "tag",
    "layer_tag"
)

PERMISSIONS = {
    "read": "GRANT SELECT ON {} TO {};",
    "write": "GRANT SELECT, UPDATE, INSERT ON {} TO {};",
    "": "REVOKE ALL ON {} FROM {}"
}


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
    def execute(self, *args, **kwargs) -> psycopg2.extensions.cursor:
        return self.db.execute_sql(*args, **kwargs)

    def get_users_with_layers(self, grantor=True):
        cursor = self.execute(f"""
            SELECT t1.rolname, t2.table_name, t2.privilege_type
            FROM pg_roles AS t1
            LEFT JOIN information_schema.role_table_grants as t2
            ON t1.rolname = t2.grantee
            WHERE t1.rolcanlogin = true
            AND t1.rolname NOT IN %s
            AND (t2.privilege_type IN %s OR t2.privilege_type IS NULL)
            AND (t2.table_name NOT IN %s OR t2.table_name IS NULL)
            {'--' if grantor else ''}AND (t2.grantor IS NULL OR t2.grantee = %s)
            ORDER BY 2
        """, (DB_RESTRICTED_USERS, ('SELECT', 'INSERT'), DB_RESTRICTED_TABLES, self.user))
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
        return users, layers

    def get_users_with_groups(self):
        cursor = self.execute("""
            SELECT pg_user.usename, rolname FROM pg_user
            JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
            JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
        """)
        return dict([i for i in cursor.fetchall()])

    def get_users_for_group(self, group):
        cursor = self.execute("""
            SELECT pg_user.usename, rolname FROM pg_user
            JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
            JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
            WHERE rolname = %s
        """, (group,))
        return [i[0] for i in cursor.fetchall()]

    # Get permissions for layers
    def get_permissions(self, grantor):
        users, layers = self.get_users_with_layers(grantor=grantor)
        users_wo_admins = [user for user in users if not self.is_user_admin(user)]
        permissions = []
        for layer in layers:
            perm = {
                "name": layer,
                "id": self.hash_name(layer),
                "users": {}
            }
            for user in users:
                if self.is_user_admin(user):
                    perm['users'][user] = 'write'
                else:
                    perm['users'][user] = users[user].get(layer, "")
            permissions.append(perm)
        return {
            'permissions': permissions,
            'users': sorted(users)
        }
    
    def copy_permissions(self, user_from, user_to):
        users, layers = self.get_users_with_layers(grantor=user_from)
        permissions = []
        for layer in layers:
            permission = users[user_from].get(layer, "")
            permissions.append({
                "layer": layer,
                "permission": permission
            })
            self.execute(SQL(PERMISSIONS[""]).format(Identifier(layer), Identifier(user_to)))
            if permission:
                self.execute(SQL(PERMISSIONS[permission]).format(Identifier(layer), Identifier(user_to)))
        return permissions

    def group_exists(self, group):
        cursor = self.execute(SQL("""
            SELECT 1 FROM pg_group WHERE groname NOT LIKE 'pg_%%' AND groname = %s
        """), (group,))
        return cursor.fetchone() != None

    def add_group(self, group):
        if self.group_exists(group):
            raise ValueError("group exists")
        self.execute(SQL("""
            CREATE GROUP {};
        """).format(Identifier(group)))
        if self.app.config['TESTING']:
            self.redis.lpush('group_list', group)

    def delete_group(self, group):
        if not self.group_exists(group):
            raise ValueError("group not exists")
        if group == os.environ['DEFAULT_GROUP']:
            raise ValueError("group restricted")
        for user in self.get_users_for_group(group):
            self.assign_user(user, os.environ['DEFAULT_GROUP'])
        self.execute(SQL("""
            DROP GROUP {};
        """).format(Identifier(group)))

    def assign_user(self, user, group):
        self.execute(SQL("""ALTER GROUP {} ADD USER {}""").format(
            Identifier(group), Identifier(user)))

    def unassign_user(self, user, group):
        self.execute(SQL("""ALTER GROUP {} DROP USER {}""").format(
            Identifier(group), Identifier(user)))

    # Get user groups
    def get_groups(self):
        groups = []
        cursor = self.execute(
            """SELECT groname FROM pg_group WHERE groname NOT LIKE 'pg_%%';""")
        for row in cursor.fetchall():
            groups.append(row[0])
        return groups

    def get_user_group(self, user=None):
        if user is None:
            user = self.user
        cursor = self.execute("""
            SELECT rolname FROM pg_user
            JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
            JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
            WHERE
            pg_user.usename = %s;
        """, (user,))
        groups = [g[0] for g in cursor.fetchall() if g[0] != os.environ['DEFAULT_GROUP']]
        try:         
            return groups[0]
        except IndexError:
            return os.environ['DEFAULT_GROUP']

    def is_user_admin(self, user = None):
        if not user:
            user = self.user
        cursor = self.execute("""
            SELECT rolname FROM pg_user
            JOIN pg_auth_members ON (pg_user.usesysid = pg_auth_members.member)
            JOIN pg_roles ON (pg_roles.oid = pg_auth_members.roleid)
            WHERE
            pg_user.usename = %s and rolname = %s;
        """, (user, ADMIN_GROUP,))

        return bool([group for group in cursor.fetchall()])

    # Layers list
    def get_layers(self):
        if self.is_user_admin():
            cursor = self.execute("""
                SELECT DISTINCT table_name FROM information_schema.role_table_grants
                WHERE grantee = %s
                AND table_name NOT IN %s
            """, (ADMIN_GROUP, DB_RESTRICTED_TABLES))
        else:
            cursor = self.execute("""
                SELECT DISTINCT table_name FROM information_schema.role_table_grants
                WHERE grantee = %s
                AND table_name NOT IN %s
            """, (self.user, DB_RESTRICTED_TABLES))

        tags_by_layer_id = LayerTag.get_tags_by_layer_id()

        result = []
        for row in cursor.fetchall():
            name = row[0]
            id_ = self.hash_name(name)
            tags = tags_by_layer_id.get(id_, [])

            result.append({
                "name": name,
                "id": id_,
                "tags": tags
            })

        return result

    # Check if layer exists by layer name
    def layer_exists(self, layer):
        cursor = self.execute("""
            SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s
        """, (layer,))
        return cursor.fetchone() != None

    # Create new layer by name and fields
    def create_layer(self, name, fields, geom_type):
        id_column_name = "id"

        columns = [id_column_name] + [f["name"] for f in fields]
        types = [AsIs(f) for f in ["serial"] + [f["type"] for f in fields]]
        table_string = SQL("""
            CREATE TABLE {} ({})
        """).format(
            Identifier(name),
            SQL(', ').join(map(lambda c: SQL("{} %s").format(Identifier(c)), columns))
        )
        with self.db.atomic():
            self.execute(table_string, *[types])
            self.execute(SQL("""
                GRANT ALL PRIVILEGES ON TABLE {} TO {};
            """).format(Identifier(name), Identifier(self.user)))
            self.execute(SQL("""
                GRANT ALL PRIVILEGES ON TABLE {} TO {};
            """).format(Identifier(name), Identifier(ADMIN_GROUP)))
            self.execute(SQL("""
                ALTER TABLE {} OWNER TO {};
            """).format(Identifier(name), Identifier(self.user)))
            self.execute("""
                INSERT INTO public.layer_styles (
                    f_table_catalog,
                    f_table_schema,
                    f_table_name,
                    f_geometry_column,
                    stylename,
                    styleqml,
                    stylejson,
                    useasdefault
                )
                VALUES (
                    'cloud',
                    'public',
                    %s,
                    'geometry',
                    'default',
                    %s,
                    %s,
                    True
                );
            """, (name, create_qml(geom_type), json.dumps(create_stylejson(geom_type),)))
            self.execute(SQL("ALTER TABLE {} ADD PRIMARY KEY ({});").format(
                Identifier(name), Identifier(id_column_name)))


def get_cloud():
    return Cloud({"app": current_app, "user": request.user})


def cloud_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        cloud = get_cloud()
        return f(cloud, *args, **kws)
    return decorated_function
