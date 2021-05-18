import json
import asyncio
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ReportWebsocketConsumer(WebsocketConsumer):
    def connect(self):
        self.channel = 'get_updates'
        async_to_sync(self.channel_layer.group_add)(
            self.channel,
            self.channel_name
        )
        self.accept()
        print("#######CONNECTED############")


    def websocket_disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel,
            self.channel_name
        )
        print("DISCONNECED CODE: ",code)


    def websocket_receive(self, text_data=None, bytes_data=None):
        print(" MESSAGE RECEIVED")
        data = json.loads(text_data)
        message = data['message']
        async_to_sync(self.channel_layer.group_send)(
            self.channel,{
                "type": 'send_message_to_frontend',
                "message": message
            }
        )

    def send_message_to_frontend(self,event):
        print("EVENT TRIGERED")
        # Receive message from room group
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))