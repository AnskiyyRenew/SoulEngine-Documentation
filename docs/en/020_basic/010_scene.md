---
title: Scene
---

In Soul Engine, every room can be called a room, or a Scene.<br>
By default, every Scene is a pure black area with no additional content shown.

Scene Manager path: `Scripts/Libraries/SceneManager.lua`

---

## How a Scene Runs

Scenes are placed in `Scripts/Scenes/` by default. There is also a Game-region copy: `Game/Scenes/`, where **same-named files take priority over the engine directory** and fall back only when not found. So if you want to replace an engine-built-in Scene, you don't need to modify the engine — just put a same-named file into `Game/Scenes/`.

There must be one Scene running at all times; simply put: from the moment you enter the game until you quit, every frame you are inside some Scene, and there is no "void period".

---

## Creating a Scene

Open the Scene path and you will see many default Scenes, but in practice you only need to focus on two files to create a new Scene: `scene_template.lua` and `scene_template_full.lua`.

One is the lightweight version (use this file for daily development), and one is the full version (use this file when making certain page tools).

If you cannot find them, they may have been accidentally deleted; below are the two versions of the Scene code, which you can copy directly:

??? example "template"
    ```lua
    local scene = {}

    function scene.update(dt)
    end

    function scene.draw()
    end

    function scene.clear()
        Layers.clear()
    end

    return scene
    ```

??? example "full"
    ```lua
    local scene = {}

    -- ============================================
    -- 1. CORE LIFECYCLE CALLBACKS
    -- ============================================

    --- Called once when the scene is first loaded.
    function scene.load()
    end

    --- Called every frame to update the scene state.
    --- @param dt number|nil Delta time since last update.
    function scene.update(dt)
    end

    --- Called every frame to draw the scene.
    function scene.draw()
    end

    --- Called when leaving the scene.
    function scene.clear()
    end

    --- Called when the game is about to quit.
    function scene.quit()
        print("SE.quit: Game is quitting... Goodbye!")
    end


    -- ============================================
    -- 2. KEYBOARD CALLBACKS
    -- ============================================

    --- Called when a key is pressed.
    --- @param key string The key name (e.g., "escape", "a").
    --- @param scancode string The scancode of the key.
    --- @param isrepeat boolean True if this is a repeated key event.
    function scene.keypressed(key, scancode, isrepeat)
        if key == "escape" then
            SE.event.quit() -- Press ESC to quit the game
        end
        print("SE.keypressed: Key '" .. key .. "' pressed")
    end

    --- Called when a key is released.
    --- @param key string The key name.
    --- @param scancode string The scancode of the key.
    function scene.keyreleased(key, scancode)
        print("SE.keyreleased: Key '" .. key .. "' released")
    end

    --- Called when text input is received (e.g., from IME or character input).
    --- @param text string The input text.
    function scene.textinput(text)
        -- Example: append input text to a string
        print("SE.textinput: Text input received: " .. text)
    end


    -- ============================================
    -- 3. MOUSE CALLBACKS
    -- ============================================

    --- Called when a mouse button is pressed.
    --- @param x number X coordinate of the mouse.
    --- @param y number Y coordinate of the mouse.
    --- @param button number The button number (1 = left, 2 = right, etc.).
    --- @param istouch boolean True if the event came from a touchscreen.
    --- @param presses number Number of presses in a row (for double-click detection).
    function scene.mousepressed(x, y, button, istouch, presses)
        print(string.format("SE.mousepressed: Button %d pressed at (%d, %d)", button, x, y))
    end

    --- Called when a mouse button is released.
    --- @param x number X coordinate of the mouse.
    --- @param y number Y coordinate of the mouse.
    --- @param button number The button number.
    --- @param istouch boolean True if the event came from a touchscreen.
    --- @param presses number Number of presses in a row.
    function scene.mousereleased(x, y, button, istouch, presses)
        print(string.format("SE.mousereleased: Button %d released at (%d, %d)", button, x, y))
    end

    --- Called when the mouse is moved.
    --- @param x number Current X coordinate.
    --- @param y number Current Y coordinate.
    --- @param dx number Change in X since last frame.
    --- @param dy number Change in Y since last frame.
    --- @param istouch boolean True if the event came from a touchscreen.
    function scene.mousemoved(x, y, dx, dy, istouch)
        -- Mouse move events are frequent; avoid printing debug info here.
        -- Use this to update mouse-related logic (e.g., hover states).
    end

    --- Called when the mouse wheel is scrolled.
    --- @param x number Horizontal scroll amount.
    --- @param y number Vertical scroll amount.
    function scene.wheelmoved(x, y)
        print(string.format("SE.wheelmoved: Scrolled dx=%.1f, dy=%.1f", x, y))
    end


    -- ============================================
    -- 4. WINDOW & SYSTEM CALLBACKS
    -- ============================================

    --- Called when the window gains or loses focus.
    --- @param f boolean True if the window gained focus, false if it lost focus.
    function scene.focus(f)
        if f then
            print("SE.focus: Window gained focus")
        else
            print("SE.focus: Window lost focus")
        end
    end

    --- Called when the window is resized.
    --- @param w number New window width.
    --- @param h number New window height.
    function scene.resize(w, h)
        print(string.format("SE.resize: Window resized to %dx%d", w, h))
        -- Use this to recalculate UI layout or camera viewport
    end

    --- Called when the window visibility changes (minimized/restored).
    --- @param v boolean True if the window is visible.
    function scene.visible(v)
        if v then
            print("SE.visible: Window is now visible")
        else
            print("SE.visible: Window is now hidden")
        end
    end


    -- ============================================
    -- 5. DRAG & DROP CALLBACKS
    -- ============================================

    --- Called when one or more files are dragged and dropped onto the window.
    --- @param file SE.File The dropped file object.
    function scene.filedropped(file)
    end

    --- Called when a directory is dragged and dropped onto the window.
    --- @param dir SE.File The dropped directory object (also a SE.File).
    function scene.directorydropped(dir)
    end

    return scene
    ```

