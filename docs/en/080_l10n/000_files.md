---
title: Directories and Language Files
---

Localization recognizes only two directories, and the files are **one JSON per language**.

| Directory | Belongs to | Priority |
|---|---|---|
| `Game/Localization/` | Your game | **① Checked first** |
| `Localization/` | Engine default | ② Fallback |

Files in the directories are named `<language code>.json`, e.g. `en.json`, `zh_CN.json`. The current state of both directories in the project:

```
Localization/
├── en.json          ← Engine-bundled English
└── zh_CN.json       ← Engine-bundled Chinese

Game/Localization/
└── README.md        ← Currently empty; you need to put JSON in it yourself
```

---

## Lookup order

The two same-named files are **not an either/or**, but **layered**: `Game/Localization/` is the high-priority patch layer, and the engine's copy is the fallback layer.

The candidate layers in the source (`Scripts/Libraries/Localize.lua` top) are ordered from high to low priority:

```lua
local ROOT_LOCALIZATION = "Localization/"          -- ② Fallback
local GAME_LOCALIZATION = "Game/Localization/"     -- ① Patch
local LAYER_PATHS = { GAME_LOCALIZATION, ROOT_LOCALIZATION }
```

At load time, **every existing layer is read** and merged (`mergeInto`) starting from the lowest priority, with the higher priority overwriting key by key:

| Case | Result |
|---|---|
| Game area has `"A"`, engine doesn't | Use Game area's A |
| Both sides have `"A"` | **Game area wins** |
| Game area didn't write `"A"` | **Automatically falls back to the engine's copy** |

!!! note "The Game area only needs to write the entries you want to change"
    For example, put only one line in `Game/Localization/zh_CN.json`:

    ```json
    {
      "Battle.EnemiesName.Sol": "Sol"
    }
    ```

    The rest of the hundreds of keys (Battle buttons, menu, save page…) are still taken from `Localization/zh_CN.json`, and the terminal won't spit `[L10N WARNING] Missing localization key`.

!!! warning "Arrays are replaced wholesale, not merged by index"
    Array values like `"Battle.GameoverText": ["* A", "* B"]` are **fully replaced** once the Game area writes them. If you only want to change one segment, you still have to copy the whole array over and edit it.

!!! warning "A corrupted JSON in some layer is skipped"
    When the Game-area copy fails to parse, it only prints `... (layer skipped)` and keeps using the engine's copy; it **won't** take down the whole language, nor **won't** fall back to `en`. (It only falls back to `en` if both layers are broken.)

### How to confirm which copy is currently in use

At startup the terminal prints all layers that participated in the merge, with the higher priority on the left of the arrow:

```
[L10N] L10n has started successfully, using language: zh_CN (Game/Localization/zh_CN.json > Localization/zh_CN.json)
```

You can also query anytime:

```lua
print(Localize.GetLanguagePath("zh_CN"))   -- the highest-priority path
print(Localize.currentFile)                -- same as above, the main source of the loaded language
print(table.concat(Localize.GetSources(), " > "))   -- all layers participating in the merge, by priority
```

---

## Choosing a language

The language is set in the two `conf_pure.lua` files, **and the Game-area copy runs later and overrides the engine's**:

```lua
-- conf_pure.lua (engine root)
Global.SetVariable("Language", "en")
Global.SetVariable("Language", "zh_CN")    -- Writing the same variable twice: the later one wins
```

