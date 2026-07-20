---
title: 'Shooter: Web Export'
description: 'Export the shooter as WebGL and host it on EVOID.'
---

# Shooter: Web Export

Export the shooter as a WebGL game and host it on the EVOID server.

## 1. Export Godot to HTML5

### Install Export Template

1. Godot → Editor → Manage Export Templates
2. Download "HTML5" template
3. Install

### Create Export Preset

1. Project → Export → Add → HTML5
2. Set:
   - **Export Path**: `builds/arena-shooter/`
   - **Variant**: Release
   - **Progressive Web App**: Enabled

### Export

1. Click "Export Project"
2. Check "Export Debug" for testing
3. Click "Export"

Output:
```
builds/arena-shooter/
├── index.html
├── index.js
├── index.wasm
├── game.pck
└── icon.png
```

## 2. Server: Host the Game

Update `server/main.py` to serve the game:

```python
from evoid_godot import GameHost, SplashConfig

# Create game host
host = GameHost()
host.register_build(
    "arena-shooter",
    "builds/arena-shooter/",
    title="Arena Shooter",
    splash=SplashConfig(
        bg_color="#0d1117",
        accent_color="#e94560",
        subtitle="Multiplayer Arena Shooter",
    ),
)

# Add to routes
from starlette.routing import Route, Mount

app = Starlette(
    routes=[
        # Game hosting
        Mount("/game", app=host.create_router()),

        # Game API
        Route("/health", health),
        Route("/state", game_state),
        WebSocketRoute("/ws", ws_endpoint),
    ],
)
```

## 3. Client: Auto-Connect in WebGL

Update the player script to auto-detect WebGL:

```gdscript
# scripts/player.gd — update _ready

func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)
    EvoidBus.subscribe(EvoidTopics.GAME_STATE_SYNC, _on_state_sync)

    # Auto-connect in WebGL builds
    if OS.has_feature("web"):
        # Same-origin WebSocket
        EvoidApp.connect_to_server()
```

## 4. Run

```bash
cd server
python main.py
```

Open `http://localhost:8000/game/arena-shooter/`

## 5. How It Works

```
User visits /game/arena-shooter/
    ↓
1. HTML splash loads instantly (<100ms)
2. Service Worker registers
3. engine.wasm streams in background
4. game.pck loads in chunks
5. Game starts — splash fades
6. WebSocket connects to /ws
7. Player joins game
```

## 6. Multi-Player in Browser

Open two browser tabs:
- Tab 1: `http://localhost:8000/game/arena-shooter/`
- Tab 2: `http://localhost:8000/game/arena-shooter/`

Both connect to the same server. See each other's movements and shots.

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Godot HTML5 export | Build WebGL game |
| `GameHost` | Serve game with instant loading |
| `SplashConfig` | Custom splash screen |
| Auto-connect | Detect WebGL, connect to same-origin |
| Service Worker | Cache game for instant repeat visits |

## Congratulations

You've built a complete multiplayer shooter with:
- Real-time movement sync
- Shot detection
- Health system
- Score tracking
- WebGL deployment
- Instant loading

## Next

Try the [Tic-Tac-Toe](tictactoe-overview.md) tutorial for a turn-based game.
