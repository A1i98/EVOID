---
title: 'Tic-Tac-Toe: Multiplayer'
description: 'Room system, matchmaking, private games.'
---

# Tic-Tac-Toe: Multiplayer

Add room system and matchmaking for private games.

## 1. Server: Room Management

The server already has room support (from `tictactoe-server.md`). Let's add matchmaking:

```python
# server/matchmaking.py

waiting_players = {}  # room_id → player_id
active_games = {}     # room_id → Game


async def quick_match(player_id: str) -> dict:
    """Find or create a game."""
    # Check for waiting players
    for room_id, waiting_id in list(waiting_players.items()):
        if waiting_id != player_id:
            # Found a match!
            del waiting_players[room_id]
            return {"room_id": room_id, "opponent": waiting_id}

    # No match — create new room and wait
    room_id = "room_%d" % hash(player_id) % 100000
    waiting_players[room_id] = player_id
    return {"room_id": room_id, "waiting": True}


async def cancel_match(player_id: str) -> dict:
    """Cancel waiting for a match."""
    for room_id, waiting_id in list(waiting_players.items()):
        if waiting_id == player_id:
            del waiting_players[room_id]
            return {"cancelled": True}
    return {"error": "not_waiting"}
```

## 2. Server: Add Matchmaking Endpoints

```python
# server/main.py — add to routes

from matchmaking import quick_match, cancel_match

async def handle_quick_match(ctx: Context) -> dict:
    player_id = ctx.intent.metadata.get("player_id")
    return await quick_match(player_id)


async def handle_cancel_match(ctx: Context) -> dict:
    player_id = ctx.intent.metadata.get("player_id")
    return await cancel_match(player_id)


register(Intent(name="quick_match", level=Level.STANDARD))
register(Intent(name="cancel_match", level=Level.STANDARD))
register_processor("quick_match", handle_quick_match)
register_processor("cancel_match", handle_cancel_match)
```

## 3. Client: Quick Match Button

Update the lobby:

```gdscript
# scripts/lobby.gd — add quick match

@onready var quick_match_button: Button = $QuickMatchButton
@onready var private_button: Button = $PrivateButton


func _ready() -> void:
    quick_match_button.pressed.connect(_on_quick_match)
    private_button.pressed.connect(_on_private_game)
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)


func _on_quick_match() -> void:
    status_label.text = "Searching for opponent..."
    EvoidApp.send_intent("quick_match", {"player_id": player_id})


func _on_private_game() -> void:
    var room = room_input.text.strip_edges()
    if room.is_empty():
        status_label.text = "Enter a room name"
        return
    EvoidApp.connect_to_server("ws://localhost:8000/ws", room)


func _on_game_event(payload: Dictionary) -> void:
    var event_type = payload.get("type", "")

    match event_type:
        "match_found":
            var room_id = payload.get("room_id")
            status_label.text = "Match found! Joining..."
            EvoidApp.connect_to_server("ws://localhost:8000/ws", room_id)
        "waiting":
            status_label.text = "Waiting for opponent..."
```

## 4. Client: Turn Indicator

Show whose turn it is:

```gdscript
# scripts/main.gd — update _on_game_event

func _on_game_event(payload: Dictionary) -> void:
    var event_type = payload.get("type", "")

    match event_type:
        "player_joined":
            _on_player_joined(payload)
        "move_made":
            _on_move_made(payload)
        "game_over":
            _on_game_over(payload)


func _on_move_made(payload: Dictionary) -> void:
    var game = payload.get("game", {})
    var current_turn = game.get("current_turn", "")

    if current_turn == player_id:
        $HUD/InfoLabel.text = "Your turn (%s)" % my_mark
    else:
        $HUD/InfoLabel.text = "Opponent's turn"
```

## 5. Client: Game History

Show move history:

```gdscript
# scripts/main.gd — add move history

var move_history: Array = []


func _on_move_made(payload: Dictionary) -> void:
    var player = payload.get("player_id", "")
    var position = payload.get("position", 0)
    var mark = payload.get("mark", "")

    move_history.append({
        "player": player,
        "position": position,
        "mark": mark,
    })

    _update_history_ui()


func _update_history_ui() -> void:
    var history_text = "Moves:\n"
    for move in move_history:
        var pos_name = ["TL", "TC", "TR", "ML", "MC", "MR", "BL", "BC", "BR"][move["position"]]
        history_text += "%s: %s at %s\n" % [move["mark"], move["player"], pos_name]
    $HUD/HistoryLabel.text = history_text
```

## 6. Test Multiplayer

1. Start server
2. Open two Godot instances
3. Both click "Quick Match"
4. Server matches them
5. Play!

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Quick match | Auto-find opponent |
| Private rooms | Room code for friends |
| Turn indicator | Show whose turn it is |
| Move history | Track game progress |

## Next

Now let's deploy as WebGL — [Web Deploy](tictactoe-web.md).
