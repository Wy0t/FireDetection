- Step.1 Create .venv
- Step.2 python -m pip install Django
- Step.3 django-admin startproject FireDetection
- Step.4 cd FireDetection
- Step.5 python manage.py startapp detection
- Step.6 pip install channels djangorestframework
- Step.7 INSTALLED_APPS += ['channels', 'detection', 'rest_framework'] and ASGI_APPLICATION = 'FireDetection.asgi.application'
- Step.? pip install channels_redis
- Step.? pip install daphne
- Step.? pip install python-dotenv

# 啟用步驟

# 參數設置
- SECRET_KEY = 'django-secret-key'
- STREAM_URL = 'stream-url'

# 啟動後端
- daphne -p 8000 FireDetection.asgi:application
- daphne -p 8000 -b 0.0.0.0 FireDetection.asgi:application
啟動 redis 作為 Channels 的後端
- redis-server

