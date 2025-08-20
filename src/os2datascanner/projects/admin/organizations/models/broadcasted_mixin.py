# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.

from abc import ABC
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from os2datascanner.utils.test_helpers import in_test_environment

from os2datascanner.projects.grants.models import Grant
from ..broadcast_bulk_events import BulkCreateEvent, BulkUpdateEvent, BulkDeleteEvent
from ..publish import publish_events

from os2datascanner.utils.section import suppress_django_signals
from os2datascanner.core_organizational_structure.utils import get_serializer


class Broadcasted(ABC):  # noqa
    """Virtual superclass for objects for which changes should be broadcasted.
    (Register classes as virtual subclasses using the Broadcasted.register
    decorator.)"""


def get_broadcastable_dict(sender, instance, delete=False):
    if delete:
        return {sender.__name__: [str(instance.pk)]}
    else:
        serializer = get_serializer(sender)
        serialized_data = serializer(instance).data
        return {serializer.Meta.model.__name__: [serialized_data]}


# TODO: change to avoid using save/delete-signals as they are not called on bulk actions
@receiver(post_save)
def post_save_broadcast(sender, instance, created, **kwargs):
    # We cannot support get_serializer() when we're encountering __fake__objects,
    # i.e. when trying to modify data in "Broadcast" child-objects in f.e. migrations.
    # This is an implementation detail of Django, only being aware of the model definition and
    # not class attributes, such as serializer_class. There isn't really any good way
    # of disabling signals in migrations.
    if (in_test_environment()
            or not isinstance(instance, Broadcasted)
            or type(instance).__module__ == "__fake__"
            or suppress_django_signals):
        return

    # Special case for GrantExtra: GrantExtra does not exist in the report module, but Grant and
    # subclasses of Grant do -- these are what we _actually_ want to synchronize here!
    from os2datascanner.projects.admin.organizations.models.grant_extra import GrantExtra
    if isinstance(instance, GrantExtra):
        # The sender is GrantExtra. Let's check if the grant should be synchronized or deleted
        should_broadcast = instance.should_broadcast
        pre_should_broadcast = instance.previous_should_broadcast
        if not should_broadcast and not pre_should_broadcast:
            # Do nothing.
            return
        # Then we replace the instance with the Grant-object
        instance = Grant.objects.get_subclass(pk=instance.grant.pk)
        sender = instance.__class__
        created = should_broadcast and not pre_should_broadcast
        broadcastable_dict = get_broadcastable_dict(sender, instance, delete=not should_broadcast)
    else:
        should_broadcast = None  # Because we're not dealing with a GrantExtra
        broadcastable_dict = get_broadcastable_dict(sender, instance)

    if created:
        event = BulkCreateEvent(broadcastable_dict)
    # It's important to distinguish between False and None here. (I.e. do not use "not")
    elif should_broadcast is False:
        # Special case for deleting existing grants
        event = BulkDeleteEvent(broadcastable_dict)
    else:
        event = BulkUpdateEvent(broadcastable_dict)

    publish_events([event])


@receiver(m2m_changed)
def broadcasted_m2m_changed(sender, instance, action, *args, **kwargs):
    """ When a broadcasted ManyToMany relation is changed,
    we want to propagate that change to the report module.
    These changes are not always registered in a post-save, so we do it here as well.
    This currently includes the Account-Permission and Scanner-OrganizationalUnit relations.
    """
    if sender.__name__ not in ["Account_permissions", "Scanner_org_unit"] \
            or action not in ["post_add", "post_remove"]:
        return
    broadcastable_dict = get_broadcastable_dict(instance.__class__, instance)

    event = BulkUpdateEvent(broadcastable_dict)

    publish_events([event])


@receiver(post_delete)
def post_delete_broadcast(sender, instance, **kwargs):
    if (in_test_environment()
            or not isinstance(instance, Broadcasted)
            or type(instance).__module__ == "__fake__"
            or suppress_django_signals):
        return

    broadcastable_dict = get_broadcastable_dict(sender, instance, delete=True)
    event = BulkDeleteEvent(broadcastable_dict)
    publish_events([event])
