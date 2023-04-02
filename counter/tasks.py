from celery import shared_task
from time import sleep
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def count():
    i=0
    while(True):
        print(i)
        sleep(1)
        i += 1
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "counter",
            {
                "type": "number",
                "value": i,
            },
        )