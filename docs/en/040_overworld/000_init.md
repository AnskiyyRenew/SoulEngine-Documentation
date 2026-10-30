---
title: Initialization and Scene Skeleton
---

An Overworld scene is very thin — it only does three things: load the Map, play music, and push `Overworld` every frame.

Path: `Scripts/Scenes/Overworld/`. The engine ships `scene_sol.lua` which you can copy directly.

Like other scenes, `Game/Scenes/Overworld/<same_name>.lua` will **override** the engine's version. See [Basic Development → Scenes](../020_basic/010_scene.md).

---

## Minimal Scene

```lua
local scene = {}
local ow = ImportFile("Overworld")

ow.Init("Maps/main_scene/sol.lua")
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

!!! danger "Both lines in `scene.clear` are required"
    What `ow.Clear()` actually does: `Map.Destroy()` destroys all collision bodies and sprites of the map → `Camera:unBounds()` unlocks the camera bounds → clears the module cache of the entire `Scripts.Libraries.Overworld` tree → `Camera:reset()`. <br>
    `Layers.clear()` clears the layers. Omitting the former will cause leftover state from the previous run when entering the Overworld a second time.

!!! note "`Overworld` is also one of the types overrideable in the Game area"
    `Overworld` belongs to the `Scripts.Libraries.Overworld` module tree, and the `Game/` area does **not** override it (the things that can be overridden are `Encounter` / `Animations` / `Waves` / `Souls` / `Sprites` / `Fonts`, etc.). <br>
    To change Overworld behavior, use a hack script under `Game/Hacks/`. See [Basic Development → Game Area and Asset Override](../020_basic/110_game_area.md).

!!! tip "`World.Destroy()` is currently never called"
    `World.Destroy()` does exist, but there is **no call site anywhere** in the library — `ow.Clear()` goes through `Map.Destroy()`, and the physics world itself is dropped together with the module cache. <br>
    When writing your own extensions, don't assume it has already been called.

![OW-01](../img/040_overworld/ow_01_overworld_scene.png)

---

## Layers

`Overworld` automatically creates the following layers when imported; the order is the draw/occlusion order:

| Layer | Value | What goes in it |
|---|---|---|
| `Background` | -100 | Background |
| `Map` | 0 | The map itself (drawn by the engine; do not manually put things in here) |
| `BelowPlayer` | 49 | Things behind the player that can block them (boxes, signs) |
| `Player` | 50 | Player |
| `UponPlayer` | 51 | Things in front of the player |
| `GUI` | 80 | Dialog boxes, menus, save page |
| `TOP` | 100 | Full-screen black overlay (scene transition fade) |
| `DEBUG` | 200 | Debug drawing |

Objects like boxes and signs that are "sometimes in front, sometimes behind" are automatically switched between `BelowPlayer` and `UponPlayer` by the engine **every frame** based on the player's position — you don't need to worry about it.

---

## Loading the Map

!!! example "Initialization methods"
    - `Overworld.Init(lua_file)` loads a map.
        - `lua_file` is the path of the map file relative to the project root, e.g. `"Maps/main_scene/sol.lua"`.
    - `Overworld.ResolveMapPath(lua_file)` returns the actual path that will be handed to STI (Game area takes priority). Usually no need to call manually.
    - `Overworld.AutoCameraBounds()` recomputes the camera bounds based on the map's actual coverage. `Init` already calls it once automatically.
    - `Overworld.SetMusic(mpath)` plays background music; an already-playing track of the same name will not be restarted.

Override rules for the map's Game area: `Maps/main_scene/sol.lua` first looks for `Game/Maps/main_scene/sol.lua`, and uses it if present.

!!! warning "When overriding a map, bring its tiles along"
    STI finds tiles by the **map file's relative path** (the `.lua` writes `../images/...`). <br>
    So the Game-area copy of the map must also have the corresponding `../images/` directory tree next to it, otherwise the tiles will be entirely missing.

---

## Global Variables

`Overworld` exports a batch of global variables when imported — use them directly when writing scene logic:

| Global | What it is |
|---|---|
| `Overworld` | Overworld master control table |
| `Map` | Map module (= `Overworld.map`) |
| `World` | Physics world (= `Map.world`) |
| `Char` | Player (= `Map.char`) |
| `Stat` | Menu |
| `Save` | Save page (= `Overworld._pages.save`) |
| `Chest` | Chest page (= `Overworld._pages.chest`) |
| `Step` | Encounter step counter |
| `DATA` | Save data (see below) |
| `FLAG` | = `DATA.flags` |
| `CHEST` | = `DATA.chests` |
| `ITEMS` | Item database |

There are also two global functions:

!!! example "Global functions"
    - `GetRelativePos(x, y)` converts "screen coordinates" into "world coordinates that follow the camera". Essential when making your own UI.
    - `SpawnBlock(x, y, width, height, thickness)` draws a white-bordered black-filled box and returns a block object with `Destroy()`.

---

## DATA: Save Data

`DATA` is the save itself. It comes from `Game/Logics/init.lua`; if a save exists, the saved copy is used directly.

Below are the engine's default values (the original contents of `Game/Logics/init.lua`):

```lua
logic = {
    time = 0,                  -- playtime (seconds)
    room_name = "--",          -- place name shown at the save point
    room = "Overworld",        -- current scene name
    marker = 2,                -- which mark to use when entering the next map
    position = {0, 0},         -- save position
    direction = "down",        -- save facing
    savedpos = false,          -- whether there is a "load position" pending consumption

    player = {
        name = "Chara", lv = 1,
        maxhp = 20, hp = 20,
        gold = 0, exp = 0,
        atk = 0, watk = 0, def = 0, edef = 0,
        weapon = "stick", armor = "bandage",
        items = {              -- inventory (stores item id strings)
            "ButterscotchPie",
            "PunchCard"
        },
        getcell = false,       -- whether the CELL menu is unlocked
        cells = {              -- phone contacts
            {id = "Toriel_1", name = "Call Mom"},
            -- ...
        }
    },
}
```

!!! tip "How the player's landing spot is determined (three-step override)"
    `Map.Init` writes the player's position three times in a row, **each later one overriding the earlier**:

    1. First place at the **first** mark (`map.objects.marks[1]`);
    2. Then use `Overworld.FindObject("mark", DATA.marker)` to find the mark whose `id` equals `DATA.marker`, and move there if found — **if not found, stay at the step-1 position**, without error;
    3. Finally, if `DATA.savedpos` is `true`, place directly at `DATA.position` (this is the path used when loading / returning from Battle).

    So `marker = 2` only matters if this map actually has a mark with `id = 2`.

!!! example "Other fields on DATA"
    - `flags` custom switch table, accessed via the global `FLAG`. Use like `FLAG["test_killed"] = 1`.
    - `chests` what is in the chests, accessed via the global `CHEST`, in the form `CHEST["chest"] = {"Spider"}`.
    - `lv_data` level table, 20 levels, each with `hp` / `at` / `df` / `totalExp`. **Both level-up settlement and menu display read from it**.

!!! tip "There is a dedicated page for `Game/Logics/`"
    World rules (how the level curve is set, how to expand past max level, story switches, chest contents) are all written in **[Game Logic and World Rules](../020_basic/120_game_logics.md)**. This page only covers how `DATA` is used at runtime.

!!! warning "`Game/Logics/init.lua` is a hard require, with no fallback"
    The source of `DATA` is hardcoded to `require("Game.Logics")` (`Scripts/Libraries/Overworld/init.lua` line 85). <br>
    The engine itself does not ship this file, so **deleting or renaming it will crash directly**. To reset the save, delete the save variable first, not the file.

!!! tip "Changed Logics but nothing took effect?"
    At the end of `Game/Logics/init.lua` there is a snippet: if `Global.GetSaveVariable("Overworld")` exists, the entire `logic` is replaced with the saved copy — your changed defaults will be completely skipped. <br>
    When debugging, comment out those two lines, or delete the save variable first.

---

## ITEMS: Item Database

The lookup order for the item table is `Game.Logics.items` → `Scripts.Logics.items` (the `owRequireGameFirst` in `Scripts/Libraries/Overworld/init.lua`).

!!! warning "The `Scripts/Logics/` fallback directory does not currently exist"
    The engine side **simply has no** `Scripts/Logics/items.lua`, so that entry in the list can never be hit — in fact the item table **only has `Game/Logics/items.lua` as a source**. <br>
    When both are missing, it prints `[Overworld] WARNING: items table not found under Game.Logics or Scripts.Logics.`, and then any use of `ITEMS.FindItemByID` will crash from indexing `nil`.

Item definitions are pure data tables, each with `id` / `name` / `_color`. Actions (`use` / `info` / `drop`) and phone calls are routed through two tables keyed by **id**, whose values are `function(id)` closures that usually call `Overworld.dialogNew`; `items.lua` also provides the `drop_item(id)` / `show_sprite(path)` helpers (the former removes an item from the inventory, the latter seizes control, draws a sprite, and clears it on cancel).

```lua
local db = {
    {id = "MonsterCandy", name = "Monster Candy"},
    {id = "Spider",       name = "Spider", _color = {0.5, 1, 0}},
    -- ...
}

