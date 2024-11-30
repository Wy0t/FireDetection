import json
import os
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
from dotenv import load_dotenv

load_dotenv()

class WebRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pc = None
        await self.accept()

    async def disconnect(self, close_code):
        if self.pc:
            await self.pc.close()
        await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data['type'] == 'offer':
                print("收到 offer")
                self.pc = RTCPeerConnection()
                
                # 設置 RTSP 串流
                player = MediaPlayer(os.getenv('STREAM_URL'), format='rtsp')
                print(f"RTSP URL: {os.getenv('STREAM_URL')}")
                
                if player.video:
                    print("找到視訊軌道")
                    self.pc.addTrack(player.video)
                else:
                    print("沒有找到視訊軌道")
                
                # 處理 offer
                offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
                await self.pc.setRemoteDescription(offer)
                
                # 創建並發送 answer
                answer = await self.pc.createAnswer()
                await self.pc.setLocalDescription(answer)
                
                await self.send(text_data=json.dumps({
                    'type': 'answer',
                    'sdp': self.pc.localDescription.sdp
                }))
                
        except Exception as e:
            print(f"WebRTC error: {str(e)}")
            if self.pc:
                await self.pc.close()
