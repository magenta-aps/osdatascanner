# Development environment

## TL;DR

To get a development environment to run, follow these steps:

1.  Clone the repo and start the containers:

         git clone git@git.magenta.dk:os2datascanner/os2datascanner.git
         cd os2datascanner
         source build_env.sh # exports git variables for build arguments
         docker-compose pull # pre-fetches images to avoid building locally
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

- `code/src/os2datascanner/projects/admin/locale/`
- `code/src/os2datascanner/projects/admin/adminapp/migrations/`
- `code/src/os2datascanner/projects/report/locale/`
- `code/src/os2datascanner/projects/report/reportapp/migrations/`

If you want the `django-admin shell_plus` commands to record command-line
history (which you probably do in the development environment), you should also
run `chmod -R o+w` for the following locations:

- `dev-environment/admin/ipython/`
- `dev-environment/report/ipython/`


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
docker-compose run explorer pytest --color=yes /code/src/os2datascanner/engine2/tests
docker-compose run report pytest /code/src/os2datascanner/projects/report/tests
```

The admin and report projects can also be run with django test:
```bash
docker-compose run admin python -m django test os2datascanner.projects.admin.tests
docker-compose run report python -m django test os2datascanner.projects.report.tests
```

Please note that the engine tests can be run using any of the five pipeline
services as the basis, but a specific one is provided above for easy reference.

### Mutation testing

We utilize [mutmut](https://pypi.org/project/mutmut/) to do 
[mutation testing](https://en.wikipedia.org/wiki/Mutation_testing) of our test 
suite.

In a nutshell, mutation testing works by introducing small changes (mutations)
to some place in the code, then running relevant tests to make sure _some_ 
tests correctly _fail_ with the mutation present. If no tests fail, the 
sensitivity of the tests are likely too low.

Mutmut is executed locally, so it must be installed first:

```
pip install mutmut
```

The desired settings are configured in the files `setup.cfg` under `[mutmut]`
and `mutmut_config.py`.

When all settings are configured, mutation testing is run with

```
mutmut run
```

## Benchmark

Like the test-suite, the engine also has a benchmarking suite, which is run
automatically as a part of the CI pipeline. It can be run manually as well
with `pytest` due to the `pytest-benchmark` fixture.

To run the benchmarks execute the following command:
```bash
docker-compose run explorer pytest --color=yes --benchmark-only /code/src/os2datascanner/engine2/tests/benchmarks
```

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


### IDE Debugging

It is possible to debug problems or follow data flows in the code using
breakpoints via an IDE. This section describes this procedure for PyCharm. The
overall procedure is as follows:
1. Start the entire Docker Compose stack.
2. Stop the component you wish to debug.
3. Start the component you wish to debug in PyCharm.

We will here use the `explorer` component as an example for a file scan using
the Samba service - if you perform the procedure on another component and for
another source, the files and configuration changes below may have to be
adjusted accordingly, but the overall principle should be the same.

In the `explorer` case, two configuration changes are required: 1) the AMQP
hostname and port and 2) the Samba UNC. The former can be changed by creating
a file similar to `os2datascanner/dev-environment/engine/dev-settings.toml` and
the latter can be changed directly in the admin module in the browser.

The complete list of steps to get it up and running are the following:

1. Create a replacement file for
   `os2datascanner/dev-environment/engine/dev-settings.toml` with this content
   (only the `AMQP_HOST` and `AMQP_POST` have changed):

        secret_value = "THIS VALUE IS NOT SECRET"
       
        [amqp]
        # Nested amqp settings are picked up by the common amqp utility module
        AMQP_HOST = "localhost"
        AMQP_PORT = 8072
        AMQP_USER = "os2ds"
        AMQP_PWD = "os2ds"
       
        # timeout for requests (in seconds)
        timeout = 20
        ttl = 25
   
    Assume we save this file at `/tmp/my-dev-settings.toml`.

2. Start the Docker Compose stack with (double check that you are using the
   latest version of `docker-compose.yml` where the Docker RabbitMQ port 5672
   has been exposed as port 8072 on `localhost`):
   
        $ docker compose up -d

3. Stop the `explorer` service:

        $ docker compose stop explorer

4. Run the usual `quickstart_dev` commands as described above.
5. Login to the admin module and navigate to the
   [Filescanner](http://localhost:8020/filescanners/). Press the "Edit"
   button for the "Lille Samba" and update the `UNC` to
   `//localhost:8139/e2test` (remember to save).
