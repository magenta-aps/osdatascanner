## Testing


### Unit tests

Each module has its own test-suite. These are run automatically as part of the
CI pipeline, which also produces a code coverage report for each test-suite.

During development, the test can be run using the relevant Docker image for
each module. As some of the tests are integration tests that require auxiliary
services - such as access to a database and/or message queue - we recommend
using the development `docker compose` set-up to run the tests, as this takes
care of the required settings and bindings.

To run the test-suites using docker compose and PyTest, on running services:

```bash
docker compose exec admin pytest /code/src/os2datascanner/projects/admin
docker compose exec explorer pytest --color=yes /code/src/os2datascanner/engine2/tests
docker compose exec report pytest /code/src/os2datascanner/projects/report/tests
```

The engine tests can be run using any of the pipeline
services as the basis, but a specific one is provided above for easy reference.

You can also opt for one-off containers f.e. like:

`docker compose run --rm admin pytest /code/src/os2datascanner/projects/admin`

Be aware that codepaths aren't _exactly_ the same inside the containers, as they are on your machine.
That's why you must point at `/code/..` when running them through one of the containers.

**Hints**:

- You can disable warnings using the flag `--disable-warnings`
- Run a specific test in provided file by using flag `-k <test_name>`


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

### Benchmark

Like the test-suite, the engine also has a benchmarking suite, which is run
automatically as a part of the CI pipeline. It can be run manually as well
with `pytest` due to the `pytest-benchmark` fixture.

To run the benchmarks execute the following command:
```bash
docker compose run explorer pytest --color=yes --benchmark-only /code/src/os2datascanner/engine2/tests/benchmarks
```