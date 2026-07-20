---
title: 'Shooter: Multiplayer'
description: 'Connect two players, sync state, handle disconnects.'
---

# Shooter: Multiplayer

Connect two players and keep their game state synchronized.

## 1. Server: Room System

Add room management to the server:

```python
# server/rooms.py

rooms = {}  # room_id → {players, state}

async def create_room(room_id: str) -> dict:
    rooms[room_id] = {
        "players": {},
        "state": {"scores": {}},
    }
    return {"room_id": room_id, "created": True}


async def join_room(room_id: str, player_id: str) -> dict:
    if room_id not in rooms:
        await create_room(room_id)

    room = rooms[room_id]
    room["players"][player_id] = {
        "x": 960, "y": 540, "health": 100
    }
    room["state"]["scores"][player_id] = 0

    return {
        "room_id": room_id,
        "players": list(room["players"].keys()),
        "scores": room["state"]["scores"],
    }


async def leave_room(room_id: str, player_id: str) -> dict:
    if room_id in rooms:
        rooms[room_id]["players"].pop(player_id, None)
        rooms[room_id]["state"]["scores"].pop(player_id, None)

        if not rooms[room_id]["players"]:
            del rooms[room_id]

    return {"left": True}
```

## 2. Server: Broadcast to Room

Update the server to broadcast only to players in the same room:

```python
# server/main.py — update broadcast functions

room_connections = {}  # room_id → set of websockets

async def broadcast_to_room(room_id: str, message: dict):
    """Send message to all players in a room."""
    if room_id not in room_connections:
        return

    dead = set()
    for ws in room_connections[room_id]:
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(ws)

    room_connections[room_id] -= dead


# Update WebSocket handler
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    player_id = None
    room_id = None

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "connect":
                player_id = data.get("player_id")
                room_id = data.get("room_id", "default")

                # Add to room
                if room_id not in room_connections:
                    room_connections[room_id] = set()
                room_connections[room_id].add(websocket)

                # Join room
                result = await join_room(room_id, player_id)

                # Notify all players
                await broadcast_to_room(room_id, {
                    "type": "event",
                    "event": "player_joined",
                    "player_id": player_id,
                    "players": result["players"],
                    "scores": result["scores"],
                })

            elif data.get("type") == "intent":
                # Add player_id and room_id to metadata
                data["metadata"]["player_id"] = player_id
                data["metadata"]["room_id"] = room_id

                # Execute through EVOID pipeline
                from evoid.core.runtime import execute
                from evoid import Intent, Level
                intent = Intent(
                    name=data.get("name", ""),
                    level=Level(data.get("level", "standard")),
                    metadata=data.get("metadata", {}),
                )
                result = await execute(intent)

            elif data.get("type") == "disconnect":
                if player_id and room_id:
                    await leave_room(room_id, player_id)
                    await broadcast_to_room(room_id, {
                        "type": "event",
                        "event": "player_left",
                        "player_id": player_id,
                    })
                break

    except WebSocketDisconnect:
        if player_id and room_id:
            await leave_room(room_id, player_id)
            await broadcast_to_room(room_id, {
                "type": "event",
                "event": "player_left",
                "player_id": player_id,
            })
    finally:
        if room_id and websocket in room_connections.get(room_id, set()):
            room_connections[room_id].discard(websocket)
```

## 3. Client: Room Selection

Add a lobby scene to the Godot project:

```gdscript
# scripts/lobby.gd
extends Control
## Lobby — lets players create or join rooms.

@onready var room_input: LineEdit = $RoomInput
@onready var join_button: Button = $JoinButton
@onready var status_label: Label = $StatusLabel


func _ready() -> void:
    join_button.pressed.connect(_on_join_pressed)
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)


func _on_join_pressed() -> void:
    var room_id = room_input.text.strip_edges()
    if room_id.is_empty():
        status_label.text = "Enter a room name"
        return

    status_label.text = "Connecting..."
    EvoidApp.connect_to_server("ws://localhost:8000/ws", room_id)


func _on_connected(_data: Dictionary) -> void:
    status_label.text = "Connected! Joining room..."
    var room_id = room_input.text.strip_edges()

    EvoidApp.send_intent("player_join", {
        "player_id": "player_%d" % randi() % 10000,
        "room_id": room_id,
    })

    # Switch to game scene
    await get_tree().create_timer(0.5).timeout
    get_tree().change_scene_to_file("res://scenes/main.tscn")
```

## 4. Client: Sync Remote Players

Update the main script to handle multiple players:

```gdscript
# scripts/main.gd — update _on_player_joined

func _on_player_joined(payload: Dictionary) -> void:
    var player_id: String = payload.get("player_id", "")
    if player_id != local_player_id and player_id not in players:
        _spawn_player(player_id, false)

    # Update player list UI
    _update_player_list(payload.get("players", []))


func _on_player_left(payload: Dictionary) -> void:
    var player_id: String = payload.get("player_id", "")
    if player_id in players:
        players[player_id].queue_free()
        players.erase(player_id)


func _update_player_list(player_list: Array) -> void:
    # Update UI showing connected players
    var label = $HUD/PlayerList
    label.text = "Players: %d" % player_list.size()
```

## 5. Client: Score Display

```gdscript
# scripts/hud.gd
extends CanvasLayer
## HUD — shows health, score, and player list.

@onready var health_bar: ProgressBar = $HealthBar
@onready var score_label: Label = $ScoreLabel
@onready var player_list: Label = $PlayerList


func _ready() -> void:
    EvoidBus.subscribe("health_changed", _on_health_changed)
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)


func _on_health_changed(payload: Dictionary) -> void:
    health_bar.value = payload.get("health", 100)


func _on_game_event(payload: Dictionary) -> void:
    if payload.get("type") == "player_killed":
        var killer = payload.get("killer_id", "")
        var target = payload.get("target_id", "")
        score_label.text = "%s killed %s" % [killer, target]
```

## 6. Test Multiplayer

1. Start server: `python server/main.py`
2. Open Godot project
3. Run two instances
4. Both join the same room
5. Move and shoot — see each other's actions

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Room system | Players grouped by room ID |
| Broadcast | Send to all players in a room |
| Lobby | Room selection UI |
| Remote players | Spawn/despawn on join/leave |
| Score tracking | Server-side score management |

## Next

Now let's deploy as WebGL — [Web Export](shooter-web.md).
