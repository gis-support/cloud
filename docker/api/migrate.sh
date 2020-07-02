#!/bin/bash
cd /api
echo "Migrating..."
pipenv run python -u migrate.py "$@"
echo "Migrations finished"
