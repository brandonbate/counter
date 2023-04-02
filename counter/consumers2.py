import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import SyncConsumer
from counter.tasks import count
from counter.models import AvailablePlayer
from asgiref.sync import sync_to_async
import random
import string

#def random_string(n):
#    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=n))

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
            # This is an indentifier used by channels for game communication.
            #self.game_id = random_string(10)

            # Assign X and O randomly to players.
            #(available_player_piece, current_player_piece) = ('X','O') if random.uniform(0, 1) < 0.5 else ('O','X')
            
            # Create an attribute so GameConsumer can remember which piece the current_player is using.
            #self.playing = current_player_piece
            
            # Send message to available_player with game_id over channel_layer.
            # The GameConsumer for available_player will receive this data via the start_game function.
            #new_game_data_for_available_player = {"type": "start_game", 
            #                                      "game_id": self.game_id,
            #                                      "your_piece": available_player_piece}

            new_game_data_for_available_player = {'type': 'start', 'first': 0}
            await self.channel_layer.send(available_player, new_game_data_for_available_player);

            #self.game_id_name = "game_%s" % self.game_id
            #self.moves = []
            #await self.channel_layer.group_add(self.game_id_name, self.channel_name)
            #await self.channel_layer.group_add('counter', self.channel_name)
    
            # Send message to current_player through WebSocket.
            #new_game_data_for_current_player = {"type": "start_game", 
            #                                    "game_id": self.game_id,
            #                                    "your_piece": current_player_piece}
            
            new_game_data_for_current_player = {'type': 'start', 'first': 0}
            await self.channel_layer.send(self.channel_name, new_game_data_for_current_player);

            count.delay()

        else:
            # Adds players channel_name to the database.
            await sync_to_async(self.add_channel_name_to_db)()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("counter", self.channel_name)

    async def start(self, data):
        await self.channel_layer.group_add("counter", self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("sent button pressed")
        #count.delay()

    # Receive message from channel layer
    async def number(self, event):
        print("new_number")
        await self.send(text_data=json.dumps({"number": event["value"]}))