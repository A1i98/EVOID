---
title: 'Shooter: Client'
description: 'Godot client: player movement, shooting, enemy rendering, effects. Based on HuntSquare.'
---

# Shooter: Client Setup

The client handles input, renders the game, and sends intents to the server. Based on HuntSquare: every entity is a colored square.

## 1. Godot Project Setup

1. Open Godot 4.4+
2. Create project: `top-down-shooter`
3. Copy EVOID plugin: `cp -r evoid_godot addons/`
4. Enable: Project → Plugins → EVOID → Enable

### Assets

Copy from HuntSquare:
- `Assets/Square.png`: universal sprite (player, enemies, bullets)
- `Assets/Circle.png`: particle texture
- `Assets/Font.ttf`: HUD font

## 2. Player Script

Create `scripts/Player.gd`:

```gdscript
extends Sprite2D
## Player — WASD movement, mouse shooting, server sync.

var speed: int = 150
var velocity: Vector2 = Vector2()
var can_shoot: bool = true
var is_dead: bool = false

@export var bullet_scene: PackedScene = preload("res://scenes/Bullet.tscn")


func _ready() -> void:
    # Register with server
    EvoidApp.send_intent("player_join", {})


func _process(delta: float) -> void:
    if is_dead:
        return

    # WASD movement (HuntSquare input mapping)
    velocity.x = int(Input.is_action_pressed("kright")) - int(Input.is_action_pressed("kleft"))
    velocity.y = int(Input.is_action_pressed("kdown")) - int(Input.is_action_pressed("kup"))
    velocity = velocity.normalized()

    # Clamp to viewport (24px margin)
    global_position.x = clamp(global_position.x, 24, 616)
    global_position.y = clamp(global_position.y, 24, 336)
    global_position += speed * velocity * delta

    # Send position to server
    EvoidApp.send_intent("player_move", {
        "x": global_position.x, "y": global_position.y,
    })

    # Shooting
    if Input.is_action_pressed("click_left") and can_shoot:
        _shoot()


func _shoot() -> void:
    can_shoot = false
    $Reload_Speed.start()

    # Spawn local bullet (optimistic)
    var bullet = bullet_scene.instantiate()
    bullet.global_position = global_position
    get_tree().current_scene.add_child(bullet)

    # Tell server
    var direction = (get_global_mouse_position() - global_position).normalized()
    EvoidApp.send_intent("player_shot", {
        "origin": [global_position.x, global_position.y],
        "direction": [direction.x, direction.y],
    })


func _on_Reload_Speed_timeout() -> void:
    can_shoot = true


func _on_Hitbox_area_entered(area: Area2D) -> void:
    if area.is_in_group("Enemy") and not is_dead:
        is_dead = true
        visible = false
        EvoidApp.send_intent("player_hit", {})
        await get_tree().create_timer(1.0).timeout
        get_tree().reload_current_scene()
```

## 3. Enemy Script

Create `scripts/Enemy.gd`:

```gdscript
extends Sprite2D
## Enemy — moves toward player, takes damage, dies with effects.

var velocity: Vector2 = Vector2()
var stun: bool = false
var hp: int = 4
var speed: int = 80
var points: float = 1.0
var screen_shake: int = 120
var enemy_id: String = ""

@onready var current_color: Color = modulate
var blood_scene: PackedScene = preload("res://scenes/Blood.tscn")


func setup(data: Dictionary) -> void:
    enemy_id = data.get("enemy_id", "")
    hp = data.get("hp", 4)
    speed = data.get("speed", 80)
    points = data.get("points", 1.0)
    global_position = Vector2(data.get("x", 0), data.get("y", 0))

    # Color by type
    match data.get("type", "red"):
        "red":   modulate = Color(0.976, 0.075, 0.243)
        "teal":  modulate = Color(0.188, 0.541, 0.659)
        "purple": modulate = Color(0.710, 0.349, 1.0, 0.87)
    current_color = modulate


func _process(delta: float) -> void:
    if hp <= 0:
        _die()
        return

    # Move toward player (HuntSquare pattern)
    var player = get_tree().get_first_node_in_group("Player")
    if player and not stun:
        velocity = global_position.direction_to(player.global_position)
        global_position += velocity * speed * delta
    elif stun:
        velocity = velocity.lerp(Vector2.ZERO, 0.35)
        global_position += velocity * delta


func _die() -> void:
    # Screen shake
    var cam = get_viewport().get_camera_2d()
    if cam and cam.has_method("screen_shake"):
        cam.screen_shake(screen_shake, 0.2)

    # Blood particles (HuntSquare pattern)
    var blood = blood_scene.instantiate()
    blood.global_position = global_position
    blood.rotation = velocity.angle()
    blood.modulate = current_color.darkened(0.52)
    get_tree().current_scene.add_child(blood)

    queue_free()


func take_damage() -> void:
    if stun:
        return
    modulate = Color("#b796a5")
    velocity -= velocity * 6  # Knockback
    stun = true
    hp -= 1
    $Stun_timer.start()

    # Tell server
    EvoidApp.send_intent("enemy_hit", {"enemy_id": enemy_id})


func _on_Stun_timer_timeout() -> void:
    modulate = current_color
    stun = false
```

