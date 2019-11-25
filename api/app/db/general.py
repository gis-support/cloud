#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import current_app, request, jsonify
from playhouse.postgres_ext import PostgresqlExtDatabase
from psycopg2.sql import SQL, Identifier, Placeholder
from psycopg2.extensions import AsIs
from functools import wraps, partial
from app.helpers.cloud import Cloud
from app.helpers.layer import Layer
import psycopg2
import jwt
import uuid
import math
import json

database = PostgresqlExtDatabase(
    None,
    register_hstore=False,
    autorollback=True,
    field_types={'geometry': 'geometry'}
)


def user_exists(user):
    cur = current_app._db.execute_sql(
        'SELECT 1 FROM pg_roles WHERE rolname=%s AND rolcanlogin=true', (user,))
    return cur.fetchone() != None


def create_user(user, password):
    current_app._db.execute_sql(SQL("CREATE USER {} WITH ENCRYPTED PASSWORD %s").format(
        Identifier(user)), (password,))
    current_app._db.execute_sql(SQL("GRANT CONNECT ON DATABASE {} TO {};").format(
        Identifier(current_app.config['DBNAME']), Identifier(user)))
    if current_app.config['TESTING']:
        current_app._redis.lpush('user_list', user)


def tile_ul(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return lon_deg, lat_deg


def create_mvt_tile(z, x, y, name):
    xmin, ymin = tile_ul(x, y, z)
    xmax, ymax = tile_ul(x+1, y+1, z)
    cur = current_app._db.cursor()
    query = SQL('''SELECT ST_AsMVT(tile) FROM (SELECT id,
        ST_AsMVTGeom(geometry,ST_Makebox2d(ST_SetSrid(ST_MakePoint(%s,%s),4326),
        ST_SetSrid(ST_MakePoint(%s,%s),4326)),4096,8,true) AS geom FROM {}) AS tile''').format(Identifier(name))
    cur.execute(query, (xmin, ymin, xmax, ymax))
    tile = cur.fetchone()[0]
    return tile.tobytes()


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
            return jsonify({"error": "token required"}), 403
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
