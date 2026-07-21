---
title: 'Tic-Tac-Toe: Server'
description: 'Server-side game logic — board state, turns, win detection.'
---

# Tic-Tac-Toe: Server Logic

The server owns the game state. Players send moves, server validates and updates.

## 1. Game Logic

Create `server/game.py`:

```python
"""Tic-Tac-Toe game logic — pure functions, no side effects."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Game:
    """A single tic-tac-toe game."""
    board: list[str] = field(default_factory=lambda: [""] * 9)
    players: dict[str, str] = field(default_factory=dict)  # player_id → "X" or "O"
    current_turn: str = ""
    winner: str | None = None
    is_draw: bool = False
    move_count: int = 0

    def join(self, player_id: str) -> str:
        """Add a player, return their mark (X or O)."""
        if len(self.players) >= 2:
            raise ValueError("Game is full")

        if not self.players:
            mark = "X"
            self.current_turn = player_id
        else:
            mark = "O"

        self.players[player_id] = mark
        return mark

    def make_move(self, player_id: str, position: int) -> dict:
        """Make a move. Returns success/error."""
        if self.winner or self.is_draw:
            return {"error": "game_over"}

        if player_id not in self.players:
            return {"error": "not_in_game"}

        if player_id != self.current_turn:
            return {"error": "not_your_turn"}

        if position < 0 or position > 8:
            return {"error": "invalid_position"}

        if self.board[position] != "":
            return {"error": "position_occupied"}

        # Place mark
        mark = self.players[player_id]
        self.board[position] = mark
        self.move_count += 1

        # Check for winner
        if self._check_winner(mark):
            self.winner = player_id
            return {"success": True, "winner": player_id, "mark": mark}

        # Check for draw
        if self.move_count == 9:
            self.is_draw = True
            return {"success": True, "draw": True}

        # Switch turn
        for pid, m in self.players.items():
            if pid != player_id:
                self.current_turn = pid
                break

        return {"success": True, "next_turn": self.current_turn}

    def _check_winner(self, mark: str) -> bool:
        """Check if a mark has won."""
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
            [0, 4, 8], [2, 4, 6],              # diags
        ]
        return any(
            all(self.board[i] == mark for i in line)
            for line in wins
        )

    def to_dict(self) -> dict:
        """Export game state."""
        return {
            "board": self.board,
            "players": self.players,
            "current_turn": self.current_turn,
            "winner": self.winner,
            "is_draw": self.is_draw,
        }
```

## 2. Server Entry Point

Create `server/main.py`:

