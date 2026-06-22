## Docker Compose

You can (and should) use `docker compose` to start the OSdatascanner system and its runtime
dependencies.

A `docker-compose.yml` for development is included in the repository. It
specifies the settings to start and connect all required services.

### Admin

#### `admin`

Reachable on: http://localhost:8020

Runs the django application that provides the administration
interface for defining and managing organisations, rules, scans etc.

#### `admin_checkup_collector`

Runs the **collector** service that saves `ScheduledCheckup` and `UserErrorLog` objects
to the admin database.

`ScheduledCheckup`s are objects a `Scanner` must revisit at its next run.

`UserErrorLog`s are objects that represent _some_ error during a scan, which can be displayed for
the user.

#### `admin_cron`

Runs `supercronic` pointed at `docker/admin/crontab` which is responsible for starting scheduled
`Scannerjob`s, import jobs and checking `GraphGrant` expiry.

#### `admin_job_runner`

Responsible for picking up and executing `BackgroundJob`s, which are our different import jobs.

#### `admin_status_collector`

Runs the **collector** service that saves `ScanStatus`, `ScanStatusSnapshot`
and `MIMETypeProcessStat` objects.

These are objects that relate to the progress of a `Scanner` run.

### Report

#### `report`

Reachable on: http://localhost:8040

Runs the django application that provides the interface for
accessing and handling reported matches.

#### `report_cron`

Runs `supercronic` pointed at `docker/report/crontab` which is responsible for sending out emails
and pushing some metrics.

#### `report_email_tagger`

Optional service/required only for labelling of O365 emails.

Reads from RabbitMQ `os2ds_email_tags` queue and labels O365 emails in Outlook.

#### `report_event_collector`

Runs the **collector** service that saves events sent from the admin module.

An event is an update or deletion of one or more model objects. F.e. `Organization`, `Account`
or others.

#### `report_result_collector`

Runs the **collector** service that saves match
results to the database of the report module.

Depending on configuration, it can also write to the RabbitMQ queue: `os2ds_email_tags`,
which is read by the optional `email_tagger`

### Engine

#### `explorer`

Runs the **explorer** stage of the engine.

#### `exporter`

Runs the **exporter** stage of the engine.

#### `worker`

Runs the **worker** stage of the engine, which includes:

- `processor`
- `matcher`
- `tagger`

These _can_ be run separately, but are most commonly used bundled as a `worker`.

### API

#### `api_server`

Runs the OSdatascanner API.

#### `swagger_ui`

Swagger UI for our `api_server`

### Required infrastructure

#### `db`

Runs a postgres database server based on [the official postgres
docker image](https://hub.docker.com/_/postgres/).

#### `queue`

Runs a RabbitMQ message queue server based on [the official
RabbitMQ docker image](https://hub.docker.com/_/rabbitmq/) , including a
plugin providing a web interface for monitoring (and managing) queues and
users.

The web interface can be reached on: http://localhost:8030

### Helper / one-shot services

#### `admin_migrate`

Responsible for applying database migrations from
everything in the "admin" project.

#### `frontend`

Builds and bundles different frontend static files.

#### `pg_upgrade`

A helper service specific to upgrading PostgreSQL version.

#### `report_migrate`

Responsible for applying database migrations from
everything in the "report" project.

### Test data sources

#### `init_SBSYS_DB`

A helper service that pre-populates the `SBSYS_DB` with relevant test data.

#### `mailhog`

A SMTP-server for testing purposes.

Web interface available at `http://localhost:8025/`.

#### `nginx`

A webserver that exposes the same folder as `samba`.

#### `samba`

A Samba service that serves up some test files in a shared folder
called `e2test`. This can be useful to test the file scanner.

The Samba server is available as `samba:139` inside the Docker environment
and `localhost:8139` on the host machine. The full UNC of the shared folder
in the Docker environment is `//samba/e2test`.

The Samba server doesn't require a workgroup name, but it does require a
username (`os2`) and password (`swordfish`).

Thus, from the host: `smbclient -p 8139 -U os2%swordfish //localhost/e2test`

#### `SBSYS_DB`

An MSSQL server used to simulate an SBSYS database.

### Authentication & SSO (testing)

#### `idp`

A `simplesamlphp` identity provider which can be used to test Single Sign-On.

#### `ldap-server`

An `openldap` server that can be used to test LDAP import.

#### `ldap-server-admin`

Graphical interface for `ldap-server`

#### `localkeycloak.os2datascanner`

A Keycloak instance used for LDAP import and Single Sign-On.

#### `postgres-keycloak`

PostgreSQL database for Keycloak.

#### `traefik`

Traefik instance.

### Observability

#### `cadvisor`

Collects certain system metrics from containers.

#### `grafana`

Dashboards to display metrics.

#### `prometheus`

For collecting metrics and a place to scrape them from.

#### `pushgateway`

A prometheus helper, to push metrics to.

### Machine learning

#### `ai-classifier`

Runs a text classifier that can be used in OSdatascanner `Rule` creation.

### Developer tooling

#### `docs`

Runs an `mkdocs` image, for locally viewing our ReadTheDocs.


### Profiles

The `docker-compose.yml` use `--profiles` which requires version
`docker compose > 1.28`.

To start the core components(`engine`, `report`- and `admin` interface, `db`
and `queue`) of datascanner, use

```sh
docker compose up -d
```

To start a service behind a `profiles` flag, use

```sh
docker compose --profile api up -d
```

The following `profiles` are available: `ldap`, `sso`, `api`, `metric` and
`ai`.

The development config files are stored in `os2datascanner/dev-environment/`


#### `--profile ldap`

The `ldap` profile defines a Keycloak instance and connected Postgres database,
as well as a OpenLDAP server and admin interface.

Be sure to enable import and structured org. features on the client in the admin module's django admin page.

#### `--profile sso`

Starts Keycloak and its db, and the `idp` service.

#### `--profile cron`

The `cron` profile starts two instances of [`supercronic`](https://github.com/aptible/supercronic),
one for the admin system and one for the report module, for testing that task
scheduling works properly.

These services are not enabled by default because settings that make sense in
production ("start this scanner at midnight", "send emails out every day at
10am", or "synchronise this organisation every day at 3pm") don't normally make
sense in the development environment.

#### `--profile ai`

The `ai` profile starts the `ai-classifier` helper component, which performs
additional classification on the results of certain special CPR and regex
matches.


#### `--profile metric`

Starts the observability stack.