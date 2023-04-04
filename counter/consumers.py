import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer
from counter.tasks import count
from counter.models import AvailablePlayer
from asgiref.sync import sync_to_async

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

            # We assign one of the players to be a host. They are in charge of killing the celery task.
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

    async def start(self, data):
        self.r = redis.Redis()
        await self.channel_layer.group_add("counter", self.channel_name)

    # Receive message from channel layer emitted by the celery task.
    async def number(self, event):
        # Relays number back to client
        await self.send(text_data=json.dumps({"number": event["value"]}))

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Passes the button action to the Redis server to be handled by the celery task.
        self.r.rpush('action',data['action'])
