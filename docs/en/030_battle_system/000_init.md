---
title: Battle Initialization
---

---

## Battle Scene

The contents of the battle scene changed within the past week: instead of certain scenes having their own layers, they are now placed under `init.lua` by default.

Below is the code that initializes all layers. This is not mandatory — you may adjust the layers as you see fit:

```lua
Layers.new_layer("BOTTOM", -1000)
Layers.new_layer("Background", -10)
Layers.new_layer("UI", 0)
Layers.new_layer("ArenasExtraW", 10)
Layers.new_layer("ArenasExtraB", 10.01)
Layers.new_layer("UponArena", 11)
Layers.new_layer("BelowPlayer", 12)
Layers.new_layer("Player", 13)
Layers.new_layer("BelowBullets", 25)
Layers.new_layer("Bullets", 30)
Layers.new_layer("ArenasCoverW", 50)
Layers.new_layer("ArenasCoverB", 50.01)
Layers.new_layer("TopAll", 60)
Layers.new_layer("TOP", 1000)
```



---

## Encounter File

Note: This file involves a lot of localization. See the **[Localization](../080_l10n/index.md)** topic for details.

Strictly speaking, calling this part an `Encounter` would be more accurate.<br>
**The main purpose of this file is to initialize the battle scene first, turning the standardized battle scene into a customized version.**

It is responsible for defining: player data (when entering battle), enemy data (count, HP, actions, etc.), the item inventory, and some other miscellaneous things.<br>
Below is a standard template; it is collapsed by default because it is very long:

??? tip "Standard Game Template"

    ```lua
    local encounter = {
        narration = Localize.localizeText("Battle.Narration.Default"),
        can_flee = true,
        flee_percent = 0.75,
        enemy_id = 1,
        enemies = {
            {
                id = "Poseur",
                name = Localize.localizeText("Battle.EnemiesName.Poseur"),
                animation = require("Game.Animations.Poseur"),

                maxdamage = 400,
                dmg_float = 2,  -- Some random stuff......I hate them

                show_hpbar = true, -- Sans... stop hiding your hp bar.
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
                    {id = "Check", name = Localize.localizeText("Battle.Actions.Names.Check")},
                    {id = "Pose",  name = Localize.localizeText("Battle.Actions.Names.Pose")},
                }
            },
        },

        state = "DEFENDING",
        wave = "bones.wave1",

        player = {
            name = "end",
            lv = 20,
            maxhp = 99,
            hp = 99
        },

        items = {
            {id = "CHOCOLATE", _color = {0.4, 1, 1}, name = "Chocolate"},
            {id = "END", _color = {0.4, 0, 1}, name = "END", _cantdestroy = true},
        }
    }

    -- Assign internal _id to each statically-defined enemy
    for i = 1, #encounter.enemies
    do
        local e = encounter.enemies[i]
        e._id = encounter.enemy_id
        encounter.enemy_id = encounter.enemy_id + 1
    end

    -- The following methods are now provided by Battle.game_apis via metatable:
    --   encounter:AddEnemy(data)  — adds a validated enemy with auto-assigned _id
    --   encounter:AddItem(item)    — adds a validated item
    --   encounter:ForceAttack(id)   — makes the enemy whose string `id` matches
    --                                 enter one attack cycle (Battle.attack.Restart)

    return encounter
    ```

The game body is defined through an `encounter` table. Below are the properties and methods that the `encounter` table provides:

