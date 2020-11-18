from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from inspect import ismethod
from os2datascanner.utils import amqp_connection_manager
import json
import logging
import sys

logger = logging.getLogger(__name__)

class Event():
    def __init__(self, event_type, model_class, instance, meta = {}):
        self.event_type = event_type
        self.model_class = model_class
        self.instance = instance
        self.meta = meta

    def to_json_object(self):
        return {
            "type": self.event_type,
            "model_class": self.instance.__class__.__name__,
            "instance": self.instance.to_json_object() 
                            if hasattr(self.instance, "to_json_object") and 
                               ismethod(getattr(self.instance, "to_json_object"))
                            else "missing to_json_object() method"
        }

def publish_events(events):
    try:
        # TODO: use settings.AMQP_EVENTS_TARGET or similar
        queue = "os2ds_model_change_events"
        amqp_connection_manager.start_amqp(queue)
        for event in events:
            json_event = event.to_json_object()
            print("published: {0}".format(json_event))
            amqp_connection_manager.send_message(
                queue, json.dumps(json_event))
        amqp_connection_manager.close_connection()
    except Exception as e: 
        # log the error
        logger.error("Could not publish event. Error: "+format(e))


@receiver(post_save)
def post_save_callback(**kwargs):
    event = Event('create' if kwargs.get("created") else 'update', 
                  kwargs.get('sender'), 
                  kwargs.get('instance'))
    publish_events([event])

@receiver(post_delete)
def post_delete_callback(**kwargs):
    event = Event('delete', kwargs.get('sender'), kwargs.get('instance'))
    publish_events([event])
