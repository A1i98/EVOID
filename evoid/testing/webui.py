"""WebUI — Docker-style test dashboard."""

from __future__ import annotations

import json
from typing import Any


def create_test_app(results: list[dict] | None = None) -> Any:
    """Create a Starlette app for test results."""
    try:
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import HTMLResponse, JSONResponse
        from starlette.routing import Route
    except ImportError:
        raise ImportError("uv add 'evoid[testing]'")

    _results = results or []

    async def dashboard(request: Request) -> HTMLResponse:
        return HTMLResponse(_html(_results))

    async def api(request: Request) -> JSONResponse:
        total = len(_results)
        passed = sum(1 for r in _results if r.get("outcome") == "passed")
        return JSONResponse({"total": total, "passed": passed, "failed": total - passed, "results": _results})

    return Starlette(routes=[Route("/", dashboard), Route("/api/results", api)])


def serve(results: list[dict], host: str = "0.0.0.0", port: int = 8001) -> None:
    """Serve the dashboard."""
    import uvicorn
    print(f"Dashboard: http://{host}:{port}")
    uvicorn.run(create_test_app(results), host=host, port=port)


def _html(results: list[dict]) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.get("outcome") == "passed")
    failed = total - passed
    duration = sum(r.get("duration", 0) for r in results)
    rate = (passed / total * 100) if total else 0
    color = "#10b981" if failed == 0 else "#ef4444"
    data = json.dumps(results)

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tests</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui;background:#0f172a;color:#e2e8f0;padding:2rem}}
.h{{margin-bottom:2rem}}.h h1{{font-size:1.5rem;font-weight:600}}.h p{{color:#94a3b8;font-size:.875rem;margin-top:.25rem}}
.s{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}}
.st{{background:#1e293b;border-radius:8px;padding:1.25rem;border:1px solid #334155}}
.sl{{font-size:.75rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em}}
.sv{{font-size:2rem;font-weight:700;margin-top:.25rem}}.sv.p{{color:#10b981}}.sv.f{{color:#ef4444}}.sv.t{{color:#3b82f6}}.sv.d{{color:#f59e0b}}
.ts{{background:#1e293b;border-radius:8px;border:1px solid #334155;overflow:hidden}}
.t{{display:flex;align-items:center;padding:.75rem 1rem;border-bottom:1px solid #334155}}.t:last-child{{border-bottom:none}}
.ti{{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;margin-right:.75rem;flex-shrink:0}}
.ti.p{{background:#10b981;color:#fff}}.ti.f{{background:#ef4444;color:#fff}}
.tn{{flex:1;font-size:.875rem}}.td{{color:#64748b;font-size:.75rem}}
.pb{{height:4px;background:#334155;border-radius:2px;margin-bottom:2rem;overflow:hidden}}
.pv{{height:100%;background:{color};width:{rate}%}}</style></head><body>
<div class="h"><h1>Test Dashboard</h1><p>EVOID IOP Tests</p></div>
<div class="pb"><div class="pv"></div></div>
<div class="s"><div class="st"><div class="sl">Total</div><div class="sv t">{total}</div></div>
<div class="st"><div class="sl">Passed</div><div class="sv p">{passed}</div></div>
<div class="st"><div class="sl">Failed</div><div class="sv f">{failed}</div></div>
<div class="st"><div class="sl">Duration</div><div class="sv d">{duration:.2f}s</div></div></div>
<div class="ts" id="ts"></div>
<script>const r={data};const c=document.getElementById('ts');r.forEach(x=>{{const d=document.createElement('div');d.className='t';const i=x.outcome==='passed'?'+':'x';const k=x.outcome==='passed'?'p':'f';d.innerHTML=`<div class="ti ${{k}}">${{i}}</div><div class="tn">${{x.name}}</div><div class="td">${{(x.duration||0).toFixed(3)}}s</div>`;c.appendChild(d)}})</script></body></html>"""