6. (This step is not required for IDE debugging, but it serves as a command
   line example - adjust accordingly to use `pdb`). Activate the Python
   virtual environment (assuming this has already been created and that Python
   requirements have been installed) and navigate to the `src` folder:

        $ cd path/to/os2datascanner
        $ source venv/bin/activate
        $ cd src
        $ OS2DS_ENGINE_USER_CONFIG_PATH=/tmp/my-dev-settings.toml \
          python -m os2datascanner.engine2.pipeline.run_stage explorer

    The scanner should work as usual, and you can start a scan with a locally
    running (non-Docker) `explorer`.

7. For using the PyCharm IDE you will need to create a run/debug configuration
   corresponding the Python command in the previous step. In PyCharm, click the
   "Run configurations" dropdown and click "Edit Configurations...". Click the
   "+" button (top left corner) and add a new "Python" configuration. Edit the
   configuration to match the Python command above as seen in this screenshot
   (make sure to set module name and parameters, environment variables and
   the working directory):

    ![Run Configuration](./run_conf.png)

8. A debug session can now be started - add some breakpoints and start the run
   using the "Debug" button next to the selected (explorer) run configuration
   in the top right corner. You should be able to follow the flow of data
   through the code, inspect variables and objects and step through the code.

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

-   `datasynth`: a webserver that generates websites based on url configuration.
    If you want to use a customized websource for testing, you can also go to:
    `http://0.0.0.0:5010/websource` and add query parameters to define your websource.
    the site will respond with a reference to a web site which is randomly generated.
    the parameters allowed are: size (in bytes), sub_files, seed,
    matches( ie. `matches={"match":amount}`), and depth. The generated sources are
    available to the host by replacing `datasynth` with `localhost` or `0.0.0.0`.

Note: Due to limitations in the way datasynth is configured to generate data, 
scanning a datasynth web-source with sitemap can lead to more matches than expected.

A generated web-source can contain matches scattered throughout subfiles(links to other pages/files), 
but the generated sitemap currently cannot take into account how many matches are located at the root/index page. 
This means that when scanning with a sitemap, datascanner will find all the matches on the landing page and all the matches created
with the sitemap, leading to more matches found than configured in the source params.
So when creating tests with datasynth using a sitemap keep this in mind. The easy
workaround is to not count matches found on the landing page. (landing_page.matches + sitemap.matches)


-   `mailhog`: a SMTP-server for testing purposes.
    web interface available at `http://localhost:8025/`.

### Connecting to the host

Sometimes it can be helpful to start a temporary server on your computer and
scan it from the Docker environment. To do that, just configure your scan to
use the IP address `172.17.0.1`: inside a Docker container, this address refers
to the host machine. (Some Windows and Mac editions of Docker also define a DNS
name for the host, `host.docker.internal`.)

Note that you might need to adjust your firewall to allow connections from the
virtual Docker networks. By default, these are all given addresses in the range
`172.*.*.*`, equivalent to `172.0.0.0/8` in CIDR notation. Using the `ufw`
command, for example, you might do something like this to allow all connections
from that range:

    `ufw allow from 172.0.0.0/8 to any`

### Using header exchanges and `queue_suffix` for parallel execution

A **worker** process can either be "owned" by an organisation or serve all organisations.
Having **worker** processes that are owned by different organisations, allows the engine
to run multiple scanner jobs in parallel (one pr. organisation). To use this feature,
you can either start a **worker** with the `--queue-suffix` flag:

```sh
python3 run_stage.py worker --queue-suffix <name_of_organisation>
```

OR set the `QUEUE_SUFFIX` environment variable like this (inherits from host):

```sh
# in bash
export QUEUE_SUFFIX = '<name_of_organisation>'
docker-compose up -d --build worker
```

Note that, if all workers belong to organisation A and you start a scanner job belonging
to organisation B, then no data will be scanned as no workers are available.

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

