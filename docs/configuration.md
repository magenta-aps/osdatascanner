# Configuration

The OSdatascanner system is configured using `.toml`-files -- one for each
module. Most configuration settings come with reasonable defaults and need not
be changed for a standard set-up, but most can be adjusted as needed, and a few
must be given in order for the system to work. Below follows minimal examples
for each module.

## Configuration for the Admin-module

An almost minimal example of the `admin-user-settings.toml` configuration file:

```toml
SECRET_KEY = "<some secret key - see Django documentation>"
DECRYPTION_HEX = "<hex value of 32 random bytes for en-/decryption>"

# [site]
# The URL of this site, used in links in emails and in the redirect URL for
# OAuth 2.0 services. (This value should end with a forward slash.)
SITE_URL = "<domain url for admin module>"
# See the official Django documentation for details on ALLOWED_HOSTS
ALLOWED_HOSTS = []

# [scans] All scans are disabled by default, enable only the ones to use
ENABLE_FILESCAN = true
ENABLE_WEBSCAN = true
ENABLE_EXCHANGESCAN = true

# [email]
DEFAULT_FROM_EMAIL = "<email address used as sender from the system>"
ADMIN_EMAIL = "<email address for sys-admin>"
EMAIL_HOST = "<host name of email service>"

[amqp]
# Nested amqp settings are picked up by the common amqp utility module
AMQP_HOST = "<amqp service name>"
AMQP_USER = "<amqp user name>"
AMQP_PWD = "<amqp user password>"

[DATABASES]

    [DATABASES.default]
    ENGINE = "django.db.backends.postgresql_psycopg2"
    NAME = "os2datascanner_admin"
    USER = "<user name for dedicated admin db-user>"
    PASSWORD = "<user password for dedicated admin db-user>"
    HOST = "<database service name>"
```

### Keycloak Settings
These settings are not mandatory for running the admin module, but can be used to enable LDAP import of users and hierarchy.

A prerequisite for this functionality is running and configuring a Keycloak instance.
OS2datascanner contains a Keycloak installation that can be used, but using an external installation is also possible.

To configure the admin module's Keycloak functionality the following settings must be set.
```toml
# [keycloak]
KEYCLOAK_BASE_URL = "" # Host url for Keycloak
KEYCLOAK_ADMIN_CLIENT = "" # Admin client to use Keycloak's API to perform actions
KEYCLOAK_ADMIN_SECRET = "" # Admin client secret for authenticating 
```



## Configuration for the Engine components

A minimal example of the `enginge-user-settings.toml` configuration file:

```toml
[amqp]
# Nested amqp settings are picked up by the common amqp utility module
AMQP_HOST = "<amqp service name>"
AMQP_USER = "<amqp user name>"
AMQP_PWD = "<amqp user password>"
```

Each container also accepts the following environment variables:

|Variable|                   Values                    |Default|
|:------:|:-------------------------------------------:|:-----:|
|LOG_LEVEL| critical, error, warn, warning, info, debug |info|
|ENABLE_PROFILING|                 true, false                 |false|
|EXPORT_METRICS|                 true, false                 |false|
|PROMETHEUS_PORT|                 port number                 |9091|
|WIDTH|                 size (int)                  |3|
|SCHEDULE_ON_CPU|                  cpu (int)                  |None|
|RESTART_AFTER|             Message count (int)             |None|


## Configuration for the Report-module

An almost minimal example of the `report-user-settings.toml` configuration file
can be seen below. **Please note:** the metadata settings for `SAML2_AUTH` are
mutually exclusive, and you should only ever set one of them.

```toml
SECRET_KEY = "<some secret key - see Django documentation>"

# [site]
# The URL of this site, used in links in emails and in the redirect URL for
# OAuth 2.0 services. (This value should end with a forward slash.)
SITE_URL = "<domain url for admin module>"
# See the official Django documentation for details on ALLOWED_HOSTS
ALLOWED_HOSTS = []

# [installation]
# The name of the institution, to be included in the notification signoff
NOTIFICATION_INSTITUTION = '<organisation name>'

# [email]
DEFAULT_FROM_EMAIL = "<email address used as sender from the system>"
ADMIN_EMAIL = "<email address for sys-admin>"
EMAIL_HOST = "<host name of email service>"

[amqp]
# Nested amqp settings are picked up by the common amqp utility module
AMQP_HOST = "<amqp service name>"
AMQP_USER = "<amqp user name>"
AMQP_PWD = "<amqp user password>"

[DATABASES]

    [DATABASES.default]
    ENGINE = "django.db.backends.postgresql_psycopg2"
    NAME = "os2datascanner_admin"
    USER = "<user name for dedicated admin db-user>"
    PASSWORD = "<user password for dedicated admin db-user>"
    HOST = "<database service name>"
```

## Gunicorn

The two Django apps and the API use `Gunicorn` to serve web requests. By
default Gunicorn starts up `CPU_COUNT*2+1` workers. To override this default
use the `GUNICORN_WORKERS` environment variable. Eg.  `GUNICORN_WORKERS=2`.

## Note

The configuration system is _layered_; each module defines a basic set of
sensible defaults, and user configuration is applied on top of that set.
The layering is strictly enforced by default, so you can't define a setting
not already defined by a lower level.

| Base | User | Allowed? |
| ---- | ---- | -------- |
| `SECRET_KEY = "placeholder"` | `SECRET_KEY = "ProductionValue!4"` | yes |
| `HOSTNAME = "localhost"` | `HOSTNAME = "production.vstkom.internal"` | yes |
| (`TIME_ZONE` not set) | `TIME_ZONE = "Europe/Copenhagen"` | no |

You can override this enforcement and extend the set of allowed settings at
any level by setting the special setting `__also__` to a list of names of
settings:

| Base | User | Allowed? |
| ---- | ---- | -------- |
| (`TIME_ZONE` not set) | `TIME_ZONE = "Europe/Copenhagen"` | no |
| (`TIME_ZONE` not set) | `__also__ = ["TIME_ZONE"]`<br>`TIME_ZONE = "Europe/Copenhagen"` | yes |
