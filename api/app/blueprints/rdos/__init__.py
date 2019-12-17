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
    app.register_blueprint(mod_attachments, url_prefix='/api')
