---
title: Lookup and Substitution
---

There is only one entry point for lookup:

```lua
Localize.localizeText(key)
Localize.localizeText(key, substitution parameters)
```

`Localize` is global (imported at `main.lua` startup via `ImportFile("Localize")`), so it can be called directly anywhere.

---

## Two ways to write the key

| Style | Example | Note |
|---|---|---|
| String | `"Battle.Spare"` | Most common |
| Table | `{"Battle", "Spare"}` | Joined internally with `.`, equivalent to the above |

```lua
Localize.localizeText("Battle.Spare")
Localize.localizeText({"Battle", "Spare"})     -- the same key
```

!!! warning "Only string elements in the table get joined"
    When joining, it's `if type(elements[i]) == "string"` that is collected; numbers and booleans are **silently dropped**. If the result is an empty table it returns `nil` and prints `Invalid localization key table.`.

---

## Substitution parameters (formats)

The second parameter is handed to `string.format`, supporting all placeholders like `%s` `%d` `%f` `%x`.

```json
"Battle.HP.NotFull": "* You recovered %s HP!"
```

```lua
Localize.localizeText("Battle.HP.NotFull", {12})
-- -> "* You recovered 12 HP!"
```

### Multiple placeholders

Fill them in order; the wrong order makes the text come out wrong:

```json
"Battle.WinTexts1": "* You won![wait:0.5]\n* You got %s XP and %s gold.\n"
```

```lua
Localize.localizeText("Battle.WinTexts1", {exp, gold})
```

### A single value doesn't need a table wrapper

If what you pass isn't a table, the engine wraps it itself:

```lua
Localize.localizeText("Battle.HP.NotFull", 12)      -- equivalent to {12}
```

!!! warning "Mismatched parameters return the original text"
    When `string.format` fails (not enough parameters, wrong type, extra `%`), the engine **does not error**, it only prints a line `[L10N WARNING] string.format failed for key: ...`, then **returns the string with `%s` verbatim**. The player will see the literal `%s`.

    ```lua
    Localize.localizeText("Battle.HP.NotFull")       -- forgot to pass parameters
    -- -> "* You recovered %s HP!"   ← comes out verbatim, placeholder not substituted
    ```

---

## Return value is not just a string

The looked-up value has two legal types, with different return behavior:

| Value in JSON | Without formats | With formats |
|---|---|---|
| String | Return string after substitution | Same as left |
| Array | **Return the whole array as-is** | **Per-element** substitution on each string element, return a new array |

```json
"Overworld.Menu.Buttons": ["Item", "Stat", "Phone"],
"Battle.GameoverText": ["* Our fate\n  rests on you...", "* %s![wait:0.5]\n  Hold your determination..."],
"Overworld.Menu.Interval": [215, 312, 425]
```

```lua
Localize.localizeText("Overworld.Menu.Buttons")[1]           -- "Item"
Localize.localizeText("Battle.GameoverText", {Player.name})  -- array, both lines had %s substituted
local x = tonumber(Localize.localizeText("Overworld.Menu.Interval")[1])  -- 215
```

!!! tip "The localization file is also used to store layout values"
    `Overworld.Menu.Interval` is a set of x coordinates, not text. Because buttons differ in length across languages, putting coordinates into the translation file is a reasonable usage.

!!! warning "Non-string elements in an array are kept as-is"
    During per-element substitution `else result[i] = current[i]` — numbers are not processed by `string.format`.

---

## Dynamically joined keys

Keys can be assembled at runtime; this is for "configuring different text per enemy / per action". The engine's Battle scene does exactly this:

```lua
-- Scripts/Scenes/Battle/scene_battle_init.lua:24
Battle.BattleDialogue(
    Localize.localizeText("Battle.Actions.Texts." .. enemy.id .. "." .. action.id),
    "ACTIONSELECT"
)
```

The corresponding keys in JSON:

```json
"Battle.Actions.Texts.Poseur.Check": ["* Poseur[wait:0.5] - 0 ATK 0 DEF..."],
"Battle.Actions.Texts.Poseur.Pose":  ["* You and Poseur strike a pose..."]
```

!!! warning "A joined key won't auto-find its parent"
    If `Battle.Actions.Texts.Poseur.Pose` doesn't exist, it just doesn't exist; it **won't** fall back to `Battle.Actions.Texts.Poseur`. Miss one enemy and you miss a stretch of dialogue.

---

## Where the engine looks up keys

| Location | Keys used |
|---|---|
| `Game/Encounter/*.lua` | `Battle.Narration.Default`, `Battle.EnemiesName.*`, `Battle.Actions.Names.*` |
| `Scripts/Scenes/Battle/scene_battle*.lua` | `Battle.Actions.Texts.<enemy>.<action>` |
| `Scripts/Scenes/scene_gameover.lua` | `Battle.GameoverText` |
| `Scripts/Libraries/Overworld/stat.lua` | `Overworld.Menu.Buttons` / `.Item` / `.Stat` / `.Interval` |
| `Scripts/Libraries/Overworld/shop.lua` | `Overworld.Shop.Action.<action>` |
| `Scripts/Libraries/Overworld/Pages/save.lua` | `Overworld.Save.Buttons` / `.Success` |
| `Scripts/Libraries/Overworld/Pages/chest.lua` | `Overworld.Chest.Title` / `.Tip` |
| `Scripts/Waves/nobody_came.lua` | `Overworld.Text.NobodyCame` |
| `Scripts/Libraries/Controller/VirtualKeyboard.lua` | `VirtualKeyboard.*` |

