# EVOID Deployment

راهنمای استقرار اپلیکیشن EVOID در محیط production.

## مفاهیم پایه

### Deployment یعنی چی؟
Deployment یعنی انجام مراحل لازم برای در دسترس قرار دادن اپلیکیشن برای کاربران.

برای یک Web API، معمولاً شامل قرار دادن اون در یک ماشین راه دور با یک سرور هست که عملکرد و پایداری خوبی داشته باشه.

### تفاوت Development و Production
| جنبه | Development | Production |
|------|-------------|------------|
| سرور | `evo service run` | Uvicorn/Gunicorn با workers |
| Auto-reload | فعال | غیرفعال |
| Debug | فعال | غیرفعال |
| Logging | ساده | ساختاریافته |
| SSL | نداره | الزامی |

## استراتژی‌های deployment

### ۱. اجرای دستی

```bash
# اجرای ساده
evo service run api

# اجرا با Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# اجرا با Robyn
python main.py
```

### ۲. Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install -e .

COPY . .

EXPOSE 8000

CMD ["evo", "service", "run", "api"]
```

```bash
docker build -t my-api .
docker run -p 8000:8000 my-api
```

### ۳. Systemd Service

```ini
[Unit]
Description=EVOID API Service
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/opt/my-api
ExecStart=/opt/my-api/.venv/bin/evo service run api
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable my-api
sudo systemctl start my-api
```

### ۴. Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    restart: unless-stopped
```

## SSL / HTTPS

### با Certbot (Let's Encrypt)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d myapi.example.com
```

### با Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name myapi.example.com;

    ssl_certificate /etc/letsencrypt/live/myapi.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapi.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## بهترین شیوه‌ها

### لاگینگ
```python
from evoid.engines.logger import structlog as log

log.init("my-api", level="INFO")
```

### Environment Variables
```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
```

### Graceful Shutdown
```python
import signal
import sys

def shutdown(sig, frame):
    # Cleanup resources
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
```

### Health Check
```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/health", level="ephemeral")
async def health() -> dict:
    return {"status": "healthy"}
```

## Worker Configuration

### Uvicorn with Workers
```bash
# CPU cores * 2 + 1
uvicorn main:app --workers 9 --host 0.0.0.0 --port 8000
```

### با Gunicorn + Uvicorn Workers
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## مانیتورینگ

### Process Management
```bash
# بررسی وضعیت سرویس
systemctl status my-api

# مشاهده لاگ‌ها
journalctl -u my-api -f

# ریستارت
systemctl restart my-api
```

### Metrics
```python
from evoid.engines.metrics import simple as metrics

# افزایش counter
metrics.increment("requests.total")

# ثبت زمان اجرا
start = metrics.timer_start("request.duration")
# ... اجرای درخواست
metrics.timer_stop("request.duration", start)
```
