---
title: 'Shooter: Server'
description: 'EVOID server: enemy spawning, difficulty scaling, game state, hit detection.'
---

# Shooter: Server Setup

The server owns all game state. Clients send intents. The server validates, updates, and broadcasts.

## 1. Install Dependencies

```bash
uv add evoid evoid-godot websockets
```

## 2. Game State

Create `server/game.py`:

```python
from dataclasses import dataclass, field
from evoid import Intent, Level

# ── Enemy Definitions ──────────────────────────────────────────────────

@dataclass(frozen=True)
class EnemyType:
    name: str
    speed: int
    hp: int
    knockback: int
    screen_shake: int
    points: float

ENEMIES = {
    "red":   EnemyType(name="red",   speed=80,  hp=4, knockback=600,  screen_shake=120, points=1.0),
    "teal":  EnemyType(name="teal",  speed=40,  hp=5, knockback=400,  screen_shake=300, points=3.0),
    "purple": EnemyType(name="purple", speed=150, hp=1, knockback=2000, screen_shake=50,  points=0.5),
}

# ── Game Room (data only, no methods) ──────────────────────────────────

@dataclass
class GameRoom:
    room_id: str
    players: dict = field(default_factory=dict)   # player_id → {x, y, health, score}
    enemies: dict = field(default_factory=dict)   # enemy_id → {type, x, y, hp}
    spawn_timer: float = 3.0
    difficulty_tick: float = 1.0
    next_enemy_id: int = 0


def spawn_enemy(room: GameRoom) -> dict:
    """Create a new enemy and add it to the room. Returns enemy data."""
    import random
    enemy_type = random.choice(list(ENEMIES.values()))
    # Spawn outside 640x360 viewport
    x = random.uniform(-160, 670)
    y = random.uniform(-90, 390)
    while 0 < x < 640 and 0 < y < 360:
        x = random.uniform(-160, 670)
        y = random.uniform(-90, 390)

    enemy_id = f"enemy_{room.next_enemy_id}"
    room.next_enemy_id += 1

    room.enemies[enemy_id] = {
        "type": enemy_type.name,
        "x": x, "y": y,
        "hp": enemy_type.hp,
        "speed": enemy_type.speed,
        "points": enemy_type.points,
    }
    return {"enemy_id": enemy_id, **room.enemies[enemy_id]}


def tick_difficulty(room: GameRoom) -> float:
    """Decrease spawn interval. Returns new interval."""
    if room.spawn_timer > 0.25:
        room.spawn_timer -= 0.025
    return room.spawn_timer
```

## 3. Intent Handlers

Create `server/main.py`:

