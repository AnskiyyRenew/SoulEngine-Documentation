---
title: Battle Scene and Callbacks
---

The battle's **flow** is handled by the engine, the battle's **content** is handled by the encounter file, and the layer in between — "what exactly happens in this battle" (e.g. how much healing an item gives, what to play on flee) — is written in the battle scene.

Path: `Scripts/Scenes/Battle/`. The engine ships four: `scene_battle.lua`, `scene_battle_init.lua`, `scene_battle_template.lua`, `scene_battle_ow.lua`; just copy one and modify it.

---

## Scene Skeleton

```lua
local scene = {}

-- 1) Import the battle module
Battle = ImportFile("Battle")
Battle.SetEndRoom("scene_end")

-- 2) Load the encounter file
Game = Battle.SetGame("Poseur")
Game:AddItem({id = "STABLE", _color = {0.5, 0, 0}, name = "ImNotFood"})

-- 3) Initialize each enemy's animation (one line per enemy)
--    position is just a plain field on the instance; animation ops are also
--    written directly on the instance (dot, no self passed)
Game:InitAnimation(1, {320, 140})

-- Example: after getting the instance, change expression / move position
-- local boss = Game.enemies[1].animation
-- boss.SetFace(3)
-- boss.cpos[1] = 260

-- 4) Write callbacks
local function HandleItems(item)
    Player.Heal(99, true)
    Battle.BattleDialogue({"* You ate " .. item.name .. "."}, "ACTIONSELECT")
end

Battle.HandleItems = HandleItems

-- 5) Background
local background = Sprites.CreateSprite("px.png", "Background")
background:Scale(640, 480)

function scene.update(dt)
    Battle.Update(dt)
end

function scene.clear()
    Layers.clear()
    Battle.Clear()
end

return scene
```

!!! danger "Neither Line in `scene.clear` Can Be Omitted"
    `Battle.Clear()` clears the whole set of caches — encounter, animation, wave, Soul, attack pattern;<br>
    `Layers.clear()` clears the layers. Omit the former and the second time you enter battle you'll get the leftover state from the previous one (enemies still carrying the last HP bar, Soul reusing the last color), and it **won't error** — very hard to debug.

---

## Callback Overview

These callbacks are all fields on `Battle`, called by the engine at fixed moments. **Just override them in the scene**; if not written, the engine's empty implementation is used.

!!! example "Flow Callbacks"
    - `Battle.HandleActions(enemy, action)` The player confirmed an action in `ACTMENU`.
        - `enemy` The enemy being acted upon.
        - `action` The selected action table, containing `id` and `name`.
    - `Battle.HandleItems(item)` The player used an item.
        - `item` The used item table. Whether the item is consumed is handled by the engine (`_cantdestroy` = `true` keeps it).
    - `Battle.HandleSpare()` The player selected `Spare` in `MERCYMENU`, **and there are still enemies on the field that haven't been spared**.
        - Spareable enemies have already been removed at this point, and their `gold` has been settled into `Battle.GOLD`.
        - When not a single enemy remains, the engine goes straight to `Battle.Win()` and **won't** reach here; so this callback only appears in scenes where "some enemies are spareable".
    - `Battle.HandleFlee()` The player selected `Flee` in `MERCYMENU` and the check succeeded.
    - `Battle.FleeUpdate(dt)` Called every frame while in the `FLEEING` state.
    - `Battle.DefenseEnding()` Called at the instant the enemy turn ends and returns to the player turn.
    - `Battle.OnHit(bullet)` The player's Soul touched a bullet.
        - `bullet` The sprite object hit; read its `HurtMode` to decide whether to deduct HP.
    - `Battle.EnteringState(old, new)` Called when the state switches. **When overriding, you must call the default implementation first**:
        ```lua
        local function EnteringState(oldstate, newstate)
            Battle.defaultEnteringState(oldstate, newstate)
            -- your own logic
        end
        ```
    - `Battle.Win(extra_texts, on_complete)` Battle won. Also recommended to call `Battle.defaultWin`:
        ```lua
        local function Win()
            Battle.defaultWin({"* Your LOVE increased!"})
        end
        Battle.Win = Win
        ```

!!! warning "`HandleSpare` Is an Empty Function in the Engine; Not Taking It Over Causes Trouble"
    On the engine side there is only `function battle.HandleSpare() end`.<br>
    And on the same frame the player confirms Spare, the engine has already `destroy_elements()` and cleared the Spare menu's options (`state.typers`).
    If you do nothing and the state is still stuck at `MERCYMENU`, the next frame it will read that already-emptied table and directly throw `attempt to index a nil value`.

    So whenever your battle has a situation where "some enemies are spareable, others aren't", you must take it over in the scene. The laziest approach is to just advance to the enemy turn as usual:

    ```lua
    local function HandleSpare()
        Battle.BattleDialogue({"* The remaining enemies aren't about to let you off."}, "DEFENDING")
    end

    Battle.HandleSpare = HandleSpare
    ```

    The two built-in Poseurs are both `canspare = true`; one Spare clears them and goes straight to `Win()`, so you won't hit this in the demo scene.

