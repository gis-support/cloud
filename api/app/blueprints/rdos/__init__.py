#!/usr/bin/python
# -*- coding: utf-8 -*-

# Attachments
from app.blueprints.rdos.attachments.routings import mod_attachments
from app.blueprints.rdos.attachments.models import Attachment
# Services
from app.blueprints.rdos.services.routings import mod_services
from app.blueprints.rdos.services.models import Service
# Analysis
from app.blueprints.rdos.analysis.routings import mod_analysis
from app.blueprints.rdos.analysis.models import Settings

TABLES = [
    Attachment,
    Service,
    Settings
]


def init_rdos(app):
    app._db.create_tables(TABLES, safe=True)
    app.register_blueprint(mod_attachments, url_prefix='/api')
    app.register_blueprint(mod_services, url_prefix='/api')
    app.register_blueprint(mod_analysis, url_prefix='/api')
