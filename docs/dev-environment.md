# Development environment

## TL;DR

To get a development environment to run, follow these steps:

1.  Clone the repo and start the containers:

         git clone git@git.magenta.dk:os2datascanner/os2datascanner.git
         cd os2datascanner
         docker-compose up -d

    You can now reach the following services on their respective ports:

    - Administration module: http://localhost:8020
    - Web interface for message queues: http://localhost:8030
    - Report module: http://localhost:8040

2. Create users and other initial setup with the [quickstart
   commands](../management-commands). The commands will describe what they
   do in more detail, but in short they create users named "dev" with the
   password "dev" and setup a scan source.

         docker-compose exec admin django-admin quickstart_dev
         docker-compose exec report django-admin quickstart_dev

3.  Start a scan:

    1.  Log into the administration module with the newly created superuser at
        http://localhost:8020

    2.  Go to "Filescans" at http://localhost:8020/filescanners/

    3.  Start the scan by clicking the play button and confirming your choice.

4.  Follow the engine activity in RabbitMQ (optional):

    Credentials for the message queue web interface can be found in
    here in `dev-environment/rabbitmq.env`.

    1.  Log into the web interface for RabbitMQ at http://localhost:8030
    2.  Queue activity is available on the `Queues` tab.

5.  See the results:

    1.  Log into the report module with the newly created superuser at
        http://localhost:8040


## Missing permissions in development environment

During development, we mount our local editable files into the docker
containers which means they are owned by the local user, and **not** the user
running inside the container. Thus any processes running inside the container,
like management commands, will not be allowed to create or update files in the
mounted locations.

In order to fix this, we need to allow "others" to write to the relevant
locations. This can be done with `chmod -R o+w <path>` (`o` is for "other
users", `+w` is to add write-permissions and `-R` is used to add the
permissions recursively down through the file structure from the location
`<path>` points to).

The above is necessary whenever a process needs write permissions, but should
always be done for the following locations:

- `code/src/os2datascanner/projects/<module>/locale/`
- `code/src/os2datascanner/projects/<module>/<module>app/migrations/`

`<module>` being either `admin` or `report`.

**NB!** Git will only save executable permissions, which means that granting
other users write permissions on your local setup, will not compromise
production security.


## Interesting files for development

We've included some interesting files to scan in `dev-environment/data`.
Multiple files in the directory include CPR numbers, but because of context
only 4 should be expected to be found from a scan.

`samba` and `nginx` both expose this folder.

Please expand the folder, if you have something interesting to add.


## Tests

Each module has its own test-suite. These are run automatically as part of the
CI pipeline, which also produces a code coverage report for each test-suite.

During development, the test can be run using the relevant Docker image for
each module. As some of the tests are integration tests that require auxiliary
services - such as access to a database and/or message queue - we recommend
using the development docker-compose set-up to run the tests, as this takes
care of the required settings and bindings.

To run the test-suites using docker-compose and PyTest:
```bash
docker-compose run admin pytest /code/src/os2datascanner/projects/admin
docker-compose run explorer pytest --color=yes src/os2datascanner/engine2/tests
docker-compose run report pytest /code/src/os2datascanner/projects/report/tests
```

The admin and report projects can also be run with django test:
```bash
docker-compose run admin python -m django test os2datascanner.projects.admin.tests
docker-compose run report python -m django test os2datascanner.projects.report.tests
```

Please note that the engine tests can be run using any of the five pipeline
services as the basis, but a specific one is provided above for easy reference.


## Translations (i18n)

When the applications are already `up` and running as described above, you can
recompile the translations with the command:

    docker-compose exec (report|admin) django-admin compilemessages

Refreshing the page, you should see your new translations.


## Debugging

### Shell access

To access a shell on any container based on the OS2datascanner module
images, run

    docker-compose {exec|run} <container name> bash


### Printing Stacktraces

A stacktrace is printed to `stderr` if pipeline components receive `SIGUSR1`.
The scan continues without interuption.

The components must be startet using `run_stage`

Running the engine locally,

    python -m os2datascanner.engine2.pipeline.run_stage worker ps aux | grep os2datascanner
    kill -USR1 <pid>

Running the engine in Docker, using the namespace sharing between localhost and
docker

    docker top os2datascanner_worker_1 # get the `<pid>`of the python process
    kill -USR1 `<pid>`
    docker logs os2datascanner_worker_1


### Removing messages from the queue

If a malformed message get published to the queue, the `pipeline_collector`s or
engine components might crash when trying to parse the message.

And since messages are only removed from the queue after parsing succeeded and
acknowledged by the consumer (the queues are persistent; restarting `RabbitMQ`
does not clear the queues), you might end up in a crash-loop.

