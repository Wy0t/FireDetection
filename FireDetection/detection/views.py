from django.conf import settings
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class UploadImageView_FromUser(APIView):
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
    
class UploadImageView_FromServer(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            file_obj = request.FILES['image']
            upload_dir = settings.SERVER_ROOT
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file_path = os.path.join(upload_dir, file_obj.name)

            # 使用 chunks() 方法保存文件
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            return Response({
                "status": "success",
                "file_path": file_path
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=400)

class AlertView(APIView):
    def post(self, request):
        try:
            # 從請求中獲取純文本消息
            message = request.body.decode('utf-8')  # 直接從request.body讀取文本
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "alert_group",  # 前端需要加入此群組
                {
                    "type": "alert_message", 
                    "message": message
                }
            )
            
            return Response({
                "status": "success",
                "message": "警報訊息已接收並轉發",
                "content": message
            }, content_type='text/plain')
            
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=400, content_type='text/plain')

