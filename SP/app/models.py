from django.db import models

class Video(models.Model):
    # 影片檔案欄位
    file = models.FileField(upload_to='videos/')
    
    # 其他欄位，例如影片的描述、標題或上傳時間
    title = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # 你可以根據需要添加更多的欄位

    def __str__(self):
        return self.title or "Untitled"
