import json
import asyncio
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import AsyncConsumer
from asgiref.sync import sync_to_async

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

class ReportWebsocketConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        from .models.documentreport_model import DocumentReport
        from channels.db import database_sync_to_async
        print("connected")
        await self.accept()
        # Make call to db somehow - works with "123" for example.
        # maybe rest?
    
        @database_sync_to_async
        def get_documentreports():
        # Hardcoded filter
            documentreports = DocumentReport.objects.filter(
                    data__matches__matched=True).filter(
                    resolution_status__isnull=True).filter(
                    sensitivity=250).filter(
                    data__scan_tag__scanner__pk=2)
            return [x.data for x in documentreports]

        await asyncio.sleep(3)
        obj = await get_documentreports()
        # print(obj)

        # await asyncio.sleep(5)

        await self.send_json(obj)


    async def websocket_receive(self, event):
        print("receive", event)

    async def websocket_disconnect(self, event):
        print("disconnected", event)
