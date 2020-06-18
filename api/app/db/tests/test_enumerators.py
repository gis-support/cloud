from typing import Tuple

import peewee
import pytest
from playhouse.postgres_ext import PostgresqlExtDatabase

from app.db import enumerators
from conftest import TEST_ENUM_NAME

@pytest.mark.enumerators
class TestEnumerators:

    @staticmethod
    def build_select_enum_sql(name):
        sql = f"SELECT * FROM pg_type WHERE typname = '{name}';"
        return sql

    @staticmethod
    def get_enum_values(database: PostgresqlExtDatabase, name: str):
        sql = f"""SELECT t2.enumlabel
                 FROM pg_type t1 JOIN pg_enum t2 ON t1.oid = t2.enumtypid
                 WHERE t1.typname='{name}'"""

        cursor = database.execute_sql(sql)

        result = tuple(row[0] for row in cursor.fetchall())
        return result

    def test_create_enumerator_string_values(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME
        enum_values = ("v1", "v2", "v3")

        enumerators.create_enumerator(enum_name, enum_values)

        sql_select = self.build_select_enum_sql(enum_name)
        cursor = database.execute_sql(sql_select)

        rows = cursor.fetchall()
        assert len(rows) == 1

        actual_values = self.get_enum_values(database, enum_name)

        assert actual_values == enum_values

    def test_create_enumerator_mixed_values(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME
        enum_values = (1, True, "v3")

        enumerators.create_enumerator(enum_name, enum_values)

        sql_select = self.build_select_enum_sql(enum_name)
        cursor = database.execute_sql(sql_select)

        rows = cursor.fetchall()
        assert len(rows) == 1

        actual_values = self.get_enum_values(database, enum_name)
        expected_values = ("1", "True", "v3")

        assert actual_values == expected_values

    def test_create_enumerator_duplicate(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME

        enumerators.create_enumerator(enum_name)

        with pytest.raises(peewee.ProgrammingError):
            enumerators.create_enumerator(enum_name)

        sql_select = self.build_select_enum_sql(enum_name)
        cursor = database.execute_sql(sql_select)

        rows = cursor.fetchall()
        assert len(rows) == 1

    def test_create_and_drop_enumerator(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME

        enumerators.create_enumerator(enum_name)

        enumerators.drop_enumerator(enum_name)

        sql_select = self.build_select_enum_sql(enum_name)
        cursor = database.execute_sql(sql_select)

        rows = cursor.fetchall()
        assert len(rows) == 0

    def test_drop_non_existent_enumerator(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME

        with pytest.raises(peewee.ProgrammingError):
            enumerators.drop_enumerator(enum_name, if_exists=False)

    def test_drop_non_existent_enumerator_safe(self, database: PostgresqlExtDatabase):
        enum_name = TEST_ENUM_NAME

        enumerators.drop_enumerator(enum_name, if_exists=True)

    def test_get_columns_using_enumerator(self, database: PostgresqlExtDatabase, database_table: Tuple[str, str]):
        enum_name = TEST_ENUM_NAME

        enumerators.create_enumerator(enum_name)

        columns = enumerators.get_columns_used_by_enumerator(enum_name)
        assert len(columns) == 0

        schema_name = database_table[0]
        table_name = database_table[1]
        column_name = "test_column"

        sql_add_column = f"ALTER TABLE {schema_name}.{table_name} ADD COLUMN {column_name} {enum_name}"
        database.execute_sql(sql_add_column)

        columns = enumerators.get_columns_used_by_enumerator(enum_name)

        assert len(columns) == 1
        expected_data = {
            "schema_name": schema_name,
            "table_name": table_name,
            "column_name": column_name
        }
        assert columns[0] == expected_data

        assert enumerators.is_enumerator_used_by_any_column(enum_name) is True

    def test_is_enumerator_used_by_any_column(self, database: PostgresqlExtDatabase, database_table: Tuple[str, str]):
        enum_name = TEST_ENUM_NAME

        enumerators.create_enumerator(enum_name)

        assert enumerators.is_enumerator_used_by_any_column(enum_name) is False

        schema_name = database_table[0]
        table_name = database_table[1]
        column_name = "test_column"

        sql_add_column = f"ALTER TABLE {schema_name}.{table_name} ADD COLUMN {column_name} {enum_name}"
        database.execute_sql(sql_add_column)

        assert enumerators.is_enumerator_used_by_any_column(enum_name) is True

    def test_drop_enumerator_which_is_used_by_columns(self, database: PostgresqlExtDatabase,
                                                      database_table: Tuple[str, str]):
        enum_name = TEST_ENUM_NAME

        enumerators.create_enumerator(enum_name)

        schema_name = database_table[0]
        table_name = database_table[1]
        column_name = "test_column"

        sql_add_column = f"ALTER TABLE {schema_name}.{table_name} ADD COLUMN {column_name} {enum_name}"
        database.execute_sql(sql_add_column)

        with pytest.raises(peewee.InternalError):
            enumerators.drop_enumerator(enum_name)
