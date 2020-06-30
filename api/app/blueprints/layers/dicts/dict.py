from typing import Any, List

from peewee import AutoField, TextField, SQL

from psycopg2 import sql as psysql
from app.db import enumerators
from app.db.base_model import BaseModel
from app.helpers.cloud import get_cloud


class Dict(BaseModel):

    class Meta:
        table_name = "dict"
        schema = "system"
        constraints = [
            SQL("CONSTRAINT dict_unique UNIQUE (layer_id, column_name, enumerator_name)")
        ]

    id = AutoField(primary_key=True)
    layer_id = TextField()
    column_name = TextField()
    enumerator_name = TextField()

    def get_values(self):
        return enumerators.get_values_of_enumerator(self.enumerator_name)

    def set_values(self, values: List[Any]):
        cloud = get_cloud()
        table_name = cloud.unhash_name(self.layer_id)

        current_values = set(enumerators.get_values_of_enumerator(self.enumerator_name))

        values_to_be_removed = current_values - set(values)

        sql_set_type_to_text = psysql.SQL("ALTER TABLE {} ALTER COLUMN {} TYPE TEXT").format(
            psysql.Identifier(table_name), psysql.Identifier(self.column_name)
        )

        values_to_be_removed_sql = [psysql.Literal(str(value)) for value in values_to_be_removed]

        sql_set_null = psysql.SQL("UPDATE {table_name} SET {column_name} = NULL WHERE {column_name} IN ({values})").format(
            table_name=psysql.Identifier(table_name),
            column_name=psysql.Identifier(self.column_name),
            values=psysql.SQL(",").join(values_to_be_removed_sql)
        )
        sql_drop_old_enumerator = psysql.SQL("DROP TYPE {}").format(psysql.Identifier(self.enumerator_name))
        sql_set_type_to_enumerator = psysql.SQL("""ALTER TABLE {table_name} ALTER COLUMN {column_name} 
                                     TYPE {enumerator_name} USING {column_name}::{enumerator_name}""").format(
            table_name=psysql.Identifier(table_name), column_name=psysql.Identifier(self.column_name),
            enumerator_name=psysql.Identifier(self.enumerator_name)
        )

        db = self._meta.database
        with db.atomic():
            db.execute_sql(sql_set_type_to_text)
            db.execute_sql(sql_drop_old_enumerator)

            if len(values_to_be_removed) > 0:
                db.execute_sql(sql_set_null)

            enumerators.create_enumerator(self.enumerator_name, values)
            db.execute_sql(sql_set_type_to_enumerator)

    @classmethod
    def update_layer_id(cls, old_layer_id: str, new_layer_id: str):
        cls.update(layer_id=new_layer_id).where(cls.layer_id == old_layer_id).execute()

