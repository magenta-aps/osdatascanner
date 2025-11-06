from pprint import pprint

from django.core.management import BaseCommand, CommandError
from os2datascanner.utils.token_caller import TokenCaller

from django.conf import settings
from ...keycloak_services import request_access_token
from ...models import LDAPConfig
from ....import_services.models import Realm


class Command(BaseCommand):
    help = "Management command for interacting with Keycloak"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            type=str,
            choices=[
                "list-realms",
                "search-users",
                "delete-user",
                "recreate-federation",
            ],
            help="Action to perform",
        )
        parser.add_argument("--realm-id", type=str, help="Target realm ID")
        parser.add_argument("--username", type=str, help="Target username")
        parser.add_argument("--user-id", type=str, help="Target user ID")

    @staticmethod
    def _get_realm_or_fail(realm_id: str | None):
        """
        Returns (realm_id, Caller)
        If realm_id isn't provided, attempts to load the single Realm object.
        # OBS: realm_id is actually a name, not an ID per se.
        """
        if realm_id:
            caller = TokenCaller(
                request_access_token,
                f"{settings.KEYCLOAK_BASE_URL}/auth/admin/realms/{realm_id}",
            )
            return realm_id, caller

        try:
            realm = Realm.objects.get()
        except (Realm.DoesNotExist, Realm.MultipleObjectsReturned):
            raise CommandError("realm_id is required if multiple or no Realm objects exist "
                               "in OSdatascanner.")

        return realm.realm_id, realm.make_caller()

    def _success(self, msg):
        self.stdout.write(msg, style_func=self.style.SUCCESS)

    def _warning(self, msg):
        self.stdout.write(msg, style_func=self.style.WARNING)

    def handle(self, *args, **options):
        action = options["action"]
        realm_id = options.get("realm_id")
        username = options.get("username")
        user_id = options.get("user_id")

        match action:
            case "list-realms":
                caller = TokenCaller(
                    request_access_token,
                    f"{settings.KEYCLOAK_BASE_URL}/auth/admin",
                )

                resp = caller.get("/realms/")
                realms = [
                    {key: r.get(key) for key in ("id", "realm", "enabled")}
                    for r in resp.json()
                ]

                self._success("Listing realms:")
                pprint(realms)
                return

            case "search-users":
                if not username:
                    raise CommandError("--username is required when searching for users.")

                realm_id, caller = self._get_realm_or_fail(realm_id)
                resp = caller.get(f"/users?username={username}")

                pprint(resp.json())
                self._success(f"Searched users in realm '{realm_id}'.")
                return

            case "delete-user":
                if not user_id:
                    raise CommandError("--user-id is required for deleting a user.")

                self._warning(
                    "If using User federation /LDAP Import, "
                    "deleting a federated user will simply recreate them and may not be"
                    "what you want!"
                )

                realm_id, caller = self._get_realm_or_fail(realm_id)
                resp = caller.delete(f"/users/{user_id}")

                pprint(resp)
                self._success(f"Deleted user '{user_id}' in realm '{realm_id}'.")
                return

            case "recreate-federation":
                from ...views.ldap_config_views import _keycloak_creation

                try:
                    ldap_config = LDAPConfig.objects.get()
                except (LDAPConfig.DoesNotExist, LDAPConfig.MultipleObjectsReturned):
                    raise CommandError("No single LDAPConfig found. Cannot recreate federation.")

                realm_id, caller = self._get_realm_or_fail(realm_id)

                user_federations = caller.get(
                    "/components?type=org.keycloak.storage.UserStorageProvider"
                ).json()

                if len(user_federations) > 1:
                    raise CommandError("More than one User federation found!",
                                       user_federations)
                elif len(user_federations) == 0:
                    self._warning("No existing User federation found. Creating one.")
                else:
                    deleted = caller.delete(f"/components/{user_federations[0].get('id')}")
                    self._success(f"Deleted existing User federation: {deleted}")

                creating_conf = LDAPConfig.objects.filter(
                    pk=ldap_config.pk
                ).values().first()
                # No need to print the encrypted values
                creating_conf.pop("_ldap_password")

                self._success("Creating based on config: ")
                pprint(creating_conf)
                _keycloak_creation(ldap_config)
                self._success("Recreated federation successfully.")
                return

            case _:
                raise CommandError(f"Unknown action: {action}")
