---
title: Modifying Game Information
---

This page is part of the **common base** — both paths need it.

This page only covers the game's basic information; it does not add new content yet. The full variable reference is in [Basic development → Configuration](../020_basic/000_conf.md) .

---

## Modifying the Configuration File (conf.lua)

You only need to look at the content before the `love.conf(t)` line:

```lua
-- Soul Engine Configuration File
_VER = "3.0.0-stable"

-- Set to true when building the game for release
_RELEASED = false

-- The game's information
_INFO = {
    TITLE = "Soul Engine - v3.0.0",
    VERSION = "0.0.0", -- THIS IS YOUR GAME'S VERSION, the "_VER" upon means the engine's version.
    AUTHOR = "end",
    CONTACT = "NaN",
    WEBSITE = "NaN",
}

-- This is your window size. Change these values to set your desired resolution.
LOGICAL_WIDTH, LOGICAL_HEIGHT = 640, 480
CANVAS_WIDTH, CANVAS_HEIGHT = 640, 480

-- How much the GAME SCREEN is scaled. It is ALWAYS kept dead-centre.
--     "integer" → whole-number scaling (pixel-perfect)
--     "auto"    → fill as much of the window / screen as possible (the default)
--     false/nil → 1:1, no scaling
SCREEN_SCALE = "auto"

-- Legacy switch, only used when SCREEN_SCALE is nil: true = "auto" while
-- fullscreen and 1:1 otherwise. Prefer SCREEN_SCALE.
FILL_SCREEN = true

-- Enable error handler to show custom error screen
-- If you don't know which error crashed the game. Then you need to set it to false.
USE_ERRHANDLER = true
```

!!! important "Modifiable Variables"
    - `_RELEASED` whether the game is a released version; this usually disables all debug features, awaiting export and release.
    - All content of `_INFO` can be modified:
        - `TITLE` <u>Does not take effect on Android.</u> This is the game window title.
        - `VERSION` the game version, modify as needed.
        - `AUTHOR` who the game author is—change to your own name.
        - `CONTACT` the author/team's contact information.
        - `WEBSITE` leave blank or fill in the game's release page.
    - `LOGICAL_WIDTH` the window's width.
    - `LOGICAL_HEIGHT` the window's height.
    - `CANVAS_WIDTH` the in-game screen's width.
    - `CANVAS_HEIGHT` the in-game screen's height.
    - `SCREEN_SCALE` how large the in-game screen is drawn; the canvas is **always centered**: `"integer"` scales only by whole-number multiples (pixel-perfect), `"auto"` fills as much of the window as possible (allows fractional multiples, the default), a number fixes the multiplier, `false` keeps 1:1 with no scaling. At runtime you can also switch with the global function `SetScreenScale(mode)` and read the current multiplier with `GetScreenScale()`.
    - `FILL_SCREEN` whether to fill the entire screen. <u>Now just a legacy switch</u>—it only takes effect when `SCREEN_SCALE` is unset (`nil`); for new projects just change `SCREEN_SCALE`.
    - `USE_ERRHANDLER` whether to enable the custom error screen, default `true`. <u>But this feature is not very stable; issues during drawing may cause a crash. If you want to see all errors, temporarily disable it.</u>

!!! warning "Other Variables"
    These variables can also be modified, but it's best not to.

    - `_VER` the engine version identifier; you can modify it without leaving any problem—it just records which engine version it is.

    <u>`_VERSION` is a Lua built-in global used to return the current Lua version number. It is **not** in `conf.lua`, so don't go looking for it.</u>

---

## Modifying Initialization Configuration (conf_pure.lua)

After modifying the `conf.lua` file, you also need to initialize settings such as—but not limited to—`initial room`, `main color`, and `language used`.

The initialization configuration is split into two files, **and they are layered, not an either/or choice**:

| File | Purpose |
|---|---|
| Root `conf_pure.lua` | Engine default values; lays out all the variables used |
| `Game/conf_pure.lua` | Your game's overrides; executed later, same-named variables overwrite the engine's copy |

So the correct approach is: **write only the few lines you want to change into `Game/conf_pure.lua`** and leave the engine's copy alone. Variables you don't write automatically inherit the engine defaults; if the Game copy has an error, the engine rolls back entirely to the defaults and prints a `[Conf] WARNING`, without freezing the game.

Below is the engine's default initialization content (that is, the root `conf_pure.lua`, excerpted):