There are two ways to clear the queues.
1. use the web-interface to `RabbitMQ`, as described in [step 4 in TL;DR:](## TL;DR:),
   to `Purge Messages`
2. or from the CLI: `docker-compose exec queue rabbitmqctl purge_queue os2ds_scan_specs`


## docker-compose

You can use `docker-compose` to start the OS2datascanner system and its runtime
dependencies (PostgreSQL and RabbitMQ).

A `docker-compose.yml` for development is included in the repository. It
specifies the settings to start and connect all required services.


### Services

The main services for OS2datascanner are:

-   `admin_frontend`: Only needed in development.

    Watches the frontend files and provides support for rebuilding the
    frontend easily during the development process.

-   `admin`: Reachable on: http://localhost:8020

    Runs the django application that provides the administration
    interface for defining and managing organisations, rules, scans etc.

-   `explorer`: Runs the **explorer** stage of the engine.

-   `processor`: Runs the **processor** stage of the engine.

-   `matcher`: Runs the **matcher** stage of the engine.

-   `tagger`: Runs the **tagger** stage of the engine.

-   `exporter`: Runs the **exporter** stage of the engine.

-   `report_frontend`: Only needed in development.

    Watches the frontend files and provides support for rebuilding the
    frontend easily during the development process.

-   `report`: Reachable on: http://localhost:8040

    Runs the django application that provides the interface for
    accessing and handling reported matches.

-   `report_collector`: Runs the **collector** service that saves match
    results to the database of the report module.

These depend on some auxillary services:

-   `db`: Runs a postgres database server based on [the official postgres
    docker image](https://hub.docker.com/_/postgres/).

-   `queue`: Runs a RabbitMQ message queue server based on [the official
    RabbitMQ docker image](https://hub.docker.com/_/rabbitmq/) , including a
    plugin providing a web interface for monitoring (and managing) queues and
    users.

    The web interface can be reached on: http://localhost:8030

-   `samba`: a Samba service that serves up some test files in a shared folder
    called `e2test`. This can be useful to test the file scanner.

    The Samba server is available as `samba:139` inside the Docker environment
    and `localhost:8139` on the host machine. The full UNC of the shared folder
    in the Docker environment is `//samba/e2test`.

    The Samba server doesn't require a workgroup name, but it does require a
    username (`os2`) and password (`swordfish`).

    Thus from the host: `smbclient -p 8139 -U os2%swordfish //localhost/e2test`

-   `nginx`: a webserver that exposes the same folder as `samba`.

-   `mailhog`: a SMTP-server for testing purposes. 
    web interface available at `http://localhost:8025/`.


### profiles

The `docker-compose.yml` use `--profiles` which requires version
`docker-compose > 1.28`.

To start the core components(`engine`, `report`- and `admin` interface, `db`
and `queue`) of datascanner, use

```sh
docker-compose up -d
```

To start a service behind a `profiles` flag, use

```sh
docker-compose --profile api up -d
```

The following `profiles` are available: `ldap`, `sso`, `api` and `metric`.

The development config files are stored in `os2datascanner/dev-environment/`


#### `--profile ldap`

The `ldap` profile defines a Keycloak instance and connected Postgres database,
as well as a OpenLDAP server and admin interface.

Be sure to enable import and structured org. features on the client in the admin module's django admin page.


#### Keycloak instance

Interface available at `localhost:8090` on the host machine.

By default, login credentials will be `admin:admin`

The Keycloak instance is automatically configured by a mounted `realm.json` file.
This file contains configurations for a client in the "Master Realm" with appropriate permissions
to perform actions such as creation of new realms, users and user federation connections.

In `dev-settings.toml` appropriate settings for the **KEYCLOAK_BASE_URL**, **KEYCLOAK_ADMIN_CLIENT** and 
**KEYCLOAK_CLIENT_SECRET** are set.

The purpose of the Keycloak instance is to use its User Federation support. When an LDAP configuration is set in
OS2Datascanner, we create a "User Federation" in Keycloak which imports data from e.g. Active Directory. 
Finally, we import this data to Django.


#### Setting up OpenLDAP

OS2datascanner's development environment incorporates the OpenLDAP server,
which should be used to work with the system's organisational import
functionality. Setting up OpenLDAP is a little complicated, though; even though
the "L" stands for "lightweight", LDAP is an old technology that doesn't *feel*
very lightweight.

We suggest two ways of defining an organisation in OpenLDAP:

* through the _phpLDAPadmin_ frontend, also included in the development
  environment. This is a fairly self-explanatory but clunky UI for much of
  LDAP's functionality; or

* through an external LDAP client program, such as those provided by the
  Ubuntu/Debian package `ldap-utils`.

If you wish to access the phpLDAPadmin it will be accessible on the host machine at `localhost:8100`

Credentials will be `cn=admin,dc=magenta,dc=test:testMAG`


##### External LDAP clients

The development environment's OpenLDAP server is also exposed to the host
system on port 387, the usual port for LDAP servers. That means it's fairly
easy to interact with it from outside the Docker universe.

LDAP has a standard text format, known as the _LDAP Data Interchange Format_,
for representing objects in the organisational hierarchy. We can define an
organisation in this format and then give it to a tool like `ldapadd` in order
to import it into the LDAP world:

```
$ cat <<END > organisation.ldif
dn: ou=Test Department,dc=magenta,dc=test
objectClass: organizationalUnit
ou: Test Department

dn: cn=Mikkel Testsen,ou=Test Department,dc=magenta,dc=test
objectClass: inetOrgPerson
cn: Mikkel Testsen
givenName: Mikkel
sn: Testsen
mail: mt@test.example

dn: cn=Hamish MacTester,ou=Test Department,dc=magenta,dc=test
objectClass: inetOrgPerson
cn: Hamish MacTester
givenName: Hamish
sn: MacTester
mail: hm@test.example
END
$ ldapadd -D cn=admin,dc=magenta,dc=test -w testMAG -f organisation.ldif 
adding new entry "ou=Test Department,dc=magenta,dc=test"

adding new entry "cn=Mikkel Testsen,ou=Test Department,dc=magenta,dc=test"

adding new entry "cn=Hamish MacTester,ou=Test Department,dc=magenta,dc=test"
```

## Setting up scans
This page describes how to set up and use the different scans.

### Web Scan

...

### File Scan

...

### Exchange Scan


An Exchange scan scans an organizations active directory (AD),
by looking through a AD server.

A developer can create their own LDAP server by following the instructions in: 
[LDAP](../dev-environment/#setting-up-openldap) and [LDAP-Profile](../dev-environment/#-profile-ldap).
When a server has been set up.

When the enviroment has been set up, simply log in with:
login DN: cn=admin,dc=magenta,dc=test
Password: testMAG

Then click the globe to the left that says `dc=magenta,dc=test` and create a `child entry`. 
Select `Generic: Organisational Unit` and give it a desired name. Commit it.
Now create a `Courier Mail: Account` the same way. Commit it.
Add as many users and organizational units as desired.

Then go to [organisations](http://localhost:8020/organizations/) and add an importservice.
```
protocol: ldap
connection url: ldap_server
username: cn=admin,dc=magenta,dc=test
password: testMAG

supplier: Other supplier
import based on: Organizational units

Classes for user-objects: inetOrgPerson
Search scope: whole subtree

username: mail
RDN: cn
UUID: uid
```

Now you can add a new Exchangescanner job:

``` 
URL: @magenta43dk.onmicrosoft.com
service-endpoint: https://outlook.office365.com/EWS/Exchange.asmx

user information: Use bitwarden to get the proper authentication.

then select the organizational units and desired rules.
```

### Google Drive Scan

...

### Office 365 Scan

...

### Gmail Scan

...

### SBSYS Scan

...


## Linting and static analysis

The coding standards below should be followed by all new and edited code for
the project.

To test any CI job, you can do so by running:
```
docker run -d \
    --name gitlab-runner \
    --restart always \
    -v $PWD:$PWD \
    -v /var/run/docker.sock:/var/run/docker.sock \
    gitlab/gitlab-runner:latest
```
then run 
`docker exec -it -w $PWD gitlab-runner gitlab-runner exec docker <job name>`

where job name could be "Lint Python".



Linting checks are applied for:

JS : Linting is done with JSHint and will fail hard if not being complied with.
check https://jshint.com/docs/options/ for a list of all options/rules jshint 
uses.

linting for specific lines or rules can be done with /* jshint -<error-code> */,
however a developer should write the reson for disabling a specific rule.


Python: Linting checks are done for python as well, the test are based on PEP 8 standards
implemented through flake8 and bugbear. Furthermore there are static code analyzers that 
evaluate the commited code based on three complexity metrics:

Cognitive complexcity: a metric for how readable a piece of code is. this can be reduced
by reducing nested loops and if -statements.

Cyclomatic complexity: a fancy way of saying how many paths your code can take, it helps us 
see how testable a piece of code is. Commonly a good cyclomatic number for a method would
be less than 15, when it reaches 16-30 this is normally a sign that the code is not easy 
to test and it should be considered reducing its complexity. 30 to 50 should be stricly 
prohibited.
Above 75 is an indicator for each change may trigger a 'bad fix'.
https://betterembsw.blogspot.com/2014/06/avoid-high-cyclomatic-complexity.html


Expressive complexcity: a way to measure how complex individual statements are. Ideally they 
should not have a a value higher than 7.

Linting can be checked locally by installing:
`pip install pyproject-flake8 flake8-bugbear flake8-cognitive-complexity flake8-expression-complexity`
and the running:
`pflake8 src`


