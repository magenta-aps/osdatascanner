import structlog
from itertools import chain
from django.apps import apps
from django.db import connection, transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from os2datascanner.utils.system_utilities import time_now
from os2datascanner.core_organizational_structure.utils import get_serializer
from .models import (Account, Alias, Position, OrganizationalUnit)
from ..import_services.models.imported_mixin import Imported
from ..organizations.models.broadcasted_mixin import Broadcasted
from ..organizations.models.organization import Organization
from ..core.models.administrator import Administrator
from ..organizations.broadcast_bulk_events import (BulkCreateEvent, BulkUpdateEvent,
                                                   BulkDeleteEvent)
from ..organizations.publish import publish_events

logger = structlog.get_logger("admin_organizations")


def get_broadcasted_models():
    """Returns a list of all models (except Organization & DummyBroadCastedModel)
    that inherit from Broadcasted and Imported."""
    models = []
    for model in apps.get_models():
        # We'll only want Organization included in create.
        # Deleting an Org from the report module potentially destroys too much.
        # (Document reports)
        if (issubclass(model, Broadcasted)
                and issubclass(model, Imported)
                and model is not Organization):
            models.append(model)
    return models


def group_into(collection, *models, key=lambda o: o):
    """Collects a heterogeneous sequence of Django model objects into subsets
    of the same type, and yields each model manager and (non-empty) collection
    in the model order specified.

    The input collection does not need to contain Django model objects, as long
    as an appropriate key function is provided to select such an object from
    each item in the collection."""
    if collection:
        for subset in models:
            manager = subset.objects

            instances = [k for k in collection if isinstance(key(k), subset)]
            if instances:
                yield (manager, instances)


def set_imported_fields(model_objects: list):
    """Takes a list of model objects, iterates and updates model fields
    that stem from the Imported model class."""
    now = time_now()
    for o in model_objects:
        # TODO: import_requested should perhaps be background job creation time.
        o.imported = True
        o.last_import = now
        o.last_import_requested = now


def create_and_serialize(manager, instances):
    """Provided a model manager and a list of serialized instances,
     bulk creates and returns instances in a serialized fashion."""
    serializer = get_serializer(manager.model)
    created_instances = manager.bulk_create(instances)
    if hasattr(manager, "rebuild"):
        manager.rebuild()
        for instance in created_instances:
            instance.refresh_from_db(fields=['lft', 'rght', 'tree_id', 'level'])
        instances = created_instances
    return serializer(instances, many=True).data


def update_and_serialize(manager, instances):
    logger.debug(f"update_and_serialize received {manager} with instances: "
                 f"{instances}")
    properties = set()
    serializer = get_serializer(manager.model)
    for __, props in instances:
        properties |= set(props)
    logger.debug(f"found properties: {properties}")

    # We'll only want to send one update instruction pr. object.
    unique_instances = set(obj for obj, _ in instances)
    logger.debug(f"unique_instances: {unique_instances}")

    manager.bulk_update(unique_instances, properties)
    return serializer(unique_instances, many=True).data


def delete_and_listify(manager, instances):
    deletion_pks = [str(i.pk) for i in instances]
    logger.debug(f"delete_and_listify received instructions "
                 f"to delete for: {manager} the following list of primary keys: {deletion_pks}")
    manager.filter(pk__in=deletion_pks).delete()
    return deletion_pks


def prepare_and_publish(
        org: Organization,
        all_uuids, to_add, to_delete, to_update,
        *,
        # XXX: Remove this keyword argument and make all import jobs use the
        # same import order!
        delete_first=False):

    def do_deletion(to_delete, delete_dict):
        for model, selector_expr in [
                (Alias, "account__organization"),
                (Account, "organization"),
                (OrganizationalUnit, "organization")]:
            relevant_objects = (
                    model.objects.filter(**{selector_expr: org})
                    .exclude(imported=False))
            # TODO: This isn't safe in a multi-tenant environment.
            # Technically there's a miniscule risk that two objects of different model types
            # share UUID, which could mean an object that should be deleted, won't be.
            to_delete.append(
                    relevant_objects.exclude(imported_id__in=all_uuids))
            logger.debug(f"to_delete post append of {model}: {to_delete}")

        # Look in Position
        to_delete = list(chain(*to_delete))
        for manager, instances in group_into(
                to_delete, Alias, Position, Account, OrganizationalUnit):
            model_name = manager.model.__name__

            logger.debug(f"Processing to_delete for model {manager} "
                         f" Instances: {instances}")
            delete_dict[model_name] = delete_and_listify(manager, instances)

    """ In a transaction, sorts out to_add, to_delete and to_update.
        Creates objects in the admin module and publishes broadcast events."""
    with transaction.atomic():
        if settings.PREPNPUB_IMMEDIATE_CONSTRAINTS:
            logger.warning("Enabling immediate database constraints")
            connection.cursor().execute("SET CONSTRAINTS ALL IMMEDIATE")
        logger.debug(f"Entered prepare_and_publish with to_delete containing: \n"
                     f"{to_delete}")

        delete_dict = {}

        if delete_first:
            do_deletion(to_delete, delete_dict)

        # Creates
        # TODO: Place the order of which objects should be created/updated somewhere reusable
        set_imported_fields(to_add)  # Updates imported_time etc.
        creation_dict = {}
        for manager, instances in group_into(
                to_add, OrganizationalUnit, Account, Position, Alias):
            model_name = manager.model.__name__
            creation_dict[model_name] = create_and_serialize(manager, instances)

        # Updates
        # TODO: We're not actually updating "Imported" fields/timestamps. Should we?
        update_dict = {}
        logger.debug(f"Entered prepare_and_publish with to_update containing: \n"
                     f"{to_update}")
        for manager, instances in group_into(
                to_update, Alias, Position, Account, OrganizationalUnit,
                key=lambda k: k[0]):
            logger.debug(f"Iterating updates for manager {manager}")
            model_name = manager.model.__name__
            update_dict[model_name] = update_and_serialize(manager, instances)

        if not delete_first:
            do_deletion(to_delete, delete_dict)

        event = [BulkCreateEvent(creation_dict),
                 BulkUpdateEvent(update_dict)]
        event.insert(
                0 if delete_first else 2,
                BulkDeleteEvent(delete_dict))

        logger.info("Database operations complete")

    # Make sure we publish events _after_ the transaction is completed.
    logger.info("Publishing events..")
    publish_events(event)


def user_allowed(user, org_slug):
    """Checks that the user is allowed to see content for the given org slug,
    and returns the Organization object."""
    org = get_object_or_404(Organization, slug=org_slug)
    allowed = user.is_authenticated and (
                user.has_perm("core.view_client") or Administrator.objects.filter(
                    user=user, client=org.client).exists())
    return org, allowed


class ClientAdminMixin:
    """Mixin for making sure, that the requesting user is either an admin for
    the client, for which they are requesting data, or is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        org, allowed = user_allowed(request.user, kwargs['org_slug'])
        # Add the organization to the kwargs for future use.
        self.kwargs['org'] = org
        if allowed:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404(
                _("Account not found.")
                )