!!! example "Encounter Table Properties"
    - `narration` The narration text printed in the battle box during the player's turn. Here it uses `Localize` to fetch the text, but you can write Chinese or English directly — both display fine.
    - `can_flee` Whether to show the `Flee` option in the `Mercy` button. Can be disabled in some boss fights.
    - `flee_percent` The flee probability. Has no effect if `can_flee` is off.
    - `enemy_id` Incremented when a new enemy is added, used to give each enemy a new unique id.
    - `state` The state when first entering battle. This is explained later; it is recommended to pick `ACTIONSELECT` (player turn) or `DEFENDING` (go straight to the enemy turn, i.e. an opening kill).
    - `wave` The turn script when first entering battle, can be used together with the `DEFENDING` state. See the `Turn Script` section below for load order.
    - `enemies` The enemy table, storing the data for all enemies.
        - `id` The detection id used internally. Usually English; any string works as long as there is no conflict, since this part is not translated.
        - `name` **This is the name that actually gets displayed** and will be localized.
        - `animation` Which animation this enemy uses.
        - `maxdamage` The maximum damage that can be dealt to the enemy. If later integrated with `Overworld`, the max damage can be computed by a formula.
        - `dmg_float` The dealt damage gets a random `+ 0 ~ dmg_float` added on top of the current damage. Default is `2`.
        - `show_hpbar` Whether to show the HP bar. In the original UNDERTALE there is one monster with a special case: `Sans` does not show an HP bar even while attacking.
        - `maxhp` The enemy's maximum HP.
        - `hp` The enemy's current HP.
        - `gold` The gold the enemy carries, obtained after killing or sparing it.
        - `exp` The experience the enemy carries, obtained only after killing it.
        - `defensetext` The text shown when you hit the enemy but deal no damage.
        - `misstext` The text shown when you miss the input window and fail to hit the enemy.
        - `canspare` Whether the enemy can be spared (will automatically turn yellow-named).
        - `killable` Whether the enemy can be killed. If `false`, the enemy will not die even when its HP bar is empty — useful for extra execution animations.
        - `position` Where the enemy stands. This is not the enemy's own animation, but rather the coordinate used for the hit reaction animation, i.e. where the player will slash toward.
        - `actions` The action table, describing what behaviors can be performed on the enemy.
            - `id` The action id, also not localized.
            - `name` The action's name, also what is actually displayed on screen.
    - `player` Player data.
        - `name` The player's name.
        - `lv` The player's level.
        - `maxhp` The player's maximum HP.
        - `hp` The player's current HP.
    - `items` The inventory.
        - `id` Each item's detection id, not localized.
        - `name` Each item's actually displayed name.
        - `_cantdestroy` (optional) If `true`, the item is not consumed when used.

Besides the properties above, the `encounter` table also has a batch of methods mounted via a metatable (from `Scripts/Libraries/Battle/game_apis.lua`), which you can call directly using colon syntax:

!!! example "Encounter Table Methods"
    - `AddEnemy(data)` Adds an enemy. Auto-fills missing fields and assigns a unique `_id`, returning the completed enemy table.
        - `data` The enemy data table, with fields identical to those listed under `enemies` above.
    - `AddItem(item)` Adds an item. Auto-validates the item format and returns the completed item table.
        - `item` The item data table.
            - `id` The item's detection id, not localized. If missing or invalid, replaced with `STONE`.
            - `name` The item's actually displayed name. If missing or invalid, replaced with `Stone`.
            - `_color` (optional) The item's color, composed of three numbers `0 ~ 1`.
            - `_cantdestroy` (optional) If `true`, the item is not consumed when used.
    - `InitAnimation(index, pos)` Initializes the animation of the `index`-th enemy and returns the animation instance.
        - `index` The enemy's ordinal in the `enemies` table.
        - `pos` The animation's position.
        - Return value: the enemy's animation instance. All subsequent operations are performed on it (`anim.SetFace(3)`);
          repeated calls do not rebuild it — they return the same instance as-is.
    - `ForceAttack(id)` Makes the specified enemy enter one attack resolution cycle (internally calls `Battle.attack.Restart`).
        - `id` The enemy's **string** `id` (the same style as `enemy_id`, not the `_id` number).
        - Note: it only looks up by `id`; if not found, it simply prints
          `[Battle - forceAttack] WARNING: No enemy found with id = ...` and does nothing;
          and this warning **is printed even on success**, so don't be fooled by it — judge by whether the enemy actually moved.

