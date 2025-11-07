# `adminapp/fixtures/`

The files in this folder define objects that can be loaded into the
OSdatascanner administration system's database using the `loaddata`
management command.

| Fixture | Test? | Prod? | Contents |
| ------- | ----- | ----- | -------- |
| `rules-sbsys` | ✅ | ✅ | | Our collection of SBSYS rules we update and maintain |
| `org-sbsys` | ✅ | ❎ | A test organisation for SBSYS rules |

## Reserved primary keys

The following ranges of primary keys are set aside for use by particular files
in this folder:

* `os2datascanner.Rule`, primary keys 9990100 to 9990199 inclusive

  Reserved for `rules-sbsys.json`.
* `os2datascanner.Rule`, primary key 8880100

  Reserved for `rules-cpr-da.json`
* `os2datascanner.RuleCategory`, primary keys 1001 and 1002

  Reserved for `rules-cpr-da.json`