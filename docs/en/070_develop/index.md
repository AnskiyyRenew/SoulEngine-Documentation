---
title: Developer Tools
---

---

The engine ships with some **development-only debugging and assistive tools** that let you inspect and modify the game's running state in real time, and visually generate assets — greatly improving debugging efficiency. The vast majority of these tools only take effect in development builds; they're automatically excluded when packaging for release and never enter the shipped game.

---

## Pages in This Topic

| Page | Content |
|---|---|
| [Scene Assist Tools](./000_toolscenes.md) | The engine's built-in tool scenes; the bezier easing editor (visually shape easing curves and export code) |
| [Object Debugger](./010_debugger.md) | In-game click / drag sprites, change properties, four-point deformation, export object code |
| [Variable Debugger](./020_devtool.md) | `F8` variable tree + console, inspect and modify any field in the engine's memory in real time |
| [Engine Hotkeys](./030_hotkeys.md) | Full table of `F2` ~ `F9` hotkeys: reload, fullscreen, hot-reload, debug info, hitboxes, the two debuggers |
| [Resource Preloading](./040_preload.md) | `SE.Preload(...)` / `SE.PreloadAll()` decode Game-area resources into cache ahead of time, avoiding first-reference stutter |
| [Native Secret Store](./050_secrets.md) | Compile secrets like the GameJolt private key into a `.dll` / `.so` and read them back through FFI, instead of leaving them in plain text |
| [Bundled Assets](./060_bundled_assets.md) | Which files under the engine's `Resources/` are actually in use: fonts, sounds, music, sprites and native libraries, and where each is used |
