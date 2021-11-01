# Access to the test-server

The testserver follows `head` of the main branch and can be reached at

- http://test.os2datascanner.dk
- http://test-admin.os2datascanner.dk

Either login with the azure account `datascanner-admin@magneta43.onmicrosoft.com`
(password found in bitwarden) or append `/admin` to the urls, in order to login
with the `test[-admin].os2datascanner.dk` credentials also found at
https://vault.bitwarden.com

The server is provisioned by 
[salt](https://labs.docs.magenta.dk/projects/os2ds/os2ds_state.html)
where [specific
configuration](https://git.magenta.dk/labs/salt-automation/-/blob/master/salt/pillar/customers/magenta/os2ds/test_web.sls)
is set. At each merge to the main branch, a gitlab
runner will push docker images of `report`, `admin`, `engine` and `api` to
dockerhub, and then run `Deploy Test` to get the salt minions to pull the new
images. 

The initial server configuration(bootstrapping) is done by
[terraform](https://labs.docs.magenta.dk/projects/os2ds/saas_tf.html)
which defines [server
resources](https://git.magenta.dk/labs/salt-automation/-/tree/master/terraform/os2ds/test-servers),
dns and install salt minions.


## Shell access to the servers

The test-server is hosted at Google Cloud and shell access requires the
[gcloud cli](https://labs.docs.magenta.dk/google-cloud-platform/gcloud.html)

when initializing with `gcloud init`, select the primary project as
`magenta-labs-os2ds-development`.


list all virtual servers within the project
```sh
gcloud compute instances list --project magenta-labs-os2ds-development
```

### dump the database

The following shows how to logon to the `test-web`, dump the
database and copy it to a local machine
```sh
gcloud compute ssh --project=magenta-labs-os2ds-development --zone=europe-west4-b test-web

# great, we're in. Become root
sudo -s
# all datascanner containers are available here
cd /opt/docker/os2ds_web
docker-compose exec db pg_dumpall -U postgres --clean > test_db.sql
gzip test_sb.sql
chown xxx_magenta_aps_dk. test_db.sql.gz
mv test_db.sql.gz /home/xxx_magenta_aps_dk/
^D^D

# back at localhost -- copy and extract the dump
gcloud compute scp --project=magenta-labs-os2ds-development --zone=europe-west4-b test-web:~/test_db.sql.gz ~/Downloads
gunzip -k ~/Downloads/test_db.sql.gz

cd path/to/DS
# clear current database by removing volumes
docker-compose down -v
docker-compose up -d db
docker-compose exec -T db psql -U postgres < ~/Downloads/test_db.sql

# change user and permissions and rename the db.
# test-web have the db users os2ds_{report,admin}, whereas we use
# os2datascanner_{report,admin}_dev
docker-compose exec db psql -U postgres

alter database os2ds_admin rename to os2datascanner_admin;
alter database os2ds_report rename to os2datascanner_report;

# connect to db
\c os2datascanner_admin
reassign owned by os2ds_admin to os2datascanner_admin_dev;
\c os2datascanner_report
reassign owned by os2ds_report to os2datascanner_report_dev;

# change password of user postgres. Change it to os2datascanner as set in 
# dev-environment/db.env
\password postgres
```

The `DocumentReport` table might be too large to test migrations in a practical
way. Move it to a backup-table and created a new, smaller `DocumentReport`

```sh
# move/copy content of DocumentReport to backup table
\c os2datascanner_report
# try to rename
alter table os2datascanner_report_documentreport rename to doc_report_bak;

# othervise copy and truncate
create table doc_report_bak as (select * from os2datascanner_report_documentreport);
truncate os2datascanner_report_documentreport cascade;

# create a new DocumentReport with desired content
create table os2datascanner_report_documentreport as
((SELECT * FROM doc_report_bak where sort_key = '.' LIMIT 10) union
(SELECT * FROM doc_report_bak where sort_key != '.' LIMIT 10));

# or insert into it
insert intoos2datascanner_report_documentreport (...);

# see how many entries we got
select count(*) from os2datascanner_report_documentreport;

# use `extended_display`(\x) to show columns as key,value pairs
# usefull when some columns take too much screen "real-estate"
\x  # maybe \x auto, if you prefer
select * from os2datascanner_report_documentreport limit 10;
```


### debug the engine

The following shows how to logon to the `test-engine` server, set a
`breakpoint()` and debug the code running in the container

```
gcloud compute ssh test-engine-0 --project=magenta-labs-os2ds-development --zone=europe-west4-b
sudo -s
cd /opt/docker/os2ds_engine
```

`pdb` expect a usable terminal with a TTY. Add the following to the `explorer` definition in `docker-compose.yml`

```
    stdin_open: true
    tty: true
```

then re-up the container to reload the config, login as root to install `pdbpp`,
set a breakpoint and attach to the running container

```
docker-compose up -d

docker-compose exec -u root <container> bash
apt install neovim
pip install pdbpp
# set breakpoint() using vim
vim src/os2datascanner/engine2/
^d

# dont stop the container, the changes are not persistant
docker-compose restart <container>
docker-compose logs -f --tail 100 <container>  # check things are starting as expected
docker ps  # to get container id
docker attach <container_id>

# when python reach the breakpoint, toggle to sticky mode and step through the code
sticky

# when done, detach from the container without stopping it
^p ^q

# discard all changes to the container
docker-compose stop
docker-compose up -d
```

Note that `^` should be read as `Ctrl`.
