## Translations 

!!! note 
    This is one of the places where you may frequently find yourself struggling with
    missing permissions. Consult the [Missing Permissions](missing-permissions.md) section if you
    do.

The mother tongue of the project is English, but with the requirement of everything being available with
Danish translations.

So, during your development, you should always use English language, but keep your translations compiled (meaning in use), 
to verify that Danish translations are available and correct.

For the most part, our user facing strings are from our Django projects, which then use Django's translation support.

For more in depth of that, refer to their documentation [here](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/)

Throughout the project, there are several translation files:

### Admin & Report module (the regulars)

These are for the most part fairly straight forward Django projects, containing translation files
for Python and template (.html) code `django.po`, and Javascript `djangojs.po`

These files are located here:

**Admin:**

`os2datascanner/projects/admin/locale/da/LC_MESSAGES/django.po`  
`os2datascanner/projects/admin/locale/da/LC_MESSAGES/djangojs.po`

**Report:**

`os2datascanner/projects/report/locale/da/LC_MESSAGES/django.po`  
`os2datascanner/projects/report/locale/da/LC_MESSAGES/djangojs.po`

If you've marked something up for translation, you should then first run one of below commands.

For Python or template translations, run:
`docker compose exec <admin|report> django-admin makemessages --all`


For Javascript translations, run:

`docker compose exec <admin|report> django-admin makemessages -d djangojs --all`

That should update corresponding `django.po` or `djangojs.po` file(s).

It is now your job to check out these for changes, and add your translation string.

When you do, it is important that you check for potential `fuzzy` marked translations. These need
manual correction, as they mean that Django tried to be clever, but couldn't _really_ make out what to do.
Failing to correct these (by deleting the fuzzy mark and ensuring correct translation), will render the translation invalid/unused.


### Shared Django apps

We also have our "shared" apps, located at:

`os2datascanner/projects/shared/locale/da/LC_MESSAGES/django.po`  
`os2datascanner/projects/grants/locale/da/LC_MESSAGES/django.po`  
`os2datascanner/core_organizational_structure/locale/da/LC_MESSAGES/django.po`

These are slightly more convoluted to generate `django.po` changes for, as they're part of the admin and report projects,
but not _really_ anyway - they can be symlinks or mounted in and installed at runtime, etc.

So, to do this, you may need to jump into a running `admin` or `report` container, navigate to one of the shared app's path and borrow
`manage.py` from `admin` or `report`.

In one line, using `docker compose exec --workdir` option, it looks something like below.

**Grants:**

```bash
docker compose exec --workdir /code/src/os2datascanner/projects/grants admin ../admin/manage.py makemessages --all
```

**Shared:**
```bash
docker compose exec --workdir /code/src/os2datascanner/projects/shared admin ../admin/manage.py makemessages --all
```

**Core Organizational Structure:**

```bash
docker compose exec --workdir /code/src/os2datascanner/core_organizational_structure admin ../projects/admin/manage.py makemessages --all
```


### Engine2 translations

The engine isn't a Django project, so, it doesn't work _exactly_ the same, but we've tried to implement
a way that almost makes it feel like it, by creating a helper script `manage.sh`, that behaves more or less like the Django one.

You'll find the translations at:
`os2datascanner/engine2/locale/da/LC_MESSAGES/osds_engine2.po`

To generate translations, you need a running engine container, f.e. a `worker`.

Then, run the following:

```bash
docker compose exec worker engine2/locale/manage.sh makemessages
```



### Django Compiling messages (Enabling translation)

**For admin / report**:
When the applications are already `up` and running as you can
(re)compile the translations with the command:

    docker compose exec <report|admin> django-admin compilemessages

**For the shared apps:**

We need the same kind of trickery, just with `compilemessages` instead.

F.e.:

```bash
docker compose exec --workdir /code/src/os2datascanner/projects/grants admin ../admin/manage.py compilemessages
```


Refreshing the page, you should see your new translations in effect.

### Engine2 Compiling messages (Enabling translation)

Run:

```bash
docker compose exec worker engine2/locale/manage.sh compilemessages
```