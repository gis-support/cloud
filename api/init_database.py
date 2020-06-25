from app.db.database import database
from app.db.migrations.utils import insert_migrations
from app.db.tables import create_tables

try:
    from app.local_config import Config
except ImportError:
    from app.default_config import Config

if __name__ == '__main__':
    config = Config.__dict__
    database.init(
        config['DBNAME'],
        host=config['DBHOST'],
        user=config['DBUSER'],
        password=config['DBPASS'],
        port=config['DBPORT']
    )

    create_tables()
    insert_migrations()
