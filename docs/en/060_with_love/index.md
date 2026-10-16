---
title: Working with LÖVE
---

`SoulEngine` is built on `love`, which means it's impossible to detach from `love`'s underlying layer.

And `love2d` has many excellent APIs, and in some cases you must use these APIs for development — they aren't directly included in any single file of `SoulEngine`.

This topic covers how `love2d`'s native APIs work together with `SoulEngine`.

---

## What is `SE`

The first thing loaded when `main.lua` starts up is it:

```lua
SE = ImportFile("Engine.FuncProtector")
```

`FuncProtector` returns a table, categorized by LÖVE's module names, where **every function is a direct forward to the corresponding `love.xxx`**:

```lua
SE.graphics.newCanvas(640, 480)            -- equivalent to love.graphics.newCanvas(640, 480)
SE.audio.newSource("a.wav", "static")      -- equivalent to love.audio.newSource("a.wav", "static")
SE.filesystem.read("config.json")          -- equivalent to love.filesystem.read("config.json")
```

So you don't need to learn a new API: **just replace `love.` with `SE.`**. Parameters, return values, and error behavior are all identical — the explanations on the [LOVE2D wiki](https://love2d.org/wiki) can be copied as-is.

!!! example "Rewrite Rule"

    ```lua
    love.graphics.rectangle("fill", 0, 0, 10, 10)
    SE.graphics.rectangle("fill", 0, 0, 10, 10)
    ```

    Only change the module name at the start; nothing after it needs to move.

### Why This Extra Layer

Open `Scripts/Libraries/Engine/FuncProtector.lua`, and every function body looks like this:

```lua
newCanvas = function(...)
    -- TODO: Implement adaptation logic
    return love.graphics.newCanvas(...)
end,
```

That `TODO` (implement adaptation logic) is for later: certain behaviors differ across LÖVE versions and platforms, and when they actually need handling, **only this layer needs to change** — neither the engine internals nor your game code need to move.

Currently all functions are pure pass-throughs with no extra behavior, so you can safely treat it as `love`.

### What It Wraps

20 categories in total, 316 functions:

| Table under `SE` | Corresponding LÖVE module | Function count |
| --- | --- | --- |
| `SE.graphics` | `love.graphics` | 101 |
| `SE.window` | `love.window` | 36 |
| `SE.filesystem` | `love.filesystem` | 31 |
| `SE.audio` | `love.audio` | 26 |
| `SE.physics` | `love.physics` | 22 |
| `SE.mouse` | `love.mouse` | 18 |
| `SE.math` | `love.math` | 16 |
| `SE.data` | `love.data` | 10 |
| `SE.keyboard` | `love.keyboard` | 9 |
| `SE.system` | `love.system` | 8 |
| `SE.event` | `love.event` | 6 |
| `SE.timer` | `love.timer` | 6 |
| `SE.joystick` | `love.joystick` | 6 |
| `SE.font` | `love.font` | 5 |
| `SE._top` | LÖVE's own top-level functions | 4 |
| `SE.thread` | `love.thread` | 3 |
| `SE.touch` | `love.touch` | 3 |
| `SE.image` | `love.image` | 3 |
| `SE.sound` | `love.sound` | 2 |
| `SE.video` | `love.video` | 1 |

`SE._top` is special — it holds the top-level functions of the `love` table itself (functions not inside any submodule):

```lua
SE._top.getVersion()                      -- equivalent to love.getVersion()
SE._top.isVersionCompatible("11.4")
```

!!! note "What's Not Wrapped"
    Event callbacks (`keypressed`, `update`, `draw`, etc.) aren't here — the engine forwards events to the scene; see [Scenes](../020_basic/010_scene.md) for how to write them.<br>
    LÖVE's **object methods** (`source:play()`, `canvas:renderTo()`) aren't here either; they travel with the object.

### Functions the Engine Added Itself

At the end of `FuncProtector.lua` there are two blocks that aren't pass-throughs but utilities written by the engine, available right now:

!!! example "Tool Functions SE.tools"

    - `SE.tools.hexColor(hexcode)` → `{r, g, b}`
        - Converts a hex color string into the three `0 ~ 1` numbers that `setColor` accepts. Supports both `#RGB` and `#RRGGBB` forms; the `#` is optional.
        - Returns `nil` (without error) when the input isn't a string or the length is wrong, so it's safe to use for parsing colors given by players/config files.

!!! example "Drawing Shortcuts SE.draw_"

    - `SE.draw_.colorText(r, g, b, a, ...)` → nothing
        - First `setColor`, then calls `print` with the remaining arguments, finally **automatically restoring the color to white**. Parameters are exactly the same as `love.graphics.print`.
        - This saves the step of "must restore color after drawing" — forgetting to restore will bleed onto everything drawn afterward; see the pitfalls in [Image Drawing](./000_graphics.md).

```lua
SE.draw_.colorText(1, 0, 0, 1, "Hello", 100, 200)

local c = SE.tools.hexColor("#C14949")
SE.graphics.setColor(c[1], c[2], c[3], 1)
```

`conf_pure.lua` sets the main color with these two lines (commented out by default; uncomment to change the main color):

```lua
Global.SetVariable("MainColor", SE.tools.hexColor("#C14949"))
```

## When Not to Use SE

`SE` is the **low-level fallback**, not the first choice. Prefer the engine's own wrapped versions, because they additionally handle Game area override, caching, volume following, and the like:

| What you want to do | First choice | Instead of |
| --- | --- | --- |
| Load a sprite | `Sprites.New` | `SE.graphics.newImage` |
| Load a font | `Fonts.New` | `SE.graphics.newFont` |
| Play audio | `Audio.PlaySound` / `Audio.PlayMusic` | `SE.audio.newSource` |

Conversely, for **things the engine doesn't wrap** (building a Canvas, writing a Shader, drawing shapes directly, reading/writing files…) just use `SE` with confidence. The engine internals do the same: `Sprites.lua` loads sprites at its lowest level with `SE.graphics.newImage`, it just wraps caching, Game area priority, and pixel snapping on top.

---

## Contents of This Topic

- [Image Drawing](./000_graphics.md) — the relationship between `SE.graphics` and `love.graphics`, a full rundown of all 101 functions
- [Audio System](./010_audio.md) — the division of labor between `SE.audio` and the engine's `Audio` library

!!! info "Tip"
    Everything in this topic can also be found on the [LOVE2D wiki](https://love2d.org/wiki), but here we only cover a few of the most commonly used ones.
