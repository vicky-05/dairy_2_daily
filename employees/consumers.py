from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from orders.models import Order  # Replace 'orders' with your actual app name
from products.models import Product

class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Extract the order_id from the URL kwargs
            self.order_id = self.scope['url_route']['kwargs']['order_id']
            self.group_name = f'order_{self.order_id}'

            if not self.order_id:
                await self.close()
                return

            # Join the group for this order
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()
        except Exception as e:
            print(f"Error in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Leave the group on disconnect
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in disconnect: {e}")

    # Handle messages received from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            status = text_data_json.get('status')  # Get the status from the payload

            if status:
                # Update the order's status in the database
                update_successful = await self.update_order_status(self.order_id, status)

                if update_successful:
                    # Broadcast the updated status to all clients in the group
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'order_status_update',
                            'status': status,
                            'order_id': self.order_id,
                        }
                    )
                else:
                    # Send an error message back to the WebSocket client
                    await self.send(text_data=json.dumps({
                        'error': f"Failed to update order {self.order_id}.",
                    }))
            else:
                print(f"Invalid status received: {text_data}")
        except Exception as e:
            print(f"Error in receive: {e}")

    # Send updated status to the WebSocket client
    async def order_status_update(self, event):
        try:
            status = event['status']
            order_id = event['order_id']

            # Send the status update to the WebSocket client
            await self.send(text_data=json.dumps({
                'order_id': order_id,
                'status': status,
            }))
        except Exception as e:
            print(f"Error in order_status_update: {e}")

    # Update the order status in the database
    @sync_to_async
    def update_order_status(self, order_id, status):
        try:
            order = Order.objects.get(id=order_id)

            # Allow valid status transitions only
            if (order.status == "Pending" and status == "Shipping") or \
               (order.status == "Shipping" and status == "Completed"):
                order.status = status
                order.save()
                 # If the order is completed, reduce product quantity
                if status == "Completed":
                    try:
                        # Look up the product using product_name and product_slug
                        product = Product.objects.get(name=order.product_name, slug=order.product_slug)
                        
                        if product.quantity >= order.product_quantity:  # Ensure there is enough stock
                            product.quantity -= order.product_quantity  # Reduce stock
                            product.save()
                        else:
                            print(f"Not enough stock for {product.name}.")
                            return False
                    except Product.DoesNotExist:
                        print(f"Product {order.product_name} does not exist.")
                        return False
                return True
            else:
                print(f"Invalid status transition: {order.status} -> {status}")
                return False
            
        except Order.DoesNotExist:
            print(f"Order {order_id} does not exist.")
            return False

class SubscriptionStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "subscription_updates"
        
        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        area = data.get("area")
        message = data.get("message")
        action = data.get("action")
        delay = data.get("delay")

        


        # Broadcast message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_message",
                "area": area,
                "message": message,
                "action": action,
                "delay": delay,
            }
        )

    # Broadcast the message to WebSocket clients
    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps({
            "area": event["area"],
            "message": event["message"],
            "action": event["action"],
            "delay": event["delay"],
        }))