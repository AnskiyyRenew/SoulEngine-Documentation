---
title: Global Variables
---

Global variables usually refer to variables that can be obtained or modified anywhere in the game, including stored variables.

Global library path: `Scripts/Libraries/Global.lua`

---

## In-Game Global Variables

These game variables disappear and are cleared after quitting the game; they are usually only used for operations like dividing phases within the game.

Use `Global.SetVariable(name, value)` to set a global variable named `name`.

- `name` The global variable's name.
- `value` The global variable's value. Supports: strings, numbers, booleans, tables, functions... almost all types can be stored, including files opened by `io`.

!!! example "Setting a global variable"
    Sets the name to `Chara`.
    ```lua
    Global.SetVariable("name", "Chara")
    ```

Use `Global.GetVariable(name)` to get the value of a global variable named `name`.

!!! example "Getting a global variable"
    Can get the Player's global variable.
    ```lua
    Global.GetVariable("player")
    ```

Use `Global.EnsureVariable(name, value)` to get an existing global variable; if no existing one, it creates a global variable with value `value`.

!!! warning "EnsureVariable returns `nil` on the 'create' call"
    This function only `return`s the value when it **already exists**; the actual creation call only assigns, without returning a value. So don't write `local x = Global.EnsureVariable("x", 1)` and then use `x` — the first call will tell you `x` is `nil`.

    To get the value, add a `GetVariable`:

    ```lua
    Global.EnsureVariable("config", {master = 1, sfx = 1})
    local config = Global.GetVariable("config")
    ```

!!! example "Ensuring a global variable"
    If `config` does not exist yet, create a `config` variable with value `{master = 1, sfx = 1}`; if it exists, read `config` directly.
    ```lua
    Global.EnsureVariable("config", {
        master = 1,
        sfx = 1
    })
    ```

**If you don't use the `EnsureVariable` feature, you can also manually check `nil` and `GetVariable`:**

!!! example "Primitive method"
    If you don't yet understand what `or` does outside of conditional judgments, see the [Short-circuit selection](../000_before/020_lua.md) topic.<br>
    This can catch the value directly because `SetVariable` **returns** what was set.
    ```lua
    local config =  Global.GetVariable("config") or
                    Global.SetVariable("config", {
                        master = 1,
                        sfx = 1
                    })
    ```

---

## Local Stored Variables

The variables under this section are all stored locally, suitable for game Save / Load operations.<br>
Note: this is not the Save / Load attack of `PS Flowey`; this is a separate battle effect.

!!! tip "Function differences"
    - For easy memory, all `set`, `get`, `ensure` operations have a `save` appended at the end.
    - Only supports storing: strings, numbers, tables.

Below are all the function names directly; the usage is the same as the previous section:

- `Global.SetSaveVariable(name, value)`
- `Global.GetSaveVariable(name)`
- `Global.EnsureSaveVariable(name, value)`
- `Global.DeleteSaveVariable(name)`

The extra `Delete` operation can clear storage, which can also be used in a `real reset` operation.

**The library used for storing tables is `dkjson`; see [Intermediate Development → JSON Library](../050_intermediate/000_dkjson.md) for details**
