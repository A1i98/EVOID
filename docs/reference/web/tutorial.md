# EVOID Tutorial Structure

ساختار آموزش EVOID — از ساده به پیچیده، گام به گام.

## ساختار Tutorial

### پایه
1. First Steps — اولین endpoint با @route
2. Path Parameters — پارامترهای مسیر
3. Query Parameters — پارامترهای query string
4. Request Body — دریافت داده از body
5. Validation — اعتبارسنجی داده‌ها

### Intent & Pipeline
6. Intent Levels — سه سطح حفاظت
7. Pipeline Basics — درک pipeline execution
8. Pipeline Extension — اضافه کردن processor قبل/بعد
9. Pipeline Inspection — بررسی state در هر مرحله

### Processors
10. Custom Processors — نوشتن processor سفارشی
11. Built-in Processors — validator، auth، rate limiter
12. Processor Composition — ترکیب processorها

### Web Patterns
13. @controller Style — کنترلرهای کلاس‌محور
14. Error Handling — مدیریت خطاها
15. Response Status Codes — کدهای وضعیت
16. Middleware Patterns — الگوهای middleware

### Advanced
17. Parallel Execution — اجرای موازی Intentها
18. Inter-Service Communication — ارتباط بین سرویس‌ها
19. Message Bus — انتشار و اشتراک‌گذاری
20. Custom Adapters — نوشتن adapter سفارشی

### Infrastructure
21. Dependency Injection — تزریق وابستگی
22. Caching — کش با Intent levels
23. Storage — ذخیره‌سازی داده
24. Configuration — پیکربندی پروژه

### Testing & Deployment
25. Testing — تست pipeline و processorها
26. Debugging — عیب‌یابی
27. Deployment — استقرار در production

## الگوی هر صفحه

هر صفحه آموزشی این ساختار رو دنبال می‌کنه:

```
1. عنوان + توضیح کوتاه
2. مثال minimal (5-10 خط)
3. توضیح خط به خط
4. مثال پیشرفته‌تر
5. نکات و بهترین شیوه‌ها
6. لینک به صفحه بعدی
```

## مثال: First Steps

### هدف
ساخت اولین endpoint در ۳ خط.

### @route style
```python
from evoid.web.route import Service, get

app = Service("my-api")

@get("/")
async def home() -> dict:
    return {"message": "Hello from EVOID!"}
```

### Native style
```python
from evoid import Intent, Level, add_intent

HELLO = Intent(name="hello", level=Level.EPHEMERAL)

async def handler(intent: Intent) -> dict:
    return {"message": "Hello from EVOID!"}

add_intent(HELLO, handler)
```

### چی اتفاق افتاد؟
1. **Intent** — یک declaration از هدف ایجاد شد
2. **Processor** — تابع handler به عنوان processor ثبت شد
3. **Pipeline** — runtime یک pipeline پیش‌فرض بر اساس level ساخت

### بعدی: Path Parameters →

## مثال: Intent Levels

### هدف
درک تفاوت سه سطح حفاظت.

### سه سطح
```python
from evoid.web.route import Service, get, post

app = Service("my-api")

# EPHEMERAL — فقط validate
@get("/cache/data", level="ephemeral")
async def cached_data() -> dict:
    return {"data": "cached"}

# STANDARD — validate + authorize
@get("/users/{id}", level="standard")
async def get_user(id: int) -> dict:
    return {"id": id}

# CRITICAL — validate + authorize + audit + protect
@post("/payments", level="critical")
async def process_payment(amount: float) -> dict:
    return {"status": "paid"}
```

### هر level چیکار می‌کنه؟
| Level | Pipeline | Timeout | Use Case |
|-------|----------|---------|----------|
| `ephemeral` | `validate` | 5s | Cache، sessions |
| `standard` | `validate`, `authorize` | 10s | کاربران، پست‌ها |
| `critical` | `validate`, `authorize`, `audit`, `protect` | 30s | پرداخت، اسناد حقوقی |

### بعدی: Pipeline Basics →

## مثال: Custom Processor

### هدف
نوشتن یک processor سفارشی.

### کد
```python
from evoid.core import Context, register_processor

async def enrich_user(ctx: Context) -> dict:
    # خواندن از state
    user_id = ctx.state.get("user_id")

    # پردازش
    user = await db.get_user(user_id)

    # نوشتن در state
    ctx.state["user"] = user

    return {"enriched": True}

register_processor("enrich_user", enrich_user)
```

### بعدی: Pipeline Extension →

## مثال: Pipeline Extension

### هدف
اضافه کردن processor به pipeline بدون جایگزینی.

### کد
```python
from evoid.core.extend import before, after, before_processor

# اضافه کردن قبل از handler
before("GET:/users/{id}", "log_request")

# اضافه کردن بعد از handler
after("GET:/users/{id}", "cache_response")

# اضافه کردن قبل از processor خاص
before_processor("GET:/users/{id}", "authorize", "check_permission")
```

### بعدی: Parallel Execution →
