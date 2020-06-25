from peewee import AutoField, TextField

from app.db.base_model import BaseModel


class Migration(BaseModel):
    """Model przechowujący nazwy dotychczas wykonanych skryptów migracyjnych"""

    class Meta:
        table_name = "migration"
        schema = "system"

    id = AutoField(primary_key=True)
    script = TextField()

    @staticmethod
    def script_sorter(name):
        return int(name.split('_')[0])
