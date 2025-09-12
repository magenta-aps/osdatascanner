# `adminapp/fixtures/`

The files in this folder define objects that can be loaded into the
OSdatascanner administration system's database using the `loaddata`
management command.

## Reserved primary keys

The following ranges of primary keys are set aside for use by particular files
in this folder:

* `os2datascanner.Rule`, primary keys 9990100 to 9990199 inclusive

  Reserved for `rules-sbsys.json`.