## 4. Bullet Script

Create `scripts/Bullet.gd`:

```gdscript
extends Sprite2D
## Bullet — flies toward mouse cursor, destroys on screen exit.

var velocity: Vector2 = Vector2(1, 0)
var speed: int = 250
var look_once: bool = true


func _process(delta: float) -> void:
    if look_once:
        look_at(get_global_mouse_position())
        look_once = false
    global_position += velocity.rotated(rotation) * speed * delta


func _on_VisibilityNotifier2D_screen_exited() -> void:
    queue_free()
```

## 5. World Script

Create `scripts/World.gd`:

```gdscript
extends Node2D
## World — listens for server events, spawns enemies.

var enemy_scene: PackedScene = preload("res://scenes/Enemy.tscn")
var enemies: Dictionary = {}  # enemy_id → node


func _ready() -> void:
    EvoidBus.subscribe("enemy_spawned", _on_enemy_spawned)
    EvoidBus.subscribe("enemy_killed", _on_enemy_killed)
    EvoidBus.subscribe("enemy_damaged", _on_enemy_damaged)
    EvoidBus.subscribe("player_killed", _on_player_killed)


func _on_enemy_spawned(data: Dictionary) -> void:
    var enemy = enemy_scene.instantiate()
    enemy.setup(data)
    add_child(enemy)
    enemies[data.get("enemy_id", "")] = enemy


func _on_enemy_killed(data: Dictionary) -> void:
    var enemy_id = data.get("enemy_id", "")
    if enemy_id in enemies:
        enemies[enemy_id].hp = 0  # Triggers _die() in next frame
        enemies.erase(enemy_id)


func _on_enemy_damaged(data: Dictionary) -> void:
    var enemy_id = data.get("enemy_id", "")
    if enemy_id in enemies:
        enemies[enemy_id].take_damage()


func _on_player_killed(data: Dictionary) -> void:
    if data.get("player_id") == "":
        # Local player died
        get_tree().reload_current_scene()
```

## 6. Camera Script

Create `scripts/WorldCam.gd`:

```gdscript
extends Camera2D
## Camera — screen shake and zoom (from HuntSquare).

var screen_shake_start: bool = false
var shake_intensity: float = 0.0


func _process(delta: float) -> void:
    zoom = zoom.lerp(Vector2(1, 1), 0.3)
    if screen_shake_start:
        global_position += Vector2(
            randf_range(-shake_intensity, shake_intensity),
            randf_range(-shake_intensity, shake_intensity)
        ) * delta
    else:
        global_position = global_position.lerp(Vector2(320, 180), 0.3)


func screen_shake(intensity: float, time: float) -> void:
    zoom = Vector2(1, 1) - Vector2(intensity * 0.0015, intensity * 0.0015)
    shake_intensity = intensity
    $Screen_shake_time.wait_time = time
    $Screen_shake_time.start()
    screen_shake_start = true


func _on_Screen_shake_time_timeout() -> void:
    screen_shake_start = false
```

## 7. Input Map

| Action | Keys |
|--------|------|
| `kleft` | A, Left |
| `kright` | D, Right |
| `kup` | W, Up |
| `kdown` | S, Down |
| `click_left` | Left Mouse |

## 8. Run

1. Start server: `cd server && python main.py`
2. Open Godot project
3. Press Play (F5)
4. WASD to move, left-click to shoot

## What You Learned

| Concept | What It Is |
|---------|-----------|
| `EvoidApp.send_intent()` | Send player actions to server |
| `EvoidBus.subscribe()` | Receive server events |
| `enemy.setup(data)` | Server-driven enemy creation |
| HuntSquare pattern | Colored squares, knockback, blood effects |
| Server-authoritative | Client renders, server decides |

## Next

Add multiplayer: [Multiplayer](shooter-multiplayer.md).
