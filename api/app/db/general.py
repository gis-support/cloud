#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import current_app, request, jsonify
from flask.cli import with_appcontext
from playhouse.postgres_ext import PostgresqlExtDatabase
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs
from peewee import Model
from functools import wraps, partial
from app.helpers.cloud import Cloud
from app.helpers.layer import Layer
from shapely.geometry import shape
from os import path as op
from io import BytesIO
import psycopg2
import jwt
import uuid
import math
import json
import click

database = PostgresqlExtDatabase(
    None,
    register_hstore=False,
    autorollback=True,
    field_types={'geometry': 'geometry'}
)


class BaseModel(Model):
    class Meta:
        database = database


def user_exists(user):
    cur = current_app._db.execute_sql(
        'SELECT 1 FROM pg_roles WHERE rolname=%s AND rolcanlogin=true', (user,))
    return cur.fetchone() != None


def create_user(user, password):
    current_app._db.execute_sql(SQL("CREATE USER {} WITH ENCRYPTED PASSWORD %s").format(
        Identifier(user)), (password,))
    current_app._db.execute_sql(SQL("GRANT CONNECT ON DATABASE {} TO {};").format(
        Identifier(current_app.config['DBNAME']), Identifier(user)))
    current_app._db.execute_sql(
        SQL("""ALTER GROUP {} ADD USER {}""").format(Identifier(current_app.config['DEFAULT_GROUP']), Identifier(user)))
    if current_app.config['TESTING']:
        current_app._redis.lpush('user_list', user)


def authenticate_user(user, password):
    try:
        con = psycopg2.connect(
            database=current_app.config['DBNAME'],
            user=user,
            password=password,
            host=current_app.config['DBHOST'],
            port=current_app.config['DBPORT']
        )
        con.close()
        return True
    except Exception as e:
        return False


def create_token(user):
    random_uuid = str(uuid.uuid4())
    token = jwt.encode({"user": user, "uuid": random_uuid},
                       current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    current_app._redis.set(random_uuid, user, ex=600)
    return token


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        token = request.args.get('token')
        # W przypadku braku tokena
        if not token:
            if 'Authorization' not in request.headers:
                return jsonify({"error": "token required"}), 403
            token = request.headers['Authorization']
        # W przypadku niepoprawnego tokena
        try:
            user_data = jwt.decode(
                token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({"error": "invalid token"}), 403
        random_uuid = user_data.get('uuid')
        user = user_data.get('user')
        # W przypadku złamania soli i podmianki czegokolwiek w JWT
        if not user or not random_uuid:
            return jsonify({"error": "invalid token"}), 403
        user_redis = current_app._redis.get(random_uuid)
        if not user_redis or user_redis.decode('utf-8') != user:
            return jsonify({"error": "invalid token"}), 403
        # Wydłużenie tokena o kolejne 10min
        current_app._redis.set(random_uuid, user, ex=600)
        request.user = user
        return f(*args, **kws)
    return decorated_function


def cloud_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        cloud = Cloud({"app": current_app, "user": request.user})
        return f(cloud, *args, **kws)
    return decorated_function


def layer_decorator(func=None, *, permission=None):
    if func is None:
        return partial(layer_decorator, permission=permission)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            layer = Layer(
                {"app": current_app, "user": request.user, "lid": kwargs.get('lid')})
            if permission == "owner":
                layer.check_owner()
            if permission == 'write':
                layer.check_write()
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except PermissionError as e:
            return jsonify({"error": str(e)}), 403
        kwargs['layer'] = layer
        return func(*args, **kwargs)
    return wrapper


@click.command(short_help='Fill db with default values.')
@with_appcontext
def fill_data():
    if not user_exists('cli'):
        create_user('cli', 'cli')
    cloud = Cloud({"app": current_app, "user": "cli"})
    name = "elo layr"
    geom_type = "MULTIPOLYGON"
    fields = [
        {'name': 'geometry', 'type': 'geometry(MULTIPOLYGON, 4326)'},
        {'name': 'test', 'type': 'character varying'}
    ]
    cloud.create_layer(name, fields, geom_type)
    layer = Layer({"app": current_app, "user": "cli", "name": "polygon layer"})
    TEST_DATA_PATH = op.join(op.dirname(op.abspath(
        __file__)), '..', 'tests', 'layers', 'correct_feature.json')
    data = json.loads(open(TEST_DATA_PATH).read())
    geometry = 'SRID=4326;{}'.format(shape(data['geometry']).wkt)
    columns = []
    values = []
    for k, v in data['properties'].items():
        if k in layer.columns():
            columns.append(k)
            values.append(v)
    layer.add_feature(columns, values)
