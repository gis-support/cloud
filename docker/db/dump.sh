#!/bin/bash
db_list=(`echo ${POSTGRES_DBNAME} | tr ',' ' '`)
main_db="${db_list[0]}"
PGPASSWORD=$POSTGRES_PASS pg_dump -h localhost -U $POSTGRES_USER -Fc $main_db > /dumps/dump-`date +%Y%m%d-%H%M`.dump