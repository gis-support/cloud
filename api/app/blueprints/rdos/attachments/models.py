from app.db.general import BaseModel
from peewee import TextField
from playhouse.shortcuts import model_to_dict
import os


class Attachment(BaseModel):
    name = TextField(null=True)
    link = TextField(null=True)
    group = TextField(null=True, default=os.environ['DEFAULT_GROUP'])
    lid = TextField(null=True)
    fid = TextField(null=True)

    @staticmethod
    def get_attachments(lid, fid, group):
        groups = set([group, os.environ['DEFAULT_GROUP']])
        query = Attachment.select().where(
            Attachment.group << groups,
            Attachment.lid == lid,
            Attachment.fid == fid).dicts()
        data = {key: [] for key in groups}
        for row in query:
            if row['group'] not in data:
                data[row['group']] = []
            data[row['group']].append(row)
        return data

    @staticmethod
    def add_attachment(data):
        attachment = Attachment.create(**data)
        return model_to_dict(attachment)

    @staticmethod
    def delete_attachment(lid, fid, aid):
        attachment = Attachment.delete().where(
            (Attachment.lid == lid) &
            (Attachment.fid == fid) &
            (Attachment.id == aid)
        ).execute()
        return attachment

    @staticmethod
    def sync(old_lid, new_lid):
        Attachment.update(lid=new_lid).where(
            Attachment.lid == old_lid).execute()
