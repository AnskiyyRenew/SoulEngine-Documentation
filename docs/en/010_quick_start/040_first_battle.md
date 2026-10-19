---
title: Your first battle
---

This page is path A: building a playable battle from scratch. After finishing it, an enemy appears on screen and you can resolve one attack and sit through one enemy turn.

Prerequisite: the four [common base](./index.md) pages.

---

## A battle is three files

| File | What it owns | Where this page puts it |
|---|---|---|
| Encounter | Who the enemy is, its HP, the GOLD and EXP it drops | `Game/Encounter/myfirst.lua` |
| Wave | What happens during the enemy turn, and when it ends | `Game/Waves/myfirst.lua` |
| Battle scene | Wires the other two together, handles buttons and damage | `Game/Scenes/Battle/myfirst.lua` |

!!! note "Why everything goes in `Game/`"
    `Game/` is the content root for each game. Where a name exists in both places, the Game area wins, so upgrading the engine never overwrites your files. The full rule is in [Basic development → Game area and overrides](../020_basic/110_game_area.md) .

---

## Step 1: the encounter

Copy `Game/Encounter/_temp.lua` , rename it to `myfirst.lua` in the same directory, and replace its contents with this:

```lua
local encounter = {
    narration = "* The first battle begins.",
    can_flee = true,
    flee_percent = 0.75,
    enemy_id = 1,
    enemies = {
        {
            id = "MyFirst",
            name = "Training Dummy",
            animation = require("Game.Animations.Poseur"),

            maxdamage = 400,
            dmg_float = 2,

            show_hpbar = true,
            maxhp = 100,
            hp = 100,
            gold = 1,
            exp = 1,

            defensetext = "MISS",
            misstext = "MISS",

            canspare = true,
            killable = true,

            position = {320, 140},
            actions = {
                {id = "Check", name = "Check"},
            }
        },
    },

    state = "ACTIONSELECT",
    wave = "myfirst",

    player = {
        name = "Chara",
        lv = 1,
        maxhp = 20,
        hp = 20
    },

    items = {
        {id = "CHOCOLATE", _color = {0.4, 1, 1}, name = "Chocolate"},
    }
}

for i = 1, #encounter.enemies
do
    local e = encounter.enemies[i]
    e._id = encounter.enemy_id
    encounter.enemy_id = encounter.enemy_id + 1
end

return encounter
```

The fields that matter are these; leave the rest at their defaults:

| Field | Meaning |
|---|---|
| `narration` | The first line of narration above the battle box on entry |
| `enemies[].id` | Enemy identifier; ACT lines are looked up by it |
| `enemies[].name` | The name shown in the ACT menu |
| `enemies[].animation` | `require` an animation module, rooted at `Game/Animations/` |
| `enemies[].maxhp` / `hp` | Maximum HP and current HP |
| `enemies[].show_hpbar` | Whether the HP bar is drawn |
| `enemies[].maxdamage` | Damage cap for a single attack; a negative value heals instead |
| `enemies[].position` | Where the enemy sits on screen; the canvas is 640 × 480 |
| `enemies[].actions` | The actions offered in the ACT menu |
| `state` | State on entry; `ACTIONSELECT` means the player can act immediately |
| `wave` | Name of the wave file used for enemy turns, without extension |
| `player` | Player name, LV and HP |
| `items` | The in-battle inventory, read by the ITEM menu |

!!! warning "The file `animation` points at must exist"
    `require("Game.Animations.Poseur")` maps to `Game/Animations/Poseur.lua` . If it is missing the whole encounter fails to load.<br>
    The engine ships four you can reference directly: `Poseur` , `dummy` , `loox` and `sans` .

!!! tip "`player` is overridden when entering from the Overworld"
    A battle triggered by the Overworld reads save data first; the encounter's `player` table is only the template used when there is no save. See [Battle system → Battle initialization](../030_battle_system/000_init.md) .

---

## Step 2: the wave

Copy `Scripts/Waves/_template.lua` to `Game/Waves/myfirst.lua` . The template ships with `EndWave()` commented out, so the turn never ends — change it to this:

