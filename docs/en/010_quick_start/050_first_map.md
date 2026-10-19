---
title: Your first map
---

This page is path B: getting a character walking on a map and triggering dialogue.

The map used here is the one bundled with the engine, so no assets need preparing first. Prerequisite: the four [common base](./index.md) pages.

---

## The Overworld is two pieces

| Piece | What it owns | What this page uses |
|---|---|---|
| Map file | Ground, walls, and the interaction objects placed on it | The bundled `Maps/main_scene/main_0.lua` |
| Overworld scene | Loads the map, plays music, advances each frame, handles interactions | `Game/Scenes/Overworld/myfirst.lua` |

Building your own map requires Tiled — see the end of this page.

---

## Step 1: the Overworld scene

Create `Game/Scenes/Overworld/myfirst.lua` with this content:

```lua
local scene = {}
local ow = ImportFile("Overworld")

ow.Init("Maps/main_scene/main_0.lua")
ow.SetMusic("Start.ogg")

function scene.update(dt)
    ow.Update(dt)
end

function scene.draw()
    ow.Draw()
end

function scene.clear()
    ow.Clear()
    Layers.clear()
end

return scene
```

What each part does:

| Code | Role |
|---|---|
| `ImportFile("Overworld")` | Loads the Overworld library and registers globals such as `Map` , `Char` and `DATA` |
| `ow.Init(path)` | Loads the map and clamps the camera to its actual covered area |
| `ow.SetMusic(path)` | Plays background music; a track already playing under the same name is not restarted |
| `ow.Update(dt)` and `ow.Draw()` | Advance and draw each frame |
| `ow.Clear()` and `Layers.clear()` | Destroy the map and clear layers when leaving the scene |

!!! danger "Neither line in `scene.clear` is optional"
    `ow.Clear()` destroys every collider and sprite of the map, releases the camera bounds, and clears the whole `Scripts.Libraries.Overworld` module cache.<br>
    Dropping it means the second visit to the Overworld inherits the previous run's state.

!!! warning "Game-area override for map paths"
    `Maps/main_scene/main_0.lua` is first looked up as `Game/Maps/main_scene/main_0.lua` , and that copy wins if it exists.<br>
    STI resolves tile images relative to the map file, so a Game-area copy must ship its own `../images/` tree beside it, otherwise the tiles are lost entirely.

---

## Step 2: make it the first scene

Add this line to `Game/conf_pure.lua` :

```lua
Global.SetVariable("FirstRoom", "Overworld.myfirst")
```

---

## How to verify

Press F5 to reload (or restart the game) and check each item:

| Check | Expected |
|---|---|
| Map renders | Ground and walls appear on screen |
| Character moves | Arrow keys move the character and the camera follows |
| Wall collision | Walking into a wall stops the character instead of passing through |
| Music | `Start.ogg` starts playing |

!!! warning "The map is black or the tiles are missing"
    Tile image paths are resolved relative to the map file. Copying a map file elsewhere without `Maps/images/` leaves every tile unresolvable.

!!! warning "The character does not move"
    Check that `scene.update` calls `ow.Update(dt)` and that `scene.draw` calls `ow.Draw()` .

---

## Adding a dialogue trigger

Overworld dialogue takes two steps: **touch, then confirm**. While the player stands on the object, `getInteractResult` returns `true` , and the dialogue only opens once the confirm key is pressed.

Add this to `scene.update` :

```lua
function scene.update(dt)
    ow.Update(dt)

    if (ow.getInteractResult("trigger", 1)) then
        if (Controller.GetState("confirm") == 1) then
            ow.dialogNew({"* This is a test map."})
        end
    end
end
```

- `getInteractResult("trigger", 1)` — the type name matches the object layer name (objects in the `triggers` layer have type `trigger` ), and the number matches the object's `id` property.
- `Controller.GetState("confirm") == 1` means the confirm key was pressed this frame, so holding it does not re-trigger.
- In the bundled `main_0` map, the trigger with `id` 1 sits at Tiled coordinates `(20, 100)` , which is roughly world coordinates `(40, 200)` .

!!! warning "Runtime coordinates are twice the Tiled coordinates"
    Map tiles are 20 × 20 and the map is drawn at 2× scale, so one tile occupies 40 × 40 in the world.<br>
    The engine already applies the conversion when generating colliders, so `obj.x` is a world coordinate; hard-coded numbers have to be doubled by hand.

!!! tip "Finding where an interaction object is"
    Set `Overworld.debug` to `true` and every object's collider is drawn, colour-coded by type. Pressing space teleports the camera to the world coordinates under the mouse.

---

## Building your own map

Beyond the bundled map, a new one has to be edited in Tiled and follow the engine's conventions for layers and properties:

| Step | Notes |
|---|---|
| Tileset | 20 × 20 tiles; the tileset must be embedded in the map |
| Collision layer | A `walls` layer; colliders are generated from it |
| Spawn point | A `marks` layer; the `id` decides which point you enter from |
| Interaction layers | `triggers` / `signs` / `warps` / `saves` / `chests` |
| Export | Save as `.lua` under `Maps/` , then pass it to `ow.Init` |

Full details are in [Overworld → Map and object layers](../040_overworld/010_map.md) and [Overworld → STI and tilesets](../040_overworld/015_sti.md) .

---

## Where to go on this path

| What you want next | Where |
|---|---|
| Switching scenes, NPC dialogue | [Overworld → Interaction and dialogue](../040_overworld/030_interact.md) |
| Player sprite, movement, facing | [Overworld → Character](../040_overworld/020_char.md) |
| Menu, save points, chests | [Overworld → Menu · save · chests](../040_overworld/040_menu.md) |
| Random encounters that start a battle | [Overworld → Encounters](../040_overworld/050_encounter.md) |
| Building a shop | [Overworld → Shop](../040_overworld/060_shop.md) |

For every destination, see [What to read next](./060_next.md) .
