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
from ..broadcast_bulk_events import BulkCreateEvent, BulkUpdateEvent, BulkDeleteEvent
from ..publish import publish_events

from os2datascanner.utils.section import suppress_django_signals
from os2datascanner.core_organizational_structure.utils import get_serializer


class Broadcasted(ABC):  # noqa
    """Virtual superclass for objects for which changes should be broadcasted.
    (Register classes as virtual subclasses using the Broadcasted.register
    decorator.)"""


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
    serializer = get_serializer(sender)
    serialized_data = serializer(instance).data
    broadcastable_dict = {sender.__name__: [serialized_data]}
    if created:
        event = BulkCreateEvent(broadcastable_dict)
    else:
        event = BulkUpdateEvent(broadcastable_dict)

    publish_events([event])


@receiver(m2m_changed)
def account_permissions_changed(sender, instance, action, *args, **kwargs):
    """When account permissions are changed, we want to propagate that change to the report module.
    Since permissions on the Account model is a many-to-many field, it is not always registered in
    a post-save, so we have to do it here as well."""
    if not sender.__name__ == "Account_permissions" or action not in ["post_add", "post_remove"]:
        return
    serializer = get_serializer(instance.__class__)
    serialized_data = serializer(instance).data
    broadcastable_dict = {instance.__class__.__name__: [serialized_data]}

    event = BulkUpdateEvent(broadcastable_dict)

    publish_events([event])


@receiver(post_delete)
def post_delete_broadcast(sender, instance, **kwargs):
    if (in_test_environment()
            or not isinstance(instance, Broadcasted)
            or type(instance).__module__ == "__fake__"
            or suppress_django_signals):
        return

    broadcastable_dict = {sender.__name__: [str(instance.pk)]}
    event = BulkDeleteEvent(broadcastable_dict)
    publish_events([event])
