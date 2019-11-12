#!/bin/bash
cd /api
echo "Tests running, please wait..."
echo "$@"
pipenv run python tests.py "$@"
echo "Tests finished."