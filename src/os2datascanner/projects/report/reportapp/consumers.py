import json
import asyncio
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ReportWebsocketConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        from .models.documentreport_model import DocumentReport
        from channels.db import database_sync_to_async
        print("connected")
        await self.accept()
        # maybe rest?
    
        @database_sync_to_async
        def get_documentreports():
        # Hardcoded filter
                    # .filter(
                    # sensitivity=250).filter(
                    # data__scan_tag__scanner__pk=1)
            documentreports = DocumentReport.objects.filter(
                    data__matches__matched=True).filter(
                    resolution_status__isnull=True)
            return [x.data for x in documentreports]

        await asyncio.sleep(3)
        obj = await get_documentreports()

        await self.send_json(obj)


    async def websocket_receive(self, event):
        from .models.documentreport_model import DocumentReport
        from channels.db import database_sync_to_async
        text_data_json = json.loads(event['text'])
        message = text_data_json['message']

        @database_sync_to_async
        def get_new():
            documentreports = DocumentReport.objects.filter(
                    data__matches__matched=True).filter(
                    resolution_status__isnull=True).filter(
                    sensitivity=message)
            print(documentreports.count())
            return [x.data for x in documentreports]

        await asyncio.sleep(1)
        obj = await get_new()

        await self.send_json(obj)


    async def websocket_disconnect(self, event):
        print("disconnected", event)
