---
title: Localization
---

Localization (L10n) pulls **all player-facing text** out of the code and into JSON files.
In the code you only write "keys"; at runtime a Lua library looks up the table, replaces placeholders, and produces the actual text for the current language.

Three pieces:

| Role | Path | Description |
|---|---|---|
| Engine default translations | `Localization/` | The engine's own copy (`en.json`, `zh_CN.json`), fallback |
| Game override translations | `Game/Localization/` | **Your game's copy goes here**, same-named files are **layered on top of the engine's** |
| Lookup & replace library | `Scripts/Libraries/Localize.lua` | Reads files, looks up keys, does `string.format` replacement |

!!! note "'Game first' is an engine-wide convention"
    It's not just translations — sprites, sounds, waves, maps, etc. all follow the "first `Game/`, then the engine directory" order.
    The full mapping is in **[Basic Development → Game Area & Resource Override](../020_basic/110_game_area.md)**.

---

## The Flow in One Line

```
Global.SetVariable("Language", "zh_CN") in Game/conf_pure.lua
        ↓
main.lua calls Localize.setFile(Global.GetVariable("Language")) at startup
        ↓
Localize reads the two layers Game/Localization/zh_CN.json and Localization/zh_CN.json,
        Game-layer keys override engine-layer keys, Game-unwritten keys fall back automatically
        ↓
dkjson decodes and merges into one flat "key → text" table
        ↓
In code: Localize.localizeText("Battle.Spare", {...})
        ↓
Look up table + string.format replace %s → return final string (or array)
```

---

## Pages in This Topic

| Page | Content |
|---|---|
| [Directories & Language Files](./000_files.md) | Priority of the two directories, how to choose a language, how to add a new language, hot reload |
| [Lookup & Replacement](./010_usage.md) | All uses of `localizeText`, dynamic keys, consequences of missing keys, typewriter tags |

---

## Minimal Example

Add a key to `Game/Localization/zh_CN.json`:

```json
{
  "MyGame.Greeting": "* Hello, %s!"
}
```

Fetch it in code:

```lua
local text = Localize.localizeText("MyGame.Greeting", {Player.name})
-- -> "* Hello, Frisk!"
```

After editing, press **F2** to reload translations — no game restart needed.
