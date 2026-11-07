# Protagonist design study — v2

**Status: design exploration only. Not approved for production and not integrated into gameplay.**

## Intent

Develop a memorable side-view silhouette for the swordsman without copying an existing character. The signature read is a wind-pulled vermilion signal scarf, swept asymmetric hair, a high-collar split coat, a compact utility harness, and a drawn katana.

## Construction

- Canvas: 160 × 192 px, transparent RGBA source.
- Facing: right; forward-leaning, ready stance.
- Silhouette: scarf and rear coat tails stream behind the body; the head, torso, legs and blade remain separate readable masses.
- Costume: layered blue-black coat over a fitted underlayer, asymmetrical shoulder reinforcement, belt hardware, small field pouch, reinforced trousers and grounded boots.
- Face: visible profile, focused eye, cheek and jaw planes.
- Weapon: single-edged steel blade, wrapped hilt and guard; the hands are intentionally kept near the grip as a two-handed ready pose.
- Palette: 30 used colors grouped into cool navy/blue values, muted skin, warm red accents, desaturated steel/cyan reflections and restrained brass hardware.

## Pixel-art checks completed

- Native canvas verified at 160 × 192 px.
- Transparent background verified; non-transparent artwork is bounded inside the canvas.
- All shapes and highlights are aligned to the pixel grid; no smoothing or antialiasing is used.
- Inspected at native size, 4× nearest-neighbour enlargement and 0.55× gameplay-scale reduction. The scarf, coat silhouette, boots and blade remain identifiable at reduced size.

## Open issues — do not treat as solved

1. The weapon grip and overlapping forearms need another anatomy pass before animation.
2. The face profile needs a closer expression/readability pass.
3. The leg overlap and coat tails need motion testing so they do not merge during locomotion.
4. This is one key-pose study, not an animation set. No breathing, run, attack, hit, parry, jump, fall or death frames are approved by this file.
5. Actual Godot camera-scale and Android runtime inspection is still outstanding.

## Acceptance rule

This study remains outside the runtime asset paths. It must not be copied into the player atlas or substituted for missing animation frames. Promote it only after the design review, pose corrections, and in-game visual inspection.