If your game wants to specify it, change the same line in `Game/conf_pure.lua` (that whole file is just the root's copy pasted then changed).

At startup `main.lua` reads it:

```lua
Localize.setFile(Global.GetVariable("Language"))
```

!!! warning "Language must be a string"
    The first line of `setFile` is `if (type(language) ~= "string")` — passing `nil` prints `[L10N WARNING] Invalid language file.` and then **returns directly**, loading no language at all. The next first call to `localizeText` will lazily load `en`, but `currentLanguage` is still `nil`, and places depending on it (like the virtual keyboard deciding Chinese vs English) will treat it as English.

### No restriction on language codes

`en`, `zh_CN`, `zh_TW`, `ja`, `ko` … name them freely, as long as they match the filename. The only thing that parses it is the virtual keyboard, which judges Chinese by the **first two characters**:

```lua
if (code and code:sub(1, 2):lower() == "zh") then return "zh" end
```

---

## Adding a new language

Take adding Japanese as an example:

1. **Copy** `Localization/en.json` to `Game/Localization/ja.json` (put it in the Game area to avoid editing the engine directory; the Game area now automatically overlays on top of the engine's copy, so **writing only your words also works**, but for a full translation it's still recommended to copy completely first then change)
2. Translate entry by entry, **only change the value to the right of the colon, don't touch a single character of the key on the left**
3. In `Game/conf_pure.lua`, change to `Global.SetVariable("Language", "ja")`
4. Run the game and check whether the terminal prints `using language: ja (Game/Localization/ja.json)`
5. After that, edit the JSON and press **F2** to hot-reload

!!! note "Missing keys are no longer fatal, but still print a warning"
    If you miss an entry while translating, or mistype a key name, at runtime it's just one line `[L10N WARNING] Missing localization key: ...`, it won't crash, but the player will see blank or garbled text. Because the Game area automatically falls back to the engine's copy, a missing key only affects **the part you newly wrote**.

---

## Hot reload

| Key | Behavior |
|---|---|
| **F2** | `Localize.reload()` + re-execute both `conf_pure.lua` + switch to the `F2Room` scene |
| **F5** | In dev mode, additionally clears the module cache and re-runs Hacks (including `Localize.reload()`) |

```lua
function localize.reload()
    if localize.currentLanguage then
        localize.setFile(localize.currentLanguage)
    else
        print("[L10N WARNING] No language loaded to reload.")
    end
end
```

!!! warning "To change language, change conf then F2"
    `reload()` only re-reads the file for the **current language**. To switch to another language, you must first change `Language` in `conf_pure.lua`, then press F2 (F2 re-runs conf). Pressing F2 directly won't switch languages.

!!! warning "When switching languages at runtime, remember to clear the cache"
    The virtual keyboard caches its label lookups; after changing language call once:

    ```lua
    VirtualKeyboard.ClearLabelCache()
    ```

---

## Structure of the JSON file

The engine's translation table is **flat**: the key is a whole dot-separated string.

```json
{
  "Battle.Spare": "Spare",
  "Battle.HP.NotFull": "* You recovered %s HP!",
  "Overworld.Menu.Buttons": ["Item", "Stat", "Phone"]
}
```

| Value type | Allowed | Note |
|---|---|---|
| String | ✅ | Most common, may contain placeholders like `%s` |
| Array | ✅ | Multi-segment text (e.g. GameoverText), or pure numeric values (e.g. menu coordinates) |
| Number / Boolean | ❌ | Prints `Invalid localization value` and returns `nil` |
| Nested object | ⚠️ | Can be stored in but **cannot be retrieved** (key lookup is flat `file["xxx"]`) |

!!! warning "Nested objects cannot be retrieved"
    The lookup implementation is `local file = ...; current = file[key]` — one step, nohierarchical descent. A nested structure like `"Items": {}` can be written in but not read out (nor is it used anywhere in the engine).

    ```json
    "Items": { "Candy": { "name": "Candy" } }   // ✗ Cannot be retrieved
    "Items.Candy.name": "Candy"                  // ✓ This is the way
    ```

!!! note "BOM is actually let through by dkjson, but still don't include it"
    dkjson's `scanwhite` skips a leading UTF-8 BOM, so a translation file with BOM **usually still reads**. But the engine's SafeJson **explicitly rejects** a BOM (see **[Advanced Development → JSON library](../050_intermediate/000_dkjson.md)**). For convenience, always save as `UTF-8` (without BOM).

!!! warning "Path is case-sensitive"
    The engine reads the disk directly with `love.filesystem.read("Localization/zh_CN.json")`. On Windows case doesn't matter, but **once packaged to Android / Linux the whole thing won't be read**. Filenames must be all-lowercase language code + `.json`.

!!! note "What's read is love.filesystem's search path"
    That is, "save directory first, then game directory". If you used `love.filesystem.write` to write a same-named file into the save directory, it will **override** the in-game copy.

---

## Appendix: what if you want "full override"

Key-based merging is now the default behavior. If you genuinely want a language to be **completely unaffected by the engine's copy** (e.g. a new-version story rewrote all battle copy and you don't want to inherit any old values), don't count on deleting the engine file — just **write out** all the keys that language needs in the Game area; missing keys will still fall back to the engine's copy.

To truly disconnect, you can only give that language a value in the Game area that doesn't contain the key, or give the language a name for which the engine directory has no corresponding file (in which case only the Game layer exists).
