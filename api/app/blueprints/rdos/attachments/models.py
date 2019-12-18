from app.db.general import BaseModel
from peewee import TextField


class Attachment(BaseModel):
    name = TextField(null=True)
    link = TextField(null=True)
    group = TextField(null=True, default="default")
    lid = TextField(null=True)
    fid = TextField(null=True)

    @staticmethod
    def get_attachments(lid, fid, group):
        query = Attachment.select().where(
            Attachment.group << [group, 'public'],
            Attachment.lid == lid,
            Attachment.fid == fid).dicts()
        data = {
            'public': [],
            'default': []  # temporary, wait for user groups
        }
        for row in query:
            if row['group'] not in data:
                data[row['group']] = []
            data[row['group']].append(row)
        return data

    @staticmethod
    def add_attachment(data):
        attachment = Attachment.create(**data)
        return attachment.id

    @staticmethod
    def sync(old_lid, new_lid):
        Attachment.update(lid=new_lid).where(
            Attachment.lid == old_lid).execute()
