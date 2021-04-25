#!/usr/bin/env bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python -m flask db upgrade
python -m flask run --host=0.0.0.0

exec "$@"
