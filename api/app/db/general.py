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

database = PostgresqlExtDatabase(
    None,
    register_hstore=False,
    autorollback = True,
    field_types={'geometry':'geometry'}
)

def user_exists(user):
    cur = current_app._db.execute_sql('SELECT 1 FROM pg_roles WHERE rolname=%s', (user,))
    return cur.fetchone() != None

def create_user(user, password):
    current_app._db.execute_sql(SQL("CREATE USER {} WITH ENCRYPTED PASSWORD %s").format(Identifier(user)), (password,))
    current_app._db.execute_sql(SQL("GRANT CONNECT ON DATABASE {} TO {};").format(Identifier(current_app.config['DBNAME']), Identifier(user)))

def list_layers(user):
    cur = current_app._db.execute_sql("SELECT DISTINCT table_name FROM information_schema.role_table_grants where grantee = %s", (user,))
    return [row[0] for row in cur.fetchall()]

def table_exists(table):
    try:
        current_app._db.execute_sql("SELECT %s::regclass", (table,))
        return True
    except:
        return False

def create_table(name, fields, user):
    table_string = "CREATE TABLE {} ("
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