```lua
-- Initialize
Global.SetVariable("FirstRoom", "Battle.scene_battle_init")   -- same-named variable written several times; the last one wins
Global.SetVariable("MainColor", {1, 1, 1})
Global.SetVariable("Language", "zh_CN")
Global.SetVariable("UseRealTime(dt)", false)
Global.SetVariable("ScreenShaders", {})
Global.SetVariable("FPS", 60)
Global.SetVariable("F2Room", "scene_logo")
Global.SetVariable("Volume", {
    Master = 1,
    Music  = 1,
    Sounds = 1
})

Global.SetVariable("ControllerSimulation", {
    virtualKeyboard = false,
    joystick        = false,
})
Global.SetVariable("ControllerDeadzone", 0.15)

-- Network things
Global.SetVariable("GamejoltID", nil)
Global.SetVariable("GamejoltPK", nil)
Global.SetVariable("DiscordAppID", "1342517648348680202")

Global.SetVariable("SE_MEMORY_SAFETY", true)
Global.SetVariable("OPT_COUNT_SPRITES", 2000)
Global.SetVariable("OPT_COUNT_TYPERS", 300)
Global.SetVariable("OPT_MEMORY_MAXSIZE", 0.8)
Global.SetVariable("OPT_LRU_SPRITES", {false, 180})
Guard = ImportFile("Engine.MemorySafety")
```

Below is an explanation of all **global variables**.

### Normal Initialization

- `FirstRoom` the initial room; upon entering the engine you'll go directly into this room's path. The engine default is `Battle.scene_battle_init`; to switch to your own scene, write it again in `Game/conf_pure.lua`. <u>Scenes live in `Scripts/Scenes/`; to override an engine-built-in scene, put a same-named file in `Game/Scenes/`, where the Game area takes priority.</u>
- `MainColor` the game's main color tone; most of the engine's attacks and text, etc. will follow the color defined by this variable. If you want to make an `Underfell` fan game, you can try pink.
- `Language` the language the game uses. <u>The engine first checks `Game/Localization/`, then falls back to `Localization/` for missing keys</u>; if there's no specific language, write it yourself.
- `UseRealTime(dt)` usually `false` (off); if enabled, all movement operations will use **real time**.
- `ScreenShaders` no need to worry about it for now.
- `FPS` defaults to 60, can be modified.
- `F2Room` the scene returned to after pressing the `F2` key, defaults to `scene_logo`.
- `Volume` the default volume; if you want to set the global volume later, modify this variable.
- `ControllerSimulation` can simulate touchscreen control mode.
- `ControllerDeadzone` the gamepad stick deadzone (`0 ~ 1`); larger means less drift but lower precision. Default `0.15`; sensitive can use `0.10`, lenient can use `0.20`.

### Networking

- `GamejoltID` the game page ID on `gamejolt`, usually 6 to 7 digits. See [Networking → GameJolt](../090_network/000_gamejolt.md) for details.
- `GamejoltPK` is short for `private_key`, also viewable on the game release page. It ends up as plain text in the package; to hide it, see [Developer Tools → Native Secret Store](../070_develop/050_secrets.md).
- `DiscordAppID` can connect `Discord RPC` to display game progress and more in your personal activity on Discord. See [Networking → Discord RPC](../090_network/010_discord.md) for details.

### Memory Protection

- `SE_MEMORY_SAFETY` defaults to `true` (on); enables memory protection to prevent memory leaks.
- `OPT_COUNT_SPRITES` the maximum number of sprites that can be created; a warning appears at `2000`, and creation is blocked at double that number.
- `OPT_COUNT_TYPERS` allows a maximum of 300 typewriters present at once.
- `OPT_MEMORY_MAXSIZE` warns when memory usage reaches 80% of total memory.
- `OPT_LRU_SPRITES` sprite cache recycling, defaults to `{false, 180}` i.e. **off**: the second item `180` is the judgment duration in seconds, but when the first item is `false` it won't trigger recycling—sprites that enter the cache stay forever. To turn it on, change to `{true, 180}`; sprites unused for more than `180` seconds will be recycled and re-loaded from disk next time they're needed.

!!! danger "On whether to monitor memory"
    `SE_MEMORY_SAFETY` is the master switch. If your game truly needs such a large number of images and typewriters, you can turn this variable off.

    But if memory leaks become severe enough to crash the machine, you bear the consequences yourself.

---

## How to verify

Restart the game after making changes and check against this table:

| Change | What should happen |
|---|---|
| `_INFO.TITLE` | The window title bar shows the text you entered; has no effect on Android |
| `LOGICAL_WIDTH` / `LOGICAL_HEIGHT` | The window size changes |
| `SCREEN_SCALE` | The game screen changes size inside the window; it stays centred |
| `FirstRoom` in `Game/conf_pure.lua` | The game opens directly into that scene instead of the logo scene |

!!! warning "Two reasons a change has no effect"
    - The change was written into the root `conf_pure.lua` while `Game/conf_pure.lua` also sets the same variable. The Game copy runs later and overwrites the engine default.
    - `Game/conf_pure.lua` has a syntax error. The engine then rolls back entirely to the defaults, prints `[Conf] WARNING` , and every change in that file is dropped.
