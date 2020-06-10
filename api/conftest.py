#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
from flask import request

from app.create import create_app
from psycopg2.sql import SQL, Identifier

SYSTEM_TABLES = [
    'geography_columns',
    'geometry_columns',
    'spatial_ref_sys',
    'raster_columns',
    'raster_overviews',
    'layer_styles',
    "tag",
    "layer_tag"
]


@pytest.fixture()
def app():
    app = create_app('testing')
    yield app
    # Teardown
    users_to_delete = app._redis.lrange('user_list', 0, -1)
    for user in users_to_delete:
        try:
            app._db.execute_sql(SQL("REASSIGN OWNED BY {user} TO postgres;DROP OWNED BY {user};DROP USER {user};").format(
                user=Identifier(user.decode('utf-8'))))
        except:
            pass
    groups_to_delete = app._redis.lrange('group_list', 0, -1)
    for group in groups_to_delete:
        try:
            app._db.execute_sql(SQL("DROP GROUP IF EXISTS {user};").format(
                user=Identifier(group.decode('utf-8'))))
        except:
            pass
    app._db.execute_sql("TRUNCATE layer_styles RESTART IDENTITY;")
    app._db.execute_sql("TRUNCATE layer_tag RESTART IDENTITY;")
    app._db.execute_sql("TRUNCATE tag RESTART IDENTITY CASCADE;")
    app._redis.delete('user_list')
    cur = app._db.execute_sql(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables_to_delete = [row[0]
                        for row in cur.fetchall() if row[0] not in SYSTEM_TABLES]
    for table in tables_to_delete:
        app._db.execute_sql('DROP TABLE "{}" cascade'.format(table))
    cur.close()

@pytest.fixture
def app_request_context(client):
    with client.application.test_request_context():
        request.user = "test"
        yield