from app.db.general import BaseModel
from peewee import TextField


class Attachment(BaseModel):
    link = TextField(null=True)
    group = TextField(null=True, default="default")

    @staticmethod
    def get_all_for_group(group):
        query = Attachment.select().where(
            Attachment.group << [group, 'public']).dicts()
        return [row for row in query]
