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
    return database
