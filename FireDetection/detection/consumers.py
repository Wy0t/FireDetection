import cv2
import json
import base64
import asyncio
import numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
import time
import os
from dotenv import load_dotenv

load_dotenv()

def connect_stream(url=None, max_retries=3):
    if url is None:
        url = os.getenv('STREAM_URL')
    for attempt in range(max_retries):
        print(f"嘗試連接串流 (第 {attempt + 1} 次)")
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            return cap
        time.sleep(1)
    return None

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
        rtsp_url = 'rtsp://192.168.177.142:554'
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        # 設置低延遲參數
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        try:
            while self.is_streaming:
                ret, frame = cap.read()
                if not ret:
                    continue

                # 降低解析度
                frame = cv2.resize(frame, (1280, 720))
                
                # 降低 JPEG 品質以減少傳輸量
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                
                frame_data = base64.b64encode(buffer).decode('utf-8')
                await self.send(text_data=frame_data)
                
                # 減少等待時間
                await asyncio.sleep(0.01)  # 提高更新頻率
                
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
