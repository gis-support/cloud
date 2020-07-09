from collections import defaultdict
from typing import Union, Optional, Dict

from peewee import SQL, AutoField, TextField, ForeignKeyField

from app.db.base_model import BaseModel


class Tag(BaseModel):

    class Meta:
        table_name = "tag"
        schema = "system"

    id = AutoField(primary_key=True)
    name = TextField(unique=True)
    color = TextField()

    @classmethod
    def does_tag_with_name_exist(cls, name: str, except_: Optional[Union["cls"]] = None) -> bool:
        query = cls.select().where(cls.name == name)
        if except_:
            query = query.where(cls.id != except_)
        return query.exists()


class LayerTag(BaseModel):

    class Meta:
        table_name = "layer_tag"
        schema = "system"
        constraints = [
            SQL("CONSTRAINT layer_tag_unique UNIQUE (layer_id, tag_id)")
        ]

    id = AutoField(primary_key=True)
    layer_id = TextField()
    tag = ForeignKeyField(model=Tag, db_column="tag_id")

    @classmethod
    def is_layer_already_tagged(cls, layer_id: str, tag: Union[int, Tag]):
        return cls.select().where(cls.layer_id == layer_id, cls.tag == tag).exists()

    @classmethod
    def get_tags_by_layer_id(cls) -> Dict[str, list]:

        query = Tag.select(Tag, cls.layer_id).join(cls).dicts()

        result = defaultdict(list)
        for row in query:
            layer_id = row.pop("layer_id")
            result[layer_id].append(row)

        return result

    @classmethod
    def update_layer_id(cls, old_layer_id: str, new_layer_id: str):
        cls.update(layer_id=new_layer_id).where(cls.layer_id == old_layer_id).execute()