After copying, paste it in the same directory and rename it (into `Scripts/Scenes/`; to override an engine-built-in Scene put it in `Game/Scenes/`, same name takes priority).

---

## Switching Scenes

Use the `Scenes.switchTo(scene, ...)` function to switch to another Scene.

- `scene` The Scene to go to, with the path counted from `Scripts/Scenes/`.
- `...` Variable parameters; you can put some values in here to pass to the target Scene. Normally you can use `global variables` instead, but this is more convenient.

The example below shows switching Scenes with parameters; you will most likely see the input `320, 240` printed to the terminal:
!!! example "Switching Scenes with parameters"
    ```lua
    Scenes.switchTo("scene_gameover", 320, 240)
    ```

    scene_gameover:
    ```lua
    function scene.load(...)
        print(...)
    end
    ```

---

## Clearing a Scene

When leaving a Scene, you need to clear all the images / audio / typer assets you created in the Scene, to prevent them from carrying into the next Scene.

The `scene.clear()` function is responsible for this.<br>
Normally, we write the `Layers.Clear()` function inside it, which thoroughly clears all visible content in the Scene.

For audio, we use the `Audio.Clear()` function to clear it.

!!! example "Clearing audio and images"
    ```lua
    function scene.clear()
        Layers.Clear()
        Audio.Clear()
    end
    ```

---

## Clearing the Cache

**Aside from the above, the most important and also the easiest-to-forget part to clean up is the cache.**

When entering a Scene, each Scene produces a cache due to the `require` operation, and that cache cannot be fully cleared simply by clearing Layers and Audio.

Symptom: the second time you enter a Scene, some variables remain in the state they were when you last left.

!!! warning "Cache residue"
    Back in `Soul Engine v1.1.0` it was the cache that did us in, so I pay special attention to this.

1.**Use `package.loaded` to unload the cache:**

!!! example "package.loaded"
    ```lua
    package.loaded["Scripts.Libraries.Beat"] = nil
    ```

**Note: the key name here uses a dot (`.`), not a slash (`/`).** <br>
The keys in `package.loaded` are the module names used in `require`, e.g. `require("Scripts.Libraries.Beat")` produces the key `Scripts.Libraries.Beat`.<br>
Writing `"Scripts/Libraries/Beat"` will not error, but **it also clears nothing** — it is one of the easiest pitfalls.

If you get stuck on a beat in some Scene, and then re-enter the Scene and find the starting beat is several hundred, now at the very beginning it will be reset to zero properly.

2.**Use `ClearModuleTree(path)` to clear the cache of all contents in a folder.**

!!! example "CMT function"
    ```lua
    ClearModuleTree("Scripts.Libraries.Attacks")
    ClearModuleTree("Scripts.Libraries.Battle")
    ```

After use, all libraries in these two folders will have their cache cleared; you no longer need to write out each file path one by one.

3.**Use `ClearGameTree(sub_root)` to clear the cache of the `Game/` tree.**

!!! example "CGT function"
    ```lua
    ClearGameTree("Souls")       -- clears Game.Souls.*
    ClearGameTree("Animations")  -- clears Game.Animations.*
    ClearGameTree()              -- no parameter = clears the entire Game region
    ```

`Game/` is **a second tree independent of `Scripts.Libraries`**. Things like `Game/Souls/`, `Game/Animations/`, `Game/Encounter/`, `Game/Attacks/`, `Game/Waves/` cannot be cleared using only `ClearModuleTree("Scripts...")` — they must be cleared separately with this.<br>
(Both trees are provided by `Scripts/Libraries/Engine/PathDefiner.lua`, and neither touches `Game/Hacks/` or `Game/Logics/`.)

