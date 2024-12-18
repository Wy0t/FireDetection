import os
import json
import base64
from io import BytesIO
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class UploadImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.data['file']
        upload_dir = settings.MEDIA_ROOT  # 使用 MEDIA_ROOT
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)  # 確保目錄存在

        file_path = os.path.join(upload_dir, file_obj.name)

        # 保存文件
        with open(file_path, "wb+") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return Response({"status": "success", "file_path": file_path})
    
class AlertView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # 獲取 JSON 數據
            json_data = request.data.get('json')
            if not json_data:
                raise ValueError("Missing JSON data")
            
            json_data = json.loads(json_data)  # 解析 JSON 字串為字典
            message = json_data.get('message', "No message provided")
            detections = json_data.get('detections', [])

            # 獲取圖片
            file_obj = request.FILES['image']
            upload_dir = settings.SERVER_ROOT
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file_path = os.path.join(upload_dir, file_obj.name)

            # 保存圖片
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            # 使用 PIL 繪製圖片
            with Image.open(file_path) as img:
                draw = ImageDraw.Draw(img)
                font = ImageFont.truetype("arial.ttf", 30)  # 設置字體和大小

                for obj in detections:
                    # 從 JSON 中獲取邊界框並繪製
                    xmin = obj.get('xMin', 0)
                    ymin = obj.get('yMin', 0)
                    xmax = obj.get('xMax', img.width)
                    ymax = obj.get('yMax', img.height)
                    draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)

                    # 顯示識別文字
                    object_name = obj.get('type', 'Unknown')
                    score = obj.get('score', 0)
                    text = f"{object_name} ({score})"
                    text_x = xmin
                    text_y = ymin - 30 if ymin > 30 else ymin  # 避免文字超出圖像頂部
                    draw.text((text_x, text_y), text, fill="cyan", font=font)

                # 將圖片轉換成 Base64
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # 推送警報消息到 Channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "alert_group",
                {
                    "type": "alert_message",
                    "message": message,
                    "image": img_base64
                }
            )

            return Response({
                "status": "success",
                "message": message,
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=400)