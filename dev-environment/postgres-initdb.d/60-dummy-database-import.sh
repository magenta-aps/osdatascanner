#!/bin/sh

psql --username "$REPORT_DATABASE_USER" "$REPORT_DATABASE_NAME" < "/docker-entrypoint-initdb.d/60-dummy-database.sqldump"
