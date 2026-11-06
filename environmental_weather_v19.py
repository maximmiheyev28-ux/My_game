#!/usr/bin/env python3
"""v1.9: add pixel-snapped animated rain and drifting fog behind gameplay."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEVEL = ROOT / "scripts" / "levels" / "level.gd"
FX_DIR = ROOT / "scripts" / "fx"
WEATHER = FX_DIR / "weather_overlay.gd"
SHADER = FX_DIR / "weather_overlay.gdshader"

shader_source = """shader_type canvas_item;
render_mode unshaded;

uniform vec4 rain_tint : source_color = vec4(0.42, 0.78, 0.96, 1.0);
uniform float rain_opacity : hint_range(0.0, 0.35) = 0.16;
uniform float fog_opacity : hint_range(0.0, 0.12) = 0.035;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void fragment() {
    // Snap the weather pattern to a 480x270 virtual pixel grid.
    vec2 uv = floor(UV * vec2(480.0, 270.0)) / vec2(480.0, 270.0);
    float column = floor(uv.x * 180.0);
    float seed = hash21(vec2(column, 3.0));
    float speed = 1.8 + hash21(vec2(column, 1.0)) * 2.2;
    float phase = fract(uv.y * 7.0 + TIME * speed + hash21(vec2(column, 2.0)) * 4.0);
    float narrow = 1.0 - step(0.19, abs(fract(uv.x * 180.0) - 0.5));
    float rain = step(0.935, seed) * step(0.14, phase) * (1.0 - step(0.76, phase)) * narrow;

    // Slow low-contrast fog bands drift independently from the rain.
    float fog_wave = sin(uv.y * 10.0 + TIME * 0.19 + sin(uv.x * 5.0 + TIME * 0.11) * 0.7);
    float fog = smoothstep(0.15, 0.95, fog_wave * 0.5 + 0.5);
    float alpha = rain * rain_opacity + fog * fog_opacity;
    COLOR = vec4(rain_tint.rgb, alpha);
}
"""

weather_source = '''extends Node2D

const WEATHER_SHADER: Shader = preload("res://scripts/fx/weather_overlay.gdshader")

func _ready() -> void:
    var layer := CanvasLayer.new()
    layer.name = "WEATHER_CANVAS"
    layer.layer = -1
    add_child(layer)

    var overlay := ColorRect.new()
    overlay.name = "RAIN_AND_FOG"
    overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
    overlay.color = Color.WHITE
    overlay.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

    var material := ShaderMaterial.new()
    material.shader = WEATHER_SHADER
    overlay.material = material
    layer.add_child(overlay)
'''

FX_DIR.mkdir(parents=True, exist_ok=True)
if not WEATHER.exists() or WEATHER.read_text(encoding="utf-8") != weather_source:
    WEATHER.write_text(weather_source, encoding="utf-8")
if not SHADER.exists() or SHADER.read_text(encoding="utf-8") != shader_source:
    SHADER.write_text(shader_source, encoding="utf-8")

source = LEVEL.read_text(encoding="utf-8")
marker = '    weather_overlay.name = "WEATHER_OVERLAY"'
if marker not in source:
    anchor = '''    ambient_lights.call("setup", camera)
    add_child(ambient_lights)
'''
    addition = anchor + '''
    # Subtle pixel-snapped rain and slow fog add motion without covering gameplay.
    var weather_overlay := Node2D.new()
    weather_overlay.set_script(load("res://scripts/fx/weather_overlay.gd"))
    weather_overlay.name = "WEATHER_OVERLAY"
    add_child(weather_overlay)
'''
    if source.count(anchor) != 1:
        raise SystemExit(f"v1.9 level insertion anchor mismatch: {source.count(anchor)}")
    source = source.replace(anchor, addition, 1)
    LEVEL.write_text(source, encoding="utf-8")

final_source = LEVEL.read_text(encoding="utf-8")
assert marker in final_source, "Weather overlay was not installed in level.gd"
assert "preload(\"res://scripts/fx/weather_overlay.gdshader\")" in weather_source
assert "TIME * speed" in shader_source
assert "shader_type canvas_item;" in shader_source and "COLOR = vec4" in shader_source
assert "layer.layer = -1" in weather_source, "Weather must render behind gameplay sprites"
assert '"""' not in weather_source, "GDScript must not contain a multiline shader string"
print("v1.9: installed separate pixel-snapped rain/fog shader and GDScript overlay.")
