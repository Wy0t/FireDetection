from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("api/", include("detection.urls")),  # 引入 app 的路由
]

# 添加靜態文件路由支持
if settings.DEBUG:  # 僅在開發模式下啟用
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