```lua
local wave = ImportFile("Battle.Waves")
local EndWave = wave.EndWave
local Arena = Battle.mainarena
Player.canMove = true

local mask = Masks.New("rectangle", 320, 320, 155, 130, 0, 0)

local time = 0
function wave.Update(dt)
    mask:Follow(Arena.black)

    time = time + 1
    if (time == 180) then
        EndWave()
    end
end

return wave
```

- `time` counts frames at 60 per second by default, so `180` is about 3 seconds.
- `EndWave()` ends the enemy turn and hands control back. **A turn that never calls it never ends.**

The wave is the entire content of an enemy turn; this page only builds an empty one. To put bullets in it, see [Battle system → Bullet library](../030_battle_system/060_bullets.md) .

---

## Step 3: the battle scene

Copy `Scripts/Scenes/Battle/scene_battle_template.lua` to `Game/Scenes/Battle/myfirst.lua` and change two lines near the top:

```lua
Battle = ImportFile("Battle")
Battle.SetEndRoom("scene_end")
Game = Battle.SetGame("myfirst")
Game:InitAnimation(1, {320, 140})
```

- `Battle.SetGame("myfirst")` takes the file name under `Game/Encounter/` , without `.lua` .
- `Game:InitAnimation(1, {320, 140})` builds the animation instance for enemy #1 and places it at `{320, 140}` .

!!! danger "Without `InitAnimation` the enemy never appears"
    Until it is initialized, `enemy.animation` is the animation **module**, not an instance. The engine only drives instances carrying the `_bound` marker each frame; a module is skipped outright, so no sprite is ever created.<br>
    The result: the battle starts, the UI and buttons all work, but no enemy is visible and nothing is printed to the terminal.

The three functions at the end of the scene stay as they are:

```lua
function scene.update(dt)
    Battle.Update(dt)
    Blasters.Update(dt)
end

function scene.clear()
    Layers.clear()
    Battle.Clear()
end
```

!!! warning "Neither line in `scene.clear` is optional"
    `Battle.Clear()` clears the battle library plus the module cache for this encounter, animation, wave and soul.<br>
    Dropping it means the second battle you enter inherits the previous one's state.

---

## Step 4: make it the first scene

Add this line to `Game/conf_pure.lua` :

```lua
Global.SetVariable("FirstRoom", "Battle.myfirst")
```

---

## How to verify

Press F5 to reload (or restart the game) and check each item:

| Check | Expected |
|---|---|
| Enemy visible | The enemy sprite appears in the upper area, at `{320, 140}` |
| Battle box | The box and the four buttons FIGHT / ACT / ITEM / MERCY appear at the bottom |
| Narration | The `narration` text shows above the battle box |
| Choosing FIGHT | The attack bar runs, and enemy HP drops after it resolves |
| Enemy turn | The wave runs for about 3 seconds, then returns control automatically |
| HP bar | The bar under the enemy tracks its HP |

!!! warning "No enemy on screen"
    Check that the scene calls `Game:InitAnimation` , and that the animation file under `Game/Animations/` exists.

!!! warning "Stuck in the enemy turn"
    Check whether `EndWave()` in the wave file is still commented out.

!!! warning "Terminal reports the encounter was not found"
    When the terminal prints `[Battle System] WARNING: encounter 'myfirst' not found` , compare `Game/Encounter/myfirst.lua` against the argument to `Battle.SetGame` . Both are written without an extension.

---

## Where to go on this path

| What you want next | Where |
|---|---|
| Add a second enemy, swap the animation | [Battle system → Battle initialization](../030_battle_system/000_init.md) |
| Put bones and bullets into enemy turns | [Battle system → Bullet library](../030_battle_system/060_bullets.md) |
| Change the attack bar and damage formula | [Battle system → Attack patterns](../030_battle_system/040_attack.md) |
| Use another soul mode (blue, orange, …) | [Battle system → Player and souls](../030_battle_system/030_player.md) |
| Trigger this battle from the Overworld | [Overworld → Encounters](../040_overworld/050_encounter.md) |

For every destination, see [What to read next](./060_next.md) .
