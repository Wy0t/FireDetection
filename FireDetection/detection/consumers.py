import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
from dotenv import load_dotenv

load_dotenv()

class WebRTCConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pc = None
        self.player = None

    async def connect(self):
        print("WebSocket 連接建立")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket 連接關閉，代碼: {close_code}")
        await self.cleanup()

    async def cleanup(self):
        print("開始清理資源")
        try:
            if self.pc:
                print("關閉 RTCPeerConnection")
                await self.pc.close()
                self.pc = None
            
            if self.player:
                print("關閉 MediaPlayer")
                self.player.video.stop()
                self.player = None
                
        except Exception as e:
            print(f"清理資源時發生錯誤: {str(e)}")
        finally:
            print("資源清理完成")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data['type'] == 'offer':
                print("收到 offer")
                await self.cleanup()
                
                self.pc = RTCPeerConnection()
                
                rtsp_url = os.getenv('STREAM_URL')
                print(f"嘗試連接 RTSP: {rtsp_url}")
                
                try:
                    self.player = MediaPlayer(
                        rtsp_url,
                        format='rtsp',
                        options={
                            'rtsp_transport': 'tcp',
                            'fflags': 'nobuffer',
                            'rw_timeout': '5000000',        # 5秒讀寫逾時
                            'reconnect': '1',               # 重連
                            'reconnect_streamed': '1',      # 重連串流
                            'reconnect_delay_max': '10',     # 最大重連延遲
                            'max_delay': '500000'           # 0.5秒延遲緩衝
                        }
                    )
                    
                    if not self.player or not self.player.video:
                        raise Exception("無法獲取視訊軌道")
                    
                    print("成功獲取視訊軌道")
                    self.pc.addTrack(self.player.video)
                    
                    # 處理 WebRTC 協商
                    offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])
                    await self.pc.setRemoteDescription(offer)
                    
                    answer = await self.pc.createAnswer()
                    await self.pc.setLocalDescription(answer)
                    
                    print("成功創建 answer")
                    await self.send(text_data=json.dumps({
                        'type': 'answer',
                        'sdp': self.pc.localDescription.sdp
                    }))
                    
                except Exception as e:
                    print(f"串流建立錯誤: {str(e)}")
                    await self.cleanup()
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
                    
        except Exception as e:
            print(f"一般錯誤: {str(e)}")
            await self.cleanup()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "alert_group"

        # 加入群組
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # 離開群組
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # 接收推送的訊息
    async def alert_message(self, event):
        message = event['message']
        image_base64 = event['image']

        # 發送給前端
        await self.send(text_data=json.dumps({
            'message': message,
            'image': image_base64
        }))