!!! tip "Difference Between Properties and Methods"
    Properties are **data**, written statically in the table; methods are **operations** used to append to or modify the data in the table.<br>
    The difference is: properties are read with a dot (`encounter.wave`), while methods are called with a colon (`encounter:AddEnemy(...)`).<br>
    A field is a method when it is defined as a function, so the table above looks a lot like the property table but is called differently.

!!! warning "A Warning Is Not an Error"
    When `AddItem` and `AddEnemy` find invalid data, they do not halt the game. Instead they print a warning and replace it with a default value:

    ```
    [Battle - Items] WARNING: Invalid item id.
    [Battle - Enemy] WARNING: Invalid enemy id, using default.
    ```

    The purpose of this is to guarantee the battle always runs, but **the replaced field won't tell you which enemy caused the problem**, so when you see a warning, go back and check the encounter file yourself.

---

## Turn Script

`wave` holds the name of a turn script (without the `.lua` extension), e.g. `bones.wave1`.<br>
This name is handed to `Battle.LoadWave` to resolve. The search order is:

1. `Game/Waves/<name>.lua` — the Game area, **priority**.
2. `Scripts/Waves/<name>.lua` — engine default, fallback.

If neither location is found, or the Game-area copy **exists but errors while loading**, the engine prints a warning and automatically falls back to the default `wave` script, ensuring the battle won't freeze over a single wave file.

!!! warning "Terminal Output on Fallback"
    When not found:

    ```
    [Battle - Wave] WARNING: wave 'bones.wave1' not found. Searched, in order:
        Game.Waves.bones.wave1  (Game/Waves/bones/wave1.lua)
        Scripts.Waves.bones.wave1  (Scripts/Waves/bones/wave1.lua)
    [Battle - Wave] Falling back to the default wave (Scripts.Waves.wave).
    ```

    When the Game-area copy is broken (**Note: it still falls back successfully, but it will definitely tell you the override has a problem** — it is not silent):

    ```
    [Battle] WARNING: 'Game.Waves.bones.wave1' exists but failed to load; using Scripts.Waves.bones.wave1 instead.
    [Battle]   <the actual error message>
    ```

    Therefore, **whenever you see `exists but failed to load`, it means your override did not take effect** — go fix that file; don't suspect the engine didn't read it.

Available methods:

!!! example "Turn Script Methods"
    - `Battle.LoadWave(wave_name)` Loads a turn script and returns the finally selected wave table.
        - `wave_name` The turn script name. Uses the default `wave` when left empty or `nil`.
    - `Battle.waveModule` The full module name that actually loaded successfully last time, e.g. `Game.Waves.bones.wave1`. Can be used to confirm whether the override took effect.
    - `Battle.ClearWaveModule(wave_name)` Clears the turn script's cache.
        - `wave_name` The turn script name. Uses the current `Battle.wave` when left empty.

!!! tip "Why Clear Cache in Both Locations"
    `ClearWaveModule` clears the same-name cache in **both** the Game area and the engine directory at once.<br>
    This way, when a script has been moved between the two locations (from `Scripts/Waves/` to `Game/Waves/`), no leftover old version remains.

---

## Enemy Animation

Starting with `3.0.0`, animations are bound to the encounter file; any operations done to them during battle are received by dedicated functions.

Animation **does not use a metatable**: `New(pos)` returns a plain table that uses `_class` to point back to the module itself.
All functions are declared with a dot, and their first parameter is the instance `self`. Before `New` returns, it calls
`Battle.BindAnimation(self, this module)`, binding these functions **onto the instance itself**,
so external dispatch is written with a dot and does not pass `self`:

```lua
anim.SetFace(3)        -- instead of cls.SetFace(anim, 3)
anim.Update(dt)
anim.cpos[1] = 100     -- position is just a plain field on the instance, read/write directly
```

Writing it with a colon (`anim:Update(dt)`) would pass the instance one extra time and the engine would error on the spot.
(Sprites are still engine objects, so keep the colon syntax `sprite:Set(...)`).

