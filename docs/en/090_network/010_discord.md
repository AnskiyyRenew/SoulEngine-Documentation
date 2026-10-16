---
title: Discord RPC
---

`Scripts/Libraries/DiscordRPC.lua` makes the Player's Discord profile show "Playing XX" — that is **Rich Presence**:

```
SoulEngine
Fighting Sans
Route: Genocide
Played for 12 minutes
```

Small icons, lobby player count, join buttons, etc. all come from this single library.

---

## Why `discord-rpc` instead of the Game SDK

The comment at the top of the file is very clear; restated here because **you should not "upgrade" it**:

!!! quote "`DiscordRPC.lua:12-18`"
    Why not the Discord Game SDK (discord_game_sdk.dll)?
    The Game SDK proved unstable / unusable through a direct LuaJIT FFI binding:
    `DiscordCreate` succeeds, but `get_activity_manager()` etc. return NULL no
    matter what (any flags/version/app-id), so calling any activity method
    dereferences a NULL pointer and hard-crashes the game.

In other words: **the Discord Game SDK crashes the game outright through FFI** (it gets a NULL manager pointer),
whereas the old `discord-rpc` library has only a few flat C functions (`Discord_Initialize` / `Discord_UpdatePresence`),
with no vtable and no manager getter — the path proven to work in LÖVE.

!!! note "The DiscordGameSDK directory isn't empty, it's just unused"
    This directory **was not deleted**; its `x64/` and `x86/` subdirectories contain 7 files (`discord_game_sdk.dll` / `.dll.lib` / `.so` / `.dylib` / `.bundle`), all still under version control.

    They remain only as traces of "someone tried this path before" — **the engine code references none of them**.
    The one actually loaded is `Resources/Libs/DiscordRPC/discord-rpc-x64.dll` next door.
    **Don't change the code to call the Game SDK just because they're there** — the crash described above was measured.

---

## Dependencies and availability conditions

| Condition | Description |
|---|---|
| LuaJIT's `ffi` | Only present in LÖVE's LuaJIT build. In a pure Lua build the whole library degrades to a no-op |
| Native library files | `Resources/Libs/DiscordRPC/discord-rpc-x64.dll` / `discord-rpc-x86.dll` |
| Discord client running | If Discord isn't open it just won't show, but won't error |

