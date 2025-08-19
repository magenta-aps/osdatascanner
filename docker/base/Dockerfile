# Copyright (C) 2020 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
FROM node:15 AS frontend

WORKDIR /code/src/os2datascanner/projects

COPY --chown=node:node src/os2datascanner/projects/static ./static
RUN npm ci --prefix static; \

# Build production bundle
# NB! Doesn't start a webserver, only bundles files!
    npm run prod --prefix static

USER node

# Build development bundle
# NB! Watches for changes, so no automatic exit!
CMD ["npm", "run", "dev", "--prefix", "static"]

FROM python:3.13.6-bookworm as base

# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1 \
  PYTHONPATH=/code/src/:$PYTHONPATH

# Ensure system user and install system depedencies
WORKDIR /code/requirements
COPY requirements/sys-requirements/sys-requirements-all.txt \
     ./sys-requirements/

COPY requirements/python-requirements/requirements-all.txt \
     ./python-requirements/

ARG SUPERCRONIC_VERSION=v0.1.12
ARG SUPERCRONIC_SHA1SUM=048b95b48b708983effb2e5c935a1ef8483d9e3e

# hadolint ignore=DL3008,SC2046,DL4006
RUN set -ex \
  # Install system dependencies from file.
  && apt-get -y update \
  && apt-get -y install --no-install-recommends $(grep -oh '^[^#][[:alnum:].-]*' sys-requirements/sys-requirements*.txt) \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man/?? /usr/share/man/??_* \
  # install supercronic
  && curl -fsSL "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/supercronic-linux-amd64" \
     -o /usr/local/bin/supercronic \
  && echo "${SUPERCRONIC_SHA1SUM}  /usr/local/bin/supercronic" | sha1sum -c - \
  && chmod +x /usr/local/bin/supercronic \
  # Install python dependencies and clean up build dependencies
  && pip install --no-cache-dir -r python-requirements/requirements-all.txt \
  && apt-get -y autoremove

WORKDIR /code/resources
COPY resources ./
RUN set -ex && /code/resources/prepare.sh

# Copy frontend dist folder to static
WORKDIR /code/src/os2datascanner/projects/static
COPY --from=frontend /code/src/os2datascanner/projects/static/dist ./dist

# Copy code
WORKDIR /code/src/os2datascanner
COPY src/os2datascanner ./

# Compile engine translations
RUN set -ex \
  && /code/src/os2datascanner/engine2/locale/manage.sh compilemessages

ENV \
  OS2DS_ENGINE_SYSTEM_CONFIG_PATH=/docker/settings/engine-system.toml \
  OS2DS_ENGINE_USER_CONFIG_PATH=/docker/settings/engine-user.toml

# Every component must have the engine settings available
COPY docker/engine/docker-settings.toml /docker/settings/engine-system.toml

ENTRYPOINT ["/docker/entrypoint.sh"]

# hadolint ignore=DL3006
FROM base AS engine

LABEL org.opencontainers.image.title="OS2datascanner - Engine" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2datascanner.magenta.dk/" \
      org.opencontainers.image.documentation="https://os2datascanner.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/os2datascanner/os2datascanner"

RUN groupadd -g 63030 -r os2ds_engine \
  && useradd -u 63030 --no-log-init -r -g os2ds_engine os2ds_engine

COPY docker/engine/docker-entrypoint.sh /docker/entrypoint.sh

# Set up to run given command as the new user
USER os2ds_engine:os2ds_engine

EXPOSE 9091
CMD ["explorer", "--help"]

# hadolint ignore=DL3006
FROM base AS api

LABEL org.opencontainers.image.title="OS2datascanner - API" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2datascanner.magenta.dk/" \
      org.opencontainers.image.documentation="https://os2datascanner.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/os2datascanner/os2datascanner"

RUN groupadd -g 63050 -r os2ds_api\
  && useradd -u 63050 --no-log-init -r -g os2ds_api os2ds_api

