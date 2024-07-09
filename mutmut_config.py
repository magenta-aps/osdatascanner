def pre_mutation(context):
    # Change the path here to the path of the tests you want to do mutation
    # testing on. Remember to change the [mutmut]-settings in setup.cfg as well.
    path = "tests/test_miniscanner.py"
    module = "admin"
    context.config.test_command = f"docker compose exec {module} pytest {path}"

    # We don't test for log statements, so skip those lines during mutation.
    line = context.current_source_line.strip()
    if line.startswith('log.'):
        context.skip = True
