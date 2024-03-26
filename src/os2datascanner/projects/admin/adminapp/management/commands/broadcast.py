from django.core.management.base import BaseCommand

from ....organizations.broadcast_bulk_events import BulkBroadcastEvent, BulkCreateEvent, \
    BulkDeleteEvent
from ....organizations.publish import publish_events
from ....organizations.models.organization import OrganizationSerializer
from ....organizations.models.organization import Organization
from ....organizations.utils import get_broadcasted_models
from os2datascanner.core_organizational_structure.utils import get_serializer


class BulkPurgeEvent(BulkBroadcastEvent):
    def __init__(self, classes: list):
        super().__init__("bulk_event_purge_all")
        self.classes = classes

    def to_json_object(self) -> dict:
        return super().to_json_object() | {
            "classes": self.classes
        }


class Command(BaseCommand):
    """
        Synchronize or purge Organizational Structure models between Admin and Report module through
        a single message.

        Often times you want to use --purge followed by --sync --no-org.
        For new installations you likely want --sync-all, to synchronize the Organization object.
    """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "-p", "--purge",
            default=False,
            action="store_true",
            help="Purge data that stem from an import-job (Imported=True) in the report module "
                 "Run --purge-all if you wish to delete manually created org data as well. "
                 "OBS: Does not delete Organization objects!"
        )
        parser.add_argument(
            "-pa", "--purge-all",
            default=False,
            action="store_true",
            help="Purge data that represent organizational structure, regardless of imported flag "
                 "Run --purge if you don't wish to delete manually created org data as well."
                 "OBS: Does not delete Organization objects!"
        )
        parser.add_argument(
            "-s", "--sync",
            default=False,
            action="store_true",
            help="Sync data that stem from an import-job (Imported=True) in the report module "
                 "Run --sync-all if you wish to sync manually created org data as well. "
                 "OBS: Includes Organization, combine with --no-org if you wish otherwise"
        )
        parser.add_argument(
            "-sa", "--sync-all",
            default=False,
            action="store_true",
            help="Syncdata that represent organizational structure, regardless of imported flag "
                 "Run --sync if you don't wish to sync manually created org data as well. "
                 "OBS: Includes Organization, combine with --no-org if you wish otherwise "
        )
        parser.add_argument(
            "--no-org",
            default=False,
            action="store_true",
            help="Exclude Organization in create message"
        )

    def handle(self, *args, purge, purge_all, sync, sync_all,  no_org, **options):
        broadcasted_models = get_broadcasted_models()

        if purge:
            to_delete = {}
            printable_output = {}
            for model in broadcasted_models:
                qs = model.objects.filter(imported=True).values_list("pk", flat=True)
                # It's a bit tedious, but we currently need str - not f.e. UUID.
                list_pks = [str(pk) for pk in qs]
                to_delete[model.__name__] = list_pks
                printable_output[model.__name__] = len(list_pks)

            print(f"Publishing deletion instructions for Imported=True models.. Model:Count \n"
                  f" {printable_output}")
            event = BulkDeleteEvent(to_delete)

        elif purge_all:  # Delete
            deletion_list = [broadcastable_model.__name__ for broadcastable_model in
                             broadcasted_models if not broadcastable_model == Organization]
            # Publishes a structure of:
            # {
            #     "time": "<>",
            #     "type": "bulk_event_purge_all",
            #     "publisher": "admin",
            #     "classes": [
            #         "Account",
            #         "Alias",
            #         "OrganizationalUnit",
            #         "Position"
            #     ]
            # }
            print(f"Publishing deletion instructions: \n {deletion_list}")
            event = BulkPurgeEvent(deletion_list)

        elif sync:  # Create
            creation_dict = {}
            for broadcastable_model in broadcasted_models:
                serializer = get_serializer(broadcastable_model)
                serialized_imported = serializer(
                    broadcastable_model.objects.filter(imported=True), many=True).data
                creation_dict[broadcastable_model.__name__] = serialized_imported

            if not no_org:
                creation_dict["Organization"] = OrganizationSerializer(
                    Organization.objects.all(), many=True).data

            print(f"Publishing creation instructions:\n {creation_dict}")
            # Publishes a structure of:
            # {
            #     "time": "<time>",
            #     "type": "bulk_event_create",
            #     "publisher": "admin",
            #     "classes": {
            #         "Account": "[<serialized objects>]",
            #         "Alias": "[<serialized objects>]",
            #         "OrganizationalUnit": "[<serialized objects>]",
            #         "Position": "[<serialized objects>]",
            #         "Organization": "[<serialized objects>]"
            #     }
            # }
            event = BulkCreateEvent(creation_dict)

        elif sync_all:
            creation_dict = {}
            for broadcastable_model in broadcasted_models:
                serializer = get_serializer(broadcastable_model)
                serialized_imported = serializer(
                    broadcastable_model.objects.all(), many=True).data
                creation_dict[broadcastable_model.__name__] = serialized_imported

            if not no_org:
                creation_dict["Organization"] = OrganizationSerializer(
                    Organization.objects.all(), many=True).data

            print(f"Publishing creation instructions:\n {creation_dict}")
            # Publishes a structure of:
            # {
            #     "time": "<time>",
            #     "type": "bulk_event_create",
            #     "publisher": "admin",
            #     "classes": {
            #         "Account": "[<serialized objects>]",
            #         "Alias": "[<serialized objects>]",
            #         "OrganizationalUnit": "[<serialized objects>]",
            #         "Position": "[<serialized objects>]",
            #         "Organization": "[<serialized objects>]"
            #     }
            # }
            event = BulkCreateEvent(creation_dict)

        else:
            print(f"{self.print_help('manage.py', 'broadcast')}")
            return

        publish_events([event])
