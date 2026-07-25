---
title: 'Shooter: Web Export'
description: 'Export as WebGL, host on EVOID server, instant loading with Service Worker.'
---

# Shooter: Web Export

Export the shooter as WebGL and host it on the EVOID server.

## 1. Export Godot to HTML5

1. Godot → Editor → Manage Export Templates → download HTML5
2. Project → Export → Add → HTML5
3. Set Export Path: `builds/top-down-shooter/`
4. Enable Progressive Web App
5. Click Export

Output:
```
builds/top-down-shooter/
├── index.html
├── index.js
├── index.wasm
├── game.pck
└── icon.png
```

The `EvoidExportPlugin` auto-injects Service Worker registration into `index.html`.

## 2. Server: Host the Game

The server already hosts the game (from the server tutorial):

```python
from evoid_godot import GameHost, SplashConfig

host = GameHost()
host.register_build(
    "top-down-shooter",
    "builds/top-down-shooter/",
    title="Top-Down Shooter",
    splash=SplashConfig(
        bg_color="#0d1117",
        accent_color="#e94560",
        subtitle="Top-Down Shooter",
    ),
)
```

## 3. Client: Auto-Connect

Update `Player.gd` to auto-detect WebGL:

```gdscript
func _ready() -> void:
    EvoidApp.auto_connect()  # Detects WebGL, connects to same-origin
    EvoidApp.send_intent("player_join", {})
```

`auto_connect()` does three things:
1. Checks `OS.has_feature("web")` — desktop falls back to `connect_to_server()`
2. Resolves WebSocket URL from `window.location` (same-origin)
3. Connects with configured game_id

## 4. Run

```bash
cd server && python main.py
```

Open `http://localhost:8000/game/top-down-shooter/`

## 5. How Loading Works

```
User visits /game/top-down-shooter/
    ↓
1. HTML splash loads (<100ms)
    ↓
2. Service Worker registers (auto-injected)
    ↓
3. engine.wasm streams (~5-10MB)
    ↓
4. game.pck loads in chunks (256KB each)
    ↓
5. Game starts
    ↓
6. WebSocket connects → player joins
```

| Visit | Time |
|-------|------|
| First | ~8-10s |
| Repeat (cached) | <1s |

## 6. Test Multiplayer in Browser

Open two tabs:
- Tab 1: `http://localhost:8000/game/top-down-shooter/`
- Tab 2: `http://localhost:8000/game/top-down-shooter/`

Both join the same room. See each other's movements and shots.

## 7. Binary Intents (Optional)

For bandwidth optimization:

```gdscript
# Instead of JSON:
EvoidApp.send_intent("player_shot", {"origin": pos, "direction": dir})

# Use binary (~60% smaller):
EvoidClient.send_intent_binary("player_shot", {"origin": pos, "direction": dir})
```

Server handles both formats. Binary is optional.

## What You Learned

| Concept | What It Is |
|---------|-----------|
| Godot HTML5 export | Build WebGL game |
| `EvoidExportPlugin` | Auto Service Worker injection |
| `GameHost` | Serve game with splash screen |
| `auto_connect()` | Detect WebGL, connect same-origin |
| Service Worker | Cache for instant repeat visits |
| Binary intents | Bandwidth optimization |

## Congratulations

You've built a complete survival shooter with:
- Server-authoritative game state
- 3 enemy types with different stats
- Progressive difficulty scaling
- Room-based multiplayer
- WebGL deployment with instant loading
- IOP Intents for every game action

## Next

Try [Tic-Tac-Toe](tictactoe-overview.md) for a turn-based game with embed support.
