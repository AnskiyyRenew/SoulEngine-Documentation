---
title: Game Logic and World Rules
---

`Game/Logics/` is the part **unique to your game**: what the world looks like at the start, how levels rise, what the story switches are called, what's inside chests. Changing this **does not require touching the engine**.

Paths: `Game/Logics/init.lua` (the world's initial state and rule tables), `Game/Logics/items.lua` (the item table).

> This page covers the "world rules" layer.<br>
> How each `DATA` field is used at runtime is documented in [Overworld → Initialization and Scene Skeleton](../040_overworld/000_init.md);<br>
> how the item table is used is in the `ITEMS` section of that same page;<br>
> the Game area override order is in [Game Area and Asset Override](./110_game_area.md).

---

## How It Is Loaded

```lua
-- Scripts/Libraries/Overworld/init.lua
DATA  = DATA or require("Game.Logics")
FLAG  = DATA.flags
CHEST = DATA.chests
```

!!! warning "This file has no engine fallback"
    The engine **hard-requires** `Game.Logics` — unlike sprites or waves, which "fall back to `Scripts/` if the Game area lacks it."<br>
    A missing `Game/Logics/init.lua` means the entire main world cannot start.

!!! tip "This table IS the save"
    The save page runs `Global.SetSaveVariable("Overworld", DATA)` — the **entire `DATA` is written to disk**.<br>
    So adding a field in Logics is equivalent to adding a field to the save.

`items.lua` is the exception — it goes Game-first: `Game.Logics.items` → `Scripts.Logics.items` (the engine copy does not exist in the current project, so in practice only the Game area copy exists).

---

## File Skeleton

```lua
local path = (...):match("(.-)[^%.]+$")
local logic = {}

Global.SetVariable("FUN", math.random(0, 100))   -- ① globals can be set at top level

logic = { ... }            -- ② the world's default state (player, position, inventory…)
logic.flags   = { ... }    -- ③ story switches
logic.chests  = { ... }    -- ④ what's in chests
logic.lv_data = { ... }    -- ⑤ world rules: level curve

-- Global.DeleteSaveVariable("Overworld")          -- ⑥ force a new save during debugging
if (Global.GetSaveVariable("Overworld")) then
    logic = Global.GetSaveVariable("Overworld")    -- ⑦ if a save exists, use that copy
end

return logic
```

- **①** You can set globals directly at the top level. `FUN` is the "fun value" from UNDERTALE, re-randomized each time a new save is started.
- **⑦** If a save exists, it entirely replaces the defaults — so **changes to Logics not taking effect** is caused by this; see the `DATA` section in [Overworld → Initialization and Scene Skeleton](../040_overworld/000_init.md). During debugging, comment out that line, or use **⑥** to delete the save outright.

---

## lv_data: The Growth Curve

This is the most typical "world rule" — max level, HP per level, and EXP per level are all in this one table.

| Field | Meaning |
|---|---|
| `lv` | Level |
| `hp` | **Max HP** at this level (directly overrides `maxhp`) |
| `at` | Attack → written into `DATA.player.atk` |
| `df` | Defense → written into `DATA.player.def` |
| `totalExp` | **Cumulative** EXP required to reach this level (not "how much for this level") |

??? example "The engine-bundled 20-level table"
    ```lua
    logic.lv_data = {
        { lv = 1,  hp = 20,  at = 10,  df = 10, totalExp = 0      },
        { lv = 2,  hp = 24,  at = 12,  df = 10, totalExp = 10     },
        { lv = 3,  hp = 28,  at = 14,  df = 10, totalExp = 30     },
        { lv = 4,  hp = 32,  at = 16,  df = 10, totalExp = 70     },
        { lv = 5,  hp = 36,  at = 18,  df = 11, totalExp = 120    },
        { lv = 6,  hp = 40,  at = 20,  df = 11, totalExp = 200    },
        { lv = 7,  hp = 44,  at = 22,  df = 11, totalExp = 300    },
        { lv = 8,  hp = 48,  at = 24,  df = 11, totalExp = 500    },
        { lv = 9,  hp = 52,  at = 26,  df = 12, totalExp = 800    },
        { lv = 10, hp = 56,  at = 28,  df = 12, totalExp = 1200   },
        { lv = 11, hp = 60,  at = 30,  df = 12, totalExp = 1700   },
        { lv = 12, hp = 64,  at = 32,  df = 12, totalExp = 2500   },
        { lv = 13, hp = 68,  at = 34,  df = 13, totalExp = 3500   },
        { lv = 14, hp = 72,  at = 36,  df = 13, totalExp = 5000   },
        { lv = 15, hp = 76,  at = 38,  df = 13, totalExp = 7000   },
        { lv = 16, hp = 80,  at = 40,  df = 13, totalExp = 10000  },
        { lv = 17, hp = 84,  at = 42,  df = 14, totalExp = 15000  },
        { lv = 18, hp = 88,  at = 44,  df = 14, totalExp = 25000  },
        { lv = 19, hp = 92,  at = 46,  df = 14, totalExp = 50000  },
        { lv = 20, hp = 99,  at = 48,  df = 14, totalExp = 99999  }
    }
    ```

### How Leveling Is Settled

When a battle ends, `Battle.SyncToOverworld()` in `Scripts/Libraries/Battle/init.lua` (called from `Battle.Clear()`) writes the results back into `DATA`:

```lua
DATA.player.exp = DATA.player.exp + (Battle.EXP or 0)
DATA.player.gold = DATA.player.gold + (Battle.GOLD or 0)
DATA.player.hp = math.max(0, math.min(DATA.player.maxhp, Player.hp))

while (DATA.lv_data[DATA.player.lv + 1] and
       DATA.player.exp >= DATA.lv_data[DATA.player.lv + 1].totalExp) do
    local old_max = DATA.player.maxhp
    DATA.player.lv = DATA.player.lv + 1

    local row = DATA.lv_data[DATA.player.lv]
    DATA.player.maxhp = row.hp
    DATA.player.atk = row.at
    DATA.player.def = row.df

    -- UNDERTALE rule: current HP rises by the same amount max HP rose
    DATA.player.hp = math.min(DATA.player.maxhp, DATA.player.hp + (DATA.player.maxhp - old_max))
end
```

!!! example "Settlement rule summary"
    - A single battle can **level up multiple times** (it's a `while`, not an `if`).
    - `maxhp` / `atk` / `def` are **overridden by the table**, not accumulated; whatever the table says is what you get.
    - The amount of max HP gained is **also added to current HP** (leveling heals).
    - `weapon` / `armor` / `gold` / `exp` are not governed by the level table.

!!! warning "`watk` / `edef` are currently display-only"
    `player.watk` (weapon attack) and `player.edef` (armor defense) only appear in the STAT menu display; the engine does **not** add them to `atk` / `def`.<br>
    To make equipment actually take effect, you must add it yourself at settlement or damage calculation.

---

### Want to Expand to LV 30? Just Add Rows

The cap is entirely determined by **table length** — the loop condition is `DATA.lv_data[lv + 1]` existing, so:

```lua
{ lv = 21, hp = 106, at = 50, df = 15, totalExp = 150000 },
{ lv = 22, hp = 113, at = 52, df = 15, totalExp = 220000 },
-- ... keep going up to 30
```

After adding them, no engine code needs to change — the menu, level-up settlement, and EXP display will all follow along.

!!! warning "Opening the STAT menu at max level crashes"
    `Overworld.CalcNextEXP()` is written like this:

    ```lua
    local next_total = DATA.lv_data[DATA.player.lv + 1].totalExp   -- no nil check
    ```

    At max level `lv_data[lv + 1]` is `nil`, and **indexing nil directly errors** — the symptom is that opening the STAT page after reaching max level crashes.<br>
    Two fixes: write **one extra row** in the level table (e.g. if max is 20, write up to 21, keeping `totalExp` at a large enough value), or add a nil check to `CalcNextEXP` yourself (return 0 or `"--"`).

!!! tip "Don't write the EXP threshold backwards"
    `totalExp` is **cumulative** EXP, not "how much this level needs." Level 20's `99999` means "a total of 99999 EXP accumulated to reach level 20," not "fight 99999 more."

---

## flags: World Switches

```lua
logic.flags = {
    test_killed = 0
}
```

The engine exposes it as the global `FLAG`, just use it directly:

```lua
FLAG["test_killed"] = 1
if (FLAG["test_killed"] == 1) then
    -- story branch
end
```

Since the entire `DATA` is saved, `flags` are naturally **story switches that persist in saves**, requiring no extra work.

## chests: What's in Chests

```lua
logic.chests = {
    chest = { "Spider" },   -- key name corresponds to the chest id
    chest1 = {}
}
```

This is also exposed as the global `CHEST`. On opening a chest, the list is fetched by id; remember to clear it afterward, or it can be opened repeatedly (see [Menu · Save · Chest](../040_overworld/040_menu.md)).

---

## Two Things to Consider When Adding Fields

!!! warning "Old saves lack new fields"
    Saves are stored as the **entire table**. After you add `sanity = 100` to `player`, that field is `nil` in previously saved games.<br>
    When reading, either provide a default (`DATA.player.sanity or 100`), or during development just delete the save and start fresh.

!!! warning "`getcell` is force-enabled by the engine"
    `player.getcell` is written as `false` in Logics, but `Scripts/Libraries/Overworld/stat.lua` has `DATA.player.getcell = true` at the top level which overrides it.<br>
    As a result the CELL (phone) menu is ON by default, and changing Logics has no effect.

---

## Why This Layer Exists Separately

Keeping "world rules" in one file has the benefit of **tuning values without touching the engine**:

| What you want to change | Where to change |
|---|---|
| Max level 20 or 30 | Add/remove rows in `lv_data` |
| HP / ATK / DEF per level | `hp` / `at` / `df` of `lv_data` |
| How fast leveling is | `totalExp` of `lv_data` |
| Name at start / items / spawn point | `player` and `room` / `marker` / `position` |
| Where story branches are recorded | `flags` |
| What chests give | `chests` |
| Which items exist | `items.lua` in the same directory |

In other words, worldview-level settings (is this a "world capped at level 20" or "level 30") are fully decided in `Game/Logics/`, with the engine completely untouched.