ENV \
  OS2DS_SERVER_SYSTEM_CONFIG_PATH=/docker/settings/server-system.toml \
  OS2DS_SERVER_USER_CONFIG_PATH=/docker/settings/server-user.toml

COPY docker/api/docker-settings.toml /docker/settings/server-system.toml
COPY docker/api/gunicorn-settings.py /docker/settings/server-gunicorn.py

WORKDIR /code/src/os2datascanner/server
USER os2ds_api:os2ds_api
EXPOSE 5000

ENTRYPOINT []
CMD ["gunicorn", \
     "--config", "/docker/settings/server-gunicorn.py", \
     "os2datascanner.server.wsgi"]

FROM base AS web_base

WORKDIR /code/src/os2datascanner/projects/grants
RUN django-admin compilemessages

WORKDIR /code/src/os2datascanner/projects/shared
RUN django-admin compilemessages

WORKDIR /code/src/os2datascanner/core_organizational_structure
RUN django-admin compilemessages

# hadolint ignore=DL3006
FROM web_base AS admin

LABEL org.opencontainers.image.title="OS2datascanner - Administration" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2datascanner.magenta.dk/" \
      org.opencontainers.image.documentation="https://os2datascanner.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/os2datascanner/os2datascanner"

ENV \
  OS2DS_ADMIN_SYSTEM_CONFIG_PATH=/docker/settings/admin-system.toml \
  OS2DS_ADMIN_USER_CONFIG_PATH=/docker/settings/admin-user.toml \ 
  DJANGO_SETTINGS_MODULE=os2datascanner.projects.admin.settings

RUN groupadd -g 63020 -r os2ds_admin \
  && useradd -u 63020 --no-log-init -r -g os2ds_admin os2ds_admin \
  && install -o os2ds_admin -g os2ds_admin -d /code/uploads/admin \
  && install -o os2ds_admin -g os2ds_admin -d /code/static \
  && install -o os2ds_admin -g os2ds_admin -d /code/build \
  && install -o os2ds_admin -g os2ds_admin -d /code/var

COPY docker/admin/crontab /docker/settings/admin-crontab
COPY docker/admin/docker-settings.toml /docker/settings/admin-system.toml
COPY docker/insecure-settings.toml /docker/settings/admin-insecure.toml
COPY docker/docker-entrypoint-django.sh /docker/entrypoint.sh
COPY docker/gunicorn-settings.py /docker/settings/admin-gunicorn.py

# Run the server as the os2ds_admin user on port 5000
WORKDIR /code/src/os2datascanner/projects/admin

# Make os2ds_admin owner of /docker. This is only needed to remove the
# insecure settings file after `collectstatic`.
RUN chown -R os2ds_admin:os2ds_admin /docker

USER os2ds_admin:os2ds_admin

# Unfortunately, `manage.py` requires all settings to be set. We include a set
# of insecure setting here for only this purpose. We make sure to delete it
# afterward. If `insecure-settings.toml` is found in any production image,
# consider it a bug. See `insecure-settings.toml` for a detailed explanation.
RUN set -ex \
  && OS2DS_ADMIN_USER_CONFIG_PATH=/docker/settings/admin-insecure.toml OS2DS_ENGINE_USER_CONFIG_PATH='' python manage.py collectstatic --no-input --clear \
  && OS2DS_ADMIN_USER_CONFIG_PATH=/docker/settings/admin-insecure.toml OS2DS_ENGINE_USER_CONFIG_PATH='' python manage.py compilemessages \
  && rm /docker/settings/admin-insecure.toml

EXPOSE 5000
ENTRYPOINT ["/docker/entrypoint.sh"]
CMD ["gunicorn", "--config", "/docker/settings/admin-gunicorn.py", "asgi", "os2datascanner.projects.report.asgi:application"]

