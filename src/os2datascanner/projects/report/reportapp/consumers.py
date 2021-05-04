# import json
import asyncio
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer

# class ReportWebsocketConsumer(WebsocketConsumer):
#     def connect(self):
#         print("Connected")
#         self.accept()
        

#     def disconnect(self, close_code):
#         print("Disconnected")
        
#     def receive(self, event):
#         print("recieve", event)



# class ReportWebsocketConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#     def disconnect(self, close_code):
#         pass
#     def receive(self, text_data):
#         "Handle incoming WebSocket data"
#         from .models.documentreport_model import DocumentReport
#         self.send(text_data='123')

class ReportWebsocketConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })

        # Make call to db somehow - works with "123" for example.
        obj = "123"

        await self.send({
            'type': 'websocket.send',
            'text': obj,
        })


    async def websocket_receive(self, event):
        print("receive", event)

    async def websocket_disconnect(self, event):
        print("disconnected", event)