-- Item action table (keyed by id); each action is a fn(id).
db._actions = {
    Spider = {
        use  = function(id) Overworld.dialogNew({"* You ate the Spider...", "* I CAN'T UNDERSTAND."}) end,
        info = function(id) Overworld.dialogNew("* A spider.") end,
        drop = function(id) drop_item(id); Overworld.dialogNew("* You dropped the Spider...") end,
    },
}

-- Cell action table (keyed by id); each value is fn(id).
db._cell_actions = {
    -- Toriel_1 = function(id) Overworld.dialogNew("* Ring ring...") end,
}
```

!!! example "ITEMS methods"
    - `ITEMS.FindItemByID(id)` gets the item definition by id, returning a table with `id` / `name` / `_color`.
    - `ITEMS.GetActionByID(id, action)` fetches the fn registered in `_actions` (legacy compat).
    - `ITEMS.DoItemAction(id, action)` third-level menu router: looks up the registered `use` / `info` / `drop` fn by id and runs it. **Unregistered id or action falls through to the default**, which assembles a generic line from the name (and removes the item on `drop`).
    - `ITEMS.DoCellAction(id)` cell router: looks up the fn registered in `_cell_actions` and runs it. **Unregistered falls through to the default** (`Overworld.dialogNew`).
    - `ITEMS.FindCellNameByID(id)` looks up a cell's display name by id (cell names live only in `DATA.player.cells`).
        - `action` is `"use"` / `"info"` / `"drop"`.

!!! tip "Default fallback"
    Items not registered in `_actions` do not error: `use` / `info` assemble a generic line from the name, and `drop` removes the item before notifying. Bulk one-off items need no per-id entry — register only those that need custom behaviour (e.g. showing a sprite).

The inventory only stores **id strings**; the name and color are looked up via `FindItemByID` at display time.

---

## Overworld Master Control Method Reference

!!! example "Overworld methods"
    - `Overworld.Init(lua_file)` loads the map.
    - `Overworld.Update(dt)` advances every frame (menu → map → save page → chest page → encounter counter).
    - `Overworld.Draw()` draws; currently an empty implementation, left for you to draw the HUD.
    - `Overworld.Clear()` destroys everything and clears the cache.
    - `Overworld.SetMusic(mpath)` plays music.
    - `Overworld.CalcNextEXP()` returns how much EXP is still needed for the next level.

!!! example "Overworld properties"
    - `Overworld.map` the map module.
    - `Overworld.stat` the menu module.
    - `Overworld.debug` whether debug drawing is enabled, default `false`.
    - `Overworld.follow_player` whether the camera auto-follows the player, default `true`.
    - `Overworld.ui_prefer` whether dialogs and the menu appear at the top or bottom by default, `"auto"` (default, derived from the player's position on screen) / `"down"` / `"up"`.
    - `Overworld.ui_threshold` the auto-detection line in canvas Y, default `320`.

---

## Debugging

Set `Overworld.debug` to `true`:

- All Tiled object collision bodies are drawn (colored by type).
- Pressing **Space** teleports the camera to the world coordinate under the mouse, for aligning coordinates.

See [Maps and Object Layers → Debug](./010_map.md).
