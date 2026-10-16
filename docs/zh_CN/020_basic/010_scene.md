---
title: 场景
---

SoulEngine 中，房间与场景指同一概念，本文统一称为场景。<br>
每个场景默认状态下都是纯黑色区域，没有任何额外内容展示。

场景管理器路径： `Scripts/Libraries/SceneManager.lua`

---

## 场景的运行

场景默认放在 `Scripts/Scenes/` 。另外还有一份游戏区： `Game/Scenes/` ，**同名文件优先于引擎目录**，找不到才回退。替换引擎自带的场景时，将同名文件放入 `Game/Scenes/` 即可，无需修改引擎目录。

运行期间必须存在一个场景：从进入游戏到退出游戏，每一帧都处于某个场景之中，不存在 `虚空期` 。

---

## 新建一个场景

场景目录下包含多个默认场景。新建场景时参照两个文件： `scene_template.lua` 与 `scene_template_full.lua` 。

`scene_template.lua` 为轻量版，用于日常开发； `scene_template_full.lua` 为完全版，用于制作页面工具。

若未找到这两个文件，可直接使用下列代码：

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

复制以后，粘贴在同目录并改名（放在 `Scripts/Scenes/` ；要覆盖引擎自带的场景就放 `Game/Scenes/` ，同名优先）。

---

## 跳转场景

使用 `Scenes.switchTo(scene, ...)` 函数来跳转至另一个场景。

- `scene` 要去的场景，从 `Scripts/Scenes/` 开始算路径。
- `...` 不定参数，可填入需要传递给目标场景的值。该参数也可由全局变量代替。

下面的例子展示带参数切换场景，传入的 `320, 240` 会输出到终端：
!!! example "带参数的切换场景"
    ```lua
    Scenes.switchTo("scene_gameover", 320, 240)
    ```

    scene_gameover：
    ```lua
    function scene.load(...)
        print(...)
    end
    ```

---

## 清理场景

离开场景时，需清除场景内创建的图片、音频与打字机素材，避免带入下一个场景。

`scene.clear()` 函数负责此功能。<br>
通常在其中调用 `Layers.Clear()` ，该函数会清除场景内所有可视内容。

音频使用 `Audio.Clear()` 清除。

!!! example "清除音频和图片"
    ```lua
    function scene.clear()
        Layers.Clear()
        Audio.Clear()
    end
    ```

---

## 缓存的清理

**除上述内容外，缓存同样需要清理，该部分容易被遗漏。**

进入场景时， `require` 操作会产生模块缓存，该缓存无法由 `Layers` 与 `Audio` 的清理函数移除。

残留表现为：第二次进入场景时，某些变量保持上次离开时的值。

!!! warning "缓存残留"
    `Soul Engine v1.1.0` 曾因缓存残留出现问题，清理流程需覆盖 `require` 产生的全部模块。

1.**使用 `package.loaded` 卸载缓存：**

!!! example "package.loaded"
    ```lua
    package.loaded["Scripts.Libraries.Beat"] = nil
    ```

**注意：这里的键名用的是点号（ `.` ），不是斜杠（ `/` ）。** <br>
`package.loaded` 里的键就是 `require` 时用的模块名，比如 `require("Scripts.Libraries.Beat")` 产生的键是 `Scripts.Libraries.Beat` 。<br>
写成 `"Scripts/Libraries/Beat"` 不会报错，但不会清除任何缓存。

若重新进入场景时节拍计数从上次的值继续累加，执行上述清理后，计数会在场景开始时归零。

2.**使用 `ClearModuleTree(path)` 来清除一个文件夹里的所有内容缓存。**

!!! example "CMT函数"
    ```lua
    ClearModuleTree("Scripts.Libraries.Attacks")
    ClearModuleTree("Scripts.Libraries.Battle")
    ```

调用后，这两个文件夹下所有库的缓存都会被清除，无需逐个写出文件路径。

3.**使用 `ClearGameTree(sub_root)` 来清除 `Game/` 这棵树的缓存。**

!!! example "CGT函数"
    ```lua
    ClearGameTree("Souls")       -- 清掉 Game.Souls.*
    ClearGameTree("Animations")  -- 清掉 Game.Animations.*
    ClearGameTree()              -- 不传参数 = 清掉整个 Game 区
    ```

`Game/` 是**独立于 `Scripts.Libraries` 的第二棵树**。像 `Game/Souls/` 、 `Game/Animations/` 、 `Game/Encounter/` 、 `Game/Attacks/` 、 `Game/Waves/` 这些内容，这些模块无法由 `ClearModuleTree("Scripts...")` 清除，需要单独调用 `ClearGameTree` 。<br>
（这两棵树都由 `Scripts/Libraries/Engine/PathDefiner.lua` 提供，两者均不涉及 `Game/Hacks/` 与 `Game/Logics/` 。）

---

注：场景无需卸载自身， `SceneManager` 会清除场景本身；其他库的卸载流程需写在场景的 `clear` 函数中。

---

## 部分示例

??? example "logo讲解"
    路径： `Scripts/Scenes/scene_logo.lua`

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

    开始时重置音频与摄像机，并创建 logo。<br>
    同时播放音频 `snd_intro.ogg` 。

    `draw` 绘制角落的文字与提示语。

    `update` 中 `time` 增加到 180 后，提示语 `PRESS Z OR ENTER` 开始闪烁（通过改变透明度 `alpha` 实现）。

    玩家按下 Z 或 ENTER 时，跳转到 `Battle` 文件夹中的 `scene_battle_init` 场景，执行 `scene.clear()` 函数中的内容清场离开。

??? example "清理缓存"
    路径： `Scripts/Libraries/Battle/init.lua`

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

        -- Game 区有自己的一棵树：只清 Scripts.Libraries.Battle 会把这些留下，
        -- 下次进战斗就会拿到上一次的遭遇 / 怪物动画 / 灵魂模块，连状态一起带过来。
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
        -- 公开包装，内部会同时清 Game.Waves. 与 Scripts.Waves. 两个前缀
        Battle.ClearWaveModule(Battle.wave)
        battle.restoring_arena = false

        -- Clear the entire Battle library tree (UI, buttons, Player, Arenas,
        -- game_apis, Waves, PlayerAttacks, Souls, etc.) in a single pass.
        ClearModuleTree("Scripts.Libraries.Attacks")
        ClearModuleTree("Scripts.Libraries.Battle")
    end
    ```
    调用该函数时，会清理游戏文件、攻击文件、**Game 区的攻击 / 遭遇 / 怪物动画 / 波次 / 灵魂**，以及整个战斗库树的缓存。

    清理后，下次进入战斗时重新加载上述模块。

    注：`Battle.ClearWaveModule(Battle.wave)` 是 `Battle` 库提供的方法，它**同时**清除 `Game.Waves.` 与 `Scripts.Waves.` 两个前缀下的同名缓存。手写 `ClearModuleTree` 只覆盖其中一个前缀，回合脚本在两个位置之间移动后会残留旧版本。