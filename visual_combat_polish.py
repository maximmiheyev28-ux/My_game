#!/usr/bin/env python3
"""v1.5 combat presentation pass: animated enemy deaths and sharper katana impact."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def patch_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text(encoding="utf-8")
    if new in source:
        print(f"Already applied: {label}")
        return
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one patch anchor, found {count} in {path}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")
    print(f"Applied: {label}")

enemy = ROOT / "scripts/enemies/enemy.gd"
patch_once(
    enemy,
    '''func die() -> void:
    if not is_inside_tree():
        return
    Game.play_sfx("hit")
    var spark := Sprite2D.new()
    spark.texture = visual.texture
    spark.global_position = global_position + Vector2(0, -25)
    spark.modulate = Color(0.35, 0.86, 0.95, 0.58)
    get_parent().add_child(spark)
    var tween := spark.create_tween()
    tween.tween_property(spark, "scale", Vector2(1.45, 1.45), 0.18)
    tween.parallel().tween_property(spark, "modulate:a", 0.0, 0.18)
    tween.tween_callback(spark.queue_free)
    queue_free()
''',
    '''func die() -> void:
    if not is_inside_tree() or is_in_group("defeated"):
        return
    add_to_group("defeated")
    set_physics_process(false)
    set_process(false)
    collision_layer = 0
    collision_mask = 0
    velocity = Vector2.ZERO
    Game.play_sfx("hit")

    # A readable 0.24-second pixel disintegration replaces the instant pop.
    var burst := Node2D.new()
    burst.z_index = 24
    burst.global_position = global_position + Vector2(0.0, -27.0)
    get_parent().add_child(burst)
    var shard_colors := [Color(1.0,0.34,0.67), Color(0.42,0.88,1.0), Color(0.95,0.91,1.0)]
    for i in range(9):
        var shard := Polygon2D.new()
        var w := 2.0 + float(i % 3)
        var h := 3.0 + float((i * 2) % 4)
        shard.polygon = PackedVector2Array([Vector2(-w, -h), Vector2(w, -h * 0.35), Vector2(0.0, h)])
        shard.color = shard_colors[i % shard_colors.size()]
        shard.position = Vector2(float((i % 3) - 1) * 5.0, float(i / 3) * 3.0 - 4.0)
        burst.add_child(shard)
        var shard_tween := shard.create_tween()
        var direction := -1.0 if i % 2 == 0 else 1.0
        shard_tween.set_parallel(true)
        shard_tween.tween_property(shard, "position", shard.position + Vector2(direction * (12.0 + float(i % 4) * 4.0), -10.0 - float(i % 3) * 5.0), 0.24).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
        shard_tween.tween_property(shard, "rotation", direction * 1.8, 0.24)
        shard_tween.tween_property(shard, "modulate:a", 0.0, 0.24)
    var death_tween := create_tween()
    death_tween.set_parallel(true)
    death_tween.tween_property(visual, "scale", Vector2(1.18, 0.72), 0.10)
    death_tween.tween_property(visual, "modulate", Color(0.35,0.88,1.0,0.0), 0.22)
    death_tween.tween_property(visual, "rotation", 0.16 if direction == 1.0 else -0.16, 0.22)
    death_tween.chain().tween_callback(burst.queue_free)
    death_tween.tween_callback(queue_free)
''',
    "enemy defeat dissolve and shard burst",
)

slash = ROOT / "scripts/fx/slash_effect.gd"
patch_once(
    slash,
    '''    # Individual sparks travel tangentially from the slash arc.
    for i in range(13):
''',
    '''    # A crisp contact flash makes a successful katana strike readable at phone scale.
    var impact_alpha := clampf((1.0 - sweep) * 1.35, 0.0, 1.0)
    draw_circle(Vector2(43.0, -17.0), 5.0 + pulse * 2.0, Color(0.84,0.96,1.0,impact_alpha*0.72))
    draw_arc(Vector2(43.0,-17.0), 10.0 + pulse * 3.0, -0.9, 2.5, 16, Color(1.0,0.43,0.78,impact_alpha), 1.4, false)
    for ray in range(8):
        var angle := float(ray) * TAU / 8.0 + life * 0.8
        var start := Vector2(43.0,-17.0) + Vector2(cos(angle),sin(angle)) * 7.0
        var finish := Vector2(43.0,-17.0) + Vector2(cos(angle),sin(angle)) * (12.0 + pulse * 4.0)
        draw_line(start, finish, Color(0.76,0.94,1.0,impact_alpha*0.9), 1.0)

    # Individual sparks travel tangentially from the slash arc.
    for i in range(13):
''',
    "katana impact flash and radial sparks",
)
print("v1.5 combat presentation pass complete.")
