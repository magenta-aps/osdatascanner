def pre_mutation(context):
    # Change the path here to the path of the tests you want to do mutation
    # testing on. Remember to change the [mutmut]-settings in setup.cfg as well.
    path = "organizations/tests/test_account_outlook_setting.py"
    context.config.test_command = "docker compose exec report pytest " + path

    # We don't test for log statements, so skip those lines during mutation.
    line = context.current_source_line.strip()
    if line.startswith('log.'):
        context.skip = True
