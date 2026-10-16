---
title: Game Area and Asset Override
---

`Game/` is the **root directory of content that belongs to each game itself** — this is the `Game area` repeatedly mentioned throughout this documentation.<br>
All engine-bundled assets live in their own original directories; your own content goes into the Game area instead.

The only purpose of this separation is: **engine updates will not wipe out your game content.**

---

## Division of Labor Between Two Paths

| | Engine directory | Game area |
|---|---|---|
| Purpose | Default content bundled with the engine | Content for your specific game |
| When updating the engine | Replaced wholesale | **Preserved as-is** |
| Priority | Low (fallback) | High (preferred) |

Therefore, follow one iron rule while developing: **do not modify anything directly under the engine directory.**

If you really need to change engine-bundled behavior or assets, the correct approach is to copy it into the Game area and edit that copy. Keep the engine-directory copy untouched, so you can simply overwrite it when upgrading the engine later — your changes will not be lost.

---

## General Rule: Game First, Main Directory as Fallback

Except for a few things that only read from the Game area, all other resources follow the same lookup order:

1. First check whether the Game area has a file with the same name.
2. If yes → use the Game area copy directly (**override takes effect**).
3. If no → fall back to the engine-directory copy.

This order applies to **paths**, regardless of file type: scenes, sprites, audio, translations, wave scripts, maps, attack patterns, Souls, item tables all go through this logic.

---

## What Supports Override

| Content | Game area path | Engine fallback path |
|---|---|---|
| Scene | `Game/Scenes/<name>.lua` | `Scripts/Scenes/<name>.lua` |
| Sprite | `Game/Resources/Sprites/` | `Resources/Sprites/` |
| Sound effect | `Game/Resources/Sounds/` | `Resources/Sounds/` |
| Music | `Game/Resources/Music/` | `Resources/Music/` |
| Font | `Game/Resources/Fonts/` | `Resources/Fonts/` |
| Translation (key overlay) | `Game/Localization/` | `Localization/` |
| Wave script | `Game/Waves/<name>.lua` | `Scripts/Waves/<name>.lua` |
| Attack Pattern | `Game/Attacks/<name>.lua` | `Scripts/Libraries/Battle/PlayerAttacks/<name>.lua` |
| Soul | `Game/Souls/<name>.lua` | `Scripts/Libraries/Battle/Player/Souls/<name>.lua` |
| Map | Same relative path under `Game/` | `Maps/` |
| Item table | `Game/Logics/items.lua` | `Scripts/Logics/items.lua` |

!!! note "Two easy pitfalls"
    - For **fonts**, just write the filename: `Fonts.New("determination_mono.ttf", 27)` will first look in `Game/Resources/Fonts/`. All font loading in the engine goes through this entry, so you don't need to change any call code — drop in a file with the same name and it gets swapped.
    - The engine fallback directory `Scripts/Logics/` for the **item table does not currently exist** (the engine does not ship this file), so in practice the item table now only has `Game/Logics/items.lua` as its single source. The same-directory `Game/Logics/init.lua` is even a hard require, with no fallback at all.

---

## What Only Reads From the Game Area

The following content has **no** available same-named engine-side directory. It is game-specific data — just write it directly in the Game area, no need to worry about overrides:

| Content | Path |
|---|---|
| Encounter | `Game/Encounter/` |
| Monster animation | `Game/Animations/` |
| Game logic data | `Game/Logics/` |
| Hack scripts | `Game/Hacks/` |
| Whole-module replacement map | `Game/Overrides.lua` |
| Configuration override | `Game/conf_pure.lua` |

This is also why these items appear with only a single path in the docs — they are yours by nature, and the engine provides no default version.

Among these, **`Game/conf_pure.lua` is "layered" rather than "fallback"**, unlike the others: the engine always runs the root `conf_pure.lua` first to lay down all default values, then runs your copy to override the same-named variables. So you only need to write the few lines you want to change. If your copy errors out halfway through, the engine will roll back entirely to the defaults and print `[Conf] WARNING: ... exists but failed to load; using the engine defaults ...`, and the game will still start.

!!! tip "What goes in game logic"
    World rules (level curve, how max level expands, story switches, chest contents) have their own page: **[Game Logic and World Rules](./120_game_logics.md)**.

!!! warning "Don't confuse `Game/Logics` with `Game/Hacks`"
    Both directories have "logic"-like names, but their responsibilities are completely different: `Game/Logics/` holds **data** (level tables, chest contents), while `Game/Hacks/` holds **code** (rewriting engine behavior). The next section covers the latter.

