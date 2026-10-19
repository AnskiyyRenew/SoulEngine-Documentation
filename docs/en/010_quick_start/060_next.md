---
title: What to read next
---

After finishing either path, the project holds a runnable result. This page lists where to go next by what you want to build, and ends with a troubleshooting order for when something stops working.

---

## Battle

| What you want to build | Where |
|---|---|
| Add a second enemy, swap the animation | [Battle system → Battle Initialization](../030_battle_system/000_init.md) |
| Change the battle interface, buttons, status bar | [Battle system → UI](../030_battle_system/010_ui.md) |
| Resize the battle box, cut holes, masks | [Battle system → Battle Box](../030_battle_system/020_arena.md) |
| Swap soul modes, one-way platforms | [Battle system → Player and Soul](../030_battle_system/030_player.md) |
| Change the attack bar, damage formula, custom weapons | [Battle system → Attack Pattern](../030_battle_system/040_attack.md) |
| The full shape of an enemy turn | [Battle system → Turn Script](../030_battle_system/050_waves.md) |
| Bones, bone walls, homing blasters | [Battle system → Bullet Library](../030_battle_system/060_bullets.md) |
| Controlling battle flow, callback list | [Battle system → Battle Scene and Callbacks](../030_battle_system/070_scene.md) |

## Overworld

| What you want to build | Where |
|---|---|
| Scene skeleton, layers, save data | [Overworld → Initialization and Scene Skeleton](../040_overworld/000_init.md) |
| New maps, object layer properties, debugging | [Overworld → Maps and Object Layers](../040_overworld/010_map.md) |
| Tilesets, animated tiles | [Overworld → STI and Tilesets](../040_overworld/015_sti.md) |
| Player sprite, movement, facing | [Overworld → Character](../040_overworld/020_char.md) |
| Switching scenes, NPC dialogue | [Overworld → Interaction and Dialogue](../040_overworld/030_interact.md) |
| Menu, save points, chests | [Overworld → Menu · Save · Chest](../040_overworld/040_menu.md) |
| Random encounters leading into battle | [Overworld → Encounter](../040_overworld/050_encounter.md) |
| Shop trading, talk topics | [Overworld → Shop](../040_overworld/060_shop.md) |

## Presentation and assets

| What you want to build | Where |
|---|---|
| Every sprite property and animation | [Basic development → Sprites](../020_basic/020_sprites.md) |
| The full typer tag list and the other two typers | [Basic development → Typers](../020_basic/030_typers.md) |
| Layer order, adding and removing layers | [Basic development → Layers System](../020_basic/040_layers.md) |
| Background music and sound effects | [Basic development → Audio](../020_basic/050_audio.md) |
| Fades, movement, scaling | [Basic development → Tween](../020_basic/100_tween.md) |
| Masks, borders, canvas and screen | [Basic development → Mask](../020_basic/080_mask.md) / [Border](../020_basic/090_border.md) / [Canvas & Screen](../020_basic/070_screen.md) |
| Interface widgets for menus | [Basic development → GUI Library](../020_basic/160_gui.md) |
| Input, gamepads, key mapping | [Basic development → Input and Controller](../020_basic/150_controller.md) |
| Shaders, ShaderToy conversion | [Intermediate development → Shaders](../050_intermediate/020_shaders.md) / [ShaderToy Conversion Library](../050_intermediate/010_shadertoy.md) |
| What assets ship with the engine | [Developer tools → Bundled Assets](../070_develop/060_bundled_assets.md) |

## Systems and project

| What you want to build | Where |
|---|---|
| Game-area override rules, patching the engine with Hacks | [Basic development → Game Area and Asset Override](../020_basic/110_game_area.md) |
| Global variables, save variables | [Basic development → Global Variables](../020_basic/060_global.md) |
| Level curve, story flags, chest contents | [Basic development → Game Logic and World Rules](../020_basic/120_game_logics.md) |
| Language files and text lookup | [Localization](../080_l10n/index.md) |
| Trophies, leaderboards, cloud saves | [Networking → GameJolt API](../090_network/000_gamejolt.md) |
| Discord activity display | [Networking → Discord RPC](../090_network/010_discord.md) |
| Multiplayer | [Networking → sock networking](../090_network/020_sock.md) |
| Asset preloading, avoiding first-frame stutter | [Developer tools → Asset Preloading](../070_develop/040_preload.md) |

## Releasing

| What you want to build | Where |
|---|---|
| Packaging as exe / APK / web | [Export and release](../100_export/index.md) |
| The pre-release checklist | [Export and release](../100_export/index.md) |
| Hiding the GameJolt private key | [Developer tools → Native Secret Store](../070_develop/050_secrets.md) |

---

## Troubleshooting order

1. **Read the terminal first.** Missing files, failed module loads and missing sprites all print a line containing `[WARNING]` . The console is on by default on Windows.
2. **Press F5 to hot-reload.** This clears the module cache and re-enters the current scene, so you do not have to restart after a code change. Press F2 instead when what changed is `conf_pure.lua` .
3. **Press F6 to print environment info.** It reports the current scene name, sprite count and layer object count, which confirms whether a change actually took effect.
4. **Check the file is in the right place.** The Game area wins over the engine directory, and an error only appears when neither root has the file. See [Basic development → Game Area and Asset Override](../020_basic/110_game_area.md) .
5. **Check path casing.** Image paths are case-insensitive on Windows; once packaged for Android or Linux the image is not found.

!!! note "Hotkeys only work in development builds"
    `F5` and `F6` require `_RELEASED = false` and stop working once packaged. All hotkeys are listed in [Developer tools → Engine Hotkeys](../070_develop/030_hotkeys.md) .

!!! tip "Not sure what ships with the engine"
    [Developer tools → Bundled Assets](../070_develop/060_bundled_assets.md) lists the fonts, sounds and sprites actually referenced by the engine. Checking it before making assets avoids duplicating work.

---

## Back to the start

[Quick Start](./index.md)