For the full list of engine-bundled keys, see `Localization/zh_CN.json` directly, grouped by prefix:

| Prefix | Manages what |
|---|---|
| `Battle.Narration.*` | The first narration line when entering Battle |
| `Battle.Spare` / `.Flee` | Battle buttons |
| `Battle.HP.*` | Heal prompt |
| `Battle.Items.Page` / `Battle.WinTexts*` | Item pagination, victory settlement |
| `Battle.GameoverText` | The two game-over lines |
| `Battle.EnemiesName.<enemy id>` | Enemy name |
| `Battle.Actions.Names.<action id>` | Action name in the ACT menu |
| `Battle.Actions.Texts.<enemy id>.<action id>` | The lines spoken after selecting an action |
| `Overworld.Menu.*` | Menu buttons, STAT panel layout |
| `Overworld.Save.*` / `Overworld.Chest.*` | Save page, chest page |
| `Overworld.Shop.Action.*` | Shop buy/sell/talk/leave |
| `VirtualKeyboard.*` | Virtual keyboard editor UI text |

!!! example "Adding translation for your own enemy"
    1. Write `Localize.localizeText("Battle.EnemiesName.Sol")` in `Game/Encounter/<your enemy>.lua`
    2. Add `"Battle.EnemiesName.Sol": "Sol"` in `Game/Localization/<language>.json`
    3. Press F2 to reload

    The key name can be anything, as long as both sides match; but **following the engine's prefixes** is easier to maintain.

---

## What happens when a key is missing

```lua
if current == nil then
    print("[L10N WARNING] Missing localization key: " .. tostring(elements))
    return nil
end
```

It doesn't error, it returns `nil`. But this `nil` is handed directly to the caller:

```lua
-- In battle: nil goes straight into the typewriter
Battle.BattleDialogue(Localize.localizeText("..."), "ACTIONSELECT")
```

`Typers.EText.New(nil, ...)` will blow up later when iterating the text — the symptom is "crashes only after you press", rather than quietly showing blank. So when you see `Missing localization key` in the terminal, don't treat it as noise; it's a signal of **impending crash or display glitch**.

!!! warning "Looking up keys every frame spams warnings"
    Menu-type code redraws every frame and looks up keys every frame; miss one key and that's 60 lines of warnings per second. Either fill in the key, or cache the result yourself like the virtual keyboard does.

---

## Typewriter tags pass through verbatim

The `[wait:0.5]`, `[speed:0.05]`, `\n` in translation text are **not handled by the localization layer**; `localizeText` only does `string.format`, and the tags are handed to the typewriter verbatim for interpretation.

```json
"Battle.Narration.Default": "* Poseur struck[wait:0.5]\n  [speed:0.05]a pose!"
```

!!! warning "When writing JSON, line breaks are `\n`"
    JSON can't have a direct line break; you must write the `\n` escape. The typewriter's layout (like two-space indentation) is achieved with spaces in the string, so preserve those spaces when translating.

---

## Virtual keyboard's special channel

The virtual keyboard doesn't call `localizeText` directly, but goes through its own `VirtualKeyboard.L(key)`:

```lua
function VirtualKeyboard.L(key)
    -- ① First look up "VirtualKeyboard." .. key
    local full = VirtualKeyboard.l10nPrefix .. key
    local ok, value = pcall(l.localizeText, full)
    cached = (ok and type(value) == "string" and value ~= "") and value or false
    if (cached) then return cached end

    -- ② If not found, use the built-in word set
    local set = LABEL_SETS[resolveLanguage()] or LABEL_SETS.en
    return set[key] or LABEL_SETS.en[key] or key
end
```

| Field / function | Action |
|---|---|
| `VirtualKeyboard.useLocalize` | Default `true`; turn off to use only the built-in word set |
| `VirtualKeyboard.l10nPrefix` | Default `"VirtualKeyboard."` |
| `VirtualKeyboard.SetLanguage("zh"/"en"/table)` | Force-specify; passing a table means a custom whole word set |
| `VirtualKeyboard.ClearLabelCache()` | Clear cache, **must call after switching language at runtime** |

!!! note "It's the only module with a built-in fallback word set"
    Other modules get `nil` on a missing key; the virtual keyboard falls back to `LABEL_SETS.en` on a missing key, at most showing English, no crash. To change its text, add `VirtualKeyboard.<key>` to the JSON.

---

## Pitfalls

!!! warning "Value being number/boolean returns nil"
    Only `string` and `table` are legal. Writing `"Battle.Foo": 123` prints `Invalid localization value for key: ...` and returns `nil`.

!!! warning "Don't write trailing commas or comments in JSON"
    dkjson's tolerance for loose JSON is limited (it supports `//` and `/* */` comments, but not trailing commas). A parse failure falls back to `en` and prints position info:

    ```
    [L10N WARNING] Invalid language file.
                   Using default language. (en)
    [L10N Error]   ... JSON parse error at position 123 in ...: ...
    ```

    Use that `position` to locate the character directly.

!!! warning "Changed translation but it didn't take effect? Check in this order"
    1. Does the terminal line `using language: xxx (path)` point to the file you edited
    2. Did you forget to press **F2** after editing
    3. Did the JSON fail to parse (there would be an `Invalid language file` warning)
    4. Is the key name misspelled (there would be a `Missing localization key` warning)
    5. Is the Chinese garbled (file encoding should be UTF-8)
