#!/usr/bin/env python3
"""Give enemy attacks readable windups and clear parry windows."""
from pathlib import Path

ROOT = Path.cwd()
path = ROOT / "scripts" / "enemies" / "enemy.gd"
source = path.read_text(encoding="utf-8")

def replace_once(old: str, new: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one enemy-script anchor; found {count}: {old[:90]!r}")
    source = source.replace(old, new)

replace_once(
"""var _frames: Array[Texture2D] = []
""",
"""var _frames: Array[Texture2D] = []
var _attack_windup := 0.0
var _pending_attack := ""
var _pending_target := Vector2.ZERO
"""
)
replace_once(
"""    attack_cooldown = maxf(0.0, attack_cooldown - delta)
    patrol_clock += delta
    _frame_clock += delta
""",
"""    attack_cooldown = maxf(0.0, attack_cooldown - delta)
    patrol_clock += delta
    _frame_clock += delta

    if _attack_windup > 0.0:
        _attack_windup = maxf(0.0, _attack_windup - delta)
        velocity.x = move_toward(velocity.x, 0.0, 1700.0 * delta)
        if _attack_windup <= 0.0:
            if _pending_attack == "melee":
                _melee_attack()
            elif _pending_attack == "shoot":
                _shoot(_pending_target)
            _pending_attack = ""
            visual.modulate = Color.WHITE
        else:
            if not is_on_floor():
                velocity.y += GRAVITY * delta
            move_and_slide()
            _animate(delta)
            return
"""
)
replace_once(
"""                if absf(dx) < 420.0 and attack_cooldown <= 0.0:
                    _shoot(target_position)
                    attack_cooldown = 1.65
""",
"""                if absf(dx) < 420.0 and attack_cooldown <= 0.0:
                    _begin_attack("shoot", target_position, 0.46)
                    attack_cooldown = 1.65
"""
)
replace_once(
"""                if absf(dx) < 43.0 and absf(dy) < 58.0 and attack_cooldown <= 0.0:
                    _melee_attack()
                    attack_cooldown = 1.25 if enemy_kind != "aberration" else 0.9
""",
"""                if absf(dx) < 43.0 and absf(dy) < 58.0 and attack_cooldown <= 0.0:
                    var windup := 0.34 if enemy_kind != "aberration" else 0.24
                    _begin_attack("melee", target_position, windup)
                    attack_cooldown = 1.25 if enemy_kind != "aberration" else 0.9
"""
)
replace_once(
"""func _melee_attack() -> void:
""",
"""func _begin_attack(kind: String, target_position: Vector2, windup: float) -> void:
    _pending_attack = kind
    _pending_target = target_position
    _attack_windup = windup
    velocity.x = 0.0
    if kind == "shoot":
        var warning := Line2D.new()
        warning.points = PackedVector2Array([Vector2.ZERO, target_position - global_position])
        warning.width = 1.5
        warning.default_color = Color(1.0, 0.24, 0.34, 0.62)
        warning.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        warning.global_position = global_position + Vector2(0.0, -25.0)
        get_parent().add_child(warning)
        var warning_tween := warning.create_tween()
        warning_tween.tween_property(warning, "modulate:a", 0.0, windup)
        warning_tween.tween_callback(warning.queue_free)

func _melee_attack() -> void:
"""
)
replace_once(
"""    visual.position.y = -32.0 + sin(patrol_clock * 7.0) * (1.4 if absf(velocity.x) < 10.0 else 0.7)
    if not stasis_frozen:
        visual.modulate = Color.WHITE if enemy_kind != "hunter" else Color(0.92,0.84,1.0)
""",
"""    visual.position.y = -32.0 + sin(patrol_clock * 7.0) * (1.4 if absf(velocity.x) < 10.0 else 0.7)
    if _attack_windup > 0.0:
        var pulse := 0.72 + 0.28 * absf(sin(patrol_clock * 24.0))
        visual.modulate = Color(1.0, 0.36, 0.38, pulse)
        visual.scale = Vector2(1.06, 0.94)
        visual.rotation = sin(patrol_clock * 18.0) * 0.025
    else:
        visual.scale = Vector2.ONE
        visual.rotation = 0.0
        if not stasis_frozen:
            visual.modulate = Color.WHITE if enemy_kind != "hunter" else Color(0.92,0.84,1.0)
"""
)
path.write_text(source, encoding="utf-8")
print("Enemy attack telegraphs installed.")
