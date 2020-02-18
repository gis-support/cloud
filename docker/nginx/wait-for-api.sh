#!/bin/sh
# wait-for-api.sh

set -e

until curl -s $CONTAINER_BASENAME-api-prod:$APP_PROD_API_PORT/api/docs > /dev/null; do
  sleep 1
done