!!! warning "Only the Windows library exists for now"
    Under `Resources/Libs/DiscordRPC/` there are **only two .dlls**, no Linux `.so`, and no macOS `.dylib`.
    Although the source code has the candidate filenames for those two platforms written out, the files are not shipped with the engine.
    To support other platforms you must download from [discord-rpc releases](https://github.com/discord/discord-rpc/releases) and put them in that directory.

Behavior when dependencies are missing: **no error**.

```lua
local ok, err = Discord.init()
if (not ok) then print(err) end   -- just prints a line, the game keeps running
```

Without `ffi`, `init` / `setActivity` / `on*` are all replaced with the same `unavailable()`, returning `false, "DiscordRPC: LuaJIT FFI is unavailable..."`;
`update` / `shutdown` / `isAvailable` become safe empty functions.

---

## The engine already wires it up

`main.lua` has already run the whole flow:

```lua
-- love.load()
Discord.application_id = Global.GetVariable("DiscordAppID")
Discord.init()

Discord.setActivity({
    details     = "Fighting Sans",
    state       = "Route: Genocide",
    large_image = "qq20250220-225345",
    large_text  = "It's a bad time.",
    start       = Discord.timestamp(),   -- timestamp to start counting
})

-- love.update(dt)
Discord.update(dt)

-- love.quit()
Discord.shutdown()
```

So **the most common usage is only one step**: replace the ID in `Game/conf_pure.lua` with your own.

```lua
Global.SetVariable("DiscordAppID", "1234567890123456789")
```

!!! tip "Write it in `Game/conf_pure.lua`, not the root one"
    There are **two** `conf_pure.lua` files and they are layered: the root one holds engine defaults, and the `Game/conf_pure.lua` one overrides it.
    Your changes should go in **`Game/conf_pure.lua`** — editing the root one will be overwritten on engine update.
    For a comparison of the two, see [Configuration file](../010_quick_start/000_conf.md).

!!! danger "App ID must be a string"
    A 19-digit number **exceeds 2^53**; Lua's number is a double, so writing it as a numeric literal loses precision and Discord will reject the connection.

    ```lua
    Global.SetVariable("DiscordAppID", "1342517648348680202")   -- correct
    Global.SetVariable("DiscordAppID", 1342517648348680202)     -- wrong: precision loss
    ```

    The library internally does `tostring(client_id)`, but **the precision is already lost at the moment you write it into the config**.

---

## Methods

!!! example "Lifecycle"
    - `init(client_id, options)` connects to Discord. If `client_id` is omitted, it uses `Discord.application_id`.
        - `options.auto_register` tries to register the protocol when `true` (usually not needed).
        - `options.steam_id` links Steam (optional).
    - `update(dt)` **must be called every frame**; internally runs `Discord_RunCallbacks()`. The engine already calls it inside `love.update(dt)`.
    - `shutdown()` disconnects, called inside `love.quit()` (already done by the engine).
    - `isAvailable()` whether it has been initialized successfully.

!!! example "Setting Presence"
    - `setActivity(activity)` sets/updates the displayed content; the parameter is a table (fields below).
    - `clearActivity()` clears the display (the Player returns to the "playing nothing" state).
    - `timestamp(seconds)` gets the current unix timestamp (seconds); an offset can be passed, used for `start` / `finish`.

!!! example "Callbacks"
    - `onReady(callback)` fires when Discord accepts the connection; the callback receives a `user` table (`userId` / `username` / `discriminator` / `avatar`) or `nil`.
    - `onDisconnected(callback)` fires on disconnect; the callback receives `(errorCode, message)`.
    - `onError(callback)` fires on error; the callback receives `(errorCode, message)`. **A wrong App ID usually shows up here.**
    - `onJoin(callback)` fires when someone joins via an invite; the callback receives a `joinSecret` string.
    - `onSpectate(callback)` fires on spectating; the callback receives a `spectateSecret` string.
    - `onJoinRequest(callback)` fires when someone requests to join; the callback receives a `user` table.
    - `respond(user_id, reply)` responds to a join request; `reply` takes `Discord.JoinReply.No` / `.Yes` / `.Ignore`.

!!! example "Constants and state"
    - `Discord.JoinReply` = `{ No = 0, Yes = 1, Ignore = 2 }`.
    - `Discord.VERSION` the library version, currently `"2.1.0"`.
    - `Discord.application_id` your App ID (string).
    - `Discord.available` whether it has been initialized.
    - `Discord.last_error` the reason for the most recent failure.

---

## What can go in the activity table

Both naming styles are accepted, **prefer the underscore column** (Game SDK style):

| Field | Equivalent | Meaning | Byte limit |
|---|---|---|---|
| `details` | — | first line of text ("Fighting Sans") | 128 |
| `state` | — | second line of text ("Route: Genocide") | 128 |
| `start` | `startTimestamp` | start timestamp → shows "played xx:xx" | — |
| `finish` / `end` | `endTimestamp` | end timestamp → shows "remaining xx:xx" | — |
| `large_image` | `largeImageKey` | large image asset key | 32 |
| `large_text` | `largeImageText` | text shown when hovering the large image | 128 |
| `small_image` | `smallImageKey` | small image (overlaid on bottom-right of large image) asset key | 32 |
| `small_text` | `smallImageText` | text shown when hovering the small image | 128 |
| `party_id` | `partyId` | party/room identifier | 128 |
| `party_size` | — | pass `{current count, limit}` or `{current=, max=}` | — |
| `partySize` / `partyMax` | — | give the two numbers directly (takes effect when `party_size` is not used) | — |
| `match_secret` | `matchSecret` | match secret | 128 |
| `join_secret` | `joinSecret` | secret for invite-join | 128 |
| `spectate_secret` | `spectateSecret` | spectate secret | 128 |
| `instance` | — | whether it can be joined, defaults to `true` | — |

```lua
Discord.setActivity({
    details     = "Exploring the ruins",
    state       = "LV " .. DATA.player.lv .. " · HP " .. DATA.player.hp,
    large_image = "ruins",
    large_text  = "Ruins",
    small_image = "frisk",
    small_text  = "Frisk",
    start       = Discord.timestamp(),      -- count from now
    party_size  = {2, 4},                   -- shows (2 of 4)
})
```

!!! warning "The byte limit is not a character limit"
    `state` / `details` are **128 bytes**; under UTF-8 one Chinese character takes 3 bytes — **at most about 42 Chinese characters**; exceeding it causes Discord to silently drop the whole Presence.
    Truncate long text yourself.

!!! warning "Image keys must be uploaded in the backend"
    `large_image` / `small_image` holds the key obtained after uploading an image in **Discord Developer Portal → your app → Rich Presence → Art Assets** (filename without extension),
    not a file path and not a URL. A key that was never uploaded will silently not show the image.
    The engine default `qq20250220-225345` is an asset under SoulEngine's own app — **once you switch to your own App ID it no longer exists**, so remember to change it too.

!!! warning "`start` / `finish` are second-level unix timestamps"
    `Discord.timestamp()` returns `os.time()`. Passing milliseconds would be treated as the year 50000, and the timer display would break.

---

## Three practical usages

**① Switch Presence with the scene**

```lua
function SceneBattle:load()
    Discord.setActivity({
        details = "Fighting " .. Battle.enemies[1].name,
        state   = "LV " .. DATA.player.lv,
        start   = Discord.timestamp(),
    })
end
```

**② Use `onReady` to confirm the App ID is correct**

```lua
Discord.onReady(function(user)
    if (user) then
        print("[Discord] connected:", user.username)
    else
        print("[Discord] connected (no user info obtained)")
    end
end)

Discord.onError(function(code, msg)
    print("[Discord] error", code, msg)   -- most likely the App ID is wrong
end)
```

**③ Invite a friend to join**

```lua
-- host
Discord.setActivity({ ..., party_id = room.id, party_size = {n, 4}, join_secret = room.secret })

-- host receives the request
Discord.onJoinRequest(function(user)
    -- decide for yourself whether to let them in
    Discord.respond(user.userId, Discord.JoinReply.Yes)
end)
```

---

## Pitfall summary

!!! warning "`Discord.update(dt)` must be called every frame"
    Internally it is `Discord_RunCallbacks()`. If you skip it: Presence **won't refresh** and all callbacks **won't fire**.
    The engine already calls it inside `love.update(dt)`; unless you built your own separate `love.update` branch, don't duplicate it or delete it.

!!! note "Don't touch that `jit.off(discord.update)` line"
    `Discord_RunCallbacks()` re-enters Lua through the FFI callback **from C**. Doing this inside JIT-compiled code,
    LuaJIT throws `unprotected error in call to Lua API` — and it happens about 2 seconds after connecting to Discord, at the moment the ready event fires.
    The library specifically turns off JIT for `update` so it always runs in the interpreter: **deleting this line will crash the game when you least expect it.**

??? quote "That comment and code"
    ```lua
    -- CRITICAL for LuaJIT: `discord.update` calls Discord_RunCallbacks, which
    -- re-enters Lua through the FFI callback trampolines above. ... Disable JIT
    -- for this function so it always runs in the interpreter. NOTE: `jit` is a
    -- LuaJIT builtin that must be loaded explicitly; the previous
    -- `local jit = nil` shadowed the global and silently broke this.
    local ok_jit, jit = pcall(require, "jit")
    if (ok_jit and jit and jit.off) then
        jit.off(discord.update)
    end
    ```

!!! warning "Presence has an update rate limit"
    The Discord server rate-limits (roughly 5 times / 20 seconds); exceeding it silently drops updates and may trigger `onError`.
    **Don't call `setActivity` every frame** — only call it when the state actually changes (switch scene, level up, enter Battle).

!!! note "Connecting takes one or two seconds"
    `init()` returning `true` only means the local call succeeded, not that Discord has accepted it.
    To confirm, hook `onReady`; Presence generally appears in the client 1–2 seconds later.

!!! note "Exceptions in callbacks don't crash the game"
    When a user writes wrong code in a callback, the library catches it with `pcall` and prints `[DiscordRPC] callback error: ...`.
    Because these callbacks come in from the C side, a normal `pcall` can't catch them, so the library wraps one layer in each proxy itself.

!!! note "`instance` is on by default"
    `p.instance = (t.instance ~= false) and 1 or 0` — only **explicitly writing `instance = false`** turns it off.
    If `join_secret` isn't configured, leaving it on does nothing; no invite button appears out of nowhere.
