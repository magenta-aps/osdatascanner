import datetime
from uuid import UUID
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from os2datascanner.projects.admin.core.models import Client, Feature
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.models import LDAPConfig


class Command(BaseCommand):
    help = (
        'Enables and prepopulates an LDAP import job for a specific client '
        'and organization.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--client-name',
            type=str,
            help='The name of the client to configure. Required if more than '
                 'one client exists.')
        parser.add_argument(
            '--org-name',
            type=str,
            help='The name of the organization to configure. Required if the '
                 'client has more than one organization.')

    @transaction.atomic
    def handle(self, *args, **options):
        # circular dependency
        from os2datascanner.projects.admin.import_services.views.ldap_config_views import (
            _keycloak_creation, _keycloak_update
        )

        client_name = options['client_name']
        org_name = options['org_name']

        client = self.get_client(client_name)
        self.stdout.write(f"Found client: '{client.name}'.")

        client.features |= (
            Feature.ORG_STRUCTURE.value | Feature.IMPORT_SERVICES.value
        )
        client.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Enabled ORG_STRUCTURE and IMPORT_SERVICES for client "
                f"'{client.name}'."
            )
        )

        organization = self.get_organization(client, org_name)
        self.stdout.write(f"Found organization: '{organization.name}'.")

        ldap_config_data = {
            'hide_units_on_import': False,
            'importservice_ptr_id': UUID(
                '66b1150a-e11b-4453-978e-5cba4d49eb8c'),
            'created': datetime.datetime(
                2026, 1, 14, 9, 44, 34, 435408, tzinfo=datetime.timezone.utc),
            'last_modified': datetime.datetime(
                2026, 1, 14, 9, 44, 34, 433370, tzinfo=datetime.timezone.utc),
            'last_exported': None,
            'deleted_at': None,
            'vendor': 'ad',
            'import_into': 'ou',
            'group_filter': '',
            'import_managers': False,
            'username_attribute': 'uid',
            'firstname_attribute': 'givenName',
            'upn_attribute': None,
            'rdn_attribute': 'cn',
            'uuid_attribute': 'entryUUID',
            'object_sid_attribute': None,
            'user_obj_classes': 'inetOrgPerson',
            'custom_user_filter': '',
            'connection_protocol': 'ldap://',
            'connection_url': 'ldap-server:389',
            'users_dn': 'ou=Organization,dc=magenta,dc=test',
            'search_scope': 2,
            'bind_dn': 'cn=admin,dc=magenta,dc=test',
            '_ldap_password': [
                'c1428ad6e58876f0d96a95bad536ec54', '3a6c1c50900a80'],
        }

        ldap_config, created = LDAPConfig.objects.update_or_create(
            organization=organization,
            defaults=ldap_config_data
        )

        # Push the configuration to Keycloak
        if created:
            self.stdout.write(
                f"Creating Keycloak configuration for '{organization.name}'...")
            _keycloak_creation(ldap_config)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created LDAPConfig and Keycloak "
                    f"configuration for organization '{organization.name}'."
                )
            )
        else:
            self.stdout.write(
                f"Updating Keycloak configuration for '{organization.name}'...")
            _keycloak_update(ldap_config)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated existing LDAPConfig and Keycloak "
                    f"configuration for organization '{organization.name}'."
                )
            )

    def get_client(self, name):
        if name:
            try:
                return Client.objects.get(name=name)
            except Client.DoesNotExist:
                raise CommandError(f"Client with name '{name}' does not exist.")
        else:
            clients = Client.objects.all()
            if clients.count() == 0:
                raise CommandError("No clients found. Please create a client first.")
            if clients.count() > 1:
                raise CommandError(
                    "More than one client exists. Please specify which one to "
                    "use with --client-name."
                )
            return clients.first()

    def get_organization(self, client, name):
        if name:
            try:
                return Organization.objects.get(client=client, name=name)
            except Organization.DoesNotExist:
                raise CommandError(
                    f"Organization with name '{name}' for client "
                    f"'{client.name}' does not exist."
                )
        else:
            orgs = Organization.objects.filter(client=client)
            if orgs.count() == 0:
                raise CommandError(
                    f"No organizations found for client '{client.name}'.")
            if orgs.count() > 1:
                raise CommandError(
                    f"More than one organization exists for client "
                    f"'{client.name}'. Please specify which one to use with "
                    f"--org-name."
                )
            return orgs.first()
