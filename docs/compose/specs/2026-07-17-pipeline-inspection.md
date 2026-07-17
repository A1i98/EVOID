# Pipeline Inspection & Variable Routing API

> Give users visibility into pipeline execution and control over how specific variables flow through specific intents.

## [S1] Problem

Users need to:
1. See what happened during pipeline execution (which processors ran, what data they produced, timing)
2. Customize how a specific variable flows through a specific intent's pipeline
3. Route variables through specific processors at specific points

## [S2] Current State

### Already exists:
- `extend.py`: before/after/before_processor/after_processor/replace_pipeline/remove_processor
- `Result`: processors tuple + duration
- `Context`: state, deps, metadata, errors

### Missing:
- Per-processor timing and data capture
- Variable-specific routing rules
- Pipeline execution report

## [S3] Design: Pipeline Reporting

### Extend Result with per-processor details

```python
@dataclass(frozen=True)
class ProcessorResult:
    """What one processor did."""
    name: str
    duration: float
    input_state: dict[str, Any]  # snapshot before
    output_state: dict[str, Any]  # snapshot after
    success: bool
    error: Exception | None = None

@dataclass(frozen=True)
class Result:
    success: bool
    value: Any = None
    error: Exception | None = None
    processors: tuple[str, ...] = ()
    duration: float = 0.0
    # NEW: per-processor details
    steps: tuple[ProcessorResult, ...] = ()
```

### Usage

```python
result = await execute(intent)

# See which processors ran
for step in result.steps:
    print(f"{step.name}: {step.duration:.3f}s")

# See data flow through a specific variable
for step in result.steps:
    if "user_id" in step.output_state:
        print(f"{step.name} produced user_id={step.output_state['user_id']}")
```

## [S4] Design: Variable Routing

### Route specific variables through specific processors

```python
from evoid.core.extend import route_variable

# For intent "GET:/users/{id}", route "user_id" through "enrich_user" before "authorize"
route_variable(
    intent_name="GET:/users/{id}",
    variable="user_id",
    through="enrich_user",
    before="authorize",
)

# The enrich_user processor receives user_id in ctx.metadata
# and can transform it before authorize sees it
```

### How it works

1. User defines a routing rule: `route_variable(intent, variable, through, before)`
2. Before the target processor runs, the routing processor extracts the variable
3. The routing processor passes it to the specified processor
4. The result replaces the variable in ctx.metadata

### Processor contract for routed variables

```python
async def enrich_user(ctx: Context) -> dict:
    """Receives user_id, returns enriched user data."""
    user_id = ctx.metadata.get("user_id")
    user = await db.get_user(user_id)
    ctx.state["enriched_user"] = user
    return {"enriched": True}
```

## [S5] Implementation

### Files to modify:
- `evoid/core/pipeline.py` — add ProcessorResult, capture per-processor data
- `evoid/core/extend.py` — add route_variable()
- `evoid/core/runtime.py` — pass routing config to pipeline

### Files to create:
- `evoid/core/routing.py` — routing rule storage and resolution

### Files to document:
- `docs/docs-astro/src/content/docs/tutorial/pipeline-inspection.md`

## [S6] Pipeline Execution Flow

```
1. Intent arrives
2. Resolve pipeline (with overrides + routing rules)
3. For each processor:
   a. Snapshot ctx.state (input)
   b. Run processor
   c. Snapshot ctx.state (output)
   d. Record ProcessorResult(name, duration, input, output, success)
4. Return Result with steps
```

## [S7] Variable Routing Flow

```
1. Intent arrives with metadata {"user_id": 123}
2. Pipeline: [validate, authorize, handler]
3. Routing rule: route "user_id" through "enrich_user" before "authorize"
4. Modified pipeline: [validate, enrich_user, authorize, handler]
5. enrich_user receives user_id from ctx.metadata
6. enrich_user writes enriched_user to ctx.state
7. authorize can now use ctx.state["enriched_user"]
```
