#!/bin/bash
db_list=(`echo ${POSTGRES_DBNAME} | tr ',' ' '`)
main_db="${db_list[0]}"
PGPASSWORD=$POSTGRES_PASS pg_restore -h localhost -U $POSTGRES_USER -d $main_db /dumps/"$@"