---

Note: a Scene does not need to unload itself additionally; `SceneManager` will actively clear the Scene itself, but the main thing is to write the unloading process for other libraries well inside the Scene's `clear` function.

---

## Some Examples

??? example "logo walkthrough"
    Path: `Scripts/Scenes/scene_logo.lua`

    ```lua
    local scene = {}
    Audio.Clear()
    Camera:reset()

    local logo = Sprites.CreateSprite("Logo.png")
    local time = 0
    local alpha = 0

    Audio.PlaySound("snd_intro.ogg")
    local font = Fonts.New("determination_mono.ttf", 13, "mono")
    font:setFilter("nearest", "nearest")

    local tip = Fonts.New("Mars Needs Cunnilingus.ttf", 13, "mono")
    tip:setFilter("nearest", "nearest")

    function scene.update(dt)
        time = time + 1
        if (time >= 180 and time % 60 == 0) then
            alpha = 1 - alpha
        end

        if (Controller.GetState("confirm") == 1) then
            Scenes.switchTo("Battle.scene_battle_init")
        end
    end

    function scene.draw()
        SE.graphics.setFont(font)
        SE.graphics.setColor(0.4, 0.4, 0.4, alpha)
        SE.graphics.printf("[PRESS Z OR ENTER]", 0, 320, 640, "center")

        SE.graphics.setFont(font)
        SE.graphics.setColor(1, 0, 0, 1)
        SE.graphics.printf("Undertale By Toby Fox © 2015", 0, 445, 640, "left")

        SE.graphics.setColor(0.4, 0, 1, 1)
        SE.graphics.printf("SoulEngine By Anskiyy © 2024", 0, 460, 640, "left")

        SE.graphics.setColor(1, 1, 1, 1)
        SE.graphics.printf(_VER, 0, 460, 640, "right")
    end

    function scene.clear()
        Audio.Clear()
        Layers.clear()
    end

    return scene
    ```

    At the start it resets the audio and Camera, and creates the logo.<br>
    It also plays the audio `snd_intro.ogg` (similar to a "thud" opening).

    draw renders the small corner text and the prompt.

    When update's time keeps increasing to 180, the prompt `PRESS Z OR ENTER` starts to light up and blink (done by controlling the alpha `alpha`).

    When the Player presses Z or ENTER, it switches to the `scene_battle_init` Scene in the `Battle` folder, executing the content in `scene.clear()` to clear the scene and leave.

??? example "clearing the cache"
    Path: `Scripts/Libraries/Battle/init.lua`

    ```lua
    function battle.Clear()
        -- Clear the game module tree so it re-queries Localize on next load
        if battle.gameName then
            ClearModuleTree(battle.gameName)
        end

        -- Clear all loaded attack pattern modules. attack_paths holds resolved
        -- module names, so both roots (Game.Attacks.* and
        -- Scripts.Libraries.Battle.PlayerAttacks.*) are covered.
        for i = #battle.attack_paths, 1, -1
        do
            ClearModuleTree(battle.attack_paths[i])
        end
        ClearGameTree("Attacks")

        -- Game region has its own tree: only clearing Scripts.Libraries.Battle
        -- leaves these behind, and next time you enter battle you'd get the last
        -- encounter / monster animation / soul module, bringing state along.
        ClearGameTree("Encounter")
        ClearGameTree("Animations")
        ClearGameTree("Waves")
        ClearGameTree("Souls")

        if (Battle._wave) then
            Battle._wave._end = false
            Battle._wave.objects = {}
            Battle._wave._paths = {}
        end
        Battle._wave = {}
        -- public wrapper; internally clears both Game.Waves. and Scripts.Waves. prefixes
        Battle.ClearWaveModule(Battle.wave)
        battle.restoring_arena = false

        -- Clear the entire Battle library tree (UI, buttons, Player, Arenas,
        -- game_apis, Waves, PlayerAttacks, Souls, etc.) in a single pass.
        ClearModuleTree("Scripts.Libraries.Attacks")
        ClearModuleTree("Scripts.Libraries.Battle")
    end
    ```
    When called: clears the game files, attack files, **the Game region's attacks / encounters / monster animations / waves / souls**, and the entire battle library tree's cache.

    Ensures everything is normal next time you enter.

    Note: `Battle.ClearWaveModule(Battle.wave)` is a dedicated method provided by the `Battle` library; it clears the same-named cache under **both** the `Game.Waves.` and `Scripts.Waves.` prefixes at once, which is more reliable than writing `ClearModuleTree` by hand — even if the round script was moved between the two locations, no old version remains.
