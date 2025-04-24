# The `_staging` module

This folder is intended as a test and staging area for extensions to the
OSdatascanner data access model. Code in this folder is allowed to be a bit
more experimental, and `Rule`s and conversions can be freely mixed with
`Source`s and `Handle`s.

Importing anything from this module will print a warning to the console:

```
2025-04-24T07:30:23.422625Z [warning  ] importing experimental data access
model extensions [engine2] func_name=<module> module=__init__
```

Due to the way `engine2` classes automatically contribute themselves to central
registries, unconditionally importing anything from this module (outside of the
test suite) is forbidden. Conditional imports are okay as long as they're
disabled by default:

```python
# Forbidden
from os2datascanner.engine2.model._staging import something

# Allowed
if settings.engine2["model"]["something"].get("enabled", False):
    from os2datascanner.engine2.model._staging import something
```

## A few things to bear in mind

* Code in this module doesn't have to _work_, but it must still pass the CI
  pipeline's normal checks for code quality.

* Similarly, code in this module isn't required to have tests at first, but
  developers should start writing these as the code settles down, and they
  should be in place by the time the code moves to the normal model.

* Code in this module should follow the usual rules for JSON representations,
  in particular preserving backwards compatibility with old representations.

* Don't make `Scanner` subclasses in the administration system for code in
  this module. (It doesn't make sense to litter the admin system's migration
  history with tweaks and adjustments for a model that's still in flux.)

  If you want to see how matches are treated by the report module, use the API
  server to run test scans, and use the report module's
  `/admin/os2datascanner_report/documentreport/import/` endpoint to import the
  resulting messages.