```python
import asyncio
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from evoid import Intent, Level, subscribe, publish, register, register_processor
from evoid.core import Context
from evoid_godot import Topics, setup_game_subscriptions
from game import Game

# ── Game State ──────────────────────────────────────────────────────────

games = {}  # room_id → Game
connections = {}  # room_id → {player_id: websocket}

# ── Handlers ────────────────────────────────────────────────────────────

async def handle_player_join(ctx: Context) -> dict:
    """Join a game room."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")
    room_id = intent.metadata.get("room_id", "default")

    if room_id not in games:
        games[room_id] = Game()

    game = games[room_id]

    try:
        mark = game.join(player_id)
    except ValueError as e:
        return {"error": str(e)}

    # Track connection
    if room_id not in connections:
        connections[room_id] = {}
    connections[room_id][player_id] = ctx.intent.metadata.get("websocket")

    # Broadcast join
    await broadcast_to_room(room_id, {
        "type": "event",
        "event": "player_joined",
        "player_id": player_id,
        "mark": mark,
        "game": game.to_dict(),
    })

    return {"joined": True, "mark": mark, "game": game.to_dict()}


async def handle_make_move(ctx: Context) -> dict:
    """Make a move on the board."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")
    room_id = intent.metadata.get("room_id", "default")
    position = intent.metadata.get("position", -1)

    if room_id not in games:
        return {"error": "game_not_found"}

    game = games[room_id]
    result = game.make_move(player_id, position)

    if "error" in result:
        return result

    # Broadcast move to all players
    await broadcast_to_room(room_id, {
        "type": "event",
        "event": "move_made",
        "player_id": player_id,
        "position": position,
        "mark": game.players.get(player_id, ""),
        "game": game.to_dict(),
    })

    # If game over, broadcast result
    if result.get("winner"):
        await broadcast_to_room(room_id, {
            "type": "event",
            "event": "game_over",
            "winner": result["winner"],
            "game": game.to_dict(),
        })
    elif result.get("draw"):
        await broadcast_to_room(room_id, {
            "type": "event",
            "event": "game_over",
            "draw": True,
            "game": game.to_dict(),
        })

    return result


async def handle_leave_game(ctx: Context) -> dict:
    """Leave a game room."""
    intent = ctx.intent
    player_id = intent.metadata.get("player_id")
    room_id = intent.metadata.get("room_id", "default")

    if room_id in connections:
        connections[room_id].pop(player_id, None)
        if not connections[room_id]:
            del connections[room_id]

    if room_id in games:
        game = games[room_id]
        game.players.pop(player_id, None)
        if not game.players:
            del games[room_id]

    await broadcast_to_room(room_id, {
        "type": "event",
        "event": "player_left",
        "player_id": player_id,
    })

    return {"left": True}


# ── Broadcast ───────────────────────────────────────────────────────────

async def broadcast_to_room(room_id: str, message: dict):
    """Send message to all players in a room."""
    if room_id not in connections:
        return

    dead = set()
    for pid, ws in connections[room_id].items():
        if ws is None:
            continue
        try:
            await ws.send_json(message)
        except Exception:
            dead.add(pid)

    for pid in dead:
        connections[room_id].pop(pid, None)


# ── Register Intents ────────────────────────────────────────────────────

register(Intent(name="player_join", level=Level.STANDARD))
register(Intent(name="make_move", level=Level.STANDARD))
register(Intent(name="leave_game", level=Level.STANDARD))

register_processor("player_join", handle_player_join)
register_processor("make_move", handle_make_move)
register_processor("leave_game", handle_leave_game)

setup_game_subscriptions("tic-tac-toe")


# ── WebSocket ───────────────────────────────────────────────────────────

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

                # Store websocket
                if room_id not in connections:
                    connections[room_id] = {}
                connections[room_id][player_id] = websocket

                # Join game
                from evoid.core.runtime import execute
                intent = Intent(
                    name="player_join",
                    level=Level.STANDARD,
                    metadata={
                        "player_id": player_id,
                        "room_id": room_id,
                        "websocket": websocket,
                    },
                )
                await execute(intent)

            elif data.get("type") == "intent":
                data["metadata"]["player_id"] = player_id
                data["metadata"]["room_id"] = room_id
                data["metadata"]["websocket"] = websocket

                from evoid.core.runtime import execute
                intent = Intent(
                    name=data.get("name", ""),
                    level=Level(data.get("level", "standard")),
                    metadata=data.get("metadata", {}),
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
            if room_id in connections:
                connections[room_id].pop(player_id, None)
            if room_id in games:
                games[room_id].players.pop(player_id, None)
                if not games[room_id].players:
                    del games[room_id]


# ── App ─────────────────────────────────────────────────────────────────

app = Starlette(
    routes=[
        WebSocketRoute("/ws", ws_endpoint),
    ],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 3. Test the Logic

```python
# test_game.py
from game import Game

game = Game()

# Player 1 joins
mark1 = game.join("alice")
assert mark1 == "X"

# Player 2 joins
mark2 = game.join("bob")
assert mark2 == "O"

# Alice plays center
result = game.make_move("alice", 4)
assert result["success"]
assert game.board[4] == "X"

# Bob plays corner
result = game.make_move("bob", 0)
assert result["success"]
assert game.board[0] == "O"

# Alice plays top-right
result = game.make_move("alice", 2)
assert result["success"]

# Bob plays bottom-left
result = game.make_move("bob", 6)
assert result["success"]

# Alice plays bottom-right — WINS (diagonal)
result = game.make_move("alice", 8)
assert result["winner"] == "alice"
assert game.winner == "alice"

print("All tests passed!")
```

## 4. Run

```bash
cd server
python main.py
# Server running at ws://localhost:8000/ws
```

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `Game` dataclass | Pure game logic, no side effects |
| Server ownership | Server decides valid moves |
| Turn management | Server tracks whose turn it is |
| Win detection | Server checks for winner |
| Room system | Multiple games at once |

## Next

Now let's build the Godot client — [Client Setup](tictactoe-client.md).
