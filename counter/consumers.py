import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer


class CountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("start")
        await self.accept()
        await self.channel_layer.group_add("spam", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("spam", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        self.channel_layer.send("for-worker", {"type": "generate", "id": 123456789})

        #print(text_data)
        #self.channel_layer.send("test", {"type": "generate", "id": 123456789})

    # Receive message from room group
    async def new_number(self, event):
        print("new_number")
        await self.send(text_data=json.dumps({"number": event["number"]}))
        
class GenerateConsumer(SyncConsumer):
    def generate(self, message):
        print(message)