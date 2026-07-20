---
title: 'Overview'
description: 'Build multiplayer games with Godot + EVOID. From shooter to tic-tac-toe.'
---

# Godot + EVOID Game Tutorials

Build real multiplayer games with Godot (client) and EVOID (server). Two complete projects, from scratch to deployment.

!!! info "Who is this for?"
    - Game developers who want multiplayer without writing server code from scratch
    - Web developers who want to embed games in their sites
    - Anyone who wants to see IOP in action beyond REST APIs

## What You'll Build

### Project 1: Arena Shooter

A Counter-Strike-style top-down shooter. Two players, real-time movement and shooting.

```
Player 1 (Godot) ←→ EVOID Server ←→ Player 2 (Godot)
```

**What you learn:**
- WebSocket real-time communication
- Player movement sync
- Shot detection and broadcasting
- Game state management
- Hosting Godot WebGL on EVOID

### Project 2: Online Tic-Tac-Toe

A browser-based tic-tac-toe. One player in Godot, one in browser (or both in Godot).

```
Player 1 (Godot/WebGL) ←→ EVOID Server ←→ Player 2 (Godot/WebGL)
```

**What you learn:**
- Turn-based game logic
- Server-side validation (no cheating)
- Room/matchmaking system
- Instant game loading (no download)
- Embedding games in websites

## Architecture

Both projects follow the same pattern:

```
┌─────────────────┐         ┌─────────────────┐
│  Godot Client   │ ←─────→ │  EVOID Server   │
│  (Player View)  │  WSS    │  (Game Logic)   │
└─────────────────┘         └─────────────────┘
        │                           │
        │   evoid_godot plugin      │   evoid-godot plugin
        │   (GDScript)              │   (Python)
        │                           │
        ├─ EvoidApp                 ├─ GameHost
        ├─ EvoidClient              ├─ game_intent_handler
        ├─ EvoidBus                 ├─ setup_game_subscriptions
        └─ EvoidConfig              └─ Topics
```

### The Two Plugins

| Plugin | Runs Where | What It Does |
|--------|-----------|--------------|
| **evoid_godot** (GDScript) | Godot client | WebSocket connection, state machine, event bus |
| **evoid-godot** (Python) | EVOID server | Intent handling, message bus, game hosting |

## Prerequisites

- Godot 4.x installed
- Python 3.12+ with `uv`
- Basic GDScript knowledge
- Basic Python knowledge

## Quick Setup

```bash
# 1. Install EVOID server plugins
uv add evoid evoid-godot

# 2. Clone the Godot plugin
git clone https://github.com/EvolveBeyond/evoid-godot.git

# 3. Copy to your Godot project
cp -r evolvebeyond-evoid-godot/evoid_godot your-game/addons/
```

## Project Structure

```
your-game/
├── addons/
│   └── evoid_godot/           # Godot plugin (client)
│       ├── core/
│       │   ├── app.gd         # State machine + orchestration
│       │   ├── client.gd      # WebSocket connection
│       │   ├── event_bus.gd   # Pub/sub messaging
│       │   ├── config.gd      # Configuration
│       │   └── topics.gd      # Topic constants
│       ├── plugin.cfg
│       └── plugin.gd
├── scenes/
│   ├── main.tscn              # Main game scene
│   ├── player.tscn            # Player prefab
│   └── lobby.tscn             # Matchmaking lobby
└── scripts/
    ├── main.gd                # Game controller
    ├── player.gd              # Player logic
    └── network.gd             # EVOID integration
```

## How It Works

### Client (Godot)

```gdscript
# 1. Connect to server
func _ready():
    EvoidApp.connect_to_server("wss://your-server.com", "my-game")

# 2. Send player actions
func _on_shot_pressed():
    EvoidApp.send_intent("player_shot", {
        "origin": global_position,
        "direction": aim_direction,
    })

# 3. Receive server events
func _ready():
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)

func _on_game_event(payload: Dictionary):
    match payload.get("type"):
        "player_moved": update_player(payload)
        "shot_fired": show_bullet(payload)
```

### Server (EVOID)

```python
# 1. Setup game
from evoid_godot import setup_game_subscriptions, setup_game_hosting
setup_game_subscriptions("my-game")

# 2. Handle game intents
from evoid import subscribe

async def on_shot(intent):
    # Validate shot (server-side anti-cheat)
    player_id = intent.metadata["player_id"]
    origin = intent.metadata["origin"]
    direction = intent.metadata["direction"]

    # Broadcast to all players
    await publish(Intent(
        name="game_event",
        metadata={"type": "shot_fired", "player_id": player_id}
    ))

subscribe("game:my-game:player_shot", on_shot)

# 3. Serve the game
host = setup_game_hosting("my-game", "builds/my-game/")
app = Starlette(routes=[Mount("/game", app=host.create_router())])
```

## Next

Start with the [Arena Shooter](shooter-overview.md) — it covers real-time movement and shooting.

Or skip to [Tic-Tac-Toe](tictactoe-overview.md) — it covers turn-based logic and instant loading.