Here is a standard animation template:

??? example "Animation Template"

    ```lua
    local MyMonster = {}

    function MyMonster.New(pos)
        local self = {}

        -- The instance uses `_class` to point back to this module
        self._class = MyMonster

        self.running = true
        self.x = 0
        self.y = 0
        self.elements = {}
        self.hurting = false
        self.hurttime = 0
        self.intensity = 16
        MyMonster.Init(self, pos)

        -- Required: bind this module's functions to the instance, so callers can write `anim.Hurt()`
        Battle.BindAnimation(self, MyMonster)

        return self
    end

    function MyMonster.Init(self, pos)
        local _pos = (pos or {320, 140})
        local sprite = Sprites.CreateSprite("poseur.png", "UI")
        sprite:MoveTo(_pos[1], _pos[2])

        self.sprite = sprite
        self.cpos = {sprite.x, sprite.y}
    end

    function MyMonster.Hurt(self)
        self.hurting = true
        self.intensity = 16
    end

    --- OPTIONAL: called the moment an attack is LAUNCHED at this enemy, before the
    --- hit lands. Implement it to react (brace / dodge / telegraph / counter, ...).
    --- `data` may contain:
    ---   data.enemy    → this enemy table
    ---   data.damage   → planned damage for the hit
    ---   data.perfect  → true when the timing landed in the perfect zone
    ---   data.offset   → distance from the perfect zone (0 = perfect)
    ---   data.position → {x, y} of the enemy on screen
    ---   data.attack   → the attack pattern instance
    function MyMonster.OnAttack(self, data)
    end

    function MyMonster.Spare(self)
    end

    function MyMonster.Update(self, dt)
        if (not self.running) then
            return
        end

        -- ====================>
        -- TODO: put your monster's animation code here.
        --
        -- Example: react to engine-provided state
        --   if (self.canspare) then ... end            -- spareable?
        --   if (self.dead) then                        -- HP hit 0 and killable
        --       self.sprite:SetAnimation({"death_0.png", "death_1.png"}, 0.1)
        --   end

        -- Default hurt shake: knock the sprite sideways, decaying toward 0.
        if (self.hurting) then
            local p = self.sprite
            p.x = self.cpos[1] + self.intensity
            if (self.intensity > 0) then
                self.intensity = self.intensity - 1
                self.intensity = -self.intensity
            elseif (self.intensity < 0) then
                self.intensity = -self.intensity
            end
        end
        -- <====================
    end

    function MyMonster.Destroy(self)
        if (not self.sprite) then
            return
        end

        -- TODO: play a death effect here, e.g. sprite:Dust(true, true)
        self.sprite:Dust(true, true)
        self.sprite = nil

        -- Destroy every extra object registered in `elements`.
        for i = #self.elements, 1, -1
        do
            local e = self.elements[i]
            if (e and e.Destroy) then
                e:Destroy()
            end
        end
        self.elements = {}
    end

    return MyMonster
    ```

Next, all the functions are described. The signatures in parentheses are **the internal module signatures** — the function bodies rely on these `self` arguments;
when called from outside (the scene, waves, attack patterns), always write `anim.Foo(...)` without passing `self`,
for example `anim.Hurt()`, `anim.Update(dt)`, `anim.SetFace(3)`.