The following `profiles` are available: `ldap`, `sso`, `api`, `metric` and
`ai`.

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
OS2datascanner, we create a "User Federation" in Keycloak which imports data from e.g. Active Directory. 
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

### `--profile cron`

The `cron` profile starts two instances of [`supercronic`](https://github.com/aptible/supercronic),
one for the admin system and one for the report module, for testing that task
scheduling works properly.

These services are not enabled by default because settings that make sense in
production ("start this scanner at midnight", "send emails out every day at
10am", or "synchronise this organisation every day at 3pm") don't normally make
sense in the development environment.

### `--profile ai`

The `ai` profile starts the `ai-classifier` helper component, which performs
additional classification on the results of certain special CPR and regex
matches.

## Setting up OS2mo-importjob

OS2datascanner's development environment incorporates OS2mo organisational import
functionality. To test functionality, it is required to clone the Git-repository.

1. Clone the repo and start the OS2mo-project
    ```
    git clone https://github.com/OS2mo/os2mo.git
    cd os2mo
    ```
2. Add a docker-compose.override.yml file in the root of the OS2mo project, and add the code: 
    ```
    services:
      mo:
        environment:
          OS2MO_AUTH: "false"
    ```
    This allows you to access localhost:5001, using the user admin/admin. 
    
3. Run the container with:
    ```
    docker-compose up --build
    ```

4. Go to http://localhost:5000/auth/admin/master/console/#/mo/clients
5. Enter username and password "admin"
6. Select the client "dipex"
7. Go to tab "Credentials"
8. Copy the "Secret". You can regenerate a new secret here as well
9. Open the dev-settings.toml file in the OS2datascanner-project and scroll down to "[os2mo]"  
10. Change OS2MO_CLIENT_ID to "dipex" and OS2MO _CLIENT_SECRET to the secret
11. Start the OS2datascanner-project. Use the "--build" flag to let the updated 
dev-settings.toml-file take effect.
    ```
    docker-compose up --build
    ```

12. Go to http://localhost:8020/admin/core/client/
13. Change your "client"-object in the Django-admin page to both allow "support of 
structured organizations" and "importservice (OS2mo)"

You can now perform an OS2mo-import from the organizations-page, http://localhost:8020/organizations/.

`Note:` If you would like to run a larger fixture than the default "Kolding kommune"-fixture, start by emptying the databases in both containers with the command:

    docker-compose down -v --remove-orphans

Repeat previous command on both containers until you no longer receive errors on either of the projects, like:

    error while removing network: network os2mo_default id <id> has active endpoints

When you get this warning, the database is empty:

    WARNING: Network os2mo_default not found.

Then build both containers again, but build the OS2mo-container with the command:

    FIXTURE=aalborg docker compose up --build


## Prerequisites for setting up an Office 365 scannerjob

To be able to scan files and emails from Office 365 using OSdatascanner, 
you'll need to complete the following steps:

1. Register an Azure Application:  
    Begin by registering an Azure Application in your Azure portal. This 
    application will allow OSdatascanner to retrieve data from your Office 365 
    environment.

2. Grant Required Permissions:  
    Once the Azure Application is registered, ensure that it has been granted 
    the necessary permissions to access Office 365 data.

3. Provide OSdatascanner with Application Details:  
    After setting up the Azure Application and assigning the required permissions, 
    you'll need to update OSdatascanner with the application's details.

    Open the *dev-settings.toml* file for both the admin and report folders.

    Locate the section labeled [msgraph] and insert the following values from your
    Azure Application:

    * Application ID (Client ID)
    * Directory ID (Tenant ID)
    * Client Secret

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
should not have a value higher than 7.

Linting can be checked locally by installing:
`pip install pyproject-flake8 flake8-bugbear flake8-cognitive-complexity flake8-expression-complexity`
and the running:
`pflake8 src`


Templates : Template linting is done with djLint and will fail hard if not being complied with.
check https://www.djlint.com/docs/getting-started/ for a list of all options/rules djLint 
uses. 

### Git hooks

developers can install the precommit framework to run automated pre-commit test to tell them 
if they will fail the linter-jobs.
The pre-commit framework can be installed like this:

`pip install pre-commit`,

`pre-commit install`.

to skip hooks a single time use the `--no-verify` option on your git commit command.
