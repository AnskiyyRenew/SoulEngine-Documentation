---
title: Engine Hotkeys
---

The engine has a set of operation and debugging hotkeys. **Most take effect only in the development build (`_RELEASED = false`)** and are automatically disabled after packaging.

| Hotkey | Action | Scope |
|---|---|---|
| `F2` | Reload localization text, re-run both `conf_pure` configs, and switch to `F2Room` | All versions |
| `F4` | Toggle fullscreen / window | All versions |
| `F5` | **Hot reload**: clear cached engine modules and Game-area content, re-enter the current scene, and re-apply Hacks | Dev build only |
| `F6` | Print a debug info dump to the console (FPS, resolution, scale, current scene, input devices, sprite count, layer count, Hack report) | Dev build only |
| `F7` | Toggle Battle collision boxes (`Battle.ToggleHitboxes()`, inside the Battle scene) | Dev build only |
| `F8` | Toggle the **variable debugger** (DevTool) | Dev build only |
| `F9` | Toggle the **object debugger** (Debugger) info-text show/hide | Dev build only |

!!! note "About F3"
    The engine has **no** `F3`, nor an FPS overlay. To see the frame rate, use the `FPS` field printed by `F6`, or press `F8` to open the variable debugger and read the live value.

---

## Details of each hotkey

### F2 — Reload config and localization
Re-read the language file, re-execute both engine and Game `conf_pure.lua`, then jump to the scene specified by `F2Room`. Use it when you've changed copy or config and want to see the effect immediately.

### F4 — Fullscreen toggle
Switch between window and fullscreen, while recomputing the canvas scale; the border scales along with it.

### F5 — Hot reload
More thorough than `F2`: clears the `Scripts.Libraries` and Game-area module caches, re-enters the current scene, then reloads `Game/Hacks/`. **No need to restart the game after changing code.**

### F6 — Debug info
Prints a set of current state to the console: frame rate, window resolution, canvas scale, current scene name, virtual-keyboard and gamepad counts, sprite count, layer-object count, and the Hack registration status. Good for quickly confirming the environment.

### F7 — Battle collision boxes
Only meaningful inside the Battle scene, used to visualize perfect-pixel hitboxes. Related content: [Collision](../050_intermediate/030_collision.md) and [Battle Scene and Callbacks](../030_battle_system/070_scene.md).

### F8 / F9 — The two debuggers
`F8` opens the [variable debugger](./020_devtool.md), and `F9` controls the [object debugger](./010_debugger.md) info-text show/hide. See their respective pages for the division of labor.

---

## Custom hotkeys

The hotkeys are written in `main.lua`'s `love.keypressed`:

- Global hotkeys (`F2` / `F4` / `F5` / `F6` / `F8`) check `key` directly.
- `F7` inside Battle is polled every frame by `Battle` via `Keyboard.GetState("f7")`.

To add your own hotkey, copy the corresponding block and change the key name.
