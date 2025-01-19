# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the order_id from the URL
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f'order_{self.order_id}'

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        status = text_data_json['status']

        # Send status update to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'order_status_update',
                'status': status
            }
        )

    # Handle incoming status update
    async def order_status_update(self, event):
        status = event['status']

        # Send status to WebSocket
        await self.send(text_data=json.dumps({
            'status': status
        }))
