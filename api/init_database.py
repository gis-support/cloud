from app.create import create_app
from app.db.database import database
from app.db.migrations.utils import insert_migrations
from app.db.tables import create_tables

if __name__ == '__main__':
    app = create_app()
    create_tables(app._db)
    insert_migrations()
