## Git hooks

developers can install the precommit framework to run automated pre-commit test to tell them 
if they will fail the linter-jobs.
The pre-commit framework can be installed like this:

```bash
pip install pre-commit
pre-commit install
```

to skip hooks a single time use the `--no-verify` option on your git commit command.

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

### JavaScript 

Linting is done with JSHint and will fail hard if not being complied with.
check https://jshint.com/docs/options/ for a list of all options/rules jshint 
uses.

Linting for specific lines or rules can be done with /* jshint -<error-code> */,
however a developer should write the reason for disabling a specific rule.


### Python 

Linting checks are done for python as well, the test are based on PEP 8 standards
implemented through flake8 and bugbear. Furthermore, there are static code analyzers that 
evaluate the commited code based on three complexity metrics:

### Cognitive complexity 

A metric for how readable a piece of code is. this can be reduced
by reducing nested loops and if -statements.

### Cyclomatic complexity

A fancy way of saying how many paths your code can take, it helps us 
see how testable a piece of code is. Commonly a good cyclomatic number for a method would
be less than 15, when it reaches 16-30 this is normally a sign that the code is not easy 
to test, and it should be considered reducing its complexity. 30 to 50 should be strictly 
prohibited.
Above 75 is an indicator for each change may trigger a 'bad fix'.

https://betterembsw.blogspot.com/2014/06/avoid-high-cyclomatic-complexity.html


### Expressive complexity: 

A way to measure how complex individual statements are. Ideally they 
should not have a value higher than 7.

### Templates

Template linting is done with djLint and will fail hard if not being complied with.
Check [djLint](https://djlint.com/docs/getting-started/) for a list of all options/rules djLint 
uses. 

