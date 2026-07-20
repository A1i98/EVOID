---
title: 'Tic-Tac-Toe: Web Deploy'
description: 'Deploy as WebGL with instant loading. Embed in any website.'
---

# Tic-Tac-Toe: Web Deploy

Export as WebGL and host on EVOID with instant loading.

## 1. Export to HTML5

1. Project → Export → Add → HTML5
2. Set export path: `builds/tic-tac-toe/`
3. Enable Progressive Web App
4. Export

## 2. Server: Host the Game

```python
# server/main.py — add hosting

from evoid_godot import GameHost, SplashConfig

host = GameHost()
host.register_build(
    "tic-tac-toe",
    "builds/tic-tac-toe/",
    title="Tic-Tac-Toe",
    splash=SplashConfig(
        bg_color="#1a1a2e",
        accent_color="#e94560",
        subtitle="Online Multiplayer",
    ),
)

from starlette.routing import Mount

app = Starlette(
    routes=[
        Mount("/game", app=host.create_router()),
        WebSocketRoute("/ws", ws_endpoint),
    ],
)
```

## 3. Client: Auto-Connect

Update `scripts/main.gd`:

```gdscript
func _ready() -> void:
    EvoidBus.subscribe(EvoidTopics.NET_AVAILABLE, _on_connected)
    EvoidBus.subscribe(EvoidTopics.GAME_EVENT, _on_game_event)

    # Auto-connect in WebGL
    if OS.has_feature("web"):
        EvoidApp.connect_to_server()
    else:
        EvoidApp.connect_to_server(server_url)
```

## 4. Embed in a Website

The game runs at `/game/tic-tac-toe/`. Embed it in any HTML page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Play Tic-Tac-Toe</title>
    <style>
        .game-container {
            width: 400px;
            height: 600px;
            border: 2px solid #333;
            border-radius: 8px;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <h1>Play Tic-Tac-Toe Online</h1>
    <div class="game-container">
        <iframe
            src="/game/tic-tac-toe/"
            width="400"
            height="600"
            frameborder="0"
        ></iframe>
    </div>
    <p>Share this link with a friend to play together!</p>
</body>
</html>
```

## 5. Share Link

Share the game URL:
```
https://your-server.com/game/tic-tac-toe/
```

Both players open the link, enter the same room, and play.

## 6. How It Works

```
Player 1 opens link
    ↓
HTML splash loads (<100ms)
    ↓
Service Worker caches game
    ↓
engine.wasm + game.pck stream in
    ↓
Game starts
    ↓
WebSocket connects to /ws
    ↓
Player joins room
    ↓
Waiting for opponent...
    ↓
Player 2 opens same link
    ↓
Joins same room
    ↓
Game starts!
```

## 7. Custom Domain

For production, use a custom domain:

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name games.yourdomain.com;

    location /game/ {
        proxy_pass http://localhost:8000/game/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| HTML5 export | Build WebGL game |
| `GameHost` | Serve with instant loading |
| Embed | iframe in any website |
| Share link | Direct URL to game |
| Custom domain | Production deployment |

## Congratulations

You've built a complete online tic-tac-toe with:
- Turn-based gameplay
- Server-side validation (no cheating)
- Room system
- Win/draw detection
- WebGL deployment
- Instant loading
- Embeddable in any website

## Summary: What You Built

| Project | What It Teaches |
|---------|----------------|
| **Arena Shooter** | Real-time sync, movement, shooting, health |
| **Tic-Tac-Toe** | Turn-based, validation, rooms, win detection |

Both use the same EVOID plugins:
- **evoid_godot** (GDScript) — client connection
- **evoid-godot** (Python) — server logic + hosting

## Next

- Try building your own game with these patterns
- Check the [Plugin Collection](../learn/plugin-collection.md) for more tools
- Read the [Security](../learn/security.md) docs for production deployment
