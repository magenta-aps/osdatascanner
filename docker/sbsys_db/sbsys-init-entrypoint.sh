#!/bin/bash

# Initialize the DB structure (the password used is not sensitive as it
# is only use in the development environment and in the GitLab CI pipeline)
/opt/mssql-tools18/bin/sqlcmd -C -S SBSYS_DB -U sa -P ub3rStr0nGpassword -d master -i /db_init.sql;

# Populate the SBSYS DB (for development and testing)
python -m os2datascanner.integrations.sbsys.dev_env.db_init
