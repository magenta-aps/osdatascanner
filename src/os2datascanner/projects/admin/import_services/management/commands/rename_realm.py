# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from os2datascanner.projects.admin.core.models import Client
from os2datascanner.projects.admin.organizations.models import Organization
from os2datascanner.projects.admin.import_services.models import Realm


class Command(BaseCommand):
    help = (
        'Renames the Realm of an Organization. '
        'IMPORTANT: You also need to update realm id in the OIDC endpoints, in the report settings.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "realm_id",
            type=str,
            help="The new realm-id",
        )
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

    def handle(self, realm_id, *args, **options):
        client_name = options['client_name']
        org_name = options['org_name']
        if Realm.objects.count() == 0:
            raise CommandError("No Realms found.")

        elif Realm.objects.filter(realm_id=realm_id).exists():
            raise CommandError(
                f"Realm with id '{realm_id}' already exists. "
                f"Please provide a unique realm id."
            )

        elif Realm.objects.count() > 1:

            client = self.get_client(client_name)
            self.stdout.write(f"Found client: '{client.name}'.")

            organization = self.get_organization(client, org_name)
            self.stdout.write(f"Found organization: '{organization.name}'.")

            if not Realm.objects.filter(organization=organization).exists():
                raise CommandError(
                    f"Organization with name '{org_name}' for client "
                    f"'{client.name}' does not have a realm."
                )

            realm = organization.realm

        else:
            realm = Realm.objects.all().first()

        self.stdout.write(f"Found realm: '{realm.realm_id}'.")

        tc = realm.make_caller()
        response = tc.put("", json={"id": realm_id, "realm": realm_id})
        if response.status_code != 204:
            raise CommandError(
                f"Renaming Keycloak Realm failed: {response.reason}"
            )
        self.stdout.write(self.style.SUCCESS(f"Renamed Keycloak Realm to '{realm_id}'"))

        realm.realm_id = realm_id
        realm.save()
        self.stdout.write(self.style.SUCCESS(f"Renamed Realm object to '{realm_id}'"))

        for idp in realm.providers.iterator():
            idp.entity_id = f"{settings.KEYCLOAK_BASE_URL}/auth/realms/{realm.realm_id}"
            idp.save()
            self.stdout.write(self.style.SUCCESS(
                f"Updated entity_id for IdentityProvider '{idp.alias}' to '{idp.entity_id}'"
            ))

            if auth_flow := realm.authentication_flows.first():
                response = idp.update_identity_provider(auth_flow)
                if response.status_code != 204:
                    self.stdout.write(self.style.ERROR(
                        f"Failed to update IdentityProvider '{idp.alias}' "
                        f"in Keycloak: {response.reason}"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"Propagated IdentityProvider '{idp.alias}' change to Keycloak"
                    ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"No authentication flow found for realm '{realm.realm_id}', "
                    f"skipping Keycloak update for IdentityProvider '{idp.alias}'"
                ))

        self.stdout.write(self.style.WARNING(
            "Remember to update OIDC endpoints in report settings!"))

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
