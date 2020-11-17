from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from os2datascanner.utils import amqp_connection_manager
import json

def publish_events(events):
    # TODO: use settings.AMQP_EVENTS_TARGET or similar
    queue = "os2ds_model_events"
    amqp_connection_manager.start_amqp(queue)
    for event in events:
        serialized = json.dumps(event)
        print("published: {0}".format(serialized))
        amqp_connection_manager.send_message(
            queue, serialized)
    amqp_connection_manager.close_connection()

@receiver(post_save)
def post_save_callback(sender, **kwargs):
    event = {
        'instance': model_to_dict(kwargs.get('instance')),
        'type': 'create' if kwargs.get("created") else 'update',
    }
    publish_events([event])

@receiver(post_delete)
def post_save_callback(sender, **kwargs):
    event = {
        'instance': model_to_dict(kwargs.get('instance')),
        'type': 'delete',
    }
    publish_events([event])
