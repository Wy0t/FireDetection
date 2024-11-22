from channels.generic.websocket import AsyncWebsocketConsumer
import json
import base64
import asyncio

class LiveFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # 模擬每秒發送一幀影像數據
        self.keep_sending = True
        while self.keep_sending:
            # 模擬影像數據 (Base64 格式)
            fake_image_data = base64.b64encode(b"fake_image_data").decode("utf-8")
            await self.send(fake_image_data)
            await asyncio.sleep(1)  # 每秒發送一幀

    async def disconnect(self, close_code):
        # 當 WebSocket 斷開時，停止發送數據
        self.keep_sending = False

    async def send_image(self, image_data):
        await self.send(image_data)

class FireAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "fire_alert_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def fire_alert(self, event):
        await self.send(text_data=json.dumps(event))
