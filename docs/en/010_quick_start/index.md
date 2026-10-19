---
title: Quick Start
---

This topic answers one question: after installing `SoulEngine` and `LOVE2D`, what do you do next.

The topic has two parts. The four **common base** pages cover what every path needs — read them and you can get something on screen. The **two paths** are independent of each other: pick one, finish it, and you get a runnable result. You do not need to do both.

---

## Pick an entry point by what you want to build

| What you want to build | Entry point |
|---|---|
| A turn-based battle you can actually play | [Your first battle](./040_first_battle.md) |
| A map you can walk around on | [Your first map](./050_first_map.md) |
| Interfaces, cutscenes, minigames | Read the common base below, then write your own scene |
| Not decided yet | Read the common base below, then come back here |

!!! note "The common base is not optional"
    Both paths require knowing how to create a scene and place a sprite. The difference between `conf.lua` and `Game/conf_pure.lua`, and the Game-area override rule, also belong to this layer.

---

## What the engine can do

The engine is split into modules by responsibility. The table below maps what you want to build to the module that owns it:

| What you want to build | Owned by | Read |
|---|---|---|
| Turn-based battles, bullets, enemy turns | Battle system | [Battle system](../030_battle_system/index.md) |
| Walking on a map, dialogue, save points, chests, encounters | Overworld | [Overworld system](../040_overworld/index.md) |
| Shop trading, refusal lines, talk topics | Overworld → Shop | [Shop](../040_overworld/060_shop.md) |
| Menu, status page, inventory | Overworld → Menu | [Menu · save · chests](../040_overworld/040_menu.md) |
| Custom interfaces, cutscenes, minigames | Scenes + sprites + typers + GUI | [Basic development](../020_basic/index.md) |
| Background music and sound effects | Audio | [Basic development → Audio](../020_basic/050_audio.md) |
| Switching languages | Localize | [Localization](../080_l10n/index.md) |
| Trophies, leaderboards, cloud saves | GameJolt | [Network → GameJolt](../090_network/000_gamejolt.md) |
| Packaging as exe / APK / web | Packager | [Export and release](../100_export/index.md) |

!!! tip "What the engine does not cover"
    Maps are edited in Tiled, and tileset and character art have to be drawn or sourced by you. The engine loads and runs that content; it does not ship an editor for making it.

---

## Common base

Four pages, read in order. Each one ends with how to verify it worked:

| Page | What you can do after it | How to verify |
|---|---|---|
| [Editing game info](./000_conf.md) | Change window title, author, first scene | The window title and the scene you land in both change |
| [Creating and switching scenes](./010_scene.md) | Make the engine open a scene you wrote | The console prints your text, or a sprite appears centre screen |
| [Creating sprites](./020_sprites.md) | Put an image on screen and change its properties | The image appears on screen |
| [Displaying text](./030_typers.md) | Print a line of text on screen | The text types out character by character |

---

## The two paths

### Path A: a battle you can play

- **Result**: an enemy appears on screen, and you can resolve one attack and survive one enemy turn.
- **Files to touch**: the encounter, the battle scene, and the first-scene setting — three places.
- **Start here**: [Your first battle](./040_first_battle.md)

### Path B: a map you can walk on

- **Result**: the character walks around the map, and stepping on a marker triggers dialogue.
- **Files to touch**: the Overworld scene and the first-scene setting — two places. The bundled map can be used as-is.
- **Start here**: [Your first map](./050_first_map.md)
- Building your own map requires Tiled, see [Overworld → Map and object layers](../040_overworld/010_map.md) .

---

## Once you have a result

[What to read next](./060_next.md)
