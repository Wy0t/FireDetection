from channels.generic.websocket import AsyncWebsocketConsumer
import cv2
import json
import base64
import asyncio
import subprocess

class LiveFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 建立 WebSocket 連線時的處理
        self.room_group_name = 'live_feed'

        # 接受 WebSocket 連線
        await self.accept()

        # 開始讀取 RTSP 影像流
        self.cap = cv2.VideoCapture('rtsp://192.168.177.2:554')
        if not self.cap.isOpened():
            await self.send(text_data=json.dumps({
                'error': 'Unable to connect to RTSP stream'
            }))
            return
        
        # 每 100 毫秒讀取一幀影像並發送至 WebSocket
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # 將影像轉換為 JPEG 格式
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # 將影像轉換為 base64 編碼，便於在 WebSocket 中傳送
            encoded_frame = base64.b64encode(frame_bytes).decode('utf-8')

            # 發送影像至 WebSocket
            await self.send(text_data=json.dumps({
                'image': encoded_frame
            }))

            # 等待一段時間（可根據需要調整）
            await asyncio.sleep(0.1)

    async def disconnect(self, close_code):
        # 關閉 RTSP 連接
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        # 斷開 WebSocket 連線
        await self.close()

class FireAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "fire_alert_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def fire_alert(self, event):
        await self.send(text_data=json.dumps(event))
