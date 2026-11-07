# Visual production brief — The Last Signal

This document is the acceptance standard for replacing the temporary transparent placeholders. The placeholders are a clean-slate staging state, not finished game art.

## Global art direction
- Original high-detail HD pixel art with a restrained cyber-noir palette and deliberate color clustering.
- Every asset must read clearly at the actual in-game camera scale; no vector-like geometric placeholders, primitive silhouettes, procedural facade grids, or noisy detail sprayed over weak forms.
- Materials must be distinguishable through pixel texture, value grouping, edge treatment and lighting.
- Backgrounds, characters, props, effects and cinematics must share one coherent perspective, lighting logic and pixel scale.
- Keep the visual hierarchy legible: focal subjects first, supporting architecture second, decoration last.

## Hero and character artwork — mandatory
The protagonist and every enemy are individually authored character illustrations, not geometric constructions.

### Character design
- Define a readable silhouette and consistent anatomy, proportions, pose language and center of mass.
- Render face/head, hair, clothing layers, armor, weapons, straps, folds, seams and material transitions as intentional pixel-art forms.
- Use controlled palettes with highlights, midtones, shadows and selective emissive accents. Avoid flat fills and random single-pixel noise.
- Preserve identity, costume details, weapon dimensions and light direction across every frame and animation.
- Katana must be a distinct, correctly held object with coherent grip, blade orientation and attack arcs.

### Animation set
Create distinct, hand-authored poses/frames for idle (including subtle breathing), walk/run, start/stop, jump/fall/land, attack/combos, hit reaction, dodge, death and any story-specific actions. Enemies need their own locomotion, telegraphs, attacks, reactions and defeat animations. Do not meet frame counts by duplicating or mechanically shifting one pose.

### Sprite-sheet and integration requirements
- Use consistent per-character canvas dimensions, pivot/foot anchors and frame timing.
- Keep feet grounded and weapon/body motion physically coherent.
- Check sprite silhouettes against bright and dark backgrounds and at native gameplay zoom.
- Confirm animation transitions do not pop, jitter, stretch or change character proportions.
- Validate actual Godot scene playback, camera framing, collision alignment and Android performance.

## Environment and depth
- Build coherent architectural masses with identifiable landmarks and believable rooflines, windows, doors, cables, signage and street-level contact.
- Split only physically coherent depth planes. Objects attached to buildings must move with those buildings; ground props must remain attached to the world.
- Parallax must never detach roofs, signs, ledges, shadows or props from their supports.
- Use atmospheric perspective, selective lighting, rain, reflections and restrained animated details without flattening the scene.

## Cinematics and effects
- Cutscenes must be animated compositions using character poses, camera movement, lighting and environmental motion, not static dialogue boxes pretending to be cinematics.
- Combat effects must clarify timing, direction, contact and consequences without obscuring gameplay.

## Quality gates before an art set is accepted
1. Inspect every character and environment sheet at 100% and at actual game scale.
2. Verify unique, intentional animation poses and consistent character identity.
3. Run the game and inspect all chapters, character states, combat and cutscenes.
4. Check grounding, anchors, parallax and collision alignment while moving the camera.
5. Reject any asset that reads as primitive geometry, generic placeholder art, noisy procedural decoration or a disconnected floating layer.
6. Run Godot import/parse validation and an Android ARM64 build after integration.

A successful APK build is necessary but does not prove artistic quality. Visual acceptance requires in-game inspection.
