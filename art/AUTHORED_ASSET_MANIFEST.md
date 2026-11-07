# Authored pixel-art assets — first protagonist pass

This commit adds a fixed raster sprite atlas for the protagonist. The atlas is committed as a lossless WebP image with transparency; CI only slices its authored frames into the existing PNG resource paths. It does not draw or procedurally generate artwork.

## Protagonist atlas

- Source: `assets/authored/characters/protagonist_frames.webp`
- Canvas: 1248 × 112 px, 13 cells of 96 × 112 px.
- Frames: idle, two distinct run poses, three attack phases, jump, fall, hurt, parry, and three stasis-effect poses.
- Visual details: restrained cyber-noir palette, layered coat and lining, face and swept hair, belt hardware, boots, katana, selective cyan/red accents.
- Idle currently has one still frame; a dedicated breathing cycle is not yet authored.
- Run currently has two unique frames. Attack has three authored phases.

## Integration and validation

`reset_visual_assets.py` preserves the authored atlas, installs its fixed frames after the original source archive is restored, and updates player idle/run arrays to the actual frame counts. It does not overwrite files under `assets/authored/`.

Local checks completed: atlas dimensions and alpha channel inspected, extracted frame dimensions checked, reset script executed against the restored source snapshot, and `tools/validate_project.py` passed. Godot runtime playback and the Android build have not yet been verified for this art commit.

## Enemy atlas

- Source: `assets/authored/enemies/enemy_frames.webp`
- Canvas: 1152 × 112 px, 12 cells of 96 × 112 px.
- Four distinct archetypes: riot enforcer (`guard`), masked marksman (`shooter`), pale ronin (`hunter`), and bio-mechanical aberration (`aberration`).
- Each archetype has separate idle, locomotion and attack poses. CI slices the fixed frames into the filenames already loaded by `scripts/enemies/enemy.gd`. The player is scaled to 0.55 and enemies to 0.5 so the 112 px artwork aligns with the existing collision feet; stasis scaling preserves that baseline.

## Remaining scope

This is an initial protagonist pass, not completion of the game's art or final acceptance. Bosses, environments, props, combat effects, UI artwork and animated cinematics still require their own authored pixel-art work and in-game visual review.
