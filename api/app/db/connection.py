from app.db.database import database


def create_db(config):
    database.init(config['DBNAME'],
                  host=config['DBHOST'],
                  user=config['DBUSER'],
                  password=config['DBPASS'],
                  port=config['DBPORT'])
    return database