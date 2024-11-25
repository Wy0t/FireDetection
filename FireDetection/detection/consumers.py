import cv2
import json
import base64
import asyncio
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_streaming = True
        self.stream_task = asyncio.create_task(self.stream_video())

    async def disconnect(self, close_code):
        self.is_streaming = False
        if self.stream_task:
            self.stream_task.cancel()
        await self.close()

    async def stream_video(self):
        rtsp_url = 'rtsp://192.168.177.2:554'
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            await self.send("Could not open RTSP stream.")
            return

        try:
            while self.is_streaming:
                ret, frame = cap.read()
                if not ret:
                    break

                # 將影像壓縮成 JPEG 格式
                _, buffer = cv2.imencode('.jpg', frame)
                # 編碼成 base64 字串以便傳輸
                frame_data = base64.b64encode(buffer).decode('utf-8')

                # 發送影像資料到前端
                await self.send(text_data=frame_data)
                # 控制幀率
                await asyncio.sleep(0.03)  # 約 30 FPS
        except asyncio.CancelledError:
            pass
        finally:
            cap.release()

class FireAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "fire_alert_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def fire_alert(self, event):
        await self.send(text_data=json.dumps(event))
