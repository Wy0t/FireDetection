from django.conf import settings
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser


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