!!! example "Standard OnHit"
    The engine passes the bullet's `HurtMode` to you as-is; how to interpret it is up to you:
    The engine passes the bullet's `HurtMode` to you as-is; how to interpret it is up to you:

    ```lua
    local function OnHit(bullet)
        local damage = 1
        local mode = (bullet["HurtMode"] or "normal"):lower()

        if (mode == "normal") then
            Player.Hurt(damage)
        elseif (mode == "blue" or mode == "cyan") then
            -- Blue: only hurt while moving
            if (Controller.GetState("arrows") > 0) then
                Player.Hurt(damage)
            end
        elseif (mode == "orange") then
            -- Orange: only hurt while standing still
            if (Controller.GetState("arrows") <= 0) then
                Player.Hurt(damage)
            end
        end
    end
    ```

---

## Dialogue

Almost all battle text goes through the typewriter; the engine provides two wrappers:

!!! example "Dialogue Methods"
    - `Battle.BattleDialogue(texts, final_state)` Play a narration; after it finishes, switch to the specified state.
        - `texts` The text array (**cannot be Chinese** unless the font supports it).
        - `final_state` Which state to switch to after playing, default `"ACTIONSELECT"`.
    - `Battle.FullDialogue(texts, call)` Play a narration; after it finishes, execute a function.
        - `call` What to do after playing, e.g. `function () Battle._end = true end`.
    - `Battle.narration_text` The typewriter object for the always-on narration line in the battle box.

!!! note "Waiting and Fast-Forwarding in Battle Text"
    You can mix in typewriter tags within `texts`; the two most common in battle dialogue are:

    - `[wait:x]` Pause for `x` **seconds** before continuing. It uses the typewriter's **own** `waittime` timer, independent of the per-character interval — writing `[wait:0.5]` then `[speed:0.01]`, that half-second pause won't be swallowed by the speed-up.
    - `[speed:x]` Change the per-character interval (each character `x` seconds); takes effect until the next `[speed:]`. Default `1/15 ≈ 0.0667` seconds.

    When the player holds the **cancel key** (default `X`), the engine will **directly clear the current `waittime`** and immediately finish the remaining characters, without waiting segment by segment. Text with `[noskip]` ignores this.

    The complete tag table is in [Basic Development → Typewriter](../020_basic/030_typers.md).

---

## State and Flow Control

!!! example "State Methods"
    - `Battle.ChangeState(new_state)` Switch state. **This is the only proper way to switch**, it guarantees `EnteringState` is called exactly once.
    - `Battle.state` The current state. Available values see [UI → State Flow](./010_ui.md).
    - `Battle.game` The current encounter table.
    - `Battle.EXP` / `Battle.GOLD` The EXP and gold accumulated in this battle, auto-added when an enemy dies.
    - `Battle._end` Once set to `true`, the screen starts fading out; once the fade completes, it switches to `Battle.room_end`.
    - `Battle.SetEndRoom(room)` Set which scene to go to after the battle ends, default `"scene_end"`.
    - `Battle.room_end` The currently set ending scene name.

!!! example "Selected Items"
    - `Battle.selected_enemy_index` Which enemy the player currently has selected.
    - `Battle.selected_action_index` Which action the player currently has selected.
    - `Battle.selected_index` Which item the player currently has selected.

These three values are especially useful inside `EnteringState` — e.g. to judge "the player used Check on enemy #1".

---

## Other Available Methods

!!! example "General Methods"
    - `Battle.Update(dt)` Called every frame; advances the player, battle box, UI, and all enemy animations.
    - `Battle.UpdateRestore(dt)` Called during the battle box's rebound after the enemy turn ends; the engine has already hooked it up.
    - `Battle.Clear()` Clear the entire battle module tree and the Game-area battle content cache.
    - `Battle.SetGame(file)` Load the encounter file, returns the encounter table (returns nothing if not found).
    - `Battle.SetAttackPattern(name)` Switch attack pattern, see [Attack Pattern](./040_attack.md).
    - `Battle.Defending()` Manually enter the enemy turn (rarely needed; the state machine walks there itself).

---

## Connecting with Overworld

Battles entered by bumping into them from the overworld use `scene_battle_ow.lua`, which does two extra things compared to a normal battle scene:

1. **Entry**: Push `DATA.player`'s save data into `Player`; the battle uses real HP rather than the template values from the encounter file.
2. **Exit**: On `scene.clear`, write EXP / GOLD / remaining HP back into `DATA`, and settle level-ups per `DATA.lv_data`.

To change the level-up rules (e.g. raise the level cap from 20 to 30, change the HP curve per level), go to the `lv_data` table in `Game/Logics/init.lua`, see **[Game Logic and World Rules](../020_basic/120_game_logics.md)**;<br>
to change "how much you get for winning", change the enemy's `exp` and `gold` in the encounter file.

---

## Debugging Tips

- Enemy animation didn't show → check the terminal for `[Game - Animation] WARNING: Enemy #x has no animation.`, most likely the `InitAnimation` index is wrong.
- Wave didn't take effect → check for `exists but failed to load`, see [Battle Initialization](./000_init.md).
- Second time entering battle the state is off → check `Battle.Clear()` in `scene.clear`.
- Battle ended but didn't switch scene → check whether the scene name set by `Battle.SetEndRoom` actually exists.
- **Collision looks wrong** (HP deducted though clearly no contact / no deduction though clearly hit) → press `F7` to open the hitbox overlay, or call `Battle.ToggleHitboxes(true)` in code. When perfect-pixel collision is on, you see the real pixel outline rather than a rectangle, see [Basic Development → Sprites → Perfect Pixel Collision](../020_basic/020_sprites.md).