ARG COMMIT_TAG
ARG COMMIT_SHA
ARG CURRENT_BRANCH
ENV COMMIT_TAG=${COMMIT_TAG} \
    COMMIT_SHA=${COMMIT_SHA} \
    CURRENT_BRANCH=${CURRENT_BRANCH}

# hadolint ignore=DL3006
FROM web_base AS report

LABEL org.opencontainers.image.title="OS2datascanner - Report" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2datascanner.magenta.dk/" \
      org.opencontainers.image.documentation="https://os2datascanner.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/os2datascanner/os2datascanner"

ENV \
  OS2DS_REPORT_SYSTEM_CONFIG_PATH=/docker/settings/report-system.toml \
  OS2DS_REPORT_USER_CONFIG_PATH=/docker/settings/report-user.toml \
  DJANGO_SETTINGS_MODULE=os2datascanner.projects.report.settings

RUN groupadd -g 63040 -r os2ds_report\
  && useradd -u 63040 --no-log-init -r -g os2ds_report os2ds_report \
  && install -o os2ds_report -g os2ds_report -d /code/src/os2datascanner/projects/report/media/images \
  && install -o os2ds_report -g os2ds_report -d /code/build \
  && install -o os2ds_report -g os2ds_report -d /code/static \
  && install -o os2ds_report -g os2ds_report -d /code/var

COPY docker/report/crontab /docker/settings/report-crontab
COPY docker/report/docker-settings.toml /docker/settings/report-system.toml
COPY docker/insecure-settings.toml /docker/settings/report-insecure.toml
COPY docker/docker-entrypoint-django.sh /docker/entrypoint.sh
COPY docker/gunicorn-settings.py /docker/settings/report-gunicorn.py

# Run the server as the os2ds_report user on port 5000
WORKDIR /code/src/os2datascanner/projects/report
# Make os2ds_report owner of /docker. This is only needed to remove the
# insecure settings file after `collectstatic`.
RUN chown -R os2ds_report:os2ds_report /docker

USER os2ds_report:os2ds_report

# Unfortunately, `manage.py` requires all settings to be set. We include a set
# of insecure setting here for only this purpose. We make sure to delete it
# afterward. If `insecure-settings.toml` is found in any production image,
# consider it a bug. See `insecure-settings.toml` for a detailed explanation.
RUN set -ex \
  && OS2DS_REPORT_USER_CONFIG_PATH=/docker/settings/report-insecure.toml OS2DS_ENGINE_USER_CONFIG_PATH='' python manage.py collectstatic --no-input --clear \
  && OS2DS_REPORT_USER_CONFIG_PATH=/docker/settings/report-insecure.toml OS2DS_ENGINE_USER_CONFIG_PATH='' python manage.py compilemessages \
  && rm /docker/settings/report-insecure.toml

EXPOSE 5000
ENTRYPOINT ["/docker/entrypoint.sh"]
CMD ["gunicorn", "--config", "/docker/settings/report-gunicorn.py", "asgi", "os2datascanner.projects.report.asgi:application"]

FROM base AS sbsys-init

ENV ACCEPT_EULA=Y \
    MSSQL_COLLATION=SQL_Danish_Pref_CP1_CI_AS \
    SBSYS_HOST=SBSYS_DB \
    SBSYS_PORT=1433 \
    SBSYS_USER=sa \
    # Password not sensitive (only used in dev env and in the GitLab pipeline)
    SBSYS_PASSWORD=ub3rStr0nGpassword \
    SBSYS_DATABASE=SbSysNetDrift

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl https://packages.microsoft.com/keys/microsoft.asc \
    | tee /etc/apt/trusted.gpg.d/microsoft.asc \
    && curl https://packages.microsoft.com/config/debian/11/prod.list \
       | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends msodbcsql18=18.3.3.1-1 \
       mssql-tools18=18.2.1.1-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY docker/sbsys_db/ ./

ENTRYPOINT ["/bin/bash", "/code/sbsys-init-entrypoint.sh"]
