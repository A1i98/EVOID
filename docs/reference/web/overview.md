# EVOID Web Overview

## EVOID چیست؟

EVOID یک runtime مرجع برای Intent-Oriented Programming (IOP) هست. داده‌هات به سیستم میگن چی میخوان. Runtime مدیریت می‌کنه چطور انجام بشه.

## ویژگی‌های کلیدی

| ویژگی | توضیح |
|-------|-------|
| **Intent-Driven** | داده اعلام می‌کنه چی میخواد، runtime تصمیم می‌گیره چطور انجام بده |
| **Async-Native** | پشتیبانی کامل async/await |
| **Plugin-Based** | هر engine قابل تعویض هست |
| **Pipeline Composition** | Processorها توابع خالص هستن که کنار هم قرار می‌گیرن |
| **Multi-Adapter** | ASGI, CLI, Telegram, Robyn, WebSocket |
| **Zero Overhead** | IOP بدون هزینه اضافی اجرا میشه |

## نصب

```bash
uv add evoid
```

یا با pip:

```bash
pip install evoid
```

الزامی: Python 3.13+

## مثال اولیه

### @route (Function-based)

```python
from evoid.web.route import Service, get, post

app = Service("my-api")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}

@get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    return {"id": user_id, "name": f"User {user_id}"}

@post("/users")
async def create_user(name: str, email: str) -> dict:
    return {"status": "created", "name": name}
```

### @controller (Class-based)

```python
from evoid.web.controller import Service, Controller, GET, POST

app = Service("my-api")

@Controller("/users")
class UserController:
    @GET("/{user_id}")
    async def get_user(self, user_id: int) -> dict:
        return {"id": user_id}

    @POST("/")
    async def create_user(self, name: str, email: str) -> dict:
        return {"status": "created"}
```

### Native (Full Control)

```python
from evoid import Intent, Level, add_intent

MY_INTENT = Intent(name="get_user", level=Level.STANDARD)

async def handler(intent: Intent) -> dict:
    return {"id": 1, "name": "Alice"}

add_intent(MY_INTENT, handler)
```

## اجرا

```bash
evo init my-api
cd my-api
evo service new api
evo service run api
```

سرور در `http://0.0.0.0:8000` شروع میشه.

## چیزی که با یک declaration دریافت می‌کنی

با یک declaration ساده از type:
- **Editor support** — completion، type checks
- **Validation** — اعتبارسنجی خودکار با خطاهای واضح
- **Input conversion** — JSON، path params، query params، cookies، headers
- **Output conversion** — Python types → JSON
- **Pipeline execution** — processorها به ترتیب اجرا میشن

## Intent Levels

| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache، sessions، داده موقت |
| `standard` | `validate`, `authorize` | 10s | پروفایل کاربر، پست، نظرات |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | پرداخت، پزشکی، حقوقی |

## تفاوت EVOID با FastAPI

| جنبه | FastAPI | EVOID |
|------|---------|-------|
| پارادایم | OOP + FP | IOP |
| جریان داده | Request → Response | Intent → Pipeline → Result |
| Extension | Middleware | Pipeline Extension (before/after) |
| Communication | HTTP | Intent-based (Message Bus) |
| State | Request-scoped | Context (mutable databag) |
| Validation | Pydantic model | Schema Engine (pluggable) |
