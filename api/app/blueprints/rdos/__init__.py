#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.blueprints.rdos.attachments.routings import mod_attachments
from app.blueprints.rdos.attachments.models import Attachment

TABLES = [
    Attachment
]


def init_rdos(app):
    app._db.drop_tables(reversed(TABLES), safe=True, cascade=True)
    app._db.create_tables(TABLES, safe=True)
    add_initial_attachments()
    app.register_blueprint(mod_attachments, url_prefix='/api')


def add_initial_attachments():
    Attachment.create(link="google.com", group="default")
    Attachment.create(link="google.com", group="public")
    Attachment.create(link="google.com", group="private")
