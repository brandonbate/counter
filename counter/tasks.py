from celery import shared_task
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis

@shared_task
def count():
    r = redis.Redis()
    i=0
    while(True):
        print(i)
        sleep(1)
        i += 1

        while(r.exists('action')):
            if r.lpop('action').decode('utf-8') == 'skip':
                i+= 10

        channel_layer = get_channel_layer()
        # Broadcasts count back to consumers.
        async_to_sync(channel_layer.group_send)(
            "counter",
            {
                "type": "number",
                "value": i,
            },
        )