from peewee import PostgresqlDatabase

from app.db.database import database


def init_priviliges(database: PostgresqlDatabase):
    with database.atomic():
        database.execute_sql("GRANT SELECT on layer_styles to public;")


def create_db(config):
    database.init(config['DBNAME'],
                  host=config['DBHOST'],
                  user=config['DBUSER'],
                  password=config['DBPASS'],
                  port=config['DBPORT'])

    init_priviliges(database)

    return database