```python
import asyncio
import json
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from evoid import Intent, Level, register, register_processor
from evoid.core import Context
from evoid_godot import GameHost, setup_game_subscriptions
from game import GameRoom, ENEMIES, spawn_enemy, tick_difficulty

# ── State ──────────────────────────────────────────────────────────────

rooms = {}             # room_id → GameRoom
connections = {}       # room_id → set of websockets
GAME_ID = "top-down-shooter"

# ── Intent Handlers ────────────────────────────────────────────────────

async def handle_player_move(ctx: Context) -> dict:
    """Validate and broadcast player movement."""
    meta = ctx.intent.metadata
    player_id = meta.get("player_id")
    room_id = meta.get("room_id", "default")
    x = max(0, min(meta.get("x", 0), 640))
    y = max(0, min(meta.get("y", 0), 360))

    room = rooms.get(room_id)
    if room and player_id in room.players:
        room.players[player_id]["x"] = x
        room.players[player_id]["y"] = y

    return {"synced": True}


async def handle_player_shot(ctx: Context) -> dict:
    """Validate shot and broadcast to room."""
    meta = ctx.intent.metadata
    room_id = meta.get("room_id", "default")
    await broadcast_to_room(room_id, {
        "type": "event", "event": "shot_fired",
        "player_id": meta.get("player_id"),
        "origin": meta.get("origin", [0, 0]),
        "direction": meta.get("direction", [0, 1]),
    })
    return {"confirmed": True}


async def handle_enemy_hit(ctx: Context) -> dict:
    """Process bullet hitting enemy. Server decides damage."""
    meta = ctx.intent.metadata
    room_id = meta.get("room_id", "default")
    enemy_id = meta.get("enemy_id")
    room = rooms.get(room_id)

    if not room or enemy_id not in room.enemies:
        return {"error": "enemy not found"}

    enemy = room.enemies[enemy_id]
    enemy["hp"] -= 1

    if enemy["hp"] <= 0:
        # Enemy killed
        enemy_type = ENEMIES[enemy["type"]]
        player_id = meta.get("player_id")
        if player_id in room.players:
            room.players[player_id]["score"] += enemy_type.points

        del room.enemies[enemy_id]

        await broadcast_to_room(room_id, {
            "type": "event", "event": "enemy_killed",
            "enemy_id": enemy_id,
            "player_id": player_id,
            "score": room.players.get(player_id, {}).get("score", 0),
            "screen_shake": enemy_type.screen_shake,
        })
        return {"killed": True, "score": room.players[player_id]["score"]}

    # Enemy damaged but alive
    await broadcast_to_room(room_id, {
        "type": "event", "event": "enemy_damaged",
        "enemy_id": enemy_id, "hp": enemy["hp"],
    })
    return {"damaged": True, "hp": enemy["hp"]}


async def handle_player_hit(ctx: Context) -> dict:
    """Player touched by enemy. One hit = death."""
    meta = ctx.intent.metadata
    room_id = meta.get("room_id", "default")
    player_id = meta.get("player_id")
    room = rooms.get(room_id)

    if room and player_id in room.players:
        await broadcast_to_room(room_id, {
            "type": "event", "event": "player_killed",
            "player_id": player_id,
        })
    return {"died": True}


# ── Register Intents ───────────────────────────────────────────────────

for name, level in [
    ("player_move", Level.EPHEMERAL),
    ("player_shot", Level.STANDARD),
    ("enemy_hit", Level.STANDARD),
    ("player_hit", Level.CRITICAL),
]:
    register(Intent(name=name, level=level))

register_processor("player_move", handle_player_move)
register_processor("player_shot", handle_player_shot)
register_processor("enemy_hit", handle_enemy_hit)
register_processor("player_hit", handle_player_hit)

setup_game_subscriptions(GAME_ID)


# ── WebSocket + Broadcast ──────────────────────────────────────────────

async def broadcast_to_room(room_id: str, message: dict):
    if room_id not in connections:
        return
    dead = set()
    for ws in connections[room_id]:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)
    connections[room_id] -= dead


async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    player_id = None
    room_id = None

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "connect":
                player_id = data.get("player_id", f"p_{id(websocket)}")
                room_id = data.get("room_id", "default")

                if room_id not in rooms:
                    rooms[room_id] = GameRoom(room_id=room_id)
                if room_id not in connections:
                    connections[room_id] = set()
                connections[room_id].add(websocket)

                room = rooms[room_id]
                room.players[player_id] = {"x": 320, "y": 180, "health": 1, "score": 0}

                await broadcast_to_room(room_id, {
                    "type": "event", "event": "player_joined",
                    "player_id": player_id,
                    "players": list(room.players.keys()),
                })

            elif data.get("type") == "intent":
                from evoid.core.runtime import execute
                intent = Intent(
                    name=data.get("name", ""),
                    level=Level(data.get("level", "standard")),
                    metadata={**data.get("metadata", {}), "player_id": player_id, "room_id": room_id},
                )
                result = await execute(intent)
                await websocket.send_json({
                    "result": result.value if result.success else {"error": str(result.error)}
                })

            elif data.get("type") == "disconnect":
                break

    except WebSocketDisconnect:
        pass
    finally:
        if player_id and room_id:
            room = rooms.get(room_id)
            if room:
                room.players.pop(player_id, None)
            await broadcast_to_room(room_id, {
                "type": "event", "event": "player_left", "player_id": player_id,
            })
            connections.get(room_id, set()).discard(websocket)


# ── Background Tasks ───────────────────────────────────────────────────

async def game_loop():
    """Server-side game loop: spawn enemies, tick difficulty."""
    while True:
        await asyncio.sleep(1.0)
        for room_id, room in list(rooms.items()):
            if not room.players:
                continue

            # Tick difficulty
            tick_difficulty(room)

            # Spawn enemy
            enemy = spawn_enemy(room)
            await broadcast_to_room(room_id, {
                "type": "event", "event": "enemy_spawned", **enemy,
            })


# ── App ────────────────────────────────────────────────────────────────

from evoid_godot import SplashConfig

host = GameHost()
host.register_build(GAME_ID, "builds/top-down-shooter/", title="Top-Down Shooter",
    splash=SplashConfig(bg_color="#0d1117", accent_color="#e94560", subtitle="Top-Down Shooter"))

app = Starlette(
    routes=[
        Mount("/game", app=host.create_router()),
        WebSocketRoute("/ws", ws_endpoint),
    ],
    on_startup=[lambda: asyncio.create_task(game_loop())],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. Run

```bash
cd server && python main.py
# Server: http://localhost:8000
# WebSocket: ws://localhost:8000/ws
# Game: http://localhost:8000/game/top-down-shooter/
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `GameRoom` | Server-owned game state (dataclass) |
| `EnemyType` | Frozen dataclass for enemy stats |
| `game_loop()` | Background task: spawn enemies, tick difficulty |
| Intent handlers | Validate + update + broadcast |
| `broadcast_to_room()` | Send events to all players in a room |

## Next

Now build the Godot client — [Client Setup](shooter-client.md).
