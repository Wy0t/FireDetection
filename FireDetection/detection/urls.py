from django.urls import path
from .views import UploadImageView, AlertView

urlpatterns = [
    path("upload_image/", UploadImageView.as_view(), name="upload_image"),
    path("alert/", AlertView.as_view(), name="alert"),
]
