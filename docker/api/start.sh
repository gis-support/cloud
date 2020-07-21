#!/bin/bash
cd /api
pipenv --python 3.8.3 --site-packages && pipenv install --skip-lock && pipenv run python run.py