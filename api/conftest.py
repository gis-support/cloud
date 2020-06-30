#!/usr/bin/python
# -*- coding: utf-8 -*-
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pytest
from flask import request

from flask import request
from flask.testing import FlaskClient
from playhouse.postgres_ext import PostgresqlExtDatabase

from app.create import create_app
from psycopg2.sql import SQL, Identifier

from app.tests.utils import TEST_DATA_DIR

SYSTEM_TABLES = [
    'geography_columns',
    'geometry_columns',
    'spatial_ref_sys',
    'raster_columns',
    'raster_overviews',
    'layer_styles',
    "tag",
    "layer_tag",
    "dict",
    "attachment",
]

TEST_ENUM_NAME = "test_enum"

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
    app._db.execute_sql("TRUNCATE system.layer_styles RESTART IDENTITY;")
    app._db.execute_sql("TRUNCATE system.layer_tag RESTART IDENTITY;")
    app._db.execute_sql("TRUNCATE system.tag RESTART IDENTITY CASCADE;")
    app._db.execute_sql("TRUNCATE system.dict RESTART IDENTITY CASCADE;")
    app._db.execute_sql(f"TRUNCATE system.attachment_qgis RESTART IDENTITY CASCADE;")
    app._db.execute_sql(f"DROP TYPE IF EXISTS {TEST_ENUM_NAME} CASCADE;")

    app._redis.delete('user_list')
    cur = app._db.execute_sql(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables_to_delete = [row[0]
                        for row in cur.fetchall() if row[0] not in SYSTEM_TABLES]
    for table in tables_to_delete:
        app._db.execute_sql('DROP TABLE "{}" cascade'.format(table))
    cur.close()


@pytest.fixture
def app_request_context(client: FlaskClient):
    with client.application.test_request_context():
        request.user = "test"
        yield


@pytest.fixture
def database(client: FlaskClient) -> PostgresqlExtDatabase:
    return client.application._db


@pytest.fixture
def database_table(client: FlaskClient) -> Tuple[str, str]:

    schema_name = "public"
    table_name = f"test_table_{uuid.uuid4()}"
    table_name = table_name.replace("-", "_")

    app = client.application
    database = app._db

    database.execute_sql(f"CREATE TABLE {schema_name}.{table_name} (id serial);")
    yield schema_name, table_name
    database.execute_sql(f"DROP TABLE {schema_name}.{table_name} CASCADE;")

@pytest.fixture()
def app_request_context(client):
    with client.application.test_request_context():
        request.user = "test"
        yield

@pytest.fixture(autouse=True)
def temp_uploads_path(client, tmpdir_factory):
    temp_dir = tmpdir_factory.mktemp("TEMP_UPLOADS")
    client.application.config["UPLOADS"] = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="session")
def resources_directory() -> Path:
    return Path(TEST_DATA_DIR)