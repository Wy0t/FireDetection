import asyncio
import json
import os
import socket
from channels.generic.websocket import AsyncWebsocketConsumer
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
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

                # 初始化 RTCPeerConnection 並使用封裝的配置
                configuration = RTCConfiguration(iceServers=[
                    RTCIceServer(urls="stun:stun.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun1.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun2.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun3.l.google.com:19302"),
                    RTCIceServer(urls="stun:stun4.l.google.com:19302")
                ])
                self.pc = RTCPeerConnection(configuration)

                rtsp_url = os.getenv('STREAM_URL')
                print(f"嘗試連接 RTSP: {rtsp_url}")

                try:
                    # 設置 RTSP 超時
                    connect_task = asyncio.create_task(self.create_media_player(rtsp_url))
                    await asyncio.wait_for(connect_task, timeout=5)

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

                except asyncio.TimeoutError:
                    error_message = "RTSP 連接超時，無法在 5 秒內建立連線"
                    print(error_message)
                    await self.cleanup()
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': error_message
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

    async def create_media_player(self, rtsp_url):
        # 驗證 RTSP URL 是否可連接
        parsed_url = rtsp_url.replace("rtsp://", "").split(":")
        host = parsed_url[0]
        port = int(parsed_url[1]) if len(parsed_url) > 1 else 554

        try:
            with socket.create_connection((host, port), timeout=5):
                print("RTSP 伺服器可連接，開始初始化 MediaPlayer")
        except socket.error as e:
            raise Exception(f"無法連接到 RTSP 伺服器: {str(e)}")

        self.player = MediaPlayer(
            rtsp_url,
            format='rtsp',
            options={
                'rtsp_transport': 'udp',  # 使用 UDP
            }
        )
        # 確保視訊軌道可用
        if not self.player or not self.player.video:
            raise Exception("無法獲取視訊軌道")

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