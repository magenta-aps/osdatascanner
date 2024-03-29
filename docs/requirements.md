# Requirements

## Dependency tree

To avoid having to repeat shared requirements in several files, both system
requirements and python requirements have been split into several files
according to the "inheritance" tree below:

```
                                                  ------- api
                                                /
              ------------------------- engine -
            /
    common -                    ------- admin
            \                 /
              ------- django -
                              \
                                ------- report
```


## Python dependency tree

For each of the OS²datascanner components (**engine**, **admin**, **report**), a
`requirements-<component>.txt` file is generated using `pip-tools` and `.in`-files.
The `.in`-files used by `pip-tools` are organized according to the "inheritance"
tree below, and each `.in`-file includes all packages from its "parent file":

```
                                                  ------- api
                                                /
              ------------------------- engine -
            /
    common -                    ------- admin
            \                 /
              ------- django -
                              \
                                ------- report

                                        test

                                        lint
```

The requirements for the two Django components (**admin** and **report**) are
restricted by the versions required by the **engine**-component due to code
imports.

Furthermore, requirements for testing and linting are to be used by all three
components; both `test` and `lint` requirements are constrained by
(but does not include!) the versions from the `engine`, `admin`, and `report`
`.txt`-files, while `lint` requirements are **additionally** constrained by
the versions required by `test`.

To (re)generate the necessary `requirements-*.txt`-files during development, a
`Dockerfile` and `docker-compose.yml` have been provided in the
`./dev-environment/`-folder. The generated Docker image contains all system
dependencies, thus ensuring that `pip-tools` pin packages to the correct
versions. To generate the
`../requirements/python-requirements/requirements-*.txt`-files, simply run
`docker-compose up` from the `dev-environment/` folder.
