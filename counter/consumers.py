import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer
from counter.tasks import count
from counter.models import AvailablePlayer
from asgiref.sync import sync_to_async
import random
import string

def find_available_player():
    available_player = AvailablePlayer.objects.first()
    if(available_player):
        available_player_channel_name = available_player.channel_name
        # We remove this player from the database.
        AvailablePlayer.objects.filter(channel_name = available_player_channel_name).delete()

        return available_player_channel_name
    
    return None

class CountConsumer(AsyncWebsocketConsumer):

    def add_channel_name_to_db(self):
        # Before adding the channel_name, we do a bit of housekeeping. We may sure that the
        # channel_name isn't already on the database due to a glitch.
        AvailablePlayer.objects.filter(channel_name = self.channel_name).delete()
        player = AvailablePlayer(channel_name = self.channel_name)
        player.save()
    
    async def connect(self):

        # Accepts all WebSocket traffic from user.
        await self.accept()

        # We check if there any available players.
        available_player = await sync_to_async(find_available_player)()
        
        if(available_player):
            new_counter_data = {'type': 'start', 'first': 0}
            await self.channel_layer.send(available_player, new_counter_data);
            await self.channel_layer.send(self.channel_name, new_counter_data);

            self.host = True
            self.task = count.delay()

        else:
            self.host = False
            # Adds players channel_name to the database.
            await sync_to_async(self.add_channel_name_to_db)()

    async def disconnect(self, close_code):
        if(self.host):
            self.task.revoke(terminate=True)

        await self.channel_layer.group_discard("counter", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    async def start(self, data):
        await self.channel_layer.group_add("counter", self.channel_name)

    # Receive message from channel layer
    async def number(self, event):
        await self.send(text_data=json.dumps({"number": event["value"]}))
