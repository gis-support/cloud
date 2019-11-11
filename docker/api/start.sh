#!/bin/bash
cd /api
pipenv --three --site-packages && pipenv install --skip-lock && pipenv run python run.py