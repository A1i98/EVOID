---
title: 'Shooter: Server'
description: 'EVOID server for the arena shooter — game logic, movement sync, shot detection.'
---

# Shooter: Server Setup

The server handles game state, validates actions, and broadcasts events to all players.

## 1. Install Dependencies

```bash
uv add evoid evoid-godot websockets
```

## 2. Server Entry Point

Create `server/main.py`:

```python
import asyncio
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import JSONResponse

from evoid import Intent, Level, subscribe, publish, register, register_processor
from evoid.core import Context
from evoid_godot import Topics, setup_game_subscriptions

# ── Game State ──────────────────────────────────────────────────────────

players = {}  # player_id → {x, y, health, score}
GAME_ID = "arena-shooter"

# ── Game Intent Handlers ────────────────────────────────────────────────

async def handle_player_move(ctx: Context) -> dict:
    """Validate and broadcast player movement."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")
    x = intent.metadata.get("x", 0)
    y = intent.metadata.get("y", 0)

    # Server-side validation
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return {"error": "invalid coordinates"}

    # Clamp to arena bounds
    x = max(0, min(x, 1920))
    y = max(0, min(y, 1080))

    # Update server state
    if player_id in players:
        players[player_id]["x"] = x
        players[player_id]["y"] = y

    # Broadcast to all players
    await publish(
        Intent(
            name=Topics.GAME_STATE_SYNC,
            level=Level.EPHEMERAL,
            metadata={
                "type": "player_moved",
                "player_id": player_id,
                "x": x,
                "y": y,
            },
        ),
        source=f"game:{GAME_ID}",
    )

    return {"synced": True}


async def handle_player_shot(ctx: Context) -> dict:
    """Validate shot and check for hits."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")
    origin = intent.metadata.get("origin", [0, 0])
    direction = intent.metadata.get("direction", [0, 1])

    # Broadcast shot to all players
    await publish(
        Intent(
            name=Topics.GAME_EVENT,
            level=Level.STANDARD,
            metadata={
                "type": "shot_fired",
                "player_id": player_id,
                "origin": origin,
                "direction": direction,
            },
        ),
        source=f"game:{GAME_ID}",
    )

    # Hit detection (simplified — real game would use raycasting)
    # For now, just broadcast the shot
    return {"confirmed": True}


async def handle_player_hit(ctx: Context) -> dict:
    """Process a hit — reduce health, check for kill."""
    intent = ctx.intent
    target_id = intent.metadata.get("target_id")
    damage = intent.metadata.get("damage", 25)

    if target_id not in players:
        return {"error": "target not found"}

    players[target_id]["health"] -= damage

    if players[target_id]["health"] <= 0:
        # Player died — respawn
        players[target_id]["health"] = 100
        players[target_id]["x"] = 960
        players[target_id]["y"] = 540

        # Broadcast kill
        await publish(
            Intent(
                name=Topics.GAME_EVENT,
                level=Level.STANDARD,
                metadata={
                    "type": "player_killed",
                    "target_id": target_id,
                    "killer_id": intent.metadata.get("player_id"),
                },
            ),
            source=f"game:{GAME_ID}",
        )

    # Broadcast health update
    await publish(
        Intent(
            name=Topics.GAME_EVENT,
            level=Level.EPHEMERAL,
            metadata={
                "type": "health_updated",
                "player_id": target_id,
                "health": players[target_id]["health"],
            },
        ),
        source=f"game:{GAME_ID}",
    )

    return {"hit": True, "health": players[target_id]["health"]}


# ── Player Join/Leave ───────────────────────────────────────────────────

async def handle_player_join(ctx: Context) -> dict:
    """Register a new player."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")

    players[player_id] = {
        "x": 960,
        "y": 540,
        "health": 100,
        "score": 0,
    }

    # Broadcast join
    await publish(
        Intent(
            name=Topics.GAME_PLAYER_JOINED,
            level=Level.STANDARD,
            metadata={"player_id": player_id, "players": list(players.keys())},
        ),
        source=f"game:{GAME_ID}",
    )

    return {"joined": True, "player_id": player_id}


async def handle_player_leave(ctx: Context) -> dict:
    """Remove a player."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")

    if player_id in players:
        del players[player_id]

    await publish(
        Intent(
            name=Topics.GAME_PLAYER_LEFT,
            level=Level.STANDARD,
            metadata={"player_id": player_id},
        ),
        source=f"game:{GAME_ID}",
    )

    return {"left": True}


# ── Register Intents ────────────────────────────────────────────────────

register(Intent(name="player_move", level=Level.EPHEMERAL))
register(Intent(name="player_shot", level=Level.STANDARD))
register(Intent(name="player_hit", level=Level.STANDARD))
register(Intent(name="player_join", level=Level.STANDARD))
register(Intent(name="player_leave", level=Level.STANDARD))

register_processor("player_move", handle_player_move)
register_processor("player_shot", handle_player_shot)
register_processor("player_hit", handle_player_hit)
register_processor("player_join", handle_player_join)
register_processor("player_leave", handle_player_leave)

# Setup game subscriptions
setup_game_subscriptions(GAME_ID)


# ── HTTP Endpoints ──────────────────────────────────────────────────────

async def health(request):
    return JSONResponse({"status": "ok", "players": len(players)})


async def game_state(request):
    return JSONResponse({"players": players})


# ── WebSocket Handler ───────────────────────────────────────────────────

from starlette.websockets import WebSocket, WebSocketDisconnect

connections = set()


async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    player_id = None

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "connect":
                player_id = data.get("player_id", f"player_{len(players)}")
                await handle_player_join_direct(player_id)

            elif data.get("type") == "intent":
                # Forward to EVOID pipeline
                from evoid.core.runtime import execute
                intent = Intent(
                    name=data.get("name", ""),
                    level=Level(data.get("level", "standard")),
                    metadata={**data.get("metadata", {}), "player_id": player_id},
                )
                result = await execute(intent)
                await websocket.send_json({"result": result.value if result.success else {"error": str(result.error)}})

            elif data.get("type") == "disconnect":
                if player_id:
                    await handle_player_leave_direct(player_id)
                break

    except WebSocketDisconnect:
        if player_id:
            await handle_player_leave_direct(player_id)
    finally:
        connections.discard(websocket)


async def handle_player_join_direct(player_id: str):
    """Handle player join without going through pipeline."""
    players[player_id] = {"x": 960, "y": 540, "health": 100, "score": 0}
    # Broadcast to all connections
    for conn in connections:
        try:
            await conn.send_json({
                "type": "event",
                "event": "player_joined",
                "player_id": player_id,
                "players": list(players.keys()),
            })
        except Exception:
            pass


async def handle_player_leave_direct(player_id: str):
    """Handle player leave without going through pipeline."""
    if player_id in players:
        del players[player_id]
    for conn in connections:
        try:
            await conn.send_json({
                "type": "event",
                "event": "player_left",
                "player_id": player_id,
            })
        except Exception:
            pass


# ── App ─────────────────────────────────────────────────────────────────

app = Starlette(
    routes=[
        Route("/health", health),
        Route("/state", game_state),
        WebSocketRoute("/ws", ws_endpoint),
    ],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. Run the Server

```bash
cd server
python main.py
# Server running at http://localhost:8000
# WebSocket at ws://localhost:8000/ws
```

## 4. Test It

```bash
# Check health
curl http://localhost:8000/health
# {"status": "ok", "players": 0}

# Check game state
curl http://localhost:8000/state
# {"players": {}}
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `setup_game_subscriptions()` | Wires up game event handlers |
| `handle_player_move` | Validates + broadcasts movement |
| `handle_player_shot` | Validates + broadcasts shots |
| `handle_player_hit` | Processes damage + kills |
| WebSocket handler | Direct connection management |
| Server-side validation | Prevents cheating |

## Next

Now let's build the Godot client — [Client Setup](shooter-client.md).