!!! example "Function Methods"
    - `New(pos)` The animation's position, returns an independent plain-table instance.
    - `Init(self, pos)` Animation initialization, responsible for creating the sprite and variables.
    - `Hurt(self)` Executed when taking damage (the player's weapon sends a Hurt signal).
    - `OnAttack(self, data)` Executed when the attack key is pressed during calibration; `data` stores the calibration result, etc.
    - `Spare(self)` Executed when spared successfully; can produce effects like the enemy turning black.
    - `Destroy(self)` Executed once when killed, can be used for effects like turning to dust.
    - `Update(self, dt)` Executed every frame; the vast majority of animation code is written here.

### Initializing Animation

The initialization flow is semi-automatic: `InitAnimation` is a method the engine provides through `game_apis`, and we only need to **call** it in the battle scene, once per enemy.

`index` is which enemy (1-based). If you write too large or a wrong number, it won't error — the terminal just emits a warning.

!!! warning "Terminal Warning"
    ```
    [Game - Animation] WARNING: Enemy #x has no animation.
    ```

For `pos`, since each monster's standing position may differ during battle.<br>
When initializing and assigning enemies, you need to use the `pos` parameter to adjust the position.

!!! example "Usage Example"

    ```lua
    local mobs = {"froggit", "whimsum", "migosp"}
    local ypos = {
        ["froggit"] = 160
        ["whimsum"] = 80
        ["migosp"]  = 200
    }

    -- After saving ypos, we can decide what to spawn
    for i = 1, 3
    do
        -- Randomly pick one of these three monsters
        local name = mobs[math.random(#mobs)]

        Game:AddEnemy(
            {
                id = name,
                name = name,
                animation = require("Game.Animations." .. name),

                maxdamage = 400,
                dmg_float = 2,  -- Some random stuff......I hate them

                show_hpbar = true, -- Sans... stop hiding your hp bar.
                maxhp = 100,
                hp = 100,
                gold = 1,
                exp = 1,

                defensetext = "MISS",
                misstext = "MISS",

                canspare = true,
                killable = true,

                -- Set position
                position = {100 + 150 * (i - 1), ypos[name]},

                actions = {
                    {id = "Check", name = Localize.localizeText("Battle.Actions.Names.Check")},
                    {id = "Pose",  name = Localize.localizeText("Battle.Actions.Names.Pose")},
                }
            },
        )
    end
    ```

---

### Writing Animation

For the vast majority of fan projects, we can drop the `Spare` feature, and most of our code will be written in the `Update` function.

```lua
function MyMonster.Update(self, dt)
    if (not self.running) then
        return
    end

    -- ====================>
    -- TODO: put your monster's animation code here.
    --
    -- Example: react to engine-provided state
    --   if (self.canspare) then ... end            -- spareable?
    --   if (self.dead) then                        -- HP hit 0 and killable
    --       self.sprite:SetAnimation({"death_0.png", "death_1.png"}, 0.1)
    --   end

    -- Default hurt shake: knock the sprite sideways, decaying toward 0.
    if (self.hurting) then
        local p = self.sprite
        p.x = self.cpos[1] + self.intensity
        if (self.intensity > 0) then
            self.intensity = self.intensity - 1
            self.intensity = -self.intensity
        elseif (self.intensity < 0) then
            self.intensity = -self.intensity
        end
    end
    -- <====================
end
```

The comments provide a small example: you can switch animations with `canspare`, or switch to another set with `dead` — though those comments won't actually run as-is.<br>
Without conditional wrapping, we can write another set of ordinary animation.

**If you want a detailed tutorial on how to write good animations, go to [Advanced Development → Math Tutorial](../050_intermediate/040_math.md).**

Here is a partial explanation, using Sans as a special example:

??? example "Sans Animation"

    ```lua
    function Sans.OnAttack(self, data)
        local ty = 220
        Tween.CreateTween(function (v)
            self.cpos[1] = v
        end, "Quad", "Out", 320, ty, 40)
        Tween.CreateTween(function (v)
            self.cpos[1] = v
        end, "Quad", "Out", ty, 320, 35, 80)
    end

    function Sans.Spare(self)
        -- Spared: sans fades out instead of dying.
        for _, sprite in ipairs(Sans.AllSprites(self)) do
            sprite.alpha = 0.5
        end
    end

    function Sans.Update(self, dt)
        if (not self.running) then
            return
        end

        if (not self.legs or not self.body or not self.head or not self.cpos) then
            return
        end

        -- A "30 FPS frame tick": every counter ported from the original advances by
        -- this much, so the animation speed is frame-rate independent.
        local step = dt * SOURCE_FPS

        -- ====================>
        -- 1) SWAY / BOUNCE ----------------------------------------------------
        -- bounce 0 = still, 1 = idle 8-shape, 2 = medium bob, 3 = tired bob.
        local xoff, yoff = 0, 0
        local bounce = math.floor(self.bounce or 0)

        if (bounce == 3) then
            -- Large, slow vertical breathing (worn-out sans).
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 18) * 2
        elseif (bounce == 2) then
            -- Medium vertical bob.
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 15) * 4
        elseif (bounce == 1) then
            -- Idle: fast vertical + slow horizontal → a small figure 8.
            self.siner = self.siner + step
            yoff = math.sin(self.siner / 3)
            xoff = math.cos(self.siner / 6)
        else
            -- Still.
            self.siner = 0
        end

        local scale = self.bounce_scale or 1
        xoff = xoff * scale
        yoff = yoff * scale
        self.xoff = xoff
        self.yoff = yoff

        -- 2) HURT SHAKE -------------------------------------------------------
        -- Same decay as the reference: flip the sign every tick while the
        -- magnitude shrinks by one unit per tick (0.5 units per frame at 60 FPS).
        local shake_x = 0
        if (self.hurting) then
            shake_x = self.intensity
            if (self.intensity > 0) then
                self.intensity = -(self.intensity - step)
            else
                self.intensity = -self.intensity
            end

            if (math.abs(self.intensity) <= step) then
                self.intensity = 0
                self.hurting = false
            end
        end

        -- 3) HEAD OFFSETS (attack poses) --------------------------------------
        if (self.head_auto_return) then
            local k = math.min(1, (self.head_return_speed or 6) * dt)
            self.headx = self.headx - self.headx * k
            self.heady = self.heady - self.heady * k
            if (math.abs(self.headx) < 0.05) then self.headx = 0 end
            if (math.abs(self.heady) < 0.05) then self.heady = 0 end
        end

        -- 4) BLUE-EYE AUTO-OFF (only for :FlashBlueEye) -----------------------
        if (self._blueeye_timer) then
            self._blueeye_timer = self._blueeye_timer - dt
            if (self._blueeye_timer <= 0) then
                self._blueeye_timer = nil
                if (self._blueeye_flash) then
                    self._blueeye_flash = false
                    self.facetype = 0
                    self.f_i = 0
                end
            end
        end

        -- 5) TORSO IDLE CYCLE --------------------------------------------------
        -- The original only drew the plain torso while no arm animation was
        -- playing (`movearm == 0`); the same flag pauses this cycle.
        if (math.floor(self.movearm or 0) == 0) then
            self.torso_time = self.torso_time + dt
            if (self.torso_time >= TORSO_INTERVAL) then
                self.torso_time = self.torso_time - TORSO_INTERVAL
                self.torsoframe = (self.torsoframe + 1) % TORSO_FRAMES
                self.body:Set(self.torso_frames[self.torsoframe + 1])
            end
        end

        -- 6) FACE / BLUE EYE / SWEAT ------------------------------------------
        Sans.UpdateFace(self, step)

        -- 7) PLACE EVERY PART --------------------------------------------------
        Sans.ApplyOffsets(self, xoff, yoff, shake_x)

        -- 8) DEATH -------------------------------------------------------------
        -- `self.dead` is set by Battle.Update once HP hit 0 and the enemy is
        -- killable. sans has no death sheet yet, so we just freeze the idle sway
        -- and let Destroy() play the dust effect. Add your own animation here.
        if (self.dead) then
            self.bounce = 0
        end
        -- <====================
    end
    ```

Since it is too long, we only look at the idle left-right sway animation when `bounce = 1`:

!!! example "Idle Animation"

    ```lua
    self.siner = self.siner + step
    yoff = math.sin(self.siner / 3)
    xoff = math.cos(self.siner / 6)
    ```

It uses trigonometric functions to set up periodic movement; `/3` and `/6` produce two different speeds, meaning the head and body move along an `∞` trajectory.
