from typing import Any, Collection

from psycopg2.sql import SQL, Literal, Identifier

from app.db.connection import database

def create_enumerator(name: str, values: Collection[Any] = None):
    values = values or []

    string_values = map(str, values)
    parsed_values = map(Literal, string_values)
    sql = SQL("CREATE TYPE {} AS ENUM ({})").format(
        Identifier(name),
        SQL(",").join(parsed_values)
    )

    database.execute_sql(sql)

def get_values_of_enumerator(name: str):
    if not does_enumerator_exist(name):
        raise ValueError(f"enumerator {name} does not exist")

    sql = SQL(
        """SELECT t2.enumlabel
             FROM pg_type t1 
             JOIN pg_enum t2 
             ON t1.oid = t2.enumtypid 
             WHERE t1.typname = {} """
    ).format(Literal(name))

    cursor = database.execute_sql(sql)

    result = [row[0] for row in cursor]
    return result

def does_enumerator_exist(name) -> bool:
    sql = SQL("SELECT typname FROM pg_type WHERE typname={}").format(Literal(name))
    cursor = database.execute_sql(sql)
    return bool(cursor.fetchone())

def get_columns_used_by_enumerator(name) -> list:
    sql = SQL(
        "SELECT table_schema, table_name, column_name "
        "FROM information_schema.columns "
        "WHERE data_type = 'USER-DEFINED' and udt_name = {};"
    ).format(Literal(name))

    cursor = database.execute_sql(sql)

    result = []
    while (row := cursor.fetchone()) is not None:
        result.append({
            "schema_name": row[0],
            "table_name": row[1],
            "column_name": row[2]
        })

    return result

def is_enumerator_used_by_any_column(name) -> bool:
    columns = get_columns_used_by_enumerator(name)
    return len(columns) != 0

def drop_enumerator(name, if_exists=True):
    sql = SQL("DROP TYPE {} {}").format(
        SQL("if exists" if if_exists else ""),
        Identifier(name)
    )  # CASCADE drops dependent columns which is too drastic, so we better don't use it

    database.execute_sql(sql)
