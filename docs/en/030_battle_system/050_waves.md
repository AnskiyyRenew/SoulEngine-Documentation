---
title: Turn Script
---

Everything that happens during the enemy's turn is written in the **Turn Script** (`Wave`): how bullets come out, when they come out, and when they finish after coming out.

Path: `Game/Waves/` (Game area, priority), `Scripts/Waves/` (engine default, fallback).<br>
The name resolution rules are in [Battle Initialization → Turn Script](./000_init.md).

---

## What Happens in a Turn

```
Player's turn ends (press for enemy turn)
  ↓
Battle.Defending()
  ├─ Soul returns to (320, 320)
  ├─ Main battle box activates and shrinks to 155x130
  └─ Battle.LoadWave(...) loads and executes your wave file (top-level code runs only this once)
  ↓
wave.Update(dt) called every frame
  ↓
You call EndWave() inside it
  ↓
Engine destroys wave.objects, clears the imported library cache
  ↓
State returns to ACTIONSELECT, battle box smoothly restores to 565x130
```

!!! tip "Top-Level Code Runs Only Once"
    The wave file is `require`d in — **top-level code executes only once when loaded**.<br>
    "Things to do every frame" must be written into `wave.Update`; "initialize once when entering the turn" goes in the top level.

![BA-05](../img/030_battle_system/ba_05_wave_running.png)

---

## File Skeleton

```lua
local wave = ImportFile("Battle.Waves")
local EndWave = wave.EndWave
local Arena = Battle.mainarena

-- Let the player move
Player.canMove = true
-- Switch to blue Soul
Player.SetSoul(6)

-- Bullet mask: follows the battle box
local mask = Masks.New("rectangle", 320, 320, 155, 130, 0, 0)

local time = 0
function wave.Update(dt)
    mask:Follow(Arena.black)

    -- TODO: spawn bullets, advance logic

    time = time + 1
    if (time == 300) then
        EndWave()
    end
end

return wave
```

The first line is fixed: `ImportFile("Battle.Waves")` gets the **table shared by all waves**, which the engine uses to wrap up.

---

## Wave Available Methods

!!! example "Wave Methods"
    - `EndWave()` End this turn. Destroys all objects in `wave.objects`, clears the library cache imported via `wave.Import`, and sets `ENDED` to `true`.
    - `Import(path)` Import an engine library; on error it only prints, doesn't crash.
        - `path` The library path, e.g. `"Attacks.Bones"`.
    - `objects` A table you stuff things into yourself. `EndWave` auto-destroys everything inside, saving you from writing cleanup by hand.
    - `Update(dt)` **Defined by you**, called by the engine every frame.
    - `ENDED` Whether this turn has ended (the engine reads it).

!!! example "Global Values Commonly Used in Waves"
    - `Battle.mainarena` The main battle box; change its shape here (see [Battle Box](./020_arena.md)).
    - `Battle.TIME_F` How many **frames** have passed since the battle started.
    - `Battle.TIME_R` How many **seconds** have passed since the battle started.
    - `Player.canMove` Whether the player can control the Soul; remember to set it back to `true` at the start.
    - `Player.SetSoul(id)` Switch Soul.
    - `Arenas` The battle box library. **This is a global** (mounted when the battle library loaded).
    - `Player` / `UI` Are also globals, directly usable.

!!! warning "The Bullet Library Is NOT a Global"
    `Bones`, `Blasters` are **not** mounted on the global; using them directly gets `nil`.<br>
    `Bones` is obtained via the wave's own `wave.Import("Attacks.Bones")`;<br>
    `Blasters` needs the **battle scene** itself to `ImportFile("Attacks.Blasters")` and mount it as a global (the engine's own `scene_battle_init.lua`, `scene_battle_template.lua` do exactly this), so it becomes visible in waves.

!!! danger "Remember to Restore What You Changed"
    `Player.canMove`, `Player.SetSoul`, battle box size, etc. are **not** automatically restored at the end of the turn.<br>
    If a wave switches the Soul to blue and the next wave doesn't switch it back, the player stays blue. Get into the habit of explicitly setting them once at the start of every wave.

---

## Spawning Bullets

The bullet library must be `Import`ed first, then you manually call its `Update` — **if the wave doesn't write `bones.Update(dt)`, the bones simply won't move**.

```lua
local wave = ImportFile("Battle.Waves")
local EndWave = wave.EndWave
local Arena = Battle.mainarena

local bones = wave.Import("Attacks.Bones")
local mask  = Masks.New("rectangle", 320, 320, 155, 130, 0, 0)

-- A bone falling from the top edge
local bone = bones.New2D("sans", 40, {320, 180}, 0, {0, 2})
bone:SetStencils({mask})
table.insert(wave.objects, bone)

function wave.Update(dt)
    mask:Follow(Arena.black)
    bones.Update(dt)

    if (Battle.TIME_R > 5) then
        EndWave()
    end
end

return wave
```

For the complete method list of bones and blasters, see [Bullet Library](./060_bullets.md).

---

## Making Your Own Bullets

You don't have to use the bullet library. Any sprite with `isBullet = true` gets included in the player's collision check:

```lua
local bullet = Sprites.CreateSprite("bullet.png", "Bullets")
bullet:Scale(2, 2)
bullet:MoveTo(320, 240)
bullet:SetStencils({mask})
bullet.isBullet = true
table.insert(wave.objects, bullet)
```

!!! warning "Don't Forget to Stuff It Into wave.objects"
    If you don't, `EndWave` won't destroy it, and it will stay on screen and still be visible in the next turn.

---

## Multi-Phase Waves

To split a turn into several phases of performance, using `time` as a state machine is the most direct approach:

??? example "Three-Phase Wave"
    ```lua
    local wave = ImportFile("Battle.Waves")
    local EndWave = wave.EndWave
    local Arena = Battle.mainarena
    local bones = wave.Import("Attacks.Bones")

    local time = 0

    -- Phase 1: bone rain
    local function phase1()
        local b = bones.New2D("sans", 40, {math.random(220, 420), 200}, 0, {0, 3})
        b:SetStencils({Arena.mask and {Arena.mask} or {}})
        table.insert(wave.objects, b)
    end

    function wave.Update(dt)
        bones.Update(dt)

        if (time < 120 and time % 20 == 0) then
            phase1()
        elseif (time == 180) then
            Arena:Resize(200, 130)       -- Phase 2: box widens
        elseif (time == 300) then
            Arena:RotateTo(15)           -- Phase 3: box rotates
        elseif (time == 480) then
            EndWave()
        end

        time = time + 1
    end

    return wave
    ```

---

## Cache and Hot Reload

The wave module may have cache in both locations; `Battle.ClearWaveModule` clears **both** at once:

!!! example "Cache Methods"
    - `Battle.ClearWaveModule(wave_name)` Clear a wave's module cache; leaves the current `Battle.wave` empty.
    - `Battle.waveModule` The full module name that actually loaded successfully last time, e.g. `Game.Waves.bones.wave1`, usable to confirm whether the Game-area override took effect.

The engine auto-clears once at the end of the turn, so during normal play you don't need to worry about it. Only when **you changed the wave file while debugging but it didn't take effect** do you need to handle it manually.
