#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.db.general import database
from peewee import ProgrammingError


def create_db(config):
    database.init(config['DBNAME'],
                  host=config['DBHOST'],
                  user=config['DBUSER'],
                  password=config['DBPASS'],
                  port=config['DBPORT'])
    if config['TESTING'] == True:
        # Docker Postgis by Kartoza has problem with multidatabase init scripts
        database.execute_sql("""
            CREATE TABLE IF NOT EXISTS public.layer_styles (
                id serial NOT NULL,
                f_table_catalog varchar NULL,
                f_table_schema varchar NULL,
                f_table_name varchar NULL,
                f_geometry_column varchar NULL,
                stylename text NULL,
                styleqml xml NULL,
                stylesld xml NULL,
                useasdefault bool NULL,
                description text NULL,
                "owner" varchar(63) NULL,
                ui xml NULL,
                update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT layer_styles_pkey PRIMARY KEY (id)
            );
        """)
        try:
            database.execute_sql("""
                CREATE GROUP "default";
            """)
        except ProgrammingError:
            pass
    return database
