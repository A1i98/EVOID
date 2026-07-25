---
title: 'Shooter: Multiplayer'
description: 'Room system, state sync, disconnect handling. Multiple players in the same game.'
---

# Shooter: Multiplayer

Multiple players share the same game. The server manages rooms and synchronizes state.

## How It Works

```
Player A connects → joins "room_1" → server creates room
Player B connects → joins "room_1" → server adds to room
Both see each other's movements and shots
Player A disconnects → server removes from room
Player B continues alone
```

The server already handles rooms (from the server tutorial). The client needs a lobby to pick a room.

## 1. Client: Lobby Scene

Create `scenes/Lobby.tscn` with a LineEdit, Button, and Label.

Create `scripts/Lobby.gd`:

```gdscript
extends Control
## Lobby — pick a room name, connect to server.

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
    status_label.text = "Connected!"
    await get_tree().create_timer(0.5).timeout
    get_tree().change_scene_to_file("res://scenes/World.tscn")
```

## 2. Client: Remote Player Sync

Update `World.gd` to handle remote players:

```gdscript
# Add to World.gd

var player_scene: PackedScene = preload("res://scenes/Player.tscn")
var local_player_id: String = ""
var players: Dictionary = {}  # player_id → node


func _ready() -> void:
    # ... existing subscriptions ...
    EvoidBus.subscribe("player_joined", _on_player_joined)
    EvoidBus.subscribe("player_left", _on_player_left)


func _on_player_joined(data: Dictionary) -> void:
    var pid = data.get("player_id", "")
    if pid != local_player_id and pid not in players:
        var player = player_scene.instantiate()
        player.global_position = Vector2(200, 180)
        player.is_local = false
        add_child(player)
        players[pid] = player


func _on_player_left(data: Dictionary) -> void:
    var pid = data.get("player_id", "")
    if pid in players:
        players[pid].queue_free()
        players.erase(pid)
```

## 3. Client: Score Display

Create `scripts/HUD.gd`:

```gdscript
extends CanvasLayer
## HUD — shows score and highscore.

var highscore: float = 0.0


func _ready() -> void:
    EvoidBus.subscribe("enemy_killed", _on_enemy_killed)


func _on_enemy_killed(data: Dictionary) -> void:
    var score = data.get("score", 0)
    $ScoreLabel.text = str(score)
    if score > highscore:
        highscore = score
        $HighscoreLabel.text = "Highscore: " + str(highscore)
```

## 4. What Changes

| Before (Single Player) | After (Multiplayer) |
|------------------------|---------------------|
| Enemies spawn from server | Same — server controls spawning |
| Local player only | Remote players appear |
| Score is local | Score is server-authoritative |
| No lobby | Room selection before game |

## 5. Test

1. Start server: `python main.py`
2. Open Godot, run instance 1 → join "room_1"
3. Open Godot again, run instance 2 → join "room_1"
4. Both players see the same enemies and each other

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Room system | Players grouped by room ID |
| Remote players | Spawn on join, despawn on leave |
| Server-authoritative score | Client reads, server writes |
| Lobby | Room selection before game |

## Next

Deploy as WebGL — [Web Export](shooter-web.md).
