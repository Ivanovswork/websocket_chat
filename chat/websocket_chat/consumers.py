import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model  # Используем get_user_model для User
from django.apps import apps


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_id = self.scope['url_route']['kwargs']['sender_id']
        self.recipient_id = self.scope['url_route']['kwargs']['recipient_id']
        self.room_group_name = f'chat_{self.sender_id}_{self.recipient_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.sender_id
        recipient_id = self.recipient_id

        # Получаем модели с помощью apps.get_model() и get_user_model()
        User = get_user_model()
        Messages = apps.get_model('websocket_chat', 'Messages')

        # Получаем объекты User (асинхронно)
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        recipient = await sync_to_async(User.objects.get)(id=recipient_id)

        # Сохраняем сообщение в базу данных (асинхронно)
        await self.save_message(sender, recipient, message)

        # Отправляем сообщение в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'recipient_id': recipient_id,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        recipient_id = event['recipient_id']

        # Отправляем сообщение клиенту
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
        }))

    @sync_to_async
    def save_message(self, sender, recipient, message):
        # Получаем модель Messages внутри функции
        Messages = apps.get_model('websocket_chat', 'Messages')
        Messages.objects.create(sender_id=sender, recipient_id=recipient, text=message)