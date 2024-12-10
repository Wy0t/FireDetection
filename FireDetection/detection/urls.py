from django.urls import path
from .views import UploadImageView_FromUser, AlertView, UploadImageView_FromServer

urlpatterns = [
    path("upload_image/", UploadImageView_FromUser.as_view(), name="upload_image"),
    path("upload/", UploadImageView_FromServer.as_view(), name="upload"),
    path("alert/", AlertView.as_view(), name="alert"),
]
