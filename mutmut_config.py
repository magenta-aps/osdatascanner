def pre_mutation(context):
    context.config.test_command = "docker-compose exec admin django-admin test "\
                                  "os2datascanner.projects.admin.tests.test_admin_collector"