---

## Rewriting Engine Internals With Hacks

All the methods above share one premise: the content itself must be "placeable elsewhere." But some things don't belong to any category — such as the battle UI layout, the battle flow state machine, or the internal behavior of the sprite library. They live in `Scripts/Libraries/`, and previously the only way to change them was to touch the engine.

The Game area provides two supported entry points:

### 1. `Game/Overrides.lua` — declarative whole-module replacement

A map of `["engine module name"] = "Game module name"`, suitable for "I want to rewrite this whole module":

```lua
-- Game/Overrides.lua
return {
    ["Scripts.Libraries.Battle.UI"] = "Game.UI.Battle",
}
```

### 2. `Game/Hacks/*.lua` — imperative patching

Executed once each at startup in **filename numeric-prefix** order, suitable for "I only want to change one or two functions":

```lua
-- Game/Hacks/010_my_battle.lua
return {
    name = "My battle tweak",
    apply = function(Hack)
        Hack.After("Scripts.Libraries.Battle", function(battle)
            -- runs once after the engine finishes loading Battle
        end)
    end
}
```

Available primitives: `Hack.Replace` (whole-module replace), `Hack.After` (post-load callback), `Hack.Wrap` (wrap a function), `Hack.Set`, and the more internal `Hack.Patch`. Full docs and caveats are in `Game/Hacks/README.md`.

!!! warning "Filename rules"
    **Every `.lua` in `Game/Hacks/` is treated as an entry and executed**; only files beginning with an underscore `_` are skipped.<br>
    So if you want to put a whole module in this directory as replacement material, the filename must include an underscore (e.g. `_my_ui.lua`), otherwise it will be run as an entry and then complain "this file returns neither a function nor a `{apply = ...}`".

!!! tip "Press F5 after editing"
    Both entry points first undo and then re-apply on hot reload, so after editing the config pressing **F5** takes effect without restarting.

---

## What Happens When an Override Breaks

One thing deserves its own section: **override failures are always reported, never silent.**

When the engine looks up a resource it strictly distinguishes "file does not exist" from "file exists but errored on load," yielding three possible outcomes:

!!! example "Three outcomes"

    **1. Normal override** — the Game area has it and it loads fine. No output; the Game area copy is used directly.

    **2. Override not found, fallback succeeded** — the Game area doesn't have it, the engine-directory copy is used:

    ```
    [Battle] WARNING: 'bones.wave1' not found in Game.Waves. (fell back to Scripts.Waves.bones.wave1).
    ```

    This is **normal** — just confirm "I indeed didn't write this override."

    **3. Override exists but is broken** — the Game area has this file, but it errors on load:

    ```
    [Battle] WARNING: 'Game.Waves.bones.wave1' exists but failed to load; using Scripts.Waves.bones.wave1 instead.
    [Battle]   <the actual error message>
    ```

    **Seeing `exists but failed to load` means your override did not take effect**, and the actual error is printed too — just fix it accordingly.

Different subsystems use different warning prefixes; just look for the words `exists but failed to load`:

| Prefix | From |
|---|---|
| `[Battle]` | Encounter, wave, attack pattern, Soul |
| `[Scenes]` | Scene |
| `[Overworld]` | Map, item table |
| `[Conf]` | `Game/conf_pure.lua` |
| `[Hack]` | `Game/Hacks/` and `Game/Overrides.lua` |

!!! warning "Why 'not found' and 'broken' must not be conflated"
    Early versions used the success/failure of `pcall(require, ...)` to decide whether a module exists.<br>
    The problem is that `pcall` returning `false` has two completely different causes: **the file does not exist**, and **the file exists but its top-level code errored**.<br>
    Treating the latter as "does not exist" causes two bad things at once: the fallback chain is silently truncated (you think the override took effect, but the old version runs), and the real error is swallowed without display.<br>
    So now it is **check whether the file exists first, then decide whether to require it**. A few extra lines buy you the guarantee that once something breaks, you will definitely see it.

---

## Some Caveats

- **Always use forward slashes `/`** for paths, starting from the project root directory.
- **Filenames must match exactly** — override is "same-name replacement," not "nearest merge." Once you put `px.png` in the Game area, the engine-directory `px.png` is no longer used at all.
- **Map image references are relative paths**. The engine's map `.lua` references tiles via `../images/...`, so when overriding a map, the Game area copy must also bring its own corresponding `../images/` directory tree, otherwise tiles will be missing.
- **When an override doesn't take effect, check the terminal first.** The third case above will always print a warning — don't guess.
