#!/bin/bash
cd /api
echo "Tests running, please wait..."
pipenv run python tests.py "$@"
echo "Tests finished."