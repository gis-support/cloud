#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import current_app, request, jsonify
from playhouse.postgres_ext import PostgresqlExtDatabase
from psycopg2.sql import SQL, Identifier, Composed, Literal
from psycopg2.extensions import AsIs
from functools import wraps
import psycopg2
import jwt
import uuid
import math
import json

database = PostgresqlExtDatabase(
    None,
    register_hstore=False,
    autorollback = True,
    field_types={'geometry':'geometry'}
)

def user_exists(user):
    cur = current_app._db.execute_sql('SELECT 1 FROM pg_roles WHERE rolname=%s AND rolcanlogin=true', (user,))
    return cur.fetchone() != None

def create_user(user, password):
    current_app._db.execute_sql(SQL("CREATE USER {} WITH ENCRYPTED PASSWORD %s").format(Identifier(user)), (password,))
    current_app._db.execute_sql(SQL("GRANT CONNECT ON DATABASE {} TO {};").format(Identifier(current_app.config['DBNAME']), Identifier(user)))
    if current_app.config['TESTING']:
        current_app._redis.lpush('user_list', user)
    
def hashed(name):
    try:
        lid = current_app._hashids.encode(int(name.encode('utf-8').hex(), 16))
        return lid
    except:
        return False

def unhashed(lid):
    try:
        name = bytes.fromhex(hex(current_app._hashids.decode(lid)[0])[2:]).decode('utf-8')
        return name
    except:
        return False

def list_layers(user):
    cur = current_app._db.execute_sql("SELECT DISTINCT table_name FROM information_schema.role_table_grants where grantee = %s", (user,))
    return [{
        "name": row[0],
        "id": hashed(row[0])
    } for row in cur.fetchall()]

def table_exists(table):
    cur = current_app._db.execute_sql("SELECT relname FROM pg_class WHERE relkind in ('r', 'v', 't', 'm', 'f', 'p') AND relname = %s", (table,))
    return cur.fetchone() != None

def create_table(name, fields, user):
    table_string = "CREATE TABLE {} (id serial, "
    table_columns_names = [Identifier(name)]
    table_columns_types = []
    for idx, field in enumerate(fields):
        table_string += "{} %s"
        table_columns_names.append(Identifier(field["name"]))
        table_columns_types.append(AsIs(field["type"])) #sql injcection proof, bo typy są zadeklarowane
        if idx + 1 != len(fields):
            table_string += ","
        else:
            table_string += ")"
    current_app._db.execute_sql(SQL(table_string).format(*table_columns_names), [*table_columns_types])
    current_app._db.execute_sql(SQL('GRANT ALL PRIVILEGES ON TABLE {} TO {};').format(Identifier(name), Identifier(user)))

def remove_table(name):
    current_app._db.execute_sql(SQL("DROP TABLE {} CASCADE").format(Identifier(name)))

def geojson(name):
    cur = current_app._db.execute_sql(SQL("""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(ST_AsGeoJSON(t.*)::json)
        )
        FROM (SELECT * from {}) as t;""").format(Identifier(name)))
    return cur.fetchone()[0]

def geojson_single(name, fid):
    cur = current_app._db.execute_sql(SQL("""
        SELECT ST_AsGeoJSON(t.*)
        FROM (SELECT * from {} WHERE id=%s) as t;""").format(Identifier(name)), (fid,))
    g = cur.fetchone()
    if not g:
        return {"error": "invalid id"}, 401
    return json.loads(g[0]), 200

def tile_ul(x, y, z):
    n = 2.0 ** z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return  lon_deg,lat_deg

def create_mvt_tile(z, x, y, name):
    xmin,ymin = tile_ul(x, y, z)
    xmax,ymax = tile_ul(x+1, y+1, z)
    cur = current_app._db.cursor()
    query = SQL('''SELECT ST_AsMVT(tile) FROM (SELECT id,
        ST_AsMVTGeom(geometry,ST_Makebox2d(ST_SetSrid(ST_MakePoint(%s,%s),4326),
        ST_SetSrid(ST_MakePoint(%s,%s),4326)),4096,8,true) AS geom FROM {}) AS tile''').format(Identifier(name))
    cur.execute(query,(xmin ,ymin, xmax, ymax))
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
    token = jwt.encode({"user": user, "uuid": random_uuid}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    current_app._redis.set(random_uuid, user, ex=600)
    return token

def permission_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        lid = kws.get('lid')
        if not lid:
            return jsonify({"error":"layer id is required"}), 401
        name = unhashed(lid)
        if not name:
            return jsonify({"error":"layer id is invalid"}), 401
        if not table_exists(name):
            return jsonify({"error":"layer not exists"}), 401
        if name not in [layer['name'] for layer in list_layers(request.user)]:
            return jsonify({"error":"access denied"}), 403
        return f(*args, **kws)
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        token = request.args.get('token')
        # W przypadku braku tokena
        if not token:
            return jsonify({"error": "login required"}), 403
        # W przypadku niepoprawnego tokena
        try:
            user_data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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