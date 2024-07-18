def pre_mutation(context):
    # Change the path here to the path of the tests you want to do mutation
    # testing on. Remember to change the [mutmut]-settings in setup.cfg as well.
    path = "tests/test_miniscanner.py"
    module = "admin"
    context.config.test_command = f"docker compose exec {module} pytest {path}"

    # Some things we don't care about -- log messages and help text, stuff like that.
    exceptions = (
        # Logging messages
        'log.',
        'self.stdout.write(',
        # Other
        'metavar=',  # metavars of management commands
        'help=',  # help text
        'help = __doc__',  # more help text
    )
    line = context.current_source_line.strip()
    if line.startswith(exceptions):
        context.skip = True
