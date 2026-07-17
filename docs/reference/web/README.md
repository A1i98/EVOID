# EVOID Web Documentation Reference

ساختار داکیومنت وب بر اساس الگوهای جهانی (FastAPI, Express, Gin) و پارادایم IOP.

## ساختار

```
Web Documentation
├── README.md              — این فایل
├── overview.md            — ویژگی‌ها، نصب، مثال اولیه
├── tutorial.md            — ساختار آموزش (گام به گام)
└── deployment.md          — استراتژی‌های deployment
```

## اصول داکیومنت‌نویسی EVOID

### ۱. Code-First
هر مفهوم با یک مثال کد شروع میشه. کاربر باید بتونه کد رو کپی و اجرا کنه.

### ۲. IOP-Centric
تمام مثال‌ها بر پارادایم IOP بنا شده‌اند:
- **Intent** جایگزین Route decorator میشه
- **Pipeline** جایگزین Middleware chain میشه
- **Processor** جایگزین Controller method میشه
- **Context** جایگزین Request/Response object میشه

### ۳. Three Syntax Styles
هر مثال در سه سینتکس ارائه میشه:
- **@route** — Function-based (سریع‌ترین شروع)
- **@controller** — Class-based (سازمان‌یافته)
- **Native** — Full control (انعطاف‌پذیرترین)

### ۴. Progressive Complexity
آموزش از ساده به پیچیده:
1. Minimal example (5 خط)
2. Path parameters
3. Request body
4. Validation
5. Processors
6. Pipeline customization
7. Parallel execution
8. Inter-service communication

## الگوهای مستندات جهانی

| الگو | FastAPI | Express | EVOID |
|------|---------|---------|-------|
| Badges | ✓ | ✓ | ✓ |
| Social proof | ✓ | ✗ | آینده |
| Step-by-step tutorial | ✓ | ✓ | ✓ |
| API Reference | ✓ | ✓ | آینده |
| Interactive docs | Swagger | ✗ | آینده |
| Performance benchmarks | ✓ | ✗ | آینده |
| Deployment guide | ✓ | ✓ | ✓ |
| How-To recipes | ✓ | ✗ | آینده |
| Multi-language | ✓ | ✗ | آینده |
