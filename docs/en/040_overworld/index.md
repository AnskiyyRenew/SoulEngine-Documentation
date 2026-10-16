---
title: Overworld
---

`Overworld` is "the part where you walk around on a map": maps, collision, movement, dialogue, save points, chests, encounters — all here.

Path: `Scripts/Libraries/Overworld/`.<br>
Scene path: `Scripts/Scenes/Overworld/`, with same-named files also accepting `Game/Scenes/Overworld/` override.

> These modules are likewise not standalone libraries that run on their own. `init.lua` handles overall assembly and scheduling; `map` / `char` / `world` / `stat` / `shop` / `Pages` each manage a piece, communicating with each other through `DATA` and the physics world's collision events.

> The `Game area` concept and resource lookup order that recur throughout this topic are explained in one place: **[Basic Development → Game Area & Resource Override](../020_basic/110_game_area.md)**.

---

## How an Overworld Runs

```
Enter Overworld scene
  ↓
Overworld.Init(map path)
  ├─ Build physics world, register collision callbacks
  ├─ Scan Tiled object layers → generate collision bodies and runtime objects
  ├─ Place player at spawn point (mark)
  └─ Auto-limit camera to the map's actual coverage
  ↓
Each frame Overworld.Update(dt)
  ├─ Menu / map / player / save page / chest page / encounter counting
  └─ Player hits warp / chest / sign / save / trigger → recorded into interactions
  ↓
You read interactions in the scene and decide what to do (dialogue, switch scene, open chest…)
```

---

## Pages in This Topic

| Page | Content |
|---|---|
| [Initialization & Scene Skeleton](./000_init.md) | How to write a scene, layers, global variables, DATA |
| [🔧 Map & Object Layers](./010_map.md) | Which layers to build in Tiled, each layer's properties, debugging |
| [🔧 STI & Tilesets](./015_sti.md) | Tilesets must be embedded in the map, 20 × 20 tiles, tileset image paths, animated tiles |
| [Characters](./020_char.md) | Player sprite, movement, collision body, Frisk Dance |
| [Interaction & Dialogue](./030_interact.md) | Collision interaction, dialogue, scene switching |
| [Menu · Save · Chest](./040_menu.md) | Menu, save points, chest page |
| [Encounters](./050_encounter.md) | Step-based encounters, connecting with the battle scene |
| [Shop](./060_shop.md) | Shop scene, buy/sell settlement, rejection lines, conversation topics & queue |

---

## A Few Things to Know First

!!! warning "Overworld coordinates are doubled"
    The map uses `20x20` tiles, drawn at an overall **2×** scale.<br>
    So **runtime coordinates = Tiled pixel coordinates × 2**: a `20x20` tile occupies `40x40` in the world.<br>
    The engine already multiplies for you when generating collision bodies, so reading `obj.x` gives you world coordinates; but **remember to multiply by 2 when hardcoding values yourself**.

!!! warning "The camera is limited to the map"
    `Overworld.Init` automatically scans all non-empty tiles in the map, computes the real coverage, and calls `Camera:setBounds`.<br>
    To control it yourself, call `Camera:setBounds` again after `Init` to override it.

!!! tip "The camera follows the player by default"
    `Overworld.follow_player` defaults to `true`. Set it to `false` and the camera stops moving; during cutscenes you can manually push the camera with `Camera:setPosition(x, y)`.
